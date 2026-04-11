from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTEXT_DIR = ROOT / "context"
REGISTRY_RENDERER_PATH = ROOT / "automation" / "render_context_registries.py"


def _load_registry_renderer():
    spec = importlib.util.spec_from_file_location("render_context_registries", REGISTRY_RENDERER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_rfc_0073_slice_one_central_context_artifacts_exist_and_cross_link() -> None:
    rfc = (ROOT / "rfcs" / "RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md").read_text(
        encoding="utf-8"
    )
    checklist = (ROOT / "rfcs" / "RFC-0073-implementation-checklist.md").read_text(encoding="utf-8")
    context_index = (CONTEXT_DIR / "README.md").read_text(encoding="utf-8")
    quickstart = (CONTEXT_DIR / "LOTUS-QUICKSTART-CONTEXT.md").read_text(encoding="utf-8")
    engineering = (CONTEXT_DIR / "LOTUS-ENGINEERING-CONTEXT.md").read_text(encoding="utf-8")
    reference_map = (CONTEXT_DIR / "CONTEXT-REFERENCE-MAP.md").read_text(encoding="utf-8")
    ledger = (CONTEXT_DIR / "platform-engineering-ledger.md").read_text(encoding="utf-8")
    digest = (CONTEXT_DIR / "recent-architectural-decisions-digest.md").read_text(encoding="utf-8")

    assert "- Status: Implemented" in rfc
    assert "Slice 1 | Central context architecture | Complete" in checklist
    assert "human-maintained memory" in rfc
    assert "platform engineering ledger" in rfc
    assert "recent architectural decisions digest" in rfc

    assert "RFC-0073" in context_index
    assert "./LOTUS-QUICKSTART-CONTEXT.md" in context_index
    assert "./LOTUS-ENGINEERING-CONTEXT.md" in context_index
    assert "./CONTEXT-REFERENCE-MAP.md" in context_index
    assert "./lotus-context-manifest.json" in context_index

    assert "./LOTUS-ENGINEERING-CONTEXT.md" in quickstart
    assert "./CONTEXT-REFERENCE-MAP.md" in quickstart
    assert "./lotus-context-manifest.json" in quickstart
    assert "./platform-engineering-ledger.md" in quickstart
    assert "./recent-architectural-decisions-digest.md" in quickstart

    assert "./LOTUS-QUICKSTART-CONTEXT.md" in engineering
    assert "./CONTEXT-REFERENCE-MAP.md" in engineering
    assert "./lotus-context-manifest.json" in engineering
    assert "./platform-engineering-ledger.md" in engineering
    assert "./recent-architectural-decisions-digest.md" in engineering

    assert "./LOTUS-QUICKSTART-CONTEXT.md" in reference_map
    assert "./LOTUS-ENGINEERING-CONTEXT.md" in reference_map
    assert "./lotus-context-manifest.json" in reference_map
    assert "Repository-Local Context Documents" in reference_map

    assert "canonical local runtime must be treated as a governed operator flow" in ledger.lower()
    assert "ci should use github for heavy execution" in ledger.lower()
    assert "rfc-0071" in digest.lower()
    assert "rfc-0072" in digest.lower()
    assert "documentation and memory posture" in digest.lower()


def test_lotus_context_manifest_has_full_ecosystem_inventory_and_required_registries() -> None:
    manifest = json.loads((CONTEXT_DIR / "lotus-context-manifest.json").read_text(encoding="utf-8"))

    assert manifest["schema_version"] == "1.0"
    assert manifest["generated_by"] == "human-maintained"
    assert manifest["reading_order"] == [
        "AGENTS.md",
        "context/LOTUS-QUICKSTART-CONTEXT.md",
        "context/LOTUS-ENGINEERING-CONTEXT.md",
        "REPOSITORY-ENGINEERING-CONTEXT.md",
        "context/CONTEXT-REFERENCE-MAP.md",
    ]

    assert manifest["context_documents"]["index"] == "context/README.md"
    assert manifest["context_documents"]["agents_operating_contract_source"] == "context/AGENTS-OPERATING-CONTRACT.md"
    assert manifest["context_documents"]["quickstart"] == "context/LOTUS-QUICKSTART-CONTEXT.md"
    assert manifest["context_documents"]["engineering_context"] == "context/LOTUS-ENGINEERING-CONTEXT.md"
    assert manifest["context_documents"]["reference_map"] == "context/CONTEXT-REFERENCE-MAP.md"
    assert manifest["context_documents"]["task_routing_guide"] == "context/TASK-ROUTING-GUIDE.md"
    assert manifest["context_documents"]["ecosystem_registries"] == "context/ECOSYSTEM-REGISTRIES.md"
    assert manifest["context_documents"]["platform_engineering_ledger"] == "context/platform-engineering-ledger.md"
    assert (
        manifest["context_documents"]["recent_architectural_decisions_digest"]
        == "context/recent-architectural-decisions-digest.md"
    )

    assert manifest["maintenance"]["central_owner_repository"] == "lotus-platform"
    assert manifest["maintenance"]["repository_local_context_pattern"] == "REPOSITORY-ENGINEERING-CONTEXT.md"
    assert "canonical commands or validation flow changes" in manifest["maintenance"]["update_triggers"]

    assert manifest["task_routes"]["frontend"][0] == "context/LOTUS-QUICKSTART-CONTEXT.md"
    assert "REPOSITORY-ENGINEERING-CONTEXT.md" in manifest["task_routes"]["backend"]
    assert "context/lotus-context-manifest.json" in manifest["task_routes"]["platform_validation"]

    repositories = {entry["repository"] for entry in manifest["applications"]}
    assert repositories == {
        "lotus-platform",
        "lotus-workbench",
        "lotus-gateway",
        "lotus-core",
        "lotus-performance",
        "lotus-risk",
        "lotus-advise",
        "lotus-manage",
        "lotus-report",
        "lotus-ai",
    }

    assert all(entry["repo_context_path"] == "REPOSITORY-ENGINEERING-CONTEXT.md" for entry in manifest["applications"])
    assert all("requires_platform_end_to_end_validation" in entry for entry in manifest["applications"])

    authority_domains = {entry["domain"] for entry in manifest["domain_authority_map"]}
    assert authority_domains == {
        "portfolio-management-and-transactions",
        "performance-analytics",
        "risk-analytics",
        "advisory-workflows",
        "management-and-operations",
        "reporting-and-document-generation",
        "ai-capabilities",
    }

    standard_names = {entry["name"] for entry in manifest["standards_registry"]}
    assert "Continuous Integration, Validation, and Release Governance Standard" in standard_names
    assert "Testing Pyramid and Coverage Standard" in standard_names
    assert "Enterprise Readiness Standard" in standard_names
    assert "Scalability and Availability Standard" in standard_names
    assert "Domain Vocabulary Glossary" in standard_names
    assert "Platform Integration Architecture Bible" in standard_names

    active_rfcs = {entry["id"] for entry in manifest["active_rfc_registry"]}
    assert active_rfcs == {"RFC-0071", "RFC-0072", "RFC-0073", "RFC-0074"}
    implementation_postures = {entry["id"]: entry["implementation_posture"] for entry in manifest["active_rfc_registry"]}
    assert implementation_postures["RFC-0071"] == "implemented and governed"
    assert "partially implemented" in implementation_postures["RFC-0072"]
    assert implementation_postures["RFC-0073"] == "implemented and governed"
    assert implementation_postures["RFC-0074"] == "approved; Slice 1 complete"


def test_rfc_0073_slice_two_agents_operating_contract_is_governed_and_cross_linked() -> None:
    checklist = (ROOT / "rfcs" / "RFC-0073-implementation-checklist.md").read_text(encoding="utf-8")
    context_index = (CONTEXT_DIR / "README.md").read_text(encoding="utf-8")
    agents_contract = (CONTEXT_DIR / "AGENTS-OPERATING-CONTRACT.md").read_text(encoding="utf-8")
    sync_script = (ROOT / "automation" / "Sync-AgentOperatingContract.ps1").read_text(encoding="utf-8")

    assert "Slice 2 | AGENTS.md modernization | Complete" in checklist
    assert "AGENTS-OPERATING-CONTRACT.md" in context_index

    assert "Mandatory Reading Order" in agents_contract
    assert "Mandatory Operating Rules" in agents_contract
    assert "Context Maintenance Rule" in agents_contract
    assert "Skills, Automation, And Async Execution" in agents_contract
    assert "LOTUS-QUICKSTART-CONTEXT.md" in agents_contract
    assert "LOTUS-ENGINEERING-CONTEXT.md" in agents_contract
    assert "CONTEXT-REFERENCE-MAP.md" in agents_contract
    assert "REPOSITORY-ENGINEERING-CONTEXT.md" in agents_contract
    assert "deployed `AGENTS.md`" in agents_contract
    assert "Sync-AgentOperatingContract.ps1" in agents_contract
    assert '[switch]$CheckOnly' in sync_script
    assert "Normalize-ContractContent" in sync_script
    assert "Resolve-DefaultTargetPath" in sync_script
    assert 'if ($env:GITHUB_ACTIONS -eq "true")' in sync_script
    assert "Agent operating contract check skipped because deployed AGENTS target is not present on this GitHub runner" in sync_script
    assert "[System.IO.File]::WriteAllText" in sync_script
    assert "Target AGENTS file is not synchronized with the governed source." in sync_script


def test_rfc_0073_slice_three_a_repository_context_contract_and_platform_pilot_exist() -> None:
    checklist = (ROOT / "rfcs" / "RFC-0073-implementation-checklist.md").read_text(encoding="utf-8")
    reference_map = (CONTEXT_DIR / "CONTEXT-REFERENCE-MAP.md").read_text(encoding="utf-8")
    contract = (CONTEXT_DIR / "Repository-Engineering-Context-Contract.md").read_text(encoding="utf-8")
    template = (CONTEXT_DIR / "templates" / "REPOSITORY-ENGINEERING-CONTEXT.template.md").read_text(
        encoding="utf-8"
    )
    platform_repo_context = (ROOT / "REPOSITORY-ENGINEERING-CONTEXT.md").read_text(encoding="utf-8")
    manifest = json.loads((CONTEXT_DIR / "lotus-context-manifest.json").read_text(encoding="utf-8"))

    assert "Slice 3A | Repository-local context contract and platform pilot | Complete" in checklist
    assert "Repository Engineering Context Contract" in reference_map
    assert "REPOSITORY-ENGINEERING-CONTEXT.template.md" in reference_map

    for heading in (
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
    ):
        assert heading in contract
        assert f"## {heading}" in template
        assert f"## {heading}" in platform_repo_context

    assert "./context/LOTUS-QUICKSTART-CONTEXT.md" in platform_repo_context
    assert "./context/LOTUS-ENGINEERING-CONTEXT.md" in platform_repo_context
    assert "./context/CONTEXT-REFERENCE-MAP.md" in platform_repo_context
    assert (
        manifest["context_documents"]["repository_engineering_context_contract"]
        == "context/Repository-Engineering-Context-Contract.md"
    )
    statuses = {entry["repository"]: entry["status"] for entry in manifest["applications"]}
    assert statuses["lotus-platform"] == "implemented"
    assert statuses["lotus-workbench"] == "implemented"


def test_rfc_0073_slice_three_b_wave_one_rollout_is_recorded_in_manifest() -> None:
    checklist = (ROOT / "rfcs" / "RFC-0073-implementation-checklist.md").read_text(encoding="utf-8")
    manifest = json.loads((CONTEXT_DIR / "lotus-context-manifest.json").read_text(encoding="utf-8"))

    assert (
        "Slice 3B | Repository-local context rollout wave 1 (`lotus-workbench`, `lotus-gateway`, `lotus-core`) | Complete"
        in checklist
    )

    statuses = {entry["repository"]: entry["status"] for entry in manifest["applications"]}
    assert statuses["lotus-workbench"] == "implemented"
    assert statuses["lotus-gateway"] == "implemented"
    assert statuses["lotus-core"] == "implemented"
    assert statuses["lotus-performance"] == "implemented"


def test_rfc_0073_slice_three_c_wave_two_rollout_is_recorded_in_manifest() -> None:
    checklist = (ROOT / "rfcs" / "RFC-0073-implementation-checklist.md").read_text(encoding="utf-8")
    manifest = json.loads((CONTEXT_DIR / "lotus-context-manifest.json").read_text(encoding="utf-8"))

    assert "Slice 3 | Repository-local context rollout | Complete" in checklist
    assert (
        "Slice 3C | Repository-local context rollout wave 2 (`lotus-performance`, `lotus-risk`, `lotus-advise`, `lotus-manage`, `lotus-report`, `lotus-ai`) | Complete"
        in checklist
    )

    statuses = {entry["repository"]: entry["status"] for entry in manifest["applications"]}
    assert statuses["lotus-performance"] == "implemented"
    assert statuses["lotus-risk"] == "implemented"
    assert statuses["lotus-advise"] == "implemented"
    assert statuses["lotus-manage"] == "implemented"
    assert statuses["lotus-report"] == "implemented"
    assert statuses["lotus-ai"] == "implemented"


def test_rfc_0073_slice_four_task_routing_and_registries_are_hardened() -> None:
    checklist = (ROOT / "rfcs" / "RFC-0073-implementation-checklist.md").read_text(encoding="utf-8")
    context_index = (CONTEXT_DIR / "README.md").read_text(encoding="utf-8")
    quickstart = (CONTEXT_DIR / "LOTUS-QUICKSTART-CONTEXT.md").read_text(encoding="utf-8")
    engineering = (CONTEXT_DIR / "LOTUS-ENGINEERING-CONTEXT.md").read_text(encoding="utf-8")
    reference_map = (CONTEXT_DIR / "CONTEXT-REFERENCE-MAP.md").read_text(encoding="utf-8")
    registries = (CONTEXT_DIR / "ECOSYSTEM-REGISTRIES.md").read_text(encoding="utf-8")
    task_routing_guide = (CONTEXT_DIR / "TASK-ROUTING-GUIDE.md").read_text(encoding="utf-8")
    manifest = json.loads((CONTEXT_DIR / "lotus-context-manifest.json").read_text(encoding="utf-8"))
    registry_renderer = _load_registry_renderer()

    assert "Slice 4 | Reference map and task-routing hardening | Complete" in checklist
    assert "./TASK-ROUTING-GUIDE.md" in context_index
    assert "./ECOSYSTEM-REGISTRIES.md" in context_index
    assert "./PROCEDURAL-MEMORY-INDEX.md" in context_index

    assert "./TASK-ROUTING-GUIDE.md" in quickstart
    assert "./ECOSYSTEM-REGISTRIES.md" in quickstart

    assert "## Task Routing Guidance" in engineering
    assert "./TASK-ROUTING-GUIDE.md" in engineering
    assert "./ECOSYSTEM-REGISTRIES.md" in engineering
    assert "./PROCEDURAL-MEMORY-INDEX.md" in engineering

    assert "./TASK-ROUTING-GUIDE.md" in reference_map
    assert "./ECOSYSTEM-REGISTRIES.md" in reference_map
    assert "These are now the implementation-truth entrypoints for each repo:" in reference_map
    assert "once it exists" not in reference_map
    assert "will become the implementation truth" not in reference_map

    for heading in (
        "## Frontend And Product-Surface Work",
        "## Backend API And Domain-Service Work",
        "## Cross-App Integration And Platform Validation Work",
        "## Standards, RFC, And Governance Work",
        "## Async Execution And Heavy Validation Routing",
    ):
        assert heading in task_routing_guide

    assert "## Application Registry" in registries
    assert "## Domain Authority Map" in registries
    assert "## Standards Registry" in registries
    assert "## Active RFC Registry" in registries

    rendered = registry_renderer.render_registry_document(manifest)
    assert registries == rendered


def test_rfc_0073_slice_five_context_drift_controls_are_wired_into_platform_repo_checks() -> None:
    checklist = (ROOT / "rfcs" / "RFC-0073-implementation-checklist.md").read_text(encoding="utf-8")
    automation_readme = (ROOT / "automation" / "README.md").read_text(encoding="utf-8")
    directory_map = (ROOT / "automation" / "docs" / "Directory-Map.md").read_text(encoding="utf-8")
    repo_checks = (ROOT / "automation" / "Invoke-PlatformRepoChecks.ps1").read_text(encoding="utf-8")
    validator = (ROOT / "automation" / "validate_engineering_context_system.py").read_text(encoding="utf-8")

    assert "Slice 5 | Drift control and validation foundation | Complete" in checklist
    assert "python automation/validate_engineering_context_system.py" in automation_readme
    assert "output/engineering-context-system-validation.json" in automation_readme
    assert "output/engineering-context-system-validation.md" in automation_readme
    assert "validate_engineering_context_system.py" in directory_map
    assert "& $toolingPython automation/validate_engineering_context_system.py" in repo_checks
    assert 'Sync-AgentOperatingContract.ps1") -CheckOnly' in repo_checks
    assert "ECOSYSTEM-REGISTRIES.md is out of sync with lotus-context-manifest.json" in validator
    assert "all application context statuses must be `implemented`" in validator


def test_rfc_0073_slice_six_procedural_memory_is_governed_and_linked() -> None:
    rfc = (ROOT / "rfcs" / "RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md").read_text(
        encoding="utf-8"
    )
    checklist = (ROOT / "rfcs" / "RFC-0073-implementation-checklist.md").read_text(encoding="utf-8")
    context_index = (CONTEXT_DIR / "README.md").read_text(encoding="utf-8")
    quickstart = (CONTEXT_DIR / "LOTUS-QUICKSTART-CONTEXT.md").read_text(encoding="utf-8")
    engineering = (CONTEXT_DIR / "LOTUS-ENGINEERING-CONTEXT.md").read_text(encoding="utf-8")
    reference_map = (CONTEXT_DIR / "CONTEXT-REFERENCE-MAP.md").read_text(encoding="utf-8")
    agents_contract = (CONTEXT_DIR / "AGENTS-OPERATING-CONTRACT.md").read_text(encoding="utf-8")
    automation_readme = (ROOT / "automation" / "README.md").read_text(encoding="utf-8")
    directory_map = (ROOT / "automation" / "docs" / "Directory-Map.md").read_text(encoding="utf-8")
    repo_checks = (ROOT / "automation" / "Invoke-PlatformRepoChecks.ps1").read_text(encoding="utf-8")
    procedural_memory_index = (CONTEXT_DIR / "PROCEDURAL-MEMORY-INDEX.md").read_text(encoding="utf-8")
    change_playbooks = (CONTEXT_DIR / "playbooks" / "CHANGE-PLAYBOOKS.md").read_text(encoding="utf-8")
    pr_loop_playbook = (CONTEXT_DIR / "playbooks" / "PR-LOOP-PLAYBOOK.md").read_text(encoding="utf-8")
    validation_playbook = (CONTEXT_DIR / "playbooks" / "VALIDATION-PLAYBOOK.md").read_text(encoding="utf-8")
    fix_forward_patterns = (CONTEXT_DIR / "playbooks" / "FIX-FORWARD-PATTERNS.md").read_text(encoding="utf-8")
    manifest = json.loads((CONTEXT_DIR / "lotus-context-manifest.json").read_text(encoding="utf-8"))

    assert "- Status: Implemented" in rfc
    assert "Implementation posture: `Complete`" in checklist
    assert "Slice 6 | Skills, automation, and procedural memory alignment | Complete" in checklist
    assert "./PROCEDURAL-MEMORY-INDEX.md" in context_index
    assert "./PROCEDURAL-MEMORY-INDEX.md" in quickstart
    assert "./PROCEDURAL-MEMORY-INDEX.md" in engineering
    assert "./PROCEDURAL-MEMORY-INDEX.md" in reference_map

    assert "Change Playbooks" in procedural_memory_index
    assert "PR Loop Playbook" in procedural_memory_index
    assert "Validation Playbook" in procedural_memory_index
    assert "Fix-Forward Patterns" in procedural_memory_index

    assert "Backend API And Domain-Service Change Playbook" in change_playbooks
    assert "Frontend And Product-Surface Change Playbook" in change_playbooks
    assert "Cross-Repository Integration Change Playbook" in change_playbooks
    assert "RFC-Driven Slice Playbook" in change_playbooks
    assert "GitHub-Backed Heavy Execution Rule" in pr_loop_playbook
    assert "Platform End-To-End Proof" in validation_playbook
    assert "Local-Only Assumption Pattern" in fix_forward_patterns
    assert "Fix-Forward Patterns" in reference_map
    assert "PROCEDURAL-MEMORY-INDEX.md" in agents_contract
    assert "python automation/validate_lotus_skill_alignment.py" in automation_readme
    assert "output/lotus-skill-alignment-validation.json" in automation_readme
    assert "validate_lotus_skill_alignment.py" in directory_map
    assert "& $toolingPython automation/validate_lotus_skill_alignment.py" in repo_checks

    assert manifest["context_documents"]["procedural_memory_index"] == "context/PROCEDURAL-MEMORY-INDEX.md"
    assert manifest["procedural_memory"]["change_playbooks"] == "context/playbooks/CHANGE-PLAYBOOKS.md"
    assert manifest["procedural_memory"]["pr_loop_playbook"] == "context/playbooks/PR-LOOP-PLAYBOOK.md"
    assert manifest["procedural_memory"]["validation_playbook"] == "context/playbooks/VALIDATION-PLAYBOOK.md"
    assert manifest["procedural_memory"]["fix_forward_patterns"] == "context/playbooks/FIX-FORWARD-PATTERNS.md"


def test_rfc_0074_slice_two_developer_onboarding_is_governed_and_linked() -> None:
    checklist = (ROOT / "rfcs" / "RFC-0074-implementation-checklist.md").read_text(encoding="utf-8")
    reference_map = (CONTEXT_DIR / "CONTEXT-REFERENCE-MAP.md").read_text(encoding="utf-8")
    onboarding = (ROOT / "docs" / "onboarding" / "LOTUS-DEVELOPER-ONBOARDING.md").read_text(
        encoding="utf-8"
    )

    assert "Slice 2 | Developer onboarding guide | Complete" in checklist
    assert "docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md" in checklist
    assert "../docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md" in reference_map

    for required_link in (
        "../../rfcs/RFC-0071-centralized-environment-scoped-service-addressing-and-ingress-governance.md",
        "../../rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md",
        "../../rfcs/RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md",
        "../../rfcs/RFC-0074-repeatable-developer-and-agent-bootstrap-system.md",
        "../../Local%20Development%20Runbook.md",
        "../../context/LOTUS-QUICKSTART-CONTEXT.md",
        "../../context/CONTEXT-REFERENCE-MAP.md",
        "../../context/AGENTS-OPERATING-CONTRACT.md",
        "../../context/playbooks/PR-LOOP-PLAYBOOK.md",
        "../../context/playbooks/VALIDATION-PLAYBOOK.md",
        "../../context/playbooks/FIX-FORWARD-PATTERNS.md",
    ):
        assert required_link in onboarding

    for heading in (
        "## Expected Workspace Layout",
        "## First Pull Sequence",
        "## Prerequisite Classification",
        "### Required For Normal Development",
        "### Required For Full-Stack Validation",
        "### Optional Or Task-Specific",
        "## Codex Agent Context And Skills",
        "## GitHub And CI Posture",
        "## Ingress And Canonical Endpoints",
        "## DSN And Environment Posture",
        "## Validation Depth",
        "## Fresh Machine Readiness Checklist",
        "## Current RFC-0074 Boundary",
    ):
        assert heading in onboarding

    for required_phrase in (
        "Onboarding should not silently start Docker stacks",
        "Do not overwrite local Codex guidance blindly",
        "Do not run full local CI reflexively",
        "Until those slices are complete, do not assume bootstrap scripts or platform-owned skill sync exist.",
        "http://workbench.dev.lotus",
        "http://gateway.dev.lotus",
        "gh pr checks <pr-number> --watch=false",
        "powershell -ExecutionPolicy Bypass -File automation\\Sync-Dev-Ingress-Hosts.ps1 -Apply",
    ):
        assert required_phrase in onboarding


def test_rfc_0074_slice_three_agent_ramp_up_is_governed_and_linked() -> None:
    checklist = (ROOT / "rfcs" / "RFC-0074-implementation-checklist.md").read_text(encoding="utf-8")
    reference_map = (CONTEXT_DIR / "CONTEXT-REFERENCE-MAP.md").read_text(encoding="utf-8")
    ramp_up = (ROOT / "docs" / "onboarding" / "LOTUS-AGENT-RAMP-UP.md").read_text(
        encoding="utf-8"
    )

    assert "Implementation posture: `Approved | Slice 3 complete`" in checklist
    assert "Slice 3 | Agent ramp-up guide and first-prompt standard | Complete" in checklist
    assert "docs/onboarding/LOTUS-AGENT-RAMP-UP.md" in checklist
    assert "../docs/onboarding/LOTUS-AGENT-RAMP-UP.md" in reference_map

    for required_link in (
        "../../rfcs/RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md",
        "../../rfcs/RFC-0074-repeatable-developer-and-agent-bootstrap-system.md",
        "../../context/LOTUS-QUICKSTART-CONTEXT.md",
        "../../context/LOTUS-ENGINEERING-CONTEXT.md",
        "../../context/CONTEXT-REFERENCE-MAP.md",
        "../../context/PROCEDURAL-MEMORY-INDEX.md",
        "../../context/AGENTS-OPERATING-CONTRACT.md",
        "../../context/playbooks/PR-LOOP-PLAYBOOK.md",
        "../../context/playbooks/VALIDATION-PLAYBOOK.md",
        "../../context/playbooks/FIX-FORWARD-PATTERNS.md",
        "./LOTUS-DEVELOPER-ONBOARDING.md",
    ):
        assert required_link in ramp_up

    for heading in (
        "## First Prompt Template",
        "## First-Turn Checklist",
        "## Context Budget Tiers",
        "### Tier 1: Startup Context",
        "### Tier 2: Governance Context",
        "### Tier 3: Deep Context",
        "## Skill Selection",
        "## Validation Lane Selection",
        "## Async GitHub Monitoring",
        "## Context Maintenance Rule",
        "## Anti-Patterns",
        "## Current RFC-0074 Boundary",
    ):
        assert heading in ramp_up

    for required_phrase in (
        "Read <lotus-platform>/context/LOTUS-QUICKSTART-CONTEXT.md",
        "Read C:\\Users\\Sandeep\\projects\\lotus-platform\\context\\LOTUS-QUICKSTART-CONTEXT.md",
        "Do not start with Tier 3 by default.",
        "lotus-backend-delivery-governance",
        "lotus-frontend-delivery-governance",
        "lotus-pr-premerge-gate",
        "gh pr checks <pr-number> --watch=false",
        "Do not update durable context for transient CI state unless it becomes a repeatable pattern.",
        "Until those slices are complete, do not assume platform-owned skill sync or bootstrap readiness scripts exist.",
    ):
        assert required_phrase in ramp_up
