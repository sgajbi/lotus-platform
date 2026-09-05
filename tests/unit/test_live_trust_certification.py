from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CERTIFIER_PATH = ROOT / "automation" / "generate_live_trust_certification.py"


def _load_certifier_module():
    automation_path = str(ROOT / "automation")
    if automation_path not in sys.path:
        sys.path.insert(0, automation_path)
    spec = importlib.util.spec_from_file_location(
        "generate_live_trust_certification_test", CERTIFIER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _snapshot(product_id: str = "lotus-performance:ReturnsSeriesBundle:v1") -> dict:
    producer, product_name, product_version = product_id.split(":")
    return {
        "contract_id": "lotus-domain-product-trust-telemetry-snapshot",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0087"],
        "emitted_at_utc": "2026-04-19T00:00:00Z",
        "product_id": product_id,
        "producer_repository": producer,
        "product_name": product_name,
        "product_version": product_version,
        "source_repository": producer,
        "freshness": {
            "freshness_class": "daily",
            "freshness_state": "current",
            "evaluated_at_utc": "2026-04-19T00:00:00Z",
            "age_seconds": 60,
            "max_allowed_age_seconds": 86400,
        },
        "completeness_status": "complete",
        "reconciliation_status": "not_applicable",
        "data_quality_status": "quality_passed",
        "lineage": {
            "lineage_materialized": True,
            "evidence_access_class": "customer_consumable",
        },
        "blocking": {"blocked": False},
        "observed_trust_metadata": {
            "product_name": product_name,
            "product_version": product_version,
            "generated_at": "2026-04-19T00:00:00Z",
            "as_of_date": "2026-04-19",
            "correlation_id": "corr-001",
        },
        "evidence": {
            "correlation_id": "corr-001",
            "validation_lanes": ["feature", "pr-merge"],
        },
    }


def test_live_trust_certification_certifies_current_snapshot(tmp_path: Path) -> None:
    certifier = _load_certifier_module()
    snapshot_path = tmp_path / "returns-series.json"
    snapshot_path.write_text(json.dumps(_snapshot()), encoding="utf-8")

    report = certifier.build_live_trust_certification_report(
        snapshot_path,
        generated_at_utc="2026-04-19T00:00:00Z",
    )

    assert report["contract_id"] == "lotus-domain-product-live-trust-certification"
    assert report["summary"]["certification_state"] == "certified"
    assert report["summary"]["telemetry_snapshot_count"] == 1
    assert report["summary"]["certified_snapshot_count"] == 1
    assert report["summary"]["issue_count"] == 0
    assert report["product_certifications"][0]["product_id"] == (
        "lotus-performance:ReturnsSeriesBundle:v1"
    )


def test_live_trust_certification_flags_stale_blocked_and_invalid_snapshot(
    tmp_path: Path,
) -> None:
    certifier = _load_certifier_module()
    snapshot = _snapshot()
    snapshot["freshness"]["freshness_state"] = "stale"
    snapshot["completeness_status"] = "stale"
    snapshot["data_quality_status"] = "quality_failed"
    snapshot["lineage"]["lineage_materialized"] = False
    snapshot["blocking"] = {"blocked": True, "blocked_reason": "upstream_break_open"}
    snapshot["observed_trust_metadata"]["unsupported_field"] = "bad"
    snapshot_path = tmp_path / "blocked.json"
    snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")

    report = certifier.build_live_trust_certification_report(
        snapshot_path,
        generated_at_utc="2026-04-19T00:00:00Z",
    )

    issue_codes = {issue["code"] for issue in report["issues"]}
    assert report["summary"]["certification_state"] == "attention_required"
    assert report["summary"]["attention_required_count"] == 1
    assert "invalid_trust_telemetry" in issue_codes
    assert "freshness_not_current" in issue_codes
    assert "completeness_attention_required" in issue_codes
    assert "data_quality_attention_required" in issue_codes
    assert "lineage_not_materialized" in issue_codes
    assert "product_blocked" in issue_codes


def test_live_trust_certification_rejects_missing_required_metadata(
    tmp_path: Path,
) -> None:
    certifier = _load_certifier_module()
    snapshot = _snapshot()
    snapshot["observed_trust_metadata"] = {}
    snapshot_path = tmp_path / "missing-required-metadata.json"
    snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")

    report = certifier.build_live_trust_certification_report(
        snapshot_path,
        generated_at_utc="2026-04-19T00:00:00Z",
    )

    assert report["summary"]["certification_state"] == "attention_required"
    assert report["summary"]["certified_snapshot_count"] == 0
    assert report["summary"]["issue_count"] == 5
    assert all(
        issue["code"] == "invalid_trust_telemetry"
        and "missing required product field" in issue["detail"]
        for issue in report["issues"]
    )


def test_live_trust_certification_writes_json_and_markdown(tmp_path: Path) -> None:
    certifier = _load_certifier_module()
    telemetry_dir = tmp_path / "telemetry"
    output_dir = tmp_path / "certification"
    telemetry_dir.mkdir()
    (telemetry_dir / "returns-series.json").write_text(
        json.dumps(_snapshot()),
        encoding="utf-8",
    )

    certifier.write_live_trust_certification_report(
        telemetry_dir,
        output_dir,
        generated_at_utc="2026-04-19T00:00:00Z",
    )

    report = json.loads(
        (output_dir / "domain-product-live-trust-certification.json").read_text(
            encoding="utf-8"
        )
    )
    markdown = (output_dir / "domain-product-live-trust-certification.md").read_text(
        encoding="utf-8"
    )

    assert report["summary"]["certification_state"] == "certified"
    assert "# Lotus Domain Product Live Trust Certification" in markdown
    assert "| `ReturnsSeriesBundle` | `lotus-performance` | `certified` |" in markdown
