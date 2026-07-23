# Deployment Promotion Contracts

This contract family governs platform-owned proof that a Lotus service deployment consumes the
same immutable image digest produced by service-owned release evidence.

## Contract

- `deployment-promotion-manifest.schema.json` defines the versioned manifest.
- `examples/lotus-archive-deployment-promotion.valid.json` is the first proof-set example.
- `examples/lotus-idea-deployment-promotion.pending.json` binds current `lotus-idea` mainline
  release evidence while explicitly preserving staging and production deployed-digest blockers.
- `automation/validate_deployment_promotion_manifest.py` validates the schema and semantic rules.

The manifest is intentionally separate from service-owned build provenance. Service repositories
still own Dockerfile hygiene, image build metadata, SBOM generation, vulnerability scans, Cosign
signatures, provenance attestations, and `release-evidence.json` generation.

## Required Proof

For every included environment, the validator requires:

1. image references in digest form, without mutable tags,
2. a deployed digest that matches the service release-evidence digest,
3. no rebuild between environments,
4. same-digest promotion when one included environment promotes from another, and
5. evidence refs for the release artifact and deployment manifest.

An environment can be out of scope only with an explicit reason and follow-up evidence. A manifest
with `deployment_evidence_status: deployment_pending` may contain only out-of-scope environments;
it is release-bound readiness evidence, not deployment proof. Out-of-scope production remains
non-certified until live deployment proof exists.

## Validation

```powershell
python automation/validate_deployment_promotion_manifest.py
python automation/validate_deployment_promotion_manifest.py --manifest platform-contracts/deployment-promotion/examples/lotus-archive-deployment-promotion.valid.json
python automation/validate_deployment_promotion_manifest.py --manifest platform-contracts/deployment-promotion/examples/lotus-idea-deployment-promotion.pending.json
```

The platform feature lane runs this validator so contract drift is blocked before PR merge.
