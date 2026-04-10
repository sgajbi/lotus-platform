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

## Current-State Gap Matrix

| Repository | Profile | Current workflow posture | Current strengths | Main gaps to target state | Priority |
| --- | --- | --- | --- | --- | --- |
| `lotus-workbench` | UI Product | Single `ci.yml` covers PR and `main`; `pr-auto-merge.yml` exists | Strong PR/main gate, browser smoke, Docker parity, build coverage | No explicit dedicated Feature Lane; Main Releasability Gate not separated from PR gate; platform E2E dependency not yet expressed in repo docs/workflow naming | P1 |
| `lotus-gateway` | Experience API | Single `ci.yml` covers PR and `main`; `workflow_dispatch` live upstream check exists; `pr-auto-merge.yml` exists | Strong contract, integration, coverage, Docker, and local parity gates; live upstream validation exists | No explicit dedicated Feature Lane; Main Releasability Gate not separated; live upstream workflow is not yet named as part of platform validation taxonomy | P1 |
| `lotus-core` | Domain API | One large `ci.yml` covers PR, `main`, merge-group, scheduled, and manual heavy checks; `pr-auto-merge.yml` exists | Strongest maturity in heavy gates, load gates, latency, docker smoke, and institutional sign-off evidence | Workflow is overloaded; Feature, PR, Main, and heavy system lanes are not explicitly separated; lane naming is not aligned to RFC-0072 | P0 |
| `lotus-performance` | Domain API | Single `ci.yml` covers PR and `main`; `pr-auto-merge.yml` exists | Strong governance gates, test pyramid gate, coverage, Docker | No explicit dedicated Feature Lane; Main Releasability Gate not separated; no explicit platform validation participation documented | P1 |
| `lotus-risk` | Domain API | Single `ci.yml` covers PR and `main`; `pr-auto-merge.yml` exists | Governance gates, coverage, Docker | No explicit dedicated Feature Lane; Main Releasability Gate not separated; no explicit platform validation participation documented | P1 |
| `lotus-advise` | Domain API | Single `ci.yml` covers PR and `main`; nightly full workflow exists; `pr-auto-merge.yml` exists | Stronger than baseline on dependency freshness, Postgres smoke, production-profile gates, nightly posture | No explicit Feature Lane separation; Main Releasability Gate not separated from PR gate; nightly workflow not yet classified under platform taxonomy | P1 |
| `lotus-manage` | Domain API | Explicit `feature-lane.yml`, `pr-merge-gate.yml`, `main-releasability.yml`, and `pr-auto-merge.yml` now exist | Strong governance gates, typecheck-tests-critical, split test suites, coverage, Docker; explicit lane naming now aligned | Platform End-to-End Validation Lane participation still needs to be documented and wired; branch-protection rollout must be applied from platform governance | P1 |
| `lotus-report` | Domain API | Explicit `feature-lane.yml`, `pr-merge-gate.yml`, `main-releasability.yml`, and `pr-auto-merge.yml` now exist | Strong governance gates, split test suites, coverage, Docker; explicit lane naming now aligned | Platform End-to-End Validation Lane participation still needs to be documented and wired; branch-protection rollout must be applied from platform governance | P1 |
| `lotus-ai` | Shared Capability Service | `backend-service-pipeline.yml` and `ci.yml`; broad push trigger already captures feature-branch events; `pr-auto-merge.yml` exists | Best current approximation of a feature-branch lane because push is not restricted to `main`; includes runtime-mode smoke and capability-specific governance gates | Lane naming still not aligned; PR and Main gates still blended in one workflow; platform E2E participation via gateway is not yet formalized | P1 |
| `lotus-platform` | Platform Governance / Automation | Platform-specific governance and cross-app workflows exist, but no explicit RFC-0072 lane suite yet | Owns cross-app validation and governance automation; strong ingress and validation foundation | Needs explicit lane-oriented workflow strategy for its own repo; needs cross-repo rollout reporting as first-class artifact; needs platform validation lane naming convergence | P0 |

## Cross-Repository Gap Themes

### 1. PR and `main` are usually blended

Most Lotus repos currently use one main CI workflow for both:

1. PR Merge Gate
2. Main Releasability Gate

That is workable but below the RFC target model.

### 2. Dedicated Feature Lane is mostly missing

With the partial exception of `lotus-ai`, repositories do not yet expose a clearly named, intentionally fast Feature Lane.

### 3. Platform validation exists but is not yet normalized

There is already meaningful platform-grade validation in:

1. `lotus-platform`
2. `lotus-gateway`
3. `lotus-workbench`

But it is not yet named and governed consistently as the `Platform End-to-End Validation Lane`.

### 4. Workflow names still drift

Repositories are using:

1. `Backend Service Pipeline`
2. `Lotus Core Pipeline`
3. `Advisor Workbench Quality Gate`
4. `Advisor Experience API Pipeline`
5. other repo-specific names

These are understandable, but they do not yet make the RFC-0072 lane intent obvious.

### 5. Scaffold coverage is backend-first, not platform-wide

`automation/New-Lotus-Service.ps1` and the backend templates give a strong baseline for backend services, but the full lane model is not yet scaffolded by default for:

1. frontend products,
2. shared capability services,
3. platform-governance repos.

## Recommended Next Implementation Focus

### P0

1. `lotus-platform`
   - define its own explicit lane structure and rollout reporting
2. `lotus-core`
   - decompose the overloaded workflow into explicit lanes without losing current strong evidence quality

### P1

1. `lotus-workbench`
2. `lotus-gateway`
3. `lotus-performance`
4. `lotus-risk`
5. `lotus-advise`
6. `lotus-ai`

Primary work:

1. split explicit Feature Lane from PR/Main blend,
2. document Main Releasability Gate explicitly,
3. align workflow naming and required-check language.

## Convergence Rules for Later Slices

1. Do not weaken existing strong checks merely to fit naming.
2. Split lanes by purpose, not by arbitrary file count.
3. Keep heavy or expensive jobs out of fast lanes unless risk justifies them.
4. Preserve repository-native command parity while refactoring workflows.
5. Keep platform validation centralized where system truth matters.
