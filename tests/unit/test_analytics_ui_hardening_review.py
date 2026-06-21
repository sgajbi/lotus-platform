from __future__ import annotations

import copy
import json
from pathlib import Path

import yaml

from automation.validate_analytics_ui_hardening_review import validate_hardening_review


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_DIR = ROOT / "context" / "contracts"
OBSERVABILITY_CONTRACT_PATH = CONTRACT_DIR / "analytics-ui-observability-contract.json"
ROLLOUT_CONTRACT_PATH = CONTRACT_DIR / "analytics-ui-observability-rollout-readiness.json"
HARDENING_REVIEW_PATH = CONTRACT_DIR / "analytics-ui-observability-hardening-review.json"
PANEL_REGISTRY_PATH = CONTRACT_DIR / "workbench-panel-registry.json"
DASHBOARD_PATH = (
    ROOT
    / "platform-stack"
    / "grafana"
    / "dashboards"
    / "analytics-ui-observability-overview.json"
)
ALERT_RULES_PATH = (
    ROOT
    / "platform-stack"
    / "prometheus"
    / "rules"
    / "analytics-ui-observability.rules.yml"
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_alert_rules() -> dict:
    return yaml.safe_load(ALERT_RULES_PATH.read_text(encoding="utf-8"))


def _validate(
    observability_contract: dict,
    rollout_contract: dict,
    hardening_review: dict,
) -> list[str]:
    return validate_hardening_review(
        observability_contract=observability_contract,
        rollout_contract=rollout_contract,
        hardening_review=hardening_review,
        panel_registry=_load_json(PANEL_REGISTRY_PATH),
        dashboard=_load_json(DASHBOARD_PATH),
        alert_rules=_load_alert_rules(),
    )


def test_analytics_ui_hardening_review_artifacts_are_present_and_governed() -> None:
    readme = (CONTRACT_DIR / "README.md").read_text(encoding="utf-8")
    schema = _load_json(
        CONTRACT_DIR / "analytics-ui-observability-hardening-review.schema.json"
    )
    review = _load_json(HARDENING_REVIEW_PATH)

    assert "analytics-ui-observability-hardening-review.schema.json" in readme
    assert "analytics-ui-observability-hardening-review.json" in readme
    assert (
        schema["properties"]["contract_id"]["const"]
        == "analytics-ui-observability-hardening-review"
    )
    assert schema["properties"]["governed_by_rfc"]["const"] == "RFC-0108"
    assert review["contract_id"] == "analytics-ui-observability-hardening-review"
    assert review["governed_by_rfc"] == "RFC-0108"
    assert review["lifecycle_status"] == "second-last-hardening-implemented"


def test_analytics_ui_hardening_review_validator_accepts_baseline() -> None:
    review = _load_json(HARDENING_REVIEW_PATH)

    assert "/proposals/{proposalId}" in review["panel_state_review"][
        "certified_route_groups_reviewed"
    ]
    assert "/recommendations?portfolioId={portfolio_id}&mode=copilot" in review[
        "panel_state_review"
    ]["certified_route_groups_reviewed"]
    assert (
        _validate(
            _load_json(OBSERVABILITY_CONTRACT_PATH),
            _load_json(ROLLOUT_CONTRACT_PATH),
            review,
        )
        == []
    )


def test_analytics_ui_hardening_review_rejects_unreviewed_event() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    rollout = _load_json(ROLLOUT_CONTRACT_PATH)
    review = copy.deepcopy(_load_json(HARDENING_REVIEW_PATH))
    review["telemetry_field_review"]["runtime_events_reviewed"].remove(
        "workbench.analytics.attention"
    )

    errors = _validate(observability, rollout, review)

    assert any("missing implemented events" in error for error in errors)


def test_analytics_ui_hardening_review_rejects_sensitive_metric_labels() -> None:
    observability = copy.deepcopy(_load_json(OBSERVABILITY_CONTRACT_PATH))
    rollout = _load_json(ROLLOUT_CONTRACT_PATH)
    review = _load_json(HARDENING_REVIEW_PATH)
    observability["metric_families"].append(
        {
            "metric_name": "lotus_test_sensitive_metric_total",
            "owner_repo": "lotus-platform",
            "implemented": True,
            "metric_type": "counter",
            "labels": ["route", "portfolio_id", "unregistered_label"],
            "purpose": "test-only metric",
        }
    )

    errors = _validate(observability, rollout, review)

    assert any("forbidden labels ['portfolio_id']" in error for error in errors)
    assert any(
        "unsupported labels ['portfolio_id', 'unregistered_label']" in error
        for error in errors
    )


def test_analytics_ui_hardening_review_rejects_sensitive_trace_attributes() -> None:
    observability = copy.deepcopy(_load_json(OBSERVABILITY_CONTRACT_PATH))
    rollout = _load_json(ROLLOUT_CONTRACT_PATH)
    review = _load_json(HARDENING_REVIEW_PATH)
    observability["telemetry_contract"]["trace_attributes"].append("trace_id")

    errors = _validate(observability, rollout, review)

    assert any(
        "trace_attributes: forbidden attributes ['trace_id']" in error
        for error in errors
    )
    assert any(
        "trace_attributes: unsupported attributes ['trace_id']" in error
        for error in errors
    )


def test_analytics_ui_hardening_review_rejects_unreviewed_panel_state() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    rollout = _load_json(ROLLOUT_CONTRACT_PATH)
    review = copy.deepcopy(_load_json(HARDENING_REVIEW_PATH))
    review["panel_state_review"]["non_telemetry_registry_states"] = []

    errors = _validate(observability, rollout, review)

    assert any("registry states are not reviewed" in error for error in errors)


def test_analytics_ui_hardening_review_rejects_unimplemented_dashboard_metric() -> None:
    observability = copy.deepcopy(_load_json(OBSERVABILITY_CONTRACT_PATH))
    rollout = _load_json(ROLLOUT_CONTRACT_PATH)
    review = _load_json(HARDENING_REVIEW_PATH)
    observability["metric_families"].append(
        {
            "metric_name": "lotus_fake_metric_total",
            "owner_repo": "lotus-platform",
            "implemented": False,
            "metric_type": "counter",
            "labels": ["route"],
            "purpose": "test-only metric",
        }
    )
    dashboard = _load_json(DASHBOARD_PATH)
    dashboard["panels"][0]["targets"][0]["expr"] = "sum(lotus_fake_metric_total)"

    errors = validate_hardening_review(
        observability_contract=observability,
        rollout_contract=rollout,
        hardening_review=review,
        panel_registry=_load_json(PANEL_REGISTRY_PATH),
        dashboard=dashboard,
        alert_rules=_load_alert_rules(),
    )

    assert any("dashboard references unimplemented metrics" in error for error in errors)


def test_analytics_ui_hardening_review_rejects_alert_rule_drift() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    rollout = _load_json(ROLLOUT_CONTRACT_PATH)
    review = _load_json(HARDENING_REVIEW_PATH)
    alert_rules = _load_alert_rules()
    rule = alert_rules["groups"][0]["rules"][0]
    rule["expr"] = "sum(lotus_unimplemented_alert_metric_total) > 0"
    rule["labels"]["alert_id"] = "analytics-ui-test-alert-drift"
    rule["annotations"].pop("runbook")

    errors = validate_hardening_review(
        observability_contract=observability,
        rollout_contract=rollout,
        hardening_review=review,
        panel_registry=_load_json(PANEL_REGISTRY_PATH),
        dashboard=_load_json(DASHBOARD_PATH),
        alert_rules=alert_rules,
    )

    assert any(
        "analytics-ui-test-alert-drift: alert references unimplemented metrics "
        "['lotus_unimplemented_alert_metric_total']" in error
        for error in errors
    )
    assert any(
        "analytics-ui-test-alert-drift: runbook annotation is required" in error
        for error in errors
    )
    assert any(
        "dashboard_certification_review.alert_ids do not match alert rules" in error
        for error in errors
    )


def test_analytics_ui_hardening_review_rejects_open_p1_finding() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    rollout = _load_json(ROLLOUT_CONTRACT_PATH)
    review = copy.deepcopy(_load_json(HARDENING_REVIEW_PATH))
    review["findings"].append(
        {
            "finding_id": "RFC0108-HARDENING-OPEN-P1",
            "severity": "P1",
            "status": "planned_residual",
            "summary": "test-only open finding",
            "evidence": "test-only evidence",
        }
    )

    errors = _validate(observability, rollout, review)

    assert any("P0/P1 findings must be closed" in error for error in errors)
