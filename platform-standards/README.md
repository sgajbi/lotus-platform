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

1. `../Continuous Integration, Validation, and Release Governance Standard.md`
2. `../rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`

## One-Command Lotus Service Scaffold

```powershell
powershell -ExecutionPolicy Bypass -File automation/New-Lotus-Service.ps1 `
  -ServiceName lotus-risk `
  -Description "Risk and exposure analytics service" `
  -Port 8130
```

This generates a production-grade backend baseline with:

- explicit feature, PR merge, and main releasability workflows
- merge-commit auto-merge workflow
- scaffolded `.editorconfig`, `.gitattributes`, `.gitignore`, and `.dockerignore` from platform templates
- Makefile + lint/typecheck/test/coverage/security gates
- FastAPI app with health/readiness and metrics
- OpenAPI gate script
- Unit/integration/e2e tests
- standards docs (`docs/standards/*`)
- automation registration in `automation/repos.json` and `automation/service-map.json`

RFC-0072 note:

1. the backend scaffold now emits the explicit lane model by default,
2. existing repos still need their own convergence rollout,
3. the template contract is defined in `Backend-CI-Lane-Template-Contract.md`.

Use `-SkipAutomationRegistration` only for temporary local experiments.

