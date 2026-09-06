# New Backend Service Scaffold

## Current Scope

`automation/New-Lotus-Service.ps1` is the platform-owned generator for new Lotus backend
repositories. It provides a governed engineering baseline, not a supported business capability or
production certification.

| Reader | Start Here | Decision |
| --- | --- | --- |
| Service owner | [Usage](#usage) | Choose the service profile and generate the repository. |
| API reviewer | [Response Example Parity](#response-example-parity) | Verify documented responses remain bound to code-owned serialization. |
| CI or platform owner | [Generated Controls](#generated-controls) | Review blocking gates and release evidence. |
| Product or governance reviewer | [Promotion Boundaries](#promotion-boundaries) | Confirm the scaffold is not being presented as feature support. |

Use it when a new backend service should start from the governed Lotus baseline: service profile,
layered package skeleton, repo-native Makefile, explicit CI lanes, starter health/readiness/API
behavior, product-safe errors, structured logs, quality scorecard, endpoint certification,
supported-feature governance, caller-context and capability-policy primitives, downstream-client
resilience templates, write-capable idempotency/audit models, demo-claims documentation, and
report-only architecture/quality evidence.

## Generated Controls

Blocking scaffold gates such as `make architecture-boundary-gate`, `make ci-contract-gate`,
`make maintainability-gate`, `make documentation-contract-gate`,
`make quality-scorecard-gate`, `make monetary-float-guard`,
`make source-observability-contract-gate`, `make operation-metric-contract-gate`, and
`make implementation-truth-gate` are designed to be worktree-clean. Use explicit report commands
such as `make architecture-boundary-report` and
`make quality-baseline` when an RFC, PR, scorecard, or review needs durable quality artifacts.

`make ci-contract-gate` is the day-one anti-drift check for generated backend services. It prevents
future scaffold or agent changes from silently removing Makefile targets, least-privilege workflow
permissions, approved action majors, merge/releasability coverage, Docker validation, release
evidence, endpoint-certification, supported-feature, security-audit, architecture, or OpenAPI
controls, plus operation metric contract posture. It also protects safe cleanup wiring, workflow-dispatch access, and the merged-PR Main
Releasability dispatch needed for rebase auto-merged PRs, plus `LOTUS_AUTOMERGE_TOKEN` usage so
the merge actor is not the suppressed workflow token.

`make clean` calls the generated `scripts/clean_generated_artifacts.py` utility. It removes only
known local cache, build, and coverage artifacts while pruning `.git`, `.venv`, and `node_modules`.
The generated CI contract gate fails if future changes replace that utility with an inline
Makefile command or remove the script.

`make maintainability-gate` blocks oversized Python files/functions in `src`, `tests`, and
`scripts` so generated services start with conservative module-size guardrails before feature work
begins.

`make monetary-float-guard` blocks money-like `float` annotations, literals,
return annotations, and conversions in generated application source. The guard
is AST-backed and allows non-monetary operational floats, such as timeout
seconds, so precision governance is strict without noisy exceptions.

`make documentation-contract-gate` blocks deletion, thinning, missing anchors, and placeholder
erosion across generated README, repository context, standards, runbooks, quality, evidence, and
wiki surfaces so future agents and operators retain the context needed to apply the bank-buyable
contract.

`make quality-scorecard-gate` blocks bank-buyable scorecard drift. It validates the required
control matrix, approved readiness status vocabulary, evidence anchors, and stale scaffold-era
scorecard underclaims once certified business endpoint evidence exists.

`make source-observability-contract-gate` blocks ad hoc application logging in `src/app`. Feature
code must use the central observability module rather than raw `print()`, direct Python logging, or
low-level `log_event` calls. Generated request diagnostics log route templates rather than raw URL
paths.

`make operation-metric-contract-gate` protects generated operation telemetry vocabulary. It keeps
the `*_operation_events_total` metric name, bounded label set, and forbidden sensitive operation
attribute keys source-safe before a service adds real business workflows. It does not certify
dashboards, alerts, business operations, data-mesh telemetry, or supported-feature promotion.

`make implementation-truth-gate` is the day-one current-state claim guard for generated backend
services. It prevents generated or agent-authored README/docs/wiki text from claiming demo
readiness, production support, certification, live source ingestion, Gateway/Workbench support, or
client-ready publication before supported-feature evidence exists.

`make endpoint-certification-gate` keeps public OpenAPI operations synchronized with the endpoint
ledger. Once a business/operator endpoint is marked `certified`, the ledger must also cite bounded
operation-event test evidence so API contract certification and supportability telemetry proof move
together. Health/readiness/metadata endpoints remain `baseline_certified`.

### Response Example Parity

Every `baseline_certified` or `certified` success example must also match code-owned runtime
serialization. The generated gate invokes safe static `GET` routes directly or loads an explicit
deterministic callable for endpoints that cannot be invoked safely during a contract check. It then
compares the complete JSON structure, including aliases, scalar types, blockers, statuses, and
version fields.

Dynamic timestamps, request IDs, or environment values require an explicit RFC 6901 field pointer
and an approved narrow normalizer. Readiness, supportability, certification, promotion, blocker,
schema, contract-version, and version fields cannot be normalized. A second copied documentation
literal is not runtime evidence.

The authoritative behavior is defined by
`platform-contracts/api-governance/endpoint-example-parity-contract.v1.json` and
`docs/standards/Endpoint Example Parity Standard.md`. This gate proves deterministic example
parity; it does not replace authorization, dependency, live-runtime, or supported-feature proof.

The scaffolded CI templates use the platform-approved workflow action runtime baseline and must not
ship with GitHub runner Node-runtime deprecation warnings. Main releasability also emits release
evidence: coverage artifacts, a CycloneDX dependency SBOM generated with `cyclonedx-py`, and a
release metadata manifest. The current deployable-image provenance target additionally covers Git
SHA image tags, OCI labels for commit/ref/source/version/build/run metadata, CI-only image push,
digest-bearing release manifests, SBOM, vulnerability scanning, signing, provenance attestation,
digest-based deploys, `/version` metadata parity, same-image promotion, and build-secret leak
checks.
Generated services also inherit the governed vulnerability and technology-maturity posture:
application libraries, runtime dependencies, base images, and deployable images default to mature,
widely deployed, well-documented, actively maintained technology. Beta, preview, experimental,
incubating, unsupported, or novelty-driven major upgrades require issue-backed, time-bounded
exceptions with ownership, vulnerability posture, compensating controls, rollback, expiry, and a
planned fix path before any bank-buyable or production-ready claim.
Generated repos also include a merged-PR dispatcher that starts Main Releasability on `main` after
PR completion.
The scaffolded auto-merge workflow requires `LOTUS_AUTOMERGE_TOKEN`; repositories without that
secret warn and skip auto-merge instead of failing the PR helper check. Those repositories should
use a human or release actor to rebase merge.

## Usage

Detailed guide:

- [Lotus Backend Service Scaffold Guide](https://github.com/sgajbi/lotus-platform/blob/main/docs/onboarding/LOTUS-BACKEND-SERVICE-SCAFFOLD-GUIDE.md)

Common command:

```powershell
$env:LOTUS_WORKSPACE_ROOT = "<workspace-root>"
Set-Location "$env:LOTUS_WORKSPACE_ROOT/lotus-platform"
powershell -ExecutionPolicy Bypass -File automation/New-Lotus-Service.ps1 `
  -ServiceName lotus-example `
  -Description "Example Lotus backend service" `
  -ServiceProfile domain-service `
  -DestinationRoot $env:LOTUS_WORKSPACE_ROOT
```

## Promotion Boundaries

Do not treat a generated repository as bank-buyable by default. The scaffold is a governed starting
point; the owning team must add real domain behavior, tests, endpoint certification,
supported-feature evidence, security posture, observability, runbooks, and wiki truth before
promoting capabilities.

Mesh placeholders are opt-in through `-IncludeMeshPlaceholders`. When generated, they start as
`Planned` and `not_certified` and must be replaced with repo-owned implementation and certification
evidence before any mesh readiness claim.

