# Backend CI Lane Template Contract

- Status: Active
- Governing RFC: `rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`

## Purpose

Define the platform-owned backend workflow template contract that new Lotus services inherit by default.

## Generated Workflow Files

`automation/New-Lotus-Service.ps1` must scaffold these workflow files for every new backend service:

1. `.github/workflows/feature-lane.yml`
2. `.github/workflows/pr-merge-gate.yml`
3. `.github/workflows/main-releasability.yml`
4. `.github/workflows/pr-auto-merge.yml`
5. `.github/workflows/merged-pr-main-releasability.yml`

## Lane Intent

### Remote Feature Lane

Purpose:

1. fast branch-push protection,
2. deterministic local-quality feedback,
3. no expensive full-pyramid or release-only checks.

Required job names:

1. `Feature Lane / Workflow Lint`
2. `Feature Lane / Lint Typecheck Security`
3. `Feature Lane / Tests (unit)`

### Pull Request Merge Gate

Purpose:

1. merge-blocking quality gate,
2. full backend test pyramid,
3. branch-protection source of truth.

Required job names:

1. `PR Merge Gate / Workflow Lint`
2. `PR Merge Gate / Lint Typecheck Security`
3. `PR Merge Gate / Tests (unit)`
4. `PR Merge Gate / Tests (integration)`
5. `PR Merge Gate / Tests (e2e)`
6. `PR Merge Gate / Coverage Gate (Combined)`
7. `PR Merge Gate / Validate Docker Build`

### Main Releasability Gate

Purpose:

1. post-merge releasability evidence,
2. rerun PR-grade confidence on `main`,
3. retained artifacts for release review.

Required job names:

1. `Main Releasability / Workflow Lint`
2. `Main Releasability / Lint Typecheck Security`
3. `Main Releasability / Tests (unit)`
4. `Main Releasability / Tests (integration)`
5. `Main Releasability / Tests (e2e)`
6. `Main Releasability / Coverage Gate (Combined)`
7. `Main Releasability / Validate Docker Build`

Required retained artifacts:

1. `main-releasability-coverage-data`
2. `main-releasability-release-evidence`

The `main-releasability-release-evidence` artifact must contain:

1. `sbom.cdx.json`
2. `release-evidence.json`

## Branch-Protection Default

New backend services must register the PR Merge Gate job names in `automation/repository-governance-policy.json`.

Feature-lane and main-releasability jobs must not be configured as required PR checks.

## Auto-Merge Default

The scaffolded `pr-auto-merge.yml` must request rebase auto-merge, not squash or merge-commit
auto-merge. It must authenticate with `LOTUS_AUTOMERGE_TOKEN`, not `${{ github.token }}`, so PR
merge completion is performed by a non-suppressed actor that can trigger post-merge workflow
dispatch. Lotus PR completion preserves scoped commits on a linear `main` history.

The scaffolded `merged-pr-main-releasability.yml` must dispatch `main-releasability.yml` when a PR
is merged to `main`. This keeps post-merge release evidence explicit for rebase auto-merged PRs
instead of depending only on a push-triggered workflow run.

## Report-Only Scaffold Quality Commands

New backend service scaffolds must include these repo-native report-only commands:

1. `make architecture-boundary-report`
2. `make quality-baseline`

New backend service scaffolds must include this repo-native blocking anti-drift command:

1. `make ci-contract-gate`
2. `make implementation-truth-gate`

Blocking commands wired into `make check`, `make ci`, Feature Lane, PR Merge Gate, or Main
Releasability must not create or rewrite durable report artifacts in a clean checkout. Report
artifacts belong behind explicit report-only commands so local preflight and CI gates remain
repeatable and worktree-clean.

`make ci-contract-gate` is allowed and expected to run through `make lint` because it is
worktree-clean and validates the lane contract itself: required Makefile targets, least-privilege
workflow permissions, non-suppressed auto-merge token usage, approved action-runtime majors,
merge-grade coverage, Docker validation, release evidence, endpoint certification,
supported-feature promotion control, and local quality gate wiring. It must also protect
`workflow_dispatch` on `main-releasability.yml` and the merged-PR dispatch workflow that starts
post-merge release evidence.

`make implementation-truth-gate` is allowed and expected to run through `make lint` because it is
worktree-clean and blocks unqualified README/docs/wiki current-state claims of demo readiness,
production support, certification, live source ingestion, Gateway/Workbench support, or
client-ready publication before supported-feature evidence exists.

Report-only commands must not become blocking CI gates until `lotus-ci-enforcement-governance`
confirms the signal is measured, deterministic, low-noise, lane-appropriate, and backed by an
exception policy.

## Validation

The platform validator `automation/Validate-Backend-Standards.ps1` must distinguish:

1. `explicit` lane workflow mode,
2. `legacy` single-workflow mode,
3. `missing` workflow mode.
