from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

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


TOLERANCE = Decimal("0.0001")


def _poll_core_portfolio_timeseries(
    session: requests.Session,
    *,
    core_query_base_url: str,
    scenario_ids: ScenarioIds,
) -> None:
    _poll_post_json(
        session,
        f"{core_query_base_url}/integration/portfolios/{scenario_ids.portfolio_id}/analytics/portfolio-timeseries",
        {
            "as_of_date": "2026-03-20",
            "window": {"start_date": "2026-03-16", "end_date": "2026-03-20"},
            "frequency": "daily",
            "reporting_currency": "USD",
            "consumer_system": "lotus-platform",
        },
        predicate=lambda payload: len(payload.get("observations", [])) == 5,
    )


def _post_stateful_contribution(
    session: requests.Session,
    *,
    performance_base_url: str,
    scenario_ids: ScenarioIds,
) -> dict[str, Any]:
    contribution_response = _post_json(
        session,
        f"{performance_base_url}/performance/contribution",
        {
            "portfolio_id": scenario_ids.portfolio_id,
            "report_start_date": "2026-03-16",
            "report_end_date": "2026-03-20",
            "analyses": [{"period": "ITD", "frequencies": ["daily"]}],
            "emit": {"timeseries": True, "by_position_timeseries": True},
            "input_mode": "stateful",
            "stateful_input": {},
        },
    )
    return _follow_async_result(
        session,
        contribution_response,
        performance_base_url=performance_base_url,
        fallback_result_prefix="/performance/contribution/results",
    )


def _post_stateful_twr(
    session: requests.Session,
    *,
    performance_base_url: str,
    scenario_ids: ScenarioIds,
) -> dict[str, Any]:
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
            "include_benchmark": False,
        },
    )
    return _follow_async_result(
        session,
        twr_response,
        performance_base_url=performance_base_url,
        fallback_result_prefix="/performance/twr/results",
    )


def _append_defect(
    defects: list[dict[str, str]],
    *,
    code: str,
    message: str,
    evidence: dict[str, object],
) -> None:
    defects.append(
        {
            "app": "lotus-performance",
            "code": code,
            "message": message,
            "evidence": json.dumps(evidence),
        }
    )


def _sum_position_contribution(position_contributions: list[dict[str, Any]]) -> Decimal:
    return sum(
        Decimal(str(position["total_contribution"])) for position in position_contributions
    )


def _position_ids(rows: list[dict[str, Any]]) -> set[str]:
    return {row["position_id"].split(":")[-1] for row in rows}


def _by_position_daily_totals(
    by_position_timeseries: list[dict[str, Any]],
) -> dict[str, Decimal]:
    daily_totals: dict[str, Decimal] = {}
    for series in by_position_timeseries:
        for point in series.get("series", []):
            daily_totals.setdefault(point["date"], Decimal("0"))
            daily_totals[point["date"]] += Decimal(str(point["contribution"]))
    return daily_totals


def _validate_contribution_input_mode(
    contribution: dict[str, Any], defects: list[dict[str, str]]
) -> None:
    if contribution.get("input_mode") != "stateful":
        _append_defect(
            defects,
            code="CONTRIBUTION_INPUT_MODE_MISMATCH",
            message="Contribution response did not preserve stateful input mode.",
            evidence={"input_mode": contribution.get("input_mode")},
        )


def _validate_contribution_total_return(
    *,
    portfolio_return: Decimal,
    twr_portfolio_return: Decimal,
    defects: list[dict[str, str]],
) -> None:
    if abs(portfolio_return - twr_portfolio_return) <= TOLERANCE:
        return
    _append_defect(
        defects,
        code="CONTRIBUTION_TWR_TOTAL_RETURN_MISMATCH",
        message="Contribution total portfolio return does not align with live stateful TWR for the same window.",
        evidence={
            "contribution_total_portfolio_return": str(portfolio_return),
            "twr_total_portfolio_return": str(twr_portfolio_return),
        },
    )


def _validate_position_contribution_sum(
    *,
    contribution_total: Decimal,
    summed_position_contribution: Decimal,
    defects: list[dict[str, str]],
) -> None:
    if abs(contribution_total - summed_position_contribution) <= TOLERANCE:
        return
    _append_defect(
        defects,
        code="CONTRIBUTION_POSITION_SUM_MISMATCH",
        message="Contribution total does not reconcile to the sum of flat position contributions.",
        evidence={
            "total_contribution": str(contribution_total),
            "summed_position_contribution": str(summed_position_contribution),
        },
    )


def _validate_daily_position_reconciliation(
    *,
    timeseries: list[dict[str, Any]],
    by_position_timeseries: list[dict[str, Any]],
    defects: list[dict[str, str]],
) -> None:
    by_position_totals = _by_position_daily_totals(by_position_timeseries)
    for point in timeseries:
        point_date = point["date"]
        daily_total = Decimal(str(point["total_contribution"]))
        by_position_total = by_position_totals.get(point_date, Decimal("0"))
        if abs(daily_total - by_position_total) <= TOLERANCE:
            continue
        _append_defect(
            defects,
            code="CONTRIBUTION_DAILY_POSITION_RECONCILIATION_MISMATCH",
            message="Contribution daily total does not reconcile to the sum of emitted per-position contribution series for the same date.",
            evidence={
                "date": point_date,
                "daily_total_contribution": str(daily_total),
                "summed_position_series_contribution": str(by_position_total),
            },
        )
        break


def _expected_position_ids(scenario_ids: ScenarioIds) -> set[str]:
    return {
        scenario_ids.cash_security_id,
        scenario_ids.aapl_security_id,
        scenario_ids.msft_security_id,
    }


def _validate_position_id_sets(
    *,
    expected_position_ids: set[str],
    contribution_position_ids: set[str],
    by_position_ids: set[str],
    defects: list[dict[str, str]],
) -> None:
    if contribution_position_ids != expected_position_ids:
        _append_defect(
            defects,
            code="CONTRIBUTION_POSITION_ID_SET_MISMATCH",
            message="Contribution result did not include the expected seeded positions.",
            evidence={
                "expected_position_ids": sorted(expected_position_ids),
                "actual_position_ids": sorted(contribution_position_ids),
            },
        )

    if by_position_ids != expected_position_ids:
        _append_defect(
            defects,
            code="CONTRIBUTION_POSITION_SERIES_SET_MISMATCH",
            message="Contribution by-position timeseries did not include the expected seeded positions.",
            evidence={
                "expected_position_ids": sorted(expected_position_ids),
                "actual_position_ids": sorted(by_position_ids),
            },
        )


def _validate_position_series_lengths(
    by_position_timeseries: list[dict[str, Any]], defects: list[dict[str, str]]
) -> None:
    for series in by_position_timeseries:
        if len(series.get("series", [])) == 5:
            continue
        _append_defect(
            defects,
            code="CONTRIBUTION_POSITION_SERIES_LENGTH_MISMATCH",
            message="Contribution by-position timeseries did not preserve the expected five business dates.",
            evidence={
                "position_id": series.get("position_id"),
                "point_count": len(series.get("series", [])),
            },
        )
        break


def _run_validation(
    *,
    core_query_base_url: str,
    core_ingestion_base_url: str,
    performance_base_url: str,
    scenario_suffix: str | None,
    skip_seed: bool,
) -> dict[str, object]:
    scenario_ids: ScenarioIds = _build_ids_for_suffix(scenario_suffix) if scenario_suffix else _build_ids()
    defects: list[dict[str, str]] = []

    with requests.Session() as session:
        if not skip_seed:
            _seed_core_data(session, ingestion_base_url=core_ingestion_base_url, ids=scenario_ids)

        _poll_core_portfolio_timeseries(
            session,
            core_query_base_url=core_query_base_url,
            scenario_ids=scenario_ids,
        )

        contribution = _post_stateful_contribution(
            session,
            performance_base_url=performance_base_url,
            scenario_ids=scenario_ids,
        )
        twr = _post_stateful_twr(
            session,
            performance_base_url=performance_base_url,
            scenario_ids=scenario_ids,
        )

        contribution_itd = contribution["results_by_period"]["ITD"]
        twr_itd = twr["results_by_period"]["ITD"]
        contribution_total = Decimal(str(contribution_itd["total_contribution"]))
        portfolio_return = Decimal(str(contribution_itd["total_portfolio_return"]))
        twr_portfolio_return = Decimal(str(twr_itd["portfolio"]["summary"]["period_return"]["base"]))
        position_contributions = contribution_itd.get("position_contributions") or []
        timeseries = contribution_itd.get("timeseries") or []
        by_position_timeseries = contribution_itd.get("by_position_timeseries") or []

        summed_position_contribution = _sum_position_contribution(position_contributions)
        by_position_ids = _position_ids(by_position_timeseries)
        contribution_position_ids = _position_ids(position_contributions)
        expected_position_ids = _expected_position_ids(scenario_ids)

        _validate_contribution_input_mode(contribution, defects)
        _validate_contribution_total_return(
            portfolio_return=portfolio_return,
            twr_portfolio_return=twr_portfolio_return,
            defects=defects,
        )
        _validate_position_contribution_sum(
            contribution_total=contribution_total,
            summed_position_contribution=summed_position_contribution,
            defects=defects,
        )
        _validate_daily_position_reconciliation(
            timeseries=timeseries,
            by_position_timeseries=by_position_timeseries,
            defects=defects,
        )
        _validate_position_id_sets(
            expected_position_ids=expected_position_ids,
            contribution_position_ids=contribution_position_ids,
            by_position_ids=by_position_ids,
            defects=defects,
        )
        _validate_position_series_lengths(by_position_timeseries, defects)

    return {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "status": "passed" if not defects else "failed",
        "scenario_seed_mode": "reused_existing" if skip_seed else "fresh_seeded",
        "scenario": asdict(scenario_ids),
        "performance": {
            "input_mode": contribution.get("input_mode"),
            "contribution_total_portfolio_return_pct": str(portfolio_return),
            "contribution_total_pct": str(contribution_total),
            "summed_position_contribution_pct": str(summed_position_contribution),
            "twr_total_portfolio_return_pct": str(twr_portfolio_return),
            "position_ids": sorted(contribution_position_ids),
            "daily_points": len(timeseries),
            "by_position_series_count": len(by_position_timeseries),
            "defects": defects,
        },
    }


def _write_outputs(result: dict[str, object], *, output_json: Path, output_markdown: Path) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# Cross-App Core -> Performance Contribution Validation",
        "",
        f"- Generated: {result['generated_at_utc']}",
        f"- Status: {result['status']}",
        f"- Portfolio ID: {result['scenario']['portfolio_id']}",
        "",
        "## What This Checks",
        "",
        "- realistic stateful contribution sourcing from lotus-core",
        "- contribution total portfolio return matches stateful TWR for the same portfolio and window",
        "- contribution total reconciles to flat position contributions",
        "- each emitted daily total contribution reconciles to the sum of the emitted per-position daily contribution series",
        "- by-position contribution series include the expected seeded positions and dates",
        "",
        "## lotus-performance",
        "",
        f"- Input mode: {result['performance']['input_mode']}",
        f"- Contribution total portfolio return pct: {result['performance']['contribution_total_portfolio_return_pct']}",
        f"- Contribution total pct: {result['performance']['contribution_total_pct']}",
        f"- Summed position contribution pct: {result['performance']['summed_position_contribution_pct']}",
        f"- TWR total portfolio return pct: {result['performance']['twr_total_portfolio_return_pct']}",
        f"- Daily points: {result['performance']['daily_points']}",
        f"- By-position series count: {result['performance']['by_position_series_count']}",
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
    parser.add_argument("--core-ingestion-base-url", default="http://core-ingestion.dev.lotus")
    parser.add_argument("--core-query-base-url", default="http://core-control.dev.lotus")
    parser.add_argument("--performance-base-url", default="http://performance.dev.lotus")
    parser.add_argument("--output-json", default="output/cross-app/core-performance-contribution-validation.json")
    parser.add_argument("--output-markdown", default="output/cross-app/core-performance-contribution-validation.md")
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
        core_query_base_url=args.core_query_base_url,
        core_ingestion_base_url=args.core_ingestion_base_url,
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
