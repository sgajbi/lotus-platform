from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_front_office_runtime_route_is_unambiguous() -> None:
    routing_map = _read(ROOT / "context" / "LOTUS-SKILL-ROUTING-MAP.md")
    agents_contract = _read(ROOT / "context" / "AGENTS-OPERATING-CONTRACT.md")
    ramp_up = _read(ROOT / "docs" / "onboarding" / "LOTUS-AGENT-RAMP-UP.md")
    runtime_skill = _read(ROOT / "codex" / "skills" / "lotus-front-office-runtime" / "SKILL.md")
    qa_skill = _read(ROOT / "codex" / "skills" / "lotus-qa-platform-validator" / "SKILL.md")
    frontend_skill = _read(ROOT / "codex" / "skills" / "lotus-frontend-delivery-governance" / "SKILL.md")

    assert "| Bring up canonical Workbench runtime, validate populated panels, generate governed demo screenshots | `lotus-front-office-runtime` |" in routing_map
    assert "PB_SG_GLOBAL_BAL_001" in routing_map
    assert "choose `lotus-front-office-runtime` first" in agents_contract
    assert "Treat `lotus-front-office-runtime` as the primary skill route for these tasks." in ramp_up
    assert "Do not accept screenshot-only proof." in runtime_skill
    assert "Use `lotus-front-office-runtime` instead for:" in qa_skill
    assert "use `lotus-front-office-runtime` as the" in frontend_skill


def test_async_github_posture_is_reinforced_across_guidance() -> None:
    pr_skill = _read(ROOT / "codex" / "skills" / "lotus-pr-premerge-gate" / "SKILL.md")
    qa_skill = _read(ROOT / "codex" / "skills" / "lotus-qa-platform-validator" / "SKILL.md")
    lifecycle_skill = _read(ROOT / "codex" / "skills" / "lotus-validation-resolution-lifecycle" / "SKILL.md")
    ramp_up = _read(ROOT / "docs" / "onboarding" / "LOTUS-AGENT-RAMP-UP.md")

    assert "gh pr checks <PR_NUMBER> --watch=false" in pr_skill
    assert "let GitHub execute the heavy lanes" in qa_skill
    assert "let GitHub run heavy PR checks where possible" in lifecycle_skill
    assert "gh pr checks <pr-number> --watch=false" in ramp_up


def test_platform_automation_ops_uses_task_ledger_contract() -> None:
    routing_map = _read(ROOT / "context" / "LOTUS-SKILL-ROUTING-MAP.md")
    skill = _read(ROOT / "codex" / "skills" / "platform-automation-ops" / "SKILL.md")
    profile_guide = _read(
        ROOT / "codex" / "skills" / "platform-automation-ops" / "references" / "profile-guide.md"
    )
    validator = _read(ROOT / "automation" / "validate_lotus_skill_alignment.py")

    assert "Launch or monitor detached platform automation profiles" in routing_map
    assert "RFC-0096 governed delegation evidence" in routing_map
    assert "AGENT-CONTEXT-AND-TASK-LEDGER.md" in skill
    assert "engineering-task-ledger-contract.v1.json" in skill
    assert "delegation-policy-contract.v1.json" in skill
    assert "Govern Delegated Work" in skill
    assert "engineering_task_id" in skill
    assert "no PR merge" in skill
    assert "no wiki" in skill
    assert "Do not summarize detached work from chat memory alone" in skill
    assert "cleanup_state" in profile_guide
    assert "Do not translate `LOST` into success" in profile_guide.replace("\n", " ")
    assert '"platform-automation-ops"' in validator
    assert '"engineering_task_id"' in validator


def test_stale_screenshot_only_and_platform_stack_patterns_are_rejected() -> None:
    routing_map = _read(ROOT / "context" / "LOTUS-SKILL-ROUTING-MAP.md")
    engineering_context = _read(ROOT / "context" / "LOTUS-ENGINEERING-CONTEXT.md")
    ramp_up = _read(ROOT / "docs" / "onboarding" / "LOTUS-AGENT-RAMP-UP.md")
    deployed_agents_path = Path(r"C:\Users\Sandeep\.codex\AGENTS.md")
    deployed_agents = (
        deployed_agents_path
        if deployed_agents_path.exists()
        else ROOT / "context" / "AGENTS-OPERATING-CONTRACT.md"
    ).read_text(encoding="utf-8")
    runtime_skill = _read(ROOT / "codex" / "skills" / "lotus-front-office-runtime" / "SKILL.md")
    frontend_skill = _read(ROOT / "codex" / "skills" / "lotus-frontend-delivery-governance" / "SKILL.md")

    assert "Do not use screenshot capture alone as proof" in routing_map
    assert "Do not accept screenshot-only proof." in runtime_skill
    assert "Screenshots alone are not proof for governed front-office surfaces." in frontend_skill
    assert "Do not default to `lotus-platform/platform-stack` as the primary front-office product bring-up path." in ramp_up
    assert "Do not improvise a parallel front-office stack sequence from `lotus-platform/platform-stack`" in engineering_context
    assert "label it with a `diagnostic-` prefix" in deployed_agents
