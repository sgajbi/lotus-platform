from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATOR_PATH = ROOT / "automation" / "generate_enterprise_mesh_operating_report.py"
GENERATED_AT_UTC = "2026-04-20T00:00:00Z"


def _load_generator_module():
    automation_path = str(ROOT / "automation")
    if automation_path not in sys.path:
        sys.path.insert(0, automation_path)
    spec = importlib.util.spec_from_file_location(
        "generate_enterprise_mesh_operating_report_test", GENERATOR_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _mesh_status(*, state: str = "certified", issue: dict | None = None) -> dict:
    issue_count = 1 if issue else 0
    return {
        "contract_id": "lotus-mesh-certification-status",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0089", "RFC-0091"],
        "generated_at_utc": GENERATED_AT_UTC,
        "gate_mode": "blocking",
        "certification_state": state,
        "required_products": [
            {
                "product_id": "lotus-core:PortfolioStateSnapshot:v1",
                "producer_repository": "lotus-core",
                "certification_state": "certified"
                if not issue
                else "attention_required",
                "freshness_state": "current",
                "completeness_status": "complete",
                "reconciliation_status": "reconciled",
                "data_quality_status": "quality_passed",
                "issue_count": issue_count,
            }
        ],
        "summary": {
            "required_product_count": 1,
            "certified_required_product_count": 0 if issue else 1,
            "attention_required_product_count": issue_count,
            "issue_count": issue_count,
            "error_count": 1 if issue and issue["severity"] == "error" else 0,
            "warning_count": 1 if issue and issue["severity"] == "warning" else 0,
            "info_count": 0,
        },
        "issues": [issue] if issue else [],
        "source_artifacts": {},
        "live_trust_certification": {"product_certifications": []},
    }


def _history_record(*, generated_at_utc: str, state: str) -> dict:
    return {
        "contract_id": "lotus-mesh-certification-history-record",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0091"],
        "pack_id": generated_at_utc,
        "generated_at_utc": generated_at_utc,
        "certification_state": state,
        "gate_mode": "blocking",
        "summary": {
            "required_product_count": 1,
            "certified_required_product_count": 1 if state == "certified" else 0,
            "attention_required_product_count": 0 if state == "certified" else 1,
            "error_count": 0 if state == "certified" else 1,
            "warning_count": 0,
        },
        "product_history": [
            {
                "product_id": "lotus-core:PortfolioStateSnapshot:v1",
                "producer_repository": "lotus-core",
                "certification_state": state,
                "issue_count": 0 if state == "certified" else 1,
            }
        ],
    }


def test_operating_report_marks_clean_current_state_with_limited_history() -> None:
    generator = _load_generator_module()

    report = generator.build_enterprise_mesh_operating_report(
        current_status=_mesh_status(),
        history_records=[],
        generated_at_utc=GENERATED_AT_UTC,
        source_status_path=Path("output/mesh-certification/status.json"),
        history_directory=Path("output/history"),
    )

    assert report["contract_id"] == "lotus-enterprise-mesh-operating-report"
    assert report["governed_by_rfcs"] == ["RFC-0092"]
    assert report["operating_state"] == "production_ready_limited_history"
    assert report["drift_trend"]["history_record_count"] == 0
    assert report["escalation_queue"] == []
    assert report["product_operating_posture"][0]["operating_state"] == "healthy"


def test_operating_report_detects_regression_and_escalation_owner() -> None:
    generator = _load_generator_module()
    issue = {
        "severity": "error",
        "code": "stale_telemetry",
        "producer_repository": "lotus-core",
        "product_id": "lotus-core:PortfolioStateSnapshot:v1",
        "remediation": "Refresh the producer telemetry snapshot.",
        "source_evidence_path": "lotus-core/contracts/trust-telemetry/example.json",
    }

    report = generator.build_enterprise_mesh_operating_report(
        current_status=_mesh_status(state="failed", issue=issue),
        history_records=[
            _history_record(generated_at_utc="2026-04-18T00:00:00Z", state="certified")
        ],
        generated_at_utc=GENERATED_AT_UTC,
        source_status_path=Path("output/mesh-certification/status.json"),
        history_directory=Path("output/history"),
    )

    assert report["operating_state"] == "blocked"
    assert report["drift_trend"]["regression_since_previous"] is True
    assert report["escalation_queue"] == [
        {
            "severity": "error",
            "family": "telemetry",
            "code": "stale_telemetry",
            "owner_repository": "lotus-core",
            "product_id": "lotus-core:PortfolioStateSnapshot:v1",
            "remediation": "Refresh the producer telemetry snapshot.",
            "source_evidence_path": "lotus-core/contracts/trust-telemetry/example.json",
        }
    ]
    assert "lotus-core" in report["operator_guidance"][0]


def test_operating_report_counts_history_and_writes_artifacts(tmp_path: Path) -> None:
    generator = _load_generator_module()
    status_path = tmp_path / "enterprise-mesh-certification-status.json"
    history_directory = tmp_path / "history"
    output_directory = tmp_path / "out"
    history_directory.mkdir()
    status_path.write_text(json.dumps(_mesh_status()), encoding="utf-8")
    for index in range(2):
        (history_directory / f"history-{index}.json").write_text(
            json.dumps(
                _history_record(
                    generated_at_utc=f"2026-04-1{index}T00:00:00Z",
                    state="certified",
                )
            ),
            encoding="utf-8",
        )

    report = generator.build_report_from_paths(
        mesh_status_path=status_path,
        history_directory=history_directory,
        generated_at_utc=GENERATED_AT_UTC,
    )
    generator.write_enterprise_mesh_operating_report(
        report,
        output_directory=output_directory,
    )

    assert report["operating_state"] == "production_ready"
    assert report["drift_trend"]["history_record_count"] == 2
    assert report["drift_trend"]["consecutive_certified_runs"] == 2
    assert (
        output_directory / "enterprise-mesh-operating-report.json"
    ).exists()
    markdown = (
        output_directory / "enterprise-mesh-operating-report.md"
    ).read_text(encoding="utf-8")
    assert "# Lotus Enterprise Mesh Operating Report" in markdown
    assert "## Escalation Queue" in markdown
