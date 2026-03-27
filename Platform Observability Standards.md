# Platform Observability Standards

## Scope

Applies to lotus-core, lotus-performance, lotus-manage, lotus-report, lotus-gateway, and UI-facing backend interactions.

Machine-readable contract source:
- `platform-contracts/cross-cutting-platform-contract.yaml`

## 1. Logging Standard

- Format: structured JSON logs for application output.
- Required fields:
  - `timestamp`
  - `level`
  - `service`
  - `environment`
  - `correlation_id` (or `request_id`)
  - `trace_id` (when tracing is enabled)
  - `message`
- Recommended contextual fields:
  - `endpoint`
  - `http_method`
  - `status_code`
  - `latency_ms`
  - `tenant_id`
  - `user_id` (if available and policy-compliant)

Container logging baseline:
- Docker `json-file` logging driver
- rotation: `max-size=10m`, `max-file=5`

## 2. Health Checks

Every service must expose:
- liveness endpoint (`/health` or `/health/live`)
- readiness endpoint (`/health/ready`)

Readiness must validate critical dependencies:
- lotus-core ingestion: Kafka availability
- lotus-core query: database connectivity
- lotus-manage: database availability
- lotus-report/lotus-gateway: upstream dependency availability where appropriate

## 3. Metrics Standard

Minimum service metrics:
- request count
- request latency
- error rate
- dependency latency/error counts
- queue/background consumer lag or processing counters where applicable

Scale-signal metrics required for capacity decisions:
- CPU and memory usage for service containers
- database query latency and connection pool saturation
- queue depth / consumer lag for async workloads
- throughput and p95/p99 response latency by endpoint

Naming conventions:
- snake_case metric names
- stable labels: `service`, `env`, `endpoint`, `method`, `status_code`

Platform metrics stack:
- Prometheus for scraping
- Grafana for dashboards

## 4. Tracing Standard

- Use OpenTelemetry OTLP export.
- Propagate correlation across service boundaries:
  - `X-Correlation-Id` (request correlation)
  - W3C Trace Context headers (`traceparent`, `tracestate`) for distributed tracing
- Preserve inbound correlation ID; generate only when missing.

## 5. Operational Conventions

- Standard troubleshooting order:
  1. Container health status
  2. Service logs
  3. Metrics panels
  4. Trace spans
- Runbook updates are mandatory whenever:
  - service endpoint/port changes
  - health check semantics change
  - logging/tracing/metrics behavior changes

## 6. Centralized Local Stack

Use:
- `lotus-platform/platform-stack/docker-compose.yml`

Ownership rule:

- `lotus-platform/platform-stack` is the canonical shared observability and shared infrastructure baseline.
- Application repositories may keep app-local overlays and app-specific dashboard content.
- Application repositories must not be documented as the owner of shared Prometheus, Grafana, or telemetry bootstrap.

Included observability baseline:
- `prometheus`
- `grafana`
- `otel-collector`

Infrastructure evidence links:
- `platform-stack/prometheus/prometheus.yml`
- `platform-stack/docker-compose.yml`
- `platform-stack/grafana/provisioning/datasources/datasource.yml`

Application boundary:

1. Shared scrape configuration belongs in `lotus-platform`.
2. Shared datasource provisioning belongs in `lotus-platform`.
3. Shared dashboard provisioning belongs in `lotus-platform`.
4. App-specific dashboards may remain in the owning application repo and be mounted into the canonical platform Grafana runtime.
5. App-level instrumentation remains owned by the application repo.

