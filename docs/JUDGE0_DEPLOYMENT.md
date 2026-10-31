# Judge0 CE deployment and security runbook

AlgoForge sends source code and selected stdin to a separate Judge0 service over HTTPS. It never executes student code in the FastAPI process. The judge is a separate, high-risk security boundary and should run on a dedicated Linux host.

## Release and compatibility

The official Judge0 GitHub releases page currently lists **Judge0 CE v1.13.1** as the latest CE release. The release notes date it to 18 April 2024 and include fixes for three security vulnerabilities affecting versions up to v1.13.0. No newer CE release was listed when this runbook was checked on 30 October 2026. That does not by itself guarantee that the project remains actively maintained; assess the release cadence, open security issues and dependency health before operating a public judge.

Official references:

- Releases and deployment procedure: <https://github.com/judge0/judge0/releases>
- API documentation for CE v1.13.1: <https://ce.judge0.com/docs>
- Official `judge0.conf` authentication and dependency settings: <https://github.com/judge0/judge0/blob/master/judge0.conf>
- Project repository: <https://github.com/judge0/judge0>

## 1. Prepare a dedicated Linux host

The official v1.13.1 release says Judge0 has only been tested on Linux and recommends Ubuntu 22.04. It documents the following GRUB configuration for that environment:

1. Edit `/etc/default/grub` as an administrator.
2. Add `systemd.unified_cgroup_hierarchy=0` to the `GRUB_CMDLINE_LINUX` value.
3. Apply the change with `sudo update-grub`.
4. Reboot the host.

Install Docker Engine and Docker Compose using the official Docker instructions for the selected Ubuntu release. Do not assume that a generic Docker-in-Docker container is an equivalent judge host. Check the host kernel, cgroups, CPU and memory capacity, storage capacity and the exact privilege requirements of the selected Judge0 release.

**Isolation warning:** Judge0's worker execution architecture has significant host-level privileges and resource-control requirements. Do not place it on the same host as the production AlgoForge database or other valuable workloads. Do not mount application secrets, database volumes, cloud credentials or private source trees into worker containers. Restrict worker egress and access to internal/private IP ranges, including cloud metadata services.

## 2. Download the official release

Use the upstream release archive, not an unverified third-party image or Compose file:

```bash
curl -fL -o judge0-v1.13.1.zip \
  https://github.com/judge0/judge0/releases/download/v1.13.1/judge0-v1.13.1.zip
unzip judge0-v1.13.1.zip
cd judge0-v1.13.1
```

Read the included release configuration and deployment notes before starting services. Review the archive contents and image tags; do not silently substitute a different branch or tag.

## 3. Configure passwords and API authentication

Generate three different secrets:

```bash
openssl rand -hex 32  # Redis password
openssl rand -hex 32  # PostgreSQL password
openssl rand -hex 32  # Judge0 API authentication token
```

Edit the included `judge0.conf` and set the generated values:

```dotenv
REDIS_PASSWORD=<unique-redis-password>
POSTGRES_PASSWORD=<unique-postgres-password>
AUTHN_HEADER=X-Auth-Token
AUTHN_TOKEN=<unique-judge0-api-token>
```

`AUTHN_HEADER` and `AUTHN_TOKEN` enable Judge0 API authentication. The default header is `X-Auth-Token`; the token must be sent in the HTTP header on every call. Do not put tokens in URLs, logs, browser code or source control. The PostgreSQL and Redis credentials must be unique and must not be reused from AlgoForge.

Keep an encrypted copy of the configuration in your secret manager. The AlgoForge app needs only the API token and the HTTPS URL; it should not know the Judge0 database or Redis passwords.

## 4. Start Judge0

Follow the release's documented startup sequence:

```bash
docker-compose up -d db redis
sleep 10s
docker-compose up -d
sleep 5s
docker-compose ps
```

The upstream instructions expose the API on port `2358` and its Swagger UI at `/docs`. Do not leave that port open to the public internet. Bind it to a private interface or firewall it so only the AlgoForge backend host or a trusted private ingress can reach it. Terminate TLS at a trusted reverse proxy and use a valid certificate. The app must connect to the HTTPS URL, not the raw public `http://host:2358` endpoint.

The upstream deployment may use privileged worker services. Restrict host access, SSH access, inbound firewall rules, worker egress and access to the Docker socket. Keep Judge0 and its compiler images patched; test upgrades on a disposable environment first.

## 5. Configure AlgoForge

Set the following only in the server-side `.env` or secret manager for the AlgoForge API:

```dotenv
JUDGE0_URL=https://judge.internal.example
JUDGE0_TOKEN=<same-token-as-Judge0-AUTHN_TOKEN>
JUDGE0_LANGUAGE_C=103
JUDGE0_LANGUAGE_CPP=105
JUDGE0_LANGUAGE_JAVA=91
JUDGE0_LANGUAGE_PYTHON=109
JUDGE0_TIMEOUT_SECONDS=25
```

The language IDs above are convenience defaults taken from the public CE v1.13.1 language list. Language IDs can differ in another Judge0 distribution or after configuration changes. Verify `GET /languages` against **your own instance** and update the four IDs before accepting submissions.

Restart AlgoForge and verify its health endpoint:

```bash
curl https://your-algoforge-host.example/api/judge/health
```

Then test one small, trusted program in each language. Confirm authenticated access, compilation, output comparison, timeouts, memory limits, concurrency, queue behavior and cleanup. Include deliberate infinite-loop and oversized-output tests in an isolated staging environment.

AlgoForge production startup fails closed unless it has PostgreSQL, HTTPS `PUBLIC_BASE_URL`, password-authenticated Redis, an HTTPS private/contracted Judge0 URL, and `JUDGE0_TOKEN`. The public shared endpoint `ce.judge0.com` is rejected in production mode.

## 6. Workload limits and operations

AlgoForge currently requests these per-test-case limits from Judge0:

- CPU time: 2 seconds plus 1 second extra allowance.
- Wall-clock time: 5 seconds.
- Memory: 128,000 KB.
- Stack: 64,000 KB.
- Process/thread count: 30.

These are request-side limits, not a complete host security policy. Before public use, also configure maximum source size, maximum batch size, per-user submission limits, per-user concurrency, queue-depth limits, worker count, storage quotas, network egress restrictions, abuse alerts and billing alerts. Review the exact options supported by the installed release.

Monitor queue depth and wait time, worker crashes, API error rates, CPU and memory pressure, disk capacity, unexpected network traffic, authentication failures and submission bursts. Set retention periods for source code, stdin, stdout and stderr. Keep a backup/restore procedure for Judge0's own database where relevant, and maintain a tested rollback plan.

## 7. Development endpoint and privacy

The `.env.example` uses the public shared CE endpoint solely as a local development convenience. Code and stdin submitted through that configuration are sent from the AlgoForge backend to a third-party service. Do not submit credentials, private source code or sensitive data to the shared endpoint. Its uptime, rate limits, data handling and language versions are not controlled by AlgoForge.

For public production, use an isolated self-hosted Judge0 installation or a contracted managed service with an appropriate security and data-processing agreement. A working `/api/judge/health` response alone is not a security review or proof that all compiler versions work correctly.
