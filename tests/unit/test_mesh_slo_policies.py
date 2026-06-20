from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "automation" / "validate_mesh_slo_policies.py"
POLICY_DIRECTORY = ROOT / "platform-contracts" / "mesh-slo"


def _load_validator_module():
    automation_path = str(ROOT / "automation")
    if automation_path not in sys.path:
        sys.path.insert(0, automation_path)
    spec = importlib.util.spec_from_file_location(
        "validate_mesh_slo_policies_test", VALIDATOR_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_checked_in_mesh_slo_policies_are_valid() -> None:
    validator = _load_validator_module()

    assert validator.validate_mesh_slo_policies(POLICY_DIRECTORY) == []


def test_mesh_slo_policy_validation_rejects_missing_required_product(
    tmp_path: Path,
) -> None:
    validator = _load_validator_module()
    for policy_path in POLICY_DIRECTORY.glob("*.slo.v1.json"):
        if "lotus-risk" not in policy_path.name:
            (tmp_path / policy_path.name).write_text(
                policy_path.read_text(encoding="utf-8"),
                encoding="utf-8",
            )

    issues = validator.validate_mesh_slo_policies(tmp_path)

    assert issues == [
        f"{tmp_path}: missing required mesh SLO policy for lotus-risk product lotus-risk:RiskMetricsReport:v1"
    ]


def test_mesh_slo_evaluator_reports_status_and_lineage_violations(
    tmp_path: Path,
) -> None:
    validator = _load_validator_module()
    policy = json.loads(
        (
            POLICY_DIRECTORY / "lotus-risk-risk-metrics-report.slo.v1.json"
        ).read_text(encoding="utf-8")
    )
    telemetry_path = tmp_path / "risk-telemetry.json"
    telemetry = {
        "product_id": "lotus-risk:RiskMetricsReport:v1",
        "freshness": {"age_seconds": 60},
        "completeness_status": "stale",
        "reconciliation_status": "unreconciled",
        "data_quality_status": "quality_failed",
        "lineage": {"lineage_materialized": False},
    }
    telemetry_path.write_text(json.dumps(telemetry), encoding="utf-8")

    violations = validator.evaluate_mesh_slo_violations(
        telemetry_payloads={
            "lotus-risk:RiskMetricsReport:v1": (telemetry_path, telemetry)
        },
        policies={
            "lotus-risk:RiskMetricsReport:v1": (
                POLICY_DIRECTORY / "lotus-risk-risk-metrics-report.slo.v1.json",
                policy,
            )
        },
    )

    assert {violation["code"] for violation in violations} == {
        "mesh_slo_completeness_violation",
        "mesh_slo_reconciliation_violation",
        "mesh_slo_data_quality_violation",
        "mesh_slo_lineage_violation",
    }
    assert all(violation["severity"] == "blocking" for violation in violations)


def test_mesh_slo_evaluator_reports_freshness_violation(tmp_path: Path) -> None:
    validator = _load_validator_module()
    policy_path = POLICY_DIRECTORY / "lotus-risk-risk-metrics-report.slo.v1.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    telemetry_path = tmp_path / "risk-telemetry.json"
    telemetry = {
        "product_id": "lotus-risk:RiskMetricsReport:v1",
        "freshness": {"age_seconds": 999999},
        "completeness_status": policy["completeness"]["required_status"],
        "reconciliation_status": policy["reconciliation"]["required_status"],
        "data_quality_status": policy["data_quality"]["required_status"],
        "lineage": {"lineage_materialized": True},
    }

    violations = validator.evaluate_mesh_slo_violations(
        telemetry_payloads={
            "lotus-risk:RiskMetricsReport:v1": (telemetry_path, telemetry)
        },
        policies={"lotus-risk:RiskMetricsReport:v1": (policy_path, policy)},
    )

    assert [violation["code"] for violation in violations] == [
        "mesh_slo_freshness_violation"
    ]
    assert violations[0]["product_id"] == "lotus-risk:RiskMetricsReport:v1"
    assert "Telemetry age 999999s exceeds SLO" in violations[0]["detail"]
