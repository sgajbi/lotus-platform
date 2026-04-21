from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _powershell_executable() -> str:
    executable = shutil.which("pwsh") or shutil.which("powershell")
    assert executable is not None, "pwsh or powershell is required for wiki sync tests"
    return executable


def _powershell_command(*args: str) -> list[str]:
    executable = _powershell_executable()
    command = [executable, "-NoProfile"]
    if "powershell" in executable.lower():
        command.extend(["-ExecutionPolicy", "Bypass"])
    command.extend(["-File", str(ROOT / "automation" / "Sync-RepoWikis.ps1"), *args])
    return command


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def _init_wiki_remote(tmp_path: Path, repo_name: str, content: str) -> Path:
    remote = tmp_path / "remotes" / f"{repo_name}.wiki.git"
    seed = tmp_path / "seed" / f"{repo_name}-wiki"
    remote.parent.mkdir(parents=True)
    seed.mkdir(parents=True)

    _git(remote.parent, "init", "--bare", remote.name)
    _git(seed, "init")
    _git(seed, "config", "user.email", "wiki-sync@example.com")
    _git(seed, "config", "user.name", "Wiki Sync Test")
    (seed / "Home.md").write_text(content, encoding="utf-8")
    _git(seed, "add", "Home.md")
    _git(seed, "commit", "-m", "seed wiki")
    _git(seed, "branch", "-M", "master")
    _git(seed, "remote", "add", "origin", str(remote))
    _git(seed, "push", "origin", "master")
    return remote


def test_repo_wiki_sync_check_only_passes_when_published_clone_matches_source(
    tmp_path: Path,
) -> None:
    repo_name = "lotus-platform"
    workspace = tmp_path / "workspace"
    publish_root = tmp_path / "publish"
    source = workspace / repo_name / "wiki"
    source.mkdir(parents=True)
    (source / "Home.md").write_text("# Home\n", encoding="utf-8")
    _init_wiki_remote(tmp_path, repo_name, "# Home\n")

    result = subprocess.run(
        _powershell_command(
            "-CheckOnly",
            "-Repository",
            repo_name,
            "-WorkspaceRoot",
            str(workspace),
            "-PublishRoot",
            str(publish_root),
            "-RemoteOwner",
            str(tmp_path / "remotes"),
        ),
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "lotus-platform" in result.stdout
    assert "0" in result.stdout


def test_repo_wiki_sync_check_only_fails_on_unpublished_wiki_drift(tmp_path: Path) -> None:
    repo_name = "lotus-platform"
    workspace = tmp_path / "workspace"
    publish_root = tmp_path / "publish"
    source = workspace / repo_name / "wiki"
    source.mkdir(parents=True)
    (source / "Home.md").write_text("# Updated Home\n", encoding="utf-8")
    _init_wiki_remote(tmp_path, repo_name, "# Stale Home\n")

    result = subprocess.run(
        _powershell_command(
            "-CheckOnly",
            "-Repository",
            repo_name,
            "-WorkspaceRoot",
            str(workspace),
            "-PublishRoot",
            str(publish_root),
            "-RemoteOwner",
            str(tmp_path / "remotes"),
        ),
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "published GitHub wiki is not synchronized" in result.stderr + result.stdout
    assert "Home.md" in result.stderr + result.stdout


def test_repo_wiki_sync_pr_gate_allows_unpublished_branch_wiki_changes(
    tmp_path: Path,
) -> None:
    repo_name = "lotus-platform"
    workspace = tmp_path / "workspace"
    publish_root = tmp_path / "publish"
    repo_root = workspace / repo_name
    source = repo_root / "wiki"
    source.mkdir(parents=True)
    (source / "Home.md").write_text("# Updated Home\n", encoding="utf-8")
    _init_wiki_remote(tmp_path, repo_name, "# Stale Home\n")
    _git(repo_root, "init")
    _git(repo_root, "config", "user.email", "wiki-sync@example.com")
    _git(repo_root, "config", "user.name", "Wiki Sync Test")

    result = subprocess.run(
        _powershell_command(
            "-CheckOnly",
            "-AllowUnpublishedSourceChanges",
            "-Repository",
            repo_name,
            "-WorkspaceRoot",
            str(workspace),
            "-PublishRoot",
            str(publish_root),
            "-RemoteOwner",
            str(tmp_path / "remotes"),
        ),
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "Publish after merge" in result.stderr + result.stdout


def test_platform_checks_include_repo_wiki_sync_gate() -> None:
    repo_checks = (ROOT / "automation" / "Invoke-PlatformRepoChecks.ps1").read_text(
        encoding="utf-8"
    )

    assert 'Sync-RepoWikis.ps1") -CheckOnly -Repository "lotus-platform"' in repo_checks
    assert "-AllowUnpublishedSourceChanges" in repo_checks
