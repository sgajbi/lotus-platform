# RFC-0087 - Live Trust Telemetry and Certification Plane

| Field | Value |
| --- | --- |
| Status | Draft |
| Created | 2026-04-19 |
| Last Updated | 2026-04-19 |
| Owners | lotus-platform architecture; domain repository maintainers; lotus-gateway maintainers |
| Depends On | RFC-0071; RFC-0072; RFC-0079; RFC-0084; RFC-0085; RFC-0086 |
| Related Standards | `RFC-0071-centralized-environment-scoped-service-addressing-and-ingress-governance.md`; `RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`; `RFC-0079-gateway-evidence-and-lineage-contract.md`; `RFC-0084-mesh-governance.md`; `RFC-0085-gateway-governed-domain-product-publication-and-trust-contracts.md`; `RFC-0086-repo-native-domain-product-onboarding-and-federated-rollout.md`; `Platform Observability Standards.md` |
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

Overall classification: `Partially implemented (requires enhancement)`

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

1. `C:/Users/Sandeep/projects/lotus-gateway/src/app/services/platform_capabilities_service.py`
2. `C:/Users/Sandeep/projects/lotus-gateway/src/app/services/performance_workspace_service.py`
3. `C:/Users/Sandeep/projects/lotus-gateway/src/app/services/risk_workspace_service.py`
4. `C:/Users/Sandeep/projects/lotus-gateway/tests/integration/test_workbench_router.py`

Assessment:

Gateway knows how to expose trust posture, but current behavior is still largely route-shaped rather
than backed by a shared live trust telemetry plane.

#### 3. Lotus already has observability and evidence patterns

Evidence:

1. `Platform Observability Standards.md`
2. `rfcs/RFC-0079-gateway-evidence-and-lineage-contract.md`
3. `rfcs/RFC-0081-slice-11-performance-accessibility-and-operability-hardening-evidence.md`

Assessment:

There is enough existing posture around observability, evidence, and lineage to justify a stronger
platform-owned live trust plane rather than inventing an entirely new model.

### What is only partially implemented

1. freshness and supportability are partially exposed but not consistently runtime-certified,
2. lineage and evidence exist in strong pockets but not as one live product-certification model,
3. trust posture is available in some gateway contracts but not yet derived from a shared telemetry
   source,
4. platform validation does not yet issue durable trust certification from live signals.

### What is not yet implemented

1. no common live trust telemetry contract family across repositories,
2. no platform certification rule that converts raw telemetry into governed trust states,
3. no durable trust-certification artifact family that gateway can consume consistently,
4. no cross-repo requirement that governed products emit live freshness, completeness, lineage, and
   blocked-state signals in a standardized way.

## Requirement-to-Implementation Traceability

| Requirement | Current evidence | Current status | RFC-0087 response |
| --- | --- | --- | --- |
| Move from declared trust to operational truth | Trust vocabularies and route-level supportability exist, but live shared telemetry does not | Partially satisfied | Add governed telemetry contracts, certification rules, and trust artifacts |
| Make trust posture customer-credible | Gateway and workbench can show some trust posture today | Partially satisfied | Back those states with runtime evidence and certification instead of only declared policy |
| Keep the work implementation-bearing | Observability and evidence patterns exist already | Partially satisfied | Define product-emitted telemetry, platform certification, and gateway consumption slices |
| Preserve second-last and final closure slices | User requested this quality posture consistently | Not yet satisfied before this pass | RFC includes mandatory Slice 7 and Slice 8 plus review gates |

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

### Gap 1: Live trust telemetry contracts

There is no standard contract yet for product-emitted freshness, completeness, reconciliation,
evidence, and blocked-state telemetry.

### Gap 2: Platform certification logic

The platform does not yet turn trust telemetry into governed certified trust states.

### Gap 3: Durable trust artifacts

Gateway and discovery surfaces do not yet have one consistent platform-certified artifact family to
consume.

### Gap 4: Cross-repo emission discipline

Producer and consumer repos are not yet required to emit governed live trust telemetry for their
products and dependencies.

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
2. `C:/Users/Sandeep/projects/lotus-gateway/src/app/services/platform_capabilities_service.py`
3. `C:/Users/Sandeep/projects/lotus-gateway/src/app/services/performance_workspace_service.py`
4. `C:/Users/Sandeep/projects/lotus-gateway/src/app/services/risk_workspace_service.py`
5. `Platform Observability Standards.md`
6. `rfcs/RFC-0079-gateway-evidence-and-lineage-contract.md`

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

### Conscious no-change decisions at RFC draft stage

1. no skills are changed in this draft-only pass,
2. no context files are changed until durable artifact paths and commands exist,
3. no existing docs are removed until runtime certification is implemented.

That no-change posture at the draft stage is intentional rather than accidental.

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

This RFC is complete only when:

1. governed live trust telemetry exists for the first wave,
2. `lotus-platform` produces certified trust artifacts from runtime telemetry,
3. gateway consumes certified trust posture for covered route families,
4. workbench surfaces covered by the first wave render runtime-backed trust states,
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

1. Which first-wave repos should emit telemetry first: producers only, or producers plus gateway?
2. Should trust certification artifacts be persisted only in platform automation outputs or also in
   repo-local evidence directories?
3. Which trust states must be blocking in CI versus informational at first rollout?

## Next Actions

1. refine the trust telemetry schema family and artifact locations,
2. identify the first-wave certification targets,
3. prepare implementation prompts for the participating repos and gateway.
