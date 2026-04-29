from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT_PATH = (
    ROOT / "context" / "contracts" / "analytics-ui-observability-contract.json"
)
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
DEFAULT_REVIEW_OUTPUT = (
    ROOT / "output" / "rfc-0108-slice-8-proof-review" / "latest.json"
)

CANONICAL_PORTFOLIO_ID = "PB_SG_GLOBAL_BAL_001"
CANONICAL_BENCHMARK_CODE = "BMK_PB_GLOBAL_BALANCED_60_40"
EXPECTED_SCREENSHOT_COUNT = 7
EXPECTED_METRIC_NAMES = {
    "lotus_workbench_panel_hydration_duration_seconds",
    "lotus_workbench_panel_state_total",
    "lotus_workbench_api_request_duration_seconds",
    "lotus_analytics_ui_attention_events_total",
}


@dataclass(frozen=True)
class ReviewInputs:
    qa_summary_path: Path
    contract_path: Path = DEFAULT_CONTRACT_PATH
    dashboard_path: Path = DEFAULT_DASHBOARD_PATH
    alert_rules_path: Path = DEFAULT_ALERT_RULES_PATH
    output_path: Path | None = DEFAULT_REVIEW_OUTPUT


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_prometheus_metric_name(metric_name: str) -> str:
    for suffix in ("_bucket", "_sum", "_count", "_created"):
        if metric_name.endswith(suffix):
            return metric_name[: -len(suffix)]
    return metric_name


def _implemented_metric_names(contract: dict[str, Any]) -> set[str]:
    return {
        str(metric.get("metric_name"))
        for metric in contract.get("metric_families", [])
        if metric.get("implemented") is True
    }


def _metrics_referenced_by_dashboard(dashboard: dict[str, Any]) -> set[str]:
    return {
        _normalize_prometheus_metric_name(metric_name)
        for metric_name in re.findall(
            r"lotus_[a-z0-9_]+", json.dumps(dashboard, sort_keys=True)
        )
    }


def _metrics_referenced_by_alerts(alert_rules: dict[str, Any]) -> set[str]:
    referenced: set[str] = set()
    for group in alert_rules.get("groups", []):
        for rule in group.get("rules", []):
            referenced.update(
                _normalize_prometheus_metric_name(metric_name)
                for metric_name in re.findall(
                    r"lotus_[a-z0-9_]+", str(rule.get("expr", ""))
                )
            )
    return referenced


def _resolve_live_summary(
    qa_summary: dict[str, Any], qa_summary_path: Path
) -> tuple[dict[str, Any] | None, Path | None]:
    embedded = qa_summary.get("governed_live_summary") or qa_summary.get(
        "live_validation_summary"
    )
    if isinstance(embedded, dict):
        path_value = (
            embedded.get("summary_path")
            or embedded.get("path")
            or qa_summary.get("live_validation_summary_path")
        )
        return embedded, _resolve_optional_path(path_value, qa_summary_path.parent)
    if isinstance(embedded, str):
        summary_path = _resolve_optional_path(embedded, qa_summary_path.parent)
        if summary_path is None or not summary_path.exists():
            return None, summary_path
        return _load_json(summary_path), summary_path

    path_value = (
        qa_summary.get("governed_live_summary_path")
        or qa_summary.get("live_validation_summary_path")
        or qa_summary.get("validation_summary_path")
    )
    summary_path = _resolve_optional_path(path_value, qa_summary_path.parent)
    if summary_path is None or not summary_path.exists():
        return None, summary_path
    return _load_json(summary_path), summary_path


def _resolve_optional_path(value: object, base_dir: Path) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    candidate = (base_dir / path).resolve()
    if candidate.exists():
        return candidate
    return (ROOT / path).resolve()


def _screenshot_index_path(
    live_summary: dict[str, Any], live_summary_path: Path | None, qa_summary_path: Path
) -> Path | None:
    for key in ("shot_index_path", "screenshot_index_path"):
        candidate = _resolve_optional_path(
            live_summary.get(key),
            live_summary_path.parent if live_summary_path else qa_summary_path.parent,
        )
        if candidate is not None:
            return candidate
    if live_summary_path is not None:
        return live_summary_path.with_name("SHOT-INDEX.md")
    screenshots = live_summary.get("screenshots", [])
    if screenshots and isinstance(screenshots[0], dict):
        first_path = _resolve_optional_path(
            screenshots[0].get("path"), qa_summary_path.parent
        )
        if first_path is not None:
            return first_path.parent / "SHOT-INDEX.md"
    return None


def _screenshot_path(path_value: object, qa_summary_path: Path) -> Path | None:
    return _resolve_optional_path(path_value, qa_summary_path.parent)


def _validate_live_summary(
    *,
    errors: list[str],
    live_summary: dict[str, Any],
    live_summary_path: Path | None,
    qa_summary_path: Path,
) -> dict[str, Any]:
    evidence: dict[str, Any] = {}
    if live_summary.get("portfolioId") != CANONICAL_PORTFOLIO_ID:
        errors.append(
            f"live summary portfolioId must be {CANONICAL_PORTFOLIO_ID}"
        )
    if live_summary.get("benchmarkCode") != CANONICAL_BENCHMARK_CODE:
        errors.append(
            f"live summary benchmarkCode must be {CANONICAL_BENCHMARK_CODE}"
        )

    screenshots = live_summary.get("screenshots", [])
    if not isinstance(screenshots, list) or len(screenshots) < EXPECTED_SCREENSHOT_COUNT:
        errors.append(
            f"live summary must include at least {EXPECTED_SCREENSHOT_COUNT} screenshots"
        )
    else:
        missing_screenshots = []
        for item in screenshots:
            if not isinstance(item, dict):
                missing_screenshots.append("<non-object screenshot entry>")
                continue
            resolved = _screenshot_path(item.get("path"), qa_summary_path)
            if resolved is None or not resolved.exists():
                missing_screenshots.append(str(item.get("path")))
        if missing_screenshots:
            errors.append(f"screenshot files missing: {missing_screenshots}")
        evidence["screenshot_count"] = len(screenshots)

    for section_name in ("apiChecks", "uiChecks", "calculationChecks"):
        section = live_summary.get(section_name, [])
        if not isinstance(section, list) or not section:
            errors.append(f"live summary {section_name} must be non-empty")
        else:
            evidence[f"{section_name}_count"] = len(section)

    panel_classifications = live_summary.get("panelClassifications", [])
    if not isinstance(panel_classifications, list) or not panel_classifications:
        errors.append("live summary panelClassifications must be non-empty")
    else:
        unsupported_states = [
            f"{panel.get('panel')}={panel.get('state')}"
            for panel in panel_classifications
            if isinstance(panel, dict)
            and str(panel.get("state")) in {"supported_blank", "blank", "error"}
        ]
        if unsupported_states:
            errors.append(
                "live summary contains unsupported panel states: "
                f"{unsupported_states}"
            )
        evidence["panel_classification_count"] = len(panel_classifications)

    shot_index_path = _screenshot_index_path(
        live_summary, live_summary_path, qa_summary_path
    )
    if shot_index_path is None or not shot_index_path.exists():
        errors.append("SHOT-INDEX.md is missing for canonical screenshot evidence")
    else:
        evidence["shot_index_path"] = str(shot_index_path)

    return evidence


def _validate_metric_artifacts(
    *,
    errors: list[str],
    contract: dict[str, Any],
    dashboard: dict[str, Any],
    alert_rules: dict[str, Any],
) -> dict[str, Any]:
    implemented_metrics = _implemented_metric_names(contract)
    if not EXPECTED_METRIC_NAMES <= implemented_metrics:
        errors.append(
            "contract is missing implemented Workbench metric names: "
            f"{sorted(EXPECTED_METRIC_NAMES - implemented_metrics)}"
        )

    dashboard_metrics = _metrics_referenced_by_dashboard(dashboard)
    unimplemented_dashboard_metrics = sorted(dashboard_metrics - implemented_metrics)
    if unimplemented_dashboard_metrics:
        errors.append(
            "dashboard references unimplemented metrics: "
            f"{unimplemented_dashboard_metrics}"
        )

    alert_metrics = _metrics_referenced_by_alerts(alert_rules)
    unimplemented_alert_metrics = sorted(alert_metrics - implemented_metrics)
    if unimplemented_alert_metrics:
        errors.append(
            f"alert rules reference unimplemented metrics: {unimplemented_alert_metrics}"
        )

    return {
        "implemented_metrics": sorted(implemented_metrics),
        "dashboard_metrics": sorted(dashboard_metrics),
        "alert_metrics": sorted(alert_metrics),
    }


def _forbidden_terms(contract: dict[str, Any]) -> set[str]:
    base_terms = set(contract.get("forbidden_fields", []))
    base_terms.update(
        {
            "client_name",
            "client id",
            "household_id",
            "account_number",
            "holding_id",
            "transaction_id",
            "advisor_behavior",
            "screen_content",
            "request_body",
            "response_body",
            "raw_entitlement_failure",
            "CIF_",
        }
    )
    return {
        term
        for term in base_terms
        if term
        not in {
            # Canonical proof may record the synthetic portfolio identifier in
            # validation metadata, but the metric/dashboard/alert contract
            # still forbids it as a telemetry label or dashboard variable.
            "portfolio_id",
        }
    }


def _validate_sensitive_content(
    *,
    errors: list[str],
    contract: dict[str, Any],
    paths: list[Path],
) -> dict[str, Any]:
    forbidden_terms = _forbidden_terms(contract)
    findings: list[str] = []
    scanned_paths = 0
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        scanned_paths += 1
        text = path.read_text(encoding="utf-8", errors="ignore")
        lowered = text.lower()
        for term in forbidden_terms:
            if term.lower() in lowered:
                findings.append(f"{path}: contains forbidden term {term}")
    if findings:
        errors.extend(findings)
    return {"sensitive_content_scanned_files": scanned_paths}


def review_canonical_proof(inputs: ReviewInputs) -> dict[str, Any]:
    errors: list[str] = []
    qa_summary = _load_json(inputs.qa_summary_path)
    contract = _load_json(inputs.contract_path)
    dashboard = _load_json(inputs.dashboard_path)
    alert_rules = yaml.safe_load(inputs.alert_rules_path.read_text(encoding="utf-8"))

    status = str(qa_summary.get("status") or qa_summary.get("result") or "").lower()
    if status and status not in {"ok", "passed", "success"}:
        errors.append(f"canonical QA summary status is not ok: {status}")

    live_summary, live_summary_path = _resolve_live_summary(
        qa_summary, inputs.qa_summary_path
    )
    if live_summary is None:
        errors.append("canonical QA summary does not reference a live validation summary")
        live_evidence: dict[str, Any] = {}
    else:
        live_evidence = _validate_live_summary(
            errors=errors,
            live_summary=live_summary,
            live_summary_path=live_summary_path,
            qa_summary_path=inputs.qa_summary_path,
        )

    metric_evidence = _validate_metric_artifacts(
        errors=errors,
        contract=contract,
        dashboard=dashboard,
        alert_rules=alert_rules,
    )

    sensitive_scan_paths = [inputs.qa_summary_path]
    if live_summary_path is not None:
        sensitive_scan_paths.append(live_summary_path)
    shot_index = (
        _screenshot_index_path(live_summary, live_summary_path, inputs.qa_summary_path)
        if live_summary is not None
        else None
    )
    if shot_index is not None:
        sensitive_scan_paths.append(shot_index)
    sensitive_evidence = _validate_sensitive_content(
        errors=errors,
        contract=contract,
        paths=sensitive_scan_paths,
    )

    review = {
        "status": "passed" if not errors else "failed",
        "rfc": "RFC-0108",
        "slice": "Slice 8 canonical Workbench implementation proof",
        "qa_summary_path": str(inputs.qa_summary_path),
        "live_summary_path": str(live_summary_path) if live_summary_path else None,
        "evidence": {
            **live_evidence,
            **metric_evidence,
            **sensitive_evidence,
        },
        "errors": errors,
    }

    if inputs.output_path is not None:
        inputs.output_path.parent.mkdir(parents=True, exist_ok=True)
        inputs.output_path.write_text(f"{json.dumps(review, indent=2)}\n", encoding="utf-8")

    return review


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Review RFC-0108 canonical analytics UI proof evidence."
    )
    parser.add_argument("qa_summary", type=Path)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT_PATH)
    parser.add_argument("--dashboard", type=Path, default=DEFAULT_DASHBOARD_PATH)
    parser.add_argument("--alert-rules", type=Path, default=DEFAULT_ALERT_RULES_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_REVIEW_OUTPUT)
    args = parser.parse_args()

    review = review_canonical_proof(
        ReviewInputs(
            qa_summary_path=args.qa_summary,
            contract_path=args.contract,
            dashboard_path=args.dashboard,
            alert_rules_path=args.alert_rules,
            output_path=args.output,
        )
    )
    if review["errors"]:
        for error in review["errors"]:
            print(error)
        return 1
    print("RFC-0108 canonical analytics UI proof review passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
