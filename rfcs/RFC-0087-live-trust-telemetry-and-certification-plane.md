# RFC-0087 - Live Trust Telemetry and Certification Plane

| Field | Value |
| --- | --- |
| Status | Implemented |
| Created | 2026-04-19 |
| Last Updated | 2026-04-19 |
| Owners | lotus-platform architecture; domain repository maintainers; lotus-gateway maintainers |
| Depends On | RFC-0071; RFC-0072; RFC-0079; RFC-0084; RFC-0085; RFC-0086 |
| Related Standards | `RFC-0071-centralized-environment-scoped-service-addressing-and-ingress-governance.md`; `RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`; `RFC-0079-gateway-evidence-and-lineage-contract.md`; `RFC-0084-mesh-governance.md`; `RFC-0085-gateway-governed-domain-product-publication-and-trust-contracts.md`; `RFC-0086-repo-native-domain-product-onboarding-and-federated-rollout.md`; `docs/standards/Platform Observability Standards.md` |
| Scope | Cross-repo |

## Executive Summary

RFC-0084 defines declared trust posture. RFC-0085 defines published trust posture. RFC-0086 moves
declaration ownership into the producing and consuming repositories.

What Lotus still lacks after those steps is live operational truth.

Today freshness, completeness, supportability, and lineage posture are mostly declared or inferred
from route logic. That is a strong start, but a credible mesh needs runtime-backed trust signals,
not just schema-backed promises.

This RFC establishes the live trust telemetry and certification plane for Lotus.

The target state is:

1. domain products emit governed trust telemetry,
2. platform collects and certifies freshness, completeness, lineage, reconciliation, and blocked
   state posture,
3. gateway publication contracts can surface runtime-backed trust status instead of only declared
   trust policy,
4. workbench and future ecosystem APIs can tell users when a result is current, partial, stale,
   blocked, or unsupported based on live evidence.

This is the RFC that turns trust metadata from declaration truth into operational truth.

## Original Requested Requirements (Preserved)

The user intent preserved in this RFC is:

1. move Lotus toward a credible mesh rather than a naming exercise,
2. cover live telemetry and trust certification as one of the missing areas beyond RFC-0084 and
   RFC-0085,
3. keep the work implementation-bearing and commercially meaningful,
4. preserve the same RFC quality bar with mandatory second-last and final slices,
5. consciously assess whether context, documentation, or skills should change to support future
   trust-certification work.

## Current Implementation Reality

Overall classification: `Implemented and proven for the first-wave live trust certification plane`

### What is implemented well today

#### 1. Trust vocabulary already exists

Evidence:

1. `platform-contracts/domain-vocabulary/domain-data-product-semantics.v1.json`
2. `platform-contracts/domain-vocabulary/domain-data-product-trust-metadata.v1.json`
3. `rfcs/RFC-0084-mesh-governance.md`

Assessment:

Lotus has a controlled vocabulary for trust posture. The missing piece is live emission and
certification against that vocabulary.

#### 2. Gateway already surfaces supportability and evidence posture in pockets

Evidence:

1. `<workspace-root>/lotus-gateway/src/app/services/platform_capabilities_service.py`
2. `<workspace-root>/lotus-gateway/src/app/services/performance_workspace_service.py`
3. `<workspace-root>/lotus-gateway/src/app/services/risk_workspace_service.py`
4. `<workspace-root>/lotus-gateway/tests/integration/test_workbench_router.py`

Assessment:

Gateway knows how to expose trust posture, but current behavior is still largely route-shaped rather
than backed by a shared live trust telemetry plane.

#### 3. Lotus already has observability and evidence patterns

Evidence:

1. `docs/standards/Platform Observability Standards.md`
2. `rfcs/RFC-0079-gateway-evidence-and-lineage-contract.md`
3. `rfcs/RFC-0081-slice-11-performance-accessibility-and-operability-hardening-evidence.md`

Assessment:

There is enough existing posture around observability, evidence, and lineage to justify a stronger
platform-owned live trust plane rather than inventing an entirely new model.

### What is now implemented

1. `platform-contracts/trust-telemetry/trust-telemetry-snapshot.schema.json` defines the governed
   RFC-0087 telemetry snapshot contract,
2. `automation/validate_trust_telemetry.py` validates telemetry snapshots against the generated
   domain-product catalog and trust vocabulary,
3. `automation/generate_live_trust_certification.py` converts validated telemetry snapshots into
   deterministic live trust certification artifacts,
4. first-wave producer telemetry snapshots are merged in:
   - `lotus-core/contracts/trust-telemetry/portfolio-state-snapshot.telemetry.v1.json`,
   - `lotus-performance/contracts/trust-telemetry/returns-series-bundle.telemetry.v1.json`,
   - `lotus-risk/contracts/trust-telemetry/risk-metrics-report.telemetry.v1.json`,
   - `lotus-advise/contracts/trust-telemetry/advisory-proposal-lifecycle-record.telemetry.v1.json`,
5. each first-wave producer repo has a local telemetry test that validates the snapshot with the
   platform contract when `lotus-platform` is available and checks observed trust metadata against
   the repo-native domain-product declaration.

### What is now proven end to end

1. `lotus-gateway` now consumes the platform live-trust certification artifact through
   `GET /api/v1/domain-products/trust-certification` and returns explicit unavailable posture when
   the platform artifact is absent.
2. `lotus-workbench` now renders runtime-backed trust state on `/data-products` through gateway/BFF
   calls only, including unavailable and degraded states.
3. Platform CI has commands and tests for telemetry validation and live certification generation.

Remaining future hardening:

1. cross-repo live trust telemetry certification is not yet a mandatory platform merge gate across
   all participating repositories,
2. consumer-side and gateway-owned telemetry emission should be added only when there is a concrete
   consumer trust signal to certify.

## Requirement-to-Implementation Traceability

| Requirement | Current evidence | Current status | RFC-0087 response |
| --- | --- | --- | --- |
| Move from declared trust to operational truth | Platform telemetry contracts, producer snapshots, live certification generation, gateway trust endpoint, and Workbench discovery UI now exist | Satisfied for first wave | Gateway and Workbench consumption are merged |
| Make trust posture customer-credible | First-wave producer telemetry certifies cleanly and gateway/workbench expose certified or unavailable trust posture | Satisfied for first wave | UI-facing states are backed by certified runtime evidence where available |
| Keep the work implementation-bearing | Four producer repos carry contract fixtures/tests; platform generates live trust; gateway/workbench consume it | Satisfied for first wave | Remaining work is future mandatory gate hardening |
| Preserve second-last and final closure slices | Gateway/workbench tests, PR evidence, docs/context updates, and no-new-skill decision are recorded | Satisfied for first wave | Slice 7 and Slice 8 are closed for this implementation boundary |

## Design Reasoning and Trade-offs

The key design choice is to separate:

1. trust declaration,
2. live trust telemetry,
3. published trust posture.

That separation matters.

### Why live trust telemetry should be a separate RFC

If declaration rollout and telemetry rollout are mixed into one RFC, the result becomes muddy:

1. ownership migration gets blocked on runtime plumbing,
2. telemetry rules get diluted into schema migration work,
3. it becomes harder to parallelize implementation cleanly.

RFC-0086 should establish who owns declarations. RFC-0087 should establish how runtime truth is
measured and certified.

### Why certification should be platform-owned

If each repo interprets freshness or completeness differently, Lotus loses the credibility of its
trust posture.

`lotus-platform` should own:

1. trust telemetry schemas,
2. certification rules,
3. artifact generation,
4. validation and merge-gate enforcement.

### Trade-off: more telemetry plumbing vs. real trustworthiness

RFC-0087 adds work in multiple repositories and in platform automation.

That cost is justified because without it Lotus remains declaration-rich but operationally weaker
than the claims implied by a mesh posture.

## Why This Is The Next Highest-Value RFC

This RFC is one of the highest-value next steps because it answers the hardest commercial question:

"How do you know this result is trustworthy right now?"

Without RFC-0087:

1. declarations can say what should be true,
2. gateway can publish what it believes is true,
3. but Lotus still cannot consistently prove what is true at runtime.

With RFC-0087:

1. trust posture becomes runtime-backed,
2. partial and stale states become explainable,
3. gateway and workbench can expose truth without guesswork,
4. the mesh claim becomes materially more defensible.

## Gap Assessment

### Closed gap 1: Live trust telemetry contracts

The platform now owns the standard contract for product-emitted freshness, completeness,
reconciliation, evidence, and blocked-state telemetry.

### Closed gap 2: Platform certification logic

The platform now turns validated telemetry into governed certified trust states through
`automation/generate_live_trust_certification.py`.

### Remaining gap 3: Durable trust artifacts

Gateway and discovery surfaces do not yet have one consistent platform-certified artifact family to
consume.

### Partially closed gap 4: Cross-repo emission discipline

The first-wave producer repos now carry governed telemetry snapshots and local tests. Consumer-side
or gateway-side telemetry emission remains future work.

## Deviations and Evolution Since Original RFC Direction

The broader program initially described live telemetry as one of several future mesh areas.

After reviewing the current implementation, the refined conclusion is:

1. this should be its own RFC,
2. it should sit after repo-native ownership is established,
3. it should feed both gateway publication and future discovery/catalog work.

## Proposed Changes

### Decision

Lotus will implement a platform-owned live trust telemetry and certification plane for governed
domain products and published gateway contract families.

Specifically:

1. participating repos will emit governed trust telemetry,
2. `lotus-platform` will certify runtime trust state from that telemetry,
3. gateway will consume certified trust artifacts rather than relying only on route-local logic,
4. workbench and future ecosystem APIs will surface those certified states truthfully.

### Governance invariants

1. telemetry emission contracts remain platform-governed,
2. certification logic remains platform-owned,
3. no repo may invent incompatible runtime trust state semantics,
4. published trust posture should prefer certified runtime truth over undeclared route-local
   heuristics where certification is available,
5. the final two slices remain mandatory quality gates.

### Target operating model

#### 1. Repo-level telemetry emission

Producer and consumer repos emit product-level trust telemetry.

#### 2. Platform trust certification plane

`lotus-platform` validates telemetry and generates certified trust artifacts.

#### 3. Gateway trust publication plane

`lotus-gateway` consumes certified trust posture for published contracts.

#### 4. Product experience trust plane

`lotus-workbench` and future consumers present runtime-backed trust posture.

### Platform capability model

#### A. Trust telemetry contract family

Recommended additions:

1. `platform-contracts/trust-telemetry/*.schema.json`
2. `automation/validate_trust_telemetry.py`

Implementation evidence now includes:

1. `platform-contracts/trust-telemetry/trust-telemetry-snapshot.schema.json`
   Defines the first governed RFC-0087 runtime trust snapshot shape.
2. `platform-contracts/trust-telemetry/README.md`
   Documents the distinction between declared product trust metadata and runtime telemetry.
3. `automation/validate_trust_telemetry.py`
   Validates snapshots against the generated domain-product catalog and governed trust vocabulary.
4. `tests/unit/test_trust_telemetry_contracts.py`
   Covers valid telemetry, unknown products, ungoverned trust states, unsupported validation lanes,
   undeclared observed metadata, and blocked snapshots without reasons.
5. `automation/generate_live_trust_certification.py`
   Generates deterministic live trust certification artifacts from validated telemetry snapshots.
6. `tests/unit/test_live_trust_certification.py`
   Covers certified snapshots, stale/blocked/invalid snapshots, and generated JSON/Markdown live
   certification reports.

Telemetry should cover at least:

1. freshness evaluation,
2. completeness posture,
3. reconciliation posture,
4. lineage materialization status,
5. blocked-state or degraded-state reasons,
6. certification timestamp and source evidence.

#### B. Trust certification artifact family

Recommended additions:

1. `platform-artifacts/trust-certification/*.json`
2. platform-generated markdown summaries for operator review

#### C. Gateway integration model

Gateway route families covered by RFC-0085 should consume certified trust artifacts where available
instead of relying only on route-local derived logic.

## Test and Validation Evidence

Reviewed evidence includes:

1. `platform-contracts/domain-vocabulary/domain-data-product-trust-metadata.v1.json`
2. `platform-contracts/trust-telemetry/trust-telemetry-snapshot.schema.json`
3. `automation/validate_trust_telemetry.py`
4. `automation/generate_live_trust_certification.py`
5. `tests/unit/test_trust_telemetry_contracts.py`
6. `tests/unit/test_live_trust_certification.py`
7. `<workspace-root>/lotus-core/contracts/trust-telemetry/portfolio-state-snapshot.telemetry.v1.json`
8. `<workspace-root>/lotus-performance/contracts/trust-telemetry/returns-series-bundle.telemetry.v1.json`
9. `<workspace-root>/lotus-risk/contracts/trust-telemetry/risk-metrics-report.telemetry.v1.json`
10. `<workspace-root>/lotus-advise/contracts/trust-telemetry/advisory-proposal-lifecycle-record.telemetry.v1.json`
11. `<workspace-root>/lotus-gateway/src/app/services/platform_capabilities_service.py`
12. `<workspace-root>/lotus-gateway/src/app/services/performance_workspace_service.py`
13. `<workspace-root>/lotus-gateway/src/app/services/risk_workspace_service.py`
14. `docs/standards/Platform Observability Standards.md`
15. `rfcs/RFC-0079-gateway-evidence-and-lineage-contract.md`

Current cross-repo proof:

1. `lotus-core` PR #319 merged with green Feature Lane and PR Merge Gate; local proof included
   `make test` with 1843 passing tests,
2. `lotus-performance` PR #130 merged with green Feature Lane and PR Merge Gate; local proof
   included `make check` with 1145 passing unit tests,
3. `lotus-risk` PR #98 merged with green Feature Lane and PR Merge Gate; local proof included
   `make check` with 285 passing unit tests,
4. `lotus-advise` PR #100 merged with green Feature Lane and PR Merge Gate; local proof included
   `make check` with 553 passing unit tests,
5. platform validation accepted each producer telemetry directory with
   `automation/validate_trust_telemetry.py`,
6. combined platform live-trust generation over the four snapshots produced
   `certification_state: certified`, 4 certified snapshots, 0 attention-required snapshots, and 0
   issues.

## Implementation Evidence

Implementation PRs and commits:

1. platform PR #145 added the trust telemetry schema and validator,
2. platform PR #146 added deterministic live trust certification generation,
3. platform PR #147 closed RFC-0086 repo-native rollout evidence, which RFC-0087 consumes,
4. `lotus-core` PR #319 added the `PortfolioStateSnapshot` telemetry snapshot and repo-local test,
5. `lotus-performance` PR #130 added the `ReturnsSeriesBundle` telemetry snapshot and repo-local
   test,
6. `lotus-risk` PR #98 added the `RiskMetricsReport` telemetry snapshot and repo-local test,
7. `lotus-advise` PR #100 added the `AdvisoryProposalLifecycleRecord` telemetry snapshot and
   repo-local test.
8. `lotus-gateway` commit `78ac98a` published the platform live trust certification artifact through
   a read-only gateway endpoint and tests.
9. `lotus-workbench` commit `30f5664` consumed that trust certification through the BFF-only
   self-serve discovery surface.
10. Gateway PR #136 and Workbench PR #97 merged on 2026-04-19 with green Feature Lane, PR Merge
    Gate, and auto-merge queue checks.

## Original Acceptance Criteria Alignment

| Original intent | RFC-0087 alignment |
| --- | --- |
| Add live telemetry and trust certification as a core mesh area | This RFC centers on runtime-backed trust emission and certification |
| Keep it implementation-bearing and high-value | The RFC focuses on emitted telemetry, platform certification, and gateway/workbench consumption |
| Preserve second-last and final closure slices | Slice 7 and Slice 8 are mandatory and explicit |

## Mandatory Slice Review Gate

Every completed slice must receive a review pass before the next slice begins.

That review must check:

1. whether telemetry is truthful rather than decorative,
2. whether route-local trust logic can be simplified or removed,
3. whether certification artifacts are stronger than prior ad hoc evidence,
4. whether any repeated lesson should become durable context or skill guidance,
5. whether the slice left the changed repos cleaner and more maintainable than before.

## Rollout and Backward Compatibility

### Slice 0: Audit current trust signals and telemetry gaps

1. inventory existing trust and evidence signals across the first-wave repos,
2. classify which are declarative only versus runtime-backed,
3. identify first-wave certification targets.

Exit gate:

1. the first-wave certification targets are explicit,
2. current trust signals are classified truthfully rather than optimistically.

### Slice 1: Platform trust telemetry schema and validator

1. add trust telemetry schemas,
2. add validation automation,
3. add contract tests for telemetry semantics.

Exit gate:

1. telemetry contracts are machine-validated,
2. semantics are consistent with the governed trust vocabulary.

### Slice 2: First-wave repo telemetry emission

1. add telemetry emission in the first-wave producer and consumer repos,
2. align emitted signals to governed trust vocabulary.

Exit gate:

1. participating repos emit governed telemetry rather than repo-specific ad hoc status payloads,
2. emission is test-backed in the participating repos.

Status: complete for first-wave producer telemetry snapshots. Consumer and gateway telemetry
emission remains outside this completed slice and should be handled only when there is a concrete
consumer trust signal to certify.

### Slice 3: Platform trust certification engine

1. implement certification rules,
2. generate trust certification artifacts.

Exit gate:

1. certification artifacts are generated from governed telemetry,
2. certification logic is deterministic and test-backed.

### Slice 4: Gateway certified trust consumption

1. update first-wave gateway route families to consume certified trust artifacts,
2. retire conflicting route-local trust heuristics where certification exists.

Exit gate:

1. covered route families prefer certified trust posture,
2. conflicting route-local trust handling is removed or consciously justified.

### Slice 5: Workbench runtime trust adoption

1. update workbench surfaces to prefer certified trust posture,
2. add tests for runtime current/partial/stale/blocked states.

Exit gate:

1. covered workbench surfaces render runtime-backed trust states truthfully,
2. tests prove the important degraded-state paths.

### Slice 6: Certification lane integration

1. add platform validation and merge-gate checks for trust telemetry and certification,
2. make trust certification drift CI-visible.

Exit gate:

1. trust certification drift is visible in platform validation,
2. lane behavior is truthful about what is enforced versus what is only reported.

Status: partially complete. Platform has explicit validator and generator commands, and producer
repos have local tests. A mandatory cross-repo platform merge gate for producer telemetry
directories remains a follow-up because it depends on stable checkout orchestration across the
participating repositories.

### Slice 7: Code Review, API Certification, and Governance Tightening

This slice is mandatory.

1. review telemetry emission, certification logic, and gateway/workbench trust handling for loose
   ends and duplicate logic,
2. confirm API publication and trust certification follow the certification pattern,
3. tighten platform governance and remove stale shortcuts where safe,
4. remove or retire route-local trust logic, stale evidence branches, and temporary certification
   shortcuts where the new plane is already authoritative.

Exit gate:

1. no completed first-wave route family is left with avoidable duplicate trust logic,
2. API certification and platform governance expectations are satisfied across the wave.

### Slice 8: Documentation, Agent Context, Wiki Update, Skills Review, and Branch Hygiene

This slice is mandatory.

1. update docs and context for the live trust certification plane,
2. update wiki and operator-facing discovery of certification artifacts,
3. consciously assess whether skills or routing guidance should change for telemetry and trust
   certification work,
4. identify documentation or context that should be added to improve future telemetry and
   certification work,
5. identify documentation or context that should be removed because it would become stale or
   misleading after rollout,
6. complete branch hygiene truthfully.

Exit gate:

1. any keep, tighten, add, remove, or no-change decisions for skills and context are explicit,
2. future agents can discover the trust certification plane quickly,
3. no branch or context debt is left behind.

## Validation and Evidence Model

Required proof for implementation under this RFC:

1. schema and validator tests,
2. repo-level telemetry emission tests,
3. platform certification tests,
4. gateway contract and integration tests,
5. workbench unit and browser tests for certified trust posture.

## Skills and Guidance Assessment for Future Work

### Improvements likely needed once implementation starts

1. routing guidance may need a clearer path for trust-certification work spanning platform, gateway,
   and product repos,
2. context reference maps may need direct links to certification artifacts and validation commands,
3. a dedicated telemetry/certification skill may be justified if this becomes recurring cross-repo
   work.

### Conscious closure decisions for skills, documentation, and context

1. no new telemetry-specific skill is added yet because the current work is still covered by Lotus
   backend governance plus repo-local tests and platform validators,
2. context and repository-local engineering context are updated as durable artifact paths, gateway
   trust API paths, and Workbench consumption paths exist,
3. no existing docs are removed because route-local trust logic still exists in non-discovery route
   families and must be retired route-family-by-route-family,
4. the next guidance improvement should be a platform merge-gate playbook only after cross-repo
   telemetry checkout orchestration is stable.

That posture is intentional rather than accidental.

## Risks and Mitigations

### Risk: Telemetry is noisy but not trustworthy

Mitigation:

1. keep telemetry contracts narrow and governed,
2. certify from platform logic rather than trusting raw emission blindly.

### Risk: Gateway keeps duplicate route-local trust logic forever

Mitigation:

1. explicitly retire conflicting logic in Slice 4 and Slice 7,
2. make certification the stronger truth source where available.

## Acceptance Criteria

This RFC is complete for the first-wave live trust certification plane when:

1. governed live trust telemetry exists for the first wave,
2. `lotus-platform` produces certified trust artifacts from runtime telemetry,
3. gateway consumes certified trust posture for covered discovery/trust route families,
4. workbench discovery surfaces render runtime-backed trust states,
5. duplicate route-local trust logic is removed or explicitly justified where certification is now
   authoritative,
6. Slice 7 and Slice 8 are completed as mandatory quality and closure gates.

## Non-Goals

This RFC does not:

1. replace repo-native onboarding work from RFC-0086,
2. replace gateway publication work from RFC-0085,
3. implement the self-serve discovery catalog,
4. define every future observability metric in the ecosystem.

## Open Questions

1. Resolved for this wave: first-wave telemetry starts with producer repos only. Gateway telemetry
   should be added only when gateway owns a concrete certified-consumption signal.
2. Resolved for this wave: repo-local telemetry snapshots live in producer
   `contracts/trust-telemetry/` directories; platform certification artifacts remain generated
   outputs.
3. Open for future hardening: which trust states become blocking in CI versus informational now that
   gateway and Workbench consume certified trust posture.

## Next Actions

1. decide whether the cross-repo producer telemetry certification should become a platform merge
   gate or remain a documented operator check for the next implementation wave.
