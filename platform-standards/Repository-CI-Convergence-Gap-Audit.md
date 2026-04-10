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

1. `lotus-platform` adopting its own explicit lane structure,
2. branch-protection and required-check enforcement being applied consistently from platform governance,
3. platform end-to-end validation lane hardening and advanced enterprise controls.

## Current-State Gap Matrix

| Repository | Profile | Current workflow posture | Current strengths | Main gaps to target state | Priority |
| --- | --- | --- | --- | --- | --- |
| `lotus-workbench` | UI Product | Explicit `feature-lane.yml`, `pr-merge-gate.yml`, `main-releasability.yml`, and `pr-auto-merge.yml` now exist | Strong explicit lane split, browser smoke, Docker parity, build coverage, and a hardened Playwright smoke startup contract | Platform End-to-End Validation Lane participation still remains platform-owned rather than repo-local; branch-protection rollout must be applied from platform governance | P1 |
| `lotus-gateway` | Experience API | Explicit `feature-lane.yml`, `pr-merge-gate.yml`, `main-releasability.yml`, `platform-end-to-end-validation.yml`, and `pr-auto-merge.yml` now exist | Strong contract, integration, coverage, Docker, local parity, and explicitly named live upstream validation | Branch-protection rollout must be applied from platform governance; remaining rollout work is now in other repos rather than gateway workflow structure | P1 |
| `lotus-core` | Domain API | Explicit `feature-lane.yml`, `pr-merge-gate.yml`, `main-releasability.yml`, and `pr-auto-merge.yml` now exist | Strong explicit lane split while retaining heavy gates for load, latency, Docker smoke, coverage, and institutional sign-off evidence; repo-native `make ci` and `make ci-main` now map cleanly to PR-grade versus release-grade validation | Platform End-to-End Validation Lane participation still remains platform-owned rather than repo-local; branch-protection rollout must be applied from platform governance | P1 |
| `lotus-performance` | Domain API | Explicit `feature-lane.yml`, `pr-merge-gate.yml`, `main-releasability.yml`, and `pr-auto-merge.yml` now exist | Strong governance gates, explicit lane split, coverage, Docker, and repo-native PR parity via a tightened `make ci` contract | Platform End-to-End Validation Lane participation still remains platform-owned rather than repo-local; branch-protection rollout must be applied from platform governance | P1 |
| `lotus-risk` | Domain API | Explicit `feature-lane.yml`, `pr-merge-gate.yml`, `main-releasability.yml`, and `pr-auto-merge.yml` now exist | Strong governance gates, explicit lane split, test-pyramid enforcement, coverage, Docker, and project-scoped dependency security auditing | Platform End-to-End Validation Lane participation still remains platform-owned rather than repo-local; branch-protection rollout must be applied from platform governance | P1 |
| `lotus-advise` | Domain API | Explicit `feature-lane.yml`, `pr-merge-gate.yml`, `main-releasability.yml`, `nightly-postgres-full.yml`, and `pr-auto-merge.yml` now exist | Strong governance gates, explicit lane split, nightly Postgres posture, project-scoped dependency health, Docker validation, and Postgres-backed runtime smoke under explicit lane naming | Platform End-to-End Validation Lane participation still remains platform-owned rather than repo-local; branch-protection rollout must be applied from platform governance | P1 |
| `lotus-manage` | Domain API | Explicit `feature-lane.yml`, `pr-merge-gate.yml`, `main-releasability.yml`, and `pr-auto-merge.yml` now exist | Strong governance gates, typecheck-tests-critical, split test suites, coverage, Docker; explicit lane naming now aligned | Platform End-to-End Validation Lane participation still needs to be documented and wired; branch-protection rollout must be applied from platform governance | P1 |
| `lotus-report` | Domain API | Explicit `feature-lane.yml`, `pr-merge-gate.yml`, `main-releasability.yml`, and `pr-auto-merge.yml` now exist | Strong governance gates, split test suites, coverage, Docker; explicit lane naming now aligned | Platform End-to-End Validation Lane participation still needs to be documented and wired; branch-protection rollout must be applied from platform governance | P1 |
| `lotus-ai` | Shared Capability Service | Explicit `feature-lane.yml`, `pr-merge-gate.yml`, `main-releasability.yml`, and `pr-auto-merge.yml` now exist | Strong capability-specific governance gates, runtime-mode smoke, project-scoped dependency health, coverage, and Docker validation under explicit lane naming | Platform End-to-End Validation Lane participation still remains gateway-mediated rather than repo-local; branch-protection rollout must be applied from platform governance | P1 |
| `lotus-platform` | Platform Governance / Automation | Platform-specific governance and cross-app workflows exist, but no explicit RFC-0072 lane suite yet | Owns cross-app validation and governance automation; strong ingress and validation foundation | Needs explicit lane-oriented workflow strategy for its own repo; needs cross-repo rollout reporting as first-class artifact; needs platform validation lane naming convergence | P0 |

## Cross-Repository Gap Themes

### 1. Platform validation exists but is not yet normalized

There is already meaningful platform-grade validation in:

1. `lotus-platform`
2. `lotus-gateway`
3. `lotus-workbench`

But it is not yet named and governed consistently as the `Platform End-to-End Validation Lane`.

### 2. Workflow names still drift

Repositories are using:

1. `Backend Service Pipeline`
2. `Lotus Core Pipeline`
3. `Advisor Workbench Quality Gate`
4. `Advisor Experience API Pipeline`
5. other repo-specific names

These are understandable, but they do not yet make the RFC-0072 lane intent obvious.

### 3. Scaffold coverage is backend-first, not platform-wide

`automation/New-Lotus-Service.ps1` and the backend templates give a strong baseline for backend services, but the full lane model is not yet scaffolded by default for:

1. frontend products,
2. shared capability services,
3. platform-governance repos.

## Recommended Next Implementation Focus

### P0

1. `lotus-platform`
   - define its own explicit lane structure and rollout reporting

### P1

1. platform participation follow-through for converged product and service repos
2. branch-protection rollout from governance policy
3. `lotus-ai` platform-governance follow-through

Primary work:

1. keep platform validation centralized where system truth matters,
2. align workflow naming and required-check language,
3. apply branch-protection defaults consistently across repos.

## Convergence Rules for Later Slices

1. Do not weaken existing strong checks merely to fit naming.
2. Split lanes by purpose, not by arbitrary file count.
3. Keep heavy or expensive jobs out of fast lanes unless risk justifies them.
4. Preserve repository-native command parity while refactoring workflows.
5. Keep platform validation centralized where system truth matters.
