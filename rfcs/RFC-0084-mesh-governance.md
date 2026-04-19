# RFC-0084 - Lotus Governed Domain Data Product Platform and Mesh Governance

| Field | Value |
| --- | --- |
| Status | Draft |
| Created | 2026-04-19 |
| Last Updated | 2026-04-19 |
| Owners | lotus-platform architecture; lotus-platform governance |
| Depends On | RFC-0067; RFC-0071; RFC-0072; RFC-0073; RFC-0082; RFC-0083 |
| Related Standards | `RFC-0067-centralized-api-vocabulary-inventory-and-openapi-documentation-governance.md`; `RFC-0071-centralized-environment-scoped-service-addressing-and-ingress-governance.md`; `RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`; `RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md`; `RFC-0082-lotus-core-domain-authority-and-analytics-serving-boundary-hardening.md`; `RFC-0083-lotus-core-system-of-record-target-architecture.md`; `C:/Users/Sandeep/projects/lotus-core/docs/architecture/RFC-0082-contract-family-inventory.md`; `C:/Users/Sandeep/projects/lotus-performance/docs/technical/RFC-0082-upstream-contract-family-map.md`; `C:/Users/Sandeep/projects/lotus-risk/docs/domain-apis/RFC-0082-upstream-contract-family-map.md`; `C:/Users/Sandeep/projects/lotus-gateway/docs/standards/RFC-0082-upstream-contract-family-map.md`; `C:/Users/Sandeep/projects/lotus-manage/docs/standards/RFC-0082-upstream-contract-family-map.md` |
| Scope | Cross-repo |

## Executive Summary

Lotus already has several capabilities that deliver the real value people usually want when they say
"data mesh":

1. domain authority is explicit at the repository level,
2. cross-repository vocabulary is governed centrally,
3. platform-owned validation already enforces cross-repo standards,
4. `lotus-core` already publishes governed source-data products with ownership, security, lineage,
   and consumer bindings,
5. downstream repositories are starting to document and constrain their upstream dependency posture.

What Lotus does not yet have is the platform-owned control plane that turns those strengths into a
coherent, sellable ecosystem capability.

Today the strongest product-governance implementation lives inside `lotus-core`. `lotus-platform`
does not yet own a cross-domain data-product registry, producer and consumer declaration model,
identifier registry, trust metadata standard, or CI-enforced lifecycle for domain products across
the estate.

This RFC proposes a pragmatic target state:

1. keep domain ownership in the domain repositories,
2. make domain products first-class governed artifacts,
3. centralize only governance, catalog, semantic control, trust metadata, and validation,
4. make lineage, freshness, completeness, and supportability explicit,
5. create a customer-credible trust story that becomes a real Lotus differentiator.

This RFC is intentionally not a textbook data-mesh compliance exercise. The goal is a banking-grade
governed domain data-product platform that preserves current Lotus strengths and materially improves
commercial explainability.

## Problem

Lotus already behaves like a governed multi-service estate, but it still lacks one platform-owned
rule set for domain products across the ecosystem.

That leaves five practical problems.

### 1. Mesh-grade behavior exists, but mostly inside one domain

`lotus-core` already has named products, consumer declarations, security classification, trust
metadata, and contract guards.

Equivalent platformized discipline does not yet exist across:

1. `lotus-performance` analytics products,
2. `lotus-risk` analytics products,
3. `lotus-advise` advisory outputs,
4. `lotus-manage` operational workflow products,
5. `lotus-report` reporting and evidence products,
6. `lotus-ai` runtime and evaluation products.

### 2. Semantic governance exists, but product governance does not

RFC-0067 gives Lotus meaningful vocabulary control and cross-repo naming discipline.

What it does not yet provide is:

1. product ownership declarations,
2. consumer approval declarations,
3. lifecycle and deprecation posture,
4. freshness and completeness obligations,
5. lineage and trust requirements per product.

### 3. Platform validation is strong, but narrow in product scope

`lotus-platform` already owns cross-repo validation lanes, repository governance, and contract-backed
runtime validation.

It does not yet validate, across the estate:

1. whether every authoritative product is registered,
2. whether producers publish required trust metadata,
3. whether consumers use approved product versions,
4. whether critical product dependencies are fully declared,
5. whether cross-domain identifier semantics are consistent.

### 4. Customer trust evidence is still implementation-centric

Lotus has valuable supportability and lineage surfaces, especially in `lotus-core`.

But the estate cannot yet present one coherent, customer-credible explanation for:

1. who owns a result,
2. what upstream products were used,
3. whether the result is complete, partial, stale, blocked, or unreconciled,
4. what evidence exists if the result is challenged.

### 5. Without a platform-owned product model, the estate can drift

If each domain continues to improve locally without a shared governance plane, Lotus risks:

1. duplicated product shapes,
2. hidden downstream dependencies,
3. uneven producer maturity,
4. weak customer-facing explainability,
5. cross-repo truth discoverable only by reading many repositories.

## Original Requested Requirements (Preserved)

The original user request, preserved in intent, was:

1. deep-dive and audit the Lotus ecosystem rather than writing a superficial RFC,
2. evaluate current implementation, capabilities, and features before prescribing architecture,
3. use mesh qualities only where they deliver meaningful value rather than forcing textbook
   terminology,
4. position `lotus-platform` as a mesh platform and governance layer only if the implementation case
   is defensible,
5. identify game-changing capabilities that can become a true Lotus USP for future customers,
6. make RFC-0084 tighter and bring it to a gold standard before implementation starts,
7. include a second-last implementation slice for code review, loose-end tightening, API
   certification-pattern compliance, and platform-governance conformance,
8. include a final slice for documentation, agent context, wiki update, skill guidance review, and
   branch hygiene,
9. consciously assess whether skills, guidance, documentation, or context should be improved,
   reduced, or left unchanged.

## Current Implementation Reality

Overall classification: `Partially implemented (requires enhancement)`

Lotus is not starting from zero. It already has several strong building blocks.

### What is implemented well today

#### 1. Domain authority and repository responsibility are explicit

Evidence:

1. `C:/Users/Sandeep/projects/lotus-platform/context/lotus-context-manifest.json`
2. `C:/Users/Sandeep/projects/lotus-platform/context/ECOSYSTEM-REGISTRIES.md`
3. `C:/Users/Sandeep/projects/lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`

Assessment:

Strong foundation for ownership and boundary clarity, but not yet a domain-product registry.

#### 2. Platform-owned semantic governance already exists

Evidence:

1. `C:/Users/Sandeep/projects/lotus-platform/platform-contracts/api-vocabulary/README.md`
2. `C:/Users/Sandeep/projects/lotus-platform/platform-contracts/api-vocabulary/validate_api_vocabulary_catalog.py`
3. `C:/Users/Sandeep/projects/lotus-platform/platform-contracts/domain-vocabulary/canonical-performance-periods.v1.json`
4. `C:/Users/Sandeep/projects/lotus-platform/rfcs/RFC-0067-centralized-api-vocabulary-inventory-and-openapi-documentation-governance.md`

Assessment:

This is already a real mesh-grade semantic control plane. RFC-0084 should extend it.

#### 3. Platform-owned cross-repo validation already exists

Evidence:

1. `C:/Users/Sandeep/projects/lotus-platform/automation/Invoke-PlatformValidationLane.ps1`
2. `C:/Users/Sandeep/projects/lotus-platform/automation/platform-validation-profiles.json`
3. `C:/Users/Sandeep/projects/lotus-platform/automation/core_performance_cross_app_validation.py`
4. `C:/Users/Sandeep/projects/lotus-platform/automation/validate_repository_governance.py`
5. `C:/Users/Sandeep/projects/lotus-platform/automation/validate_platform_validation_coverage.py`

Assessment:

The platform already owns executable governance. The missing step is to govern domain products with
the same rigor.

#### 4. Machine-readable platform contracts already exist

Evidence:

1. `C:/Users/Sandeep/projects/lotus-platform/context/contracts/README.md`
2. `C:/Users/Sandeep/projects/lotus-platform/context/contracts/canonical-front-office-demo-data-contract.json`
3. `C:/Users/Sandeep/projects/lotus-platform/context/contracts/canonical-front-office-demo-data-invariants.json`
4. `C:/Users/Sandeep/projects/lotus-platform/context/contracts/workbench-panel-registry.json`

Assessment:

Lotus already knows how to operationalize machine-readable cross-repo truth.

#### 5. `lotus-core` already behaves like a governed producer of source-data products

Evidence:

1. `C:/Users/Sandeep/projects/lotus-core/src/libs/portfolio-common/portfolio_common/source_data_products.py`
2. `C:/Users/Sandeep/projects/lotus-core/src/libs/portfolio-common/portfolio_common/source_data_security.py`
3. `C:/Users/Sandeep/projects/lotus-core/scripts/source_data_product_contract_guard.py`
4. `C:/Users/Sandeep/projects/lotus-core/scripts/analytics_input_consumer_contract_guard.py`
5. `C:/Users/Sandeep/projects/lotus-core/docs/architecture/RFC-0082-contract-family-inventory.md`
6. `C:/Users/Sandeep/projects/lotus-core/docs/architecture/RFC-0082-downstream-endpoint-consumer-and-test-coverage-audit.md`

Assessment:

This is the estate's strongest current implementation of mesh-grade product discipline and should
be treated as the first producer reference model.

#### 6. Some consumer dependency mapping already exists

Evidence:

1. `C:/Users/Sandeep/projects/lotus-performance/docs/technical/RFC-0082-upstream-contract-family-map.md`
2. `C:/Users/Sandeep/projects/lotus-risk/docs/domain-apis/RFC-0082-upstream-contract-family-map.md`
3. `C:/Users/Sandeep/projects/lotus-gateway/docs/standards/RFC-0082-upstream-contract-family-map.md`
4. `C:/Users/Sandeep/projects/lotus-manage/docs/standards/RFC-0082-upstream-contract-family-map.md`

Assessment:

The direction is correct, but the model is still more documentation-backed than platform-registered
and validator-driven across all domains.

### What is only partially implemented

1. lineage and evidence posture exist in strong pockets, especially in `lotus-core`, but not as one
   platform-owned cross-domain contract,
2. trust metadata fields exist in some producer flows, but not as a platform-wide requirement,
3. downstream dependency maps exist, but not yet as a complete product-consumer registry.

### What is not yet implemented

1. no platform-wide domain data-product registry,
2. no platform-owned producer and consumer declaration schema across the estate,
3. no platform-wide identifier registry for cross-domain joins,
4. no platform rule requiring all critical products to publish trust metadata,
5. no generated platform trust surface for ownership, freshness, completeness, and evidence posture.

## Requirement-to-Implementation Traceability

| Requirement | Current implementation evidence | Current status | RFC-0084 response |
| --- | --- | --- | --- |
| Deep ecosystem audit before prescribing architecture | Platform context system, RFC-0067 assets, RFC-0082 artifacts, `lotus-core` source-data product implementation, cross-repo upstream maps | Partially satisfied | This RFC grounds every recommendation in current code, contracts, automation, and docs |
| Preserve domain ownership | Repository authority map in `lotus-context-manifest.json` and central context | Satisfied | Keep authoritative data and business logic in domain repos; centralize governance only |
| Achieve mesh-grade value without slogan-driven design | Semantic governance and `lotus-core` product discipline already show real value | Partially satisfied | Focus on governed domain products, trust metadata, lineage, and explainability |
| Make `lotus-platform` the governance layer | Platform already owns cross-repo validation and machine-readable contracts | Partially satisfied | Extend platform ownership into registry, schema, validator, and catalog control plane |
| Create a sellable customer trust story | Partial evidence surfaces exist, mostly in `lotus-core` | Not satisfied | Add trust metadata, lineage semantics, generated product catalog, and workflow-level trust summaries |
| Make RFC-0084 implementation-ready and gold standard | Previous draft had strong substance but weaker RFC-standard traceability and closure slices | Not satisfied before this pass | This pass adds preserved requirements, implementation classification, traceability, stronger rollout slices, and explicit closure gates |
| Include a second-last slice for code review, loose-end tightening, API certification, and governance conformance | Not present in the earlier draft | Not satisfied before this pass | Added an explicit penultimate tightening slice |
| Include a final slice for documentation, context, wiki, and branch hygiene | RFC-0080 had this pattern; RFC-0084 draft did not | Not satisfied before this pass | Added an explicit final closure slice |
| Assess skills and guidance improvements consciously | Existing Lotus skill system and context system exist | Partially satisfied | Added dedicated assessment and final-slice decision criteria |

## Design Reasoning and Trade-offs

Lotus is already too far along in executable governance to stop at repository-level architecture
discipline. The estate has enough evidence to justify a product-governance layer that customers can
eventually understand and trust.

The commercial reason matters:

1. customers do not buy "data mesh" terminology,
2. customers buy confidence that numbers and workflows are owned, explainable, current, and
   supportable,
3. Lotus can plausibly deliver that because much of the hard groundwork already exists.

The correct balance is:

1. domain repos own business truth and published domain products,
2. `lotus-platform` owns schemas, registries, policies, validators, generated catalogs, and
   readiness evidence rules,
3. consumers compose products but do not become shadow authorities.

This RFC therefore accepts several deliberate trade-offs:

1. incremental platformization over a one-shot redesign,
2. strongest early alignment in `lotus-core`, `lotus-performance`, and `lotus-risk`,
3. generated catalogs and validators before any customer-facing trust UI,
4. no coupling of this capability to a particular transport, lakehouse, event bus, or data-stack
   technology choice.

## Gap Assessment

The critical gaps are specific product and governance gaps, not generic architecture gaps.

### Gap 1: Platform-wide product registry

Lotus has repository inventories and one repo-local product catalog in `lotus-core`, but no
platform-owned registry for all authoritative domain products.

### Gap 2: Producer and consumer lifecycle contracts

There is no standard platform schema covering:

1. product identity,
2. lifecycle status,
3. approved consumers,
4. deprecation and migration posture,
5. version compatibility,
6. freshness and completeness obligations.

### Gap 3: Identifier and temporal semantics registry

RFC-0067 gives Lotus vocabulary discipline, but the estate still lacks a governed registry for:

1. cross-domain join keys,
2. identifier stability rules,
3. cross-domain temporal semantics,
4. readiness and trust vocabularies.

### Gap 4: Platform-wide trust metadata requirements

Important products can still omit freshness, completeness, lineage, evidence, or reconciliation
metadata without violating a platform-owned rule.

### Gap 5: Customer-credible trust surfaces

Lotus cannot yet generate one coherent answer to:

1. what product produced this output,
2. who owns it,
3. how fresh it is,
4. what evidence exists,
5. whether the result is complete, partial, stale, blocked, or unreconciled,
6. which upstream products are involved.

## Deviations and Evolution Since Original RFC Direction

This pass tightens the RFC in several ways.

1. It moves from broad narrative into the Lotus RFC standard structure.
2. It makes current implementation reality explicit instead of mixing aspiration with truth.
3. It classifies the current state as partially implemented rather than implying a blank slate.
4. It makes commercial trust and supportability central to the design case.
5. It adds explicit penultimate and final closure slices for engineering quality and governance
   follow-through.

## Proposed Changes

### Decision

Lotus adopts the following architectural direction.

1. `lotus-platform` becomes the governed domain data-product platform and mesh governance layer for
   the Lotus ecosystem.
2. Authoritative business data and business computations remain in the domain services.
3. The platform owns the control plane for registration, semantics, identifiers, trust metadata,
   lineage policy, validation, and generated discovery artifacts.
4. Lotus will measure success by trustable domain products and explainable cross-domain workflows,
   not by terminology compliance.

### Governance invariants

These invariants are mandatory. Implementation slices may choose different tactical designs, but
they must not violate these outcomes.

1. Domain repositories remain the only authoritative owners of their business-domain products.
2. `lotus-platform` owns governance, registry, validation, semantic-control, and discovery-plane
   responsibilities rather than business computation.
3. Every cross-domain product must have an owner, version, lifecycle status, approved-consumer
   posture, and deprecation path.
4. Every critical product must publish enough trust metadata for downstream explainability and
   operational support.
5. Every cross-domain consumer dependency must be declared explicitly rather than inferred from
   incidental API usage.
6. Every cross-domain product and dependency that matters operationally must be validator-addressable
   in CI.
7. Platform-generated trust and discovery surfaces must report partial, stale, blocked, and
   unreconciled states truthfully rather than collapsing them into generic success.
8. `lotus-gateway` and other composition layers may compose products, but they must not become shadow
   authorities or shadow registries.
9. RFC-0067 semantic governance remains the canonical base layer for product and identifier
   vocabulary.
10. The final two implementation slices remain mandatory quality gates, not optional cleanup work.

### Target operating model

The target operating model has four layers.

#### 1. Domain product producers

Authoritative producers remain in the domain repositories:

1. `lotus-core` for operational source truth,
2. `lotus-performance` for performance analytics,
3. `lotus-risk` for risk analytics,
4. `lotus-advise` for advisory products,
5. `lotus-manage` for management workflow and execution-state products,
6. `lotus-report` for reporting and evidence products,
7. `lotus-ai` for AI runtime, evaluation, and workflow-support products.

#### 2. Platform governance and registry plane

`lotus-platform` owns:

1. machine-readable product registry schemas,
2. producer and consumer declaration schemas,
3. identifier and trust vocabularies,
4. validators and CI gates,
5. generated catalogs and discovery artifacts,
6. governance workflows for approvals, deprecations, and version migration.

#### 3. Consumer composition layer

Consumer repos and gateway surfaces compose governed products, but they do not replace domain
ownership or become an unofficial registry.

#### 4. Trust and evidence layer

Lotus validates and eventually surfaces:

1. ownership,
2. freshness,
3. completeness,
4. lineage,
5. evidence posture,
6. version compatibility,
7. partial and blocked-state truthfulness.

### Platform capability model

`lotus-platform` should add a new capability family under `platform-contracts/` for governed domain
products.

#### A. Domain data-product registry

Introduce contracts such as:

1. `platform-contracts/domain-data-products/*.json`
2. `platform-contracts/domain-data-products.schema.json`
3. `platform-contracts/domain-data-product-consumers.schema.json`

Minimum fields should include:

1. `product_name`
2. `product_version`
3. `owner_repository`
4. `product_family`
5. `authoritative_domain`
6. `lifecycle_status`
7. `request_scope`
8. `temporal_scope`
9. `required_trust_metadata`
10. `freshness_policy`
11. `completeness_policy`
12. `lineage_policy`
13. `security_profile_ref`
14. `approved_consumers`
15. `deprecation_policy`

#### B. Identifier and semantic registry

Introduce machine-readable registries for:

1. cross-domain business identifiers,
2. identifier stability and lifecycle rules,
3. temporal semantics,
4. readiness and trust vocabularies for freshness, quality, reconciliation, and blocked-state
   reporting.

This extends RFC-0067 rather than replacing it.

Rationale for `platform-contracts/`:

1. this capability is a platform governance contract family rather than a local runtime/demo
   contract,
2. it belongs next to API vocabulary and other machine-readable platform standards,
3. it should be treated as ecosystem contract infrastructure, not repository-context metadata,
4. keeping it under `platform-contracts/` reduces the risk of mixing durable governance contracts
   with narrower context-owned runtime artifacts.

#### C. Trust metadata contract

Promote the best current `lotus-core` metadata patterns into a platform standard. High-value fields
likely include:

1. `product_name`
2. `product_version`
3. `tenant_id`
4. `generated_at`
5. `as_of_date`
6. `restatement_version`
7. `reconciliation_status`
8. `data_quality_status`
9. `latest_evidence_timestamp`
10. `source_batch_fingerprint`
11. `policy_version`
12. `correlation_id`
13. `lineage_bundle_id`

#### D. Producer and consumer declaration model

Each repository should declare:

1. which products it publishes,
2. which products it consumes,
3. which versions it depends on,
4. which platform validations cover those dependencies.

#### E. Federated governance workflow

The platform should define:

1. when a new product requires an RFC versus a smaller contract-review slice,
2. how owners approve new consumers,
3. how product deprecations are announced and enforced,
4. how version drift fails CI.

#### F. Platform trust surfaces

Lotus should generate artifacts that answer:

1. what products exist,
2. who owns them,
3. how fresh they are,
4. which trust metadata they publish,
5. which customer-critical workflows depend on them.

Start with generated JSON and Markdown. Product-facing surfaces can follow later.

### Proposed product families

The initial platform vocabulary should cover at least:

1. `operational_source_data`
2. `analytics_input`
3. `analytics_output`
4. `simulation_and_projected_state`
5. `workflow_and_decision_state`
6. `reporting_and_evidence`
7. `supportability_and_control_plane`
8. `ai_runtime_and_evaluation`

### Repository implications

#### `lotus-platform`

1. create cross-domain product registry schemas,
2. create trust and identifier registries,
3. add validators and CI gates,
4. generate discovery artifacts and governance evidence.

#### `lotus-core`

1. map the existing source-data product model into platform schemas,
2. keep current guards as the first producer reference implementation,
3. align existing trust and security fields with platform standards.

#### `lotus-performance`

1. declare initial analytics output products,
2. publish trust metadata requirements,
3. register upstream dependencies on governed core products.

#### `lotus-risk`

1. declare governed risk products,
2. publish upstream dependency and trust metadata posture,
3. keep performance-return and core dependency posture explicit and test-backed.

#### `lotus-gateway`

1. declare upstream product dependencies for stable experience contracts and published gateway APIs,
2. surface trust posture where user experience or ecosystem-facing API behavior depends on it,
3. remain the governed ecosystem API face, composition layer, ingress, policy, and cross-cutting
   publication plane,
4. avoid becoming a domain-product authority or shadow registry for data products owned elsewhere.

### Gateway position

`lotus-gateway` should remain important, but its role needs to stay precise.

The right long-term model is:

1. domain services own domain products,
2. `lotus-platform` owns domain-product governance and registry truth,
3. `lotus-gateway` owns ecosystem API publishing, ingress, composition, policy enforcement,
   cross-cutting controls, and consumer-facing contract shaping where needed.

That means `lotus-gateway` can and should be the face of Lotus APIs without becoming the owner of
the underlying domain products.

#### What `lotus-gateway` should own

1. unified API ingress for UI and ecosystem consumers,
2. authentication, authorization, entitlement, throttling, audit correlation, and cross-cutting
   publication controls,
3. composition of multiple domain products into consumer-friendly API contracts,
4. versioned published API surfaces for external consumers,
5. exposure of trust posture where customer-facing APIs need it.

#### What `lotus-gateway` should not own

1. canonical domain truth that belongs in source systems such as `lotus-core`,
2. analytics truth that belongs in `lotus-performance` or `lotus-risk`,
3. the platform registry of what products exist and who owns them,
4. silent private copies of product semantics that drift from the authoritative producers.

#### Practical recommendation

This is the right thing to do if it is implemented with discipline.

It becomes the wrong thing if gateway turns into:

1. a second product registry,
2. a second semantic authority,
3. a place where domain logic is reimplemented for publishing convenience.

The clean separation is:

1. producers own product truth,
2. `lotus-platform` owns product governance truth,
3. `lotus-gateway` owns API publication and composition truth.

#### `lotus-advise`, `lotus-manage`, `lotus-report`, `lotus-ai`

1. identify authoritative products,
2. classify internal-only versus stable ecosystem contracts,
3. register trust metadata and consumer dependencies for stable products in later slices.

## Test and Validation Evidence

This RFC is grounded in implementation evidence gathered from current repositories and platform
artifacts.

Reviewed evidence includes:

1. `lotus-platform/context/lotus-context-manifest.json`
2. `lotus-platform/context/ECOSYSTEM-REGISTRIES.md`
3. `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`
4. `lotus-platform/platform-contracts/api-vocabulary/*`
5. `lotus-platform/context/contracts/*`
6. `lotus-platform/automation/Invoke-PlatformValidationLane.ps1`
7. `lotus-platform/automation/platform-validation-profiles.json`
8. `lotus-platform/automation/core_performance_cross_app_validation.py`
9. `lotus-platform/automation/validate_repository_governance.py`
10. `lotus-platform/automation/validate_platform_validation_coverage.py`
11. `lotus-core/src/libs/portfolio-common/portfolio_common/source_data_products.py`
12. `lotus-core/src/libs/portfolio-common/portfolio_common/source_data_security.py`
13. `lotus-core/scripts/source_data_product_contract_guard.py`
14. `lotus-core/scripts/analytics_input_consumer_contract_guard.py`
15. `lotus-core/docs/architecture/RFC-0082-contract-family-inventory.md`
16. `lotus-performance/docs/technical/RFC-0082-upstream-contract-family-map.md`
17. `lotus-risk/docs/domain-apis/RFC-0082-upstream-contract-family-map.md`
18. `lotus-gateway/docs/standards/RFC-0082-upstream-contract-family-map.md`
19. `lotus-manage/docs/standards/RFC-0082-upstream-contract-family-map.md`

Validation performed for this RFC slice:

1. current-reality audit across platform and domain repositories,
2. RFC structure review against the Lotus RFC standard template,
3. documentation diff verification before commit.

No runtime or behavior change is implemented by this RFC-only slice.

## Original Acceptance Criteria Alignment

| Intended outcome | Alignment in this RFC |
| --- | --- |
| Lotus should preserve domain ownership | Explicitly preserved |
| Lotus should gain a platform-owned governance layer | Explicitly proposed |
| Lotus should gain stronger explainability and trust posture | Explicitly proposed |
| Lotus should avoid slogan-driven architecture | Explicitly preserved |
| Lotus should become commercially stronger and more credible | Explicitly positioned through trust, lineage, and supportability |
| Future work should be guided by better skills and context | Explicit penultimate and final slices added |

## Rollout and Backward Compatibility

This RFC should be implemented in controlled slices.

### Slice 0: Audit baseline and approval

Deliverables:

1. approve this RFC as the platform-owned direction,
2. record current strengths, gaps, and initial producer candidates,
3. confirm the initial scope as governance and registry plane rather than central data movement.

Minimum validation:

1. RFC review,
2. documentation truthfulness review,
3. no runtime changes.

### Slice 1: Platform registry schemas

Deliverables:

1. add domain data-product registry schemas,
2. add producer and consumer declaration schemas,
3. define required trust metadata and lifecycle fields,
4. define initial product-family vocabulary.

Minimum validation:

1. schema tests,
2. contract tests in `lotus-platform/tests/unit`,
3. docs and context updates.

### Slice 2: Core producer alignment

Deliverables:

1. map `lotus-core` source-data products into platform registry format,
2. align `lotus-core` security and trust metadata to platform-owned profiles,
3. validate producer declarations from `lotus-core`.

Minimum validation:

1. `lotus-core` product-guard tests,
2. platform schema validation,
3. targeted repo-local proof.

### Slice 3: First analytics producer onboarding

Deliverables:

1. register the first governed `lotus-performance` analytics products,
2. register the first governed `lotus-risk` analytics products,
3. define trust metadata expectations for analytics outputs,
4. add producer and consumer declarations for those repositories.

Initial scope decision for this RFC:

1. `lotus-performance` and `lotus-risk` are the first analytics producer wave after `lotus-core`,
2. `lotus-gateway` is not part of the first producer wave and should be treated as a governed
   consumer/composer unless a future slice introduces gateway-owned cross-cutting API products with
   separate justification.

Minimum validation:

1. affected repo feature-lane proof,
2. platform conformance tests,
3. targeted cross-app validation.

### Slice 4: Identifier and semantic hardening

Deliverables:

1. add machine-readable cross-domain identifier rules,
2. align product contracts to canonical identifier references,
3. define shared readiness and trust vocabularies.

Minimum validation:

1. platform validator coverage,
2. affected repo contract proof,
3. RFC-0067 compatibility checks.

### Slice 5: Trust and supportability contract expansion

Deliverables:

1. define a platform-owned trust metadata contract,
2. define lineage bundle expectations,
3. define freshness, completeness, reconciliation, and blocked-state semantics,
4. define operator-only versus customer-consumable evidence classes.

Minimum validation:

1. platform contract tests,
2. selected producer alignment tests,
3. cross-app scenario proof for critical workflows.

### Slice 6: Platform consumer validation

Deliverables:

1. fail CI when consumers depend on undeclared products,
2. fail CI when versions drift without approved migration posture,
3. fail CI when mandatory trust metadata is absent.

Minimum validation:

1. validator tests,
2. producer-consumer fixture coverage,
3. targeted repo integration checks.

### Slice 7: Code Review, API Certification, and Governance Tightening

Deliverables:

1. review implementation for loose ends, duplicated logic, stale compatibility handling, and
   overgrown modules,
2. ensure affected APIs follow the Lotus endpoint certification and documentation posture rather than
   only passing local tests,
3. verify OpenAPI, vocabulary, route-family, and contract-governance expectations are satisfied,
4. tighten tests, validators, and supporting docs where gaps remain before closure.

Minimum validation:

1. targeted code review findings are resolved or consciously deferred,
2. affected APIs follow certification-pattern requirements and platform governance rules,
3. feature-lane and repo-native validation evidence is current and truthful.

### Slice 8: Documentation, Agent Context, Wiki Update, Skills Review, and Branch Hygiene

Deliverables:

1. review whether `AGENTS.md`, central context, onboarding docs, or skill routing guidance must be
   updated to reflect the implemented data-product governance model,
2. update the relevant platform wiki or equivalent durable knowledge surface with approved
   operating-model guidance and discovery links,
3. record any conscious no-change decisions for context, skills, or documentation,
4. remove stale guidance or obsolete references created by the implementation journey,
5. complete branch hygiene, RFC cross-link cleanup, and truthful closure evidence before final RFC
   closure.

Mandatory review questions for this final slice:

1. Did implementation create a new repeated workflow that needs a Lotus skill or routing change?
2. Did any existing skill become stale, overlapping, or misleading?
3. Did central context or onboarding material fall behind actual platform behavior?
4. Is there any documentation that should be removed rather than expanded?
5. Is the branch, PR evidence, and cross-repo reference state clean enough for truthful closure?

Minimum validation:

1. documentation and context diff review,
2. skill and routing review,
3. branch hygiene verification,
4. explicit recorded no-change decisions where applicable.

## Validation and Evidence Model

RFC-0084 implementation should use the RFC-0072 lane model rather than ad hoc proof.

### Required feature-lane evidence

For any slice implementing this RFC:

1. targeted repo-native validation in the changed repository,
2. contract, schema, or validator proof for the changed governance surface,
3. updated docs proving the operating model changed intentionally,
4. explicit note of affected producers, consumers, and registries.

### Required PR Merge Gate evidence

1. `lotus-platform` PR-grade proof when schemas, validators, catalogs, or governance automation
   change,
2. affected producer repo PR-grade proof when product declarations or trust metadata contracts
   change,
3. affected consumer repo PR-grade proof when dependency posture or response semantics change,
4. truthful note of remaining deferred gaps.

### Platform end-to-end evidence

Platform end-to-end validation is required when:

1. gateway or workbench behavior changes because trust surfaces or dependency posture changed,
2. critical seeded workflows depend on the newly governed products,
3. customer-visible readiness, completeness, or lineage behavior changes.

### Lane mapping by expected slice type

| Slice type | Typical repositories | Minimum lane | Escalation trigger |
| --- | --- | --- | --- |
| RFC/docs-only direction | `lotus-platform` | Feature Lane docs proof | none unless runtime or contracts change |
| registry schema and validator work | `lotus-platform` | Feature Lane plus schema/contract tests | PR Merge Gate when validator or contract behavior changes |
| producer declaration onboarding | producer repo plus `lotus-platform` | Feature Lane in both touched repos | PR Merge Gate when published contracts or trust metadata change |
| consumer conformance work | consumer repo plus `lotus-platform` | Feature Lane in affected consumer | PR Merge Gate when dependency semantics or runtime behavior change |
| trust-surface or gateway-facing changes | `lotus-platform`, `lotus-gateway`, affected producers | PR Merge Gate | platform end-to-end validation |
| Slice 7 certification and governance tightening | all touched repos | PR Merge Gate | platform end-to-end validation when customer-visible behavior changed |

### Certification expectation for Slice 7

The penultimate slice is not a cosmetic review.

It must confirm that:

1. affected APIs follow Lotus endpoint certification posture,
2. OpenAPI and vocabulary governance remain current,
3. route-family and ownership classifications remain accurate,
4. tests and validators are meaningful rather than superficial,
5. implementation did not leave drift between code, contracts, docs, and repo context.

## Open Questions

1. Which `lotus-performance` and `lotus-risk` products should be the first platform-registered
   analytics outputs?
2. Which trust metadata fields must be global versus product-family-specific?
3. Which product families should remain internal-only in the first rollout?
4. Should gateway-facing contracts surface lineage references directly, or should that remain in
   operator-facing supportability surfaces first?
5. At what maturity level should Lotus expose a customer-facing trust surface rather than generated
   platform artifacts only?

## Next Actions

1. Review and approve this RFC as the platform direction for governed domain data products.
2. Start Slice 1 in `lotus-platform/platform-contracts/` by defining the initial registry schemas
   and validator surface.
3. Treat `lotus-core` source-data product governance as the first producer reference model.
4. Treat `lotus-performance` and `lotus-risk` as the first analytics producer wave in Slice 3.
5. Keep `lotus-gateway` scoped as the ecosystem API face and governed consumer/composer rather than
   a default domain-product authority.
6. Preserve Slice 7 and Slice 8 as mandatory quality and closure gates rather than optional cleanup.

## Skills and Guidance Assessment for Future Work

This RFC requires a conscious assessment of whether Lotus guidance should change.

### Improvements likely needed once implementation starts

1. `LOTUS-SKILL-ROUTING-MAP.md` may need a clearer route for cross-repo domain-product governance
   work if this becomes a repeated implementation pattern rather than a one-off RFC.
2. `LOTUS-ENGINEERING-CONTEXT.md` and `CONTEXT-REFERENCE-MAP.md` may need new links once the
   registry schemas, generated catalogs, and validators exist.
3. `ECOSYSTEM-REGISTRIES.md` and `lotus-context-manifest.json` may need references to platform-owned
   product registries once those artifacts become durable truth.
4. If implementation introduces repeated producer-onboarding work, Lotus may eventually justify a
   dedicated skill for domain-product governance or a tighter extension of an existing Lotus
   delivery/governance skill.

### Conscious no-change decisions at RFC draft stage

1. No skill files are changed by this RFC-only slice because the product-governance workflow is not
   yet implemented and routing changes would be premature.
2. No central context files are changed yet because RFC approval and first implementation slices
   should define the durable artifact locations before context is updated.
3. No documentation should be removed yet because this RFC pass is defining direction, not retiring
   existing implementation guidance.

That no-change posture is intentional rather than accidental.

## Non-Goals

This RFC does not:

1. centralize all business data into `lotus-platform`,
2. require a lakehouse, warehouse, universal event bus, or transport strategy as the defining
   architectural choice,
3. replace service APIs with a separate central query fabric,
4. force textbook data-mesh terminology into customer-facing material,
5. blur domain authority between repositories.

## Risks and Mitigations

### Risk: The platform becomes a documentation-heavy bureaucracy

Mitigation:

1. keep the registry machine-readable,
2. back important rules with validators,
3. onboard producers incrementally,
4. prioritize high-value products first.

### Risk: Domain teams experience this as centralization

Mitigation:

1. keep business ownership in the domain repos,
2. centralize only governance, schemas, catalog, and trust rules,
3. make declarations repo-owned but platform-validated.

### Risk: The estate claims mesh capability before earning it

Mitigation:

1. use objective acceptance criteria,
2. require executable validation,
3. avoid commercial claims that outrun implementation truth.

### Risk: Guidance drifts once implementation starts

Mitigation:

1. keep the final documentation and context slice mandatory,
2. require a conscious skills and guidance assessment before closure,
3. remove stale guidance rather than letting it accumulate.

## Acceptance Criteria

This RFC is considered implemented when all of the following are true.

1. `lotus-platform` owns a machine-readable cross-domain data-product registry.
2. At least `lotus-core`, `lotus-performance`, and `lotus-risk` publish platform-governed product
   declarations.
3. The platform validates producer and consumer declarations in CI.
4. Product trust metadata requirements are platform-owned and executable.
5. Cross-domain identifiers and key temporal semantics are machine-readable and governed centrally.
6. Consumer dependencies are explicit and version-aware.
7. The platform can generate a trustworthy catalog of product ownership, lifecycle, and dependency
   posture.
8. Lotus can explain freshness, completeness, lineage, and supportability for important cross-domain
   outputs consistently.
9. Slice 7 verifies API certification-pattern compliance and loose-end tightening before closure.
10. Slice 8 records documentation, context, skills, wiki, and branch-hygiene outcomes truthfully.
11. The implementation strengthens current domain authority rather than creating a shadow central
    data system.
