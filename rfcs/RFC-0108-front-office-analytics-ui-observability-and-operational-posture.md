# RFC-0108: Front-Office Analytics UI Observability And Operational Posture

- Status: Implementation Started; Slice 1 Complete
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

Gold-pass conclusion: RFC-0108 is implementation-ready as a governed execution guide. Slice 0 and
Slice 1 are now implementation-backed; product telemetry, Workbench/gateway/backend runtime metrics,
dashboards, alerts, attention events, audit events, and canonical browser proof remain unstarted.

## Critical Review Findings And Gold-Standard Corrections

This gold-pass review intentionally looked for ambiguity before implementation starts. The
following findings are now corrected in this RFC:

| Finding | Why it would weaken implementation | Gold-standard correction |
| --- | --- | --- |
| Platform scaffolding was under-specified. | Teams would solve cross-cutting API, Swagger, logging, health, CI, and documentation gaps inside app-local slices. | Slice 0 now requires platform automation and app scaffolding improvements that benefit future Lotus applications, not only RFC-0108. |
| Cleanup/documentation scope was too narrow. | Observability work can leave duplicate docs, stale wiki truth, dead helpers, and unclear ownership. | Slice 1 now explicitly covers dead-code removal, repository structure, documentation structure, wiki source-of-truth placement, and wiki publication usability. |
| Proof slice stopped at browser evidence. | Screenshots or single happy-path captures can pass while gateway/backend/dashboard evidence is inconsistent. | Slice 8 now requires live end-to-end proof, critical evidence review, gap iteration, sensitive-data assertions, and reconciliation across browser, gateway, backend, dashboard, logs, and metrics. |
| API certification expectations were generic. | Gateway/BFF/backend endpoints might ship with weak Swagger, examples, error semantics, or untested failure behavior. | The second-last slice now makes API certification, Swagger quality, error handling, enterprise data mesh posture, and final quality tightening explicit. |
| Supported-features promotion was aspirational. | Feature flags or docs could claim observability before implementation-backed proof exists. | The supported-features section now distinguishes planned, implemented, and promoted states and requires evidence before any promotion. |
| CI and branch hygiene were implicit. | A long-running RFC branch could drift from checks or leave repos in an unclear state. | Delivery expectations now require remote branch tracking, GitHub checks, periodic monitoring, prompt fix-forward, PR evidence, post-merge verification, and clean local repos. |
| Skills/context review was not concrete. | Future agents could miss reusable patterns and repeat avoidable work. | Final closure now requires a conscious skills, guidance, documentation, and agent-context review with explicit change or no-change decisions. |

The RFC remains pre-implementation for product telemetry behavior. Slice 0 platform scaffolding and
Slice 1 Workbench/Gateway observability vocabulary foundations are implementation-backed. No
Workbench product metric, dashboard, API behavior change, attention event, audit event, or
runtime-emitted Workbench UI state is implementation-backed until the relevant slice records code,
tests, evidence, PRs, and merge state.

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

## Requirement Traceability

| Requirement | Owning slice(s) | Required evidence before claim |
| --- | --- | --- |
| Platform-level scaffolding improvements for repeatable concerns | Slice 0 | `lotus-platform` automation diff, scaffold tests, generated sample evidence, and context/wiki guidance where platform truth changes. |
| Cleanup and structure before feature expansion | Slice 1 | Dead-code search results, diff review, docs/wiki source-of-truth decision, and focused lint/unit evidence. |
| Browser-to-gateway-to-backend correlation | Slices 2-4 | Browser test, BFF/gateway API test, backend header-forwarding test, and malformed trace-context test. |
| UI state, freshness, degraded, empty, and error observability | Slices 2, 5, 6 | Unit/browser state tests, safe telemetry contract validation, and dashboard/metric reconciliation. |
| No-sensitive-content controls | Slices 2, 5-9, second-last slice | Contract validator, artifact grep/assertions, review checklist, and no forbidden labels in metrics/dashboards. |
| Attention events for actionable degradation | Slice 6 | Source-backed reason-code tests, deduplication tests, severity tests, and operator response documentation. |
| Audit events for entitlement-relevant reads and privileged actions | Slice 7 | Allow/deny tests, audit field-safety tests, caller-context proof, and unsupported-scope declaration where audit is deferred. |
| Canonical Workbench live proof | Slice 8 | Governed runtime evidence for `PB_SG_GLOBAL_BAL_001`, browser artifacts, gateway/API/backend artifacts, dashboard proof, and reconciliation notes. |
| Rollout readiness without overclaiming | Slice 9 | Certified route/panel list, planned route/panel list, supported-features update, rollout checklist, and residual-debt register. |
| Final production-grade review and closure | Second-last and final slices | Code review notes, API certification output, Swagger evidence, CI status, docs/context/wiki/supported-features updates, post-merge wiki publication, and clean repo status. |

## Dependency And Ownership Map

| Dependency | Owner | RFC-0108 use | Required posture |
| --- | --- | --- | --- |
| Canonical portfolio and demo-data invariants | `lotus-platform`, `lotus-workbench` | First proof dataset, defaulting to `PB_SG_GLOBAL_BAL_001`. | Use RFC-0076/RFC-0077 source truth; do not infer identities from UI fixtures. |
| Workbench analytics panels | `lotus-workbench` | Browser rendering, hydration, panel state, user-visible state, and frontend telemetry. | Consume gateway/BFF contracts only; no raw backend calls or fake unsupported states. |
| Gateway/BFF analytics delivery | `lotus-gateway` and Workbench BFF layer where present | API delivery, fan-out, trace propagation, safe diagnostics, and status normalization. | Preserve safe correlation/trace context and expose product-safe errors and OpenAPI examples. |
| Performance analytics | `lotus-performance` | Returns/performance panel data, freshness, and source supportability. | Domain service owns calculation truth, freshness, and supportability semantics. |
| Risk analytics | `lotus-risk` | Risk panel data, freshness, and source supportability. | Domain service owns risk metric truth, freshness, and supportability semantics. |
| Portfolio identity and entitlement context | `lotus-core`, `lotus-gateway` | Portfolio/caller context, entitlement-relevant read posture, and audit inputs. | Do not leak restricted identifiers or raw entitlement failures into telemetry. |
| Platform observability and dashboards | `lotus-platform` | Contracts, validators, dashboards, alert rules, evidence expectations, and governance hooks. | Dashboard and alert references must be generated or validated against implemented metrics only. |

## Delivery And Branch Hygiene Expectations

Implementation work must use GitHub deliberately:

1. create or continue a remote feature branch for each implementation slice,
2. keep commits small, meaningful, and scoped to the slice,
3. push early enough for GitHub checks to run asynchronously,
4. monitor checks at regular intervals while continuing non-conflicting work,
5. fix failures promptly and record the real failing check, root cause, and fix,
6. do not allow stale branches, failing checks, or dirty local repos to become normal,
7. open PRs only when the slice is implementation-ready and the local validation story is truthful,
8. keep PR descriptions aligned with actual commands, artifacts, endpoints, routes, panels, commits,
   and evidence paths,
9. after merge, verify `main`, publish wiki changes where required, and return affected repos to a
   clean state before moving to the next slice.

Branch hygiene is an implementation requirement, not an administrative afterthought.

## Cross-Slice Acceptance Criteria

RFC-0108 is not complete until all of the following are true:

1. all promoted supported-features entries are implementation-backed,
2. every changed API, BFF route, dashboard, alert, and panel state has focused tests,
3. every new or changed API follows the certification pattern and has high-quality Swagger,
4. every operator-facing metric/dashboard/alert references implemented metrics only,
5. no metrics label, trace attribute, log field, browser event, screenshot evidence, or dashboard
   variable carries forbidden sensitive content,
6. Workbench, gateway, and backend evidence reconcile for the same canonical flow,
7. proof includes failure, stale, degraded, empty, permission-blocked, and happy paths where the
   first-wave scope supports them,
8. docs, wiki source, platform context, supported-features, and skills/guidance decisions match the
   merged implementation,
9. GitHub feature-lane and PR-merge-gate checks are green or every deviation is explicit and
   approved,
10. affected local repos are clean and on the expected branch at closure.

## Risk Register

| Risk | Impact | Mitigation | Owning slice |
| --- | --- | --- | --- |
| Sensitive client or portfolio content leaks into UI telemetry. | Regulatory and client confidentiality breach. | Contract-first allowed/forbidden fields, no-sensitive-content tests, artifact grep/assertions, and second-last field review. | Slices 2, 5-9, second-last slice |
| UI claims observability for unsupported or unimplemented backend behavior. | False operator confidence and product trust damage. | Supported-features governance, source-backed panel state mapping, and rollout readiness review. | Slices 1, 5, 9 |
| Dashboard or alert rules reference metrics that do not exist. | Broken operations posture and noisy/on-paper observability. | Dashboard/alert contract validators and implemented-metric inventory. | Slices 2, 5, 9 |
| Correlation identifiers become high-cardinality metric labels. | Metrics cardinality explosion and possible diagnostic leakage. | Explicit forbidden-label validation and diagnostics API separation. | Slices 2-4 |
| Platform scaffolding gaps repeat across apps. | Tech debt spreads into each implementation repo. | Slice 0 improves app scaffolding automation and default governance hooks in `lotus-platform`. | Slice 0 |
| Evidence is superficial. | Implementation closes without proving real user/operator behavior. | Slice 8 requires live proof, critical evidence review, reconciliation, and iteration until gaps are fixed. | Slice 8 |
| CI drifts while long-running work continues. | Late merge failures and unclear branch quality. | Remote branch, asynchronous checks, periodic monitoring, prompt fix-forward, and PR evidence discipline. | All slices |

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

### Slice 0: Platform Automation And Scaffolding Improvement

Purpose: fix repeatable platform and scaffolding gaps before telemetry is emitted.

Required work:

1. identify gaps in `lotus-platform` automation that should already be handled as platform
   scaffolding instead of app-local reinvention,
2. improve `lotus-platform` automation so repeatable gaps are fixed at the platform level,
3. identify cross-cutting concerns that future Lotus apps should receive by default, including API
   certification pattern, Swagger quality, observability, health/liveness/readiness endpoints,
   structured logging, product-safe error handling, test scaffolding, CI defaults, documentation
   scaffolding, governance hooks, supported-features placeholders, and evidence-pack layout,
4. ensure documentation scaffolding, governance hooks, supported-features placeholders, and
   evidence-pack layout are generated consistently instead of copied into each app,
5. ensure API certification pattern defaults are explicit in generated service scaffolds,
6. improve app scaffolding automation so future apps start with these defaults under governance from
   day one,
7. create platform contract directories and validator entry points for analytics UI telemetry,
8. define the expected evidence artifact layout for browser, gateway, backend, dashboard, and
   sensitive-data proof,
9. add validator coverage that rejects missing contract files before implementation starts,
10. update platform context and skill routing if this becomes a repeatable implementation pattern,
11. identify the canonical Workbench route and panel set for Slice 1,
12. during later slices, if more platform or scaffolding gaps are discovered, improve the platform
    scaffold instead of leaving repeatable fixes local to an app.

Exit criteria:

1. contract and validator tests pass,
2. scaffolding tests prove generated apps receive the improved baseline,
3. no Workbench telemetry is emitted before the contract exists,
4. first-wave route/panel scope is recorded,
5. any app-local workaround for repeatable concerns is either removed or converted into a platform
   default.

### Slice 1: Cleanup And Structure

Purpose: prepare Workbench and gateway code structure without changing product claims.

Required work:

1. identify existing panel state handling and telemetry/logging patterns,
2. remove duplicate or stale local observability helpers if encountered,
3. centralize Workbench analytics observability vocabulary in one module,
4. centralize gateway analytics fan-out telemetry vocabulary in one module,
5. remove dead code and unused documentation fragments exposed by the observability review,
6. improve repository structure where needed so analytics observability contracts, dashboard
   definitions, tests, and evidence are discoverable,
7. improve document structure and reduce sprawl,
8. move long-lived operator or governance material to repo-local wiki source when it belongs there,
9. avoid duplicate documentation across repo docs and wiki source; record the source-of-truth
   decision,
10. ensure wiki source is usable and publishable,
11. keep supported-features planned until proof exists.

Exit criteria:

1. no duplicate route/panel telemetry vocabulary remains in the first-wave path,
2. focused lint/type/unit tests pass,
3. no UI feature claim is promoted,
4. wiki source reflects the intended post-RFC state where operator truth changed,
5. duplicate documentation is removed or intentionally linked from one source of truth.

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
6. run sensitive-content assertions over evidence artifacts,
7. critically review the evidence instead of accepting artifact existence as proof,
8. identify gaps, inconsistencies, false positives, missing state coverage, and loose ends,
9. iterate on implementation and evidence until the first-wave scope is genuinely gold standard.

Exit criteria:

1. browser evidence, API evidence, backend telemetry, and dashboard proof reconcile,
2. no-sensitive-content assertions pass,
3. proof records route, panel, correlation id, trace id where safe, commit SHAs, and check names,
4. critical review findings are either fixed or explicitly deferred with owner, reason, and next
   action,
5. the proof ledger distinguishes implementation-backed behavior from planned rollout behavior.

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
6. verify platform governance and enterprise data mesh standards are met,
7. ensure all APIs added or changed by RFC-0108 are properly certified,
8. ensure Swagger is complete and high quality:
   - endpoints are grouped correctly,
   - every endpoint has clear what/when/how guidance,
   - full request and response examples exist,
   - every attribute has description, type, and example value,
   - product-safe error examples are present,
9. ensure error handling is complete, correct, and properly tested,
10. make final quality improvements before closure,
11. record residual scope explicitly.

Exit criteria:

1. no P0/P1 privacy, telemetry, unsupported-feature, or panel-state finding remains,
2. API certification, Swagger, error-handling, dashboard, and enterprise-governance checks pass,
3. CI and local proof are green,
4. residual scope is deliberate and documented.

### Final Slice: Closure

Purpose: close RFC-0108 with truthful product and operator documentation.

Required work:

1. update supported-features only for implementation-backed observability behavior,
2. update Workbench/gateway/backend docs and repo-local wiki source where operator truth changed,
3. update platform context, agent context, skills guidance, and RFC index,
4. consciously review whether skills, guidance, documentation, or agent context should be added,
   removed, tightened, or clarified to improve future work, faster ramp-up, and stronger agent
   effectiveness,
5. if no skill/guidance/context change is needed, record that as an explicit deliberate outcome,
6. publish wiki after merge where required,
7. clean branches and verify all affected repos are on clean `main`,
8. record final evidence in this RFC.

Exit criteria:

1. docs, wiki source, context, supported-features, and RFC evidence match merged implementation,
2. CI is green after merge,
3. skill/guidance/context review has an explicit change or no-change decision,
4. local repos are clean before the next RFC starts.

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

Candidate supported-feature keys must remain planned until implementation-backed proof exists.

| Supported-feature key | Initial status | Owner | Promotion evidence |
| --- | --- | --- | --- |
| `platform.scaffolding.analytics_ui_observability_baseline` | Implemented | `lotus-platform` | Slice 0 adds app scaffolding automation for product-safe errors, structured JSON events, supported-features placeholders, RFC evidence scaffolding, operations/API-certification docs, generated-app tests, and analytics UI observability contract validation. |
| `workbench.analytics.observability.correlation_trace` | Planned | `lotus-workbench` | Browser/BFF trace propagation tests, gateway/backend reconciliation, and no forbidden metric labels. |
| `workbench.analytics.observability.contract_vocabulary` | Implemented | `lotus-workbench` | Slice 1 adds code-owned analytics UI observability vocabulary and tests for allowed labels, forbidden sensitive fields, state vocabulary, and planned Workbench metric-family names without emitting product telemetry. |
| `workbench.analytics.observability.panel_state_metrics` | Planned | `lotus-workbench` | Panel state tests for ready, empty, partial, stale, degraded, error, permission-blocked, and unsupported where in scope. |
| `workbench.analytics.observability.freshness_degraded_state` | Planned | `lotus-workbench`, `lotus-performance`, `lotus-risk` | Source-backed freshness/supportability contract proof and browser validation. |
| `workbench.analytics.observability.attention_events` | Planned | `lotus-workbench`, `lotus-platform` | Attention-event contract, deduplication tests, severity tests, and operator response docs. |
| `workbench.analytics.observability.entitlement_audit_events` | Planned | `lotus-workbench`, `lotus-gateway`, `lotus-core` | Caller-context proof, allow/deny audit tests, and sensitive-field assertions. |
| `workbench.analytics.observability.safe_dashboard` | Planned | `lotus-platform` | Dashboard validation against implemented metrics and forbidden-variable tests. |
| `gateway.analytics.observability.fanout_metrics` | Planned | `lotus-gateway` | Fan-out metric/log tests, backend reconciliation, and OpenAPI/API certification evidence where API shape changes. |
| `gateway.analytics.observability.contract_vocabulary` | Implemented | `lotus-gateway` | Slice 1 adds code-owned analytics UI observability vocabulary and tests for allowed labels, forbidden sensitive fields, state vocabulary, and planned gateway metric-family names without emitting fan-out metrics. |
| `analytics.backend.observability.freshness_supportability` | Planned | `lotus-performance`, `lotus-risk` | Backend freshness/supportability tests and gateway/Workbench state reconciliation. |

No key may be promoted from planned to supported until the relevant Workbench, gateway, backend,
dashboard, no-sensitive-content, and browser proof exists.

Any final implementation closure must update this table with implementation-backed status,
evidence links, and residual planned items. Aspirational wording in docs, wiki, dashboards, route
metadata, panel registry entries, or supported-features files is prohibited.

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

Evidence review rules:

1. artifact existence is not proof; the implementation owner must inspect the content,
2. browser evidence must reconcile with API/backend evidence for the same route, panel, commit, and
   correlation path,
3. dashboard evidence must reference implemented metrics and must not rely on placeholder panels,
4. sensitive-data assertions must run over generated evidence artifacts, not only source files,
5. each failed or flaky check must be triaged with root cause and fix-forward evidence,
6. final closure evidence must state what remains unsupported and why.

## Implementation Proof Ledger

| Slice | Evidence source | Command/API/artifact | Result | Follow-up |
| --- | --- | --- | --- | --- |
| Pre-implementation gold pass | PR #225 / commit `755be9a` | RFC tightened before implementation | Ready for implementation planning | Do not emit analytics UI telemetry until Slice 0 contract exists. |
| Slice 0: platform automation and scaffolding improvement | `automation/New-Lotus-Service.ps1`; `context/contracts/analytics-ui-observability-contract.json`; `automation/validate_analytics_ui_observability_contract.py`; scaffold contract tests | `python -m pytest tests\unit\test_repository_hygiene_scaffold_contract.py -q`; `python -m pytest tests\unit\test_analytics_ui_observability_contract.py -q`; `python automation\validate_analytics_ui_observability_contract.py` | Complete for platform scaffold baseline | Workbench/gateway/backend implementation remains planned for later slices. |
| Slice 0 heartbeat advisory | `output/heartbeat/heartbeat-status.md` generated locally, not committed as source truth | `powershell -ExecutionPolicy Bypass -File automation\Run-Heartbeat.ps1 -Branch feature/rfc-0108-analytics-ui-observability` | Succeeded with `attention_required` from historical failed background-run ledger entries and stale mesh certification evidence | Advisory findings are not Slice 0 blockers; GitHub PR checks remain source truth for PR health. |
| Slice 1: cleanup and structure | `lotus-workbench/src/features/analytics-observability/contract.ts`; `lotus-gateway/src/app/observability/analytics_ui.py`; repo-local wiki operations runbooks | `npm run test -- tests/unit/analytics-observability-contract.test.ts`; `python -m pytest tests\unit\test_analytics_ui_observability_contract.py -q` | Complete locally for code-owned observability vocabulary foundations | Product telemetry, fan-out metrics, dashboards, attention events, audit events, and browser proof remain planned. |

## Final Gold-Pass Assessment

RFC-0108 is gold-pass ready as the governed implementation plan for analytics UI observability.
Slice 0 is complete for platform automation and scaffolding improvement. Slice 1 is complete for
cleanup and structure: Workbench and Gateway now have code-owned analytics UI observability
vocabulary modules, focused tests reject sensitive/ad hoc labels, repo-local wiki operations
runbooks identify the source of truth, and supported-features governance records only the
implementation-backed contract vocabulary foundations.

Implementation must not move to product telemetry until Slice 2 telemetry contract work is
completed and validated. Workbench, gateway, backend metrics, dashboards, alerts, attention events,
audit events, and canonical `PB_SG_GLOBAL_BAL_001` browser proof remain planned.
