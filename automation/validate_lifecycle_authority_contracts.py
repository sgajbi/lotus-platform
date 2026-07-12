from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = ROOT / "platform-contracts" / "lifecycle-authority"
EXAMPLES_DIR = CONTRACT_DIR / "examples"
CERTIFICATION_PATH = CONTRACT_DIR / "producer-certification.v1.json"
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


def validate_decision(decision: dict[str, Any]) -> list[str]:
    errors = _find_forbidden(decision, "decision")
    claims = decision.get("claims")
    signature = decision.get("signature")
    if not isinstance(claims, dict) or not isinstance(signature, dict):
        return errors + ["decision claims and signature must be objects"]
    expected_claims = {
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
    if set(claims) != expected_claims:
        errors.append("decision claims must contain exactly the governed fields")
    constants = {
        "schema_version": "lotus.lifecycle-authority-decision.v1",
        "issuer": "bank-lifecycle-governance",
        "decision_status": "approved",
    }
    for field, expected in constants.items():
        if claims.get(field) != expected:
            errors.append(f"claims.{field} must equal {expected}")
    for field in (
        "decision_id",
        "tenant_id",
        "candidate_id",
        "authority_ref",
        "change_reference",
    ):
        if not isinstance(claims.get(field), str) or not REFERENCE.fullmatch(
            claims[field]
        ):
            errors.append(f"claims.{field} must be a source-safe reference")
    if not isinstance(claims.get("replay_nonce"), str) or not SHA256.fullmatch(
        claims["replay_nonce"]
    ):
        errors.append("claims.replay_nonce must be a lowercase SHA-256 digest")
    action = claims.get("action")
    if action not in EXPECTED_DOMAINS:
        errors.append("claims.action must be governed")
    elif claims.get("authority_domain") != EXPECTED_DOMAINS[action]:
        errors.append(
            f"claims.authority_domain must equal {EXPECTED_DOMAINS[action]} for {action}"
        )
    timestamps = [
        _utc(claims.get(name))
        for name in ("issued_at_utc", "effective_at_utc", "expires_at_utc")
    ]
    if any(value is None for value in timestamps):
        errors.append("decision timestamps must be RFC-3339 UTC values ending with Z")
    elif not timestamps[0] <= timestamps[1] < timestamps[2]:
        errors.append(
            "decision validity window must satisfy issued <= effective < expires"
        )
    if (
        decision.get("key_discovery_path")
        != "/.well-known/lotus-lifecycle-authority-keys"
    ):
        errors.append("key_discovery_path must be governed")
    if set(signature) != {
        "algorithm",
        "key_id",
        "rotation_epoch",
        "signature_base64url",
    }:
        errors.append("signature must contain exactly the governed fields")
    if signature.get("algorithm") != "EdDSA":
        errors.append("signature.algorithm must equal EdDSA")
    if (
        not isinstance(signature.get("rotation_epoch"), int)
        or signature["rotation_epoch"] < 1
    ):
        errors.append("signature.rotation_epoch must be positive")
    if not isinstance(
        signature.get("signature_base64url"), str
    ) or not BASE64URL.fullmatch(signature["signature_base64url"]):
        errors.append("signature.signature_base64url must be unpadded base64url")
    return errors


def validate_key_discovery(document: dict[str, Any]) -> list[str]:
    errors = _find_forbidden(document, "key_discovery")
    if document.get("schema_version") != "lotus.lifecycle-authority-keys.v1":
        errors.append("key discovery schema_version must be governed")
    if document.get("issuer") != "bank-lifecycle-governance":
        errors.append("key discovery issuer must be governed")
    keys = document.get("keys")
    if not isinstance(keys, list) or not keys:
        return errors + ["key discovery keys must be a non-empty list"]
    identities: set[tuple[object, object]] = set()
    for index, key in enumerate(keys):
        if not isinstance(key, dict):
            errors.append(f"keys[{index}] must be an object")
            continue
        identity = (key.get("key_id"), key.get("rotation_epoch"))
        if identity in identities:
            errors.append(f"keys[{index}] duplicates key identity and rotation epoch")
        identities.add(identity)
        if key.get("algorithm") != "EdDSA" or key.get("curve") != "Ed25519":
            errors.append(f"keys[{index}] must use EdDSA with Ed25519")
        if key.get("status") not in {"active", "rotated", "revoked"}:
            errors.append(f"keys[{index}].status must be governed")
        if key.get("status") == "revoked" and key.get("not_after_utc") is None:
            errors.append(f"keys[{index}] revoked key must have not_after_utc")
        start, end = (
            _utc(key.get("not_before_utc")),
            _utc(key.get("not_after_utc")) if key.get("not_after_utc") else None,
        )
        if start is None or (key.get("not_after_utc") is not None and end is None):
            errors.append(f"keys[{index}] validity timestamps must be RFC-3339 UTC")
        elif end is not None and start >= end:
            errors.append(f"keys[{index}] validity window must increase")
    return errors


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
    if (
        not isinstance(controls, dict)
        or not controls
        or any(value is not False for value in controls.values())
    ):
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
    errors = validate_decision(
        _load(EXAMPLES_DIR / "lifecycle-authority-decision.valid.json")
    )
    errors.extend(
        validate_key_discovery(
            _load(EXAMPLES_DIR / "lifecycle-authority-key-discovery.valid.json")
        )
    )
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
