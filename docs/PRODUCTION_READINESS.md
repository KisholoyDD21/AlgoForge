# Production readiness and assurance plan

**Status:** Not production-certified. This document records the evidence required before opening a public multi-user service.

## Release gates

### Gate A — Application correctness
- [x] Automated backend tests run locally.
- [x] Fresh SQLite migration is exercised in CI.
- [x] Frontend JavaScript syntax is checked in CI.
- [x] Add Playwright browser checks for learning-path rendering, navigation landmarks, theme persistence, mobile overflow and function-mode workspace controls (execution in this managed environment is blocked; CI installs Chromium).
- [ ] Extend browser tests to cover registration, a successful full-suite submission and the contest journey.
- [ ] Add migration test against the supported PostgreSQL version.
- [ ] Add restore-from-backup test and migration rollback/recovery procedure.

### Gate B — Judge safety and correctness
- [x] Web API delegates code execution to a separate Judge0-compatible service.
- [x] Private test cases are not returned in normal API responses.
- [ ] Deploy a dedicated authenticated judge service.
- [ ] Verify all configured language IDs and compiler versions against that deployment.
- [ ] Verify C, C++, Java and Python accepted/wrong-answer/compile-error/runtime-error/timeout/memory-limit cases live.
- [ ] Validate kernel/cgroup/container restrictions, non-root workers, read-only filesystem, process limits, no network egress and cleanup behavior.
- [ ] Load-test concurrent submissions and queue saturation.
- [ ] Set per-account and global execution quotas and cost alerts.

### Gate C — Security assurance
- [x] Production configuration has fail-closed checks for critical dependencies and HTTPS judge configuration.
- [x] Secrets are configured server-side and `.env` is ignored by Git.
- [ ] Complete a scoped OWASP ASVS 5.0.0 verification plan and record evidence.
- [ ] Run dependency and container image vulnerability scans.
- [ ] Review authentication/session lifecycle, CSRF, CORS, CSP, IDOR and account deletion.
- [ ] Conduct independent penetration testing before public launch.
- [ ] Document incident response, key rotation and breach notification process.

### Gate D — Operations and reliability
- [ ] Configure production domain, TLS, HSTS and secure cookie settings.
- [ ] Configure structured logs, metrics, tracing and alerting without logging source code or secrets unnecessarily.
- [ ] Configure automated encrypted database backups and test restoration.
- [ ] Add health/readiness probes for database, Redis and judge dependencies.
- [ ] Define deployment, rollback, incident and on-call procedures.
- [ ] Perform load and soak testing with a stated traffic target.
- [ ] Define retention/deletion policies and operational ownership.

### Gate E — Product, accessibility and legal
- [ ] Run manual WCAG 2.2 accessibility review with keyboard and screen reader.
- [ ] Run Lighthouse and capture production Core Web Vitals; do not claim a score before measurement.
- [ ] Review all imported problem records, source links and licence/provenance metadata.
- [ ] Complete privacy policy and terms with real operator identity, processors, retention and jurisdiction details.
- [ ] Provide account export/deletion and support contact workflows.
- [ ] Clearly label self-reported external solves and heuristic predictions.

## Release rule

Do not describe AlgoForge as production-ready until all applicable release gates have evidence attached to a tagged release. A passing unit-test suite or a successful local Docker start is necessary but not sufficient.


## 0.8.0 product scope notes

- Four guided DSA tracks now resolve modules to actual catalogue items, calculate account progress from recorded problem status and apply a 60% prerequisite threshold. See [learning-path design](LEARNING_PATHS.md).
- Seven original questions now have verified function-style adapters across C, C++, Java and Python. Other original questions continue to use standard input/output.
- The catalogue remains 159 entries. Learning-path modules with insufficient matching questions are marked as catalogue gaps; completing the learning-path engine does not mean the 500-question target is complete.
- The 0.8.0 automated suite contains 76 collected tests (73 passed locally; three Chromium browser checks are skipped by the managed local environment). This is not a substitute for an external security review, production judge deployment, browser accessibility audit or load test.
