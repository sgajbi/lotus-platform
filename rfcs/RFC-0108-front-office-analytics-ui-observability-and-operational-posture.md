# RFC-0108: Front-Office Analytics UI Observability And Operational Posture

- Status: Gold-Pass Ready; Implementation Not Started
- Date: 2026-04-29
- Gold-pass hardened: 2026-04-29
- Owners:
  - `lotus-platform` observability/governance
  - `lotus-workbench` owners
  - `lotus-gateway` owners
  - `lotus-performance` owners
  - `lotus-risk` owners
  - `lotus-core` owners where portfolio identity, entitlement, or position context is required
  - `lotus-advise` owners where advisory panels are included
- Target repositories:
  - `lotus-platform`
  - `lotus-workbench`
  - `lotus-gateway`
  - `lotus-performance`
  - `lotus-risk`
  - `lotus-core`
  - optionally `lotus-advise` when advisory analytics panels enter scope
- Depends on:
  - `RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`
  - `RFC-0076` canonical front-office demo-data contracts and panel validation posture
  - `RFC-0077` Workbench panel registry posture where panel certification is required
  - `RFC-0087-live-trust-telemetry-and-certification-plane.md`
  - `RFC-0088-self-serve-discovery-and-dependency-catalog.md`
  - `RFC-0089-mesh-certification-merge-gate-and-operational-trust-enforcement.md`
  - `RFC-0091-enterprise-data-mesh-maturity-and-production-readiness.md`
  - `RFC-0105-reporting-observability-operations-and-replay-tooling.md`
- Follow-on RFC boundaries:
  - RFC-0108 does not replace reporting observability from RFC-0105.
  - RFC-0108 is not an extension of RFC-0105.
  - RFC-0108 does not certify reporting security from RFC-0106.
  - RFC-0108 does not claim final reporting production readiness from RFC-0107.
  - A later analytics production-certification RFC may consume RFC-0108 evidence if a broader
    front-office release gate is needed.

## Summary

RFC-0105 made the reporting flow operationally supportable for the first-wave asynchronous
reporting surface. The same enterprise posture must now extend to interactive analytics UI
surfaces without treating reporting as a special lane.

This RFC defines the governed observability and operational posture for front-office analytics
display paths: browser and Workbench UI rendering, gateway/BFF delivery, backend analytics API
fan-out, user-visible freshness/degraded states, safe attention events, audit-relevant reads, and
operator diagnostics.

The platform pattern must trace browser to gateway to backend execution for page load, panel
hydration, API fan-out, calculation freshness, empty states, degraded widgets, user-visible stale
data, and frontend/backend correlation without copying sensitive product content into telemetry.

Implementation must start with one canonical Workbench analytics path, using
`PB_SG_GLOBAL_BAL_001` unless a later slice records a stronger source-backed reason. The first-wave
goal is not to instrument every page. It is to prove a reusable browser-to-gateway-to-backend
observability pattern with UI-specific privacy, entitlement, and user-experience semantics.

## Critical Review Outcome

The idea is correct, but it must not be implemented by casually copying RFC-0105 backend reporting
patterns into the UI.

Key differences:

1. reporting observability tracks asynchronous evidence production: jobs, snapshots, render,
   archive, rerender, regenerate, replay, and batch attention,
2. analytics UI observability tracks interactive read/display flows: route load, panel hydration,
   BFF fan-out, backend calculation freshness, empty states, degraded widgets, entitlement-aware
   display, and user-visible stale data,
3. UI telemetry can accidentally expose client names, portfolio ids, holdings, screen content,
   advisor behavior, entitlement failures, or screenshots,
4. UI metrics and traces require a stricter allowed/forbidden field model than backend job metrics,
5. dashboard and alert claims must reference only implemented metrics and proven browser/API
   behavior,
6. supported-features must not promote operational observability until browser, gateway, backend,
   dashboard, and no-sensitive-content evidence exist.

Gold-pass conclusion: RFC-0108 is implementation-ready as a governed execution guide. Actual
implementation remains unstarted.

## Gold-Pass Readiness Assessment

| Review area | Gold-pass finding | Required implementation posture |
| --- | --- | --- |
| Scope clarity | RFC-0108 owns interactive analytics UI observability, not reporting job operations. | Do not reopen RFC-0105 reporting flows; consume its vocabulary only where platform-wide concepts overlap. |
| Privacy | Browser telemetry carries higher content-leak risk than backend operation metrics. | Define allowed fields and forbidden fields before adding UI telemetry, logs, traces, screenshots, breadcrumbs, or replay artifacts. |
| Source backing | User-visible state must come from gateway/backing services, not decorative UI inference. | Every panel state must map to supported gateway/backend posture: loading, ready, empty, partial, stale, degraded, error, or permission-blocked. |
| Correlation | The platform needs browser-to-gateway-to-backend traceability. | Propagate correlation and trace identifiers without exposing portfolio, client, holding, or entitlement data as labels. |
| Operations | Operators need attention events for user-visible degradation. | Emit bounded attention events for actionable degradation only; do not alert on unsupported or unimplemented metrics. |
| Proof | UI observability requires browser evidence plus API/backend evidence. | Closure requires Playwright/browser artifacts, gateway/API evidence, backend logs/metrics, dashboard validation, and sensitive-data assertions. |
| Closure | Documentation, wiki, context, supported-features, skills guidance, and branch hygiene are part of readiness. | Close only after docs, wiki source, context, PR evidence, and local branches are synchronized. |

## Pre-Implementation No-Go Gates

Implementation must not begin until the first implementation branch records:

1. canonical Workbench route or panel set in scope,
2. canonical portfolio id, defaulting to `PB_SG_GLOBAL_BAL_001`,
3. gateway/BFF endpoints used by the route,
4. backend services in the fan-out path,
5. current source for freshness, supportability, partial, stale, unavailable, empty, and
   permission-blocked states,
6. current caller-context and entitlement source used by the UI and gateway,
7. allowed telemetry fields and forbidden telemetry fields,
8. browser evidence strategy,
9. dashboard and alert contract strategy,
10. CI lanes and canonical front-office validation commands required before merge.

If one of these is unknown, the first slice must resolve it or narrow scope before adding telemetry.

## Mandatory Privacy And No-Sensitive-Content Controls

RFC-0108 telemetry must be identifier-safe by default.

Forbidden in logs, metrics labels, traces, browser breadcrumbs, screenshots intended for operator
evidence, replay artifacts, dashboard variables, and alert annotations unless a later security RFC
explicitly certifies a safe exception:

1. client names,
2. household names,
3. account numbers,
4. portfolio ids as labels or metric dimensions,
5. instrument names or identifiers,
6. holdings,
7. transaction-level details,
8. raw entitlement failures,
9. screen text captured as telemetry payload,
10. raw API request or response bodies,
11. advisor free-text notes,
12. document ids or archive object references,
13. trace ids or correlation ids as metric labels.

Allowed first-wave telemetry fields:

1. route key,
2. panel key,
3. service key,
4. operation key,
5. supportability state,
6. freshness bucket,
7. degraded reason code,
8. empty-state reason code,
9. entitlement posture code,
10. latency bucket,
11. status code class,
12. bounded error category,
13. region code only where already safe and non-sensitive,
14. environment key.

No implementation may add high-cardinality or sensitive labels to improve debugging convenience.
Operator lookup must use protected diagnostics APIs rather than public metrics labels.

## User-Visible State Vocabulary

Every analytics panel in first-wave scope must classify the displayed state as one of:

| State | Meaning | Required UI/telemetry posture |
| --- | --- | --- |
| `loading` | Request or hydration in progress | Skeleton or stable loading state, no misleading stale data claim. |
| `ready` | Data is complete enough for normal advisor use | As-of date, benchmark/mandate/currency/unit, and source posture visible or one click away. |
| `empty` | Source-backed business condition has no data | Empty reason code; no generic failure wording. |
| `partial` | Some sources available and some missing | Available data remains visible; missing source/capability reason is explicit. |
| `stale` | Data exists but freshness objective is breached | Freshness bucket and safe interpretation guidance. |
| `degraded` | Panel is usable with reduced supportability | Bounded degraded reason and attention event when operator action is required. |
| `error` | Panel cannot render useful data | Product-safe error, support reference or correlation id where allowed. |
| `permission_blocked` | Caller is not entitled or workflow does not allow display | No leakage of restricted portfolio, client, holding, or entitlement detail. |
| `unsupported` | Capability is not implemented or not certified | Supported-features remains planned; no decorative workaround. |

## Target Scope

In scope:

1. platform analytics UI observability contract,
2. browser-to-gateway-to-backend correlation and trace propagation,
3. structured frontend logs/events with bounded fields,
4. gateway/BFF request and fan-out telemetry alignment,
5. backend analytics service telemetry alignment for the selected panels,
6. panel hydration, render, error, degraded, stale, empty, and permission-blocked state metrics,
7. user-visible attention events for actionable degradation,
8. audit events for privileged/operator actions and entitlement-relevant analytics reads where
   supported,
9. no-sensitive-content controls for UI logs, metrics, traces, screenshots, breadcrumbs, and replay
   artifacts,
10. dashboard and alert contracts tied only to implemented metrics,
11. canonical Workbench proof through `PB_SG_GLOBAL_BAL_001`,
12. supported-features governance for analytics UI observability claims.

Out of scope:

1. reporting job/rerender/regenerate/replay behavior already owned by RFC-0105,
2. final reporting security certification owned by RFC-0106,
3. final enterprise reporting production certification owned by RFC-0107,
4. full Workbench scheduler-management or reporting document retrieval unless included by a later
   approved scope,
5. broad user behavior analytics or advisor productivity tracking,
6. session replay of screen content,
7. telemetry containing client, portfolio, holding, or transaction content,
8. decorative trust or health badges not backed by gateway/platform evidence.

## Architecture Direction

The first-wave architecture is:

1. `lotus-workbench` creates or preserves a route-level correlation id and trace context,
2. Workbench BFF/API calls propagate correlation and trace headers to `lotus-gateway`,
3. `lotus-gateway` propagates safe identifiers to `lotus-performance`, `lotus-risk`, and other
   domain services used by the selected analytics panels,
4. each service emits bounded metrics/logs using the platform contract,
5. Workbench emits panel-level hydration/render/state events without sensitive content,
6. platform dashboards consume implemented metric names only,
7. attention events are produced only for actionable user-visible degradation,
8. diagnostics APIs provide protected lookup paths where operators need detail beyond metrics.

Workbench must not call raw backend services directly. Gateway/BFF remains the product-facing
integration boundary.

## Required Metric Families

First-wave metric names and labels must be contract-defined before implementation. Candidate
families:

| Metric family | Owner | Required bounded labels |
| --- | --- | --- |
| `lotus_workbench_panel_hydration_duration_seconds` | `lotus-workbench` | `route`, `panel`, `state`, `freshness_bucket` |
| `lotus_workbench_panel_state_total` | `lotus-workbench` | `route`, `panel`, `state`, `reason` |
| `lotus_workbench_api_request_duration_seconds` | `lotus-workbench` BFF | `route`, `operation`, `status_class` |
| `lotus_gateway_analytics_fanout_duration_seconds` | `lotus-gateway` | `operation`, `service`, `status_class` |
| `lotus_gateway_analytics_degraded_total` | `lotus-gateway` | `operation`, `service`, `reason` |
| `lotus_analytics_freshness_bucket_total` | domain services | `service`, `product`, `freshness_bucket`, `supportability_state` |
| `lotus_analytics_ui_attention_events_total` | platform/gateway/workbench | `route`, `panel`, `attention_type`, `severity` |

Forbidden metric labels:

1. `portfolio_id`,
2. `client_id`,
3. `client_name`,
4. `household_id`,
5. `account_id`,
6. `instrument_id`,
7. `holding_id`,
8. `transaction_id`,
9. `trace_id`,
10. `correlation_id`,
11. `document_id`,
12. `advisor_id`,
13. raw route params.

## Implementation Slices

### Slice 0: Platform Automation And Telemetry Scaffolding

Purpose: create the governed analytics UI observability scaffold before telemetry is emitted.

Required work:

1. create platform contract directories and validator entry points for analytics UI telemetry,
2. define the expected evidence artifact layout for browser, gateway, backend, dashboard, and
   sensitive-data proof,
3. add validator coverage that rejects missing contract files before implementation starts,
4. update platform context and skill routing if this becomes a repeatable implementation pattern,
5. identify the canonical Workbench route and panel set for Slice 1.

Exit criteria:

1. contract and validator tests pass,
2. no Workbench telemetry is emitted before the contract exists,
3. first-wave route/panel scope is recorded.

### Slice 1: Cleanup And Structure

Purpose: prepare Workbench and gateway code structure without changing product claims.

Required work:

1. identify existing panel state handling and telemetry/logging patterns,
2. remove duplicate or stale local observability helpers if encountered,
3. centralize Workbench analytics observability vocabulary in one module,
4. centralize gateway analytics fan-out telemetry vocabulary in one module,
5. keep supported-features planned until proof exists.

Exit criteria:

1. no duplicate route/panel telemetry vocabulary remains in the first-wave path,
2. focused lint/type/unit tests pass,
3. no UI feature claim is promoted.

### Slice 2: Telemetry Contract

Purpose: define the frontend/backend telemetry contract before product instrumentation.

Required work:

1. add the analytics UI observability contract for frontend/backend telemetry names, allowed
   labels, forbidden fields, severity levels, state vocabulary, attention event types, and evidence
   requirements,
2. define metric names, log event names, trace attributes, attention-event attributes, audit-event
   attributes, dashboard references, and alert references,
3. define no-sensitive-content controls for logs, metrics, traces, breadcrumbs, audit records,
   screenshots, replay artifacts, and evidence bundles,
4. add validator coverage that rejects forbidden labels and unimplemented dashboard metric
   references,
5. record how protected diagnostics APIs may be used when metrics intentionally omit sensitive
   lookup detail.

Exit criteria:

1. contract and validator tests pass,
2. dashboard and alert definitions cannot reference unimplemented metrics,
3. forbidden fields fail validation before runtime instrumentation exists.

### Slice 3: Browser-To-Gateway Trace And Correlation Propagation

Purpose: prove correlation and trace propagation through the interactive analytics path.

Required work:

1. preserve or create browser route correlation id,
2. propagate safe headers from Workbench/BFF to gateway,
3. propagate safe headers from gateway to backend services,
4. add tests for valid and malformed trace contexts,
5. keep trace and correlation identifiers out of metric labels.

Exit criteria:

1. browser/API tests prove propagation,
2. backend tests prove header forwarding,
3. no malformed `traceparent` is emitted,
4. no sensitive identifiers are added as labels.

### Slice 4: Gateway And Analytics Backend Structured Logging

Purpose: align API delivery telemetry with UI state without leaking content.

Required work:

1. add gateway fan-out duration, request, structured-log, and degraded reason telemetry for selected
   analytics operations,
2. align backend freshness/supportability fields with the UI state contract,
3. add gateway/backend tests for partial and unavailable sources,
4. preserve source ownership: `lotus-performance` and `lotus-risk` own their analytics truth,
5. ensure protected diagnostics provide operator lookup paths without exposing sensitive labels.

Exit criteria:

1. gateway telemetry reconciles with Workbench panel states,
2. backend contracts expose enough source-backed freshness/supportability evidence,
3. unsupported state is not faked by the UI.

### Slice 5: Metrics, Dashboards, Alerts, And Freshness Contracts

Purpose: expose operational posture through implemented metrics only.

Required work:

1. instrument selected panels for hydration duration and state transitions,
2. classify ready, empty, partial, stale, degraded, error, permission-blocked, and unsupported
   states,
3. surface as-of date, benchmark/mandate/currency/unit, and supportability posture where the panel
   displays analytics,
4. add Grafana dashboard panels for implemented Workbench/gateway/backend metric families,
5. add alert rules only for implemented metrics and thresholds,
6. add unit, browser, and contract tests for state classification, freshness buckets, dashboards,
   and alert references.

Exit criteria:

1. state vocabulary is used consistently,
2. tests cover at least ready, empty, stale/degraded, error, and permission-blocked states,
3. dashboard loads with implemented metrics,
4. alert rules validate,
5. telemetry excludes sensitive content.

### Slice 6: UI State And Attention Events

Purpose: distinguish actionable user-visible degradation from normal telemetry.

Required work:

1. emit bounded attention events for stale, degraded, or repeated panel failures when operator
   action is required,
2. map attention events to user-visible state and source-backed reason codes,
3. avoid broad behavior analytics or screen-content capture,
4. add tests for attention deduplication, bounded severity, and field safety.

Exit criteria:

1. attention events are source-backed and actionable,
2. attention events avoid client/portfolio/holding content,
3. unsupported attention behavior remains planned.

### Slice 7: Audit Events For Entitlement-Relevant Reads And Privileged Actions

Purpose: make entitlement-relevant analytics reads and privileged/operator actions auditable where
supported.

Required work:

1. emit audit events for entitlement-relevant analytics reads where supported by the caller-context
   and entitlement model,
2. emit audit events for privileged/operator actions related to diagnostics, suppression, or
   protected lookup,
3. avoid raw entitlement failures and avoid restricted client, portfolio, holding, or screen
   content,
4. add allow/deny and field-safety tests for audit behavior.

Exit criteria:

1. audit events are bounded and source-backed,
2. unsupported audit behavior remains planned,
3. audit records can be reconciled with gateway/backend evidence without sensitive telemetry labels.

### Slice 8: Canonical Workbench Implementation Proof

Purpose: prove the path through a real Workbench analytics flow.

Required work:

1. bring up the governed front-office runtime,
2. validate the selected route/panels with `PB_SG_GLOBAL_BAL_001`,
3. capture browser evidence after API/calculation/panel validation passes,
4. capture gateway/API/backend logs and metrics for the same correlation path,
5. capture dashboard validation for implemented metrics and alert rules,
6. run sensitive-content assertions over evidence artifacts.

Exit criteria:

1. browser evidence, API evidence, backend telemetry, and dashboard proof reconcile,
2. no-sensitive-content assertions pass,
3. proof records route, panel, correlation id, trace id where safe, commit SHAs, and check names.

### Slice 9: Rollout Proof And Expansion Readiness

Purpose: prove the pattern can expand without broad unsupported claims.

Required work:

1. document which Workbench routes and panels are certified and which remain planned,
2. record the reusable rollout checklist for additional analytics UI surfaces,
3. prove contract validators catch at least one forbidden label and one unimplemented metric
   reference,
4. update supported-features only for implementation-backed behavior,
5. record residual debt and expansion blockers.

Exit criteria:

1. expansion guidance is source-backed by Slice 8 proof,
2. planned and supported observability claims are clearly separated,
3. residual scope is deliberate and documented.

### Second-Last Slice: Hardening, Review, And Certification

Purpose: complete code review, API certification, and governance audit before closure.

Required work:

1. review every telemetry field against the contract,
2. review all panel states for truthful backend support,
3. remove dead, duplicate, or decorative observability code,
4. certify OpenAPI and dashboard contracts,
5. verify GitHub CI lanes across platform, Workbench, gateway, and backend services,
6. record residual scope explicitly.

Exit criteria:

1. no P0/P1 privacy, telemetry, unsupported-feature, or panel-state finding remains,
2. CI and local proof are green,
3. residual scope is deliberate and documented.

### Final Slice: Closure

Purpose: close RFC-0108 with truthful product and operator documentation.

Required work:

1. update supported-features only for implementation-backed observability behavior,
2. update Workbench/gateway/backend docs and repo-local wiki source where operator truth changed,
3. update platform context, agent context, skills guidance, and RFC index,
4. publish wiki after merge where required,
5. clean branches and verify all affected repos are on clean `main`,
6. record final evidence in this RFC.

Exit criteria:

1. docs, wiki source, context, supported-features, and RFC evidence match merged implementation,
2. CI is green after merge,
3. local repos are clean before the next RFC starts.

## API And UI Certification Requirements

Every new or changed API, BFF route, dashboard, or panel involved in RFC-0108 must satisfy:

1. typed request and response contracts where API shape changes,
2. synthetic examples only,
3. product-safe errors,
4. no-sensitive-content logging and telemetry tests,
5. OpenAPI quality for gateway/backend APIs,
6. browser tests for route and panel state behavior,
7. dashboard/alert contract tests where metrics are consumed,
8. supported-features promotion only after proof.

## Supported Features Governance

Candidate supported-feature keys must remain planned until implementation-backed proof exists:

1. `workbench.analytics.observability.correlation_trace`,
2. `workbench.analytics.observability.panel_state_metrics`,
3. `workbench.analytics.observability.freshness_degraded_state`,
4. `workbench.analytics.observability.attention_events`,
5. `workbench.analytics.observability.safe_dashboard`,
6. `gateway.analytics.observability.fanout_metrics`,
7. `analytics.backend.observability.freshness_supportability`.

No key may be promoted from planned to supported until the relevant Workbench, gateway, backend,
dashboard, no-sensitive-content, and browser proof exists.

## Evidence Expectations

Required evidence before closure:

1. platform contract tests,
2. Workbench unit/integration/browser tests,
3. gateway API and fan-out tests,
4. backend analytics freshness/supportability tests,
5. dashboard/alert contract tests,
6. canonical front-office runtime proof,
7. Playwright/browser evidence for the selected route/panels,
8. gateway/API/backend log and metric evidence,
9. no-sensitive-content assertions over logs, metrics, traces, screenshots, and artifacts,
10. GitHub feature lane and PR merge gate evidence,
11. wiki synchronization and publication evidence where docs changed,
12. final clean-state branch hygiene evidence.

## Implementation Proof Ledger

| Slice | Evidence source | Command/API/artifact | Result | Follow-up |
| --- | --- | --- | --- | --- |
| Pre-implementation gold pass | This RFC revision | RFC tightened before implementation | Ready for implementation planning | Do not emit analytics UI telemetry until Slice 0 contract exists. |

## Final Gold-Pass Assessment

RFC-0108 is gold-pass ready as the governed implementation plan for analytics UI observability.
Implementation has not started. The expected first implementation step is Slice 0: platform
contract and scaffolding for frontend/backend analytics telemetry names, allowed labels, forbidden
fields, state vocabulary, attention events, and evidence requirements.
