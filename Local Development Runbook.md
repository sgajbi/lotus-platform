# Local Development Runbook (Docker, Bash)

- Last updated: 2026-02-24
- Scope: run `lotus-advise` + `lotus-gateway` + `lotus-workbench` together with Docker, run `lotus-core` and `lotus-report` standalone when needed, and keep standardized local gates for `lotus-performance`
- Current phase: lotus-manage-first UI/lotus-gateway workflows with lotus-core integration and lotus-performance baseline hardening

## 1. Prerequisites

```bash
docker --version
docker compose version
git --version
```

Expected:
- Docker Engine must be running.
- Use Git Bash (commands below are Bash format).

## 1.1 Centralized Full-Platform Compose (Recommended)

Canonical centralized orchestration now lives in:
- `lotus-platform/platform-stack/docker-compose.yml`

Canonical service identities for local `dev`:

- Workbench: `http://workbench.dev.lotus`
- Gateway: `http://gateway.dev.lotus`
- Manage: `http://manage.dev.lotus`
- Performance: `http://performance.dev.lotus`
- Report: `http://report.dev.lotus`
- Core query: `http://core-query.dev.lotus`
- Core control-plane: `http://core-control.dev.lotus`
- Core ingestion: `http://core-ingestion.dev.lotus`

Ports remain an internal platform-stack implementation detail. Operator and application-facing
configuration should use the environment-scoped hostnames above. Direct host-port publishing is a
debug-only override, not the default contract.

Required hosts-file entries are listed in:

- `platform-stack/dev-ingress/hosts.example`

DNS / hostname setup rule:

- local `*.dev.lotus` names are resolved through the Windows hosts file, not public DNS
- `platform-stack/dev-ingress/hosts.example` is the source of truth for the required mappings
- all browser, operator, and cross-app examples in this runbook assume those hostnames resolve locally before the stack is started

Preview the managed hosts-file block:

```powershell
cd C:\Users\Sandeep\projects\lotus-platform
powershell -ExecutionPolicy Bypass -File automation/Sync-Dev-Ingress-Hosts.ps1
```

Apply the managed block to the Windows hosts file:

```powershell
cd C:\Users\Sandeep\projects\lotus-platform
powershell -ExecutionPolicy Bypass -File automation/Sync-Dev-Ingress-Hosts.ps1 -Apply
```

If the apply step is not run from an elevated shell, the tool writes a staged file instead:

- `output/hosts-preview/hosts.merged`

Use that staged file only as an admin handoff artifact. Do not copy partial entries manually.

### 1.1.1 platform-stack .env setup

Before first bring-up, copy `.env.example` and set the repo paths to the local Lotus clones that
this machine should orchestrate:

```powershell
cd C:\Users\Sandeep\projects\lotus-platform\platform-stack
Copy-Item .env.example .env
```

Minimum required path variables:

- `LOTUS_CORE_REPO_PATH`
- `LOTUS_PERFORMANCE_REPO_PATH`
- `LOTUS_REPORT_REPO_PATH`
- `LOTUS_MANAGE_REPO_PATH`
- `BFF_REPO_PATH`
- `UI_REPO_PATH`

Example local values:

- `LOTUS_CORE_REPO_PATH=C:\Users\Sandeep\projects\lotus-core`
- `LOTUS_PERFORMANCE_REPO_PATH=C:\Users\Sandeep\projects\lotus-performance`
- `LOTUS_REPORT_REPO_PATH=C:\Users\Sandeep\projects\lotus-report`
- `LOTUS_MANAGE_REPO_PATH=C:\Users\Sandeep\projects\lotus-manage`
- `BFF_REPO_PATH=C:\Users\Sandeep\projects\lotus-gateway`
- `UI_REPO_PATH=C:\Users\Sandeep\projects\lotus-workbench`

### 1.1.2 Bring up ingress-first platform-stack

Run end-to-end stack (lotus-core, lotus-performance, lotus-manage, lotus-report, lotus-gateway, UI + observability):

```powershell
cd C:\Users\Sandeep\projects\lotus-platform\platform-stack
docker compose up -d --build
docker compose ps
```

Key endpoints:
- Workbench: `http://workbench.dev.lotus`
- Gateway: `http://gateway.dev.lotus`
- Core query: `http://core-query.dev.lotus`
- Core ingestion: `http://core-ingestion.dev.lotus`
- Manage: `http://manage.dev.lotus`
- Performance: `http://performance.dev.lotus`
- Report: `http://report.dev.lotus`
- Prometheus: `http://prometheus.dev.lotus`
- Grafana: `http://grafana.dev.lotus`

### 1.1.3 Verify DNS and ingress before app debugging

Run this operator loop in order:

```powershell
cd C:\Users\Sandeep\projects\lotus-platform
powershell -ExecutionPolicy Bypass -File automation/Validate-Dev-Ingress-Smoke.ps1
powershell -ExecutionPolicy Bypass -File automation/Explain-Dev-Ingress-Status.ps1
```

Interpretation:

- `dns_not_configured`
  - hosts-file mappings are missing or not yet applied
- `ingress_unreachable`
  - `dev-ingress` is not serving; bring up `dev-ingress` first
- `services_unreachable`
  - edge routing is working; refresh only the named downstream services
- `ready`
  - canonical hostnames are live and routing correctly

### 1.1.4 Direct-host ingress fallback for mixed local bring-up

Use this only when you are not running full `platform-stack`, for example when:

- `lotus-core` is running from its own repo compose
- `lotus-performance` is running from its own repo compose
- `lotus-gateway` and `lotus-workbench` are running as direct local processes

In that case, start a minimal ingress that proxies the canonical hostnames to the direct local
ports using:

- `platform-stack/dev-ingress/Caddyfile.direct-host`

This is the supported fallback when you need canonical `*.dev.lotus` URLs without handing full app
ownership to `platform-stack`.

## 2. Service Identities and Dependencies

- lotus-manage API: `http://manage.dev.lotus`
- lotus-core query API: `http://core-query.dev.lotus`
- lotus-core control-plane API: `http://core-control.dev.lotus`
- lotus-core ingestion API: `http://core-ingestion.dev.lotus`
- lotus-performance API: `http://performance.dev.lotus`
- lotus-report API: `http://report.dev.lotus`
- lotus-gateway API: `http://gateway.dev.lotus`
- UI: `http://workbench.dev.lotus`

Legacy direct host ports are available only through `platform-stack/docker-compose.host-ports.yml`
when a debugging workflow genuinely requires them.

Dependency chain:
- UI -> lotus-gateway
- lotus-gateway -> lotus-manage
- lotus-gateway -> lotus-core API surfaces
- lotus-gateway/UI -> lotus-report (reporting and aggregation views)
- lotus-manage -> Postgres (via its compose file)

## 3. One-Time Pull

```bash
cd /c/Users/sande/dev/lotus-advise && git checkout main && git pull --ff-only
cd /c/Users/sande/dev/lotus-gateway && git checkout main && git pull --ff-only
cd /c/Users/sande/dev/lotus-workbench && git checkout main && git pull --ff-only
```

## 4. Start All 3 Apps (Docker)

Run these in 3 separate Git Bash terminals.

## 4.1 Start lotus-manage (+ Postgres)

```bash
cd /c/Users/sande/dev/lotus-advise
docker compose up -d --build
docker compose ps
```

## 4.2 Start lotus-gateway

```bash
cd /c/Users/sande/dev/lotus-gateway
export DECISIONING_SERVICE_BASE_URL="http://manage.dev.lotus"
export PORTFOLIO_DATA_INGESTION_BASE_URL="http://core-ingestion.dev.lotus"
export PORTFOLIO_DATA_PLATFORM_BASE_URL="http://core-query.dev.lotus"
docker compose up -d --build
docker compose ps
```

If you explicitly need raw host ports for debugging:

```powershell
cd C:\Users\Sandeep\projects\lotus-platform\platform-stack
docker compose -f docker-compose.yml -f docker-compose.host-ports.yml up -d --build
docker compose ps
```

Run ingress-first smoke validation:

  ```powershell
  cd C:\Users\Sandeep\projects\lotus-platform
  powershell -ExecutionPolicy Bypass -File automation/Validate-Dev-Ingress-Smoke.ps1
  ```

  Explain the current ingress rollout state and the next required operator step:

  ```powershell
  cd C:\Users\Sandeep\projects\lotus-platform
  powershell -ExecutionPolicy Bypass -File automation/Explain-Dev-Ingress-Status.ps1
  ```

  When only routed services are unhealthy, this command now tells you the exact `docker compose up -d ...` refresh command to run for the affected services.
  When the edge itself is likely down, it tells you to run `docker compose up -d dev-ingress` first.
  The smoke artifact posture vocabulary is:
  `dns_resolution_failed`, `http_error`, `connection_refused`, `timeout`, `transport_error`.
  For `http_error` and `timeout`, it now tells you to inspect `docker compose logs --tail=200 ...` for the affected services before refresh.

Important:

- if you are using full `platform-stack`, do not also run a separate direct-host ingress on port `80`
- if you are using mixed standalone services, do not expect `workbench.dev.lotus` or `gateway.dev.lotus` to work until some ingress layer is listening on port `80`

## 4.3 Start UI

```bash
cd /c/Users/sande/dev/lotus-workbench
export BFF_BASE_URL="http://gateway.dev.lotus"
docker compose up -d --build
docker compose ps
```

## 5. Smoke Checks

```bash
curl -sSf http://manage.dev.lotus/docs >/dev/null && echo "manage ok"
curl -sSf http://gateway.dev.lotus/health >/dev/null && echo "gateway ok"
curl -sSf http://workbench.dev.lotus >/dev/null && echo "workbench ok"
```

Manual UI checks:
- `http://workbench.dev.lotus/suite`
  - verify role selector (`Advisor`, `Risk`, `Compliance`) filters priorities and playbook content
- `http://workbench.dev.lotus/pas/intake`
  - verify operation selector is available (`Create Portfolio`, `Add Positions`, `Add Transactions`, `Add Instruments`, `Add Market Data`)
  - verify portfolio/instrument/currency fields provide lookup suggestions from lotus-core query via lotus-gateway
  - verify non-portfolio operations allow list row add/remove and submit successfully
  - verify list operations render in table-style editors with dense enterprise controls
  - verify no button/text overlap at narrow widths (mobile/tablet), and horizontal scroll appears for wide tables/toggles
  - submit each operation and verify success message with relevant published counts
  - upload CSV package and verify parser validation + success queue message
- `http://workbench.dev.lotus/pa/analytics`
- `http://workbench.dev.lotus/proposals/simulate`
- `http://workbench.dev.lotus/proposals`
- `http://workbench.dev.lotus/workbench` (verify route resolves to a live portfolio workbench when lookup data exists)
- open any proposal from `http://workbench.dev.lotus/proposals` and verify detail view renders version + lineage sections

## 6. Logs and Debugging

Tail logs:

```bash
cd /c/Users/sande/dev/lotus-advise && docker compose logs -f --tail=200
cd /c/Users/sande/dev/lotus-gateway && docker compose logs -f --tail=200
cd /c/Users/sande/dev/lotus-workbench && docker compose logs -f --tail=200
```

Restart a single stack:

```bash
cd /c/Users/sande/dev/lotus-gateway
docker compose down
docker compose up -d --build
```

## 7. Stop All

```bash
cd /c/Users/sande/dev/lotus-workbench && docker compose down
cd /c/Users/sande/dev/lotus-gateway && docker compose down
cd /c/Users/sande/dev/lotus-advise && docker compose down
```

If you need clean volumes (destructive for local DB data):

```bash
cd /c/Users/sande/dev/lotus-advise && docker compose down -v
```

## 8. Common Failure Cases

- `Cannot connect to Docker daemon`
  - Docker Desktop/Engine is not running.
- lotus-gateway cannot reach lotus-manage
  - Check `DECISIONING_SERVICE_BASE_URL=http://manage.dev.lotus`.
- lotus-gateway cannot reach lotus-core ingestion
  - Check `PORTFOLIO_DATA_INGESTION_BASE_URL=http://core-ingestion.dev.lotus`.
- lotus-gateway cannot reach lotus-core query
  - Check `PORTFOLIO_DATA_PLATFORM_BASE_URL=http://core-query.dev.lotus`.
- UI cannot reach lotus-gateway
  - Check `BFF_BASE_URL=http://gateway.dev.lotus`.
- Port conflict on `3000/8100/8000/5432`
  - Stop conflicting process/container and rerun `docker compose up -d --build`.
- lotus-performance conflict with lotus-manage on `8000`
  - lotus-performance Docker compose now defaults to host port `8002` (`PA_HOST_PORT` override supported).

## 9. CI Parity Note

- Local Docker startup uses each repo's `docker-compose.yml`.
- CI parity tests use each repo's `docker-compose.ci-local.yml`.
- Keep both paths green when changing infra or test commands.

## 10. lotus-core Local Docker Run (No Port Conflicts)

lotus-core now uses dedicated host ports and can run in parallel with lotus-manage/lotus-gateway/UI.

lotus-core canonical local identities:
- Ingestion API: `http://core-ingestion.dev.lotus`
- Query API: `http://core-query.dev.lotus`
- Postgres: `localhost:55432`
- Prometheus: `http://prometheus.dev.lotus`
- Grafana: `http://grafana.dev.lotus`

### 10.1 Pull Latest

```bash
cd /c/Users/sande/dev/lotus-core
git checkout main
git pull --ff-only
```

### 10.2 Start lotus-core

```bash
cd /c/Users/sande/dev/lotus-core
docker compose up -d --build
docker compose ps
```

lotus-core startup now includes automated demo dataset bootstrap (`demo_data_loader`).
Validate bootstrap completion:

```bash
cd /c/Users/sande/dev/lotus-core
docker compose logs --tail=200 demo_data_loader
```

### 10.3 Health + API Smoke

```bash
curl -sSf http://core-ingestion.dev.lotus/health/ready >/dev/null && echo "pas-ingestion ok"
curl -sSf http://core-query.dev.lotus/health/ready >/dev/null && echo "pas-query ok"
curl -sSf http://core-query.dev.lotus/docs >/dev/null && echo "pas-swagger ok"
curl -sSf http://report.dev.lotus/health >/dev/null && echo "ras ok"
```

Support/lineage API smoke:

```bash
curl -s "http://core-query.dev.lotus/support/portfolios/PORT001/overview"
curl -s "http://core-query.dev.lotus/lineage/portfolios/PORT001/securities/SEC001"
```

### 10.4 Stop lotus-core

```bash
cd /c/Users/sande/dev/lotus-core
docker compose down
```

### 10.5 Targeted Refresh Standard (Fast Feedback)

Do not restart the full platform by default. Rebuild only changed services:

```bash
# lotus-core: refresh only ingestion service after ingestion changes
cd /c/Users/sande/dev/lotus-core
docker compose up -d --build ingestion_service

# lotus-core: refresh only demo loader after demo pack script changes
docker compose up -d --build demo_data_loader

# lotus-gateway/UI targeted refresh examples
cd /c/Users/sande/dev/lotus-gateway && docker compose up -d --build lotus-gateway
cd /c/Users/sande/dev/lotus-workbench && docker compose up -d --build lotus-workbench

# lotus-report targeted refresh example
cd /c/Users/sande/dev/lotus-report && docker compose up -d --build
```

Use container logs first for debugging:

```bash
docker logs --tail=200 <container_name>
```

## 11. Live lotus-core + lotus-performance + lotus-manage + lotus-report -> lotus-gateway Capabilities E2E (Docker)

This path validates `lotus-gateway` aggregation endpoint against live upstream containers:
- lotus-core query service
- lotus-performance service
- lotus-manage service
- lotus-gateway service

### 11.1 Pull Latest

```bash
cd /c/Users/sande/dev/lotus-advise && git checkout main && git pull --ff-only
cd /c/Users/sande/dev/lotus-core && git checkout main && git pull --ff-only
cd /c/Users/sande/dev/lotus-performance && git checkout main && git pull --ff-only
cd /c/Users/sande/dev/lotus-gateway && git checkout main && git pull --ff-only
```

### 11.2 Start Stack From lotus-gateway Repo

```bash
cd /c/Users/sande/dev/lotus-gateway
export DPM_REPO_PATH=/c/Users/sande/dev/lotus-advise
export PAS_REPO_PATH=/c/Users/sande/dev/lotus-core
export PA_REPO_PATH=/c/Users/sande/dev/lotus-performance
make e2e-up
```

### 11.3 Run Live E2E Assertion

```bash
cd /c/Users/sande/dev/lotus-gateway
make test-e2e-live
```

Expected output:
- `E2E platform capabilities assertion passed`

### 11.4 Manual API Smoke

```bash
curl -s "http://gateway.dev.lotus/api/v1/platform/capabilities?consumerSystem=lotus-gateway&tenantId=default"
```

Response should include:
- `data.partialFailure=false`
- `data.sources.pas`
- `data.sources.pa`
- `data.sources.dpm`
- `data.sources.ras`

### 11.5 Teardown

```bash
cd /c/Users/sande/dev/lotus-gateway
make e2e-down
```

## 12. Performance Analytics Local Workflow (Aligned Baseline)

Repository: `lotus-performance`

### 12.1 Setup

```bash
cd /c/Users/sande/dev/lotus-performance
python -m venv .venv
source .venv/Scripts/activate
make install
```

### 12.2 Local Gates

```bash
make check
make ci-local
```

Docker CI parity:

```bash
make ci-local-docker
make ci-local-docker-down
```

### 12.3 Local Runtime

```bash
make docker-up
curl -sSf http://performance.dev.lotus/docs >/dev/null && echo "performance analytics ok"
make docker-down
```

## 13. Documentation and RFC Governance (Mandatory)

- Keep documentation and code synchronized in the same PR when behavior changes.
- Open a new RFC (or update an existing RFC) for every non-trivial platform engineering change:
  - CI/gates/tooling changes
  - architecture/ownership changes
  - contract/error-handling behavior changes
- Update this runbook whenever local commands, dependency flow, or smoke-check steps change.

## 14. Shared Automation Toolkit (Cross-Repo)

Canonical location: `lotus-platform/automation`

Reference docs:
- `automation/docs/Automation-Guide.md` (what to run and when)
- `automation/docs/Profile-Reference.md` (profile-by-profile usage)
- `automation/docs/Directory-Map.md` (organized script/config map)

### 14.1 One-Shot Platform Pulse

```powershell
cd C:\Users\Sandeep\projects\lotus-platform
powershell -ExecutionPolicy Bypass -File automation\Platform-Pulse.ps1
```

This runs:
- multi-repo sync (safe, no pull on dirty worktrees)
- open PR monitor (`author:@me`)

### 14.2 Continuous Agent Loop

```powershell
cd C:\Users\Sandeep\projects\lotus-platform
powershell -ExecutionPolicy Bypass -File automation\Run-Agent.ps1
```

One iteration only:

```powershell
powershell -ExecutionPolicy Bypass -File automation\Run-Agent.ps1 -Once
```

Output artifacts:
- `output/pr-monitor.json`
- `output/agent-status.md`
- `output/backend-standards-conformance.json`
- `output/backend-standards-conformance.md`

### 14.3 Targeted Service Refresh (No Full Stack Restart)

Example for lotus-core:

```powershell
powershell -ExecutionPolicy Bypass -File automation\Service-Refresh.ps1 -ProjectPath C:/Users/Sandeep/projects/lotus-core -Services query_service demo_data_loader
```

Changed-files based (recommended):

```powershell
powershell -ExecutionPolicy Bypass -File automation\Service-Refresh.ps1 -ProjectPath C:/Users/Sandeep/projects/lotus-core -ChangedOnly -BaseRef origin/main
```

### 14.4 Offload Parallel Work Outside Chat

Use these profiles to run repeatable, long-running tasks without consuming chat context:

```powershell
# fast development quality checks in parallel
powershell -ExecutionPolicy Bypass -File automation\Run-Parallel-Tasks.ps1 -Profile fast-feedback -MaxParallel 3

# one-time dependency bootstrap (run before fast-feedback on new machine)
powershell -ExecutionPolicy Bypass -File automation\Run-Parallel-Tasks.ps1 -Profile bootstrap-env -MaxParallel 2

# CI parity checks in parallel
powershell -ExecutionPolicy Bypass -File automation\Run-Parallel-Tasks.ps1 -Profile ci-parity -MaxParallel 2

# detached/background execution
powershell -ExecutionPolicy Bypass -File automation\Start-Background-Run.ps1 -Profile docker-build -MaxParallel 2

# check background status on demand
powershell -ExecutionPolicy Bypass -File automation\Check-Background-Runs.ps1

# live watch background status
powershell -ExecutionPolicy Bypass -File automation\Check-Background-Runs.ps1 -Watch -IntervalSeconds 20

# summarize only actionable failures from latest runs
powershell -ExecutionPolicy Bypass -File automation\Summarize-Task-Failures.ps1 -Latest 3

# OpenAPI contract quality conformance baseline
powershell -ExecutionPolicy Bypass -File automation\Run-Parallel-Tasks.ps1 -Profile openapi-conformance-baseline -MaxParallel 1

# Domain vocabulary conformance baseline
powershell -ExecutionPolicy Bypass -File automation\Run-Parallel-Tasks.ps1 -Profile domain-vocabulary-conformance -MaxParallel 1

# RFC conformance inventory + centralized backlog baseline
powershell -ExecutionPolicy Bypass -File automation\Run-Parallel-Tasks.ps1 -Profile rfc-conformance-baseline -MaxParallel 1

# PR lifecycle automation (monitor checks, queue auto-merge, cleanup merged branches)
powershell -ExecutionPolicy Bypass -File automation\Close-PR-Loop.ps1

# Continuous PR lifecycle watch
powershell -ExecutionPolicy Bypass -File automation\Close-PR-Loop.ps1 -Watch -IntervalSeconds 30

# Autonomous full foundation governance sweep
powershell -ExecutionPolicy Bypass -File automation\Run-Parallel-Tasks.ps1 -Profile autonomous-foundation -MaxParallel 1

# Dependency vulnerability rollup baseline
powershell -ExecutionPolicy Bypass -File automation\Generate-Dependency-Vulnerability-Rollup.ps1
```

Profiles are defined in `automation/task-profiles.json` and currently include:
- `bootstrap-env`
- `fast-feedback`
- `docker-build`
- `ci-parity`
- `docker-ci-parity`
- `pas-data-smoke`
- `migration-quality`
- `coverage-pyramid-baseline`
- `backend-standards-conformance`
- `enforce-backend-governance`
- `openapi-conformance-baseline`
- `domain-vocabulary-conformance`
- `repo-metadata-validation`
- `rfc-conformance-baseline`
- `pr-lifecycle`
- `autonomous-foundation`

Windows note for `ci-parity`: coverage-scoped pytest commands in the profile use `set COVERAGE_FILE=... &&` because the task runner executes via `cmd /c`.
`ci-parity` intentionally omits host `pip check` for lotus-manage/lotus-performance due shared interpreter drift; run `docker-ci-parity` when you need strict isolated dependency parity.

Artifacts:
- `output/task-runs/*.json`
- `output/task-runs/*.md`
- `output/task-runs/*.out.log`
- `output/task-runs/*.err.log`
- `output/background-runs.json`
- `output/pr-lifecycle.json`
- `output/pr-lifecycle.md`
- `output/rfc-conformance-inventory.json`
- `output/rfc-conformance-inventory.md`
- `output/rfc-conformance-backlog.json`
- `output/rfc-conformance-backlog.md`
- `output/dependency-vulnerability-rollup.json`
- `output/dependency-vulnerability-rollup.md`
- `output/agent-status.json`

### 14.5 Local-CI Parity Evidence

Generate explicit parity evidence between local standard commands and CI workflow gates:

```powershell
powershell -ExecutionPolicy Bypass -File automation\Generate-Local-CI-Parity-Evidence.ps1
```

Artifacts:
- `output/local-ci-parity-evidence.json`
- `output/local-ci-parity-evidence.md`


