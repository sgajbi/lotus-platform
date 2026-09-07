from __future__ import annotations

import importlib.util
import json
import re

import pytest
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
    assert "front-office product proof must route through the governed workbench runtime" in ledger.lower()
    assert "ci should use github for heavy execution" in ledger.lower()
    assert "rfc-0071" in digest.lower()
    assert "rfc-0072" in digest.lower()
    assert "documentation and memory posture" in digest.lower()
    assert "front-office local runtime routing" in digest.lower()


def test_lotus_context_manifest_has_full_ecosystem_inventory_and_required_registries() -> None:
    manifest = json.loads((CONTEXT_DIR / "lotus-context-manifest.json").read_text(encoding="utf-8"))

    assert manifest["schema_version"] == "1.0"
    assert manifest["generated_by"] == "human-maintained"
    # The startup set, not the old flat order: the repository's own context and
    # the skill routing map replace the broad engineering context and reference
    # map, which are task-routed now rather than read by default.
    assert manifest["reading_order"] == [
        "AGENTS.md",
        "context/LOTUS-QUICKSTART-CONTEXT.md",
        "REPOSITORY-ENGINEERING-CONTEXT.md",
        "context/LOTUS-SKILL-ROUTING-MAP.md",
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

    # A task route lists what the task *adds* to the startup set, not an absolute
    # reading list, which is what `task_routes_extend_reading_order` declares. So
    # the startup documents must not be repeated inside a route, and a route that
    # adds nothing is legitimately empty.
    startup = set(manifest["reading_order"])
    for name, additions in manifest["task_routes"].items():
        assert not startup.intersection(additions), (
            f"{name} repeats a startup document instead of extending the set: "
            f"{sorted(startup.intersection(additions))}"
        )

    assert manifest["task_routes"]["frontend"] == [], (
        "frontend adds nothing beyond the startup set; its broad context is conditional"
    )
    assert "context/CONTEXT-REFERENCE-MAP.md" in manifest["task_routes"]["backend"]
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
        "lotus-render",
        "lotus-archive",
        "lotus-ai",
        "lotus-idea",
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
        "generated-document-archive-retrieval-retention-and-legal-hold",
        "ai-capabilities",
        "opportunity-intelligence-and-idea-lifecycle",
    }

    standard_names = {entry["name"] for entry in manifest["standards_registry"]}
    assert "Continuous Integration, Validation, and Release Governance Standard" in standard_names
    assert "Testing Pyramid and Coverage Standard" in standard_names
    assert "Enterprise Readiness Standard" in standard_names
    assert "Lotus Bank-Buyable Engineering Contract" in standard_names
    assert "Scalability and Availability Standard" in standard_names
    assert "Domain Vocabulary Glossary" in standard_names
    assert "Platform Integration Architecture Bible" in standard_names

    active_rfcs = {entry["id"] for entry in manifest["active_rfc_registry"]}
    assert active_rfcs == {
        "RFC-0071",
        "RFC-0072",
        "RFC-0073",
        "RFC-0074",
        "RFC-0093",
        "RFC-0094",
        "RFC-0095",
        "RFC-0096",
        "RFC-0103",
    }
    implementation_postures = {
        entry["id"]: entry["implementation_posture"]
        for entry in manifest["active_rfc_registry"]
    }
    assert implementation_postures["RFC-0071"] == "implemented and governed"
    assert "partially implemented" in implementation_postures["RFC-0072"]
    assert implementation_postures["RFC-0073"] == "implemented and governed"
    assert implementation_postures["RFC-0074"] == "implemented and governed"
    assert implementation_postures["RFC-0093"] == "implemented on main"
    assert implementation_postures["RFC-0094"] == "implemented on main"
    assert implementation_postures["RFC-0095"] == "implemented"
    assert implementation_postures["RFC-0096"] == "implemented"
    assert "implemented for supported first-wave archive scope" in implementation_postures["RFC-0103"]
    assert "Workbench retrieval and production certification deferred" in implementation_postures["RFC-0103"]


def test_rfc_0073_slice_two_agents_operating_contract_is_governed_and_cross_linked() -> None:
    checklist = (ROOT / "rfcs" / "RFC-0073-implementation-checklist.md").read_text(encoding="utf-8")
    context_index = (CONTEXT_DIR / "README.md").read_text(encoding="utf-8")
    agents_contract = (CONTEXT_DIR / "AGENTS-OPERATING-CONTRACT.md").read_text(encoding="utf-8")
    sync_script = (ROOT / "automation" / "Sync-AgentOperatingContract.ps1").read_text(encoding="utf-8")

    assert "Slice 2 | AGENTS.md modernization | Complete" in checklist
    assert "AGENTS-OPERATING-CONTRACT.md" in context_index

    assert "Progressive Context Discovery" in agents_contract
    assert "Before substantial work, load this small starting set" in agents_contract
    assert "Do not load the complete context estate by default" in agents_contract
    assert "Target Repository Root Rule" in agents_contract
    assert "Mandatory Operating Rules" in agents_contract
    assert "Context Maintenance Rule" in agents_contract
    assert "Skills, Automation, And Async Execution" in agents_contract
    assert "Front-Office Runtime Routing Rule" in agents_contract
    assert "LOTUS-QUICKSTART-CONTEXT.md" in agents_contract
    assert "LOTUS-ENGINEERING-CONTEXT.md" in agents_contract
    assert "CONTEXT-REFERENCE-MAP.md" in agents_contract
    assert "REPOSITORY-ENGINEERING-CONTEXT.md" in agents_contract
    assert "Do not assume the inherited shell working directory is the task repository" in agents_contract
    assert "inspect the active branch, worktrees, and existing changes before editing" in agents_contract
    assert "designated repository owner" in agents_contract
    assert "to continue scoped work" in agents_contract
    assert "VS Code multi-root" in agents_contract
    assert "switch command `workdir` to that target repo" in agents_contract
    assert "child agents do not inherit the wrong cwd" in agents_contract
    assert "deployed `AGENTS.md`" in agents_contract
    assert "Sync-AgentOperatingContract.ps1" in agents_contract
    assert "canonical-front-office-local-runtime.md" in agents_contract
    assert "npm run live:stack:up" in agents_contract
    assert "PB_SG_GLOBAL_BAL_001" in agents_contract
    assert "Canonical platform QA includes `lotus-idea` by default" in agents_contract
    assert "Do not reintroduce an opt-in flag" in agents_contract


def test_agent_entry_points_share_one_authoritative_contract() -> None:
    agents_contract = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    governed_contract = (CONTEXT_DIR / "AGENTS-OPERATING-CONTRACT.md").read_text(
        encoding="utf-8"
    )
    claude_adapter = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    sync_script = (ROOT / "automation" / "Sync-AgentOperatingContract.ps1").read_text(
        encoding="utf-8"
    )

    assert agents_contract == governed_contract
    assert "[AGENTS.md](AGENTS.md)" in claude_adapter
    assert "[REPOSITORY-ENGINEERING-CONTEXT.md](REPOSITORY-ENGINEERING-CONTEXT.md)" in claude_adapter
    assert "adapter, not a second policy source" in claude_adapter
    assert "## Mandatory Operating Rules" not in claude_adapter
    assert '[switch]$CheckOnly' in sync_script
    assert "Normalize-ContractContent" in sync_script
    assert "Resolve-DefaultTargetPath" in sync_script
    assert '$target.kind -eq "deployed" -and $env:GITHUB_ACTIONS -eq "true"' in sync_script
    assert "Agent operating contract check skipped because deployed AGENTS target is not present on this GitHub runner" in sync_script
    assert "[System.IO.File]::WriteAllText" in sync_script
    assert "Target AGENTS file is not synchronized with the governed source:" in sync_script


def test_rfc_0073_slice_two_a_repo_root_agents_are_synchronized_and_validated() -> None:
    checklist = (ROOT / "rfcs" / "RFC-0073-implementation-checklist.md").read_text(encoding="utf-8")
    evidence = (
        ROOT / "rfcs" / "RFC-0073-slice-2a-repo-root-agents-deployment-and-drift-control-evidence.md"
    ).read_text(encoding="utf-8")
    agents_contract = (CONTEXT_DIR / "AGENTS-OPERATING-CONTRACT.md").read_text(encoding="utf-8")
    platform_repo_agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    sync_script = (ROOT / "automation" / "Sync-AgentOperatingContract.ps1").read_text(encoding="utf-8")
    validator = (ROOT / "automation" / "validate_engineering_context_system.py").read_text(encoding="utf-8")
    repo_checks = (ROOT / "automation" / "Invoke-PlatformRepoChecks.ps1").read_text(encoding="utf-8")

    assert "Implementation posture: `Complete`" in checklist
    assert "Slice 2A | Repo-root AGENTS deployment and drift control | Complete" in checklist
    assert "Review outcome:" in checklist
    assert "repo-root `AGENTS.md` drift visibility now exists through the context validator" in checklist

    assert "repo-root `AGENTS.md` copies across the in-scope Lotus repositories" in evidence
    assert "`automation/Sync-AgentOperatingContract.ps1` now supports" in evidence
    assert "The mandatory slice review was completed before moving forward." in evidence
    assert "no repo-specific content was added to repo-root `AGENTS.md`" in evidence

    assert platform_repo_agents == agents_contract
    assert "Repo-root `AGENTS.md` files across Lotus repositories" in agents_contract
    assert "automation/repos.json" in validator
    assert "application_repositories != registered_repositories" in validator
    assert "applications registry must include 11 Lotus repositories" not in validator

    for required_item in (
        "[string[]]$Repository = @()",
        "[switch]$AllRepoRoots",
        "[switch]$IncludeDeployedTarget",
        "Resolve-RequestedTargets",
        "Resolve-RepoRootTargetPath",
        # The deployed copy is still supported, but it is no longer the target a
        # bare check falls back to: on a runner that file does not exist, so the
        # check skipped its only target and reported success having compared
        # nothing. A bare check now defaults to this repository's own copy.
        "deployed target",
        "lotus-platform repo-root target",
    ):
        assert required_item in sync_script

    assert "default deployed target" not in sync_script, (
        "a bare -CheckOnly must not fall back to the machine-local deployed file"
    )

    assert 'Sync-AgentOperatingContract.ps1") -CheckOnly -TargetPath (Join-Path $repoRoot "AGENTS.md")' not in repo_checks
    assert "platform repo agents" in validator
    assert "repo-root AGENTS.md is not synchronized" in validator
    assert "missing repo-root AGENTS.md" in validator


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
    assert (
        "`lotus-idea` is repo-native and included by default in canonical platform/runtime automation"
        in engineering
    )
    assert "do not reintroduce an opt-in flag" in engineering
    assert "future-wave `lotus-idea`" not in engineering
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
    assert (
        "Invoke-CheckedCommand $toolingPython automation/validate_engineering_context_system.py"
        in repo_checks
    )
    assert (
        '$agentContractScript = Join-Path $PSScriptRoot "Sync-AgentOperatingContract.ps1"'
        in repo_checks
    )
    assert "& $agentContractScript -CheckOnly" in repo_checks
    assert 'Assert-LastExitCode "$agentContractScript -CheckOnly"' in repo_checks
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
    agent_context_task_ledger = (
        CONTEXT_DIR / "playbooks" / "AGENT-CONTEXT-AND-TASK-LEDGER.md"
    ).read_text(encoding="utf-8")
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
    assert "Agent Context And Task Ledger Playbook" in procedural_memory_index
    assert "Agentic Coding Quality Evaluation Loop" in procedural_memory_index

    assert "Backend API And Domain-Service Change Playbook" in change_playbooks
    assert "Frontend And Product-Surface Change Playbook" in change_playbooks
    assert "Cross-Repository Integration Change Playbook" in change_playbooks
    assert "RFC-Driven Slice Playbook" in change_playbooks
    assert "GitHub-Backed Heavy Execution Rule" in pr_loop_playbook
    assert "Platform End-To-End Proof" in validation_playbook
    assert "Local-Only Assumption Pattern" in fix_forward_patterns
    assert "Identifier Preservation" in agent_context_task_ledger
    assert "Detached Task Ledger" in agent_context_task_ledger
    assert "delegation-policy-contract.v1.json" in agent_context_task_ledger
    assert "Delegated code changes are evidence, not review" in agent_context_task_ledger
    assert "overlapping active write scopes" in agent_context_task_ledger
    assert "Promotion Decisions" in agent_context_task_ledger
    assert "Fix-Forward Patterns" in reference_map
    assert "Agent Context And Task Ledger Playbook" in reference_map
    assert "Agentic Coding Quality Evaluation Loop" in reference_map
    assert "PROCEDURAL-MEMORY-INDEX.md" in agents_contract
    assert "AGENT-CONTEXT-AND-TASK-LEDGER.md" in agents_contract
    assert "engineering_task_id" in agents_contract
    assert "output/background-runs.json" in agents_contract
    assert "delegation-policy-contract.v1.json" in agents_contract
    assert "Delegate only bounded non-blocking work" in agents_contract
    assert "Do not delegate broad" in agents_contract
    assert "Wiki Publication Rule" in agents_contract
    assert "Sync-RepoWikis.ps1" in agents_contract
    assert "Repo-local `wiki/` is the authored source of truth" in agents_contract
    assert "-AllowUnpublishedSourceChanges" in agents_contract
    assert "strict parity verification" in agents_contract
    assert (
        "Sync-RepoWikis.ps1 -CheckOnly -Repository lotus-platform -AllowUnpublishedSourceChanges"
        in engineering
    )
    assert "strict parity" in engineering
    assert "python automation/validate_lotus_skill_alignment.py" in automation_readme
    assert "output/lotus-skill-alignment-validation.json" in automation_readme
    assert "validate_lotus_skill_alignment.py" in directory_map
    assert (
        "Invoke-CheckedCommand $toolingPython automation/validate_lotus_skill_alignment.py"
        in repo_checks
    )
    assert (
        '$repoWikiSyncScript = Join-Path $PSScriptRoot "Sync-RepoWikis.ps1"'
        in repo_checks
    )
    assert (
        '& $repoWikiSyncScript -CheckOnly -Repository "lotus-platform" '
        "-AllowUnpublishedSourceChanges"
        in repo_checks
    )

    assert manifest["context_documents"]["procedural_memory_index"] == "context/PROCEDURAL-MEMORY-INDEX.md"
    assert manifest["procedural_memory"]["change_playbooks"] == "context/playbooks/CHANGE-PLAYBOOKS.md"
    assert manifest["procedural_memory"]["pr_loop_playbook"] == "context/playbooks/PR-LOOP-PLAYBOOK.md"
    assert manifest["procedural_memory"]["validation_playbook"] == "context/playbooks/VALIDATION-PLAYBOOK.md"
    assert manifest["procedural_memory"]["fix_forward_patterns"] == "context/playbooks/FIX-FORWARD-PATTERNS.md"
    assert (
        manifest["procedural_memory"]["agent_context_and_task_ledger"]
        == "context/playbooks/AGENT-CONTEXT-AND-TASK-LEDGER.md"
    )
    assert (
        manifest["procedural_memory"]["agentic_coding_quality_evaluation_loop"]
        == "context/playbooks/AGENTIC-CODING-QUALITY-EVALUATION-LOOP.md"
    )


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
        "../operations/Local%20Development%20Runbook.md",
        "https://github.com/sgajbi/lotus-workbench/blob/main/docs/operations/"
        "canonical-front-office-local-runtime.md",
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
        "## Canonical Front-Office Runtime",
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
        "platform-owned bootstrap automation exists",
        "http://workbench.dev.lotus",
        "http://gateway.dev.lotus",
        "gh pr checks <pr-number> --watch=false",
        "powershell -ExecutionPolicy Bypass -File automation\\Sync-Dev-Ingress-Hosts.ps1 -Apply",
        "Canonical Front-Office Local Runtime",
        "npm run live:stack:up",
        "PB_SG_GLOBAL_BAL_001",
        "primary front-office demo bring-up path",
        "RFC-0074 is implemented and governed.",
    ):
        assert required_phrase in onboarding

    for stale_phrase in (
        "At Slice 5, this guide is the onboarding entrypoint",
        "Later RFC-0074 slices will add",
    ):
        assert stale_phrase not in onboarding


def test_rfc_0074_slice_three_agent_ramp_up_is_governed_and_linked() -> None:
    checklist = (ROOT / "rfcs" / "RFC-0074-implementation-checklist.md").read_text(encoding="utf-8")
    reference_map = (CONTEXT_DIR / "CONTEXT-REFERENCE-MAP.md").read_text(encoding="utf-8")
    ramp_up = (ROOT / "docs" / "onboarding" / "LOTUS-AGENT-RAMP-UP.md").read_text(
        encoding="utf-8"
    )

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
        "## Front-Office Runtime Routing",
        "## Async GitHub Monitoring",
        "## Context Maintenance Rule",
        "## Anti-Patterns",
        "## Current RFC-0074 Boundary",
    ):
        assert heading in ramp_up

    for required_phrase in (
        "Read the target repository's AGENTS.md, <lotus-platform>/context/LOTUS-QUICKSTART-CONTEXT.md",
        "Read the target repository's AGENTS.md, <workspace-root>/lotus-platform/context/LOTUS-QUICKSTART-CONTEXT.md",
        "Do not start with Tier 3 by default.",
        "lotus-backend-delivery-governance",
        "lotus-frontend-delivery-governance",
        "lotus-pr-premerge-gate",
        "gh pr checks <pr-number> --watch=false",
        "Do not update durable context for transient CI state unless it becomes a repeatable pattern.",
        "RFC-0074 is implemented and governed.",
        "automation/Bootstrap-LotusDeveloperEnvironment.ps1 -Profile fast",
        "platform-owned Lotus skills under `lotus-platform/codex/skills`",
        "canonical-front-office-local-runtime.md",
        "PB_SG_GLOBAL_BAL_001",
        "lotus-platform/platform-stack",
    ):
        assert required_phrase in ramp_up

    for stale_phrase in (
        "automated skill sync and bootstrap readiness scripts are not implemented yet",
        "Later RFC-0074 slices will add",
        "At Slice 3, this guide defines agent ramp-up",
    ):
        assert stale_phrase not in ramp_up


def test_rfc_0074_slice_four_lotus_skill_inventory_is_governed() -> None:
    checklist = (ROOT / "rfcs" / "RFC-0074-implementation-checklist.md").read_text(encoding="utf-8")
    developer_onboarding = (ROOT / "docs" / "onboarding" / "LOTUS-DEVELOPER-ONBOARDING.md").read_text(
        encoding="utf-8"
    )
    ramp_up = (ROOT / "docs" / "onboarding" / "LOTUS-AGENT-RAMP-UP.md").read_text(encoding="utf-8")
    skills_root = ROOT / "codex" / "skills"
    manifest = json.loads((skills_root / "lotus-skill-manifest.json").read_text(encoding="utf-8"))
    readme = (skills_root / "README.md").read_text(encoding="utf-8")

    assert "Implementation posture: `Complete`" in checklist
    assert "Slice 4 | Skill distribution and synchronization design | Complete" in checklist
    assert "codex/skills/lotus-skill-manifest.json" in checklist
    assert "../../codex/skills/README.md" in developer_onboarding
    assert "lotus-platform/codex/skills" in ramp_up

    expected_skills = {
        "gh-address-comments",
        "gh-fix-ci",
        "gh-issue-fix-qa-loop",
        "lotus-backend-delivery-governance",
        "lotus-app-issue-discovery",
        "lotus-codebase-review-ledger",
        "lotus-ci-enforcement-governance",
        "lotus-demo-readiness-certification",
        "lotus-endpoint-certification-loop",
        "lotus-skill-context-governance",
        "lotus-frontend-delivery-governance",
        "lotus-front-office-runtime",
        "lotus-linkedin-thought-leadership",
        "lotus-methodology-doc-v3",
        "lotus-pr-premerge-gate",
        "lotus-qa-platform-validator",
        "lotus-readme-wiki-governance",
        "lotus-rfc-review-loop",
        "lotus-rfc0067-rollout",
        "lotus-transaction-rfc-loop",
        "lotus-validation-resolution-lifecycle",
        "platform-automation-ops",
        "platform-pulse-monitor",
        "targeted-service-refresh",
    }
    manifest_names = {entry["name"] for entry in manifest["skills"]}
    directory_names = {path.name for path in skills_root.iterdir() if path.is_dir()}

    assert manifest["source"] == "lotus-platform/codex/skills"
    assert manifest["unknown_local_skill_policy"] == "preserve"
    assert manifest_names == expected_skills
    assert directory_names == expected_skills

    for entry in manifest["skills"]:
        skill_dir = ROOT / entry["path"]
        skill_doc = skill_dir / "SKILL.md"
        assert skill_dir.exists()
        assert skill_doc.exists()
        assert f"name: {entry['name']}" in skill_doc.read_text(encoding="utf-8")

    assert any(entry["name"] == "gh-address-comments" and not entry["directly_lotus_owned"] for entry in manifest["skills"])
    assert any(entry["name"] == "gh-fix-ci" and not entry["directly_lotus_owned"] for entry in manifest["skills"])
    assert any(entry["name"] == "gh-issue-fix-qa-loop" and not entry["directly_lotus_owned"] for entry in manifest["skills"])
    assert "Unknown local skills must be preserved" in readme

    governed_text_suffixes = {".json", ".md", ".ps1", ".py", ".toml", ".yaml", ".yml"}
    governed_text_paths = [
        path
        for path in skills_root.rglob("*")
        if path.is_file() and path.suffix.lower() in governed_text_suffixes
    ]
    assert governed_text_paths
    assert not any(path.suffix == ".pyc" for path in governed_text_paths)
    for path in governed_text_paths:
        text = path.read_text(encoding="utf-8")
        assert "pbwm-platform-docs" not in text
        assert "C:\\Users\\Sandeep" not in text
        assert "C:/Users/Sandeep" not in text
        assert "--squash --delete-branch" not in text


def test_rfc_0074_slice_five_bootstrap_automation_is_governed_and_safe() -> None:
    checklist = (ROOT / "rfcs" / "RFC-0074-implementation-checklist.md").read_text(encoding="utf-8")
    onboarding = (ROOT / "docs" / "onboarding" / "LOTUS-DEVELOPER-ONBOARDING.md").read_text(
        encoding="utf-8"
    )
    automation_readme = (ROOT / "automation" / "README.md").read_text(encoding="utf-8")
    directory_map = (ROOT / "automation" / "docs" / "Directory-Map.md").read_text(encoding="utf-8")
    validate_script = (ROOT / "automation" / "Validate-LotusDeveloperEnvironment.ps1").read_text(
        encoding="utf-8"
    )
    bootstrap_script = (ROOT / "automation" / "Bootstrap-LotusDeveloperEnvironment.ps1").read_text(
        encoding="utf-8"
    )

    assert "Implementation posture: `Complete`" in checklist
    assert "Slice 5 | Bootstrap and validation automation | Complete" in checklist

    assert "automation/Bootstrap-LotusDeveloperEnvironment.ps1" in checklist
    assert "automation/Validate-LotusDeveloperEnvironment.ps1" in checklist
    assert "output/developer-environment-readiness.json" in checklist
    assert ".md` reports" in checklist
    assert "Slice 6 is the next permitted implementation slice" in checklist

    assert "Validate-LotusDeveloperEnvironment.ps1 -Mode Inspect -Profile fast" in onboarding
    assert "Bootstrap-LotusDeveloperEnvironment.ps1 -Profile fast" in onboarding
    assert "unknown local Codex skills are preserved" in onboarding
    assert "skill synchronization automation is not implemented yet" not in onboarding

    assert "Validate-LotusDeveloperEnvironment.ps1 -Mode Inspect -Profile fast" in automation_readme
    assert "Bootstrap-LotusDeveloperEnvironment.ps1 -Profile fast" in automation_readme
    assert "Validate-LotusDeveloperEnvironment.ps1" in directory_map
    assert "Bootstrap-LotusDeveloperEnvironment.ps1" in directory_map

    for required in (
        '[ValidateSet("Inspect", "Sync", "Validate")]',
        '[ValidateSet("fast", "extended", "platform")]',
        "Test-GitHubAuth",
        "Test-DockerPosture",
        "Test-RepositoryPresence",
        "Test-ContextDocs",
        "Test-SkillSync",
        "Test-AgentsSync",
        "Test-IngressPosture",
        "Test-DsnPosture",
        "Redact-Value",
        "unknown local skills are preserved",
        "developer-environment-readiness.json",
        "developer-environment-readiness.md",
        "NoExitOnBlocked",
        "Refusing to synchronize skill outside the requested Codex skills target root.",
        "Refusing to synchronize a skill onto its governed source directory.",
        "exit 1",
    ):
        assert required in validate_script

    assert '"-Mode", "Sync"' in bootstrap_script
    assert "ValidateAfterSync" in bootstrap_script
    assert "Validate-LotusDeveloperEnvironment.ps1" in bootstrap_script


def test_rfc_0074_slice_six_validation_drift_controls_are_governed() -> None:
    checklist = (ROOT / "rfcs" / "RFC-0074-implementation-checklist.md").read_text(encoding="utf-8")
    validator = (ROOT / "automation" / "validate_engineering_context_system.py").read_text(encoding="utf-8")
    bootstrap_tests = (ROOT / "tests" / "unit" / "test_developer_environment_bootstrap.py").read_text(
        encoding="utf-8"
    )

    assert "Implementation posture: `Complete`" in checklist
    assert "Slice 6 | Validation coverage and drift control | Complete" in checklist
    assert "tests/unit/test_developer_environment_bootstrap.py" in checklist
    assert "Slice 7 is the next permitted implementation slice" in checklist

    for required in (
        "LOTUS-DEVELOPER-ONBOARDING.md: missing bootstrap guidance",
        "LOTUS-DEVELOPER-ONBOARDING.md: missing front-office runtime boundary guidance",
        "LOTUS-DEVELOPER-ONBOARDING.md: stale RFC-0074 boundary remains",
        "LOTUS-AGENT-RAMP-UP.md: missing context-budget guardrail",
        "LOTUS-AGENT-RAMP-UP.md: stale RFC-0074 boundary remains",
        "LOTUS-AGENT-RAMP-UP.md: missing front-office runtime routing",
        "missing required bootstrap behavior",
        "Validate-LotusDeveloperEnvironment.ps1",
        "Bootstrap-LotusDeveloperEnvironment.ps1",
    ):
        assert required in validator

    for required in (
        "test_developer_environment_inspect_report_is_redacted_and_structured",
        "test_developer_environment_bootstrap_sync_is_idempotent_and_scoped",
        "super-secret-password",
        "assert secret_dsn not in raw_report",
        "local-private-skill",
    ):
        assert required in bootstrap_tests


def test_rfc_0074_slice_seven_repository_context_links_are_governed() -> None:
    rfc = (ROOT / "rfcs" / "RFC-0074-repeatable-developer-and-agent-bootstrap-system.md").read_text(
        encoding="utf-8"
    )
    checklist = (ROOT / "rfcs" / "RFC-0074-implementation-checklist.md").read_text(encoding="utf-8")
    platform_repo_context = (ROOT / "REPOSITORY-ENGINEERING-CONTEXT.md").read_text(encoding="utf-8")

    assert "- Status: Implemented" in rfc
    assert "Implementation posture: `Complete`" in checklist
    assert "Slice 7 | Repository-local cross-link rollout | Complete" in checklist
    assert "RFC-0074 is implemented and governed" in checklist
    assert "[Lotus Developer Onboarding](./docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md)" in platform_repo_context
    assert "[Lotus Agent Ramp-Up](./docs/onboarding/LOTUS-AGENT-RAMP-UP.md)" in platform_repo_context
    assert "repo-native `lotus-idea` declarations" in platform_repo_context
    assert "Canonical front-office QA also includes `lotus-idea` by default" in platform_repo_context
    assert "catalog-visible future-wave `lotus-idea`" not in platform_repo_context


# --- The agent contract's path ownership rule --------------------------------


# --- The documentation link check --------------------------------------------
#
# This suite otherwise reads the validator as source text. These checks execute
# it, so the module is imported the way the registry renderer is.
#
# Every rejection below is paired with an acceptance. Four candidate rules were
# measured against the estate before one survived: a bare `<placeholder>` inside
# a shell fence occurs 127 times across 28 files and is a documented convention,
# a commented-out-command heuristic produced a single estate hit that was a
# descriptive sentence, and treating anchors and wiki page names as paths
# reported 225 broken links where the real count is zero. A checker whose false
# positives outnumber its findings gets switched off, so the acceptances are the
# point rather than padding.


def _contract_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_engineering_context_system",
        ROOT / "automation" / "validate_engineering_context_system.py",
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONTEXT_VALIDATOR = _contract_validator()


def _contract_path_errors(contract: str) -> list[str]:
    errors: list[str] = []
    CONTEXT_VALIDATOR._validate_agents_contract_paths(
        errors=errors, agents_contract=contract
    )
    return errors


def _documents(tmp_path: Path, body: str) -> dict[str, Path]:
    document = tmp_path / "doc.md"
    document.write_text(body, encoding="utf-8")
    return {"example document": document}


def _link_errors(tmp_path: Path, body: str, monkeypatch) -> list[str]:
    """Treat the fixture directory as the repository root for the escape rule."""
    monkeypatch.setattr(CONTEXT_VALIDATOR, "ROOT", tmp_path.resolve())
    errors: list[str] = []
    CONTEXT_VALIDATOR._validate_document_links(
        errors=errors, documents=_documents(tmp_path, body)
    )
    return errors


def test_a_bare_platform_document_is_rejected() -> None:
    """This file is deployed byte-identically, so a bare path reads as local.

    A blob-parity check cannot catch this. The contract is identical in all
    twelve repositories and still wrong in eleven, because correctness depends
    on where the file sits rather than on what it contains.
    """
    errors = _contract_path_errors("Read `LOTUS-ENGINEERING-CONTEXT.md` for architecture.")

    assert len(errors) == 1
    assert "LOTUS-ENGINEERING-CONTEXT.md" in errors[0]


def test_a_qualified_platform_document_is_accepted() -> None:
    contract = "Read `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md` for architecture."

    assert _contract_path_errors(contract) == []


def test_a_document_owned_by_each_repository_stays_bare() -> None:
    """`AGENTS.md` and the repository context are meant to resolve locally."""
    contract = "Read `AGENTS.md` and `REPOSITORY-ENGINEERING-CONTEXT.md` first."

    assert _contract_path_errors(contract) == []


def test_a_sibling_repository_document_is_accepted_when_qualified() -> None:
    """Ownership, not platform-ness, is the rule."""
    contract = "See `lotus-workbench/docs/operations/canonical-front-office-local-runtime.md`."

    assert _contract_path_errors(contract) == []


def test_a_generated_artifact_is_correctly_bare() -> None:
    """`output/background-runs.json` is produced wherever the automation runs.

    The contract calls it local automation evidence, and Git does not track it
    here, so qualifying it would assert the opposite of what it means. Tracking
    is what separates a document a reader must open from an artifact a run
    produces.
    """
    contract = "Treat `output/background-runs.json` as local automation evidence."

    assert _contract_path_errors(contract) == []


def test_a_platform_script_the_reader_must_run_is_not_exempt() -> None:
    """The rule covers anything the contract names, not only documents."""
    errors = _contract_path_errors("Use `automation/Sync-AgentOperatingContract.ps1`.")

    assert len(errors) == 1
    assert "Sync-AgentOperatingContract.ps1" in errors[0]


def test_a_platform_path_that_does_not_exist_is_rejected() -> None:
    """Qualifying a path is not the same as the path being real."""
    errors = _contract_path_errors("Read `lotus-platform/context/NOT-A-REAL-DOCUMENT.md`.")

    assert len(errors) == 1
    assert "does not track" in errors[0]


def test_a_path_with_arguments_after_it_is_still_a_path() -> None:
    """A backtick span is often a command, not a bare path.

    Requiring the closing backtick straight after the extension skipped
    `automation/Sync-AgentOperatingContract.ps1 -CheckOnly`, and the contract
    was shipping exactly that: an unqualified platform script this check could
    not see, in the pull request written to catch unqualified platform paths.
    """
    errors = _contract_path_errors(
        "Run `automation/Sync-AgentOperatingContract.ps1 -CheckOnly` to verify."
    )

    assert len(errors) == 1
    assert "Sync-AgentOperatingContract.ps1" in errors[0]


def test_a_qualified_command_span_is_accepted() -> None:
    contract = "Run `lotus-platform/automation/Sync-AgentOperatingContract.ps1 -CheckOnly`."

    assert _contract_path_errors(contract) == []


def test_an_unreadable_inventory_is_an_error_not_an_empty_one(monkeypatch) -> None:
    """An empty inventory makes every bare path look untracked, so nothing is examined."""
    import subprocess as _subprocess

    validator = _contract_validator()

    def _failing_run(*args, **kwargs):
        return _subprocess.CompletedProcess(
            args=[], returncode=128, stdout="", stderr=""
        )

    monkeypatch.setattr(validator.subprocess, "run", _failing_run)
    with pytest.raises(RuntimeError, match="unable to read the Git inventory"):
        validator._tracked_platform_paths()


def test_the_shipped_contract_qualifies_every_platform_document() -> None:
    """The rule runs against the contract that is actually deployed."""
    contract = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert _contract_path_errors(contract) == []


def test_a_concrete_skill_path_is_validated(tmp_path: Path) -> None:
    """Only the `<skill-name>` template is exempt, not every path ending in SKILL.md.

    Exempting the suffix meant a misspelled or invented skill read as correct,
    which is worse than leaving it bare: the qualification makes it look
    checked.
    """
    errors = _contract_path_errors(
        "See `lotus-platform/codex/skills/definitely-not-a-skill/SKILL.md`."
    )

    assert len(errors) == 1
    assert "definitely-not-a-skill" in errors[0]


def test_the_skill_name_template_stays_exempt() -> None:
    """The template names a shape rather than a document, and must not be resolved."""
    contract = "Skills live in `lotus-platform/codex/skills/<skill-name>/SKILL.md`."

    assert _contract_path_errors(contract) == []


def test_a_real_skill_path_is_accepted() -> None:
    contract = (
        "See `lotus-platform/codex/skills/lotus-skill-context-governance/SKILL.md`."
    )

    assert _contract_path_errors(contract) == []


def test_a_markdown_link_target_is_inspected() -> None:
    """A link destination is a path a reader follows as literally as a code span.

    Checking only inline-code spans left every link unexamined, so a
    platform-owned document reached through a link kept the defect the spans
    had been cleared of.
    """
    errors = _contract_path_errors(
        "Read [the layering standard](docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md)."
    )

    assert len(errors) == 1
    assert "LOTUS-DOCUMENTATION-LAYERING.md" in errors[0]


def test_a_qualified_markdown_link_is_accepted() -> None:
    contract = (
        "Read [the layering standard]"
        "(lotus-platform/docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md)."
    )

    assert _contract_path_errors(contract) == []


def test_an_external_link_is_not_read_as_a_path() -> None:
    contract = "Read it at [the repository](https://github.com/sgajbi/lotus-platform)."

    assert _contract_path_errors(contract) == []


def test_an_explicit_relative_prefix_does_not_bypass_ownership() -> None:
    """`./docs/...` names the same document as `docs/...`.

    Comparing the unnormalized string missed every explicit-relative form,
    which is the conventional spelling in Markdown â€” so the most likely way to
    write the link was the one way that escaped the check.
    """
    errors = _contract_path_errors(
        "See [the standard](./docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md)."
    )

    assert len(errors) == 1
    assert "LOTUS-DOCUMENTATION-LAYERING.md" in errors[0]


def test_a_parent_relative_prefix_does_not_bypass_ownership() -> None:
    errors = _contract_path_errors(
        "See [the context](../context/LOTUS-ENGINEERING-CONTEXT.md)."
    )

    assert len(errors) == 1


def test_a_relative_prefix_in_a_code_span_is_captured() -> None:
    """The token pattern must admit a leading `./`, the conventional spelling.

    Excluding a leading dot meant such spans produced no token at all, so the
    normalization was never reached â€” the earlier Markdown-link fix covered
    links and left inline code untouched.
    """
    errors = _contract_path_errors(
        "See `./docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md`."
    )

    assert len(errors) == 1
    assert "LOTUS-DOCUMENTATION-LAYERING.md" in errors[0]


def test_a_parent_relative_prefix_in_a_code_span_is_captured() -> None:
    errors = _contract_path_errors("See `../context/LOTUS-ENGINEERING-CONTEXT.md`.")

    assert len(errors) == 1


def test_the_contract_gives_a_runnable_sync_command() -> None:
    """A path identifying a script is not a command that runs it.

    The qualified `lotus-platform/...` form resolves from the workspace root, so
    an agent standing in an adopter repository cannot execute it as written.
    """
    contract = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "LOTUS_WORKSPACE_ROOT" in contract
    assert "-File automation/Sync-AgentOperatingContract.ps1" in contract, (
        "the runnable form must invoke the script from the lotus-platform checkout"
    )


def test_a_relative_prefix_on_a_qualified_path_is_still_accepted() -> None:
    """Normalizing must not turn a correctly qualified path into a finding."""
    contract = (
        "See [it](./lotus-platform/docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md)."
    )

    assert _contract_path_errors(contract) == []


def test_an_unknown_repository_prefix_is_rejected() -> None:
    """A misspelled repository is qualified-looking and resolves nowhere."""
    errors = _contract_path_errors("See `lotus-workbenchh/docs/operations/runtime.md`.")

    assert len(errors) == 1
    assert "the estate does not have" in errors[0]


def test_a_governed_repository_prefix_is_accepted() -> None:
    contract = "See `lotus-workbench/docs/operations/canonical-front-office-local-runtime.md`."

    assert _contract_path_errors(contract) == []


def test_an_empty_repository_registry_is_an_error(monkeypatch) -> None:
    """Accepting every prefix unexamined is the failure this check exists to stop."""
    validator = _contract_validator()
    monkeypatch.setattr(
        validator.Path, "read_text", lambda *args, **kwargs: '{"repos": []}'
    )
    with pytest.raises(RuntimeError, match="registry is empty"):
        validator._governed_repositories()


def _quickstart_task_routes() -> list[str]:
    """Return each numbered route in the quickstart's Reading Paths By Task section."""
    quickstart = (CONTEXT_DIR / "LOTUS-QUICKSTART-CONTEXT.md").read_text(encoding="utf-8")
    section = quickstart.split("## Reading Paths By Task", 1)[1].split("\n## ", 1)[0]
    routes: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if stripped[:2] in {"1.", "2.", "3.", "4."}:
            routes.append(stripped)
        elif routes and stripped:
            routes[-1] += " " + stripped
    return routes


# Naming the broad context, in any of the forms the estate writes it.
_BROAD_CONTEXT_MENTION = re.compile(
    r"\[[^\]]*lotus engineering context[^\]]*\]\([^)]*\)"
    r"|lotus-engineering-context\.md"
    r"|lotus engineering context"
    # The delivery skills call it "the central engineering context".
    r"|central engineering context"
)
# A mention is acceptable when the same sentence says when it applies, or states
# that this route is the case it exists for.
_BROAD_CONTEXT_CONDITIONS = (
    "only when",
    "only if",
    "when the change",
    "where the change",
    "the case the broad context exists for",
    "this playbook is the case for",
    "the case it exists for",
    # Naming the cross-repository case *is* the qualification: the integration
    # route is what the broad context exists for, and saying so inline is how
    # both the quickstart and the routing guide express it.
    "for cross-repository architecture",
    "cross-app integration",
)


def _unconditional_broad_context(text: str) -> list[str]:
    """Return every load clause that reaches the broad context without qualifying it.

    Checking that an approved conditional sentence is *present* accepts a
    document that also carries an unconditional one: the approved text survives
    the edit and simply stops describing what the document now says.

    Whitespace is normalized first. The estate wraps Markdown at 100 columns, so
    a condition and the mention it qualifies routinely sit on different physical
    lines. Matching raw text made the verdict depend on where a line happened to
    wrap and reported documents that were already correct.

    Sentences are then split into clauses on semicolons. A qualification carried
    by a comma or a colon belongs to the mention it introduces -- "this is the
    case the broad context exists for: read ..." -- and splitting there would
    separate a condition from what it qualifies. A semicolon joins an
    independent instruction, which must carry its own condition: without this
    split, appending "; nevertheless always load the central engineering
    context" to an approved sentence passed, because the approved condition was
    still somewhere in the same sentence.
    """
    offenders: list[str] = []
    for sentence in re.split(r"(?<=\.)\s+", " ".join(text.split())):
        for clause in sentence.split(";"):
            lowered = clause.lower()
            if not _BROAD_CONTEXT_MENTION.search(lowered):
                continue
            if any(condition in lowered for condition in _BROAD_CONTEXT_CONDITIONS):
                continue
            offenders.append(
                "unconditional broad-context instruction: " + clause.strip()[:120]
            )
    return offenders


def _broad_context_policy_errors(routes: list[str]) -> list[str]:
    if len(routes) != 4:
        return [f"expected four task routes, found {len(routes)}"]
    frontend, backend, integration, governance = routes
    broad_context = "[Lotus Engineering Context](./LOTUS-ENGINEERING-CONTEXT.md)"
    broad_context_lower = broad_context.lower()
    errors: list[str] = []

    for index, route in enumerate(routes, start=1):
        for complaint in _unconditional_broad_context(route):
            errors.append(f"route {index}: {complaint}")

    condition = "only if the change crosses a repository boundary"
    frontend_lower = frontend.lower()
    if condition not in frontend_lower or broad_context_lower not in frontend_lower:
        errors.append("frontend route must conditionally link broad context")
    elif frontend_lower.index(condition) > frontend_lower.index(broad_context_lower):
        errors.append("frontend route loads broad context before its condition")
    backend_condition = (
        "only when the change crosses a repository boundary or changes shared engineering policy"
    )
    backend_lower = backend.lower()
    if backend_condition not in backend_lower or broad_context_lower not in backend_lower:
        errors.append("backend route must conditionally link broad context")
    elif backend_lower.index(backend_condition) > backend_lower.index(broad_context_lower):
        errors.append("backend route loads broad context before its condition")

    reason = "This is the case the broad context exists for"
    if reason not in integration or broad_context not in integration:
        errors.append("integration route must explain and link broad context")
    elif integration.index(reason) > integration.index(broad_context):
        errors.append("integration route loads broad context before its reason")

    condition = "when the change sets policy across repositories"
    governance_lower = governance.lower()
    if condition not in governance_lower or broad_context_lower not in governance_lower:
        errors.append("governance route must conditionally link broad context")
    elif governance_lower.index(condition) > governance_lower.index(broad_context_lower):
        errors.append("governance route loads broad context before its condition")
    return errors


def _routing_guide_broad_context_policy_errors(guide: str) -> list[str]:
    def section(heading: str) -> str:
        return guide.split(f"## {heading}", 1)[1].split("\n## ", 1)[0]

    frontend = section("Frontend And Product-Surface Work")
    backend = section("Backend API And Domain-Service Work")
    integration = section("Cross-App Integration And Platform Validation Work")
    governance = section("Standards, RFC, And Governance Work")
    broad_context = "[Lotus Engineering Context](./LOTUS-ENGINEERING-CONTEXT.md)"
    broad_context_lower = broad_context.lower()
    frontend_condition = "only when the change crosses a repository boundary"
    backend_condition = "only when the change crosses a repository boundary or changes shared engineering policy"
    governance_condition = "when the change sets policy across repositories"
    frontend_flat = " ".join(frontend.split()).lower()
    backend_flat = " ".join(backend.split()).lower()
    governance_flat = " ".join(governance.split()).lower()
    errors: list[str] = []

    for sentence in _unconditional_broad_context(guide):
        errors.append(sentence)
    if frontend_condition not in frontend_flat or broad_context_lower not in frontend_flat:
        errors.append("frontend guide must conditionally link broad context")
    elif frontend_flat.index(frontend_condition) > frontend_flat.index(broad_context_lower):
        errors.append("frontend guide loads broad context before its condition")
    if backend_condition not in backend_flat or broad_context_lower not in backend_flat:
        errors.append("backend guide must conditionally link broad context")
    elif backend_flat.index(backend_condition) > backend_flat.index(broad_context_lower):
        errors.append("backend guide loads broad context before its condition")
    if "for cross-repository architecture" not in integration or broad_context not in integration:
        errors.append("integration guide must explain and link broad context")
    if governance_condition not in governance_flat or broad_context_lower not in governance_flat:
        errors.append("governance guide must conditionally link broad context")
    elif governance_flat.index(governance_condition) > governance_flat.index(broad_context_lower):
        errors.append("governance guide loads broad context before its condition")
    return errors


def _delivery_skill_context_policy_errors(skill: str, condition: str) -> list[str]:
    normalized = " ".join(skill.split()).lower()
    engineering_context = "`lotus-platform/context/lotus-engineering-context.md`"
    expected_reference = f"{engineering_context} only when {condition}"
    expected_action = f"load the central engineering context only when {condition}"
    errors: list[str] = []

    for sentence in _unconditional_broad_context(skill):
        errors.append(sentence)
    if "common startup set" not in normalized:
        errors.append("delivery skill must inherit the common startup set")
    if expected_reference not in normalized:
        errors.append("delivery skill reference must conditionally route broad context")
    if expected_action not in normalized:
        errors.append("delivery skill action must conditionally load broad context")
    return errors


def test_quickstart_task_routes_apply_the_broad_context_policy() -> None:
    """Local routes may reach broad context only through an explicit condition."""
    routes = _quickstart_task_routes()

    assert _broad_context_policy_errors(routes) == []

    regressed_routes = routes.copy()
    regressed_routes[1] = regressed_routes[1].replace(
        "Only when the change crosses a repository boundary or changes shared engineering policy,",
        "Always",
    )
    errors = _broad_context_policy_errors(regressed_routes)

    assert "backend route must conditionally link broad context" in errors
    # The counting guard catches it independently, which is the point of adding
    # it: the phrase check passes as soon as approved text is present anywhere,
    # so an edit that keeps the approved sentence and adds an unconditional one
    # would otherwise slip through. Both firing here is two guards agreeing,
    # not a duplicate.
    assert any("unconditional broad-context" in error for error in errors), errors


def test_task_routing_guide_and_manifest_extend_the_common_startup_set() -> None:
    """Human and machine routes must not restate an obsolete default order."""
    guide = (CONTEXT_DIR / "TASK-ROUTING-GUIDE.md").read_text(encoding="utf-8")
    manifest = json.loads((CONTEXT_DIR / "lotus-context-manifest.json").read_text(encoding="utf-8"))

    assert guide.count("common startup set") == 5
    assert "Read in this order:" not in guide
    assert manifest["task_routes_extend_reading_order"] is True
    assert manifest["task_routes"]["frontend"] == []
    assert manifest["task_routes"]["backend"] == [
        "context/CONTEXT-REFERENCE-MAP.md"
    ]
    assert manifest["conditional_task_routes"]["frontend"][0]["when"] == (
        "change_crosses_repository_boundary"
    )
    assert manifest["conditional_task_routes"]["frontend"][0]["add"] == [
        "context/LOTUS-ENGINEERING-CONTEXT.md",
        "context/CONTEXT-REFERENCE-MAP.md",
    ]
    for route in manifest["task_routes"].values():
        assert "REPOSITORY-ENGINEERING-CONTEXT.md" not in route
        assert "context/LOTUS-SKILL-ROUTING-MAP.md" not in route


def test_task_routing_guide_preserves_conditional_broad_context_policy() -> None:
    """The longer human guide must preserve the same task conditions as the quickstart."""
    guide = (CONTEXT_DIR / "TASK-ROUTING-GUIDE.md").read_text(encoding="utf-8")
    assert _routing_guide_broad_context_policy_errors(guide) == []

    regressed = re.sub(
        r"Only when the change\s+crosses a repository boundary or changes shared engineering policy",
        "for every backend task, before other context",
        guide,
        count=1,
    )
    errors = _routing_guide_broad_context_policy_errors(regressed)

    assert "backend guide must conditionally link broad context" in errors
    # The sentence guard catches it independently: the phrase check
    # passes as soon as approved text appears anywhere, so an edit that
    # keeps it and adds an unconditional instruction needs the second.
    assert any("unconditional broad-context" in error for error in errors), errors

    frontend_regression = re.sub(
        r"Only when the\s+change crosses a repository boundary",
        "for every frontend task before other context",
        guide,
        count=1,
    )
    errors = _routing_guide_broad_context_policy_errors(frontend_regression)

    assert "frontend guide must conditionally link broad context" in errors
    assert any("unconditional broad-context" in error for error in errors), errors

    governance_regression = guide.replace(
        "when the change sets policy across repositories",
        "for every standards task before other context",
        1,
    )
    errors = _routing_guide_broad_context_policy_errors(governance_regression)

    assert "governance guide must conditionally link broad context" in errors
    assert any("unconditional broad-context" in error for error in errors), errors


def test_reference_map_routes_without_restarting_context_discovery() -> None:
    """A task route may open the map without reopening the broad default context."""
    reference_map = (CONTEXT_DIR / "CONTEXT-REFERENCE-MAP.md").read_text(encoding="utf-8")
    introduction = reference_map.split("\n## ", 1)[0]

    assert "after the common startup set is complete" in introduction
    assert "do not restart discovery" in introduction
    assert "LOTUS-ENGINEERING-CONTEXT.md" not in introduction


def test_delivery_skills_preserve_conditional_broad_context_depth() -> None:
    """Selecting a delivery skill must not reopen broad context for a local task."""
    cases = {
        "lotus-frontend-delivery-governance": "the change crosses a repository boundary",
        "lotus-backend-delivery-governance": (
            "the change crosses a repository boundary or changes shared engineering policy"
        ),
        "lotus-readme-wiki-governance": (
            "documentation changes shared architecture or policy across repositories"
        ),
        "lotus-app-issue-discovery": (
            "the review crosses a repository boundary or evaluates shared engineering policy"
        ),
        "lotus-pr-premerge-gate": (
            "the change crosses a repository boundary or changes shared release policy"
        ),
    }
    for skill_name, condition in cases.items():
        skill = (ROOT / "codex" / "skills" / skill_name / "SKILL.md").read_text(encoding="utf-8")
        normalized_skill = " ".join(skill.split())
        assert _delivery_skill_context_policy_errors(normalized_skill, condition) == []

        unconditional_reference = normalized_skill.replace(
            f"only when {condition}",
            "for every task",
            1,
        )
        errors = _delivery_skill_context_policy_errors(unconditional_reference, condition)

        assert "delivery skill reference must conditionally route broad context" in errors
        # The sentence guard catches it independently: the phrase check
        # passes as soon as approved text appears anywhere, so an edit that
        # keeps it and adds an unconditional instruction needs the second.
        assert any("unconditional broad-context" in error for error in errors), errors

        unconditional_action = normalized_skill.replace(
            f"load the central engineering context only when {condition}",
            "load the central engineering context for every task",
            1,
        )
        errors = _delivery_skill_context_policy_errors(unconditional_action, condition)

        assert "delivery skill action must conditionally load broad context" in errors
        assert any("unconditional broad-context" in error for error in errors), errors


def test_quickstart_states_the_startup_set_once() -> None:
    """One section defines it; the others reference it, so they cannot disagree."""
    quickstart = (CONTEXT_DIR / "LOTUS-QUICKSTART-CONTEXT.md").read_text(encoding="utf-8")

    assert quickstart.count("default startup set") == 1, (
        "the startup set must be defined in exactly one place; a second "
        "statement is what drifted out of agreement with AGENTS.md"
    )


def test_quickstart_routes_the_broad_context_by_task_not_by_default() -> None:
    """The broad context stays reachable, but only where a task needs it."""
    quickstart = (CONTEXT_DIR / "LOTUS-QUICKSTART-CONTEXT.md").read_text(encoding="utf-8")
    raw = quickstart.split("## Reading Paths By Task", 1)[1].split("\n## ", 1)[0]
    # Markdown wraps prose across lines, so a sentence is matched with its
    # whitespace collapsed rather than as the bytes that happen to be on disk.
    section = " ".join(raw.split()).lower()

    assert "./lotus-engineering-context.md" in section, (
        "removing the route to the broad context would trade one defect for another"
    )
    for qualifier in ("only if the change crosses a repository boundary",
                      "the case the broad context exists for"):
        assert qualifier in section, f"missing the reason a route loads it: {qualifier}"

_ADDITIVE_ROUTED_DOCUMENTS = (
    "codex/skills/lotus-qa-platform-validator/SKILL.md",
    "codex/skills/lotus-validation-resolution-lifecycle/SKILL.md",
    "codex/skills/lotus-skill-context-governance/SKILL.md",
    "context/playbooks/ENTERPRISE-BACKEND-REFACTORING-INSTRUCTIONS.md",
    "context/playbooks/CHANGE-PLAYBOOKS.md",
)


def test_routed_documents_extend_the_startup_set_rather_than_reopening_it() -> None:
    """A route that reloads the broad context defeats the condition that selected it.

    The skill-routing map and the manifest send ordinary single-repository work
    into these documents. Conditioning only the quickstart routes left the
    documents those routes lead to still requiring the broad context
    unconditionally, so a consumer that followed the complete route bypassed the
    condition entirely and read exactly what the policy exists to avoid.
    """
    for relative in _ADDITIVE_ROUTED_DOCUMENTS:
        document = (ROOT / relative).read_text(encoding="utf-8")
        assert _unconditional_broad_context(document) == [], relative
        assert "already loaded" in document, (
            f"{relative} must state that the startup set is already loaded, or a "
            "consumer rereads what it is holding"
        )


def test_the_additive_guard_rejects_a_reinstated_unconditional_load() -> None:
    """The guard must fail on the text it exists to reject, not merely pass today."""
    reinstated = """
The common startup set is already loaded. Before substantial work, add:

1. `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`
2. `lotus-platform/context/PROCEDURAL-MEMORY-INDEX.md`
"""
    assert _unconditional_broad_context(reinstated), (
        "restoring the unconditional bullet must be reported"
    )


def test_an_added_clause_cannot_hide_behind_an_approved_condition() -> None:
    """A semicolon joins an independent instruction, which needs its own condition.

    Accepting a whole sentence as soon as any approved condition appeared let an
    additive unconditional directive ride along inside qualified text: the
    phrase checks stayed satisfied because the approved wording was still there.
    """
    approved = (
        "Read `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md` only when the "
        "change crosses a repository boundary."
    )
    assert _unconditional_broad_context(approved) == []

    contradicted = (
        approved[:-1] + "; nevertheless always load the central engineering context."
    )
    offenders = _unconditional_broad_context(contradicted)
    assert offenders, (
        "an appended unconditional clause must not inherit the approved condition"
    )
    assert "nevertheless" in offenders[0]


def test_a_condition_that_wraps_still_qualifies_its_mention() -> None:
    """The estate wraps Markdown at 100 columns; a verdict must not depend on where.

    Matching raw text made a correctly written playbook fail purely because its
    condition continued on the next physical line.
    """
    wrapped = """
1. read [Lotus Engineering Context](../LOTUS-ENGINEERING-CONTEXT.md), which this
   playbook is the case for
"""
    assert _unconditional_broad_context(wrapped) == []


def test_link_check_rejects_a_route_that_does_not_resolve(tmp_path: Path, monkeypatch) -> None:
    errors = _link_errors(tmp_path, monkeypatch=monkeypatch, body="See [the pack](./docs/absent.md).\n")

    assert len(errors) == 1
    assert "./docs/absent.md" in errors[0]


def test_link_check_rejects_a_link_that_needs_a_sibling_checkout(
    tmp_path: Path, monkeypatch
) -> None:
    """It resolves on a developer machine and 404s everywhere else."""
    sibling = tmp_path / "lotus-workbench" / "docs"
    sibling.mkdir(parents=True)
    (sibling / "runtime.md").write_text("x", encoding="utf-8")
    repo = tmp_path / "lotus-platform"
    repo.mkdir()
    monkeypatch.setattr(CONTEXT_VALIDATOR, "ROOT", repo)

    document = repo / "doc.md"
    document.write_text(
        "See [the runtime](../lotus-workbench/docs/runtime.md).\n", encoding="utf-8"
    )
    errors: list[str] = []
    CONTEXT_VALIDATOR._validate_document_links(
        errors=errors, documents={"example document": document}
    )

    assert len(errors) == 1, "the target exists locally, which is exactly the trap"
    assert "sibling checkout" in errors[0]


def test_link_check_accepts_a_percent_encoded_path(tmp_path: Path, monkeypatch) -> None:
    """Governed standards have spaces in their filenames; %20 is not a defect."""
    standards = tmp_path / "docs" / "standards"
    standards.mkdir(parents=True)
    (standards / "Lotus Data Mesh Standard.md").write_text("x", encoding="utf-8")

    assert (
        _link_errors(
            tmp_path,
            monkeypatch=monkeypatch,
            body="See [it](./docs/standards/Lotus%20Data%20Mesh%20Standard.md).\n",
        )
        == []
    )


def test_link_check_accepts_an_anchor_and_an_external_url(tmp_path: Path, monkeypatch) -> None:
    """Neither is a repository path; reading them as paths produced 225 false failures."""
    body = (
        "See [the section](#status-model) and "
        "[the repo](https://github.com/sgajbi/lotus-platform).\n"
    )

    assert _link_errors(tmp_path, monkeypatch=monkeypatch, body=body) == []


def test_link_check_keeps_a_fragment_out_of_the_path(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "other.md").write_text("x", encoding="utf-8")

    assert _link_errors(tmp_path, monkeypatch=monkeypatch, body="See [it](./other.md#a-heading).\n") == []


def test_link_check_rejects_a_broken_titled_link(tmp_path: Path, monkeypatch) -> None:
    """`[g](missing.md "details")` is valid Markdown the old pattern did not match.

    A destination capture that forbade whitespace skipped titled links
    entirely, so a broken route passed the guard silently — worse than being
    reported wrongly, because nothing said so.
    """
    errors = _link_errors(
        tmp_path, monkeypatch=monkeypatch, body='See [g](missing.md "details").\n'
    )

    assert len(errors) == 1
    assert "missing.md" in errors[0]


def test_link_check_accepts_a_titled_link_to_a_real_file(
    tmp_path: Path, monkeypatch
) -> None:
    (tmp_path / "guide.md").write_text("x", encoding="utf-8")

    assert (
        _link_errors(
            tmp_path, monkeypatch=monkeypatch, body='See [g](guide.md "details").\n'
        )
        == []
    )


def test_link_check_accepts_a_query_bearing_link(tmp_path: Path, monkeypatch) -> None:
    """`guide.md?plain=1` names `guide.md`; a query is not part of the filename."""
    (tmp_path / "guide.md").write_text("x", encoding="utf-8")

    assert (
        _link_errors(tmp_path, monkeypatch=monkeypatch, body="See [v](guide.md?plain=1).\n")
        == []
    )
    assert (
        _link_errors(
            tmp_path, monkeypatch=monkeypatch, body="See [v](guide.md?plain=1#top).\n"
        )
        == []
    )


def test_the_skill_routing_map_is_link_checked() -> None:
    """It is a mandatory starting document, and `required_files` does not list it.

    A broken route in the document an agent is told to read fourth is exactly
    what this check exists to catch, so the governed set is extended rather than
    left to whatever happened to be in the existence map.
    """
    routing_map = CONTEXT_DIR / "LOTUS-SKILL-ROUTING-MAP.md"
    original = routing_map.read_text(encoding="utf-8")
    try:
        routing_map.write_text(
            original + "\n[broken](definitely-missing-route.md)\n", encoding="utf-8"
        )
        errors = [
            error
            for error in CONTEXT_VALIDATOR.validate_engineering_context_system()
            if "definitely-missing-route.md" in error
        ]
    finally:
        routing_map.write_text(original, encoding="utf-8")

    assert len(errors) == 1, "a broken route in the routing map went unreported"


def test_the_governed_documents_have_no_unresolvable_route() -> None:
    """The rule runs against the real estate, not only against fixtures."""
    errors = [
        error
        for error in CONTEXT_VALIDATOR.validate_engineering_context_system()
        if "links to a path that does not exist" in error
        or "links outside the repository" in error
    ]

    assert errors == [], errors


def test_link_check_rejects_a_broken_reference_definition(
    tmp_path: Path, monkeypatch
) -> None:
    """A reference-style route carries its destination on a separate line.

    `[guide][target]` names no path at all; the path lives on the `[target]:`
    definition, which the inline pattern never sees. A document could route
    through a file that does not exist and pass a blocking gate.
    """
    errors = _link_errors(
        tmp_path,
        monkeypatch=monkeypatch,
        body="See [the guide][target]." + chr(10) * 2 + "[target]: ./absent.md" + chr(10),
    )

    assert len(errors) == 1, errors
    assert "./absent.md" in errors[0]


def test_link_check_accepts_a_reference_definition_that_resolves(
    tmp_path: Path, monkeypatch
) -> None:
    """The paired acceptance: a definition pointing at a real file is a route."""
    (tmp_path / "present.md").write_text("# present" + chr(10), encoding="utf-8")

    errors = _link_errors(
        tmp_path,
        monkeypatch=monkeypatch,
        body="See [the guide][target]." + chr(10) * 2 + "[target]: ./present.md" + chr(10),
    )

    assert errors == [], errors


def test_link_check_ignores_a_link_inside_a_fenced_example(
    tmp_path: Path, monkeypatch
) -> None:
    """A fenced example demonstrates syntax; it is displayed, not followed.

    Treating it as a live link makes the guard fail on correct documentation
    unless the illustrative filename happens to exist, which is how a useful
    check gets switched off.
    """
    fence = chr(96) * 3
    body = (
        "Write a link like this:"
        + chr(10) * 2
        + fence
        + "markdown"
        + chr(10)
        + "[example](not-a-real-file.md)"
        + chr(10)
        + fence
        + chr(10)
    )

    assert _link_errors(tmp_path, monkeypatch=monkeypatch, body=body) == []


def test_link_check_still_reads_links_after_a_fence_closes(
    tmp_path: Path, monkeypatch
) -> None:
    """The paired acceptance: skipping a fence must not skip the rest of the file."""
    fence = chr(96) * 3
    body = (
        fence
        + chr(10)
        + "[example](not-a-real-file.md)"
        + chr(10)
        + fence
        + chr(10) * 2
        + "And a real route: [pack](./also-absent.md)."
        + chr(10)
    )

    errors = _link_errors(tmp_path, monkeypatch=monkeypatch, body=body)

    assert len(errors) == 1, errors
    assert "./also-absent.md" in errors[0]
    assert "not-a-real-file.md" not in errors[0]


def test_link_check_ignores_a_link_inside_a_code_span(
    tmp_path: Path, monkeypatch
) -> None:
    """An inline code span is the same case as a fence, in one line."""
    body = (
        "The form is "
        + chr(96)
        + "[example](not-a-real-file.md)"
        + chr(96)
        + "."
        + chr(10)
    )

    assert _link_errors(tmp_path, monkeypatch=monkeypatch, body=body) == []


def test_link_check_rejects_an_absolute_filesystem_destination(
    tmp_path: Path, monkeypatch
) -> None:
    """An absolute path is machine-specific even when it exists right now.

    Joining discards the left operand, so an absolute destination that happens
    to sit under this checkout passed both containment and existence. It is a
    404 on every other machine, which is precisely what this check exists to
    catch.
    """
    real_file = tmp_path / "README.md"
    real_file.write_text("# readme" + chr(10), encoding="utf-8")

    errors = _link_errors(
        tmp_path,
        monkeypatch=monkeypatch,
        body="See [the readme](" + real_file.resolve().as_posix() + ")." + chr(10),
    )

    assert len(errors) == 1, errors
    assert "absolute filesystem path" in errors[0], errors


def test_link_check_accepts_the_relative_form_of_the_same_file(
    tmp_path: Path, monkeypatch
) -> None:
    """The paired acceptance: the same target, written portably, is a route."""
    (tmp_path / "README.md").write_text("# readme" + chr(10), encoding="utf-8")

    errors = _link_errors(
        tmp_path, monkeypatch=monkeypatch, body="See [the readme](./README.md)." + chr(10)
    )

    assert errors == [], errors


def test_the_checked_document_set_comes_from_the_manifest() -> None:
    """A hand-maintained map drifts from the routes it is supposed to cover.

    Both documents below are routed into by the manifest's business-app RFC
    route and were absent from the explicit map, so a broken link in either one
    passed a blocking gate.
    """
    routes = CONTEXT_VALIDATOR._governed_markdown_documents()
    routed_paths = {path.resolve() for path in routes.values()}

    for relative in (
        "platform-standards/LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md",
        "context/playbooks/ENTERPRISE-BACKEND-REFACTORING-INSTRUCTIONS.md",
        "context/LOTUS-SKILL-ROUTING-MAP.md",
    ):
        assert (ROOT / relative).resolve() in routed_paths, relative


def test_an_empty_manifest_cannot_pass_the_link_check_by_inspecting_nothing(
    tmp_path: Path, monkeypatch
) -> None:
    """Zero routes and zero broken routes must not be the same green."""
    empty_context = tmp_path / "context"
    empty_context.mkdir()
    (empty_context / "lotus-context-manifest.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(CONTEXT_VALIDATOR, "CONTEXT_DIR", empty_context)

    with pytest.raises(ValueError, match="no Markdown routes"):
        CONTEXT_VALIDATOR._governed_markdown_documents()


def test_link_check_reports_a_route_to_a_document_that_is_not_there(
    tmp_path: Path, monkeypatch
) -> None:
    """A manifest route to a missing document is the finding, not a skip.

    Skipping a non-existent document was a silent pass: the manifest could send
    an agent to a file that does not exist and the gate whose whole purpose is
    proving routes resolve would say nothing.
    """
    errors: list[str] = []
    monkeypatch.setattr(CONTEXT_VALIDATOR, "ROOT", tmp_path.resolve())
    CONTEXT_VALIDATOR._validate_document_links(
        errors=errors,
        documents={"routed document": tmp_path / "never-written.md"},
    )

    assert len(errors) == 1, errors
    assert "does not exist" in errors[0]


def test_link_check_accepts_a_route_to_a_document_that_is_there(
    tmp_path: Path, monkeypatch
) -> None:
    """The paired acceptance, so the rejection is about absence and nothing else."""
    present = tmp_path / "present.md"
    present.write_text("# present" + chr(10), encoding="utf-8")

    errors: list[str] = []
    monkeypatch.setattr(CONTEXT_VALIDATOR, "ROOT", tmp_path.resolve())
    CONTEXT_VALIDATOR._validate_document_links(
        errors=errors, documents={"routed document": present}
    )

    assert errors == [], errors


def test_link_check_accepts_an_external_url_in_any_case(
    tmp_path: Path, monkeypatch
) -> None:
    """URI schemes are case-insensitive; a matched lowercase prefix is not a rule.

    `HTTPS://example.com/guide` was resolved as a repository-relative path and
    reported as a missing file, so a valid external reference failed a blocking
    gate.
    """
    body = (
        "See [the guide](HTTPS://example.com/guide) and "
        "[the other](MailTo:someone@example.com)." + chr(10)
    )

    assert _link_errors(tmp_path, monkeypatch=monkeypatch, body=body) == []


def test_link_check_still_reads_a_relative_route_beside_an_external_one(
    tmp_path: Path, monkeypatch
) -> None:
    """The paired acceptance: skipping schemes must not skip relative paths."""
    body = (
        "See [external](HTTPS://example.com) and [local](./absent.md)." + chr(10)
    )

    errors = _link_errors(tmp_path, monkeypatch=monkeypatch, body=body)

    assert len(errors) == 1, errors
    assert "./absent.md" in errors[0]


def test_link_check_keeps_the_whole_fence_delimiter(
    tmp_path: Path, monkeypatch
) -> None:
    """Documentation that demonstrates a fence opens with a longer one.

    Truncating every opener to three characters let the inner triple-backtick
    line close the outer block, so everything after it was read as live routes.
    """
    outer = chr(96) * 4
    inner = chr(96) * 3
    body = (
        "How to write a fenced example:"
        + chr(10) * 2
        + outer
        + chr(10)
        + inner
        + "markdown"
        + chr(10)
        + "[example](not-a-real-file.md)"
        + chr(10)
        + inner
        + chr(10)
        + "[another](also-not-real.md)"
        + chr(10)
        + outer
        + chr(10)
    )

    assert _link_errors(tmp_path, monkeypatch=monkeypatch, body=body) == []


def test_link_check_resumes_after_the_longer_fence_actually_closes(
    tmp_path: Path, monkeypatch
) -> None:
    """The paired acceptance: the outer fence must still end where it ends."""
    outer = chr(96) * 4
    inner = chr(96) * 3
    body = (
        outer
        + chr(10)
        + inner
        + chr(10)
        + "[example](not-a-real-file.md)"
        + chr(10)
        + inner
        + chr(10)
        + outer
        + chr(10) * 2
        + "A real route: [pack](./absent-route.md)."
        + chr(10)
    )

    errors = _link_errors(tmp_path, monkeypatch=monkeypatch, body=body)

    assert len(errors) == 1, errors
    assert "./absent-route.md" in errors[0]

