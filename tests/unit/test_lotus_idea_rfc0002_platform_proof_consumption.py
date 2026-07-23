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
    assert contract["platform_posture"] == "certification_candidate_not_certified"


def test_lotus_idea_rfc0002_platform_proof_contract_accepts_baseline() -> None:
    assert _validate(_load_json(CONTRACT_PATH)) == []


def test_broker_runtime_proof_may_clear_only_external_broker_dependency() -> None:
    contract = _load_json(CONTRACT_PATH)
    proof = contract["accepted_runtime_proofs"][0]

    assert proof["schema_version"] == "lotus-idea.outbox-broker-runtime-execution.v1"
    assert proof["evidence_class"] == "runtime_execution"
    assert proof["clears_only"] == ["external_broker_runtime_proof_missing"]
    assert contract["platform_blockers_cleared"] == [
        "idea_external_broker_runtime_proof_dependency_consumable"
    ]


def test_broker_runtime_proof_retains_product_and_publication_boundaries() -> None:
    contract = _load_json(CONTRACT_PATH)
    proof = contract["accepted_runtime_proofs"][0]

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


def test_validator_rejects_supported_feature_overclaim() -> None:
    contract = copy.deepcopy(_load_json(CONTRACT_PATH))
    contract["platform_blockers_cleared"].append(
        "idea_supported_feature_promotion_missing"
    )

    errors = _validate(contract)

    assert any("platform_blockers_cleared overclaims" in error for error in errors)


def test_validator_rejects_data_mesh_certification_overclaim() -> None:
    contract = copy.deepcopy(_load_json(CONTRACT_PATH))
    contract["platform_posture"] = "certified"

    errors = _validate(contract)

    assert any("platform_posture must keep IdeaCandidate not certified" in error for error in errors)


def test_validator_rejects_missing_remaining_blocker() -> None:
    contract = copy.deepcopy(_load_json(CONTRACT_PATH))
    proof = contract["accepted_runtime_proofs"][0]
    proof["remaining_certification_blockers"].remove(
        "platform_mesh_event_publication_proof_missing"
    )

    errors = _validate(contract)

    assert any("remaining_certification_blockers" in error for error in errors)


def test_validator_rejects_unknown_proof_class() -> None:
    contract = copy.deepcopy(_load_json(CONTRACT_PATH))
    contract["accepted_runtime_proofs"][0]["schema_version"] = (
        "lotus-idea.outbox-broker-source-contract.v1"
    )

    errors = _validate(contract)

    assert any("schema_version must be lotus-idea.outbox-broker-runtime-execution.v1" in error for error in errors)
