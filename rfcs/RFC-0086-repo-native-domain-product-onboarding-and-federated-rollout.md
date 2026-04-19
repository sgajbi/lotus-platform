# RFC-0086 - Repo-Native Domain Product Onboarding and Federated Rollout

| Field | Value |
| --- | --- |
| Status | Implemented |
| Created | 2026-04-19 |
| Last Updated | 2026-04-19 |
| Owners | lotus-platform architecture; domain repository maintainers |
| Depends On | RFC-0072; RFC-0073; RFC-0082; RFC-0084 |
| Related Standards | `RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`; `RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md`; `RFC-0082-lotus-core-domain-authority-and-analytics-serving-boundary-hardening.md`; `RFC-0084-mesh-governance.md`; `C:/Users/Sandeep/projects/lotus-core/REPOSITORY-ENGINEERING-CONTEXT.md`; `C:/Users/Sandeep/projects/lotus-performance/REPOSITORY-ENGINEERING-CONTEXT.md`; `C:/Users/Sandeep/projects/lotus-risk/REPOSITORY-ENGINEERING-CONTEXT.md`; `C:/Users/Sandeep/projects/lotus-manage/REPOSITORY-ENGINEERING-CONTEXT.md`; `C:/Users/Sandeep/projects/lotus-advise/REPOSITORY-ENGINEERING-CONTEXT.md`; `C:/Users/Sandeep/projects/lotus-report/REPOSITORY-ENGINEERING-CONTEXT.md`; `C:/Users/Sandeep/projects/lotus-ai/REPOSITORY-ENGINEERING-CONTEXT.md` |
| Scope | Cross-repo |

## Executive Summary

RFC-0084 created a platform-owned control plane for governed domain products.

That was the right first step, but the current declarations still live in `lotus-platform`. That is
good enough to prove the model and validate first-wave producer and consumer posture. Before
RFC-0086 implementation, it was not good enough to claim federated ownership at the
operating-model level.

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
   include `lotus-manage`, `lotus-advise`, and `lotus-report`, with `lotus-ai` explicitly held out
   of the first-wave producer or consumer declaration set until it owns a governed domain product or
   catalog-consuming capability.

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

Overall classification: `Implemented`

### What is implemented well today

#### 1. Platform-owned product governance exists

Evidence:

1. `platform-contracts/domain-data-products.schema.json`
2. `platform-contracts/domain-data-product-consumers.schema.json`
3. `platform-contracts/domain-data-products/validate_domain_data_product_contracts.py`
4. `rfcs/RFC-0084-mesh-governance.md`

Assessment:

Lotus has a real control plane. The remaining problem is ownership locality and rollout breadth.

#### 2. Repo-native declarations now prove the pattern

Evidence:

1. `lotus-core/contracts/domain-data-products/lotus-core-products.v1.json`
2. `lotus-performance/contracts/domain-data-products/lotus-performance-products.v1.json`
3. `lotus-performance/contracts/domain-data-products/lotus-performance-consumers.v1.json`
4. `lotus-risk/contracts/domain-data-products/lotus-risk-products.v1.json`
5. `lotus-risk/contracts/domain-data-products/lotus-risk-consumers.v1.json`
6. `lotus-advise/contracts/domain-data-products/lotus-advise-products.v1.json`
7. `lotus-advise/contracts/domain-data-products/lotus-advise-consumers.v1.json`
8. `lotus-report/contracts/domain-data-products/lotus-report-consumers.v1.json`
9. `lotus-manage/contracts/domain-data-products/lotus-manage-consumers.v1.json`

Assessment:

The declaration model is not hypothetical. It now models real producers and consumers in the
owning repositories for the current rollout wave.

#### 3. Some repo-local evidence already exists outside the platform repo

Evidence:

1. `lotus-core/docs/architecture/RFC-0082-contract-family-inventory.md`
2. `lotus-performance/docs/technical/RFC-0082-upstream-contract-family-map.md`
3. `lotus-risk/docs/domain-apis/RFC-0082-upstream-contract-family-map.md`
4. `lotus-gateway/docs/standards/RFC-0082-upstream-contract-family-map.md`

Assessment:

There is already repo-local knowledge about product and dependency posture. RFC-0086 should turn
that into repo-native machine-readable declarations instead of keeping it mostly in docs or only in
`lotus-platform`.

### What is now implemented in platform aggregation

1. the standard repo-native declaration location is `contracts/domain-data-products`,
2. `platform-contracts/domain-data-products/domain-product-source-manifest.v1.json` records included
   repo-native sources,
3. `automation/generate_domain_product_discovery.py` loads included declarations from sibling
   repositories and validates them as one federated source set before writing generated artifacts,
4. `generated/domain-product-catalog.json`, `generated/domain-product-dependency-graph.json`, and
   `generated/domain-product-certification-report.json` are generated from the federated set,
5. `lotus-manage`, `lotus-advise`, and `lotus-report` are included in the current generated catalog
   and certification report.

### Closure posture

1. `lotus-ai` is not a first-wave RFC-0086 producer or consumer declaration participant because it
   does not currently own a stable governed domain product or a repo-native
   `contracts/domain-data-products/` declaration set. AI-facing catalog explanation and guidance
   belongs in the RFC-0088 discovery and AI-consumer work, after gateway publication exposes the
   governed catalog and trust facts.
2. transitional platform mirror declarations are retained as compatibility evidence only. They are
   no longer authoritative for the included rollout wave because the source manifest has empty
   `platform_declaration_paths` for every included repository, and the active generated catalog must
   not use `platform-contracts/domain-data-products/` as a product or consumer source path.
3. Repo-native validation entrypoints are present in participating repositories, and platform
   aggregation/certification tests prove the federated declaration set remains centrally
   certifiable.

## Requirement-to-Implementation Traceability

| Requirement | Current evidence | Current status | RFC-0086 response |
| --- | --- | --- | --- |
| Move from platform-only proof to federated ownership | Repo-native declarations exist in the current rollout repositories and platform aggregation reads them | Satisfied | Keep platform as validator and aggregator |
| Broaden rollout beyond the first wave | Current generated catalog includes `lotus-core`, `lotus-performance`, `lotus-risk`, `lotus-advise`, `lotus-report`, and `lotus-manage`; `lotus-ai` has no first-wave domain-product declaration set | Satisfied | `lotus-ai` is consciously out of the RFC-0086 producer/consumer wave until an AI product or governed consumer capability exists |
| Make onboarding repeatable rather than centrally handcrafted | Source manifest plus federated generator now define the repeatable path | Satisfied | Keep future onboarding repo-native and validator-backed |
| Keep work parallelizable across repos | Each participating repo owns declarations under the same `contracts/domain-data-products/` path and the source manifest lets platform aggregate them independently | Satisfied | Keep per-repo declaration updates disjoint and validator-backed |
| Preserve strong closure discipline | User requested same quality posture as RFC-0084 and RFC-0085 | Satisfied for RFC-0086 | Slice 7 and Slice 8 closure evidence is recorded below and protected by `tests/unit/test_domain_product_rollout_closure.py` |

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

## Why This Is The Next Highest-Value RFC

This is the highest-value follow-on to RFC-0084 outside the gateway publication plane because it
solves the ownership problem that still prevents Lotus from behaving like a truly federated system.

If Lotus stopped at RFC-0084 and only added more platform-owned declaration files, it would have a
strong governance proof but still a weak federated operating model. The platform would know a lot,
but the owning repositories would not yet carry declaration truth as part of their normal delivery
contract.

RFC-0086 is the point where that changes. It gives Lotus:

1. ownership locality,
2. parallelizable repo rollout,
3. repeatable onboarding,
4. the right foundation for later discovery, telemetry, and federation claims.

## Gap Assessment

### Closed gap 1: Repo-native declaration ownership

Current rollout declarations are owned where the code lives for the participating repositories.

### Closed gap 2: Standardized declaration layout in each repo

The governed repo-native layout is `contracts/domain-data-products/`.

### Closed gap 3: Broader producer and consumer rollout

The broader first wave now includes `lotus-advise`, `lotus-report`, and `lotus-manage` alongside
`lotus-core`, `lotus-performance`, and `lotus-risk`.

### Closed gap 4: Repo-native validation entrypoints

Participating repositories carry repo-native validation posture and platform aggregation remains the
central certification check.

### Closed gap 5: Aggregated discovery and certification inputs

Platform validation aggregates from the governed source manifest and generated catalog,
dependency-graph, and certification artifacts are derived from that federated source set.

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

1. no first-wave producer or consumer declaration is required under this RFC,
2. future AI-facing mesh work should consume the gateway-published catalog and trust APIs instead of
   declaring an AI product before there is a stable governed AI data product,
3. when `lotus-ai` does own a stable governed product or catalog-consuming capability, it should
   use the same `contracts/domain-data-products/` repo-native pattern.

#### `lotus-platform`

1. own aggregation rules and validation automation,
2. own templates and onboarding documentation,
3. generate ecosystem-level certification inputs from the repo-native declarations.

## Test and Validation Evidence

This RFC is grounded in current implementation evidence.

Reviewed evidence includes:

1. `platform-contracts/domain-data-products/validate_domain_data_product_contracts.py`
2. `platform-contracts/domain-data-products/domain-product-source-manifest.v1.json`
3. `C:/Users/Sandeep/projects/lotus-core/contracts/domain-data-products/lotus-core-products.v1.json`
4. `C:/Users/Sandeep/projects/lotus-performance/contracts/domain-data-products/lotus-performance-products.v1.json`
5. `C:/Users/Sandeep/projects/lotus-performance/contracts/domain-data-products/lotus-performance-consumers.v1.json`
6. `C:/Users/Sandeep/projects/lotus-risk/contracts/domain-data-products/lotus-risk-products.v1.json`
7. `C:/Users/Sandeep/projects/lotus-risk/contracts/domain-data-products/lotus-risk-consumers.v1.json`
8. `C:/Users/Sandeep/projects/lotus-advise/contracts/domain-data-products/lotus-advise-products.v1.json`
9. `C:/Users/Sandeep/projects/lotus-advise/contracts/domain-data-products/lotus-advise-consumers.v1.json`
10. `C:/Users/Sandeep/projects/lotus-report/contracts/domain-data-products/lotus-report-consumers.v1.json`
11. `C:/Users/Sandeep/projects/lotus-manage/contracts/domain-data-products/lotus-manage-consumers.v1.json`
12. `generated/domain-product-catalog.json`
13. `generated/domain-product-dependency-graph.json`
14. `generated/domain-product-certification-report.json`
15. `tests/unit/test_domain_product_rollout_closure.py`

Current generated proof:

1. 6 included repositories: `lotus-core`, `lotus-performance`, `lotus-risk`, `lotus-advise`,
   `lotus-report`, and `lotus-manage`,
2. 23 governed products,
3. 17 consumer dependency edges,
4. 0 pending repositories,
5. certified catalog posture,
6. no active product or consumer source path points at
   `platform-contracts/domain-data-products/`.

## Closure Implementation Evidence

Implementation PRs and commits:

1. platform PR #144, `5fe3c2d`, implemented federated repo-native aggregation and certification
   from the source manifest,
2. platform PR #145 and #146 built on the generated catalog for RFC-0087 trust telemetry and live
   trust certification, proving downstream RFCs can consume the federated output,
3. this closure slice records the explicit `lotus-ai` posture, mirror-retention decision, and
   executable rollout-closure test.

Slice 7 outcome:

1. API certification pattern: no new public API was introduced by RFC-0086; the relevant contract
   surface is the platform source manifest, generated catalog, dependency graph, and certification
   report,
2. platform governance: source-of-truth ownership is repo-native for included repositories, while
   platform remains the schema, validation, aggregation, and certification authority,
3. duplicate/dead logic: transitional platform mirror declaration files are retained only as
   compatibility evidence and are not used by the generated catalog for included repositories,
4. branch and CI evidence: platform aggregation and certification tests cover the federated rollout
   and are part of the feature-lane validation set.

Slice 8 outcome:

1. documentation and context are updated to state the implemented rollout posture,
2. agent context points future workers to the source manifest and repo-native declaration paths,
3. wiki update is not required for RFC-0086 because no operator-facing command changed in this
   closure slice,
4. skills review: no new skill is required yet; repeatable repo-native onboarding can continue to
   use existing backend governance and RFC review skills until a second rollout wave shows enough
   repetition to justify a dedicated mesh-onboarding skill,
5. branch hygiene: this slice must merge through a normal platform PR and return `lotus-platform`
   to clean `main`.

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
4. whether any repeated onboarding lesson should become durable guidance,
5. whether the slice left the repo cleaner and easier to maintain than before.

## Rollout and Backward Compatibility

### Slice 0: Audit baseline and repo ownership map

1. classify current platform-owned declarations into long-term repo owners,
2. identify which declarations remain platform-owned versus transitional,
3. map the next rollout wave repository by repository.

Exit gate:

1. every current declaration has an explicit target owner,
2. transitional versus durable platform-owned files are classified truthfully.

### Slice 1: Repo-native layout standard and templates

1. define governed in-repo declaration locations,
2. add templates and onboarding guidance,
3. add aggregation rules that can discover repo-native files.

Exit gate:

1. the in-repo file layout standard is explicit,
2. onboarding templates are sufficient to start parallel repo implementation safely.

### Slice 2: First-wave declaration migration

1. move or mirror `lotus-core`, `lotus-performance`, and `lotus-risk` declarations into their
   owning repos,
2. keep platform validation aligned during the transition.

Exit gate:

1. the first-wave repos own their own declaration content,
2. migration posture for any mirrored files is explicit rather than implicit.

### Slice 3: Broader domain rollout

1. onboard `lotus-manage`,
2. onboard `lotus-advise`,
3. onboard `lotus-report`,
4. document `lotus-ai` as outside the first-wave producer and consumer declaration set until it owns
   a stable governed product or catalog-consuming capability.

Exit gate:

1. the broader domain wave has real repo-native declarations for participating repos,
2. product and dependency ownership is explicit across the participating repos,
3. excluded repositories have a conscious posture and future onboarding condition.

### Slice 4: Repo-native validation and CI alignment

1. add local validation entrypoints in the owning repos,
2. align repo-native CI and platform aggregation checks.

Exit gate:

1. each participating repo has a truthful local validation path,
2. repo-native and platform-native checks agree on declaration validity.

### Slice 5: Aggregation and certification hardening

1. update platform automation to aggregate repo-native declarations,
2. generate consistent certification inputs from the federated declaration set.

Exit gate:

1. platform aggregation no longer depends on platform-curated declarations as the primary truth,
2. certification inputs are generated from the federated set consistently.

### Slice 6: Discovery and onboarding-readiness preparation

1. make the federated declaration set ready for later catalog and telemetry RFCs,
2. harden ownership, lifecycle, and consumer-approval posture across the broader rollout wave.

Exit gate:

1. later discovery and telemetry RFCs can build on this foundation without redesigning declaration
   ownership,
2. ownership and lifecycle posture are explicit enough for downstream automation.

### Slice 7: Code Review, Governance Tightening, and Loose-End Closure

This slice is mandatory.

1. review each participating repo for declaration duplication, stale transitional copies, and weak
   validation paths,
2. tighten platform aggregation, validation, and rollout rules,
3. confirm the broader rollout follows the certification pattern and platform governance,
4. remove or retire transitional copies and onboarding shortcuts where the migration is already
   complete.

Exit gate:

1. no completed rollout repo is left with avoidable declaration duplication,
2. certification-pattern and governance expectations are satisfied across the wave.

### Slice 8: Documentation, Agent Context, Wiki Update, Skills Review, and Branch Hygiene

This slice is mandatory.

1. update platform and repo docs for repo-native declaration ownership,
2. update context and reference maps where durable paths changed,
3. consciously assess whether skills or onboarding guidance should change for future repo rollout
   work,
4. identify documentation or context that should be added to improve future multi-repo rollout work,
5. identify documentation or context that should be removed because it would become stale or
   misleading after migration,
6. close branch and PR hygiene truthfully.

Exit gate:

1. any keep, tighten, add, remove, or no-change decisions for skills and context are explicit,
2. future agents can discover the repo-native onboarding path quickly,
3. no branch or context debt is left behind.

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

### Conscious no-change and follow-up decisions at closure

1. no new dedicated mesh-onboarding skill is added in this closure pass because the existing Lotus
   backend governance and RFC review skills cover the current work,
2. platform context is updated now that durable repo-native paths are implemented,
3. no existing docs are removed until the retained mirror declaration files are retired or a future
   cleanup RFC proves they no longer have compatibility value.

That posture is intentional rather than accidental.

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
3. the broader rollout wave includes `lotus-manage`, `lotus-advise`, and `lotus-report`, with
   `lotus-ai` consciously excluded from the first-wave declaration set until it has a stable
   governed product or consumer capability,
4. repo-native validation paths exist for the participating repositories,
5. transitional copies are either removed or explicitly justified,
6. Slice 7 and Slice 8 are completed as mandatory quality and closure gates.

Status: complete for RFC-0086.

## Non-Goals

This RFC does not:

1. replace RFC-0085 gateway publication work,
2. implement live telemetry or freshness measurement,
3. implement the discovery catalog itself,
4. allow repository-specific schema variants,
5. claim that federation is complete before broader rollout and validation are actually finished.

## Open Questions

1. Resolved: included repositories are fully repo-native for active aggregation; transitional
   platform mirrors are retained as compatibility evidence only.
2. Resolved: only stable governed products and explicit governed consumer dependencies belong in
   the RFC-0086 declaration wave. Internal-only products require a future acceptance decision before
   being added to the catalog.
3. Resolved: gateway publication belongs to RFC-0085, not RFC-0086. Gateway may expose the catalog
   and trust posture, but does not become a repo-native product owner under this RFC.

## Next Actions

1. continue RFC-0087 first-wave live telemetry emission in producer repositories,
2. continue RFC-0085 gateway publication from generated platform artifacts,
3. continue RFC-0088 Workbench discovery and trust UX through gateway-only consumption.
