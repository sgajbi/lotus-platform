from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTEXT_DIR = ROOT / "context"
WORKSPACE_ROOT = ROOT.parent


def _load_registry_renderer():
    module_path = ROOT / "automation" / "render_context_registries.py"
    spec = importlib.util.spec_from_file_location("render_context_registries", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load render_context_registries module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalize_text(value: str) -> str:
    return value.replace("\r\n", "\n").rstrip("\n\r")


def _validate_application_registry_matches_repos(
    *,
    errors: list[str],
    applications: list[dict],
    repository_registry: list[dict],
) -> None:
    registered_repositories = {
        entry.get("name") for entry in repository_registry if entry.get("name")
    }
    application_repositories = {
        entry.get("repository") for entry in applications if entry.get("repository")
    }
    if application_repositories != registered_repositories:
        missing_from_manifest = sorted(registered_repositories - application_repositories)
        missing_from_registry = sorted(application_repositories - registered_repositories)
        errors.append(
            "lotus-context-manifest.json: applications registry must match automation/repos.json"
            f" (missing_from_manifest={missing_from_manifest}, missing_from_registry={missing_from_registry})"
        )
    if any(entry.get("status") != "implemented" for entry in applications):
        errors.append("lotus-context-manifest.json: all application context statuses must be `implemented`")


def _validate_application_agent_contract_sync(
    *,
    errors: list[str],
    warnings: list[str],
    applications: list[dict],
    normalized_agents_contract: str,
) -> None:
    for application in applications:
        repository_name = application.get("repository")
        if not repository_name:
            errors.append("lotus-context-manifest.json: application entry missing repository name")
            continue
        repo_root = ROOT if repository_name == "lotus-platform" else WORKSPACE_ROOT / repository_name
        if not repo_root.exists():
            continue
        repo_context_path = repo_root / application.get("repo_context_path", "REPOSITORY-ENGINEERING-CONTEXT.md")
        if not repo_context_path.exists():
            continue
        _validate_repo_context_shape(
            errors=errors,
            warnings=warnings,
            repository_name=repository_name,
            repo_context_path=repo_context_path,
        )
        repo_agents_path = repo_root / "AGENTS.md"
        if not repo_agents_path.exists():
            target = errors if repository_name == "lotus-platform" else warnings
            target.append(f"{repository_name}: missing repo-root AGENTS.md")
            continue
        repo_agents_text = _normalize_text(_read_text(repo_agents_path))
        if repo_agents_text != normalized_agents_contract:
            target = errors if repository_name == "lotus-platform" else warnings
            target.append(
                f"{repository_name}: repo-root AGENTS.md is not synchronized with context/AGENTS-OPERATING-CONTRACT.md"
            )



# The contract in context/Repository-Engineering-Context-Contract.md states these
# in prose. Nothing measured them until now, and three repositories had drifted
# without anyone seeing it -- the declared-versus-measured gap, in the corpus
# that describes every other posture surface.
REQUIRED_REPO_CONTEXT_SECTIONS = (
    "Repository Role",
    "Business And Domain Responsibility",
    "Current-State Summary",
    "Architecture And Module Map",
    "Runtime And Integration Boundaries",
    "Repo-Native Commands",
    "Validation And CI Expectations",
    "Standards And RFCs That Govern This Repository",
    "Known Constraints And Implementation Notes",
    "Context Maintenance Rule",
    "Cross-Links",
)

# Matched by document rather than by one path form: lotus-platform links its own
# copies as `./context/...` while siblings link `../lotus-platform/context/...`.
# Requiring the sibling spelling reported the owning repository as non-conformant
# -- a rule correct about the case that motivated it and wrong about the one
# nobody checked.
REQUIRED_REPO_CONTEXT_CROSS_LINKS = (
    "context/LOTUS-QUICKSTART-CONTEXT.md",
    "context/LOTUS-ENGINEERING-CONTEXT.md",
    "context/CONTEXT-REFERENCE-MAP.md",
)

# A prose line beginning with an issue reference renders as an H1: "#681 was the
# tracker" becomes a top-level heading in the outline, which a heading-based
# check reads as structure and a human reads as a section that does not exist.
_ISSUE_AS_HEADING = re.compile(r"^#[0-9]", re.MULTILINE)



def _validate_repo_context_shape(
    *,
    errors: list[str],
    warnings: list[str],
    repository_name: str,
    repo_context_path: Path,
) -> None:
    """Check one repository context document against the contract's required shape.

    A mismatch is an error for lotus-platform and a warning elsewhere, matching
    how AGENTS.md drift is already treated: this repository owns the contract,
    and a sibling that has not caught up must not block the lane that publishes
    the requirement.
    """
    text = _read_text(repo_context_path)
    headings = {
        line.lstrip("#").strip()
        for line in text.splitlines()
        if line.startswith("#")
    }
    missing_sections = [
        section for section in REQUIRED_REPO_CONTEXT_SECTIONS if section not in headings
    ]
    missing_links = [
        link for link in REQUIRED_REPO_CONTEXT_CROSS_LINKS if link not in text
    ]

    target = errors if repository_name == "lotus-platform" else warnings
    if missing_sections:
        target.append(
            f"{repository_name}: REPOSITORY-ENGINEERING-CONTEXT.md is missing "
            f"{len(missing_sections)} required section(s): {', '.join(missing_sections)}"
        )
    if missing_links:
        target.append(
            f"{repository_name}: REPOSITORY-ENGINEERING-CONTEXT.md is missing required "
            f"cross-link(s): {', '.join(missing_links)}"
        )
    fake_headings = _ISSUE_AS_HEADING.findall(text)
    if fake_headings:
        target.append(
            f"{repository_name}: REPOSITORY-ENGINEERING-CONTEXT.md has {len(fake_headings)} "
            "line(s) starting with an issue reference, which render as top-level headings; "
            "reflow the line or write 'issue #123'"
        )


def _validate_manifest_path_map(
    *,
    errors: list[str],
    manifest: dict,
) -> None:
    context_documents = manifest.get("context_documents", {})
    for key, expected_path in {
        "index": "context/README.md",
        "quickstart": "context/LOTUS-QUICKSTART-CONTEXT.md",
        "engineering_context": "context/LOTUS-ENGINEERING-CONTEXT.md",
        "reference_map": "context/CONTEXT-REFERENCE-MAP.md",
        "task_routing_guide": "context/TASK-ROUTING-GUIDE.md",
        "ecosystem_registries": "context/ECOSYSTEM-REGISTRIES.md",
        "procedural_memory_index": "context/PROCEDURAL-MEMORY-INDEX.md",
        "agents_operating_contract_source": "context/AGENTS-OPERATING-CONTRACT.md",
    }.items():
        if context_documents.get(key) != expected_path:
            errors.append(f"lotus-context-manifest.json: context_documents.{key} must equal `{expected_path}`")

    procedural_memory = manifest.get("procedural_memory", {})
    for key, expected_path in {
        "change_playbooks": "context/playbooks/CHANGE-PLAYBOOKS.md",
        "pr_loop_playbook": "context/playbooks/PR-LOOP-PLAYBOOK.md",
        "validation_playbook": "context/playbooks/VALIDATION-PLAYBOOK.md",
        "fix_forward_patterns": "context/playbooks/FIX-FORWARD-PATTERNS.md",
        "agent_context_and_task_ledger": "context/playbooks/AGENT-CONTEXT-AND-TASK-LEDGER.md",
        "agentic_coding_quality_evaluation_loop": (
            "context/playbooks/AGENTIC-CODING-QUALITY-EVALUATION-LOOP.md"
        ),
    }.items():
        if procedural_memory.get(key) != expected_path:
            errors.append(f"lotus-context-manifest.json: procedural_memory.{key} must equal `{expected_path}`")


def _validate_manifest_standards_registry(
    *,
    errors: list[str],
    manifest: dict,
) -> None:
    standards_registry = manifest.get("standards_registry", [])
    standard_names = {
        entry.get("name") for entry in standards_registry if isinstance(entry, dict)
    }
    for standard_name in (
        "Continuous Integration, Validation, and Release Governance Standard",
        "Testing Pyramid and Coverage Standard",
        "Dependency Hygiene and Security Standard",
        "Platform Observability Standards",
        "Enterprise Readiness Standard",
        "Scalability and Availability Standard",
        "Domain Vocabulary Glossary",
        "Platform Integration Architecture Bible",
    ):
        if standard_name not in standard_names:
            errors.append(f"lotus-context-manifest.json: standards registry missing `{standard_name}`")


def _validate_manifest_rfc_postures(
    *,
    errors: list[str],
    manifest: dict,
) -> None:
    active_rfcs = manifest.get("active_rfc_registry", [])
    rfc_postures = {
        entry.get("id"): entry.get("implementation_posture")
        for entry in active_rfcs
        if isinstance(entry, dict)
    }
    if rfc_postures.get("RFC-0071") != "implemented and governed":
        errors.append("lotus-context-manifest.json: RFC-0071 implementation posture drifted")
    if "partially implemented" not in str(rfc_postures.get("RFC-0072", "")):
        errors.append("lotus-context-manifest.json: RFC-0072 implementation posture drifted")
    if rfc_postures.get("RFC-0073") != "implemented and governed":
        errors.append("lotus-context-manifest.json: RFC-0073 implementation posture drifted")
    if rfc_postures.get("RFC-0074") != "implemented and governed":
        errors.append("lotus-context-manifest.json: RFC-0074 implementation posture drifted")


def _validate_rendered_ecosystem_registries(
    *,
    errors: list[str],
    manifest: dict,
    ecosystem_registries: str,
) -> None:
    registry_renderer = _load_registry_renderer()
    rendered_registries = registry_renderer.render_registry_document(manifest)
    if ecosystem_registries != rendered_registries:
        errors.append("ECOSYSTEM-REGISTRIES.md is out of sync with lotus-context-manifest.json")


def _validate_manifest_contract(
    *,
    errors: list[str],
    warnings: list[str],
    manifest: dict,
    repository_registry: list[dict],
    normalized_agents_contract: str,
    ecosystem_registries: str,
) -> None:
    applications = manifest.get("applications", [])
    _validate_application_registry_matches_repos(
        errors=errors,
        applications=applications,
        repository_registry=repository_registry,
    )
    _validate_application_agent_contract_sync(
        errors=errors,
        warnings=warnings,
        applications=applications,
        normalized_agents_contract=normalized_agents_contract,
    )
    _validate_manifest_path_map(errors=errors, manifest=manifest)
    _validate_manifest_standards_registry(errors=errors, manifest=manifest)
    _validate_manifest_rfc_postures(errors=errors, manifest=manifest)
    _validate_rendered_ecosystem_registries(
        errors=errors,
        manifest=manifest,
        ecosystem_registries=ecosystem_registries,
    )


def _validate_agents_operating_contract(*, errors: list[str], agents_contract: str) -> None:
    required_sections = (
        "Mandatory Reading Order",
        "Mandatory Operating Rules",
        "Context Maintenance Rule",
        "Wiki Publication Rule",
        "Skills, Automation, And Async Execution",
        "Front-Office Runtime Routing Rule",
    )
    for heading in required_sections:
        _require_agents_contract_text(
            errors=errors,
            agents_contract=agents_contract,
            text=heading,
            error=f"AGENTS-OPERATING-CONTRACT.md: missing section `{heading}`",
        )

    _require_agents_contract_texts(
        errors=errors,
        agents_contract=agents_contract,
        requirements=(
            (
                "PROCEDURAL-MEMORY-INDEX.md",
                "AGENTS-OPERATING-CONTRACT.md: missing procedural memory index cross-link",
            ),
            (
                "AGENT-CONTEXT-AND-TASK-LEDGER.md",
                "AGENTS-OPERATING-CONTRACT.md: missing agent context and task ledger playbook cross-link",
            ),
            (
                "engineering_task_id",
                "AGENTS-OPERATING-CONTRACT.md: missing engineering_task_id preservation guidance",
            ),
            (
                "output/background-runs.json",
                "AGENTS-OPERATING-CONTRACT.md: missing background-run evidence guidance",
            ),
            (
                "Sync-RepoWikis.ps1",
                "AGENTS-OPERATING-CONTRACT.md: missing wiki publication check guidance",
            ),
            (
                "Repo-local `wiki/` is the authored source of truth",
                "AGENTS-OPERATING-CONTRACT.md: missing repo-local wiki source-of-truth guidance",
            ),
            (
                "Repo-root `AGENTS.md` files across Lotus repositories",
                "AGENTS-OPERATING-CONTRACT.md: missing repo-root synchronization guidance",
            ),
        ),
    )

    for text in (
        "lotus-workbench/docs/operations/canonical-front-office-local-runtime.md",
        "npm run live:stack:up",
        "npm run live:validate",
        "Invoke-Canonical-FrontOffice-QA.ps1 -ScreenshotDirectory",
        "PB_SG_GLOBAL_BAL_001",
    ):
        if text not in agents_contract:
            errors.append(f"AGENTS-OPERATING-CONTRACT.md: missing front-office runtime routing `{text}`")


def _require_agents_contract_texts(
    *,
    errors: list[str],
    agents_contract: str,
    requirements: tuple[tuple[str, str], ...],
) -> None:
    for text, error in requirements:
        _require_agents_contract_text(
            errors=errors,
            agents_contract=agents_contract,
            text=text,
            error=error,
        )


def _require_agents_contract_text(
    *,
    errors: list[str],
    agents_contract: str,
    text: str,
    error: str,
) -> None:
    if text not in agents_contract:
        errors.append(error)


def _validate_required_developer_onboarding_text(
    *,
    errors: list[str],
    developer_onboarding: str,
) -> None:
    for text in (
        "Validate-LotusDeveloperEnvironment.ps1 -Mode Inspect -Profile fast",
        "Bootstrap-LotusDeveloperEnvironment.ps1 -Profile fast",
        "unknown local Codex skills are preserved",
        "output/developer-environment-readiness.json",
        "output/developer-environment-readiness.md",
        "Canonical Front-Office Local Runtime",
        "npm run live:stack:up",
        "Invoke-Canonical-FrontOffice-QA.ps1",
        "ScreenshotDirectory",
        "PB_SG_GLOBAL_BAL_001",
        "RFC-0074 is implemented and governed.",
    ):
        if text not in developer_onboarding:
            errors.append(f"LOTUS-DEVELOPER-ONBOARDING.md: missing bootstrap guidance `{text}`")


def _validate_stale_developer_onboarding_text(
    *,
    errors: list[str],
    developer_onboarding: str,
) -> None:
    if "primary front-office demo bring-up path" not in developer_onboarding:
        errors.append("LOTUS-DEVELOPER-ONBOARDING.md: missing front-office runtime boundary guidance")
    for stale_text in (
        "At Slice 5, this guide is the onboarding entrypoint",
        "Later RFC-0074 slices will add",
    ):
        if stale_text in developer_onboarding:
            errors.append(f"LOTUS-DEVELOPER-ONBOARDING.md: stale RFC-0074 boundary remains `{stale_text}`")


def _validate_required_agent_ramp_up_text(
    *,
    errors: list[str],
    agent_ramp_up: str,
) -> None:
    if "Do not start with Tier 3 by default." not in agent_ramp_up:
        errors.append("LOTUS-AGENT-RAMP-UP.md: missing context-budget guardrail")
    if "RFC-0074 is implemented and governed." not in agent_ramp_up:
        errors.append("LOTUS-AGENT-RAMP-UP.md: missing implemented RFC-0074 boundary")
    if "automation/Bootstrap-LotusDeveloperEnvironment.ps1 -Profile fast" not in agent_ramp_up:
        errors.append("LOTUS-AGENT-RAMP-UP.md: missing bootstrap automation guidance")
    if (
        "Platform-owned skill artifacts now exist under `lotus-platform/codex/skills`" not in agent_ramp_up
        and "platform-owned Lotus skills under `lotus-platform/codex/skills`" not in agent_ramp_up
    ):
        errors.append("LOTUS-AGENT-RAMP-UP.md: missing governed skill source guidance")


def _validate_stale_agent_ramp_up_text(
    *,
    errors: list[str],
    agent_ramp_up: str,
) -> None:
    for stale_text in (
        "automated skill sync and bootstrap readiness scripts are not implemented yet",
        "Later RFC-0074 slices will add",
        "At Slice 3, this guide defines agent ramp-up",
    ):
        if stale_text in agent_ramp_up:
            errors.append(f"LOTUS-AGENT-RAMP-UP.md: stale RFC-0074 boundary remains `{stale_text}`")


def _validate_agent_front_office_routing_text(
    *,
    errors: list[str],
    agent_ramp_up: str,
) -> None:
    for text in (
        "## Front-Office Runtime Routing",
        "canonical-front-office-local-runtime.md",
        "npm run live:stack:up",
        "Invoke-Canonical-FrontOffice-QA.ps1 -ScreenshotDirectory",
        "PB_SG_GLOBAL_BAL_001",
    ):
        if text not in agent_ramp_up:
            errors.append(f"LOTUS-AGENT-RAMP-UP.md: missing front-office runtime routing `{text}`")


def _validate_onboarding_guidance(
    *,
    errors: list[str],
    developer_onboarding: str,
    agent_ramp_up: str,
) -> None:
    _validate_required_developer_onboarding_text(
        errors=errors,
        developer_onboarding=developer_onboarding,
    )
    _validate_stale_developer_onboarding_text(
        errors=errors,
        developer_onboarding=developer_onboarding,
    )
    _validate_required_agent_ramp_up_text(errors=errors, agent_ramp_up=agent_ramp_up)
    _validate_stale_agent_ramp_up_text(errors=errors, agent_ramp_up=agent_ramp_up)
    _validate_agent_front_office_routing_text(errors=errors, agent_ramp_up=agent_ramp_up)


def _validate_rfc_completion(*, errors: list[str], rfc: str, checklist: str) -> None:
    if "- Status: Implemented" not in rfc:
        errors.append("RFC-0073 must be marked Implemented once all slices are complete")
    if "Slice 5 | Drift control and validation foundation | Complete" not in checklist:
        errors.append("RFC-0073 checklist: Slice 5 must be marked complete")
    if "Slice 6 | Skills, automation, and procedural memory alignment | Complete" not in checklist:
        errors.append("RFC-0073 checklist: Slice 6 must be marked complete")
    if "Implementation posture: `Complete`" not in checklist:
        errors.append("RFC-0073 checklist must record complete implementation posture")
    if "Slice 2A | Repo-root AGENTS deployment and drift control | Complete" not in checklist:
        errors.append("RFC-0073 checklist: Slice 2A must be marked complete")


def _validate_context_index_entrypoints(
    errors: list[str],
    context_index: str,
) -> None:
    for link_target in (
        "./LOTUS-QUICKSTART-CONTEXT.md",
        "./LOTUS-ENGINEERING-CONTEXT.md",
        "./CONTEXT-REFERENCE-MAP.md",
        "./TASK-ROUTING-GUIDE.md",
        "./ECOSYSTEM-REGISTRIES.md",
        "./PROCEDURAL-MEMORY-INDEX.md",
    ):
        if link_target not in context_index:
            errors.append(f"context/README.md: missing link to `{link_target}`")


def _validate_quickstart_entrypoints(
    errors: list[str],
    quickstart: str,
) -> None:
    if "./TASK-ROUTING-GUIDE.md" not in quickstart:
        errors.append("LOTUS-QUICKSTART-CONTEXT.md: missing task routing guide cross-link")
    if "./ECOSYSTEM-REGISTRIES.md" not in quickstart:
        errors.append("LOTUS-QUICKSTART-CONTEXT.md: missing ecosystem registries cross-link")


def _validate_engineering_context_entrypoints(
    errors: list[str],
    engineering: str,
) -> None:
    if "## Task Routing Guidance" not in engineering:
        errors.append("LOTUS-ENGINEERING-CONTEXT.md: missing task routing guidance section")
    if "./TASK-ROUTING-GUIDE.md" not in engineering:
        errors.append("LOTUS-ENGINEERING-CONTEXT.md: missing task routing guide cross-link")
    if "./ECOSYSTEM-REGISTRIES.md" not in engineering:
        errors.append("LOTUS-ENGINEERING-CONTEXT.md: missing ecosystem registries cross-link")
    if "./PROCEDURAL-MEMORY-INDEX.md" not in engineering:
        errors.append("LOTUS-ENGINEERING-CONTEXT.md: missing procedural memory index cross-link")
    for text in (
        "## Front-Office Runtime Governance",
        "lotus-workbench/docs/operations/canonical-front-office-local-runtime.md",
        "npm run live:stack:up",
        "Invoke-Canonical-FrontOffice-QA.ps1 -ScreenshotDirectory",
        "PB_SG_GLOBAL_BAL_001",
    ):
        if text not in engineering:
            errors.append(f"LOTUS-ENGINEERING-CONTEXT.md: missing front-office runtime guidance `{text}`")
    for text in (
        "For RFC-0093/RFC-0094 agent engineering governance:",
        "AGENT-CONTEXT-AND-TASK-LEDGER.md",
        "platform-contracts/agent-engineering/engineering-task-ledger-contract.v1.json",
        "output/background-runs.json",
        "repository, branch, PR",
    ):
        if text not in engineering:
            errors.append(f"LOTUS-ENGINEERING-CONTEXT.md: missing agent engineering guidance `{text}`")


def _validate_reference_map_entrypoints(
    errors: list[str],
    reference_map: str,
) -> None:
    if "These are now the implementation-truth entrypoints for each repo:" not in reference_map:
        errors.append("CONTEXT-REFERENCE-MAP.md: repo-local context section is stale or missing")
    if "once it exists" in reference_map or "will become the implementation truth" in reference_map:
        errors.append("CONTEXT-REFERENCE-MAP.md: stale rollout language must not remain")


def _validate_task_routing_entrypoints(
    errors: list[str],
    task_routing_guide: str,
) -> None:
    for heading in (
        "## Frontend And Product-Surface Work",
        "## Backend API And Domain-Service Work",
        "## Cross-App Integration And Platform Validation Work",
        "## Standards, RFC, And Governance Work",
        "## Async Execution And Heavy Validation Routing",
    ):
        if heading not in task_routing_guide:
            errors.append(f"TASK-ROUTING-GUIDE.md: missing heading `{heading}`")


def _validate_procedural_memory_entrypoints(
    errors: list[str],
    procedural_memory_index: str,
) -> None:
    if "Change Playbooks" not in procedural_memory_index:
        errors.append("PROCEDURAL-MEMORY-INDEX.md: missing Change Playbooks reference")
    if "PR Loop Playbook" not in procedural_memory_index:
        errors.append("PROCEDURAL-MEMORY-INDEX.md: missing PR Loop Playbook reference")
    if "Validation Playbook" not in procedural_memory_index:
        errors.append("PROCEDURAL-MEMORY-INDEX.md: missing Validation Playbook reference")
    if "Fix-Forward Patterns" not in procedural_memory_index:
        errors.append("PROCEDURAL-MEMORY-INDEX.md: missing Fix-Forward Patterns reference")
    if "Agent Context And Task Ledger Playbook" not in procedural_memory_index:
        errors.append("PROCEDURAL-MEMORY-INDEX.md: missing Agent Context And Task Ledger Playbook reference")
    if "Agentic Coding Quality Evaluation Loop" not in procedural_memory_index:
        errors.append("PROCEDURAL-MEMORY-INDEX.md: missing Agentic Coding Quality Evaluation Loop reference")


def _validate_context_entrypoints(
    *,
    errors: list[str],
    context_index: str,
    quickstart: str,
    engineering: str,
    reference_map: str,
    task_routing_guide: str,
    procedural_memory_index: str,
) -> None:
    _validate_context_index_entrypoints(errors, context_index)
    _validate_quickstart_entrypoints(errors, quickstart)
    _validate_engineering_context_entrypoints(errors, engineering)
    _validate_reference_map_entrypoints(errors, reference_map)
    _validate_task_routing_entrypoints(errors, task_routing_guide)
    _validate_procedural_memory_entrypoints(errors, procedural_memory_index)


def _validate_playbook_content(
    *,
    errors: list[str],
    change_playbooks: str,
    pr_loop_playbook: str,
    validation_playbook: str,
    fix_forward_patterns: str,
    agent_context_task_ledger: str,
) -> None:
    for text, label in (
        ("Backend API And Domain-Service Change Playbook", "CHANGE-PLAYBOOKS.md"),
        ("Frontend And Product-Surface Change Playbook", "CHANGE-PLAYBOOKS.md"),
        ("Cross-Repository Integration Change Playbook", "CHANGE-PLAYBOOKS.md"),
        ("RFC-Driven Slice Playbook", "CHANGE-PLAYBOOKS.md"),
        ("Working Sequence", "PR-LOOP-PLAYBOOK.md"),
        ("GitHub-Backed Heavy Execution Rule", "PR-LOOP-PLAYBOOK.md"),
        ("Validation Layers", "VALIDATION-PLAYBOOK.md"),
        ("Platform End-To-End Proof", "VALIDATION-PLAYBOOK.md"),
        ("Stale Expectation Pattern", "FIX-FORWARD-PATTERNS.md"),
        ("Validator Overreach Pattern", "FIX-FORWARD-PATTERNS.md"),
        ("Local-Only Assumption Pattern", "FIX-FORWARD-PATTERNS.md"),
        ("Identifier Preservation", "AGENT-CONTEXT-AND-TASK-LEDGER.md"),
        ("Detached Task Ledger", "AGENT-CONTEXT-AND-TASK-LEDGER.md"),
        ("Promotion Decisions", "AGENT-CONTEXT-AND-TASK-LEDGER.md"),
    ):
        target_doc = {
            "CHANGE-PLAYBOOKS.md": change_playbooks,
            "PR-LOOP-PLAYBOOK.md": pr_loop_playbook,
            "VALIDATION-PLAYBOOK.md": validation_playbook,
            "FIX-FORWARD-PATTERNS.md": fix_forward_patterns,
            "AGENT-CONTEXT-AND-TASK-LEDGER.md": agent_context_task_ledger,
        }[label]
        if text not in target_doc:
            errors.append(f"{label}: missing required content `{text}`")


def _validate_developer_environment_automation(
    *,
    errors: list[str],
    developer_environment_validation: str,
    developer_environment_bootstrap: str,
) -> None:
    for text, label, content in (
        ('[ValidateSet("Inspect", "Sync", "Validate")]', "Validate-LotusDeveloperEnvironment.ps1", developer_environment_validation),
        ('[ValidateSet("fast", "extended", "platform")]', "Validate-LotusDeveloperEnvironment.ps1", developer_environment_validation),
        ("Redact-Value", "Validate-LotusDeveloperEnvironment.ps1", developer_environment_validation),
        ("Test-SkillSync", "Validate-LotusDeveloperEnvironment.ps1", developer_environment_validation),
        ("developer-environment-readiness.json", "Validate-LotusDeveloperEnvironment.ps1", developer_environment_validation),
        ("Refusing to synchronize skill outside the requested Codex skills target root.", "Validate-LotusDeveloperEnvironment.ps1", developer_environment_validation),
        ("Resolve-PowerShellExecutable", "Bootstrap-LotusDeveloperEnvironment.ps1", developer_environment_bootstrap),
        ('"-Mode", "Sync"', "Bootstrap-LotusDeveloperEnvironment.ps1", developer_environment_bootstrap),
    ):
        if text not in content:
            errors.append(f"{label}: missing required bootstrap behavior `{text}`")


def _validate_repository_context_contracts(
    *,
    errors: list[str],
    repo_context_contract: str,
    repo_context_template: str,
    platform_repo_context: str,
) -> None:
    if "Context Maintenance Rule" not in repo_context_contract:
        errors.append("Repository-Engineering-Context-Contract.md: missing Context Maintenance Rule")
    if "## Context Maintenance Rule" not in repo_context_template:
        errors.append("REPOSITORY-ENGINEERING-CONTEXT.template.md: missing Context Maintenance Rule heading")
    if "## Context Maintenance Rule" not in platform_repo_context:
        errors.append("REPOSITORY-ENGINEERING-CONTEXT.md: missing Context Maintenance Rule heading")


def validate_engineering_context_system() -> list[str]:
    errors, _warnings = validate_engineering_context_system_with_warnings()
    return errors


def validate_engineering_context_system_with_warnings() -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    required_files = {
        "context index": CONTEXT_DIR / "README.md",
        "quickstart": CONTEXT_DIR / "LOTUS-QUICKSTART-CONTEXT.md",
        "engineering context": CONTEXT_DIR / "LOTUS-ENGINEERING-CONTEXT.md",
        "reference map": CONTEXT_DIR / "CONTEXT-REFERENCE-MAP.md",
        "task routing guide": CONTEXT_DIR / "TASK-ROUTING-GUIDE.md",
        "ecosystem registries": CONTEXT_DIR / "ECOSYSTEM-REGISTRIES.md",
        "procedural memory index": CONTEXT_DIR / "PROCEDURAL-MEMORY-INDEX.md",
        "change playbooks": CONTEXT_DIR / "playbooks" / "CHANGE-PLAYBOOKS.md",
        "pr loop playbook": CONTEXT_DIR / "playbooks" / "PR-LOOP-PLAYBOOK.md",
        "validation playbook": CONTEXT_DIR / "playbooks" / "VALIDATION-PLAYBOOK.md",
        "fix-forward patterns": CONTEXT_DIR / "playbooks" / "FIX-FORWARD-PATTERNS.md",
        "agent context and task ledger playbook": CONTEXT_DIR
        / "playbooks"
        / "AGENT-CONTEXT-AND-TASK-LEDGER.md",
        "manifest": CONTEXT_DIR / "lotus-context-manifest.json",
        "repository registry": ROOT / "automation" / "repos.json",
        "agents contract": CONTEXT_DIR / "AGENTS-OPERATING-CONTRACT.md",
        "repository context contract": CONTEXT_DIR / "Repository-Engineering-Context-Contract.md",
        "repository context template": CONTEXT_DIR / "templates" / "REPOSITORY-ENGINEERING-CONTEXT.template.md",
        "platform repo context": ROOT / "REPOSITORY-ENGINEERING-CONTEXT.md",
        "platform repo agents": ROOT / "AGENTS.md",
        "developer onboarding": ROOT / "docs" / "onboarding" / "LOTUS-DEVELOPER-ONBOARDING.md",
        "agent ramp up": ROOT / "docs" / "onboarding" / "LOTUS-AGENT-RAMP-UP.md",
        "developer environment bootstrap": ROOT / "automation" / "Bootstrap-LotusDeveloperEnvironment.ps1",
        "developer environment validation": ROOT / "automation" / "Validate-LotusDeveloperEnvironment.ps1",
        "ledger": CONTEXT_DIR / "platform-engineering-ledger.md",
        "decisions digest": CONTEXT_DIR / "recent-architectural-decisions-digest.md",
        "rfc checklist": ROOT / "rfcs" / "RFC-0073-implementation-checklist.md",
    }

    for label, path in required_files.items():
        if not path.exists():
            errors.append(f"missing required context artifact: {label} -> {path.relative_to(ROOT)}")

    if errors:
        return errors, warnings

    context_index = _read_text(required_files["context index"])
    quickstart = _read_text(required_files["quickstart"])
    engineering = _read_text(required_files["engineering context"])
    reference_map = _read_text(required_files["reference map"])
    task_routing_guide = _read_text(required_files["task routing guide"])
    ecosystem_registries = _read_text(required_files["ecosystem registries"])
    procedural_memory_index = _read_text(required_files["procedural memory index"])
    change_playbooks = _read_text(required_files["change playbooks"])
    pr_loop_playbook = _read_text(required_files["pr loop playbook"])
    validation_playbook = _read_text(required_files["validation playbook"])
    fix_forward_patterns = _read_text(required_files["fix-forward patterns"])
    agent_context_task_ledger = _read_text(
        required_files["agent context and task ledger playbook"]
    )
    agents_contract = _read_text(required_files["agents contract"])
    repo_context_contract = _read_text(required_files["repository context contract"])
    repo_context_template = _read_text(required_files["repository context template"])
    platform_repo_context = _read_text(required_files["platform repo context"])
    developer_onboarding = _read_text(required_files["developer onboarding"])
    agent_ramp_up = _read_text(required_files["agent ramp up"])
    developer_environment_bootstrap = _read_text(required_files["developer environment bootstrap"])
    developer_environment_validation = _read_text(required_files["developer environment validation"])
    rfc = _read_text(ROOT / "rfcs" / "RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md")
    checklist = _read_text(required_files["rfc checklist"])
    manifest = json.loads(_read_text(required_files["manifest"]))
    repository_registry = json.loads(_read_text(required_files["repository registry"]))
    normalized_agents_contract = _normalize_text(agents_contract)

    _validate_rfc_completion(errors=errors, rfc=rfc, checklist=checklist)

    _validate_context_entrypoints(
        errors=errors,
        context_index=context_index,
        quickstart=quickstart,
        engineering=engineering,
        reference_map=reference_map,
        task_routing_guide=task_routing_guide,
        procedural_memory_index=procedural_memory_index,
    )

    _validate_playbook_content(
        errors=errors,
        change_playbooks=change_playbooks,
        pr_loop_playbook=pr_loop_playbook,
        validation_playbook=validation_playbook,
        fix_forward_patterns=fix_forward_patterns,
        agent_context_task_ledger=agent_context_task_ledger,
    )

    _validate_agents_operating_contract(errors=errors, agents_contract=agents_contract)

    _validate_onboarding_guidance(
        errors=errors,
        developer_onboarding=developer_onboarding,
        agent_ramp_up=agent_ramp_up,
    )

    _validate_developer_environment_automation(
        errors=errors,
        developer_environment_validation=developer_environment_validation,
        developer_environment_bootstrap=developer_environment_bootstrap,
    )

    _validate_repository_context_contracts(
        errors=errors,
        repo_context_contract=repo_context_contract,
        repo_context_template=repo_context_template,
        platform_repo_context=platform_repo_context,
    )

    _validate_manifest_contract(
        errors=errors,
        warnings=warnings,
        manifest=manifest,
        repository_registry=repository_registry,
        normalized_agents_contract=normalized_agents_contract,
        ecosystem_registries=ecosystem_registries,
    )

    return errors, warnings


def build_markdown(errors: list[str], warnings: list[str] | None = None) -> str:
    warnings = warnings or []
    lines = [
        "# Engineering Context System Validation",
        "",
        f"Status: `{'ok' if not errors else 'gap'}`",
        "",
    ]
    if not errors and not warnings:
        lines.append("The governed RFC-0073 context system is synchronized and valid.")
        return "\n".join(lines)

    if errors:
        lines.extend(
            [
                "## Gaps",
                "",
            ]
        )
        lines.extend(f"- {error}" for error in errors)
    if warnings:
        if errors:
            lines.append("")
        lines.extend(
            [
                "## Warnings",
                "",
            ]
        )
        lines.extend(f"- {warning}" for warning in warnings)
    return "\n".join(lines)


def main() -> int:
    errors, warnings = validate_engineering_context_system_with_warnings()
    output_dir = ROOT / "output"
    output_dir.mkdir(exist_ok=True)
    (output_dir / "engineering-context-system-validation.json").write_text(
        json.dumps(
            {
                "status": "ok" if not errors else "gap",
                "errors": errors,
                "warnings": warnings,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (output_dir / "engineering-context-system-validation.md").write_text(
        build_markdown(errors, warnings),
        encoding="utf-8",
    )
    if errors:
        print("Engineering context system validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    if warnings:
        print("Engineering context system validation passed with warnings.")
        for warning in warnings:
            print(f"- {warning}")
        return 0

    print("Engineering context system validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
