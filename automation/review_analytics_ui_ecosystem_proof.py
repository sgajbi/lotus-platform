from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from automation.review_analytics_ui_canonical_proof import (  # noqa: E402
    DEFAULT_ALERT_RULES_PATH,
    DEFAULT_CONTRACT_PATH,
    DEFAULT_DASHBOARD_PATH,
    _load_json,
    _metrics_referenced_by_alerts,
    _metrics_referenced_by_dashboard,
    _resolve_live_summary,
    _resolve_optional_path,
    _screenshot_index_path,
    _validate_metric_artifacts,
    _validate_sensitive_content,
)

DEFAULT_ECOSYSTEM_PROOF_CONTRACT_PATH = (
    ROOT / "context" / "contracts" / "analytics-ui-observability-ecosystem-proof.json"
)
DEFAULT_ECOSYSTEM_COMPLETION_CONTRACT_PATH = (
    ROOT / "context" / "contracts" / "analytics-ui-observability-ecosystem-completion.json"
)
DEFAULT_REVIEW_OUTPUT = (
    ROOT / "output" / "rfc-0108-slice-16-ecosystem-proof" / "latest.json"
)

ACCEPTED_QA_STATUSES = {"ok", "passed", "success"}
FAILED_API_STATES = {"failed", "error"}
READY_PANEL_STATES = {"ready", "demo_ready"}
WORKFLOW_EXPECTATIONS = {
    "ACCEPT": ("READY", "READY"),
    "SUPERSEDE": ("HISTORICAL", "HISTORICAL"),
    "REVISE": ("HISTORICAL", "HISTORICAL"),
}


@dataclass(frozen=True)
class EcosystemReviewInputs:
    qa_summary_path: Path
    proof_contract_path: Path = DEFAULT_ECOSYSTEM_PROOF_CONTRACT_PATH
    observability_contract_path: Path = DEFAULT_CONTRACT_PATH
    ecosystem_completion_contract_path: Path = DEFAULT_ECOSYSTEM_COMPLETION_CONTRACT_PATH
    dashboard_path: Path = DEFAULT_DASHBOARD_PATH
    alert_rules_path: Path = DEFAULT_ALERT_RULES_PATH
    protected_diagnostics_response_path: Path | None = None
    protected_diagnostics_url: str | None = None
    gateway_openapi_path: Path | None = None
    gateway_openapi_url: str | None = None
    output_path: Path | None = DEFAULT_REVIEW_OUTPUT


def _fetch_json(url: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
    request = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def _load_optional_json(path: Path | None, url: str | None) -> dict[str, Any] | None:
    if path is not None:
        return _load_json(path)
    if url:
        return _fetch_json(
            url,
            headers={
                "X-Actor-Id": "support-operator-1",
                "X-Tenant-Id": "tenant-sg",
                "X-Region": "APAC",
                "X-Role": "support-operator",
            },
        )
    return None


def _description_index(entries: object) -> dict[str, dict[str, Any]]:
    if not isinstance(entries, list):
        return {}
    indexed: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if isinstance(entry, dict):
            description = str(entry.get("description", ""))
            if description:
                indexed[description] = entry
    return indexed


def _panel_index(entries: object) -> dict[str, dict[str, Any]]:
    if not isinstance(entries, list):
        return {}
    indexed: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if isinstance(entry, dict):
            panel = str(entry.get("panel", ""))
            if panel:
                indexed[panel] = entry
    return indexed


def _validate_runtime_identity(
    *,
    errors: list[str],
    live_summary: dict[str, Any],
    proof_contract: dict[str, Any],
) -> dict[str, Any]:
    runtime = proof_contract.get("canonical_runtime", {})
    expected_portfolio = runtime.get("portfolio_id")
    expected_benchmark = runtime.get("benchmark_code")
    expected_as_of = runtime.get("governed_as_of_date")
    evidence = {
        "portfolio_id": live_summary.get("portfolioId"),
        "benchmark_code": live_summary.get("benchmarkCode"),
        "governed_as_of_date": live_summary.get("canonicalAsOfDate")
        or live_summary.get("asOfDate"),
    }

    if evidence["portfolio_id"] != expected_portfolio:
        errors.append(f"live summary portfolioId must be {expected_portfolio}")
    if evidence["benchmark_code"] != expected_benchmark:
        errors.append(f"live summary benchmarkCode must be {expected_benchmark}")
    if expected_as_of and evidence["governed_as_of_date"] not in {
        expected_as_of,
        None,
    }:
        errors.append(f"live summary governed as-of date must be {expected_as_of}")
    return evidence


def _validate_journeys(
    *,
    errors: list[str],
    live_summary: dict[str, Any],
    proof_contract: dict[str, Any],
) -> dict[str, Any]:
    api_checks = {
        **_description_index(live_summary.get("apiChecks")),
        **_description_index(live_summary.get("uiChecks")),
    }
    panel_checks = _panel_index(live_summary.get("panelClassifications"))
    allowed_partial_panels = set(
        proof_contract.get("canonical_runtime", {}).get("allowed_partial_panels", [])
    )
    journey_evidence: dict[str, Any] = {}

    for journey in proof_contract.get("required_journeys", []):
        journey_id = str(journey.get("journey_id", "<missing>"))
        missing_apis = []
        for expected_description in journey.get("required_api_descriptions", []):
            if expected_description not in api_checks:
                missing_apis.append(expected_description)
                continue
            status = str(api_checks[expected_description].get("status", "")).lower()
            if status in FAILED_API_STATES:
                errors.append(f"{journey_id}: API check failed: {expected_description}")

        missing_panels = []
        for expected_panel in journey.get("required_panel_ids", []):
            panel = panel_checks.get(expected_panel)
            if panel is None:
                missing_panels.append(expected_panel)
                continue
            state = str(panel.get("state", ""))
            if expected_panel in allowed_partial_panels:
                if state not in READY_PANEL_STATES | {"partial"}:
                    errors.append(
                        f"{journey_id}: panel {expected_panel} has unexpected state {state}"
                    )
            elif state not in READY_PANEL_STATES:
                errors.append(
                    f"{journey_id}: panel {expected_panel} must be ready, got {state}"
                )

        if missing_apis:
            errors.append(f"{journey_id}: missing API checks {missing_apis}")
        if missing_panels:
            errors.append(f"{journey_id}: missing panel classifications {missing_panels}")
        journey_evidence[journey_id] = {
            "api_checks": len(journey.get("required_api_descriptions", [])),
            "panel_checks": len(journey.get("required_panel_ids", [])),
        }

    return {"journeys": journey_evidence}


def _validate_workflow_pack(
    *, errors: list[str], live_summary: dict[str, Any]
) -> dict[str, Any]:
    entries = {
        str(entry.get("action") or entry.get("actionType")): entry
        for entry in live_summary.get("workflowPackChecks", [])
        if isinstance(entry, dict) and (entry.get("action") or entry.get("actionType"))
    }
    for action, (expected_result, expected_task_flow) in WORKFLOW_EXPECTATIONS.items():
        entry = entries.get(action)
        if entry is None:
            errors.append(f"workflowPackChecks missing {action}")
            continue
        if entry.get("resultSupportabilityStatus") != expected_result:
            errors.append(f"{action}: resultSupportabilityStatus must be {expected_result}")
        if entry.get("taskFlowSupportabilityStatus") != expected_task_flow:
            errors.append(f"{action}: taskFlowSupportabilityStatus must be {expected_task_flow}")
    return {"workflow_actions": sorted(entries)}


def _validate_screenshots(
    *,
    errors: list[str],
    live_summary: dict[str, Any],
    live_summary_path: Path | None,
    qa_summary_path: Path,
    proof_contract: dict[str, Any],
) -> dict[str, Any]:
    minimum = int(
        proof_contract.get("canonical_runtime", {}).get("minimum_screenshot_count", 0)
    )
    screenshots = live_summary.get("screenshots", [])
    if not isinstance(screenshots, list) or len(screenshots) < minimum:
        errors.append(f"live summary must include at least {minimum} screenshots")
        screenshot_count = len(screenshots) if isinstance(screenshots, list) else 0
    else:
        missing = []
        for screenshot in screenshots:
            if not isinstance(screenshot, dict):
                missing.append("<non-object screenshot>")
                continue
            path = _resolve_optional_path(screenshot.get("path"), qa_summary_path.parent)
            if path is None or not path.exists():
                missing.append(str(screenshot.get("path")))
        if missing:
            errors.append(f"screenshot files missing: {missing}")
        screenshot_count = len(screenshots)

    shot_index_path = _screenshot_index_path(
        live_summary, live_summary_path, qa_summary_path
    )
    if shot_index_path is None or not shot_index_path.exists():
        errors.append("SHOT-INDEX.md is missing for ecosystem screenshot evidence")
    return {
        "screenshot_count": screenshot_count,
        "shot_index_path": str(shot_index_path) if shot_index_path else None,
    }


def _validate_protected_diagnostics(
    *,
    errors: list[str],
    proof_contract: dict[str, Any],
    response: dict[str, Any] | None,
) -> dict[str, Any]:
    proof = proof_contract.get("protected_diagnostics_proof", {})
    if response is None:
        errors.append("protected diagnostics response evidence is required")
        return {}

    expected_audit = proof.get("expected_audit_event")
    if response.get("auditEvent") != expected_audit:
        errors.append(f"protected diagnostics auditEvent must be {expected_audit}")
    if response.get("supportReference") != proof.get("support_reference"):
        errors.append("protected diagnostics supportReference does not match contract")
    safe_dimensions = response.get("safeDimensions", {})
    if not isinstance(safe_dimensions, dict):
        errors.append("protected diagnostics safeDimensions must be an object")
        safe_dimensions = {}
    missing_dimensions = sorted(
        set(proof.get("required_safe_dimensions", [])) - set(safe_dimensions)
    )
    if missing_dimensions:
        errors.append(f"protected diagnostics safeDimensions missing {missing_dimensions}")

    response_text = json.dumps(
        {
            key: value
            for key, value in response.items()
            if key not in {"forbiddenFields", "supportReference"}
        },
        sort_keys=True,
    ).lower()
    leaked_fields = sorted(
        field
        for field in proof.get("forbidden_response_fields", [])
        if field.lower() in response_text
    )
    if leaked_fields:
        errors.append(f"protected diagnostics leaked forbidden fields: {leaked_fields}")
    advertised_forbidden = set(response.get("forbiddenFields", []))
    missing_forbidden = sorted(
        set(proof.get("forbidden_response_fields", [])) - advertised_forbidden
    )
    if missing_forbidden:
        errors.append(
            f"protected diagnostics forbiddenFields missing {missing_forbidden}"
        )
    return {
        "protected_diagnostics_audit_event": response.get("auditEvent"),
        "protected_diagnostics_safe_dimensions": sorted(safe_dimensions),
    }


def _validate_openapi(
    *,
    errors: list[str],
    proof_contract: dict[str, Any],
    openapi: dict[str, Any] | None,
) -> dict[str, Any]:
    if openapi is None:
        errors.append("Gateway OpenAPI evidence is required")
        return {}
    paths = openapi.get("paths", {})
    if not isinstance(paths, dict):
        errors.append("Gateway OpenAPI paths must be an object")
        paths = {}
    missing_paths = [
        path
        for path in proof_contract.get("openapi_proof", {}).get("required_paths", [])
        if path not in paths
    ]
    if missing_paths:
        errors.append(f"Gateway OpenAPI missing paths {missing_paths}")
    diagnostics_path = "/api/v1/analytics-ui/diagnostics/{support_reference}"
    operation = paths.get(diagnostics_path, {}).get("get", {})
    operation_text = json.dumps(operation, sort_keys=True).lower()
    for required_term in (
        "protected",
        "diagnostics",
        "support_reference",
        "gateway.analytics.audit.protected_diagnostics_lookup",
    ):
        if required_term not in operation_text:
            errors.append(f"Gateway diagnostics OpenAPI missing {required_term}")
    return {"openapi_paths": sorted(paths)}


def _validate_dashboard_alert_inventory(
    *,
    errors: list[str],
    proof_contract: dict[str, Any],
    observability_contract: dict[str, Any],
    dashboard: dict[str, Any],
    alert_rules: dict[str, Any],
) -> dict[str, Any]:
    metric_evidence = _validate_metric_artifacts(
        errors=errors,
        contract=observability_contract,
        dashboard=dashboard,
        alert_rules=alert_rules,
    )
    dashboard_ids = {str(dashboard.get("uid") or dashboard.get("dashboard_id"))}
    missing_dashboards = sorted(
        set(
            proof_contract.get("dashboard_alert_proof", {}).get(
                "required_dashboard_ids", []
            )
        )
        - dashboard_ids
    )
    if missing_dashboards:
        errors.append(f"dashboard evidence missing {missing_dashboards}")

    actual_alerts = {
        str(rule.get("labels", {}).get("alert_id"))
        for group in alert_rules.get("groups", [])
        for rule in group.get("rules", [])
        if isinstance(rule, dict)
    }
    missing_alerts = sorted(
        set(proof_contract.get("dashboard_alert_proof", {}).get("required_alert_ids", []))
        - actual_alerts
    )
    if missing_alerts:
        errors.append(f"alert evidence missing {missing_alerts}")

    return {
        **metric_evidence,
        "dashboard_metrics": sorted(_metrics_referenced_by_dashboard(dashboard)),
        "alert_metrics": sorted(_metrics_referenced_by_alerts(alert_rules)),
        "alert_ids": sorted(actual_alerts),
    }


def _validate_residual_scope(
    *,
    errors: list[str],
    proof_contract: dict[str, Any],
    observability_contract: dict[str, Any],
    ecosystem_contract: dict[str, Any],
) -> dict[str, Any]:
    feature_status = {
        str(feature.get("feature_key")): str(feature.get("status"))
        for feature in observability_contract.get("supported_feature_keys", [])
        if isinstance(feature, dict)
    }
    residual_keys = {
        str(entry.get("feature_key")) for entry in proof_contract.get("residual_scope", [])
    }
    for residual_key in residual_keys:
        if feature_status.get(residual_key) != "planned":
            errors.append(f"{residual_key}: residual feature must remain planned")
    slice_status = {
        int(entry.get("slice_id")): str(entry.get("status"))
        for entry in ecosystem_contract.get("ecosystem_completion_slices", [])
        if isinstance(entry, dict) and str(entry.get("slice_id")).isdigit()
    }
    if slice_status.get(16) != "implemented":
        errors.append("Slice 16 must be implemented in ecosystem completion contract")
    for slice_id in (17, 18):
        if slice_status.get(slice_id) != "planned":
            errors.append(f"Slice {slice_id} must remain planned after Slice 16")
    return {"residual_feature_keys": sorted(residual_keys)}


def review_ecosystem_proof(inputs: EcosystemReviewInputs) -> dict[str, Any]:
    errors: list[str] = []
    qa_summary = _load_json(inputs.qa_summary_path)
    proof_contract = _load_json(inputs.proof_contract_path)
    observability_contract = _load_json(inputs.observability_contract_path)
    ecosystem_contract = _load_json(inputs.ecosystem_completion_contract_path)
    dashboard = _load_json(inputs.dashboard_path)
    alert_rules = yaml.safe_load(inputs.alert_rules_path.read_text(encoding="utf-8"))
    diagnostics_response = _load_optional_json(
        inputs.protected_diagnostics_response_path, inputs.protected_diagnostics_url
    )
    openapi = _load_optional_json(inputs.gateway_openapi_path, inputs.gateway_openapi_url)

    status = str(qa_summary.get("status") or qa_summary.get("result") or "").lower()
    if status not in ACCEPTED_QA_STATUSES:
        errors.append(f"ecosystem QA summary status is not ok: {status}")

    live_summary, live_summary_path = _resolve_live_summary(
        qa_summary, inputs.qa_summary_path
    )
    if live_summary is None:
        errors.append("ecosystem QA summary does not reference a live validation summary")
        live_evidence: dict[str, Any] = {}
    else:
        live_evidence = {
            **_validate_runtime_identity(
                errors=errors,
                live_summary=live_summary,
                proof_contract=proof_contract,
            ),
            **_validate_journeys(
                errors=errors,
                live_summary=live_summary,
                proof_contract=proof_contract,
            ),
            **_validate_workflow_pack(errors=errors, live_summary=live_summary),
            **_validate_screenshots(
                errors=errors,
                live_summary=live_summary,
                live_summary_path=live_summary_path,
                qa_summary_path=inputs.qa_summary_path,
                proof_contract=proof_contract,
            ),
        }

    sensitive_paths = [inputs.qa_summary_path]
    if live_summary_path is not None:
        sensitive_paths.append(live_summary_path)
    if live_summary is not None:
        shot_index = _screenshot_index_path(
            live_summary, live_summary_path, inputs.qa_summary_path
        )
        if shot_index is not None:
            sensitive_paths.append(shot_index)

    review = {
        "status": "failed",
        "rfc": "RFC-0108",
        "slice": "Slice 16 ecosystem implementation proof",
        "qa_summary_path": str(inputs.qa_summary_path),
        "live_summary_path": str(live_summary_path) if live_summary_path else None,
        "evidence": {
            **live_evidence,
            **_validate_protected_diagnostics(
                errors=errors,
                proof_contract=proof_contract,
                response=diagnostics_response,
            ),
            **_validate_openapi(
                errors=errors,
                proof_contract=proof_contract,
                openapi=openapi,
            ),
            **_validate_dashboard_alert_inventory(
                errors=errors,
                proof_contract=proof_contract,
                observability_contract=observability_contract,
                dashboard=dashboard,
                alert_rules=alert_rules,
            ),
            **_validate_residual_scope(
                errors=errors,
                proof_contract=proof_contract,
                observability_contract=observability_contract,
                ecosystem_contract=ecosystem_contract,
            ),
            **_validate_sensitive_content(
                errors=errors,
                contract=observability_contract,
                paths=sensitive_paths,
            ),
        },
        "errors": errors,
    }
    review["status"] = "passed" if not errors else "failed"

    if inputs.output_path is not None:
        inputs.output_path.parent.mkdir(parents=True, exist_ok=True)
        inputs.output_path.write_text(f"{json.dumps(review, indent=2)}\n", encoding="utf-8")
    return review


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Review RFC-0108 Slice 16 ecosystem implementation proof."
    )
    parser.add_argument("qa_summary", type=Path)
    parser.add_argument("--proof-contract", type=Path, default=DEFAULT_ECOSYSTEM_PROOF_CONTRACT_PATH)
    parser.add_argument("--observability-contract", type=Path, default=DEFAULT_CONTRACT_PATH)
    parser.add_argument(
        "--ecosystem-completion-contract",
        type=Path,
        default=DEFAULT_ECOSYSTEM_COMPLETION_CONTRACT_PATH,
    )
    parser.add_argument("--dashboard", type=Path, default=DEFAULT_DASHBOARD_PATH)
    parser.add_argument("--alert-rules", type=Path, default=DEFAULT_ALERT_RULES_PATH)
    parser.add_argument("--protected-diagnostics-response", type=Path)
    parser.add_argument("--protected-diagnostics-url")
    parser.add_argument("--gateway-openapi", type=Path)
    parser.add_argument("--gateway-openapi-url")
    parser.add_argument("--output", type=Path, default=DEFAULT_REVIEW_OUTPUT)
    args = parser.parse_args()

    review = review_ecosystem_proof(
        EcosystemReviewInputs(
            qa_summary_path=args.qa_summary,
            proof_contract_path=args.proof_contract,
            observability_contract_path=args.observability_contract,
            ecosystem_completion_contract_path=args.ecosystem_completion_contract,
            dashboard_path=args.dashboard,
            alert_rules_path=args.alert_rules,
            protected_diagnostics_response_path=args.protected_diagnostics_response,
            protected_diagnostics_url=args.protected_diagnostics_url,
            gateway_openapi_path=args.gateway_openapi,
            gateway_openapi_url=args.gateway_openapi_url,
            output_path=args.output,
        )
    )
    if review["errors"]:
        for error in review["errors"]:
            print(error)
        return 1
    print("RFC-0108 ecosystem implementation proof review passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
