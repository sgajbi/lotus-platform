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

    periods = payload["periods"]
    codes = [item["code"] for item in periods]
    assert codes == ["MTD", "QTD", "YTD", "1Y", "3Y", "5Y", "SI", "EXPLICIT"]

    by_code = {item["code"]: item for item in periods}
    assert by_code["YTD"]["start_rule"] == "first_day_of_anchor_year"
    assert by_code["1Y"]["start_rule"] == "anchor_minus_1_year_plus_1_day"
    assert by_code["QTD"]["start_rule"] == "first_day_of_anchor_quarter"
    assert by_code["EXPLICIT"]["category"] == "explicit"


def test_canonical_performance_period_vocabulary_keeps_ytd_and_1y_distinct():
    payload = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    by_code = {item["code"]: item for item in payload["periods"]}

    assert by_code["YTD"]["semantics"] == "calendar_to_date"
    assert by_code["1Y"]["semantics"] == "trailing_window"
    assert by_code["YTD"]["start_rule"] != by_code["1Y"]["start_rule"]
