# RFC-0091 - Enterprise Data Mesh Maturity And Production Readiness

| Field | Value |
| --- | --- |
| Status | In Progress |
| Created | 2026-04-20 |
| Last Updated | 2026-04-20 |
| Owners | lotus-platform architecture; domain repository maintainers; lotus-gateway maintainers; lotus-workbench maintainers; security and operations owners |
| Depends On | RFC-0072; RFC-0084; RFC-0085; RFC-0086; RFC-0087; RFC-0088; RFC-0089; RFC-0090 |
| Related Standards | `RFC-GOVERNANCE-STANDARD.md`; `RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`; `Continuous Integration, Validation, and Release Governance Standard.md` |
| Scope | Enterprise mesh maturity, runtime operations, onboarding, access governance, audit evidence |

## Executive Summary

RFC-0084 through RFC-0090 made Lotus a real first-wave governed mesh:

1. domain-data-product contracts exist,
2. first-wave repo-native declarations exist,
3. trust telemetry and live certification exist,
4. gateway exposes read-only publication APIs,
5. Workbench exposes self-serve discovery,
6. mesh certification runs locally and in GitHub cross-repo blocking mode.

That is credible mesh foundation. It is not yet mature enterprise data mesh.

RFC-0091 defines the final maturity program required to sell Lotus as an enterprise data mesh
capability with confidence. The goal is not to add more mesh vocabulary. The goal is to make the
mesh operational, extensible, auditable, secure, and adoptable across repositories and customer
deployment contexts.

## Original Requested Requirements

The user intent preserved in this RFC is:

1. determine what remains after RFC-0084 through RFC-0090 before calling Lotus a mature enterprise
   data mesh,
2. create a final RFC that is implementation-bearing rather than documentation-only,
3. focus on high business value and customer-sellable capability,
4. avoid textbook data-mesh theatre and instead implement practical differentiators,
5. include the mandatory second-last code review/API-certification/governance slice,
6. include the mandatory final documentation, agent context, wiki, skills/guidance, and branch
   hygiene slice.

## Current Implementation Reality

Overall classification: `first-wave governed mesh implemented; enterprise maturity gaps remain`

Implemented foundation:

1. RFC-0084: platform domain-product governance contract family.
2. RFC-0085: gateway read-only publication and trust API face.
3. RFC-0086: repo-native source declarations and federated aggregation.
4. RFC-0087: trust telemetry schema, validation, and live trust certification.
5. RFC-0088: self-serve discovery and dependency catalog in Workbench.
6. RFC-0089: mesh certification gate and operator artifacts.
7. RFC-0090: GitHub cross-repo blocking mesh certification workflow.

Remaining maturity gaps:

1. runtime telemetry is still primarily snapshot/file-contract based rather than continuously
   emitted from live service workflows,
2. product onboarding is governed but not yet fully self-service through repo-native scaffolds,
   templates, and certification checklists,
3. access governance is not yet customer/tenant/role aware across discovery and publication,
4. SLOs for freshness, completeness, reconciliation, quality, lineage, and certification drift are
   not yet promoted into operational alerts and escalation rules,
5. audit evidence exists as artifacts but not yet as a durable certification history and exportable
   customer evidence pack,
6. broader product rollout beyond the first-wave blocking set is not yet complete,
7. data-product lifecycle states are represented, but deprecation, replacement, compatibility, and
   consumer impact workflows are not yet enforced end to end.

## Implementation Status And Evidence

Current implementation status: `Slice 0 implemented on RFC-0091 branch`

Implemented evidence:

1. `automation/generate_enterprise_mesh_maturity_matrix.py`
   Generates and checks the RFC-0091 maturity matrix.
2. `generated/enterprise-mesh-maturity-matrix.json`
   Machine-readable repository and product maturity posture.
3. `generated/enterprise-mesh-maturity-matrix.md`
   Human-readable maturity posture for operators and implementation planning.
4. `tests/unit/test_enterprise_mesh_maturity_matrix.py`
   Protects repository classification, candidate products, generated artifact writes, and stale
   artifact detection.
5. `automation/README.md`
   Documents the generator and `--check` command.

Slice 0 review result:

1. every governed Lotus repository has explicit participation,
2. candidate expansion products are explicit,
3. `lotus-ai` posture is explicit,
4. generated artifacts are reproducible and test-protected,
5. no gateway, Workbench, or platform-generated artifact becomes product authority.

## Enterprise Mesh Maturity Definition

Lotus can be called a mature enterprise data mesh when these statements are true:

1. product truth stays with domain owners,
2. platform provides self-service contracts, validators, evidence, and enforcement,
3. gateway is the API face and does not become the product authority,
4. Workbench discovery is customer/operator useful and truthful,
5. access governance is explicit, role-aware, tenant-aware, and auditable,
6. trust posture is produced from runtime evidence, not decorative UI state,
7. stale, blocked, incomplete, unreconciled, and uncertified states are visible and enforceable,
8. onboarding a new product is repeatable without architecture handholding,
9. certification history can be exported as evidence for customer review,
10. CI and runtime operations prevent mesh drift before it reaches customers.

## Implementation Boundary

RFC-0091 is intentionally broad, but implementation must be wave-based.

The first enterprise maturity wave is:

| Area | Required first maturity-wave scope |
| --- | --- |
| Producers | `lotus-core`, `lotus-performance`, `lotus-risk`, `lotus-advise` |
| Candidate expansion | `lotus-report`, `lotus-manage` |
| Explicit posture decision | `lotus-ai` |
| API face | `lotus-gateway` |
| Discovery and operator UX | `lotus-workbench` |
| Platform governance | `lotus-platform` |
| Required customer proof | evidence pack for the first-wave products plus at least one promoted candidate product |

The RFC is not complete if it only adds platform schemas. It must prove at least one end-to-end
enterprise maturity path from product declaration through runtime evidence, SLO, access posture,
certification history, gateway publication, Workbench discovery, and evidence-pack export.

## Done And Not-Done Semantics

### Done

RFC-0091 can be marked implemented when:

1. the first maturity wave is fully certified,
2. at least one non-first-wave product is promoted through the new onboarding and lifecycle process,
3. the enterprise mesh gate blocks meaningful runtime, SLO, access, lifecycle, and evidence drift,
4. gateway and Workbench expose mature mesh posture without becoming authorities,
5. customer/auditor evidence packs can be generated and access-filtered,
6. GitHub cross-repo proof is green on the final implementation PR.

### Not Done

RFC-0091 must not be marked implemented if:

1. runtime evidence remains only static fixture documentation,
2. access governance exists only as prose,
3. evidence packs require manual assembly,
4. SLO drift is reported but not enforced,
5. gateway or Workbench duplicates product authority,
6. a maturity-wave repo has ambiguous product participation,
7. the final implementation only updates platform docs and tests without cross-repo proof.

## Requirement-To-Implementation Traceability

| Requirement | Current evidence | Current status | RFC-0091 response |
| --- | --- | --- | --- |
| Continuous runtime trust evidence | RFC-0087 schema and first-wave snapshots | Partial | Add service-emitted telemetry hooks and durable ingestion/export path |
| Self-service product onboarding | Repo-native declarations and source manifest | Partial | Add scaffolds, checklist, validator pack, and onboarding acceptance gate |
| Access-governed discovery | Gateway and Workbench discovery exist | Partial | Add tenant/role/consumer entitlement policy to publication and UI discovery |
| Operational SLO enforcement | Gate checks freshness and trust state | Partial | Add SLO policy contract, drift alerts, escalation ownership, and evidence history |
| Audit/customer evidence | Certification artifacts exist per run | Partial | Add certification history and exportable evidence pack |
| Broader rollout | First-wave producers certified | Partial | Promote additional products through controlled wave plan |
| Lifecycle governance | Lifecycle fields exist in catalog | Partial | Enforce deprecation, replacement, compatibility, and consumer-impact workflows |

## Design Principles

### No New Product Authority

RFC-0091 must not move data-product ownership into `lotus-platform`, `lotus-gateway`, or
`lotus-workbench`. Producers own product truth. Platform owns governance, certification, templates,
validators, and cross-repo evidence.

### Runtime Evidence Over Cosmetic Status

Trust state must come from producer evidence, certification logic, and operational SLOs. UI and
gateway may expose trust posture, but they must not invent trust posture.

### Self-Service With Guardrails

Product onboarding should be fast for a domain team, but impossible to complete incorrectly. The
scaffold should create the right files, tests, docs, telemetry hooks, and validation commands.

### Customer Evidence Is A Product Feature

Mature mesh value is not only discovery. It is the ability to prove provenance, freshness, quality,
lineage, certification, access policy, and consumer impact to a customer, auditor, or operator.

## Proposed Changes

### Decision

Implement an enterprise mesh maturity layer across platform, gateway, Workbench, and domain repos.

The program will add:

1. runtime telemetry emission and evidence ingestion,
2. self-service data-product onboarding templates and gates,
3. tenant/role/consumer-aware access policy for discovery and publication,
4. SLO and escalation policy contracts,
5. durable certification history and exportable evidence packs,
6. broader product rollout wave controls,
7. lifecycle/deprecation/compatibility governance.

## Public Interfaces And Contracts

### Platform Contracts

Add or extend platform contract families:

1. `platform-contracts/domain-data-products/`
   Add product lifecycle, compatibility, deprecation, replacement, and onboarding policy
   extensions where needed.
2. `platform-contracts/trust-telemetry/`
   Extend runtime telemetry posture to include emission source, service version, runtime
   environment, and evidence retention metadata.
3. `platform-contracts/mesh-slo/`
   New contract family for product-level freshness, completeness, reconciliation, data-quality,
   lineage, certification, and availability thresholds.
4. `platform-contracts/mesh-access/`
   New contract family for tenant, role, approved-consumer, and use-case policy.
5. `platform-contracts/mesh-evidence/`
   New contract family for certification history and customer evidence-pack manifests.

### Generated Platform Artifacts

RFC-0091 should create or extend generated artifacts rather than making operators assemble maturity
evidence manually:

1. `generated/enterprise-mesh-maturity-matrix.json`
2. `generated/enterprise-mesh-maturity-matrix.md`
3. `output/mesh-certification/enterprise-mesh-certification-status.json`
4. `output/mesh-certification/enterprise-mesh-certification-status.md`
5. `output/mesh-evidence-packs/<pack-id>/evidence-pack-manifest.json`
6. `output/mesh-evidence-packs/<pack-id>/evidence-pack-summary.md`

Generated artifacts remain derived evidence. They must not become source truth.

### Platform Automation

Add automation for:

1. generating a new product declaration scaffold,
2. validating a product onboarding bundle,
3. validating mesh SLO policies,
4. validating mesh access policies,
5. ingesting or collecting runtime telemetry snapshots from repos,
6. creating certification history records,
7. exporting evidence packs,
8. extending the mesh certification gate to include mature enterprise checks.

### Gateway APIs

Gateway should expose read-only APIs for:

1. catalog and product detail,
2. dependencies and consumers,
3. trust posture,
4. access posture for the current caller context,
5. certification history summary,
6. evidence pack download or manifest retrieval where permitted.

Gateway must not:

1. own product truth,
2. silently hide blocked products without explicit unavailable/degraded posture,
3. compute trust state using local heuristics when certified platform evidence exists.

### Workbench UX

Workbench should expose operator/customer-facing surfaces for:

1. product discovery,
2. trust posture,
3. dependency and consumer impact,
4. access eligibility and request path,
5. certification history,
6. evidence pack export,
7. blocked/stale/deprecated/replaced product states.

Workbench must consume gateway/BFF only.

### Domain Repositories

Each participating producer repository must provide:

1. repo-native product declaration,
2. telemetry emission or snapshot generation,
3. SLO policy declaration,
4. access policy declaration,
5. onboarding tests,
6. runtime evidence tests,
7. product lifecycle/deprecation tests where relevant.

### Ownership Map

| Capability | Owner | Must not own |
| --- | --- | --- |
| Product declaration truth | Producer repository | Gateway, Workbench, platform-generated artifacts |
| Contract schema and validators | `lotus-platform` | Domain calculation truth |
| Runtime telemetry emission | Producer repository | UI or gateway heuristics |
| Access policy contract | `lotus-platform` plus domain owner declarations | Unreviewed route-local allowlists |
| Publication API | `lotus-gateway` | Product registry authority |
| Operator/customer discovery | `lotus-workbench` | Direct platform-file reads |
| Evidence-pack generation | `lotus-platform` | Manual spreadsheet/wiki assembly |
| Certification enforcement | `lotus-platform` CI and mesh gate | Untracked ad hoc scripts |

## Implementation Slices

### Slice 0: Baseline Audit And Maturity Matrix

1. audit current product declarations, telemetry snapshots, gateway APIs, Workbench discovery, and
   mesh certification gates,
2. produce `generated/enterprise-mesh-maturity-matrix.json` and `.md` by repository and product,
3. classify each product as `certified_first_wave`, `candidate`, `consumer_only`,
   `not_mesh_participant`, or `deferred`,
4. define the exact products that will be promoted into the enterprise maturity wave,
5. document why any repo remains outside the wave,
6. add tests proving the maturity matrix includes every Lotus repo and rejects ambiguous
   participation.

Exit gate:

1. maturity matrix exists,
2. no repo is ambiguously in or out,
3. implementation scope is explicit before code changes begin,
4. generated matrix is reproducible and test-protected.

### Slice 1: Self-Service Product Onboarding Kit

1. add repo-native declaration scaffold templates,
2. add telemetry fixture/scaffold templates,
3. add SLO/access policy templates,
4. add product onboarding checklist generator,
5. add validation command that checks the full onboarding bundle,
6. add generated checklist output for producer, consumer, gateway, Workbench, telemetry, SLO,
   access, evidence, lifecycle, tests, and docs,
7. add tests proving a valid scaffold passes and incomplete scaffolds fail.

Exit gate:

1. a domain team can scaffold a new product without copying from another repo by hand,
2. incomplete products fail with actionable errors,
3. templates use governed vocabulary and platform contracts,
4. onboarding output tells the domain team exactly which files and commands are required.

### Slice 2: Runtime Telemetry Emission And Collection

1. define runtime telemetry emission adapters or repo-local generation hooks,
2. implement first-wave live emission or deterministic runtime collection in at least
   `lotus-core`, `lotus-performance`, `lotus-risk`, and `lotus-advise`,
3. add platform collection or ingestion automation,
4. add tests proving runtime evidence includes product identity, service version, environment,
   freshness, completeness, reconciliation, quality, lineage, blocking, and source evidence,
5. update the mesh certification gate to prefer runtime evidence over static fixtures when both are
   available,
6. include deterministic local-mode generation so developers can prove telemetry without a long
   running production stack.

Exit gate:

1. runtime evidence can be generated from repo-native commands,
2. platform can collect or consume it,
3. certification output records the evidence source,
4. static fixture fallback is explicit and cannot masquerade as live runtime evidence.

### Slice 3: Mesh SLO Policy And Operational Drift Enforcement

1. add `platform-contracts/mesh-slo/`,
2. define per-product thresholds for freshness, completeness, reconciliation, quality, lineage,
   certification age, and evidence retention,
3. validate policies against product declarations and telemetry,
4. extend mesh certification to flag SLO drift,
5. add escalation owner, severity, and remediation metadata,
6. add generated SLO drift reports,
7. define which SLO violations are advisory and which are blocking.

Exit gate:

1. every maturity-wave product has an SLO policy,
2. SLO violations are visible in certification output,
3. escalation ownership is explicit,
4. blocking SLO violations fail the enterprise mesh gate.

### Slice 4: Access Governance And Entitled Discovery

1. add `platform-contracts/mesh-access/`,
2. define tenant, role, consumer, and use-case policy structure,
3. extend gateway discovery APIs to return access posture for the caller context,
4. extend Workbench discovery to show accessible, requestable, restricted, and blocked states,
5. add tests proving unauthorized products are not presented as usable,
6. add audit metadata showing why access is allowed or denied,
7. define an operator override path for break-glass diagnostics without exposing restricted
   customer-facing details.

Exit gate:

1. discovery is no longer one-size-fits-all,
2. access policy is explainable and test-protected,
3. gateway remains a policy publisher, not a product authority,
4. restricted visibility cannot hide unhealthy mesh posture from operators.

### Slice 5: Certification History And Customer Evidence Packs

1. add `platform-contracts/mesh-evidence/`,
2. persist certification history records as derived artifacts,
3. generate customer/auditor evidence pack manifests,
4. include product identity, owner repo, version, source declarations, telemetry evidence, SLO
   posture, access posture, dependency graph, certification state, and validation lanes,
5. expose evidence pack manifests through gateway where permitted,
6. add Workbench evidence-pack affordance for authorized users,
7. classify evidence fields by `public_customer`, `restricted_customer`, `operator_only`, and
   `internal_only`.

Exit gate:

1. evidence is durable across runs,
2. a customer-review pack can be generated without manual assembly,
3. evidence packs do not leak restricted product details to unauthorized users,
4. evidence-pack tests prove restricted fields are filtered.

### Slice 6: Broader Product Rollout And Lifecycle Governance

1. promote selected `lotus-report`, `lotus-manage`, and appropriate additional products into the
   maturity wave,
2. decide `lotus-ai` posture explicitly:
   - producer if it owns a stable governed AI product,
   - consumer if it consumes mesh products,
   - non-participant if neither is true,
3. enforce lifecycle states: active, preview, deprecated, replaced, blocked, retired,
4. enforce compatibility and consumer-impact checks for product version changes,
5. add deprecation/replacement tests and docs,
6. extend the certification gate to block unsafe lifecycle drift,
7. define consumer notification and migration evidence for deprecated/replaced products.

Exit gate:

1. maturity wave includes more than the original first-wave products,
2. lifecycle and compatibility changes are governed,
3. consumers are protected from silent breaking changes,
4. promoted products have runtime, SLO, access, evidence, and lifecycle proof.

### Slice 7: Enterprise Mesh Certification Gate

1. extend RFC-0089/RFC-0090 gate coverage to include runtime evidence preference, SLO policy,
   access policy, evidence history, lifecycle governance, and broader rollout products,
2. add advisory and blocking modes for each maturity check family,
3. update GitHub workflow artifacts and summary for maturity checks,
4. add tests for passing, warning, and blocking conditions,
5. verify the gate remains modular and does not become a monolithic script,
6. publish a concise operator status taxonomy for telemetry, SLO, access, lifecycle, evidence,
   gateway, and Workbench failures.

Exit gate:

1. enterprise maturity checks are enforced in local and GitHub gates,
2. operators can distinguish telemetry, SLO, access, lifecycle, gateway, and Workbench failures,
3. gate implementation remains maintainable and testable,
4. the GitHub workflow uploads enterprise maturity artifacts on success and failure.

### Slice 8: Code Review, API Certification, And Governance Tightening

This slice is mandatory and second-last.

1. review all APIs against the certification pattern,
2. verify gateway remains publication and policy face, not product authority,
3. verify Workbench consumes gateway/BFF only,
4. verify product contracts remain repo-native and platform-governed,
5. remove duplicate/dead/onboarding-copy logic,
6. split any monolithic automation into clear modules,
7. verify tests are high-value and fail on meaningful drift,
8. run local feature lane, PR Merge Gate, and cross-repo mesh gate,
9. review whether the maturity wave creates new security or privacy obligations,
10. review whether the enterprise mesh gate needs to be split into new modules before merge,
11. review generated artifacts and confirm none are manually edited source truth.

Exit gate:

1. APIs follow the certification pattern,
2. platform governance is satisfied,
3. codebase is cleaner and more modular than before the RFC,
4. no duplicate mesh authority exists,
5. privacy and evidence-pack leakage risks are explicitly reviewed.

### Slice 9: Documentation, Agent Context, Wiki Update, Skills Review, And Branch Hygiene

This slice is mandatory and final.

1. update RFC status and implementation evidence,
2. update runbooks for onboarding, runtime telemetry, SLOs, access governance, evidence packs, and
   lifecycle changes,
3. update platform context and repo-local contexts,
4. update wiki and operator/customer-facing documentation,
5. assess whether new skills are needed for mesh onboarding, SLO triage, or evidence-pack
   generation,
6. record a keep, tighten, add, remove, or no-change decision for skills/guidance,
7. update `LOTUS-SKILL-ROUTING-MAP.md` if the implementation creates repeatable enterprise mesh
   task routing,
8. update shared memory and remove stale active claims if agents worked in parallel,
9. complete PR evidence, merge readiness, and branch hygiene.

Exit gate:

1. future agents can implement and operate enterprise mesh without chat history,
2. operators can onboard, certify, troubleshoot, and export evidence,
3. branch and PR hygiene is complete,
4. skills/guidance decision is explicit,
5. documentation states what is customer-ready versus operator-only.

## Validation Plan

Required validation:

1. platform contract tests for new SLO, access, evidence, and lifecycle schemas,
2. maturity matrix generation and validation tests,
3. onboarding scaffold tests,
4. runtime telemetry emission tests in participating producer repos,
5. gateway API contract tests for access posture and evidence manifests,
6. Workbench unit and browser smoke tests for entitled discovery and evidence-pack states,
7. mesh certification gate tests for runtime evidence, SLO drift, access drift, lifecycle drift,
   and evidence history,
8. evidence-pack filtering tests for restricted fields,
9. local blocking cross-repo mesh certification,
10. GitHub cross-repo mesh certification workflow,
11. Feature Lane and PR Merge Gate in all touched repos.

Candidate platform commands:

```powershell
python -m pytest tests/unit/test_enterprise_mesh_*.py -q
python automation/generate_enterprise_mesh_maturity_matrix.py --check
python automation/mesh_certification_gate.py --mode blocking --generated-at-utc 2026-04-20T00:00:00Z --require-sibling-repos
powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane feature
powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane pr-merge
```

## Acceptance Criteria

RFC-0091 is complete when:

1. maturity matrix and product wave scope are explicit,
2. new data products can be scaffolded and validated through a governed self-service path,
3. maturity-wave products emit or generate runtime trust evidence through repo-native commands,
4. mesh SLO policy is validated and enforced,
5. access-governed discovery works through gateway and Workbench,
6. certification history and evidence packs can be generated and exposed safely,
7. broader product rollout includes selected non-first-wave products,
8. lifecycle, compatibility, deprecation, and replacement are enforced,
9. enterprise mesh certification runs locally and in GitHub,
10. at least one end-to-end evidence pack proves declaration, runtime evidence, SLO, access,
    lifecycle, gateway, Workbench, certification, and validation-lane posture,
11. Slice 8 and Slice 9 are completed according to `RFC-GOVERNANCE-STANDARD.md`.

## Non-Goals

This RFC does not:

1. replace domain repositories as product authorities,
2. make gateway the data-product registry,
3. require every Lotus repo to become a producer immediately,
4. expose restricted evidence to unauthorized users,
5. build a generic external data marketplace,
6. replace existing RFC-0084 through RFC-0090 controls.

## Risks And Mitigations

### Risk: Maturity Scope Becomes Too Broad

Mitigation:

1. require Slice 0 maturity matrix,
2. promote products in waves,
3. block ambiguous repo/product participation.

### Risk: Gateway Becomes Product Authority By Accident

Mitigation:

1. keep product truth repo-native,
2. add gateway contract tests proving it publishes platform evidence rather than inventing product
   truth,
3. include this in Slice 8 governance review.

### Risk: Access Governance Hides Operational Problems

Mitigation:

1. distinguish restricted visibility from unhealthy product state,
2. keep operator views capable of showing blocked/stale/deprecated states,
3. preserve audit evidence for access decisions.

### Risk: Evidence Packs Leak Sensitive Metadata

Mitigation:

1. add evidence-pack manifest policy,
2. classify evidence fields,
3. validate export eligibility by tenant, role, consumer, and use case.

### Risk: Mesh Gate Becomes A Monolith

Mitigation:

1. split validation families into modules,
2. keep tests per validation family,
3. keep the workflow as orchestration only.

## Skills And Guidance Assessment

Initial decision:

1. no new skill is created at RFC proposal time,
2. existing skills are sufficient for early implementation:
   - `lotus-backend-delivery-governance`,
   - `lotus-frontend-delivery-governance`,
   - `lotus-pr-premerge-gate`,
   - `lotus-rfc-review-loop`,
   - `github:gh-fix-ci`,
3. Slice 9 must consciously reassess whether enterprise mesh onboarding, SLO triage, or evidence
   pack generation should become a dedicated skill or explicit skill-routing row.

## Next Actions

1. review RFC-0091 for scope and sequencing,
2. decide first maturity-wave products and repos in Slice 0,
3. implement Slice 1 only after Slice 0 scope is approved.
