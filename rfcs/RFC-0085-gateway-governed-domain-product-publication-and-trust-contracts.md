# RFC-0085 - Gateway-Governed Domain Product Publication and Trust Contracts

| Field | Value |
| --- | --- |
| Status | Draft |
| Created | 2026-04-19 |
| Last Updated | 2026-04-19 |
| Owners | lotus-platform architecture; lotus-gateway maintainers; lotus-workbench maintainers |
| Depends On | RFC-0067; RFC-0071; RFC-0072; RFC-0079; RFC-0081; RFC-0082; RFC-0084 |
| Related Standards | `RFC-0067-centralized-api-vocabulary-inventory-and-openapi-documentation-governance.md`; `RFC-0071-centralized-environment-scoped-service-addressing-and-ingress-governance.md`; `RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`; `RFC-0079-gateway-evidence-and-lineage-contract.md`; `RFC-0081-lotus-workbench-ui-uplift-and-advisory-lifecycle-integration.md`; `RFC-0082-lotus-core-domain-authority-and-analytics-serving-boundary-hardening.md`; `RFC-0084-mesh-governance.md`; `C:/Users/Sandeep/projects/lotus-gateway/docs/standards/RFC-0082-upstream-contract-family-map.md`; `C:/Users/Sandeep/projects/lotus-workbench/REPOSITORY-ENGINEERING-CONTEXT.md`; `C:/Users/Sandeep/projects/lotus-gateway/REPOSITORY-ENGINEERING-CONTEXT.md` |
| Scope | Cross-repo |

## Executive Summary

RFC-0084 gave Lotus a real control plane for governed domain data products:

1. product declarations,
2. consumer declarations,
3. semantic registries,
4. trust metadata registries,
5. validator-backed cross-reference rules.

What Lotus still lacks is the publication plane that turns those internal governance capabilities
into something product teams, operators, and eventually customers can actually depend on.

Today `lotus-gateway` already contains valuable trust-aware behavior, but it is still largely
implemented route by route. `lotus-workbench` already wants trustworthy cross-domain contracts, but
some surfaces still carry fallback assumptions and contract-gap messaging. The platform does not yet
own a validator-backed publication model that binds gateway-facing contracts to RFC-0084 upstream
product declarations.

This RFC proposes the next high-value move:

1. keep business truth in the domain repositories,
2. keep governance truth in `lotus-platform`,
3. make `lotus-gateway` the governed API publication and composition plane for registered domain
   products,
4. make `lotus-workbench` consume gateway trust posture directly instead of inventing local trust
   assumptions.

This is intentionally not another vocabulary-only or documentation-only RFC. The business value is
concrete:

1. every published portfolio, performance, and risk contract can identify its authority,
2. every important result can carry freshness, supportability, and evidence posture,
3. gateway can become the reusable face of Lotus APIs without becoming a shadow domain authority,
4. future ecosystem-facing APIs can inherit a strong publication model rather than being retrofitted
   later.

## Original Requested Requirements (Preserved)

The user intent preserved in this RFC is:

1. write the next highest-value RFC after RFC-0084,
2. make it implementation-bearing rather than another documentation-only exercise,
3. target real business value, strong foundations, and the right long-term direction,
4. treat `lotus-gateway` as the likely ecosystem API face for cross-cutting publication concerns,
5. avoid forcing data products to solve publication, policy, and consumer-facing trust concerns
   individually if gateway should own them,
6. make the RFC gold standard before implementation starts,
7. require the second-last slice to cover code review, API certification-pattern conformance, and
   platform-governance tightening,
8. require the final slice to cover documentation, agent context, wiki updates, branch hygiene, and
   a conscious assessment of skills and guidance,
9. improve future agent effectiveness where a durable lesson should be promoted into context,
   documentation, or skill guidance.

## Current Implementation Reality

Overall classification: `Partially implemented (requires enhancement)`

Lotus is not starting from zero. The important point is that the right implementation fragments
already exist, but they are not yet one governed publication model.

### What is implemented well today

#### 1. RFC-0084 gives Lotus a real product-governance control plane

Evidence:

1. `platform-contracts/domain-data-products.schema.json`
2. `platform-contracts/domain-data-product-consumers.schema.json`
3. `platform-contracts/domain-data-products/validate_domain_data_product_contracts.py`
4. `platform-contracts/domain-vocabulary/domain-data-product-semantics.v1.json`
5. `platform-contracts/domain-vocabulary/domain-data-product-trust-metadata.v1.json`
6. `rfcs/RFC-0084-mesh-governance.md`

Assessment:

The platform already owns a serious control plane for governed domain products. RFC-0085 should
consume and operationalize that foundation rather than create another parallel governance family.

#### 2. `lotus-gateway` already behaves like an emerging trust-aware publication layer

Evidence:

1. `C:/Users/Sandeep/projects/lotus-gateway/src/app/services/platform_capabilities_service.py`
2. `C:/Users/Sandeep/projects/lotus-gateway/src/app/services/performance_workspace_service.py`
3. `C:/Users/Sandeep/projects/lotus-gateway/src/app/services/risk_workspace_service.py`
4. `C:/Users/Sandeep/projects/lotus-gateway/tests/contract/test_platform_capabilities_contract.py`
5. `C:/Users/Sandeep/projects/lotus-gateway/tests/integration/test_workbench_router.py`

Assessment:

Gateway already knows how to surface readiness, freshness, supportability, partial state, and
lineage-adjacent behavior. The weakness is not absence. The weakness is lack of one reusable,
platform-governed publication model that binds those contracts back to registered upstream products.

#### 3. `lotus-workbench` already has product appetite for trustworthy contracts

Evidence:

1. `C:/Users/Sandeep/projects/lotus-workbench/src/shell/app-switcher-nav.tsx`
2. `C:/Users/Sandeep/projects/lotus-workbench/src/apps/performance/capabilities.ts`
3. `C:/Users/Sandeep/projects/lotus-workbench/src/apps/performance/components/performance-evidence-mode.tsx`
4. `C:/Users/Sandeep/projects/lotus-workbench/tests/unit/app-switcher-nav.test.tsx`
5. `C:/Users/Sandeep/projects/lotus-workbench/tests/e2e/performance-workbench.smoke.spec.ts`

Assessment:

Workbench already renders trust-adjacent information. It is ready to consume a stronger contract
shape once that shape becomes explicit and stable.

### What is only partially implemented

1. gateway trust posture is route-aware but not publication-manifest-aware,
2. platform validation can validate product declarations but not yet gateway publication contracts,
3. workbench consumes some trust posture but still carries fallback assumptions where gateway should
   be authoritative,
4. route-level OpenAPI and trust posture are not yet certified against a platform publication
   contract family.

### What is not yet implemented

1. no platform-owned gateway publication schema family,
2. no validator-backed mapping from published gateway contract families to RFC-0084 upstream product
   declarations,
3. no shared gateway publication-trust section that can be reused across stable route families,
4. no first-wave workbench cleanup that removes conflicting fallback trust logic once those gateway
   contracts exist,
5. no CI-visible certification that published APIs, manifests, and UI consumption remain aligned.

## Requirement-to-Implementation Traceability

| Requirement | Current evidence | Current status | RFC-0085 response |
| --- | --- | --- | --- |
| Build on real implementation, not a blank-sheet architecture | RFC-0084 contract family, gateway trust-aware services, workbench trust-aware UI surfaces | Partially satisfied | Ground the RFC in current code and use first-wave surfaces that already have meaningful trust logic |
| Keep gateway as the ecosystem API face without making it a shadow domain authority | Existing gateway repo role and route families; RFC-0084 boundary rules | Partially satisfied | Make gateway authoritative for publication only, not for domain truth or product registry truth |
| Give Lotus business value, not only governance vocabulary | Gateway already exposes supportability, evidence, and partial-state behavior in pockets | Partially satisfied | Standardize those behaviors into stable published contract families that product and customers can trust |
| Reduce duplicated publication and trust handling across producers | Current trust behavior exists mostly route by route in gateway and downstream UI assumptions remain | Not yet satisfied | Introduce publication manifests, shared trust contract modules, and validator-backed rules |
| Make workbench consume truthful contract posture instead of local fallbacks | `app-switcher-nav.tsx`, `performance/capabilities.ts`, and evidence-mode copy show fallback behavior | Partially satisfied | First-wave workbench adoption explicitly removes or narrows fallback trust assumptions |
| Include a second-last slice for code review, API certification, and governance tightening | User requested explicitly | Not yet satisfied before this pass | RFC includes mandatory Slice 7 for code review, API certification, and governance tightening |
| Include a final slice for docs, context, wiki, branch hygiene, and skills review | User requested explicitly | Not yet satisfied before this pass | RFC includes mandatory Slice 8 for documentation, context, wiki, branch hygiene, and conscious skills/context review |
| Improve future agent effectiveness where durable lessons emerge | Existing Lotus skill routing and context system already exist | Partially satisfied | Final slice includes explicit keep/tighten/add/remove decisions for skills, docs, and context |

## Design Reasoning and Trade-offs

The key architectural choice is to make `lotus-gateway` the publication plane, not the product
registry and not the domain authority.

This split is deliberate.

### Why gateway should own publication

Gateway is the right place to own:

1. ecosystem-facing API identity,
2. consumer-oriented contract shaping,
3. auth, policy, throttling, and audit correlation at the API face,
4. cross-domain composition,
5. trustworthy partial-state reporting for published contracts.

That aligns with the current repository role and with the direction you described.

### Why gateway should not own product truth

If gateway owns domain truth, Lotus will drift into:

1. duplicated business logic,
2. duplicated semantics,
3. hidden upstream dependencies,
4. route-level truth that no longer matches domain authorities.

RFC-0084 already created the right split:

1. producers own product truth,
2. `lotus-platform` owns governance truth,
3. gateway should own publication truth.

### Why this should be implemented now

This is the right next step because the estate already has enough maturity to make the move:

1. the control plane now exists,
2. gateway already carries trust-aware behavior,
3. workbench already consumes gateway-first contracts,
4. delaying the publication model increases route-by-route drift and UI fallback accumulation.

### Trade-off: extra contract machinery now vs. retrofitting later

This RFC adds one more contract family and validator surface. That is extra implementation work now.

The trade-off is worth it because it avoids:

1. many one-off route conventions,
2. undocumented trust posture drift,
3. later external API work having to reverse-engineer gateway behavior from Python services and UI
   assumptions.

## Gap Assessment

### Gap 1: Platform-owned publication schema and validator

The platform can validate producer and consumer product declarations, but it cannot yet validate how
gateway publishes those products.

### Gap 2: Gateway publication manifests

Gateway has route contracts but no machine-readable publication manifests that bind stable route
families to RFC-0084 upstream products, trust requirements, and certification status.

### Gap 3: Shared publication-trust contract family

Gateway trust posture exists in pockets, but it is not yet reusable enough to govern portfolio,
performance, risk, workflow, and future external contract families consistently.

### Gap 4: Workbench fallback cleanup

Workbench still contains deterministic fallback or contract-gap posture in places where a governed
gateway publication model should become the single source of trust truth.

### Gap 5: Certification and merge-gate integration

The platform does not yet certify that:

1. gateway publication manifests are valid,
2. gateway OpenAPI contracts follow the publication model,
3. workbench consumes those contracts truthfully.

## Deviations and Evolution Since Original RFC

This RFC started from the direction that gateway should become the cross-cutting API face of Lotus.

After reviewing the current implementation, the important refinement is:

1. gateway should own API publication and composition,
2. gateway should not own a second product registry,
3. gateway should not own hidden semantic truth,
4. workbench adoption must be part of the feature, not a deferred follow-up.

That last point matters. A weaker RFC could have stopped at platform schema plus gateway manifests.
This pass deliberately treats workbench cleanup as part of the same implementation program, because
otherwise the product surface would continue to carry contradictory trust behavior.

## Proposed Changes

### Decision

Lotus will implement `lotus-gateway` as the governed publication and composition plane for
platform-registered domain products.

Specifically:

1. `lotus-platform` remains the owner of domain-product registry, semantics, trust metadata, and
   validator governance,
2. `lotus-gateway` will add a machine-readable publication-manifest family for stable published
   contract families,
3. every stable gateway publication manifest must reference RFC-0084 upstream product declarations,
4. first-wave gateway contracts must expose authority, freshness, supportability, and evidence
   posture through a governed reusable trust vocabulary,
5. `lotus-workbench` will consume those gateway contract sections directly and remove conflicting
   fallback assumptions for first-wave surfaces,
6. publication drift will become CI-visible through platform validation and certification gates.

### Governance invariants

These invariants are mandatory.

1. Domain services remain authoritative for business-domain truth and business computation.
2. `lotus-platform` remains authoritative for registry, semantics, trust metadata, and validation
   rules.
3. `lotus-gateway` is authoritative only for API publication, composition, policy, and
   consumer-facing contract shaping.
4. No stable gateway publication may omit its upstream product bindings.
5. No stable gateway publication may claim readiness without the trust metadata it declares as
   required.
6. No stable workbench surface covered by this RFC may invent freshness or supportability states
   outside the gateway contract.
7. API publication concerns should be solved once in gateway rather than reinvented in every
   producer.
8. The final two implementation slices are mandatory quality gates, not optional cleanup work.

### Target operating model

The target model has four layers.

#### 1. Domain product producers

Authoritative producers remain in the domain repositories:

1. `lotus-core`,
2. `lotus-performance`,
3. `lotus-risk`,
4. `lotus-advise`,
5. `lotus-manage`,
6. `lotus-report`,
7. `lotus-ai`.

#### 2. Platform governance control plane

`lotus-platform` owns:

1. upstream product declarations,
2. consumer declarations,
3. semantics and trust registries,
4. gateway publication schemas,
5. publication validators,
6. certification automation.

#### 3. Gateway publication and composition plane

`lotus-gateway` owns:

1. published contract identity,
2. API publication manifests,
3. cross-domain composition into consumer-friendly contracts,
4. publication-trust posture,
5. ecosystem-facing API controls.

#### 4. Product experience consumption layer

`lotus-workbench` consumes those gateway contracts and presents authority, freshness,
supportability, and evidence posture truthfully.

### Platform capability model

#### A. Gateway publication manifest family

Introduce a platform-governed publication contract family for stable gateway-published contract
families.

Recommended locations:

1. `C:/Users/Sandeep/projects/lotus-gateway/contracts/publication/*.json`
2. `platform-contracts/gateway-publication.schema.json`
3. `automation/validate_gateway_publications.py`

Each publication manifest should declare at least:

1. `publication_name`
2. `publication_version`
3. `published_by_repository`
4. `consumer_persona`
5. `published_surface`
6. `gateway_route_family`
7. `upstream_products`
8. `required_trust_metadata`
9. `freshness_contract`
10. `partial_state_contract`
11. `authority_contract`
12. `evidence_contract`
13. `openapi_component_refs`
14. `certification_status`
15. `deprecation_policy`

#### B. Standardized gateway publication-trust section

Stable gateway contracts should converge on a shared trust section that can be reused across route
families.

Minimum governed vocabulary should cover:

1. `authority`
2. `freshness`
3. `supportability`
4. `evidence`
5. `upstream_products`
6. `partial_failures`
7. `policy_versions`

This does not require one giant response envelope for every route. It requires one governed
publication-trust vocabulary and reusable schema family for stable contract families.

#### C. Upstream product binding and approval model

Every stable gateway publication manifest must reference RFC-0084 product declarations by product
name and version range.

Validation should fail when:

1. gateway binds to undeclared products,
2. gateway binds to unapproved or drifting product versions,
3. gateway-required trust metadata is not guaranteed by upstream products,
4. gateway route documentation drifts from publication manifests,
5. published OpenAPI contracts omit required publication-trust sections for covered route families.

#### D. Workbench contract-consumption model

For publication families brought under this RFC, `lotus-workbench` should:

1. consume gateway trust posture directly,
2. remove deterministic fallbacks that conflict with contract-backed truth,
3. distinguish `ready`, `partial`, `stale`, `blocked`, and `unavailable` states explicitly,
4. use publication-trust sections to drive shell availability, evidence mode, and trust-oriented
   summary panels.

### First-wave scope

The first implementation wave should target the surfaces with the strongest current value and the
lowest reinvention risk.

#### `lotus-gateway`

1. `shellBootstrap`
2. portfolio workspace overview family
3. performance workspace summary family
4. performance evidence family
5. risk workspace summary and analytics family

#### `lotus-workbench`

1. shell navigation and workspace availability
2. portfolio overview trust posture
3. performance summary and evidence mode
4. risk summary and supportability panels

#### `lotus-platform`

1. publication schema and validator
2. publication certification automation
3. context and discovery links for the publication contract family

### Gateway position

Your stated direction is right if the ownership split stays disciplined.

The right model is:

1. producers own product truth,
2. `lotus-platform` owns governance truth,
3. `lotus-gateway` owns API publication truth.

That means gateway should own:

1. the face of Lotus APIs,
2. cross-cutting publication and policy controls,
3. consumer-oriented contract shaping,
4. trustful partial-state reporting for published contracts.

Gateway should not own:

1. canonical domain truth,
2. hidden product registries,
3. duplicated domain calculations,
4. private semantics that drift from the platform registries.

## Test and Validation Evidence

This RFC is grounded in current implementation evidence rather than blank-sheet design.

Reviewed evidence includes:

1. `platform-contracts/domain-data-products/validate_domain_data_product_contracts.py`
2. `C:/Users/Sandeep/projects/lotus-gateway/src/app/services/platform_capabilities_service.py`
3. `C:/Users/Sandeep/projects/lotus-gateway/src/app/services/performance_workspace_service.py`
4. `C:/Users/Sandeep/projects/lotus-gateway/src/app/services/risk_workspace_service.py`
5. `C:/Users/Sandeep/projects/lotus-gateway/tests/contract/test_platform_capabilities_contract.py`
6. `C:/Users/Sandeep/projects/lotus-gateway/tests/integration/test_workbench_router.py`
7. `C:/Users/Sandeep/projects/lotus-workbench/src/shell/app-switcher-nav.tsx`
8. `C:/Users/Sandeep/projects/lotus-workbench/src/apps/performance/capabilities.ts`
9. `C:/Users/Sandeep/projects/lotus-workbench/src/apps/performance/components/performance-evidence-mode.tsx`
10. `C:/Users/Sandeep/projects/lotus-workbench/tests/unit/app-switcher-nav.test.tsx`
11. `C:/Users/Sandeep/projects/lotus-workbench/tests/e2e/performance-workbench.smoke.spec.ts`

## Original Acceptance Criteria Alignment

| Original intent | RFC-0085 alignment |
| --- | --- |
| Make the next RFC implementation-bearing and high business value | The RFC centers on gateway publication, contract trust posture, and workbench adoption rather than prose-only governance |
| Put gateway in the right long-term role | The RFC makes gateway the publication plane while keeping domain truth and governance truth elsewhere |
| Do not make domain services each solve cross-cutting publication concerns | Shared publication-manifest and trust-contract patterns move those concerns into gateway and platform governance |
| Require second-last and final closure slices | Slice 7 and Slice 8 are mandatory and explicitly shaped around those asks |
| Consciously review skills and context | Final slice includes explicit assessment criteria and allows a truthful no-change outcome |

## Mandatory Slice Review Gate

Every completed slice must receive a review pass before the next slice begins.

That review must check:

1. whether the implementation can be simplified further,
2. whether dead code, duplicate trust handling, stale fallback logic, or non-standard route branches
   should be removed,
3. whether naming, modular boundaries, and tests still match the actual contract,
4. whether any repeated lesson should be promoted into durable context, documentation, or skill
   guidance.

The review question is not only "did the slice land?" It is "is this now the cleanest truthful
version of the slice that should remain in the codebase?"

## Rollout and Backward Compatibility

### Slice 0: Audit baseline and approval

1. audit current gateway route families against RFC-0084 product declarations,
2. classify which gateway surfaces are already close to the publication model,
3. identify workbench surfaces that still rely on fallback trust assumptions,
4. produce the baseline inventory before introducing schemas.

Exit gate:

1. one approved baseline inventory exists,
2. first-wave route families are explicitly selected.

### Slice 1: Platform publication schema and validator

1. add `platform-contracts/gateway-publication.schema.json`,
2. add `automation/validate_gateway_publications.py`,
3. add high-value unit tests for manifest validation and upstream binding rules,
4. document the publication contract family under `platform-contracts/`.

Exit gate:

1. publication manifests are machine-validated,
2. validator proves cross-reference binding to RFC-0084 product declarations.

Backward-compatibility posture:

1. additive platform capability only,
2. no gateway route contract changes yet.

### Slice 2: Gateway first-wave publication manifests

1. add first-wave publication manifests in `lotus-gateway`,
2. bind `shellBootstrap`, portfolio overview, performance summary, performance evidence, and risk
   route families to upstream products,
3. capture route-family-level authority, freshness, supportability, and evidence posture.

Exit gate:

1. every first-wave route family has a publication manifest,
2. publication manifests validate against platform schemas.

Backward-compatibility posture:

1. manifests land before response-shape changes,
2. current consumers remain unchanged.

### Slice 3: Gateway shared publication-trust contract family

1. introduce reusable gateway schemas or contract modules for authority, freshness,
   supportability, and evidence posture,
2. refactor first-wave route families onto those shared structures,
3. tighten OpenAPI and contract tests accordingly.

Exit gate:

1. first-wave contracts use one governed trust vocabulary,
2. contract tests prove stable serialized shape.

Backward-compatibility posture:

1. prefer additive contract evolution where possible,
2. replace older route-local trust structures only when consumers are updated in the same slice.

### Slice 4: Workbench trust-aware adoption and fallback removal

1. update `lotus-workbench` shell and first-wave surfaces to consume governed gateway contract
   sections directly,
2. remove or narrow fallback behavior that conflicts with contract-backed truth,
3. update unit, integration, and browser tests for `ready`, `partial`, `stale`, `blocked`, and
   `unavailable` states.

Exit gate:

1. workbench no longer relies on legacy trust assumptions for first-wave route families,
2. browser validation shows truthful partial-state and evidence behavior.

Backward-compatibility posture:

1. UI fallback removal happens only after gateway contracts are in place,
2. contract and UI rollout must stay synchronized per route family.

### Slice 5: Publication certification and merge-gate integration

1. extend platform validation so manifests, gateway contracts, and workbench consumption are
   certified together,
2. add certification checks that route families expose required publication-trust posture,
3. align feature-lane and merge-gate validation with the publication model.

Exit gate:

1. publication drift becomes CI-visible,
2. first-wave route families are certification-backed.

Backward-compatibility posture:

1. new checks may begin as non-blocking on first introduction,
2. they should become blocking once first-wave route families are aligned.

### Slice 6: Customer-facing and ecosystem-facing API readiness

1. define which first-wave publication contracts are internal-only versus ecosystem-publishable,
2. harden consumer-facing route documentation and examples,
3. expose stable contract identity and policy posture needed for future external API publication.

Exit gate:

1. Lotus can point to at least one trustworthy, governed, published API family as a product asset,
2. publication posture is explicit rather than implied.

Backward-compatibility posture:

1. internal-only and ecosystem-facing publication states must be explicit,
2. do not imply external support before certification is complete.

### Slice 7: Code Review, API Certification, and Governance Tightening

This slice is mandatory.

1. review gateway route families for loose ends, duplicated trust logic, stale branches, and
   unnecessary special cases,
2. ensure APIs follow the endpoint certification pattern and publication-manifest governance,
3. retire or simplify route-local trust helpers where shared modules are sufficient,
4. tighten OpenAPI, contract tests, and validation automation to remove avoidable ambiguity,
5. confirm all relevant platform governance expectations are satisfied before closure.

Exit gate:

1. no known first-wave publication surface is running on stale or duplicate trust logic,
2. API certification and publication governance are aligned.

### Slice 8: Documentation, Agent Context, Wiki Update, Skills Review, and Branch Hygiene

This slice is mandatory.

1. update platform context and reference maps for the publication contract family,
2. update gateway and workbench docs and wiki content to reflect the new publication model,
3. consciously assess whether Lotus skills or routing guidance need to be added, tightened, kept,
   or left unchanged for gateway publication and trust-certification work,
4. identify documentation or context that should be added or removed to improve future agent
   effectiveness,
5. complete truthful PR and branch hygiene before closure.

Exit gate:

1. future work can discover the publication model quickly,
2. any no-change decision for skills or context is documented consciously rather than omitted,
3. no temporary branch or context debt is left behind.

## Validation and Evidence Model

Required proof for implementation under this RFC:

1. platform unit tests for publication schema and validator behavior,
2. gateway contract tests for first-wave publication-trust contract shapes,
3. gateway integration tests for `ready`, `partial`, `stale`, `blocked`, and `unavailable` paths,
4. workbench unit and browser tests proving truthful consumption of those states,
5. PR-gate evidence that manifests, OpenAPI docs, gateway behavior, and workbench behavior remain
   aligned.

## Skills and Guidance Assessment for Future Work

This RFC requires a conscious assessment of whether Lotus guidance should change.

### Improvements likely needed once implementation starts

1. `LOTUS-SKILL-ROUTING-MAP.md` may need a clearer route for cross-repo gateway publication and
   trust-certification work if this becomes a repeated delivery pattern,
2. `CONTEXT-REFERENCE-MAP.md` may need direct links to the gateway publication schema family and
   certification automation once they exist,
3. `LOTUS-ENGINEERING-CONTEXT.md` may need an explicit publication-plane section once the gateway
   contract family becomes durable platform truth,
4. if repeated delivery work shows a stable pattern, Lotus may justify a dedicated skill or an
   extension to an existing backend/governance skill for gateway publication certification.

### Conscious no-change decisions at RFC draft stage

1. no skill files are changed in this RFC-only pass because the publication workflow is not yet
   implemented and routing changes would be premature,
2. no central context files are changed yet because durable artifact locations and commands should be
   validated in implementation first,
3. no documentation is removed yet because current drift should be reassessed after first-wave
   rollout evidence exists.

That no-change posture at the draft stage is intentional rather than accidental.

## Risks and Mitigations

### Risk: Gateway becomes a monolith

Mitigation:

1. keep publication logic modular and contract-oriented,
2. keep domain computation upstream,
3. certify route families individually instead of centralizing all behavior in one service layer.

### Risk: This turns into another documentation-heavy governance program

Mitigation:

1. every slice is implementation-bearing,
2. route, contract, validator, and UI changes are required,
3. workbench adoption is part of the feature, not a deferred aspiration.

### Risk: Trust posture becomes decorative instead of truthful

Mitigation:

1. require upstream product bindings,
2. fail validation when required trust metadata is missing,
3. test partial, stale, and blocked paths explicitly,
4. do not let UI invent states outside the gateway contract.

### Risk: Gateway publication and workbench adoption drift out of sync

Mitigation:

1. certify manifests, API contracts, and UI consumption together,
2. roll out route-family by route-family rather than with one broad, ambiguous cutover.

## Acceptance Criteria

This RFC is complete only when:

1. `lotus-platform` owns a validator-backed gateway publication schema family,
2. `lotus-gateway` first-wave route families publish machine-readable manifests bound to RFC-0084
   upstream products,
3. first-wave gateway contracts expose governed authority, freshness, supportability, and evidence
   posture in a reusable way,
4. `lotus-workbench` first-wave surfaces consume those contract sections directly without
   conflicting fallback trust assumptions,
5. publication drift is CI-visible through platform validation and certification gates,
6. Slice 7 and Slice 8 are completed as mandatory quality and closure gates.

## Open Questions

1. Which first-wave gateway route family should become the first ecosystem-publishable API contract:
   shell capabilities, portfolio overview, or performance summary?
2. Should publication manifests live only in `lotus-gateway`, or should selected publication
   metadata also be mirrored into platform-generated discovery artifacts?
3. Which trust posture fields should be mandatory for every stable gateway publication versus only
   for analytically sensitive surfaces?

## Next Actions

1. approve this RFC as the next implementation program after RFC-0084,
2. start Slice 0 with a gateway route-family inventory and RFC-0084 product-binding audit,
3. implement the platform publication schema and validator before changing route contracts,
4. use shell bootstrap, portfolio overview, performance, and risk as the first publication wave
   because they already carry meaningful trust-aware behavior and immediate business value.
