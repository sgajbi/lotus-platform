from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_front_office_qa_wrapper_is_wired_into_platform_profile_and_docs() -> None:
    wrapper = (ROOT / "automation" / "Invoke-Canonical-FrontOffice-QA.ps1").read_text(encoding="utf-8")
    profiles_doc = json.loads((ROOT / "automation" / "task-profiles.json").read_text(encoding="utf-8"))
    automation_readme = (ROOT / "automation" / "README.md").read_text(encoding="utf-8")
    automation_guide = (ROOT / "automation" / "docs" / "Automation-Guide.md").read_text(encoding="utf-8")
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
    assert "[switch]$BuildImages" in wrapper
    assert "[switch]$RemoveImages" in wrapper
    assert "[switch]$SkipDpmCommandCenterSeed" in wrapper
    assert "Get-LotusDockerArtifacts" in wrapper
    assert "Remove-LotusDockerArtifacts" in wrapper
    assert "Assert-NoLotusDockerArtifacts" in wrapper
    assert "docker_before" in wrapper
    assert "docker_after_clean" in wrapper
    assert "Docker Evidence" in wrapper
    assert "dpm_command_center_seed_summary" in wrapper
    assert "DPM command-center seed status" in wrapper
    assert "Screenshot directory" in wrapper
    assert "Runtime transcript" in wrapper
    assert "Canonical contract:" in wrapper
    assert "Governed by:" in wrapper
    assert '$summary.steps -contains "bring-up" -or $summary.steps -contains "validate"' in wrapper
    assert "validation did not produce a live summary" in wrapper
    assert "validation summary is stale" in wrapper

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
    assert "Assert-CampaignDefinitionMatchesSeed" in dpm_seed
    assert "DpmPortfolioUniverseCandidate:v1" in dpm_seed
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
    assert "source-backed DPM campaign definition" in automation_readme
    assert "DpmPortfolioUniverseCandidate:v1" in automation_readme
    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -Clean -BringUp -BuildImages" in automation_readme
    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -Clean -RemoveImages" in automation_readme
    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp" in automation_guide
    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -ScreenshotDirectory <path>" in automation_guide
    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -Clean -BringUp -BuildImages" in automation_guide
    assert "Docker cleanup scope" in automation_guide
    assert "runtime transcript" in automation_guide
    assert "DPM command-center seed" in automation_guide
    assert "DpmPortfolioUniverseCandidate:v1" in automation_guide
    assert "Invoke-Canonical-FrontOffice-QA.ps1" in directory_map
    assert "Invoke-DpmCommandCenterSeed.ps1" in directory_map
    assert "`qa-platform-readiness`" in profile_reference
    assert "`qa-platform-readiness-clean-core`" in profile_reference
    assert "`qa-platform-readiness-clean-core-build`" in profile_reference
    assert "Governed front-office runtime bring-up and populated UI proof" in profile_reference


def test_front_office_docs_distinguish_governed_ui_qa_from_backend_runtime_qa() -> None:
    automation_readme = (ROOT / "automation" / "README.md").read_text(encoding="utf-8")
    automation_guide = (ROOT / "automation" / "docs" / "Automation-Guide.md").read_text(encoding="utf-8")

    for content in (automation_readme, automation_guide):
        assert "governed `lotus-workbench` runtime" in content
        assert "backend/runtime QA readiness automation" in content or "Backend/runtime QA readiness validation" in content
        assert "Invoke-Platform-QA.ps1 -BringUp" in content
        assert "Invoke-Canonical-FrontOffice-QA.ps1 -BringUp" in content
