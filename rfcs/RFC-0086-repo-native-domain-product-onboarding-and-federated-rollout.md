# RFC-0086 - Repo-Native Domain Product Onboarding and Federated Rollout

| Field | Value |
| --- | --- |
| Status | Draft |
| Created | 2026-04-19 |
| Last Updated | 2026-04-19 |
| Owners | lotus-platform architecture; domain repository maintainers |
| Depends On | RFC-0072; RFC-0073; RFC-0082; RFC-0084 |
| Related Standards | `RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`; `RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md`; `RFC-0082-lotus-core-domain-authority-and-analytics-serving-boundary-hardening.md`; `RFC-0084-mesh-governance.md`; `C:/Users/Sandeep/projects/lotus-core/REPOSITORY-ENGINEERING-CONTEXT.md`; `C:/Users/Sandeep/projects/lotus-performance/REPOSITORY-ENGINEERING-CONTEXT.md`; `C:/Users/Sandeep/projects/lotus-risk/REPOSITORY-ENGINEERING-CONTEXT.md`; `C:/Users/Sandeep/projects/lotus-manage/REPOSITORY-ENGINEERING-CONTEXT.md`; `C:/Users/Sandeep/projects/lotus-advise/REPOSITORY-ENGINEERING-CONTEXT.md`; `C:/Users/Sandeep/projects/lotus-report/REPOSITORY-ENGINEERING-CONTEXT.md`; `C:/Users/Sandeep/projects/lotus-ai/REPOSITORY-ENGINEERING-CONTEXT.md` |
| Scope | Cross-repo |

## Executive Summary

RFC-0084 created a platform-owned control plane for governed domain products.

That was the right first step, but the current declarations still live in `lotus-platform`. That is
good enough to prove the model and validate first-wave producer and consumer posture. It is not yet
good enough to claim federated ownership at the operating-model level.

The next step is to move from platform-curated declarations to repo-native declarations owned by the
repositories that actually produce and consume the products.

This RFC defines that rollout.

The target state is:

1. every authoritative producer repository owns its own product declarations,
2. every consumer repository owns its own dependency declarations,
3. `lotus-platform` validates, aggregates, and certifies those declarations centrally,
4. onboarding new products becomes template-driven and repeatable rather than manually curated in one
   platform repo,
5. broader domain rollout extends beyond `lotus-core`, `lotus-performance`, and `lotus-risk` to
   include `lotus-manage`, `lotus-advise`, `lotus-report`, and `lotus-ai`.

This is the RFC that turns RFC-0084 from a strong governance proof into a genuinely federated
operating model.

## Original Requested Requirements (Preserved)

The user intent preserved in this RFC is:

1. move beyond a platform-only proof and toward a more credible mesh operating model,
2. cover repo-native onboarding, broader domain rollout, and the foundations needed for future
   self-serve scaling,
3. make the work implementation-bearing and parallelizable across repositories,
4. avoid central curation becoming a long-term bottleneck,
5. keep the same Lotus RFC quality bar with mandatory second-last and final closure slices,
6. consciously assess whether context, documentation, or skills should change to support future
   multi-repo rollout work.

## Current Implementation Reality

Overall classification: `Partially implemented (requires enhancement)`

### What is implemented well today

#### 1. Platform-owned product governance exists

Evidence:

1. `platform-contracts/domain-data-products.schema.json`
2. `platform-contracts/domain-data-product-consumers.schema.json`
3. `platform-contracts/domain-data-products/validate_domain_data_product_contracts.py`
4. `rfcs/RFC-0084-mesh-governance.md`

Assessment:

Lotus has a real control plane. The remaining problem is ownership locality and rollout breadth.

#### 2. First-wave declarations already prove the pattern

Evidence:

1. `platform-contracts/domain-data-products/lotus-core-products.v1.json`
2. `platform-contracts/domain-data-products/lotus-performance-products.v1.json`
3. `platform-contracts/domain-data-products/lotus-performance-consumers.v1.json`
4. `platform-contracts/domain-data-products/lotus-risk-products.v1.json`
5. `platform-contracts/domain-data-products/lotus-risk-consumers.v1.json`

Assessment:

The declaration model is not hypothetical. It already models real producers and consumers.

#### 3. Some repo-local evidence already exists outside the platform repo

Evidence:

1. `C:/Users/Sandeep/projects/lotus-core/docs/architecture/RFC-0082-contract-family-inventory.md`
2. `C:/Users/Sandeep/projects/lotus-performance/docs/technical/RFC-0082-upstream-contract-family-map.md`
3. `C:/Users/Sandeep/projects/lotus-risk/docs/domain-apis/RFC-0082-upstream-contract-family-map.md`
4. `C:/Users/Sandeep/projects/lotus-gateway/docs/standards/RFC-0082-upstream-contract-family-map.md`

Assessment:

There is already repo-local knowledge about product and dependency posture. RFC-0086 should turn
that into repo-native machine-readable declarations instead of keeping it mostly in docs or only in
`lotus-platform`.

### What is only partially implemented

1. product truth is federated conceptually but not yet in declaration ownership,
2. first-wave rollout covers only part of the ecosystem,
3. platform validation exists, but repo-native onboarding templates and local checks do not yet
   exist,
4. wider consumer declarations remain incomplete outside the current first wave.

### What is not yet implemented

1. no standard repo-native declaration location across the domain repos,
2. no platform-supported aggregation flow that discovers declarations from each repo as native
   source files,
3. no broader domain onboarding for `lotus-manage`, `lotus-advise`, `lotus-report`, and `lotus-ai`,
4. no standardized onboarding templates or repo-native validation entrypoints for declaration
   maintenance.

## Requirement-to-Implementation Traceability

| Requirement | Current evidence | Current status | RFC-0086 response |
| --- | --- | --- | --- |
| Move from platform-only proof to federated ownership | First-wave declarations exist only in `lotus-platform` | Partially satisfied | Move declarations into owning repos and make platform the validator and aggregator |
| Broaden rollout beyond the first wave | Current first wave covers `lotus-core`, `lotus-performance`, and `lotus-risk` | Not yet satisfied | Onboard `lotus-manage`, `lotus-advise`, `lotus-report`, and `lotus-ai` |
| Make onboarding repeatable rather than centrally handcrafted | Schemas and validator exist, but no repo-native template flow exists | Not yet satisfied | Add templates, repo-native layout guidance, and platform aggregation rules |
| Keep work parallelizable across repos | Current model is technically cross-repo but not yet structured for independent repo implementation | Partially satisfied | Define per-repo rollout slices and shared validator expectations |
| Preserve strong closure discipline | User requested same quality posture as RFC-0084 and RFC-0085 | Not yet satisfied before this pass | Include mandatory Slice 7 and Slice 8 plus a mandatory slice review gate |

## Design Reasoning and Trade-offs

The key design choice is to make declaration content repo-native while keeping validation and
discovery platform-native.

That split matters.

### Why declarations should become repo-native

Repo-native declarations:

1. align ownership with the repository that actually produces or consumes the product,
2. reduce the risk that `lotus-platform` becomes a manual metadata bottleneck,
3. make declaration updates move with the code and tests they describe,
4. enable broader rollout using parallel repo work without central file contention.

### Why aggregation and validation should stay platform-native

If every repo invents its own rules, Lotus loses the very governance value RFC-0084 created.

`lotus-platform` should remain the owner of:

1. schemas,
2. semantic registries,
3. trust registries,
4. aggregation and validation automation,
5. certification and discovery artifacts.

### Trade-off: more repo changes now vs. stronger long-term federation

RFC-0086 requires touching many repositories.

That is more implementation work in the short term, but it prevents:

1. long-term central curation debt,
2. product declarations drifting from the code that owns them,
3. future product onboarding becoming a platform team bottleneck.

## Gap Assessment

### Gap 1: Repo-native declaration ownership

Current declarations are validated, but they are not yet owned where the code lives.

### Gap 2: Standardized declaration layout in each repo

There is no single governed pattern yet for where producer and consumer declarations should live in
each repository.

### Gap 3: Broader producer and consumer rollout

The estate still lacks repo-native onboarding for the broader domain and shared-capability wave.

### Gap 4: Repo-native validation entrypoints

Teams do not yet have a standard local command or CI hook that proves their declarations are valid
before platform aggregation runs.

### Gap 5: Aggregated discovery and certification inputs

Platform validation still assumes the platform repo is the main declaration source instead of
aggregating from multiple owning repositories.

## Deviations and Evolution Since Original RFC Direction

RFC-0084 proved the declaration model in `lotus-platform` first. That was the right sequencing.

This RFC deliberately evolves that model instead of treating the platform-owned files as the final
state.

The refined position is:

1. platform-owned schemas and validators remain durable,
2. platform-owned declaration content is transitional except for platform-owned product families,
3. long-term federation requires repo-native content ownership.

## Proposed Changes

### Decision

Lotus will move governed domain product declarations from a platform-curated first-wave model to a
repo-native ownership model with platform-owned aggregation and validation.

Specifically:

1. each producer repo will own its own producer declarations,
2. each consumer repo will own its own consumer declarations,
3. `lotus-platform` will validate and aggregate those declarations centrally,
4. broader domain rollout will onboard the remaining core Lotus repositories,
5. onboarding patterns will be template-driven and repo-native.

### Governance invariants

1. declaration content belongs with the repo that owns the product or dependency,
2. schemas, semantics, trust registries, and validators remain platform-owned,
3. no repo may fork its own incompatible declaration schema,
4. no broader rollout slice is complete without repo-native tests or validation entrypoints,
5. the final two slices remain mandatory quality gates.

### Target operating model

#### 1. Producer-owned declarations

Each authoritative producer repo owns machine-readable declarations for the products it publishes.

#### 2. Consumer-owned dependency declarations

Each consuming repo owns machine-readable declarations for the upstream governed products it depends
on.

#### 3. Platform-owned federation layer

`lotus-platform` discovers, validates, aggregates, and certifies declarations from all participating
repositories.

#### 4. Discovery and telemetry preparation layer

The output of this RFC becomes the durable foundation for later discovery-catalog and live
telemetry RFCs.

### Repository implications

#### `lotus-core`

1. move or mirror current first-wave producer declarations into repo-native governed locations,
2. wire repo-native validation into local and CI checks.

#### `lotus-performance`

1. own producer and consumer declarations in-repo,
2. keep upstream dependency posture explicit and validator-backed.

#### `lotus-risk`

1. own producer and consumer declarations in-repo,
2. keep analytics dependency posture explicit and test-backed.

#### `lotus-manage`

1. identify authoritative workflow and operational-state products,
2. add first repo-native producer and consumer declarations.

#### `lotus-advise`

1. identify authoritative recommendation and advisory workflow products,
2. add repo-native declarations for stable governed products and dependencies.

#### `lotus-report`

1. identify governed reporting and evidence products,
2. declare upstream product dependencies explicitly.

#### `lotus-ai`

1. classify stable AI runtime or evaluation products,
2. declare upstream dependencies and trust requirements for governed AI-backed products.

#### `lotus-platform`

1. own aggregation rules and validation automation,
2. own templates and onboarding documentation,
3. generate ecosystem-level certification inputs from the repo-native declarations.

## Test and Validation Evidence

This RFC is grounded in current implementation evidence.

Reviewed evidence includes:

1. `platform-contracts/domain-data-products/validate_domain_data_product_contracts.py`
2. `platform-contracts/domain-data-products/lotus-core-products.v1.json`
3. `platform-contracts/domain-data-products/lotus-performance-products.v1.json`
4. `platform-contracts/domain-data-products/lotus-performance-consumers.v1.json`
5. `platform-contracts/domain-data-products/lotus-risk-products.v1.json`
6. `platform-contracts/domain-data-products/lotus-risk-consumers.v1.json`
7. `C:/Users/Sandeep/projects/lotus-core/docs/architecture/RFC-0082-contract-family-inventory.md`
8. `C:/Users/Sandeep/projects/lotus-performance/docs/technical/RFC-0082-upstream-contract-family-map.md`
9. `C:/Users/Sandeep/projects/lotus-risk/docs/domain-apis/RFC-0082-upstream-contract-family-map.md`

## Original Acceptance Criteria Alignment

| Original intent | RFC-0086 alignment |
| --- | --- |
| Push toward a more credible mesh operating model | Repo-native declarations make ownership federated rather than centrally curated |
| Make rollout parallelizable | Per-repo onboarding slices allow independent implementation once the standard is fixed |
| Avoid central bottleneck | Platform validates and aggregates, but repos own declaration content |
| Preserve strong closure discipline | Slice 7 and Slice 8 are mandatory and explicit |

## Mandatory Slice Review Gate

Every completed slice must receive a review pass before the next slice begins.

That review must check:

1. whether declaration ownership is now in the right repository,
2. whether duplicated metadata or stale platform-curated copies can be removed,
3. whether repo-native validation commands and tests are strong enough,
4. whether any repeated onboarding lesson should become durable guidance.

## Rollout and Backward Compatibility

### Slice 0: Audit baseline and repo ownership map

1. classify current platform-owned declarations into long-term repo owners,
2. identify which declarations remain platform-owned versus transitional,
3. map the next rollout wave repository by repository.

### Slice 1: Repo-native layout standard and templates

1. define governed in-repo declaration locations,
2. add templates and onboarding guidance,
3. add aggregation rules that can discover repo-native files.

### Slice 2: First-wave declaration migration

1. move or mirror `lotus-core`, `lotus-performance`, and `lotus-risk` declarations into their
   owning repos,
2. keep platform validation aligned during the transition.

### Slice 3: Broader domain rollout

1. onboard `lotus-manage`,
2. onboard `lotus-advise`,
3. onboard `lotus-report`,
4. onboard `lotus-ai`.

### Slice 4: Repo-native validation and CI alignment

1. add local validation entrypoints in the owning repos,
2. align repo-native CI and platform aggregation checks.

### Slice 5: Aggregation and certification hardening

1. update platform automation to aggregate repo-native declarations,
2. generate consistent certification inputs from the federated declaration set.

### Slice 6: Discovery and onboarding-readiness preparation

1. make the federated declaration set ready for later catalog and telemetry RFCs,
2. harden ownership, lifecycle, and consumer-approval posture across the broader rollout wave.

### Slice 7: Code Review, Governance Tightening, and Loose-End Closure

This slice is mandatory.

1. review each participating repo for declaration duplication, stale transitional copies, and weak
   validation paths,
2. tighten platform aggregation, validation, and rollout rules,
3. confirm the broader rollout follows the certification pattern and platform governance.

### Slice 8: Documentation, Agent Context, Wiki Update, Skills Review, and Branch Hygiene

This slice is mandatory.

1. update platform and repo docs for repo-native declaration ownership,
2. update context and reference maps where durable paths changed,
3. consciously assess whether skills or onboarding guidance should change for future repo rollout
   work,
4. close branch and PR hygiene truthfully.

## Validation and Evidence Model

Required proof for implementation under this RFC:

1. platform validator tests for repo-native discovery and aggregation,
2. repo-native validation commands or tests in the participating repos,
3. cross-repo proof that aggregated declarations still validate centrally,
4. truthful migration evidence that stale transitional copies are either removed or consciously
   retained temporarily.

## Skills and Guidance Assessment for Future Work

### Improvements likely needed once implementation starts

1. `LOTUS-SKILL-ROUTING-MAP.md` may need a clearer route for multi-repo declaration rollout work,
2. `CONTEXT-REFERENCE-MAP.md` may need direct links to repo-native declaration locations and
   aggregation automation,
3. a dedicated skill may eventually be justified for repo-native product onboarding if this becomes
   a repeated program across the ecosystem.

### Conscious no-change decisions at RFC draft stage

1. no skills are changed in this draft-only pass,
2. no context files are changed until durable repo-native paths are implemented,
3. no existing docs are removed until migration is complete and platform aggregation is stable.

## Risks and Mitigations

### Risk: Federation creates schema drift

Mitigation:

1. keep schemas platform-owned,
2. fail CI on incompatible declaration structure.

### Risk: Repo rollout becomes noisy and inconsistent

Mitigation:

1. use templates,
2. use repo-native validation commands,
3. review each slice before starting the next.

### Risk: Transitional copies become permanent duplicates

Mitigation:

1. classify transitional copies explicitly,
2. remove them in Slice 7 where safe,
3. keep migration evidence truthful.

## Acceptance Criteria

This RFC is complete only when:

1. the participating repos own their own product or consumer declaration content,
2. `lotus-platform` aggregates and validates those declarations centrally,
3. the broader rollout wave includes `lotus-manage`, `lotus-advise`, `lotus-report`, and
   `lotus-ai`,
4. repo-native validation paths exist for the participating repositories,
5. Slice 7 and Slice 8 are completed as mandatory quality and closure gates.

## Open Questions

1. Should repo-native declarations be moved fully, or mirrored temporarily during migration?
2. Which repos should be allowed to declare internal-only products versus only stable governed
   products?
3. Should the gateway repo own any repo-native consumer declarations in this RFC, or should that
   remain coupled to RFC-0085 implementation?

## Next Actions

1. refine this RFC with the exact repo-native file layout standard,
2. define the aggregation path and migration posture for the current first-wave declarations,
3. prepare per-repo implementation prompts once the rollout slices are approved.
