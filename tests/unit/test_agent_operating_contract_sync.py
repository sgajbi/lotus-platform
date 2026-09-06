from __future__ import annotations

import os
import re
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


def _console_text(result: subprocess.CompletedProcess[str]) -> str:
    """Return a script's combined output with its terminal decoration removed.

    PowerShell renders an exception with ANSI colour sequences and wraps it to
    the console width, and both differ between a Windows developer machine and
    an Ubuntu runner. Asserting on the raw bytes passed locally and failed in
    CI on a message that was actually present, so the decoration is stripped
    and whitespace collapsed before any comparison.
    """
    combined = (result.stdout or "") + (result.stderr or "")
    stripped = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", combined)
    # PowerShell 7 renders an exception in ConciseView: it wraps to the console
    # width and draws a gutter, so line breaks and `|` characters land inside
    # the message itself. Stripping colour and collapsing whitespace still
    # failed in CI on a phrase that was present. Comparing only letters and
    # digits discards every layout decision the terminal made and leaves what
    # the script actually said.
    return re.sub(r"[^0-9a-z]+", "", stripped.lower())


def _says(result: subprocess.CompletedProcess[str], phrase: str) -> bool:
    """True when the output contains this phrase, however the terminal drew it."""
    return re.sub(r"[^0-9a-z]+", "", phrase.lower()) in _console_text(result)


def _readable(result: subprocess.CompletedProcess[str]) -> str:
    """The output with colour removed and whitespace collapsed, for a human.

    `_console_text` strips punctuation so a comparison survives PowerShell's
    line wrapping, which makes it unreadable in a failure message. Comparisons
    use that; anything a person has to read uses this.
    """
    combined = (result.stdout or "") + (result.stderr or "")
    return " ".join(re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", combined).split())


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

    assert result.returncode != 0, _readable(result)
    # Compared through the decoration stripper: PowerShell wraps its exception
    # to the console width and draws a gutter, so where the break lands depends
    # on the message length and the host, not on what the script decided.
    assert _says(result, "Agent operating contract check failed for 2 target(s)")
    assert _says(result, str(ai_target_path))
    assert _says(result, str(risk_target_path))


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

    assert result.returncode != 0, (
        "the caller asked for this target to be written and it was not, so the "
        "run must not report success"
    )
    assert target_agents.read_text(encoding="utf-8") == "# target contract\n"
    assert "differs from or cannot be verified against origin/main" in (
        result.stdout + result.stderr
    )


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


def test_unrelated_source_edit_does_not_change_contract_provenance_by_interpreter(
    tmp_path: Path,
) -> None:
    interpreters = list(
        dict.fromkeys(path for path in (shutil.which("pwsh"), shutil.which("powershell")) if path)
    )
    assert interpreters, "no PowerShell interpreter available to test"

    script = ROOT / "automation" / "Sync-AgentOperatingContract.ps1"
    for index, interpreter in enumerate(interpreters):
        case_root = tmp_path / f"case-{index}"
        source_origin = case_root / "source-origin.git"
        source_repo = case_root / "source"
        source_contract = source_repo / "context" / "AGENTS-OPERATING-CONTRACT.md"
        unrelated = source_repo / "unrelated.txt"
        workspace_root = case_root / "workspace"
        target_repo = workspace_root / "lotus-ai"
        target_agents = target_repo / "AGENTS.md"

        subprocess.run(["git", "init", "--bare", str(source_origin)], check=True, capture_output=True)
        source_contract.parent.mkdir(parents=True)
        subprocess.run(["git", "init", str(source_repo)], check=True, capture_output=True)
        _run_git(source_repo, "checkout", "-b", "main")
        _run_git(source_repo, "config", "user.email", "test@example.com")
        _run_git(source_repo, "config", "user.name", "Test User")
        _run_git(source_repo, "remote", "add", "origin", str(source_origin))
        source_contract.write_text("# governed contract\n", encoding="utf-8")
        unrelated.write_text("committed\n", encoding="utf-8")
        _run_git(source_repo, "add", ".")
        _run_git(source_repo, "commit", "-m", "seed source")
        _run_git(source_repo, "push", "-u", "origin", "main")
        unrelated.write_text("uncommitted but unrelated\n", encoding="utf-8")

        target_repo.mkdir(parents=True)
        subprocess.run(["git", "init", str(target_repo)], check=True, capture_output=True)
        _run_git(target_repo, "config", "user.email", "test@example.com")
        _run_git(target_repo, "config", "user.name", "Test User")
        target_agents.write_text("# old contract\n", encoding="utf-8")
        _run_git(target_repo, "add", ".")
        _run_git(target_repo, "commit", "-m", "seed target")

        command = [interpreter, "-NoProfile"]
        if "powershell" in Path(interpreter).stem.lower():
            command += ["-ExecutionPolicy", "Bypass"]
        result = subprocess.run(
            command
            + [
                "-File",
                str(script),
                "-SourcePath",
                str(source_contract),
                "-WorkspaceRoot",
                str(workspace_root),
                "-Repository",
                "lotus-ai",
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )

        assert result.returncode == 0, result.stderr + result.stdout
        assert target_agents.read_text(encoding="utf-8") == "# governed contract\n", (
            result.stderr + result.stdout
        )
        assert "Synchronized AGENTS operating contract" in result.stdout


def _run_sync_with_env(
    env: dict[str, str], *args: str
) -> subprocess.CompletedProcess[str]:
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
        env={**os.environ, **env},
    )


def _committed_repository(root: Path, relative_path: str, content: str) -> Path:
    """Create a checkout with one file committed at HEAD."""
    git = shutil.which("git")
    assert git is not None, "git is required for committed-content tests"
    subprocess.run([git, "init", str(root)], check=True, capture_output=True)
    _run_git(root, "checkout", "-b", "main")
    _run_git(root, "config", "user.email", "test@example.com")
    _run_git(root, "config", "user.name", "Test User")
    target = root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    _run_git(root, "add", ".")
    _run_git(root, "commit", "-m", "initial")
    return target


CONTRACT = "# governed contract\n"


def test_check_only_reads_the_committed_blob_not_the_working_tree(
    tmp_path: Path,
) -> None:
    """A correct working tree over a drifted commit is what the repository ships.

    The bytes on disk are whatever an editor or another session last left there.
    Reading them lets a repository whose *commit* is unsynchronized report that
    it is synchronized, which is the state every other clone would receive.
    """
    source = _committed_repository(
        tmp_path / "source", "context/AGENTS-OPERATING-CONTRACT.md", CONTRACT
    )
    workspace_root = tmp_path / "workspace"
    target = _committed_repository(
        workspace_root / "lotus-ai", "AGENTS.md", "# drifted contract\n"
    )
    # The working tree is repaired but the commit is not: the old check read
    # this and passed.
    target.write_text(CONTRACT, encoding="utf-8")

    result = _run_sync_result(
        "-SourcePath",
        str(source),
        "-WorkspaceRoot",
        str(workspace_root),
        "-Repository",
        "lotus-ai",
        "-CheckOnly",
    )

    output = _console_text(result)
    assert result.returncode != 0, (
        "the working tree matched, but the commit this repository would ship "
        f"did not: {output}"
    )
    assert _says(result, "Committed AGENTS file is not synchronized")


def test_check_only_accepts_a_correct_commit_under_a_dirty_working_tree(
    tmp_path: Path,
) -> None:
    """The other direction, so the rule is a comparison and not a stricter mood.

    An uncommitted local edit is not a synchronization failure; the repository
    still ships the governed contract.
    """
    source = _committed_repository(
        tmp_path / "source", "context/AGENTS-OPERATING-CONTRACT.md", CONTRACT
    )
    workspace_root = tmp_path / "workspace"
    target = _committed_repository(workspace_root / "lotus-ai", "AGENTS.md", CONTRACT)
    target.write_text("# a local edit in progress\n", encoding="utf-8")

    result = _run_sync_result(
        "-SourcePath",
        str(source),
        "-WorkspaceRoot",
        str(workspace_root),
        "-Repository",
        "lotus-ai",
        "-CheckOnly",
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_force_does_not_deploy_a_contract_that_is_not_on_origin_main(
    tmp_path: Path,
) -> None:
    """Force overrides an ownership judgement, never provenance.

    Content that is not on origin/main exists nowhere the receiving repository
    could pull it from, so deploying it publishes policy with no source.
    """
    git = shutil.which("git")
    assert git is not None

    source_origin = tmp_path / "source-origin.git"
    source_repo = tmp_path / "source"
    subprocess.run(
        [git, "init", "--bare", str(source_origin)], check=True, capture_output=True
    )
    source_contract = _committed_repository(
        source_repo, "context/AGENTS-OPERATING-CONTRACT.md", "# main contract\n"
    )
    _run_git(source_repo, "remote", "add", "origin", str(source_origin))
    _run_git(source_repo, "push", "-u", "origin", "main")
    _run_git(source_repo, "checkout", "-b", "topic")
    source_contract.write_text("# branch-only contract\n", encoding="utf-8")
    _run_git(source_repo, "add", ".")
    _run_git(source_repo, "commit", "-m", "branch contract")

    workspace_root = tmp_path / "workspace"
    target = _committed_repository(
        workspace_root / "lotus-ai", "AGENTS.md", "# target contract\n"
    )

    result = _run_sync_result(
        "-SourcePath",
        str(source_contract),
        "-WorkspaceRoot",
        str(workspace_root),
        "-Repository",
        "lotus-ai",
        "-Force",
    )

    assert result.returncode != 0, (
        "a refusal is not a deferral: the target was left unchanged, so the "
        f"run must not exit successfully. {_readable(result)}"
    )
    assert target.read_text(encoding="utf-8") == "# target contract\n", (
        "-Force deployed a contract that exists on no main branch"
    )
    assert _says(result, "-Force does not override this")


def test_force_still_overrides_a_dirty_sibling_checkout(tmp_path: Path) -> None:
    """The override Force is for must keep working, or the guard is just a block."""
    git = shutil.which("git")
    assert git is not None

    source_origin = tmp_path / "source-origin.git"
    source_repo = tmp_path / "source"
    subprocess.run(
        [git, "init", "--bare", str(source_origin)], check=True, capture_output=True
    )
    source_contract = _committed_repository(
        source_repo, "context/AGENTS-OPERATING-CONTRACT.md", CONTRACT
    )
    _run_git(source_repo, "remote", "add", "origin", str(source_origin))
    _run_git(source_repo, "push", "-u", "origin", "main")

    workspace_root = tmp_path / "workspace"
    target = _committed_repository(
        workspace_root / "lotus-ai", "AGENTS.md", "# target contract\n"
    )
    (workspace_root / "lotus-ai" / "unrelated.txt").write_text(
        "work in progress\n", encoding="utf-8"
    )

    result = _run_sync_result(
        "-SourcePath",
        str(source_contract),
        "-WorkspaceRoot",
        str(workspace_root),
        "-Repository",
        "lotus-ai",
        "-Force",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert target.read_text(encoding="utf-8") == CONTRACT, (
        "-Force must still override the dirty-checkout skip it exists for"
    )


def test_check_only_fails_when_it_verified_nothing(tmp_path: Path) -> None:
    """Reporting success for zero comparisons is how this passed on every runner."""
    result = _run_sync_with_env(
        {
            "GITHUB_ACTIONS": "true",
            "CODEX_HOME": str(tmp_path / "absent-codex-home"),
        },
        "-CheckOnly",
        "-IncludeDeployedTarget",
    )

    output = _readable(result)
    assert result.returncode != 0, output
    assert _says(result, "verified no targets")


def test_check_only_defaults_to_this_repository_not_the_deployed_file(
    tmp_path: Path,
) -> None:
    """The repository's own CI check must not depend on a workstation install."""
    result = _run_sync_with_env(
        {
            "GITHUB_ACTIONS": "true",
            "CODEX_HOME": str(tmp_path / "absent-codex-home"),
        },
        "-CheckOnly",
    )

    output = _readable(result)
    assert result.returncode == 0, output
    assert _says(result, "synchronized for 1 target(s)"), output
    assert not _says(result, "absent-codex-home"), (
        "a bare check reached for the machine-local deployed file"
    )


def test_check_only_reads_the_commit_before_requiring_a_file_on_disk(
    tmp_path: Path,
) -> None:
    """A repository ships its commit, not its checkout.

    A file deleted from the working tree but present at HEAD is synchronized:
    every clone receives the committed content. Reporting it as missing would
    describe the state of one checkout rather than the state of the repository.
    """
    source = _committed_repository(
        tmp_path / "source", "context/AGENTS-OPERATING-CONTRACT.md", CONTRACT
    )
    workspace_root = tmp_path / "workspace"
    target = _committed_repository(workspace_root / "lotus-ai", "AGENTS.md", CONTRACT)
    target.unlink()
    assert not target.exists()

    result = _run_sync_result(
        "-SourcePath",
        str(source),
        "-WorkspaceRoot",
        str(workspace_root),
        "-Repository",
        "lotus-ai",
        "-CheckOnly",
    )

    assert result.returncode == 0, _readable(result)


def test_an_explicit_target_inside_a_checkout_is_compared_by_commit(
    tmp_path: Path,
) -> None:
    """How a target was named must not change what is inspected.

    An explicit -TargetPath inside a repository ships its commit exactly as a
    repo-root target does, so a drifted commit under a repaired working tree
    must fail either way.
    """
    source = _committed_repository(
        tmp_path / "source", "context/AGENTS-OPERATING-CONTRACT.md", CONTRACT
    )
    target = _committed_repository(
        tmp_path / "adopter", "AGENTS.md", "# drifted contract\n"
    )
    target.write_text(CONTRACT, encoding="utf-8")

    result = _run_sync_result(
        "-SourcePath", str(source), "-TargetPath", str(target), "-CheckOnly"
    )

    assert result.returncode != 0, (
        "the working tree matched, so a bytes-on-disk comparison would pass an "
        f"unsynchronized commit: {_readable(result)}"
    )
    assert _says(result, "Committed AGENTS file is not synchronized")


def test_committed_content_comparison_keeps_leading_whitespace(
    tmp_path: Path,
) -> None:
    """Whitespace is content; trimming it would report two files as equal."""
    source = _committed_repository(
        tmp_path / "source", "context/AGENTS-OPERATING-CONTRACT.md", CONTRACT
    )
    workspace_root = tmp_path / "workspace"
    _committed_repository(
        workspace_root / "lotus-ai", "AGENTS.md", "   " + CONTRACT
    )

    result = _run_sync_result(
        "-SourcePath",
        str(source),
        "-WorkspaceRoot",
        str(workspace_root),
        "-Repository",
        "lotus-ai",
        "-CheckOnly",
    )

    assert result.returncode != 0, (
        "an indented copy of the contract is not the contract: "
        f"{_readable(result)}"
    )


def test_a_deferred_target_still_reports_success(tmp_path: Path) -> None:
    """A dirty sibling is re-runnable; a refusal is not. They must not report alike.

    Skipping a repository someone else is mid-slice in is a deferral: the
    operator re-runs it there once it is clean. Failing the whole run for that
    would make an `-AllRepoRoots` sweep unusable. Refusing unmerged provenance
    is different in kind, and only that one is an error.
    """
    git = shutil.which("git")
    assert git is not None

    source_origin = tmp_path / "source-origin.git"
    source_repo = tmp_path / "source"
    subprocess.run(
        [git, "init", "--bare", str(source_origin)], check=True, capture_output=True
    )
    source_contract = _committed_repository(
        source_repo, "context/AGENTS-OPERATING-CONTRACT.md", CONTRACT
    )
    _run_git(source_repo, "remote", "add", "origin", str(source_origin))
    _run_git(source_repo, "push", "-u", "origin", "main")

    workspace_root = tmp_path / "workspace"
    target = _committed_repository(
        workspace_root / "lotus-ai", "AGENTS.md", "# target contract\n"
    )
    (workspace_root / "lotus-ai" / "in-progress.txt").write_text(
        "another session is working here\n", encoding="utf-8"
    )

    result = _run_sync_result(
        "-SourcePath",
        str(source_contract),
        "-WorkspaceRoot",
        str(workspace_root),
        "-Repository",
        "lotus-ai",
    )

    assert result.returncode == 0, _readable(result)
    assert target.read_text(encoding="utf-8") == "# target contract\n"
    assert _says(result, "has uncommitted changes")


def test_a_nested_target_is_read_at_its_own_path(tmp_path: Path) -> None:
    """`<rev>:<path>` resolves from the tree root, not from the file's directory.

    Deriving the revision path from the leaf and the repository root from the
    parent directory looked up `<repo>/AGENTS.md` for a target at
    `<repo>/config/AGENTS.md`. That passes or fails on whatever happens to sit
    at the root, which is a different file than the one requested.
    """
    source = _committed_repository(
        tmp_path / "source", "context/AGENTS-OPERATING-CONTRACT.md", CONTRACT
    )
    adopter = tmp_path / "adopter"
    _committed_repository(adopter, "AGENTS.md", CONTRACT)
    nested = adopter / "config" / "AGENTS.md"
    nested.parent.mkdir(parents=True)
    nested.write_text("# a different nested contract\n", encoding="utf-8")
    _run_git(adopter, "add", ".")
    _run_git(adopter, "commit", "-m", "nested contract")

    result = _run_sync_result(
        "-SourcePath", str(source), "-TargetPath", str(nested), "-CheckOnly"
    )

    assert result.returncode != 0, (
        "the root copy matches, so reading the wrong path passes while the "
        f"requested file differs: {_readable(result)}"
    )
    assert _says(result, "Committed AGENTS file is not synchronized")


def test_a_disk_target_is_compared_to_the_committed_source(tmp_path: Path) -> None:
    """An uncommitted source edit must not agree with itself.

    A deployed copy carrying the same uncommitted edit as the source working
    tree would otherwise pass, while differing from the contract at HEAD, which
    is the version every repository actually receives.
    """
    source_repo = tmp_path / "source"
    source = _committed_repository(
        source_repo, "context/AGENTS-OPERATING-CONTRACT.md", CONTRACT
    )
    drifted = "# an uncommitted edit\n"
    source.write_text(drifted, encoding="utf-8")

    deployed = tmp_path / "codex-home" / "AGENTS.md"
    deployed.parent.mkdir(parents=True)
    deployed.write_text(drifted, encoding="utf-8")

    result = _run_sync_result(
        "-SourcePath", str(source), "-TargetPath", str(deployed), "-CheckOnly"
    )

    assert result.returncode != 0, (
        "the deployed copy matches the source working tree but not the "
        f"contract at HEAD: {_readable(result)}"
    )
