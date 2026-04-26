# Architecture

## Major platform surfaces

### `automation/`

PowerShell and Python automation for:

- repo checks
- PR monitoring
- background runs
- platform QA
- ingress diagnostics
- standards validation
- cross-app validation flows

### `context/`

Central Lotus context system:

- quickstart and engineering context
- reference map and task routing
- registries and manifest
- procedural memory and playbooks
- governed agent operating contract

### `platform-standards/`

Shared standards and scaffolds for backend repositories, workflows, and CI lanes.

### `platform-contracts/`

Machine-readable governance plane for ecosystem-wide contract families.

For the mesh platform, this now includes:

- producer and consumer declarations under `platform-contracts/domain-data-products/`
- identifier and temporal semantics under `platform-contracts/domain-vocabulary/domain-data-product-semantics.v1.json`
- trust metadata, evidence classes, and lineage bundle classes under
  `platform-contracts/domain-vocabulary/domain-data-product-trust-metadata.v1.json`
- trust telemetry contracts under `platform-contracts/trust-telemetry/`
- mesh SLO policies under `platform-contracts/mesh-slo/`
- mesh access policies under `platform-contracts/mesh-access/`
- mesh evidence-pack policies under `platform-contracts/mesh-evidence/`

### `generated/`

Derived platform evidence, not source truth:

- domain-product catalog
- domain-product dependency graph
- domain-product certification report
- enterprise mesh maturity matrix

### `platform-stack/`

Shared local ingress and infrastructure support stack. It includes service-owned infrastructure
needed for production-like local readiness, including `lotus-report-postgres` for the
`lotus-report` report-job and batch ledger.

This supports the ecosystem runtime, but it is not the canonical populated front-office product
proof path.

### `codex/skills/`

Platform-owned Lotus skills and governed skill manifest.

### `rfcs/`

Platform and ecosystem governance RFC inventory.

## Relationship to the rest of Lotus

1. `lotus-platform` defines platform-wide guidance and validators
2. each Lotus repo owns its own implementation truth
3. `lotus-workbench` owns canonical populated front-office runtime proof
4. `lotus-platform` owns the supporting governance, ingress, and validation system around that flow
5. `lotus-gateway` may remain the ecosystem API face, but RFC-0084 keeps product authority in the
   producing domain repositories rather than moving it into the gateway

## Enterprise mesh architecture

Lotus now has a governed data mesh control plane across the ecosystem:

1. domain repositories own repo-native product declarations and trust telemetry,
2. `lotus-platform` aggregates declarations, validates contracts, certifies trust posture, and
   produces derived catalog, graph, maturity, evidence, and operating artifacts,
3. `lotus-gateway` publishes the read-only domain-product API face without becoming product
   authority,
4. `lotus-workbench` consumes gateway/BFF APIs for self-serve discovery and dependency/trust UX,
5. RFC-0092 adds production operating posture over the certified mesh: operating state,
   limited-history honesty, drift trend, regression detection, product posture, escalation
   ownership, and operator guidance.

Current maturity-wave products:

1. `lotus-core:PortfolioStateSnapshot:v1`
2. `lotus-performance:ReturnsSeriesBundle:v1`
3. `lotus-risk:RiskMetricsReport:v1`
4. `lotus-advise:AdvisoryProposalLifecycleRecord:v1`
5. `lotus-report:ClientReportEvidencePack:v1`
6. `lotus-manage:PortfolioActionRegister:v1`

## Documentation layering

- `README.md`
  fast platform orientation
- `wiki/`
  operator and onboarding summaries
- `docs/`
  long-form guidance
- `context/`
  governed central context system
- `rfcs/`
  architectural and governance decisions

For the explicit Lotus split between README, `wiki/`, deep `docs/`, and platform `context/`, use
[Lotus Documentation Layering](../docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md).
