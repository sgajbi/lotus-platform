# RFC-0090 - Cross-Repo Mesh Certification PR Merge Gate

| Field | Value |
| --- | --- |
| Status | Implemented |
| Created | 2026-04-20 |
| Last Updated | 2026-04-20 |
| Owners | lotus-platform architecture; CI governance; domain repository maintainers; lotus-gateway maintainers; lotus-workbench maintainers |
| Depends On | RFC-0072; RFC-0084; RFC-0085; RFC-0086; RFC-0087; RFC-0088; RFC-0089 |
| Related Standards | `RFC-GOVERNANCE-STANDARD.md`; `RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`; `Continuous Integration, Validation, and Release Governance Standard.md` |
| Scope | Cross-repo CI enforcement |

## Executive Summary

RFC-0089 implemented the mesh certification gate as a real platform control. The gate can run in
blocking mode locally when sibling repositories are checked out next to `lotus-platform`, and
platform CI runs an advisory smoke that does not require those sibling repositories.

The remaining operational gap is GitHub enforcement.

RFC-0090 will make the RFC-0089 blocking mesh certification gate runnable as a GitHub PR Merge Gate
workflow by checking out the first-wave producer repositories, `lotus-gateway`, and
`lotus-workbench` next to `lotus-platform`, running the gate in blocking mode, and uploading the
operator artifacts for review.

This is not a new mesh concept. It is the CI enforcement layer that makes the existing mesh gate
harder to bypass.

## Original Requested Requirements

The user intent preserved in this RFC is:

1. do not reopen RFC-0089 after it has been implemented, merged, and closed unless the missing work
   belongs inside its existing boundary,
2. create a new RFC if the remaining work is a distinct implementation program,
3. make the next step implementation-bearing, not documentation-only,
4. turn RFC-0089's local blocking proof into GitHub blocking proof,
5. preserve the mandatory second-last code review/API-certification/governance slice and final
   documentation/context/wiki/skills/branch-hygiene slice.

## Current Implementation Reality

Overall classification: `RFC-0089 implemented; GitHub cross-repo blocking orchestration not yet implemented`

Implemented today:

1. `automation/mesh_certification_gate.py`
   Runs advisory or blocking mesh certification.
2. `automation/Invoke-PlatformRepoChecks.ps1`
   Runs an advisory mesh gate smoke in platform CI.
3. Local blocking command:
   `python automation/mesh_certification_gate.py --mode blocking --generated-at-utc 2026-04-20T00:00:00Z --require-sibling-repos`
4. Operator artifacts:
   `output/mesh-certification/mesh-certification-status.json`,
   `output/mesh-certification/mesh-certification-status.md`, and
   `output/mesh-certification/mesh-certification-issues.json`.

Gap:

1. GitHub's `lotus-platform` checkout does not include sibling repositories,
2. the GitHub PR Merge Gate therefore runs advisory mesh certification, not blocking cross-repo
   mesh certification,
3. operator artifacts are generated locally but not uploaded by a dedicated cross-repo workflow.

## Requirement-to-Implementation Traceability

| Requirement | Current evidence | Current status | RFC-0090 response |
| --- | --- | --- | --- |
| Run mesh certification in GitHub blocking mode | RFC-0089 local blocking command exists | Not satisfied in GitHub | Add multi-repo checkout workflow and run RFC-0089 gate with `--require-sibling-repos` |
| Keep producer/gateway/workbench ownership clear | RFC-0089 gate inspects sibling evidence but writes only platform artifacts | Partially satisfied | Workflow checks out sibling repos read-only and writes artifacts only under platform workflow output |
| Make failures reviewable from GitHub | RFC-0089 writes local operator artifacts | Partially satisfied | Upload mesh certification status, Markdown, and issues as workflow artifacts |
| Support coordinated cross-repo branches without making it mandatory | Current local proof can use any checked-out branch | Not formalized | Start with sibling `main`; add explicit optional branch override inputs |
| Preserve closure discipline | RFC-GOVERNANCE-STANDARD exists | Satisfied in RFC shape | Include mandatory Slice 7 and Slice 8 |

## Design Reasoning And Trade-offs

### Why this is RFC-0090 instead of another RFC-0089 slice

RFC-0089 is already implemented, merged, and closed. Its acceptance criteria were met for
first-wave local blocking enforcement and platform advisory CI. GitHub multi-repo orchestration is a
distinct CI-enforcement enhancement with its own operational risks:

1. authentication and repository access,
2. branch selection across repositories,
3. artifact upload,
4. workflow runtime and flake posture.

Keeping this as RFC-0090 avoids blurring the already closed RFC-0089 implementation boundary.

### Why start with sibling `main`

The first GitHub implementation should validate `lotus-platform` changes against the current
`main` branch of sibling repos. That gives a stable baseline and avoids accidental branch-name
coupling.

Optional branch override inputs can be added for coordinated cross-repo PRs, but they should be
explicit rather than inferred.

### Why the workflow should call the existing gate

The workflow should not duplicate mesh certification logic. It should:

1. checkout repositories,
2. arrange sibling paths,
3. call `automation/mesh_certification_gate.py`,
4. upload artifacts,
5. fail or pass based on the existing gate exit code.

## Proposed Changes

### Decision

Add a platform-owned GitHub workflow for cross-repo mesh certification.

The workflow will:

1. checkout `lotus-platform`,
2. checkout first-wave sibling repos next to it:
   - `lotus-core`,
   - `lotus-performance`,
   - `lotus-risk`,
   - `lotus-advise`,
   - `lotus-gateway`,
   - `lotus-workbench`,
3. default sibling refs to `main`,
4. support manual branch override inputs for coordinated cross-repo validation,
5. run the RFC-0089 gate in blocking mode with `--require-sibling-repos`,
6. upload `output/mesh-certification/` artifacts,
7. document which checks are blocking and which are advisory.

### Trigger Model

Required initial triggers:

1. `pull_request` on `main` for `lotus-platform` changes touching:
   - `.github/workflows/`,
   - `automation/mesh_certification_gate.py`,
   - `automation/Invoke-PlatformRepoChecks.ps1`,
   - `platform-contracts/domain-data-products/`,
   - `platform-contracts/trust-telemetry/`,
   - `generated/domain-product-catalog.json`,
   - `generated/domain-product-dependency-graph.json`,
   - `rfcs/RFC-0089-*`,
   - `rfcs/RFC-0090-*`,
2. `workflow_dispatch` with optional sibling branch inputs.

Future triggers can be added in sibling repos after this platform-owned workflow is stable.

### Repository Checkout Contract

The workflow must use a deterministic sibling layout under the GitHub workspace:

| Repository | Checkout path | Default ref | Purpose |
| --- | --- | --- | --- |
| `sgajbi/lotus-platform` | `lotus-platform` | PR head | owns workflow, gate automation, and artifacts |
| `sgajbi/lotus-core` | `lotus-core` | `main` | `PortfolioStateSnapshot` telemetry |
| `sgajbi/lotus-performance` | `lotus-performance` | `main` | `ReturnsSeriesBundle` telemetry |
| `sgajbi/lotus-risk` | `lotus-risk` | `main` | `RiskMetricsReport` telemetry |
| `sgajbi/lotus-advise` | `lotus-advise` | `main` | `AdvisoryProposalLifecycleRecord` telemetry |
| `sgajbi/lotus-gateway` | `lotus-gateway` | `main` | domain-product publication route evidence |
| `sgajbi/lotus-workbench` | `lotus-workbench` | `main` | `/data-products` gateway/BFF consumption evidence |

The gate must run from `lotus-platform` with sibling paths exactly one directory above it, matching
RFC-0089's local blocking proof layout.

### Branch Override Inputs

Manual workflow dispatch should support optional refs:

1. `lotus_core_ref`,
2. `lotus_performance_ref`,
3. `lotus_risk_ref`,
4. `lotus_advise_ref`,
5. `lotus_gateway_ref`,
6. `lotus_workbench_ref`.

Empty inputs mean `main`.

Branch overrides must be explicit in the workflow summary. If an override ref does not resolve, the
workflow should fail before running the mesh gate so the failure is clearly checkout-related rather
than a certification failure.

### Artifact Contract

The workflow must upload:

1. `output/mesh-certification/mesh-certification-status.json`,
2. `output/mesh-certification/mesh-certification-status.md`,
3. `output/mesh-certification/mesh-certification-issues.json`.

The artifact name should include the workflow run id or commit SHA so multiple runs can be compared.

### Permissions And Security Contract

The workflow must use least privilege:

1. `contents: read` by default,
2. no write permissions,
3. no pull-request mutation permissions,
4. no secret-dependent behavior for public or internal read-only repository checkouts,
5. artifact upload limited to generated mesh certification files.

If private-repository access requires a token, the token must be read-only and documented as an
environment prerequisite rather than hardcoded into workflow YAML.

### Failure Semantics

The workflow should distinguish:

1. checkout failures,
2. Python/setup failures,
3. mesh certification failures,
4. artifact upload failures.

Mesh certification failures are product/governance failures and should preserve
`mesh-certification-status.json`, `.md`, and `mesh-certification-issues.json` for review.
Checkout or setup failures should be fixed as CI infrastructure issues and should not be described
as data-product certification failures.

### Step Summary Contract

The workflow should append a GitHub Actions step summary containing:

1. refs used for each repository,
2. gate mode,
3. certification state,
4. error, warning, and info counts,
5. artifact name,
6. fix-forward pointer to `docs/operations/mesh-certification-gate-runbook.md`.

## Implementation Slices

### Slice 0: Baseline And Workflow Contract

1. document workflow triggers, sibling repositories, default refs, and override inputs,
2. define artifact upload contract,
3. define failure semantics for missing repo checkout, missing telemetry, catalog drift, gateway
   drift, and Workbench drift,
4. define least-privilege workflow permissions and checkout path layout,
5. define GitHub Actions step summary expectations.

Exit gate:

1. CI contract is explicit,
2. artifact contract is explicit,
3. no mesh certification logic is duplicated in workflow YAML,
4. security and permissions posture is explicit.

### Slice 1: Multi-Repo Checkout Workflow

1. add a GitHub workflow that checks out `lotus-platform` plus required sibling repositories,
2. arrange the checkout layout so sibling repos sit next to `lotus-platform`,
3. use `actions/checkout` with least required permissions,
4. keep default refs on `main`,
5. support manual branch override inputs,
6. fail early with clear messaging when a requested ref cannot be checked out.

Exit gate:

1. workflow can checkout all required repositories,
2. sibling layout matches the RFC-0089 local blocking command assumptions,
3. workflow summary records the resolved refs.

### Slice 2: Blocking Mesh Certification Job

1. run `python automation/mesh_certification_gate.py --mode blocking --generated-at-utc <timestamp> --require-sibling-repos`,
2. preserve the exit code as the workflow pass/fail signal,
3. upload mesh certification artifacts on success and failure,
4. expose a concise GitHub Actions step summary,
5. ensure artifact upload still runs when the mesh gate fails.

Exit gate:

1. a failing mesh certification gate fails the GitHub workflow,
2. operator artifacts are available even on failure,
3. certification failures are distinguishable from checkout/setup failures.

### Slice 3: Path And Manual Trigger Hardening

1. restrict automatic PR runs to mesh-impacting platform paths,
2. keep `workflow_dispatch` available for manual cross-repo proof,
3. document when maintainers should run manual branch override validation,
4. make path filters explicit and test-protected.

Exit gate:

1. normal platform PRs are not slowed by unrelated cross-repo checkout,
2. mesh-impacting platform PRs receive blocking proof.

### Slice 4: Local And Workflow Tests

1. add workflow contract tests that verify required repos, branch inputs, artifact upload, and gate
   command are present,
2. add a documentation/governance test protecting RFC-0090's mandatory closure slices,
3. test least-privilege permissions and absence of write-token scopes,
4. test that artifact upload is configured with `if: always()` or equivalent,
5. run platform feature and PR-merge lanes.

Exit gate:

1. workflow structure is test-protected,
2. platform lanes are green,
3. workflow does not gain unnecessary permissions.

### Slice 5: Operator Runbook Update

1. update the mesh certification runbook with GitHub workflow usage,
2. document manual branch override examples,
3. document how to download and inspect workflow artifacts,
4. document fix-forward ownership by issue code,
5. document how to tell checkout/setup failures apart from mesh certification failures.

Exit gate:

1. an operator can run and debug the GitHub cross-repo gate without chat history.

### Slice 6: GitHub Workflow Proof And Evidence Capture

1. open the implementation PR from the feature branch,
2. verify the GitHub **Cross-Repo Mesh Certification Gate** runs for workflow or mesh-impacting
   platform changes,
3. confirm the uploaded artifact name and certification state are visible in PR evidence,
4. confirm checkout or setup failures are reported as CI infrastructure failures rather than mesh
   product failures,
5. fix-forward any workflow drift before marking the RFC implemented.

Exit gate:

1. GitHub can run the blocking cross-repo gate,
2. evidence is captured in PR checks or explicitly documented if the proof boundary depends on a
   pending GitHub run.

### Slice 7: Code Review, API Certification, And Governance Tightening

This slice is mandatory and second-last.

1. review workflow permissions, checkout refs, artifact upload behavior, and failure semantics,
2. confirm gateway and Workbench checks still follow the certification pattern and do not move
   product authority into gateway or UI,
3. confirm platform governance checks are aligned with RFC-0072,
4. remove duplicate or stale workflow logic,
5. confirm tests catch meaningful drift,
6. confirm generated artifacts are derived evidence and are not committed as source truth,
7. confirm the workflow calls `automation/mesh_certification_gate.py` rather than copying any gate
   logic into YAML.

Exit gate:

1. workflow is minimal, auditable, and maintainable,
2. API certification and platform governance expectations are satisfied,
3. no duplicate mesh certification logic exists outside `automation/mesh_certification_gate.py`.

### Slice 8: Documentation, Agent Context, Wiki Update, Skills Review, And Branch Hygiene

This slice is mandatory and final.

1. update RFC status and implementation evidence,
2. update platform context and repo-local context if workflow behavior changes,
3. update wiki and runbook surfaces,
4. assess whether skill routing or a new skill is needed for GitHub mesh certification failures,
5. record a keep, tighten, add, remove, or no-change decision for skills/guidance,
6. update `CONTEXT-REFERENCE-MAP.md` if new workflow paths or artifacts become durable routing
   targets,
7. complete truthful PR evidence, merge readiness, and branch cleanup.

Exit gate:

1. future agents can find and run the GitHub cross-repo mesh gate,
2. operators can inspect artifacts and fix failures,
3. branch and PR hygiene is complete,
4. skills/guidance decision is explicit even when the decision is no-change.

## Validation Plan

Required validation:

1. workflow contract tests,
2. RFC closure governance tests,
3. targeted mesh certification gate tests,
4. platform Feature Lane,
5. platform PR Merge Gate,
6. GitHub workflow proof for the new cross-repo gate.

Candidate commands:

```powershell
python -m pytest tests/unit/test_mesh_certification_gate.py tests/unit/test_rfc_closure_governance.py -q
python -m pytest tests/unit/test_mesh_certification_workflow.py -q
powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane feature
powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane pr-merge
```

## Acceptance Criteria

RFC-0090 is complete when:

1. GitHub can run the RFC-0089 mesh certification gate in blocking mode with required sibling repos,
2. automatic triggers cover mesh-impacting platform changes,
3. manual branch override inputs exist for coordinated cross-repo validation,
4. mesh certification artifacts are uploaded on success and failure,
5. workflow structure is covered by meaningful contract tests,
6. least-privilege workflow permissions are test-protected,
7. checkout/setup failures are distinguishable from mesh certification failures,
8. Slice 7 and Slice 8 are completed according to `RFC-GOVERNANCE-STANDARD.md`.

## Non-Goals

This RFC does not:

1. redefine RFC-0089 issue taxonomy,
2. change first-wave required products,
3. add new domain-product declarations,
4. require sibling repos to adopt the workflow immediately,
5. build a customer-facing discovery UI,
6. replace repo-native gateway or Workbench tests.

## Risks And Mitigations

### Risk: Multi-repo checkout slows normal platform PRs

Mitigation:

1. use path filters for automatic PR runs,
2. keep manual dispatch available,
3. do not attach the gate to unrelated platform-only changes.

### Risk: Branch overrides create misleading proof

Mitigation:

1. default every sibling repo to `main`,
2. require explicit manual inputs for non-main refs,
3. include refs in the GitHub step summary and uploaded artifact metadata where practical.

### Risk: Workflow duplicates certification logic

Mitigation:

1. keep all certification logic in `automation/mesh_certification_gate.py`,
2. use workflow tests to ensure the workflow calls the script rather than reimplementing checks.

## Skills And Guidance Assessment

Final decision:

1. no new skill is created for RFC-0090,
2. `lotus-pr-premerge-gate`, `github:gh-fix-ci`, `lotus-backend-delivery-governance`, and
   `lotus-rfc-review-loop` are sufficient for the first implementation,
3. `LOTUS-SKILL-ROUTING-MAP.md` is tightened to route RFC-0089/RFC-0090 mesh gate failures to the
   existing delivery, PR, RFC, and GitHub CI skills,
4. this is a conscious no-add decision: a dedicated mesh-certification skill should be created only
   if repeated GitHub failure patterns prove that the existing skill set is too broad.

## Implementation Status And Evidence

Implementation classification: `Implemented pending PR merge and GitHub check evidence`.

Implemented artifacts:

1. `.github/workflows/mesh-certification-gate.yml`
   Runs the cross-repo blocking mesh certification gate with read-only permissions, explicit
   sibling checkout layout, manual branch overrides, artifact upload, step summary, and delayed
   failure after artifact preservation.
2. `tests/unit/test_mesh_certification_workflow.py`
   Protects trigger paths, branch override inputs, sibling checkout layout, blocking gate command,
   absence of duplicated issue taxonomy in workflow YAML, artifact upload on failure, and summary
   failure semantics.
3. `tests/unit/test_workflow_security_validator.py` and
   `tests/unit/test_workflow_action_runtime_validator.py`
   Include the new workflow in platform workflow security and action-runtime baselines.
4. `docs/operations/mesh-certification-gate-runbook.md`
   Documents GitHub workflow usage, manual branch override examples, artifacts, and failure
   classification.

Local evidence captured before PR:

1. `python -m pytest tests/unit/test_mesh_certification_workflow.py tests/unit/test_workflow_security_validator.py tests/unit/test_workflow_action_runtime_validator.py -q`
2. `python automation/validate_workflow_security.py`
3. `python automation/validate_workflow_action_runtime.py`
4. `python automation/mesh_certification_gate.py --mode blocking --generated-at-utc 2026-04-20T00:00:00Z --require-sibling-repos`
   Certified in blocking mode with `0` errors, `0` warnings, and `0` info issues.
5. `python -m pytest tests/unit/test_mesh_certification_gate.py tests/unit/test_mesh_certification_workflow.py tests/unit/test_workflow_security_validator.py tests/unit/test_workflow_action_runtime_validator.py tests/unit/test_rfc_closure_governance.py -q`

Final implementation closure requires the RFC-0090 PR to run the GitHub
**Cross-Repo Mesh Certification Gate** and the normal platform Feature Lane and PR Merge Gate.

## Next Actions

1. open and verify the RFC-0090 implementation PR,
2. fix-forward any GitHub workflow, Feature Lane, or PR Merge Gate failures,
3. merge only after required checks are green and branch hygiene is complete.
