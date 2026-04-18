from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _powershell_executable() -> str:
    executable = shutil.which("pwsh") or shutil.which("powershell")
    assert executable is not None, "pwsh or powershell is required for AGENTS sync tests"
    return executable


def _run_sync(*args: str) -> subprocess.CompletedProcess[str]:
    command = [_powershell_executable(), "-NoProfile"]
    if shutil.which("powershell") and "powershell" in _powershell_executable().lower():
        command.extend(["-ExecutionPolicy", "Bypass"])
    command.extend(
        [
            "-File",
            str(ROOT / "automation" / "Sync-AgentOperatingContract.ps1"),
            *args,
        ]
    )
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )


def test_sync_agent_operating_contract_can_sync_explicit_and_repo_root_targets(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    repo_root = workspace_root / "lotus-ai"
    repo_root.mkdir(parents=True)
    explicit_target = tmp_path / "custom" / "AGENTS.md"

    _run_sync(
        "-WorkspaceRoot",
        str(workspace_root),
        "-Repository",
        "lotus-ai",
        "-TargetPath",
        str(explicit_target),
    )

    governed_source = (ROOT / "context" / "AGENTS-OPERATING-CONTRACT.md").read_text(encoding="utf-8")
    repo_agents = (repo_root / "AGENTS.md").read_text(encoding="utf-8")
    explicit_agents = explicit_target.read_text(encoding="utf-8")

    assert repo_agents == governed_source
    assert explicit_agents == governed_source


def test_sync_agent_operating_contract_check_only_detects_repo_root_drift(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    repo_root = workspace_root / "lotus-ai"
    repo_root.mkdir(parents=True)

    _run_sync(
        "-WorkspaceRoot",
        str(workspace_root),
        "-Repository",
        "lotus-ai",
    )

    target_path = repo_root / "AGENTS.md"
    target_path.write_text("# drifted\n", encoding="utf-8")

    result = subprocess.run(
        [
            _powershell_executable(),
            "-NoProfile",
            *(
                ["-ExecutionPolicy", "Bypass"]
                if shutil.which("powershell") and "powershell" in _powershell_executable().lower()
                else []
            ),
            "-File",
            str(ROOT / "automation" / "Sync-AgentOperatingContract.ps1"),
            "-WorkspaceRoot",
            str(workspace_root),
            "-Repository",
            "lotus-ai",
            "-CheckOnly",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "Target AGENTS file is not synchronized with the governed source" in result.stderr + result.stdout
