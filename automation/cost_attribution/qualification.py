from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from automation.cost_attribution.attestation import (
    TRUSTED_REPOSITORY,
    TRUSTED_SIGNER_WORKFLOW,
    TRUSTED_SOURCE_REF,
    VerifiedCostAttributionAttestation,
)
from automation.cost_attribution.application import SCHEMA_VERSION


QUALIFICATION_SCHEMA_VERSION = (
    "lotus-platform.service-cost-attribution-qualification.v1"
)


def qualify_service_cost_attribution(
    *,
    artifact: dict[str, Any],
    attestation: VerifiedCostAttributionAttestation,
    generated_at_utc: datetime,
    qualification_run_id: str,
) -> dict[str, Any]:
    _validate_artifact(artifact)
    if generated_at_utc.tzinfo is None or generated_at_utc.utcoffset() is None:
        raise ValueError("generated_at_utc must be timezone-aware")
    if not qualification_run_id.strip():
        raise ValueError("qualification_run_id must not be blank")
    provenance = artifact["provenance"]
    if attestation.repository != TRUSTED_REPOSITORY:
        raise ValueError("cost-attribution attestation repository is not trusted")
    if attestation.signer_workflow != TRUSTED_SIGNER_WORKFLOW:
        raise ValueError("cost-attribution signer workflow is not trusted")
    if attestation.source_ref != TRUSTED_SOURCE_REF:
        raise ValueError(
            "cost-attribution evidence must originate from refs/heads/main"
        )
    if attestation.source_commit_sha != provenance["sourceCommitSha"]:
        raise ValueError(
            "attestation commit does not match cost-attribution provenance"
        )
    if provenance["sourceRef"] != TRUSTED_SOURCE_REF:
        raise ValueError("cost-attribution artifact source ref must be refs/heads/main")
    return {
        "schemaVersion": QUALIFICATION_SCHEMA_VERSION,
        "repository": "lotus-platform",
        "proofScope": "attested_service_cost_attribution_qualification",
        "claimPosture": "cost_attribution_certified",
        "generatedAtUtc": generated_at_utc.astimezone(UTC)
        .isoformat()
        .replace("+00:00", "Z"),
        "qualificationRunId": qualification_run_id,
        "service": artifact["service"],
        "billingPeriod": artifact["billingPeriod"],
        "currency": artifact["currency"],
        "resourceObservation": artifact["resourceObservation"],
        "costAttributionArtifactSha256": attestation.subject_sha256,
        "sourceCommitSha": attestation.source_commit_sha,
        "sourceRef": attestation.source_ref,
        "signerWorkflow": attestation.signer_workflow,
        "attestationRepository": attestation.repository,
        "attestationVerified": True,
        "costAttributionCertified": True,
        "supportedFeaturePromoted": False,
    }


def _validate_artifact(artifact: dict[str, Any]) -> None:
    if artifact.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("unsupported cost-attribution artifact schema")
    if artifact.get("repository") != "lotus-platform":
        raise ValueError("cost-attribution artifact repository must be lotus-platform")
    if artifact.get("proofScope") != "source_safe_service_cost_attribution":
        raise ValueError("cost-attribution artifact proof scope is invalid")
    if artifact.get("claimPosture") != "reconciled_not_attested":
        raise ValueError(
            "cost-attribution artifact must be reconciled before qualification"
        )
    if artifact.get("costAttributionReconciled") is not True:
        raise ValueError("cost-attribution artifact is not reconciled")
    if artifact.get("costAttributionCertified") is not False:
        raise ValueError("pre-attestation artifact must remain uncertified")
    if artifact.get("certificationBlockers") != ["artifact_attestation_missing"]:
        raise ValueError("pre-attestation artifact blockers are inconsistent")
    if artifact.get("supportedFeaturePromoted") is not False:
        raise ValueError(
            "cost-attribution evidence must not promote supported features"
        )
    for name in ("service", "billingPeriod", "resourceObservation", "provenance"):
        if not isinstance(artifact.get(name), dict):
            raise ValueError(f"cost-attribution artifact {name} must be an object")
