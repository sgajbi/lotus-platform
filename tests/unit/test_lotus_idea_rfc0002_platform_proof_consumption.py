from __future__ import annotations

import copy
import json
from pathlib import Path

from automation.validate_lotus_idea_rfc0002_platform_proof_consumption import (
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = (
    ROOT / "context" / "contracts" / "lotus-idea-rfc0002-platform-proof-consumption.json"
)
SCHEMA_PATH = (
    ROOT / "context" / "contracts" / "lotus-idea-rfc0002-platform-proof-consumption.schema.json"
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(contract: dict) -> list[str]:
    return validate_contract(contract, _load_json(SCHEMA_PATH))


def _proof_by_name(contract: dict, proof_name: str) -> dict:
    proofs = {
        proof["proof_name"]: proof for proof in contract["accepted_runtime_proofs"]
    }
    return proofs[proof_name]


def _operational_proof_by_name(contract: dict, proof_name: str) -> dict:
    proofs = {
        proof["proof_name"]: proof for proof in contract["accepted_operational_proofs"]
    }
    return proofs[proof_name]


def test_lotus_idea_rfc0002_platform_proof_contract_is_governed() -> None:
    readme = (ROOT / "context" / "contracts" / "README.md").read_text(
        encoding="utf-8"
    )
    contract = _load_json(CONTRACT_PATH)
    schema = _load_json(SCHEMA_PATH)

    assert "lotus-idea-rfc0002-platform-proof-consumption.schema.json" in readme
    assert "lotus-idea-rfc0002-platform-proof-consumption.json" in readme
    assert (
        schema["properties"]["contract_id"]["const"]
        == "lotus-idea-rfc0002-platform-proof-consumption"
    )
    assert contract["governed_by_rfc"] == "RFC-0002"
    assert contract["contract_version"] == "1.2.0"
    assert contract["platform_posture"] == "certification_candidate_not_certified"


def test_lotus_idea_rfc0002_platform_proof_contract_accepts_baseline() -> None:
    assert _validate(_load_json(CONTRACT_PATH)) == []


def test_broker_runtime_proof_may_clear_only_external_broker_dependency() -> None:
    contract = _load_json(CONTRACT_PATH)
    proof = _proof_by_name(contract, "outbox_broker_runtime_execution")

    assert proof["schema_version"] == "lotus-idea.outbox-broker-runtime-execution.v1"
    assert proof["evidence_class"] == "runtime_execution"
    assert proof["clears_only"] == ["external_broker_runtime_proof_missing"]
    assert "idea_external_broker_runtime_proof_dependency_consumable" in contract[
        "platform_blockers_cleared"
    ]


def test_broker_runtime_proof_retains_product_and_publication_boundaries() -> None:
    contract = _load_json(CONTRACT_PATH)
    proof = _proof_by_name(contract, "outbox_broker_runtime_execution")

    assert set(proof["remaining_certification_blockers"]) == {
        "downstream_consumer_runtime_proof_missing",
        "platform_mesh_event_publication_proof_missing",
        "gateway_workbench_proof_missing",
        "supported_feature_promotion_missing",
    }
    assert "idea_supported_feature_promotion_missing" in contract[
        "platform_blockers_retained"
    ]
    assert "idea_data_product_certification_missing" in contract[
        "platform_blockers_retained"
    ]
    assert any(
        "does not certify platform mesh event publication" in boundary
        for boundary in contract["non_proof_boundaries"]
    )


def test_consumer_runtime_proof_may_clear_only_downstream_consumer_dependency() -> None:
    contract = _load_json(CONTRACT_PATH)
    proof = _proof_by_name(contract, "outbox_consumer_runtime_execution")

    assert (
        proof["schema_version"]
        == "lotus-idea.outbox-consumer-runtime-execution.v1"
    )
    assert proof["evidence_class"] == "runtime_execution"
    assert proof["runtime_mode"] == "local_asgi_testclient_aggregate"
    assert proof["clears_only"] == ["downstream_consumer_runtime_proof_missing"]
    assert set(proof["domain_consumers"]) == {
        "lotus-advise",
        "lotus-manage",
        "lotus-report",
    }
    assert "idea_downstream_consumer_runtime_proof_dependency_consumable" in contract[
        "platform_blockers_cleared"
    ]


def test_consumer_runtime_proof_retains_platform_gateway_and_promotion_boundaries() -> None:
    contract = _load_json(CONTRACT_PATH)
    proof = _proof_by_name(contract, "outbox_consumer_runtime_execution")

    assert set(proof["remaining_certification_blockers"]) == {
        "platform_mesh_event_publication_proof_missing",
        "gateway_workbench_proof_missing",
        "supported_feature_promotion_missing",
    }
    assert set(proof["must_remain_false"]) == {
        "gatewayWorkbenchProofPresent",
        "platformMeshEventCertified",
        "supportedFeaturePromoted",
        "productionCertificationGranted",
        "certificationClosed",
    }
    assert "idea_gateway_workbench_live_journey_proof_missing" in contract[
        "platform_blockers_retained"
    ]
    assert any(
        "Downstream consumer runtime execution proof does not certify Gateway or Workbench"
        in boundary
        for boundary in contract["non_proof_boundaries"]
    )


def test_cost_attribution_proof_clears_only_consumable_contract_boundary() -> None:
    contract = _load_json(CONTRACT_PATH)
    proof = _operational_proof_by_name(
        contract,
        "service_cost_attribution_contract_and_qualification",
    )

    assert proof["schema_version"] == "lotus-platform.service-cost-attribution.v1"
    assert (
        proof["qualification_schema_version"]
        == "lotus-platform.service-cost-attribution-qualification.v1"
    )
    assert proof["evidence_status"] == "contract_available_protected_execution_pending"
    assert proof["clears_only"] == ["cost_attribution_contract_consumable"]
    assert "idea_cost_attribution_contract_consumable" in contract[
        "platform_blockers_cleared"
    ]
    assert set(proof["remaining_certification_blockers"]) == {
        "protected_finops_runner_missing",
        "protected_cost_attribution_execution_missing",
        "attested_cost_artifact_verification_missing",
        "lotus_idea_consumer_certification_missing",
        "production_cost_attribution_missing",
    }
    assert "idea_protected_finops_execution_missing" in contract[
        "platform_blockers_retained"
    ]
    assert "idea_attested_cost_artifact_verification_missing" in contract[
        "platform_blockers_retained"
    ]


def test_deployment_promotion_proof_clears_only_pending_manifest_boundary() -> None:
    contract = _load_json(CONTRACT_PATH)
    proof = _operational_proof_by_name(
        contract,
        "deployment_promotion_readiness_manifest",
    )

    assert proof["schema_version"] == "lotus.deployment-promotion-manifest.v1"
    assert proof["evidence_status"] == "deployment_pending"
    assert proof["release_repository"] == "lotus-idea"
    assert proof["clears_only"] == ["deployment_promotion_manifest_consumable"]
    assert "idea_deployment_promotion_manifest_consumable" in contract[
        "platform_blockers_cleared"
    ]
    assert set(proof["remaining_certification_blockers"]) == {
        "staging_deployed_digest_observation_missing",
        "production_deployed_digest_observation_missing",
        "same_digest_promotion_evidence_missing",
        "protected_migration_execution_missing",
        "supported_feature_promotion_missing",
    }
    assert "idea_production_deployed_digest_observation_missing" in contract[
        "platform_blockers_retained"
    ]
    assert "idea_protected_migration_execution_missing" in contract[
        "platform_blockers_retained"
    ]


def test_validator_rejects_supported_feature_overclaim() -> None:
    contract = copy.deepcopy(_load_json(CONTRACT_PATH))
    contract["platform_blockers_cleared"].append(
        "idea_supported_feature_promotion_missing"
    )

    errors = _validate(contract)

    assert any("platform_blockers_cleared overclaims" in error for error in errors)


def test_validator_rejects_production_cost_attribution_overclaim() -> None:
    contract = copy.deepcopy(_load_json(CONTRACT_PATH))
    proof = _operational_proof_by_name(
        contract,
        "service_cost_attribution_contract_and_qualification",
    )
    proof["remaining_certification_blockers"].remove(
        "production_cost_attribution_missing"
    )

    errors = _validate(contract)

    assert any(
        "cost-attribution remaining_certification_blockers" in error
        for error in errors
    )


def test_validator_rejects_deployment_certification_overclaim() -> None:
    contract = copy.deepcopy(_load_json(CONTRACT_PATH))
    proof = _operational_proof_by_name(
        contract,
        "deployment_promotion_readiness_manifest",
    )
    proof["evidence_status"] = "same_digest_proven"

    errors = _validate(contract)

    assert any("evidence_status must be deployment_pending" in error for error in errors)


def test_validator_rejects_data_mesh_certification_overclaim() -> None:
    contract = copy.deepcopy(_load_json(CONTRACT_PATH))
    contract["platform_posture"] = "certified"

    errors = _validate(contract)

    assert any("platform_posture must keep IdeaCandidate not certified" in error for error in errors)


def test_validator_rejects_missing_remaining_blocker() -> None:
    contract = copy.deepcopy(_load_json(CONTRACT_PATH))
    proof = _proof_by_name(contract, "outbox_broker_runtime_execution")
    proof["remaining_certification_blockers"].remove(
        "platform_mesh_event_publication_proof_missing"
    )

    errors = _validate(contract)

    assert any("remaining_certification_blockers" in error for error in errors)


def test_validator_rejects_unknown_proof_class() -> None:
    contract = copy.deepcopy(_load_json(CONTRACT_PATH))
    proof = _proof_by_name(contract, "outbox_broker_runtime_execution")
    proof["schema_version"] = (
        "lotus-idea.outbox-broker-source-contract.v1"
    )

    errors = _validate(contract)

    assert any("schema_version must be lotus-idea.outbox-broker-runtime-execution.v1" in error for error in errors)


def test_validator_rejects_missing_consumer_runtime_proof() -> None:
    contract = copy.deepcopy(_load_json(CONTRACT_PATH))
    contract["accepted_runtime_proofs"] = [
        _proof_by_name(contract, "outbox_broker_runtime_execution")
    ]

    errors = _validate(contract)

    assert any("exactly two bounded proofs" in error for error in errors)


def test_validator_rejects_consumer_runtime_overclaim() -> None:
    contract = copy.deepcopy(_load_json(CONTRACT_PATH))
    proof = _proof_by_name(contract, "outbox_consumer_runtime_execution")
    proof["clears_only"] = ["gateway_workbench_proof_missing"]

    errors = _validate(contract)

    assert any(
        "consumer runtime proof may clear only downstream_consumer_runtime_proof_missing"
        in error
        for error in errors
    )
