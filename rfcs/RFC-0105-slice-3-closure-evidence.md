# RFC-0105 Slice 3 Closure Evidence

This note records implementation-backed closure evidence for RFC-0105 Slice 3 as of 2026-04-27.
Slice 3 covers the first-wave reporting metrics contract, dashboard artifact, alert rules, label
discipline, and initial SLA objective plus escalation-owner material. `stuck_jobs` and
`sla_breaches` remain explicitly deferred to Slice 8 by design and are not claimed here.

## Scope Closed

1. `lotus-report`
   - durable batch-pressure metric `lotus_report_batch_pressure_last_counts`
   - bounded report operation, duration, batch-runtime, and scheduler metrics retained as the
     report-side contract base
2. `lotus-render`
   - bounded render operation, duration, and artifact-size metrics used as alert and dashboard
     sources
3. `lotus-archive`
   - bounded archive operation, duration, and document-size metrics with operation-aware status
     mapping
4. `lotus-platform`
   - machine-readable contract:
     `context/contracts/reporting-observability-contract.json`
   - contract schema:
     `context/contracts/reporting-observability-contract.schema.json`
   - runbook:
     `docs/operations/reporting-observability-runbook.md`
   - dashboard artifact:
     `platform-stack/grafana/dashboards/reporting-observability-overview.json`
   - alert rules:
     `platform-stack/prometheus/rules/reporting-observability.rules.yml`
   - first-wave SLA objective and escalation-owner inventory embedded in the contract and runbook

## Truthful Scope Boundary

1. Slice 3 implements thresholds for:
   - report operation failures
   - render latency p95
   - archive latency p95
   - dispatch-ready backlog
   - retry-ready pressure
2. Slice 3 explicitly does not implement:
   - `stuck_jobs`
   - `sla_breaches`
3. Those deferred alert families are recorded in the contract with owning later slice `Slice 8`
   and rationale. They are intentionally absent from live rule files.

## Contract And Test Evidence

The following repo-local gates passed on 2026-04-27:

1. `python -m pytest tests/unit/test_reporting_observability_contract.py tests/unit/test_platform_stack_observability_contract.py -q`
   - result: `14 passed`
2. `docker compose exec -T prometheus promtool check config /etc/prometheus/prometheus.yml`
   - result: Prometheus config valid and `5 rules found`

These tests and validators protect:

1. dashboard references only implemented metrics,
2. alert rules align with contract alert ids, severity, owner repo, and runbook path,
3. contract label inventories match the service-owned metric contracts in `lotus-report`,
   `lotus-render`, and `lotus-archive`,
4. service metric sources keep explicit forbidden-label sets for sensitive and high-cardinality
   identifiers such as `portfolio_id`, `tenant_id`, `trace_id`, `correlation_id`, and
   `report_job_id`,
5. Prometheus stack config mounts and loads the reporting rule directory,
6. report, render, and archive scrape targets remain declared in the platform-owned config,
7. contract references stay free of invented metric names.

## Live Runtime Evidence

Live platform-stack proof on 2026-04-27:

1. `docker compose up -d prometheus grafana`
2. `docker compose up -d lotus-report`
3. `docker exec pbwm-platform-grafana-1 sh -lc "wget -qO- 'http://127.0.0.1:3000/api/search?query=Reporting%20Observability%20Overview'"`
4. `docker exec pbwm-platform-prometheus-1 sh -lc "wget -qO- 'http://127.0.0.1:9090/api/v1/rules'"`
5. `docker exec pbwm-platform-prometheus-1 sh -lc "wget -qO- 'http://127.0.0.1:9090/api/v1/targets'"`
6. `docker exec pbwm-platform-prometheus-1 sh -lc "ls -la /etc/prometheus/rules"`

Observed runtime facts:

1. Grafana API returned dashboard uid `reporting-observability-overview`
2. Prometheus mounted `/etc/prometheus/rules/reporting-observability.rules.yml`
3. Prometheus API returned the `reporting-observability` rule group
4. the live rule set exposed five alert rules:
   - `ReportOperationFailures`
   - `RenderLatencyP95`
   - `ArchiveLatencyP95`
   - `BatchDispatchReadyBacklog`
   - `BatchRetryReadyPressure`
5. after one full evaluation interval, all five rules reported `health: "ok"` with populated
   `lastEvaluation` timestamps
6. target health proved the first-wave reporting signal surface was live:
   - `lotus-report` `health: "up"`
   - `lotus-render` `health: "up"`
   - `lotus-archive` `health: "up"`

Additional previously captured metric exposure proof remains part of the closure set:

1. `lotus-report` direct metrics endpoint exposed `lotus_report_batch_pressure_last_counts` on
   `http://127.0.0.1:8300/metrics`
2. `lotus-render` direct metrics endpoint exposed render metric families on
   `http://127.0.0.1:8310/metrics`
3. `lotus-archive` direct metrics endpoint exposed archive metric families on
   `http://127.0.0.1:8150/metrics`

## Closure Decision

Slice 3 is closed for first-wave RFC-0105 scope. The contract, dashboard, rule files, label
discipline, initial SLA objectives, escalation-owner roles, repo-local validators, and live
platform-stack proof are now implementation-backed. Deferred families remain truthful and
explicitly owned by Slice 8.
