# Reporting Observability Runbook

This runbook defines the first-wave operational interpretation for the implemented RFC-0105 Slice 3
metrics contract. It must stay aligned with
`context/contracts/reporting-observability-contract.json`.

## Report Operation Failures

- Alert id: `report-operation-failures`
- Owner repo: `lotus-report`
- Metric: `lotus_report_operations_total`
- Severity: `P2`
- Threshold: failed report operations exceed 5 per 15 minutes
- Initial action:
  inspect `lotus-report` logs by correlation id or trace id, then reconcile report-job status,
  snapshot status, render handoff, and archive handoff.

## Render Latency P95

- Alert id: `render-latency-p95`
- Owner repo: `lotus-render`
- Metric: `lotus_render_operation_duration_seconds`
- Severity: `P2`
- Threshold: p95 render duration exceeds 5 seconds for 15 minutes
- Initial action:
  inspect render package size, template version, typst runtime health, and render job status mix.

## Archive Latency P95

- Alert id: `archive-latency-p95`
- Owner repo: `lotus-archive`
- Metric: `lotus_archive_operation_duration_seconds`
- Severity: `P2`
- Threshold: p95 archive duration exceeds 2 seconds for 15 minutes
- Initial action:
  inspect archive write path, metadata persistence, download latency, and storage adapter health.

## Batch Dispatch Ready Backlog

- Alert id: `batch-dispatch-ready-backlog`
- Owner repo: `lotus-report`
- Metric: `lotus_report_batch_pressure_last_counts`
- Severity: `P2`
- Threshold: `pressure_state=dispatch_ready_items` exceeds 100 for 15 minutes
- Initial action:
  inspect `lotus_report_batch_pressure_last_counts`, batch scheduler pass counts, worker pass counts,
  and back-pressure reasons to determine whether backlog growth is driven by capacity or item
  failure posture.

## Batch Retry Ready Pressure

- Alert id: `batch-retry-ready-pressure`
- Owner repo: `lotus-report`
- Metric: `lotus_report_batch_pressure_last_counts`
- Severity: `P3`
- Threshold: `pressure_state=retry_ready_items` exceeds 25 for 15 minutes
- Initial action:
  inspect retryable batch items, failure categories, next retry timestamps, and whether render or
  archive downstream failures are dominating the retry mix.

## Initial SLA Objectives And Escalation Owners

- `report-operation-reliability`
  - owner repo: `lotus-report`
  - escalation owner role: `reporting-service-owner`
  - objective: failed report operations stay at or below 5 per rolling 15-minute window
- `render-latency-objective`
  - owner repo: `lotus-render`
  - escalation owner role: `render-service-owner`
  - objective: render duration p95 stays at or below 5 seconds over a rolling 15-minute window
- `archive-latency-objective`
  - owner repo: `lotus-archive`
  - escalation owner role: `archive-service-owner`
  - objective: archive duration p95 stays at or below 2 seconds over a rolling 15-minute window
- `batch-dispatch-backlog-objective`
  - owner repo: `lotus-report`
  - escalation owner role: `reporting-service-owner`
  - objective: dispatch-ready batch items stay at or below 100 over a rolling 15-minute window
- `batch-retry-pressure-objective`
  - owner repo: `lotus-report`
  - escalation owner role: `reporting-service-owner`
  - objective: retry-ready batch items stay at or below 25 over a rolling 15-minute window

## Deferred Families

- `stuck_jobs`
  Deferred to RFC-0105 Slice 8, which owns stuck-state metrics, scanner thresholds, and recovery
  guidance.
- `sla_breaches`
  Deferred to RFC-0105 Slice 8, which owns SLA breach metrics, attention events, and simulation
  proof.
