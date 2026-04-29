# Analytics UI Observability Runbook

This runbook covers the RFC-0108 first-wave Workbench analytics UI observability alerts.
The Slice 5 alert rules are intentionally bounded to implemented Workbench metric families and
must not include portfolio identifiers, client names, trace identifiers, request bodies, response
bodies, or screen content.

## analytics-ui-panel-error-rate

Use this alert when selected Workbench analytics panels report `error`, `degraded`, or
`permission_blocked` state for at least ten minutes.

Triage steps:

1. Check the Analytics UI Observability Overview dashboard by route, panel, and state.
2. Compare the affected route with Gateway structured fan-out logs for the same operation family.
3. Verify whether the panel state is a legitimate entitlement block, a degraded upstream source, or
   a UI-side request failure.
4. Use protected service diagnostics for entity-specific investigation; do not add portfolio,
   client, or trace identifiers to metric labels, dashboard variables, or alert annotations.

## analytics-ui-api-request-latency-p95

Use this alert when selected Workbench analytics API request p95 latency exceeds three seconds for
at least ten minutes.

Triage steps:

1. Check the dashboard latency panel by route, operation, and status class.
2. Review Gateway fan-out logs for matching operation latency and degraded-source reasons.
3. Confirm whether backend analytics services are returning stale, partial, degraded, or error
   responses.
4. Keep remediation notes bounded to route, panel, service, operation, status class, and state.
