# AlgoForge

**AlgoForge 0.4.0** is an independent, pattern-first DSA practice platform. It combines a multi-platform metadata catalogue with original AlgoForge exercises, an isolated code-judging integration, learning roadmaps, progress tracking and scheduled practice contests.

This repository is a production-oriented application foundation, not a claim that a public service has already been deployed or that every third-party platform feature is replicated. Read [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) before launch.

## Current contents

See [CHANGELOG.md](CHANGELOG.md) for the 0.4.0 release changes and [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for tested features versus remaining launch requirements.

- Responsive desktop/mobile interface, dark/light theme, landing page, dashboard, problem explorer, patterns, roadmaps, playground, submissions, bookmarks, profile, contests, problem discussions, moderation console and draft legal pages.
- FastAPI + SQLAlchemy backend with local SQLite and production PostgreSQL configuration.
- Account registration/login, scrypt password hashes, HTTP-only session cookies, expiry and role checks.
- User profile/timezone, progress, bookmarks, personal notes, submissions and daily activity/streak persistence.
- A **159-record initial catalogue**: 140 metadata-only third-party links across LeetCode, CSES, Codeforces, HackerRank, AtCoder and CodeChef, plus 19 original AlgoForge problems.
- **77 platform-owned test cases** for the 19 original problems. Full hidden inputs/outputs remain private; only marked sample test output can be returned to a learner.
- Full-test-suite verdict workflow for original problems through a separate Judge0 CE-compatible service: Accepted, Wrong Answer, compilation/runtime/time-limit errors and measured time/memory.
- Professional problem workspace with Monaco editor, resizable statement/editor panes, custom test cases, per-case result cards, one-click full-suite submissions, and C/C++/Java/Python support.
- Code autosave to browser storage for guests and account-synchronised drafts for signed-in learners, with up to 30 previous snapshots and restore controls.
- Function-signature execution mode for four AlgoForge-original problems (Running Sum, Maximum Pair Sum, Binary Search Index and Missing Number) in C, C++, Java and Python; other original problems retain their documented stdin/stdout interface until their signatures are configured.
- Advanced DSA analytics: total active days, contribution counts, pattern and topic mastery, attempted weak areas, last-seven-day reports with previous-week comparison, 7/14-day consistency and practice recommendations.
- A simple learning-completion projection based on the last 14 days of recorded completions. It is a trend estimate, not a guarantee; externally self-reported completions may contribute to this metric.
- Complexity feedback that separates a low-confidence static estimate, expected approach complexity and Judge0's measured execution metrics.
- Scheduled contests with registration, server-side start/end enforcement, problem release at start and scoring/penalty leaderboard.
- Admin-protected original-problem create/update/delete operations. Existing problems with submissions, contest references or learner progress cannot be deleted; problems with submissions cannot have their judging suite rewritten.
- Daily challenge, achievements, profile timezone, bookmarks and personal notes.
- Authenticated problem threads, replies, voting, reporting, author deletion and admin hide/unhide moderation.
- Account deletion explicitly removes the user's community content and all children attached to threads they authored.
- Redis-backed shared rate limiting in production; development fallback is process-local.
- PostgreSQL, Redis and optional Caddy HTTPS Compose services, migrations, CI tests and operational documentation.

## Quick start: Windows PowerShell

Requirements: Python 3.11+ (Python 3.12 is used in the Docker image).

```powershell
# Extract the ZIP, open the algoforge folder in VS Code, then run:
.\run_local.ps1

# Or use the manual commands below when you want to manage the environment yourself:
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open <http://localhost:8000>. In development only, a demo account is created automatically:

```text
Email:    demo@algoforge.dev
Password: demo-pass-123
```

Never use the demo account or development cookie settings in production. The demo account is not created when `APP_ENV=production`.

## Quick start: Docker Compose

Set strong URL-safe `POSTGRES_PASSWORD` and `REDIS_PASSWORD` values in `.env` (separate long random hex values are suitable), then run:

```bash
docker compose up --build -d
```

The local Compose stack starts the application, PostgreSQL and password-protected Redis. The web container is published on `127.0.0.1:8000`; it is not directly exposed on every network interface. Open <http://localhost:8000>.

## The question catalogue and 500-question target

The initial database seed contains 159 records:

| Source | Records | Content treatment |
|---|---:|---|
| LeetCode | 102 | Metadata and official links only |
| CSES | 16 | Metadata and official links only |
| Codeforces | 10 | Metadata and official links only |
| HackerRank | 5 | Metadata and official links only |
| AtCoder | 4 | Metadata and official links only |
| CodeChef | 3 | Metadata and official links only |
| AlgoForge Originals | 19 | Original statements and platform-owned test cases |
| **Total** | **159** | |

The target overall catalogue is **150 Easy / 250 Medium / 100 Hard (500 total)**. The current seeded distribution is 59 Easy / 79 Medium / 21 Hard. The importer fills the shortfall using rating/tag metadata from the official Codeforces `problemset.problems` API; it does not copy problem statements, examples, editorials or private tests.

Run from a machine with outbound HTTPS access to Codeforces:

```bash
python scripts/import_codeforces.py
```

For Docker:

```bash
docker compose exec web python scripts/import_codeforces.py
```

The importer is safe to rerun and skips existing slugs. It exits with a non-zero status if the official API is unreachable. Ratings are mapped into AlgoForge's own difficulty buckets: Easy up to 1100, Medium 1101–1800 and Hard above 1800. These are product-side classifications, not equivalent to another platform's difficulty labels. The importer uses a single public API request; Codeforces' published API guidance should be checked before expanding or scheduling repeated imports.

**Important:** The 500 target is a metadata discovery set, not 500 problems with rehosted statements or AlgoForge hidden tests. Official problem statements and judging remain on the source sites unless AlgoForge has explicit rights to host them. Read [docs/DATA_LICENSING.md](docs/DATA_LICENSING.md).

## Professional coding workspace

Open an AlgoForge-original problem to use the split problem/editor workspace. The splitter can be dragged with a mouse or adjusted with the arrow keys; Home and End move to the minimum and maximum panel widths. The width is remembered in local storage on that browser.

Four original problems currently provide function-style interfaces in all four supported languages:

| Problem | C++ / Java / Python / C method |
|---|---|
| Running Sum | `runningSum` |
| Maximum Pair Sum | `maxPairSum` |
| Binary Search Index | `search` |
| Missing Number | `missingNumber` |

Each signature has a trusted input/output adapter which is appended server-side. The adapters are explicit and problem-specific; other originals and metadata-only external problems use standard input/output mode. Custom test cases may include an optional expected output. When supplied, each case is compared and displayed individually; without an expected output it is shown as executed, not passed. Full private-suite submission is a separate action and is the only way to earn an AlgoForge Accepted verdict.

Code is autosaved locally for guests and synchronised to a user-scoped draft for signed-in users. The History button lists snapshots and allows restoration. Signed-in snapshots are capped at 30 per draft. Do not store passwords, API keys or other secrets in draft code.

## Advanced DSA analytics

The Analytics page uses actual account records rather than sample values:

- **Total Active Days:** distinct local calendar dates with at least one recorded solved contribution.
- **Contributions:** total newly recorded problem completions across those dates. Repeatedly opening or resubmitting an already-solved problem does not inflate this count.
- Pattern/topic mastery: solved problems divided by all catalogue entries with that tag.
- Weak patterns and topics: only attempted categories below the 60% mastery threshold are flagged; untouched categories are not mislabelled as weak.
- Weekly report and 7/14-day consistency: derived from per-day activity rows, with the current seven-day period compared to the previous seven days.
- Recommendations: unfinished questions prioritised toward weak patterns and accessible difficulty.
- Learning prediction: a simple 14-day solve-velocity estimate, not a guarantee or AI forecast.

The UI intentionally does not hardcode an example like `238` active days or `203` contributions. Those totals belong to each account and will start low for a new account, then increase from recorded activity. External-platform completions are self-reported; original-platform completions are recorded only after an Accepted AlgoForge judge verdict.

## Enable code execution and problem judging

The application never executes submitted code in the FastAPI process. The development `.env.example` points to the shared Judge0 CE endpoint for convenience. This is subject to third-party rate limits and availability. For production, deploy a separate private Judge0 CE-compatible service and set these values in `.env`:

```dotenv
JUDGE0_URL=https://your-private-judge-host.example
JUDGE0_TOKEN=your-server-side-token
JUDGE0_LANGUAGE_C=103
JUDGE0_LANGUAGE_CPP=105
JUDGE0_LANGUAGE_JAVA=91
JUDGE0_LANGUAGE_PYTHON=109
JUDGE0_TIMEOUT_SECONDS=25
```

Language IDs depend on the exact Judge0 deployment. These defaults match the public Judge0 CE v1.13.1 language listing checked on 30 October 2026 (C 103, C++ 105, Java 91, Python 109); **verify `/languages` on your own judge before accepting submissions**. Production startup also requires `JUDGE0_TOKEN` and a Judge0 instance configured with `AUTHN_HEADER=X-Auth-Token` / `AUTHN_TOKEN`. The application exposes:

- `GET /api/judge/health`
- `GET /api/judge/languages`

The API sends per-case CPU, wall-time, memory, stack and process limits. It creates asynchronous submissions, polls results and returns only sample stdout/stderr. Hidden case input/output is never included in public problem APIs or student responses.

When you copy `.env.example`, the playground can use the shared CE endpoint for development after checking that your local server can reach it. Do not use that public endpoint for a public production platform. The initial catalogue's third-party records are not judgeable on AlgoForge. Only original AlgoForge problems have owned test suites and can return a genuine AlgoForge Accepted verdict. Function-style mode is currently configured for Running Sum, Maximum Pair Sum, Binary Search Index and Missing Number; other original problems use stdin/stdout. A custom test run with no expected output is an execution result, not a judged pass, and never awards a solved mark.

**Production rule:** Deploy Judge0 on a dedicated, isolated Linux host or secured private environment. Restrict network access so untrusted code cannot reach the AlgoForge API, PostgreSQL, Redis, cloud metadata services or the public internet. Do not treat the public Judge0 CE endpoint as a production SLA or a security boundary under your control. Review the official deployment guide in [docs/JUDGE0_DEPLOYMENT.md](docs/JUDGE0_DEPLOYMENT.md).

## Production deployment on a VPS

This Compose setup expects a Linux VPS with Docker Engine and Docker Compose v2. It is not a one-click managed hosting deploy.

1. Point a DNS A/AAAA record for your domain to the VPS and allow inbound TCP 80/443.
2. Set the production values in `.env`. Use separate random secrets for PostgreSQL, Redis and Judge0; production startup rejects an unauthenticated Redis URL or a Judge0 URL without a server-side API token:

```dotenv
APP_ENV=production
POSTGRES_PASSWORD=long-random-url-safe-secret
PUBLIC_DOMAIN=practice.example.com
PUBLIC_BASE_URL=https://practice.example.com
COOKIE_SECURE=true
BOOTSTRAP_ADMIN_EMAIL=admin@example.com
BOOTSTRAP_ADMIN_PASSWORD=a-long-unique-password
JUDGE0_URL=https://your-private-judge-host.example
JUDGE0_TOKEN=server-side-token
REDIS_PASSWORD=separate-long-random-secret
```

3. Set the four `JUDGE0_LANGUAGE_*` values for the deployed judge.
4. Start the app, database, Redis and Caddy reverse proxy:

```bash
docker compose --profile production up --build -d
```

5. Sign in with the bootstrap admin, confirm `/api/judge/health`, create and test one original problem, and then remove `BOOTSTRAP_ADMIN_PASSWORD` from the environment and restart the web service. Keep the admin credentials in a secret manager, not in Git.
6. Configure managed backups for PostgreSQL and a separate backup/restore drill. Monitor Judge0 workers, queue depth, CPU/memory saturation, web errors and Redis health.

Caddy obtains and renews certificates automatically when DNS and ports are configured correctly. The Compose web port remains loopback-only; Caddy proxies through the internal Compose network. Review proxy trust and network access before putting the host behind another CDN or load balancer.

## Admin operations

Create the first admin through environment variables before startup (`BOOTSTRAP_ADMIN_EMAIL` and `BOOTSTRAP_ADMIN_PASSWORD`). Admin endpoints require the admin role.

- `GET /api/admin/summary`
- `GET /api/admin/problems`
- `POST /api/admin/problems`
- `PUT /api/admin/problems/{slug}`
- `DELETE /api/admin/problems/{slug}`
- `POST /api/admin/contests`

Problem authoring requires a full statement, at least two test cases, and at least one sample case. Test case inputs and expected outputs are private except for cases explicitly marked `sample: true`. Once a problem has submissions, updating its judge suite is blocked to preserve historical verdict integrity.

## Useful commands

```bash
# Apply schema migrations
alembic upgrade head

# Run tests
pytest -q

# Static checks
python -m compileall -q app scripts migrations
node --check app/static/app.js

# API health and Judge0 integration checks
curl http://localhost:8000/api/health
curl http://localhost:8000/api/judge/health
curl http://localhost:8000/api/judge/languages

# Expand the metadata catalogue
python scripts/import_codeforces.py
```

## Project structure

```text
algoforge/
├── app/
│   ├── main.py                 # FastAPI APIs, models, auth, Judge0 orchestration
│   ├── native_problems.py      # 19 original problems and 77 private/sample cases
│   ├── seed_data.py            # 140 third-party metadata records
│   └── static/                 # Single-page frontend, design system, images and favicon
├── deploy/
│   ├── Caddyfile
│   └── JUDGE0_DEPLOYMENT.md
├── docs/                       # Research, platform comparison and data licensing
├── migrations/                 # Alembic migrations
├── scripts/                    # Codeforces metadata importer
├── tests/                       # API, auth, importer, judging, contest, analytics, drafts and compiled language harness tests
├── Dockerfile
├── run_local.ps1              # One-command Windows local setup and launch
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
└── .env.example
```

## API overview

- Authentication: `/api/auth/register`, `/api/auth/login`, `/api/auth/logout`, `/api/me`
- Catalogue: `/api/problems`, `/api/problems/{slug}`, `/api/platforms`, `/api/patterns`, `/api/roadmaps`
- User data: `/api/dashboard`, `/api/analytics`, `/api/achievements`, `/api/daily-challenge`, `/api/problems/{slug}/progress`, `/bookmark`, `/note`
- Drafts: `/api/drafts/{problem_key}/{language}`, `/versions`, `/restore`
- Playground: `/api/run`, `/api/run/{submission_id}`
- Problem judging: `/api/problems/{slug}/submit`, `/api/problems/{slug}/run-custom`, `/api/submissions/{id}/judge`
- Contests: `/api/contests`, `/api/contests/{slug}`, `/register`, `/leaderboard`
- Community: `/api/problems/{slug}/discussions`, `/api/discussions/{id}/comments`, `/vote`, `/report`
- Admin: `/api/admin/summary`, `/api/admin/problems`, `/api/admin/contests`, `/api/admin/discussion-reports`, `/api/admin/discussions/{id}/moderate`
- Operations: `/api/health`, `/api/judge/health`, `/api/judge/languages`
- SEO: `/robots.txt`, `/sitemap.xml`

Interactive API documentation is available at `/api/docs` in development only. Public landing/legal pages are server-delivered, while most signed-in views are a client-rendered single-page application; this is **not full per-route server-side rendering**.

## Known launch requirements

See [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md). In particular, this build has not had a live Judge0 integration test, real-world load test, independent security assessment or public-domain deployment. Email verification, password recovery, OAuth, notifications, external platform account sync, third-party analytics, fully server-rendered routes, broader 301 migration rules and legal review remain deployment/product work. Basic problem discussions, replies, votes, reports and admin moderation are implemented; advanced social features are not. Do not describe these as operational until implemented and tested.
