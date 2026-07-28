from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT_PATH = (
    ROOT / "context" / "contracts" / "lotus-idea-rfc0002-platform-proof-consumption.json"
)
DEFAULT_SCHEMA_PATH = (
    ROOT
    / "context"
    / "contracts"
    / "lotus-idea-rfc0002-platform-proof-consumption.schema.json"
)

EXPECTED_BROKER_REQUIRED_CHECKS = {
    "timezoneAwareGeneratedAtUtc",
    "httpServiceRuntimeMode",
    "brokerConfigured",
    "publisherAdapterObserved",
    "sourceSafeEnvelopePublished",
    "publicationAccepted",
    "failureReasonBounded",
    "supportabilityStatusNotPromoted",
    "nonProofClaimsRetained",
}
EXPECTED_CONSUMER_REQUIRED_CHECKS = {
    "timezoneAwareGeneratedAtUtc",
    "adviseConsumerRuntimeObserved",
    "manageConsumerRuntimeObserved",
    "reportConsumerRuntimeObserved",
    "consumerProofRefsBound",
    "consumerProofDigestsBound",
    "domainConsumerCoverageComplete",
    "gatewayWorkbenchProofSeparated",
    "platformMeshPublicationProofSeparated",
    "nonProofClaimsRetained",
}
EXPECTED_BROKER_REMAINING_BLOCKERS = {
    "downstream_consumer_runtime_proof_missing",
    "platform_mesh_event_publication_proof_missing",
    "gateway_workbench_proof_missing",
    "supported_feature_promotion_missing",
}
EXPECTED_CONSUMER_REMAINING_BLOCKERS = {
    "platform_mesh_event_publication_proof_missing",
    "gateway_workbench_proof_missing",
    "supported_feature_promotion_missing",
}
EXPECTED_FALSE_CLAIMS = {
    "downstreamConsumersCertified",
    "platformMeshEventCertified",
    "gatewayWorkbenchProofPresent",
    "supportedFeaturePromoted",
    "productionCertificationGranted",
    "certificationClosed",
}
EXPECTED_CONSUMER_FALSE_CLAIMS = {
    "platformMeshEventCertified",
    "gatewayWorkbenchProofPresent",
    "supportedFeaturePromoted",
    "productionCertificationGranted",
    "certificationClosed",
}
EXPECTED_DOMAIN_CONSUMERS = {"lotus-advise", "lotus-manage", "lotus-report"}
EXPECTED_COST_REQUIRED_CHECKS = {
    "decimalMoneyRepresentation",
    "halfEvenRounding",
    "sharedPlatformResidualAssignment",
    "resourceObservationDigestBound",
    "rawBillingRowsExcluded",
    "providerAccountIdentifiersExcluded",
    "attestationRepositoryPinned",
    "signerWorkflowPinned",
    "mainSourceRefPinned",
    "subjectDigestPinned",
    "supportedFeatureNotPromoted",
    "runtimeServiceSplitNotIntroduced",
}
EXPECTED_DEPLOYMENT_REQUIRED_CHECKS = {
    "digestImageReferenceOnly",
    "sbomReferenceBound",
    "signatureReferenceBound",
    "provenanceAttestationReferenceBound",
    "deploymentPendingHasNoDeployedDigest",
    "stagingFollowUpIssueRetained",
    "productionFollowUpIssueRetained",
    "operatorRunbookBound",
    "mutableTagsRejected",
    "productionCertificationNotClaimed",
}
EXPECTED_COST_REMAINING_BLOCKERS = {
    "protected_finops_runner_missing",
    "protected_cost_attribution_execution_missing",
    "attested_cost_artifact_verification_missing",
    "lotus_idea_consumer_certification_missing",
    "production_cost_attribution_missing",
}
EXPECTED_DEPLOYMENT_REMAINING_BLOCKERS = {
    "staging_deployed_digest_observation_missing",
    "production_deployed_digest_observation_missing",
    "same_digest_promotion_evidence_missing",
    "protected_migration_execution_missing",
    "supported_feature_promotion_missing",
}
EXPECTED_COST_FALSE_CLAIMS = {
    "costAttributionCertifiedWithoutAttestation",
    "applicationOwnsBillingAuthority",
    "providerBillingCredentialsPersisted",
    "supportedFeaturePromoted",
    "productionCertificationGranted",
    "certificationClosed",
}
EXPECTED_DEPLOYMENT_FALSE_CLAIMS = {
    "stagingDeploymentCertified",
    "productionDeploymentCertified",
    "sameDigestPromotionCertified",
    "productionCertificationGranted",
    "supportedFeaturePromoted",
    "certificationClosed",
}
EXPECTED_MESH_REQUIRED_CHECKS = {
    "repoNativeSourceManifestIncluded",
    "certificationCandidateNotRequiredProduct",
    "sloPolicyCoveragePresent",
    "accessPolicyCoveragePresent",
    "evidencePackPolicyCoveragePresent",
    "telemetryCollectionIncludesCandidate",
    "nonSnapshotTelemetryArtifactsIgnored",
    "gatewayWorkbenchProofSeparated",
    "supportedFeatureNotPromoted",
    "meshCertificationNotClaimed",
}
EXPECTED_MESH_REMAINING_BLOCKERS = {
    "platform_mesh_event_publication_proof_missing",
    "gateway_workbench_proof_missing",
    "supported_feature_promotion_missing",
    "data_product_certification_missing",
    "production_certification_missing",
}
EXPECTED_MESH_FALSE_CLAIMS = {
    "meshCertified",
    "requiredMaturityProduct",
    "platformMeshEventCertified",
    "gatewayWorkbenchProofPresent",
    "supportedFeaturePromoted",
    "productionCertificationGranted",
    "certificationClosed",
}
CERTIFICATION_BLOCKERS_THAT_MUST_REMAIN = {
    "idea_platform_mesh_event_publication_proof_missing",
    "idea_gateway_workbench_live_journey_proof_missing",
    "idea_protected_finops_execution_missing",
    "idea_attested_cost_artifact_verification_missing",
    "idea_staging_deployed_digest_observation_missing",
    "idea_production_deployed_digest_observation_missing",
    "idea_same_digest_promotion_evidence_missing",
    "idea_protected_migration_execution_missing",
    "idea_data_product_certification_missing",
    "idea_supported_feature_promotion_missing",
    "idea_production_certification_missing",
    "data_mesh_certification_and_platform_catalog",
    "supported_feature_promotion_missing",
    "platform_mesh_event_publication_proof_missing",
}
EXPECTED_PLATFORM_BLOCKERS_CLEARED = {
    "idea_external_broker_runtime_proof_dependency_consumable",
    "idea_downstream_consumer_runtime_proof_dependency_consumable",
    "idea_cost_attribution_contract_consumable",
    "idea_deployment_promotion_manifest_consumable",
    "idea_mesh_candidate_catalog_policy_consumable",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_contract(contract: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    _validate_header(contract, schema, errors)

    proofs = _runtime_proofs_by_name(contract.get("accepted_runtime_proofs"), errors)
    if proofs is None:
        return errors
    operational_proofs = _operational_proofs_by_name(
        contract.get("accepted_operational_proofs"), errors
    )
    if operational_proofs is None:
        return errors
    mesh_proofs = _mesh_proofs_by_name(contract.get("accepted_mesh_proofs"), errors)
    if mesh_proofs is None:
        return errors

    _validate_broker_runtime_proof(proofs["outbox_broker_runtime_execution"], errors)
    _validate_consumer_runtime_proof(proofs["outbox_consumer_runtime_execution"], errors)
    _validate_cost_attribution_operational_proof(
        operational_proofs["service_cost_attribution_contract_and_qualification"],
        errors,
    )
    _validate_deployment_promotion_operational_proof(
        operational_proofs["deployment_promotion_readiness_manifest"],
        errors,
    )
    _validate_mesh_publication_readiness_proof(
        mesh_proofs["platform_mesh_publication_readiness"],
        errors,
    )
    _validate_blocker_policy(contract, errors)
    _validate_boundaries(contract, errors)
    _validate_owner_evidence(contract, errors)
    _validate_local_commands(contract, errors)
    return errors


def _validate_header(
    contract: dict[str, Any],
    schema: dict[str, Any],
    errors: list[str],
) -> None:
    properties = schema.get("properties", {})
    if properties.get("contract_id", {}).get("const") != (
        "lotus-idea-rfc0002-platform-proof-consumption"
    ):
        errors.append("schema contract_id const is not governed")
    if properties.get("contract_version", {}).get("const") != "1.3.0":
        errors.append("schema contract_version const must be 1.3.0")
    if contract.get("contract_id") != "lotus-idea-rfc0002-platform-proof-consumption":
        errors.append("contract_id must be lotus-idea-rfc0002-platform-proof-consumption")
    if contract.get("contract_version") != "1.3.0":
        errors.append("contract_version must be 1.3.0")
    if contract.get("governed_by_rfc") != "RFC-0002":
        errors.append("governed_by_rfc must be RFC-0002")
    if contract.get("product_id") != "lotus-idea:IdeaCandidate:v1":
        errors.append("product_id must remain lotus-idea:IdeaCandidate:v1")
    if contract.get("producer_repository") != "lotus-idea":
        errors.append("producer_repository must remain lotus-idea")
    if contract.get("platform_posture") != "certification_candidate_not_certified":
        errors.append("platform_posture must keep IdeaCandidate not certified")


def _runtime_proofs_by_name(
    proofs: object,
    errors: list[str],
) -> dict[str, dict[str, Any]] | None:
    if not isinstance(proofs, list) or len(proofs) != 2:
        errors.append("accepted_runtime_proofs must contain exactly two bounded proofs")
        return None
    by_name: dict[str, dict[str, Any]] = {}
    for proof in proofs:
        if not isinstance(proof, dict):
            errors.append("accepted runtime proof must be an object")
            return None
        proof_name = proof.get("proof_name")
        if not isinstance(proof_name, str):
            errors.append("accepted runtime proof missing proof_name")
            return None
        if proof_name in by_name:
            errors.append(f"duplicate accepted runtime proof {proof_name}")
            return None
        by_name[proof_name] = proof
    expected_names = {
        "outbox_broker_runtime_execution",
        "outbox_consumer_runtime_execution",
    }
    if set(by_name) != expected_names:
        errors.append("accepted_runtime_proofs must contain broker and consumer runtime proofs")
        return None
    return by_name


def _operational_proofs_by_name(
    proofs: object,
    errors: list[str],
) -> dict[str, dict[str, Any]] | None:
    if not isinstance(proofs, list) or len(proofs) != 2:
        errors.append("accepted_operational_proofs must contain exactly two bounded proofs")
        return None
    by_name: dict[str, dict[str, Any]] = {}
    for proof in proofs:
        if not isinstance(proof, dict):
            errors.append("accepted operational proof must be an object")
            return None
        proof_name = proof.get("proof_name")
        if not isinstance(proof_name, str):
            errors.append("accepted operational proof missing proof_name")
            return None
        if proof_name in by_name:
            errors.append(f"duplicate accepted operational proof {proof_name}")
            return None
        by_name[proof_name] = proof
    expected_names = {
        "service_cost_attribution_contract_and_qualification",
        "deployment_promotion_readiness_manifest",
    }
    if set(by_name) != expected_names:
        errors.append(
            "accepted_operational_proofs must contain cost-attribution and "
            "deployment-promotion proofs"
        )
        return None
    return by_name


def _mesh_proofs_by_name(
    proofs: object,
    errors: list[str],
) -> dict[str, dict[str, Any]] | None:
    if not isinstance(proofs, list) or len(proofs) != 1:
        errors.append("accepted_mesh_proofs must contain exactly one bounded proof")
        return None
    proof = proofs[0]
    if not isinstance(proof, dict):
        errors.append("accepted mesh proof must be an object")
        return None
    proof_name = proof.get("proof_name")
    if proof_name != "platform_mesh_publication_readiness":
        errors.append(
            "accepted_mesh_proofs must contain platform_mesh_publication_readiness"
        )
        return None
    return {proof_name: proof}


def _validate_broker_runtime_proof(proof: dict[str, Any], errors: list[str]) -> None:
    _validate_expected_fields(
        proof,
        errors,
        {
            "proof_name": "outbox_broker_runtime_execution",
            "schema_version": "lotus-idea.outbox-broker-runtime-execution.v1",
            "repository": "lotus-idea",
            "proof_type": "outbox_broker_runtime_execution",
            "proof_scope": "configured_http_broker_publication",
            "evidence_class": "runtime_execution",
            "runtime_mode": "http_service",
            "broker_dependency": "lotus-platform-broker",
            "publisher_adapter": "HttpOutboxEventPublisher",
            "publish_path": "/events/lotus-idea/outbox",
        },
    )
    _validate_set_field(
        proof,
        errors,
        field_name="required_runtime_checks",
        expected=EXPECTED_BROKER_REQUIRED_CHECKS,
        error_message="broker required_runtime_checks must match Idea runtime proof checks",
    )
    _validate_exact_list(
        proof,
        errors,
        field_name="clears_only",
        expected=["external_broker_runtime_proof_missing"],
        error_message=(
            "broker runtime proof may clear only external_broker_runtime_proof_missing"
        ),
    )
    _validate_set_field(
        proof,
        errors,
        field_name="remaining_certification_blockers",
        expected=EXPECTED_BROKER_REMAINING_BLOCKERS,
        error_message=(
            "broker remaining_certification_blockers must preserve non-broker blockers"
        ),
    )
    _validate_set_field(
        proof,
        errors,
        field_name="must_remain_false",
        expected=EXPECTED_FALSE_CLAIMS,
        error_message="broker must_remain_false must preserve non-proof claim boundaries",
    )
    _require_refs(
        proof,
        errors,
        [
            "lotus-idea PR #732",
            "lotus-idea issue #694",
            "make outbox-broker-runtime-execution-proof-gate",
        ],
    )


def _validate_consumer_runtime_proof(proof: dict[str, Any], errors: list[str]) -> None:
    _validate_expected_fields(
        proof,
        errors,
        {
            "proof_name": "outbox_consumer_runtime_execution",
            "schema_version": "lotus-idea.outbox-consumer-runtime-execution.v1",
            "repository": "lotus-idea",
            "proof_type": "outbox_consumer_runtime_execution",
            "proof_scope": (
                "advise_manage_report_runtime_receipts_with_gateway_workbench_separated"
            ),
            "evidence_class": "runtime_execution",
            "runtime_mode": "local_asgi_testclient_aggregate",
        },
    )
    _validate_set_field(
        proof,
        errors,
        field_name="domain_consumers",
        expected=EXPECTED_DOMAIN_CONSUMERS,
        error_message="consumer domain_consumers must cover Advise, Manage, and Report",
    )
    _validate_set_field(
        proof,
        errors,
        field_name="required_runtime_checks",
        expected=EXPECTED_CONSUMER_REQUIRED_CHECKS,
        error_message="consumer required_runtime_checks must match Idea runtime proof checks",
    )
    _validate_exact_list(
        proof,
        errors,
        field_name="clears_only",
        expected=["downstream_consumer_runtime_proof_missing"],
        error_message=(
            "consumer runtime proof may clear only downstream_consumer_runtime_proof_missing"
        ),
    )
    _validate_set_field(
        proof,
        errors,
        field_name="remaining_certification_blockers",
        expected=EXPECTED_CONSUMER_REMAINING_BLOCKERS,
        error_message=(
            "consumer remaining_certification_blockers must preserve non-consumer blockers"
        ),
    )
    _validate_set_field(
        proof,
        errors,
        field_name="must_remain_false",
        expected=EXPECTED_CONSUMER_FALSE_CLAIMS,
        error_message="consumer must_remain_false must preserve non-proof claim boundaries",
    )
    _require_refs(
        proof,
        errors,
        [
            "lotus-idea PR #735",
            "lotus-idea issue #694",
            "lotus-idea issue #379",
            "make outbox-consumer-runtime-execution-proof-gate",
        ],
    )


def _validate_cost_attribution_operational_proof(
    proof: dict[str, Any],
    errors: list[str],
) -> None:
    _validate_expected_fields(
        proof,
        errors,
        {
            "proof_name": "service_cost_attribution_contract_and_qualification",
            "schema_version": "lotus-platform.service-cost-attribution.v1",
            "qualification_schema_version": (
                "lotus-platform.service-cost-attribution-qualification.v1"
            ),
            "repository": "lotus-platform",
            "proof_type": "service_cost_attribution",
            "proof_scope": "source_safe_service_cost_attribution_for_lotus_idea",
            "evidence_class": "source_contract",
            "evidence_status": "contract_available_protected_execution_pending",
            "consumer_repository": "lotus-idea",
        },
    )
    _validate_set_field(
        proof,
        errors,
        field_name="required_checks",
        expected=EXPECTED_COST_REQUIRED_CHECKS,
        error_message=(
            "cost-attribution required_checks must preserve Decimal, attestation, "
            "source-safe, and no-runtime-service-split controls"
        ),
    )
    _validate_exact_list(
        proof,
        errors,
        field_name="clears_only",
        expected=["cost_attribution_contract_consumable"],
        error_message=(
            "cost-attribution proof may clear only cost_attribution_contract_consumable"
        ),
    )
    _validate_set_field(
        proof,
        errors,
        field_name="remaining_certification_blockers",
        expected=EXPECTED_COST_REMAINING_BLOCKERS,
        error_message=(
            "cost-attribution remaining_certification_blockers must preserve "
            "protected FinOps execution and attestation blockers"
        ),
    )
    _validate_set_field(
        proof,
        errors,
        field_name="must_remain_false",
        expected=EXPECTED_COST_FALSE_CLAIMS,
        error_message=(
            "cost-attribution must_remain_false must reject billing authority and "
            "certification overclaims"
        ),
    )
    _require_refs(
        proof,
        errors,
        [
            "sgajbi/lotus-platform#495",
            "platform-contracts/cost-attribution/service-cost-attribution.schema.json",
            "automation/cost_attribution/qualification.py",
            ".github/workflows/service-cost-attribution-evidence.yml",
            "tests/unit/test_service_cost_attribution_attestation.py",
        ],
    )


def _validate_deployment_promotion_operational_proof(
    proof: dict[str, Any],
    errors: list[str],
) -> None:
    _validate_expected_fields(
        proof,
        errors,
        {
            "proof_name": "deployment_promotion_readiness_manifest",
            "schema_version": "lotus.deployment-promotion-manifest.v1",
            "repository": "lotus-platform",
            "proof_type": "deployment_promotion",
            "proof_scope": "release_bound_digest_promotion_readiness_for_lotus_idea",
            "evidence_class": "deployment",
            "evidence_status": "deployment_pending",
            "consumer_repository": "lotus-idea",
            "manifest_ref": (
                "platform-contracts/deployment-promotion/examples/"
                "lotus-idea-deployment-promotion.pending.json"
            ),
            "release_repository": "lotus-idea",
            "release_commit_sha": "f98ebce19720d29e0d9649786d20694cedcb8211",
            "release_workflow_run_id": "29982792450",
            "release_image_digest": (
                "sha256:a2ed6e706a56ac7d7845804f93bd50c6c342c8aabccca0bee96e6a51b300c7a2"
            ),
        },
    )
    _validate_set_field(
        proof,
        errors,
        field_name="required_checks",
        expected=EXPECTED_DEPLOYMENT_REQUIRED_CHECKS,
        error_message=(
            "deployment-promotion required_checks must preserve digest, SBOM, "
            "signature, attestation, pending, follow-up, and no-claim controls"
        ),
    )
    _validate_exact_list(
        proof,
        errors,
        field_name="clears_only",
        expected=["deployment_promotion_manifest_consumable"],
        error_message=(
            "deployment-promotion proof may clear only "
            "deployment_promotion_manifest_consumable"
        ),
    )
    _validate_set_field(
        proof,
        errors,
        field_name="remaining_certification_blockers",
        expected=EXPECTED_DEPLOYMENT_REMAINING_BLOCKERS,
        error_message=(
            "deployment-promotion remaining_certification_blockers must preserve "
            "live deployed-digest and protected migration blockers"
        ),
    )
    _validate_set_field(
        proof,
        errors,
        field_name="must_remain_false",
        expected=EXPECTED_DEPLOYMENT_FALSE_CLAIMS,
        error_message=(
            "deployment-promotion must_remain_false must reject deployment and "
            "production certification overclaims"
        ),
    )
    _require_refs(
        proof,
        errors,
        [
            "sgajbi/lotus-platform#599",
            "sgajbi/lotus-idea#375",
            "platform-contracts/deployment-promotion/examples/lotus-idea-deployment-promotion.pending.json",
            "automation/validate_deployment_promotion_manifest.py",
            "tests/unit/test_deployment_promotion_manifest.py",
        ],
    )


def _validate_mesh_publication_readiness_proof(
    proof: dict[str, Any],
    errors: list[str],
) -> None:
    _validate_expected_fields(
        proof,
        errors,
        {
            "proof_name": "platform_mesh_publication_readiness",
            "schema_version": "lotus-domain-product-source-manifest.v1",
            "repository": "lotus-platform",
            "proof_type": "mesh_publication_readiness",
            "proof_scope": "catalog_visible_candidate_with_policy_and_telemetry_coverage",
            "evidence_class": "source_contract",
            "evidence_status": "catalog_visible_not_certified",
            "consumer_repository": "lotus-idea",
            "product_id": "lotus-idea:IdeaCandidate:v1",
            "source_manifest_ref": (
                "platform-contracts/domain-data-products/"
                "domain-product-source-manifest.v1.json"
            ),
            "slo_policy_ref": (
                "platform-contracts/mesh-slo/"
                "lotus-idea-idea-candidate.slo.v1.json"
            ),
            "access_policy_ref": (
                "platform-contracts/mesh-access/"
                "lotus-idea-idea-candidate.access.v1.json"
            ),
            "evidence_policy_ref": (
                "platform-contracts/mesh-evidence/"
                "lotus-idea-idea-candidate.evidence-pack-policy.v1.json"
            ),
        },
    )
    _validate_set_field(
        proof,
        errors,
        field_name="required_checks",
        expected=EXPECTED_MESH_REQUIRED_CHECKS,
        error_message=(
            "mesh required_checks must preserve source-manifest, policy, telemetry, "
            "and no-certification controls"
        ),
    )
    _validate_exact_list(
        proof,
        errors,
        field_name="clears_only",
        expected=["mesh_candidate_catalog_policy_consumable"],
        error_message=(
            "mesh readiness proof may clear only "
            "mesh_candidate_catalog_policy_consumable"
        ),
    )
    _validate_set_field(
        proof,
        errors,
        field_name="remaining_certification_blockers",
        expected=EXPECTED_MESH_REMAINING_BLOCKERS,
        error_message=(
            "mesh remaining_certification_blockers must preserve mesh event, "
            "Gateway/Workbench, supported-feature, and certification blockers"
        ),
    )
    _validate_set_field(
        proof,
        errors,
        field_name="must_remain_false",
        expected=EXPECTED_MESH_FALSE_CLAIMS,
        error_message="mesh must_remain_false must reject certification overclaims",
    )
    _require_refs(
        proof,
        errors,
        [
            "sgajbi/lotus-platform#598",
            "sgajbi/lotus-idea#380",
            "sgajbi/lotus-idea#692",
            "platform-contracts/domain-data-products/domain-product-source-manifest.v1.json",
            "platform-contracts/mesh-slo/lotus-idea-idea-candidate.slo.v1.json",
            "platform-contracts/mesh-access/lotus-idea-idea-candidate.access.v1.json",
            "platform-contracts/mesh-evidence/lotus-idea-idea-candidate.evidence-pack-policy.v1.json",
            "automation/collect_trust_telemetry.py",
            "automation/mesh_certification_gate.py",
            "automation/mesh_maturity_scope.py",
            "tests/unit/test_trust_telemetry_collection.py",
        ],
    )


def _validate_expected_fields(
    proof: dict[str, Any],
    errors: list[str],
    expected_fields: dict[str, str],
) -> None:
    for field_name, expected_value in expected_fields.items():
        if proof.get(field_name) != expected_value:
            errors.append(f"{field_name} must be {expected_value}")


def _validate_set_field(
    proof: dict[str, Any],
    errors: list[str],
    *,
    field_name: str,
    expected: set[str],
    error_message: str,
) -> None:
    if set(proof.get(field_name) or []) != expected:
        errors.append(error_message)


def _validate_exact_list(
    proof: dict[str, Any],
    errors: list[str],
    *,
    field_name: str,
    expected: list[str],
    error_message: str,
) -> None:
    if proof.get(field_name) != expected:
        errors.append(error_message)


def _require_refs(
    proof: dict[str, Any],
    errors: list[str],
    required_refs: list[str],
) -> None:
    refs = proof.get("source_safe_evidence_refs") or []
    for required_ref in required_refs:
        if required_ref not in refs:
            errors.append(f"source_safe_evidence_refs missing {required_ref}")


def _validate_blocker_policy(contract: dict[str, Any], errors: list[str]) -> None:
    cleared = set(contract.get("platform_blockers_cleared") or [])
    forbidden_cleared = sorted(cleared & CERTIFICATION_BLOCKERS_THAT_MUST_REMAIN)
    if forbidden_cleared:
        errors.append(f"platform_blockers_cleared overclaims {forbidden_cleared}")
    if cleared != EXPECTED_PLATFORM_BLOCKERS_CLEARED:
        errors.append(
            "platform_blockers_cleared must contain only runtime, cost-contract, "
            "and deployment-readiness dependency markers"
        )

    retained = set(contract.get("platform_blockers_retained") or [])
    missing_retained = sorted(CERTIFICATION_BLOCKERS_THAT_MUST_REMAIN - retained)
    if missing_retained:
        errors.append(f"platform_blockers_retained missing {missing_retained}")


def _validate_boundaries(contract: dict[str, Any], errors: list[str]) -> None:
    boundaries = " ".join(contract.get("non_proof_boundaries") or [])
    for forbidden_claim in [
        "downstream consumer execution",
        "platform mesh event publication",
        "Gateway or Workbench live journey behavior",
        "supported feature",
        "data-product certification",
        "production certification",
        "production cost attribution",
        "billing authority",
        "staging or production deployment",
        "protected migration execution",
    ]:
        if forbidden_claim not in boundaries:
            errors.append(f"non_proof_boundaries must mention {forbidden_claim}")


def _validate_owner_evidence(contract: dict[str, Any], errors: list[str]) -> None:
    evidence_items = contract.get("owner_repo_evidence") or []
    owner_repositories = {item.get("repository") for item in evidence_items}
    if owner_repositories != {
        "lotus-idea",
        "lotus-gateway",
        "lotus-workbench",
        "lotus-platform",
    }:
        errors.append("owner_repo_evidence must cover Idea, Gateway, Workbench, and Platform")
    issues = {item.get("issue") for item in evidence_items}
    for required_issue in {
        "sgajbi/lotus-platform#495",
        "sgajbi/lotus-platform#598",
        "sgajbi/lotus-platform#599",
        "sgajbi/lotus-idea#380",
    }:
        if required_issue not in issues:
            errors.append(f"owner_repo_evidence missing {required_issue}")


def _validate_local_commands(contract: dict[str, Any], errors: list[str]) -> None:
    local_commands = contract.get("validation", {}).get("local_commands") or []
    if (
        "python automation/validate_lotus_idea_rfc0002_platform_proof_consumption.py"
        not in local_commands
    ):
        errors.append("validation local_commands missing platform proof-consumption validator")
    if (
        "python automation/validate_deployment_promotion_manifest.py --manifest "
        "platform-contracts/deployment-promotion/examples/"
        "lotus-idea-deployment-promotion.pending.json"
        not in local_commands
    ):
        errors.append("validation local_commands missing Idea deployment manifest validator")


def validate_default_paths(
    *,
    contract_path: Path = DEFAULT_CONTRACT_PATH,
    schema_path: Path = DEFAULT_SCHEMA_PATH,
) -> list[str]:
    return validate_contract(load_json(contract_path), load_json(schema_path))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate bounded platform consumption of Lotus Idea RFC-0002 proofs."
    )
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT_PATH)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    args = parser.parse_args()

    errors = validate_default_paths(
        contract_path=args.contract,
        schema_path=args.schema,
    )
    for error in errors:
        print(error)
    if errors:
        return 1
    print("Lotus Idea RFC-0002 platform proof-consumption contract is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
