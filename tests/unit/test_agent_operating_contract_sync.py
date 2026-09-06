from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LOTUS_REPOSITORIES = [
    "lotus-workbench",
    "lotus-gateway",
    "lotus-core",
    "lotus-performance",
    "lotus-risk",
    "lotus-advise",
    "lotus-manage",
    "lotus-report",
    "lotus-ai",
    "lotus-render",
    "lotus-archive",
    "lotus-idea",
]


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


def _run_sync_result(*args: str) -> subprocess.CompletedProcess[str]:
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
    )


def _run_git(repo_root: Path, *args: str) -> None:
    git = shutil.which("git")
    assert git is not None, "git is required for stale checkout hint tests"
    subprocess.run([git, "-C", str(repo_root), *args], check=True, text=True, capture_output=True)


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


def test_sync_agent_operating_contract_check_only_reports_all_repo_root_drift(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    for repository in LOTUS_REPOSITORIES:
        (workspace_root / repository).mkdir(parents=True)

    ai_repo_root = workspace_root / "lotus-ai"
    risk_repo_root = workspace_root / "lotus-risk"

    _run_sync(
        "-WorkspaceRoot",
        str(workspace_root),
        "-AllRepoRoots",
    )

    ai_target_path = ai_repo_root / "AGENTS.md"
    risk_target_path = risk_repo_root / "AGENTS.md"
    ai_target_path.write_text("# drifted ai\n", encoding="utf-8")
    risk_target_path.write_text("# drifted risk\n", encoding="utf-8")

    result = _run_sync_result(
        "-WorkspaceRoot",
        str(workspace_root),
        "-AllRepoRoots",
        "-CheckOnly",
    )

    assert result.returncode != 0
    output = result.stderr + result.stdout
    assert "Agent operating contract check failed for 2 target(s)" in output
    assert str(ai_target_path) in output
    assert str(risk_target_path) in output


def test_sync_agent_operating_contract_check_only_reports_stale_repo_root_hint(tmp_path: Path) -> None:
    git = shutil.which("git")
    assert git is not None, "git is required for stale checkout hint tests"

    workspace_root = tmp_path / "workspace"
    repo_root = workspace_root / "lotus-ai"
    origin = tmp_path / "origin.git"
    updater = tmp_path / "updater"
    repo_root.mkdir(parents=True)

    subprocess.run([git, "init", "--bare", str(origin)], check=True, text=True, capture_output=True)
    subprocess.run([git, "init", str(repo_root)], check=True, text=True, capture_output=True)
    _run_git(repo_root, "checkout", "-b", "main")
    _run_git(repo_root, "config", "user.email", "test@example.com")
    _run_git(repo_root, "config", "user.name", "Test User")
    _run_git(repo_root, "remote", "add", "origin", str(origin))

    target_path = repo_root / "AGENTS.md"
    target_path.write_text("# stale contract\n", encoding="utf-8")
    _run_git(repo_root, "add", "AGENTS.md")
    _run_git(repo_root, "commit", "-m", "seed stale contract")
    _run_git(repo_root, "push", "-u", "origin", "main")

    subprocess.run([git, "clone", str(origin), str(updater)], check=True, text=True, capture_output=True)
    _run_git(updater, "checkout", "main")
    _run_git(updater, "config", "user.email", "test@example.com")
    _run_git(updater, "config", "user.name", "Test User")
    governed_source = (ROOT / "context" / "AGENTS-OPERATING-CONTRACT.md").read_text(encoding="utf-8")
    (updater / "AGENTS.md").write_text(governed_source, encoding="utf-8")
    _run_git(updater, "add", "AGENTS.md")
    _run_git(updater, "commit", "-m", "sync contract")
    _run_git(updater, "push", "origin", "main")
    _run_git(repo_root, "fetch", "origin", "main")

    result = _run_sync_result(
        "-WorkspaceRoot",
        str(workspace_root),
        "-Repository",
        "lotus-ai",
        "-CheckOnly",
    )

    assert result.returncode != 0
    output = result.stderr + result.stdout
    assert str(target_path) in output
    assert "checkout hint: main is behind origin/main by 1 commit(s)" in output


def test_sync_refuses_branch_only_contract_for_a_sibling_worktree(tmp_path: Path) -> None:
    git = shutil.which("git")
    assert git is not None

    source_origin = tmp_path / "source-origin.git"
    source_repo = tmp_path / "source"
    source_contract = source_repo / "context" / "AGENTS-OPERATING-CONTRACT.md"
    workspace_root = tmp_path / "workspace"
    target_repo = workspace_root / "lotus-ai"

    subprocess.run([git, "init", "--bare", str(source_origin)], check=True, capture_output=True)
    source_contract.parent.mkdir(parents=True)
    subprocess.run([git, "init", str(source_repo)], check=True, capture_output=True)
    _run_git(source_repo, "checkout", "-b", "main")
    _run_git(source_repo, "config", "user.email", "test@example.com")
    _run_git(source_repo, "config", "user.name", "Test User")
    _run_git(source_repo, "remote", "add", "origin", str(source_origin))
    source_contract.write_text("# main contract\n", encoding="utf-8")
    _run_git(source_repo, "add", ".")
    _run_git(source_repo, "commit", "-m", "main contract")
    _run_git(source_repo, "push", "-u", "origin", "main")
    _run_git(source_repo, "checkout", "-b", "topic")
    source_contract.write_text("# branch-only contract\n", encoding="utf-8")
    _run_git(source_repo, "add", ".")
    _run_git(source_repo, "commit", "-m", "branch contract")

    target_repo.mkdir(parents=True)
    subprocess.run([git, "init", str(target_repo)], check=True, capture_output=True)
    _run_git(target_repo, "config", "user.email", "test@example.com")
    _run_git(target_repo, "config", "user.name", "Test User")
    target_agents = target_repo / "AGENTS.md"
    target_agents.write_text("# target contract\n", encoding="utf-8")
    _run_git(target_repo, "add", ".")
    _run_git(target_repo, "commit", "-m", "target contract")

    result = _run_sync_result(
        "-SourcePath",
        str(source_contract),
        "-WorkspaceRoot",
        str(workspace_root),
        "-Repository",
        "lotus-ai",
    )

    assert result.returncode == 0
    assert target_agents.read_text(encoding="utf-8") == "# target contract\n"
    assert "differs from or cannot be verified against origin/main" in (result.stdout + result.stderr)


def test_check_only_does_not_leak_failed_git_probe_status(tmp_path: Path) -> None:
    source = tmp_path / "source" / "AGENTS.md"
    target = tmp_path / "target" / "AGENTS.md"
    source.parent.mkdir(parents=True)
    target.parent.mkdir(parents=True)
    source.write_text("# portable contract\n", encoding="utf-8")
    target.write_text("# portable contract\n", encoding="utf-8")

    result = _run_sync_result(
        "-SourcePath",
        str(source),
        "-TargetPath",
        str(target),
        "-CheckOnly",
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "Agent operating contract is synchronized for 1 target(s)." in result.stdout


def test_sync_script_runs_on_every_installed_powershell_interpreter() -> None:
    """The script must work under the interpreter that actually invokes it.

    The helpers above prefer `pwsh`, so the suite exercised PowerShell 7 while
    operators and automation invoke `powershell.exe`, which is Windows
    PowerShell 5.1. An API present only in 7 therefore passed every test and
    failed in use: [System.IO.Path]::GetRelativePath threw MethodNotFound, the
    relative path was never assigned, and the origin/main comparison ran with an
    empty pathspec -- diffing the whole tree instead of the contract file, so any
    unrelated local edit made the guard refuse to sync.

    Interpreter-specific failures are silent in output that otherwise looks
    successful, so this asserts on the diagnostics rather than the exit code.
    """
    interpreters = [path for path in (shutil.which("pwsh"), shutil.which("powershell")) if path]
    assert interpreters, "no PowerShell interpreter available to test"

    script = ROOT / "automation" / "Sync-AgentOperatingContract.ps1"
    forbidden = ("MethodNotFound", "VariableIsUndefined", "CommandNotFoundException")

    for interpreter in interpreters:
        command = [interpreter, "-NoProfile"]
        if "powershell" in Path(interpreter).stem.lower():
            command += ["-ExecutionPolicy", "Bypass"]
        result = subprocess.run(
            command + ["-File", str(script), "-CheckOnly"],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        combined = f"{result.stdout}\n{result.stderr}"
        for token in forbidden:
            assert token not in combined, f"{Path(interpreter).name} reported {token}:\n{combined}"
