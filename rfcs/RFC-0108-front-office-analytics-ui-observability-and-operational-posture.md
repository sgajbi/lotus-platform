# RFC-0108: Front-Office Analytics UI Observability And Operational Posture

- Status: Reopened For Ecosystem Completion; Slice 17 Ecosystem Hardening Certified
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
  - `lotus-manage` owners where management and operations panels or data products are included
  - `lotus-report`, `lotus-render`, `lotus-archive`, and `lotus-ai` owners where their product,
    evidence, document, archive, or AI-backed surfaces participate in the unified user journey
- Target repositories:
  - `lotus-platform`
  - `lotus-workbench`
  - `lotus-gateway`
  - `lotus-performance`
  - `lotus-risk`
  - `lotus-core`
  - `lotus-advise`
  - `lotus-manage`
  - `lotus-report`
  - `lotus-render`
  - `lotus-archive`
  - `lotus-ai`
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
  - RFC-0108 is now reopened to add required ecosystem-completion slices that remove the
    remaining planned analytics UI observability gaps and extend the same operational posture
    uniformly across the Lotus ecosystem.

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

Gold-pass conclusion: RFC-0108 remains the governed execution guide. The first-wave scope is
implementation-backed through final closure, and the RFC is now reopened for required ecosystem
completion slices. Slice 0, Slice 1, Slice 2, Slice 3, Slice 4, Slice 5, Slice 6, Slice 7, and
Slice 8 are implementation-backed. Slice 2 adds the platform
telemetry contract and code-owned Workbench/Gateway constants for event names, severity levels,
attention/audit event types, trace attributes, dashboard/alert reference policy, and protected
diagnostics policy. Slice 3 adds browser/BFF/gateway/backend correlation and trace propagation
without emitting product telemetry. Slice 4 adds product-safe Gateway structured fan-out logs for
selected Workbench performance and risk analytics operations. Slice 5 adds first-wave Workbench
browser metric events, a Prometheus text scrape route, platform dashboard panels, and alert rules
for selected performance-summary, performance-details, and risk-summary analytics reads. Slice 6
adds bounded Workbench attention events for stale, degraded, partial-source, and repeated-failure
selected analytics panel states. Slice 7 adds product-safe Gateway analytics read audit logs for
selected Workbench performance and risk analytics reads, with successful upstream reads emitting
bounded `analytics_read_allowed` events and upstream `401`/`403` denials emitting bounded
`analytics_read_denied` events. Slice 8 adds platform-owned canonical proof review and live
governed Workbench proof for `PB_SG_GLOBAL_BAL_001`, including API checks, browser screenshots,
calculation sanity, panel classifications, Workbench `/api/metrics` exposure, dashboard/alert
metric reconciliation, and sensitive-content assertions. The reopened ecosystem-completion wave now
requires backend freshness/supportability metrics, full caller-context entitlement certification,
all supported Workbench surfaces, all UI-facing Gateway fan-out path rollout, and all Lotus app
supportability signals to be implemented before overall RFC-0108 closure.

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

Slice 0 platform scaffolding, Slice 1 Workbench/Gateway observability vocabulary foundations,
Slice 2 telemetry-contract governance, Slice 3 correlation propagation, Slice 4 Gateway structured
fan-out logs, Slice 5 first-wave Workbench metrics/dashboard/alert contracts, Slice 6 Workbench
attention events, Slice 7 Gateway analytics read audit events, Slice 8 canonical Workbench proof,
and Slice 13 selected Gateway fan-out metrics, protected diagnostics lookup, expanded central
Gateway client fan-out coverage, and direct `lotus-core` query/control-plane plus ingestion
fan-out coverage are implementation-backed. Backend freshness metrics, full caller-context
entitlement certification, and broad Workbench rollout remain planned until later slices record
code, tests, evidence, PRs, and merge state.

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
4. broad user behavior analytics or advisor productivity tracking,
5. session replay of screen content,
6. telemetry containing client, portfolio, holding, or transaction content,
7. decorative trust or health badges not backed by gateway/platform evidence.

## Ecosystem Completion Extension

The first-wave implementation proved the pattern for selected Workbench performance and risk
analytics flows. That is no longer sufficient for the desired Lotus posture. RFC-0108 now requires
the same observability and operational supportability standard to be completed across the whole
Lotus ecosystem.

The ecosystem-completion wave must not dilute the privacy and supported-features rules that made
the first wave safe. It must instead expand them uniformly. Slices 10 and 11 are implemented:
Slice 10 adds the ecosystem contract plus validator-protected per-app gap matrix before runtime
work resumes, and Slice 11 makes the platform scaffold and CI posture enforce the uniform baseline
for future backend services and Workbench/UI surfaces.

Required ecosystem coverage:

1. `lotus-workbench`: all supported front-office routes, panels, BFF routes, user-visible state,
   attention events, screenshots, and browser proof.
2. `lotus-gateway`: all UI-facing fan-out paths, request correlation, safe structured logs,
   latency/error/degraded metrics, entitlement-relevant read audits, and protected diagnostics.
3. `lotus-core`: portfolio, booking, account, holding, mandate, transaction, and entitlement
   supportability signals that downstream UI surfaces depend on.
4. `lotus-performance`: performance freshness, completeness, calculation supportability,
   period-quality signals, and degraded-source reasons.
5. `lotus-risk`: risk freshness, completeness, calculation supportability, concentration/drawdown
   data-quality signals, and degraded-source reasons.
6. `lotus-advise`: advisory proposal, recommendation, suitability, and decision-support
   supportability signals where Workbench renders advisory UI surfaces.
7. `lotus-manage`: management action register, mandate operations, task/action workflow, and
   operational posture signals where Workbench or Gateway exposes management surfaces.
8. `lotus-report`: report evidence-pack supportability signals that intersect front-office
   evidence surfaces, while keeping RFC-0105 reporting job operations as their own domain.
9. `lotus-render`: rendering-service health, latency, degradation, and deterministic output
   supportability signals consumed by reporting/evidence surfaces.
10. `lotus-archive`: archive retrieval, retention, legal-hold, access-audit, and document
    availability supportability signals consumed by evidence surfaces.
11. `lotus-ai`: AI-backed feature supportability, degraded/unavailable model posture, bounded
    workflow-pack status, and no-sensitive-content telemetry where AI-backed surfaces are exposed.
12. `lotus-platform`: cross-repo contracts, scaffolding, validators, dashboards, alerts,
    runbooks, CI gates, wiki/context governance, and final proof aggregation.

Uniform posture means every included app must have, at minimum:

1. health/liveness/readiness and service metadata posture aligned with platform scaffold rules,
2. request correlation and trace propagation where it participates in a user journey,
3. structured product-safe logs for successful, degraded, denied, and failed paths,
4. bounded metrics for latency, error, freshness, degraded state, empty state where relevant, and
   operator attention,
5. OpenAPI/Swagger quality and examples for all changed HTTP APIs,
6. product-safe problem-details errors and tested failure handling,
7. entitlement-relevant read and privileged/operator action audit events where applicable,
8. protected diagnostics lookup instead of leaking identifiers into metrics, logs, screenshots, or
   dashboard labels,
9. dashboard and alert references that use implemented metrics only,
10. repo-local docs/wiki source and supported-features updates backed by proof,
11. evidence that browser, gateway, backend, dashboard, logs, metrics, and no-sensitive assertions
    reconcile for the same user journey.

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
| `lotus_analytics_ui_attention_events_total` | workbench | `route`, `panel`, `service`, `operation`, `attention_type`, `severity`, `state`, `reason`, `freshness_bucket`, `supportability_state` |

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

### Ecosystem Completion Slice 10: Reopen Governance And Contract Expansion

Purpose: turn RFC-0108 from first-wave analytics UI proof into a complete ecosystem execution
program without losing the evidence and supported-features discipline already established.

Required work:

1. change RFC-0108 lifecycle and platform context from first-wave closure to reopened ecosystem
   completion,
2. expand the analytics UI observability contract into an ecosystem observability contract that
   records every participating Lotus repository, route family, service family, metric family,
   audit-event family, protected-diagnostics family, dashboard, alert, runbook, and evidence
   requirement,
3. add a machine-readable per-app gap matrix covering `lotus-workbench`, `lotus-gateway`,
   `lotus-core`, `lotus-performance`, `lotus-risk`, `lotus-advise`, `lotus-manage`,
   `lotus-report`, `lotus-render`, `lotus-archive`, `lotus-ai`, and `lotus-platform`,
4. classify every app gap as `implemented`, `partially_implemented`, `planned`,
   `not_applicable_with_rationale`, or `blocked_with_owner`,
5. add validators that reject missing app coverage, unsupported implemented claims, forbidden
   labels, dashboard references to unimplemented metrics, missing runbooks, missing wiki-source
   decisions, and missing supported-features entries,
6. map first-wave RFC-0108 proof into the new matrix without reclassifying planned items as done,
7. create the execution ledger for ecosystem completion slices and require one PR per slice unless
   a slice is explicitly documentation-only.

Exit criteria:

1. ecosystem gap matrix exists and is validator-protected,
2. every Lotus app has an explicit observability posture row,
3. every planned item has owner, repo, blocker, and required proof,
4. first-wave implemented claims remain backed by prior PR/evidence,
5. no new runtime implementation begins before the expanded contract passes locally and in CI.

### Ecosystem Completion Slice 11: Platform Automation, Scaffolding, And CI Enforcement

Purpose: make uniform observability the default platform behavior instead of app-by-app custom
work.

Required work:

1. improve `lotus-platform` service scaffolding so new backend services start with health,
   liveness, readiness, metadata, metrics, correlation/trace propagation, structured JSON logs,
   product-safe errors, OpenAPI quality checks, supported-features placeholders, operations docs,
   wiki-source placeholders, and RFC evidence layout,
2. improve Workbench or UI scaffolding patterns so new UI surfaces start with bounded panel state,
   BFF request instrumentation, safe metric labels, attention-event hooks, browser evidence
   scaffolding, and no-sensitive-content test hooks,
3. add or tighten CI/workflow gates so every participating repository can run the relevant
   observability, OpenAPI, supported-features, docs/wiki, and no-sensitive-content checks,
4. provide reusable validators and templates rather than repeating local implementations,
5. update context, skill routing, onboarding, and repository engineering context templates if the
   ecosystem rollout creates durable new workflow guidance,
6. prove generated scaffolds and CI templates through contract tests.

Exit criteria:

1. platform scaffolding tests prove new apps receive the uniform baseline,
2. CI/workflow templates include the observability and documentation checks required by this RFC,
3. no app-local workaround remains where a platform-level scaffold or validator should own the
   behavior,
4. future Lotus apps can start with the same governed observability posture by default.

Slice 11 implementation evidence:

1. `context/contracts/analytics-ui-observability-scaffold-ci-enforcement.json` and its schema
   define the governed scaffold/CI enforcement contract.
2. `automation/validate_analytics_ui_scaffold_ci_enforcement.py` verifies generated backend
   defaults, Workbench/UI template defaults, reusable validators, and workflow/CI wiring.
3. `automation/New-Lotus-Service.ps1` now generates `scripts/no_sensitive_content_guard.py` and
   `scripts/supported_features_gate.py` alongside OpenAPI, evidence, docs, wiki, metrics,
   correlation, and product-safe error scaffolding.
4. `platform-standards/templates/Makefile.backend.template` runs `no-sensitive-content-guard` and
   `supported-features-gate` as baseline quality gates.
5. `platform-standards/templates/workbench-observability-surface.template.ts` provides the
   reusable bounded-state, safe-label, attention-event, and no-sensitive-key pattern for future
   Workbench/UI surfaces.
6. `automation/Invoke-PlatformRepoChecks.ps1` runs the RFC-0108 observability, ecosystem, and
   scaffold/CI validators in platform feature and PR merge lanes.

### Ecosystem Completion Slice 12: Backend Service Freshness And Supportability Metrics

Status: partially implemented. `lotus-risk` implements Slice 12 runtime proof for
`POST /analytics/risk/calculate` through `metadata.calculation_supportability`,
`lotus_risk_calculation_supportability_total`, and
`risk.observability.calculation_supportability`. `lotus-performance` implements Slice 12 runtime
proof for `POST /performance/twr` through `calculation_supportability`,
`lotus_performance_calculation_supportability_total`, and
`performance.observability.calculation_supportability`. `lotus-advise` implements Slice 12 runtime
proof through `GET /platform/capabilities` `supportability`,
`lotus_advise_advisory_supportability_total`, and
`advise.observability.advisory_supportability`. `lotus-manage` implements Slice 12 runtime
proof for `GET /rebalance/supportability/summary` through `supportability.state`,
`supportability.reason`, `supportability.freshness_bucket`,
`lotus_manage_action_register_supportability_total`, and
`manage.observability.action_register_supportability`. `lotus-report` implements Slice 12 runtime
proof through `GET /integration/capabilities` `supportability`,
`lotus_report_evidence_surface_supportability_total`, and
`report.observability.evidence_surface_supportability`. `lotus-core` implements Slice 12 runtime
proof through `PortfolioReadinessResponse.supportability`,
`lotus_core_portfolio_supportability_total`, and
`core.observability.portfolio_supportability`. `lotus-render` implements Slice 12 runtime proof
through `GET /metadata` `supportability`, `lotus_render_supportability_total`, and
`render.observability.render_supportability`. `lotus-archive` implements Slice 12 runtime proof
through `GET /metadata` `supportability`, `lotus_archive_supportability_total`, and
`archive.observability.archive_supportability`. `lotus-ai` implements Slice 12 runtime proof through
`observability_runtime.ai_surface_supportability` on `GET /platform/observability/runtime-status`
and `GET /platform/runtime-status`, `lotus_ai_surface_supportability_state`, and
`ai.observability.ai_surface_supportability`. These proofs include repo-native tests, OpenAPI
quality or contract proof where applicable, docs, and wiki source updates. Remaining performance
and risk endpoint families. Gateway PR #166 (`0e0e7f18fc8ff65b443487e54db4cc61e5ad5521`)
now preserves performance/risk source calculation supportability through fan-out state, risk
workspace supportability, and performance evidence context. Workbench canonical browser
reconciliation still requires implementation-backed supportability proof before this slice can
close.

Purpose: finish source-backed freshness, data-quality, and supportability signals in the domain
services that feed front-office UI state.

Required work:

1. implement governed freshness/supportability metric families in `lotus-performance` and
   `lotus-risk` for the analytics calculations already surfaced in Workbench,
2. implement equivalent source-backed supportability signals in `lotus-core`, `lotus-render`,
   `lotus-archive`, and `lotus-ai` where their
   data or capabilities affect Workbench, Gateway, evidence, advisory, management, report, archive,
   or AI-backed surfaces,
3. standardize freshness buckets, supportability states, empty-state reasons, degraded reasons,
   calculation-quality reasons, and retryability reasons across services,
4. ensure each service emits product-safe logs and metrics without portfolio, client, account,
   holding, transaction, document, advisor, request-body, response-body, raw prompt, or model-output
   content,
5. add repo-native tests for ready, stale, degraded, empty, error, permission-blocked, and
   unsupported paths where applicable,
6. update each service's OpenAPI/Swagger and operations docs when API shape or operator behavior
   changes,
7. update supported-features only after service-native implementation and proof.

Exit criteria:

1. every participating backend service has source-backed supportability metrics or an explicit
   not-applicable rationale,
2. `analytics.backend.observability.freshness_supportability` can be promoted only after
   `lotus-performance` and `lotus-risk` pass source-backed proof,
3. Workbench freshness/degraded-state claims have backend-owned evidence,
4. no backend service leaks sensitive identifiers or payload content into telemetry.

### Ecosystem Completion Slice 13: Gateway Fan-Out Metrics, Protected Diagnostics, And Audit Completion

Status: partially implemented. `lotus-gateway` emits
`lotus_gateway_analytics_fanout_duration_seconds` with bounded `operation`, `service`, and
`status_class` labels and `lotus_gateway_analytics_degraded_total` with bounded `operation`,
`service`, and `reason` labels for the selected Workbench performance and risk analytics fan-out
path. Gateway PR #163 expands the same bounded fan-out wrapper to central `lotus-manage`,
`lotus-report`, `lotus-archive`, and `lotus-ai` client seams with explicit operation labels so
proposal, job, document, run, portfolio, raw prompt, and model-output content never become
telemetry dimensions. Gateway PR #164 completes direct `lotus-core` query/control-plane and
`lotus-core` ingestion fan-out coverage with explicit operation labels and no portfolio, session,
upload, request-body, trace, or correlation identifiers as telemetry dimensions. Gateway also exposes
`GET /api/v1/analytics-ui/diagnostics/{support_reference}` for protected operator diagnostics
lookup, requires governed caller context plus an operator support role, rejects raw-looking
identifiers by requiring opaque `gdiag-*` support references, returns only bounded support posture,
and emits
`gateway.analytics.audit.protected_diagnostics_lookup` without support references, portfolio ids,
trace ids, correlation ids, request bodies, response bodies, or raw entitlement failures in audit
fields. Gateway unit and integration tests prove metric-family names, label names, metric
increments, forbidden sensitive-label rejection, protected lookup authorization, raw identifier
rejection, OpenAPI visibility, and bounded audit fields. Slice 13 Gateway fan-out coverage is
complete for the implemented Gateway client seams; ecosystem dashboard reconciliation and final
end-to-end proof remain planned in later slices.

Purpose: complete Gateway as the uniform product-facing observability and diagnostics boundary.

Required work:

1. implement `lotus_gateway_analytics_fanout_duration_seconds`,
   `lotus_gateway_analytics_degraded_total`, and any additional governed fan-out metric families
   required for all UI-facing Gateway operations,
2. apply the metric pattern to Gateway calls into `lotus-core`, `lotus-performance`, `lotus-risk`,
   `lotus-advise`, `lotus-manage`, `lotus-report`, `lotus-render`, `lotus-archive`, and
   `lotus-ai` where those calls support Workbench surfaces,
3. extend the protected diagnostics lookup pattern across every UI-facing Gateway operation that
   needs operator support references, without placing portfolio, client, account, holding,
   transaction, document, advisor, trace, or correlation identifiers in metric labels or dashboard
   variables,
4. complete audit events for remaining entitlement-relevant reads and privileged/operator actions,
   preserving the protected diagnostics lookup audit constraints,
5. ensure OpenAPI/Swagger for new or changed Gateway APIs is complete with grouped endpoints,
   what/when/how guidance, request/response examples, attribute descriptions, types, examples, and
   product-safe error examples,
6. add gateway tests for success, partial, degraded, timeout, permission-denied, upstream
   unavailable, malformed traceparent, and protected-diagnostics authorization paths,
7. reconcile Gateway metrics with dashboard and alert contracts.

Exit criteria:

1. `gateway.analytics.observability.fanout_metrics` is promoted from planned to implemented,
2. `gateway.analytics.observability.protected_diagnostics` is promoted from planned to implemented,
3. `gateway.analytics.observability.all_ui_fanout_paths` is promoted from planned to implemented
   for implemented Gateway client seams,
4. Gateway is the single UI-facing diagnostics boundary for protected lookup,
5. dashboards and alerts reference only implemented Gateway metrics,
6. API certification and Swagger checks pass.

### Ecosystem Completion Slice 14: Workbench All-Surface Observability Rollout

Purpose: extend Workbench observability from selected canonical panels to every supported
front-office surface without decorative or unsupported claims.

Required work:

1. inventory every supported Workbench route, panel, BFF route, evidence surface, advisory surface,
   management surface, reporting/evidence surface, archive surface, and AI-backed surface,
2. map each surface to Gateway operations and backend supportability sources,
3. implement panel hydration, API duration, state, attention, empty/degraded/stale/error, and
   permission-blocked observability for every supported surface,
4. consume backend-owned freshness/supportability and Gateway fan-out state instead of inferring
   decorative UI status,
5. keep unsupported panels explicit as unsupported and unpromoted,
6. add browser/unit tests for all state classes and sensitive-label exclusion,
7. capture governed browser proof only after API, calculation, panel, and supportability validation
   pass.

Exit criteria:

1. all supported Workbench surfaces have source-backed observability or explicit unsupported
   posture,
2. `workbench.analytics.observability.freshness_degraded_state` can be promoted only after
   backend and Gateway proof exists,
3. no Workbench surface claims supportability that Gateway/backend services do not provide,
4. browser evidence reconciles with Gateway/backend evidence.

### Ecosystem Completion Slice 15: Dashboards, Alerts, Runbooks, And Operator Diagnostics

Purpose: provide ecosystem-level operator surfaces tied only to implemented telemetry.

Required work:

1. extend Grafana dashboards and Prometheus alert rules to cover Workbench, Gateway, and every
   participating backend service,
2. group dashboards by user journey, service, route family, panel family, source system, and
   supportability state without sensitive variables,
3. add runbooks for attention events, degraded panels, stale calculations, Gateway fan-out
   degradation, backend freshness failures, entitlement denials, protected diagnostics lookup,
   archive/report/evidence unavailability, and AI-backed degraded state,
4. ensure alert severities distinguish user-visible degradation, service degradation, stale data,
   unsupported capability, and security/entitlement posture,
5. add validators proving dashboards and alerts reference implemented metrics only,
6. prove operator diagnostics do not require raw request/response bodies, screen content, client
   identifiers, portfolio identifiers, raw prompts, or generated AI output.

Exit criteria:

1. dashboards and alerts cover every implemented ecosystem metric family,
2. every alert has a runbook and bounded severity,
3. dashboard and alert validators reject forbidden variables, annotations, and unimplemented metric
   references,
4. operator diagnostics are useful without sensitive-content leakage.

### Ecosystem Completion Slice 16: Ecosystem Implementation Proof

Purpose: prove the complete Lotus user journey end to end, not only one canonical panel.

Required work:

1. bring up the governed ecosystem runtime with all required sibling repositories,
2. validate canonical and expanded Workbench surfaces through Gateway-backed APIs,
3. capture browser evidence, Gateway evidence, backend logs/metrics, dashboards, alerts, protected
   diagnostics proof, audit proof, OpenAPI proof, and no-sensitive-content assertions,
4. prove representative journeys across portfolio state, performance analytics, risk analytics,
   advisory, management action register, report evidence, render/archive-backed evidence, and
   AI-backed support where supported,
5. record commit SHAs, PR numbers, check names, route/panel ids, service ids, metric names,
   dashboard ids, runbook paths, and evidence artifact paths,
6. critically review evidence for inconsistencies and iterate until the implementation is genuinely
   production-grade.

Exit criteria:

1. all included journeys pass live proof,
2. evidence reconciles across browser, Gateway, backend services, dashboards, alerts, audit logs,
   and protected diagnostics,
3. no-sensitive-content assertions pass over source, telemetry artifacts, screenshots, logs,
   metrics, traces, and evidence bundles,
4. gaps are fixed or explicitly rejected as unsupported with owner-approved rationale.

### Ecosystem Completion Slice 17: Ecosystem Hardening, Review, And Certification

Status: implemented. Slice 17 adds
`context/contracts/analytics-ui-observability-ecosystem-hardening.json` and
`automation/validate_analytics_ui_ecosystem_hardening.py`, plus validator tests, to make the
second-last reopened-ecosystem review executable rather than narrative-only. The validator
reconciles the Slice 16 proof contract, the ecosystem-completion gap matrix, supported-features
status, protected diagnostics OpenAPI proof, dashboard and alert proof, per-repository review
rows, residual planned scope, local proof commands, GitHub check expectations, and no-open-P0/P1
findings. It promotes only
`platform.analytics.observability.ecosystem_hardening_certification`; backend freshness,
Workbench freshness/degraded-state promotion, all-supported-surface promotion, and final ecosystem
closure remain planned.

Purpose: perform the required second-last review for the reopened ecosystem scope.

Required work:

1. perform full code review across all changed repositories,
2. remove dead code, duplicate observability logic, stale docs, unused metrics, and decorative
   supportability claims,
3. verify API certification pattern compliance and Swagger quality for every changed API,
4. verify platform governance, enterprise data mesh standards, supported-features governance, and
   no-sensitive-content controls,
5. verify every implemented supported-feature key has repo-native tests, platform validators,
   GitHub check evidence, docs/wiki source, and live proof,
6. verify dashboards, alerts, runbooks, protected diagnostics, audit events, and operator workflows,
7. fix all P0/P1 findings before closure and explicitly triage P2/P3 findings with owner and
   target slice.

Exit criteria:

1. no P0/P1 privacy, supportability, telemetry, API, Swagger, dashboard, alert, audit, or
   unsupported-feature finding remains,
2. every API and metric family is certified,
3. all participating repos have green relevant CI,
4. supported-features exactly matches implementation-backed reality.

### Ecosystem Completion Slice 18: Final Ecosystem Closure

Purpose: close RFC-0108 only after uniform observability and operational posture is implemented
across the Lotus ecosystem.

Required work:

1. update RFC-0108, RFC index, context, repo-local engineering contexts, docs, runbooks,
   supported-features, wiki source, and machine-readable contracts to final ecosystem state,
2. publish every changed repo wiki after merge,
3. update skills, guidance, scaffolding, validators, or agent context where the ecosystem rollout
   produced durable reusable lessons; otherwise record explicit no-change decisions,
4. verify every affected repository is clean on `main...origin/main`,
5. delete completed feature branches locally and remotely,
6. record final ecosystem evidence, PRs, merge commits, wiki publication commits, check names,
   evidence directories, and residual unsupported scope.

Exit criteria:

1. RFC-0108 has no planned observability/supportability feature key for included Lotus apps unless
   it is explicitly out of scope with owner-approved rationale,
2. all docs, wiki source, context, contracts, dashboards, alerts, runbooks, and supported-features
   match merged implementation,
3. all GitHub checks are green,
4. every affected repo is clean,
5. Lotus has a uniform, implementation-backed observability and operational posture across the
   full supported user journey.

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
| `platform.analytics.observability.telemetry_contract` | Implemented | `lotus-platform` | Slice 2 adds the governed analytics UI telemetry contract for browser events, gateway log events, severity levels, attention event types, audit event types, trace attributes, dashboard/alert reference policy, protected diagnostics policy, and validator tests without emitting runtime telemetry. |
| `platform.analytics.observability.rollout_readiness` | Implemented | `lotus-platform` | Slice 9 adds the machine-readable rollout-readiness contract, validator, and unit tests that tie certified Workbench route/panel scope to Slice 8 proof, separate residual planned scope, and prove validators reject forbidden labels and unimplemented metric references. |
| `platform.analytics.observability.hardening_certification` | Implemented | `lotus-platform` | Second-last slice adds a machine-readable hardening review contract, validator, and tests covering telemetry fields, panel states, API/Swagger applicability, dashboard and alert certification, enterprise governance, residual planned scope, and no open P0/P1 findings before closure. |
| `platform.analytics.observability.final_closure` | Implemented | `lotus-platform` | Final closure adds the machine-readable final closure contract, validator, tests, docs/context/wiki source updates, explicit skills and guidance review, required wiki publication, residual planned-scope preservation, and branch hygiene requirements before closure. |
| `platform.analytics.observability.ecosystem_completion_contract` | Implemented | `lotus-platform` | Slice 10 adds the ecosystem observability contract, per-app gap matrix, validator, tests, execution ledger posture, and supported-features checks for every Lotus repository while keeping runtime work blocked until the expanded contract is merged. |
| `platform.analytics.observability.scaffold_ci_enforcement` | Implemented | `lotus-platform` | Slice 11 adds generated backend no-sensitive-content and supported-features gates, a reusable Workbench observability surface template with bounded state and safe labels, a machine-readable scaffold/CI enforcement contract, validator, tests, and platform repo check wiring so scaffolding and CI templates enforce the uniform baseline. |
| `platform.analytics.observability.ecosystem_dashboards_alerts` | Implemented | `lotus-platform` | Slice 15 extends the platform Grafana dashboard, Prometheus alert rules, operator runbook, contract validator, and platform-stack tests across every currently implemented RFC-0108 metric family: Workbench panel state, panel hydration, API request latency, attention events, Gateway fan-out duration/degradation, and AI surface supportability. Backend freshness metrics remain planned and are intentionally excluded until implementation proof exists. |
| `platform.analytics.observability.ecosystem_implementation_proof` | Implemented | `lotus-platform` | Slice 16 adds a platform-owned ecosystem proof contract and reviewer that reconciles the live canonical Workbench proof bundle, supported portfolio/performance/risk/advisory/manage/report/evidence/AI journeys, browser screenshots, Gateway-backed API checks, workflow-pack supportability actions, dashboard and alert implemented-metric references, protected diagnostics lookup, Gateway OpenAPI diagnostics route evidence, residual planned scope, and no-sensitive-content assertions. Backend freshness metrics, full RFC-0079 risk/evidence scope, and final hardening remain planned. |
| `platform.analytics.observability.ecosystem_hardening_certification` | Implemented | `lotus-platform` | Slice 17 adds a machine-readable ecosystem hardening contract, schema, validator, and unit tests that reconcile supported-features posture, per-repository gap-matrix reviews, Slice 16 proof, protected diagnostics OpenAPI evidence, dashboard and alert review, residual planned scope, and no-open-P0/P1 findings before final closure. |
| `platform.analytics.observability.ecosystem_final_closure` | Implemented | `lotus-platform` | Slice 18 adds a separate machine-readable ecosystem final closure contract, schema, validator, and unit tests that reconcile Slice 17 hardening, Slice 16 proof, ecosystem completion status, residual planned scope, required local and GitHub proof, wiki publication requirements, and branch hygiene while preserving backend freshness and full Workbench supported-surface residuals as planned. |
| `workbench.analytics.observability.correlation_trace` | Implemented | `lotus-workbench` | Slice 3 adds Workbench analytics UI correlation helpers, client-side BFF request headers, BFF proxy correlation/trace generation and malformed traceparent replacement tests, while keeping correlation and trace identifiers out of metric labels. |
| `workbench.analytics.observability.contract_vocabulary` | Implemented | `lotus-workbench` | Slice 1 adds code-owned analytics UI observability vocabulary and tests for allowed labels, forbidden sensitive fields, state vocabulary, and planned Workbench metric-family names without emitting product telemetry. |
| `workbench.analytics.observability.panel_state_metrics` | Implemented | `lotus-workbench` | Slice 5 adds local Workbench analytics UI metric events, `/api/metrics` Prometheus text export, and tests for ready, empty, partial, stale, degraded, error, permission-blocked, unsupported, API duration, panel state, panel hydration, and sensitive-field exclusion for selected performance-summary, performance-details, and risk-summary reads. Slice 14 partial proof expands the same wrapper to supported Portfolio workspace, client-side Performance, Risk, and explicit report-batch operator reads with an explicit observed-surface registry and no portfolio, client, session, report batch, trace, request-body, response-body, or screen-content metric labels. |
| `workbench.analytics.observability.freshness_degraded_state` | Planned | `lotus-workbench`, `lotus-performance`, `lotus-risk` | Slice 14 partial Workbench proof records source-backed stale/degraded classification on newly observed client reads when response metadata is present. `lotus-performance` now covers completed TWR, MWR, contribution, and attribution calculation supportability through PR #138, and `lotus-risk` now covers `risk/calculate`, drawdown, rolling metrics, historical attribution, and concentration through PR #107. Gateway PR #166 (`0e0e7f18fc8ff65b443487e54db4cc61e5ad5521`) preserves those source supportability states through Gateway fan-out state, risk workspace supportability, and performance evidence context. Workbench PR #118 (`f048b46b292789e5e79e413191a1e717f0c5bec9`) reconciles Gateway `source_supportability` arrays into freshness and supportability state derivation plus live validation `supportabilityChecks`. Workbench PR #119 (`1ecf0942805588747bfbee1b2b4ca808ce286e29`) and lotus-core PR #328 (`5c6a22470069552a4e91eaf98ee976d5dd5c6a8d`) prove clean governed canonical runtime execution for the current supported surface. Full Workbench promotion remains planned for complete RFC-0079 risk/evidence and all-supported-surface coverage, not because source-supportability propagation or canonical proof is blocked. |
| `workbench.analytics.observability.attention_events` | Implemented | `lotus-workbench`, `lotus-platform` | Slice 6 adds Workbench attention events and the `lotus_analytics_ui_attention_events_total` counter for stale, degraded, partial-source, and repeated-failure selected analytics panel states, with deduplication tests, bounded severity tests, source-backed reason codes, dashboard/alert contract coverage, and operator response docs. |
| `workbench.analytics.observability.entitlement_audit_events` | Implemented | `lotus-gateway` | Slice 7 adds Gateway product-safe selected analytics read audit logs. Successful upstream reads emit `analytics_read_allowed`; upstream `401`/`403` denials emit `analytics_read_denied`; tests prove bounded audit fields and exclusion of portfolio, client, request/response body, and raw entitlement-failure content. Slice 13 adds protected diagnostics lookup audit proof; full caller-context entitlement certification remains planned. |
| `workbench.analytics.observability.canonical_proof` | Implemented | `lotus-platform`, `lotus-workbench` | Slice 8 adds platform-owned canonical proof review plus governed live Workbench proof for `PB_SG_GLOBAL_BAL_001`: API checks, calculation sanity, panel classifications, browser screenshots, Workbench `/api/metrics` family exposure, dashboard/alert metric reconciliation, and sensitive-content assertions. |
| `workbench.analytics.observability.safe_dashboard` | Implemented | `lotus-platform` | Slice 5 adds a platform Grafana dashboard, Prometheus scrape config, and alert rules that reference only implemented Workbench metric-family names, with validator and unit coverage rejecting unimplemented metric references and forbidden dashboard/alert content. |
| `workbench.analytics.observability.all_supported_surfaces` | Planned | `lotus-workbench` | Slice 14 partial proof instruments supported Portfolio workspace, client-side Performance, Risk, and explicit report-batch operator reads in `lotus-workbench` with a code-owned observed-surface registry, unit coverage, typecheck, lint, repo-local wiki source, no-sensitive metric label assertions, endpoint reconciliation against the governed Workbench registry, canonical browser proof, source support-state proof, partial RFC-0079 performance evidence-context reconciliation through Gateway and Workbench, PR #118 Gateway `source_supportability` reconciliation for performance/risk Workbench reads, and clean canonical runtime proof through Workbench PR #119 plus lotus-core PR #328. Full all-supported-surface promotion remains planned until full RFC-0079 risk/evidence scope and every supported Workbench surface are separately implemented and certified. |
| `gateway.analytics.observability.fanout_metrics` | Implemented | `lotus-gateway` | Slice 13 proof emits `lotus_gateway_analytics_fanout_duration_seconds` and `lotus_gateway_analytics_degraded_total` from the selected Workbench performance/risk analytics path, central manage, report, archive, and AI client seams, and direct `lotus-core` query/control-plane plus ingestion client seams. Tests prove bounded labels, metric increments, forbidden sensitive-label rejection, and safe degraded records without proposal, job, document, run, portfolio, prompt, model-output, session, upload, or request-body content. Slice 15 adds dashboard and alert reconciliation for the implemented Gateway metric families. |
| `gateway.analytics.observability.protected_diagnostics` | Implemented | `lotus-gateway` | Slice 13 proof adds `GET /api/v1/analytics-ui/diagnostics/{support_reference}` with caller-context and operator-role requirements, opaque `gdiag-*` references, product-safe response posture, bounded OpenAPI documentation, raw identifier rejection, and `gateway.analytics.audit.protected_diagnostics_lookup` audit fields that exclude support references, portfolio ids, trace ids, correlation ids, request/response bodies, and raw entitlement failures. |
| `gateway.analytics.observability.all_ui_fanout_paths` | Implemented | `lotus-gateway` | Slice 13 applies safe fan-out logs, metrics, trace propagation, degraded-state classification, audits, and diagnostics to implemented UI-facing Gateway client seams, including selected Workbench analytics, central manage/report/archive/AI, and direct `lotus-core` query/control-plane plus ingestion paths. |
| `gateway.analytics.observability.correlation_trace` | Implemented | `lotus-gateway` | Slice 3 proves Gateway middleware accepts valid traceparent, rejects malformed traceparent, emits safe response trace headers, and forwards correlation and trace context to analytics backend clients without adding sensitive labels. |
| `gateway.analytics.observability.contract_vocabulary` | Implemented | `lotus-gateway` | Slice 1 adds code-owned analytics UI observability vocabulary and tests for allowed labels, forbidden sensitive fields, state vocabulary, and planned gateway metric-family names without emitting fan-out metrics. |
| `gateway.analytics.observability.structured_fanout_logs` | Implemented | `lotus-gateway` | Slice 4 emits product-safe structured gateway fan-out logs for selected Workbench performance and risk analytics operations with route, service, operation, state, supportability, status class, bounded reason, and no sensitive request/response payload fields. |
| `analytics.backend.observability.freshness_supportability` | Planned | `lotus-performance`, `lotus-risk` | `lotus-performance` now emits `calculation_supportability` and bounded `lotus_performance_calculation_supportability_total` labels for completed TWR, MWR, contribution, and attribution calculations through PR #138. `lotus-risk` now emits `metadata.calculation_supportability` and bounded `lotus_risk_calculation_supportability_total` labels for `risk/calculate`, drawdown, rolling metrics, historical attribution, and concentration through PR #107. Gateway PR #166 consumes those source supportability blocks through the experience API, maps stale/partial/unavailable posture into bounded fan-out state, and preserves source supportability in risk workspace supportability items plus performance evidence context. Workbench PR #118 reconciles Gateway `source_supportability` arrays into UI freshness/supportability derivation and canonical live validation summaries, and Workbench PR #119 plus lotus-core PR #328 prove clean governed canonical runtime execution. Full backend freshness/supportability promotion remains planned until every supported metric family and surface is separately implemented and certified. |
| `core.observability.portfolio_supportability` | Implemented for portfolio readiness; Gateway and Workbench reconciliation implemented for supported portfolio readiness reads | `lotus-core`, `lotus-gateway`, `lotus-workbench` | Slice 12 partial proof implements `PortfolioReadinessResponse.supportability`, bounded `lotus_core_portfolio_supportability_total` labels, capability publication, repo-native unit/integration/OpenAPI/API-vocabulary/no-alias proof, docs, and wiki source updates. Gateway PR #167 preserves lotus-core portfolio readiness `supportability` through the portfolio readiness API and normalizes source freshness into Workbench vocabulary. Workbench PR #120 consumes the Gateway supportability block into the detailed portfolio workspace and records no-sensitive `portfolio.readiness` supportability metrics. |
| `performance.observability.calculation_supportability` | Implemented for TWR, MWR, contribution, and attribution; Gateway and Workbench reconciliation implemented for supported performance reads | `lotus-performance` | Slice 12 partial proof implemented TWR `calculation_supportability`, bounded `lotus_performance_calculation_supportability_total` labels, integration capability publication, repo-native integration/OpenAPI/API-vocabulary/no-alias/domain-product/lint/typecheck proof, docs, and wiki source updates. PR #138 extends the same source-owned block and metric to completed MWR, contribution, and attribution responses; PR checks were green, `make check` passed locally, and wiki source was published. Gateway PR #166 consumes performance source supportability into performance evidence context and capability posture; Workbench PR #118 derives supported performance freshness/supportability from Gateway `source_supportability` and records live validation supportability checks. |
| `risk.observability.calculation_supportability` | Implemented for risk endpoint families; Gateway and Workbench reconciliation implemented for supported risk reads | `lotus-risk` | Slice 12 partial proof implements `metadata.calculation_supportability`, bounded `lotus_risk_calculation_supportability_total` labels, integration capability publication, repo-native tests, OpenAPI quality proof, docs, and wiki source updates for `risk/calculate`. PR #107 completes the same source-owned supportability contract across drawdown, rolling metrics, historical attribution, and concentration with green Feature Lane and PR Merge Gate checks, docs, vocabulary, monetary-float guard baseline, and published wiki source. Gateway PR #166 consumes risk source supportability into fan-out classification and risk workspace supportability items; Workbench PR #118 derives supported risk freshness/supportability from Gateway `source_supportability` and records live validation supportability checks. |
| `advise.observability.advisory_supportability` | Implemented for capability-level advisory supportability; Gateway/Workbench reconciliation planned | `lotus-advise` | Slice 12 partial proof implements `GET /platform/capabilities` `supportability`, bounded `lotus_advise_advisory_supportability_total` labels, capability publication, repo-native `make check` proof, docs, and wiki source updates. Gateway consumption and Workbench advisory surface reconciliation remain planned. |
| `manage.observability.action_register_supportability` | Implemented for supportability summary; Gateway and Workbench reconciliation implemented for supported portfolio workspace rebalance reads | `lotus-manage`, `lotus-gateway`, `lotus-workbench` | Slice 12 partial proof implements `supportability.state`, `supportability.reason`, `supportability.freshness_bucket`, bounded `lotus_manage_action_register_supportability_total` labels, capability publication, repo-native service/API/OpenAPI tests, docs, and wiki source updates. Gateway PR #168 preserves lotus-manage action-register supportability through the portfolio workspace rebalance summary with optional-section partial failure handling. Workbench PR #121 consumes the Gateway supportability block into portfolio operational support copy and derives bounded no-sensitive freshness/supportability metrics from nested rebalance supportability. |
| `report.observability.evidence_surface_supportability` | Implemented for evidence-surface capability posture; Gateway and Workbench reconciliation implemented for supported report-batch operator reads | `lotus-report`, `lotus-gateway`, `lotus-workbench` | Slice 12 partial proof implements `GET /integration/capabilities` `supportability`, bounded `lotus_report_evidence_surface_supportability_total` labels, capability publication, repo-native `make check` proof, docs, and wiki source updates. Gateway PR #169 preserves lotus-report evidence-surface supportability through report-batch create/status/run-once responses with bounded fallback reasons. Workbench PR #122 consumes the Gateway supportability block for report-batch operator reads and records bounded no-sensitive supportability metrics. |
| `render.observability.render_supportability` | Implemented for render metadata supportability; Gateway/Workbench reconciliation planned | `lotus-render` | Slice 12 partial proof implements `GET /metadata` `supportability`, bounded `lotus_render_supportability_total` labels, runtime/readiness/template-registry backed posture, repo-native `make check` proof, docs, and wiki source updates. PR #6 merged as `d2198f821516cb25bd8e0a36d42f10e04d7fdd5f` and wiki published as `34ecc05`. Gateway consumption and Workbench evidence-surface reconciliation remain planned. |
| `archive.observability.archive_supportability` | Implemented for archive metadata supportability; Gateway/Workbench reconciliation planned | `lotus-archive` | Slice 12 partial proof implements `GET /metadata` `supportability`, bounded `lotus_archive_supportability_total` labels, retrieval/retention/legal-hold/access-audit/lifecycle backed posture, explicit Workbench non-support state, repo-native `make check` proof, docs, and wiki source updates. PR #17 merged as `031fcc1a2e46cc4750d47a06c99b65387e7b95ef` and wiki published as `98ce3b7`. Gateway consumption and Workbench archive-surface reconciliation remain planned. |
| `ai.observability.ai_surface_supportability` | Implemented for AI surface runtime supportability; Gateway and Workbench reconciliation implemented for supported advisor-brief reads | `lotus-ai`, `lotus-gateway`, `lotus-workbench` | Slice 12 partial proof implements `observability_runtime.ai_surface_supportability` on `GET /platform/observability/runtime-status` and `GET /platform/runtime-status`, bounded `lotus_ai_surface_supportability_state` labels, workflow-pack runtime/provider/safety source posture for advisor brief, lotus-performance TWR inspection support brief, and workspace rationale surfaces, repo-native targeted tests/lint/typecheck proof, docs, and wiki source updates. Gateway PR #170 preserves lotus-ai AI surface supportability through advisor-brief responses. Workbench PR #123 consumes the Gateway supportability block for supported advisor-brief reads and records bounded no-sensitive supportability metrics. |

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
| Slice 2: telemetry contract | `context/contracts/analytics-ui-observability-contract.json`; `automation/validate_analytics_ui_observability_contract.py`; `lotus-workbench/src/features/analytics-observability/contract.ts`; `lotus-gateway/src/app/observability/analytics_ui.py` | `python -m pytest tests\unit\test_analytics_ui_observability_contract.py -q`; `python automation\validate_analytics_ui_observability_contract.py`; `npm run test -- tests/unit/analytics-observability-contract.test.ts`; `python -m pytest tests\unit\test_analytics_ui_observability_contract.py -q` | Complete locally for governed telemetry names, severity levels, attention/audit event vocabularies, trace attributes, dashboard/alert reference policy, and protected diagnostics policy | Runtime correlation propagation starts in Slice 3; product telemetry remains planned. |
| Slice 3: browser-to-gateway trace and correlation propagation | `lotus-workbench/src/features/analytics-observability/correlation.ts`; `lotus-workbench/src/app/api/bff/[...path]/route.ts`; `lotus-workbench/src/features/workbench/api.ts`; `lotus-gateway/src/app/middleware/correlation.py`; `lotus-gateway/src/app/clients/lotus_analytics_client.py` | `npm run test -- tests/unit/analytics-observability-correlation.test.ts tests/unit/bff-route.test.ts tests/unit/workbench-api.test.ts tests/unit/analytics-observability-contract.test.ts`; `npm run typecheck`; `python -m pytest tests\unit\test_correlation_middleware.py tests\unit\test_upstream_clients.py::test_lotus_analytics_client_workspace_summary_forwards_trace_context tests\unit\test_analytics_ui_observability_contract.py -q` | Complete locally for safe browser/BFF/gateway/backend correlation and trace propagation | Product telemetry, metrics, dashboards, alerts, attention events, audit events, and canonical browser proof remain planned. |
| Slice 4: Gateway and analytics backend structured logging | `lotus-gateway/src/app/observability/analytics_ui.py`; `lotus-gateway/src/app/clients/lotus_analytics_client.py`; `context/contracts/analytics-ui-observability-contract.json` | `python -m pytest tests\unit\test_analytics_ui_observability_contract.py tests\unit\test_upstream_clients.py::test_lotus_analytics_client_emits_safe_structured_fanout_log tests\unit\test_upstream_clients.py::test_lotus_analytics_client_emits_safe_unavailable_fanout_log tests\unit\test_upstream_clients.py::test_lotus_analytics_client_workspace_summary_forwards_trace_context -q`; `python automation\validate_analytics_ui_observability_contract.py`; `python -m pytest tests\unit\test_analytics_ui_observability_contract.py -q` | Complete locally for product-safe Gateway structured fan-out logs over selected Workbench performance and risk analytics operations | Metrics, dashboards, alerts, attention events, audit events, Workbench browser telemetry, and canonical browser proof remain planned. |
| Slice 5: Metrics, dashboards, alerts, and freshness contracts | `lotus-workbench/src/features/analytics-observability/metrics.ts`; `lotus-workbench/src/app/api/metrics/route.ts`; `lotus-platform/context/contracts/analytics-ui-observability-contract.json`; `lotus-platform/platform-stack/grafana/dashboards/analytics-ui-observability-overview.json`; `lotus-platform/platform-stack/prometheus/rules/analytics-ui-observability.rules.yml`; `lotus-platform/platform-stack/prometheus/prometheus.yml` | `npm run test -- tests/unit/analytics-observability-metrics.test.ts tests/unit/workbench-api.test.ts tests/unit/analytics-observability-contract.test.ts tests/unit/metrics-route.test.ts`; `npm run typecheck`; `python automation\validate_analytics_ui_observability_contract.py`; `python -m pytest tests\unit\test_analytics_ui_observability_contract.py tests\unit\test_platform_stack_observability_contract.py -q`; `python -m ruff check automation\validate_analytics_ui_observability_contract.py tests\unit\test_analytics_ui_observability_contract.py tests\unit\test_platform_stack_observability_contract.py` | Complete locally for first-wave Workbench metric events, Prometheus text export, platform scrape config, dashboard panels, alert rules, state classification, freshness buckets, and sensitive-field exclusion for selected analytics reads | Gateway/backend metrics, attention events, audit events, and canonical browser proof remain planned. |
| Slice 6: UI state and attention events | `lotus-workbench/src/features/analytics-observability/metrics.ts`; `lotus-workbench/src/features/analytics-observability/contract.ts`; `lotus-platform/context/contracts/analytics-ui-observability-contract.json`; `lotus-platform/platform-stack/grafana/dashboards/analytics-ui-observability-overview.json`; `lotus-platform/platform-stack/prometheus/rules/analytics-ui-observability.rules.yml`; `lotus-platform/docs/operations/analytics-ui-observability-runbook.md` | `npm run test -- tests/unit/analytics-observability-metrics.test.ts tests/unit/analytics-observability-contract.test.ts tests/unit/metrics-route.test.ts`; `npm run typecheck`; `python automation\validate_analytics_ui_observability_contract.py`; `python -m json.tool context\contracts\analytics-ui-observability-contract.json`; `python -m json.tool platform-stack\grafana\dashboards\analytics-ui-observability-overview.json` | Complete locally for bounded Workbench attention events, attention counter export, repeated-failure thresholding, deduplication, dashboard/alert contract references, operator runbook guidance, and sensitive-field exclusion | Gateway/backend metrics, read audit events, and canonical browser proof remain planned at this historical slice boundary. |
| Slice 7: audit events for entitlement-relevant reads and privileged actions | `lotus-gateway/src/app/observability/analytics_ui.py`; `lotus-gateway/src/app/clients/lotus_analytics_client.py`; `lotus-platform/context/contracts/analytics-ui-observability-contract.json`; `lotus-platform/docs/operations/analytics-ui-observability-runbook.md` | `python -m pytest tests\unit\test_analytics_ui_observability_contract.py tests\unit\test_upstream_clients.py::test_lotus_analytics_client_emits_safe_structured_fanout_log tests\unit\test_upstream_clients.py::test_lotus_analytics_client_emits_safe_read_allowed_audit_log tests\unit\test_upstream_clients.py::test_lotus_analytics_client_emits_safe_read_denied_audit_log tests\unit\test_upstream_clients.py::test_lotus_analytics_client_emits_safe_unavailable_fanout_log -q`; `python automation\validate_analytics_ui_observability_contract.py`; `python -m pytest tests\unit\test_analytics_ui_observability_contract.py tests\unit\test_platform_stack_observability_contract.py -q` | Complete locally for Gateway selected analytics read allow/deny audit logs, bounded audit field validation, upstream denial classification, and sensitive-field exclusion | Gateway/backend metrics, full caller-context entitlement certification, and canonical browser proof remain planned at this historical slice boundary. |
| Slice 8: canonical Workbench implementation proof | `automation/review_analytics_ui_canonical_proof.py`; `tests/unit/test_analytics_ui_canonical_proof_review.py`; `output/front-office-qa/canonical-front-office-qa-20260429-131616.json`; `output/rfc-0108-slice-8-canonical/live-validation-summary.json`; `output/rfc-0108-slice-8-canonical/SHOT-INDEX.md`; Workbench `/api/metrics` live response | `powershell -ExecutionPolicy Bypass -File automation\Invoke-Canonical-FrontOffice-QA.ps1 -BringUp -KeepRunning -LotusAiEnvFile .env.example -ScreenshotDirectory output\rfc-0108-slice-8-canonical`; `python automation\review_analytics_ui_canonical_proof.py output\front-office-qa\canonical-front-office-qa-20260429-131616.json`; `Invoke-WebRequest -UseBasicParsing http://workbench.dev.lotus/api/metrics`; `python -m pytest tests\unit\test_analytics_ui_observability_contract.py tests\unit\test_analytics_ui_canonical_proof_review.py -q` | Complete locally for governed `PB_SG_GLOBAL_BAL_001` live proof: canonical seed verified, API checks passed, calculation sanity passed, seven browser screenshots were captured after validation, panel classifications reconciled with the registry, dashboard/alert artifacts referenced only implemented metrics, Workbench exposed all four implemented metric families, and the proof reviewer passed no-sensitive and reconciliation checks | Gateway/backend metrics, full caller-context entitlement certification, and broad rollout remain planned at this historical slice boundary. |
| Slice 9: rollout proof and expansion readiness | `context/contracts/analytics-ui-observability-rollout-readiness.json`; `automation/validate_analytics_ui_rollout_readiness.py`; `tests/unit/test_analytics_ui_rollout_readiness.py`; `context/contracts/workbench-panel-registry.json`; `context/contracts/analytics-ui-observability-contract.json` | `python automation\validate_analytics_ui_rollout_readiness.py`; `python -m pytest tests\unit\test_analytics_ui_rollout_readiness.py tests\unit\test_analytics_ui_observability_contract.py tests\unit\test_analytics_ui_canonical_proof_review.py -q`; `python -m ruff check automation\validate_analytics_ui_rollout_readiness.py tests\unit\test_analytics_ui_rollout_readiness.py` | Complete locally for source-backed expansion readiness: certified Workbench route/panel scope is tied to Slice 8 proof, the evidence panel is explicitly `certified_partial`, the reusable rollout checklist is contract-governed, validator proof cases cover forbidden labels and unimplemented metrics, and residual gateway/backend/entitlement scope remains planned | Second-last hardening, API certification review, final docs/context/wiki/skills review, PR merge evidence, and branch hygiene remain. |
| Second-last slice: hardening, review, and certification | `context/contracts/analytics-ui-observability-hardening-review.json`; `automation/validate_analytics_ui_hardening_review.py`; `tests/unit/test_analytics_ui_hardening_review.py`; `platform-stack/grafana/dashboards/analytics-ui-observability-overview.json`; `platform-stack/prometheus/rules/analytics-ui-observability.rules.yml` | `python automation\validate_analytics_ui_observability_contract.py`; `python automation\validate_analytics_ui_rollout_readiness.py`; `python automation\validate_analytics_ui_hardening_review.py`; `python -m pytest tests\unit\test_analytics_ui_observability_contract.py tests\unit\test_analytics_ui_rollout_readiness.py tests\unit\test_analytics_ui_hardening_review.py tests\unit\test_platform_stack_observability_contract.py -q`; `python -m ruff check automation\validate_analytics_ui_observability_contract.py automation\validate_analytics_ui_rollout_readiness.py automation\validate_analytics_ui_hardening_review.py tests\unit\test_analytics_ui_observability_contract.py tests\unit\test_analytics_ui_rollout_readiness.py tests\unit\test_analytics_ui_hardening_review.py` | Complete locally for second-last hardening: telemetry fields, panel states, API/Swagger applicability, dashboard/alert references, enterprise governance, residual planned scope, and no-open-P0/P1 findings are contract-reviewed and validator-protected | Final docs/context/wiki/skills review, PR merge evidence, wiki publication, and branch hygiene remain. |
| Final slice: closure | `context/contracts/analytics-ui-observability-final-closure.json`; `automation/validate_analytics_ui_final_closure.py`; `tests/unit/test_analytics_ui_final_closure.py`; `context/contracts/analytics-ui-observability-contract.json`; `rfcs/README.md`; `context/LOTUS-ENGINEERING-CONTEXT.md`; `context/CONTEXT-REFERENCE-MAP.md`; `wiki/RFC-Index.md` | `python automation\validate_analytics_ui_final_closure.py`; `python -m pytest tests\unit\test_analytics_ui_final_closure.py tests\unit\test_analytics_ui_observability_contract.py tests\unit\test_analytics_ui_rollout_readiness.py tests\unit\test_analytics_ui_hardening_review.py tests\unit\test_platform_stack_observability_contract.py tests\unit\test_analytics_ui_canonical_proof_review.py -q`; `python -m ruff check automation\validate_analytics_ui_final_closure.py tests\unit\test_analytics_ui_final_closure.py`; `powershell -ExecutionPolicy Bypass -File automation\Sync-RepoWikis.ps1 -CheckOnly -Repository lotus-platform` | Complete locally for final closure: implementation-backed supported features are final, residual planned scope remains blocked from promotion, docs/context/wiki source are updated, skills/guidance review records no change required, and wiki publication/branch hygiene are required after merge | Merge PR, publish wiki, delete feature branch, and verify clean repositories. |
| Ecosystem Slice 10: reopen governance and contract expansion | `context/contracts/analytics-ui-observability-ecosystem-completion.json`; `context/contracts/analytics-ui-observability-ecosystem-completion.schema.json`; `automation/validate_analytics_ui_ecosystem_completion.py`; `tests/unit/test_analytics_ui_ecosystem_completion.py`; `context/contracts/analytics-ui-observability-contract.json` | `python automation\validate_analytics_ui_ecosystem_completion.py`; `python automation\validate_analytics_ui_observability_contract.py`; `python -m pytest tests\unit\test_analytics_ui_observability_contract.py tests\unit\test_analytics_ui_rollout_readiness.py tests\unit\test_analytics_ui_hardening_review.py tests\unit\test_analytics_ui_final_closure.py tests\unit\test_analytics_ui_ecosystem_completion.py -q` | Complete for Slice 10: every Lotus app is represented in the gap matrix, first-wave evidence is protected, runtime work was blocked until Slice 10 merged, and unsupported implemented claims are validator-rejected | Slice 11 now owns platform scaffolding and CI enforcement. |
| Ecosystem Slice 11: platform automation, scaffolding, and CI enforcement | `context/contracts/analytics-ui-observability-scaffold-ci-enforcement.json`; `context/contracts/analytics-ui-observability-scaffold-ci-enforcement.schema.json`; `automation/validate_analytics_ui_scaffold_ci_enforcement.py`; `tests/unit/test_analytics_ui_scaffold_ci_enforcement.py`; `automation/New-Lotus-Service.ps1`; `platform-standards/templates/Makefile.backend.template`; `platform-standards/templates/workbench-observability-surface.template.ts`; `automation/Invoke-PlatformRepoChecks.ps1` | `python automation\validate_analytics_ui_scaffold_ci_enforcement.py`; `python automation\validate_analytics_ui_observability_contract.py`; `python automation\validate_analytics_ui_ecosystem_completion.py`; `python -m pytest tests\unit\test_analytics_ui_scaffold_ci_enforcement.py tests\unit\test_repository_hygiene_scaffold_contract.py -q` | Complete locally for Slice 11: generated services start with no-sensitive-content and supported-features gates, Workbench/UI surfaces have a reusable bounded-state safe-label template, platform CI runs the RFC-0108 validators, and runtime app feature keys remain planned | Proceed to Slice 12 backend supportability implementation. |
| Ecosystem Slice 12: backend service freshness and supportability metrics | Partial repo-native implementation in `lotus-core`, `lotus-risk`, `lotus-performance`, `lotus-advise`, `lotus-manage`, `lotus-report`, `lotus-render`, `lotus-archive`, and `lotus-ai`; Gateway PR #166 and Workbench PR #118 now consume performance/risk source supportability for supported Workbench reads; Gateway PR #167 and Workbench PR #120 now consume core portfolio readiness supportability for supported portfolio reads; Gateway PR #168 and Workbench PR #121 now consume manage action-register supportability for supported portfolio workspace rebalance reads; Gateway PR #169 and Workbench PR #122 now consume report evidence-surface supportability for supported report-batch operator reads; Gateway PR #170 and Workbench PR #123 now consume AI surface supportability for supported advisor-brief reads; Workbench PR #119 and lotus-core PR #328 prove clean governed canonical runtime execution | `lotus-core`: `python -m pytest tests\unit\services\query_service\services\test_capabilities_service.py tests\unit\services\query_service\services\test_operations_service.py tests\integration\services\query_control_plane_service\test_operations_router_dependency.py tests\integration\services\query_control_plane_service\test_control_plane_app.py tests\unit\services\query_service\test_openapi_quality_gate.py -q`; `python -m ruff check ...`; `python -m ruff format --check ...`; `python scripts\route_contract_family_guard.py`; `git diff --check`; PR Merge Gate including latency rerun passed. `lotus-risk`: `python -m pytest tests\unit\test_risk_engine_branch_coverage.py tests\unit\test_capabilities_contract.py tests\integration\test_observability.py -q`; `python -m ruff check src\app\observability.py src\app\contracts\capabilities.py src\app\contracts\risk.py src\app\services\risk_engine.py tests\unit\test_risk_engine_branch_coverage.py tests\unit\test_capabilities_contract.py tests\integration\test_observability.py`; `python -m mypy src\app\observability.py src\app\contracts\capabilities.py src\app\contracts\risk.py src\app\services\risk_engine.py`; `python scripts\openapi_quality_gate.py`. `lotus-performance`: repo-native integration/OpenAPI/API-vocabulary/no-alias/domain-product/lint/typecheck proof. `lotus-advise`: `make check` covering lint, typecheck, OpenAPI, no-alias, API vocabulary, domain-data-product validation, and 585 unit tests. `lotus-manage`: `python -m pytest tests\unit\dpm\supportability\test_dpm_run_support_service_coverage.py tests\unit\dpm\api\test_integration_capabilities_api.py tests\unit\dpm\api\test_api_rebalance.py::test_dpm_supportability_summary_endpoint tests\unit\dpm\contracts\test_contract_openapi_supportability_docs.py -q`; `python -m ruff check ...`; `python -m mypy src\api\observability.py src\api\routers\rebalance_runs.py src\core\rebalance_runs\models.py src\core\rebalance_runs\service.py src\core\rebalance_runs\__init__.py`. `lotus-report`: `make check` covering lint, typecheck, OpenAPI, and 419 unit tests plus targeted integration supportability metric proof. `lotus-render`: `make check` covering lint, typecheck, OpenAPI, template registry validation, and 69 unit tests plus GitHub PR Merge Gate with unit/integration/e2e/coverage/Docker build proof. `lotus-archive`: `make check` covering lint, typecheck, OpenAPI, migration gate, and 70 unit tests plus GitHub PR Merge Gate with unit/integration/e2e/coverage/Docker build proof. `lotus-ai`: `python -m pytest tests\unit\test_ai_surface_supportability.py tests\unit\test_observability_runtime.py tests\unit\test_platform_status.py tests\integration\test_observability_api_contract.py -q`; `python -m ruff check ...`; `python -m mypy src\app\services\ai_surface_supportability.py src\app\services\observability_runtime.py`; `git diff --check`. `lotus-gateway`: PR #166 `make check`, `make ci`, Feature Lane, PR Merge Gate, Docker build/parity, and wiki publication proof; PR #167 targeted portfolio contract/router/service tests, `make lint`, targeted mypy, Feature Lane, PR Merge Gate, Docker build/parity, and auto-merge proof; PR #168 targeted DPM client, portfolio service, router, and upstream-client tests, targeted mypy, `make lint`, Feature Lane, PR Merge Gate, Docker build/parity, and auto-merge proof; PR #169 targeted report contract/router tests, targeted mypy, ruff, Feature Lane, PR Merge Gate, Docker build/parity, and wiki publication proof; PR #170 targeted advisor-brief service/client/router tests, targeted mypy, make lint including monetary-float guard, Feature Lane, PR Merge Gate, Docker build/parity, and auto-merge proof. `lotus-workbench`: PR #118 focused unit tests, typecheck, lint, `make check`, green CI, and wiki publication proof; PR #119 `npm test -- --run tests/unit/live-stack-script.test.ts tests/unit/production-ai-env.test.ts tests/unit/scripts-proxy-environment.test.ts`, `npm run typecheck`, `npm run lint`, `npm run live:validate`, green CI, and wiki publication proof; PR #120 focused portfolio API and observability metric tests, typecheck, lint, Feature Lane, PR Merge Gate, Playwright smoke, Docker build/parity, and auto-merge proof; PR #121 focused portfolio API, performance snapshot, and observability metric tests, typecheck, lint, Feature Lane, PR Merge Gate, Playwright smoke, Docker build/parity, and auto-merge proof; PR #122 focused report-batch API and observability metric tests, typecheck, lint, Feature Lane, PR Merge Gate, Playwright smoke, Docker build/parity, and wiki publication proof; PR #123 focused advisor-brief API and observability metric tests, typecheck, lint, Feature Lane, PR Merge Gate, Playwright smoke, Docker build/parity, and auto-merge proof. `lotus-core`: PR #328 `python -m pytest tests/unit/tools/test_front_office_portfolio_seed.py -q`, live canonical reseed evidence for `PB_SG_GLOBAL_BAL_001`, green CI, and wiki publication proof. | Partial: core portfolio readiness, completed risk endpoint families, completed performance calculation families, advisory capabilities supportability, manage supportability summary, report evidence-surface supportability, render metadata supportability, archive metadata supportability, and AI surface supportability now emit source-backed supportability posture and bounded metrics without sensitive labels; Gateway consumes performance/risk source supportability into bounded fan-out and workspace/evidence state, preserves core portfolio readiness supportability into the portfolio readiness API, preserves manage action-register supportability into the portfolio workspace rebalance summary, preserves report evidence-surface supportability into report-batch create/status/run-once responses, and preserves AI surface supportability into advisor-brief responses; Workbench consumes Gateway `source_supportability` into freshness/supportability state and validation `supportabilityChecks`, consumes portfolio readiness supportability into detailed portfolio workspace state plus no-sensitive readiness metrics, consumes manage action-register supportability into portfolio operational support copy plus no-sensitive nested supportability metrics, consumes report evidence-surface supportability into report-batch operator read metrics, and consumes AI surface supportability into advisor-brief read metrics; the governed canonical runtime now passes cleanly for the current supported surface. | Full promotion remains planned for residual full RFC-0079 risk/evidence scope and every supported Workbench surface, not because performance/risk source-supportability propagation, portfolio readiness supportability propagation, manage action-register supportability propagation, report evidence-surface supportability propagation, AI surface supportability propagation, or canonical proof is blocked. |
| Ecosystem Slice 13: Gateway fan-out metrics, protected diagnostics, and audit completion | `lotus-gateway` implementation for selected analytics fan-out metrics, central manage/report/archive/AI client fan-out, direct `lotus-core` query/control-plane and ingestion client fan-out, and protected diagnostics lookup; OpenAPI certification for future changed APIs and dashboard reconciliation remain planned in later ecosystem slices | `lotus-gateway` PR #162: `make check`; protected diagnostics unit/integration proof; targeted `ruff`/`mypy`; migration smoke; Feature Lane and PR Merge Gate including Docker build/parity; wiki publication. `lotus-gateway` PR #163: `make check`; `make migration-smoke`; `make test-integration`; `make test-coverage`; `make security-audit`; Feature Lane and PR Merge Gate including coverage, Docker build, Docker parity, and wiki publication. `lotus-gateway` PR #164: `make check`; `make migration-smoke`; `make test-integration`; `make test-coverage`; `make security-audit`; Feature Lane and PR Merge Gate including coverage, Docker build, Docker parity, and wiki publication. `lotus-platform`: `python automation\validate_analytics_ui_observability_contract.py`; `python automation\validate_analytics_ui_ecosystem_completion.py`; targeted unit validators. | Implemented: `gateway.analytics.observability.fanout_metrics` is promoted for selected Workbench performance/risk analytics fan-out, central manage, report, archive, and AI client seams, and direct `lotus-core` query/control-plane plus ingestion paths. `gateway.analytics.observability.all_ui_fanout_paths` is promoted for implemented Gateway client seams. `gateway.analytics.observability.protected_diagnostics` is promoted for `GET /api/v1/analytics-ui/diagnostics/{support_reference}` with `gdiag-*` opaque references, operator caller context, raw identifier rejection, bounded support posture, and safe `protected_diagnostics_lookup` audit fields. | Later slices still own ecosystem dashboards, live proof, hardening certification, and final closure. |
| Ecosystem Slice 14: Workbench all-surface observability rollout | Partial Workbench implementation for supported Portfolio workspace, client-side Performance, Risk, and explicit report-batch operator reads; endpoint reconciliation is complete for supported API reads, canonical browser proof is captured for `PB_SG_GLOBAL_BAL_001`, source support-state proof is captured, partial RFC-0079 performance evidence-context reconciliation is captured through Gateway and Workbench, Gateway PR #166 completes Gateway-side performance/risk supportability preservation, Workbench PR #118 reconciles Gateway `source_supportability` into supported Workbench reads, Gateway PR #167 and Workbench PR #120 reconcile core portfolio readiness supportability into supported portfolio reads, Gateway PR #168 and Workbench PR #121 reconcile manage action-register supportability into supported portfolio workspace rebalance reads, Gateway PR #169 and Workbench PR #122 reconcile report evidence-surface supportability into supported report-batch operator reads, Gateway PR #170 and Workbench PR #123 reconcile AI surface supportability into supported advisor-brief reads, and Workbench PR #119 plus lotus-core PR #328 prove clean governed canonical runtime execution; full RFC-0079 risk/evidence scope and every supported Workbench surface stay planned | `lotus-workbench`: `npm test -- --run tests/unit/analytics-observability-contract.test.ts tests/unit/analytics-observability-metrics.test.ts tests/unit/workbench-api.test.ts tests/unit/portfolio-api.test.ts`; `npm test -- --run tests/unit/performance-evidence-mode.test.tsx tests/unit/performance-workspace-client.test.tsx`; `npm test -- --run tests/unit/analytics-observability-metrics.test.ts tests/unit/live-validation-calculation-sanity.test.ts`; `npm run typecheck`; `npm run lint`; `make check`; PR #118 green checks; PR #119 defaulted canonical AI env selection to deterministic env proof and passed `npm run live:validate` plus green GitHub checks; PR #120 focused portfolio API and observability metric tests, typecheck, lint, Feature Lane, PR Merge Gate, Playwright smoke, Docker build/parity, and auto-merge proof; PR #121 focused portfolio API, performance snapshot, and observability metric tests, typecheck, lint, Feature Lane, PR Merge Gate, Playwright smoke, Docker build/parity, and auto-merge proof; PR #122 focused report-batch API and observability metric tests, typecheck, lint, Feature Lane, PR Merge Gate, Playwright smoke, Docker build/parity, and auto-merge proof; PR #123 focused advisor-brief API and observability metric tests, typecheck, lint, Feature Lane, PR Merge Gate, Playwright smoke, Docker build/parity, and auto-merge proof; lotus-core PR #328 hardened canonical reseed idempotency and passed live reseed proof plus green GitHub checks. `lotus-gateway`: focused performance evidence context tests, OpenAPI contract test, ruff, and mypy plus PR #166 supportability reconciliation `make check`/`make ci`; PR #167 portfolio contract/router/service tests, `make lint`, targeted mypy, Feature Lane, PR Merge Gate, Docker build/parity, and auto-merge proof; PR #168 targeted DPM client, portfolio service, router, and upstream-client tests, targeted mypy, `make lint`, Feature Lane, PR Merge Gate, Docker build/parity, and auto-merge proof; PR #169 targeted report contract/router tests, targeted mypy, ruff, Feature Lane, PR Merge Gate, Docker build/parity, and auto-merge proof; PR #170 targeted advisor-brief service/client/router tests, targeted mypy, make lint including monetary-float guard, Feature Lane, PR Merge Gate, Docker build/parity, and auto-merge proof. `lotus-platform`: analytics UI observability and ecosystem validators plus focused unit tests; evidence `output\front-office-qa\canonical-front-office-qa-20260430-080907.json`. | Partial with browser, support-state, performance evidence-context, portfolio readiness supportability, manage action-register supportability, report evidence-surface supportability, AI advisor-brief supportability, and clean canonical runtime proof: supported Portfolio, Performance, Risk, and reporting operator reads now emit bounded API duration, panel state, hydration, stale/degraded/partial attention events, no-sensitive metric labels, source-shaped `supportability.state` / `supportability.freshness_bucket` posture, Gateway-backed portfolio readiness supportability, Gateway-backed manage action-register supportability, Gateway-backed report evidence-surface supportability, Gateway-backed AI advisor-brief supportability, and Gateway-backed performance evidence context fields for as-of date, period, basis, benchmark, scope, source services, freshness, methodology, calculation versions, coverage, fallbacks, and limitations through Workbench; Gateway now preserves source supportability for performance/risk analytics, core portfolio readiness, manage action-register reads, and report evidence-surface batch reads, and AI advisor-brief reads; Workbench now derives freshness/supportability from Gateway `source_supportability` arrays, records validation `supportabilityChecks`, carries portfolio readiness supportability into detailed portfolio workspace state and metrics, carries manage action-register supportability into portfolio operational support metrics, and carries report evidence-surface supportability into report-batch operator metrics, and carries AI advisor-brief supportability into advisor-brief metrics; governed canonical proof now passes end to end for the current supported surface. | Full RFC-0079 risk/evidence scope and every supported Workbench surface remain planned residuals. |
| Ecosystem Slice 15: dashboards, alerts, runbooks, and operator diagnostics | `context/contracts/analytics-ui-observability-contract.json`; `context/contracts/analytics-ui-observability-ecosystem-completion.json`; `automation/validate_analytics_ui_observability_contract.py`; `automation/validate_analytics_ui_ecosystem_completion.py`; `platform-stack/grafana/dashboards/analytics-ui-observability-overview.json`; `platform-stack/prometheus/rules/analytics-ui-observability.rules.yml`; `docs/operations/analytics-ui-observability-runbook.md`; platform-stack and contract tests | `python automation\validate_analytics_ui_observability_contract.py`; `python automation\validate_analytics_ui_ecosystem_completion.py`; `python -m pytest tests\unit\test_analytics_ui_observability_contract.py tests\unit\test_platform_stack_observability_contract.py tests\unit\test_analytics_ui_ecosystem_completion.py -q`; `python -m ruff check automation\validate_analytics_ui_observability_contract.py automation\validate_analytics_ui_ecosystem_completion.py tests\unit\test_analytics_ui_observability_contract.py tests\unit\test_platform_stack_observability_contract.py tests\unit\test_analytics_ui_ecosystem_completion.py` | Implemented locally for dashboard, alert, validator, and runbook coverage of every currently implemented RFC-0108 metric family: Workbench panel state, hydration, API latency, attention events, Gateway fan-out duration/degradation, and AI surface supportability. Tests assert implemented-metric-only dashboard and alert coverage, no sensitive dashboard variables, and alert runbook anchors. | Slice 16 now owns supported live ecosystem proof; backend freshness metrics remain intentionally excluded until implementation-backed proof exists. |
| Ecosystem Slice 16: ecosystem implementation proof | `context/contracts/analytics-ui-observability-ecosystem-proof.json`; `context/contracts/analytics-ui-observability-ecosystem-proof.schema.json`; `automation/review_analytics_ui_ecosystem_proof.py`; `tests/unit/test_analytics_ui_ecosystem_proof_review.py`; `output/front-office-qa/latest.json`; `output/rfc-0108-slice-14-canonical-qa/live-validation-summary.json`; live Gateway protected diagnostics and OpenAPI evidence | `python automation\review_analytics_ui_ecosystem_proof.py output\front-office-qa\latest.json --protected-diagnostics-url http://gateway.dev.lotus/api/v1/analytics-ui/diagnostics/gdiag-risk-summary-permission-blocked --gateway-openapi-url http://gateway.dev.lotus/openapi.json`; `python automation\validate_analytics_ui_observability_contract.py`; `python automation\validate_analytics_ui_ecosystem_completion.py`; `python -m pytest tests\unit\test_analytics_ui_ecosystem_proof_review.py tests\unit\test_analytics_ui_ecosystem_completion.py tests\unit\test_analytics_ui_observability_contract.py -q` | Implemented for the current supported ecosystem proof boundary: portfolio state, performance analytics, risk analytics, advisor-brief workflow actions, manage/report capability posture, evidence support posture, AI-backed advisor support, browser screenshots, Gateway-backed APIs, dashboard/alert implemented-metric reconciliation, protected diagnostics lookup, Gateway OpenAPI diagnostics route, residual planned-scope preservation, and no-sensitive evidence assertions all pass machine review. | Slice 17 hardening/certification remains planned; backend freshness metrics, full RFC-0079 risk/evidence scope, and full all-supported-surface promotion remain planned residual scope. |
| Ecosystem Slice 17: ecosystem hardening, review, and certification | `context/contracts/analytics-ui-observability-ecosystem-hardening.json`; `context/contracts/analytics-ui-observability-ecosystem-hardening.schema.json`; `automation/validate_analytics_ui_ecosystem_hardening.py`; `tests/unit/test_analytics_ui_ecosystem_hardening.py` | `python automation\validate_analytics_ui_ecosystem_hardening.py`; `python automation\validate_analytics_ui_observability_contract.py`; `python automation\validate_analytics_ui_ecosystem_completion.py`; focused unit tests and Ruff | Implemented: supported-features posture, per-repository gap-matrix reviews, Slice 16 proof, protected diagnostics OpenAPI evidence, dashboard/alert proof, residual planned scope, and no-open-P0/P1 findings are machine-reviewed before closure. | Slice 18 closes the current implementation-backed ecosystem scope while preserving residuals. |
| Ecosystem Slice 18: final ecosystem closure | `context/contracts/analytics-ui-observability-ecosystem-final-closure.json`; `context/contracts/analytics-ui-observability-ecosystem-final-closure.schema.json`; `automation/validate_analytics_ui_ecosystem_final_closure.py`; `tests/unit/test_analytics_ui_ecosystem_final_closure.py`; `context/contracts/analytics-ui-observability-contract.json`; `context/contracts/analytics-ui-observability-ecosystem-completion.json` | `python automation\validate_analytics_ui_ecosystem_final_closure.py`; `python automation\validate_analytics_ui_observability_contract.py`; `python automation\validate_analytics_ui_ecosystem_completion.py`; `python automation\validate_analytics_ui_ecosystem_hardening.py`; focused unit tests and Ruff | Implemented locally: the reopened RFC-0108 ecosystem scope is closed for current implementation-backed claims, wiki publication and branch hygiene are mandatory after merge, and backend freshness plus full Workbench supported-surface promotion remain planned residuals. | Merge PR, publish wiki, delete feature branch, and verify clean repository state. |

## Final Gold-Pass Assessment

RFC-0108 is implemented for its first-wave governed analytics UI observability scope and the
reopened ecosystem scope is now closed for current implementation-backed claims. The final closure
reconciles the governed live Workbench bundle, Gateway-backed APIs, protected diagnostics, Gateway
OpenAPI route evidence, platform dashboards and alerts, workflow-pack supportability actions,
screenshots, Slice 17 no-open-P0/P1 hardening, residual planned scope, wiki publication
requirements, branch hygiene, and no-sensitive-content assertions. Full RFC-0079 risk/evidence
scope, remaining backend freshness metrics, and full Workbench supported-surface promotion remain
planned residual scope until separately implemented and proved.
Slice 0 is complete for platform automation and scaffolding improvement. Slice 1 is complete for
cleanup and structure: Workbench and Gateway now have code-owned analytics UI observability
vocabulary modules, focused tests reject sensitive/ad hoc labels, repo-local wiki operations
runbooks identify the source of truth, and supported-features governance records only the
implementation-backed contract vocabulary foundations.

Slice 2 is complete for telemetry-contract governance. The platform contract now defines planned
browser events, gateway log events, severity levels, attention event types, audit event types,
trace/attention/audit attributes, dashboard and alert reference policy, and protected diagnostics
policy. Validators reject forbidden fields and references to unimplemented dashboard or alert
metrics. Workbench and Gateway expose matching code-owned constants and tests, still without
emitting product telemetry.

Slice 3 is complete for browser-to-gateway trace and correlation propagation. Workbench now creates
or preserves safe route-scoped correlation context for analytics UI client requests, the BFF proxy
generates missing context and replaces malformed `traceparent` headers before gateway forwarding,
and Gateway backend analytics clients forward the resolved correlation and trace context to
upstream analytics services. Correlation and trace identifiers remain forbidden as metric labels.

Slice 4 is complete for Gateway structured fan-out logging. The Gateway analytics client now emits
bounded structured log events for selected Workbench performance and risk analytics operations,
including completion and degraded/unavailable paths. The log fields are governed separately from
metrics, keep request/response payloads out of telemetry, preserve backend source ownership for
warnings, partial failures, and supportability state, and do not expose portfolio or client
identifiers as fields or labels.

Slice 5 is complete for first-wave Workbench metrics, dashboards, alerts, and freshness contracts.
Workbench now records bounded local browser metric events for selected performance-summary,
performance-details, and risk-summary analytics reads, classifies ready, empty, partial, stale,
degraded, error, permission-blocked, and unsupported states, exposes implemented metric families
through `/api/metrics`, and excludes portfolio, client, trace, correlation, request/response body,
and screen-content fields from labels. Platform now records the implemented metric inventory,
scrapes the Workbench metrics route in the platform stack, and owns Grafana dashboard and
Prometheus alert artifacts that validate against implemented metrics only.

Slice 6 is complete for UI state and attention events. Workbench now emits bounded local attention
events and the `lotus_analytics_ui_attention_events_total` counter for stale, degraded,
partial-source, and repeated-failure selected analytics panel states. Attention emission is
deduplicated by governed label identity, repeated failures require a threshold before escalation,
reason values are bounded source-backed codes, and portfolio, client, trace, correlation,
request/response body, and screen-content fields remain excluded. Platform now records the
implemented attention metric and browser event, adds the dashboard panel and alert rule, and
documents operator response guidance.

Slice 7 is complete for selected Gateway analytics read audit events. Gateway now emits bounded
structured audit logs for selected Workbench performance and risk analytics reads: successful
upstream reads emit `gateway.analytics.audit.analytics_read_allowed`, and upstream `401`/`403`
denials emit `gateway.analytics.audit.analytics_read_denied`. Audit fields are limited to route,
panel, operation, state, reason, status class, region, and environment. Tests prove that portfolio,
client, request/response body, and raw entitlement-failure content are excluded. This slice does
not claim full caller-context entitlement certification or protected diagnostics lookup audit.
Slice 13 later implements protected diagnostics lookup audit; full caller-context entitlement
certification remains planned.

Slice 8 is complete for canonical Workbench implementation proof. The governed runtime was brought
up with `PB_SG_GLOBAL_BAL_001` and `BMK_PB_GLOBAL_BALANCED_60_40`, the seed converged to complete
position and cash quality, API checks passed through the Gateway, calculation sanity checks passed,
panel classifications reconciled with the governed registry, and seven browser screenshots were
captured after validation for portfolio summary, portfolio detailed, performance summary,
performance analysis, advisor brief, risk, and evidence panels. Platform added
`automation/review_analytics_ui_canonical_proof.py` plus unit tests so the proof bundle is reviewed
for live-summary presence, screenshot/index completeness, calculation and panel evidence,
dashboard/alert implemented-metric reconciliation, and forbidden sensitive evidence terms. The live
Workbench `/api/metrics` endpoint exposed the four implemented metric families:
`lotus_workbench_panel_hydration_duration_seconds`, `lotus_workbench_panel_state_total`,
`lotus_workbench_api_request_duration_seconds`, and `lotus_analytics_ui_attention_events_total`.
The evidence panel remains truthfully classified as `partial`; this is an implementation-backed
supportability state, not a cosmetic success claim.

Gateway/backend metrics, full caller-context entitlement certification, and broad rollout beyond
the canonical path were deliberately left planned at first-wave closure. This RFC is now reopened
to finish those items and extend the same observability and operational posture across every Lotus
application. Slice 13 later adds selected Gateway fan-out metrics and protected diagnostics lookup
without closing all UI-facing Gateway fan-out coverage.

Slice 9 is complete for rollout proof and expansion readiness. Platform now owns
`context/contracts/analytics-ui-observability-rollout-readiness.json` and schema, with certified
Workbench route and panel scope sourced from Slice 8 canonical proof. The contract records the
portfolio summary, portfolio detailed, performance summary, performance analysis, advisor brief,
risk, and evidence routes. The evidence route is explicitly `certified_partial` because full
evidence and lineage behavior remains governed by RFC-0079; this prevents the partial support state
from being converted into a broad success claim. The rollout checklist requires panel-registry
ownership, code-owned vocabulary, bounded telemetry, implemented-metric-only dashboards and alerts,
browser/API/calculation/panel proof, sensitive-content assertions, supported-features promotion
only after proof, and residual-scope ownership. The Slice 9 validator also proves that expansion
governance catches forbidden metric labels and unimplemented dashboard metric references before
unsupported observability claims can ship.

After Slice 9, gateway fan-out metrics, backend freshness/supportability metrics, full
caller-context entitlement certification, and broad rollout beyond the certified Workbench routes
remain planned and deliberately blocked from supported-feature promotion. Slice 13 later promotes
selected Gateway fan-out metrics and protected diagnostics while keeping all UI-facing Gateway
fan-out rollout planned.

The second-last hardening, review, and certification slice is complete for RFC-0108's current
implementation-backed scope. Platform now owns
`context/contracts/analytics-ui-observability-hardening-review.json` and schema plus
`automation/validate_analytics_ui_hardening_review.py`. The review validates all implemented
telemetry fields against the governed allowed-label and forbidden-field policy, confirms the
certified Workbench route groups remain tied to the panel registry and Slice 9 rollout contract,
certifies the platform dashboard and alert rules against implemented metrics and runbook links,
records API/Swagger applicability, and verifies that no P0/P1 privacy, telemetry,
unsupported-feature, or panel-state finding remains open. The review also records that RFC-0108
did not add a new Gateway or backend HTTP API shape requiring new OpenAPI operations: Workbench
`/api/metrics` is an internal Prometheus text endpoint outside OpenAPI schema, while existing
Gateway Workbench analytics APIs remain covered by Gateway contract tests. Backend
freshness/supportability metrics, full caller-context entitlement certification, and broad rollout
remain planned and deliberately blocked from supported-feature promotion at this historical
first-wave hardening boundary; Slice 13 later promotes selected Gateway fan-out metrics, protected
diagnostics, and all implemented Gateway client fan-out path coverage.

The final closure slice is complete locally for RFC-0108's current implementation-backed scope.
Platform now owns `context/contracts/analytics-ui-observability-final-closure.json` and schema plus
`automation/validate_analytics_ui_final_closure.py`. The final closure contract records the merged
implementation PRs, required local proof commands, required GitHub checks, repo-local wiki
publication requirement, clean-state branch hygiene expectations, and residual planned scope. It
also promotes only `platform.analytics.observability.final_closure` as an implementation-backed
supported feature; gateway fan-out metrics, backend freshness/supportability metrics, and
Workbench source-backed freshness/degraded-state expansion remain planned.

The required skills, guidance, documentation, and agent-context review found no new routing or
skill change is needed for RFC-0108 closure. Existing Lotus guidance already routes canonical
Workbench proof through `lotus-front-office-runtime`, governed RFC and context updates through the
RFC/context documentation flow, and PR/merge discipline through the pre-merge governance flow. The
deliberate outcome is therefore no skill-map or AGENTS operating-contract change in the final
slice. Wiki source is updated in this repository and must be published with
`automation/Sync-RepoWikis.ps1 -Publish -Repository lotus-platform` after the final PR merges.
