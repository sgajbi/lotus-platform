from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT_PATH = (
    ROOT / "context" / "contracts" / "analytics-ui-observability-contract.json"
)
IMPLEMENTED_SLICE_12_PARTIAL_KEYS = {
    "analytics.backend.observability.freshness_supportability",
    "advise.observability.advisory_supportability",
    "archive.observability.archive_supportability",
    "ai.observability.ai_surface_supportability",
    "core.observability.portfolio_supportability",
    "manage.observability.action_register_supportability",
    "performance.observability.calculation_supportability",
    "render.observability.render_supportability",
    "report.observability.evidence_surface_supportability",
    "risk.observability.calculation_supportability",
}
IMPLEMENTED_SLICE_13_PARTIAL_KEYS = {
    "gateway.analytics.observability.fanout_metrics",
    "gateway.analytics.observability.protected_diagnostics",
}
IMPLEMENTED_SLICE_13_KEYS = {
    *IMPLEMENTED_SLICE_13_PARTIAL_KEYS,
    "gateway.analytics.observability.all_ui_fanout_paths",
}
IMPLEMENTED_FOUNDATION_KEYS = {
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
    "workbench.analytics.observability.advisor_brief_review_action_metrics",
    "workbench.analytics.observability.mutation_hydration_boundary",
    "workbench.analytics.observability.safe_dashboard",
    "workbench.analytics.observability.attention_events",
    "workbench.analytics.observability.entitlement_audit_events",
    "workbench.analytics.observability.canonical_proof",
    "gateway.analytics.observability.correlation_trace",
    "gateway.analytics.observability.structured_fanout_logs",
    "gateway.analytics.observability.contract_vocabulary",
}
SLICE_12_OR_LATER_LIFECYCLES = {
    "slice-12-backend-supportability-partial-implemented",
    "slice-13-gateway-fanout-metrics-partial-implemented",
    "slice-13-gateway-fanout-metrics-implemented",
    "slice-14-workbench-supported-client-reads-partial-implemented",
    "slice-15-ecosystem-dashboards-alerts-implemented",
    "slice-16-ecosystem-implementation-proof-implemented",
    "slice-17-ecosystem-hardening-certified",
    "slice-18-ecosystem-final-closure-implemented",
}
SLICE_13_OR_LATER_LIFECYCLES = {
    "slice-13-gateway-fanout-metrics-partial-implemented",
    "slice-13-gateway-fanout-metrics-implemented",
    "slice-14-workbench-supported-client-reads-partial-implemented",
    "slice-15-ecosystem-dashboards-alerts-implemented",
    "slice-16-ecosystem-implementation-proof-implemented",
    "slice-17-ecosystem-hardening-certified",
    "slice-18-ecosystem-final-closure-implemented",
}
FULL_SLICE_13_OR_LATER_LIFECYCLES = {
    "slice-13-gateway-fanout-metrics-implemented",
    "slice-14-workbench-supported-client-reads-partial-implemented",
    "slice-15-ecosystem-dashboards-alerts-implemented",
    "slice-16-ecosystem-implementation-proof-implemented",
    "slice-17-ecosystem-hardening-certified",
    "slice-18-ecosystem-final-closure-implemented",
}
SLICE_15_OR_LATER_LIFECYCLES = {
    "slice-15-ecosystem-dashboards-alerts-implemented",
    "slice-16-ecosystem-implementation-proof-implemented",
    "slice-17-ecosystem-hardening-certified",
    "slice-18-ecosystem-final-closure-implemented",
}
SLICE_16_OR_LATER_LIFECYCLES = {
    "slice-16-ecosystem-implementation-proof-implemented",
    "slice-17-ecosystem-hardening-certified",
    "slice-18-ecosystem-final-closure-implemented",
}
SLICE_17_OR_LATER_LIFECYCLES = {
    "slice-17-ecosystem-hardening-certified",
    "slice-18-ecosystem-final-closure-implemented",
}
SINGLE_FEATURE_MILESTONE_STATUS_RULES = (
    (
        SLICE_15_OR_LATER_LIFECYCLES,
        "platform.analytics.observability.ecosystem_dashboards_alerts",
        "Slice 15",
    ),
    (
        SLICE_16_OR_LATER_LIFECYCLES,
        "platform.analytics.observability.ecosystem_implementation_proof",
        "Slice 16",
    ),
    (
        SLICE_17_OR_LATER_LIFECYCLES,
        "platform.analytics.observability.ecosystem_hardening_certification",
        "Slice 17",
    ),
    (
        {"slice-18-ecosystem-final-closure-implemented"},
        "platform.analytics.observability.ecosystem_final_closure",
        "Slice 18",
    ),
    (
        None,
        "workbench.analytics.observability.caller_context_entitlement_certification",
        "Slice 19",
    ),
)
ALLOWED_LIFECYCLE_STATUSES = {
    "implementation-not-started",
    "slice-0-implemented",
    "slice-1-structure-implemented",
    "slice-2-telemetry-contract-implemented",
    "slice-3-correlation-propagation-implemented",
    "slice-4-structured-logging-implemented",
    "slice-5-metrics-dashboard-implemented",
    "slice-6-attention-events-implemented",
    "slice-7-audit-events-implemented",
    "slice-8-canonical-proof-implemented",
    "slice-9-rollout-readiness-implemented",
    "second-last-hardening-implemented",
    "final-closure-implemented",
    "slice-10-ecosystem-contract-implemented",
    "slice-11-scaffold-ci-enforcement-implemented",
    "slice-12-backend-supportability-partial-implemented",
    "slice-13-gateway-fanout-metrics-partial-implemented",
    "slice-13-gateway-fanout-metrics-implemented",
    "slice-14-workbench-supported-client-reads-partial-implemented",
    "slice-15-ecosystem-dashboards-alerts-implemented",
    "slice-16-ecosystem-implementation-proof-implemented",
    "slice-17-ecosystem-hardening-certified",
    "slice-18-ecosystem-final-closure-implemented",
}
IMPLEMENTATION_BACKED_METRIC_NAMES = {
    "lotus_workbench_panel_hydration_duration_seconds",
    "lotus_workbench_panel_state_total",
    "lotus_workbench_api_request_duration_seconds",
    "lotus_gateway_analytics_fanout_duration_seconds",
    "lotus_gateway_analytics_degraded_total",
    "lotus_analytics_freshness_bucket_total",
    "lotus_analytics_ui_attention_events_total",
    "lotus_ai_surface_supportability_state",
}
REQUIRED_STATES = {
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
REQUIRED_ARTIFACT_TYPES = {
    "browser",
    "gateway-api",
    "backend-log-metric",
    "dashboard",
    "sensitive-data-assertion",
    "github-check",
}
REQUIRED_SCAFFOLD_REQUIREMENTS = {
    "structured JSON event logging",
    "product-safe problem-details errors",
    "OpenAPI quality gate",
    "supported-features placeholder",
    "RFC implementation evidence directory",
}


def _load_contract(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require_implemented_status(
    *,
    errors: list[str],
    key: str,
    status: object,
    slice_label: str,
) -> None:
    if status != "implemented":
        errors.append(f"{key}: status must be implemented after {slice_label} proof")


def _validate_slice_12_supported_feature_status(
    *,
    errors: list[str],
    key: str,
    status: object,
    lifecycle_status: object,
) -> bool:
    if (
        lifecycle_status not in SLICE_12_OR_LATER_LIFECYCLES
        or key not in IMPLEMENTED_SLICE_12_PARTIAL_KEYS
    ):
        return False

    _require_implemented_status(
        errors=errors,
        key=key,
        status=status,
        slice_label="Slice 12",
    )
    return True


def _validate_slice_13_supported_feature_status(
    *,
    errors: list[str],
    key: str,
    status: object,
    lifecycle_status: object,
) -> bool:
    if lifecycle_status not in SLICE_13_OR_LATER_LIFECYCLES:
        return False

    implemented_slice_13_keys = (
        IMPLEMENTED_SLICE_13_KEYS
        if lifecycle_status in FULL_SLICE_13_OR_LATER_LIFECYCLES
        else IMPLEMENTED_SLICE_13_PARTIAL_KEYS
    )
    if key not in implemented_slice_13_keys:
        return False

    _require_implemented_status(
        errors=errors,
        key=key,
        status=status,
        slice_label="Slice 13",
    )
    return True


def _validate_single_feature_milestone_status(
    *,
    errors: list[str],
    key: str,
    status: object,
    lifecycle_status: object,
) -> bool:
    for allowed_lifecycles, feature_key, slice_label in SINGLE_FEATURE_MILESTONE_STATUS_RULES:
        if key != feature_key:
            continue
        if allowed_lifecycles is not None and lifecycle_status not in allowed_lifecycles:
            continue

        _require_implemented_status(
            errors=errors,
            key=key,
            status=status,
            slice_label=slice_label,
        )
        return True

    return False


def _validate_supported_feature_status(
    *,
    errors: list[str],
    key: str,
    status: object,
    lifecycle_status: object,
) -> None:
    if key in IMPLEMENTED_FOUNDATION_KEYS:
        if status not in {"planned", "implemented"}:
            errors.append(f"{key}: status must be planned or implemented")
        return

    if _validate_slice_12_supported_feature_status(
        errors=errors,
        key=key,
        status=status,
        lifecycle_status=lifecycle_status,
    ):
        return

    if _validate_slice_13_supported_feature_status(
        errors=errors,
        key=key,
        status=status,
        lifecycle_status=lifecycle_status,
    ):
        return

    if _validate_single_feature_milestone_status(
        errors=errors,
        key=key,
        status=status,
        lifecycle_status=lifecycle_status,
    ):
        return

    if status != "planned":
        errors.append(
            f"{key}: status must remain planned until implementation proof exists"
        )


def _validate_supported_feature_keys(
    *,
    errors: list[str],
    contract: dict[str, Any],
) -> None:
    feature_keys = contract.get("supported_feature_keys", [])
    if not feature_keys:
        errors.append("supported_feature_keys must list planned governance keys")
    lifecycle_status = contract.get("lifecycle_status")
    for feature in feature_keys:
        key = feature.get("feature_key", "<missing>")
        status = feature.get("status")
        _validate_supported_feature_status(
            errors=errors,
            key=key,
            status=status,
            lifecycle_status=lifecycle_status,
        )
        if not feature.get("promotion_evidence"):
            errors.append(f"{key}: promotion_evidence is required")


def _validate_contract_identity_and_lifecycle(
    *,
    errors: list[str],
    contract: dict[str, Any],
) -> None:
    if contract.get("contract_id") != "analytics-ui-observability-contract":
        errors.append("contract_id must be analytics-ui-observability-contract")
    if contract.get("governed_by_rfc") != "RFC-0108":
        errors.append("governed_by_rfc must be RFC-0108")
    if contract.get("lifecycle_status") not in ALLOWED_LIFECYCLE_STATUSES:
        errors.append(
            "lifecycle_status must be implementation-not-started, slice-0-implemented, "
            "slice-1-structure-implemented, slice-2-telemetry-contract-implemented, "
            "slice-3-correlation-propagation-implemented, "
            "slice-4-structured-logging-implemented, "
            "slice-5-metrics-dashboard-implemented, or "
            "slice-6-attention-events-implemented, or "
            "slice-7-audit-events-implemented, or "
            "slice-8-canonical-proof-implemented, or "
            "slice-9-rollout-readiness-implemented, or "
            "second-last-hardening-implemented, or "
            "final-closure-implemented, or "
            "slice-10-ecosystem-contract-implemented, or "
            "slice-11-scaffold-ci-enforcement-implemented, or "
            "slice-12-backend-supportability-partial-implemented, or "
            "slice-13-gateway-fanout-metrics-partial-implemented, or "
            "slice-13-gateway-fanout-metrics-implemented, or "
            "slice-14-workbench-supported-client-reads-partial-implemented, or "
            "slice-15-ecosystem-dashboards-alerts-implemented, or "
            "slice-16-ecosystem-implementation-proof-implemented, or "
            "slice-17-ecosystem-hardening-certified, or "
            "slice-18-ecosystem-final-closure-implemented"
        )


def _validate_label_policy(
    *,
    errors: list[str],
    allowed_labels: set[str],
    forbidden_fields: set[str],
) -> None:
    overlap = allowed_labels & forbidden_fields
    if overlap:
        errors.append(
            f"allowed_labels must not include forbidden fields: {sorted(overlap)}"
        )


def _validate_metric_family(
    *,
    errors: list[str],
    metric: dict[str, Any],
    allowed_labels: set[str],
    forbidden_fields: set[str],
) -> None:
    name = metric.get("metric_name", "<missing>")
    if name in IMPLEMENTATION_BACKED_METRIC_NAMES:
        if metric.get("implemented") is not True:
            errors.append(f"{name}: implemented must be true after Slice 5 proof")
    elif metric.get("implemented") is not False:
        errors.append(
            f"{name}: implemented must remain false before implementation proof"
        )
    labels = set(metric.get("labels", []))
    unexpected_labels = labels - allowed_labels
    if unexpected_labels:
        errors.append(
            f"{name}: labels are not in allowed_labels: {sorted(unexpected_labels)}"
        )
    forbidden_labels = labels & forbidden_fields
    if forbidden_labels:
        errors.append(
            f"{name}: labels include forbidden fields: {sorted(forbidden_labels)}"
        )
    if not metric.get("purpose"):
        errors.append(f"{name}: purpose is required")


def _validate_metric_families(
    *,
    errors: list[str],
    contract: dict[str, Any],
    allowed_labels: set[str],
    forbidden_fields: set[str],
) -> tuple[list[object], set[str]]:
    metric_families = contract.get("metric_families", [])
    if not metric_families:
        errors.append("metric_families must define planned metric candidates")

    for metric in metric_families:
        if isinstance(metric, dict):
            _validate_metric_family(
                errors=errors,
                metric=metric,
                allowed_labels=allowed_labels,
                forbidden_fields=forbidden_fields,
            )

    implemented_metric_names = {
        str(metric.get("metric_name"))
        for metric in metric_families
        if isinstance(metric, dict) and metric.get("implemented") is True
    }
    return metric_families, implemented_metric_names


def _validate_dashboard_metric_references(
    *,
    errors: list[str],
    contract: dict[str, Any],
    implemented_metric_names: set[str],
) -> None:
    if not contract.get("dashboards"):
        return

    for dashboard in contract["dashboards"]:
        dashboard_id = dashboard.get("dashboard_id", "<missing>")
        metric_names = set(dashboard.get("metric_names", []))
        missing_metrics = sorted(metric_names - implemented_metric_names)
        if missing_metrics:
            errors.append(
                f"{dashboard_id}: dashboard references unimplemented metrics: {missing_metrics}"
            )


def _validate_alert_metric_references(
    *,
    errors: list[str],
    contract: dict[str, Any],
    implemented_metric_names: set[str],
) -> None:
    if not contract.get("alerts"):
        return

    for alert in contract["alerts"]:
        alert_id = alert.get("alert_id", "<missing>")
        metric_name = str(alert.get("metric_name", ""))
        if metric_name not in implemented_metric_names:
            errors.append(
                f"{alert_id}: alert references unimplemented metric: {metric_name}"
            )


def _validate_state_vocabulary(
    contract: dict[str, Any],
    errors: list[str],
) -> None:
    states = set(contract.get("state_vocabulary", []))
    missing_states = REQUIRED_STATES - states
    if missing_states:
        errors.append(
            f"state_vocabulary missing required states: {sorted(missing_states)}"
        )


def _validate_evidence_requirements(
    contract: dict[str, Any],
    errors: list[str],
) -> None:
    evidence_requirements = contract.get("evidence_requirements", {})
    artifact_types = set(evidence_requirements.get("artifact_types", []))
    missing_artifacts = REQUIRED_ARTIFACT_TYPES - artifact_types
    if missing_artifacts:
        errors.append(
            f"evidence_requirements missing artifact types: {sorted(missing_artifacts)}"
        )


def _validate_scaffold_requirements(
    contract: dict[str, Any],
    errors: list[str],
) -> None:
    scaffold_requirements = set(contract.get("scaffold_requirements", []))
    for required in REQUIRED_SCAFFOLD_REQUIREMENTS:
        if required not in scaffold_requirements:
            errors.append(f"scaffold_requirements missing {required}")


def validate_contract(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    _validate_contract_identity_and_lifecycle(errors=errors, contract=contract)

    allowed_labels = set(contract.get("allowed_labels", []))
    forbidden_fields = set(contract.get("forbidden_fields", []))
    _validate_label_policy(
        errors=errors,
        allowed_labels=allowed_labels,
        forbidden_fields=forbidden_fields,
    )

    _, implemented_metric_names = _validate_metric_families(
        errors=errors,
        contract=contract,
        allowed_labels=allowed_labels,
        forbidden_fields=forbidden_fields,
    )
    _validate_telemetry_contract(
        errors=errors,
        contract=contract,
        allowed_labels=allowed_labels,
        forbidden_fields=forbidden_fields,
    )
    _validate_observation_boundaries(
        errors=errors,
        contract=contract,
        implemented_metric_names=implemented_metric_names,
    )
    _validate_dashboard_metric_references(
        errors=errors,
        contract=contract,
        implemented_metric_names=implemented_metric_names,
    )
    _validate_alert_metric_references(
        errors=errors,
        contract=contract,
        implemented_metric_names=implemented_metric_names,
    )
    _validate_state_vocabulary(contract, errors)
    _validate_supported_feature_keys(errors=errors, contract=contract)
    _validate_evidence_requirements(contract, errors)
    _validate_scaffold_requirements(contract, errors)
    return errors


def _validate_attribute_list(
    *,
    errors: list[str],
    name: str,
    attributes: object,
    allowed_labels: set[str],
    forbidden_fields: set[str],
) -> None:
    if not isinstance(attributes, list) or not attributes:
        errors.append(f"{name}: attributes must be a non-empty list")
        return

    attribute_set = {str(attribute) for attribute in attributes}
    unsupported = sorted(attribute_set - allowed_labels)
    if unsupported:
        errors.append(f"{name}: attributes are not in allowed_labels: {unsupported}")
    forbidden = sorted(attribute_set & forbidden_fields)
    if forbidden:
        errors.append(f"{name}: attributes include forbidden fields: {forbidden}")


def _validate_telemetry_events(
    *,
    errors: list[str],
    section_name: str,
    events: object,
    allowed_labels: set[str],
    forbidden_fields: set[str],
) -> None:
    if not isinstance(events, list) or not events:
        errors.append(f"telemetry_contract.{section_name} must define planned events")
        return

    for event in events:
        if not isinstance(event, dict):
            errors.append(f"telemetry_contract.{section_name} entries must be objects")
            continue
        event_name = str(event.get("event_name", "<missing>"))
        implementation_backed_events = {
            "workbench.analytics.panel_hydration",
            "workbench.analytics.panel_state",
            "workbench.analytics.api_request",
            "workbench.analytics.attention",
            "gateway.analytics.fanout.completed",
            "gateway.analytics.fanout.degraded",
            "gateway.analytics.audit.analytics_read_allowed",
            "gateway.analytics.audit.analytics_read_denied",
        }
        if event_name in implementation_backed_events:
            if event.get("implemented") is not True:
                errors.append(
                    f"{event_name}: implemented must be true after implementation proof"
                )
        elif event.get("implemented") is not False:
            errors.append(
                f"{event_name}: implemented must remain false before runtime proof"
            )
        if not event.get("purpose"):
            errors.append(f"{event_name}: purpose is required")
        _validate_attribute_list(
            errors=errors,
            name=event_name,
            attributes=event.get("attributes"),
            allowed_labels=allowed_labels,
            forbidden_fields=forbidden_fields,
        )


def _validate_telemetry_severity_levels(
    errors: list[str], telemetry_contract: dict[str, Any]
) -> None:
    required_severity_levels = {"info", "warning", "action_required", "critical"}
    severity_levels = set(telemetry_contract.get("severity_levels", []))
    if severity_levels != required_severity_levels:
        errors.append(
            "telemetry_contract.severity_levels must equal "
            f"{sorted(required_severity_levels)}"
        )


def _validate_telemetry_event_type_lists(
    errors: list[str], telemetry_contract: dict[str, Any]
) -> None:
    for section_name in ("attention_event_types", "audit_event_types"):
        values = telemetry_contract.get(section_name, [])
        if not isinstance(values, list) or not values:
            errors.append(f"telemetry_contract.{section_name} must be a non-empty list")


def _validate_telemetry_event_sections(
    *,
    errors: list[str],
    telemetry_contract: dict[str, Any],
    allowed_labels: set[str],
    forbidden_fields: set[str],
) -> None:
    _validate_telemetry_events(
        errors=errors,
        section_name="browser_events",
        events=telemetry_contract.get("browser_events"),
        allowed_labels=allowed_labels,
        forbidden_fields=forbidden_fields,
    )
    _validate_telemetry_events(
        errors=errors,
        section_name="gateway_log_events",
        events=telemetry_contract.get("gateway_log_events"),
        allowed_labels=allowed_labels,
        forbidden_fields=forbidden_fields,
    )


def _validate_telemetry_attribute_groups(
    *,
    errors: list[str],
    telemetry_contract: dict[str, Any],
    allowed_labels: set[str],
    forbidden_fields: set[str],
) -> None:
    for section_name in (
        "trace_attributes",
        "attention_event_attributes",
        "audit_event_attributes",
    ):
        _validate_attribute_list(
            errors=errors,
            name=f"telemetry_contract.{section_name}",
            attributes=telemetry_contract.get(section_name),
            allowed_labels=allowed_labels,
            forbidden_fields=forbidden_fields,
        )


def _validate_dashboard_reference_policy(
    errors: list[str],
    telemetry_contract: dict[str, Any],
    forbidden_fields: set[str],
) -> None:
    dashboard_policy = telemetry_contract.get("dashboard_reference_policy", {})
    if dashboard_policy.get("implemented_metrics_only") is not True:
        errors.append(
            "dashboard_reference_policy.implemented_metrics_only must be true"
        )
    dashboard_forbidden = set(dashboard_policy.get("forbidden_variables", []))
    missing_dashboard_forbidden = forbidden_fields - dashboard_forbidden
    if missing_dashboard_forbidden:
        errors.append(
            "dashboard_reference_policy.forbidden_variables missing forbidden fields: "
            f"{sorted(missing_dashboard_forbidden)}"
        )


def _validate_alert_reference_policy(
    errors: list[str],
    telemetry_contract: dict[str, Any],
    forbidden_fields: set[str],
) -> None:
    alert_policy = telemetry_contract.get("alert_reference_policy", {})
    if alert_policy.get("implemented_metrics_only") is not True:
        errors.append("alert_reference_policy.implemented_metrics_only must be true")
    alert_forbidden = set(alert_policy.get("forbidden_annotations", []))
    missing_alert_forbidden = forbidden_fields - alert_forbidden
    if missing_alert_forbidden:
        errors.append(
            "alert_reference_policy.forbidden_annotations missing forbidden fields: "
            f"{sorted(missing_alert_forbidden)}"
        )


def _validate_protected_diagnostics_policy(
    errors: list[str], telemetry_contract: dict[str, Any]
) -> None:
    diagnostics_policy = telemetry_contract.get("protected_diagnostics_policy", {})
    if diagnostics_policy.get("metrics_must_not_carry_lookup_identifiers") is not True:
        errors.append(
            "protected diagnostics must keep lookup identifiers out of metrics"
        )
    if diagnostics_policy.get("operator_lookup_requires_protected_api") is not True:
        errors.append(
            "protected diagnostics must require protected operator lookup APIs"
        )
    if diagnostics_policy.get("raw_request_response_capture_allowed") is not False:
        errors.append(
            "protected diagnostics must not allow raw request/response capture"
        )


def _validate_telemetry_contract(
    *,
    errors: list[str],
    contract: dict[str, Any],
    allowed_labels: set[str],
    forbidden_fields: set[str],
) -> None:
    telemetry_contract = contract.get("telemetry_contract")
    if not isinstance(telemetry_contract, dict):
        errors.append("telemetry_contract is required")
        return

    _validate_telemetry_severity_levels(errors, telemetry_contract)
    _validate_telemetry_event_type_lists(errors, telemetry_contract)
    _validate_telemetry_event_sections(
        errors=errors,
        telemetry_contract=telemetry_contract,
        allowed_labels=allowed_labels,
        forbidden_fields=forbidden_fields,
    )
    _validate_telemetry_attribute_groups(
        errors=errors,
        telemetry_contract=telemetry_contract,
        allowed_labels=allowed_labels,
        forbidden_fields=forbidden_fields,
    )
    _validate_dashboard_reference_policy(errors, telemetry_contract, forbidden_fields)
    _validate_alert_reference_policy(errors, telemetry_contract, forbidden_fields)
    _validate_protected_diagnostics_policy(errors, telemetry_contract)


def _validate_observation_boundaries(
    *,
    errors: list[str],
    contract: dict[str, Any],
    implemented_metric_names: set[str],
) -> None:
    boundaries = contract.get("observation_boundaries")
    if not isinstance(boundaries, list) or not boundaries:
        errors.append("observation_boundaries must define implemented UI observation boundaries")
        return

    boundary_by_id = {
        str(boundary.get("boundary_id")): boundary
        for boundary in boundaries
        if isinstance(boundary, dict)
    }
    mutation_boundary = boundary_by_id.get(
        "workbench-mutation-actions-exclude-panel-hydration"
    )
    if not mutation_boundary:
        errors.append(
            "observation_boundaries missing workbench-mutation-actions-exclude-panel-hydration"
        )
        return

    if mutation_boundary.get("owner_repo") != "lotus-workbench":
        errors.append("mutation hydration boundary must be owned by lotus-workbench")
    if mutation_boundary.get("implemented") is not True:
        errors.append("mutation hydration boundary must be implemented")

    surfaces = set(mutation_boundary.get("mutation_surfaces", []))
    if "performance-advisor-brief-review-action" not in surfaces:
        errors.append(
            "mutation hydration boundary must include performance-advisor-brief-review-action"
        )

    included_metrics = set(mutation_boundary.get("included_metric_families", []))
    excluded_metrics = set(mutation_boundary.get("excluded_metric_families", []))
    required_included = {
        "lotus_workbench_api_request_duration_seconds",
        "lotus_workbench_panel_state_total",
    }
    missing_included = sorted(required_included - included_metrics)
    if missing_included:
        errors.append(
            "mutation hydration boundary included_metric_families missing "
            f"{missing_included}"
        )
    if "lotus_workbench_panel_hydration_duration_seconds" not in excluded_metrics:
        errors.append(
            "mutation hydration boundary must exclude panel hydration metrics"
        )
    overlap = sorted(included_metrics & excluded_metrics)
    if overlap:
        errors.append(
            "mutation hydration boundary includes and excludes the same metric families: "
            f"{overlap}"
        )
    unknown_metrics = sorted((included_metrics | excluded_metrics) - implemented_metric_names)
    if unknown_metrics:
        errors.append(
            "mutation hydration boundary references unknown or unimplemented metrics: "
            f"{unknown_metrics}"
        )

    evidence = str(mutation_boundary.get("evidence", ""))
    for required_fragment in (
        "Workbench PR #136",
        "3dfdbd90878a82562ae38d8df66b1947ec16154f",
        "hydrationReviewActionLineCount=0",
        "hasApiRequestMetric=true",
        "hasPanelStateMetric=true",
        "leakedForbidden=[]",
        "2864f2c",
    ):
        if required_fragment not in evidence:
            errors.append(
                "mutation hydration boundary evidence missing "
                f"{required_fragment}"
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate RFC-0108 analytics UI observability contract."
    )
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT_PATH)
    args = parser.parse_args()

    errors = validate_contract(_load_contract(args.contract))
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Analytics UI observability contract validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
