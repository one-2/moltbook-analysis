"""Worker module for parallel trait scoring across multiple API keys."""

import asyncio
import json
import os
import sqlite3
import time
from openai import AsyncOpenAI

# OpenRouter configuration (routing to Vertex AI)
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Cache configuration - use absolute path based on this file's location
_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DB = os.path.join(_MODULE_DIR, '..', 'cache', 'trait_cache.db')


def init_db():
    """Create the cache database and table if they don't exist."""
    os.makedirs(os.path.dirname(CACHE_DB), exist_ok=True)
    conn = sqlite3.connect(CACHE_DB, timeout=30.0)  # 30 second timeout for locks

    # Enable WAL mode for better concurrent write performance
    conn.execute("PRAGMA journal_mode=WAL")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            post_id TEXT PRIMARY KEY,
            scores TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def load_cache():
    """Load the SQLite cache into a dict for fast lookups.

    Returns: {post_id: {trait: score, ...}, ...}
    """
    if not os.path.exists(CACHE_DB):
        return {}
    try:
        conn = sqlite3.connect(CACHE_DB, timeout=30.0)
        rows = conn.execute("SELECT post_id, scores FROM scores").fetchall()
        conn.close()
        return {post_id: json.loads(scores) for post_id, scores in rows}
    except Exception as e:
        print(f"Warning: Could not load cache: {e}")
        return {}


def save_batch_to_cache(batch_results, traits, max_retries=5):
    """Save a batch of results to SQLite cache immediately with retry logic."""
    for attempt in range(max_retries):
        try:
            conn = sqlite3.connect(CACHE_DB, timeout=30.0)  # 30 second timeout
            for result in batch_results:
                scores_dict = {}
                for i, trait in enumerate(traits):
                    scores_dict[trait] = result['scores'][i]
                conn.execute(
                    "INSERT OR REPLACE INTO scores (post_id, scores) VALUES (?, ?)",
                    (result['post_id'], json.dumps(scores_dict))
                )
            conn.commit()
            conn.close()
            return  # Success!
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower() and attempt < max_retries - 1:
                # Database locked, wait and retry
                wait_time = 0.5 * (2 ** attempt)  # Exponential backoff: 0.5, 1, 2, 4, 8 seconds
                print(f"Cache locked, retrying in {wait_time}s (attempt {attempt+1}/{max_retries})")
                time.sleep(wait_time)
            else:
                print(f"Warning: Could not save batch to cache after {attempt+1} attempts: {e}")
                break
        except Exception as e:
            print(f"Warning: Could not save batch to cache: {e}")
            break


def process_posts_worker(args):
    """Each worker gets a chunk of posts and one API key. Runs in separate process."""
    worker_id, posts_chunk, traits, api_key, semaphore_val, batch_size, rpm_limit, progress_dict = args
    result = asyncio.run(_async_worker(worker_id, posts_chunk, traits, api_key, semaphore_val, batch_size, rpm_limit, progress_dict))
    return result


class RateLimiter:
    """Simple RPM rate limiter using sliding window."""
    def __init__(self, rpm):
        self.rpm = rpm
        self.window = 60.0  # 1 minute window
        self.timestamps = []
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            now = time.time()
            # Remove timestamps older than 1 minute
            self.timestamps = [t for t in self.timestamps if now - t < self.window]

            if len(self.timestamps) >= self.rpm:
                # Wait until oldest request exits the window
                wait_time = self.timestamps[0] + self.window - now + 0.01
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    now = time.time()
                    self.timestamps = [t for t in self.timestamps if now - t < self.window]

            self.timestamps.append(time.time())


async def _async_worker(worker_id, posts_chunk, traits, api_key, semaphore_val, batch_size, rpm_limit, progress_dict):
    """Async work within a single process."""
    print(f"[{worker_id}] Worker starting: {len(posts_chunk)} posts, {len(traits)} traits")

    limit = asyncio.Semaphore(semaphore_val)  # Concurrency limit
    rate_limiter = RateLimiter(rpm=rpm_limit)  # Requests per minute per worker
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=OPENROUTER_BASE_URL
    )
    results = []
    cache_stats = {'hits': 0, 'misses': 0}
    worker_key = f'w{worker_id}'

    # Load cache once at worker start
    print(f"[{worker_id}] Loading cache...")
    cache = load_cache()
    print(f"[{worker_id}] Cache loaded: {len(cache)} cached posts")

    # Initialize worker stats in shared dict
    if progress_dict is not None:
        progress_dict[f'{worker_key}_completed'] = 0
        progress_dict[f'{worker_key}_total'] = len(posts_chunk)
        progress_dict[f'{worker_key}_rate_limits'] = 0
        progress_dict[f'{worker_key}_errors'] = 0

    async def get_trait_score(post_id, post_content, trait, max_retries=5):
        # Check in-memory cache
        if post_id in cache and trait in cache[post_id]:
            cached_val = cache[post_id][trait]
            if cached_val is not None:
                cache_stats['hits'] += 1
                return int(cached_val)

        cache_stats['misses'] += 1

        attempt = 0
        while True:
            await rate_limiter.acquire()  # Wait for RPM slot
            async with limit:  # Then check concurrency
                try:
                    response = await client.chat.completions.create(
                        model='openai/gpt-oss-120b',  # Vertex AI through OpenRouter
                        
                        messages=[{
                            'role': 'user',
                            'content': f"Does the text explicitly display {trait}? Reply with yes or no only. One word response. \n\n {post_content}"
                        }],
                        max_tokens=10
                    )
                    answer_text = response.choices[0].message.content.lower()
                    score = 1 if "yes" in answer_text else 0
                    return score
                except Exception as e:
                    error_str = str(e)
                    error_type = type(e).__name__
                    is_rate_limit = "429" in error_str or "rate" in error_str.lower()

                    # ALWAYS print first occurrence of any error
                    if attempt == 0:
                        print(f"[{worker_key}] ⚠️  {error_type}: {error_str[:300]}")

                    # Exponential backoff: 2, 4, 8, 16, 32... seconds (capped at 60)
                    backoff = min(2 ** (attempt + 1), 60)

                    if is_rate_limit:
                        # Track rate limit hit
                        if progress_dict is not None:
                            progress_dict[f'{worker_key}_rate_limits'] = progress_dict.get(f'{worker_key}_rate_limits', 0) + 1
                        if attempt > 0:
                            print(f"[{worker_key}] Rate limit (attempt {attempt}), waiting {backoff}s")
                        await asyncio.sleep(backoff)
                        attempt += 1
                        continue
                    else:
                        # Other error: print and retry
                        attempt += 1
                        if attempt < max_retries:
                            print(f"[{worker_key}] Retrying (attempt {attempt}/{max_retries}) in {backoff}s...")
                            await asyncio.sleep(backoff)
                            continue
                        else:
                            # Final failure - print details
                            print(f"[{worker_key}] ❌ FAILED after {max_retries} retries:")
                            print(f"[{worker_key}]    Post: {post_id}, Trait: '{trait}'")
                            print(f"[{worker_key}]    Error: {error_type}: {error_str}")
                            if progress_dict is not None:
                                progress_dict[f'{worker_key}_errors'] = progress_dict.get(f'{worker_key}_errors', 0) + 1
                            return None

    async def process_post(post):
        post_id = post.get('post', {}).get('id', 'unknown')
        post_content = post.get('post', {}).get('content', '')
        trait_tasks = [get_trait_score(post_id, post_content, trait) for trait in traits]
        scores = await asyncio.gather(*trait_tasks)
        return {'post_id': post_id, 'content': post_content, 'scores': list(scores)}

    print(f"[{worker_id}] Processing {len(posts_chunk)} posts in batches of {batch_size}")

    for i in range(0, len(posts_chunk), batch_size):
        batch = posts_chunk[i:i + batch_size]
        print(f"[{worker_id}] Starting batch {i//batch_size + 1}: {len(batch)} posts")

        batch_results = await asyncio.gather(*[process_post(p) for p in batch])
        results.extend(batch_results)

        print(f"[{worker_id}] Batch {i//batch_size + 1} complete, saving to cache...")
        # Save batch to cache immediately
        save_batch_to_cache(batch_results, traits)
        print(f"[{worker_id}] Batch {i//batch_size + 1} cached")

        # Update shared progress
        if progress_dict is not None:
            progress_dict['completed'] = progress_dict.get('completed', 0) + len(batch)
            progress_dict['cache_hits'] = progress_dict.get('cache_hits', 0) + cache_stats['hits']
            progress_dict['cache_misses'] = progress_dict.get('cache_misses', 0) + cache_stats['misses']
            progress_dict[f'{worker_key}_completed'] = progress_dict.get(f'{worker_key}_completed', 0) + len(batch)
            # Reset local stats since we've reported them
            cache_stats = {'hits': 0, 'misses': 0}

    print(f"[{worker_id}] Worker complete: {len(results)} posts processed")
    return results
