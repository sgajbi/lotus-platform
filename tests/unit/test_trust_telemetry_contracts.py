from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "automation" / "validate_trust_telemetry.py"
SCHEMA_PATH = (
    ROOT
    / "platform-contracts"
    / "trust-telemetry"
    / "trust-telemetry-snapshot.schema.json"
)


def _load_validator_module():
    automation_path = str(ROOT / "automation")
    if automation_path not in sys.path:
        sys.path.insert(0, automation_path)
    spec = importlib.util.spec_from_file_location(
        "validate_trust_telemetry_test", VALIDATOR_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _valid_snapshot() -> dict:
    return {
        "contract_id": "lotus-domain-product-trust-telemetry-snapshot",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0087"],
        "emitted_at_utc": "2026-04-19T00:00:00Z",
        "product_id": "lotus-performance:ReturnsSeriesBundle:v1",
        "producer_repository": "lotus-performance",
        "product_name": "ReturnsSeriesBundle",
        "product_version": "v1",
        "source_repository": "lotus-performance",
        "freshness": {
            "freshness_class": "daily",
            "freshness_state": "current",
            "evaluated_at_utc": "2026-04-19T00:00:00Z",
            "observed_at_utc": "2026-04-19T00:00:00Z",
            "age_seconds": 60,
            "max_allowed_age_seconds": 86400,
        },
        "completeness_status": "complete",
        "reconciliation_status": "not_applicable",
        "data_quality_status": "quality_passed",
        "lineage": {
            "lineage_materialized": True,
            "evidence_access_class": "customer_consumable",
            "lineage_bundle_id": "returns-series-20260419",
            "evidence_uris": ["artifact://returns-series/20260419"],
        },
        "blocking": {"blocked": False},
        "observed_trust_metadata": {
            "product_name": "ReturnsSeriesBundle",
            "product_version": "v1",
            "generated_at": "2026-04-19T00:00:00Z",
            "as_of_date": "2026-04-19",
            "correlation_id": "corr-001",
        },
        "evidence": {
            "correlation_id": "corr-001",
            "validation_lanes": ["feature", "pr-merge"],
            "source_artifact_uri": "artifact://returns-series/20260419",
        },
    }


def test_trust_telemetry_schema_is_governed_and_specific() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    assert schema["title"] == "Lotus Domain Product Trust Telemetry Snapshot"
    assert schema["properties"]["contract_id"]["const"] == (
        "lotus-domain-product-trust-telemetry-snapshot"
    )
    assert "RFC-0087" == schema["properties"]["governed_by_rfcs"]["contains"]["const"]
    assert "freshness" in schema["required"]
    assert "observed_trust_metadata" in schema["required"]
    assert "evidence" in schema["required"]


def test_valid_trust_telemetry_snapshot_references_catalog_and_vocabulary(
    tmp_path: Path,
) -> None:
    validator = _load_validator_module()
    snapshot_path = tmp_path / "returns-series-telemetry.json"
    snapshot_path.write_text(json.dumps(_valid_snapshot()), encoding="utf-8")

    assert validator.validate_trust_telemetry_path(snapshot_path) == []


def test_trust_telemetry_rejects_unknown_product_and_wrong_identity(
    tmp_path: Path,
) -> None:
    validator = _load_validator_module()
    snapshot = _valid_snapshot()
    snapshot["product_id"] = "lotus-performance:MissingProduct:v1"
    snapshot["product_name"] = "WrongName"
    snapshot_path = tmp_path / "bad-identity.json"
    snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")

    issues = validator.validate_trust_telemetry_path(snapshot_path)

    assert any("product_id does not exist in catalog" in issue for issue in issues)


def test_trust_telemetry_rejects_ungoverned_statuses_and_metadata(
    tmp_path: Path,
) -> None:
    validator = _load_validator_module()
    snapshot = _valid_snapshot()
    snapshot["freshness"]["freshness_class"] = "hourly"
    snapshot["freshness"]["freshness_state"] = "current"
    snapshot["freshness"]["age_seconds"] = 90000
    snapshot["freshness"]["max_allowed_age_seconds"] = 10
    snapshot["completeness_status"] = "mostly_complete"
    snapshot["reconciliation_status"] = "maybe"
    snapshot["data_quality_status"] = "great"
    snapshot["observed_trust_metadata"]["unsupported_field"] = "not-governed"
    snapshot["evidence"]["validation_lanes"] = ["feature", "nightly"]
    snapshot_path = tmp_path / "bad-statuses.json"
    snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")

    issues = validator.validate_trust_telemetry_path(snapshot_path)

    assert any("freshness.freshness_class" in issue for issue in issues)
    assert any("current conflicts with age_seconds" in issue for issue in issues)
    assert any("completeness_status" in issue for issue in issues)
    assert any("reconciliation_status" in issue for issue in issues)
    assert any("data_quality_status" in issue for issue in issues)
    assert any("unsupported_field" in issue for issue in issues)
    assert any("unsupported lanes: nightly" in issue for issue in issues)


def test_trust_telemetry_rejects_boolean_freshness_age_fields(
    tmp_path: Path,
) -> None:
    validator = _load_validator_module()
    snapshot = _valid_snapshot()
    snapshot["freshness"]["age_seconds"] = True
    snapshot["freshness"]["max_allowed_age_seconds"] = False
    snapshot_path = tmp_path / "boolean-freshness-age.json"
    snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")

    issues = validator.validate_trust_telemetry_path(snapshot_path)

    assert any("freshness.age_seconds must be >= 0" in issue for issue in issues)
    assert any(
        "freshness.max_allowed_age_seconds must be >= 1" in issue
        for issue in issues
    )


def test_trust_telemetry_requires_blocked_reason_when_blocked(
    tmp_path: Path,
) -> None:
    validator = _load_validator_module()
    snapshot = _valid_snapshot()
    snapshot["blocking"] = {"blocked": True}
    snapshot_path = tmp_path / "blocked-without-reason.json"
    snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")

    issues = validator.validate_trust_telemetry_path(snapshot_path)

    assert any("blocking.blocked_reason is required" in issue for issue in issues)


def test_trust_telemetry_rejects_malformed_lineage_fields(tmp_path: Path) -> None:
    validator = _load_validator_module()
    snapshot = _valid_snapshot()
    snapshot["lineage"] = {
        "lineage_materialized": "yes",
        "evidence_access_class": "private",
        "evidence_uris": "artifact://returns-series/20260419",
    }
    snapshot_path = tmp_path / "malformed-lineage.json"
    snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")

    issues = validator.validate_trust_telemetry_path(snapshot_path)

    assert any("lineage.lineage_materialized must be boolean" in issue for issue in issues)
    assert any("lineage.evidence_access_class" in issue for issue in issues)
    assert any("lineage.evidence_uris must be an array" in issue for issue in issues)
