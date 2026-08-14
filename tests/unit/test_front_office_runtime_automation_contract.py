from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_platform_qa_core_gate_uses_canonical_front_office_verifier() -> None:
    qa_matrix = json.loads((ROOT / "automation" / "qa-matrix.json").read_text(encoding="utf-8"))
    core_entry = next(item for item in qa_matrix["repositories"] if item["repo"] == "lotus-core")
    custom_checks = core_entry["checks"]["custom_checks"]
    canonical_check = next(
        item for item in custom_checks if item["id"] == "canonical-front-office-analytics-maturity"
    )

    command = canonical_check["command"]
    assert "front_office_portfolio_seed.py" in command
    assert "--verify-only" in command
    assert "PB_SG_GLOBAL_BAL_001" in command
    assert "BMK_PB_GLOBAL_BALANCED_60_40" not in command
    assert "core_seeded_analytics_maturity_validation.py" not in command


def test_front_office_qa_wrapper_is_wired_into_platform_profile_and_docs() -> None:
    wrapper = (ROOT / "automation" / "Invoke-Canonical-FrontOffice-QA.ps1").read_text(encoding="utf-8")
    profiles_doc = json.loads((ROOT / "automation" / "task-profiles.json").read_text(encoding="utf-8"))
    automation_readme = (ROOT / "automation" / "README.md").read_text(encoding="utf-8")
    automation_guide = (ROOT / "automation" / "docs" / "Automation-Guide.md").read_text(encoding="utf-8")
    local_dev_runbook = (ROOT / "docs" / "operations" / "Local Development Runbook.md").read_text(
        encoding="utf-8"
    )
    engineering_context = (ROOT / "context" / "LOTUS-ENGINEERING-CONTEXT.md").read_text(
        encoding="utf-8"
    )
    skill_routing_map = (ROOT / "context" / "LOTUS-SKILL-ROUTING-MAP.md").read_text(
        encoding="utf-8"
    )
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs_readme = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    wiki_home = (ROOT / "wiki" / "Home.md").read_text(encoding="utf-8")
    wiki_overview = (ROOT / "wiki" / "Overview.md").read_text(encoding="utf-8")
    wiki_platform_surfaces = (ROOT / "wiki" / "Platform-Surfaces.md").read_text(encoding="utf-8")
    wiki_sidebar = (ROOT / "wiki" / "_Sidebar.md").read_text(encoding="utf-8")
    hosts_helper = (ROOT / "automation" / "Apply-DevIngressHosts-Elevated.ps1").read_text(
        encoding="utf-8"
    )
    directory_map = (ROOT / "automation" / "docs" / "Directory-Map.md").read_text(encoding="utf-8")
    profile_reference = (ROOT / "automation" / "docs" / "Profile-Reference.md").read_text(encoding="utf-8")

    assert "Start-LotusFrontOfficeCanonical.ps1" in wrapper
    assert "Validate-LotusFrontOfficeCanonical.ps1" in wrapper
    assert "Stop-LotusFrontOfficeCanonical.ps1" in wrapper
    assert "Invoke-DpmCommandCenterSeed.ps1" in wrapper
    assert "PB_SG_GLOBAL_BAL_001" in wrapper
    assert "output/front-office-qa" in wrapper
    assert "[string]$ScreenshotDirectory" in wrapper
    assert "screenshot_directory" in wrapper
    assert "runtime_transcript" in wrapper
    assert "canonical-front-office-qa-$timestamp.log" in wrapper
    assert "latest.log" in wrapper
    assert "Start-Transcript" in wrapper
    assert "Stop-Transcript" in wrapper
    assert "output\\playwright\\live-canonical" in wrapper
    assert "live-validation-summary.json" in wrapper
    assert "canonical_contract" in wrapper
    assert "canonicalContract" in wrapper
    assert "[switch]$Clean" in wrapper
    assert "[switch]$CleanPlanOnly" in wrapper
    assert "[switch]$BuildImages" in wrapper
    assert "[switch]$RequireMainlineSources" in wrapper
    assert "RequireMainlineSources requires -BringUp" in wrapper
    assert 'if ($RequireMainlineSources -and -not $BuildImages)' in wrapper
    assert "$BuildImages = $true" in wrapper
    assert "require_mainline_sources = [bool]$RequireMainlineSources" in wrapper
    assert "mainline_source_preflight = $null" in wrapper
    assert "$summary.mainline_source_preflight = [ordered]@{" in wrapper
    assert "Invoke-MainlineSourceProvenancePreflight" in wrapper
    assert "mainline-source-provenance.mjs" in wrapper
    assert "failed before cleanup, Docker build, seed, or validation was started" in wrapper
    assert "mainline-source-provenance-preflight-latest.json" in wrapper
    assert '$summary.steps += "mainline-source-preflight"' in wrapper
    assert "$bringUpArguments.RequireMainlineSources = $true" in wrapper
    assert "-not $RequireMainlineSources -or $certifiedSourcePreflightPassed" in wrapper
    assert "Require mainline sources:" in wrapper
    assert "Mainline source preflight:" in wrapper
    assert "[switch]$RemoveImages" in wrapper
    assert "[switch]$IncludeLotusIdea" not in wrapper
    assert "[switch]$SkipDpmCommandCenterSeed" in wrapper
    assert "canonical_docker_ownership.py" in wrapper
    assert "Get-CanonicalDockerCleanupPlan" in wrapper
    assert "Assert-NoOwnedDockerArtifacts" in wrapper
    assert "docker_ownership_policy" in wrapper
    assert "docker_cleanup_plan_path" in wrapper
    assert "ownership_provenance" in wrapper
    assert "ownership_conflicts" in wrapper
    assert "Canonical clean blocked by Compose ownership conflicts" in wrapper
    assert "Get-LotusDockerArtifacts" not in wrapper
    assert "Remove-LotusDockerArtifacts" not in wrapper
    assert '$_ -match "^(lotus|pbwm|performance)"' not in wrapper
    assert "docker rm -f" not in wrapper
    assert "docker volume rm" not in wrapper
    assert "docker image rm -f" not in wrapper
    assert "Invoke-LotusIdeaDockerBringUp" not in wrapper
    assert "Invoke-LotusIdeaValidation" in wrapper
    assert "Assert-NoUnownedHostPortListener" not in wrapper
    assert "docker compose up -d --build" not in wrapper
    assert '$composeArguments = @("compose", "up", "-d")' not in wrapper
    assert '$composeArguments += "--build"' not in wrapper
    assert "preserving governed runtime started and seeded by canonical Workbench startup" in wrapper
    assert "Stop-Process" not in wrapper
    assert '$summary.status = "failed"' in wrapper
    assert "http://127.0.0.1:8330/health/ready" in wrapper
    assert "http://idea.dev.lotus/health/ready" in wrapper
    assert "lotus_idea" in wrapper
    assert "docker_before" in wrapper
    assert "docker_after_clean" in wrapper
    assert "Docker Evidence" in wrapper
    assert "include_lotus_idea = $true" in wrapper
    assert "canonical_core_demo_pack_enabled = $false" in wrapper
    assert "Canonical core demo pack enabled" in wrapper
    assert "dpm_command_center_seed_summary" in wrapper
    assert "DPM command-center seed status" in wrapper
    assert "Screenshot directory" in wrapper
    assert "Runtime transcript" in wrapper
    assert "Canonical contract:" in wrapper
    assert "Governed by:" in wrapper
    assert '$summary.steps -contains "bring-up" -or $summary.steps -contains "validate"' in wrapper
    assert "validation did not produce a live summary" in wrapper
    assert "validation summary is stale" in wrapper
    assert "Apply-DevIngressHosts-Elevated.ps1" in automation_readme
    assert "Apply-DevIngressHosts-Elevated.ps1" in automation_guide
    assert "Sync-Dev-Ingress-Hosts.ps1" in hosts_helper
    assert "-Apply" in hosts_helper
    assert "ipconfig /flushdns" in hosts_helper
    assert "Start-Process" in hosts_helper
    assert "-Verb RunAs" in hosts_helper

    dpm_seed = (ROOT / "automation" / "Invoke-DpmCommandCenterSeed.ps1").read_text(
        encoding="utf-8"
    )
    assert "canonical-front-office-demo-data-contract.json" in dpm_seed
    assert "dpm_command_center" in dpm_seed
    assert "MANDATE_PB_SG_GLOBAL_BAL_001" not in dpm_seed
    assert "refresh-from-core" in dpm_seed
    assert "/api/v1/dpm/monitoring/run-once" in dpm_seed
    assert "manage-monitoring-run-once" in dpm_seed
    assert "manage-campaign-definition-upsert" in dpm_seed
    assert "function Upsert-CampaignDefinition" in dpm_seed
    assert "Existing Manage campaign definition" in dpm_seed
    assert "Refreshing the seed-owned definition" in dpm_seed
    assert "Assert-CampaignDefinitionMatchesSeed" in dpm_seed
    assert "DpmPortfolioUniverseCandidate:v1" in dpm_seed
    assert "campaignCandidateSelectionBasis" in dpm_seed
    assert "selection_basis" in dpm_seed
    assert "source-owned selection_basis evidence" in dpm_seed
    assert "campaign_candidate_selection_basis" in dpm_seed
    assert "Supersede-LegacyCampaignDefinitions" in dpm_seed
    assert "manage-campaign-definition-supersede-legacy" in dpm_seed
    assert "source-owned candidate selection-basis evidence" in dpm_seed
    assert "/api/v1/mandates/by-portfolio/$resolvedPortfolioId" in dpm_seed
    assert "/api/v1/dpm/command-center/mandates/by-portfolio/$resolvedPortfolioId" in dpm_seed
    assert "/api/v1/dpm/command-center/waves/campaign-definitions" in dpm_seed
    assert "/api/v1/dpm/command-center/waves/campaign-discovery" in dpm_seed
    assert "dpm-command-center-seed-latest.json" in dpm_seed
    assert "posture_checks" in dpm_seed
    assert "ready-populated-command-center" in dpm_seed
    assert "gateway-command-center-partial-posture" in dpm_seed
    assert "gateway-command-center-empty-posture" in dpm_seed
    assert "DPM command-center posture validation failed" in dpm_seed
    assert "New-CanonicalOutcomeReviewGatewayBody" in dpm_seed
    assert "gateway-outcome-review-create" in dpm_seed
    assert "gateway-outcome-review-list" in dpm_seed
    assert "canonical-dpm-outcome-review:${resolvedPortfolioId}:${resolvedAsOfDate}" in dpm_seed
    assert "/api/v1/dpm/command-center/outcome-reviews" in dpm_seed
    assert (
        '-CorrelationId "corr-canonical-dpm-outcome-review-$resolvedPortfolioId-'
        in dpm_seed
    )
    assert '-ExtraHeaders @{' in dpm_seed
    assert '"Idempotency-Key" = $outcomeReviewIdempotencyKey' in dpm_seed
    assert "limit=50" in dpm_seed
    assert "$outcomeReviewRebalanceRunId" in dpm_seed
    assert "$outcomeReviewWaveId" in dpm_seed
    assert "gateway_outcome_review_verified_item" in dpm_seed
    assert "observedRunId -eq $outcomeReviewRebalanceRunId" in dpm_seed
    assert "observedWaveId -eq $outcomeReviewWaveId" in dpm_seed
    assert "Assert-OutcomeReviewPageContainsSeed" in dpm_seed
    assert "CanonicalDpmOutcomeExpectedEvidence" in dpm_seed
    assert "DpmRealizedOutcomeSnapshot:v1" in dpm_seed
    assert "[switch]$PreflightOnly" in dpm_seed
    assert "Invoke-ManageWriteAuthorizationPreflight" in dpm_seed
    assert "manage-refresh-authorization-preflight" in dpm_seed
    assert "action_register_workflow_response" in dpm_seed
    assert "manage-action-register-workflow-posture" in dpm_seed
    assert "$workflowRequiresReview" in dpm_seed
    assert "manage-action-register-workflow-not-required" in dpm_seed
    assert "DPM_WORKFLOW_NOT_REQUIRED_FOR_RUN_STATUS" in dpm_seed
    assert "does not fabricate an approval decision" in dpm_seed
    assert "authorized_validation_rejected_side_effect_free_probe" in dpm_seed
    assert "authorized_unexpected_success" not in dpm_seed
    assert "observed unexpected 2xx success" in dpm_seed
    assert "may have reached the write operation" in dpm_seed
    assert "$ErrorRecord.ErrorDetails" in dpm_seed
    assert "$errorDetails.Message" in dpm_seed
    assert "ReadAsStringAsync().GetAwaiter().GetResult()" in dpm_seed
    assert "New-ManageRequestHeaders" in dpm_seed
    assert '"X-Role" = $manageSeedRole' in dpm_seed
    assert '"X-Service-Identity" = $manageSeedServiceIdentity' in dpm_seed
    assert '"X-Capabilities" = $manageSeedCapability' in dpm_seed
    assert '$manageSeedCapability = "manage.write"' in dpm_seed
    assert 'service_identity = $manageSeedServiceIdentity' in dpm_seed
    assert 'capabilities = @($manageSeedCapability)' in dpm_seed
    assert 'preflight_only = [bool]$PreflightOnly' in dpm_seed
    assert '-Headers (New-ManageRequestHeaders -CorrelationId "corr-canonical-dpm-refresh-' in dpm_seed
    assert '-Headers (New-ManageRequestHeaders -CorrelationId "corr-canonical-dpm-monitoring-' in dpm_seed
    assert '-Headers (New-ManageRequestHeaders -CorrelationId "corr-canonical-dpm-health-recalculate-' in dpm_seed
    assert '-Headers (New-ManageRequestHeaders `' in dpm_seed
    assert '-Headers (New-ManageRequestHeaders -CorrelationId "corr-canonical-dpm-action-register-review-' in dpm_seed
    assert '-Headers (New-ManageRequestHeaders -CorrelationId "corr-canonical-dpm-campaign-upsert-' in dpm_seed
    assert '-Headers (New-ManageRequestHeaders -CorrelationId "corr-canonical-dpm-campaign-supersede-' in dpm_seed

    profiles = {profile["name"]: profile for profile in profiles_doc["profiles"]}
    qa_profile_commands = {task["command"] for task in profiles["qa-platform-readiness"]["tasks"]}
    assert (
        "powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp"
        in qa_profile_commands
    )
    clean_core_profile_commands = {
        task["command"] for task in profiles["qa-platform-readiness-clean-core"]["tasks"]
    }
    assert (
        "powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 "
        "-BringUp -CleanCoreState -LotusAiEnvFile .env.example -SeedWaitSeconds 1200"
        in clean_core_profile_commands
    )
    clean_core_build_profile_commands = {
        task["command"] for task in profiles["qa-platform-readiness-clean-core-build"]["tasks"]
    }
    assert (
        "powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 "
        "-BringUp -CleanCoreState -BuildImages -LotusAiEnvFile .env.example -SeedWaitSeconds 1200"
        in clean_core_build_profile_commands
    )

    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp" in automation_readme
    assert "`qa-platform-readiness-clean-core`" in automation_readme
    assert "`qa-platform-readiness-clean-core-build`" in automation_readme
    assert "-LotusAiEnvFile .env.example" in automation_readme
    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 `" in automation_readme
    assert "-ScreenshotDirectory C:\\Users\\Sandeep\\AppData\\Local\\Temp\\lotus-risk-module-shots" in automation_readme
    assert "canonical contract identity and version" in automation_readme
    assert "calculationChecks" in automation_readme
    assert "panelClassifications" in automation_readme
    assert "runtime transcript" in automation_readme
    assert "DPM command-center seed" in automation_readme
    assert "-IncludeLotusIdea" not in automation_readme
    assert "source-backed DPM campaign definition" in automation_readme
    assert "source-owned selection-basis evidence" in automation_readme
    assert "DpmPortfolioUniverseCandidate:v1" in automation_readme
    assert "DPM_CORE_CONTEXT_INCOMPLETE" in automation_readme
    assert "sgajbi/lotus-core#840" in automation_readme
    assert "response-body diagnostics" in automation_guide
    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -Clean -BringUp -BuildImages" in automation_readme
    assert (
        "automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp -RequireMainlineSources"
        in automation_readme
    )
    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -Clean -RemoveImages" in automation_readme
    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -CleanPlanOnly" in automation_readme
    assert "cleanup-plan-latest.json" in automation_readme
    assert "name is never sufficient" in automation_readme
    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp" in automation_guide
    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -ScreenshotDirectory <path>" in automation_guide
    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -Clean -BringUp -BuildImages" in automation_guide
    assert (
        "automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp -RequireMainlineSources"
        in automation_guide
    )
    assert "-BringUp -RequireMainlineSources" in engineering_context
    assert "require_mainline_sources" in engineering_context
    assert "mainline_source_preflight" in engineering_context
    assert "forces image builds" in engineering_context
    assert "-BringUp -RequireMainlineSources" in skill_routing_map
    assert "mainline-certified front-office proof" in skill_routing_map
    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp -RequireMainlineSources" in local_dev_runbook
    assert "require_mainline_sources" in local_dev_runbook
    assert "mainline_source_preflight" in local_dev_runbook
    assert "already-running canonical stack" in local_dev_runbook
    assert "forces image builds" in automation_guide
    assert "mainline_source_preflight" in automation_guide
    assert "must not tear down an existing canonical stack" in (
        ROOT / "codex" / "skills" / "platform-automation-ops" / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -CleanPlanOnly" in automation_guide
    assert "Broad daemon-wide" in automation_guide
    assert "repository-scoped Workbench Compose teardown" in automation_guide
    assert "-IncludeLotusIdea" not in automation_guide
    assert "lotus-idea" in automation_guide
    assert "DEMO_DATA_PACK_ENABLED=false" in automation_guide
    assert "Docker cleanup scope" in automation_guide
    assert "runtime transcript" in automation_guide
    assert "DPM command-center seed" in automation_guide
    assert "source-owned selection-basis evidence" in automation_guide
    assert "DpmPortfolioUniverseCandidate:v1" in automation_guide
    assert "Invoke-Canonical-FrontOffice-QA.ps1" in directory_map
    assert "Invoke-DpmCommandCenterSeed.ps1" in directory_map
    assert "`qa-platform-readiness`" in profile_reference
    assert "`qa-platform-readiness-clean-core`" in profile_reference
    assert "`qa-platform-readiness-clean-core-build`" in profile_reference
    assert "Governed front-office runtime bring-up and populated UI proof" in profile_reference
    assert "Reader Paths" in root_readme
    assert "Human approval reviews are optional" in root_readme
    assert "canonical private-banking seed data excludes the demo pack by default" in root_readme
    assert "`lotus-idea` is included by default in canonical platform QA" in root_readme
    assert "Canonical front-office proof and demo boundaries" in docs_readme
    assert "Documentation in this directory must stay implementation-backed" in docs_readme
    assert "Reader Paths" in wiki_home
    assert "`lotus-idea` runtime" in wiki_home
    assert "the demo pack is not part of canonical PB seed by default" in wiki_home
    assert "Included by default in canonical platform QA" in wiki_overview
    assert "Canonical front-office QA includes `lotus-idea` by default" in wiki_platform_surfaces
    assert "## Product And Demo" in wiki_sidebar
    assert "## Operations" in wiki_sidebar
    assert "## Governance" in wiki_sidebar


def test_front_office_docs_distinguish_governed_ui_qa_from_backend_runtime_qa() -> None:
    automation_readme = (ROOT / "automation" / "README.md").read_text(encoding="utf-8")
    automation_guide = (ROOT / "automation" / "docs" / "Automation-Guide.md").read_text(encoding="utf-8")

    for content in (automation_readme, automation_guide):
        assert "governed `lotus-workbench` runtime" in content
        assert "backend/runtime QA readiness automation" in content or "Backend/runtime QA readiness validation" in content
        assert "Invoke-Platform-QA.ps1 -BringUp" in content
        assert "Invoke-Canonical-FrontOffice-QA.ps1 -BringUp" in content
