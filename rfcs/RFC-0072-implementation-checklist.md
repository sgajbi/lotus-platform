# RFC-0072 Implementation Checklist

- Rollout Status: In Progress
- Governing RFC: `rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`

## Goal

Turn RFC-0072 into one explicit, platform-owned CI and validation operating model for all Lotus repositories.

## Slice Tracker

| Slice | Outcome | Status | Notes |
| --- | --- | --- | --- |
| Slice 1 | Governance and documentation foundation | Complete | RFC, standard, implementation checklist, lane mapping baseline, and branch-protection expectations are documented in `lotus-platform` |
| Slice 1A | Scaffold baseline definition | Complete | Current scaffold source of truth is identified in `lotus-platform`; future scaffold convergence remains a later implementation slice |
| Slice 2 | Repository workflow classification and gap audit | Complete | Current-state versus target-state gap inventory now exists across the Lotus estate |
| Slice 3 | Standardized workflow convergence | Complete | Application and service repositories are converged to explicit lane workflows; remaining platform-repo and branch-protection enforcement work moves to later governance slices |
| Slice 3A | Skill and developer-process alignment | Complete | Codex skills for backend delivery, frontend delivery, and pre-merge flow align to RFC-0072 |
| Slice 3B | Scaffold and template convergence | Complete | Backend scaffold now emits explicit feature, PR merge, and main releasability workflows by default |
| Slice 3C | Backend rollout wave 1 (`lotus-manage`, `lotus-report`) | Complete | Both repos now use explicit feature, PR merge, and main releasability workflows, with governance policy updated accordingly |
| Slice 3D | Experience-layer rollout wave (`lotus-gateway`, `lotus-workbench`) | Complete | Both repos now use explicit feature, PR merge, and main releasability workflows; `lotus-gateway` also exposes an explicitly named platform validation lane |
| Slice 3E | Analytics-domain rollout wave (`lotus-performance`, `lotus-risk`) | Complete | Both repos now use explicit feature, PR merge, and main releasability workflows; repo-native `make ci` contracts were tightened to be security-truthful and deterministic |
| Slice 3F | Shared capability rollout wave (`lotus-ai`) | Complete | `lotus-ai` now uses explicit feature, PR merge, and main releasability workflows; repo-native `make ci` now includes project-scoped dependency health, security audit, runtime-mode smoke, coverage, and Docker validation |
| Slice 3G | Advisory-domain rollout wave (`lotus-advise`) | Complete | `lotus-advise` now uses explicit feature, PR merge, and main releasability workflows; repo-native `make ci` now includes project-scoped dependency health, coverage, Docker validation, and Postgres-backed runtime smoke checks |
| Slice 3H | Core-domain rollout wave (`lotus-core`) | Complete | `lotus-core` now uses explicit feature, PR merge, and main releasability workflows; repo-native `make ci` and `make ci-main` now separate PR-grade versus release-grade validation while preserving strong load, latency, Docker, and institutional sign-off evidence |
| Slice 4 | Platform end-to-end lane hardening | Complete | Platform repo lanes, validation lane normalization, repository governance rollout, and manifest-driven validation coverage are implemented |
| Slice 4A | Platform repo lane foundation | Complete | `lotus-platform` now exposes explicit feature, PR merge, and main releasability workflows backed by a shared repo-check entrypoint |
| Slice 4B | Platform validation lane normalization | Complete | `lotus-platform` now exposes one explicit `platform-end-to-end-validation.yml` workflow backed by a shared validation-lane entrypoint and scheduled green-lane execution |
| Slice 4C | Repository governance policy normalization | Complete | Platform governance artifacts are now repository-scoped, include `lotus-platform`, and align branch-protection payloads with RFC-0072 review and merge policy |
| Slice 4D | Repository governance rollout and validation | Complete | Repository governance policy has been applied across governed Lotus repos and live validation now reports zero drift |
| Slice 4E | Platform validation coverage manifest and contract | Complete | Platform end-to-end validation profiles are now manifest-driven, validator-enforced, and explicitly tied to required coverage artifacts |
| Slice 5 | Advanced enterprise controls | Complete | Advanced controls now have platform-owned enforceable foundations for hygiene, workflow security, release evidence, containers, lock artifacts, runtime isolation, text normalization, and action runtime baselines |
| Slice 5A | Repository hygiene and dependency-model baseline | Complete | Backend scaffold now emits platform-owned `.gitignore` and `.dockerignore` templates, automation metadata uses repository-native commands, and scaffold output is validated against a hygiene baseline |
| Slice 5B | Workflow security and permissions baseline | Complete | Platform-owned workflow security policy now validates least-privilege permissions, restricts `pull_request_target`, and runs as part of platform repo checks |
| Slice 5C | Release evidence and SBOM scaffold baseline | Complete | Newly scaffolded backend main releasability workflows now emit retained SBOM and release metadata artifacts by default through the shared template contract |
| Slice 5D | Container build and image baseline enforcement | Complete | Platform repo checks now enforce backend scaffold Docker contracts for `.dockerignore`, multi-stage non-root Dockerfiles, and BuildKit/buildx-enabled Docker validation workflows |
| Slice 5E | Companion dependency lock scaffold baseline | Complete | Backend scaffold now emits companion runtime and CI tooling lock artifacts by default, and repository hygiene validation enforces their presence |
| Slice 5F | Platform automation runtime isolation baseline | Complete | Platform repo checks and validation lane now use a repo-owned locked Python tooling environment instead of mutating ambient user site-packages |
| Slice 5G | Repository text and line-ending hygiene scaffold baseline | Complete | Backend scaffold now emits platform-owned `.editorconfig` and `.gitattributes` templates by default, and repository hygiene validation enforces deterministic text normalization rules |
| Slice 5H | Workflow action runtime baseline | Complete | Platform-owned workflows and backend templates now enforce a modern GitHub Actions baseline for core actions, and platform repo checks fail on stale action majors |
| Slice 5I | Implementation-state reconciliation and governance drift cleanup | Complete | RFC-0072 rollout documents now distinguish implemented governance controls from the remaining merge/closeout work and stale gap language is guarded by contract tests |

## Slice 1 Completion Evidence

### Governing documents

1. `rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`
2. `Continuous Integration, Validation, and Release Governance Standard.md`
3. `Local Development Runbook.md`
4. `platform-standards/Development-Workflow-and-CI-Strategy-Standard.md`
5. `platform-standards/Repository-CI-Lane-Mapping-Baseline.md`

### Slice 1 acceptance posture

#### 1. `lotus-platform` contains the RFC and associated standard

- Complete

Evidence:

1. `rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`
2. `Continuous Integration, Validation, and Release Governance Standard.md`

#### 2. Repositories can map their current workflows to the lane model

- Complete at baseline mapping level

Evidence:

1. `platform-standards/Repository-CI-Lane-Mapping-Baseline.md`

Note:

1. This is a mapping baseline, not the full gap audit required for Slice 2.

#### 3. Branch-protection expectations are documented

- Complete

Evidence:

1. `rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`
2. `Continuous Integration, Validation, and Release Governance Standard.md`
3. `platform-standards/Development-Workflow-and-CI-Strategy-Standard.md`

## Current Scaffold Source of Truth

Current platform-owned scaffold and template assets:

1. `automation/New-Lotus-Service.ps1`
2. `platform-standards/templates/workflows/feature-lane.backend.template.yml`
3. `platform-standards/templates/workflows/pr-merge-gate.backend.template.yml`
4. `platform-standards/templates/workflows/main-releasability.backend.template.yml`
5. `platform-standards/templates/workflows/pr-auto-merge.template.yml`
6. `platform-standards/templates/Makefile.backend.template`
7. `platform-standards/README.md`

Current posture:

1. backend scaffolding now emits explicit Feature Lane, PR Merge Gate, and Main Releasability workflows by default,
2. RFC-0072 lane and security expectations are now embedded in the backend workflow source of truth,
3. existing repositories still require explicit rollout convergence.

## Slice 2 Completion Evidence

### Gap-audit artifact

1. `platform-standards/Repository-CI-Convergence-Gap-Audit.md`

### Slice 2 acceptance posture

#### 1. One platform-owned rollout document exists

- Complete

Evidence:

1. `platform-standards/Repository-CI-Convergence-Gap-Audit.md`

#### 2. Each repository has explicit target lanes and required checks

- Complete at current-state versus target-state audit level

Evidence:

1. `platform-standards/Repository-CI-Lane-Mapping-Baseline.md`
2. `platform-standards/Repository-CI-Convergence-Gap-Audit.md`

#### 3. Missing enterprise and security checks are enumerated

- Complete at audit level

Evidence:

1. `platform-standards/Repository-CI-Convergence-Gap-Audit.md`

Note:

1. Missing controls are now enumerated, but not yet implemented. That belongs to later slices.

## Slice 3B Completion Evidence

### Template-contract artifacts

1. `platform-standards/Backend-CI-Lane-Template-Contract.md`
2. `platform-standards/templates/workflows/feature-lane.backend.template.yml`
3. `platform-standards/templates/workflows/pr-merge-gate.backend.template.yml`
4. `platform-standards/templates/workflows/main-releasability.backend.template.yml`
5. `platform-standards/templates/workflows/pr-auto-merge.template.yml`

### Slice 3B acceptance posture

#### 1. New backend services receive explicit lane workflows by default

- Complete

Evidence:

1. `automation/New-Lotus-Service.ps1`
2. `platform-standards/Backend-CI-Lane-Template-Contract.md`

#### 2. Branch-protection defaults target PR Merge Gate checks, not blended checks

- Complete for new scaffold registrations

Evidence:

1. `automation/New-Lotus-Service.ps1`
2. `platform-standards/Backend-CI-Lane-Template-Contract.md`

#### 3. Platform validation can distinguish explicit lane workflows from legacy CI

- Complete

Evidence:

1. `automation/Validate-Backend-Standards.ps1`

## Slice 3C Completion Evidence

### Repo rollout artifacts

1. `lotus-manage/.github/workflows/feature-lane.yml`
2. `lotus-manage/.github/workflows/pr-merge-gate.yml`
3. `lotus-manage/.github/workflows/main-releasability.yml`
4. `lotus-report/.github/workflows/feature-lane.yml`
5. `lotus-report/.github/workflows/pr-merge-gate.yml`
6. `lotus-report/.github/workflows/main-releasability.yml`
7. `automation/repository-governance-policy.json`
8. `platform-standards/Repository-CI-Convergence-Gap-Audit.md`

### Slice 3C acceptance posture

#### 1. The first scaffold-compatible backend repos are converged to explicit lane workflows

- Complete

Evidence:

1. `lotus-manage`
2. `lotus-report`

#### 2. Platform governance defaults reflect the new PR Merge Gate check names

- Complete

Evidence:

1. `automation/repository-governance-policy.json`

#### 3. Rollout documentation reflects implemented convergence rather than only target-state gaps

- Complete

Evidence:

1. `platform-standards/Repository-CI-Convergence-Gap-Audit.md`
2. `rfcs/RFC-0072-implementation-checklist.md`

## Slice 3D Completion Evidence

### Repo rollout artifacts

1. `lotus-gateway/.github/workflows/feature-lane.yml`
2. `lotus-gateway/.github/workflows/pr-merge-gate.yml`
3. `lotus-gateway/.github/workflows/main-releasability.yml`
4. `lotus-gateway/.github/workflows/platform-end-to-end-validation.yml`
5. `lotus-workbench/.github/workflows/feature-lane.yml`
6. `lotus-workbench/.github/workflows/pr-merge-gate.yml`
7. `lotus-workbench/.github/workflows/main-releasability.yml`
8. `automation/repository-governance-policy.json`
9. `platform-standards/Repository-CI-Lane-Mapping-Baseline.md`
10. `platform-standards/Repository-CI-Convergence-Gap-Audit.md`

### Slice 3D acceptance posture

#### 1. Experience-layer repos are converged to explicit lane workflows

- Complete

Evidence:

1. `lotus-gateway`
2. `lotus-workbench`

#### 2. Gateway platform-validation participation is explicitly named and retained

- Complete

Evidence:

1. `lotus-gateway/.github/workflows/platform-end-to-end-validation.yml`

#### 3. Platform governance defaults reflect the new PR Merge Gate check names for experience-layer repos

- Complete

Evidence:

1. `automation/repository-governance-policy.json`

#### 4. Rollout documentation reflects the current converged posture for `lotus-gateway` and `lotus-workbench`

- Complete

Evidence:

1. `platform-standards/Repository-CI-Lane-Mapping-Baseline.md`
2. `platform-standards/Repository-CI-Convergence-Gap-Audit.md`

## Slice 3E Completion Evidence

### Repo rollout artifacts

1. `lotus-performance/.github/workflows/feature-lane.yml`
2. `lotus-performance/.github/workflows/pr-merge-gate.yml`
3. `lotus-performance/.github/workflows/main-releasability.yml`
4. `lotus-performance/Makefile`
5. `lotus-performance/scripts/dependency_health_check.py`
6. `lotus-risk/.github/workflows/feature-lane.yml`
7. `lotus-risk/.github/workflows/pr-merge-gate.yml`
8. `lotus-risk/.github/workflows/main-releasability.yml`
9. `lotus-risk/Makefile`
10. `lotus-risk/scripts/dependency_health_check.py`
11. `automation/repository-governance-policy.json`
12. `platform-standards/Repository-CI-Lane-Mapping-Baseline.md`
13. `platform-standards/Repository-CI-Convergence-Gap-Audit.md`

### Slice 3E acceptance posture

#### 1. Analytics-domain repos are converged to explicit lane workflows

- Complete

Evidence:

1. `lotus-performance`
2. `lotus-risk`

#### 2. Repo-native PR-grade commands now include truthful dependency and security validation

- Complete

Evidence:

1. `lotus-performance/Makefile`
2. `lotus-performance/scripts/dependency_health_check.py`
3. `lotus-risk/Makefile`
4. `lotus-risk/scripts/dependency_health_check.py`

#### 3. Platform governance defaults reflect the new PR Merge Gate check names for analytics-domain repos

- Complete

Evidence:

1. `automation/repository-governance-policy.json`

#### 4. Rollout documentation reflects the current converged posture for `lotus-performance` and `lotus-risk`

- Complete

Evidence:

1. `platform-standards/Repository-CI-Lane-Mapping-Baseline.md`
2. `platform-standards/Repository-CI-Convergence-Gap-Audit.md`

## Slice 3F Completion Evidence

### Repo rollout artifacts

1. `lotus-ai/.github/workflows/feature-lane.yml`
2. `lotus-ai/.github/workflows/pr-merge-gate.yml`
3. `lotus-ai/.github/workflows/main-releasability.yml`
4. `lotus-ai/Makefile`
5. `lotus-ai/scripts/dependency_health_check.py`
6. `automation/repository-governance-policy.json`
7. `platform-standards/Repository-CI-Lane-Mapping-Baseline.md`
8. `platform-standards/Repository-CI-Convergence-Gap-Audit.md`

### Slice 3F acceptance posture

#### 1. Shared capability service repos are converged to explicit lane workflows

- Complete for the current in-scope repo

Evidence:

1. `lotus-ai`

#### 2. Repo-native PR-grade commands include truthful dependency and security validation without workstation-environment drift

- Complete

Evidence:

1. `lotus-ai/Makefile`
2. `lotus-ai/scripts/dependency_health_check.py`

#### 3. Platform governance defaults reflect the new PR Merge Gate check names for `lotus-ai`

- Complete

Evidence:

1. `automation/repository-governance-policy.json`

#### 4. Rollout documentation reflects the current converged posture for `lotus-ai`

- Complete

Evidence:

1. `platform-standards/Repository-CI-Lane-Mapping-Baseline.md`
2. `platform-standards/Repository-CI-Convergence-Gap-Audit.md`

## Slice 3G Completion Evidence

### Repo rollout artifacts

1. `lotus-advise/.github/workflows/feature-lane.yml`
2. `lotus-advise/.github/workflows/pr-merge-gate.yml`
3. `lotus-advise/.github/workflows/main-releasability.yml`
4. `lotus-advise/Makefile`
5. `lotus-advise/scripts/dependency_health_check.py`
6. `lotus-advise/scripts/run_runtime_smoke_checks.py`
7. `automation/repository-governance-policy.json`
8. `platform-standards/Repository-CI-Lane-Mapping-Baseline.md`
9. `platform-standards/Repository-CI-Convergence-Gap-Audit.md`

### Slice 3G acceptance posture

#### 1. Advisory-domain repos are converged to explicit lane workflows

- Complete for the current in-scope repo

Evidence:

1. `lotus-advise`

#### 2. Repo-native PR-grade commands include truthful dependency, Docker, and Postgres-backed runtime validation

- Complete

Evidence:

1. `lotus-advise/Makefile`
2. `lotus-advise/scripts/dependency_health_check.py`
3. `lotus-advise/scripts/run_runtime_smoke_checks.py`

#### 3. Platform governance defaults reflect the new PR Merge Gate check names for `lotus-advise`

- Complete

Evidence:

1. `automation/repository-governance-policy.json`

#### 4. Rollout documentation reflects the current converged posture for `lotus-advise`

- Complete

Evidence:

1. `platform-standards/Repository-CI-Lane-Mapping-Baseline.md`
2. `platform-standards/Repository-CI-Convergence-Gap-Audit.md`

## Slice 3H Completion Evidence

### Repo rollout artifacts

1. `lotus-core/.github/workflows/feature-lane.yml`
2. `lotus-core/.github/workflows/pr-merge-gate.yml`
3. `lotus-core/.github/workflows/main-releasability.yml`
4. `lotus-core/Makefile`
5. `lotus-core/scripts/dependency_health_check.py`
6. `lotus-core/scripts/performance_load_gate.py`
7. `automation/repository-governance-policy.json`
8. `platform-standards/Repository-CI-Lane-Mapping-Baseline.md`
9. `platform-standards/Repository-CI-Convergence-Gap-Audit.md`

### Slice 3H acceptance posture

#### 1. Core-domain workflows are converged to explicit lane structure without losing strong evidence gates

- Complete

Evidence:

1. `lotus-core`

#### 2. Repo-native PR-grade and release-grade commands are explicitly separated and truthful

- Complete

Evidence:

1. `lotus-core/Makefile`
2. `lotus-core/scripts/dependency_health_check.py`
3. `lotus-core/scripts/performance_load_gate.py`

#### 3. Platform governance defaults reflect the new PR Merge Gate check names for `lotus-core`

- Complete

Evidence:

1. `automation/repository-governance-policy.json`

#### 4. Rollout documentation reflects the current converged posture for `lotus-core`

- Complete

Evidence:

1. `platform-standards/Repository-CI-Lane-Mapping-Baseline.md`
2. `platform-standards/Repository-CI-Convergence-Gap-Audit.md`

## Deviation Posture

There are no Slice 1 implementation deviations.

Known remaining work is implementation closeout, not technical rollout deviation:

1. merging the already-raised repo convergence PRs after required checks remain green,
2. deleting merged feature branches and returning each repository to `main`,
3. refreshing this checklist and the RFC status once the rollout PRs are merged.
