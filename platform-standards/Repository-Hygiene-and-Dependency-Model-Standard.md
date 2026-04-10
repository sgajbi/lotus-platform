# Repository Hygiene and Dependency Model Standard

## Purpose

Define the minimum repository-hygiene baseline for Lotus backend repositories so that:

1. local developer environments do not leak into source control,
2. Docker build contexts stay disciplined,
3. dependency authority is explicit rather than accidental,
4. new Lotus services start from one clean, repeatable, platform-owned baseline.

## Scope

Applies to:

1. scaffolded Lotus backend repositories,
2. existing Lotus backend repositories during convergence,
3. platform-owned template and validator assets that govern backend repository shape.

## Required Baseline Files

Every Lotus backend repository must have:

1. `.gitignore`
2. `.dockerignore` when Docker build validation or container runtime is part of the repo contract
3. one explicit dependency authority
4. a repository-native quality command documented in `README.md`

## `.gitignore` Baseline

Backend `.gitignore` must exclude at least:

1. local virtual environments
2. Python bytecode and caches
3. coverage and test artifacts
4. local environment files
5. build and distribution outputs
6. editor and workstation noise
7. local output or evidence folders that are regenerated

Platform-owned scaffold source of truth:

1. `platform-standards/templates/.gitignore.backend.template`

## `.dockerignore` Baseline

Backend `.dockerignore` must exclude at least:

1. `.git`
2. local virtual environments and caches
3. test artifacts and coverage output
4. local output folders
5. documentation and tests unless they are intentionally copied into the image

Platform-owned scaffold source of truth:

1. `platform-standards/templates/.dockerignore.backend.template`

This standard complements, but does not replace:

1. `platform-standards/Container-Build-and-Image-Engineering-Standard.md`

## Dependency Authority Baseline

Each backend repository must declare one primary dependency authority.

Allowed primary models:

1. `pyproject.toml`
2. root `requirements.txt` plus explicitly associated lock or companion files

### New scaffold rule

New Lotus backend repositories must use `pyproject.toml` as the primary dependency authority by default.

### Existing-repo convergence rule

Existing repositories may remain on a `requirements.txt`-based model while converging, but they must not accumulate undocumented hybrid drift.

### Non-negotiable rule

No newly scaffolded Lotus backend repository should be created with:

1. missing dependency authority,
2. stale references to a dependency file that the repository does not own,
3. multiple dependency authorities without explicit documentation and ownership.

## Repository-Native Command Policy

Scaffolded automation metadata must reference repository-native commands, not long ad hoc shell chains.

For new backend services, the baseline metadata contract is:

1. `preflight_fast_command = "make check"`
2. `preflight_full_command = "make ci"`

This keeps automation aligned to the repository source of truth and reduces stale command drift.

## False-Positive and Convergence Handling

For existing repositories, temporary deviation is allowed only when:

1. a repository still uses a legacy dependency model,
2. a Docker build path is not yet standardized,
3. a migration plan exists and the deviation is documented in platform rollout tracking.

These deviations are not allowed for newly scaffolded repositories.

## Acceptance Posture

This standard is satisfied for scaffolded backend repos when:

1. the scaffold emits `.gitignore` from the platform template,
2. the scaffold emits `.dockerignore` from the platform template,
3. the scaffolded repository uses `pyproject.toml` as the dependency authority,
4. automation metadata points to `make check` and `make ci`,
5. an automated contract test proves the generated repository matches this baseline.
