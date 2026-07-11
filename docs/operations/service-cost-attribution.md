# Service Cost Attribution Operations

## Scope

This runbook governs platform-owned generation and verification of aggregate service cost evidence.
It does not authorize application-owned billing calculations, expose raw provider exports, or
certify a business feature.

## Evidence Flow

```text
Authoritative normalized billing export
  -> JsonBillingExportAdapter
  -> deterministic Decimal allocation and reconciliation
  -> source-safe service attribution artifact
  -> protected mainline attestation
  -> consumer verification and qualification
```

The generated artifact remains `costAttributionCertified=false`. A consumer derives certification
only after verifying the exact subject digest against the governed repository, signer workflow,
main source ref, and source commit.

## Protected Production

Dispatch `Service Cost Attribution Evidence` from `main`.

| Control | Required value |
| --- | --- |
| Environment | `finops-production-evidence` |
| Runner labels | `self-hosted`, `lotus-finops-evidence` |
| Normalized export path | Environment secret `LOTUS_FINOPS_NORMALIZED_EXPORT_PATH` |
| Signer | `.github/workflows/service-cost-attribution-evidence.yml` |
| Source ref | `refs/heads/main` |

The workflow uploads and attests only
`output/cost-attribution/service-cost-attribution.json`. It must not upload the source export,
credentials, account identifiers, or raw billing rows.

## Operator Checks

Before dispatch:

1. confirm the billing authority, export version, period, and currency,
2. confirm completeness, freshness, partial-period, and correction posture,
3. confirm the service resource-observation digest and run identity,
4. confirm the allocation numerator and denominator use the governed methodology, and
5. obtain protected-environment approval independent of the requesting application.

After dispatch:

1. verify category allocations reconcile to the weighted source total,
2. verify any residual is assigned only to `shared_platform`,
3. verify the artifact excludes business and provider-account identifiers,
4. verify GitHub attestation against the exact artifact, and
5. retain the artifact, attestation, export digest, and correction lineage for audit.

## Failure Handling

| Condition | Action |
| --- | --- |
| Missing or stale export | Stop; do not issue qualification. |
| Partial billing period | Preserve blocked evidence; do not certify. |
| Unbalanced categories | Reject the export and reconcile at the billing authority. |
| Late adjustment or provider correction | Generate a new immutable artifact; retain the prior version. |
| Attestation/ref/commit/digest mismatch | Treat evidence as unverifiable and fail closed. |
| Billing source unavailable | Preserve prior evidence as historical only; do not infer current cost. |

Contract and methodology: [Service Cost Attribution](../../platform-contracts/cost-attribution/README.md).
