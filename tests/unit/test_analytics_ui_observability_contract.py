from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import yaml

from automation.validate_analytics_ui_observability_contract import validate_contract


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = (
    ROOT / "context" / "contracts" / "analytics-ui-observability-contract.json"
)
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


def _load_contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _normalize_prometheus_metric_name(metric_name: str) -> str:
    for suffix in ("_bucket", "_sum", "_count", "_created"):
        if metric_name.endswith(suffix):
            return metric_name[: -len(suffix)]
    return metric_name


def test_analytics_ui_observability_contract_artifacts_are_present_and_governed() -> (
    None
):
    readme = (ROOT / "context" / "contracts" / "README.md").read_text(encoding="utf-8")
    schema = json.loads(
        (
            ROOT
            / "context"
            / "contracts"
            / "analytics-ui-observability-contract.schema.json"
        ).read_text(encoding="utf-8")
    )
    contract = _load_contract()

    assert "analytics-ui-observability-contract.schema.json" in readme
    assert "analytics-ui-observability-contract.json" in readme
    assert (
        schema["properties"]["contract_id"]["const"]
        == "analytics-ui-observability-contract"
    )
    assert schema["properties"]["governed_by_rfc"]["const"] == "RFC-0108"
    assert contract["contract_id"] == "analytics-ui-observability-contract"
    assert contract["governed_by_rfc"] == "RFC-0108"
    assert (
        contract["lifecycle_status"]
        == "slice-12-backend-supportability-partial-implemented"
    )


def test_analytics_ui_observability_contract_limits_promotion_to_implemented_foundations() -> (
    None
):
    contract = _load_contract()

    assert {dashboard["dashboard_id"] for dashboard in contract["dashboards"]} == {
        "analytics-ui-observability-overview"
    }
    assert {alert["alert_id"] for alert in contract["alerts"]} == {
        "analytics-ui-panel-error-rate",
        "analytics-ui-api-request-latency-p95",
        "analytics-ui-attention-events",
    }
    implemented_metrics = {
        entry["metric_name"]
        for entry in contract["metric_families"]
        if entry["implemented"]
    }
    assert implemented_metrics == {
        "lotus_workbench_panel_hydration_duration_seconds",
        "lotus_workbench_panel_state_total",
        "lotus_workbench_api_request_duration_seconds",
        "lotus_analytics_ui_attention_events_total",
    }
    feature_status = {
        entry["feature_key"]: entry["status"]
        for entry in contract["supported_feature_keys"]
    }
    assert (
        feature_status["platform.scaffolding.analytics_ui_observability_baseline"]
        == "implemented"
    )
    assert (
        feature_status["platform.analytics.observability.telemetry_contract"]
        == "implemented"
    )
    assert (
        feature_status["platform.analytics.observability.rollout_readiness"]
        == "implemented"
    )
    assert (
        feature_status["platform.analytics.observability.hardening_certification"]
        == "implemented"
    )
    assert (
        feature_status["platform.analytics.observability.final_closure"]
        == "implemented"
    )
    assert (
        feature_status["platform.analytics.observability.ecosystem_completion_contract"]
        == "implemented"
    )
    assert (
        feature_status["platform.analytics.observability.scaffold_ci_enforcement"]
        == "implemented"
    )
    assert (
        feature_status["workbench.analytics.observability.contract_vocabulary"]
        == "implemented"
    )
    assert (
        feature_status["workbench.analytics.observability.correlation_trace"]
        == "implemented"
    )
    assert (
        feature_status["workbench.analytics.observability.panel_state_metrics"]
        == "implemented"
    )
    assert (
        feature_status["workbench.analytics.observability.safe_dashboard"]
        == "implemented"
    )
    assert (
        feature_status["workbench.analytics.observability.attention_events"]
        == "implemented"
    )
    assert (
        feature_status["workbench.analytics.observability.entitlement_audit_events"]
        == "implemented"
    )
    assert (
        feature_status["workbench.analytics.observability.canonical_proof"]
        == "implemented"
    )
    assert (
        feature_status["gateway.analytics.observability.contract_vocabulary"]
        == "implemented"
    )
    assert (
        feature_status["gateway.analytics.observability.correlation_trace"]
        == "implemented"
    )
    assert (
        feature_status["gateway.analytics.observability.structured_fanout_logs"]
        == "implemented"
    )
    assert (
        feature_status["performance.observability.calculation_supportability"]
        == "implemented"
    )
    assert (
        feature_status["risk.observability.calculation_supportability"] == "implemented"
    )
    assert (
        feature_status["manage.observability.action_register_supportability"]
        == "implemented"
    )
    assert {
        status
        for key, status in feature_status.items()
        if key
        not in {
            "platform.scaffolding.analytics_ui_observability_baseline",
            "platform.analytics.observability.telemetry_contract",
            "platform.analytics.observability.rollout_readiness",
            "platform.analytics.observability.hardening_certification",
            "platform.analytics.observability.final_closure",
            "platform.analytics.observability.ecosystem_completion_contract",
            "platform.analytics.observability.scaffold_ci_enforcement",
            "workbench.analytics.observability.correlation_trace",
            "workbench.analytics.observability.contract_vocabulary",
            "workbench.analytics.observability.panel_state_metrics",
            "workbench.analytics.observability.safe_dashboard",
            "workbench.analytics.observability.attention_events",
            "workbench.analytics.observability.entitlement_audit_events",
            "workbench.analytics.observability.canonical_proof",
            "gateway.analytics.observability.correlation_trace",
            "gateway.analytics.observability.structured_fanout_logs",
            "gateway.analytics.observability.contract_vocabulary",
            "performance.observability.calculation_supportability",
            "risk.observability.calculation_supportability",
            "manage.observability.action_register_supportability",
        }
    } == {"planned"}

    gateway_events = {
        entry["event_name"]: entry
        for entry in contract["telemetry_contract"]["gateway_log_events"]
    }
    assert gateway_events["gateway.analytics.fanout.completed"]["implemented"] is True
    assert gateway_events["gateway.analytics.fanout.degraded"]["implemented"] is True
    assert (
        gateway_events["gateway.analytics.audit.analytics_read_allowed"]["implemented"]
        is True
    )
    assert (
        gateway_events["gateway.analytics.audit.analytics_read_denied"]["implemented"]
        is True
    )
    assert {"route", "operation", "service", "state", "status_class"} <= set(
        gateway_events["gateway.analytics.fanout.completed"]["attributes"]
    )
    assert {
        "route",
        "operation",
        "service",
        "state",
        "reason",
        "error_category",
    } <= set(gateway_events["gateway.analytics.fanout.degraded"]["attributes"])
    assert {
        "route",
        "panel",
        "operation",
        "state",
        "reason",
        "status_class",
        "region",
        "environment",
    } <= set(
        gateway_events["gateway.analytics.audit.analytics_read_denied"]["attributes"]
    )


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


def test_analytics_ui_observability_contract_records_required_states_and_evidence() -> (
    None
):
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
    assert (
        "portfolio ids"
        in contract["evidence_requirements"]["forbidden_content_classes"]
    )
    assert (
        "screen content"
        in contract["evidence_requirements"]["forbidden_content_classes"]
    )


def test_analytics_ui_observability_contract_records_telemetry_contract() -> None:
    contract = _load_contract()
    telemetry_contract = contract["telemetry_contract"]
    allowed_labels = set(contract["allowed_labels"])
    forbidden_fields = set(contract["forbidden_fields"])

    assert set(telemetry_contract["severity_levels"]) == {
        "info",
        "warning",
        "action_required",
        "critical",
    }
    assert "panel_stale" in telemetry_contract["attention_event_types"]
    assert "analytics_read_denied" in telemetry_contract["audit_event_types"]
    assert {event["event_name"] for event in telemetry_contract["browser_events"]} == {
        "workbench.analytics.panel_hydration",
        "workbench.analytics.panel_state",
        "workbench.analytics.api_request",
        "workbench.analytics.attention",
    }
    assert {
        event["event_name"] for event in telemetry_contract["gateway_log_events"]
    } == {
        "gateway.analytics.fanout.completed",
        "gateway.analytics.fanout.degraded",
        "gateway.analytics.audit.analytics_read_allowed",
        "gateway.analytics.audit.analytics_read_denied",
    }

    for event in telemetry_contract["browser_events"]:
        assert event["implemented"] is True
        assert set(event["attributes"]) <= allowed_labels
        assert set(event["attributes"]).isdisjoint(forbidden_fields)

    for event in telemetry_contract["gateway_log_events"]:
        assert event["implemented"] is True
        assert set(event["attributes"]) <= allowed_labels
        assert set(event["attributes"]).isdisjoint(forbidden_fields)

    for attribute_group in (
        "trace_attributes",
        "attention_event_attributes",
        "audit_event_attributes",
    ):
        attributes = set(telemetry_contract[attribute_group])
        assert attributes <= allowed_labels
        assert attributes.isdisjoint(forbidden_fields)

    assert (
        telemetry_contract["dashboard_reference_policy"]["implemented_metrics_only"]
        is True
    )
    assert (
        telemetry_contract["alert_reference_policy"]["implemented_metrics_only"] is True
    )
    assert (
        set(telemetry_contract["dashboard_reference_policy"]["forbidden_variables"])
        >= forbidden_fields
    )
    assert (
        set(telemetry_contract["alert_reference_policy"]["forbidden_annotations"])
        >= forbidden_fields
    )
    assert telemetry_contract["protected_diagnostics_policy"] == {
        "metrics_must_not_carry_lookup_identifiers": True,
        "operator_lookup_requires_protected_api": True,
        "raw_request_response_capture_allowed": False,
    }


def test_analytics_ui_observability_contract_validator_accepts_baseline() -> None:
    assert validate_contract(_load_contract()) == []


def test_analytics_ui_observability_contract_validator_rejects_forbidden_metric_label() -> (
    None
):
    contract = copy.deepcopy(_load_contract())
    contract["metric_families"][0]["labels"].append("portfolio_id")

    errors = validate_contract(contract)

    assert any("forbidden fields" in error for error in errors)


def test_analytics_ui_observability_contract_validator_rejects_premature_dashboard_claim() -> (
    None
):
    contract = copy.deepcopy(_load_contract())
    contract["dashboards"].append(
        {
            "dashboard_id": "analytics-ui-overview",
            "metric_names": ["lotus_gateway_analytics_fanout_duration_seconds"],
        }
    )

    errors = validate_contract(contract)

    assert any(
        "dashboard references unimplemented metrics" in error for error in errors
    )


def test_analytics_ui_observability_contract_validator_rejects_premature_alert_claim() -> (
    None
):
    contract = copy.deepcopy(_load_contract())
    contract["alerts"].append(
        {
            "alert_id": "analytics-ui-panel-errors",
            "metric_name": "lotus_gateway_analytics_fanout_duration_seconds",
        }
    )

    errors = validate_contract(contract)

    assert any("alert references unimplemented metric" in error for error in errors)


def test_analytics_ui_observability_contract_validator_rejects_sensitive_event_attribute() -> (
    None
):
    contract = copy.deepcopy(_load_contract())
    contract["telemetry_contract"]["browser_events"][0]["attributes"].append(
        "client_name"
    )

    errors = validate_contract(contract)

    assert any("attributes include forbidden fields" in error for error in errors)


def test_analytics_ui_observability_dashboard_references_only_implemented_metrics() -> (
    None
):
    contract = _load_contract()
    dashboard = json.loads(DASHBOARD_PATH.read_text(encoding="utf-8"))

    implemented_metric_names = {
        entry["metric_name"]
        for entry in contract["metric_families"]
        if entry["implemented"]
    }
    dashboard_metric_names = {
        _normalize_prometheus_metric_name(metric_name)
        for metric_name in re.findall(
            r"lotus_[a-z0-9_]+", json.dumps(dashboard, sort_keys=True)
        )
    }
    forbidden_variables = set(
        contract["telemetry_contract"]["dashboard_reference_policy"][
            "forbidden_variables"
        ]
    )
    dashboard_text = json.dumps(dashboard, sort_keys=True)

    assert dashboard["uid"] == "analytics-ui-observability-overview"
    assert dashboard["title"] == "Analytics UI Observability Overview"
    assert len(dashboard["panels"]) == 4
    assert dashboard_metric_names <= implemented_metric_names
    assert all(forbidden not in dashboard_text for forbidden in forbidden_variables)


def test_analytics_ui_observability_alert_rules_align_with_contract() -> None:
    contract = _load_contract()
    rules = yaml.safe_load(ALERT_RULES_PATH.read_text(encoding="utf-8"))

    expected_alerts = {
        alert["alert_id"]: {
            "metric_name": alert["metric_name"],
            "severity": alert["severity"],
            "owner_repo": alert["owner_repo"],
            "runbook_path": alert["runbook_path"],
        }
        for alert in contract["alerts"]
    }
    actual_alerts = {}
    for group in rules["groups"]:
        for rule in group["rules"]:
            alert_id = rule["labels"]["alert_id"]
            actual_alerts[alert_id] = {
                "severity": rule["labels"]["severity"],
                "owner_repo": rule["labels"]["owner_repo"],
                "runbook_path": rule["annotations"]["runbook"],
                "expr": rule["expr"],
                "annotations": rule["annotations"],
            }

    forbidden_annotations = set(
        contract["telemetry_contract"]["alert_reference_policy"][
            "forbidden_annotations"
        ]
    )
    assert set(actual_alerts) == set(expected_alerts)
    for alert_id, expected in expected_alerts.items():
        actual = actual_alerts[alert_id]
        assert actual["severity"] == expected["severity"]
        assert actual["owner_repo"] == expected["owner_repo"]
        assert actual["runbook_path"] == expected["runbook_path"]
        assert expected["metric_name"] in actual["expr"]
        serialized_annotations = json.dumps(actual["annotations"], sort_keys=True)
        assert all(
            forbidden not in serialized_annotations
            for forbidden in forbidden_annotations
        )
