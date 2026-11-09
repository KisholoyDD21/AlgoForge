# Changelog

## 0.8.0 — Guided learning and function-workspace expansion

- Replaced four static roadmaps with four data-driven DSA tracks containing ordered modules, objectives, prerequisite rules, time estimates and catalogue-backed question recommendations.
- Added per-module and per-track progress computed from real recorded completions. Prerequisites unlock at 60% of the prior module target; catalogue gaps are displayed instead of being disguised as completed curriculum.
- Updated the Learning Paths UI with progress meters, module states, prerequisite context and direct links to matching problems.
- Added trusted function-style judge adapters and starter templates for Valid Parentheses, Maximum Subarray Sum and Longest Substring Without Repeating Characters in C, C++, Java and Python.
- Expanded compile-and-execute adapter checks and added API tests for catalogue mapping, progress updates and prerequisite unlock rules.
- No schema migration was required; learning-path definitions are version-controlled application data and user progress reuses the existing problem-progress records.


## 0.7.0 — Catalogue integrity and learning-signal milestone

- Removed fixed, fabricated pattern-progress percentages from the dashboard. Signed-in learners now see mastery calculated from their recorded progress; guests see catalogue counts rather than fake completion bars.
- Expanded problem search to include topic tags and stable problem slugs, matching the filter's user-facing description.
- Made Codeforces catalogue import non-destructive by default: dry-run preview, projected bucket totals and optional JSON report; `--apply` is required to write records.
- Added a read-only catalogue audit for metadata completeness, difficulty values, HTTPS source links, duplicate slugs and third-party content/provenance boundaries.
- Added regression tests for search, truthful dashboard progress, safe import defaults and catalogue audit rules.


## 0.6.0 — Research, repository and release-readiness milestone

- Rewrote the README as a professional project entry point with product overview, screenshots, architecture, setup, judging configuration, API map, research decisions and honest maturity boundaries.
- Expanded the research dossier with primary-source comparisons for LeetCode, Codeforces, CodeChef, AtCoder, CSES and HackerRank, plus security/accessibility/performance standards.
- Added architecture decision records and a production readiness gate checklist.
- Added third-party notices and an MIT licence boundary for original application code; external problem content, marks and dependencies remain under their own rights.
- Added GitHub issue forms, pull request template, Dependabot configuration and CodeQL workflow.
- Expanded CI to Python 3.11 and 3.12 and kept clean migration, backend test and frontend syntax checks.

## 0.5.0 — Premium UI refresh

- Reworked first-load landing page and product identity.
- Fixed frontend bootstrap invocation and theme persistence/state synchronization.
- Improved dark/light theme contrast and mobile layout.
- Added landing-page screenshots and UI QA notes.

## 0.4.0 and earlier

See the implementation history in Git tags/releases when available. The repository's implementation status is documented in `IMPLEMENTATION_STATUS.md`.
