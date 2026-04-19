# RFC-0089 - Mesh Certification Merge Gate and Operational Trust Enforcement

| Field | Value |
| --- | --- |
| Status | Implemented |
| Created | 2026-04-20 |
| Last Updated | 2026-04-20 |
| Owners | lotus-platform architecture; domain repository maintainers; lotus-gateway maintainers; lotus-workbench maintainers |
| Depends On | RFC-0072; RFC-0084; RFC-0085; RFC-0086; RFC-0087; RFC-0088 |
| Related Standards | `RFC-GOVERNANCE-STANDARD.md`; `RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`; `RFC-0084-mesh-governance.md`; `RFC-0085-gateway-governed-domain-product-publication-and-trust-contracts.md`; `RFC-0086-repo-native-domain-product-onboarding-and-federated-rollout.md`; `RFC-0087-live-trust-telemetry-and-certification-plane.md`; `RFC-0088-self-serve-discovery-and-dependency-catalog.md`; `Continuous Integration, Validation, and Release Governance Standard.md` |
| Scope | Cross-repo implementation |

## Executive Summary

RFC-0084 through RFC-0088 made the first-wave Lotus mesh real:

1. domain products are governed,
2. product and consumer declarations are repo-native,
3. runtime trust telemetry can be certified,
4. gateway publishes catalog, dependency, and trust APIs,
5. Workbench exposes self-serve discovery.

The remaining gap is enforcement.

Today the mesh can be proven, but the strongest live trust certification is not yet a mandatory
merge gate across the participating repositories. That means a producer can drift, telemetry can go
missing, or certified trust posture can become stale without a consistent blocking signal.

RFC-0089 turns the first-wave mesh from a proven capability into an operational control:

1. cross-repo live trust certification becomes a governed validation lane,
2. certification output becomes a stable operator artifact,
3. gateway and Workbench contract drift becomes visible before merge,
4. stale, missing, blocked, unreconciled, or incomplete trust evidence is classified consistently,
5. the mesh posture becomes enforceable rather than merely discoverable.

## Original Requested Requirements

The user intent preserved in this RFC is:

1. continue after RFC-0085 through RFC-0088 are implemented and merged,
2. avoid another documentation-only RFC,
3. implement the next highest-value capability that makes Lotus more credible as a sellable mesh
   platform,
4. turn live trust certification into an enforceable operating gate,
5. preserve the RFC closure model: a second-last code review/API certification/governance slice and
   a final documentation/context/wiki/skills/branch-hygiene slice.

## Current Implementation Reality

Overall classification: `Implemented for first-wave mesh certification enforcement`

### Implemented foundation

1. `platform-contracts/domain-data-products/`
   Governs first-wave domain-product and consumer declarations.
2. `platform-contracts/domain-data-products/domain-product-source-manifest.v1.json`
   Records repo-native declaration sources for `lotus-core`, `lotus-performance`, `lotus-risk`,
   `lotus-advise`, `lotus-report`, and `lotus-manage`.
3. `automation/generate_domain_product_discovery.py`
   Regenerates the platform catalog and dependency graph from governed sources.
4. `automation/validate_trust_telemetry.py`
   Validates runtime telemetry snapshots against governed product and trust vocabulary.
5. `automation/generate_live_trust_certification.py`
   Generates live trust certification artifacts from telemetry snapshots.
6. `lotus-gateway` PR #136
   Publishes domain-product catalog, detail, dependency graph, and live trust certification APIs.
7. `lotus-workbench` PR #97
   Publishes `/data-products` as the self-serve discovery and trust posture UI.
8. `lotus-platform` PR #150
   Adds the RFC closure governance standard and marks RFC-0085 through RFC-0088 implemented.

### What is now implemented

1. `automation/mesh_certification_gate.py`
   Runs the RFC-0089 mesh certification gate in `advisory` or `blocking` mode.
2. `automation/Invoke-PlatformRepoChecks.ps1`
   Runs an advisory mesh certification smoke as part of the platform repo checks.
3. `output/mesh-certification/`
   Receives generated operator artifacts:
   - `mesh-certification-status.json`,
   - `mesh-certification-status.md`,
   - `mesh-certification-issues.json`.
4. `tests/unit/test_mesh_certification_gate.py`
   Protects certified, missing, stale, advisory, artifact rendering, gateway drift, and Workbench
   drift behavior.
5. `docs/operations/mesh-certification-gate-runbook.md`
   Documents commands, outputs, issue codes, and fix-forward actions.

### Implementation boundary and future hardening

1. platform CI runs the gate in advisory mode because GitHub's platform-only checkout does not
   include sibling producer, gateway, or Workbench repositories,
2. local and PR evidence must include the blocking command with sibling repositories when the
   change affects first-wave telemetry, gateway publication, or Workbench discovery,
3. future hardening can add multi-repo checkout orchestration to run blocking mode directly in
   GitHub PR Merge Gate for cross-repo mesh changes.

## Requirement-to-Implementation Traceability

| Requirement | Current evidence | Current status | RFC-0089 response |
| --- | --- | --- | --- |
| Enforce live trust certification before relevant changes merge | `automation/mesh_certification_gate.py`; blocking local proof command | Satisfied for first-wave local proof and advisory platform lane | Future hardening may add GitHub multi-repo blocking orchestration |
| Make operational status visible | `output/mesh-certification/mesh-certification-status.json`; `.md`; `mesh-certification-issues.json` | Satisfied | Operator artifacts are generated from one status object |
| Prevent gateway/Workbench drift | Gateway and Workbench drift checks in `automation/mesh_certification_gate.py` | Satisfied at contract-presence level | Deeper behavior stays in repo-native gateway/workbench tests |
| Keep this implementation-bearing | Gate automation, tests, platform check entrypoint, runbook, context/wiki updates | Satisfied | RFC-0089 is implemented |
| Preserve second-last and final closure slices | Slice 7 and Slice 8 evidence recorded in this RFC and PR evidence | Satisfied | Closure model is preserved |

## Design Reasoning and Trade-offs

### Why this is a new RFC

RFC-0087 created the live trust certification plane. RFC-0089 governs enforcement of that plane.
Keeping enforcement separate avoids reopening an already implemented RFC and gives merge-gate
behavior its own acceptance criteria.

### Why platform should own the gate

The gate crosses repository boundaries. No producer repository can independently know whether:

1. all first-wave telemetry snapshots are present,
2. generated catalog and dependency graph are current,
3. gateway can publish the resulting trust posture,
4. Workbench is still consuming gateway rather than platform files.

`lotus-platform` is the right owner because it already owns cross-repo validation, CI governance,
and generated mesh artifacts.

### Why the first enforcement lane should be narrow

The first version should enforce the first-wave mesh products only. It should not try to certify
every future product family or external API before the enforcement contract is stable.

The first-wave included producers are:

1. `lotus-core`
2. `lotus-performance`
3. `lotus-risk`
4. `lotus-advise`

The first-wave included consumers/publication surfaces are:

1. generated platform catalog and dependency graph,
2. gateway domain-product APIs,
3. Workbench `/data-products`.

## Proposed Changes

### Decision

Lotus will add a platform-owned mesh certification merge gate and operational trust report.

The gate will:

1. validate repo-native domain-product declarations,
2. validate first-wave producer telemetry snapshots,
3. generate live trust certification,
4. fail when required products have missing, stale, blocked, incomplete, unreconciled, or invalid
   trust posture,
5. verify gateway and Workbench publication/consumption posture at the contract level,
6. publish human-readable and machine-readable operator status artifacts.

### First-wave required certification set

RFC-0089 does not make every catalog product blocking on day one. The blocking gate applies to the
first-wave products that already have live telemetry snapshots and are part of the current
end-to-end proof:

| Product id | Producer repository | Required evidence | Blocking posture |
| --- | --- | --- | --- |
| `lotus-core:PortfolioStateSnapshot:v1` | `lotus-core` | repo-native declaration; telemetry snapshot; live trust certification | Required |
| `lotus-performance:ReturnsSeriesBundle:v1` | `lotus-performance` | repo-native declaration; telemetry snapshot; live trust certification | Required |
| `lotus-risk:RiskMetricsReport:v1` | `lotus-risk` | repo-native declaration; telemetry snapshot; live trust certification | Required |
| `lotus-advise:AdvisoryProposalLifecycleRecord:v1` | `lotus-advise` | repo-native declaration; telemetry snapshot; live trust certification | Required |

The gate may report advisory findings for the broader generated catalog, but it must not fail a PR
for products outside this first-wave set until those products are deliberately promoted into the
blocking certification set.

### Gate input contract

The implementation should treat these inputs as authoritative:

1. source manifest:
   `platform-contracts/domain-data-products/domain-product-source-manifest.v1.json`,
2. generated catalog:
   `generated/domain-product-catalog.json`,
3. generated dependency graph:
   `generated/domain-product-dependency-graph.json`,
4. trust telemetry contract:
   `platform-contracts/trust-telemetry/`,
5. first-wave telemetry snapshots from sibling repositories:
   `../lotus-core/contracts/trust-telemetry/`,
   `../lotus-performance/contracts/trust-telemetry/`,
   `../lotus-risk/contracts/trust-telemetry/`, and
   `../lotus-advise/contracts/trust-telemetry/`,
6. live trust certification output from `automation/generate_live_trust_certification.py`,
7. gateway publication evidence from the domain-product route family,
8. Workbench consumption evidence from the `/data-products` gateway/BFF-only surface.

The gate must compose existing validators and generators where possible. It should not reimplement
domain-product declaration parsing, trust telemetry schema validation, or live certification logic.

### Public artifacts

Recommended generated outputs:

1. `output/mesh-certification/mesh-certification-status.json`
2. `output/mesh-certification/mesh-certification-status.md`
3. `output/mesh-certification/mesh-certification-issues.json`

The status artifact should include:

1. generated timestamp,
2. certification state,
3. included repositories,
4. product counts,
5. certified product count,
6. attention-required product count,
7. stale telemetry count,
8. blocked product count,
9. missing telemetry count,
10. issue list grouped by producer repository and product id,
11. source artifact paths,
12. validation lane and gate mode.

### Operator status schema floor

The JSON operator status artifact should have a stable minimum shape:

| Field | Purpose |
| --- | --- |
| `contract_id` | Stable artifact family id, expected to be `lotus-mesh-certification-status` |
| `contract_version` | Status artifact schema version |
| `generated_at_utc` | Deterministic generation timestamp |
| `gate_mode` | `advisory` or `blocking` |
| `certification_state` | Overall state: `certified`, `certified_with_warnings`, or `failed` |
| `required_products` | First-wave blocking product set with producer repository and certification state |
| `summary` | Product and issue counts by severity and category |
| `issues` | Stable issue list using the RFC-0089 taxonomy |
| `source_artifacts` | Paths to the manifest, catalog, graph, telemetry inputs, and live trust artifacts |

The Markdown artifact should be generated from the same in-memory result as the JSON artifact so the
human-readable and machine-readable views cannot drift.

### Gate modes

The implementation should support explicit modes:

1. `advisory`
   Report issues but do not fail the lane. Use only during initial rollout or local diagnosis.
2. `blocking`
   Fail on missing, invalid, stale, blocked, unreconciled, incomplete, or quality-failed trust
   posture for required first-wave products.

The RFC target is `blocking` mode for the first-wave required products.

### Required classification model

The gate should classify issues with stable codes:

1. `missing_telemetry`
2. `invalid_telemetry`
3. `stale_telemetry`
4. `product_blocked`
5. `completeness_attention_required`
6. `reconciliation_attention_required`
7. `data_quality_attention_required`
8. `lineage_not_materialized`
9. `catalog_drift`
10. `gateway_publication_drift`
11. `workbench_consumption_drift`

Each issue must carry:

1. severity,
2. producer repository,
3. product id when applicable,
4. remediation summary,
5. source evidence path.

Severity semantics:

1. `error`
   Fails blocking mode.
2. `warning`
   Does not fail advisory mode and should not fail blocking mode unless attached to a required
   first-wave product rule that explicitly promotes it.
3. `info`
   Records non-blocking context such as products outside the first-wave blocking set.

### Cross-repo boundary rules

The platform gate must keep ownership boundaries clean:

1. producer repositories own telemetry snapshots and product truth,
2. `lotus-platform` owns the certification gate, issue taxonomy, and operator artifacts,
3. `lotus-gateway` owns API publication and must not become the product registry,
4. `lotus-workbench` owns presentation and must consume gateway/BFF APIs only,
5. the platform gate may inspect contract evidence in sibling repos, but it must not write into
   those repos.

Gateway and Workbench drift checks should be contract-presence checks, not duplicate test suites.
If deeper behavioral proof is needed, the gate should call repo-native tests or require PR evidence
rather than reimplementing those services inside `lotus-platform`.

### CI integration

The platform Feature Lane should run a fast check over checked-in fixtures and generated artifact
drift.

The PR Merge Gate should run the blocking certification gate when:

1. platform mesh automation changes,
2. domain-product contracts change,
3. trust telemetry contracts change,
4. first-wave producer telemetry snapshots change,
5. gateway domain-product publication code changes,
6. Workbench domain-product discovery code changes.

The first implementation can use path-based triggering plus an explicit manual command. Full
multi-repo checkout orchestration may be added in a later hardening slice if GitHub workflow
complexity would make the first implementation brittle.

## Implementation Slices

### Slice 0: Baseline And Gate Contract

1. define the gate contract and issue taxonomy,
2. identify first-wave required product ids and repositories,
3. document advisory versus blocking behavior,
4. lock the operator status schema floor,
5. document the explicit non-blocking catalog products that remain advisory-only.

Exit gate:

1. required product set is explicit,
2. gate failure semantics are clear,
3. schema and issue-code stability are test-protected.

### Slice 1: Platform Mesh Certification Gate

1. add platform automation to run declaration validation, discovery drift check, telemetry
   validation, and live certification generation as one gate,
2. add blocking/advisory mode,
3. add issue classification and exit-code behavior,
4. add high-value unit tests for certified, stale, blocked, missing, and invalid telemetry paths,
5. keep the implementation modular: input discovery, validation orchestration, issue
   classification, status rendering, and CLI exit behavior should be separately testable.

Exit gate:

1. the gate can certify the current first-wave mesh,
2. meaningful failures produce actionable issue codes and remediation text,
3. implementation code does not duplicate existing validators.

### Slice 2: Operator Status Artifacts

1. generate machine-readable and Markdown status artifacts,
2. summarize product, producer, issue, and timestamp posture,
3. include source artifact provenance,
4. make JSON the canonical generated status artifact and Markdown a rendered view.

Exit gate:

1. an operator can tell whether the mesh is certified without reading raw telemetry snapshots,
2. automation can consume the JSON status deterministically,
3. JSON and Markdown status agree in tests.

### Slice 3: CI And Path-Based Enforcement

1. wire the gate into platform validation commands,
2. add GitHub workflow integration for relevant path changes,
3. document which lane is advisory and which lane is blocking,
4. update local and CI command evidence so failure modes are reproducible outside GitHub.

Exit gate:

1. relevant platform changes make mesh certification drift CI-visible,
2. blocking mode is available for PR Merge Gate use.

### Slice 4: Gateway Publication Drift Check

1. add a platform-level check that gateway exposes the required domain-product route family,
2. verify OpenAPI or contract evidence for catalog, detail, dependency graph, and trust
   certification endpoints,
3. avoid duplicating gateway tests; the platform check should verify publication presence and
   contract discoverability,
4. fail with `gateway_publication_drift` only when expected contract evidence is missing or stale.

Exit gate:

1. gateway publication drift is visible from the platform gate,
2. gateway remains API publication face only.

### Slice 5: Workbench Consumption Drift Check

1. add a platform-level check that Workbench `/data-products` exists,
2. verify Workbench uses BFF/gateway discovery APIs rather than platform files,
3. ensure degraded trust states remain tested in Workbench,
4. fail with `workbench_consumption_drift` when platform-file coupling or missing discovery surface
   is detected.

Exit gate:

1. direct platform-file UI consumption is prevented,
2. Workbench discovery remains gateway-first and trust-state truthful.

### Slice 6: Runbook And Fix-Forward Workflow

1. document how to refresh telemetry, regenerate live certification, inspect failures, and fix
   stale trust posture,
2. include examples for common failures,
3. connect the runbook to context and repository-local docs.

Exit gate:

1. an engineer can fix a failed mesh certification gate without chat history,
2. the runbook points to owning repositories and commands.

### Slice 7: Code Review, API Certification, And Governance Tightening

This slice is mandatory.

1. review the gate automation for unnecessary complexity, duplicate validation, stale path logic,
   and weak failure messages,
2. confirm gateway and Workbench API surfaces follow the endpoint certification pattern where the
   gate depends on them,
3. confirm OpenAPI, vocabulary, contract, and platform-governance checks are aligned,
4. remove dead or transitional gate logic,
5. review test quality and expand only where it catches real drift.

Exit gate:

1. the certification gate is maintainable and modular,
2. API certification and platform governance expectations are satisfied,
3. no known duplicate or dead mesh enforcement logic remains.

### Slice 8: Documentation, Agent Context, Wiki Update, Skills Review, And Branch Hygiene

This slice is mandatory.

1. update platform docs, context, and reference maps for the mesh certification gate,
2. update gateway, Workbench, and producer repo context only where operational behavior changed,
3. update wiki/runbook content for operators,
4. consciously assess whether skills or routing guidance need to change for mesh certification work,
5. record keep, tighten, add, remove, or no-change decisions for skills/guidance,
6. complete truthful PR evidence and branch hygiene.

Exit gate:

1. future agents can find and run the mesh certification gate,
2. operator documentation explains how to respond to failures,
3. branch and PR hygiene is complete,
4. any no-change decision for skills or context is explicit.

## Validation Plan

Required validation:

1. unit tests for gate issue classification,
2. unit tests for operator status artifact generation,
3. drift tests for generated catalog and live trust certification,
4. platform feature lane,
5. platform PR Merge Gate,
6. targeted gateway contract tests if gateway publication checks change,
7. targeted Workbench unit tests if discovery consumption checks change.

Candidate platform commands:

```powershell
python -m pytest tests/unit/test_mesh_certification_gate.py -q
python automation/mesh_certification_gate.py --mode blocking
powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane feature
```

## Acceptance Criteria

RFC-0089 is complete when:

1. platform owns a repeatable mesh certification gate,
2. the gate validates first-wave declarations, telemetry, live trust certification, gateway
   publication, and Workbench consumption posture,
3. blocking mode fails on required missing, stale, invalid, blocked, incomplete, unreconciled, or
   quality-failed trust evidence,
4. operator status artifacts are generated and documented,
5. CI integration makes mesh certification drift visible,
6. Slice 7 and Slice 8 are completed according to `RFC-GOVERNANCE-STANDARD.md`.

Current status: all acceptance criteria are met for the first-wave implementation boundary.

## Evidence Required Before Marking Implemented

The implementation PR must include or link:

1. local targeted unit test output for the mesh certification gate,
2. platform Feature Lane output,
3. platform PR Merge Gate output,
4. a successful blocking-mode run over the current first-wave telemetry snapshots,
5. generated operator status JSON and Markdown paths,
6. gateway publication drift-check evidence,
7. Workbench consumption drift-check evidence,
8. Slice 7 review notes showing API certification and platform-governance decisions,
9. Slice 8 documentation/context/wiki/skills/branch-hygiene notes.

## Implementation Closure Evidence

Implementation evidence:

1. targeted gate tests:
   `python -m pytest tests/unit/test_mesh_certification_gate.py -q`,
2. live-trust regression tests:
   `python -m pytest tests/unit/test_live_trust_certification.py -q`,
3. RFC closure governance tests:
   `python -m pytest tests/unit/test_rfc_closure_governance.py -q`,
4. static checks:
   `python -m ruff check automation tests`,
5. local blocking proof:
   `python automation/mesh_certification_gate.py --mode blocking --generated-at-utc 2026-04-20T00:00:00Z --require-sibling-repos`,
6. feature lane:
   `powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane feature`.

Slice 7 review outcome:

1. API certification pattern is preserved by checking gateway publication contract evidence rather
   than moving product authority into gateway,
2. Workbench governance is preserved by checking gateway/BFF-only discovery consumption and
   rejecting direct platform-file coupling,
3. platform governance is preserved by composing existing validators and keeping generated
   artifacts derived from product, telemetry, and certification inputs,
4. no duplicate schema validator or duplicate gateway/workbench test suite was introduced.

Slice 8 closure outcome:

1. platform docs now include `docs/operations/mesh-certification-gate-runbook.md`,
2. automation README documents advisory and blocking gate commands,
3. central context and wiki surfaces point to the mesh certification gate,
4. skills guidance was consciously assessed; no new skill is created in this slice because existing
   backend governance, PR pre-merge, RFC review, and QA validation skills cover the work until
   repeated operational failure patterns justify a dedicated skill.

## Non-Goals

This RFC does not:

1. redefine domain-product declarations,
2. replace RFC-0087 telemetry contracts,
3. make every future domain product mandatory in the first gate,
4. build a polished customer-facing dashboard,
5. move product truth into gateway or Workbench,
6. require full external API lifecycle management.

## Risks And Mitigations

### Risk: Cross-repo checkout orchestration becomes brittle

Mitigation:

1. start with deterministic sibling-repo paths and path-triggered CI,
2. keep the first gate narrow,
3. add heavier orchestration only after the simple gate is stable.

### Risk: The gate blocks too much too early

Mitigation:

1. support advisory mode,
2. use blocking mode only for explicitly required first-wave products,
3. classify warnings versus errors clearly.

### Risk: The gate duplicates existing validators

Mitigation:

1. compose existing validators rather than reimplementing schema checks,
2. keep issue aggregation and operator reporting as the new value.

## Skills And Guidance Assessment

Expected guidance change:

1. `CONTEXT-REFERENCE-MAP.md` should link the gate automation and status artifacts once they exist,
2. `LOTUS-ENGINEERING-CONTEXT.md` should describe the gate as the operating control for mesh trust,
3. `LOTUS-SKILL-ROUTING-MAP.md` may need a more explicit route for mesh certification work if this
   becomes a repeated operational task.

Initial no-change decision:

1. no new skill is created at RFC proposal time,
2. existing backend governance, PR pre-merge, RFC review, and QA validation skills are sufficient
   for the first implementation,
3. a dedicated mesh-certification skill should be considered only after the gate has real repeated
   use and failure patterns.

## Next Actions

1. use the blocking local proof command whenever first-wave telemetry, gateway publication, or
   Workbench discovery changes,
2. consider GitHub multi-repo checkout orchestration if cross-repo mesh changes become frequent
   enough to justify a heavier PR Merge Gate,
3. promote additional products into the blocking set only after they have repo-native telemetry
   snapshots and an explicit acceptance decision.
