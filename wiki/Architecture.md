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

For RFC-0084, this now includes:

- producer and consumer declarations under `platform-contracts/domain-data-products/`
- identifier and temporal semantics under `platform-contracts/domain-vocabulary/domain-data-product-semantics.v1.json`
- trust metadata, evidence classes, and lineage bundle classes under
  `platform-contracts/domain-vocabulary/domain-data-product-trust-metadata.v1.json`

### `platform-stack/`

Shared local ingress and infrastructure support stack.

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
