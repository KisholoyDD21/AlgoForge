# Security policy

## Supported deployment state

AlgoForge is a development-stage project. A passing test suite is not a security certification. Do not expose a deployment to public users until the production checklist in `IMPLEMENTATION_STATUS.md` has been completed and an independent security review has been performed.

## Reporting a vulnerability

Do not disclose a vulnerability in a public issue before the maintainer has had an opportunity to investigate. Use GitHub's **Report a vulnerability** flow (private vulnerability reporting / Security Advisories) on the repository where this project is hosted. If private reporting is not enabled, contact the repository owner privately through the contact method listed in that repository's profile.

Include the affected version/commit, deployment conditions, impact, and minimal reproduction steps. Do not include real user data, production tokens, or other secrets in a report.

## High-risk components

- User code is sent to the configured Judge0 service. Never execute it inside the AlgoForge API container.
- Judge0 should run on an isolated Linux host with network egress restrictions, resource limits and authenticated API access.
- Keep Judge0 tokens, database passwords, Redis passwords, session secrets and bootstrap credentials out of the browser and source control.
- Use HTTPS for all production traffic and a password-protected Redis service.
- Keep the application, base images, Python dependencies, operating system and compiler images patched.
- Back up production data securely and test restoration.

## Before reporting closure

A fix should include a regression test where practical, a description of affected versions, any required data/configuration migration, and steps for operators to deploy the fix.
