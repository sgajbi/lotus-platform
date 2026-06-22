# Platform Standards

This folder is the reusable standards package for backend repositories.

## Contents

- `templates/Makefile.backend.template`
- `templates/.editorconfig.backend.template`
- `templates/.gitattributes.backend.template`
- `templates/.gitignore.backend.template`
- `templates/.dockerignore.backend.template`
- `templates/Dockerfile.python-service.template`
- `templates/constraints.shared-build.template.txt`
- `templates/requirements.shared-runtime.lock.template.txt`
- `templates/requirements.ci-tooling.lock.template.txt`
- `templates/pre-commit.backend.template.yaml`
- `templates/workflows/feature-lane.backend.template.yml`
- `templates/workflows/pr-merge-gate.backend.template.yml`
- `templates/workflows/main-releasability.backend.template.yml`
- `templates/workflows/pr-auto-merge.template.yml`
- `templates/workflows/merged-pr-main-releasability.template.yml`
- `Development-Workflow-and-CI-Strategy-Standard.md`
- `Backend-CI-Lane-Template-Contract.md`
- `Repository-Hygiene-and-Dependency-Model-Standard.md`
- `Workflow-Security-and-Permissions-Standard.md`
- `Workflow-Action-Runtime-and-Version-Baseline.md`
- `Release-Evidence-and-SBOM-Foundation-Standard.md`
- `Platform-End-to-End-Validation-Coverage-Standard.md`
- `Repository-CI-Lane-Mapping-Baseline.md`
- `Repository-CI-Convergence-Gap-Audit.md`
- `Container-Build-and-Image-Engineering-Standard.md`
- `LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md`

## Usage

1. Copy templates into service repositories.
2. Adapt only repo-specific values (branch name, Python version, docker image tag, test paths).
3. Keep required gate names and required `make` targets unchanged (`lint`, `typecheck`, `openapi-gate`, `test`, `ci`, `security-audit`).
4. For mature multi-service repos, promote shared runtime constraints into a compiled shared runtime lock and feed that same lock into bootstrap, Docker builds, SBOM generation, and provenance manifests.
5. Run conformance validator:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Validate-Backend-Standards.ps1
```

Automation command guide: `automation/docs/Automation-Guide.md`.

Authoritative cross-repository CI governance:

1. `../docs/standards/Continuous Integration, Validation, and Release Governance Standard.md`
2. `../rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`

Cross-application bank-buyable engineering posture:

1. `LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md`

## One-Command Lotus Service Scaffold

Detailed usage guide: `docs/onboarding/LOTUS-BACKEND-SERVICE-SCAFFOLD-GUIDE.md`.

```powershell
powershell -ExecutionPolicy Bypass -File automation/New-Lotus-Service.ps1 `
  -ServiceName lotus-risk `
  -Description "Risk and exposure analytics service" `
  -ServiceProfile domain-service `
  -Port 8130
```

This generates a production-grade backend baseline with:

- service-profile-aware README, repository context, wiki source, and quality documentation
- explicit feature, PR merge, and main releasability workflows
- platform-approved workflow action runtime majors for checkout, Python setup, artifact upload,
  artifact download, and Docker Buildx setup
- main releasability release evidence with CycloneDX SBOM and release metadata artifacts
- rebase auto-merge workflow for linear, non-squash history
- merged-PR main releasability dispatcher for explicit post-merge evidence after auto-merge
- scaffolded `.editorconfig`, `.gitattributes`, `.gitignore`, and `.dockerignore` from platform templates
- Makefile + lint/typecheck/test/coverage/security gates
- generated `scripts/clean_generated_artifacts.py` with `make clean` wiring for safe cache,
  build, and local coverage cleanup
- blocking CI contract gate that protects bank-buyable lane wiring, bounded job timeouts, and
  no-soft-fail critical workflow posture plus cleanup wiring from drift
- blocking implementation-truth gate that prevents README/docs/wiki current-state claims from
  outrunning supported-feature evidence and catches stale scaffold-era demo underclaims after
  implementation evidence exists
- layered `src/app/api`, `src/app/application`, `src/app/domain`, `src/app/ports`,
  `src/app/infrastructure`, `src/app/observability`, and `src/app/security` package skeleton
- FastAPI app with health/readiness and metrics
- product-safe problem-details error scaffolding
- structured JSON application event logging
- OpenAPI gate script
- worktree-clean blocking architecture-boundary gate plus report-only architecture-boundary and
  quality-baseline commands for explicit evidence generation
- worktree-clean `make ci-contract-gate` command wired through `make lint`
- worktree-clean `make maintainability-gate` command wired through `make lint`
- worktree-clean `make documentation-contract-gate` command wired through `make lint`
- worktree-clean `make quality-scorecard-gate` command wired through `make lint`
- worktree-clean `make implementation-truth-gate` command wired through `make lint`
- safe `make clean` command backed by a tested generated cleanup utility
- endpoint certification ledger and gate script
- Unit/integration/e2e tests
- standards docs (`docs/standards/*`)
- operations docs for observability and API certification
- supported-features placeholder and RFC implementation evidence directory with a machine-readable
  evidence manifest template covering slice closure, API certification, state-machine review,
  supported-feature review, wiki-publication posture, and downstream realization
- automation registration in `automation/repos.json` and `automation/service-map.json`

RFC-0072 note:

1. the backend scaffold now emits the explicit lane model by default,
2. existing repos still need their own convergence rollout,
3. the template contract is defined in `Backend-CI-Lane-Template-Contract.md`.

Use `-SkipAutomationRegistration` only for temporary local experiments.

