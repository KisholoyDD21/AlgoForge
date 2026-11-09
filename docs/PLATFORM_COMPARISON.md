# Platform comparison and feature selection

This is a product-level comparison, not an exhaustive audit of every feature or a claim of formal parity with the platforms.

| Platform | Strengths to learn from | AlgoForge adoption | Important boundary |
|---|---|---|---|
| LeetCode | Interview-oriented problem discovery, topic filters, submissions, discussion and progress | Question explorer, tags, difficulty, notes, saved questions, submission history | The original statement, hidden tests, editorial and verdict remain with LeetCode unless permission is obtained |
| HackerRank | Structured skill tracks, language practice, tests and skill assessment | Roadmaps, language selector, practice dashboard | No HackerRank account, test or proprietary question integration |
| Codeforces | Competitive programming, rating-based difficulty, tags, contests and public API | Official metadata importer, rating-derived difficulty, pattern tags and contest links | Live account sync / contest registration not implemented |
| CodeChef | Practice, contests, ratings and community | External source links and contest discovery link (future integration) | No platform account linking or live rating sync |
| AtCoder | Contest-centric progression and clear problem archives | External source links can be added to importer later | No official account integration in this MVP |
| GeeksforGeeks | Topic-based learning, articles and practice | Topic and pattern taxonomy, learning paths | Third-party editorial content is not copied |
| CSES | Coherent algorithmic problem set and topic progression | Roadmap structure and source-link pattern | CSES problem text and tests are not mirrored |
| SPOJ | Broad archive of judged programming problems | Future metadata source only | No scraping or hidden-test import |

## Selected differentiators

- Pattern as a first-class filter, not only a loose topic tag.
- Unified C/C++/Java/Python scratchpad using one isolated execution service.
- Separate display for estimated theoretical complexity and measured runtime/memory.
- Learning paths and consistent daily activity history.
- Explicit source attribution and licence-aware metadata imports.

## Implemented product scope and remaining differences

AlgoForge now has its own original-problem judging path, scheduled contests, registration, contest problem release and a basic scoring/penalty leaderboard. It does not sync official ratings or contest accounts with Codeforces, CodeChef or AtCoder. It does not mirror third-party statements or hidden tests. Discussions, live collaboration, company-tag verification, external verdict sync and official platform account linking still require product work, authorised APIs or additional operational infrastructure.
