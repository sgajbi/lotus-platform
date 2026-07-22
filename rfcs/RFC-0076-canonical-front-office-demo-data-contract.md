# RFC-0076: Canonical Front-Office Demo Data Contract

- Status: Proposed
- Date: 2026-04-11
- Owners: lotus-platform governance
- Requires Approval From:
  - lotus-platform maintainers
  - lotus-core maintainers
  - lotus-performance maintainers
  - lotus-risk maintainers
  - lotus-gateway maintainers
  - lotus-workbench maintainers
- Related:
  - `RFC-0057-test-pyramid-and-meaningful-coverage-governance.md`
  - `RFC-0063-performance-analytics-input-contracts-and-stateful-computation.md`
  - `RFC-0067-centralized-api-vocabulary-inventory-and-openapi-documentation-governance.md`
  - `RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`
  - `RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md`
  - `RFC-0074-repeatable-developer-and-agent-bootstrap-system.md`
  - `RFC-0075-canonical-front-office-portfolio-seed-and-demo-validation-system.md`
  - `RFC-0076-implementation-checklist.md`
  - `RFC-0076-slice-1-contract-spec-evidence.md`
  - `RFC-0076-slice-2-core-contract-enforcement-evidence.md`
  - `RFC-0076-slice-3-derived-state-readiness-evidence.md`

## Summary

RFC-0075 established a governed canonical front-office runtime centered on
`PB_SG_GLOBAL_BAL_001`. The next hardening step is to govern the portfolio itself as a durable
data contract rather than a set of scripts and implied assumptions.

This RFC proposes a banking-grade contract for the canonical demo and QA portfolio, the associated
benchmark, the required economics, the derived-state readiness expectations, and the cross-service
invariants that must remain true if the Lotus analytics stack is to be trusted for demos,
regression validation, and product-surface verification.

## Decision

Lotus will treat the canonical front-office dataset as governed product infrastructure.

That means:

1. `PB_SG_GLOBAL_BAL_001` is not a smoke fixture and not disposable sample data.
2. The canonical benchmark and reference data are part of the contract, not optional seed detail.
3. The dataset must remain economically coherent across portfolio, transaction, valuation,
   performance, risk, gateway, and Workbench layers.
4. UI population is not sufficient evidence of correctness; the contract is satisfied only when
   seeded data, derived state, and downstream analytics all pass governed validation.

## Problem

The current canonical seed works, but the platform still relies on too much implicit knowledge:

1. the required transaction and holdings shape is not formally governed,
2. benchmark and market-data completeness is not expressed as a first-class contract,
3. derived-state readiness still depends on validators discovering issues after the fact,
4. downstream apps can assume support that the dataset no longer exercises,
5. future agents can confuse a demo seed with shallow UI-population data,
6. the platform lacks a durable definition of what "front-office complete" means for a canonical
   portfolio.

For a production-critical private-banking platform, this is not a strong enough operating model.

## Why This RFC Matters

The canonical portfolio serves multiple roles simultaneously:

1. demo dataset,
2. end-to-end regression dataset,
3. contract-validation dataset,
4. UI-population dataset,
5. engineering investigation dataset.

If that dataset is not explicitly governed, the platform can appear healthy while silently losing
real capability coverage.

## Goals

1. Define `PB_SG_GLOBAL_BAL_001` as the governed canonical front-office demo and QA portfolio.
2. Define `BMK_PB_GLOBAL_BALANCED_60_40` as the governed canonical balanced benchmark.
3. Define a fixed as-of date policy and a controlled refresh policy.
4. Define the minimum economic realism required for a credible private-banking portfolio.
5. Define the required transaction-lifecycle coverage.
6. Define the required instrument, cash, FX, market-price, benchmark, and risk-free coverage.
7. Define the required downstream derived-state and analytics-readiness invariants.
8. Define which repository owns each contract dimension.
9. Make the contract machine-readable and test-enforced.
10. Keep the dataset broad enough to exercise the Lotus stack without becoming operationally heavy.

## Non-Goals

1. Replacing production ingestion or client data management.
2. Creating many overlapping demo portfolios.
3. Optimizing all analytics engines as part of this RFC alone.
4. Faking unsupported capabilities to make screenshots look complete.
5. Defining new product capabilities without backend and gateway ownership.

## Contract Scope

This contract governs five layers:

1. seed identity and economic design,
2. reference and benchmark completeness,
3. derived-state readiness,
4. downstream analytics supportability,
5. validation and evidence expectations.

## Canonical Portfolio Contract

### Portfolio Identity

The canonical portfolio remains:

```text
PB_SG_GLOBAL_BAL_001
```

Required identity attributes:

1. stable portfolio code,
2. stable private-banking style display name,
3. booking center and booking entity,
4. mandate or investment-profile classification,
5. base currency,
6. relationship-manager and advisory context where supported,
7. inception date and supported analysis windows,
8. deterministic identifiers suitable for automated validation.

### Advisor-Book Assignment Identity

The canonical own-book proof uses a distinct governed portfolio-manager assignment:

```text
PB_SG_GLOBAL_BAL_001 -> PM_SG_001 (portfolio_manager / portfolio_management)
```

Core seed automation must persist that effective-dated assignment from the contract before
Workbench validation. Gateway evidence must retain `PortfolioManagerBookMembership:v1`, the
governed assignment basis, the requested business date, and Core source lineage. This identity is
not the Advisor Cockpit `advisor_sg_001` persona and is not the DPM command-center
`PM_SG_DPM_001` manager. Tenant identity remains trusted caller context until `lotus-core#798`
delivers source-confirmed ownership, so the contract must not promote the advisor-book panel beyond
its governed partial posture on tenant evidence alone.

Platform validation must execute Core's advisor-book seed verifier from the governed Core checkout,
not infer compliance from contract text or source markers. The verifier exercises the same bundle
and dependency-ordered ingestion-request builders as the live seed and returns structured evidence
for the portfolio and manager, governed business date, role and scope, effective interval,
assignment version, source system/record/product, observation time, quality status, ingestion
endpoint, and exact assignment count. Platform derives the expected proof shape from this contract
instead of maintaining a second identity list. Core must derive the reported product/version from
its executable source-data-product registry and fail when that registry disagrees with the central
contract; returning the central value unchanged is not source-product proof.
The executable proof must also bind the single PM-book route, exact Gateway/Manage consumer set,
Core ownership, query-control-plane serving plane, and analytics-input route family.

### Benchmark Identity

The canonical benchmark remains:

```text
BMK_PB_GLOBAL_BALANCED_60_40
```

Required benchmark attributes:

1. stable benchmark code,
2. stable benchmark display name,
3. benchmark composition and weights,
4. return series covering the governed warm-up and reporting windows,
5. mapping to supported portfolio analytics dimensions,
6. benchmark metadata suitable for gateway and Workbench display.

### Canonical Date Policy

The canonical as-of date is fixed unless changed through approved governance.

Initial contract date:

```text
2026-04-10
```

Date policy rules:

1. the contract date may change only through an approved RFC or approved implementation slice,
2. the seed must clearly separate historical data from projected data,
3. validators must assert freshness relative to the governed canonical date, not the machine clock,
4. any refresh must preserve economic coherence and panel support coverage.

## Economic Design Requirements

The portfolio must look and behave like a realistic front-office book, not a generic test basket.

### Required Asset-Class Coverage

The portfolio must include representative exposure across supported categories, including:

1. cash,
2. listed equity,
3. fixed income,
4. fund or multi-asset exposure,
5. alternative or private-credit style exposure where supported,
6. multi-currency exposure where supported by the current services.

### Required Instrument Reference Coverage

Each instrument in scope must have enough reference data for:

1. display and narrative labeling,
2. asset-class classification,
3. sector or issuer grouping where supported,
4. valuation and market-price support,
5. concentration analysis,
6. performance segmentation,
7. benchmark comparability where applicable,
8. risk grouping and methodology alignment.

### Required Transaction-Lifecycle Coverage

The canonical seed must exercise a broad but bounded set of economically meaningful events:

1. opening funding,
2. subscriptions or buys,
3. sales,
4. income and coupons or dividends,
5. fees or charges,
6. withdrawals,
7. FX-sensitive cash movement where supported,
8. projected cashflow behavior where supported.

The contract must explicitly define:

1. sign conventions,
2. deterministic transaction IDs,
3. deterministic source IDs,
4. deterministic economic event IDs,
5. expected quantity behavior,
6. expected cash-leg behavior,
7. expected post-transaction positions and cash state.

### Required Economic Coherence

The seeded dataset must remain coherent across:

1. transactions and resulting positions,
2. positions and valuations,
3. benchmark linkage and performance calculations,
4. concentration and holdings structure,
5. cash, cash accounts, and liquidity behavior,
6. future cashflow projections where exposed.

The contract must reject seeds that merely populate tables while failing these underlying
relationships.

## Reference and Market Data Requirements

The contract must define the minimum required completeness for:

1. instrument master data,
2. market prices,
3. FX rates where cross-currency behavior exists,
4. benchmark history,
5. risk-free or supporting rate data where the relevant analytics require it,
6. allocation metadata needed for supported views,
7. any supporting reference data required by gateway or Workbench product surfaces.

## Derived-State Readiness Contract

The canonical portfolio is not "ready" until all governed derived state is current for the
canonical date.

Required readiness includes:

1. positions,
2. valued positions,
3. position timeseries,
4. portfolio timeseries where still required by governed services,
5. analytics reference performance end date,
6. performance return path,
7. contribution and attribution source rows,
8. risk summary metrics,
9. concentration outputs,
10. drawdown outputs,
11. rolling-risk outputs,
12. historical risk attribution outputs.

The contract must distinguish:

1. seed data loaded,
2. derived state pending,
3. analytically ready,
4. product-surface ready.

## Machine-Readable Contract Artifacts

The implementation must create durable contract artifacts, for example:

```text
context/contracts/canonical-front-office-demo-data-contract.json
context/contracts/canonical-front-office-demo-data-invariants.json
```

The exact file split may vary, but the contract must remain:

1. versioned,
2. machine-readable,
3. test-consumable,
4. documented,
5. stable enough for cross-repo use.

The machine-readable contract should capture at minimum:

1. portfolio identity,
2. benchmark identity,
3. governed date,
4. supported asset and transaction categories,
5. required counts or minimum thresholds,
6. freshness and readiness expectations,
7. known supported and intentionally partial analytics surfaces,
8. contract version metadata.

## Ownership Model

Ownership must be explicit.

### `lotus-core`

Owns:

1. canonical portfolio seeding,
2. transaction and holdings economics,
3. valuation input readiness,
4. benchmark and reference data seeding where core is the system of record,
5. seed and derived-state validators.

### `lotus-performance`

Owns:

1. performance readiness expectations,
2. return-path and contribution support,
3. any contract invariants required for governed performance product surfaces.

### `lotus-risk`

Owns:

1. risk summary support,
2. concentration, drawdown, rolling-risk, and attribution readiness expectations,
3. any risk-specific completeness checks tied to the canonical portfolio.

### `lotus-gateway`

Owns:

1. truthful exposure of canonical portfolio metadata,
2. benchmark linkage exposure,
3. contract-backed downstream API behavior for supported surfaces.

### `lotus-workbench`

Owns:

1. truthful panel rendering,
2. no fake support for unsupported analytics,
3. validation and screenshot evidence aligned with the contract.

### `lotus-platform`

Owns:

1. cross-repo contract governance,
2. documentation, onboarding, and agent context alignment,
3. platform-level validation summaries and acceptance evidence.

## Validation and Evidence Rules

This RFC requires validation at three levels:

1. data-contract validation,
2. derived-state readiness validation,
3. product-surface validation.

Validation must answer:

1. is the dataset economically complete,
2. is the dataset analytically ready,
3. which panels are expected to be ready, partial, or unavailable,
4. whether any regression is caused by data, readiness, contract, or UI behavior.

## Skills, Context, and Documentation Implications

This RFC should not be implemented as a backend-only data exercise. The canonical data contract
changes how future agents and developers should reason about front-office runtime quality.

Expected guidance outcomes:

1. agent and onboarding guidance should explicitly treat the canonical portfolio as governed product
   infrastructure rather than disposable smoke data,
2. stale references to timestamped smoke portfolios or ad hoc demo seeds should be removed where
   they conflict with the governed contract,
3. front-office runtime and validation guidance should point to the contract location when dataset
   expectations matter,
4. skill updates should be made only where they materially improve routing or reduce repeated
   mistakes; otherwise "no change required" should be recorded consciously,
5. documentation should clearly distinguish between:
   - canonical demo and QA data,
   - repo-local test fixtures,
   - experimental or disposable seed paths.

Likely candidates for review during implementation:

1. `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`
2. `lotus-platform/docs/onboarding/LOTUS-AGENT-RAMP-UP.md`
3. `lotus-platform/docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md`
4. front-office runtime skills and QA/validation skills that reference seeded data behavior.

## Implementation Slices

### Slice 1: Contract Document and Machine-Readable Spec

1. add the canonical data contract document,
2. add the machine-readable contract artifacts,
3. define versioning, governed date, portfolio identity, benchmark identity, and minimum invariant
   sets.

### Slice 2: Core Seed Contract Enforcement

1. update `lotus-core` seed tooling to read or mirror the contract,
2. assert required instrument, transaction, cash, FX, market-price, benchmark, and supporting-rate
   coverage,
3. fail fast on missing, stale, or incoherent seed inputs,
4. add focused tests around economic invariants rather than superficial record counts alone.

### Slice 3: Derived-State Readiness Enforcement

1. enforce current position and valuation state for the governed date,
2. enforce analytics reference freshness and downstream readiness,
3. produce actionable diagnostics for backlog or stale state conditions,
4. ensure readiness semantics are consistent across core, performance, and risk.

### Slice 4: Cross-App Contract Adoption

1. update platform and Workbench validators to consume contract version and expected support rules,
2. align gateway expectations with the governed portfolio and benchmark contract,
3. expose contract-aware diagnostics in validation summaries and demo evidence outputs.

### Slice 5: Documentation, Agent Context, Skill Alignment, and Branch Hygiene

1. update platform onboarding, runbooks, and engineering context with the canonical data-contract
   location and ownership model,
2. review relevant skills and guidance to decide whether they should reference the contract
   explicitly or remain unchanged by design,
3. remove or tighten stale guidance that still encourages non-governed seed paths or disposable
   smoke portfolios,
4. document any conscious "no change required" decisions for skills and context where applicable,
5. complete branch hygiene, PR evidence hygiene, and cross-repo reference cleanup before closure.

## Acceptance Criteria

1. `PB_SG_GLOBAL_BAL_001` has a documented and machine-readable governed data contract.
2. The seed verifier enforces required coverage and economic invariants.
3. Derived-state readiness is validated against the governed date and contract expectations.
4. Platform and Workbench validation summaries include contract version or contract identity.
5. The implementation adds meaningful tests that would catch contract drift.
6. Documentation, agent context, and relevant skills are consciously reviewed as part of closure.
7. GitHub PR checks pass before merge.

## Risks and Mitigations

### Risk: The contract becomes too rigid

Mitigation:

1. use minimum thresholds or ranges where exact values are not business-critical,
2. version the contract explicitly,
3. require governance for material contract changes.

### Risk: The dataset becomes too heavy for repeatable local use

Mitigation:

1. keep one canonical portfolio rather than many overlapping seeds,
2. optimize for broad capability coverage with bounded data volume,
3. validate realism and runtime cost together.

### Risk: UI population drives unrealistic data decisions

Mitigation:

1. require economic coherence and backend ownership before expanding the contract,
2. fail validation when seeded data is cosmetically useful but analytically weak,
3. keep Workbench supportability subordinate to real backend capability.

## Approval Request

Approval is requested to define and enforce the canonical front-office dataset as governed product
infrastructure, with explicit economic, readiness, validation, documentation, and agent-context
obligations.
