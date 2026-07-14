# Deployment Promotion Proof

## Current Scope

This runbook defines the platform-owned proof that a Lotus deployment consumes the exact immutable
container image digest produced by service-owned release evidence. It does not certify any live
production deployment by itself.

The first proof set is `lotus-archive`, tracked by:

- `platform-contracts/deployment-promotion/examples/lotus-archive-deployment-promotion.valid.json`
- `automation/validate_deployment_promotion_manifest.py`
- GitHub issue `sgajbi/lotus-platform#522`

## Operator Workflow

1. Collect the service-owned `release-evidence.json`, SBOM, vulnerability scan, signature, and
   provenance attestation from the service repository's Main Releasability Gate.
2. Record the release image as `registry/repository/image@sha256:<digest>`. Do not use mutable tags.
3. Record each environment deployment manifest or observed deployed image digest.
4. Create or update a deployment promotion manifest under
   `platform-contracts/deployment-promotion/examples/` or the owning repository's approved evidence
   path.
5. Mark an environment as `included` only when its deployed digest can be reconciled to the release
   evidence digest.
6. Mark an environment as `out_of_scope` when no approved environment manifest or live deployed
   digest observation exists. Include the reason and follow-up issue.
7. Validate the manifest:

```powershell
python automation/validate_deployment_promotion_manifest.py --manifest <manifest>
```

## Evidence Locations

| Evidence | Owner | Location |
| --- | --- | --- |
| Release image digest | Service repository | `release-evidence.json` retained by Main Releasability |
| SBOM, scan, signature, attestation | Service repository | Main Releasability artifacts and registry attestation records |
| Deployment promotion manifest | `lotus-platform` or approved environment owner | `platform-contracts/deployment-promotion/` |
| Live deployed digest observation | Environment owner | Kubernetes, Helm, deployment platform, or approved runtime observation |
| Production certification | Release governance owner | Blocked until live production deployment proof exists |

## Failure Modes The Validator Blocks

- mutable image tags such as `:latest` or `:<commit>` without digest pinning,
- missing digest image refs,
- release-evidence digest mismatches,
- deployed digest mismatches,
- rebuild-per-environment promotion, and
- production certification claims before live deployment proof exists.

## Current Boundary

The `lotus-archive` example proves contract shape and digest reconciliation for the first platform
proof set. Production remains out of scope until an approved production deployment manifest and live
deployed-digest observation exist.
