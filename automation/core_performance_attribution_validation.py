from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import requests

from core_performance_twr_benchmark_validation import (
    ScenarioIds,
    _build_ids,
    _follow_async_result,
    _poll_post_json,
    _post_json,
    _seed_core_data,
)


def _run_validation_once(
    *,
    scenario_ids: ScenarioIds,
    core_ingestion_base_url: str,
    core_query_base_url: str,
    performance_base_url: str,
) -> dict[str, object]:
    defects: list[dict[str, str]] = []

    with requests.Session() as session:
        _seed_core_data(session, ingestion_base_url=core_ingestion_base_url, ids=scenario_ids)

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
        _poll_post_json(
            session,
            f"{core_query_base_url}/integration/portfolios/{scenario_ids.portfolio_id}/analytics/position-timeseries",
            {
                "as_of_date": "2026-03-20",
                "window": {"start_date": "2026-03-16", "end_date": "2026-03-20"},
                "frequency": "daily",
                "reporting_currency": "USD",
                "consumer_system": "lotus-platform",
                "dimensions": ["asset_class", "sector"],
            },
            predicate=lambda payload: len(payload.get("rows", [])) >= 10,
        )
        _poll_post_json(
            session,
            f"{core_query_base_url}/integration/portfolios/{scenario_ids.portfolio_id}/analytics/portfolio-timeseries",
            {
                "as_of_date": "2026-03-20",
                "window": {"start_date": "2026-03-17", "end_date": "2026-03-20"},
                "frequency": "daily",
                "reporting_currency": "USD",
                "consumer_system": "lotus-platform",
            },
            predicate=lambda payload: len(payload.get("observations", [])) == 4,
        )

        attribution_request = {
            "portfolio_id": scenario_ids.portfolio_id,
            "mode": "by_instrument",
            "group_by": ["asset_class"],
            "linking": "carino",
            "frequency": "daily",
            "report_start_date": "2026-03-16",
            "report_end_date": "2026-03-20",
            "analyses": [{"period": "ITD", "frequencies": ["daily"]}],
            "input_mode": "stateful",
            "stateful_input": {},
        }
        attribution_raw = session.post(
            f"{performance_base_url}/performance/attribution",
            json=attribution_request,
            timeout=30,
        )
        acquisition_day_guarded = False
        if attribution_raw.status_code == 422:
            acquisition_day_guarded = "cannot safely compute acquisition-day position returns" in attribution_raw.text
            if not acquisition_day_guarded:
                defects.append(
                    {
                        "app": "lotus-performance",
                        "code": "ATTRIBUTION_STATEFUL_UNEXPECTED_422",
                        "message": "Stateful attribution rejected the acquisition-day window, but not with the expected contract-gap message.",
                        "evidence": attribution_raw.text,
                    }
                )
            attribution = {
                "input_mode": "stateful",
                "benchmark_context": None,
                "results_by_period": {},
            }
        elif attribution_raw.status_code in (200, 202):
            defects.append(
                {
                    "app": "lotus-performance",
                    "code": "ATTRIBUTION_ACQUISITION_DAY_NOT_GUARDED",
                    "message": "Stateful attribution accepted an acquisition-day window that should currently fail closed until upstream position semantics are stronger.",
                    "evidence": attribution_raw.text,
                }
            )
            attribution = _follow_async_result(
                session,
                attribution_raw,
                performance_base_url=performance_base_url,
                fallback_result_prefix="/performance/attribution/results",
            )
        else:
            detail = attribution_raw.text
            defects.append(
                {
                    "app": "lotus-performance",
                    "code": "ATTRIBUTION_STATEFUL_CONTRACT_GAP",
                    "message": "Stateful attribution request was rejected because the sourced position contract cannot safely support the requested window.",
                    "evidence": detail,
                }
            )
            attribution = {
                "input_mode": "stateful",
                "benchmark_context": None,
                "results_by_period": {},
            }

        supported_attribution_response = _post_json(
            session,
            f"{performance_base_url}/performance/attribution",
            {
                "portfolio_id": scenario_ids.portfolio_id,
                "mode": "by_instrument",
                "group_by": ["asset_class"],
                "linking": "carino",
                "frequency": "daily",
                "report_start_date": "2026-03-17",
                "report_end_date": "2026-03-20",
                "analyses": [{"period": "ITD", "frequencies": ["daily"]}],
                "input_mode": "stateful",
                "stateful_input": {},
            },
        )
        supported_attribution = _follow_async_result(
            session,
            supported_attribution_response,
            performance_base_url=performance_base_url,
            fallback_result_prefix="/performance/attribution/results",
        )

        twr_response = _post_json(
            session,
            f"{performance_base_url}/performance/twr",
            {
                "portfolio_id": scenario_ids.portfolio_id,
                "report_end_date": "2026-03-20",
                "performance_start_date": "2026-03-17",
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

        twr_relative = Decimal(
            str(twr["results_by_period"]["ITD"]["relative_performance"]["summary"]["period_return"]["base"])
        )
        tolerance = Decimal("0.0001")
        total_active: Decimal | None = None
        summed_effects: Decimal | None = None
        level_total_effect: Decimal | None = None

        if attribution.get("input_mode") != "stateful":
            defects.append(
                {
                    "app": "lotus-performance",
                    "code": "ATTRIBUTION_INPUT_MODE_MISMATCH",
                    "message": "Attribution response did not preserve stateful input mode.",
                    "evidence": json.dumps({"input_mode": attribution.get("input_mode")}),
                }
            )

        benchmark_context = supported_attribution.get("benchmark_context")
        if not isinstance(benchmark_context, dict):
            benchmark_context = None

        if (benchmark_context or {}).get("benchmark_id") not in {None, scenario_ids.benchmark_id}:
            defects.append(
                {
                    "app": "lotus-performance",
                    "code": "ATTRIBUTION_BENCHMARK_CONTEXT_MISMATCH",
                    "message": "Attribution benchmark context did not resolve the seeded benchmark assignment.",
                    "evidence": json.dumps(benchmark_context or {}),
                }
            )

        if "ITD" in supported_attribution.get("results_by_period", {}):
            attribution_itd = supported_attribution["results_by_period"]["ITD"]
            reconciliation = attribution_itd["reconciliation"]
            level_totals = attribution_itd["levels"][0]["totals"]
            total_active = Decimal(str(reconciliation["total_active_return"]))
            summed_effects = Decimal(str(reconciliation["sum_of_effects"]))
            level_total_effect = Decimal(str(level_totals["total_effect"]))

            if abs(level_total_effect - summed_effects) > tolerance:
                defects.append(
                    {
                        "app": "lotus-performance",
                        "code": "ATTRIBUTION_LEVEL_TOTAL_MISMATCH",
                        "message": "Attribution top-level totals do not reconcile to the reported sum_of_effects.",
                        "evidence": json.dumps(
                            {
                                "level_total_effect": str(level_total_effect),
                                "sum_of_effects": str(summed_effects),
                            }
                        ),
                    }
                )

            if abs(total_active - twr_relative) > tolerance:
                defects.append(
                    {
                        "app": "lotus-performance",
                        "code": "ATTRIBUTION_TWR_ACTIVE_MISMATCH",
                        "message": "Attribution total active return does not align with benchmark-inclusive TWR for the same portfolio and window.",
                        "evidence": json.dumps(
                            {
                                "attribution_total_active_return": str(total_active),
                                "twr_relative_return": str(twr_relative),
                            }
                        ),
                    }
                )

    return {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "status": "passed" if not defects else "failed",
        "scenario": asdict(scenario_ids),
        "performance": {
            "input_mode": supported_attribution.get("input_mode"),
            "benchmark_context": benchmark_context,
            "acquisition_day_guarded": acquisition_day_guarded,
            "group_count": (
                len(supported_attribution["results_by_period"]["ITD"]["levels"][0]["groups"])
                if "ITD" in supported_attribution.get("results_by_period", {})
                else 0
            ),
            "attribution_total_active_return": str(total_active) if total_active is not None else None,
            "attribution_sum_of_effects": str(summed_effects) if summed_effects is not None else None,
            "twr_relative_return": str(twr_relative),
            "defects": defects,
        },
    }


def _run_validation(
    *,
    core_ingestion_base_url: str,
    core_query_base_url: str,
    performance_base_url: str,
    max_attempts: int = 3,
) -> dict[str, object]:
    last_error: str | None = None
    last_scenario: ScenarioIds | None = None

    for _ in range(max_attempts):
        scenario_ids = _build_ids()
        last_scenario = scenario_ids
        try:
            return _run_validation_once(
                scenario_ids=scenario_ids,
                core_ingestion_base_url=core_ingestion_base_url,
                core_query_base_url=core_query_base_url,
                performance_base_url=performance_base_url,
            )
        except RuntimeError as exc:
            last_error = str(exc)

    assert last_scenario is not None
    return {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "status": "failed",
        "scenario": asdict(last_scenario),
        "performance": {
            "input_mode": "stateful",
            "benchmark_context": None,
            "acquisition_day_guarded": False,
            "group_count": 0,
            "attribution_total_active_return": None,
            "attribution_sum_of_effects": None,
            "twr_relative_return": None,
            "defects": [
                {
                    "app": "lotus-core",
                    "code": "ATTRIBUTION_SEEDED_WINDOW_NOT_READY",
                    "message": "Seeded attribution validation scenario did not reach a stable core analytics window after multiple attempts.",
                    "evidence": last_error or "unknown_runtime_error",
                }
            ],
        },
    }


def _write_outputs(result: dict[str, object], *, output_json: Path, output_markdown: Path) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# Cross-App Core -> Performance Attribution Validation",
        "",
        f"- Generated: {result['generated_at_utc']}",
        f"- Status: {result['status']}",
        f"- Portfolio ID: {result['scenario']['portfolio_id']}",
        f"- Benchmark ID: {result['scenario']['benchmark_id']}",
        "",
        "## What This Checks",
        "",
        "- realistic stateful attribution sourcing from lotus-core",
        "- acquisition-day attribution windows fail closed with a clear contract-gap message",
        "- steady-state stateful attribution resolves the seeded benchmark assignment",
        "- steady-state top-level attribution totals reconcile to the reported sum of effects",
        "- steady-state attribution total active return aligns with benchmark-inclusive TWR for the same portfolio and window",
        "",
        "## lotus-performance",
        "",
        f"- Input mode: {result['performance']['input_mode']}",
        f"- Acquisition-day guarded: {result['performance']['acquisition_day_guarded']}",
        f"- Benchmark context: {json.dumps(result['performance']['benchmark_context'])}",
        f"- Group count: {result['performance']['group_count']}",
        f"- Attribution total active return: {result['performance']['attribution_total_active_return']}",
        f"- Attribution sum of effects: {result['performance']['attribution_sum_of_effects']}",
        f"- TWR relative return: {result['performance']['twr_relative_return']}",
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
    parser.add_argument("--output-json", default="output/cross-app/core-performance-attribution-validation.json")
    parser.add_argument("--output-markdown", default="output/cross-app/core-performance-attribution-validation.md")
    args = parser.parse_args()

    result = _run_validation(
        core_ingestion_base_url=args.core_ingestion_base_url,
        core_query_base_url=args.core_query_base_url,
        performance_base_url=args.performance_base_url,
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
