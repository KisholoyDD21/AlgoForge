# Contributing to AlgoForge

## Local setup

Use Python 3.11+ (the container image uses Python 3.12), create a virtual environment, install `requirements-dev.txt`, copy `.env.example` to `.env`, run `alembic upgrade head`, and start the app with `uvicorn app.main:app --reload --port 8000`.

## Before opening a pull request

Run:

```bash
python -m compileall -q app scripts migrations
pytest -q
node --check app/static/app.js
```

For schema changes, add an Alembic migration and test it against a clean database. For backend behavior, add an API or unit test. For frontend changes, verify keyboard use and desktop/mobile layouts.

## Content and licensing

Do not commit third-party problem statements, samples, editorials, solutions, hidden tests, logos or other assets without permission. Keep canonical source URLs, provenance and license information for imported metadata. Prefer original AlgoForge problem statements and judge cases when a fully graded experience is needed.

## Security-sensitive changes

Do not add shell execution to the web API. Do not expose secrets to frontend code. Do not disable role checks, resource limits, hidden-test protections or rate limits to make a feature easier to implement. Review `SECURITY.md` and `docs/JUDGE0_DEPLOYMENT.md` before changing the judge boundary.
