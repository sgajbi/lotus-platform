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

Important ownership rule:

1. `lotus-platform` owns the shared infrastructure products and their baseline configuration.
2. Application repositories may still provide app-owned images and bootstrap jobs consumed by this stack.
3. Using an app-owned migration runner or topic bootstrap job inside this compose file does not make that app the owner of shared infrastructure.
4. Grafana provisioning is platform-owned here, while app-specific dashboard JSON may still be mounted from the owning application repository.

Grafana dashboard boundary:

1. shared Grafana provisioning lives in `lotus-platform/platform-stack/grafana/provisioning`
2. platform-shared dashboard content may live in `lotus-platform/platform-stack/grafana/dashboards`
3. app-specific dashboard JSON can still be mounted from the owning repository, for example `lotus-core/grafana/dashboards`

Cross-cutting governance for this stack is defined in:
- `Platform Observability Standards.md`
- `platform-contracts/cross-cutting-platform-contract.yaml`

## 1) Setup

Copy `.env.example` to `.env` and adjust repository paths if needed.

```powershell
cd C:\Users\Sandeep\projects\lotus-platform\platform-stack
Copy-Item .env.example .env
```

## 2) Start Full Platform

```powershell
cd C:\Users\Sandeep\projects\lotus-platform\platform-stack
docker compose up -d --build
```

## 3) Smoke Endpoints

- UI: `http://localhost:3000`
- lotus-gateway readiness: `http://localhost:8100/health/ready`
- lotus-manage readiness: `http://localhost:8000/health/ready`
- lotus-core ingestion ready: `http://localhost:8200/health/ready`
- lotus-core query ready: `http://localhost:8201/health/ready`
- lotus-performance readiness: `http://localhost:8002/health/ready`
- lotus-report readiness: `http://localhost:8300/health/ready`
- Prometheus: `http://localhost:9190`
- Grafana: `http://localhost:3300` (admin/admin)

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

