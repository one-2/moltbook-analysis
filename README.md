# Moltbook Analysis

Repo for analysis of moltbook data.

## Motivation

Multi-agent AI systems (MAS) are a possible path to superintelligence, (Bostrom, 2014) and present unique risks, like emergent agency, not encountered in the single-agent setting. Our understanding of these risks is relatively poor. (Hammond et al., 2025) MAS also offer benefits from increased coordination and autonomous workforces. (Tomasev et al., 2025) Progress on MAS safety is important to realising these benefits.

[Moltbook](https://www.moltbook.com/) is a social media site for AI agents, where agent can interact with each other on a reddit-style forum free of human oversight. 

As the first  is the first natural MAS-only social environment, Moltbook extends the possibilities for study MAS safety beyond simulated environments like (UNSW Institute for Cyber Security, 2025). 

Treating Moltbook as an early case study in MAS safety, I aim to explore a few research questions:

- How do agents behave on Moltbook?
- Which MAS safety risks manifest in Moltbook, and how commonly?
- Do individual agents have power on Moltbook?
- How do subnetworks on Moltbook affect agent behaviour?
- Does the system as a whole develop trends, and to what extent can these be seen as emergent behaviour?
- How reliable is Moltbook as a case study?

I will not articulate hypotheses yet as I am presently (1 Feb 2026) aiming to characterise the system in broadstroke and investigate anything interesting, rather than conduct experiments or answer a specific question.

## The analysis

You can find my analysis in the Jupyter notebooks in the source file.

### Other work on Moltbook

You can find some other analysis on Moltbook here:

-
    

## Tools

Thank you to:

- (Newman and Rimey, 2026) for the [Moltbook data source](https://www.lesswrong.com/posts/WyrxmTwYbrwsT72sD/moltbook-data-repository).
- (Perez et al., 2022) for the traits dataset.

References are at the bottom of the page

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
    - [ ] Did further analysis of the self-improvement posts
    - [ ] Sorted traits by "self-affecting", "political", "philosophical"; and did more relevant analysis
- [ ] Collected notes into a discussion section
- [x] Added context on Moltbook
- [ ] Added links to other analysis on Moltbook harms
- [ ] Added open questions section
- [x] Added so what / hook connecting to CTN, Hammond, ...
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

Bostrom, N. (2014). *Superintelligence: Paths, dangers, strategies*. Oxford University Press.

Hammond, L., Chan, A., Clifton, J., Hoelscher-Obermaier, J., Khan, A., McLean, E., Smith, C., Barfuss, W., Foerster, J., Gavenčiak, T., Han, T. A., Hughes, E., Kovařík, V., Kulveit, J., Leibo, J. Z., & Oesterheld, C. (2025). *Multi-agent risks from advanced AI (Technical Report No. 1)*. Cooperative AI Foundation. https://doi.org/10.48550/arXiv.2502.14143

Newman, E. and Rimey, K. (2026). *Moltbook Data: A Dataset of AI Agent Social Interactions*. GitHub. https://github.com/ExtraE113/moltbook_data

Perez, E., Ringer, S., Lukošiūtė, K., Nguyen, K., Chen, E., Heiner, S., Pettit, C., Olsson, C., Kundu, S., Kadavath, S., Jones, A., Chen, A., Mann, B., Israel, B., Seethor, B., McKinnon, C., Olah, C., Yan, D., Amodei, D., . . . Kaplan, J. (2022). *Discovering language model behaviors with model-written evaluations*. arXiv. https://doi.org/10.48550/arXiv.2212.09251

Tomasev, N., Franklin, M., Leibo, J. Z., Jacobs, J., Cunningham, W. A., Gabriel, I., & Osindero, S. (2025). *Virtual agent economies*. arXiv. https://doi.org/10.48550/arXiv.2509.10147

UNSW Institute for Cyber Security. (2025). *Capture the Narrative*. https://capturethenarrative.com/
