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
    _build_ids_for_suffix,
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
    skip_seed: bool,
) -> dict[str, object]:
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
        acquisition_day_guarded = attribution_raw.status_code == 422 and (
            "cannot safely compute acquisition-day position returns" in attribution_raw.text
        )
        acquisition_day_contract_consistent = attribution_raw.status_code in (200, 202)

        if attribution_raw.status_code in (200, 202):
            attribution = _follow_async_result(
                session,
                attribution_raw,
                performance_base_url=performance_base_url,
                fallback_result_prefix="/performance/attribution/results",
            )
        else:
            attribution = {
                "input_mode": "stateful",
                "benchmark_context": None,
                "results_by_period": {},
            }
            detail = attribution_raw.text
            if "portfolio timeseries does not align with summed position timeseries" in detail:
                defects.append(
                    {
                        "app": "lotus-core",
                        "code": "ATTRIBUTION_SOURCE_ALIGNMENT_GAP",
                        "message": "lotus-core portfolio-timeseries and position-timeseries do not align for the acquisition-day attribution window.",
                        "evidence": detail,
                    }
                )
            elif attribution_raw.status_code != 422:
                defects.append(
                    {
                        "app": "lotus-performance",
                        "code": "ATTRIBUTION_STATEFUL_UNEXPECTED_ERROR",
                        "message": "Acquisition-day attribution returned an unexpected non-success response.",
                        "evidence": detail,
                    }
                )

        supported_attribution_raw = session.post(
            f"{performance_base_url}/performance/attribution",
            json={
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
            timeout=30,
        )
        if supported_attribution_raw.status_code in (200, 202):
            supported_attribution = _follow_async_result(
                session,
                supported_attribution_raw,
                performance_base_url=performance_base_url,
                fallback_result_prefix="/performance/attribution/results",
            )
        else:
            supported_attribution = {
                "input_mode": "stateful",
                "benchmark_context": None,
                "results_by_period": {},
            }
            detail = supported_attribution_raw.text
            if "portfolio timeseries does not align with summed position timeseries" in detail:
                defects.append(
                    {
                        "app": "lotus-core",
                        "code": "ATTRIBUTION_SOURCE_ALIGNMENT_GAP",
                        "message": "lotus-core portfolio-timeseries and position-timeseries do not align for the same seeded attribution window.",
                        "evidence": detail,
                    }
                )
            else:
                defects.append(
                    {
                        "app": "lotus-performance",
                        "code": "ATTRIBUTION_STATEFUL_UNEXPECTED_ERROR",
                        "message": "Supported-window stateful attribution failed unexpectedly.",
                        "evidence": detail,
                    }
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
        supported_groups_summary: list[dict[str, object]] = []
        duplicate_normalized_group_keys: list[str] = []

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
            first_level = attribution_itd["levels"][0]
            level_totals = first_level["totals"]
            total_active = Decimal(str(reconciliation["total_active_return"]))
            summed_effects = Decimal(str(reconciliation["sum_of_effects"]))
            level_total_effect = Decimal(str(level_totals["total_effect"]))
            supported_groups_summary = [
                {
                    "key": group["key"],
                    "allocation": str(group["allocation"]),
                    "selection": str(group["selection"]),
                    "interaction": str(group["interaction"]),
                    "total_effect": str(group["total_effect"]),
                }
                for group in first_level["groups"]
            ]
            duplicate_normalized_group_keys = _find_duplicate_normalized_group_keys(first_level["groups"])

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

            if duplicate_normalized_group_keys:
                defects.append(
                    {
                        "app": "lotus-performance",
                        "code": "ATTRIBUTION_GROUP_KEY_CANONICALIZATION_GAP",
                        "message": "Attribution produced duplicate first-level benchmark groups that only differ by key casing or label normalization.",
                        "evidence": json.dumps(
                            {
                                "duplicate_normalized_group_keys": duplicate_normalized_group_keys,
                                "groups": supported_groups_summary,
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
            "acquisition_day_contract_consistent": acquisition_day_contract_consistent,
            "group_count": (
                len(supported_attribution["results_by_period"]["ITD"]["levels"][0]["groups"])
                if "ITD" in supported_attribution.get("results_by_period", {})
                else 0
            ),
            "supported_window_groups": supported_groups_summary,
            "duplicate_normalized_group_keys": duplicate_normalized_group_keys,
            "attribution_total_active_return": str(total_active) if total_active is not None else None,
            "attribution_sum_of_effects": str(summed_effects) if summed_effects is not None else None,
            "twr_relative_return": str(twr_relative),
            "defects": defects,
        },
    }


def _find_duplicate_normalized_group_keys(groups: list[dict[str, object]]) -> list[str]:
    normalized_to_originals: dict[str, set[str]] = {}
    for group in groups:
        key = group.get("key")
        if not isinstance(key, dict):
            continue
        normalized = json.dumps(_normalize_group_key(key), sort_keys=True)
        original = json.dumps(key, sort_keys=True)
        normalized_to_originals.setdefault(normalized, set()).add(original)

    return sorted(
        normalized
        for normalized, originals in normalized_to_originals.items()
        if len(originals) > 1
    )


def _normalize_group_key(value: object) -> object:
    if isinstance(value, dict):
        return {str(key).lower(): _normalize_group_key(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_group_key(item) for item in value]
    if isinstance(value, str):
        return value.strip().lower()
    return value


def _run_validation(
    *,
    core_ingestion_base_url: str,
    core_query_base_url: str,
    performance_base_url: str,
    scenario_suffix: str | None,
    skip_seed: bool,
    max_attempts: int = 3,
) -> dict[str, object]:
    last_error: str | None = None
    last_scenario: ScenarioIds | None = None

    attempts = 1 if scenario_suffix or skip_seed else max_attempts

    for _ in range(attempts):
        scenario_ids = _build_ids_for_suffix(scenario_suffix) if scenario_suffix else _build_ids()
        last_scenario = scenario_ids
        try:
            return _run_validation_once(
                scenario_ids=scenario_ids,
                core_ingestion_base_url=core_ingestion_base_url,
                core_query_base_url=core_query_base_url,
                performance_base_url=performance_base_url,
                skip_seed=skip_seed,
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
            "acquisition_day_contract_consistent": False,
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
        "- acquisition-day attribution windows use the current upstream-supported contract",
        "- steady-state stateful attribution resolves the seeded benchmark assignment",
        "- steady-state top-level attribution totals reconcile to the reported sum of effects",
        "- steady-state attribution total active return aligns with benchmark-inclusive TWR for the same portfolio and window",
        "",
        "## lotus-performance",
        "",
        f"- Input mode: {result['performance']['input_mode']}",
        f"- Acquisition-day guarded: {result['performance']['acquisition_day_guarded']}",
        f"- Acquisition-day contract consistent: {result['performance']['acquisition_day_contract_consistent']}",
        f"- Benchmark context: {json.dumps(result['performance']['benchmark_context'])}",
        f"- Group count: {result['performance']['group_count']}",
        f"- Duplicate normalized group keys: {json.dumps(result['performance']['duplicate_normalized_group_keys'])}",
        f"- Attribution total active return: {result['performance']['attribution_total_active_return']}",
        f"- Attribution sum of effects: {result['performance']['attribution_sum_of_effects']}",
        f"- TWR relative return: {result['performance']['twr_relative_return']}",
        "",
        "## Supported Window Groups",
        "",
    ]

    groups = result["performance"]["supported_window_groups"]
    if groups:
        for group in groups:
            lines.extend(
                [
                    f"- Key: `{json.dumps(group['key'])}`",
                    f"  - Allocation: `{group['allocation']}`",
                    f"  - Selection: `{group['selection']}`",
                    f"  - Interaction: `{group['interaction']}`",
                    f"  - Total effect: `{group['total_effect']}`",
                ]
            )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
        "## Defects",
        "",
        ]
    )

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
    parser.add_argument("--output-json", default="output/cross-app/core-performance-attribution-validation.json")
    parser.add_argument("--output-markdown", default="output/cross-app/core-performance-attribution-validation.md")
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
    result["scenario_seed_mode"] = "reused_existing" if args.skip_seed else "fresh_seeded"
    _write_outputs(
        result,
        output_json=Path(args.output_json),
        output_markdown=Path(args.output_markdown),
    )
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
