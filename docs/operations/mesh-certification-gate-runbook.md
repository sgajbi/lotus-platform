# Mesh Certification Gate Runbook

This runbook covers the RFC-0089 mesh certification gate.

The gate turns Lotus domain-product mesh evidence into an operational control. It validates the
first-wave product declarations, RFC-0087 trust telemetry snapshots, live trust certification,
gateway publication posture, and Workbench discovery consumption posture.

## When To Run

Run the gate when any of these change:

1. `platform-contracts/domain-data-products/`
2. `platform-contracts/trust-telemetry/`
3. `generated/domain-product-catalog.json`
4. `generated/domain-product-dependency-graph.json`
5. first-wave producer telemetry snapshots in `lotus-core`, `lotus-performance`, `lotus-risk`, or
   `lotus-advise`
6. `lotus-gateway` domain-product publication routes or contracts
7. `lotus-workbench` `/data-products` discovery surface or BFF consumption code

## Commands

Platform-only advisory smoke:

```powershell
python automation/mesh_certification_gate.py --mode advisory --generated-at-utc 2026-04-20T00:00:00Z --skip-publication-checks
```

Blocking local proof with sibling repositories:

```powershell
python automation/mesh_certification_gate.py --mode blocking --generated-at-utc 2026-04-20T00:00:00Z --require-sibling-repos
```

The blocking command expects these sibling checkouts next to `lotus-platform`:

1. `lotus-core`
2. `lotus-performance`
3. `lotus-risk`
4. `lotus-advise`
5. `lotus-gateway`
6. `lotus-workbench`

## Outputs

The gate writes operator artifacts to `output/mesh-certification/`:

1. `mesh-certification-status.json`
2. `mesh-certification-status.md`
3. `mesh-certification-issues.json`

Use JSON for automation and Markdown for human review. They are rendered from the same status object.

## Required First-Wave Products

Blocking mode applies to:

1. `lotus-core:PortfolioStateSnapshot:v1`
2. `lotus-performance:ReturnsSeriesBundle:v1`
3. `lotus-risk:RiskMetricsReport:v1`
4. `lotus-advise:AdvisoryProposalLifecycleRecord:v1`

Other catalog products may be reported as advisory posture until they are deliberately promoted into
the blocking certification set.

## Fix-Forward Guide

| Issue code | Meaning | Fix-forward action |
| --- | --- | --- |
| `missing_telemetry` | A required first-wave product has no telemetry snapshot. | Add or refresh the producer repo snapshot under `contracts/trust-telemetry/`. |
| `invalid_telemetry` | A snapshot failed the RFC-0087 schema or catalog identity checks. | Run `python automation/validate_trust_telemetry.py <snapshot>` and fix the reported field. |
| `stale_telemetry` | Freshness is not `current`. | Refresh the producer snapshot or fix the producer's freshness evaluation. |
| `product_blocked` | The producer declared the product blocked. | Fix the upstream break or keep the block and do not merge dependent publication changes. |
| `completeness_attention_required` | Completeness is stale, partial, unknown, or blocked. | Fix the producer evidence so the snapshot can claim complete posture. |
| `reconciliation_attention_required` | Reconciliation is stale, unreconciled, break-open, or unknown. | Fix reconciliation evidence or keep the gate blocked. |
| `data_quality_attention_required` | Data quality failed, blocked, or unknown. | Fix data-quality evidence before marking the product certified. |
| `lineage_not_materialized` | Required lineage evidence is not materialized. | Materialize lineage evidence or document why the product cannot be certified. |
| `catalog_drift` | Required product identity or source-manifest posture drifted. | Regenerate discovery artifacts or restore the repo-native declaration/source manifest. |
| `gateway_publication_drift` | Gateway no longer exposes the required discovery/trust route family. | Restore the gateway route/contract evidence and run gateway repo-native tests. |
| `workbench_consumption_drift` | Workbench discovery is missing or bypasses gateway/BFF. | Restore `/data-products` and gateway/BFF-only consumption. |

## Review Expectations

Before marking RFC-0089 implemented:

1. run the blocking local proof with sibling repositories,
2. run `powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane feature`,
3. open a PR and wait for Feature Lane and PR Merge Gate,
4. include the mesh certification output summary in PR evidence,
5. complete the RFC second-last governance/API-certification slice,
6. complete the final docs/context/wiki/skills/branch-hygiene slice.
