# Repository CI Convergence Gap Audit

- Status: Active
- Governing RFC: `rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`

## Purpose

Record the current-state versus target-state CI posture for every Lotus repository covered by RFC-0072.

This document is the Slice 2 rollout artifact.

It is intentionally explicit about:

1. what exists now,
2. what lane it currently maps to,
3. what is still missing before full RFC-0072 convergence,
4. where the highest-value implementation work should go next.

## Target State Summary

Every repository should converge toward:

1. explicit `Remote Feature Lane`,
2. explicit `Pull Request Merge Gate`,
3. explicit `Main Releasability Gate`,
4. participation in `Platform End-to-End Validation Lane` where relevant,
5. documented branch-protection expectations,
6. repository-native command parity with CI.

## Current Rollout Posture

Application and service repositories covered by RFC-0072 have now converged to explicit lane workflows.

The remaining convergence work is concentrated in:

1. merging the raised RFC-0072 convergence PRs after GitHub checks remain green,
2. keeping branch-protection and required-check enforcement aligned through platform governance validation,
3. expanding platform end-to-end validation coverage beyond the current governed profiles as the product surface grows.

## Current-State Gap Matrix

| Repository | Profile | Current workflow posture | Current strengths | Main gaps to target state | Priority |
| --- | --- | --- | --- | --- | --- |
| `lotus-workbench` | UI Product | Explicit `feature-lane.yml`, `pr-merge-gate.yml`, `main-releasability.yml`, and `pr-auto-merge.yml` now exist | Strong explicit lane split, browser smoke, Docker parity, build coverage, and a hardened Playwright smoke startup contract | Platform-owned E2E validation remains the canonical system proof; branch protection is governed through `repository-governance-policy.json` and live drift validation | P1 |
| `lotus-gateway` | Experience API | Explicit `feature-lane.yml`, `pr-merge-gate.yml`, `main-releasability.yml`, `platform-end-to-end-validation.yml`, and `pr-auto-merge.yml` now exist | Strong contract, integration, coverage, Docker, local parity, and explicitly named live upstream validation | Branch protection is governed through `repository-governance-policy.json`; remaining work is merge closeout rather than workflow structure | P1 |
| `lotus-core` | Domain API | Explicit `feature-lane.yml`, `pr-merge-gate.yml`, `main-releasability.yml`, and `pr-auto-merge.yml` now exist | Strong explicit lane split while retaining heavy gates for load, latency, Docker smoke, coverage, and institutional sign-off evidence; repo-native `make ci` and `make ci-main` now map cleanly to PR-grade versus release-grade validation | Platform-owned E2E validation remains the canonical system proof; branch protection is governed through `repository-governance-policy.json` and live drift validation | P1 |
| `lotus-performance` | Domain API | Explicit `feature-lane.yml`, `pr-merge-gate.yml`, `main-releasability.yml`, and `pr-auto-merge.yml` now exist | Strong governance gates, explicit lane split, coverage, Docker, and repo-native PR parity via a tightened `make ci` contract | Platform-owned E2E validation remains the canonical system proof; branch protection is governed through `repository-governance-policy.json` and live drift validation | P1 |
| `lotus-risk` | Domain API | Explicit `feature-lane.yml`, `pr-merge-gate.yml`, `main-releasability.yml`, and `pr-auto-merge.yml` now exist | Strong governance gates, explicit lane split, test-pyramid enforcement, coverage, Docker, and project-scoped dependency security auditing | Platform-owned E2E validation remains the canonical system proof; branch protection is governed through `repository-governance-policy.json` and live drift validation | P1 |
| `lotus-advise` | Domain API | Explicit `feature-lane.yml`, `pr-merge-gate.yml`, `main-releasability.yml`, `nightly-postgres-full.yml`, and `pr-auto-merge.yml` now exist | Strong governance gates, explicit lane split, nightly Postgres posture, project-scoped dependency health, Docker validation, and Postgres-backed runtime smoke under explicit lane naming | Platform-owned E2E validation remains the canonical system proof; branch protection is governed through `repository-governance-policy.json` and live drift validation | P1 |
| `lotus-manage` | Domain API | Explicit `feature-lane.yml`, `pr-merge-gate.yml`, `main-releasability.yml`, and `pr-auto-merge.yml` now exist | Strong governance gates, typecheck-tests-critical, split test suites, coverage, Docker; explicit lane naming now aligned | Platform-owned E2E validation remains the canonical system proof; branch protection is governed through `repository-governance-policy.json` and live drift validation | P1 |
| `lotus-report` | Domain API | Explicit `feature-lane.yml`, `pr-merge-gate.yml`, `main-releasability.yml`, and `pr-auto-merge.yml` now exist | Strong governance gates, split test suites, coverage, Docker; explicit lane naming now aligned | Platform-owned E2E validation remains the canonical system proof; branch protection is governed through `repository-governance-policy.json` and live drift validation | P1 |
| `lotus-ai` | Shared Capability Service | Explicit `feature-lane.yml`, `pr-merge-gate.yml`, `main-releasability.yml`, and `pr-auto-merge.yml` now exist | Strong capability-specific governance gates, runtime-mode smoke, project-scoped dependency health, coverage, and Docker validation under explicit lane naming | Platform-owned E2E validation remains gateway-mediated and canonical; branch protection is governed through `repository-governance-policy.json` and live drift validation | P1 |
| `lotus-platform` | Platform Governance / Automation | Explicit `feature-lane.yml`, `pr-merge-gate.yml`, `main-releasability.yml`, and `platform-end-to-end-validation.yml` now exist | Owns cross-app validation and governance automation; strong ingress and validation foundation; platform repo now has explicit repo lanes and an explicit platform validation lane | Remaining work is cross-surface validation expansion as Lotus product coverage grows; branch protection is governed and drift-checked | P0 |

## Cross-Repository Gap Themes

### 1. Platform validation is normalized and must keep expanding with product coverage

There is already meaningful platform-grade validation in:

1. `lotus-platform`
2. `lotus-gateway`
3. `lotus-workbench`

That naming gap is now closed in `lotus-platform`. Broader cross-surface expansion remains an ongoing validation coverage activity as new product surfaces become canonical.

### 2. Legacy workflow naming drift is closed for in-scope RFC-0072 rollout branches

In-scope rollout branches now use explicit lane names. Future drift should be detected through platform-owned workflow validators and repository context maintenance.

### 3. Scaffold coverage is backend-first by design

`automation/New-Lotus-Service.ps1` and the backend templates give a strong baseline for backend services. Non-backend scaffolds should adopt the same lane model when a new frontend, platform, or shared-capability scaffold is introduced.

1. frontend products,
2. shared capability services,
3. platform-governance repos.

## Recommended Next Implementation Focus

### P0

1. merge raised RFC-0072 convergence PRs once their required GitHub checks remain green
2. keep live repository-governance drift validation green
3. expand platform E2E validation profiles when new canonical product surfaces require system-level proof

### P1

1. platform participation follow-through for new product and service capabilities
2. scaffold expansion if new non-backend app generators are introduced
3. release-evidence hardening beyond the scaffold baseline when publishable artifacts become formal release outputs

Primary work:

1. keep platform validation centralized where system truth matters,
2. align workflow naming and required-check language,
3. keep branch-protection defaults consistently governed across repos.

## Convergence Rules for Later Slices

1. Do not weaken existing strong checks merely to fit naming.
2. Split lanes by purpose, not by arbitrary file count.
3. Keep heavy or expensive jobs out of fast lanes unless risk justifies them.
4. Preserve repository-native command parity while refactoring workflows.
5. Keep platform validation centralized where system truth matters.
