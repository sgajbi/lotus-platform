from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import requests


@dataclass
class ScenarioIds:
    portfolio_id: str
    cash_security_id: str
    aapl_security_id: str
    msft_security_id: str


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


def _build_ids() -> ScenarioIds:
    suffix = datetime.now(UTC).strftime("%H%M%S")
    return _build_ids_for_suffix(suffix)


def _build_ids_for_suffix(suffix: str) -> ScenarioIds:
    return ScenarioIds(
        portfolio_id=f"LIVE_MWR_{suffix}",
        cash_security_id=f"CASH_USD_{suffix}",
        aapl_security_id=f"SEC_AAPL_{suffix}",
        msft_security_id=f"SEC_MSFT_{suffix}",
    )


def _seed_core_data(session: requests.Session, *, ingestion_base_url: str, ids: ScenarioIds) -> None:
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


def _wait_for_core_observations(session: requests.Session, *, query_base_url: str, portfolio_id: str) -> dict[str, Any]:
    return _poll_post_json(
        session,
        f"{query_base_url}/integration/portfolios/{portfolio_id}/analytics/portfolio-timeseries",
        {
            "as_of_date": "2026-03-20",
            "window": {"start_date": "2026-03-16", "end_date": "2026-03-20"},
            "frequency": "daily",
            "consumer_system": "lotus-platform",
        },
        predicate=lambda payload: len(payload.get("observations", [])) == 5,
    )


def _expected_dietz_from_observations(observations: list[dict[str, Any]]) -> Decimal:
    first_observation = observations[0]
    last_observation = observations[-1]
    begin_mv = Decimal(str(first_observation["beginning_market_value"]))
    end_mv = Decimal(str(last_observation["ending_market_value"]))
    net_cash_flow = Decimal("0")
    for observation in observations:
        for cash_flow in observation.get("cash_flows", []):
            amount = cash_flow.get("amount")
            if amount is not None:
                net_cash_flow += Decimal(str(amount))
    denominator = begin_mv + (net_cash_flow / Decimal("2"))
    if denominator == 0:
        return Decimal("0")
    numerator = end_mv - begin_mv - net_cash_flow
    return (numerator / denominator) * Decimal("100")


def _run_validation(
    *,
    core_ingestion_base_url: str,
    core_query_base_url: str,
    performance_base_url: str,
    scenario_suffix: str | None,
    skip_seed: bool,
) -> dict[str, Any]:
    scenario_ids = _build_ids_for_suffix(scenario_suffix) if scenario_suffix else _build_ids()
    defects: list[dict[str, Any]] = []

    with requests.Session() as session:
        if not skip_seed:
            _seed_core_data(session, ingestion_base_url=core_ingestion_base_url, ids=scenario_ids)
        portfolio_timeseries = _wait_for_core_observations(
            session,
            query_base_url=core_query_base_url,
            portfolio_id=scenario_ids.portfolio_id,
        )
        observations = portfolio_timeseries["observations"]
        expected_mwr = _expected_dietz_from_observations(observations)

        mwr_response = _post_json(
            session,
            f"{performance_base_url}/performance/mwr",
            {
                "portfolio_id": scenario_ids.portfolio_id,
                "as_of": "2026-03-20",
                "mwr_method": "DIETZ",
                "input_mode": "stateful",
                "stateful_input": {"window_start_date": "2026-03-16"},
            },
            expected=(200,),
        ).json()

        observed_mwr = Decimal(str(mwr_response["money_weighted_return"]))
        difference = abs(observed_mwr - expected_mwr)
        tolerance = Decimal("0.0001")

        if difference > tolerance:
            defects.append(
                {
                    "app": "lotus-performance",
                    "code": "MWR_STATEFUL_VALUE_MISMATCH",
                    "message": "Stateful MWR does not match the value implied by lotus-core portfolio timeseries.",
                    "evidence": json.dumps(
                        {
                            "expected_money_weighted_return": str(expected_mwr),
                            "observed_money_weighted_return": str(observed_mwr),
                            "difference": str(difference),
                        }
                    ),
                }
            )

    return {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "status": "passed" if not defects else "failed",
        "scenario_seed_mode": "reused_existing" if skip_seed else "fresh_seeded",
        "scenario": asdict(scenario_ids),
        "core": {
            "portfolio_timeseries_observations": len(observations),
            "window_start_date": "2026-03-16",
            "as_of_date": "2026-03-20",
            "first_observation": observations[0],
            "last_observation": observations[-1],
            "expected_dietz_return": str(expected_mwr),
        },
        "performance": {
            "money_weighted_return": str(observed_mwr),
            "method": mwr_response["method"],
            "start_date": mwr_response["start_date"],
            "end_date": mwr_response["end_date"],
            "input_mode": mwr_response["input_mode"],
            "defects": defects,
        },
    }


def _write_outputs(result: dict[str, Any], *, output_json: Path, output_markdown: Path) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# Cross-App Core -> Performance MWR Validation",
        "",
        f"- Generated: {result['generated_at_utc']}",
        f"- Status: {result['status']}",
        f"- Portfolio ID: {result['scenario']['portfolio_id']}",
        "",
        "## Scenario",
        "",
        "This scenario seeds a realistic USD portfolio into lotus-core, waits for analytics timeseries to materialize,",
        "then calls stateful `/performance/mwr` in lotus-performance.",
        "",
        "The expected MWR value is calculated directly from the sourced lotus-core portfolio timeseries using the",
        "same Simple Dietz formula the lotus-performance stateful path should apply:",
        "",
        "`(end_mv - begin_mv - net_cash_flow) / (begin_mv + net_cash_flow / 2) * 100`",
        "",
        "## Core",
        "",
        f"- Portfolio timeseries observations: {result['core']['portfolio_timeseries_observations']}",
        f"- Expected Dietz return: {result['core']['expected_dietz_return']}",
        "",
        "## lotus-performance",
        "",
        f"- Observed money-weighted return: {result['performance']['money_weighted_return']}",
        f"- Method: {result['performance']['method']}",
        f"- Input mode: {result['performance']['input_mode']}",
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
    parser.add_argument("--output-json", default="output/cross-app/core-performance-mwr-validation.json")
    parser.add_argument("--output-markdown", default="output/cross-app/core-performance-mwr-validation.md")
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
