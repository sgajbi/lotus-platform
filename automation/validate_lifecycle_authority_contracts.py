from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from automation.json_contract_validation import validate_json_schema_subset
except ModuleNotFoundError:
    from json_contract_validation import validate_json_schema_subset


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = ROOT / "platform-contracts" / "lifecycle-authority"
EXAMPLES_DIR = CONTRACT_DIR / "examples"
CERTIFICATION_PATH = CONTRACT_DIR / "producer-certification.v1.json"
DECISION_SCHEMA_PATH = CONTRACT_DIR / "lifecycle-authority-decision.schema.json"
KEY_SCHEMA_PATH = CONTRACT_DIR / "lifecycle-authority-key-discovery.schema.json"
REFERENCE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{2,255}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
BASE64URL = re.compile(r"^[A-Za-z0-9_-]+$")
FORBIDDEN_FIELDS = {
    "client_id",
    "portfolio_id",
    "legal_narrative",
    "raw_document",
    "prompt",
    "model_output",
}
EXPECTED_DOMAINS = {
    "apply_hold": "legal_and_records",
    "release_hold": "legal_and_records",
    "erase": "privacy",
    "purge": "privacy",
}
REQUIRED_CERTIFICATION_CONTROLS = {
    "bank_legal_and_records_approval",
    "bank_privacy_approval",
    "managed_key_generation_storage_and_rotation",
    "revocation_and_rotated_key_overlap_proof",
    "https_key_discovery_without_redirects",
    "decision_signature_interoperability_proof",
    "consumer_replay_and_restart_proof",
    "production_observability_and_runbook_proof",
    "mainline_ci_evidence",
}
EXPECTED_DECISION_CLAIMS = {
    "schema_version",
    "issuer",
    "audience",
    "decision_id",
    "replay_nonce",
    "tenant_id",
    "candidate_id",
    "action",
    "authority_domain",
    "authority_ref",
    "change_reference",
    "decision_status",
    "issued_at_utc",
    "effective_at_utc",
    "expires_at_utc",
}
DECISION_CONSTANT_CLAIMS = {
    "schema_version": "lotus.lifecycle-authority-decision.v1",
    "issuer": "bank-lifecycle-governance",
    "decision_status": "approved",
}
DECISION_REFERENCE_CLAIMS = (
    "decision_id",
    "tenant_id",
    "candidate_id",
    "authority_ref",
    "change_reference",
)
SIGNATURE_FIELDS = {
    "algorithm",
    "key_id",
    "rotation_epoch",
    "signature_base64url",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _utc(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        return datetime.fromisoformat(f"{value[:-1]}+00:00")
    except ValueError:
        return None


def _find_forbidden(value: object, path: str = "payload") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in FORBIDDEN_FIELDS:
                errors.append(f"{path}.{key} is a forbidden sensitive field")
            errors.extend(_find_forbidden(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_find_forbidden(child, f"{path}[{index}]"))
    return errors


def validate_example_against_schema(
    *, schema_path: Path, example_path: Path
) -> list[str]:
    return validate_json_schema_subset(schema_path, example_path)


def validate_decision(decision: dict[str, Any]) -> list[str]:
    errors = _find_forbidden(decision, "decision")
    claims = decision.get("claims")
    signature = decision.get("signature")
    if not isinstance(claims, dict) or not isinstance(signature, dict):
        return errors + ["decision claims and signature must be objects"]
    _validate_decision_claims(errors, claims)
    _validate_key_discovery_path(errors, decision)
    _validate_signature(errors, signature)
    return errors


def _validate_decision_claims(errors: list[str], claims: dict[str, Any]) -> None:
    if set(claims) != EXPECTED_DECISION_CLAIMS:
        errors.append("decision claims must contain exactly the governed fields")
    _validate_decision_claim_constants(errors, claims)
    _validate_decision_claim_references(errors, claims)
    _validate_replay_nonce(errors, claims)
    _validate_action_domain(errors, claims)
    _validate_decision_window(errors, claims)


def _validate_decision_claim_constants(
    errors: list[str], claims: dict[str, Any]
) -> None:
    for field, expected in DECISION_CONSTANT_CLAIMS.items():
        if claims.get(field) != expected:
            errors.append(f"claims.{field} must equal {expected}")


def _validate_decision_claim_references(
    errors: list[str], claims: dict[str, Any]
) -> None:
    for field in DECISION_REFERENCE_CLAIMS:
        value = claims.get(field)
        if not isinstance(value, str) or not REFERENCE.fullmatch(value):
            errors.append(f"claims.{field} must be a source-safe reference")


def _validate_replay_nonce(errors: list[str], claims: dict[str, Any]) -> None:
    value = claims.get("replay_nonce")
    if not isinstance(value, str) or not SHA256.fullmatch(value):
        errors.append("claims.replay_nonce must be a lowercase SHA-256 digest")


def _validate_action_domain(errors: list[str], claims: dict[str, Any]) -> None:
    action = claims.get("action")
    if action not in EXPECTED_DOMAINS:
        errors.append("claims.action must be governed")
        return
    if claims.get("authority_domain") != EXPECTED_DOMAINS[action]:
        errors.append(
            f"claims.authority_domain must equal {EXPECTED_DOMAINS[action]} for {action}"
        )


def _validate_decision_window(errors: list[str], claims: dict[str, Any]) -> None:
    timestamps = [
        _utc(claims.get(name))
        for name in ("issued_at_utc", "effective_at_utc", "expires_at_utc")
    ]
    if any(value is None for value in timestamps):
        errors.append("decision timestamps must be RFC-3339 UTC values ending with Z")
        return
    issued, effective, expires = timestamps
    if issued is None or effective is None or expires is None:
        errors.append("decision timestamps must be RFC-3339 UTC values ending with Z")
    elif not issued <= effective < expires:
        errors.append(
            "decision validity window must satisfy issued <= effective < expires"
        )


def _validate_key_discovery_path(
    errors: list[str], decision: dict[str, Any]
) -> None:
    if (
        decision.get("key_discovery_path")
        != "/.well-known/lotus-lifecycle-authority-keys"
    ):
        errors.append("key_discovery_path must be governed")


def _validate_signature(errors: list[str], signature: dict[str, Any]) -> None:
    if set(signature) != SIGNATURE_FIELDS:
        errors.append("signature must contain exactly the governed fields")
    if signature.get("algorithm") != "EdDSA":
        errors.append("signature.algorithm must equal EdDSA")
    rotation_epoch = signature.get("rotation_epoch")
    if not isinstance(rotation_epoch, int) or rotation_epoch < 1:
        errors.append("signature.rotation_epoch must be positive")
    signature_value = signature.get("signature_base64url")
    if not isinstance(signature_value, str) or not BASE64URL.fullmatch(signature_value):
        errors.append("signature.signature_base64url must be unpadded base64url")


def validate_key_discovery(document: dict[str, Any]) -> list[str]:
    errors = _find_forbidden(document, "key_discovery")
    _validate_key_discovery_header(errors, document)
    keys = document.get("keys")
    if not isinstance(keys, list) or not keys:
        return errors + ["key discovery keys must be a non-empty list"]
    identities: set[tuple[object, object]] = set()
    for index, key in enumerate(keys):
        _validate_key_entry(errors, index, key, identities)
    return errors


def _validate_key_discovery_header(
    errors: list[str], document: dict[str, Any]
) -> None:
    if document.get("schema_version") != "lotus.lifecycle-authority-keys.v1":
        errors.append("key discovery schema_version must be governed")
    if document.get("issuer") != "bank-lifecycle-governance":
        errors.append("key discovery issuer must be governed")


def _validate_key_entry(
    errors: list[str],
    index: int,
    key: object,
    identities: set[tuple[object, object]],
) -> None:
    if not isinstance(key, dict):
        errors.append(f"keys[{index}] must be an object")
        return
    _validate_key_identity(errors, index, key, identities)
    _validate_key_algorithm_and_status(errors, index, key)
    _validate_key_validity_window(errors, index, key)


def _validate_key_identity(
    errors: list[str],
    index: int,
    key: dict[str, Any],
    identities: set[tuple[object, object]],
) -> None:
    identity = (key.get("key_id"), key.get("rotation_epoch"))
    if identity in identities:
        errors.append(f"keys[{index}] duplicates key identity and rotation epoch")
    identities.add(identity)


def _validate_key_algorithm_and_status(
    errors: list[str], index: int, key: dict[str, Any]
) -> None:
    if key.get("algorithm") != "EdDSA" or key.get("curve") != "Ed25519":
        errors.append(f"keys[{index}] must use EdDSA with Ed25519")
    if key.get("status") not in {"active", "rotated", "revoked"}:
        errors.append(f"keys[{index}].status must be governed")
    if key.get("status") == "revoked" and key.get("not_after_utc") is None:
        errors.append(f"keys[{index}] revoked key must have not_after_utc")


def _validate_key_validity_window(
    errors: list[str], index: int, key: dict[str, Any]
) -> None:
    start = _utc(key.get("not_before_utc"))
    end = _utc(key.get("not_after_utc")) if key.get("not_after_utc") else None
    if start is None or (key.get("not_after_utc") is not None and end is None):
        errors.append(f"keys[{index}] validity timestamps must be RFC-3339 UTC")
    elif end is not None and start >= end:
        errors.append(f"keys[{index}] validity window must increase")


def validate_certification(certification: dict[str, Any]) -> list[str]:
    errors = _find_forbidden(certification, "certification")
    if certification.get("certification_status") != "not_certified":
        errors.append(
            "producer must remain not_certified until live evidence is supplied"
        )
    for field in ("supported_feature_promoted", "production_authority_verified"):
        if certification.get(field) is not False:
            errors.append(f"{field} must remain false before production certification")
    controls = certification.get("required_controls")
    if not isinstance(controls, dict):
        errors.append("required_controls must be an object")
    elif set(controls) != REQUIRED_CERTIFICATION_CONTROLS:
        errors.append(
            "required_controls must contain exactly the governed control names"
        )
    elif any(value is not False for value in controls.values()):
        errors.append(
            "all producer certification controls must remain explicitly false"
        )
    boundary = certification.get("authority_boundary", {})
    if any(
        boundary.get(field) is not False
        for field in (
            "platform_may_issue_substantive_decisions",
            "consumer_may_self_authorize_decisions",
            "fixtures_are_production_authority_evidence",
        )
    ):
        errors.append(
            "authority boundary must deny platform, consumer, and fixture authority"
        )
    return errors


def validate_lifecycle_authority_contracts() -> list[str]:
    decision_example = EXAMPLES_DIR / "lifecycle-authority-decision.valid.json"
    key_example = EXAMPLES_DIR / "lifecycle-authority-key-discovery.valid.json"
    errors = validate_example_against_schema(
        schema_path=DECISION_SCHEMA_PATH, example_path=decision_example
    )
    errors.extend(
        validate_example_against_schema(
            schema_path=KEY_SCHEMA_PATH, example_path=key_example
        )
    )
    errors.extend(validate_decision(_load(decision_example)))
    errors.extend(validate_key_discovery(_load(key_example)))
    errors.extend(validate_certification(_load(CERTIFICATION_PATH)))
    return errors


def main() -> int:
    errors = validate_lifecycle_authority_contracts()
    if errors:
        print("Lifecycle authority contract validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Lifecycle authority contracts validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
