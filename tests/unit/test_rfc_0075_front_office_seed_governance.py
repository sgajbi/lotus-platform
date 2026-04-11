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

    assert "Status: Approved - Slice 6 Complete" in rfc
    assert "`RFC-0075-slice-1-baseline-diagnostics.md`" in rfc
    assert "`RFC-0075-slice-2-docker-ingress-startup-evidence.md`" in rfc
    assert "`RFC-0075-slice-3-core-seed-data-evidence.md`" in rfc
    assert "`RFC-0075-slice-4-derived-state-readiness-evidence.md`" in rfc
    assert "`RFC-0075-slice-5-performance-risk-calculation-evidence.md`" in rfc
    assert "`RFC-0075-slice-6-panel-classification-evidence.md`" in rfc
    assert "- Status: Slice 6 complete" in checklist

    for required_item in (
        "- [x] RFC approved for Slice 1 implementation.",
        "- [x] Canonical portfolio ID confirmed as `PB_SG_GLOBAL_BAL_001`.",
        "- [x] Canonical benchmark ID confirmed as `BMK_PB_GLOBAL_BALANCED_60_40`.",
        "- [x] Record `PORT_SMOKE_%` pollution status.",
        "- [x] Record gateway/workbench mapping gaps separately from upstream calculation gaps.",
        "- [x] Standardize clean Docker teardown.",
        "- [x] Remove stale local Lotus image ambiguity when full clean mode is selected.",
        "- [x] Emit a run summary with cleanup scope and service startup evidence.",
        "- [x] Rebuild canonical transaction economics.",
        "- [x] Ensure market prices cover every instrument through the ready date.",
        "- [x] Add tests for portfolio economic sanity and date coverage.",
        "- [x] Validate portfolio timeseries reaches ready date.",
        "- [x] Validate analytics reference `performance_end_date` is current.",
        "- [x] Add focused tests for readiness checks.",
        "- [x] Validate contribution detail rows.",
        "- [x] Validate attribution detail rows or governed fallback.",
        "- [x] Validate risk row/window/contributor counts.",
        "- [x] Tighten workbench panel checks to fail on unsupported blank panels.",
        "- [x] Classify each panel as supported, intentionally empty, partial, unavailable, or out of scope.",
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


def test_rfc_0075_slice_two_startup_evidence_is_governed_and_traceable() -> None:
    evidence = (
        ROOT / "rfcs" / "RFC-0075-slice-2-docker-ingress-startup-evidence.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "# RFC-0075 Slice 2 Docker, Ingress, and Startup Evidence",
        "Invoke-Canonical-FrontOffice-QA.ps1 -Clean -RemoveImages",
        "Invoke-Canonical-FrontOffice-QA.ps1 -Clean -BringUp -BuildImages -KeepRunning",
        "Containers after clean: 0",
        "generatedAt: 2026-04-11T09:59:13.987Z",
        "workbench.dev.lotus",
        "gateway.dev.lotus",
        "lotus-manage integration capabilities",
        "lotus-report integration capabilities",
        "Validate-LotusFrontOfficeCanonical.ps1",
        "allowed Node browser-validation failures to appear as a successful PowerShell script run",
        "Evidence support remains degraded by current contract posture",
    ):
        assert required_item in evidence


def test_rfc_0075_slice_three_seed_evidence_is_governed_and_traceable() -> None:
    evidence = (ROOT / "rfcs" / "RFC-0075-slice-3-core-seed-data-evidence.md").read_text(
        encoding="utf-8"
    )

    for required_item in (
        "# RFC-0075 Slice 3 Core Seed Data Evidence",
        "fixed canonical as-of date `2026-04-10`",
        "future projected withdrawal",
        "EUR/USD FX, benchmark return, and USD risk-free coverage reach `2026-05-10`",
        "17 passed in 0.50s",
        "PORT_SMOKE_% portfolio count: 0",
        "FO_EQ_AAPL_US max market price date: 2026-04-10",
        "report_end_date: 2025-05-04",
        "Slice 4 must fix stale `performance_end_date`",
    ):
        assert required_item in evidence


def test_rfc_0075_slice_four_derived_state_evidence_is_governed_and_traceable() -> None:
    evidence = (
        ROOT / "rfcs" / "RFC-0075-slice-4-derived-state-readiness-evidence.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "# RFC-0075 Slice 4 Derived-State Readiness Evidence",
        "legacy prior-day portfolio-timeseries dependency",
        "42 passed in 1.18s",
        "5 passed in 37.65s",
        "'analytics_performance_end_date': '2026-04-10'",
        "portfolio_timeseries max(date)=2026-04-17",
        "performance_end_date=2026-04-10",
        "Live canonical Workbench validation passed for PB_SG_GLOBAL_BAL_001",
        "performance-risk-live.png",
        "contribution and attribution row counts",
    ):
        assert required_item in evidence


def test_rfc_0075_slice_five_calculation_evidence_is_governed_and_traceable() -> None:
    evidence = (
        ROOT / "rfcs" / "RFC-0075-slice-5-performance-risk-calculation-evidence.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "# RFC-0075 Slice 5 Performance and Risk Calculation Evidence",
        "calculationChecks",
        "Performance calculation sanity",
        '"portfolioReturnPct": 26.70474',
        '"contributionRows": 4',
        '"attributionState": "partial"',
        "Risk calculation sanity",
        '"readyMetricCount": 6',
        '"rollingWindowCount": 4',
        '"attributionContributorCount": 7',
        "fallback_available=true",
        "Longer rolling windows are emitted but may be warm-up only",
    ):
        assert required_item in evidence


def test_rfc_0075_slice_six_panel_classification_evidence_is_governed_and_traceable() -> None:
    evidence = (
        ROOT / "rfcs" / "RFC-0075-slice-6-panel-classification-evidence.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "# RFC-0075 Slice 6 Panel Classification Evidence",
        "panelClassifications",
        "supported panel is recorded as blank",
        '"panel": "performance.summary"',
        '"panel": "performance.analysis.attribution"',
        '"state": "partial"',
        '"panel": "performance.evidence"',
        '"state": "unavailable"',
        '"panel": "risk.historical_attribution"',
        "fallbackAvailable=true",
        "UI must render a truthful unavailable/degraded state",
    ):
        assert required_item in evidence


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
