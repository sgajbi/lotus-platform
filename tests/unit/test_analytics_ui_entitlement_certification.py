from __future__ import annotations

import copy
import json
from pathlib import Path

from automation.validate_analytics_ui_entitlement_certification import (
    validate_entitlement_certification,
)

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_DIR = ROOT / "context" / "contracts"
OBSERVABILITY_CONTRACT_PATH = CONTRACT_DIR / "analytics-ui-observability-contract.json"
CERTIFICATION_PATH = (
    CONTRACT_DIR / "analytics-ui-observability-entitlement-certification.json"
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(observability: dict, certification: dict) -> list[str]:
    return validate_entitlement_certification(
        observability_contract=observability,
        certification=certification,
    )


def test_entitlement_certification_artifacts_are_indexed_and_governed() -> None:
    readme = (CONTRACT_DIR / "README.md").read_text(encoding="utf-8")
    schema = _load_json(
        CONTRACT_DIR / "analytics-ui-observability-entitlement-certification.schema.json"
    )
    certification = _load_json(CERTIFICATION_PATH)

    assert "analytics-ui-observability-entitlement-certification.schema.json" in readme
    assert "analytics-ui-observability-entitlement-certification.json" in readme
    assert (
        schema["properties"]["contract_id"]["const"]
        == "analytics-ui-observability-entitlement-certification"
    )
    assert certification["lifecycle_status"] == "slice-19-entitlement-certification-governance"


def test_entitlement_certification_validator_accepts_baseline() -> None:
    assert _validate(_load_json(OBSERVABILITY_CONTRACT_PATH), _load_json(CERTIFICATION_PATH)) == []


def test_entitlement_certification_rejects_missing_denied_audit_event() -> None:
    observability = copy.deepcopy(_load_json(OBSERVABILITY_CONTRACT_PATH))
    certification = _load_json(CERTIFICATION_PATH)
    telemetry = observability["telemetry_contract"]
    telemetry["gateway_log_events"] = [
        event
        for event in telemetry["gateway_log_events"]
        if event["event_name"] != "gateway.analytics.audit.analytics_read_denied"
    ]

    errors = _validate(observability, certification)

    assert any("required audit events are not implemented" in error for error in errors)


def test_entitlement_certification_rejects_raw_entitlement_leakage_gap() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    certification = copy.deepcopy(_load_json(CERTIFICATION_PATH))
    certification["forbidden_evidence_fields"].remove("raw_entitlement_failure")

    errors = _validate(observability, certification)

    assert any("forbidden_evidence_fields missing" in error for error in errors)


def test_entitlement_certification_rejects_promoted_path_before_live_proof() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    certification = copy.deepcopy(_load_json(CERTIFICATION_PATH))
    certification["certified_read_paths"][0]["status"] = "implemented"

    errors = _validate(observability, certification)

    assert any("status must remain implementation_pending" in error for error in errors)


def test_entitlement_certification_rejects_missing_permission_blocked_evidence() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    certification = copy.deepcopy(_load_json(CERTIFICATION_PATH))
    certification["required_evidence"] = [
        item
        for item in certification["required_evidence"]
        if item["evidence_type"] != "workbench-permission-blocked-panel-proof"
    ]

    errors = _validate(observability, certification)

    assert any("required_evidence missing" in error for error in errors)


def test_entitlement_certification_rejects_missing_gateway_pr_evidence() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    certification = copy.deepcopy(_load_json(CERTIFICATION_PATH))
    certification["implementation_evidence"] = [
        item
        for item in certification["implementation_evidence"]
        if item["pull_request"] != "sgajbi/lotus-gateway#177"
    ]

    errors = _validate(observability, certification)

    assert any("implementation_evidence missing required proof references" in error for error in errors)


def test_entitlement_certification_rejects_unknown_evidence_path() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    certification = copy.deepcopy(_load_json(CERTIFICATION_PATH))
    certification["implementation_evidence"][0]["path_id"] = "unknown-path"

    errors = _validate(observability, certification)

    assert any("path_id must reference a certified_read_paths entry" in error for error in errors)
