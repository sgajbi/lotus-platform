# RFC-0082: Lotus Core Domain Authority and Analytics-Serving Boundary Hardening

- Status: Draft
- Date: 2026-04-14
- Owners:
  - lotus-platform architecture
  - lotus-core maintainers
- Requires Approval From:
  - lotus-platform maintainers
  - lotus-core maintainers
  - lotus-performance maintainers
  - lotus-risk maintainers
  - lotus-gateway maintainers
  - lotus-advise maintainers
  - lotus-manage maintainers
- Related:
  - `RFC-0041-platform-integration-architecture-bible-governance.md`
  - `RFC-0050-core-data-analytics-and-reporting-service-boundaries.md`
  - `RFC-0065-lotus-performance-to-lotus-performance-and-lotus-risk-split.md`
  - `RFC-0067-centralized-api-vocabulary-inventory-and-openapi-documentation-governance.md`
  - `RFC-0071-centralized-environment-scoped-service-addressing-and-ingress-governance.md`
  - `RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`
  - `C:/Users/Sandeep/projects/lotus-core/docs/RFCs/RFC 035 - Lotus Core Responsibility and Integration Contract (lotus-performance and lotus-manage).md`
  - `C:/Users/Sandeep/projects/lotus-core/docs/RFCs/RFC 049 - Lotus Core Snapshot Analytics De-Ownership and lotus-performance Input Contract.md`
  - `C:/Users/Sandeep/projects/lotus-core/docs/RFCs/RFC 063 - Stateful Analytics Input Contracts for lotus-performance APIs.md`
  - `C:/Users/Sandeep/projects/lotus-core/docs/RFCs/RFC 081 - Lotus Core Microservice Boundary Optimization and Event-Orchestration Hardening.md`

## Summary

Lotus needs one platform-owned architectural rule for what `lotus-core` is, what it is not, and how downstream analytics services are allowed to consume it.

Today, the system is directionally strong:

1. `lotus-core` is already the source of truth for portfolio, booking, transaction, valuation, cashflow, and foundational reference data.
2. `lotus-performance` and `lotus-risk` are already the intended authorities for analytics.
3. implemented contracts in `lotus-core` already support stateful downstream consumption through governed integration endpoints.
4. `lotus-core` RFCs 049 and 063 already moved the estate away from analytics-in-snapshot coupling and toward explicit analytics input contracts.

However, the platform still lacks one consolidated, enforceable cross-repository rule set for:

1. domain authority,
2. analytics-serving boundary design,
3. allowed contract families,
4. prohibited ownership overlap,
5. downstream consumption rules,
6. when to use synchronous reads, paged retrieval, export jobs, or future transport optimizations,
7. what architectural debt must be removed before the estate is treated as production-grade.

This RFC closes that gap.

It does not propose a `v2` platform or a greenfield rewrite.

It governs how the current `lotus-core`, `lotus-performance`, and `lotus-risk` repositories should be hardened while the estate is still pre-live, so the current apps become the correct architecture rather than carrying known boundary mistakes into first production release.

## Problem

Lotus has already made important boundary improvements, but the current architecture is still easier to understand repo-by-repo than platform-by-platform.

That leaves four practical risks.

### 1. `lotus-core` still looks broader than its intended ownership

`lotus-core` correctly owns canonical portfolio and transaction truth, but its runtime and documentation still present a wide downstream-facing surface that can be interpreted as:

1. source-of-truth state authority,
2. general-purpose query backend,
3. analytics input provider,
4. integration policy provider,
5. support/control-plane provider.

Some of that is correct. Some of it is necessary. Some of it should be more sharply bounded.

Without one platform rule set, downstream teams can still make the wrong architectural assumption:

- "if `lotus-core` can answer it, `lotus-core` probably owns it."

That assumption is false for analytics behavior.

### 2. Downstream analytics services still depend on multiple contract families with distributed governance

`lotus-performance` already consumes:

1. analytics timeseries contracts,
2. benchmark assignment and benchmark reference contracts,
3. policy and capability context,
4. portfolio reference metadata,
5. large-window retrieval behavior through chunking, paging, and export semantics.

That is workable, but the architectural rules for when to use each contract family are still spread across multiple repo RFCs.

### 3. The estate still lacks one explicit rule for what not to add

Pre-live estates are vulnerable to accidental complexity because teams still feel free to add:

1. overlapping contracts,
2. dual ownership of business semantics,
3. convenience endpoints that quietly become permanent,
4. transport variation without clear governance,
5. new control-plane behavior inside wrong-layer services.

This RFC exists partly to prohibit those moves.

### 4. Transport and performance conversations can distract from the real design work

Internal service-to-service performance matters, but the current `lotus-core -> lotus-performance` shape is dominated by:

1. data product design,
2. paging and chunking behavior,
3. retrieval orchestration,
4. lineage and determinism,
5. ownership separation.

Without a stronger platform boundary rule, teams can end up debating REST versus gRPC before they have stabilized the contract shape that either transport would carry.

## Decision

Lotus adopts the following platform-wide architectural position.

### 1. `lotus-core` remains the canonical authority for operational portfolio state and foundational reference state

`lotus-core` owns:

1. portfolios,
2. accounts and bookings,
3. transactions,
4. ingestion and persistence lifecycle,
5. positions,
6. valuations,
7. canonical cashflows,
8. timeseries foundations,
9. benchmark assignment and benchmark source data,
10. reference-series primitives required by downstream analytics.

### 2. `lotus-core` does not own advanced performance or risk analytics

`lotus-core` must not own:

1. performance calculations as product analytics,
2. risk calculations as product analytics,
3. attribution logic as downstream business behavior,
4. product-facing interpretation of analytics outputs,
5. cross-analytic narrative or workflow semantics that belong in `lotus-performance`, `lotus-risk`, or `lotus-gateway`.

### 3. `lotus-core` is allowed to serve analytics inputs, but only as governed data products

When `lotus-core` serves downstream analytics consumers, it must do so through explicit contract families that expose:

1. canonical input data,
2. lineage,
3. request scope,
4. freshness and completeness semantics where relevant,
5. deterministic paging or export semantics where relevant,
6. consumer context and policy provenance where relevant.

It must not expose downstream analytics behavior disguised as a core data contract.

### 4. The current estate is the production target

Lotus will not create `lotus-core-v2` or parallel replacement repos for this problem space while the system is still pre-live.

The required architectural correction work will be applied to the current repositories through governed slices.

## Why This Is The Right Choice Now

The estate is not live yet.

That changes the economic and engineering posture:

1. backward compatibility pressure is lower,
2. migration cost is lower,
3. repository and service boundaries can still be corrected without production cutover programs,
4. the risk of preserving known wrong boundaries is higher than the risk of correcting them now.

The right move is therefore:

1. no greenfield replacement,
2. no dual architecture,
3. no speculative protocol expansion,
4. yes to boundary hardening in the current repos,
5. yes to removing design debt before first production launch.

## Architectural Principles

The following principles become mandatory for `lotus-core`, `lotus-performance`, `lotus-risk`, and downstream consumers.

### 1. Domain authority is not the same as query convenience

`lotus-core` being able to provide data does not mean it owns downstream behavior derived from that data.

### 2. Analytics inputs are products

Portfolio timeseries, position timeseries, benchmark reference inputs, and reference-series inputs are not incidental helper payloads.

They are governed data products with:

1. explicit consumers,
2. explicit request scope,
3. explicit completeness semantics,
4. explicit provenance,
5. explicit change control.

### 3. Canonical contract families are better than proliferating endpoint shapes

Lotus should prefer a small number of strong contract families over many convenience endpoints with overlapping semantics.

### 4. Downstream analytics ownership must stay downstream

`lotus-performance` and `lotus-risk` own their analytics logic even when their input data is fully sourced from `lotus-core`.

### 5. Determinism beats convenience

For large-window stateful retrieval, deterministic paging, snapshot pinning, request fingerprints, and export lifecycle semantics are more important than making the call pattern look superficially simple.

### 6. Transport is subordinate to contract design

Lotus will optimize contract shape and retrieval behavior before introducing a second primary transport model for the same boundary.

## Current-State Assessment

The current estate already contains several important elements of the target architecture.

### Current implemented evidence

The decision in this RFC is grounded in current implementation reality, not only desired architecture.

Observed current evidence:

1. `lotus-core` already documents itself as the authoritative portfolio, booking, account, and transaction platform and exposes a broad read and integration surface.
2. `lotus-core` query and control-plane routing already includes:
   - operational read endpoints,
   - integration policy endpoints,
   - core snapshot endpoints,
   - benchmark and reference integration endpoints,
   - analytics input contracts.
3. `lotus-performance` already consumes `lotus-core` through a dedicated integration client with stateful portfolio-timeseries, position-timeseries, benchmark, index, FX, and risk-free retrieval methods.
4. `lotus-performance` already centralizes chunking, paging, retry, and upstream lineage capture in its stateful input boundary rather than coupling analytics code directly to `lotus-core` data access.
5. `lotus-risk` repository context already states that it integrates with `lotus-core` and `lotus-performance` for stateful and cross-analytic flows while keeping risk analytics authority local.

Representative evidence paths:

1. `C:/Users/Sandeep/projects/lotus-core/README.md`
2. `C:/Users/Sandeep/projects/lotus-core/src/services/query_control_plane_service/app/routers/analytics_inputs.py`
3. `C:/Users/Sandeep/projects/lotus-core/src/services/query_control_plane_service/app/routers/integration.py`
4. `C:/Users/Sandeep/projects/lotus-performance/app/services/core_integration_service.py`
5. `C:/Users/Sandeep/projects/lotus-performance/app/services/stateful_input_service.py`
6. `C:/Users/Sandeep/projects/lotus-performance/REPOSITORY-ENGINEERING-CONTEXT.md`
7. `C:/Users/Sandeep/projects/lotus-risk/REPOSITORY-ENGINEERING-CONTEXT.md`

### What is already directionally correct

1. `lotus-core` RFC 049 de-owned analytics sections from core snapshot behavior.
2. `lotus-core` RFC 063 established explicit analytics input contracts for `lotus-performance`.
3. `lotus-core` RFC 081 improved microservice and control-plane decomposition.
4. `lotus-performance` consumes `lotus-core` through explicit integration contracts rather than direct database coupling.
5. benchmark and reference input ownership already remains in `lotus-core` while analytics execution remains in downstream services.

### What is still incomplete

1. One platform-owned boundary contract does not yet exist for `lotus-core` downstream serving rules.
2. `lotus-core` still exposes multiple downstream-facing concerns whose target grouping should be clearer.
3. repo-local RFCs describe the current reality well, but the cross-repo operating rule is still fragmented.
4. there is no single "allowed vs forbidden" platform checklist for future additions.

## Target Model

The target model for `lotus-core` is:

1. domain write and state authority,
2. canonical read authority for operational data,
3. governed input-product provider for downstream analytics and reporting,
4. bounded control-plane and integration-policy provider,
5. not a home for downstream product analytics logic.

### Mandatory contract families

The platform recognizes four primary downstream-facing `lotus-core` contract families.
Repository-local inventories may also classify adjacent write-ingress and control-execution routes
when a downstream service depends on those surfaces. Those adjacent families are governed by the
same boundary principle: they may execute or record core-owned truth, but they must not become a
home for downstream analytics or workflow interpretation.

### Contract-family classification table

| Family | Primary consumer examples | `lotus-core` responsibility | Explicitly excluded from `lotus-core` ownership |
| --- | --- | --- | --- |
| Operational reads | `lotus-gateway`, `lotus-advise`, `lotus-manage`, support tooling | canonical state retrieval and foundational business truth | downstream analytics conclusions, narrative interpretation, product-specific derived behavior |
| Snapshot and simulation | `lotus-advise`, `lotus-manage`, `lotus-gateway`, support and simulation consumers | policy-aware state bundles and simulation-oriented governed read products | performance/risk sections, downstream analytics engine outputs |
| Analytics inputs | `lotus-performance`, `lotus-risk`, `lotus-gateway`, `lotus-advise`, reporting consumers | canonical input datasets, reference inputs, paging/export semantics, lineage and scope | performance or risk business logic, attribution narratives, active-risk interpretation |
| Control-plane and policy | support tooling, downstream services, operator automation | policy diagnostics, capabilities, supportability metadata, integration governance | primary business-domain APIs, product workflow behavior |

#### A. Operational read contracts

Purpose:

1. portfolio, position, transaction, market-data, and ledger-style operational reads,
2. authoritative current or governed historical state access,
3. direct product and support consumption where `lotus-core` is genuinely the read authority.

Examples:

1. portfolio detail and transaction query contracts,
2. lookup and reporting-support reads,
3. current-state reference and foundational dataset access.

Rules:

1. these contracts must remain domain-truth oriented,
2. they must not absorb analytics-serving semantics just because downstream consumers exist,
3. they should optimize for operational truth, not analytics convenience.

#### B. Snapshot and simulation contracts

Purpose:

1. governed multi-section snapshots,
2. simulation and what-if state access,
3. policy-aware read products for downstream integration and support tooling.

Rules:

1. snapshots must remain state-oriented,
2. snapshots must not re-grow analytics sections,
3. policy provenance and section governance remain mandatory,
4. snapshot behavior stays governed by explicit consumer and tenant context.

#### C. Analytics input contracts

Purpose:

1. canonical portfolio timeseries for performance engines,
2. canonical position timeseries for contribution and attribution engines,
3. canonical reference metadata for analytics context,
4. benchmark, index, and risk-free source contracts,
5. export lifecycle for large retrievals.

Rules:

1. these contracts exist specifically to serve downstream analytics authorities,
2. they must expose inputs, not analytics conclusions,
3. they must be deterministic, paged or export-safe, and replay-auditable,
4. they must carry enough metadata for downstream correctness without duplicating downstream logic.

#### D. Control-plane and policy contracts

Purpose:

1. capability discovery,
2. effective integration policy,
3. supportability and operator diagnostics,
4. operational control-plane access that should not pollute domain-read surfaces.

Rules:

1. these contracts belong in explicit control-plane ownership,
2. they must remain operational and policy-oriented,
3. they must not become a shadow business API surface.

### Contract design decision matrix

For new or modified `lotus-core` contracts, teams must classify the request using the following decision rules before implementation.

| Question | If yes | If no |
| --- | --- | --- |
| Is the payload canonical portfolio, booking, position, transaction, or foundational reference truth? | operational read or analytics input depending on retrieval shape | continue classification |
| Is the payload a governed multi-section state bundle or simulation state representation? | snapshot and simulation | continue classification |
| Is the payload primarily serving downstream analytics engines with large-window or deterministic retrieval needs? | analytics input | continue classification |
| Is the payload about policy, supportability, capability, operator diagnostics, or consumer-specific governance? | control-plane and policy | continue classification |
| Does the endpoint return a conclusion that belongs to performance or risk analytics business logic? | reject from `lotus-core`; route to downstream analytics authority | endpoint may still belong in `lotus-core` if another family applies |

If a proposal matches more than one family, the burden is on the proposer to justify why the surface should not be decomposed.

Default rule:

1. mixed-purpose contracts should be split unless a documented operator or correctness reason requires a unified response,
2. convenience alone is not sufficient justification.

## Mandatory Design Changes For `lotus-core`

This RFC does not claim every change is missing today. Some are partially present. The purpose here is to define what must be true when the architecture is considered complete.

### 1. Make internal ownership boundaries more explicit

`lotus-core` must present three distinct internal concerns, even if they remain in one repository:

1. write-side domain authority,
2. operational read authority,
3. downstream-serving integration/control-plane surfaces.

The repo may keep shared libraries and shared governance, but these concerns must be visible in:

1. service naming,
2. runtime boundaries,
3. routing structure,
4. tests,
5. documentation,
6. ownership and change review.

### 2. Treat analytics-serving as a named boundary, not an accidental extension of query-service

The platform target is not "query-service plus some analytics routes."

The target is:

1. operational reads are one concern,
2. analytics input products are another concern,
3. control-plane behavior is another concern.

This distinction is already partly present and must be completed consistently.

### 3. Shrink overlap between generic reads and downstream-serving products

When the same business concept is served through multiple endpoint styles, one of them usually becomes ambiguous over time.

Lotus must reduce that ambiguity by making the preferred contract family explicit and by retiring overlapping or misleading alternatives.

### 4. Standardize large-window retrieval on paged or export-first rules

For performance and risk downstream consumers:

1. small deterministic retrievals may remain synchronous,
2. medium and large retrievals must use explicit paging or export lifecycles,
3. no new "single giant response" contract should be added for convenience.

### 5. Keep enrichment and interpretation separate from bulk retrieval unless proven necessary

Bulk analytics input payloads must remain focused on canonical inputs.

Enrichment can be exposed through dedicated contracts when:

1. reuse justifies it,
2. duplication would be material,
3. ownership remains clear.

### 6. Make provenance unavoidable

Every downstream-serving contract family must continue to converge on:

1. request scope fingerprints,
2. consumer context,
3. policy provenance where applicable,
4. snapshot or page identity where applicable,
5. completeness or diagnostic metadata where applicable.

### 7. Keep benchmark and reference ownership in `lotus-core`, but not benchmark analytics ownership

`lotus-core` should continue to own:

1. benchmark assignment,
2. benchmark definitions,
3. composition windows,
4. raw benchmark and index series,
5. risk-free reference series.

It must not grow into:

1. benchmark performance product authority,
2. attribution semantics authority,
3. active risk narrative authority.

### 8. Rationalize service decomposition only when it earns its cost

The platform does not require more microservices for their own sake.

A boundary should exist only when it improves at least one of:

1. ownership clarity,
2. scaling isolation,
3. failure isolation,
4. security posture,
5. operator clarity.

This rule applies to future attempts to split query or analytics-serving behavior further.

## Detailed Boundary Rules

The following rules are mandatory for architecture reviews, RFC review, and PR review on affected repositories.

### 1. Allowed `lotus-core` downstream outputs

`lotus-core` may return:

1. canonical state rows,
2. canonical state bundles,
3. policy-scoped snapshots,
4. deterministic input datasets for downstream analytics,
5. benchmark and reference source datasets,
6. request, page, snapshot, and policy provenance,
7. quality, completeness, and freshness diagnostics about those canonical inputs.

### 2. Disallowed `lotus-core` downstream outputs

`lotus-core` must not return new product-facing payloads whose primary value is:

1. portfolio performance analysis,
2. contribution or attribution interpretation,
3. risk score or risk decomposition authority,
4. active risk narrative,
5. front-office explanation text for downstream analytics workflows,
6. gateway-friendly analytics compositions that are actually owned by downstream services.

### 3. Allowed downstream asks to `lotus-core`

`lotus-performance`, `lotus-risk`, `lotus-gateway`, `lotus-advise`, and `lotus-manage` may ask
`lotus-core` for:

1. canonical state inputs,
2. reference and assignment inputs,
3. governed snapshot views,
4. deterministic exportable source datasets,
5. control-plane/policy visibility required to consume those contracts safely.

They may not ask `lotus-core` to own their business interpretation layer.

### 4. Request-shape rules for analytics-input families

Analytics-input contracts must continue to enforce:

1. explicit request windows or periods,
2. explicit consumer context where governance depends on it,
3. deterministic page or export identity,
4. explicit currency semantics where currency-bearing values are present,
5. explicit diagnostics that tell the caller whether the source window is complete enough for safe downstream use.

### 5. Snapshot-family rules

Snapshot families must continue to enforce:

1. explicit section lists,
2. explicit consumer and tenant context,
3. explicit policy provenance,
4. strict rejection or controlled filtering when policy blocks sections,
5. no analytics-section reintroduction through convenience requests.

## Explicit Non-Goals

This RFC does not require:

1. replacing REST integration between `lotus-core` and `lotus-performance`,
2. introducing gRPC as a mandatory internal platform standard,
3. creating a new replacement repository,
4. collapsing `lotus-performance` or `lotus-risk` back into `lotus-core`,
5. moving benchmark or reference source-of-truth ownership out of `lotus-core`,
6. rewriting core calculator logic,
7. eliminating asynchronous/event-driven processing from `lotus-core`.

## REST Versus gRPC Position

This RFC makes the following platform decision.

### 1. REST remains the canonical cross-repository contract style for the current boundary

For the current `lotus-core -> lotus-performance` and `lotus-core -> lotus-risk` integration model:

1. REST/OpenAPI remains the canonical documented contract,
2. RFC-0067 governance remains the primary change-control mechanism,
3. downstream contract tests remain mandatory,
4. platform observability and support flows remain aligned around those contracts.

### 2. gRPC is not prohibited, but it is not the current target action

If Lotus later introduces gRPC for a proven internal hot path, it may do so only when:

1. the canonical REST contract is already stable,
2. the hot path is transport-bound rather than primarily query-bound,
3. the gRPC surface is narrow and internal-only,
4. dual-contract governance is explicitly documented,
5. CI and observability requirements are updated truthfully.

That is a future optimization path, not a current architectural mandate.

## Repository-Specific Implications

### `lotus-core`

Must:

1. continue converging on the governed contract families defined in this RFC,
2. keep analytics behavior de-owned,
3. reduce ambiguity between read-plane, analytics-serving, and control-plane responsibilities,
4. retire or de-emphasize overlapping contract shapes where they create boundary confusion,
5. treat downstream analytics inputs as durable products with governance, not helper payloads.

### `lotus-performance`

Must:

1. consume `lotus-core` as a canonical input authority,
2. keep performance analytics logic local,
3. avoid reconstructing foundational data ownership internally,
4. request upstream contract additions in terms of input data products, not delegated analytics.

### `lotus-risk`

Must:

1. consume `lotus-core` and `lotus-performance` through explicit governed contracts only,
2. keep risk analytics logic local,
3. avoid pushing risk interpretation semantics down into `lotus-core`,
4. use benchmark and reference inputs without recreating source-of-truth ownership.

### `lotus-gateway`

Must:

1. consume product authorities truthfully,
2. not compose unsupported analytics behavior out of raw foundational data,
3. prefer downstream product services for analytics results and `lotus-core` for canonical state or supporting inputs where the ownership model says so.

### `lotus-advise`

Must:

1. consume `lotus-core` as the canonical authority for advisory source data and core-governed simulation execution,
2. consume `lotus-risk` as the authority for advisory risk-lens enrichment,
3. keep proposal workflow, decision-summary, alternatives, approvals, and consent behavior local,
4. avoid expanding stateful operational reads into hidden performance, risk, or reporting methodology.

### `lotus-manage`

Must:

1. continue consuming `lotus-core` for canonical management-side state requirements,
2. avoid growing parallel foundational state ownership,
3. request new `lotus-core` contracts only where management workflows genuinely need core-owned truth.

## Concrete Current-State Interpretation

This RFC interprets the current repositories as follows.

### `lotus-core` today

Current reality:

1. repo-local context already positions `lotus-core` as the authoritative platform for portfolio, booking, account, and transaction data.
2. current runtime already includes split services for query, query control-plane, replay, reconciliation, and orchestration after RFC 081.
3. current query/control-plane surface already mixes the governed contract families recognized in this RFC, even though that classification is not yet the explicit platform rule.

Implication:

1. the architecture direction is not wrong,
2. the missing work is boundary normalization, naming, pruning, and cross-repo enforcement.

### `lotus-performance` today

Current reality:

1. repo-local context states clearly that performance analytics authority stays in `lotus-performance`,
2. the service already treats stateful integration, async execution, lineage capture, and benchmark-aware workflows as core contract behavior,
3. its implementation already centralizes `lotus-core` consumption through dedicated integration and stateful input services.

Implication:

1. `lotus-performance` is already architecturally closer to the target model than a greenfield discussion might suggest,
2. the key remaining work is to keep its upstream asks disciplined and resist pushing performance behavior back into `lotus-core`.

### `lotus-risk` today

Current reality:

1. repo-local context states that risk analytics authority stays in `lotus-risk`,
2. the service already depends on `lotus-core` and `lotus-performance` for stateful or cross-analytic flows,
3. the repo is explicitly product-facing enough that contract drift is visible in Workbench quickly.

Implication:

1. `lotus-risk` should be treated as a consumer that is especially sensitive to hidden boundary drift,
2. cross-analytic input contracts must be explicit, or UI-visible correctness drift will follow.

## Prohibited Moves

The following additions are prohibited unless a later approved RFC explicitly reopens them.

1. Adding performance or risk analytics sections back into `core-snapshot`.
2. Adding new `lotus-core` endpoints that return product-facing performance conclusions owned by `lotus-performance`.
3. Adding new `lotus-core` endpoints that return product-facing risk conclusions owned by `lotus-risk`.
4. Adding duplicate endpoint families that expose the same canonical input with weaker semantics.
5. Treating convenience routes as permanent platform contracts without RFC-0067 and contract-test governance.
6. Introducing a second transport family for the same cross-repo contract without explicit ownership, observability, and CI policy.
7. Hiding consumer-specific interpretation logic in `lotus-core` because a downstream service is not ready yet.

## Change Program By Repository

This section translates the architectural decision into expected work by repository.

### `lotus-core` change program

#### Required

1. inventory all active downstream-facing routes and classify them under the governed contract families,
2. document preferred contract families in architecture docs and repo context,
3. identify overlap or ambiguity between read-plane, analytics-input, and control-plane routing,
4. tighten docs and route descriptions so each contract states what it is for and what it refuses to own,
5. keep RFC-0067 governance attached to all changed public or cross-repo contract surfaces.

#### Expected likely hardening work

1. route grouping cleanup,
2. documentation normalization in README and architecture docs,
3. possible deprecation markers for ambiguous or convenience-biased routes,
4. stronger contract tests for analytics input and policy-bearing routes.

#### Not required by this RFC

1. immediate new microservice splits,
2. transport change to gRPC,
3. rewrite of existing data pipelines.

### `lotus-performance` change program

#### Required

1. map every current upstream call to a contract-family reason,
2. identify any `lotus-core` asks that are really performance-owned behavior,
3. keep lineage, chunking, paging, and export behavior truthful and documented,
4. add or tighten consumer conformance tests where the semantics are sensitive.

#### Expected likely hardening work

1. request-path inventory in technical docs,
2. explicit conformance tests for large-window retrieval semantics,
3. stricter justification for future upstream contract requests.

### `lotus-risk` change program

#### Required

1. identify which current risk workflows rely on `lotus-core` direct inputs versus `lotus-performance` outputs,
2. document those dependencies under the contract-family model,
3. ensure no risk business logic is quietly delegated to `lotus-core`.

#### Expected likely hardening work

1. cross-repo dependency mapping,
2. explicit stateful-input and benchmark-input contract checks,
3. UI-facing validation for any changed upstream semantics.

### `lotus-gateway`, `lotus-advise`, and `lotus-manage` change program

#### Required

1. confirm that new requests to `lotus-core` are genuinely core-owned state needs,
2. refuse shortcut requests that actually belong to analytics authorities,
3. align documentation and composition logic to the platform-owned ownership model.

## Implementation Plan

This RFC is designed to be applied in the current repos through controlled slices.

### Phase 0: Platform rule adoption

Deliverables:

1. approve this RFC,
2. classify it as the platform-owned authority for `lotus-core` downstream-serving boundaries,
3. cross-link it from relevant repo-local contexts and active RFCs where necessary.

Exit criteria:

1. no new boundary work is approved against `lotus-core` without reference to this RFC.

### Phase 1: Contract-family inventory and mapping

Deliverables:

1. inventory all downstream-facing `lotus-core` contracts,
2. classify each one as operational-read, snapshot/simulation, analytics-input, or control-plane,
3. identify overlaps, legacy shapes, and ambiguous ownership surfaces,
4. produce a canonical map in `lotus-core` architecture docs.

Exit criteria:

1. every active downstream-facing contract family has an explicit ownership classification.

Suggested concrete outputs:

1. one inventory table covering route, owner, family, primary consumers, and notes,
2. one overlap table listing routes that need deprecation, merge, or clearer classification,
3. one consumer map showing which repos depend on which `lotus-core` contract families.

### Phase 2: Boundary hardening in code and docs

Deliverables:

1. align service/module naming and docs to the contract-family model,
2. tighten routing and package ownership where confusion remains,
3. retire or de-emphasize overlapping surfaces that violate this RFC,
4. ensure analytics input products are described as first-class contracts.

Exit criteria:

1. `lotus-core` no longer presents ambiguous ownership between read-plane, analytics-serving, and control-plane behavior.

Suggested concrete outputs:

1. repo context updates,
2. README and architecture-doc updates,
3. route-description normalization,
4. any deprecation markers or contract notes required by RFC-0067.

### Phase 3: Cross-repo consumer conformance

Deliverables:

1. validate `lotus-performance`, `lotus-risk`, `lotus-gateway`, `lotus-advise`, and `lotus-manage` against the contract-family model,
2. add or update cross-repo contract tests where missing,
3. tighten vocabulary and provenance enforcement where consumers still rely on implicit assumptions.

Exit criteria:

1. downstream consumers use the governed contract families intentionally and without boundary drift.

Suggested concrete outputs:

1. `lotus-performance` upstream contract map,
2. `lotus-risk` upstream contract map,
3. targeted contract and conformance tests,
4. explicit gateway composition notes where user-facing behavior depends on these boundaries.

### Phase 4: Performance-shape hardening

Deliverables:

1. profile high-volume stateful retrieval paths,
2. optimize page sizes, chunk sizes, export behavior, and retrieval orchestration,
3. revisit transport only if evidence shows transport overhead is the real bottleneck.

Exit criteria:

1. large-window analytics retrieval is efficient enough under current REST governance to support planned platform use.

Suggested concrete outputs:

1. benchmark and retrieval profiling notes,
2. chunk-size and page-size recommendations,
3. explicit statement on whether transport optimization is still unnecessary after contract-shape hardening.

## Execution Checklist

The following checklist is the minimum execution baseline for early RFC-0082 slices.

### Slice 1: Inventory and classification

1. enumerate all active `lotus-core` downstream-facing routes,
2. classify each route into one contract family,
3. record primary consumers,
4. identify ambiguous or overlapping shapes,
5. publish the inventory as a durable architecture artifact.

Current Slice 1 artifact:

1. `C:/Users/Sandeep/projects/lotus-core/docs/architecture/RFC-0082-contract-family-inventory.md`

Current Slice 1 classification result:

1. `query_service` owns operational read contracts,
2. `query_control_plane_service` owns analytics input, snapshot/simulation, support, lineage, integration policy, and capability contracts,
3. `ingestion_service` owns write-ingress and adapter ingestion contracts,
4. `event_replay_service` owns replay, DLQ, ingestion health, and operations control-plane contracts,
5. `financial_reconciliation_service` owns reconciliation/control execution contracts,
6. benchmark, index, risk-free, taxonomy, enrichment, reporting, cashflow projection, and simulation summary surfaces are marked as watchlist areas requiring explicit RFC-0082 review before material expansion.

### Slice 2: Documentation and boundary normalization

1. update `lotus-core` repo context and architecture docs,
2. normalize route descriptions around what/how/when and ownership language,
3. add deprecation or boundary notes where needed,
4. align `lotus-performance` and `lotus-risk` docs to the same terminology.

Current Slice 2 documentation normalization artifacts:

1. `C:/Users/Sandeep/projects/lotus-core/README.md`
2. `C:/Users/Sandeep/projects/lotus-core/REPOSITORY-ENGINEERING-CONTEXT.md`
3. `C:/Users/Sandeep/projects/lotus-core/docs/architecture/lotus-core-target-architecture.md`
4. `C:/Users/Sandeep/projects/lotus-core/docs/architecture/QUERY-SERVICE-AND-CONTROL-PLANE-BOUNDARY.md`

Current Slice 2 result:

1. `lotus-core` README now distinguishes `query_service`, `query_control_plane_service`, `event_replay_service`, and `financial_reconciliation_service` responsibilities.
2. `lotus-core` target architecture now references RFC-0082 and the contract-family inventory as current downstream-boundary truth.
3. the query/control-plane boundary note now delegates route-family watchlist and current classification to the RFC-0082 inventory.
4. repo-local context now treats RFC-0082 classification changes as durable context changes.

### Slice 3: Conformance hardening

1. add targeted cross-repo contract tests,
2. validate no forbidden analytics ownership has crept into `lotus-core`,
3. ensure downstream consumers are using the intended contract families.

Current Slice 3 consumer-conformance artifacts:

1. `C:/Users/Sandeep/projects/lotus-performance/docs/technical/RFC-0082-upstream-contract-family-map.md`
2. `C:/Users/Sandeep/projects/lotus-performance/REPOSITORY-ENGINEERING-CONTEXT.md`
3. `C:/Users/Sandeep/projects/lotus-risk/docs/domain-apis/RFC-0082-upstream-contract-family-map.md`
4. `C:/Users/Sandeep/projects/lotus-risk/REPOSITORY-ENGINEERING-CONTEXT.md`
5. `C:/Users/Sandeep/projects/lotus-gateway/docs/standards/RFC-0082-upstream-contract-family-map.md`
6. `C:/Users/Sandeep/projects/lotus-gateway/REPOSITORY-ENGINEERING-CONTEXT.md`
7. `C:/Users/Sandeep/projects/lotus-advise/docs/architecture/RFC-0082-upstream-contract-family-map.md`
8. `C:/Users/Sandeep/projects/lotus-advise/REPOSITORY-ENGINEERING-CONTEXT.md`
9. `C:/Users/Sandeep/projects/lotus-manage/docs/standards/RFC-0082-upstream-contract-family-map.md`
10. `C:/Users/Sandeep/projects/lotus-manage/REPOSITORY-ENGINEERING-CONTEXT.md`

Current Slice 3 result:

1. `lotus-performance` maps all active `lotus-core` stateful upstream calls to RFC-0082 families and keeps performance conclusions local.
2. `lotus-risk` maps `lotus-core` calls to analytics-input, snapshot/simulation, and support metadata families while preserving `lotus-performance` authority for returns and benchmark exposure context.
3. `lotus-gateway` maps core operational read, support, policy, snapshot/simulation, analytics-input, and watchlist surfaces while preserving performance, risk, advisory, management, reporting, and AI authority upstream.
4. `lotus-advise` maps core advisory simulation, stateful source-data reads, enrichment inputs, and risk concentration enrichment while keeping advisory workflow local and domain calculations upstream.
5. `lotus-manage` maps DPM execution, supportability, policy-pack, capabilities, and source-data input posture while keeping `lotus-core` as source-data authority and `lotus-advise` as advisory workflow authority.
6. all current consumer maps explicitly defer gRPC and require retrieval-shape evidence before transport optimization is proposed.
7. existing upstream-client and integration tests are identified as current conformance evidence; no runtime contract changed in this slice.

### Slice 4: Retrieval performance hardening

1. profile hot retrieval paths,
2. tune page/chunk/export behavior,
3. document whether any further transport work is justified.

Current Slice 4 retrieval-performance artifacts:

1. `C:/Users/Sandeep/projects/lotus-performance/docs/technical/RFC-0082-retrieval-performance-hardening.md`
2. `C:/Users/Sandeep/projects/lotus-performance/docs/technical/performance_characterization.md`
3. `C:/Users/Sandeep/projects/lotus-performance/tests/benchmarks/test_stateful_input_performance.py`
4. `C:/Users/Sandeep/projects/lotus-performance/tests/benchmarks/test_returns_series_orchestration_performance.py`

Current Slice 4 result:

1. targeted 10-year stateful retrieval and returns-series orchestration characterization passed under existing governed budgets,
2. current defaults remain `90`-day portfolio chunks, `365`-day reference chunks, `4` concurrent chunks, and `5000` row portfolio/position page size,
3. current evidence does not justify gRPC between `lotus-performance` and `lotus-core`,
4. future work must tune chunking, paging, export use, concurrency, retry, and upstream query shape before proposing transport changes.

## Validation And Evidence Model

This RFC is architecture-governance work, but it must still be validated against real repositories.

### Required Feature Lane evidence

For any slice implementing this RFC:

1. targeted repo-native tests in the changed repo,
2. contract tests covering the changed boundary,
3. OpenAPI and vocabulary validation where the contract changed,
4. updated docs proving the boundary truth changed intentionally.

### Required PR Merge Gate evidence

1. `lotus-core` PR-grade gate if `lotus-core` contracts or runtime changed,
2. affected downstream repo PR-grade gate if the slice changed consumer expectations,
3. explicit evidence of which contract family was changed,
4. truthful note of any remaining gap or deferred slice.

### Platform End-to-End evidence

Required when:

1. gateway-facing product behavior changes,
2. canonical front-office workflows depend on the changed boundary,
3. seeded performance or risk workspaces rely on the adjusted contracts.

### Lane mapping by expected slice type

| Slice type | Typical repositories | Minimum lane | Escalation trigger |
| --- | --- | --- | --- |
| docs-only RFC or architecture inventory | `lotus-platform`, `lotus-core` docs | Feature Lane docs proof | none unless contracts changed |
| route-description or OpenAPI clarification | `lotus-core` | Feature Lane plus contract gates | PR Merge Gate when request/response semantics or OpenAPI output changes |
| contract-family route cleanup or deprecation | `lotus-core` plus affected consumers | PR Merge Gate | platform end-to-end when gateway/workbench behavior changes |
| consumer conformance hardening | `lotus-performance`, `lotus-risk`, `lotus-gateway`, `lotus-advise`, `lotus-manage` | Feature Lane in affected consumer plus targeted upstream tests | PR Merge Gate when contract or runtime coupling changed |
| retrieval-performance tuning | `lotus-core`, `lotus-performance` | Feature Lane plus targeted characterization | PR Merge Gate and possibly main-grade characterization if hot paths are materially altered |

### Recommended repo-native validation commands

When implementing this RFC in code, the default command posture is:

#### `lotus-core`

1. fast proof: `make test` or narrower targeted tests plus contract gates,
2. Feature Lane parity: `make ci-local`,
3. PR Merge Gate parity: `make ci`.

#### `lotus-performance`

1. fast proof: `make check`,
2. PR Merge Gate parity: `make ci`,
3. characterization-heavy work: `make test-all` as needed.

#### `lotus-risk`

1. fast proof: `make check`,
2. targeted suites: `make test-unit` and `make test-integration`,
3. PR Merge Gate parity: `make ci`.

#### `lotus-gateway`

1. fast proof: `make check`,
2. PR Merge Gate parity: `make ci`,
3. platform-facing behavior proof when Workbench contracts change.

#### `lotus-advise`

1. fast proof: `make check`,
2. PR Merge Gate parity: `make ci`,
3. live runtime proof when proposal simulation, decision-summary, or proposal-alternatives behavior changes.

#### `lotus-manage`

1. fast proof: `make check`,
2. feature-lane local parity: `make ci-local`,
3. PR Merge Gate parity: `make ci`,
4. canonical front-office proof when gateway-facing management workflows change.

## Acceptance Criteria

This RFC is considered implemented when all of the following are true.

1. Lotus has one approved platform-owned authority for `lotus-core` downstream-serving boundaries.
2. `lotus-core` contract surfaces are classifiable under governed RFC-0082 contract families without ambiguity.
3. No active `lotus-core` contract claims ownership of downstream performance or risk analytics behavior.
4. `lotus-performance`, `lotus-risk`, `lotus-gateway`, and `lotus-advise` consume `lotus-core` through explicit governed contracts rather than convenience assumptions.
5. Overlapping or weakly governed endpoint families have been retired, documented as deprecated, or formally classified.
6. Cross-repo docs and contexts reflect the actual boundary truth.
7. Any future discussion of transport optimization starts from this contract model rather than replacing it.

## Traceability To Existing RFCs

This RFC does not replace all existing repo-local RFCs. It consolidates the platform-level rule above them.

### Relationship to `lotus-core` RFC 035

`lotus-core` RFC 035 identified the cross-repo responsibility problem but left the final platform-owned boundary contract incomplete.

RFC-0082 closes that governance delta.

### Relationship to `lotus-core` RFC 049

RFC 049 de-owned analytics sections from core snapshot behavior.

RFC-0082 adopts that as a platform rule rather than a repo-local decision.

### Relationship to `lotus-core` RFC 063

RFC 063 established the implemented analytics-input family for `lotus-performance`.

RFC-0082 generalizes the governing principle:

1. analytics inputs are first-class data products,
2. they are the preferred pattern for downstream analytics sourcing,
3. they must not collapse back into generic convenience reads or snapshots.

### Relationship to `lotus-core` RFC 081

RFC 081 improved microservice and control-plane decomposition inside `lotus-core`.

RFC-0082 does not supersede those runtime decisions.

Instead, it explains how those runtime boundaries should be interpreted and governed at the platform level.

## Consequences

### Positive

1. Clearer architectural truth for `lotus-core`.
2. Lower risk of domain-ownership sprawl.
3. Better downstream contract governance.
4. Easier performance optimization because the retrieval model is explicit.
5. Lower probability of shipping pre-live design debt into first production release.

### Negative

1. Some current docs and route groupings may need cleanup.
2. Teams lose some freedom to add convenience contracts quickly.
3. Cross-repo review burden increases for boundary-changing work.

### Accepted cost

That cost is acceptable because the estate is pre-live and banking-grade architectural clarity is more valuable now than temporary speed from weakly governed additions.

## Open Questions

1. Should the contract-family inventory become a generated artifact in `lotus-core`, or remain a curated architecture document?
2. Should platform CI add an ownership assertion layer for cross-repo endpoint classification, or is RFC/document governance sufficient for now?
3. Which existing `lotus-core` endpoints, if any, still look too much like generic convenience reads and should be retired first?
4. At what measurable threshold, if any, should Lotus consider a narrow gRPC optimization for analytics-input hot paths?

## Recommended Next Actions

1. Approve this RFC as the platform-owned authority that closes the open governance delta referenced by `lotus-core` RFC 035.
2. Create a short implementation checklist for the first hardening slice:
   - contract-family inventory
   - overlap assessment
   - repo-context alignment
   - cross-repo consumer mapping
3. Update `lotus-core` architecture docs and repo context to reference this RFC once approved.
4. Add targeted cross-repo conformance checks for `lotus-performance` and `lotus-risk` consumption of analytics input contracts.
5. Keep `lotus-gateway`, `lotus-advise`, and `lotus-manage` consumer maps in the same RFC-0082 evidence package whenever upstream boundary classifications change.
