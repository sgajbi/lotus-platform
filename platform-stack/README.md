# Platform Stack (Centralized Compose)

This folder provides a centralized Docker Compose orchestration for the full PBWM platform:

- lotus-core (`lotus-core-ingestion`, `lotus-core-query`) + lotus-core dependencies (`zookeeper`, `kafka`, `lotus-core-kafka-topic-creator`, `lotus-core-postgres`, `lotus-core-migration-runner`)
- lotus-manage (`lotus-manage`, `lotus-manage-postgres`)
- lotus-performance (`lotus-performance`)
- lotus-report (`lotus-report`)
- lotus-gateway (`bff`)
- UI (`ui`)
- Observability baseline (`prometheus`, `grafana`, `otel-collector`)

This stack is the canonical shared-infrastructure baseline for local platform bring-up.

It now includes a central local ingress that exposes stable environment-scoped hostnames for the
developer-facing surfaces and directly used API products.

Important ownership rule:

1. `lotus-platform` owns the shared infrastructure products and their baseline configuration.
2. Application repositories may still provide app-owned images and bootstrap jobs consumed by this stack.
3. Using an app-owned migration runner or topic bootstrap job inside this compose file does not make that app the owner of shared infrastructure.
4. Grafana provisioning is platform-owned here, while app-specific dashboard JSON may still be mounted from the owning application repository.

Grafana dashboard boundary:

1. shared Grafana provisioning lives in `lotus-platform/platform-stack/grafana/provisioning`
2. platform-shared dashboard content may live in `lotus-platform/platform-stack/grafana/dashboards`
3. app-specific dashboard JSON can still be mounted from the owning repository, for example `lotus-core/grafana/dashboards`

Prometheus scrape boundary:

1. the canonical shared scrape config lives in `lotus-platform/platform-stack/prometheus/prometheus.yml`
2. it should only scrape services actually orchestrated by `platform-stack`
3. app-local Prometheus configs may still exist in application repositories for isolated development, but they are not the shared platform baseline

Cross-cutting governance for this stack is defined in:
- `Platform Observability Standards.md`
- `platform-contracts/cross-cutting-platform-contract.yaml`

## 1) Setup

Copy `.env.example` to `.env` and adjust repository paths if needed.

```powershell
cd C:\Users\Sandeep\projects\lotus-platform\platform-stack
Copy-Item .env.example .env
```

Add the local hostname mappings from:

- `platform-stack/dev-ingress/hosts.example`

to your hosts file before first use.

Platform-owned helper:

```powershell
cd C:\Users\Sandeep\projects\lotus-platform
powershell -ExecutionPolicy Bypass -File automation/Sync-Dev-Ingress-Hosts.ps1
```

Apply the managed block to the Windows hosts file:

```powershell
cd C:\Users\Sandeep\projects\lotus-platform
powershell -ExecutionPolicy Bypass -File automation/Sync-Dev-Ingress-Hosts.ps1 -Apply
```

## 2) Start Full Platform

```powershell
cd C:\Users\Sandeep\projects\lotus-platform\platform-stack
docker compose up -d --build
```

Optional direct host-port publishing for debugging only:

```powershell
cd C:\Users\Sandeep\projects\lotus-platform\platform-stack
docker compose -f docker-compose.yml -f docker-compose.host-ports.yml up -d --build
```

Ingress-first smoke validation:

```powershell
cd C:\Users\Sandeep\projects\lotus-platform
powershell -ExecutionPolicy Bypass -File automation/Validate-Dev-Ingress-Smoke.ps1
```

## 3) Smoke Endpoints

Canonical service identities:

- Workbench: `http://workbench.dev.lotus`
- Gateway readiness: `http://gateway.dev.lotus/health/ready`
- Manage readiness: `http://manage.dev.lotus/health/ready`
- Core query readiness: `http://core-query.dev.lotus/health/ready`
- Core ingestion readiness: `http://core-ingestion.dev.lotus/health/ready`
- Performance readiness: `http://performance.dev.lotus/health/ready`
- Report readiness: `http://report.dev.lotus/health/ready`
- Prometheus: `http://prometheus.dev.lotus`
- Grafana: `http://grafana.dev.lotus` (admin/admin)

The underlying container port mappings are implementation detail. Operators and application repos
should use the environment-scoped service hostnames above as the stable contract.

If you need legacy direct host ports for debugging, use `docker-compose.host-ports.yml`. The base
stack is ingress-first by design.

## 4) Logs

```powershell
docker compose logs -f --tail=200
```

Service-level logs:

```powershell
docker compose logs -f --tail=200 bff lotus-core-query lotus-core-ingestion lotus-performance lotus-manage lotus-report
```

## 5) Stop

```powershell
docker compose down
```

Destructive cleanup (containers + volumes):

```powershell
docker compose down -v --remove-orphans
```

