#!/usr/bin/env python3
"""Resolve date-aligned canonical portfolio cash evidence for Manage health seeding."""

from __future__ import annotations

import argparse
import json
import math
import sys
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


class CashEvidenceError(ValueError):
    """Raised when the source response cannot support a mandate-health calculation."""


def build_overview_uri(
    *, gateway_base_url: str, portfolio_id: str, as_of_date: str
) -> str:
    query = urlencode({"as_of_date": as_of_date})
    return (
        f"{gateway_base_url.rstrip('/')}/api/v1/workbench/"
        f"{quote(portfolio_id, safe='')}/overview?{query}"
    )


def cash_evidence_from_overview(
    payload: Mapping[str, Any],
    *,
    source_uri: str,
    portfolio_id: str,
    as_of_date: str,
) -> dict[str, str]:
    portfolio = payload.get("portfolio")
    if not isinstance(portfolio, Mapping):
        raise CashEvidenceError("CANONICAL_CASH_PORTFOLIO_MISSING")

    observed_portfolio_id = portfolio.get("portfolio_id")
    if observed_portfolio_id != portfolio_id:
        raise CashEvidenceError("CANONICAL_CASH_PORTFOLIO_MISMATCH")

    observed_as_of_date = payload.get("as_of_date")
    if observed_as_of_date != as_of_date:
        raise CashEvidenceError("CANONICAL_CASH_DATE_MISMATCH")
    effective_as_of_date = payload.get("effective_as_of_date")
    if effective_as_of_date != as_of_date:
        raise CashEvidenceError("CANONICAL_CASH_EFFECTIVE_DATE_MISMATCH")

    overview = payload.get("overview")
    if not isinstance(overview, Mapping):
        raise CashEvidenceError("CANONICAL_CASH_OVERVIEW_MISSING")

    raw_cash_weight = overview.get("cash_weight_pct")
    if isinstance(raw_cash_weight, bool) or not isinstance(
        raw_cash_weight, (Decimal, int, float)
    ):
        raise CashEvidenceError("CANONICAL_CASH_WEIGHT_INVALID")
    if isinstance(raw_cash_weight, float) and not math.isfinite(raw_cash_weight):
        raise CashEvidenceError("CANONICAL_CASH_WEIGHT_INVALID")

    try:
        cash_weight_pct = Decimal(str(raw_cash_weight))
    except InvalidOperation as exc:
        raise CashEvidenceError("CANONICAL_CASH_WEIGHT_INVALID") from exc
    if not cash_weight_pct.is_finite() or cash_weight_pct < 0 or cash_weight_pct > 100:
        raise CashEvidenceError("CANONICAL_CASH_WEIGHT_OUT_OF_RANGE")

    sign, digits, exponent = cash_weight_pct.as_tuple()
    normalized_cash_weight = Decimal((sign, digits, exponent - 2))
    if normalized_cash_weight == normalized_cash_weight.to_integral():
        normalized_cash_weight = normalized_cash_weight.to_integral()
    return {
        "state": "ready",
        "source_service": "lotus-gateway",
        "source_contract": "WorkbenchOverviewResponse",
        "source_uri": source_uri,
        "portfolio_id": portfolio_id,
        "requested_as_of_date": as_of_date,
        "resolved_as_of_date": str(observed_as_of_date),
        "effective_as_of_date": str(effective_as_of_date),
        "cash_weight_pct": _decimal_text(cash_weight_pct),
        "normalized_cash_weight": _decimal_text(normalized_cash_weight),
    }


def fetch_cash_evidence(
    *, gateway_base_url: str, portfolio_id: str, as_of_date: str, timeout_seconds: float
) -> dict[str, str]:
    source_uri = build_overview_uri(
        gateway_base_url=gateway_base_url,
        portfolio_id=portfolio_id,
        as_of_date=as_of_date,
    )
    request = Request(
        source_uri,
        headers={
            "Accept": "application/json",
            "X-Correlation-Id": f"corr-canonical-cash-{portfolio_id}-{as_of_date}",
        },
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:  # noqa: S310
            payload = json.loads(
                response.read().decode("utf-8"),
                parse_float=Decimal,
                parse_int=Decimal,
            )
    except HTTPError as exc:
        raise CashEvidenceError(f"CANONICAL_CASH_SOURCE_HTTP_{exc.code}") from exc
    except (URLError, TimeoutError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CashEvidenceError("CANONICAL_CASH_SOURCE_UNAVAILABLE") from exc

    if not isinstance(payload, Mapping):
        raise CashEvidenceError("CANONICAL_CASH_RESPONSE_INVALID")
    return cash_evidence_from_overview(
        payload,
        source_uri=source_uri,
        portfolio_id=portfolio_id,
        as_of_date=as_of_date,
    )


def _decimal_text(value: Decimal) -> str:
    return format(value, "f")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gateway-base-url", required=True)
    parser.add_argument("--portfolio-id", required=True)
    parser.add_argument("--as-of-date", required=True)
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    args = parser.parse_args(argv)

    try:
        evidence = fetch_cash_evidence(
            gateway_base_url=args.gateway_base_url,
            portfolio_id=args.portfolio_id,
            as_of_date=args.as_of_date,
            timeout_seconds=args.timeout_seconds,
        )
    except CashEvidenceError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(evidence, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
