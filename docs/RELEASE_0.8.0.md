# AlgoForge 0.8.0 release record

Release date: 3 November 2026

## Delivered

- Four catalogue-backed learning tracks: DSA Foundations, Graph Algorithms, Dynamic Programming and Competitive Programming Core.
- Real module progress based on `UserProgress`, explicit target counts, prerequisite gating at 60% mastery and visible catalogue-gap states.
- Learning-path UI with module objectives, time estimates, status, direct problem links and per-track progress.
- Function-style execution adapters and starter templates for seven original problems across C, C++, Java and Python.
- Three Playwright browser regression tests wired into GitHub Actions.
- New curriculum documentation and release-readiness notes.

## Verification evidence

| Check | Result |
|---|---|
| Python compile | Passed |
| JavaScript syntax | Passed |
| pytest | 73 passed; 3 browser tests skipped locally |
| Collected test cases | 76 |
| Function adapter compile/run | 28 problem-language combinations passed |
| Clean SQLite Alembic migration | Passed |
| GitHub workflow and template YAML | Parsed successfully |
| Strict catalogue audit | 159 records; 0 errors; 0 warnings |
| ZIP integrity | Verified at packaging |

The three browser checks use Chromium and are included in CI. This managed build environment blocks Chromium navigation to localhost with `ERR_BLOCKED_BY_ADMINISTRATOR`, so they are skipped locally; the GitHub Actions job installs Chromium and runs them on its runner.

## Catalogue and infrastructure boundaries

- The catalogue remains at 159 records: 140 third-party metadata/link entries and 19 AlgoForge originals.
- The target of 500 questions (150 Easy / 250 Medium / 100 Hard) is not complete.
- An official Codeforces API dry-run was attempted. Outbound DNS resolution was unavailable, so no catalogue rows were imported or modified. A dry-run failure is not treated as evidence that an import has succeeded.
- The strict audit report is saved at `reports/catalogue-audit-0.8.0.json`.
- Judge0 is still a separately operated service and was not live-tested in this environment.
- Full WCAG 2.2 audit, PostgreSQL deployment test, security review, penetration test, load test, backup/restore drill and production operations remain release gates.

## Database compatibility

No schema change was needed for this release. Learning-path definitions are version-controlled application data, and module completion is derived from existing problem-progress records.
