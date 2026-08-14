# Lotus Engineering Context

This is the canonical ecosystem context for Lotus engineering work.

Use this file after the [Lotus Quickstart Context](./LOTUS-QUICKSTART-CONTEXT.md). Use the repository-local `REPOSITORY-ENGINEERING-CONTEXT.md` for implementation truth inside a specific repository.

## Purpose

Lotus is a governed private banking technology ecosystem. It is not a loose collection of apps.

The ecosystem is designed to support:

1. portfolio management,
2. performance analytics,
3. risk analytics,
4. advisory workflows,
5. reporting and evidence production,
6. platform-grade runtime, validation, CI, ingress, and governance.

The engineering goal is a premium, production-critical, banking-grade platform where architecture clarity, operational rigor, and domain correctness are non-negotiable.

## Application Roles

### Product and experience layer

1. `lotus-workbench`
   The primary product UI. It should present a coherent banking-grade user experience and consume the unified contract from `lotus-gateway`.

2. `lotus-gateway`
   The experience API and composition layer. It provides the governed client contract for UI experiences and mediates access to domain services.

### Domain-authoritative services

1. `lotus-core`
   Authoritative for portfolio, booking, account, holding, mandate, and transaction domain data.

2. `lotus-performance`
   Authoritative for performance metrics, period analytics, and related review data.

3. `lotus-risk`
   Authoritative for drawdown, attribution, concentration, rolling risk, and related analytics.

4. `lotus-advise`
   Advisory workflow and recommendation capability.

5. `lotus-manage`
   Discretionary mandate portfolio-management execution and operational supportability capability.

6. `lotus-report`
   Reporting and document generation capability.

7. `lotus-render`
   Deterministic document rendering capability for governed reporting flows.

8. `lotus-archive`
   Generated-document archive, retrieval, retention, legal hold, access-audit, and lifecycle capability.

9. `lotus-idea`
   Wealth opportunity intelligence, idea lifecycle, governed idea evidence, and conversion
   orchestration capability.

10. `lotus-ai`
   Shared AI capability service used behind governed product and platform flows.

### Platform and governance

1. `lotus-platform`
   Owner of shared automation, ingress, standards, validation, CI governance, and environment-level operational guidance.

## Architectural Relationships

The canonical relationship model is:

1. `lotus-workbench` consumes `lotus-gateway`,
2. `lotus-gateway` consumes or aggregates domain-authoritative services,
3. domain services remain authoritative for their business domain,
4. `lotus-report` may orchestrate reporting flows across upstream domain services and `lotus-render`,
5. `lotus-archive` owns durable generated-document archive records and retrieval governance after document generation,
6. `lotus-idea` owns opportunity intelligence and idea lifecycle state without cloning source-owned portfolio,
   performance, risk, advisory, management, reporting, archive, render, gateway, or AI capabilities,
7. `lotus-platform` governs how the ecosystem is run, validated, and standardized.

### Boundary rules

1. UI features must not be superficially invented at the presentation layer.
2. Experience composition belongs in `lotus-gateway`, not scattered into direct UI-to-service coupling.
3. Domain-specific business logic belongs in the authoritative service or a governed view-model layer, not as uncontrolled UI logic.
4. Standards, validators, and platform automation are part of the architecture and should be maintained with the same discipline as product code.

## Domain Data Product Governance

For cross-domain governed data products:

1. `docs/standards/Lotus Data Mesh Standard.md` is the platform-owned human standard for what data
   mesh means in Lotus, how product authority is separated from platform certification, how app
   roles map across the ecosystem, and what proof is required before a product can be called mesh
   certified,
2. domain repositories remain authoritative for product truth,
3. `lotus-platform/platform-contracts/domain-data-products/` is the platform-owned contract family
   for producer and consumer declarations introduced by RFC-0084,
4. `lotus-platform/platform-contracts/domain-vocabulary/domain-data-product-semantics.v1.json`
   is the governed identifier, temporal-semantic, and trust-vocabulary registry that those
   declarations must reference,
5. `lotus-platform/platform-contracts/domain-vocabulary/domain-data-product-trust-metadata.v1.json`
   is the governed trust metadata field registry, evidence-class registry, and lineage-bundle
   registry for those declarations,
6. `lotus-gateway` may publish and compose APIs around those products, but it does not become the
   product authority or product registry,
7. the current RFC-0086 included repo-native rollout set is `lotus-core`, `lotus-performance`,
   `lotus-risk`, `lotus-advise`, `lotus-report`, `lotus-manage`, `lotus-gateway`, and `lotus-idea`,
8. current repositories with governed producer declarations are `lotus-core`, `lotus-performance`,
   `lotus-risk`, `lotus-advise`, `lotus-report`, `lotus-manage`, and `lotus-idea`; current
   consumer-declaration participants are `lotus-performance`, `lotus-risk`, `lotus-advise`,
   `lotus-report`, `lotus-manage`, `lotus-gateway`, and `lotus-idea`, while `lotus-gateway` remains
   consumer-only,
9. `lotus-idea` is repo-native and included by default in canonical platform/runtime automation, but
   its opportunity-intelligence products remain mesh-certification gated until runtime trust
   telemetry, SLO, access, evidence, Gateway, Workbench, and supported-feature proof pass,
10. `lotus-ai` is not a first-wave domain-product producer or consumer declaration participant until
   it owns a stable governed product or catalog-consuming capability,
11. producer and consumer declarations should stay explicit, version-aware, registry-backed, and
   validator-backed.

## Lifecycle Authority Interoperability

For signed legal-hold and privacy lifecycle decisions:

1. bank legal and records governance owns hold and release approval,
2. bank privacy governance owns erasure and purge approval,
3. a bank-controlled integration issues signed decisions and publishes managed trust keys,
4. Lotus consumers verify signature, audience, tenant and subject scope, validity, key posture,
   replay nonce, and durable single-use enforcement,
5. `platform-contracts/lifecycle-authority/` governs interoperability schemas and producer
   certification evidence without becoming a runtime decision authority,
6. `automation/validate_lifecycle_authority_contracts.py` enforces semantic mappings, source-safe
   evidence, key lifecycle posture, and fail-closed non-certification,
7. create a separately deployable authority adapter only when bank ownership, workload,
   failure-isolation, and operability evidence justify that runtime boundary.

## Domain Vocabulary Governance

For analytics period naming:

1. `lotus-platform/platform-contracts/domain-vocabulary/canonical-performance-periods.v1.json`
   is the platform-owned vocabulary for performance, risk, reporting, and front-office period
   values,
2. new or materially changed APIs should expose canonical period codes such as `YTD`, `1Y`, `3Y`,
   `5Y`, `SI`, `YEAR`, and `EXPLICIT`,
3. legacy service values such as `ONE_YEAR`, `THREE_YEAR`, `FIVE_YEAR`, and `ITD` may be accepted
   only when listed as aliases in the platform contract and normalized internally,
4. Swagger/OpenAPI examples should use canonical period codes unless they are explicitly
   documenting a legacy compatibility path,
5. services should not introduce local period enum values without first updating the platform
   vocabulary with semantics, required fields, ownership, and migration posture.

For RFC-0087 live trust telemetry:

1. `platform-contracts/trust-telemetry/` owns the governed telemetry snapshot contract,
2. `automation/validate_trust_telemetry.py` validates snapshots against the generated catalog and
   trust vocabulary,
3. first-wave producer snapshots live in `lotus-core`, `lotus-performance`, `lotus-risk`, and
   `lotus-advise` under `contracts/trust-telemetry/`,
4. `automation/generate_live_trust_certification.py` creates derived live-trust certification
   artifacts from validated snapshots,
5. gateway and Workbench must consume certified trust posture through governed APIs rather than
   inventing decorative trust state.

For the RFC-0085/RFC-0088 first-wave publication and discovery path:

1. `lotus-gateway` is the API publication face for generated domain-product discovery and trust
   evidence; it must not become a product registry or domain-product authority,
2. gateway exposes read-only domain-product catalog, detail, dependency graph, and trust
   certification APIs under `/api/v1/domain-products`,
3. gateway reads platform-generated discovery and live-trust artifacts and returns explicit
   unavailable or degraded posture when certified platform evidence is absent,
4. `lotus-workbench` exposes the first-wave self-serve discovery UI at `/data-products`,
5. Workbench discovery must consume gateway through the BFF only and must not read platform files
   directly or invent decorative trust state,
6. RFC-0085, RFC-0087, and RFC-0088 are implemented and merged for the first-wave mesh surface:
   platform PR #149 closed platform evidence, gateway PR #136 merged the publication/trust API
   surface, and Workbench PR #97 merged the `/data-products` discovery UI.
7. RFC-0089 is implemented for first-wave mesh certification enforcement:
   `automation/mesh_certification_gate.py` composes the domain-product catalog, source manifest,
   RFC-0087 telemetry validation, live trust certification, gateway publication drift checks, and
   Workbench gateway/BFF-only consumption checks. Platform CI runs an advisory gate smoke through
   `automation/Invoke-PlatformRepoChecks.ps1`; local blocking proof with sibling repositories uses
   `python automation/mesh_certification_gate.py --mode blocking --generated-at-utc 2026-04-20T00:00:00Z --require-sibling-repos`.
   Branch-local repo-native declaration previews can use
   `--catalog-source current-repo-native` to derive temporary catalog artifacts under the gate
   output directory without mutating checked-in generated catalog truth.
8. RFC-0090 is implemented for GitHub cross-repo mesh certification enforcement:
   `.github/workflows/mesh-certification-gate.yml` checks out first-wave producer repositories,
   `lotus-gateway`, and `lotus-workbench` next to `lotus-platform`, runs the RFC-0089 gate in
   blocking mode, uploads mesh-certification artifacts, and keeps product authority in producer
   repositories and platform-generated evidence rather than gateway or Workbench.
9. RFC-0091 is implemented for enterprise mesh maturity. Slice 0 provides the generated maturity
   matrix, Slice 1 provides `automation/generate_domain_product_onboarding.py` for
   scaffold-and-check onboarding bundles, Slice 2 provides
   `automation/collect_trust_telemetry.py` for runtime-preferred telemetry collection, Slice 3
   provides `platform-contracts/mesh-slo/` plus `automation/validate_mesh_slo_policies.py`, and
   Slice 4 provides `platform-contracts/mesh-access/` plus
   `automation/validate_mesh_access_policies.py`. Slice 5 provides
   `platform-contracts/mesh-evidence/` plus `automation/generate_mesh_evidence_pack.py` for
   certification-history and evidence-pack manifests. Slice 6 promotes
   `lotus-report:ClientReportEvidencePack:v1` and
   `lotus-manage:PortfolioActionRegister:v1` into the enterprise maturity wave.
   Slice 7 turns mesh certification into an enterprise maturity gate with operator-facing
   telemetry, SLO, access, lifecycle, evidence, catalog, gateway, and Workbench check families,
   evidence-policy validation, lifecycle drift validation, and RFC-0091 `enterprise-mesh-*`
   artifacts. Slice 8 centralizes the maturity-wave scope in
   `automation/mesh_maturity_scope.py`; new platform mesh automation should import that module
   instead of copying product lists. Slice 9 completed the final documentation, context, wiki,
   skills-routing, and branch-hygiene readiness updates.
   Generated onboarding bundles are starter artifacts for owning repositories; they are not
   platform-owned product truth until the owner replaces placeholders, adds repo-native tests,
   emits telemetry, and passes certification. RFC-0087/RFC-0091 onboarding scaffolds now include
   source-data API profile, API certification, and ingestion-pipeline checklists so new source
   products start with explicit ingestion, serving API, downstream consumption, OpenAPI,
   observability, and live-evidence expectations. Static telemetry fixtures remain explicit
   fallback evidence and must not masquerade as runtime telemetry. Mesh SLO, access-policy, and
   evidence-pack drift are certification evidence and must not be handled as separate decorative
   reports. Public customer evidence packs must not expose restricted telemetry paths, source
   artifacts, or consumer entitlement details.
10. RFC-0104 is implemented for first-wave batch reporting scope. Slice 0 strengthens
   `automation/New-Lotus-Service.ps1` so newly scaffolded FastAPI services include
   Swagger-quality health, liveness, readiness, and metadata endpoints plus a generated OpenAPI
   quality gate that checks summaries, descriptions, tags, response descriptions, 2xx responses,
   and success examples. Slice 1 adds the `lotus-report` `report_batch_orchestrator` module
   boundary and planned selector/frequency vocabulary while keeping
   `BATCH_RUNTIME_SUPPORTED = False`. Slice 2 adds internal durable `report_batch` and
   `report_batch_item` materialization for explicit portfolio lists and selected subsets, with
   source-backed validation and idempotent duplicate prevention. Slice 3 adds deterministic
   schedule-cycle materialization and scheduled idempotency identity for monthly, quarterly,
   semi-annual, yearly, and explicit cycles. Later slices add certified materialization/status/
   control APIs, dispatch/lease/back-pressure, retry/recovery controls, internal item execution
   through report-job/snapshot/render/archive handoff, bounded run-once, bounded runtime-pass,
   daemonized worker-process execution, config-backed internal scheduler-process materialization
   with explicit/all-active/inline-manifest scheduler selectors, gateway-facing batch
   materialization/status/control/operator-run APIs, gateway-facing scheduler administration, and
   Workbench gateway/BFF-backed explicit single-portfolio batch operation. RFC-0105
   dashboards/replay, RFC-0106 security certification, and RFC-0107 production certification remain
   pending later work.
11. RFC-0105 is implemented for first-wave scope after completing Slice 0 platform scaffold hardening, Slice 1
    `lotus-report` observability structure cleanup, Slice 2 cross-service trace and structured
    logging proof after RFC-0104 closure, Slice 3 first-wave reporting metrics, dashboard,
    alert, and SLA contracts, Slice 4 first-wave report-job operator diagnostics, Slice 5
    archived-report rerender from immutable snapshot, Slice 6 regenerate from upstream data,
    Slice 7 failed-work replay for failed retry-eligible report jobs and implementation-backed
    batch items, Slice 8 source-backed stuck-state/SLA attention scanning, and Slice 9 live
    implementation proof through `lotus-report/output/rfc-0105-live-evidence-20260428-165945`
    plus the gold-pass audit rerun
    `lotus-report/output/rfc-0105-live-evidence-20260428-234551`, which preserved numbered
    per-call render/archive evidence captures.
    It may
    consume RFC-0104 durable batch, gateway, Workbench, and
    scheduler-administration identifiers as source-backed observability inputs. The platform
    scaffold now defaults future FastAPI services to correlation-id plus trace-id propagation,
    caller-context and capability-policy primitives, downstream-client resilience templates,
    write-capable idempotency/audit models, demo-claims documentation with governed status
    vocabulary, and opt-in planned/not-certified mesh placeholders with a generated
    `data-mesh-contract-gate` for mesh-capable scaffolds,
    `lotus-report` now owns runtime correlation, request, trace, structured-log, and safe operator
    lookup vocabulary in `src/app/observability.py`, gateway/report/render/archive now preserve
    caller correlation and trace identifiers through live batch-to-archive proof while suppressing
    malformed `traceparent` headers for non-W3C trace IDs, and platform observability contracts now
    inventory first-wave report/render/archive metrics, dashboards, alert rules, and initial SLA
    objectives without claiming stuck-state or replay behavior. `lotus-report` now exposes
    `GET /reports/jobs/{job_id}/diagnostics` as a source-backed one-job operator view over status,
    latest lifecycle event, snapshot posture, upstream-lineage summary, render metadata, and archive
    handoff identifiers without raw payloads or storage references, exposes
    `POST /reports/jobs/{job_id}/rerender` for already archived PDF jobs to create an idempotent
    correction from the same snapshot id/hash with a new rerender/render/archive identity and no
    upstream recollection, exposes `POST /reports/jobs/{job_id}/regenerate` for already archived
    PDF jobs to create a new report job, fresh upstream snapshot and lineage bundle, and replacement
    archive document with explicit old/new identities, exposes `POST /reports/jobs/{job_id}/replay`
    for failed retry-eligible report jobs, and exposes
    `POST /reports/batches/{batch_id}/items/{batch_item_id}/replay` for failed retry-eligible
    implementation-backed batch items linked to failed report jobs, and exposes
    `GET /reports/operations/attention` for bounded source-backed stuck-state and SLA-breach
    attention events over active report jobs and batch items without raw payloads, portfolio scope,
    tenant identifiers, correlation identifiers, or trace identifiers. GitHub CI is green for
    Slice 7 on `lotus-report` PR `sgajbi/lotus-report#83` head
    `23dd048a3d2ee1f2dfc3fe4452b31953a8a93b4f`, including feature lane, PR merge gate
    unit/integration/e2e, combined coverage, and Docker build. Slice 8 is proven on
    `f063bbc7541d72f85ddc2e8e8a12ed27efd0665d`; GitHub PR #83 is green including feature lane
    lint/type/security and unit checks plus PR merge gate lint/type/security, unit, integration,
    e2e, combined coverage, Docker build, and workflow lint. RFC-0105 final closure is recorded
    for first-wave scope on `lotus-report` head
    `746234474cdfa25c95f08ca4796f893185b58b50` and `lotus-platform` head
    `ee835094e7bc0f407fe2afb002c90e0bccdbcd05`.
12. RFC-0108 is implemented for first-wave scope and the reopened ecosystem scope is closed for
    current implementation-backed claims. It governs front-office analytics
    UI observability across Workbench browser rendering, gateway/BFF/API delivery, backend
    analytics API fan-out, panel state, calculation freshness, empty/degraded/stale/error and
    permission-blocked states, attention events, entitlement-relevant audit events, safe operator
    diagnostics, and canonical proof using `PB_SG_GLOBAL_BAL_001`. RFC-0108 is not an extension of
    RFC-0105; reporting observability tracks asynchronous report evidence production, while
    analytics UI observability tracks interactive read/display flows and frontend/backend
    correlation from browser to gateway to backend. UI telemetry must not expose client names,
    portfolio ids, holdings, screen content, advisor behavior, raw entitlement failures, request/
    response bodies, trace ids, or correlation ids as metrics labels. Slice 0 added
    `context/contracts/analytics-ui-observability-contract.json`,
    `automation/validate_analytics_ui_observability_contract.py`, and generated-service scaffold
    defaults for product-safe problem-details errors, structured JSON application events,
    supported-features placeholders, RFC implementation evidence scaffolding, operations
    observability documentation, and API certification documentation. Slice 1 added Workbench and
    Gateway code-owned observability vocabulary foundations with tests that reject sensitive or
    ad hoc labels before runtime telemetry exists. Slice 2 added the governed telemetry contract
    for browser events, gateway log events, severity levels, attention/audit event types, trace
    attributes, dashboard/alert reference policy, protected diagnostics policy, and matching
    Workbench/Gateway code-owned constants and tests. Slice 3 added safe Workbench browser/BFF/
    gateway/backend correlation and trace propagation with malformed traceparent replacement and
    backend analytics-client forwarding proof. Slice 4 added product-safe Gateway structured
    fan-out logs for selected Workbench performance and risk analytics operations, preserving
    source-backed warnings, partial failures, supportability state, status class, and bounded
    degraded reasons without request/response payload fields or portfolio/client identifiers.
    Slice 5 added first-wave Workbench browser metric events and a Prometheus scrape path for
    selected performance-summary, performance-details, and risk-summary analytics reads, plus a
    platform Grafana dashboard and Prometheus alert rules that reference only implemented
    Workbench metric-family names. Slice 6 added Workbench attention events and the
    `lotus_analytics_ui_attention_events_total` counter for stale, degraded, partial-source, and
    repeated-failure selected analytics panel states, with bounded severity, deduplication,
    source-backed reason codes, and no sensitive metric labels. Slice 7 added Gateway product-safe
    structured analytics read audit logs for selected Workbench performance and risk analytics
    operations: successful upstream reads emit bounded `analytics_read_allowed` events, upstream
    `401`/`403` denials emit bounded `analytics_read_denied` events, and tests prove portfolio,
    client, request/response body, and raw entitlement-failure content stays out of audit fields.
    Slice 8 added governed canonical Workbench proof for `PB_SG_GLOBAL_BAL_001`, platform
    proof-review automation, browser screenshots, API/calculation/panel evidence, Workbench
    `/api/metrics` family exposure, dashboard/alert reconciliation, and sensitive-content
    assertions. Slice 9 added
    `context/contracts/analytics-ui-observability-rollout-readiness.json` and
    `automation/validate_analytics_ui_rollout_readiness.py`, tying certified Workbench route/panel
    scope to Slice 8 proof, recording the reusable expansion checklist, proving forbidden-label
    and unimplemented-metric validator failures, and keeping gateway/backend metrics, full
    caller-context entitlement certification, all UI-facing Gateway fan-out rollout, and broad
    rollout planned until later slices. The second-last slice added
    `context/contracts/analytics-ui-observability-hardening-review.json` and
    `automation/validate_analytics_ui_hardening_review.py`, validating telemetry fields, panel
    states, API/Swagger applicability, dashboard/alert certification, enterprise governance,
    residual planned scope, and no-open-P0/P1 findings before final closure. The final closure
    slice added `context/contracts/analytics-ui-observability-final-closure.json` and
    `automation/validate_analytics_ui_final_closure.py`, recording implemented-scope closure,
    merged PR evidence, required proof commands, required GitHub checks, wiki publication
    requirements, clean-state branch hygiene, residual planned scope, and an explicit no-change
    decision for skills/guidance because existing Lotus routing already covers canonical Workbench
    proof, RFC/context governance, and PR pre-merge discipline. The ecosystem-completion wave added
    required Slices 10-18 to finish current-scope uniform observability and operational posture across
    `lotus-workbench`, `lotus-gateway`, `lotus-core`, `lotus-performance`, `lotus-risk`,
    `lotus-advise`, `lotus-manage`, `lotus-report`, `lotus-render`, `lotus-archive`, `lotus-ai`,
    and `lotus-platform`. Slices 10 and 11 are complete with
    `context/contracts/analytics-ui-observability-ecosystem-completion.json`,
    `automation/validate_analytics_ui_ecosystem_completion.py`, a validator-protected per-app gap
    matrix, first-wave protected evidence, required GitHub checks, and branch policy that blocks
    runtime work before contract expansion is merged, plus
    `context/contracts/analytics-ui-observability-scaffold-ci-enforcement.json`,
    `automation/validate_analytics_ui_scaffold_ci_enforcement.py`, generated backend
    AST-backed monetary-float, no-sensitive-content, implementation-truth, and supported-features gates, a reusable
    Workbench/UI observability template, and platform repo check wiring that keeps the baseline
    platform-owned. Slice 12 is
    now partially implemented: `lotus-risk` `POST /analytics/risk/calculate` emits
    `metadata.calculation_supportability`, bounded
    `lotus_risk_calculation_supportability_total` labels, and the implemented feature key
    `risk.observability.calculation_supportability`; `lotus-manage`
    `GET /api/v1/rebalance/supportability/summary` emits `supportability.state`,
    `supportability.reason`, `supportability.freshness_bucket`, bounded
    `lotus_manage_action_register_supportability_total` labels, and the implemented feature key
    `manage.observability.action_register_supportability`. Later PRs completed performance/risk
    backend freshness supportability and Gateway/Workbench source-supportability reconciliation for
    current supported reads; Slice 12 remains partially implemented only because full Workbench
    all-supported-surface and full RFC-0079 risk/evidence promotion stay planned. Slice 13 now has
    implementation-backed Gateway proof for selected analytics fan-out metrics, protected
    diagnostics lookup, central manage/report/archive/AI client fan-out metrics, and direct
    lotus-core query/control-plane plus ingestion fan-out metrics. Slice 14 is partially
    implemented for supported Portfolio workspace, client-side Performance, Risk, explicit
    report-batch operator reads, and Gateway-backed Workbench archive metadata/download reads; Slice
    15 implements ecosystem dashboard/alert/runbook coverage for
    current metric families; Slice 16 implements platform-owned ecosystem proof automation; and
    Slice 17 implements ecosystem hardening certification with a machine-readable contract and
    validator. Slice 18 implements ecosystem final closure with
    `context/contracts/analytics-ui-observability-ecosystem-final-closure.json`,
    `automation/validate_analytics_ui_ecosystem_final_closure.py`, and focused unit tests that
    reconcile Slice 17 hardening, Slice 16 proof, ecosystem completion status, supported-feature
    posture, residual planned scope, local/GitHub proof requirements, wiki publication, branch
    hygiene, and skills guidance. Performance/risk backend freshness is now implementation-backed
    through lotus-performance PR #139 and lotus-risk PR #108, lotus-performance PR #140 hardening
    capability publication so completed MWR, contribution, or attribution supportability cannot be
    hidden by a disabled TWR capability, and lotus-performance PR #141 hardening explicit
    performance `metric_labels`, shared bounded Prometheus label tuples, and no-sensitive
    metric-label proof. Workbench PR #132 closes the 2026-05-01
    gold-pass visual hardening follow-up for the performance Summary surface: Horizon support
    values and Performance Drivers now fit the governed desktop viewport, ready-with-empty
    attribution/contribution detail contracts render truthful partial states, live Workbench e2e and
    canonical validation passed, and Workbench wiki source was published. Full RFC-0079
    risk/evidence Workbench promotion remains planned until separately implemented and proved;
    Workbench archive retrieval is implemented only through the BFF/Gateway boundary. Workbench
    PR #133 closes the current certified read-path entitlement proof gap: performance Summary, Risk
    Review, and Advisor Brief now render bounded permission-blocked UI states without raw Gateway
    entitlement response bodies, the platform entitlement certification contract is promoted for
    the current certified paths, and future certified read paths must provide equivalent
    Gateway allow/deny audit, caller-context enforcement, BFF forwarding, permission-blocked UI,
    live evidence, tests, and wiki proof before promotion. Workbench PR #134 adds
    implementation-backed Advisor Brief review-action mutation observability through the
    bounded `performance-advisor-brief-review-action` surface, `/api/metrics/events` browser
    metric ingest, `/api/metrics` export, bounded mutation errors, Gateway log/trace proof, and
    no-sensitive metric label assertions. Gateway PR #179 hardens the downstream ownership
    boundary: proposal simulation, create, list, detail, version, workflow, approval, and lineage
    calls now target `lotus-advise` `/advisory/proposals*`, while Gateway `lotus-manage`
    consumption is limited to `GET /api/v1/rebalance/runs`,
    `GET /api/v1/rebalance/supportability/summary`, and
    `GET /api/v1/platform/capabilities`; stale manage proposal and unversioned rebalance paths are
    prohibited by tests, docs, and wiki proof. Workbench PR #136 adds the production boundary that
    state-changing Workbench actions, including the Advisor Brief review-action mutation, record
    API request and panel-state metrics without incrementing panel hydration; the live proof
    recorded `hydrationReviewActionLineCount=0` and `leakedForbidden=[]`. lotus-ai PR #57 hardens
    AI surface supportability proof with bounded `supportability_reason`, explicit
    `metric_labels`, sensitive-diagnostic rejection tests, Prometheus metric-label tests,
    `make check`, `make ci`, Docker build, and published wiki source. lotus-core PR #329 hardens
    portfolio readiness supportability proof with explicit `metric_labels`,
    `lotus_core_portfolio_supportability_total` labels bounded to `state`, `reason`, and
    `freshness_bucket`, no-sensitive Prometheus label tests, full local and GitHub runtime gates,
    and published wiki source. lotus-risk PR #109 hardens risk supportability proof with explicit
    `metric_labels`, shared bounded label tuples for `lotus_risk_calculation_supportability_total`
    and `lotus_analytics_freshness_bucket_total`, no-sensitive Prometheus label tests, full local
    and GitHub runtime gates, and published wiki source. lotus-advise PR #109 hardens advisory
    supportability proof with explicit `supportability.metric_labels`, bounded
    `lotus_advise_advisory_supportability_total` labels, no-sensitive Prometheus label tests, full
    local and GitHub runtime gates, and published wiki source. Full all-supported-surface
    promotion remains separately gated.
13. The current RFC-0091 maturity-wave required product set is seven products: core portfolio
    state, core DPM source readiness, performance returns, risk metrics, advisory proposal
    lifecycle, report evidence pack, and management action register.
14. RFC-0092 is implemented for production mesh operations. The mesh certification gate now writes
    `enterprise-mesh-operating-report.json` and `.md` alongside certification status artifacts.
    The operating report consumes current certification status and optional certification-history
    records, then reports operating state, limited-history posture, drift trend, regression since
    prior certified posture, product operating posture, escalation ownership, and operator guidance.
    It is operational evidence, not product truth and not customer evidence export.
15. The durable mesh completion handoff is
    `docs/operations/enterprise-mesh-completion-handoff.md`, with machine-readable closure evidence
    in `generated/enterprise-mesh-closure-ledger.json` and published human status in
    `wiki/Enterprise-Mesh-Status.md`. Use those artifacts instead of old chat history when
    continuing mesh expansion or briefing a new agent.

For RFC governance:

1. new and reopened implementation-bearing RFCs must include a second-last code review,
   loose-end-tightening, API certification, and platform-governance slice,
2. they must also include a final documentation, agent context, wiki, skills/guidance assessment,
   and branch-hygiene slice,
3. final closure must prove that durable RFC/docs/wiki/context/contract truth is present on
   `main`; truth that exists only on an unmerged side branch is not complete,
4. before RFC tightening, implementation start, post-merge audit, final closure, or
   supported-feature promotion, agents must run stranded-truth reconciliation:
   `git fetch origin --prune` and `git branch -r --no-merged origin/main`,
5. any unmerged branch touching `docs/rfcs/`, `wiki/`, `README.md`,
   `REPOSITORY-ENGINEERING-CONTEXT.md`, `AGENTS.md`, `contracts/`, `platform-contracts/`,
   `context/`, `docs/standards/`, `.github/workflows/`, migrations, OpenAPI snapshots, API
   vocabulary inventories, or supported-features material must be classified as `must-merge`,
   `cherry-pick`, `superseded`, `delete`, or `active`,
6. restored durable truth must be indexed from a stable navigation page and pinned by an existing
   docs/current-state test pack when one exists,
7. legacy RFCs are not rewritten only for formatting, but must be upgraded when reopened.

For RFC-0093/RFC-0094 agent engineering governance:

1. use `context/playbooks/AGENT-CONTEXT-AND-TASK-LEDGER.md` when resuming long-running work,
   delegating bounded subtasks, monitoring detached checks, or recovering after context compaction,
2. preserve operational identifiers exactly in handoffs and summaries: repository, branch, PR
   number, commit SHA, check name, RFC id, file path, endpoint, contract name, portfolio id, and
   task status,
3. use `platform-contracts/agent-engineering/engineering-task-ledger-contract.v1.json` as the
   contract for detached engineering task identity, lifecycle, cleanup, evidence, delegation, and
   context-preservation fields,
4. treat `output/background-runs.json` as local automation evidence for background runs and GitHub
   Actions as the source of truth for GitHub check status,
5. use `automation/Start-Background-Run.ps1 -Repository ... -TargetType ... -Target ...` for a
   validated repository-native detached target that does not belong in the shared profile catalog;
   preserve argv serialization and add exact-HEAD, clean-tree, and required-artifact fences for
   certifying runs instead of passing a shell command string; process ownership is PID plus a
   culture-independent normalized start timestamp, so JSON-deserialized timestamp types must never
   be formatted and reparsed through the host locale,
6. use `automation/Run-Heartbeat.ps1` when a governed advisory attention snapshot is needed across
   background-run, mesh, context, workflow-pack, wiki, or PR-monitor evidence,
7. treat heartbeat output under `output/heartbeat/` as derived advisory evidence only; it does not
   replace GitHub, local background-run ledgers, mesh certification, wiki source, context
   validators, or `lotus-ai` runtime APIs as source truth,
8. use `platform-contracts/agent-engineering/delegation-policy-contract.v1.json` for governed
   RFC-0096 delegation profiles, input envelopes, output envelopes, write-scope rules, and
   heartbeat attention identifiers,
9. keep delegated implementation work accountable to the main agent: returned patches are evidence,
   not review, and require main-agent diff review plus focused tests before integration,
10. do not delegate immediate critical-path blockers, broad repo cleanup, overlapping write scopes,
   PR merge, or wiki publication without explicit main-agent ownership and review,
11. promote durable lessons into governed docs, context, wiki source, skills, validators, or RFC
   follow-ups instead of relying on chat history.

## Front-Office Runtime Governance

For local front-office product bring-up, demo readiness, UI screenshots, and populated panel validation:

1. use `docs/standards/Lotus Client Demo Certification Standard.md` as the platform-owned human
   standard for client-demo claim states, evidence requirements, demo pack structure, and
   implementation-backed talk tracks,
2. use `docs/demo/client-demo-operating-process.md` as the platform-owned operating process for
   client intake, claim classification, certification evidence, demo-pack structure, rehearsal,
   delivery, and follow-up,
3. use `docs/demo/client-demo-pack-template.md` when turning certification evidence into a
   client-understandable pack with a one-page brief, business story, demo sequence, claim table,
   boundary register, evidence map, rehearsal plan, and follow-up register,
4. prefer the `lotus-front-office-runtime` skill when choosing agent routing for these tasks,
5. use the governed canonical runtime in `lotus-workbench/docs/operations/canonical-front-office-local-runtime.md`,
6. use `lotus-workbench` live commands such as `npm run live:stack:up`, `npm run live:validate`, and `npm run live:stack:down`,
7. treat `PB_SG_GLOBAL_BAL_001` as the governed seeded reference portfolio unless a task explicitly requires another portfolio,
8. treat `lotus-platform/context/contracts/canonical-front-office-demo-data-contract.json` and `lotus-platform/context/contracts/canonical-front-office-demo-data-invariants.json` as the source of truth for canonical front-office dataset governance, including the distinct advisor-book portfolio-manager assignment consumed by Core seed automation and Workbench proof,
9. treat `lotus-platform/context/contracts/workbench-panel-registry.json` as the source of truth for governed Workbench panel identifiers, owners, support states, and screenshot ownership,
10. use `lotus-platform/automation/Invoke-Canonical-FrontOffice-QA.ps1 -ScreenshotDirectory <path>` when a platform-owned run summary, runtime transcript, and caller-directed demo screenshot pack are required,
    and use `-BringUp -RequireMainlineSources` for RFC closure, supported-feature promotion, or
    other mainline-certified front-office proof. This mode delegates Workbench's fail-closed
    exact-`origin/main` source preflight for every canonical participant and records
    `require_mainline_sources` in the platform wrapper summary,
11. treat `lotus-idea` as part of the default canonical QA runtime; do not reintroduce an opt-in flag
    or skip its readiness/teardown evidence unless the task explicitly asks for a diagnostic partial
    run,
12. treat `lotus-platform/platform-stack` as shared ingress and infrastructure support, not as the canonical front-office product bring-up path.
13. scope canonical Docker cleanup by the exact Compose project identities and repository working
    directories owned by the invocation. Emit `cleanup-plan-latest.json` before mutation, use
    `-CleanPlanOnly` for read-only review, and never infer ownership from broad Lotus-shaped names.
    Concurrent certification projects are independent runtime owners even when they use the same
    repository checkout. Reused Compose project names with a different working directory are
    ownership conflicts that must block cleanup before mutation; path containment is insufficient,
    so nested Git worktrees are conflicts too. A residual Compose volume or image
    without live container evidence for the expected checkout is equally ambiguous and must fail
    closed rather than being selected from its project label alone. The ownership inventory must
    model repository-declared project identities explicitly: `lotus-core`,
    `lotus-core-app-local`, and `lotus-core-canonical-ui` all resolve to the canonical
    `lotus-core` checkout boundary, but an alias from a temporary or other checkout is a conflict,
    not an owned resource.
14. classify composite Workbench panels from the complete governed panel contract, not from one
    ready input. Endpoint, calculation, membership, and source-snapshot readiness are component
    evidence; panel promotion requires every registry-owned dependency and limitation to support
    the target state.

Do not improvise a parallel front-office stack sequence from `lotus-platform/platform-stack` when the governed `lotus-workbench` runtime already covers the required UI surfaces and seeded-data validation flow.

Demo-ready screenshots must be captured only after canonical API, calculation, and panel validation passes. Pre-validation captures are diagnostic artifacts and must not be presented as demo-ready evidence.
Machine-readable runtime evidence should preserve canonical contract identity and version, not just portfolio and route parameters.

When live canonical proof follows code, route, BFF, panel, Dockerfile, or seed-data changes, rebuild
or targeted-refresh the impacted service images before accepting evidence. Stale containers can
produce false route 404s, missing panel fields, and empty business surfaces even after merged code
exists. Treat those symptoms as diagnostic failures until the changed services are refreshed and
validation is rerun. If a panel proves a newly implemented business capability, create or seed a real
implementation-backed entity first and record that evidence path; an empty panel is not product
proof for a populated business workflow.
This runtime and dataset posture is governed by `RFC-0076` and the governed panel-surface posture by `RFC-0077`.

## Engineering Standards

Lotus engineering is expected to be:

1. clean,
2. modular,
3. readable,
4. domain-correct,
5. reliable,
6. scalable,
7. observable,
8. production-ready.

The standing enterprise quality bar is
`platform-standards/LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md`. Agents should use it as the
default non-degradation standard for Lotus app work, not only when a user explicitly says
"refactor" or "enterprise-grade". For a bank-readiness assessment, route through
`lotus-app-issue-discovery`, read the implementation playbook, and select only the applicable
`BR-NNN` slice from `platform-contracts/bank-readiness/bank-ready-control-catalog.v1.json`. Context
and skills route to that authority; they do not duplicate its control definitions. The enterprise
backend refactoring instructions remain the measurement-heavy execution path for large refactors.

### Required delivery posture

Always:

1. look for opportunities to reduce complexity,
2. make the codebase cleaner, more readable, more maintainable, and more modular,
3. make code and test improvements that materially improve reliability and maintainability,
4. add or update documentation wherever necessary,
5. leave the codebase cleaner than you found it,
6. write meaningful, high-value tests and avoid superficial coverage,
7. keep making small, meaningful commits,
8. remove dead code, duplication, and non-standard legacy handling when encountered,
9. ensure every UI feature is genuinely backed by supported backend functionality.

### Clean code principles

1. prefer explicit, well-scoped responsibilities over convenience coupling,
2. avoid duplicated policy or logic across repositories and layers,
3. prefer shared reusable patterns over page-local or file-local hacks,
4. make naming precise, domain-correct, and stable,
5. remove stale abstractions when the product direction changes,
6. keep public contracts intentional and documented.

### Modular design principles

1. separate platform truth from repository-local truth,
2. separate domain authority from composition and presentation,
3. prefer well-defined modules and validators over ad hoc scripts,
4. treat automation and runbooks as product-quality operational code,
5. push repeatable patterns into standards, templates, skills, or validators once they recur.

## Testing Standards And Validation Model

Lotus follows the test pyramid and meaningful coverage posture defined by platform standards.

Expected validation layers include:

1. fast unit tests for local logic,
2. contract and integration tests for domain boundaries,
3. browser or end-to-end validation where product experience matters,
4. platform validation for canonical stack bring-up, ingress, seeded data, and cross-app flows,
5. CI lane validation with fast feature gates, PR merge gates, main releasability gates, and platform end-to-end validation where applicable.

### Test quality rules

1. test business and contract behavior, not just implementation trivia,
2. add regression tests for every real defect you fix,
3. prefer deterministic, minimal, high-signal tests,
4. remove stale assertions that no longer reflect the product contract,
5. keep repo-native commands truthful to the actual CI contract,
6. treat total test count as context, not proof by itself,
7. preserve measured API/runtime, contract/governance, observability/security, and
   domain-methodology test-family breadth when those inventories exist.

## Documentation Quality Standards

Documentation in Lotus is part of the delivery artifact.

Update docs when:

1. architecture changes,
2. commands change,
3. runtime or validation flow changes,
4. standards or CI rules change,
5. a repeatable pattern is worth codifying,
6. a repository’s current-state reality materially changes.

Central docs own platform truth.

Repository-local docs own repo truth.

When a repository uses a GitHub wiki, the repo-local `wiki/` directory should be treated as the
canonical authored source and the `*.wiki.git` repository should be treated as publication
transport only. PR validation now runs
`automation/Sync-RepoWikis.ps1 -CheckOnly -Repository lotus-platform -AllowUnpublishedSourceChanges`
for platform wiki source changes before merge, and agents should run the same branch-source check
with the target repository name before merging wiki-affecting changes. After merge, publish with
`automation/Sync-RepoWikis.ps1 -Publish -Repository <repo-name>`, then run strict parity
verification without `-AllowUnpublishedSourceChanges`; use `-AllRepositories` for coordinated
platform-wide audits or publication sweeps.

Do not duplicate central policy prose into every repo unless repo-local interpretation is required.

## API Quality And UI Alignment

Lotus APIs and product surfaces are expected to be:

1. clear,
2. consistent,
3. domain-correct,
4. fully modeled,
5. documented,
6. aligned with authoritative ownership boundaries.

### API and UI rules

1. use business-language contracts rather than generic field naming,
2. keep gateway contracts governed and explicit,
3. do not ship UI flows that are not supported by backend capability,
4. do not mask backend gaps with decorative UI or fabricated content,
5. keep empty, partial, loading, ready, and error states explicit for data modules.
6. for readiness, supportability, version, certification, and certified business/operator APIs,
   compare documented success examples with code-owned runtime serialization; valid JSON syntax is
   insufficient evidence. Use only explicit field-level normalizers for genuinely dynamic values,
   and compare blocker, supportability, promotion, schema, contract, and version fields exactly.
7. for multi-shape successful endpoint families, use the named-success family closure workflow in
   `codex/skills/lotus-endpoint-certification-loop/references/named-success-family-closure.md`.
   Require issue-first scope, deterministic pre/post inventory, production request/application/DTO
   execution, separate caller/source contracts, non-candidate no-write proof, exact OpenAPI/ledger
   parity, and exact-main closure evidence.

## Performance, Reliability, And Production Readiness

Lotus delivery should optimize for:

1. front-office trust,
2. operational clarity,
3. performance and low latency,
4. strong reliability,
5. maintainable observability,
6. stable production posture.

This means:

1. avoid unnecessary runtime cost and repeated work,
2. treat latency and performance regressions as product quality issues,
3. keep Docker, ingress, runtime, and validation paths repeatable,
4. provide evidence for readiness through CI artifacts, validation summaries, and truthful checks.
5. keep CI/runtime service membership in canonical service-set registries when a repository has
   one, and make scripts/tests consume those registries rather than copying command lists. Runtime
   gates that need bootstrap services such as migrations, topic creation, seed loaders, or
   control-plane one-shot containers should add them once to the shared set and let latency, E2E,
   performance, failure-recovery, and institutional validation inherit the same truth.

## Naming And Vocabulary Standards

Naming should reflect banking and investment domain reality.

Preferred vocabulary should come from:

1. private banking,
2. portfolio management,
3. performance analytics,
4. risk analytics,
5. advisory workflows,
6. reporting and investment-review language.

### Naming rules

1. file names should describe stable responsibility,
2. functions and objects should use domain-correct verbs and nouns,
3. APIs should prefer explicit business meaning over generic placeholders,
4. avoid generic labels such as `widget`, `thing`, `item`, or `stats` when a domain term exists,
5. use domain-correct terms such as `portfolio`, `benchmark`, `mandate`, `allocation`, `attribution`, `drawdown`, `exposure`, `supportability`, `readiness`, `booking`, `holding`, `proposal`, and `evidence` where appropriate.

## Agent Operating Expectations

Agents working in Lotus are expected to operate like disciplined banking-grade engineers.

### Mandatory posture

1. choose the smallest correct working set of context,
2. use standards, skills, validators, and runbooks before improvising a new local pattern,
3. prefer async GitHub-backed heavy execution when it is more efficient than repeated heavyweight local reruns,
4. promote repeatable patterns into durable guidance,
5. keep repo and platform context current when reality changes,
6. reject backend or frontend changes that pass tests but degrade measured quality through
   copy-paste, architecture-boundary drift, security suppressions, weak tests, unsupported UI,
   unsupported documentation claims, or missing runtime/browser proof.
7. re-read the active goal and focused issue at material checkpoints: before editing, after handover
   or context compaction, before PR/merge, and before selecting the next slice or endpoint family.
8. keep progress, decisions, residual blockers, and operational identifiers durable in GitHub
   issues, repository context, RFCs, ledgers, or governed task artifacts rather than relying on
   conversational memory.

### Skills and working methods

Use the right skill or workflow for the task:

1. `lotus-front-office-runtime` for canonical populated Workbench runtime, demo screenshots, and panel-proof tasks,
2. backend delivery governance for backend repos,
3. frontend delivery governance for UI work,
4. PR pre-merge governance for merge preparation,
5. QA or platform validator skills for stack and platform validation,
6. RFC or documentation skills for governance work,
7. `lotus-ci-enforcement-governance` for CI gate design, report-only inventory promotion,
   scorecard-backed regression blockers, and agent-driven development guardrails.

For CI-enforcement work, agents should first prove that the signal is measured, deterministic,
actionable, and low-noise. Prefer gates that fail early through repo-native commands and block real
degradation such as architecture-boundary erosion, insecure first-party patterns, duplicate
implementation hotspots, OpenAPI/vocabulary drift, or contract-validation failures. Keep noisy or
policy-immature metrics report-only until false positives, exceptions, and lane placement are
settled. Blocking gates must leave a clean worktree; durable report artifacts belong behind
explicit report-only commands such as `make architecture-boundary-report` or `make quality-baseline`.
When a repeatable enforcement pattern is learned, update platform-owned skills, routing context, and
local agent artifacts through the bootstrap/validation automation rather than hand-editing local
skill copies as the source of truth.
For agentic coding quality, use
`context/playbooks/AGENTIC-CODING-QUALITY-EVALUATION-LOOP.md`: deterministic repository gates are
the merge authority, while AI or LLM-based evaluators remain advisory until their datasets, graders,
false-positive posture, and exception policy are stable.

For RFC-driven business-application implementation, work from current `main` and close one
proof-backed slice before opening the next. Each slice should name the blocker codes it clears, the
blocker codes it intentionally preserves, the code/API/contract/test/docs evidence, and the merge
method used. Internal domain, application, port, adapter, and proof-module boundaries are the
default modularity target; propose a new deployable microservice only when independent runtime
scaling, deployment, ownership, data, failure-isolation, or security-boundary needs are proven.
If a repository disallows merge commits, use the repository-approved non-squash linear merge path
such as rebase merge and stop retrying merge commits after that policy is known.
Before pushing merge intent for long-running refactors, run
`python automation/validate_branch_commit_budget.py --repo-root . --base-ref origin/main --head-ref HEAD`
or the shared preflight wrapper so branches warn at 40 commits, require a tranche decision at
60 commits, and block above the governed rebase-safe limit by default.
For dependent multi-PR refactor campaigns, maintain a versioned `stacked-refactor-campaign`
manifest under the agent-engineering contract family so tranche ids, predecessor main SHAs, local
and remote evidence, issue closure posture, and final aggregate closure are not reconstructed from
chat memory or branch history.
If a repository requires signed commits, configure a registered signing key before the first PR
commit and verify every branch commit is signed before pushing merge intent. A green PR with
`mergeable=true` can still remain blocked when linear history plus signed-commit protection meets an
unsigned branch. In that case, re-sign the branch commits and push with `--force-with-lease`; do not
admin-bypass or weaken signed-commit protection.
For proof-driven RFC slices, record a compact slice closure manifest before moving on: blockers
cleared, blockers preserved, proof artifacts, commands, docs/wiki/supported-feature decisions,
merge method, post-merge validation, and branch cleanup evidence. Before deleting branches, verify
merged or superseded status with PR state plus `git log`, `git diff`, or cherry-pick evidence so
no implementation code or durable truth is lost during hygiene.

For blocker-clearing proof, classify evidence before promoting the claim. The canonical persisted
evidence-class vocabulary is governed by
`platform-contracts/evidence-classification/evidence-class-vocabulary.v1.json` and currently uses
`source_contract`, `test_execution`, `ci_execution`, `runtime_execution`, `deployment`, and
`production_certification`. `source_design_contract` and `local_test_execution` are closed legacy mappings
for stable bank-readiness catalog semantics and historical audit comments, not arbitrary aliases
for new proof artifacts. Every blocker should declare the minimum evidence
class it needs, every proof should declare the evidence class it actually supplies, and lower-class
proof such as source files or static contracts must not clear runtime, deployment, or production
certification blockers by implication. CI evidence must bind repository, workflow, job, run id, run
attempt, exact commit SHA, ref, successful conclusion, and relevant artifact digest when it clears
a blocker.

For repository organization, use capability-oriented packages inside the existing runtime layers.
Name executable source, scripts, workflows, contracts, migrations, and tests for enduring business
capabilities or engineering invariants, not RFC/slice/issue/PR identifiers; reserve those names for
actual governance and tracking artifacts. Pilot one cohesive package, migrate imports atomically,
mirror focused tests, prohibit obsolete flat paths, and verify package/runtime import truth before
expanding the pattern. Do not retain indefinite compatibility aliases or infer repository roots from
fragile fixed parent depth in moved tests. When refactoring source-backed proof, update validators
to stable symbols/interfaces or behavior and retain tamper, overclaim, and missing-source tests.
These are design-modularity controls; directory size alone never justifies a runtime service split.

For newly scaffolded backend services, CI contract gates should also protect release-evidence
semantics: rebase auto-merge must use a non-`GITHUB_TOKEN` merge actor such as
`LOTUS_AUTOMERGE_TOKEN`, and merged PRs must dispatch or otherwise prove Main Releasability on the
merged `main` commit. When that token is absent, the generated helper should warn and skip
auto-merge so an authorized human or release actor can perform the rebase merge without leaving a
permanent red helper check. Generated backend workflows must also declare bounded job-level
`timeout-minutes` values and must not soft-fail critical lanes with `continue-on-error: true`.
Release evidence and deployment promotion proof are separate contracts. Service repositories own
Dockerfile hygiene, SBOM, vulnerability scan, signing, provenance attestation, and digest-bearing
`release-evidence.json`; `lotus-platform` owns the digest-based deployment promotion manifest under
`platform-contracts/deployment-promotion/`. The platform validator
`python automation/validate_deployment_promotion_manifest.py` rejects mutable tags, missing digest
refs, release/deployed digest mismatches, rebuild-per-environment promotion, and production
certification claims before live deployment proof exists.
Application libraries and container images also require governed vulnerability posture. The default
technology choice is mature, widely deployed, well-documented, actively maintained, and supported by
broad training, scanner, and operational tooling. Beta, preview, experimental, incubating,
unsupported, or novelty-driven major upgrades are excluded from runtime and release-image posture by
default. Exceptions must be issue-backed, time-bounded, owner-assigned, and carry vulnerability,
supportability, compensating-control, rollback, and expiry evidence before a PR, release, README,
wiki, RFC, or supported-feature claim can describe the result as production-ready or bank-buyable.
`platform-contracts/vulnerability-exceptions/` defines the machine-readable exception register and
`python automation/validate_vulnerability_exception_register.py --report-only` validates schema and
semantic findings while repositories establish baselines, false-positive handling, and lane
placement. Omit `--report-only` only for focused blocking proof after promotion criteria are met.
Newly scaffolded backend services also generate `make maintainability-gate`,
`make documentation-contract-gate`, `make quality-scorecard-gate`,
`make monetary-float-guard`, `make source-observability-contract-gate`,
`make operation-metric-contract-gate`, and `make implementation-truth-gate`
through `automation/New-Lotus-Service.ps1` and run all seven through
`make lint`; they block oversized source/test/script modules, deletion or
thinning of required README/context/standards/runbook/quality/evidence/wiki
surfaces, stale bank-buyable scorecard control-matrix truth, money-like
`float` annotations/literals/return annotations/conversions, raw application
logging bypasses outside the central observability module, sensitive or unbounded
operation metric names/labels/attributes, plus unqualified
README/docs/wiki current-state claims of demo
readiness, production support, certification, live source ingestion,
Gateway/Workbench support, or client-ready publication before supported-feature
evidence exists. The generated source-observability gate blocks raw `print()`,
direct Python logging, and low-level `log_event` bypasses in `src/app`, while
generated request diagnostics log route templates instead of raw URL paths.
The generated implementation-truth gate also blocks stale
scaffold-era demo underclaims once implementation and CI evidence prove a
stronger current posture.
Generated backend architecture gates should also protect `src/app/runtime` as
the process-local composition layer: it may wire repositories, adapters,
publishers, workers, and proof generators, but it must not import API routes,
HTTP DTOs, FastAPI, or Starlette.
Backend architecture gates should also protect service package import truth. Code inside a
deployable service app package must not self-import through repo-root module paths that are absent
from wheel, Docker, or compose runtime layouts; use relative imports for same-service code, shared
contracts or ports for durable cross-service dependencies, and a focused `import app.main` runtime
proof when service packaging or app imports change. Write the proof command in the active shell's
syntax:

- POSIX: `PYTHONPATH="src/services/<service>:src/libs/portfolio-common" python -c "import app.main"`
- PowerShell: `$env:PYTHONPATH = "src/services/<service>;src/libs/portfolio-common"; python -c "import app.main"`

Generated backend Makefiles also expose `UNIT_TESTS`, `INTEGRATION_TESTS`, and
`E2E_TESTS` path overrides so focused fix-forward validation remains
repo-native instead of becoming ad hoc pytest invocation; the generated CI
contract gate protects those variables and target commands. Generated GitHub
workflow templates must consume the same Makefile surface: Feature Lane calls
`make test-unit`, PR/Main suite matrices call `make test-${{ matrix.suite }}-coverage`,
and the generated CI contract gate rejects raw workflow-level `pytest` shortcuts
or coverage paths that bypass repo-native targets.
Generated backend services also include a tested `scripts/clean_generated_artifacts.py` utility and
`make clean` wiring. The generated CI contract gate must protect that wiring so cleanup remains a
safe local hygiene command that prunes `.git`, `.venv`, and `node_modules` and removes only known
cache, build, and coverage artifacts.
Generated endpoint-certification gates require certified business/operator
endpoints to cite bounded operation-event test evidence so API contract
certification and supportability telemetry proof cannot drift apart.
Generated backend services also bind every `baseline_certified` or `certified` success example to
a source-safe route invocation or deterministic code-owned callable. The exact structural
comparator fails missing/stale fields, aliases, types, blockers, and values; dynamic values require
approved RFC 6901 pointer normalizers, and governance fields cannot be normalized.
Do not treat a green PR Merge Gate as release evidence by itself.

For enterprise backend refactors in `lotus-platform`, start from
`automation/generate_enterprise_backend_quality_baseline.py --write --check` and the measured
artifacts under `quality/`. Treat `quality/baseline_report.md`,
`quality/quality_scorecard.md`, and `quality/refactor_health_report.md` as the durable before/after
evidence trail. When a slice changes repo organization, gate posture, commands, documentation truth,
or agent workflow, update README, wiki source, `REPOSITORY-ENGINEERING-CONTEXT.md`, central context,
and the relevant platform-owned skill source in the same slice.

When a repeatable pattern emerges:

1. update the relevant context document,
2. update an existing skill,
3. add a new skill if the pattern is durable and recurring,
4. add a validator or scaffold rule if executable enforcement is valuable.

## Human-Maintained Memory

The central curated memory layer is:

1. [Platform Engineering Ledger](./platform-engineering-ledger.md)
2. [Recent Architectural Decisions Digest](./recent-architectural-decisions-digest.md)

These files exist to preserve high-value practical guidance and recent platform reality across sessions.

## Structured Reusable Context

The machine-readable ecosystem map is:

1. [lotus-context-manifest.json](./lotus-context-manifest.json)

Use the manifest for:

1. ecosystem inventory,
2. repo roles,
3. canonical commands,
4. dependency and authority lookups,
5. context-path discovery.

## Procedural Memory

The governed procedural-memory layer lives in:

1. [Procedural Memory Index](./PROCEDURAL-MEMORY-INDEX.md)

Use it when you need durable guidance for:

1. change execution,
2. PR loops and async monitoring,
3. validation depth selection,
4. fix-forward response patterns.

## Related References

Use the [Context Reference Map](./CONTEXT-REFERENCE-MAP.md) to find:

1. active standards,
2. active RFCs,
3. runbooks,
4. domain references,
5. repository-local context documents.

## Task Routing Guidance

Use the [Task Routing Guide](./TASK-ROUTING-GUIDE.md) when you want the smallest correct reading path for:

1. frontend and product-surface work,
2. backend API and domain-service work,
3. cross-app integration and platform validation work,
4. standards, RFC, and governance work.

Use the [Lotus Skill Routing Map](./LOTUS-SKILL-ROUTING-MAP.md) when you need the smallest correct
skill boundary for:

1. canonical front-office runtime work,
2. platform QA vs product-surface proof,
3. delivery governance vs PR governance,
4. async GitHub-heavy execution posture.

Use [Ecosystem Registries](./ECOSYSTEM-REGISTRIES.md) when you need a human-readable view of:

1. application roles and categories,
2. domain authority ownership,
3. standards currently in force,
4. active RFCs that still materially govern the ecosystem.

