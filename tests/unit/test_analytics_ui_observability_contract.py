from __future__ import annotations

import copy
import json
from pathlib import Path

from automation.validate_analytics_ui_observability_contract import validate_contract


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "context" / "contracts" / "analytics-ui-observability-contract.json"


def _load_contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_analytics_ui_observability_contract_artifacts_are_present_and_governed() -> None:
    readme = (ROOT / "context" / "contracts" / "README.md").read_text(encoding="utf-8")
    schema = json.loads(
        (ROOT / "context" / "contracts" / "analytics-ui-observability-contract.schema.json")
        .read_text(encoding="utf-8")
    )
    contract = _load_contract()

    assert "analytics-ui-observability-contract.schema.json" in readme
    assert "analytics-ui-observability-contract.json" in readme
    assert schema["properties"]["contract_id"]["const"] == "analytics-ui-observability-contract"
    assert schema["properties"]["governed_by_rfc"]["const"] == "RFC-0108"
    assert contract["contract_id"] == "analytics-ui-observability-contract"
    assert contract["governed_by_rfc"] == "RFC-0108"
    assert contract["lifecycle_status"] == "slice-0-implemented"


def test_analytics_ui_observability_contract_limits_promotion_to_slice0_scaffold() -> None:
    contract = _load_contract()

    assert contract["dashboards"] == []
    assert contract["alerts"] == []
    assert {entry["implemented"] for entry in contract["metric_families"]} == {False}
    feature_status = {
        entry["feature_key"]: entry["status"] for entry in contract["supported_feature_keys"]
    }
    assert feature_status["platform.scaffolding.analytics_ui_observability_baseline"] == "implemented"
    assert {
        status
        for key, status in feature_status.items()
        if key != "platform.scaffolding.analytics_ui_observability_baseline"
    } == {"planned"}


def test_analytics_ui_observability_contract_rejects_sensitive_labels() -> None:
    contract = _load_contract()
    allowed_labels = set(contract["allowed_labels"])
    forbidden_fields = set(contract["forbidden_fields"])

    assert "portfolio_id" in forbidden_fields
    assert "client_name" in forbidden_fields
    assert "holding_id" in forbidden_fields
    assert "trace_id" in forbidden_fields
    assert "correlation_id" in forbidden_fields
    assert allowed_labels.isdisjoint(forbidden_fields)

    for metric in contract["metric_families"]:
        labels = set(metric["labels"])
        assert labels <= allowed_labels
        assert labels.isdisjoint(forbidden_fields)


def test_analytics_ui_observability_contract_records_required_states_and_evidence() -> None:
    contract = _load_contract()

    assert set(contract["state_vocabulary"]) == {
        "loading",
        "ready",
        "empty",
        "partial",
        "stale",
        "degraded",
        "error",
        "permission_blocked",
        "unsupported",
    }
    assert set(contract["evidence_requirements"]["artifact_types"]) >= {
        "browser",
        "gateway-api",
        "backend-log-metric",
        "dashboard",
        "sensitive-data-assertion",
        "github-check",
    }
    assert "portfolio ids" in contract["evidence_requirements"]["forbidden_content_classes"]
    assert "screen content" in contract["evidence_requirements"]["forbidden_content_classes"]


def test_analytics_ui_observability_contract_validator_accepts_baseline() -> None:
    assert validate_contract(_load_contract()) == []


def test_analytics_ui_observability_contract_validator_rejects_forbidden_metric_label() -> None:
    contract = copy.deepcopy(_load_contract())
    contract["metric_families"][0]["labels"].append("portfolio_id")

    errors = validate_contract(contract)

    assert any("forbidden fields" in error for error in errors)


def test_analytics_ui_observability_contract_validator_rejects_premature_dashboard_claim() -> None:
    contract = copy.deepcopy(_load_contract())
    contract["dashboards"].append(
        {
            "dashboard_id": "analytics-ui-overview",
            "metric_names": ["lotus_workbench_panel_state_total"],
        }
    )

    errors = validate_contract(contract)

    assert "dashboards must remain empty until implemented metrics exist" in errors
