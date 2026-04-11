from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_rfc_0081_is_implementation_grade_and_has_final_slice() -> None:
    rfc = (
        ROOT / "rfcs" / "RFC-0081-lotus-workbench-ui-uplift-and-advisory-lifecycle-integration.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "# RFC-0081: Lotus Workbench UI Uplift and Advisory Lifecycle Integration",
        "## Decision",
        "## Scope",
        "## Governed Source Of Truth",
        "## Architecture and Technology Review",
        "## Technical Decision Summary",
        "## Skills, Context, and Documentation Implications",
        "### Slice 10: Documentation, Agent Context, Skill Alignment, and Branch Hygiene",
        "## Acceptance Criteria",
        "RFC-0076",
        "RFC-0077",
        "RFC-0078",
        "RFC-0079",
        "RFC-0080",
    ):
        assert required_item in rfc


def test_rfc_0081_bakes_visual_and_operating_patterns_into_the_contract() -> None:
    rfc = (
        ROOT / "rfcs" / "RFC-0081-lotus-workbench-ui-uplift-and-advisory-lifecycle-integration.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "## Visual and Interaction Patterns Derived From The References",
        "### Pattern 1: Entity-anchored shell header",
        "### Pattern 5: Decision rail and workflow rail",
        "### Pattern 8: Client artifact as product surface, not export button",
        "### Typography and font standards",
        "### Navigation and information architecture requirements",
        "### Codebase cleanup and dead-code expectations",
        "## Naming and Domain Language Standards",
        "## Frontend Topology and Code-Organization Standards",
        "## Agentic AI Product Readiness",
        "AI search and semantic discovery",
        "### Modern feature readiness requirements",
        "`Portfolio`",
        "`Performance`",
        "`Risk`",
        "`Proposal`",
        "`Advisory`",
        "AI-assisted",
    ):
        assert required_item in rfc


def test_rfc_0081_checklist_exists_and_matches_the_slice_model() -> None:
    checklist = (ROOT / "rfcs" / "RFC-0081-implementation-checklist.md").read_text(
        encoding="utf-8"
    )

    for required_item in (
        "# RFC-0081 Implementation Checklist",
        "## Slice 1: Current-State Assessment and UI Target Model",
        "## Slice 7: Micro-Frontend Composition and Extension Model",
        "## Slice 10: Documentation, Agent Context, Skill Alignment, and Branch Hygiene",
        "- [ ] Define professional typography, sizing, and naming standards for the shell and shared UI layer.",
        "- [ ] Define shell and navigation performance expectations.",
        "- [ ] Define code-organization and file-structure standards for the modular UI topology.",
        "- [ ] Define agentic AI extension standards for future workflow-native assist surfaces.",
        "- [ ] Define architecture and UX standards for AI search and command-driven discovery surfaces.",
        "- [ ] Dead code and obsolete frontend patterns exposed by the uplift are removed.",
        "- [ ] Banking-grade naming, typography, and code organization are standardized across the uplift.",
        "- [ ] The shell and module model remain compatible with future agentic AI workflow surfaces.",
        "- [ ] The shell and gateway model remain compatible with future AI search and modern discovery features.",
        "- [ ] Update agent guidance if the shell and module model materially changes runtime or routing behavior.",
    ):
        assert required_item in checklist
