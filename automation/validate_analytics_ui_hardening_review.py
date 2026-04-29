from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = ROOT / "context" / "contracts"
DEFAULT_OBSERVABILITY_CONTRACT_PATH = (
    CONTRACT_DIR / "analytics-ui-observability-contract.json"
)
DEFAULT_ROLLOUT_CONTRACT_PATH = (
    CONTRACT_DIR / "analytics-ui-observability-rollout-readiness.json"
)
DEFAULT_HARDENING_REVIEW_PATH = (
    CONTRACT_DIR / "analytics-ui-observability-hardening-review.json"
)
DEFAULT_PANEL_REGISTRY_PATH = CONTRACT_DIR / "workbench-panel-registry.json"
DEFAULT_DASHBOARD_PATH = (
    ROOT
    / "platform-stack"
    / "grafana"
    / "dashboards"
    / "analytics-ui-observability-overview.json"
)
DEFAULT_ALERT_RULES_PATH = (
    ROOT
    / "platform-stack"
    / "prometheus"
    / "rules"
    / "analytics-ui-observability.rules.yml"
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_prometheus_metric_name(metric_name: str) -> str:
    for suffix in ("_bucket", "_sum", "_count", "_created"):
        if metric_name.endswith(suffix):
            return metric_name[: -len(suffix)]
    return metric_name


def validate_hardening_review(
    *,
    observability_contract: dict[str, Any],
    rollout_contract: dict[str, Any],
    hardening_review: dict[str, Any],
    panel_registry: dict[str, Any],
    dashboard: dict[str, Any],
    alert_rules: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if hardening_review.get("contract_id") != "analytics-ui-observability-hardening-review":
        errors.append("contract_id must be analytics-ui-observability-hardening-review")
    if hardening_review.get("governed_by_rfc") != "RFC-0108":
        errors.append("governed_by_rfc must be RFC-0108")
    if hardening_review.get("lifecycle_status") != "second-last-hardening-implemented":
        errors.append("lifecycle_status must be second-last-hardening-implemented")

    _validate_telemetry_field_review(errors, observability_contract, hardening_review)
    _validate_panel_state_review(
        errors, observability_contract, rollout_contract, hardening_review, panel_registry
    )
    _validate_api_certification_review(errors, hardening_review)
    _validate_dashboard_review(
        errors, observability_contract, hardening_review, dashboard, alert_rules
    )
    _validate_enterprise_governance(errors, observability_contract, hardening_review)
    _validate_findings(errors, hardening_review)
    _validate_residual_scope(errors, observability_contract, rollout_contract, hardening_review)
    _validate_required_checks(errors, hardening_review)
    return errors


def _validate_telemetry_field_review(
    errors: list[str],
    observability_contract: dict[str, Any],
    hardening_review: dict[str, Any],
) -> None:
    review = hardening_review.get("telemetry_field_review", {})
    if review.get("source_contract") != observability_contract.get("contract_id"):
        errors.append("telemetry_field_review.source_contract must match observability contract")
    if review.get("allowed_label_policy") != "contract_only":
        errors.append("telemetry_field_review.allowed_label_policy must be contract_only")
    if review.get("forbidden_field_policy") != "deny_all_forbidden_fields":
        errors.append(
            "telemetry_field_review.forbidden_field_policy must be deny_all_forbidden_fields"
        )

    allowed_labels = set(observability_contract.get("allowed_labels", []))
    forbidden_fields = set(observability_contract.get("forbidden_fields", []))
    implemented_metrics = [
        metric
        for metric in observability_contract.get("metric_families", [])
        if metric.get("implemented") is True
    ]
    for metric in implemented_metrics:
        labels = set(metric.get("labels", []))
        unsupported = sorted(labels - allowed_labels)
        forbidden = sorted(labels & forbidden_fields)
        if unsupported:
            errors.append(f"{metric.get('metric_name')}: unsupported labels {unsupported}")
        if forbidden:
            errors.append(f"{metric.get('metric_name')}: forbidden labels {forbidden}")

    implemented_events = {
        event["event_name"]
        for section in ("browser_events", "gateway_log_events")
        for event in observability_contract.get("telemetry_contract", {}).get(section, [])
        if event.get("implemented") is True
    }
    reviewed_events = set(review.get("runtime_events_reviewed", []))
    missing_events = sorted(implemented_events - reviewed_events)
    if missing_events:
        errors.append(
            "telemetry_field_review.runtime_events_reviewed missing implemented events: "
            f"{missing_events}"
        )

    for section in (
        "trace_attributes",
        "attention_event_attributes",
        "audit_event_attributes",
    ):
        attributes = set(observability_contract.get("telemetry_contract", {}).get(section, []))
        forbidden = sorted(attributes & forbidden_fields)
        unsupported = sorted(attributes - allowed_labels)
        if forbidden:
            errors.append(f"telemetry_contract.{section}: forbidden attributes {forbidden}")
        if unsupported:
            errors.append(f"telemetry_contract.{section}: unsupported attributes {unsupported}")


def _validate_panel_state_review(
    errors: list[str],
    observability_contract: dict[str, Any],
    rollout_contract: dict[str, Any],
    hardening_review: dict[str, Any],
    panel_registry: dict[str, Any],
) -> None:
    review = hardening_review.get("panel_state_review", {})
    if review.get("source_registry") != panel_registry.get("contract_id"):
        errors.append("panel_state_review.source_registry must match panel registry")
    certified_routes = {
        str(group.get("route"))
        for group in rollout_contract.get("certified_route_groups", [])
        if isinstance(group, dict)
    }
    reviewed_routes = set(review.get("certified_route_groups_reviewed", []))
    missing_routes = sorted(certified_routes - reviewed_routes)
    if missing_routes:
        errors.append(
            "panel_state_review.certified_route_groups_reviewed missing routes: "
            f"{missing_routes}"
        )

    telemetry_states = set(observability_contract.get("state_vocabulary", []))
    non_telemetry_states = set(review.get("non_telemetry_registry_states", []))
    allowed_registry_states = telemetry_states | non_telemetry_states
    for panel in panel_registry.get("panels", []):
        panel_id = str(panel.get("panel_id", "<missing>"))
        unsupported_states = sorted(set(panel.get("allowed_states", [])) - allowed_registry_states)
        if unsupported_states:
            errors.append(f"{panel_id}: registry states are not reviewed: {unsupported_states}")
        if panel.get("required_support_state") == "unavailable" and "unavailable" not in non_telemetry_states:
            errors.append(f"{panel_id}: unavailable state must be reviewed as non-telemetry")


def _validate_api_certification_review(
    errors: list[str], hardening_review: dict[str, Any]
) -> None:
    api_items = hardening_review.get("api_certification_review", [])
    if not api_items:
        errors.append("api_certification_review must be non-empty")
        return
    for item in api_items:
        surface = str(item.get("surface", "<missing>"))
        status = item.get("certification_status")
        if item.get("openapi_required") is True and status not in {
            "certified",
            "planned_residual",
        }:
            errors.append(f"{surface}: OpenAPI-required surface must be certified or planned")
        if item.get("changed_by_rfc0108") is True and status == "not_applicable":
            errors.append(f"{surface}: changed RFC-0108 surface cannot be not_applicable")
        if not item.get("evidence"):
            errors.append(f"{surface}: evidence is required")


def _validate_dashboard_review(
    errors: list[str],
    observability_contract: dict[str, Any],
    hardening_review: dict[str, Any],
    dashboard: dict[str, Any],
    alert_rules: dict[str, Any],
) -> None:
    review = hardening_review.get("dashboard_certification_review", {})
    if review.get("dashboard_id") != dashboard.get("uid"):
        errors.append("dashboard_certification_review.dashboard_id must match dashboard uid")
    if review.get("implemented_metrics_only") is not True:
        errors.append("dashboard certification must require implemented metrics only")
    implemented_metric_names = {
        str(metric.get("metric_name"))
        for metric in observability_contract.get("metric_families", [])
        if metric.get("implemented") is True
    }
    dashboard_metric_names = {
        _normalize_prometheus_metric_name(metric_name)
        for metric_name in re.findall(r"lotus_[a-z0-9_]+", json.dumps(dashboard, sort_keys=True))
    }
    unimplemented = sorted(dashboard_metric_names - implemented_metric_names)
    if unimplemented:
        errors.append(f"dashboard references unimplemented metrics: {unimplemented}")

    expected_alert_ids = set(review.get("alert_ids", []))
    actual_alert_ids: set[str] = set()
    for group in alert_rules.get("groups", []):
        for rule in group.get("rules", []):
            labels = rule.get("labels", {})
            annotations = rule.get("annotations", {})
            alert_id = str(labels.get("alert_id", ""))
            actual_alert_ids.add(alert_id)
            expr = str(rule.get("expr", ""))
            rule_metrics = {
                _normalize_prometheus_metric_name(metric_name)
                for metric_name in re.findall(r"lotus_[a-z0-9_]+", expr)
            }
            unimplemented_rule_metrics = sorted(rule_metrics - implemented_metric_names)
            if unimplemented_rule_metrics:
                errors.append(
                    f"{alert_id}: alert references unimplemented metrics "
                    f"{unimplemented_rule_metrics}"
                )
            if review.get("runbook_paths_required") is True and not annotations.get("runbook"):
                errors.append(f"{alert_id}: runbook annotation is required")
    if actual_alert_ids != expected_alert_ids:
        errors.append(
            "dashboard_certification_review.alert_ids do not match alert rules: "
            f"expected {sorted(expected_alert_ids)}, actual {sorted(actual_alert_ids)}"
        )


def _validate_enterprise_governance(
    errors: list[str],
    observability_contract: dict[str, Any],
    hardening_review: dict[str, Any],
) -> None:
    review = hardening_review.get("enterprise_governance_review", {})
    if review.get("supported_features_policy") != "implementation_backed_only":
        errors.append("supported_features_policy must be implementation_backed_only")
    if review.get("sensitive_content_policy") != "no_sensitive_content":
        errors.append("sensitive_content_policy must be no_sensitive_content")
    if review.get("mesh_standards_posture") != "no_new_domain_product_or_mesh_api":
        errors.append("mesh_standards_posture must be no_new_domain_product_or_mesh_api")
    if not observability_contract.get("supported_feature_keys"):
        errors.append("supported features must be governed by the observability contract")


def _validate_findings(errors: list[str], hardening_review: dict[str, Any]) -> None:
    for finding in hardening_review.get("findings", []):
        severity = finding.get("severity")
        status = finding.get("status")
        finding_id = str(finding.get("finding_id", "<missing>"))
        if severity in {"P0", "P1"} and status != "closed":
            errors.append(f"{finding_id}: P0/P1 findings must be closed")
        if status == "planned_residual" and severity in {"P0", "P1"}:
            errors.append(f"{finding_id}: P0/P1 findings cannot be planned residual")
        if not finding.get("summary") or not finding.get("evidence"):
            errors.append(f"{finding_id}: summary and evidence are required")


def _validate_residual_scope(
    errors: list[str],
    observability_contract: dict[str, Any],
    rollout_contract: dict[str, Any],
    hardening_review: dict[str, Any],
) -> None:
    feature_status = {
        str(feature.get("feature_key")): str(feature.get("status"))
        for feature in observability_contract.get("supported_feature_keys", [])
        if isinstance(feature, dict)
    }
    rollout_residual = {
        str(item.get("feature_key"))
        for item in rollout_contract.get("residual_scope", [])
        if isinstance(item, dict)
    }
    hardening_residual = {
        str(item.get("feature_key"))
        for item in hardening_review.get("residual_scope", [])
        if isinstance(item, dict)
    }
    if hardening_residual != rollout_residual:
        errors.append(
            "hardening residual scope must match rollout residual scope: "
            f"expected {sorted(rollout_residual)}, actual {sorted(hardening_residual)}"
        )
    for feature_key in hardening_residual:
        if feature_status.get(feature_key) != "planned":
            errors.append(f"{feature_key}: residual feature must remain planned")


def _validate_required_checks(errors: list[str], hardening_review: dict[str, Any]) -> None:
    required_commands = set(hardening_review.get("required_local_commands", []))
    for command_fragment in (
        "validate_analytics_ui_observability_contract.py",
        "validate_analytics_ui_rollout_readiness.py",
        "validate_analytics_ui_hardening_review.py",
        "test_analytics_ui_hardening_review.py",
    ):
        if not any(command_fragment in command for command in required_commands):
            errors.append(f"required_local_commands must include {command_fragment}")
    required_checks = set(hardening_review.get("required_github_checks", []))
    for check_name in (
        "Cross-App Vocabulary Gate",
        "Feature Lane / Platform Repo Contracts",
        "PR Merge Gate / Platform Repo Contracts",
    ):
        if check_name not in required_checks:
            errors.append(f"required_github_checks missing {check_name}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate RFC-0108 analytics UI hardening review contract."
    )
    parser.add_argument(
        "--observability-contract",
        type=Path,
        default=DEFAULT_OBSERVABILITY_CONTRACT_PATH,
    )
    parser.add_argument(
        "--rollout-contract", type=Path, default=DEFAULT_ROLLOUT_CONTRACT_PATH
    )
    parser.add_argument(
        "--hardening-review", type=Path, default=DEFAULT_HARDENING_REVIEW_PATH
    )
    parser.add_argument("--panel-registry", type=Path, default=DEFAULT_PANEL_REGISTRY_PATH)
    parser.add_argument("--dashboard", type=Path, default=DEFAULT_DASHBOARD_PATH)
    parser.add_argument("--alert-rules", type=Path, default=DEFAULT_ALERT_RULES_PATH)
    args = parser.parse_args()

    errors = validate_hardening_review(
        observability_contract=_load_json(args.observability_contract),
        rollout_contract=_load_json(args.rollout_contract),
        hardening_review=_load_json(args.hardening_review),
        panel_registry=_load_json(args.panel_registry),
        dashboard=_load_json(args.dashboard),
        alert_rules=yaml.safe_load(args.alert_rules.read_text(encoding="utf-8")),
    )
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Analytics UI hardening review validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
