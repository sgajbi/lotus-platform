# Analytics UI Observability Runbook

This runbook covers the RFC-0108 implemented analytics UI observability alerts across Workbench,
Gateway, and AI-backed supportability surfaces. Alert rules are intentionally bounded to
implemented metric families and must not include portfolio identifiers, client names, trace
identifiers, request bodies, response bodies, raw entitlement failure text, raw prompts, generated
AI output, or screen content.

For a concise implementation-backed current-state summary and demo-readiness orientation, use the
repo-local wiki page `wiki/Analytics-UI-Observability.md`.

## analytics-ui-panel-hydration-latency-p95

Use this alert when selected Workbench analytics panel hydration p95 exceeds three seconds for at
least ten minutes.

Triage steps:

1. Check the dashboard hydration panel by route and panel.
2. Compare the affected panel with Workbench API request latency and Gateway fan-out latency for
   the same route family.
3. Confirm whether the user-visible delay is a UI render delay, a BFF/API delay, or upstream
   service fan-out delay.
4. Keep notes bounded to route, panel, service, operation, state, and status class.

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
at least ten minutes. This metric family now includes the Advisor Brief review-action mutation
where Workbench records the bounded `performance-advisor-brief-review-action` surface and
`performance.workspace.advisor-brief.review-action` operation.

Triage steps:

1. Check the dashboard latency panel by route, operation, and status class.
2. Review Gateway fan-out logs for matching operation latency and degraded-source reasons.
3. Confirm whether backend analytics services are returning stale, partial, degraded, or error
   responses.
4. For Advisor Brief review actions, confirm Workbench `/api/metrics/events` accepted bounded
   browser-originated metric events and `/api/metrics` exported the mutation surface.
5. Keep remediation notes bounded to route, panel, service, operation, status class, and state.
   Do not add reviewed-by identity, portfolio, client, correlation, trace, free-form review reason,
   request-body, or response-body values.

## gateway-analytics-fanout-latency-p95

Use this alert when Gateway analytics fan-out p95 exceeds three seconds for at least ten minutes.

Triage steps:

1. Check the dashboard Gateway fan-out panel by service, operation, and status class.
2. Compare with Workbench API latency to determine whether the latency is visible in the product
   surface.
3. Review bounded Gateway fan-out logs for service, operation, status class, state, and reason.
4. Escalate to the authoritative upstream service only when the degraded service and operation are
   clear; do not copy portfolio, trace, request, or response payload content into the alert thread.

## gateway-analytics-degraded-sources

Use this alert when Gateway analytics fan-out records degraded source outcomes for at least ten
minutes.

Triage steps:

1. Check the dashboard Gateway degraded-source panel by service, operation, and bounded reason.
2. Compare the degraded reason with Workbench panel state and attention events.
3. Use protected diagnostics lookup when entity-specific context is needed; metrics and alert
   annotations must remain product-safe.
4. Treat source degradation as service degradation unless the Workbench panel shows user-visible
   error, permission-blocked, or action-required posture.

## backend-analytics-freshness-action-required

Use this alert when performance or risk backend analytics freshness records `stale`, `degraded`,
`empty`, `error`, `permission_blocked`, or `unsupported` supportability posture for at least ten
minutes.

Triage steps:

1. Check the dashboard backend freshness panel by service, operation, freshness bucket, and
   supportability state.
2. Compare the affected source posture with Gateway fan-out degradation and Workbench panel state
   for the same service and operation family.
3. Escalate to `lotus-performance` or `lotus-risk` only with bounded service, operation,
   freshness, supportability state, and source-specific runbook evidence.
4. Do not add portfolio, client, account, transaction, trace, correlation, request, or response
   identifiers to metric labels, dashboard variables, alert annotations, or incident summaries.

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

## ai-surface-supportability-degraded

Use this alert when AI-backed analytics support surfaces report degraded, partial, unavailable, or
unsupported posture for at least ten minutes.

Triage steps:

1. Check the dashboard AI supportability panel by surface, posture, and source.
2. Confirm whether the AI-backed surface is advisory support only or blocks a user-visible
   Workbench workflow.
3. Compare AI supportability posture with Gateway fan-out degradation if the affected surface is
   reached through Gateway.
4. Do not include raw prompts, generated AI output, portfolio identifiers, client identifiers, or
   screen content in remediation notes.

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
4. Use `GET /api/v1/analytics-ui/diagnostics/{support_reference}` only with opaque `gdiag-*`
   support references and operator caller context. The protected diagnostics lookup must not expose
   support references, portfolio identifiers, trace identifiers, correlation identifiers, raw
   entitlement failures, request bodies, or response bodies in audit fields.

## Caller-Context Entitlement Certification

Full caller-context entitlement certification is governed by
`context/contracts/analytics-ui-observability-entitlement-certification.json`.

Certification rules:

1. Do not promote a Workbench read path until both `analytics_read_allowed` and
   `analytics_read_denied` evidence exists for that path.
2. Denied reads must use `permission_blocked` state and the bounded
   `upstream_authorization_denied` reason.
3. Evidence must prove caller context is required and malformed or missing caller context is
   rejected.
4. Evidence must prove raw entitlement failures, support references, portfolio identifiers, client
   identifiers, trace identifiers, correlation identifiers, request bodies, response bodies, and
   screen content are absent from audit logs, dashboards, screenshots, and tickets.
5. Workbench proof must show a permission-blocked panel state without exposing restricted details.

Run the platform gate before claiming certification:

```powershell
python automation\validate_analytics_ui_entitlement_certification.py
python -m pytest tests\unit\test_analytics_ui_entitlement_certification.py tests\unit\test_analytics_ui_observability_contract.py -q
```
