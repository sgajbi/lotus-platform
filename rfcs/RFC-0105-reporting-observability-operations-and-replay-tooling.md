# RFC-0105: Reporting Observability, Operations, And Replay Tooling

- Status: Proposed
- Date: 2026-04-23
- Owners:
  - `lotus-report` owners
  - `lotus-render` owners
  - `lotus-archive` owners
  - `lotus-gateway` owners
  - lotus-platform operations
- Target repositories:
  - `lotus-report`
  - `lotus-render`
  - `lotus-archive`
  - `lotus-gateway`
  - `lotus-platform`
- Depends on:
  - `RFC-0099-enterprise-reporting-and-document-archive-target-architecture.md`
  - `RFC-0100` through `RFC-0104`

## Summary

This RFC defines end-to-end observability and operator tooling for enterprise reporting. It covers
OpenTelemetry traces, structured logs, metrics, dashboards, alerting, failure diagnosis, rerender,
regenerate, replay, stuck-job handling, and SLA monitoring.

## Problem

Enterprise reporting failures cross service boundaries: gateway, report, upstream services, render,
archive, and batch orchestration. Operators need to identify whether a failure is caused by data,
rendering, archive storage, entitlement, timeout, or platform infrastructure.

## Target Scope

In scope:

1. trace propagation across report flows,
2. structured logging fields,
3. metrics vocabulary,
4. dashboards and alerts,
5. operator status APIs,
6. rerender from snapshot,
7. regenerate from upstream data,
8. replay failed jobs and batch items,
9. stuck-job detection,
10. SLA breach monitoring.

Out of scope:

1. new report types,
2. changing business report content,
3. legal retention behavior,
4. broad platform observability unrelated to reporting.

## Observability Contract

Required identifiers:

1. `correlation_id`,
2. `trace_id`,
3. `report_request_id`,
4. `report_job_id`,
5. `batch_id`,
6. `batch_item_id`,
7. `snapshot_id`,
8. `render_job_id`,
9. `document_id`,
10. `portfolio_id` where permitted.

Required metrics:

1. report requests by type/status,
2. report jobs in progress,
3. failures by category,
4. upstream call latency,
5. render latency,
6. archive latency,
7. batch progress,
8. retry counts,
9. stuck job counts,
10. SLA breach counts.

## Implementation Slices

### Slice 0: Cleanup And Structure

1. Review existing observability and operator docs.
2. Remove duplicate reporting diagnostics guidance.
3. Establish shared reporting observability vocabulary.
4. Prepare wiki operator runbook source.

### Slice 1: Trace And Log Propagation

1. Ensure trace/correlation propagation across gateway, report, render, archive, and upstream calls.
2. Add structured log fields.
3. Add tests for identifier propagation.

### Slice 2: Metrics And Dashboards

1. Add metrics in report, render, and archive services.
2. Add dashboard artifact or documented dashboard contract.
3. Add alert thresholds for failure rate, stuck jobs, and SLA breach.

### Slice 3: Operator APIs

1. Add support APIs to inspect request, job, batch, render, archive, and document posture.
2. Add failure detail and lineage lookup.
3. Add tests for operator authorization and redaction.

### Slice 4: Rerender, Regenerate, And Replay

1. Add rerender from existing snapshot.
2. Add regenerate from upstream data.
3. Add replay failed job/batch item.
4. Add tests proving semantics differ and are auditable.

### Slice 5: Stuck Job And SLA Monitoring

1. Add stale state detection.
2. Add SLA breach metrics and attention events.
3. Integrate with heartbeat/attention only if source evidence exists.

### Second-Last Slice: Hardening, Review, And Certification

1. Review observability coverage and operator workflows.
2. Verify no sensitive data leaks in logs/metrics.
3. Verify API certification and platform governance.

### Final Slice: Closure

1. Update docs, wiki, context, supported-features, and skills/guidance.
2. Publish wiki after merge if changed.
3. Ensure operational runbooks are complete.

## Acceptance Criteria

1. Operators can trace a report from gateway request to archived document.
2. Failures are categorized by data, render, archive, entitlement, timeout, or platform issue.
3. Rerender, regenerate, and replay semantics are explicit and tested.
4. Stuck jobs and SLA breaches are detectable.
5. Sensitive report content is not logged.

## Risks

| Risk | Mitigation |
| --- | --- |
| Observability emits sensitive content | Identifier-only logs and redacted details |
| Replay changes data unexpectedly | Separate rerender and regenerate commands |
| Dashboards drift from metrics | Test metric names and document dashboard contract |
| Operator APIs become unsafe | Require privileged roles and access audit |

## Validation

Required validation:

1. Trace propagation tests.
2. Metrics contract tests.
3. Operator API authorization tests.
4. Rerender/regenerate/replay integration tests.
5. Stuck-job and SLA simulation tests.

## Supported Features

Operator and observability features must be listed only after APIs, metrics, docs, and tests prove
they are production-usable.

