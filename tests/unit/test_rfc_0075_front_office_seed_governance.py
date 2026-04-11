from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_rfc_0075_slice_one_baseline_is_governed_and_traceable() -> None:
    rfc = (
        ROOT / "rfcs" / "RFC-0075-canonical-front-office-portfolio-seed-and-demo-validation-system.md"
    ).read_text(encoding="utf-8")
    checklist = (ROOT / "rfcs" / "RFC-0075-implementation-checklist.md").read_text(
        encoding="utf-8"
    )
    baseline = (ROOT / "rfcs" / "RFC-0075-slice-1-baseline-diagnostics.md").read_text(
        encoding="utf-8"
    )

    assert "Status: Approved - Slice 1 Complete" in rfc
    assert "`RFC-0075-slice-1-baseline-diagnostics.md`" in rfc
    assert "- Status: Slice 1 complete" in checklist

    for required_item in (
        "- [x] RFC approved for Slice 1 implementation.",
        "- [x] Canonical portfolio ID confirmed as `PB_SG_GLOBAL_BAL_001`.",
        "- [x] Canonical benchmark ID confirmed as `BMK_PB_GLOBAL_BALANCED_60_40`.",
        "- [x] Record `PORT_SMOKE_%` pollution status.",
        "- [x] Record gateway/workbench mapping gaps separately from upstream calculation gaps.",
    ):
        assert required_item in checklist

    for required_item in (
        "# RFC-0075 Slice 1 Baseline Diagnostics",
        "PB_SG_GLOBAL_BAL_001",
        "BMK_PB_GLOBAL_BALANCED_60_40",
        "2026-04-10",
        "PORT_SMOKE_*",
        "performance_end_date",
        "DPM_SUPPORTABILITY_POSTGRES_DSN_REQUIRED",
        "no containers, images, or volumes",
        "Slice 2 may start after this baseline is accepted.",
    ):
        assert required_item in baseline


def test_rfc_0075_keeps_front_office_demo_from_becoming_ui_only_fixture() -> None:
    rfc = (
        ROOT / "rfcs" / "RFC-0075-canonical-front-office-portfolio-seed-and-demo-validation-system.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "production-grade local proving ground",
        "Unsupported panels must not be faked",
        "The seed may be synthetic, but the calculations must use normal product code paths.",
        "Transaction economics must observe these invariants:",
        "Readiness must be evaluated against the fixed canonical demo as-of date.",
        "Every workbench panel must be classified before implementation",
        "Diagnostic screenshots captured before validation passes must use a `diagnostic-` prefix",
        "a clean run produces a machine-readable validation summary",
    ):
        assert required_item in rfc
