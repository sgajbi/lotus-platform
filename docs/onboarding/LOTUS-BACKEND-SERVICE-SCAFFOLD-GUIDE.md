# Lotus Backend Service Scaffold Guide

This guide explains how to use `automation/New-Lotus-Service.ps1` and what a generated Lotus
backend service starts with.

The scaffold creates a governed baseline for a new Lotus backend repository. It does not create a
finished product, domain authority, security model, data model, or business workflow. Owning teams
must replace placeholders with implementation-backed truth before promoting any capability as
supported.

Reusable scaffold lessons discovered during new-service creation are tracked in
`docs/onboarding/LOTUS-SERVICE-SCAFFOLD-LESSONS.md`. Repeated lessons should be promoted into
`automation/New-Lotus-Service.ps1` and this guide rather than fixed only in the generated app.

## When To Use It

Use the scaffold when creating a new Lotus backend repository that should start from the standard
bank-buyable baseline:

1. a domain-authoritative service,
2. an experience API,
3. a shared capability service,
4. a client-facing backend surface.

Do not use the scaffold to add a feature to an existing service. Existing services should be
improved in-place using their repository-native commands, contracts, tests, docs, and wiki source.

## Command

Basic local scaffold:

```powershell
cd C:\Users\<user>\projects\lotus-platform
powershell -ExecutionPolicy Bypass -File automation/New-Lotus-Service.ps1 `
  -ServiceName lotus-example `
  -Description "Example Lotus backend service" `
  -ServiceProfile domain-service `
  -DestinationRoot C:\Users\<user>\projects
```

Full governed bootstrap with GitHub provisioning:

```powershell
cd C:\Users\<user>\projects\lotus-platform
powershell -ExecutionPolicy Bypass -File automation/New-Lotus-Service.ps1 `
  -ServiceName lotus-example `
  -Description "Example Lotus backend service" `
  -BusinessRole "Owns example domain workflow supportability" `
  -ServiceProfile domain-service `
  -DevHostName example `
  -Port 8130 `
  -InitializeGit `
  -CreateGithubRepo `
  -GithubVisibility public `
  -EnableGithubDefaults `
  -ApplyMainBranchProtection
```

Use `-SkipAutomationRegistration` only for temporary local experiments. A real Lotus service should
be registered so platform automation, context, onboarding, and governance can discover it.

## Service Profiles

`-ServiceProfile` controls the generated role description and repository context posture. If it is
omitted, it defaults from `-Category` for backward compatibility.

| Profile | Use when | Default posture |
| --- | --- | --- |
| `domain-service` | The service owns authoritative business-domain behavior. | Keep business rules in domain/application modules and expose explicit source-owned APIs. |
| `experience-api` | The service composes backend services for a client or UI contract. | Keep client contracts stable without drifting into domain-owned business logic. |
| `shared-capability-service` | The service owns a reusable capability such as documents, archive, AI, provider access, or platform support. | Keep capability boundaries explicit and consumer-aware. |
| `client-facing-service` | The service exposes a customer- or advisor-facing backend surface. | Treat product-safe errors, permissions, auditability, and demo claims as first-class controls. |

Choose the profile based on ownership, not on implementation convenience. A profile is not a
readiness claim.

## Important Parameters

| Parameter | Purpose |
| --- | --- |
| `-ServiceName` | Repository and package identity, for example `lotus-risk`. |
| `-Description` | Human-readable service purpose used in README, context, and wiki source. |
| `-BusinessRole` | Explicit business responsibility. Defaults to `-Description` when omitted. |
| `-ServiceProfile` | Governed service profile. Use one of the profiles above. |
| `-Port` | Local service port used by generated runtime and automation metadata. |
| `-DevHostName` | Optional local ingress identity used when registering runtime/QA automation. |
| `-UpstreamDependencies` | Explicit upstream services or data products the generated context should list. |
| `-DownstreamDependencies` | Explicit consumers or downstream services the generated context should list. |
| `-IncludeMeshPlaceholders` | Opt-in only. Adds planned/not-certified mesh declaration placeholders for repos that know they will pursue mesh certification. |
| `-InitializeGit` | Initializes the generated repository and creates an initial commit. |
| `-CreateGithubRepo` | Creates the GitHub repository through `gh`. |
| `-EnableGithubDefaults` | Applies baseline repository settings. |
| `-ApplyMainBranchProtection` | Applies governed protected-`main` defaults. |
| `-SkipAutomationRegistration` | Skips platform automation registration for temporary experiments only. |
| `-Force` | Recreates the destination directory when intentionally regenerating a local test scaffold. |

## Generated Repository Shape

The generated repository starts with:

1. `AGENTS.md`
   The Lotus agent operating contract.
2. `REPOSITORY-ENGINEERING-CONTEXT.md`
   Service role, ownership boundaries, dependency map, commands, and next-step guidance.
3. `README.md`
   Fast entrypoint with service profile, quick start, validation commands, and standards links.
4. `wiki/`
   Repo-local GitHub wiki source with the standard Lotus operator/onboarding skeleton:
   `Home`, `Overview`, `Architecture`, `Getting Started`, `Development Workflow`,
   `Validation and CI`, `Operations Runbook`, `Security and Governance`, `Integrations`,
   `Roadmap`, `Supported Features`, and `_Sidebar`.
5. `.github/workflows/feature-lane.yml`
   Remote feature lane.
6. `.github/workflows/pr-merge-gate.yml`
   PR merge gate.
7. `.github/workflows/main-releasability.yml`
   Post-merge releasability gate.
8. `.github/workflows/pr-auto-merge.yml`
   Rebase auto-merge workflow for linear, non-squash history.
9. `.github/workflows/merged-pr-main-releasability.yml`
   Merged-PR dispatcher that starts Main Releasability after a PR lands on `main`.
10. `Makefile`
   Repo-native command surface for install, lint, typecheck, tests, coverage, security audit, and
   report-only baseline commands.
11. `src/app/`
    FastAPI app skeleton and layered package baseline.
12. `tests/unit`, `tests/integration`, `tests/e2e`
    Starting test pyramid.
13. `docs/operations/`
    Observability and API certification docs.
14. `docs/standards/`
    Service-local standards placeholders that must be replaced with service truth.
15. `quality/`
    Scorecard, architecture rules, CI-quality notes, refactor decision log, and generated baseline
    reports.
16. `supported-features/supported-features.json`
    Empty supported-feature registry with implementation-backed promotion policy.
17. `evidence/rfc-implementation/`
    Machine-readable evidence-manifest template for implementation slices.

For implementation-bearing RFCs with many slice evidence files, prefer a per-RFC folder under
`docs/rfcs/`, for example
`docs/rfcs/RFC-0002-enterprise-opportunity-intelligence-operating-layer/`. Keep the top-level
`docs/rfcs/README.md` as the navigation index.

The generated baseline is expected to pass `make ci` immediately after scaffold creation. Do not
lower coverage, dependency, OpenAPI, supported-feature, endpoint-certification, or security gates to
make a new app appear ready. Fix the scaffold or the generated app so the gate remains meaningful.

Generated workflow templates must also pass the platform workflow action runtime baseline. Keep
`actions/checkout`, `actions/setup-python`, `actions/upload-artifact`,
`actions/download-artifact`, and `docker/setup-buildx-action` aligned with
`platform-standards/Workflow-Action-Runtime-and-Version-Baseline.md`; do not accept GitHub runner
Node-runtime deprecation warnings as harmless noise. The `Main Releasability Gate` must generate
release evidence with the supported `cyclonedx-py` console command after `make install`, producing
`sbom.cdx.json` and `release-evidence.json`.
The merged-PR dispatcher must call `gh workflow run main-releasability.yml --ref main` so rebase
auto-merged PRs still produce explicit post-merge release evidence.
The auto-merge workflow must use `LOTUS_AUTOMERGE_TOKEN`, not `GITHUB_TOKEN`, so the merge event is
not suppressed before the dispatcher can run.

Generated workflows also declare job-level `timeout-minutes` values. The generated CI contract gate
blocks missing timeouts and `continue-on-error: true` in critical lanes so a stuck job or soft-failed
quality step cannot look like a valid enterprise gate.

Generated workflows set Git's default initial branch to `main` through workflow environment so
checkout does not emit default-branch hints. Generated Dockerfiles set
`PIP_ROOT_USER_ACTION=ignore` in controlled build stages so Docker build logs do not emit root-pip
warnings for expected image-build installs. Coverage artifact aggregation jobs set
`NODE_OPTIONS=--no-deprecation` because the current approved `actions/download-artifact@v8`
runtime can emit an upstream Node `Buffer()` deprecation warning even when repository workflow
configuration is otherwise current.

## Layered Application Baseline

Generated backend code starts with this package layout:

| Path | Responsibility |
| --- | --- |
| `src/app/main.py` | FastAPI application entrypoint, health/readiness, metadata, middleware registration. |
| `src/app/api/` | Thin route modules and HTTP DTO mapping. |
| `src/app/application/` | Use-case orchestration and application services. |
| `src/app/domain/` | Framework-free domain models, policies, and calculations. |
| `src/app/ports/` | Interfaces for external dependencies used by application logic. |
| `src/app/infrastructure/` | Concrete adapters and external clients behind ports. |
| `src/app/observability/` | Structured logging, correlation, tracing, and metrics helpers. |
| `src/app/security/` | Caller context and product-safe authorization policy primitives. |
| `src/app/resilience/` | Retry, backoff, timeout, and circuit-breaker policy primitives. |
| `src/app/contracts/` | API and contract models. |
| `src/app/middleware/` | Shared request middleware. |

Default dependency direction:

1. `api` depends on `application`,
2. `application` depends on `domain` and `ports`,
3. `domain` does not import API, infrastructure, FastAPI, persistence, or HTTP clients,
4. `infrastructure` implements `ports`,
5. `security`, `resilience`, and `observability` provide shared support primitives.

## Starting Runtime Features

The scaffold includes implementation-backed starter behavior:

1. FastAPI application bootstrap.
2. `GET /health`
3. `GET /health/live`
4. `GET /health/ready`
5. `GET /metadata`
6. `/metrics` outside the OpenAPI schema.
7. Correlation-id and trace-id propagation through response headers.
8. Structured JSON application events.
9. Product-safe problem-details error responses.
10. OpenAPI summaries, descriptions, tags, and success examples for starter endpoints.
11. Dockerfile and Docker healthcheck baseline.
12. Caller-context and capability-policy primitives with product-safe permission denied responses.
13. Downstream JSON client template with base URL validation, timeouts, trace propagation, and safe upstream error mapping.
14. Write-capable profiles start with idempotency and audit domain models plus focused tests.

These are platform starter features. They are not proof that the service has implemented its domain
workflow.

## Starting Governance And Quality Features

The scaffold starts with deterministic blocking gates for low-noise controls:

1. `make lint`
2. `make typecheck`
3. `make architecture-boundary-gate`
4. `make openapi-gate`
5. `make supported-features-gate`
6. `make endpoint-certification-gate`
7. `make ci-contract-gate`
8. `make test`
9. `make ci`
10. `make security-audit`

Remote scaffolded workflows use the same controls across Feature Lane, PR Merge Gate, and Main
Releasability. Main releasability additionally retains coverage evidence plus the dependency SBOM
and release metadata manifest required by
`platform-standards/Release-Evidence-and-SBOM-Foundation-Standard.md`.

Blocking scaffold gates must not create or rewrite durable report artifacts in a clean checkout.
For example, `make architecture-boundary-gate` runs in blocking mode and should leave the worktree
clean when it passes or fails. Generate review evidence explicitly with the matching report command
instead.

`make ci-contract-gate` is also blocking from day one. It prevents scaffold or agent changes from
silently removing Makefile targets, least-privilege workflow permissions, approved workflow action
majors, 99 percent merge/releasability coverage, Docker validation, release evidence,
endpoint-certification, supported-feature, security-audit, architecture, OpenAPI controls,
workflow-dispatch access, bounded job timeouts, no-soft-fail critical workflow posture,
non-suppressed auto-merge token usage, or merged-PR main-releasability dispatch.

It also starts with report-only quality evidence:

1. `make architecture-boundary-report`
2. `make quality-baseline`

Keep broad quality metrics report-only until `lotus-ci-enforcement-governance` proves the signal is
measured, deterministic, low-noise, lane-appropriate, and backed by an exception policy.

## Demo And Mesh Starting Point

The scaffold writes `docs/demo/demo-claims.md` as a demo-readiness ledger. Business claims start as
`Planned` unless generated code, tests, endpoint certification, supported-feature evidence, and
validation artifacts already prove the claim.

Allowed demo claim statuses are:

1. `Implemented`
2. `Partially implemented`
3. `Planned`
4. `Not applicable`
5. `Unknown - requires owner review`

Mesh files are not generated by default. Use `-IncludeMeshPlaceholders` only when the new repo is
expected to become a mesh producer or consumer and needs starting placeholders for:

1. producer and consumer declarations,
2. trust telemetry,
3. SLO policy,
4. access policy,
5. evidence policy.

Those generated mesh files are explicitly `Planned` and `not_certified`. They are not readiness
claims and must be replaced with repo-owned implementation truth before certification.

## First Commands In The Generated Repo

After generation:

```powershell
cd C:\Users\<user>\projects\lotus-example
make install
make ci-contract-gate
make architecture-boundary-gate
make architecture-boundary-report
make quality-baseline
make check
make ci
```

If GitHub was provisioned, push the initial branch and confirm the remote Feature Lane, PR Merge
Gate, and Main Releasability Gate are green before treating the repository as ready for feature
work.

## Automation Registration

For real services, the scaffold updates platform discovery and governance files by default:

1. `automation/repos.json`
2. `automation/service-map.json`
3. `automation/repository-governance-policy.json`
4. `automation/test-coverage-policy.json`
5. `automation/qa-matrix.json` when `-DevHostName` is provided
6. `automation/task-profiles.json`
7. `context/lotus-context-manifest.json`
8. `context/ECOSYSTEM-REGISTRIES.md`
9. `context/LOTUS-QUICKSTART-CONTEXT.md`
10. `context/LOTUS-ENGINEERING-CONTEXT.md`
11. `context/CONTEXT-REFERENCE-MAP.md`
12. `docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md`
13. `wiki/Integrations.md`

The scaffolded wiki is intentionally current-state oriented. It must not claim business capability
support beyond health/readiness/metadata scaffolding until implementation, endpoint certification,
supported-feature registration, CI evidence, and publication proof exist.

Review those diffs before committing. Registration changes are platform truth and should not be
left on an unmerged branch.

## What Must Be Replaced Before Promotion

Before claiming a service capability is supported, replace scaffold placeholders with real service
truth:

1. domain model and ownership boundaries,
2. real route modules under `src/app/api/`,
3. application services under `src/app/application/`,
4. domain rules under `src/app/domain/`,
5. port interfaces and infrastructure adapters,
6. caller-context and authorization policy,
7. endpoint certification entries for every public operation,
8. supported-features entries only for implementation-backed behavior,
9. observability runbook details for real dependencies and failure states,
10. security model and data-handling assumptions,
11. quality scorecard status and residual risk,
12. README, repo context, docs, and wiki source.

Demo claims must stay `Planned` until code, tests, endpoint certification, and evidence exist.

## Common Extension Sequence

For the first implementation slice in a generated service:

1. Read `AGENTS.md`, Lotus central context, and the generated repo context.
2. Create a feature branch from clean `main`.
3. Choose one capability or integration boundary.
4. Add domain/application code before route complexity grows.
5. Keep routes thin and product-safe.
6. Add meaningful unit tests for domain/application behavior.
7. Add integration or contract tests for public API behavior.
8. Update endpoint certification, supported-features, docs, and wiki source only for implemented
   behavior.
9. Run `make check` and the relevant focused tests.
10. Raise a PR with validation evidence, residual risks, and any follow-up backlog.

## What The Scaffold Does Not Provide

The scaffold does not provide:

1. production authentication or authorization,
2. service-specific persistence,
3. migrations,
4. real upstream/downstream clients,
5. business calculations,
6. certified domain-data-product declarations,
7. certified mesh telemetry, SLO, access, or evidence policies,
8. runtime SLOs,
9. service-specific dashboards and alerts,
10. load or latency budgets,
11. bank-buyable readiness by itself.

Treat the scaffold as `L1 Governed baseline` material from the Lotus Bank-Buyable Engineering
Contract, not as procurement-ready evidence.

## Validation For Scaffold Changes

When changing the scaffold itself in `lotus-platform`, run at minimum:

```powershell
python -m pytest tests/unit/test_repository_hygiene_scaffold_contract.py -q
python -m pytest tests/unit/test_ci_governance_documentation_contract.py -q
python -m pytest tests/unit/test_analytics_ui_scaffold_ci_enforcement.py -q
python automation/validate_engineering_context_system.py
powershell -ExecutionPolicy Bypass -File automation/Invoke-PlatformRepoChecks.ps1 -Lane feature
```

`Invoke-PlatformRepoChecks.ps1` uses checked command execution and fails the lane on the first
nonzero native command exit code; do not add unchecked command invocations to that wrapper.

If repo-local wiki source changes, also run:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Sync-RepoWikis.ps1 -CheckOnly -Repository lotus-platform
```

After merge to `main`, publish wiki source with:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Sync-RepoWikis.ps1 -Publish -Repository lotus-platform
```

