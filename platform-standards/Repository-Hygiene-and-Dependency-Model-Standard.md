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

1. `.editorconfig`
2. `.gitattributes`
3. `.gitignore`
4. `.dockerignore` when Docker build validation or container runtime is part of the repo contract
5. one explicit dependency authority
6. companion dependency lock artifacts under `requirements/`
7. a repository-native quality command documented in `README.md`

## `.editorconfig` Baseline

Backend `.editorconfig` must define at least:

1. `root = true`
2. `charset = utf-8`
3. `end_of_line = lf`
4. `insert_final_newline = true`
5. language-aware indentation expectations

Platform-owned scaffold source of truth:

1. `platform-standards/templates/.editorconfig.backend.template`

## `.gitattributes` Baseline

Backend `.gitattributes` must define at least:

1. a repository-wide text normalization rule
2. deterministic LF checkout for text content
3. binary handling for common image and archive artifacts

Platform-owned scaffold source of truth:

1. `platform-standards/templates/.gitattributes.backend.template`

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

They must also emit the companion lock artifacts below:

1. `requirements/shared-runtime.lock.txt`
2. `requirements/ci-tooling.lock.txt`

These files are companion evidence and install-control artifacts, not a second primary dependency authority.

### Existing-repo convergence rule

Existing repositories may remain on a `requirements.txt`-based model while converging, but they must not accumulate undocumented hybrid drift.

### Non-negotiable rule

No newly scaffolded Lotus backend repository should be created with:

1. missing dependency authority,
2. stale references to a dependency file that the repository does not own,
3. multiple dependency authorities without explicit documentation and ownership.

## Governed Dependency Vulnerability And Maturity Posture

Application libraries are part of the product's bank-readiness posture, not a local convenience
choice. The default dependency choice for Lotus application and quality-tooling code is mature,
widely deployed, well-documented technology with broad developer training, operational tooling, and
security-scanner support.

By default, Lotus repositories must exclude:

1. beta, alpha, preview, experimental, or incubating packages from runtime dependency sets,
2. novelty-driven major-version upgrades that do not clear a concrete product, security, or
   operational blocker,
3. unmaintained or low-adoption packages when a mature ecosystem-standard alternative is available,
4. packages without a credible vulnerability-disclosure, release-note, and patch-management trail,
5. dependency changes that bypass repository lock, constraints, SBOM, or vulnerability-scan
   evidence.

Exceptions are allowed only when they are explicit, time-bounded, issue-backed, and reviewed through
the repository's dependency hygiene or vulnerability-management evidence. An exception must name the
package, version, business or engineering reason, vulnerability posture, compensating controls,
expiry or revisit date, and the repository owner responsible for removal or promotion to the
standard path.

Dependency updates should therefore be treated as governed maintenance:

1. prefer minimal patch/minor updates that remediate vulnerabilities or support current platform
   policy,
2. keep major upgrades as issue-backed implementation slices with migration notes and regression
   evidence,
3. retain scanner output and SBOM evidence in the applicable CI or release lane,
4. do not present a dependency change as bank-ready while critical or high vulnerabilities remain
   unowned or while scanner coverage is absent.

## Repository-Native Command Policy

Scaffolded automation metadata must reference repository-native commands, not long ad hoc shell chains.

For new backend services, the baseline metadata contract is:

1. `preflight_fast_command = "make check"`
2. `preflight_full_command = "make ci"`

This keeps automation aligned to the repository source of truth and reduces stale command drift.

## Node Quality-Tooling Dependency Policy

A backend repository that uses Node tooling for a blocking quality, API-governance, security, or
release-evidence gate must:

1. keep the tooling package under a capability-owned directory such as `tools/api_governance/`,
2. declare exact direct tool versions in `package.json`,
3. commit the adjacent `package-lock.json`,
4. declare an exact or lower-and-upper-bounded `engines.node` contract,
5. restore the package with `npm ci`,
6. invoke only its `node_modules/.bin` executable or an owned package script, and
7. include dependency-vulnerability evidence in the applicable CI lane.

Unversioned `npx`, global npm installs, implicit latest tags, and mutable `npm install` resolution
are not acceptable blocking or release evidence. Report-only tooling is not promoted to blocking
evidence until it satisfies this contract.

Validate the repository with:

```powershell
python <lotus-platform>/automation/quality_tooling/validate_node_quality_tooling.py --repository .
```

The platform backend scaffold remains Python-only because it does not generate a Node-based gate.
Do not add unused Node dependencies to satisfy this policy; a generated repository with no Node
quality tooling satisfies the validator without an empty package manifest.

## False-Positive and Convergence Handling

For existing repositories, temporary deviation is allowed only when:

1. a repository still uses a legacy dependency model,
2. a Docker build path is not yet standardized,
3. a migration plan exists and the deviation is documented in platform rollout tracking.

These deviations are not allowed for newly scaffolded repositories.

## Acceptance Posture

This standard is satisfied for scaffolded backend repos when:

1. the scaffold emits `.editorconfig` from the platform template,
2. the scaffold emits `.gitattributes` from the platform template,
3. the scaffold emits `.gitignore` from the platform template,
4. the scaffold emits `.dockerignore` from the platform template,
5. the scaffolded repository uses `pyproject.toml` as the dependency authority,
6. the scaffold emits `requirements/shared-runtime.lock.txt`,
7. the scaffold emits `requirements/ci-tooling.lock.txt`,
8. automation metadata points to `make check` and `make ci`,
9. any blocking Node quality tooling satisfies the lock-backed dependency policy, and
10. an automated contract test proves the generated repository matches this baseline.
