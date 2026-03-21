from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path

import requests

from core_performance_twr_benchmark_validation import (
    ScenarioIds,
    _build_ids,
    _build_ids_for_suffix,
    _follow_async_result,
    _poll_post_json,
    _post_json,
    _seed_core_data,
)


def _run_validation(
    *,
    core_ingestion_base_url: str,
    core_query_base_url: str,
    performance_base_url: str,
    scenario_suffix: str | None,
    skip_seed: bool,
) -> dict[str, object]:
    scenario_ids: ScenarioIds = _build_ids_for_suffix(scenario_suffix) if scenario_suffix else _build_ids()
    defects: list[dict[str, str]] = []

    with requests.Session() as session:
        if not skip_seed:
            _seed_core_data(session, ingestion_base_url=core_ingestion_base_url, ids=scenario_ids)

        _poll_post_json(
            session,
            f"{core_query_base_url}/integration/portfolios/{scenario_ids.portfolio_id}/analytics/portfolio-timeseries",
            {
                "as_of_date": "2026-03-20",
                "window": {"start_date": "2026-03-16", "end_date": "2026-03-20"},
                "frequency": "daily",
                "consumer_system": "lotus-platform",
            },
            predicate=lambda payload: len(payload.get("observations", [])) == 5,
        )

        returns_series_response = _post_json(
            session,
            f"{performance_base_url}/integration/returns/series",
            {
                "portfolio_id": scenario_ids.portfolio_id,
                "as_of_date": "2026-03-20",
                "window": {"mode": "EXPLICIT", "from_date": "2026-03-16", "to_date": "2026-03-20"},
                "frequency": "DAILY",
                "metric_basis": "NET",
                "reporting_currency": "USD",
                "series_selection": {
                    "include_portfolio": True,
                    "include_benchmark": True,
                    "include_risk_free": False,
                },
                "input_mode": "stateful",
                "stateful_input": {},
            },
        )
        returns_series = _follow_async_result(
            session,
            returns_series_response,
            performance_base_url=performance_base_url,
            fallback_result_prefix="/integration/returns/series/results",
        )

        twr_response = _post_json(
            session,
            f"{performance_base_url}/performance/twr",
            {
                "portfolio_id": scenario_ids.portfolio_id,
                "report_end_date": "2026-03-20",
                "metric_basis": "NET",
                "analyses": [{"period": "ITD", "frequencies": ["daily"]}],
                "input_mode": "stateful",
                "stateful_input": {},
                "include_benchmark": True,
            },
        )
        twr = _follow_async_result(
            session,
            twr_response,
            performance_base_url=performance_base_url,
            fallback_result_prefix="/performance/twr/results",
        )

        benchmark_response = _post_json(
            session,
            f"{performance_base_url}/performance/benchmark",
            {
                "benchmark_id": scenario_ids.benchmark_id,
                "benchmark_start_date": "2026-03-16",
                "report_end_date": "2026-03-20",
                "analyses": [{"period": "ITD", "frequencies": ["daily"]}],
                "input_mode": "stateful",
                "return_source": "calculated",
                "stateful_input": {},
            },
        )
        benchmark = _follow_async_result(
            session,
            benchmark_response,
            performance_base_url=performance_base_url,
            fallback_result_prefix="/performance/benchmark/results",
        )

        series = returns_series["series"]
        cumulative_portfolio = Decimal(series["cumulative_portfolio_returns"][-1]["return_value"]) * Decimal("100")
        cumulative_benchmark = Decimal(series["cumulative_benchmark_returns"][-1]["return_value"]) * Decimal("100")
        cumulative_active = Decimal(series["cumulative_active_returns"][-1]["return_value"]) * Decimal("100")

        twr_itd = twr["results_by_period"]["ITD"]
        twr_portfolio_cumulative = Decimal(str(twr_itd["portfolio"]["summary"]["cumulative_return"]["base"]))
        twr_benchmark_cumulative = Decimal(str(twr_itd["benchmark"]["summary"]["cumulative_return"]["base"]))
        twr_relative_cumulative = Decimal(str(twr_itd["relative_performance"]["summary"]["cumulative_return"]["base"]))
        benchmark_cumulative = Decimal(
            str(benchmark["results_by_period"]["ITD"]["benchmark"]["summary"]["cumulative_return"]["base"])
        )

        tolerance = Decimal("0.0001")

        if returns_series.get("benchmark_context", {}).get("benchmark_id") != scenario_ids.benchmark_id:
            defects.append(
                {
                    "app": "lotus-performance",
                    "code": "RETURNS_SERIES_BENCHMARK_CONTEXT_MISMATCH",
                    "message": "Returns-series benchmark context did not resolve the expected benchmark assignment.",
                    "evidence": json.dumps(returns_series.get("benchmark_context", {})),
                }
            )

        if abs(cumulative_portfolio - twr_portfolio_cumulative) > tolerance:
            defects.append(
                {
                    "app": "lotus-performance",
                    "code": "RETURNS_SERIES_PORTFOLIO_CUMULATIVE_MISMATCH",
                    "message": "Returns-series cumulative portfolio return does not align with benchmark-inclusive TWR.",
                    "evidence": json.dumps(
                        {
                            "returns_series_cumulative_portfolio_pct": str(cumulative_portfolio),
                            "twr_cumulative_portfolio_pct": str(twr_portfolio_cumulative),
                        }
                    ),
                }
            )

        if abs(cumulative_benchmark - twr_benchmark_cumulative) > tolerance:
            defects.append(
                {
                    "app": "lotus-performance",
                    "code": "RETURNS_SERIES_BENCHMARK_CUMULATIVE_MISMATCH",
                    "message": "Returns-series cumulative benchmark return does not align with TWR benchmark output.",
                    "evidence": json.dumps(
                        {
                            "returns_series_cumulative_benchmark_pct": str(cumulative_benchmark),
                            "twr_cumulative_benchmark_pct": str(twr_benchmark_cumulative),
                        }
                    ),
                }
            )

        if abs(cumulative_benchmark - benchmark_cumulative) > tolerance:
            defects.append(
                {
                    "app": "lotus-performance",
                    "code": "RETURNS_SERIES_BENCHMARK_ENDPOINT_MISMATCH",
                    "message": "Returns-series cumulative benchmark return does not align with the dedicated benchmark endpoint.",
                    "evidence": json.dumps(
                        {
                            "returns_series_cumulative_benchmark_pct": str(cumulative_benchmark),
                            "benchmark_endpoint_cumulative_pct": str(benchmark_cumulative),
                        }
                    ),
                }
            )

        if abs(cumulative_active - twr_relative_cumulative) > tolerance:
            defects.append(
                {
                    "app": "lotus-performance",
                    "code": "RETURNS_SERIES_ACTIVE_CUMULATIVE_MISMATCH",
                    "message": "Returns-series cumulative active return does not align with TWR relative performance.",
                    "evidence": json.dumps(
                        {
                            "returns_series_cumulative_active_pct": str(cumulative_active),
                            "twr_cumulative_relative_pct": str(twr_relative_cumulative),
                        }
                    ),
                }
            )

        for portfolio_point, benchmark_point, active_point in zip(
            series["portfolio_returns"],
            series["benchmark_returns"],
            series["active_returns"],
            strict=True,
        ):
            portfolio_return = Decimal(portfolio_point["return_value"])
            benchmark_return = Decimal(benchmark_point["return_value"])
            active_return = Decimal(active_point["return_value"])
            if abs((portfolio_return - benchmark_return) - active_return) > Decimal("0.0000000001"):
                defects.append(
                    {
                        "app": "lotus-performance",
                        "code": "RETURNS_SERIES_ACTIVE_ARITHMETIC_MISMATCH",
                        "message": "Returns-series active return is not the arithmetic difference between portfolio and benchmark on every date.",
                        "evidence": json.dumps(
                            {
                                "date": portfolio_point["date"],
                                "portfolio_return": str(portfolio_return),
                                "benchmark_return": str(benchmark_return),
                                "active_return": str(active_return),
                            }
                        ),
                    }
                )
                break

    return {
        "generated_at_utc": json.loads(json.dumps(__import__("datetime").datetime.now(__import__("datetime").UTC).isoformat())),
        "status": "passed" if not defects else "failed",
        "scenario_seed_mode": "reused_existing" if skip_seed else "fresh_seeded",
        "scenario": asdict(scenario_ids),
        "performance": {
            "benchmark_context": returns_series.get("benchmark_context"),
            "portfolio_daily_points": len(series["portfolio_returns"]),
            "benchmark_daily_points": len(series["benchmark_returns"]),
            "active_daily_points": len(series["active_returns"]),
            "returns_series_cumulative_portfolio_pct": str(cumulative_portfolio),
            "returns_series_cumulative_benchmark_pct": str(cumulative_benchmark),
            "returns_series_cumulative_active_pct": str(cumulative_active),
            "twr_cumulative_portfolio_pct": str(twr_portfolio_cumulative),
            "twr_cumulative_benchmark_pct": str(twr_benchmark_cumulative),
            "twr_cumulative_relative_pct": str(twr_relative_cumulative),
            "benchmark_endpoint_cumulative_pct": str(benchmark_cumulative),
            "defects": defects,
        },
    }


def _write_outputs(result: dict[str, object], *, output_json: Path, output_markdown: Path) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# Cross-App Core -> Performance Returns Series Validation",
        "",
        f"- Generated: {result['generated_at_utc']}",
        f"- Status: {result['status']}",
        f"- Portfolio ID: {result['scenario']['portfolio_id']}",
        f"- Benchmark ID: {result['scenario']['benchmark_id']}",
        "",
        "## What This Checks",
        "",
        "- stateful benchmark-aware `/integration/returns/series`",
        "- benchmark-inclusive stateful `/performance/twr`",
        "- dedicated stateful `/performance/benchmark`",
        "- cumulative portfolio, benchmark, and active consistency across all three surfaces",
        "",
        "## lotus-performance",
        "",
        f"- Portfolio daily points: {result['performance']['portfolio_daily_points']}",
        f"- Benchmark daily points: {result['performance']['benchmark_daily_points']}",
        f"- Active daily points: {result['performance']['active_daily_points']}",
        f"- Returns-series cumulative portfolio pct: {result['performance']['returns_series_cumulative_portfolio_pct']}",
        f"- Returns-series cumulative benchmark pct: {result['performance']['returns_series_cumulative_benchmark_pct']}",
        f"- Returns-series cumulative active pct: {result['performance']['returns_series_cumulative_active_pct']}",
        "",
        "## Defects",
        "",
    ]
    defects = result["performance"]["defects"]
    if defects:
        for defect in defects:
            lines.extend(
                [
                    f"- `{defect['app']}` `{defect['code']}`: {defect['message']}",
                    f"  - Evidence: `{defect['evidence']}`",
                ]
            )
    else:
        lines.append("- none")

    output_markdown.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--core-ingestion-base-url", default="http://localhost:8200")
    parser.add_argument("--core-query-base-url", default="http://localhost:8202")
    parser.add_argument("--performance-base-url", default="http://localhost:8002")
    parser.add_argument("--output-json", default="output/cross-app/core-performance-returns-series-validation.json")
    parser.add_argument("--output-markdown", default="output/cross-app/core-performance-returns-series-validation.md")
    parser.add_argument(
        "--scenario-suffix",
        help="Reuse a specific scenario suffix such as 030053 instead of generating a fresh one.",
    )
    parser.add_argument(
        "--skip-seed",
        action="store_true",
        help="Skip ingestion and validate against an already-seeded scenario.",
    )
    args = parser.parse_args()

    result = _run_validation(
        core_ingestion_base_url=args.core_ingestion_base_url,
        core_query_base_url=args.core_query_base_url,
        performance_base_url=args.performance_base_url,
        scenario_suffix=args.scenario_suffix,
        skip_seed=args.skip_seed,
    )
    _write_outputs(
        result,
        output_json=Path(args.output_json),
        output_markdown=Path(args.output_markdown),
    )
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
