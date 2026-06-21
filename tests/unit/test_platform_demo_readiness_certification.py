from __future__ import annotations

import json
from pathlib import Path

import yaml

from automation.certify_platform_demo_readiness import build_certification


ROOT = Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _target_payload(target: str) -> dict:
    base = {
        "status": "passed",
        "scenario_seed_mode": "fresh_seeded",
        "scenario": {"portfolio_id": f"PB_{target.upper()}"},
        "performance": {"defects": []},
    }
    if target == "twr_benchmark":
        base["performance"].update(
            {
                "twr_itd_portfolio_base_return": "0.10",
                "twr_itd_benchmark_base_return": "0.08",
                "twr_itd_relative_base_return": "0.02",
                "benchmark_endpoint_itd_base_return": "0.08",
            }
        )
    elif target == "returns_series":
        base["performance"].update(
            {
                "portfolio_daily_points": 5,
                "benchmark_daily_points": 5,
                "active_daily_points": 5,
                "returns_series_cumulative_portfolio_pct": "1.0",
                "returns_series_cumulative_benchmark_pct": "0.8",
                "returns_series_cumulative_active_pct": "0.2",
            }
        )
    elif target == "contribution":
        base["performance"].update(
            {
                "contribution_total_portfolio_return_pct": "1.0",
                "contribution_total_pct": "1.0",
                "summed_position_contribution_pct": "1.0",
                "twr_total_portfolio_return_pct": "1.0",
            }
        )
    elif target == "mwr":
        base["core"] = {"expected_dietz_return": "1.1"}
        base["performance"].update(
            {
                "money_weighted_return": "1.1",
                "method": "simple_dietz",
                "input_mode": "stateful",
            }
        )
    return base


def test_platform_demo_readiness_certification_accepts_complete_green_lane_evidence(
    tmp_path: Path,
) -> None:
    artifact_dir = tmp_path / "cross-app"
    output_dir = tmp_path / "demo-readiness"
    artifact_names = {
        "twr_benchmark": "core-performance-twr-benchmark-validation.json",
        "returns_series": "core-performance-returns-series-validation.json",
        "contribution": "core-performance-contribution-validation.json",
        "mwr": "core-performance-mwr-validation.json",
    }
    for target, artifact_name in artifact_names.items():
        _write_json(artifact_dir / artifact_name, _target_payload(target))

    certification = build_certification(
        profile_name="core-performance-green-lanes",
        artifact_dir=artifact_dir,
        output_dir=output_dir,
        validation_exit_code=0,
        expected_scenario_seed_mode="fresh_seeded",
    )

    assert certification["certification_status"] == "passed"
    assert certification["gate_posture"] == "report_only"
    assert certification["issues"] == []
    assert (
        output_dir / "platform-demo-readiness-certification.json"
    ).exists()


def test_platform_demo_readiness_certification_rejects_missing_domain_figure(
    tmp_path: Path,
) -> None:
    artifact_dir = tmp_path / "cross-app"
    output_dir = tmp_path / "demo-readiness"
    payload = _target_payload("mwr")
    del payload["performance"]["money_weighted_return"]
    _write_json(artifact_dir / "core-performance-mwr-validation.json", payload)

    certification = build_certification(
        profile_name="core-performance-green-lanes",
        artifact_dir=artifact_dir,
        output_dir=output_dir,
        validation_exit_code=1,
        expected_scenario_seed_mode="fresh_seeded",
    )

    assert certification["certification_status"] == "failed"
    assert "validation command exited 1" in certification["issues"]
    assert any("money_weighted_return is missing" in issue for issue in certification["issues"])


def test_feature_lane_runs_demo_readiness_certification_report_only() -> None:
    workflow = yaml.safe_load(
        (ROOT / ".github" / "workflows" / "feature-lane.yml").read_text(
            encoding="utf-8"
        )
    )
    steps = workflow["jobs"]["repo-contracts"]["steps"]
    certification_step = next(
        step
        for step in steps
        if step.get("name") == "Run platform demo-readiness certification (report-only)"
    )
    upload_step = next(
        step
        for step in steps
        if step.get("name") == "Upload platform demo-readiness certification evidence"
    )

    assert certification_step["continue-on-error"] is True
    assert "Invoke-PlatformDemoReadinessCertification.ps1" in certification_step["run"]
    assert upload_step["if"] == "always()"
    assert upload_step["uses"] == "actions/upload-artifact@v7"
