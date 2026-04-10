from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"


def _powershell_shell() -> str:
    shell = shutil.which("pwsh") or shutil.which("powershell")
    if shell is None:
        raise RuntimeError("PowerShell is required for the platform validation lane contract test")
    return shell


def test_platform_validation_lane_workflow_is_explicit() -> None:
    workflow = (WORKFLOWS / "platform-end-to-end-validation.yml").read_text(encoding="utf-8")

    assert "name: Platform End-to-End Validation" in workflow
    assert "workflow_dispatch:" in workflow
    assert "schedule:" in workflow
    assert "Invoke-PlatformValidationLane.ps1" in workflow
    assert not (WORKFLOWS / "core-performance-cross-app-validation.yml").exists()
    assert not (WORKFLOWS / "core-performance-green-lanes.yml").exists()


def test_platform_validation_lane_dry_run_profiles_are_stable() -> None:
    shell = _powershell_shell()
    script = ROOT / "automation" / "Invoke-PlatformValidationLane.ps1"

    baseline = subprocess.run(
        [
            shell,
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
            "-ValidationProfile",
            "core-performance-baseline",
            "-DryRun",
        ],
        check=True,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    green_lanes = subprocess.run(
        [
            shell,
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
            "-ValidationProfile",
            "core-performance-green-lanes",
            "-DryRun",
        ],
        check=True,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )

    assert "baseline" in baseline.stdout
    assert "twr_benchmark" in green_lanes.stdout
    assert "returns_series" in green_lanes.stdout
    assert "contribution" in green_lanes.stdout
    assert "mwr" in green_lanes.stdout
