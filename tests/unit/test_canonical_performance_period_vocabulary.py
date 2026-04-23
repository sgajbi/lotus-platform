from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VOCAB_PATH = (
    ROOT
    / "platform-contracts"
    / "domain-vocabulary"
    / "canonical-performance-periods.v1.json"
)


def test_canonical_performance_period_vocabulary_contract_is_complete():
    payload = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))

    assert payload["contractVersion"] == "v1"
    assert payload["domain"] == "performance_periods"
    assert payload["governance"]["newApiRule"]

    periods = payload["canonicalPeriods"]
    codes = [item["canonical_code"] for item in periods]
    assert codes == [
        "1D",
        "2D",
        "5D",
        "10D",
        "1M",
        "3M",
        "6M",
        "MTD",
        "QTD",
        "YTD",
        "1Y",
        "2Y",
        "3Y",
        "5Y",
        "10Y",
        "SI",
        "YEAR",
        "EXPLICIT",
    ]

    by_code = {item["canonical_code"]: item for item in periods}
    assert by_code["YTD"]["start_rule"] == "first_day_of_anchor_year"
    assert by_code["1Y"]["start_rule"] == "anchor_minus_1_year_plus_1_day"
    assert by_code["QTD"]["start_rule"] == "first_day_of_anchor_quarter"
    assert by_code["EXPLICIT"]["category"] == "explicit"
    assert by_code["YEAR"]["minimum_required_fields"] == ["year"]
    assert by_code["SI"]["minimum_required_fields"] == ["anchor_date", "inception_date"]


def test_canonical_performance_period_vocabulary_keeps_ytd_and_1y_distinct():
    payload = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    by_code = {item["canonical_code"]: item for item in payload["canonicalPeriods"]}

    assert by_code["YTD"]["semantics"] == "calendar_to_date"
    assert by_code["1Y"]["semantics"] == "trailing_calendar_year_window"
    assert by_code["YTD"]["start_rule"] != by_code["1Y"]["start_rule"]


def test_canonical_performance_period_vocabulary_aliases_are_unambiguous():
    payload = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    periods = payload["canonicalPeriods"]
    codes = {item["canonical_code"] for item in periods}

    alias_to_code: dict[str, str] = {}
    for item in periods:
        assert item["canonical_code"].isupper()
        assert item["minimum_required_fields"]
        for alias in item["accepted_aliases"]:
            assert alias.isupper()
            assert alias not in codes
            assert alias not in alias_to_code
            alias_to_code[alias] = item["canonical_code"]

    assert alias_to_code["ONE_YEAR"] == "1Y"
    assert alias_to_code["THREE_YEAR"] == "3Y"
    assert alias_to_code["FIVE_YEAR"] == "5Y"
    assert alias_to_code["ITD"] == "SI"
    assert alias_to_code["CUSTOM"] == "EXPLICIT"


def test_canonical_performance_period_vocabulary_covers_current_lotus_dialects():
    payload = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    periods = payload["canonicalPeriods"]
    codes = {item["canonical_code"] for item in periods}
    aliases = {
        alias
        for item in periods
        for alias in item["accepted_aliases"]
    }
    accepted_values = codes | aliases

    performance_periods = {"MTD", "QTD", "YTD", "ITD", "1Y", "3Y", "5Y", "EXPLICIT"}
    performance_workspace_periods = {
        "1D",
        "2D",
        "5D",
        "10D",
        "1M",
        "3M",
        "6M",
        "YTD",
        "1Y",
        "2Y",
        "5Y",
        "10Y",
        "SI",
        "EXPLICIT",
    }
    performance_returns_series_periods = {
        "MTD",
        "QTD",
        "YTD",
        "ONE_YEAR",
        "THREE_YEAR",
        "FIVE_YEAR",
        "SI",
        "YEAR",
    }
    risk_periods = {
        "EXPLICIT",
        "YEAR",
        "MTD",
        "QTD",
        "YTD",
        "ONE_YEAR",
        "THREE_YEAR",
        "FIVE_YEAR",
        "SI",
    }
    report_review_periods = {"1M", "3M", "YTD", "5Y", "SI", "3Y"}

    assert performance_periods <= accepted_values
    assert performance_workspace_periods <= accepted_values
    assert performance_returns_series_periods <= accepted_values
    assert risk_periods <= accepted_values
    assert report_review_periods <= accepted_values


def test_canonical_performance_period_vocabulary_documents_rejected_legacy_values():
    payload = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    rejected = {
        item["value"]: item["replacement"]
        for item in payload["deprecatedOrRejectedValues"]
    }

    assert rejected["Y1"] == "1Y"
    assert rejected["Y3"] == "3Y"
    assert rejected["Y5"] == "5Y"
    assert rejected["ROLLING"] == "EXPLICIT"
