# Architecture decisions

## ADR-001: Keep the current modular monolith for the MVP

**Status:** Accepted  
**Decision:** Keep FastAPI as a modular monolith with SQLAlchemy and a relational database. Avoid splitting users, analytics, contests and discussions into microservices until measured scaling or team ownership justifies it.

**Reasoning:** The current product is a small, evolving application. A modular monolith keeps local setup, migrations, testing and deployment tractable. The online judge remains a separate service because untrusted code execution has a fundamentally different security boundary and scaling profile.

## ADR-002: Separate web application from arbitrary code execution

**Status:** Accepted  
**Decision:** Never compile or execute learner source code inside the FastAPI process/container. Submit to an authenticated, separately deployed Judge0-compatible service.

**Reasoning:** User submissions are hostile input. A separate execution system allows resource constraints, sandboxing, isolation, worker scaling and independent operational monitoring. The API's job is authentication, orchestration, verdict aggregation and persistence.

## ADR-003: Distinguish metadata discovery from native judging

**Status:** Accepted  
**Decision:** Third-party problem entries are source-linked discovery records unless explicit permission and a valid test suite exist. Only AlgoForge-owned or properly licensed problems can receive a native AlgoForge Accepted verdict.

**Reasoning:** Platform terms, copyright and database rights differ. Public visibility does not equal redistribution permission. This avoids false claims about question ownership or official verdicts.

## ADR-004: Keep measured metrics separate from algorithmic complexity

**Status:** Accepted  
**Decision:** Display expected algorithm complexity, heuristic source estimate and measured runtime/memory as distinct values.

**Reasoning:** A single execution cannot prove Big-O. Timing varies with machine, compiler, input and system load. Heuristic static analysis is not a formal proof.

## ADR-005: Keep the lightweight SPA until a migration is justified

**Status:** Accepted  
**Decision:** Retain the current FastAPI-served static SPA for this release. Reconsider Next.js/SSR if public content SEO, route-level metadata, rendering performance or team workflow demonstrates a measurable need.

**Reasoning:** A framework migration adds dependencies and operational complexity. The current application is functional as a local web app; product quality and judge reliability have higher immediate value than a framework rewrite.
