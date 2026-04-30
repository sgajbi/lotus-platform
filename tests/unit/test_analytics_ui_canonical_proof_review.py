from __future__ import annotations

import copy
import json
from pathlib import Path

import yaml

from automation.review_analytics_ui_canonical_proof import (
    CANONICAL_BENCHMARK_CODE,
    CANONICAL_PORTFOLIO_ID,
    EXPECTED_SCREENSHOT_COUNT,
    ReviewInputs,
    review_canonical_proof,
)


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


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(f"{json.dumps(payload, indent=2)}\n", encoding="utf-8")


def _copy_contract_artifacts(tmp_path: Path) -> tuple[Path, Path, Path]:
    contract_path = tmp_path / "contract.json"
    dashboard_path = tmp_path / "dashboard.json"
    alert_rules_path = tmp_path / "rules.yml"
    contract_path.write_text(CONTRACT_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    dashboard_path.write_text(
        DASHBOARD_PATH.read_text(encoding="utf-8"), encoding="utf-8"
    )
    alert_rules_path.write_text(
        ALERT_RULES_PATH.read_text(encoding="utf-8"), encoding="utf-8"
    )
    return contract_path, dashboard_path, alert_rules_path


def _write_valid_evidence(tmp_path: Path) -> tuple[Path, Path]:
    evidence_dir = tmp_path / "canonical"
    evidence_dir.mkdir()
    screenshots = []
    for index in range(EXPECTED_SCREENSHOT_COUNT):
        screenshot_path = evidence_dir / f"shot-{index}.png"
        screenshot_path.write_bytes(b"synthetic screenshot")
        screenshots.append(
            {
                "name": screenshot_path.name,
                "path": str(screenshot_path),
                "route": "/performance",
                "panel": f"panel.{index}",
                "state": "demo_ready",
            }
        )

    live_summary_path = evidence_dir / "live-validation-summary.json"
    live_summary = {
        "generatedAt": "2026-04-29T00:00:00Z",
        "portfolioId": CANONICAL_PORTFOLIO_ID,
        "benchmarkCode": CANONICAL_BENCHMARK_CODE,
        "apiChecks": [{"description": "Gateway performance summary", "ok": True}],
        "uiChecks": [{"description": "Performance route", "kind": "table"}],
        "calculationChecks": [{"description": "Return sanity", "ok": True}],
        "panelClassifications": [
            {"panel": "portfolio.summary", "state": "ready", "owner": "lotus-gateway"}
        ],
        "screenshots": screenshots,
    }
    _write_json(live_summary_path, live_summary)

    shot_index_path = evidence_dir / "SHOT-INDEX.md"
    shot_index_path.write_text(
        "# Lotus Canonical Front-Office Screenshots\n\n"
        f"- Portfolio: {CANONICAL_PORTFOLIO_ID}\n"
        f"- Benchmark: {CANONICAL_BENCHMARK_CODE}\n",
        encoding="utf-8",
    )

    qa_summary_path = tmp_path / "qa-summary.json"
    _write_json(
        qa_summary_path,
        {
            "status": "ok",
            "governed_live_summary_path": str(live_summary_path),
        },
    )
    return qa_summary_path, live_summary_path


def _review(tmp_path: Path) -> tuple[dict, Path, Path, Path, Path, Path]:
    qa_summary_path, live_summary_path = _write_valid_evidence(tmp_path)
    contract_path, dashboard_path, alert_rules_path = _copy_contract_artifacts(tmp_path)
    review = review_canonical_proof(
        ReviewInputs(
            qa_summary_path=qa_summary_path,
            contract_path=contract_path,
            dashboard_path=dashboard_path,
            alert_rules_path=alert_rules_path,
            output_path=None,
        )
    )
    return (
        review,
        qa_summary_path,
        live_summary_path,
        contract_path,
        dashboard_path,
        alert_rules_path,
    )


def test_canonical_proof_review_accepts_complete_evidence(tmp_path: Path) -> None:
    review, *_ = _review(tmp_path)

    assert review["status"] == "passed"
    assert review["errors"] == []
    assert review["evidence"]["screenshot_count"] == EXPECTED_SCREENSHOT_COUNT
    assert "lotus_workbench_panel_state_total" in review["evidence"]["dashboard_metrics"]


def test_canonical_proof_review_rejects_failed_qa_summary(tmp_path: Path) -> None:
    (
        _review_result,
        qa_summary_path,
        _live_summary_path,
        contract_path,
        dashboard_path,
        alert_rules_path,
    ) = _review(tmp_path)
    qa_summary = json.loads(qa_summary_path.read_text(encoding="utf-8"))
    qa_summary["status"] = "failed"
    _write_json(qa_summary_path, qa_summary)

    review = review_canonical_proof(
        ReviewInputs(
            qa_summary_path=qa_summary_path,
            contract_path=contract_path,
            dashboard_path=dashboard_path,
            alert_rules_path=alert_rules_path,
            output_path=None,
        )
    )

    assert review["status"] == "failed"
    assert any("status is not ok" in error for error in review["errors"])


def test_canonical_proof_review_rejects_sensitive_content(tmp_path: Path) -> None:
    (
        _review_result,
        qa_summary_path,
        live_summary_path,
        contract_path,
        dashboard_path,
        alert_rules_path,
    ) = _review(tmp_path)
    live_summary = json.loads(live_summary_path.read_text(encoding="utf-8"))
    live_summary["uiChecks"].append({"description": "client_name leaked"})
    _write_json(live_summary_path, live_summary)

    review = review_canonical_proof(
        ReviewInputs(
            qa_summary_path=qa_summary_path,
            contract_path=contract_path,
            dashboard_path=dashboard_path,
            alert_rules_path=alert_rules_path,
            output_path=None,
        )
    )

    assert review["status"] == "failed"
    assert any("client_name" in error for error in review["errors"])


def test_canonical_proof_review_rejects_dashboard_metric_drift(tmp_path: Path) -> None:
    (
        _review_result,
        qa_summary_path,
        _live_summary_path,
        contract_path,
        dashboard_path,
        alert_rules_path,
    ) = _review(tmp_path)
    dashboard = json.loads(dashboard_path.read_text(encoding="utf-8"))
    drifted_dashboard = copy.deepcopy(dashboard)
    drifted_dashboard["panels"][0]["targets"][0]["expr"] = (
        "sum(rate(lotus_unimplemented_metric_total[5m]))"
    )
    _write_json(dashboard_path, drifted_dashboard)

    review = review_canonical_proof(
        ReviewInputs(
            qa_summary_path=qa_summary_path,
            contract_path=contract_path,
            dashboard_path=dashboard_path,
            alert_rules_path=alert_rules_path,
            output_path=None,
        )
    )

    assert review["status"] == "failed"
    assert any(
        "dashboard references unimplemented metrics" in error
        for error in review["errors"]
    )


def test_canonical_proof_review_rejects_unimplemented_alert_metric(
    tmp_path: Path,
) -> None:
    (
        _review_result,
        qa_summary_path,
        _live_summary_path,
        contract_path,
        dashboard_path,
        alert_rules_path,
    ) = _review(tmp_path)
    alert_rules = yaml.safe_load(alert_rules_path.read_text(encoding="utf-8"))
    alert_rules["groups"][0]["rules"][0]["expr"] = (
        "sum(lotus_unimplemented_metric_total) > 0"
    )
    alert_rules_path.write_text(yaml.safe_dump(alert_rules), encoding="utf-8")

    review = review_canonical_proof(
        ReviewInputs(
            qa_summary_path=qa_summary_path,
            contract_path=contract_path,
            dashboard_path=dashboard_path,
            alert_rules_path=alert_rules_path,
            output_path=None,
        )
    )

    assert review["status"] == "failed"
    assert any(
        "alert rules reference unimplemented metrics" in error
        for error in review["errors"]
    )
