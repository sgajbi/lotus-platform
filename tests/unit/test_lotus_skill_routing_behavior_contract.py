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

    assert "| Bring up canonical Workbench runtime, validate populated panels, generate governed demo screenshots, or prove default `lotus-idea` canonical QA readiness/teardown | `lotus-front-office-runtime` |" in routing_map
    assert "PB_SG_GLOBAL_BAL_001" in routing_map
    assert "choose `lotus-front-office-runtime` first" in agents_contract
    assert "Treat `lotus-front-office-runtime` as the primary skill route for these tasks." in ramp_up
    assert "Do not accept screenshot-only proof." in runtime_skill
    assert "Treat `lotus-idea` as part of the default canonical platform QA runtime." in runtime_skill
    assert "DEMO_DATA_PACK_ENABLED=false" in runtime_skill
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


def test_ci_enforcement_governance_route_is_unambiguous() -> None:
    routing_map = _read(ROOT / "context" / "LOTUS-SKILL-ROUTING-MAP.md")
    engineering_context = _read(ROOT / "context" / "LOTUS-ENGINEERING-CONTEXT.md")
    ramp_up = _read(ROOT / "docs" / "onboarding" / "LOTUS-AGENT-RAMP-UP.md")
    ci_skill = _read(ROOT / "codex" / "skills" / "lotus-ci-enforcement-governance" / "SKILL.md")
    backend_skill = _read(ROOT / "codex" / "skills" / "lotus-backend-delivery-governance" / "SKILL.md")
    pr_skill = _read(ROOT / "codex" / "skills" / "lotus-pr-premerge-gate" / "SKILL.md")

    assert "| Design or promote high-signal CI enforcement" in routing_map
    assert "`lotus-ci-enforcement-governance`" in ramp_up
    assert "`lotus-ci-enforcement-governance` for CI gate design" in engineering_context
    assert "Promote gates that prevent real degradation." in ci_skill
    assert "Use `lotus-ci-enforcement-governance` as the primary route" in backend_skill
    assert "Use `lotus-ci-enforcement-governance` before this skill" in pr_skill
    assert (
        "lotus-platform/docs/standards/Continuous Integration, Validation, and Release Governance Standard.md"
        in backend_skill
    )
    assert (
        "lotus-platform/docs/standards/Continuous Integration, Validation, and Release Governance Standard.md"
        in pr_skill
    )
    assert "lotus-platform/Continuous Integration, Validation, and Release Governance Standard.md" not in backend_skill
    assert "lotus-platform/Continuous Integration, Validation, and Release Governance Standard.md" not in pr_skill


def test_lotus_app_issue_discovery_route_is_unambiguous() -> None:
    routing_map = _read(ROOT / "context" / "LOTUS-SKILL-ROUTING-MAP.md")
    skill_manifest = _read(ROOT / "codex" / "skills" / "lotus-skill-manifest.json")
    issue_skill = _read(ROOT / "codex" / "skills" / "lotus-app-issue-discovery" / "SKILL.md")
    lens_catalog = _read(
        ROOT / "codex" / "skills" / "lotus-app-issue-discovery" / "references" / "review-lenses.md"
    )

    assert "| Review a Lotus app lens by lens" in routing_map
    assert "`lotus-app-issue-discovery`" in routing_map
    assert '"lotus-app-issue-discovery"' in skill_manifest
    assert "Do not edit code unless the user explicitly asks for fixes." in issue_skill
    assert "Before raising issues, search GitHub for duplicates" in issue_skill
    assert "For the lens catalog" in issue_skill
    assert "`references/review-lenses.md`" in issue_skill
    assert "scripts/ensure_issue_discovery_labels.py" in issue_skill
    assert "Transaction lifecycle" in lens_catalog
    assert "Monitoring and observability" in lens_catalog
    assert "Data mesh, data product, and trust telemetry contracts" in lens_catalog
    assert "API documentation, standards, and duplicate endpoint posture" in lens_catalog
    assert "Repo organization" in lens_catalog
    assert "Remote repository hygiene" in lens_catalog
    assert "Agents/context organization" in lens_catalog
    assert "Documentation, wiki, README, and runbooks" in lens_catalog
    assert "Security and privacy" in lens_catalog
    assert "duplicate or unclear APIs" in routing_map
    assert "stale remote feature branches" in routing_map


def test_endpoint_and_linkedin_skills_are_governed_and_routed() -> None:
    routing_map = _read(ROOT / "context" / "LOTUS-SKILL-ROUTING-MAP.md")
    skill_manifest = _read(ROOT / "codex" / "skills" / "lotus-skill-manifest.json")
    endpoint_skill = _read(ROOT / "codex" / "skills" / "lotus-endpoint-certification-loop" / "SKILL.md")
    linkedin_skill = _read(ROOT / "codex" / "skills" / "lotus-linkedin-thought-leadership" / "SKILL.md")

    assert "`lotus-endpoint-certification-loop`" in routing_map
    assert "`lotus-linkedin-thought-leadership`" in routing_map
    assert '"lotus-endpoint-certification-loop"' in skill_manifest
    assert '"lotus-linkedin-thought-leadership"' in skill_manifest
    assert "Continuous Skill Improvement" in endpoint_skill
    assert "At the end of any meaningful use of this skill" in endpoint_skill
    assert "platform-owned skill source" in endpoint_skill
    assert "Continuous Skill Improvement" in linkedin_skill
    assert "At the end of any meaningful use of this skill" in linkedin_skill
    assert "platform-owned skill source" in linkedin_skill


def test_rfc_slice_implementation_guidance_is_explicit() -> None:
    routing_map = _read(ROOT / "context" / "LOTUS-SKILL-ROUTING-MAP.md")
    engineering_context = _read(ROOT / "context" / "LOTUS-ENGINEERING-CONTEXT.md")
    ci_standard = _read(
        ROOT
        / "docs"
        / "standards"
        / "Continuous Integration, Validation, and Release Governance Standard.md"
    )
    pr_loop = _read(ROOT / "context" / "playbooks" / "PR-LOOP-PLAYBOOK.md")
    rfc_skill = _read(ROOT / "codex" / "skills" / "lotus-rfc-review-loop" / "SKILL.md")
    ci_skill = _read(ROOT / "codex" / "skills" / "lotus-ci-enforcement-governance" / "SKILL.md")

    assert "| Implement a business-application RFC slice" in routing_map
    assert "preventing many partial slices from accumulating" in routing_map
    assert "For RFC-driven business-application implementation" in engineering_context
    assert "proof-backed slice before opening the next" in engineering_context
    assert "stop retrying merge commits after that policy is known" in engineering_context
    assert "repository governance policy is authoritative for the allowed merge methods" in ci_standard
    assert "do not repeatedly attempt merge commits after repository policy is known" in ci_standard
    assert "If GitHub rejects merge" in pr_loop
    assert "commits or the repository requires linear history" in pr_loop
    assert "One slice at a time" in rfc_skill
    assert "Bounded proof semantics" in rfc_skill
    assert "Design modularity before runtime modularity" in rfc_skill
    assert "Slice Execution Ledger" in rfc_skill
    assert "single-slice readiness statement" in ci_skill
    assert "many half-finished slices" in ci_skill


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
    assert "docs/operations/Local Development Runbook.md" in skill
    assert "`Local Development Runbook.md`" not in skill
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


def test_frontend_delivery_skill_blocks_agent_quality_regressions() -> None:
    frontend_skill = _read(ROOT / "codex" / "skills" / "lotus-frontend-delivery-governance" / "SKILL.md")

    assert (
        "lotus-platform/docs/standards/Continuous Integration, Validation, and Release Governance Standard.md"
        in frontend_skill
    )
    assert "lotus-platform/Continuous Integration, Validation, and Release Governance Standard.md" not in frontend_skill

    for required_text in (
        "Before editing product UI code, inspect the existing implementation enough to name:",
        "Before editing frontend code, produce a short quality intake from the actual product surface:",
        "name the canonical gateway endpoint, shared client, or deterministic fixture boundary",
        "nearest browser/runtime proof command and the viewport or governed panel",
        "the existing component, route, hook, client, view-model, and test patterns",
        "the current source of backend truth and whether it is canonical, fixture-only, or unsupported",
        "Reject agent-produced UI that only looks plausible.",
        "introduces a page-local data contract when a gateway or shared client already exists",
        "duplicates calculations, status mapping, table shaping, or chart data transformations",
        "handles only the happy path while silently weakening existing loading, empty, partial, error, or",
        "ships layout changes without browser validation",
    ):
        assert required_text in frontend_skill


def test_backend_delivery_skill_blocks_agent_quality_regressions() -> None:
    backend_skill = _read(ROOT / "codex" / "skills" / "lotus-backend-delivery-governance" / "SKILL.md")

    for required_text in (
        "LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md",
        "Bank-Buyable Default Bar",
        "Every meaningful backend slice should improve or preserve at least one bank-buyable control",
        "Before editing backend code, produce a short quality intake from the actual repository:",
        "name the existing module, service, repository, model, router, and test patterns",
        "identify the canonical source of business truth",
        "inspect the current duplicate-code, complexity/function-size, architecture-boundary, security",
        "Reject agent-produced backend code that only appears plausible.",
        "creates a parallel service, mapper, DTO, status enum, or contract vocabulary",
        "copies calculations, serialization envelopes, query shaping, or error mapping",
        "weakens observability, lineage, runtime-status, or supportability evidence",
        "adds tests that only freeze implementation mechanics",
    ):
        assert required_text in backend_skill


def test_ci_enforcement_skill_requires_measured_gate_intake() -> None:
    ci_skill = _read(ROOT / "codex" / "skills" / "lotus-ci-enforcement-governance" / "SKILL.md")

    for required_text in (
        "LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md",
        "Before changing CI enforcement, produce a short enforcement intake:",
        "name the current measured baseline and the artifact that records it",
        "identify the exact failure mode the gate prevents",
        "define the exception or allowlist policy before any exception is added",
        "Do not promote a gate from intuition alone.",
        "report-only. Use it for planning",
        "Prefer enforcement that blocks common agent failure modes:",
        "copied implementation hotspots that a deterministic duplicate inventory can identify",
        "architecture-boundary imports or ownership drift",
        "unsupported API shape, OpenAPI, vocabulary, no-alias, or contract drift",
        "minimum API/runtime test-family breadth",
        "maximum uncategorized-test backlog",
        "total test count as context rather than the gate itself",
        "removal of API/runtime or contract/governance tests hidden by unchanged or growing total test",
        "For agent-generated code, prefer gates that enforce",
        "degrades a Lotus app",
    ):
        assert required_text in ci_skill


def test_lotus_delivery_skills_default_to_bank_buyable_non_degradation() -> None:
    frontend_skill = _read(ROOT / "codex" / "skills" / "lotus-frontend-delivery-governance" / "SKILL.md")
    readme_wiki_skill = _read(ROOT / "codex" / "skills" / "lotus-readme-wiki-governance" / "SKILL.md")
    review_skill = _read(ROOT / "codex" / "skills" / "lotus-codebase-review-ledger" / "SKILL.md")

    for skill_text in (frontend_skill, readme_wiki_skill, review_skill):
        assert "LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md" in skill_text

    assert "Bank-Buyable Default Bar" in frontend_skill
    assert "Every meaningful product-surface slice should improve or preserve" in frontend_skill
    assert "Documentation should explain current implementation truth" in readme_wiki_skill
    assert "evidence, not create future-state confidence" in readme_wiki_skill
    assert "record the explicit" in readme_wiki_skill
    assert "no-doc/no-wiki decision in PR evidence" in readme_wiki_skill
    assert "as the default" in review_skill
    assert "control taxonomy when reviewing a Lotus app" in review_skill
    assert "bank-buyable control gaps" in review_skill


def test_readme_wiki_skill_requires_professional_wiki_publication_quality() -> None:
    readme_wiki_skill = _read(ROOT / "codex" / "skills" / "lotus-readme-wiki-governance" / "SKILL.md")
    wiki_reference = _read(
        ROOT / "codex" / "skills" / "lotus-readme-wiki-governance" / "references" / "lotus-wiki-pages.md"
    )

    for required_text in (
        "professional acceptance bar",
        "the first screen of `Home` explains the repository role, current maturity, and fastest reader",
        "each page starts with purpose and current-state scope before deep details",
        "repeated tables use stable column names across pages",
        "diagrams are used when they clarify ownership, flow, or integration posture",
        "unsupported, planned, or degraded capability is visible",
        "consistent title case, concise paragraphs, no",
        "scratch-note language",
    ):
        assert required_text in readme_wiki_skill

    for required_text in (
        "Professional Publication Checklist",
        "`Home` works as a polished reader map",
        "`_Sidebar` is grouped when the page set is large enough",
        "Business, demo, sales, support, operations, and engineering readers",
        "Unsupported, planned, degraded, or bounded-preview behavior is visible",
        "No page includes scratch-note terms",
    ):
        assert required_text in wiki_reference


def test_agent_ramp_up_requires_pre_edit_quality_intake() -> None:
    ramp_up = _read(ROOT / "docs" / "onboarding" / "LOTUS-AGENT-RAMP-UP.md")

    for required_text in (
        "Before implementation, write a short quality intake from the actual codebase.",
        "existing owner patterns, source of truth, closest meaningful tests",
        "measurable quality signal the slice will improve or preserve",
        "test-family breadth, uncategorized-test growth",
        "total test count as the only quality proxy",
        "it should keep reading instead of writing plausible code",
        "starting code changes before naming the existing owner pattern",
    ):
        assert required_text in ramp_up


def test_platform_context_records_test_family_breadth_as_quality_signal() -> None:
    engineering_context = _read(ROOT / "context" / "LOTUS-ENGINEERING-CONTEXT.md")
    routing_map = _read(ROOT / "context" / "LOTUS-SKILL-ROUTING-MAP.md")
    ledger = _read(ROOT / "context" / "platform-engineering-ledger.md")
    ramp_up = _read(ROOT / "docs" / "onboarding" / "LOTUS-AGENT-RAMP-UP.md")

    assert "treat total test count as context, not proof by itself" in engineering_context
    assert "test-family breadth" in routing_map
    assert "cap uncategorized-test drift" in routing_map
    assert "Test-family breadth can be a CI gate when total test count hides proof loss" in ledger
    assert "AGENTIC-CODING-QUALITY-EVALUATION-LOOP.md" in ramp_up


def test_agentic_coding_quality_eval_loop_is_governed_and_discoverable() -> None:
    playbook = _read(ROOT / "context" / "playbooks" / "AGENTIC-CODING-QUALITY-EVALUATION-LOOP.md")
    procedural_index = _read(ROOT / "context" / "PROCEDURAL-MEMORY-INDEX.md")
    reference_map = _read(ROOT / "context" / "CONTEXT-REFERENCE-MAP.md")
    engineering_context = _read(ROOT / "context" / "LOTUS-ENGINEERING-CONTEXT.md")
    routing_map = _read(ROOT / "context" / "LOTUS-SKILL-ROUTING-MAP.md")
    ramp_up = _read(ROOT / "docs" / "onboarding" / "LOTUS-AGENT-RAMP-UP.md")

    for required_text in (
        "deterministic repository gates that block known bad patterns",
        "evaluator datasets that replay realistic agent tasks and grade outputs",
        "Use deterministic gates for merge decisions.",
        "Total test count alone is not a gate.",
        "OpenAI agent evaluation guidance",
        "OpenTelemetry provides vendor-neutral semantic conventions",
        "SLSA defines software supply-chain controls",
        "OWASP ASVS provides a basis",
        "Do not self-grade with prose",
    ):
        assert required_text in playbook

    assert "AGENTIC-CODING-QUALITY-EVALUATION-LOOP.md" in procedural_index
    assert "AGENTIC-CODING-QUALITY-EVALUATION-LOOP.md" in reference_map
    assert "AGENTIC-CODING-QUALITY-EVALUATION-LOOP.md" in engineering_context
    assert "agentic coding eval loops" in routing_map
    assert "agentic coding quality evaluation or anti-slop feedback loops" in ramp_up
