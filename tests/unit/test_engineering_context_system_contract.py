from __future__ import annotations

import importlib.util
import json
import re
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
    assert manifest["reading_order"] == [
        "AGENTS.md",
        "context/LOTUS-QUICKSTART-CONTEXT.md",
        "REPOSITORY-ENGINEERING-CONTEXT.md",
        "context/LOTUS-SKILL-ROUTING-MAP.md",
    ]
    assert manifest["task_routes_extend_reading_order"] is True
    assert manifest["conditional_task_routes_extend_task_routes"] is True

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

    assert manifest["task_routes"]["frontend"] == []
    assert manifest["task_routes"]["backend"] == [
        "context/CONTEXT-REFERENCE-MAP.md"
    ]
    assert manifest["task_routes"]["standards_and_rfc"] == [
        "context/CONTEXT-REFERENCE-MAP.md",
        "context/platform-engineering-ledger.md",
        "context/recent-architectural-decisions-digest.md",
    ]
    assert manifest["conditional_task_routes"]["frontend"] == [
        {
            "when": "change_crosses_repository_boundary",
            "add": [
                "context/LOTUS-ENGINEERING-CONTEXT.md",
                "context/CONTEXT-REFERENCE-MAP.md",
            ],
        }
    ]
    assert manifest["conditional_task_routes"]["backend"] == [
        {
            "when": "change_crosses_repository_boundary_or_changes_shared_engineering_policy",
            "add": ["context/LOTUS-ENGINEERING-CONTEXT.md"],
        }
    ]
    assert manifest["conditional_task_routes"]["standards_and_rfc"] == [
        {
            "when": "change_sets_policy_across_repositories",
            "add": ["context/LOTUS-ENGINEERING-CONTEXT.md"],
        }
    ]
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
        "default deployed target",
    ):
        assert required_item in sync_script

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
        "../../../lotus-workbench/docs/operations/canonical-front-office-local-runtime.md",
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


def _broad_context_policy_errors(routes: list[str]) -> list[str]:
    if len(routes) != 4:
        return [f"expected four task routes, found {len(routes)}"]
    frontend, backend, integration, governance = routes
    broad_context = "[Lotus Engineering Context](./LOTUS-ENGINEERING-CONTEXT.md)"
    broad_context_lower = broad_context.lower()
    errors: list[str] = []

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


def test_quickstart_task_routes_apply_the_broad_context_policy() -> None:
    """Local routes may reach broad context only through an explicit condition."""
    routes = _quickstart_task_routes()

    assert _broad_context_policy_errors(routes) == []

    regressed_routes = routes.copy()
    regressed_routes[1] = regressed_routes[1].replace(
        "Only when the change crosses a repository boundary or changes shared engineering policy,",
        "Always",
    )
    assert _broad_context_policy_errors(regressed_routes) == [
        "backend route must conditionally link broad context"
    ]


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
    assert _routing_guide_broad_context_policy_errors(regressed) == [
        "backend guide must conditionally link broad context"
    ]

    frontend_regression = re.sub(
        r"Only when the\s+change crosses a repository boundary",
        "for every frontend task before other context",
        guide,
        count=1,
    )
    assert _routing_guide_broad_context_policy_errors(frontend_regression) == [
        "frontend guide must conditionally link broad context"
    ]

    governance_regression = guide.replace(
        "when the change sets policy across repositories",
        "for every standards task before other context",
        1,
    )
    assert _routing_guide_broad_context_policy_errors(governance_regression) == [
        "governance guide must conditionally link broad context"
    ]


def test_reference_map_routes_without_restarting_context_discovery() -> None:
    """A task route may open the map without reopening the broad default context."""
    reference_map = (CONTEXT_DIR / "CONTEXT-REFERENCE-MAP.md").read_text(encoding="utf-8")
    introduction = reference_map.split("\n## ", 1)[0]

    assert "after the common startup set is complete" in introduction
    assert "do not restart discovery" in introduction
    assert "LOTUS-ENGINEERING-CONTEXT.md" not in introduction


def _delivery_skill_context_policy_errors(skill: str, condition: str) -> list[str]:
    normalized = " ".join(skill.split()).lower()
    engineering_context = "`lotus-platform/context/lotus-engineering-context.md`"
    expected_reference = f"{engineering_context} only when {condition}"
    expected_action = f"load the central engineering context only when {condition}"
    errors: list[str] = []
    if "common startup set" not in normalized:
        errors.append("delivery skill must inherit the common startup set")
    if expected_reference not in normalized:
        errors.append("delivery skill reference must conditionally route broad context")
    if expected_action not in normalized:
        errors.append("delivery skill action must conditionally load broad context")
    return errors


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
        assert _delivery_skill_context_policy_errors(unconditional_reference, condition) == [
            "delivery skill reference must conditionally route broad context"
        ]

        unconditional_action = normalized_skill.replace(
            f"load the central engineering context only when {condition}",
            "load the central engineering context for every task",
            1,
        )
        assert _delivery_skill_context_policy_errors(unconditional_action, condition) == [
            "delivery skill action must conditionally load broad context"
        ]


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
