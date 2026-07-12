from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "automation" / "validate_lifecycle_authority_contracts.py"
CONTRACT_DIR = ROOT / "platform-contracts" / "lifecycle-authority"


def _validator():
    spec = importlib.util.spec_from_file_location(
        "lifecycle_authority_validator", VALIDATOR_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load(name: str) -> dict:
    return json.loads((CONTRACT_DIR / "examples" / name).read_text(encoding="utf-8"))


def test_contract_family_accepts_governed_examples_and_fail_closed_posture() -> None:
    assert _validator().validate_lifecycle_authority_contracts() == []


def test_decision_rejects_wrong_authority_domain_and_invalid_validity_window() -> None:
    validator = _validator()
    decision = _load("lifecycle-authority-decision.valid.json")
    decision["claims"]["authority_domain"] = "legal_and_records"
    decision["claims"]["expires_at_utc"] = decision["claims"]["effective_at_utc"]

    errors = validator.validate_decision(decision)

    assert "claims.authority_domain must equal privacy for purge" in errors
    assert (
        "decision validity window must satisfy issued <= effective < expires" in errors
    )


def test_decision_rejects_sensitive_evidence_and_weak_replay_nonce() -> None:
    validator = _validator()
    decision = _load("lifecycle-authority-decision.valid.json")
    decision["claims"]["replay_nonce"] = "predictable"
    decision["legal_narrative"] = "must never cross the contract boundary"

    errors = validator.validate_decision(decision)

    assert "decision.legal_narrative is a forbidden sensitive field" in errors
    assert "claims.replay_nonce must be a lowercase SHA-256 digest" in errors


def test_published_schema_rejects_invalid_audience_and_public_key(
    tmp_path: Path,
) -> None:
    validator = _validator()
    decision = _load("lifecycle-authority-decision.valid.json")
    decision["claims"]["audience"] = "not a lotus service"
    decision_path = tmp_path / "decision.json"
    decision_path.write_text(json.dumps(decision), encoding="utf-8")
    keys = _load("lifecycle-authority-key-discovery.valid.json")
    keys["keys"][0]["public_key_base64url"] = "padded=value"
    key_path = tmp_path / "keys.json"
    key_path.write_text(json.dumps(keys), encoding="utf-8")

    errors = validator.validate_example_against_schema(
        schema_path=validator.DECISION_SCHEMA_PATH, example_path=decision_path
    )
    errors.extend(
        validator.validate_example_against_schema(
            schema_path=validator.KEY_SCHEMA_PATH, example_path=key_path
        )
    )

    assert any("audience" in error and "does not match" in error for error in errors)
    assert any(
        "public_key_base64url" in error and "does not match" in error
        for error in errors
    )


def test_key_discovery_rejects_unbounded_revocation_and_duplicate_rotation() -> None:
    validator = _validator()
    discovery = _load("lifecycle-authority-key-discovery.valid.json")
    discovery["keys"][0]["status"] = "revoked"
    discovery["keys"].append(dict(discovery["keys"][0]))

    errors = validator.validate_key_discovery(discovery)

    assert "keys[0] revoked key must have not_after_utc" in errors
    assert "keys[1] duplicates key identity and rotation epoch" in errors


def test_certification_rejects_evidence_free_promotion() -> None:
    validator = _validator()
    certification = json.loads(
        (CONTRACT_DIR / "producer-certification.v1.json").read_text(encoding="utf-8")
    )
    certification["certification_status"] = "certified"
    certification["supported_feature_promoted"] = True

    errors = validator.validate_certification(certification)

    assert (
        "producer must remain not_certified until live evidence is supplied" in errors
    )
    assert (
        "supported_feature_promoted must remain false before production certification"
        in errors
    )


def test_certification_rejects_deleted_required_control() -> None:
    validator = _validator()
    certification = json.loads(
        (CONTRACT_DIR / "producer-certification.v1.json").read_text(encoding="utf-8")
    )
    del certification["required_controls"]["https_key_discovery_without_redirects"]

    errors = validator.validate_certification(certification)

    assert "required_controls must contain exactly the governed control names" in errors
