from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTEXT_DIR = ROOT / "context"


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


def validate_engineering_context_system() -> list[str]:
    errors: list[str] = []
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
        "manifest": CONTEXT_DIR / "lotus-context-manifest.json",
        "agents contract": CONTEXT_DIR / "AGENTS-OPERATING-CONTRACT.md",
        "repository context contract": CONTEXT_DIR / "Repository-Engineering-Context-Contract.md",
        "repository context template": CONTEXT_DIR / "templates" / "REPOSITORY-ENGINEERING-CONTEXT.template.md",
        "platform repo context": ROOT / "REPOSITORY-ENGINEERING-CONTEXT.md",
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
        return errors

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

    if "- Status: Implemented" not in rfc:
        errors.append("RFC-0073 must be marked Implemented once all slices are complete")
    if "Slice 5 | Drift control and validation foundation | Complete" not in checklist:
        errors.append("RFC-0073 checklist: Slice 5 must be marked complete")
    if "Slice 6 | Skills, automation, and procedural memory alignment | Complete" not in checklist:
        errors.append("RFC-0073 checklist: Slice 6 must be marked complete")
    if "Implementation posture: `Complete`" not in checklist:
        errors.append("RFC-0073 checklist must record complete implementation posture")

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

    if "./TASK-ROUTING-GUIDE.md" not in quickstart:
        errors.append("LOTUS-QUICKSTART-CONTEXT.md: missing task routing guide cross-link")
    if "./ECOSYSTEM-REGISTRIES.md" not in quickstart:
        errors.append("LOTUS-QUICKSTART-CONTEXT.md: missing ecosystem registries cross-link")
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
        "PB_SG_GLOBAL_BAL_001",
    ):
        if text not in engineering:
            errors.append(f"LOTUS-ENGINEERING-CONTEXT.md: missing front-office runtime guidance `{text}`")

    if "These are now the implementation-truth entrypoints for each repo:" not in reference_map:
        errors.append("CONTEXT-REFERENCE-MAP.md: repo-local context section is stale or missing")
    if "once it exists" in reference_map or "will become the implementation truth" in reference_map:
        errors.append("CONTEXT-REFERENCE-MAP.md: stale rollout language must not remain")

    for heading in (
        "## Frontend And Product-Surface Work",
        "## Backend API And Domain-Service Work",
        "## Cross-App Integration And Platform Validation Work",
        "## Standards, RFC, And Governance Work",
        "## Async Execution And Heavy Validation Routing",
    ):
        if heading not in task_routing_guide:
            errors.append(f"TASK-ROUTING-GUIDE.md: missing heading `{heading}`")

    if "Change Playbooks" not in procedural_memory_index:
        errors.append("PROCEDURAL-MEMORY-INDEX.md: missing Change Playbooks reference")
    if "PR Loop Playbook" not in procedural_memory_index:
        errors.append("PROCEDURAL-MEMORY-INDEX.md: missing PR Loop Playbook reference")
    if "Validation Playbook" not in procedural_memory_index:
        errors.append("PROCEDURAL-MEMORY-INDEX.md: missing Validation Playbook reference")
    if "Fix-Forward Patterns" not in procedural_memory_index:
        errors.append("PROCEDURAL-MEMORY-INDEX.md: missing Fix-Forward Patterns reference")

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
    ):
        target_doc = {
            "CHANGE-PLAYBOOKS.md": change_playbooks,
            "PR-LOOP-PLAYBOOK.md": pr_loop_playbook,
            "VALIDATION-PLAYBOOK.md": validation_playbook,
            "FIX-FORWARD-PATTERNS.md": fix_forward_patterns,
        }[label]
        if text not in target_doc:
            errors.append(f"{label}: missing required content `{text}`")

    for heading in (
        "Mandatory Reading Order",
        "Mandatory Operating Rules",
        "Context Maintenance Rule",
        "Skills, Automation, And Async Execution",
        "Front-Office Runtime Routing Rule",
    ):
        if heading not in agents_contract:
            errors.append(f"AGENTS-OPERATING-CONTRACT.md: missing section `{heading}`")
    if "PROCEDURAL-MEMORY-INDEX.md" not in agents_contract:
        errors.append("AGENTS-OPERATING-CONTRACT.md: missing procedural memory index cross-link")
    for text in (
        "lotus-workbench/docs/operations/canonical-front-office-local-runtime.md",
        "npm run live:stack:up",
        "npm run live:validate",
        "PB_SG_GLOBAL_BAL_001",
    ):
        if text not in agents_contract:
            errors.append(f"AGENTS-OPERATING-CONTRACT.md: missing front-office runtime routing `{text}`")

    for text in (
        "Validate-LotusDeveloperEnvironment.ps1 -Mode Inspect -Profile fast",
        "Bootstrap-LotusDeveloperEnvironment.ps1 -Profile fast",
        "unknown local Codex skills are preserved",
        "output/developer-environment-readiness.json",
        "output/developer-environment-readiness.md",
        "Canonical Front-Office Local Runtime",
        "npm run live:stack:up",
        "PB_SG_GLOBAL_BAL_001",
        "RFC-0074 is implemented and governed.",
    ):
        if text not in developer_onboarding:
            errors.append(f"LOTUS-DEVELOPER-ONBOARDING.md: missing bootstrap guidance `{text}`")
    if "primary front-office demo bring-up path" not in developer_onboarding:
        errors.append("LOTUS-DEVELOPER-ONBOARDING.md: missing front-office runtime boundary guidance")
    for stale_text in (
        "At Slice 5, this guide is the onboarding entrypoint",
        "Later RFC-0074 slices will add",
    ):
        if stale_text in developer_onboarding:
            errors.append(f"LOTUS-DEVELOPER-ONBOARDING.md: stale RFC-0074 boundary remains `{stale_text}`")

    if "Do not start with Tier 3 by default." not in agent_ramp_up:
        errors.append("LOTUS-AGENT-RAMP-UP.md: missing context-budget guardrail")
    if "RFC-0074 is implemented and governed." not in agent_ramp_up:
        errors.append("LOTUS-AGENT-RAMP-UP.md: missing implemented RFC-0074 boundary")
    for stale_text in (
        "automated skill sync and bootstrap readiness scripts are not implemented yet",
        "Later RFC-0074 slices will add",
        "At Slice 3, this guide defines agent ramp-up",
    ):
        if stale_text in agent_ramp_up:
            errors.append(f"LOTUS-AGENT-RAMP-UP.md: stale RFC-0074 boundary remains `{stale_text}`")
    if "automation/Bootstrap-LotusDeveloperEnvironment.ps1 -Profile fast" not in agent_ramp_up:
        errors.append("LOTUS-AGENT-RAMP-UP.md: missing bootstrap automation guidance")
    if "Platform-owned skill artifacts now exist under `lotus-platform/codex/skills`" not in agent_ramp_up and "platform-owned Lotus skills under `lotus-platform/codex/skills`" not in agent_ramp_up:
        errors.append("LOTUS-AGENT-RAMP-UP.md: missing governed skill source guidance")
    for text in (
        "## Front-Office Runtime Routing",
        "canonical-front-office-local-runtime.md",
        "npm run live:stack:up",
        "PB_SG_GLOBAL_BAL_001",
    ):
        if text not in agent_ramp_up:
            errors.append(f"LOTUS-AGENT-RAMP-UP.md: missing front-office runtime routing `{text}`")

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

    if "Context Maintenance Rule" not in repo_context_contract:
        errors.append("Repository-Engineering-Context-Contract.md: missing Context Maintenance Rule")
    if "## Context Maintenance Rule" not in repo_context_template:
        errors.append("REPOSITORY-ENGINEERING-CONTEXT.template.md: missing Context Maintenance Rule heading")
    if "## Context Maintenance Rule" not in platform_repo_context:
        errors.append("REPOSITORY-ENGINEERING-CONTEXT.md: missing Context Maintenance Rule heading")

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
    }.items():
        if procedural_memory.get(key) != expected_path:
            errors.append(f"lotus-context-manifest.json: procedural_memory.{key} must equal `{expected_path}`")

    applications = manifest.get("applications", [])
    if len(applications) != 10:
        errors.append("lotus-context-manifest.json: applications registry must include 10 Lotus repositories")
    if any(entry.get("status") != "implemented" for entry in applications):
        errors.append("lotus-context-manifest.json: all application context statuses must be `implemented`")

    standards_registry = manifest.get("standards_registry", [])
    standard_names = {entry.get("name") for entry in standards_registry if isinstance(entry, dict)}
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

    active_rfcs = manifest.get("active_rfc_registry", [])
    rfc_postures = {entry.get("id"): entry.get("implementation_posture") for entry in active_rfcs if isinstance(entry, dict)}
    if rfc_postures.get("RFC-0071") != "implemented and governed":
        errors.append("lotus-context-manifest.json: RFC-0071 implementation posture drifted")
    if "partially implemented" not in str(rfc_postures.get("RFC-0072", "")):
        errors.append("lotus-context-manifest.json: RFC-0072 implementation posture drifted")
    if rfc_postures.get("RFC-0073") != "implemented and governed":
        errors.append("lotus-context-manifest.json: RFC-0073 implementation posture drifted")
    if rfc_postures.get("RFC-0074") != "implemented and governed":
        errors.append("lotus-context-manifest.json: RFC-0074 implementation posture drifted")

    registry_renderer = _load_registry_renderer()
    rendered_registries = registry_renderer.render_registry_document(manifest)
    if ecosystem_registries != rendered_registries:
        errors.append("ECOSYSTEM-REGISTRIES.md is out of sync with lotus-context-manifest.json")

    return errors


def build_markdown(errors: list[str]) -> str:
    lines = [
        "# Engineering Context System Validation",
        "",
        f"Status: `{'ok' if not errors else 'gap'}`",
        "",
    ]
    if not errors:
        lines.append("The governed RFC-0073 context system is synchronized and valid.")
        return "\n".join(lines)

    lines.extend(
        [
            "## Gaps",
            "",
        ]
    )
    lines.extend(f"- {error}" for error in errors)
    return "\n".join(lines)


def main() -> int:
    errors = validate_engineering_context_system()
    output_dir = ROOT / "output"
    output_dir.mkdir(exist_ok=True)
    (output_dir / "engineering-context-system-validation.json").write_text(
        json.dumps({"status": "ok" if not errors else "gap", "errors": errors}, indent=2),
        encoding="utf-8",
    )
    (output_dir / "engineering-context-system-validation.md").write_text(
        build_markdown(errors),
        encoding="utf-8",
    )
    if errors:
        print("Engineering context system validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Engineering context system validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
