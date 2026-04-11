from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_rfc_0080_is_implementation_grade_and_includes_final_slice() -> None:
    rfc = (
        ROOT / "rfcs" / "RFC-0080-lotus-agent-runtime-demo-skill-pack-and-guidance-hardening.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "# RFC-0080: Lotus Agent Runtime, Demo Skill Pack, and Guidance Hardening",
        "## Decision",
        "## Scope",
        "## Agent Routing Rule",
        "## Governed Source of Truth",
        "lotus-front-office-runtime",
        "### Slice 1: Skill Inventory Review and Routing Map",
        "### Slice 6: Documentation, Agent Context, Skill Alignment, and Branch Hygiene",
        "## Skills, Context, and Documentation Implications",
        "## Approval Request",
        "RFC-0075",
        "RFC-0076",
        "RFC-0077",
        "RFC-0078",
        "RFC-0079",
    ):
        assert required_item in rfc


def test_rfc_0080_requires_governed_runtime_and_async_github_behavior() -> None:
    rfc = (
        ROOT / "rfcs" / "RFC-0080-lotus-agent-runtime-demo-skill-pack-and-guidance-hardening.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "canonical-front-office-local-runtime.md",
        "Invoke-Canonical-FrontOffice-QA.ps1",
        "PB_SG_GLOBAL_BAL_001",
        "screenshots without validation evidence are not sufficient proof",
        "push, enable auto-merge when appropriate, and continue useful work",
        "poll asynchronously rather than idling",
    ):
        assert required_item in rfc


def test_rfc_0080_requires_inventory_cleanup_and_conscious_no_change_review() -> None:
    rfc = (
        ROOT / "rfcs" / "RFC-0080-lotus-agent-runtime-demo-skill-pack-and-guidance-hardening.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "Dead guidance should be removed",
        "explicit keep, tighten, remove, and add decisions",
        "This RFC must also include a conscious review of what should not change.",
        "If a skill or context document already reflects the required behavior",
    ):
        assert required_item in rfc


def test_rfc_0080_slice_1_artifacts_exist_and_capture_routing_decisions() -> None:
    checklist = (ROOT / "rfcs" / "RFC-0080-implementation-checklist.md").read_text(
        encoding="utf-8"
    )
    evidence = (
        ROOT / "rfcs" / "RFC-0080-slice-1-skill-inventory-routing-evidence.md"
    ).read_text(encoding="utf-8")
    routing_map = (ROOT / "context" / "LOTUS-SKILL-ROUTING-MAP.md").read_text(
        encoding="utf-8"
    )

    for required_item in (
        "## Slice 1: Skill Inventory Review and Routing Map",
        "## Slice 6: Documentation, Agent Context, Skill Alignment, and Branch Hygiene",
        "Add `lotus-front-office-runtime`.",
    ):
        assert required_item in checklist

    for required_item in (
        "`lotus-front-office-runtime`",
        "`lotus-qa-platform-validator`",
        "`lotus-pr-premerge-gate`",
        "defer actual skill removal until replacement",
    ):
        assert required_item in evidence

    for required_item in (
        "# Lotus Skill Routing Map",
        "Routing Precedence",
        "lotus-front-office-runtime",
        "Invoke-Canonical-FrontOffice-QA.ps1",
        "Do not use screenshot capture alone as proof",
    ):
        assert required_item in routing_map
