from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_rfc_0078_is_implementation_grade_and_includes_final_slice() -> None:
    rfc = (
        ROOT / "rfcs" / "RFC-0078-modular-front-office-validation-framework.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "# RFC-0078: Modular Front-Office Validation Framework",
        "## Decision",
        "## Scope",
        "## Operator Stability Rule",
        "## Proposed Architecture",
        "contract-metadata.mjs",
        "panel-classification.mjs",
        "evidence-summary-writer.mjs",
        "## Ownership and Boundary Rules",
        "### Slice 1: Extract Core Validation Types and Result Models",
        "### Slice 5: Registry-Driven Panel Classification",
        "### Slice 6: Documentation, Agent Context, Skill Alignment, and Branch Hygiene",
        "## Skills, Context, and Documentation Implications",
        "## Approval Request",
        "RFC-0076",
        "RFC-0077",
    ):
        assert required_item in rfc


def test_rfc_0078_preserves_operator_stability_and_dead_code_removal_posture() -> None:
    rfc = (
        ROOT / "rfcs" / "RFC-0078-modular-front-office-validation-framework.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "npm run live:stack:up",
        "npm run live:validate",
        "npm run live:stack:down",
        "Invoke-Canonical-FrontOffice-QA.ps1",
        "Dead code should be removed",
        "remove obsolete helpers and dead code",
        "fail the slice if extraction only relocates complexity",
    ):
        assert required_item in rfc
