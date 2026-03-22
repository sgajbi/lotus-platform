from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
import uuid
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class ValidationConfig:
    ingestion_url: str
    query_url: str
    query_control_plane_url: str
    timeout_seconds: int
    poll_interval_seconds: float


def _post_json(url: str, payload: dict) -> tuple[int, dict | list | str]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        parsed = json.loads(body) if body else body
        return exc.code, parsed


def _poll_until(description: str, timeout_seconds: int, poll_interval: float, predicate):
    deadline = time.time() + timeout_seconds
    last_value = None
    while time.time() < deadline:
        last_value = predicate()
        if last_value is not None:
            return last_value
        time.sleep(poll_interval)
    raise AssertionError(f"{description} did not converge within {timeout_seconds}s: {last_value}")


def _day_list(start_day: str, end_day: str) -> list[str]:
    current = date.fromisoformat(start_day)
    end = date.fromisoformat(end_day)
    days: list[str] = []
    while current <= end:
        days.append(current.isoformat())
        current = current.fromordinal(current.toordinal() + 1)
    return days


def _assert_ingest_accepted(config: ValidationConfig, endpoint: str, payload: dict) -> None:
    status, body = _post_json(config.ingestion_url.rstrip("/") + endpoint, payload)
    if status != 202:
        raise AssertionError(f"Ingest {endpoint} failed with {status}: {body}")


def _query_position_timeseries(
    config: ValidationConfig, portfolio_id: str, start_date: str, end_date: str
) -> dict:
    status, body = _post_json(
        config.query_control_plane_url.rstrip("/")
        + f"/integration/portfolios/{portfolio_id}/analytics/position-timeseries",
        {
            "as_of_date": end_date,
            "window": {"start_date": start_date, "end_date": end_date},
            "consumer_system": "lotus-platform-validator",
            "frequency": "daily",
            "dimensions": [],
            "include_cash_flows": True,
            "filters": {},
            "page": {"page_size": 200},
        },
    )
    if status != 200:
        raise AssertionError(f"position-timeseries query failed with {status}: {body}")
    return body


def _query_portfolio_timeseries(
    config: ValidationConfig, portfolio_id: str, start_date: str, end_date: str
) -> dict:
    status, body = _post_json(
        config.query_control_plane_url.rstrip("/")
        + f"/integration/portfolios/{portfolio_id}/analytics/portfolio-timeseries",
        {
            "as_of_date": end_date,
            "window": {"start_date": start_date, "end_date": end_date},
            "consumer_system": "lotus-platform-validator",
            "frequency": "daily",
            "page": {"page_size": 200},
        },
    )
    if status != 200:
        raise AssertionError(f"portfolio-timeseries query failed with {status}: {body}")
    return body


def _query_reference(config: ValidationConfig, portfolio_id: str, as_of_date: str) -> dict:
    status, body = _post_json(
        config.query_control_plane_url.rstrip("/")
        + f"/integration/portfolios/{portfolio_id}/analytics/reference",
        {
            "as_of_date": as_of_date,
            "consumer_system": "lotus-platform-validator",
        },
    )
    if status != 200:
        raise AssertionError(f"analytics/reference query failed with {status}: {body}")
    return body


def run_validation(config: ValidationConfig) -> dict:
    suffix = uuid.uuid4().hex[:8].upper()
    portfolio_id = f"PLATFORM_TS_{suffix}"
    stock_security_id = f"SEC_EUR_STOCK_{suffix}"
    cash_security_id = f"CASH_{suffix}"
    start_date = "2026-03-16"
    end_date = "2026-03-20"
    seeded_days = _day_list(start_date, end_date)

    _assert_ingest_accepted(
        config,
        "/ingest/portfolios",
        {
            "portfolios": [
                {
                    "portfolio_id": portfolio_id,
                    "base_currency": "USD",
                    "open_date": "2026-03-01",
                    "risk_exposure": "High",
                    "investment_time_horizon": "Long",
                    "portfolio_type": "Discretionary",
                    "booking_center_code": "SG",
                    "client_id": "PLATFORM_QA",
                    "status": "Active",
                }
            ]
        },
    )
    _assert_ingest_accepted(
        config,
        "/ingest/instruments",
        {
            "instruments": [
                {
                    "security_id": stock_security_id,
                    "name": "Platform Euro Stock",
                    "isin": f"EU{suffix}",
                    "currency": "EUR",
                    "product_type": "Equity",
                },
                {
                    "security_id": cash_security_id,
                    "name": "US Dollar",
                    "isin": f"USD_CASH_{suffix}",
                    "currency": "USD",
                    "product_type": "Cash",
                },
            ]
        },
    )
    _assert_ingest_accepted(
        config,
        "/ingest/fx-rates",
        {
            "fx_rates": [
                {
                    "from_currency": "EUR",
                    "to_currency": "USD",
                    "rate_date": day,
                    "rate": str(Decimal("1.10") + Decimal("0.01") * index),
                }
                for index, day in enumerate(seeded_days)
            ]
        },
    )
    _assert_ingest_accepted(
        config,
        "/ingest/business-dates",
        {"business_dates": [{"business_date": start_date}]},
    )
    _assert_ingest_accepted(
        config,
        "/ingest/transactions",
        {
            "transactions": [
                {
                    "transaction_id": f"PLATFORM_DEP_{suffix}",
                    "portfolio_id": portfolio_id,
                    "instrument_id": cash_security_id,
                    "security_id": cash_security_id,
                    "transaction_date": f"{start_date}T00:00:00Z",
                    "transaction_type": "DEPOSIT",
                    "quantity": 10000,
                    "price": 1,
                    "gross_transaction_amount": 10000,
                    "trade_currency": "USD",
                    "currency": "USD",
                },
                {
                    "transaction_id": f"PLATFORM_BUY_{suffix}",
                    "portfolio_id": portfolio_id,
                    "instrument_id": stock_security_id,
                    "security_id": stock_security_id,
                    "transaction_date": f"{start_date}T00:00:00Z",
                    "transaction_type": "BUY",
                    "quantity": 100,
                    "price": 50,
                    "gross_transaction_amount": 5000,
                    "trade_currency": "EUR",
                    "currency": "EUR",
                },
                {
                    "transaction_id": f"PLATFORM_SETTLE_{suffix}",
                    "portfolio_id": portfolio_id,
                    "instrument_id": cash_security_id,
                    "security_id": cash_security_id,
                    "transaction_date": f"{start_date}T00:00:00Z",
                    "transaction_type": "SELL",
                    "quantity": 5500,
                    "price": 1,
                    "gross_transaction_amount": 5500,
                    "trade_currency": "USD",
                    "currency": "USD",
                },
            ]
        },
    )
    _assert_ingest_accepted(
        config,
        "/ingest/market-prices",
        {
            "market_prices": [
                {
                    "security_id": stock_security_id,
                    "price_date": day,
                    "price": str(Decimal("52") + Decimal(index)),
                    "currency": "EUR",
                }
                for index, day in enumerate(seeded_days)
            ]
            + [
                {
                    "security_id": cash_security_id,
                    "price_date": day,
                    "price": "1",
                    "currency": "USD",
                }
                for day in seeded_days[1:]
            ]
        },
    )
    _assert_ingest_accepted(
        config,
        "/ingest/business-dates",
        {"business_dates": [{"business_date": day} for day in seeded_days[1:]]},
    )

    def _reference_ready() -> dict | None:
        payload = _query_reference(config, portfolio_id, end_date)
        return payload if payload.get("performance_end_date") == end_date else None

    def _portfolio_ready() -> dict | None:
        payload = _query_portfolio_timeseries(config, portfolio_id, start_date, end_date)
        observed_dates = {obs["valuation_date"] for obs in payload["observations"]}
        return payload if observed_dates == set(seeded_days) else None

    def _position_ready() -> dict | None:
        payload = _query_position_timeseries(config, portfolio_id, start_date, end_date)
        position_dates = _position_dates_by_security(payload)
        if (
            position_dates.get(stock_security_id) == seeded_days
            and position_dates.get(cash_security_id) == seeded_days
        ):
            return payload
        return None

    reference_payload = _poll_until(
        "analytics reference maturity",
        config.timeout_seconds,
        config.poll_interval_seconds,
        _reference_ready,
    )

    portfolio_payload = _poll_until(
        "portfolio timeseries maturity",
        config.timeout_seconds,
        config.poll_interval_seconds,
        _portfolio_ready,
    )

    position_payload = _poll_until(
        "position timeseries maturity",
        config.timeout_seconds,
        config.poll_interval_seconds,
        _position_ready,
    )

    return {
        "portfolio_id": portfolio_id,
        "seeded_days": seeded_days,
        "reference": {
            "performance_end_date": reference_payload["performance_end_date"],
            "resolved_as_of_date": reference_payload["resolved_as_of_date"],
        },
        "portfolio_timeseries": {
            "observation_dates": [obs["valuation_date"] for obs in portfolio_payload["observations"]],
        },
        "position_timeseries": _position_dates_by_security(position_payload),
        "result": "ok",
    }


def _position_dates_by_security(payload: dict) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in payload["rows"]:
        grouped[row["security_id"]].append(row["valuation_date"])
    return dict(grouped)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate lotus-core seeded analytics maturity through platform-level API flows."
    )
    parser.add_argument("--ingestion-url", default="http://127.0.0.1:8200")
    parser.add_argument("--query-url", default="http://127.0.0.1:8201")
    parser.add_argument("--query-control-plane-url", default="http://127.0.0.1:8202")
    parser.add_argument("--timeout-seconds", type=int, default=240)
    parser.add_argument("--poll-interval-seconds", type=float, default=2.0)
    args = parser.parse_args()

    config = ValidationConfig(
        ingestion_url=args.ingestion_url,
        query_url=args.query_url,
        query_control_plane_url=args.query_control_plane_url,
        timeout_seconds=args.timeout_seconds,
        poll_interval_seconds=args.poll_interval_seconds,
    )

    try:
        result = run_validation(config)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"result": "failed", "error": str(exc)}, indent=2))
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
