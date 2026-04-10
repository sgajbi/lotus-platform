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
| Slice 3 | Standardized workflow convergence | Pending | Existing-repo workflow updates and branch-protection convergence remain a later rollout step |
| Slice 3A | Skill and developer-process alignment | Complete | Codex skills for backend delivery, frontend delivery, and pre-merge flow align to RFC-0072 |
| Slice 3B | Scaffold and template convergence | Complete | Backend scaffold now emits explicit feature, PR merge, and main releasability workflows by default |
| Slice 3C | Backend rollout wave 1 (`lotus-manage`, `lotus-report`) | Complete | Both repos now use explicit feature, PR merge, and main releasability workflows, with governance policy updated accordingly |
| Slice 4 | Platform end-to-end lane hardening | Pending | Canonical platform runtime validation exists, but RFC-0072 governance rollout is not yet completed |
| Slice 5 | Advanced enterprise controls | Pending | Security and release-hardening additions remain phased future work |

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
7. `automation/backend-governance-policy.json`
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

1. `automation/backend-governance-policy.json`

#### 3. Rollout documentation reflects implemented convergence rather than only target-state gaps

- Complete

Evidence:

1. `platform-standards/Repository-CI-Convergence-Gap-Audit.md`
2. `rfcs/RFC-0072-implementation-checklist.md`

## Deviation Posture

There are no Slice 1 implementation deviations.

Known future work is intentional rollout scope, not deviation:

1. per-repo lane-gap audit,
2. branch-protection convergence across all repos,
3. scaffold/template convergence beyond the current backend baseline,
4. advanced enterprise security controls such as SBOM and image scanning.
