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
    assert "PB_SG_GLOBAL_BAL_001" in wrapper
    assert "output/front-office-qa" in wrapper
    assert "output\\playwright\\live-canonical\\live-validation-summary.json" in wrapper
    assert "[switch]$Clean" in wrapper
    assert "[switch]$BuildImages" in wrapper
    assert "[switch]$RemoveImages" in wrapper
    assert "Get-LotusDockerArtifacts" in wrapper
    assert "Remove-LotusDockerArtifacts" in wrapper
    assert "Assert-NoLotusDockerArtifacts" in wrapper
    assert "docker_before" in wrapper
    assert "docker_after_clean" in wrapper
    assert "Docker Evidence" in wrapper
    assert '$summary.steps -contains "bring-up" -or $summary.steps -contains "validate"' in wrapper

    profiles = {profile["name"]: profile for profile in profiles_doc["profiles"]}
    qa_profile_commands = {task["command"] for task in profiles["qa-platform-readiness"]["tasks"]}
    assert (
        "powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp"
        in qa_profile_commands
    )

    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp" in automation_readme
    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -Clean -BringUp -BuildImages" in automation_readme
    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -Clean -RemoveImages" in automation_readme
    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp" in automation_guide
    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -Clean -BringUp -BuildImages" in automation_guide
    assert "Docker cleanup scope" in automation_guide
    assert "Invoke-Canonical-FrontOffice-QA.ps1" in directory_map
    assert "`qa-platform-readiness`" in profile_reference
    assert "Governed front-office runtime bring-up and populated UI proof" in profile_reference


def test_front_office_docs_distinguish_governed_ui_qa_from_backend_runtime_qa() -> None:
    automation_readme = (ROOT / "automation" / "README.md").read_text(encoding="utf-8")
    automation_guide = (ROOT / "automation" / "docs" / "Automation-Guide.md").read_text(encoding="utf-8")

    for content in (automation_readme, automation_guide):
        assert "governed `lotus-workbench` runtime" in content
        assert "backend/runtime QA readiness automation" in content or "Backend/runtime QA readiness validation" in content
        assert "Invoke-Platform-QA.ps1 -BringUp" in content
        assert "Invoke-Canonical-FrontOffice-QA.ps1 -BringUp" in content
