from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_rfc_0077_is_implementation_grade_and_includes_final_slice() -> None:
    rfc = (
        ROOT / "rfcs" / "RFC-0077-workbench-panel-registry-and-evidence-contract.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "# RFC-0077: Workbench Panel Registry and Evidence Contract",
        "## Decision",
        "## Proposed Registry Artifacts",
        "context/contracts/workbench-panel-registry.json",
        "context/contracts/workbench-panel-registry.schema.json",
        "## Registry Model",
        "## State Model",
        "## Ownership and Boundary Rules",
        "### Slice 1: Registry Specification and Testable Contract",
        "### Slice 2: Workbench Validator Adoption",
        "### Slice 3: Gateway and Panel Supportability Alignment",
        "### Slice 4: Documentation, Agent Context, Skill Alignment, and Branch Hygiene",
        "## Skills, Context, and Documentation Implications",
        "## Approval Request",
        "supported_blank",
        "performance.evidence",
        "RFC-0076",
        "RFC-0079",
    ):
        assert required_item in rfc


def test_rfc_0077_defines_minimum_panel_inventory_and_governed_acceptance_rules() -> None:
    rfc = (
        ROOT / "rfcs" / "RFC-0077-workbench-panel-registry-and-evidence-contract.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "portfolio.summary",
        "portfolio.detailed",
        "performance.summary",
        "performance.analysis.contribution",
        "performance.analysis.attribution",
        "performance.advisor_brief",
        "performance.risk.snapshot",
        "performance.risk.drawdown",
        "performance.risk.concentration",
        "performance.risk.rolling",
        "performance.risk.historical_attribution",
        "performance.evidence",
        "supported blank panels fail validation",
        "partial and unavailable panels include owner and rationale",
        "new governed panel work requires registry updates",
    ):
        assert required_item in rfc
