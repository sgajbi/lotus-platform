from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_platform_automation_python_runtime_is_locked_and_reused() -> None:
    requirements_lock = (ROOT / "automation" / "requirements.platform-automation.lock.txt").read_text(
        encoding="utf-8"
    )
    resolver = (ROOT / "automation" / "Resolve-PlatformAutomationPython.ps1").read_text(encoding="utf-8")
    repo_checks = (ROOT / "automation" / "Invoke-PlatformRepoChecks.ps1").read_text(encoding="utf-8")
    validation_lane = (ROOT / "automation" / "Invoke-PlatformValidationLane.ps1").read_text(
        encoding="utf-8"
    )
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

    assert "pytest==" in requirements_lock
    assert "requests==" in requirements_lock
    assert "PyYAML==" in requirements_lock

    assert ".venv-platform-automation" in resolver
    assert "requirements.platform-automation.lock.txt" in resolver

    assert "Resolve-PlatformAutomationPython.ps1" in repo_checks
    assert "Resolve-PlatformAutomationPython.ps1" in validation_lane
    assert "Sync-RepoWikis.ps1" in repo_checks
    assert "python -m pip install pytest requests PyYAML" not in repo_checks
    assert "python -m pip install requests" not in validation_lane

    assert ".venv-platform-automation/" in gitignore
