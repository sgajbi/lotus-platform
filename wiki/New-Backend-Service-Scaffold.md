# New Backend Service Scaffold

`automation/New-Lotus-Service.ps1` is the platform-owned generator for new Lotus backend
repositories.

Use it when a new backend service should start from the governed Lotus baseline: service profile,
layered package skeleton, repo-native Makefile, explicit CI lanes, starter health/readiness/API
behavior, product-safe errors, structured logs, quality scorecard, endpoint certification,
supported-feature governance, caller-context and capability-policy primitives, downstream-client
resilience templates, write-capable idempotency/audit models, demo-claims documentation, and
report-only architecture/quality evidence.

Blocking scaffold gates such as `make architecture-boundary-gate`, `make ci-contract-gate`,
`make maintainability-gate`, `make documentation-contract-gate`,
`make quality-scorecard-gate`, and `make implementation-truth-gate` are designed to be
worktree-clean. Use explicit report commands such as `make architecture-boundary-report` and
`make quality-baseline` when an RFC, PR, scorecard, or review needs durable quality artifacts.

`make ci-contract-gate` is the day-one anti-drift check for generated backend services. It prevents
future scaffold or agent changes from silently removing Makefile targets, least-privilege workflow
permissions, approved action majors, merge/releasability coverage, Docker validation, release
evidence, endpoint-certification, supported-feature, security-audit, architecture, or OpenAPI
controls. It also protects workflow-dispatch access and the merged-PR Main Releasability dispatch
needed for rebase auto-merged PRs, plus `LOTUS_AUTOMERGE_TOKEN` usage so the merge actor is not
the suppressed workflow token.

`make maintainability-gate` blocks oversized Python files/functions in `src`, `tests`, and
`scripts` so generated services start with conservative module-size guardrails before feature work
begins.

`make documentation-contract-gate` blocks deletion, thinning, missing anchors, and placeholder
erosion across generated README, repository context, standards, runbooks, quality, evidence, and
wiki surfaces so future agents and operators retain the context needed to apply the bank-buyable
contract.

`make quality-scorecard-gate` blocks bank-buyable scorecard drift. It validates the required
control matrix, approved readiness status vocabulary, evidence anchors, and stale scaffold-era
scorecard underclaims once certified business endpoint evidence exists.

`make implementation-truth-gate` is the day-one current-state claim guard for generated backend
services. It prevents generated or agent-authored README/docs/wiki text from claiming demo
readiness, production support, certification, live source ingestion, Gateway/Workbench support, or
client-ready publication before supported-feature evidence exists.

The scaffolded CI templates use the platform-approved workflow action runtime baseline and must not
ship with GitHub runner Node-runtime deprecation warnings. Main releasability also emits release
evidence: coverage artifacts, a CycloneDX dependency SBOM generated with `cyclonedx-py`, and a
release metadata manifest.
Generated repos also include a merged-PR dispatcher that starts Main Releasability on `main` after
PR completion.
The scaffolded auto-merge workflow requires `LOTUS_AUTOMERGE_TOKEN`; repositories without that
secret warn and skip auto-merge instead of failing the PR helper check. Those repositories should
use a human or release actor to rebase merge.

Detailed guide:

- [Lotus Backend Service Scaffold Guide](../docs/onboarding/LOTUS-BACKEND-SERVICE-SCAFFOLD-GUIDE.md)

Common command:

```powershell
cd C:\Users\<user>\projects\lotus-platform
powershell -ExecutionPolicy Bypass -File automation/New-Lotus-Service.ps1 `
  -ServiceName lotus-example `
  -Description "Example Lotus backend service" `
  -ServiceProfile domain-service `
  -DestinationRoot C:\Users\<user>\projects
```

Do not treat a generated repository as bank-buyable by default. The scaffold is a governed starting
point; the owning team must add real domain behavior, tests, endpoint certification,
supported-feature evidence, security posture, observability, runbooks, and wiki truth before
promoting capabilities.

Mesh placeholders are opt-in through `-IncludeMeshPlaceholders`. When generated, they start as
`Planned` and `not_certified` and must be replaced with repo-owned implementation and certification
evidence before any mesh readiness claim.

