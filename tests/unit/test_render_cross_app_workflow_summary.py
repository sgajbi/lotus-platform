from __future__ import annotations

from automation.render_cross_app_workflow_summary import (
    _render_baseline,
    _render_single,
)


def test_render_single_includes_scenario_metrics_and_merged_defects() -> None:
    markdown = _render_single(
        "returns_series",
        {
            "status": "failed",
            "scenario_seed_mode": "shared",
            "scenario": {
                "portfolio_id": "PB_TEST",
                "benchmark_id": "BM_TEST",
            },
            "core": {
                "portfolio_timeseries_observations": 7,
                "position_timeseries_rows": 11,
            },
            "performance": {
                "benchmark_context": {
                    "benchmark_id": "BM_RESOLVED",
                    "return_source": "seeded_fixture",
                },
                "twr_itd_portfolio_base_return": "0.123",
                "twr_itd_benchmark_base_return": "0.100",
                "defects": [
                    {
                        "app": "lotus-performance",
                        "code": "PERF_DRIFT",
                        "message": "Performance drift.",
                    },
                    "ignored",
                ],
            },
            "core_defects": [
                {
                    "app": "lotus-core",
                    "code": "CORE_MISSING",
                    "message": "Core fixture missing.",
                }
            ],
        },
    )

    assert "## Cross-App Validation Summary: `returns_series`" in markdown
    assert "- Status: `failed`" in markdown
    assert "- Scenario seed mode: `shared`" in markdown
    assert "- Portfolio: `PB_TEST`" in markdown
    assert "- Benchmark: `BM_TEST`" in markdown
    assert "- Portfolio timeseries observations: `7`" in markdown
    assert "- Position timeseries rows: `11`" in markdown
    assert "- Resolved benchmark: `BM_RESOLVED`" in markdown
    assert "- Benchmark return source: `seeded_fixture`" in markdown
    assert "- twr_itd_portfolio_base_return: `0.123`" in markdown
    assert "- twr_itd_benchmark_base_return: `0.100`" in markdown
    assert "- `lotus-performance` `PERF_DRIFT`: Performance drift." in markdown
    assert "- `lotus-core` `CORE_MISSING`: Core fixture missing." in markdown
    assert "ignored" not in markdown


def test_render_baseline_lists_validators_and_defects() -> None:
    markdown = _render_baseline(
        "baseline",
        {
            "status": "passed",
            "mode": "advisory",
            "shared_scenario_suffix": "shared-001",
            "mwr_scenario_suffix": "mwr-001",
            "validators": [
                {"key": "core", "status": "passed", "exit_code": 0},
                "ignored",
            ],
            "defects": [
                {
                    "app": "lotus-core",
                    "code": "WARN",
                    "message": "Warning only.",
                }
            ],
        },
    )

    assert "## Cross-App Validation Summary: `baseline`" in markdown
    assert "- Status: `passed`" in markdown
    assert "- Mode: `advisory`" in markdown
    assert "- Shared scenario suffix: `shared-001`" in markdown
    assert "- MWR scenario suffix: `mwr-001`" in markdown
    assert "- `core` status=`passed` exit_code=`0`" in markdown
    assert "- `lotus-core` `WARN`: Warning only." in markdown
    assert "ignored" not in markdown
