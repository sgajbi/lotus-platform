# Repository CI Lane Mapping Baseline

- Status: Active Baseline
- Governing RFC: `rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`

## Purpose

Provide the initial repository-to-lane mapping so teams can interpret current workflow files against the RFC-0072 lane model without waiting for the deeper gap-audit slice.

This document is not the full rollout gap inventory.
It is the baseline map that makes the current CI shape legible.

## Canonical Lane Model

1. `Remote Feature Lane`
2. `Pull Request Merge Gate`
3. `Main Releasability Gate`
4. `Platform End-to-End Validation Lane`

## Baseline Mapping

| Repository | Profile | Current workflow files | Lane interpretation baseline | Notes |
| --- | --- | --- | --- | --- |
| `lotus-workbench` | UI Product | `.github/workflows/feature-lane.yml`, `.github/workflows/pr-merge-gate.yml`, `.github/workflows/main-releasability.yml`, `.github/workflows/pr-auto-merge.yml` | Explicit Feature Lane, PR Merge Gate, and Main Releasability Gate are now in place | Browser smoke and Docker parity are retained under explicit lane naming |
| `lotus-gateway` | Experience API | `.github/workflows/feature-lane.yml`, `.github/workflows/pr-merge-gate.yml`, `.github/workflows/main-releasability.yml`, `.github/workflows/platform-end-to-end-validation.yml`, `.github/workflows/pr-auto-merge.yml` | Explicit Feature Lane, PR Merge Gate, Main Releasability Gate, and named platform validation lane are now in place | Live upstream validation is retained as part of the platform taxonomy |
| `lotus-core` | Domain API | `.github/workflows/feature-lane.yml`, `.github/workflows/pr-merge-gate.yml`, `.github/workflows/main-releasability.yml`, `.github/workflows/pr-auto-merge.yml` | Explicit Feature Lane, PR Merge Gate, and Main Releasability Gate are now in place | Strong heavy-gate posture is retained through explicit PR-grade and release-grade command separation, including load, latency, Docker smoke, and institutional sign-off evidence |
| `lotus-performance` | Domain API | `.github/workflows/feature-lane.yml`, `.github/workflows/pr-merge-gate.yml`, `.github/workflows/main-releasability.yml`, `.github/workflows/pr-auto-merge.yml` | Explicit Feature Lane, PR Merge Gate, and Main Releasability Gate are now in place | Repo-native `make ci` now matches the PR-grade lane contract and uses isolated dependency/security validation |
| `lotus-risk` | Domain API | `.github/workflows/feature-lane.yml`, `.github/workflows/pr-merge-gate.yml`, `.github/workflows/main-releasability.yml`, `.github/workflows/pr-auto-merge.yml` | Explicit Feature Lane, PR Merge Gate, and Main Releasability Gate are now in place | Repo-native `make ci` now matches the PR-grade lane contract and keeps security auditing project-scoped and deterministic |
| `lotus-advise` | Domain API | `.github/workflows/feature-lane.yml`, `.github/workflows/pr-merge-gate.yml`, `.github/workflows/main-releasability.yml`, `.github/workflows/nightly-postgres-full.yml`, `.github/workflows/pr-auto-merge.yml` | Explicit Feature Lane, PR Merge Gate, and Main Releasability Gate are now in place | Repo-native `make ci` now includes project-scoped dependency health, Docker validation, and Postgres-backed runtime smoke checks |
| `lotus-manage` | Domain API | `.github/workflows/feature-lane.yml`, `.github/workflows/pr-merge-gate.yml`, `.github/workflows/main-releasability.yml`, `.github/workflows/pr-auto-merge.yml` | Explicit Feature Lane, PR Merge Gate, and Main Releasability Gate are now in place | Strong governance gates are retained under explicit lane naming |
| `lotus-report` | Domain API | `.github/workflows/feature-lane.yml`, `.github/workflows/pr-merge-gate.yml`, `.github/workflows/main-releasability.yml`, `.github/workflows/pr-auto-merge.yml` | Explicit Feature Lane, PR Merge Gate, and Main Releasability Gate are now in place | Coverage and Docker validation are retained under explicit lane naming |
| `lotus-ai` | Shared Capability Service | `.github/workflows/feature-lane.yml`, `.github/workflows/pr-merge-gate.yml`, `.github/workflows/main-releasability.yml`, `.github/workflows/pr-auto-merge.yml` | Explicit Feature Lane, PR Merge Gate, and Main Releasability Gate are now in place | Capability-specific governance, runtime-mode smoke, and project-scoped dependency health are retained under explicit lane naming |
| `lotus-platform` | Platform Governance / Automation | `.github/workflows/feature-lane.yml`, `.github/workflows/pr-merge-gate.yml`, `.github/workflows/main-releasability.yml`, `.github/workflows/api-vocabulary-governance.yml`, `.github/workflows/core-performance-green-lanes.yml`, `.github/workflows/core-performance-cross-app-validation.yml` | Explicit Feature Lane, PR Merge Gate, and Main Releasability Gate now exist for the platform repo; platform validation workflows remain specialized and will be normalized further in later slices | Platform end-to-end validation naming and governance still require convergence |

## Immediate Interpretation Rules

1. Repositories with one `ci.yml` plus `pr-auto-merge.yml` are considered partially aligned, not fully converged.
2. Current `ci.yml` files often blend PR and main responsibilities; that is acceptable for the baseline map but not the final target state.
3. Workflow-dispatch or scheduled cross-app validators belong to the `Platform End-to-End Validation Lane`, even if not yet named that way.
4. The existence of a workflow file alone does not prove conformance; only the lane baseline is established here.

## Branch-Protection Baseline

Every repository must converge toward:

1. protected `main`,
2. required PR checks,
3. PR-only merge flow,
4. no direct push to `main` except governed emergency handling,
5. auto-merge only after required checks are green.

## Scaffold Baseline

Current scaffold source of truth for backend repositories:

1. `automation/New-Lotus-Service.ps1`
2. `platform-standards/templates/workflows/feature-lane.backend.template.yml`
3. `platform-standards/templates/workflows/pr-merge-gate.backend.template.yml`
4. `platform-standards/templates/workflows/main-releasability.backend.template.yml`
5. `platform-standards/templates/workflows/pr-auto-merge.template.yml`

This scaffold baseline now emits the full backend lane model by default.
Repository rollout convergence remains a later slice.
