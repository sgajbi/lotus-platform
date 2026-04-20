# Mesh Certification Gate Runbook

This runbook covers the RFC-0089 mesh certification gate, the RFC-0090 GitHub
cross-repo PR Merge Gate workflow, and the RFC-0091 enterprise maturity extensions.

The gate turns Lotus domain-product mesh evidence into an operational control. It validates the
maturity-wave product declarations, RFC-0087 trust telemetry snapshots, live trust certification,
SLO policy, access policy, evidence-pack policy, lifecycle posture, gateway publication posture,
and Workbench discovery consumption posture.

## When To Run

Run the gate when any of these change:

1. `platform-contracts/domain-data-products/`
2. `platform-contracts/trust-telemetry/`
3. `generated/domain-product-catalog.json`
4. `generated/domain-product-dependency-graph.json`
5. `platform-contracts/mesh-slo/`
6. `platform-contracts/mesh-access/`
7. `platform-contracts/mesh-evidence/`
8. maturity-wave producer telemetry snapshots in `lotus-core`, `lotus-performance`, `lotus-risk`,
   `lotus-advise`, `lotus-report`, or `lotus-manage`
9. `lotus-gateway` domain-product publication routes or contracts
10. `lotus-workbench` `/data-products` discovery surface or BFF consumption code

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
5. `lotus-report`
6. `lotus-manage`
7. `lotus-gateway`
8. `lotus-workbench`

## GitHub Cross-Repo Gate

RFC-0090 adds a dedicated GitHub Actions workflow:

```text
.github/workflows/mesh-certification-gate.yml
```

The workflow runs automatically on pull requests to `main` when mesh-impacting platform files
change. It can also be run manually from GitHub Actions as **Cross-Repo Mesh Certification Gate**.

Automatic pull-request runs cover:

1. `.github/workflows/mesh-certification-gate.yml`
2. `automation/mesh_certification_gate.py`
3. `automation/Invoke-PlatformRepoChecks.ps1`
4. `platform-contracts/domain-data-products/**`
5. `platform-contracts/trust-telemetry/**`
6. `platform-contracts/mesh-slo/**`
7. `platform-contracts/mesh-access/**`
8. `platform-contracts/mesh-evidence/**`
9. `generated/domain-product-catalog.json`
10. `generated/domain-product-dependency-graph.json`
11. `rfcs/RFC-0089-*`
12. `rfcs/RFC-0090-*`
13. `rfcs/RFC-0091-*`

The workflow checks out these repositories in sibling layout:

| Repository | Default ref | Checkout path |
| --- | --- | --- |
| `sgajbi/lotus-platform` | PR head | `lotus-platform` |
| `sgajbi/lotus-core` | `main` | `lotus-core` |
| `sgajbi/lotus-performance` | `main` | `lotus-performance` |
| `sgajbi/lotus-risk` | `main` | `lotus-risk` |
| `sgajbi/lotus-advise` | `main` | `lotus-advise` |
| `sgajbi/lotus-report` | `main` | `lotus-report` |
| `sgajbi/lotus-manage` | `main` | `lotus-manage` |
| `sgajbi/lotus-gateway` | `main` | `lotus-gateway` |
| `sgajbi/lotus-workbench` | `main` | `lotus-workbench` |

Manual runs support explicit branch or SHA override inputs:

1. `lotus_core_ref`
2. `lotus_performance_ref`
3. `lotus_risk_ref`
4. `lotus_advise_ref`
5. `lotus_report_ref`
6. `lotus_manage_ref`
7. `lotus_gateway_ref`
8. `lotus_workbench_ref`

Use overrides for coordinated cross-repo validation only. Empty inputs mean `main`.

Example manual proof:

```text
lotus_core_ref=feature/rfc0087-telemetry-refresh
lotus_performance_ref=main
lotus_risk_ref=main
lotus_advise_ref=main
lotus_report_ref=feature/rfc0091-report-product-rollout
lotus_manage_ref=feature/rfc0091-manage-product-rollout
lotus_gateway_ref=feature/rfc0085-domain-product-publication
lotus_workbench_ref=feature/rfc0088-self-serve-discovery
```

The workflow step summary records the refs used, gate mode, artifact name, certification state, and
issue counts. If an override ref cannot be checked out, treat the failure as checkout-related and
fix the ref or repository access before investigating certification issues.

## Outputs

The gate writes operator artifacts to `output/mesh-certification/`:

1. `mesh-certification-status.json`
2. `mesh-certification-status.md`
3. `mesh-certification-issues.json`
4. `enterprise-mesh-certification-status.json`
5. `enterprise-mesh-certification-status.md`
6. `enterprise-mesh-certification-issues.json`
7. `enterprise-mesh-operating-report.json`
8. `enterprise-mesh-operating-report.md`

Use JSON for automation and Markdown for human review. The `enterprise-*` files are compatibility
aliases for RFC-0091 evidence-pack and workflow consumers; they are rendered from the same status
object as the original RFC-0089 files.

The GitHub workflow uploads the same files as an artifact named:

```text
mesh-certification-<run-id>-<commit-sha>
```

Download that artifact from the workflow run when the gate fails. Inspect
`mesh-certification-status.md` first for the human summary, then use
`mesh-certification-issues.json` for exact issue codes and machine-readable evidence.

If the artifact is missing, the failure happened before the gate could write status. Check the
checkout, Python setup, and workflow infrastructure steps first.

## Enterprise Operating Report

RFC-0092 adds an operator-facing report generated from the current enterprise mesh certification
status plus optional certification-history records in
`output/mesh-evidence-packs/certification-history/`.

The report classifies the mesh into:

| Operating state | Meaning |
| --- | --- |
| `production_ready` | Current certification is clean and enough prior certification history exists to support seasoned production posture. |
| `production_ready_limited_history` | Current certification is clean, but history is still shallow. Use this wording for customer conversations until multiple history records exist. |
| `attention_required` | Current certification has warnings that need review before customer evidence export or new product promotion. |
| `blocked` | Current certification has errors or failed state. Stop mesh promotion and fix forward through owning repositories. |

The report also includes:

1. drift trend and consecutive certified run count,
2. regression since the previous history record,
3. product operating posture for every maturity-wave product,
4. escalation queue with severity, family, owner repository, product, remediation, and source
   evidence path,
5. state-specific operator guidance.

To regenerate it directly after a certification run:

```powershell
python automation/generate_enterprise_mesh_operating_report.py --generated-at-utc 2026-04-20T00:00:00Z
```

## Required Maturity-Wave Products

Blocking mode applies to:

1. `lotus-core:PortfolioStateSnapshot:v1`
2. `lotus-performance:ReturnsSeriesBundle:v1`
3. `lotus-risk:RiskMetricsReport:v1`
4. `lotus-advise:AdvisoryProposalLifecycleRecord:v1`
5. `lotus-report:ClientReportEvidencePack:v1`
6. `lotus-manage:PortfolioActionRegister:v1`

Other catalog products may be reported as advisory posture until they are deliberately promoted into
the blocking certification set.

## Maturity Check Families

The status object and Markdown summary classify issues into these operator-facing families:

| Family | What it means |
| --- | --- |
| `telemetry` | Missing, invalid, stale, blocked, incomplete, unreconciled, failed-quality, or missing-lineage telemetry. |
| `slo` | SLO policy drift or runtime SLO violation for freshness, completeness, reconciliation, quality, or lineage. |
| `access` | Mesh access-policy drift, including missing policy files or invalid gateway-only publication posture. |
| `lifecycle` | Required product lifecycle is no longer active/not-deprecated without governed successor and consumer-impact migration evidence. |
| `evidence` | Evidence-pack policy drift that would make customer/operator evidence incomplete or unsafe to export. |
| `catalog` | Source manifest, generated catalog, or dependency graph drift. |
| `gateway` | Gateway publication route or service drift. |
| `workbench` | Workbench discovery route or gateway/BFF-only consumption drift. |

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
| `mesh_slo_policy_drift` | Required SLO policy is missing or invalid. | Restore the platform SLO policy for the required product. |
| `mesh_slo_freshness_violation` | Runtime freshness exceeds the product SLO. | Refresh producer evidence or correct the freshness calculation. |
| `mesh_slo_completeness_violation` | Runtime completeness violates the product SLO. | Fix producer completeness evidence before certification. |
| `mesh_slo_reconciliation_violation` | Runtime reconciliation violates the product SLO. | Fix reconciliation evidence or keep certification blocked. |
| `mesh_slo_data_quality_violation` | Runtime data-quality posture violates the product SLO. | Fix data-quality evidence before certification. |
| `mesh_slo_lineage_violation` | Runtime lineage posture violates the product SLO. | Materialize lineage evidence or correct the policy/snapshot. |
| `mesh_access_policy_drift` | Required access policy is missing or invalid. | Restore the platform access policy for the required product. |
| `mesh_evidence_policy_drift` | Required evidence-pack policy is missing or invalid. | Restore evidence-pack policy before producing customer/operator evidence. |
| `mesh_lifecycle_drift` | Required maturity-wave product is not active/not-deprecated. | Restore active posture or add governed successor and consumer-impact migration evidence. |
| `catalog_drift` | Required product identity, source-manifest posture, or dependency-graph posture drifted. | Regenerate discovery artifacts or restore the repo-native declaration/source manifest. |
| `gateway_publication_drift` | Gateway no longer exposes the required discovery/trust route family. | Restore the gateway route/contract evidence and run gateway repo-native tests. |
| `workbench_consumption_drift` | Workbench discovery is missing or bypasses gateway/BFF. | Restore `/data-products` and gateway/BFF-only consumption. |

## Failure Classification

Use this order when debugging a GitHub run:

1. **Checkout failure**
   The failing step is one of the repository checkouts. Fix the branch input, repository name, or
   read access. Do not classify this as a mesh certification failure.
2. **Setup failure**
   The failing step is Python setup or timestamp resolution. Fix workflow infrastructure.
3. **Mesh certification failure**
   The `Run blocking mesh certification` step failed and artifacts were uploaded. Use the issue
   codes in `mesh-certification-issues.json` and the fix-forward table above.
4. **Artifact upload failure**
   The gate step passed or failed, but upload failed. Fix artifact path or workflow upload posture;
   do not change certification logic.

For private repository variants, cross-repo checkout requires a read-only token with access to the
first-wave sibling repositories. Do not hardcode tokens in workflow YAML.

## Review Expectations

Before marking RFC-0089 implemented:

1. run the blocking local proof with sibling repositories,
2. run `powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane feature`,
3. open a PR and wait for Feature Lane and PR Merge Gate,
4. include the mesh certification output summary in PR evidence,
5. complete the RFC second-last governance/API-certification slice,
6. complete the final docs/context/wiki/skills/branch-hygiene slice.

Before marking RFC-0090 implemented:

1. run workflow contract tests,
2. run workflow security and action runtime validators,
3. run the platform feature lane,
4. run the platform PR Merge Gate,
5. open a PR and verify the GitHub **Cross-Repo Mesh Certification Gate** runs for this workflow
   change,
6. include the uploaded artifact name and certification state in PR evidence,
7. complete the RFC second-last governance/API-certification slice,
8. complete the final docs/context/wiki/skills/branch-hygiene slice.
