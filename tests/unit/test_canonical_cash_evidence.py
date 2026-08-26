from decimal import Decimal

import pytest

from automation.resolve_canonical_cash_evidence import (
    CashEvidenceError,
    build_overview_uri,
    cash_evidence_from_overview,
)


def _overview(*, portfolio_id: str, as_of_date: str, cash_weight_pct: object) -> dict:
    return {
        "portfolio": {"portfolio_id": portfolio_id},
        "as_of_date": as_of_date,
        "effective_as_of_date": as_of_date,
        "overview": {"cash_weight_pct": cash_weight_pct},
        "warnings": [],
        "partial_failures": [],
    }


@pytest.mark.parametrize(
    ("cash_weight_pct", "normalized_cash_weight"),
    [
        (Decimal("10.658553"), "0.10658553"),
        (Decimal("8.589252"), "0.08589252"),
        (
            Decimal("12.34567890123456789012345678901"),
            "0.1234567890123456789012345678901",
        ),
        (Decimal("0"), "0"),
        (Decimal("100"), "1"),
    ],
)
def test_cash_evidence_normalizes_source_percentage_without_rounding(
    cash_weight_pct: Decimal,
    normalized_cash_weight: str,
) -> None:
    evidence = cash_evidence_from_overview(
        _overview(
            portfolio_id="PB_SG_GLOBAL_BAL_001",
            as_of_date="2026-04-10",
            cash_weight_pct=cash_weight_pct,
        ),
        source_uri="http://gateway.dev.lotus/api/v1/workbench/PB_SG_GLOBAL_BAL_001/overview",
        portfolio_id="PB_SG_GLOBAL_BAL_001",
        as_of_date="2026-04-10",
    )

    assert evidence["cash_weight_pct"] == format(cash_weight_pct, "f")
    assert evidence["normalized_cash_weight"] == normalized_cash_weight
    assert evidence["resolved_as_of_date"] == "2026-04-10"
    assert evidence["effective_as_of_date"] == "2026-04-10"
    assert evidence["source_contract"] == "WorkbenchOverviewResponse"


@pytest.mark.parametrize(
    ("payload", "reason"),
    [
        (
            _overview(
                portfolio_id="OTHER",
                as_of_date="2026-04-10",
                cash_weight_pct=Decimal("10"),
            ),
            "CANONICAL_CASH_PORTFOLIO_MISMATCH",
        ),
        (
            _overview(
                portfolio_id="PB_SG_GLOBAL_BAL_001",
                as_of_date="2026-05-03",
                cash_weight_pct=Decimal("10"),
            ),
            "CANONICAL_CASH_DATE_MISMATCH",
        ),
        (
            {
                "portfolio": {"portfolio_id": "PB_SG_GLOBAL_BAL_001"},
                "as_of_date": "2026-04-10",
                "effective_as_of_date": "2026-04-10",
                "warnings": [],
                "partial_failures": [],
            },
            "CANONICAL_CASH_OVERVIEW_MISSING",
        ),
        (
            {
                "as_of_date": "2026-04-10",
                "effective_as_of_date": "2026-04-10",
                "overview": {"cash_weight_pct": Decimal("10")},
                "warnings": [],
                "partial_failures": [],
            },
            "CANONICAL_CASH_PORTFOLIO_MISSING",
        ),
        (
            {
                **_overview(
                    portfolio_id="PB_SG_GLOBAL_BAL_001",
                    as_of_date="2026-04-10",
                    cash_weight_pct=Decimal("10"),
                ),
                "partial_failures": [
                    {
                        "source_service": "lotus-core",
                        "error_code": "UPSTREAM_TIMEOUT",
                    }
                ],
            },
            "CANONICAL_CASH_SOURCE_DEGRADED",
        ),
        (
            {
                **_overview(
                    portfolio_id="PB_SG_GLOBAL_BAL_001",
                    as_of_date="2026-04-10",
                    cash_weight_pct=Decimal("10"),
                ),
                "warnings": ["cash source used a fallback value"],
            },
            "CANONICAL_CASH_SOURCE_DEGRADED",
        ),
        (
            {
                **_overview(
                    portfolio_id="PB_SG_GLOBAL_BAL_001",
                    as_of_date="2026-04-10",
                    cash_weight_pct=Decimal("10"),
                ),
                "effective_as_of_date": "2026-04-09",
            },
            "CANONICAL_CASH_EFFECTIVE_DATE_MISMATCH",
        ),
        (
            _overview(
                portfolio_id="PB_SG_GLOBAL_BAL_001",
                as_of_date="2026-04-10",
                cash_weight_pct="10.0",
            ),
            "CANONICAL_CASH_WEIGHT_INVALID",
        ),
        (
            _overview(
                portfolio_id="PB_SG_GLOBAL_BAL_001",
                as_of_date="2026-04-10",
                cash_weight_pct=True,
            ),
            "CANONICAL_CASH_WEIGHT_INVALID",
        ),
        (
            _overview(
                portfolio_id="PB_SG_GLOBAL_BAL_001",
                as_of_date="2026-04-10",
                cash_weight_pct=float("nan"),
            ),
            "CANONICAL_CASH_WEIGHT_INVALID",
        ),
        (
            _overview(
                portfolio_id="PB_SG_GLOBAL_BAL_001",
                as_of_date="2026-04-10",
                cash_weight_pct=float("inf"),
            ),
            "CANONICAL_CASH_WEIGHT_INVALID",
        ),
        (
            _overview(
                portfolio_id="PB_SG_GLOBAL_BAL_001",
                as_of_date="2026-04-10",
                cash_weight_pct=Decimal("100.01"),
            ),
            "CANONICAL_CASH_WEIGHT_OUT_OF_RANGE",
        ),
    ],
)
def test_cash_evidence_fails_closed_on_untrustworthy_source_payload(
    payload: dict,
    reason: str,
) -> None:
    with pytest.raises(CashEvidenceError, match=reason):
        cash_evidence_from_overview(
            payload,
            source_uri="http://gateway.dev.lotus/source",
            portfolio_id="PB_SG_GLOBAL_BAL_001",
            as_of_date="2026-04-10",
        )


def test_overview_uri_encodes_portfolio_identity_and_business_date() -> None:
    assert build_overview_uri(
        gateway_base_url="http://gateway.dev.lotus/",
        portfolio_id="PB SG/BAL",
        as_of_date="2026-04-10",
    ) == (
        "http://gateway.dev.lotus/api/v1/workbench/PB%20SG%2FBAL/overview"
        "?as_of_date=2026-04-10"
    )
