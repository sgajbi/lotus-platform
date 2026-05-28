from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from automation.validate_supported_claim_register import (
    validate_supported_claim_register,
)


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_PATH = (
    ROOT
    / "platform-contracts"
    / "supported-claims"
    / "examples"
    / "rfc0028-advisory-bank-demo-supported-claims.valid.json"
)
README_PATH = ROOT / "platform-contracts" / "supported-claims" / "README.md"
SCHEMA_PATH = (
    ROOT
    / "platform-contracts"
    / "supported-claims"
    / "supported-claim-register.schema.json"
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_supported_claim_register_example_is_valid_and_rfc0028_ready() -> None:
    payload = _load(EXAMPLE_PATH)

    assert validate_supported_claim_register(EXAMPLE_PATH, payload) == []
    assert payload["scenario_id"] == "RFC28_BANK_DEMO_CLIENT_READY_PROOF_CANONICAL"
    assert payload["primary_portfolio_id"] == "PB_SG_GLOBAL_BAL_001"
    assert payload["proof_marker"] == "BANK_DEMO_PROOF_PACK_CREATED"
    assert payload["front_office_validation"]["requires_gateway_backing"] is True
    assert payload["front_office_validation"]["requires_browser_validation"] is True


def test_supported_claim_register_rejects_client_facing_unproved_claims() -> None:
    payload = _load(EXAMPLE_PATH)
    payload["claims"][1]["allowed_materials"] = ["DEMO_SCRIPT", "SCREENSHOT"]

    issues = validate_supported_claim_register(EXAMPLE_PATH, payload)

    assert any(
        "planned/unsupported claims cannot use client-facing materials" in item
        for item in issues
    )


def test_supported_claim_register_rejects_backend_only_screenshots_and_missing_proof() -> (
    None
):
    payload = _load(EXAMPLE_PATH)
    payload["claims"][0]["allowed_materials"] = ["SCREENSHOT"]
    payload["claims"][0]["classification"] = "IMPLEMENTATION_BACKED"
    payload["claims"][0]["evidence_refs"] = []
    payload["claims"][0]["proof_requirements"] = []

    issues = validate_supported_claim_register(EXAMPLE_PATH, payload)

    assert any(
        "implementation-backed claims require evidence and proof" in item
        for item in issues
    )

    backend_only = deepcopy(_load(EXAMPLE_PATH))
    backend_only["claims"][0]["allowed_materials"] = ["SCREENSHOT"]
    issues = validate_supported_claim_register(EXAMPLE_PATH, backend_only)

    assert any(
        "backend-only claims cannot be used for screenshots" in item for item in issues
    )


def test_supported_claim_register_contract_is_documented() -> None:
    readme = README_PATH.read_text(encoding="utf-8")
    schema = _load(SCHEMA_PATH)

    assert "Supported claim registers prevent demo" in readme
    assert "validate_supported_claim_register.py" in readme
    assert schema["title"] == "Lotus Supported Claim Register"
    assert (
        "IMPLEMENTATION_BACKED"
        in schema["properties"]["claim_taxonomy"]["items"]["enum"]
    )
