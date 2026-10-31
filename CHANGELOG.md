# Changelog

## 0.4.0 — 31 October 2026

### Coding workspace
- Added LeetCode-style method signatures and trusted input/output harnesses for Running Sum, Maximum Pair Sum, Binary Search Index and Missing Number across C, C++, Java and Python.
- Added editable custom test rows with optional expected outputs and per-case result, output, diagnostic, runtime and memory details.
- Added resizable problem/editor panes with pointer drag, keyboard controls, responsive stacking and remembered width.
- Added local and account-synchronised code autosave, up to 30 server-side draft snapshots and restore controls.

### DSA analytics
- Added account-derived Total Active Days and Contributions metrics.
- Added weekly reports and previous-week comparison, 7/14-day consistency, pattern/topic mastery, weak-pattern/topic detection, recommendations and a caveated completion-pace estimate.
- Avoided seeded/example numbers; the dashboard displays each user's actual recorded activity.

### Verification
- 47 automated tests pass locally.
- 16 C/C++/Java/Python function-harness combinations were compiled and executed against sample fixtures.
- A clean SQLite Alembic migration chain completed and created 20 tables.
- Frontend JavaScript syntax check and Python compile checks pass.

### Remaining before production
- Deploy and live-test a private isolated Judge0 service.
- Run the full question metadata import from a network-enabled environment.
- Complete independent security, load, backup/restore and public deployment validation.
