from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import requests


@dataclass
class ScenarioIds:
    portfolio_id: str
    benchmark_id: str
    cash_security_id: str
    aapl_security_id: str
    msft_security_id: str
    sp500_index_id: str
    agg_index_id: str


def _post_json(session: requests.Session, url: str, payload: dict[str, Any], *, expected=(200, 202)) -> requests.Response:
    response = session.post(url, json=payload, timeout=30)
    if response.status_code not in expected:
        raise RuntimeError(f"POST {url} failed: {response.status_code} {response.text}")
    return response


def _poll_post_json(
    session: requests.Session,
    url: str,
    payload: dict[str, Any],
    *,
    predicate,
    timeout_seconds: int = 240,
    interval_seconds: int = 2,
) -> dict[str, Any]:
    deadline = time.time() + timeout_seconds
    last_status = None
    last_body = None
    while time.time() < deadline:
        response = session.post(url, json=payload, timeout=30)
        last_status = response.status_code
        last_body = response.text
        if response.status_code == 200:
            data = response.json()
            if predicate(data):
                return data
        time.sleep(interval_seconds)
    raise RuntimeError(f"Polling failed for {url}: last_status={last_status} last_body={last_body}")


def _follow_async_result(
    session: requests.Session,
    response: requests.Response,
    *,
    performance_base_url: str,
    fallback_result_prefix: str,
    timeout_seconds: int = 240,
) -> dict[str, Any]:
    if response.status_code == 200:
        return response.json()
    accepted = response.json()
    result_path = accepted.get("result_path") or f"{fallback_result_prefix}/{accepted['calculation_id']}"
    deadline = time.time() + timeout_seconds
    last_status = None
    last_body = None
    while time.time() < deadline:
        result = session.get(f"{performance_base_url}{result_path}", timeout=30)
        last_status = result.status_code
        last_body = result.text
        if result.status_code == 200:
            return result.json()
        if result.status_code in (404, 409):
            time.sleep(2)
            continue
        raise RuntimeError(
            f"Async result failed for {result_path}: {result.status_code} {result.text}"
        )
    raise RuntimeError(
        f"Timed out waiting for async result {result_path}: last_status={last_status} last_body={last_body}"
    )


def _build_ids() -> ScenarioIds:
    suffix = datetime.now(UTC).strftime("%H%M%S")
    return _build_ids_for_suffix(suffix)


def _build_ids_for_suffix(suffix: str) -> ScenarioIds:
    return ScenarioIds(
        portfolio_id=f"LIVE_REAL_{suffix}",
        benchmark_id=f"BMK_US_60_40_{suffix}",
        cash_security_id=f"CASH_USD_{suffix}",
        aapl_security_id=f"SEC_AAPL_{suffix}",
        msft_security_id=f"SEC_MSFT_{suffix}",
        sp500_index_id=f"IDX_SP500_TR_{suffix}",
        agg_index_id=f"IDX_AGG_TR_{suffix}",
    )


def _seed_core_data(session: requests.Session, *, ingestion_base_url: str, ids: ScenarioIds) -> None:
    now_iso = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    payloads = [
        (
            "/ingest/portfolios",
            {
                "portfolios": [
                    {
                        "portfolio_id": ids.portfolio_id,
                        "base_currency": "USD",
                        "open_date": "2026-03-16",
                        "risk_exposure": "balanced",
                        "investment_time_horizon": "long_term",
                        "portfolio_type": "discretionary",
                        "booking_center_code": "SG_BOOKING",
                        "client_id": f"CLIENT_{ids.portfolio_id}",
                        "status": "active",
                    }
                ]
            },
        ),
        (
            "/ingest/instruments",
            {
                "instruments": [
                    {
                        "security_id": ids.cash_security_id,
                        "name": "US Dollar Cash",
                        "isin": f"USD_CASH_{ids.portfolio_id}",
                        "currency": "USD",
                        "product_type": "Cash",
                        "asset_class": "Cash",
                    },
                    {
                        "security_id": ids.aapl_security_id,
                        "name": "Apple Inc.",
                        "isin": f"US0378331005{ids.portfolio_id[-6:]}",
                        "currency": "USD",
                        "product_type": "Equity",
                        "asset_class": "Equity",
                        "sector": "Technology",
                        "country_of_risk": "US",
                    },
                    {
                        "security_id": ids.msft_security_id,
                        "name": "Microsoft Corporation",
                        "isin": f"US5949181045{ids.portfolio_id[-6:]}",
                        "currency": "USD",
                        "product_type": "Equity",
                        "asset_class": "Equity",
                        "sector": "Technology",
                        "country_of_risk": "US",
                    },
                ]
            },
        ),
        (
            "/ingest/business-dates",
            {
                "business_dates": [
                    {"business_date": text}
                    for text in ["2026-03-16", "2026-03-17", "2026-03-18", "2026-03-19", "2026-03-20"]
                ]
            },
        ),
        (
            "/ingest/transactions",
            {
                "transactions": [
                    {
                        "transaction_id": f"DEP_{ids.portfolio_id}",
                        "portfolio_id": ids.portfolio_id,
                        "instrument_id": ids.cash_security_id,
                        "security_id": ids.cash_security_id,
                        "transaction_date": "2026-03-16T08:00:00Z",
                        "transaction_type": "DEPOSIT",
                        "quantity": 220000,
                        "price": 1,
                        "gross_transaction_amount": 220000,
                        "trade_currency": "USD",
                        "currency": "USD",
                    },
                    {
                        "transaction_id": f"BUY_AAPL_{ids.portfolio_id}",
                        "portfolio_id": ids.portfolio_id,
                        "instrument_id": ids.aapl_security_id,
                        "security_id": ids.aapl_security_id,
                        "transaction_date": "2026-03-16T09:00:00Z",
                        "transaction_type": "BUY",
                        "quantity": 300,
                        "price": 210,
                        "gross_transaction_amount": 63000,
                        "trade_currency": "USD",
                        "currency": "USD",
                    },
                    {
                        "transaction_id": f"CASH_AAPL_{ids.portfolio_id}",
                        "portfolio_id": ids.portfolio_id,
                        "instrument_id": ids.cash_security_id,
                        "security_id": ids.cash_security_id,
                        "transaction_date": "2026-03-16T09:00:00Z",
                        "transaction_type": "SELL",
                        "quantity": 63000,
                        "price": 1,
                        "gross_transaction_amount": 63000,
                        "trade_currency": "USD",
                        "currency": "USD",
                    },
                    {
                        "transaction_id": f"BUY_MSFT_{ids.portfolio_id}",
                        "portfolio_id": ids.portfolio_id,
                        "instrument_id": ids.msft_security_id,
                        "security_id": ids.msft_security_id,
                        "transaction_date": "2026-03-16T09:05:00Z",
                        "transaction_type": "BUY",
                        "quantity": 400,
                        "price": 380,
                        "gross_transaction_amount": 152000,
                        "trade_currency": "USD",
                        "currency": "USD",
                    },
                    {
                        "transaction_id": f"CASH_MSFT_{ids.portfolio_id}",
                        "portfolio_id": ids.portfolio_id,
                        "instrument_id": ids.cash_security_id,
                        "security_id": ids.cash_security_id,
                        "transaction_date": "2026-03-16T09:05:00Z",
                        "transaction_type": "SELL",
                        "quantity": 152000,
                        "price": 1,
                        "gross_transaction_amount": 152000,
                        "trade_currency": "USD",
                        "currency": "USD",
                    },
                ]
            },
        ),
    ]
    for endpoint, payload in payloads:
        _post_json(session, f"{ingestion_base_url}{endpoint}", payload)

    market_prices = []
    for price_date in ["2026-03-16", "2026-03-17", "2026-03-18", "2026-03-19", "2026-03-20"]:
        market_prices.append({"security_id": ids.cash_security_id, "price_date": price_date, "price": 1, "currency": "USD"})
    for security_id, prices in [
        (ids.aapl_security_id, [212, 214, 211, 216, 218]),
        (ids.msft_security_id, [382, 379, 385, 388, 392]),
    ]:
        for price_date, price in zip(["2026-03-16", "2026-03-17", "2026-03-18", "2026-03-19", "2026-03-20"], prices):
            market_prices.append({"security_id": security_id, "price_date": price_date, "price": price, "currency": "USD"})
    _post_json(session, f"{ingestion_base_url}/ingest/market-prices", {"market_prices": market_prices})

    _post_json(
        session,
        f"{ingestion_base_url}/ingest/benchmark-definitions",
        {
            "benchmark_definitions": [
                {
                    "benchmark_id": ids.benchmark_id,
                    "benchmark_name": "US Balanced 60/40 Total Return",
                    "benchmark_type": "composite",
                    "benchmark_currency": "USD",
                    "return_convention": "total_return_index",
                    "benchmark_status": "active",
                    "benchmark_family": "multi_asset_strategic",
                    "benchmark_provider": "Internal",
                    "rebalance_frequency": "quarterly",
                    "classification_labels": {"asset_class": "multi_asset", "region": "us"},
                    "effective_from": "2026-01-01",
                }
            ]
        },
    )
    _post_json(
        session,
        f"{ingestion_base_url}/ingest/indices",
        {
            "indices": [
                {
                    "index_id": ids.sp500_index_id,
                    "index_name": "S&P 500 Total Return",
                    "index_currency": "USD",
                    "index_type": "equity_index",
                    "index_status": "active",
                    "index_provider": "SP",
                    "index_market": "us_large_cap",
                    "classification_labels": {"asset_class": "Equity", "region": "US"},
                    "effective_from": "2026-01-01",
                },
                {
                    "index_id": ids.agg_index_id,
                    "index_name": "US Aggregate Bond Total Return",
                    "index_currency": "USD",
                    "index_type": "bond_index",
                    "index_status": "active",
                    "index_provider": "Bloomberg",
                    "index_market": "us_bond",
                    "classification_labels": {"asset_class": "Fixed Income", "region": "US"},
                    "effective_from": "2026-01-01",
                },
            ]
        },
    )
    _post_json(
        session,
        f"{ingestion_base_url}/ingest/benchmark-compositions",
        {
            "benchmark_compositions": [
                {
                    "benchmark_id": ids.benchmark_id,
                    "index_id": ids.sp500_index_id,
                    "composition_effective_from": "2026-01-01",
                    "composition_weight": "0.6000000000",
                    "rebalance_event_id": "rebalance_2026q1",
                },
                {
                    "benchmark_id": ids.benchmark_id,
                    "index_id": ids.agg_index_id,
                    "composition_effective_from": "2026-01-01",
                    "composition_weight": "0.4000000000",
                    "rebalance_event_id": "rebalance_2026q1",
                },
            ]
        },
    )
    _post_json(
        session,
        f"{ingestion_base_url}/ingest/benchmark-assignments",
        {
            "benchmark_assignments": [
                {
                    "portfolio_id": ids.portfolio_id,
                    "benchmark_id": ids.benchmark_id,
                    "effective_from": "2026-01-01",
                    "assignment_source": "benchmark_policy_engine",
                    "assignment_status": "active",
                    "source_system": "lotus-manage",
                    "assignment_recorded_at": now_iso,
                }
            ]
        },
    )

    price_points = []
    for index_id, series_id, values in [
        (ids.sp500_index_id, f"SPX_SERIES_{ids.portfolio_id}", [5000, 5035, 5070, 5055, 5105, 5140]),
        (ids.agg_index_id, f"AGG_SERIES_{ids.portfolio_id}", [1000, 1001, 1002, 1003, 1003.5, 1004]),
    ]:
        for series_date, value in zip(
            ["2026-03-15", "2026-03-16", "2026-03-17", "2026-03-18", "2026-03-19", "2026-03-20"],
            values,
        ):
            price_points.append(
                {
                    "series_id": series_id,
                    "index_id": index_id,
                    "series_date": series_date,
                    "index_price": f"{value:.10f}",
                    "series_currency": "USD",
                    "value_convention": "close_price",
                }
            )
    _post_json(session, f"{ingestion_base_url}/ingest/index-price-series", {"index_price_series": price_points})


def _query_core(session: requests.Session, *, control_base_url: str, ids: ScenarioIds) -> dict[str, Any]:
    portfolio_payload = {
        "as_of_date": "2026-03-20",
        "window": {"start_date": "2026-03-16", "end_date": "2026-03-20"},
        "reporting_currency": "USD",
        "frequency": "daily",
        "consumer_system": "lotus-performance",
        "page": {"page_size": 500},
    }
    position_payload = {**portfolio_payload, "dimensions": ["asset_class", "sector"]}
    portfolio_timeseries = _poll_post_json(
        session,
        f"{control_base_url}/integration/portfolios/{ids.portfolio_id}/analytics/portfolio-timeseries",
        portfolio_payload,
        predicate=lambda data: len(data.get("observations", [])) >= 5,
    )
    position_timeseries = _poll_post_json(
        session,
        f"{control_base_url}/integration/portfolios/{ids.portfolio_id}/analytics/position-timeseries",
        position_payload,
        predicate=lambda data: len(data.get("rows", [])) >= 10,
    )
    benchmark_assignment = _post_json(
        session,
        f"{control_base_url}/integration/portfolios/{ids.portfolio_id}/benchmark-assignment",
        {"as_of_date": "2026-03-20", "reporting_currency": "USD"},
        expected=(200,),
    ).json()
    composition_window = _post_json(
        session,
        f"{control_base_url}/integration/benchmarks/{ids.benchmark_id}/composition-window",
        {"window": {"start_date": "2026-03-16", "end_date": "2026-03-20"}},
        expected=(200,),
    ).json()
    sp500_price_series = _post_json(
        session,
        f"{control_base_url}/integration/indices/{ids.sp500_index_id}/price-series",
        {
            "as_of_date": "2026-03-20",
            "window": {"start_date": "2026-03-15", "end_date": "2026-03-20"},
            "frequency": "daily",
        },
        expected=(200,),
    ).json()
    return {
        "portfolio_timeseries_observations": len(portfolio_timeseries["observations"]),
        "position_timeseries_rows": len(position_timeseries["rows"]),
        "assignment_benchmark_id": benchmark_assignment["benchmark_id"],
        "assignment_effective_from": benchmark_assignment["effective_from"],
        "composition_segment_count": len(composition_window["segments"]),
        "sp500_price_points": len(sp500_price_series["points"]),
        "last_portfolio_observation": portfolio_timeseries["observations"][-1],
    }


def _run_performance_validation(session: requests.Session, *, performance_base_url: str, ids: ScenarioIds) -> dict[str, Any]:
    defects: list[dict[str, str]] = []

    benchmark_response = _follow_async_result(
        session,
        _post_json(
            session,
            f"{performance_base_url}/performance/benchmark",
            {
                "benchmark_id": ids.benchmark_id,
                "benchmark_start_date": "2026-03-16",
                "report_end_date": "2026-03-20",
                "analyses": [{"period": "ITD", "frequencies": ["daily", "monthly"]}],
                "input_mode": "stateful",
                "return_source": "calculated",
                "stateful_input": {},
            },
            expected=(200, 202),
        ),
        performance_base_url=performance_base_url,
        fallback_result_prefix="/performance/benchmark/results",
    )

    twr_without_start = session.post(
        f"{performance_base_url}/performance/twr",
        json={
            "portfolio_id": ids.portfolio_id,
            "report_end_date": "2026-03-20",
            "metric_basis": "NET",
            "analyses": [{"period": "ITD", "frequencies": ["daily", "monthly"]}],
            "input_mode": "stateful",
            "stateful_input": {},
            "include_benchmark": True,
        },
        timeout=30,
    )
    if twr_without_start.status_code >= 400:
        defects.append(
            {
                "app": "lotus-performance",
                "code": "STATEFUL_TWR_START_DATE_DERIVATION",
                "message": "Stateful TWR still fails when performance_start_date is omitted.",
                "evidence": twr_without_start.text,
            }
        )

    twr_response = _follow_async_result(
        session,
        _post_json(
            session,
            f"{performance_base_url}/performance/twr",
            {
                "portfolio_id": ids.portfolio_id,
                "performance_start_date": "2026-03-16",
                "report_end_date": "2026-03-20",
                "metric_basis": "NET",
                "analyses": [{"period": "ITD", "frequencies": ["daily", "monthly"]}],
                "input_mode": "stateful",
                "stateful_input": {},
                "include_benchmark": True,
            },
            expected=(200, 202),
        ),
        performance_base_url=performance_base_url,
        fallback_result_prefix="/performance/twr/results",
    )

    benchmark_only_return = Decimal(
        str(benchmark_response["results_by_period"]["ITD"]["benchmark"]["summary"]["period_return"]["base"])
    )
    twr_portfolio_return = Decimal(
        str(twr_response["results_by_period"]["ITD"]["portfolio"]["summary"]["period_return"]["base"])
    )
    twr_benchmark_return = Decimal(
        str(twr_response["results_by_period"]["ITD"]["benchmark"]["summary"]["period_return"]["base"])
    )
    twr_relative_return = Decimal(
        str(twr_response["results_by_period"]["ITD"]["relative_performance"]["summary"]["period_return"]["base"])
    )

    if abs((twr_portfolio_return - twr_benchmark_return) - twr_relative_return) > Decimal("0.00001"):
        defects.append(
            {
                "app": "lotus-performance",
                "code": "TWR_RELATIVE_MATH_MISMATCH",
                "message": "Relative performance is not equal to portfolio minus benchmark.",
                "evidence": json.dumps(
                    {
                        "portfolio": str(twr_portfolio_return),
                        "benchmark": str(twr_benchmark_return),
                        "relative": str(twr_relative_return),
                    }
                ),
            }
        )

    if abs(benchmark_only_return - twr_benchmark_return) > Decimal("0.000001"):
        defects.append(
            {
                "app": "lotus-performance",
                "code": "BENCHMARK_RETURN_UNIT_MISMATCH",
                "message": "Dedicated benchmark endpoint and TWR benchmark block do not use the same return unit.",
                "evidence": json.dumps(
                    {
                        "benchmark_endpoint_itd_base_return": str(benchmark_only_return),
                        "twr_benchmark_itd_base_return": str(twr_benchmark_return),
                    }
                ),
            }
        )

    return {
        "benchmark_context": twr_response.get("benchmark_context"),
        "benchmark_endpoint_itd_base_return": str(benchmark_only_return),
        "twr_itd_portfolio_base_return": str(twr_portfolio_return),
        "twr_itd_benchmark_base_return": str(twr_benchmark_return),
        "twr_itd_relative_base_return": str(twr_relative_return),
        "portfolio_daily_points": len(twr_response["results_by_period"]["ITD"]["portfolio"]["breakdowns"].get("daily", [])),
        "benchmark_daily_points": len(twr_response["results_by_period"]["ITD"]["benchmark"]["breakdowns"].get("daily", [])),
        "defects": defects,
    }


def _write_summary_markdown(summary: dict[str, Any], output_markdown_path: Path) -> None:
    defects = summary["core_defects"] + summary["performance"]["defects"]
    lines = [
        "# Cross-App Core -> Performance TWR + Benchmark Validation",
        "",
        f"- Generated at: `{summary['generated_at_utc']}`",
        f"- Portfolio: `{summary['scenario']['portfolio_id']}`",
        f"- Benchmark: `{summary['scenario']['benchmark_id']}`",
        f"- Overall status: `{summary['status']}`",
        "",
        "## Core",
        "",
        f"- Portfolio timeseries observations: `{summary['core'].get('portfolio_timeseries_observations')}`",
        f"- Position timeseries rows: `{summary['core'].get('position_timeseries_rows')}`",
        f"- Assignment benchmark id: `{summary['core'].get('assignment_benchmark_id')}`",
        f"- Composition segment count: `{summary['core'].get('composition_segment_count')}`",
        "",
        "## lotus-performance",
        "",
        f"- Benchmark context: `{json.dumps(summary['performance'].get('benchmark_context'))}`",
        f"- TWR ITD portfolio return: `{summary['performance'].get('twr_itd_portfolio_base_return')}`",
        f"- TWR ITD benchmark return: `{summary['performance'].get('twr_itd_benchmark_base_return')}`",
        f"- TWR ITD relative return: `{summary['performance'].get('twr_itd_relative_base_return')}`",
        f"- Dedicated benchmark ITD return: `{summary['performance'].get('benchmark_endpoint_itd_base_return')}`",
        "",
        "## Defects",
        "",
    ]
    if not defects:
        lines.append("- None")
    else:
        for defect in defects:
            lines.append(f"- `{defect['app']}` `{defect['code']}`: {defect['message']}")
            lines.append(f"  Evidence: `{defect['evidence']}`")
    output_markdown_path.parent.mkdir(parents=True, exist_ok=True)
    output_markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ingestion-base-url", default="http://core-ingestion.dev.lotus")
    parser.add_argument("--control-base-url", default="http://core-control.dev.lotus")
    parser.add_argument("--performance-base-url", default="http://performance.dev.lotus")
    parser.add_argument("--output-json", default="output/cross-app/core-performance-twr-benchmark-validation.json")
    parser.add_argument("--output-markdown", default="output/cross-app/core-performance-twr-benchmark-validation.md")
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

    ids = _build_ids_for_suffix(args.scenario_suffix) if args.scenario_suffix else _build_ids()
    session = requests.Session()
    core_defects: list[dict[str, str]] = []

    if not args.skip_seed:
        _seed_core_data(session, ingestion_base_url=args.ingestion_base_url, ids=ids)
    core_summary = _query_core(session, control_base_url=args.control_base_url, ids=ids)
    performance_summary = _run_performance_validation(session, performance_base_url=args.performance_base_url, ids=ids)

    summary = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "status": "failed" if core_defects or performance_summary["defects"] else "passed",
        "scenario_seed_mode": "reused_existing" if args.skip_seed else "fresh_seeded",
        "scenario": asdict(ids),
        "core": core_summary,
        "performance": performance_summary,
        "core_defects": core_defects,
    }

    output_json_path = Path(args.output_json)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_summary_markdown(summary, Path(args.output_markdown))
    print(json.dumps(summary, indent=2))
    return 1 if summary["status"] != "passed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
