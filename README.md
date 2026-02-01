# Moltbook Analysis

Repo for analysis of moltbook data.

## Moltbook

[Moltbook](https://www.moltbook.com/) is a social media site for AI agents, where agent can interact with each other on a reddit-style forum free of human oversight.

It's been running since 27 January 2026 and as of 1 February has over a million registered accounts. You can find up-to-date population data at Newman and Rimey's [Moltbook Data Repository](https://www.lesswrong.com/posts/WyrxmTwYbrwsT72sD/moltbook-data-repository).

## Tools

I use (Newman and Rimey, 2026) for my data source. Thank you!

## Plan
### Early analysis
- [x] Retrieved a target file
- [x] Harvested behaviours from the "model-written evals" dataset
- [x] Used a GPT to classify some or all of the posts on the network into these categories
- [x] Extended to 100 posts
- [x] Did exploratory data analysis
- [x] Added caching
- [x] Analysed worst actors
- [x] Extended to 400 posts
- [ ] Analysed data
    - [x] Added analysis of correlations
    - [ ] Further analysis of the self-improvement problem
    - [ ] Some useful lenses on traits are "desire", "belief", "awareness"; "self enhancement", "political", "philosophical"; and returned to open questions
- [ ] Collected results and open questions into a discussion section
- [x] Added context on Moltbook
- [ ] Added so what / hook connecting to CTN, Hammond, ...
- [ ] Added replication data
- [ ] Shared on LessWrong

### Extensions
- [ ] Analysed top authors
- [ ] Analysed top posts
- [ ] Analysed comments
- [ ] Analysed author networks
- [ ] Clustered traits to see if there's a post population structure, as suggested by correlations
- [ ] Built a network map to conduct network analysis of the system
- [ ] Analysed trending posts to discover Selection Pressures (Hammond et al., 2025)
- [ ] Searched for evidence of emergent agency: Emergent Capabilities, Emergent Goals. (Hammond et al., 2025)
- [ ] Added thematic analysis
- [ ] Added network analysis
- [ ] Added time-series analysis
- [ ] Tested stability under resampling

## References

Hammond, L., Chan, A., Clifton, J., Hoelscher-Obermaier, J., Khan, A., McLean, E., Smith, C., Barfuss, W., Foerster, J., Gavenčiak, T., Han, T. A., Hughes, E., Kovařík, V., Kulveit, J., Leibo, J. Z., & Oesterheld, C. (2025). *Multi-agent risks from advanced AI (Technical Report No. 1)*. Cooperative AI Foundation. https://doi.org/10.48550/arXiv.2502.14143

Newman, E. and Rimey, K. (2026). *Moltbook Data: A Dataset of AI Agent Social Interactions*. GitHub. https://github.com/ExtraE113/moltbook_data