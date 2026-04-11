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


def test_rfc_0080_slice_2_adds_governed_front_office_runtime_skill() -> None:
    checklist = (ROOT / "rfcs" / "RFC-0080-implementation-checklist.md").read_text(
        encoding="utf-8"
    )
    evidence = (
        ROOT / "rfcs" / "RFC-0080-slice-2-front-office-runtime-skill-evidence.md"
    ).read_text(encoding="utf-8")
    skill_doc = (
        ROOT / "codex" / "skills" / "lotus-front-office-runtime" / "SKILL.md"
    ).read_text(encoding="utf-8")
    skill_ui = (
        ROOT / "codex" / "skills" / "lotus-front-office-runtime" / "agents" / "openai.yaml"
    ).read_text(encoding="utf-8")
    manifest = (ROOT / "codex" / "skills" / "lotus-skill-manifest.json").read_text(
        encoding="utf-8"
    )
    skills_readme = (ROOT / "codex" / "skills" / "README.md").read_text(encoding="utf-8")

    for required_item in (
        "## Slice 2: New Front-Office Runtime Skill",
        "- [x] Add `lotus-front-office-runtime`.",
        "- [x] Prove that the skill routes to validation-plus-evidence rather than screenshot-only success.",
    ):
        assert required_item in checklist

    for required_item in (
        "lotus-front-office-runtime",
        "screenshot-only success",
        "codex/skills/README.md",
        "stale wording",
    ):
        assert required_item in evidence

    for required_item in (
        "name: lotus-front-office-runtime",
        "PB_SG_GLOBAL_BAL_001",
        "Invoke-Canonical-FrontOffice-QA.ps1",
        "Do not accept screenshot-only proof.",
        "Use `lotus-qa-platform-validator` for backend or infrastructure QA",
    ):
        assert required_item in skill_doc

    assert 'display_name: "Lotus Front-Office Runtime"' in skill_ui
    assert '"name": "lotus-front-office-runtime"' in manifest
    assert "automation/Bootstrap-LotusDeveloperEnvironment.ps1" in skills_readme
    assert "Skill synchronization automation is not implemented" not in skills_readme


def test_rfc_0080_slice_3_hardens_existing_skill_boundaries() -> None:
    checklist = (ROOT / "rfcs" / "RFC-0080-implementation-checklist.md").read_text(
        encoding="utf-8"
    )
    evidence = (
        ROOT / "rfcs" / "RFC-0080-slice-3-existing-skill-hardening-evidence.md"
    ).read_text(encoding="utf-8")
    qa_skill = (ROOT / "codex" / "skills" / "lotus-qa-platform-validator" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    pr_skill = (ROOT / "codex" / "skills" / "lotus-pr-premerge-gate" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    frontend_skill = (
        ROOT / "codex" / "skills" / "lotus-frontend-delivery-governance" / "SKILL.md"
    ).read_text(encoding="utf-8")
    backend_skill = (
        ROOT / "codex" / "skills" / "lotus-backend-delivery-governance" / "SKILL.md"
    ).read_text(encoding="utf-8")
    lifecycle_skill = (
        ROOT / "codex" / "skills" / "lotus-validation-resolution-lifecycle" / "SKILL.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "## Slice 3: Hardening Existing Skills",
        "- [x] Tighten `lotus-qa-platform-validator`.",
        "- [x] Tighten `lotus-validation-resolution-lifecycle` where routing overlap exists.",
    ):
        assert required_item in checklist

    for required_item in (
        "`lotus-qa-platform-validator`",
        "`lotus-pr-premerge-gate`",
        "`lotus-frontend-delivery-governance`",
        "`lotus-backend-delivery-governance`",
        "`lotus-validation-resolution-lifecycle`",
        "async GitHub behavior",
        "screenshot-plus-evidence proof",
    ):
        assert required_item in evidence

    assert "Use `lotus-front-office-runtime` instead for:" in qa_skill
    assert "gh pr checks <PR_NUMBER> --watch=false" in pr_skill
    assert "continue useful work while heavy lanes run" in evidence
    assert "use `lotus-front-office-runtime` as the" in frontend_skill
    assert "do not claim UI readiness from backend checks alone" in backend_skill
    assert "compose this skill with `lotus-front-office-runtime`" in lifecycle_skill
