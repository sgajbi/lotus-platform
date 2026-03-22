from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
AUTOMATION_DIR = ROOT / "automation"
if str(AUTOMATION_DIR) not in sys.path:
    sys.path.insert(0, str(AUTOMATION_DIR))

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")

import core_performance_cross_app_suite as suite_module  # noqa: E402
from core_performance_cross_app_validation import _evaluate_expected_posture  # noqa: E402


def test_evaluate_expected_posture_accepts_clean_pass_scenario():
    posture = _evaluate_expected_posture(
        {"expected_validation": {"status": "pass"}},
        failed_core_checks=[],
        failed_performance_checks=[],
    )

    assert posture["expectation_met"] is True
    assert posture["posture"] == "pass"


def test_evaluate_expected_posture_tracks_known_core_issue_exactly():
    scenario = {
        "expected_validation": {
            "status": "known_core_issue",
            "issue_reference": "lotus-core#258",
            "expected_failed_core_checks": [
                "position_external_flow:CASH_USD_ABC123:2026-03-16",
                "position_external_flow:SEC_USD_STOCK_ABC123:2026-03-16",
            ],
            "expected_failed_performance_checks": [
                "stateful_twr_explicit_window:portfolio_period_return_zero",
            ],
        }
    }

    posture = _evaluate_expected_posture(
        scenario,
        failed_core_checks=[
            {"check": "position_external_flow:SEC_USD_STOCK_ABC123:2026-03-16"},
            {"check": "position_external_flow:CASH_USD_ABC123:2026-03-16"},
        ],
        failed_performance_checks=[
            {
                "request_id": "stateful_twr_explicit_window",
                "checks": [
                    {
                        "check": "portfolio_period_return_zero",
                        "passed": False,
                    }
                ],
            }
        ],
    )

    assert posture["expectation_met"] is True
    assert posture["posture"] == "known_issue_observed"
    assert posture["issue_reference"] == "lotus-core#258"


def test_evaluate_expected_posture_flags_known_issue_resolution_for_review():
    posture = _evaluate_expected_posture(
        {
            "expected_validation": {
                "status": "known_core_issue",
                "expected_failed_core_checks": [
                    "position_external_flow:SEC:2026-03-16"
                ],
            }
        },
        failed_core_checks=[],
        failed_performance_checks=[],
    )

    assert posture["expectation_met"] is False
    assert posture["posture"] == "known_issue_resolved"


def test_suite_reports_expectation_met_when_known_issue_is_observed(
    tmp_path, monkeypatch
):
    scenarios_dir = tmp_path / "scenarios"
    scenarios_dir.mkdir()
    (scenarios_dir / "healthy.json").write_text(
        json.dumps({"scenario_id": "healthy"}), encoding="utf-8"
    )
    (scenarios_dir / "known_issue.json").write_text(
        json.dumps({"scenario_id": "known_issue"}), encoding="utf-8"
    )
    output_path = tmp_path / "suite.json"

    def _fake_run_validation(config, scenario_path, output_path=None):  # noqa: ARG001
        if scenario_path.stem == "healthy":
            return {
                "scenario_id": "healthy",
                "result": "ok",
                "expected_posture": {
                    "expected_status": "pass",
                    "expectation_met": True,
                    "posture": "pass",
                    "issue_reference": None,
                    "expected_failed_core_checks": [],
                    "actual_failed_core_checks": [],
                },
                "failed_core_checks": [],
                "failed_performance_checks": [],
            }
        return {
            "scenario_id": "known_issue",
            "result": "failed",
            "expected_posture": {
                "expected_status": "known_core_issue",
                "expectation_met": True,
                "posture": "known_issue_observed",
                "issue_reference": "lotus-core#258",
                "expected_failed_core_checks": [
                    "position_external_flow:SEC:2026-03-16"
                ],
                "actual_failed_core_checks": ["position_external_flow:SEC:2026-03-16"],
            },
            "failed_core_checks": [{"check": "position_external_flow:SEC:2026-03-16"}],
            "failed_performance_checks": [],
        }

    monkeypatch.setattr(suite_module, "run_validation", _fake_run_validation)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "core_performance_cross_app_suite.py",
            "--scenarios-dir",
            str(scenarios_dir),
            "--output",
            str(output_path),
        ],
    )

    exit_code = suite_module.main()

    assert exit_code == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["result"] == "ok"
    assert payload["expectation_met_count"] == 2
    assert payload["failed_count"] == 1
    assert payload["posture_counts"]["known_issue_observed"] == 1


def test_suite_retries_transient_scenario_execution_failure(tmp_path, monkeypatch):
    scenarios_dir = tmp_path / "scenarios"
    scenarios_dir.mkdir()
    (scenarios_dir / "flaky.json").write_text(
        json.dumps({"scenario_id": "flaky"}), encoding="utf-8"
    )
    output_path = tmp_path / "suite.json"
    attempts = {"count": 0}

    def _flaky_run_validation(config, scenario_path, output_path=None):  # noqa: ARG001
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise RuntimeError(
                "portfolio timeseries maturity did not converge within 240s"
            )
        return {
            "scenario_id": scenario_path.stem,
            "result": "ok",
            "expected_posture": {
                "expected_status": "pass",
                "expectation_met": True,
                "posture": "pass",
                "issue_reference": None,
                "expected_failed_core_checks": [],
                "actual_failed_core_checks": [],
                "expected_failed_performance_checks": [],
                "actual_failed_performance_checks": [],
            },
            "failed_core_checks": [],
            "failed_performance_checks": [],
        }

    monkeypatch.setattr(suite_module, "run_validation", _flaky_run_validation)
    monkeypatch.setattr(suite_module.time, "sleep", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "core_performance_cross_app_suite.py",
            "--scenarios-dir",
            str(scenarios_dir),
            "--output",
            str(output_path),
            "--scenario-max-attempts",
            "2",
        ],
    )

    exit_code = suite_module.main()

    assert exit_code == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert attempts["count"] == 2
    assert payload["results"][0]["attempts"] == 2
