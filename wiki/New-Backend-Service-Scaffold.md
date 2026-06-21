# New Backend Service Scaffold

`automation/New-Lotus-Service.ps1` is the platform-owned generator for new Lotus backend
repositories.

Use it when a new backend service should start from the governed Lotus baseline: service profile,
layered package skeleton, repo-native Makefile, explicit CI lanes, starter health/readiness/API
behavior, product-safe errors, structured logs, quality scorecard, endpoint certification,
supported-feature governance, caller-context and capability-policy primitives, downstream-client
resilience templates, write-capable idempotency/audit models, demo-claims documentation, and
report-only architecture/quality evidence.

Blocking scaffold gates such as `make architecture-boundary-gate` and `make ci-contract-gate` are
designed to be worktree-clean. Use explicit report commands such as
`make architecture-boundary-report` and `make quality-baseline` when an RFC, PR, scorecard, or
review needs durable quality artifacts.

`make ci-contract-gate` is the day-one anti-drift check for generated backend services. It prevents
future scaffold or agent changes from silently removing Makefile targets, least-privilege workflow
permissions, approved action majors, merge/releasability coverage, Docker validation, release
evidence, endpoint-certification, supported-feature, security-audit, architecture, or OpenAPI
controls.

The scaffolded CI templates use the platform-approved workflow action runtime baseline and must not
ship with GitHub runner Node-runtime deprecation warnings. Main releasability also emits release
evidence: coverage artifacts, a CycloneDX dependency SBOM generated with `cyclonedx-py`, and a
release metadata manifest.

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

