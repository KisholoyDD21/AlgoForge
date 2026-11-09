# AlgoForge learning-path engine

Release: 0.8.0 · Updated: 3 November 2026

## Product intent

Learning paths turn the pattern catalogue into sequenced practice. Unlike the earlier static roadmap cards, every module is resolved against the current problem catalogue at request time. The API returns real problem links, actual per-user progress, prerequisite state and explicit catalogue coverage gaps.

## Included tracks

| Track | Intended level | Focus |
|---|---|---|
| DSA Foundations | Beginner → Intermediate | Arrays, strings, hashing, two pointers, sliding window, binary search, stacks and introductory DP |
| Graph Algorithms | Intermediate | BFS/DFS, connected components, topological sorting, shortest paths, spanning trees and DSU |
| Dynamic Programming | Intermediate → Advanced | Recurrences, memoization, grid DP, knapsack, subsequence DP and advanced state design |
| Competitive Programming Core | Beginner → Advanced | Implementation, sorting/search, greedy reasoning, number theory, bitmasks and timed practice |

Each module includes a learning objective, estimated study minutes, pattern/topic selectors, a target problem count and prerequisite module IDs. Track definitions live in `app/learning_paths.py` and are reviewed as application code. No database migration is required for curriculum edits.

## Catalogue matching

A problem is associated with a module when either:

1. Its primary `Problem.pattern` exactly matches a module pattern (case-insensitive), or
2. One of its `Problem.topics` exactly matches a module topic (case-insensitive).

Recommendations prioritize AlgoForge-original problems, then difficulty (Easy, Medium, Hard), then stable database order. The API returns at most four not-yet-solved problems for each module. Third-party rows remain metadata and canonical links; the learning path does not copy their statements, tests or editorials.

Exact matching is intentional. It makes the mapping deterministic and reviewable, but it means taxonomy synonyms must be maintained in the learning-path definition or normalized in a future taxonomy migration. A module may therefore expose a catalogue gap even when a human can identify related questions.

## Progress semantics

Progress reuses the existing `UserProgress` records rather than maintaining a second completion ledger.

- `solved` counts problems whose recorded progress status is `solved`.
- `attempted` counts `in_progress` and `solved` rows.
- `target_count` is the smaller of the module's configured target and the number of matching problems in the current catalogue.
- `progress_pct` is `solved / target_count`, capped at 100. A module with no matching problems has 0% and a `catalogue-gap` state.
- A module is complete when it has at least one matching problem and its solved count reaches `target_count`.
- A user-specific module unlocks when every prerequisite module has reached at least 60% of its own target. A track preview for a guest does not apply account-specific locks; signing in enables personalized progress.
- Externally hosted problem completions are self-reported by the learner. They are not verified by LeetCode, Codeforces, AtCoder, CSES, HackerRank or CodeChef. AlgoForge-original problems can be marked solved by a successful full-suite submission.

The overall track percentage is computed from target counts across its modules. Since the same problem may be relevant to more than one track, track progress is intentionally not additive across the four tracks and must not be presented as a percentage of the global catalogue.

## API

`GET /api/roadmaps` returns all tracks. Authentication is optional: signed-in users receive personalized module progress and prerequisite lock state; guests receive the curriculum and catalogue mapping with zero personal progress.

Relevant response fields:

- Track: `slug`, `name`, `level`, `duration`, `outcome`, `progress_pct`, `target_count`, `solved`, `module_count`, `completed_modules`.
- Module: `id`, `title`, `objective`, `patterns`, `prerequisites`, `unlocked`, `status`, `total_problems`, `target_count`, `solved`, `attempted`, `progress_pct`, `recommended`.
- Recommended problem: `slug`, `title`, `difficulty`, `pattern`, `platform`, `is_native`.

The frontend uses the returned problem slugs to navigate directly to the problem workspace. Progress refreshes when the Learning Paths view is loaded again.

## Validation

Automated API tests cover:

- All four tracks and real catalogue matches.
- Recommendation records and module shape.
- Progress updating after a learner marks a problem solved.
- Prerequisite unlock at the 60% threshold.
- Function-style execution is separately covered by compile-and-run tests for seven original problems across C, C++, Java and Python.

The catalogue is still 159 entries. A curriculum module with insufficient matches is a visible content gap, not evidence that the module has been fully authored or that the entire syllabus is covered. Continue curating the question bank and review the module-to-problem mapping as new material is added.
