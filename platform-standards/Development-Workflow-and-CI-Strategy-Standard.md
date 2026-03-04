# Development Workflow and CI Strategy Standard

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

#### Tier A: Fast PR Gates (blocking)
Run on every PR:
1. workflow lint
2. static quality (lint + typecheck)
3. unit + focused integration suites
4. contract gates (OpenAPI/vocabulary/governance where applicable)
5. runtime confidence quick gates (smoke/latency/fast load profile)

Target: fast, deterministic feedback suitable for iterative development.

#### Tier B: Full Validation Gates (heavy)
Run on:
1. `main` push
2. `workflow_dispatch`
3. scheduled/nightly runs

Includes:
1. full load/performance profiles
2. replay/drain invariants
3. heavier end-to-end and resilience checks

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
