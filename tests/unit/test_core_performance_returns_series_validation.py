from __future__ import annotations

import importlib.util
import sys
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUTOMATION_DIR = ROOT / "automation"
VALIDATOR_PATH = AUTOMATION_DIR / "core_performance_returns_series_validation.py"


def _load_module():
    if str(AUTOMATION_DIR) not in sys.path:
        sys.path.insert(0, str(AUTOMATION_DIR))
    spec = importlib.util.spec_from_file_location("returns_series_validation", VALIDATOR_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _series(*, active_return: str = "0.015") -> dict:
    return {
        "portfolio_returns": [{"date": "2026-03-16", "return_value": "0.020"}],
        "benchmark_returns": [{"date": "2026-03-16", "return_value": "0.005"}],
        "active_returns": [{"date": "2026-03-16", "return_value": active_return}],
        "cumulative_portfolio_returns": [{"return_value": "0.020"}],
        "cumulative_benchmark_returns": [{"return_value": "0.005"}],
        "cumulative_active_returns": [{"return_value": active_return}],
    }


def test_active_arithmetic_defect_allows_exact_portfolio_minus_benchmark() -> None:
    validator = _load_module()
    defects: list[dict[str, str]] = []

    validator._append_active_arithmetic_defect(defects, series=_series())

    assert defects == []


def test_active_arithmetic_defect_records_first_mismatch_with_safe_evidence() -> None:
    validator = _load_module()
    defects: list[dict[str, str]] = []

    validator._append_active_arithmetic_defect(defects, series=_series(active_return="0.010"))

    assert [defect["code"] for defect in defects] == [
        "RETURNS_SERIES_ACTIVE_ARITHMETIC_MISMATCH"
    ]
    assert '"date": "2026-03-16"' in defects[0]["evidence"]
    assert '"portfolio_return": "0.020"' in defects[0]["evidence"]


def test_cumulative_mismatch_helper_records_only_out_of_tolerance_defects() -> None:
    validator = _load_module()
    defects: list[dict[str, str]] = []

    validator._append_cumulative_mismatch(
        defects,
        actual=Decimal("1.00001"),
        expected=Decimal("1.00000"),
        code="WITHIN_TOLERANCE",
        message="Within tolerance.",
        actual_name="actual",
        expected_name="expected",
    )
    validator._append_cumulative_mismatch(
        defects,
        actual=Decimal("1.1"),
        expected=Decimal("1.0"),
        code="OUT_OF_TOLERANCE",
        message="Out of tolerance.",
        actual_name="actual",
        expected_name="expected",
    )

    assert [defect["code"] for defect in defects] == ["OUT_OF_TOLERANCE"]
    assert defects[0]["message"] == "Out of tolerance."
