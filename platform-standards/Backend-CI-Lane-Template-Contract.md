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

## Branch-Protection Default

New backend services must register the PR Merge Gate job names in `automation/repository-governance-policy.json`.

Feature-lane and main-releasability jobs must not be configured as required PR checks.

## Auto-Merge Default

The scaffolded `pr-auto-merge.yml` must request merge-commit auto-merge, not squash-only merge.

## Validation

The platform validator `automation/Validate-Backend-Standards.ps1` must distinguish:

1. `explicit` lane workflow mode,
2. `legacy` single-workflow mode,
3. `missing` workflow mode.
