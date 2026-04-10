# Development Workflow and CI Strategy Standard

Authoritative CI governance now lives in:

1. `Continuous Integration, Validation, and Release Governance Standard.md`
2. `rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`

This document remains as a concise operator-facing companion and must stay aligned to those sources.

## Purpose
Define a single, repeatable delivery workflow for all Lotus applications that keeps feedback fast, quality high, and production risk low.

## Scope
Applies to all Lotus repositories (`lotus-core`, `lotus-risk`, `lotus-performance`, `lotus-manage`, `lotus-advise`, `lotus-gateway`, and future services).

## Delivery Model

### 1. Branching and Change Slicing
1. Create one feature branch per RFC or implementation slice.
2. Branch from `main` only.
3. Keep scope small and coherent; avoid mixed unrelated changes.
4. Commit incrementally and push regularly.

### 2. PR-First Integration
1. Never commit directly to `main`.
2. Every change goes through a PR.
3. PR description must include:
- what changed
- why it changed
- validation evidence

### 3. CI Tiering (Required)

#### Tier A: Remote Feature Lane
Run on feature-branch push:
1. workflow lint
2. static quality (lint + typecheck)
3. fast unit tests
4. fast contract or schema checks

Target: fast, deterministic feedback suitable for iterative development.

#### Tier B: Pull Request Merge Gate
Run on every PR:
1. all Remote Feature Lane checks
2. integration tests
3. coverage gate
4. security audit
5. contract governance gates
6. Docker build validation
7. local parity or equivalent repo-native parity run

#### Tier C: Main Releasability Gate
Run on:
1. `main` push

Includes:
1. PR-grade gate rerun or stricter equivalent
2. release artifacts and retained evidence

#### Tier D: Platform End-to-End Validation Lane
Run on:
1. `workflow_dispatch`
2. scheduled/nightly runs

Includes:
1. canonical ingress and DNS validation
2. seeded stack bring-up validation
3. cross-app and browser-level validation
4. demo-readiness and release-readiness evidence

Target: institutional-grade operational assurance without slowing every PR.

### 4. Merge Policy
A PR can merge only when:
1. required checks are green
2. unresolved blocking review comments do not exist
3. PR scope and evidence are complete

### 5. Post-Merge Hygiene
After merge:
1. delete remote feature branch
2. delete local feature branch
3. sync local main with origin/main (`git pull --ff-only`)

Required end state: `local = remote = main`.

## Single-Developer Mode
When reviewer approval is not required:
1. PR remains mandatory.
2. CI checks act as approval control.
3. Auto-merge is allowed only after required checks are green.

## Multi-Developer Mode
When reviewer approval is required:
1. Apply same CI model.
2. Add CODEOWNERS/reviewer gates on top of CI.

## Standard PR Evidence Template
Include:
1. local commands executed
2. key CI checks and result
3. known limitations/follow-ups (if any)
4. governance impact (API vocab/OpenAPI/RFC docs)

## Anti-Patterns (Not Allowed)
1. direct pushes to `main`
2. long-lived feature branches with large unreviewable deltas
3. blocking PRs on heavyweight nightly-only checks unless high-risk change requires it
4. merging with red or unstable required checks

## Adoption Guidance
1. Each repo must align its workflow files to this standard.
2. Existing automation/skills should enforce this policy (pre-merge gate + branch hygiene).
3. Repo-specific extensions are allowed only if they are stricter than this baseline.
4. Use `platform-standards/Repository-CI-Lane-Mapping-Baseline.md` for the initial repo-to-lane interpretation until the full gap audit slice is complete.
