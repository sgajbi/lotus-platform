from __future__ import annotations

import json
import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
REPORT_REPO = ROOT.parent / "lotus-report"
RENDER_REPO = ROOT.parent / "lotus-render"
ARCHIVE_REPO = ROOT.parent / "lotus-archive"
DASHBOARD_PATH = (
    ROOT / "platform-stack" / "grafana" / "dashboards" / "reporting-observability-overview.json"
)
# Resolved at import time, so an absent sibling checkout must skip rather than
# raise: a bare next() over an empty generator raises StopIteration during
# collection, and pytest treats a collection error as fatal for the whole run.
# One optional sibling missing then hides all of tests/unit, which is what a
# fresh clone looks like before any sibling is checked out.
RENDER_METRICS_PATH = next(
    (
        path
        for path in (
            RENDER_REPO / "src" / "app" / "observability" / "render_metrics.py",
            RENDER_REPO / "src" / "app" / "render_metrics.py",
        )
        if path.exists()
    ),
    None,
)

if RENDER_METRICS_PATH is None:
    pytest.skip(
        "lotus-render is not checked out beside lotus-platform; this cross-repo "
        "metric contract is verified where both checkouts are present.",
        allow_module_level=True,
    )


def _load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def _extract_metric_names(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    return set(re.findall(r'"(lotus_[a-z0-9_]+)"', text))


def _extract_metric_contract_labels(path: Path) -> dict[str, list[str]]:
    text = path.read_text(encoding="utf-8")
    label_constants = {
        name: value
        for name, value in re.findall(r'^(METRIC_[A-Z_]+)\s*=\s*"([^"]+)"', text, re.MULTILINE)
    }
    contract_labels: dict[str, list[str]] = {}
    for match in re.finditer(
        r'name="(?P<name>lotus_[a-z0-9_]+)".*?labels=\((?P<labels>[^)]*)\)',
        text,
        re.DOTALL,
    ):
        raw_labels = [label.strip() for label in match.group("labels").split(",") if label.strip()]
        contract_labels[match.group("name")] = [label_constants.get(label, label) for label in raw_labels]
    return contract_labels


def _normalize_prometheus_metric_name(metric_name: str) -> str:
    for suffix in ("_bucket", "_sum", "_count", "_created"):
        if metric_name.endswith(suffix):
            return metric_name[: -len(suffix)]
    return metric_name


def test_reporting_observability_contract_artifacts_are_present_and_governed() -> None:
    readme = (ROOT / "context" / "contracts" / "README.md").read_text(encoding="utf-8")
    schema = _load_json(
        "context/contracts/reporting-observability-contract.schema.json"
    )
    contract = _load_json("context/contracts/reporting-observability-contract.json")

    assert "reporting-observability-contract.schema.json" in readme
    assert "reporting-observability-contract.json" in readme

    assert (
        schema["properties"]["contract_id"]["const"]
        == "reporting-observability-contract"
    )
    assert schema["properties"]["governed_by_rfc"]["const"] == "RFC-0105"

    assert contract["contract_id"] == "reporting-observability-contract"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governed_by_rfc"] == "RFC-0105"


def test_reporting_observability_contract_references_only_implemented_metrics() -> None:
    contract = _load_json("context/contracts/reporting-observability-contract.json")

    report_metrics = _extract_metric_names(
        REPORT_REPO / "src" / "app" / "reporting_metrics.py"
    )
    render_metrics = _extract_metric_names(RENDER_METRICS_PATH)
    archive_metrics = _extract_metric_names(
        ARCHIVE_REPO / "src" / "app" / "archive" / "metrics.py"
    )
    implemented_metrics = report_metrics | render_metrics | archive_metrics

    catalog_names = {
        entry["metric_name"]
        for entry in contract["metrics_catalog"]
        if entry["implemented"]
    }
    assert catalog_names <= implemented_metrics

    dashboard_metric_names = {
        metric_name
        for dashboard in contract["dashboards"]
        for metric_name in dashboard["metric_names"]
    }
    assert dashboard_metric_names <= catalog_names

    alert_metric_names = {alert["metric_name"] for alert in contract["alerts"]}
    assert alert_metric_names <= catalog_names

    for entry in contract["metrics_catalog"]:
        assert entry["metric_type"] in {"counter", "gauge", "histogram"}
        assert entry["cardinality_policy"] == "bounded-enum-only"


def test_reporting_observability_contract_labels_match_service_metric_contracts() -> None:
    contract = _load_json("context/contracts/reporting-observability-contract.json")
    expected_labels = {
        **_extract_metric_contract_labels(REPORT_REPO / "src" / "app" / "reporting_metrics.py"),
        **_extract_metric_contract_labels(RENDER_METRICS_PATH),
        **_extract_metric_contract_labels(ARCHIVE_REPO / "src" / "app" / "archive" / "metrics.py"),
    }

    for entry in contract["metrics_catalog"]:
        assert entry["labels"] == expected_labels[entry["metric_name"]]


def test_reporting_observability_metric_sources_reject_sensitive_labels() -> None:
    required_forbidden_labels = {
        "portfolio_id",
        "tenant_id",
        "trace_id",
        "correlation_id",
        "report_job_id",
    }
    for source in (
        REPORT_REPO / "src" / "app" / "reporting_metrics.py",
        RENDER_METRICS_PATH,
        ARCHIVE_REPO / "src" / "app" / "archive" / "metrics.py",
    ):
        text = source.read_text(encoding="utf-8")
        assert "FORBIDDEN_METRIC_LABELS" in text
        for forbidden_label in required_forbidden_labels:
            assert f'"{forbidden_label}"' in text


def test_reporting_observability_alerts_have_owner_severity_and_runbook_links() -> None:
    contract = _load_json("context/contracts/reporting-observability-contract.json")
    runbook = ROOT / "docs" / "operations" / "reporting-observability-runbook.md"
    runbook_text = runbook.read_text(encoding="utf-8")

    assert runbook.exists()
    assert len(contract["alerts"]) >= 5

    for alert in contract["alerts"]:
        assert alert["severity"] in {"P1", "P2", "P3"}
        assert alert["owner_repo"] in {"lotus-report", "lotus-render", "lotus-archive"}
        assert alert["runbook_path"].startswith(
            "docs/operations/reporting-observability-runbook.md#"
        )
        anchor = alert["runbook_path"].split("#", 1)[1].replace("-", " ")
        assert anchor in runbook_text.lower()


def test_reporting_observability_sla_objectives_have_explicit_owners_and_metrics() -> None:
    contract = _load_json("context/contracts/reporting-observability-contract.json")
    runbook_text = (
        ROOT / "docs" / "operations" / "reporting-observability-runbook.md"
    ).read_text(encoding="utf-8")
    catalog_names = {entry["metric_name"] for entry in contract["metrics_catalog"]}

    assert len(contract["sla_objectives"]) >= 5

    for objective in contract["sla_objectives"]:
        assert objective["metric_name"] in catalog_names
        assert objective["owner_repo"] in {
            "lotus-report",
            "lotus-render",
            "lotus-archive",
        }
        assert objective["escalation_owner_role"] in {
            "reporting-service-owner",
            "render-service-owner",
            "archive-service-owner",
        }
        assert objective["measurement_window"] == "15m rolling"
        assert objective["runbook_path"].startswith(
            "docs/operations/reporting-observability-runbook.md#"
        )
        anchor = objective["runbook_path"].split("#", 1)[1].replace("-", " ")
        assert anchor in runbook_text.lower()


def test_reporting_observability_contract_records_slice8_deferred_families_truthfully() -> (
    None
):
    contract = _load_json("context/contracts/reporting-observability-contract.json")
    deferred = {entry["alert_family"]: entry for entry in contract["deferred_alerts"]}

    assert deferred["stuck_jobs"]["deferred_to_slice"] == "Slice 8"
    assert deferred["sla_breaches"]["deferred_to_slice"] == "Slice 8"


def test_reporting_observability_dashboard_references_only_contract_metrics() -> None:
    contract = _load_json("context/contracts/reporting-observability-contract.json")
    dashboard = json.loads(DASHBOARD_PATH.read_text(encoding="utf-8"))

    contract_metric_names = {entry["metric_name"] for entry in contract["metrics_catalog"]}
    dashboard_metric_names = {
        _normalize_prometheus_metric_name(metric_name)
        for metric_name in re.findall(r"lotus_[a-z0-9_]+", json.dumps(dashboard, sort_keys=True))
    }

    assert dashboard["uid"] == "reporting-observability-overview"
    assert dashboard["title"] == "Reporting Observability Overview"
    assert len(dashboard["panels"]) >= 5
    assert dashboard_metric_names <= contract_metric_names
