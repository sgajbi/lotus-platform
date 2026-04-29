# Analytics UI Observability Runbook

This runbook covers the RFC-0108 first-wave Workbench analytics UI observability alerts.
The alert rules are intentionally bounded to implemented Workbench metric families and
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

## analytics-ui-attention-events

Use this alert when selected Workbench analytics panels emit action-required attention events for at
least ten minutes.

Triage steps:

1. Check the dashboard attention panel by route, panel, attention type, and severity.
2. Compare the attention reason with the selected panel state and Gateway fan-out logs for the same
   operation family.
3. Treat repeated failures as operator-actionable only after the Workbench deduplication threshold
   is met.
4. Keep entity-specific investigation inside protected diagnostics; do not add portfolio, client,
   correlation, trace, request, response, or screen content fields to attention labels.

## Gateway Analytics Read Audit Events

Use Gateway analytics read audit logs to reconcile selected Workbench analytics read outcomes with
the user-visible panel state without exposing entity-specific data.

Triage steps:

1. Review `gateway.analytics.audit.analytics_read_allowed` and
   `gateway.analytics.audit.analytics_read_denied` by route, panel, operation, status class, region,
   and environment.
2. Treat `analytics_read_allowed` as proof that the upstream analytics service accepted the selected
   read request, not as a full caller-context entitlement certification.
3. Treat `analytics_read_denied` as a bounded upstream `401` or `403` denial signal. The reason must
   remain `upstream_authorization_denied`; do not copy raw entitlement text into logs, dashboards, or
   tickets.
4. Keep protected diagnostics lookup audit planned until the protected diagnostics API exists and is
   certified.
