from __future__ import annotations

import re
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


def _git_output(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def _init_wiki_remote_with_files(
    tmp_path: Path, repo_name: str, files: dict[str, str]
) -> Path:
    remote = tmp_path / "remotes" / f"{repo_name}.wiki.git"
    seed = tmp_path / "seed" / f"{repo_name}-wiki"
    remote.parent.mkdir(parents=True)
    seed.mkdir(parents=True)

    _git(remote.parent, "init", "--bare", remote.name)
    _git(seed, "init")
    _git(seed, "config", "user.email", "wiki-sync@example.com")
    _git(seed, "config", "user.name", "Wiki Sync Test")
    for relative_path, content in files.items():
        path = seed / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    _git(seed, "add", "--all")
    _git(seed, "commit", "-m", "seed wiki")
    _git(seed, "branch", "-M", "master")
    _git(seed, "remote", "add", "origin", str(remote))
    _git(seed, "push", "origin", "master")
    _git(remote, "symbolic-ref", "HEAD", "refs/heads/master")
    return remote


def _init_wiki_remote(tmp_path: Path, repo_name: str, content: str) -> Path:
    return _init_wiki_remote_with_files(tmp_path, repo_name, {"Home.md": content})


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


def test_repo_wiki_sync_check_only_fails_on_case_only_filename_drift(
    tmp_path: Path,
) -> None:
    repo_name = "lotus-platform"
    workspace = tmp_path / "workspace"
    publish_root = tmp_path / "publish"
    source = workspace / repo_name / "wiki"
    source.mkdir(parents=True)
    (source / "Validation-and-CI.md").write_text("# Validation\n", encoding="utf-8")
    _init_wiki_remote_with_files(
        tmp_path,
        repo_name,
        {"Validation-And-CI.md": "# Validation\n"},
    )

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

    output = result.stderr + result.stdout
    assert result.returncode != 0
    assert "published GitHub wiki is not synchronized" in output
    assert "Validation-and-CI.md" in output
    assert "Validation-And-CI.md" in output


def test_repo_wiki_sync_check_only_uses_published_git_tree_paths(
    tmp_path: Path,
) -> None:
    repo_name = "lotus-platform"
    workspace = tmp_path / "workspace"
    publish_root = tmp_path / "publish"
    source = workspace / repo_name / "wiki"
    source.mkdir(parents=True)
    (source / "Validation-and-CI.md").write_text("# Validation\n", encoding="utf-8")
    remote = _init_wiki_remote_with_files(
        tmp_path,
        repo_name,
        {"Validation-And-CI.md": "# Validation\n"},
    )
    published_clone = publish_root / f"{repo_name}-wiki"
    _git(tmp_path, "clone", str(remote), str(published_clone))
    old_path = published_clone / "Validation-And-CI.md"
    temporary_path = published_clone / "Validation-ci.tmp"
    new_path = published_clone / "Validation-and-CI.md"
    old_path.rename(temporary_path)
    temporary_path.rename(new_path)

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

    output = result.stderr + result.stdout
    assert result.returncode != 0
    assert "published GitHub wiki is not synchronized" in output
    assert "Validation-and-CI.md" in output
    assert "Validation-And-CI.md" in output


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


def test_repo_wiki_sync_pr_gate_allows_committed_branch_wiki_changes(
    tmp_path: Path,
) -> None:
    repo_name = "lotus-platform"
    workspace = tmp_path / "workspace"
    publish_root = tmp_path / "publish"
    repo_root = workspace / repo_name
    source = repo_root / "wiki"
    source.mkdir(parents=True)
    _init_wiki_remote(tmp_path, repo_name, "# Stale Home\n")
    _git(repo_root, "init")
    _git(repo_root, "config", "user.email", "wiki-sync@example.com")
    _git(repo_root, "config", "user.name", "Wiki Sync Test")
    (source / "Home.md").write_text("# Stale Home\n", encoding="utf-8")
    _git(repo_root, "add", "wiki/Home.md")
    _git(repo_root, "commit", "-m", "seed wiki source")
    (source / "Home.md").write_text("# Updated Home\n", encoding="utf-8")
    _git(repo_root, "add", "wiki/Home.md")
    _git(repo_root, "commit", "-m", "update wiki source")

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


def test_repo_wiki_sync_publish_pushes_repo_source_to_wiki_remote(tmp_path: Path) -> None:
    repo_name = "lotus-platform"
    workspace = tmp_path / "workspace"
    publish_root = tmp_path / "publish"
    source = workspace / repo_name / "wiki"
    source.mkdir(parents=True)
    (source / "Home.md").write_text("# Published Home\n", encoding="utf-8")
    remote = _init_wiki_remote(tmp_path, repo_name, "# Stale Home\n")

    result = subprocess.run(
        _powershell_command(
            "-Publish",
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

    clone = tmp_path / "published-checkout"
    _git(tmp_path, "clone", str(remote), str(clone))
    assert (clone / "Home.md").read_text(encoding="utf-8") == "# Published Home\n"


def test_repo_wiki_sync_publish_replaces_case_only_filename_drift(tmp_path: Path) -> None:
    repo_name = "lotus-platform"
    workspace = tmp_path / "workspace"
    publish_root = tmp_path / "publish"
    source = workspace / repo_name / "wiki"
    source.mkdir(parents=True)
    (source / "Validation-and-CI.md").write_text("# Validation\n", encoding="utf-8")
    remote = _init_wiki_remote_with_files(
        tmp_path,
        repo_name,
        {"Validation-And-CI.md": "# Validation\n"},
    )

    result = subprocess.run(
        _powershell_command(
            "-Publish",
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

    clone = tmp_path / "case-published-checkout"
    _git(tmp_path, "clone", str(remote), str(clone))
    tree = set(_git_output(clone, "ls-tree", "--name-only", "HEAD").splitlines())
    assert "Validation-and-CI.md" in tree
    assert "Validation-And-CI.md" not in tree


def test_repo_wiki_sync_publish_pushes_existing_local_wiki_commit(
    tmp_path: Path,
) -> None:
    repo_name = "lotus-platform"
    workspace = tmp_path / "workspace"
    publish_root = tmp_path / "publish"
    source = workspace / repo_name / "wiki"
    source.mkdir(parents=True)
    (source / "Home.md").write_text("# Published Home\n", encoding="utf-8")
    remote = _init_wiki_remote(tmp_path, repo_name, "# Stale Home\n")
    published_clone = publish_root / f"{repo_name}-wiki"
    _git(tmp_path, "clone", str(remote), str(published_clone))
    _git(published_clone, "config", "user.email", "wiki-sync@example.com")
    _git(published_clone, "config", "user.name", "Wiki Sync Test")
    (published_clone / "Home.md").write_text("# Published Home\n", encoding="utf-8")
    _git(published_clone, "add", "Home.md")
    _git(published_clone, "commit", "-m", "local unpublished wiki commit")

    result = subprocess.run(
        _powershell_command(
            "-Publish",
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

    clone = tmp_path / "published-ahead-checkout"
    _git(tmp_path, "clone", str(remote), str(clone))
    assert (clone / "Home.md").read_text(encoding="utf-8") == "# Published Home\n"


def test_platform_checks_include_repo_wiki_sync_gate() -> None:
    repo_checks = (ROOT / "automation" / "Invoke-PlatformRepoChecks.ps1").read_text(
        encoding="utf-8"
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
    assert "-AllowUnpublishedSourceChanges" in repo_checks


def test_repo_wiki_sync_git_wrapper_preserves_exit_code_without_stderr_noise_failure() -> None:
    sync_script = (ROOT / "automation" / "Sync-RepoWikis.ps1").read_text(
        encoding="utf-8"
    )

    assert '$previousErrorActionPreference = $ErrorActionPreference' in sync_script
    assert '$ErrorActionPreference = "Continue"' in sync_script
    assert 'if ($exitCode -ne 0)' in sync_script


def _console_text(result: subprocess.CompletedProcess) -> str:
    """Readable text from a PowerShell run.

    PowerShell 7 renders a thrown message as a boxed error record: ANSI colour
    codes, a `Line |` gutter, and hard wrapping at the console width, all
    inserted *between words*. Asserting against the raw stream tests the
    terminal renderer rather than the message, and passes or fails on width.
    """
    plain = re.sub(r"\x1b\[[0-9;]*m", "", result.stderr + result.stdout)
    plain = re.sub(r"^\s*\|", " ", plain, flags=re.MULTILINE)
    return " ".join(plain.split())


def _run(repo_name: str, workspace: Path, publish_root: Path, tmp_path: Path, *args: str):
    return subprocess.run(
        _powershell_command(
            *args,
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


def _workspace_with_source(tmp_path: Path, repo_name: str, files: dict[str, str]) -> Path:
    workspace = tmp_path / "workspace"
    source = workspace / repo_name / "wiki"
    source.mkdir(parents=True)
    for relative_path, content in files.items():
        path = source / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return workspace


def test_publish_refuses_to_destroy_a_page_that_exists_only_on_the_wiki(
    tmp_path: Path,
) -> None:
    """The case the old check could not see.

    `-Publish` clears the published tree and copies source over it, so a page
    present only on the wiki is destroyed with no warning and no record outside
    the wiki repository's own history. The comparison that preceded it returned
    a list of differing paths with no direction, so it could not distinguish
    this from an ordinary unrun publish.
    """
    repo_name = "lotus-platform"
    workspace = _workspace_with_source(tmp_path, repo_name, {"Home.md": "# Home\n"})
    _init_wiki_remote_with_files(
        tmp_path,
        repo_name,
        {"Home.md": "# Home\n", "Hand-Edited.md": "# Only on the wiki\n"},
    )

    result = _run(repo_name, workspace, tmp_path / "publish", tmp_path, "-Publish")

    output = _console_text(result)
    assert result.returncode != 0, output
    assert "refusing to publish" in output
    assert "Hand-Edited.md" in output


def test_the_refused_page_is_still_on_the_wiki_afterwards(tmp_path: Path) -> None:
    """A refusal that had already deleted the file would be worthless."""
    repo_name = "lotus-platform"
    workspace = _workspace_with_source(tmp_path, repo_name, {"Home.md": "# Home\n"})
    _init_wiki_remote_with_files(
        tmp_path,
        repo_name,
        {"Home.md": "# Home\n", "Hand-Edited.md": "# Only on the wiki\n"},
    )
    publish_root = tmp_path / "publish"

    _run(repo_name, workspace, publish_root, tmp_path, "-Publish")

    assert (publish_root / f"{repo_name}-wiki" / "Hand-Edited.md").exists()


def test_publish_proceeds_when_the_loss_is_explicitly_accepted(tmp_path: Path) -> None:
    """The override exists, and names what it destroyed.

    Publishing must be possible when the published-only content is genuinely
    unwanted -- but only as a stated decision, and the warning carries the path
    so the choice is auditable afterwards.
    """
    repo_name = "lotus-platform"
    workspace = _workspace_with_source(tmp_path, repo_name, {"Home.md": "# Home\n"})
    _init_wiki_remote_with_files(
        tmp_path,
        repo_name,
        {"Home.md": "# Home\n", "Hand-Edited.md": "# Only on the wiki\n"},
    )
    publish_root = tmp_path / "publish"

    result = _run(
        repo_name,
        workspace,
        publish_root,
        tmp_path,
        "-Publish",
        "-AllowPublishedContentLoss",
    )

    output = _console_text(result)
    assert result.returncode == 0, output
    assert "Hand-Edited.md" in output
    assert not (publish_root / f"{repo_name}-wiki" / "Hand-Edited.md").exists()


def test_an_ordinary_unpublished_change_still_publishes(tmp_path: Path) -> None:
    """Source-ahead is the common case and must not be caught by the refusal.

    A guard that also blocked the ordinary path would be worse than the defect:
    it would train the operator to pass the override every time, which is the
    same erosion as a permanently red gate.
    """
    repo_name = "lotus-platform"
    workspace = _workspace_with_source(
        tmp_path, repo_name, {"Home.md": "# Home\n", "New-Page.md": "# Added\n"}
    )
    _init_wiki_remote_with_files(tmp_path, repo_name, {"Home.md": "# Home\n"})
    publish_root = tmp_path / "publish"

    result = _run(repo_name, workspace, publish_root, tmp_path, "-Publish")

    assert result.returncode == 0, result.stderr + result.stdout
    assert (publish_root / f"{repo_name}-wiki" / "New-Page.md").exists()


def test_check_only_names_the_direction_of_each_drift(tmp_path: Path) -> None:
    """`Drift: <paths>` alone cannot tell an unrun publish from lost content.

    The three classifications are separate because the responses are: publish,
    recover-then-publish, and publish. Reading a modified-in-both file as
    one-sided produces the right answer for the wrong reason, which holds until
    the file is genuinely one-sided.
    """
    repo_name = "lotus-platform"
    workspace = _workspace_with_source(
        tmp_path,
        repo_name,
        {"Home.md": "# Updated\n", "Source-Only.md": "# New\n"},
    )
    _init_wiki_remote_with_files(
        tmp_path,
        repo_name,
        {"Home.md": "# Stale\n", "Published-Only.md": "# Wiki only\n"},
    )

    result = _run(repo_name, workspace, tmp_path / "publish", tmp_path, "-CheckOnly")

    output = _console_text(result)
    assert result.returncode != 0
    assert "Home.md [ModifiedBoth]" in output
    assert "Source-Only.md [SourceOnly]" in output
    assert "Published-Only.md [PublishedOnly]" in output
    assert "publishing would destroy them" in output

def _git_workspace_with_wiki_change(
    tmp_path: Path, repo_name: str, published_state: dict[str, str], branch_state: dict[str, str]
) -> Path:
    """A workspace repo whose branch genuinely changes wiki/ relative to origin/main.

    Without this the allowance branch is unreachable: `Test-WikiSourceChanged`
    asks git what this branch did to `wiki/`, and a plain directory answers
    nothing. A test that never reaches the branch it names is not evidence about
    it, however green it runs.
    """
    workspace = tmp_path / "workspace"
    repository_root = workspace / repo_name
    source = repository_root / "wiki"
    source.mkdir(parents=True)

    def _git(*arguments: str) -> None:
        subprocess.run(
            ["git", *arguments],
            cwd=repository_root,
            check=True,
            capture_output=True,
            text=True,
        )

    _git("init", "--quiet")
    _git("config", "user.email", "test@example.invalid")
    _git("config", "user.name", "Test")
    for relative_path, content in published_state.items():
        (source / relative_path).write_text(content, encoding="utf-8")
    _git("add", "-A")
    _git("commit", "--quiet", "-m", "base")
    base = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository_root, check=True, capture_output=True, text=True,
    ).stdout.strip()
    # The script compares against origin/main, so it must exist as a ref.
    _git("update-ref", "refs/remotes/origin/main", base)

    for existing in source.iterdir():
        existing.unlink()
    for relative_path, content in branch_state.items():
        (source / relative_path).write_text(content, encoding="utf-8")
    _git("add", "-A")
    _git("commit", "--quiet", "-m", "branch edits wiki")
    return workspace


def test_an_ordinary_rename_is_not_content_loss(tmp_path: Path) -> None:
    """Old.md -> New.md with the content unchanged must still publish.

    The first version of the refusal recognised only case-only renames, so an
    ordinary move produced a PublishedOnly entry for the old path and a
    SourceOnly entry for the new one, and refused the routine post-merge
    publish. Found in review.

    Identity is the CONTENT. If the published file's bytes are still authored
    under some source path, overwriting the published tree destroys nothing --
    which is a different question from whether the path survived.
    """
    repo_name = "lotus-platform"
    workspace = _workspace_with_source(
        tmp_path, repo_name, {"Home.md": "# Home", "New-Name.md": "# Moved page"}
    )
    _init_wiki_remote_with_files(
        tmp_path,
        repo_name,
        {"Home.md": "# Home", "Old-Name.md": "# Moved page"},
    )
    publish_root = tmp_path / "publish"

    result = _run(repo_name, workspace, publish_root, tmp_path, "-Publish")

    output = result.stderr + result.stdout
    assert result.returncode == 0, output
    assert (publish_root / f"{repo_name}-wiki" / "New-Name.md").exists()
    assert not (publish_root / f"{repo_name}-wiki" / "Old-Name.md").exists()


def test_the_branch_allowance_does_not_swallow_published_only_drift(
    tmp_path: Path,
) -> None:
    """The pre-merge gate must still fail on a page that exists only live.

    `-AllowUnpublishedSourceChanges` exists so a branch that edits wiki/ is
    not blocked by its own unpublished drift. It used to consume every
    category, so an unrelated hand-edited-only page passed the gate whenever
    a branch touched wiki/ at all -- and the post-merge publish then refused,
    stranding the merged wiki change with no forward move that does not
    discard someone's page. Found in review.

    A branch never creates PublishedOnly drift, so the allowance can never
    legitimately cover it.
    """
    repo_name = "lotus-platform"
    workspace = _git_workspace_with_wiki_change(
        tmp_path,
        repo_name,
        {"Home.md": "# Home"},
        {"Home.md": "# Edited by this branch"},
    )
    _init_wiki_remote_with_files(
        tmp_path,
        repo_name,
        {"Home.md": "# Home", "Hand-Edited.md": "# Only on the wiki"},
    )

    result = _run(
        repo_name,
        workspace,
        tmp_path / "publish",
        tmp_path,
        "-CheckOnly",
        "-AllowUnpublishedSourceChanges",
    )

    output = _console_text(result)
    assert result.returncode != 0, output
    assert "Hand-Edited.md" in output

def test_identical_content_does_not_make_a_distinct_page_a_rename(
    tmp_path: Path,
) -> None:
    """Two published pages sharing content must not delete one another.

    Matching a published-only page's content against ANY source path was the
    first attempt, and review found it destroys a distinct page: if two
    published pages happen to hold the same bytes and source keeps only one,
    the other matches the retained page's hash, is classified as a rename, and
    is deleted with no override.

    The counterpart must be a source path that does not exist on the published
    wiki -- a page that genuinely arrived under a new name.
    """
    repo_name = "lotus-platform"
    shared = "# Shared boilerplate"
    workspace = _workspace_with_source(
        tmp_path, repo_name, {"Keep.md": shared}
    )
    _init_wiki_remote_with_files(
        tmp_path,
        repo_name,
        {"Keep.md": shared, "Distinct.md": shared},
    )
    publish_root = tmp_path / "publish"

    result = _run(repo_name, workspace, publish_root, tmp_path, "-Publish")

    output = _console_text(result)
    assert result.returncode != 0, output
    assert "Distinct.md" in output
    assert (publish_root / f"{repo_name}-wiki" / "Distinct.md").exists()

def test_a_page_the_repository_deleted_is_not_content_loss(tmp_path: Path) -> None:
    """A page authored in wiki/ and then removed must still publish.

    Making PublishedOnly unconditionally blocking was correct for hand edits
    and wrong for deletions: an intentional removal reaches the comparison
    looking identical to an unrelated live-only page, so the pre-merge gate
    rejected the branch and the post-merge publish refused it, leaving a
    destructive-sounding override as the only route through a decision that
    had already been reviewed and merged.

    History separates them. This page has commits under wiki/ and no file
    today, so its removal was authored.
    """
    repo_name = "lotus-platform"
    workspace = _git_workspace_with_wiki_change(
        tmp_path,
        repo_name,
        {"Home.md": "# Home", "Obsolete.md": "# Retired page"},
        {"Home.md": "# Home"},
    )
    _init_wiki_remote_with_files(
        tmp_path,
        repo_name,
        {"Home.md": "# Home", "Obsolete.md": "# Retired page"},
    )
    publish_root = tmp_path / "publish"

    result = _run(repo_name, workspace, publish_root, tmp_path, "-Publish")

    output = _console_text(result)
    assert result.returncode == 0, output
    assert not (publish_root / f"{repo_name}-wiki" / "Obsolete.md").exists()


def test_a_page_never_authored_in_source_still_blocks(tmp_path: Path) -> None:
    """The deletion allowance must not become a blanket allowance.

    A page hand-created on the live wiki has no history under wiki/, so it is
    not an authored removal and the refusal must stand. Without this the
    previous case would read as coverage while having removed the guard.
    """
    repo_name = "lotus-platform"
    workspace = _git_workspace_with_wiki_change(
        tmp_path,
        repo_name,
        {"Home.md": "# Home"},
        {"Home.md": "# Home edited"},
    )
    _init_wiki_remote_with_files(
        tmp_path,
        repo_name,
        {"Home.md": "# Home", "Hand-Made.md": "# Never in source"},
    )
    publish_root = tmp_path / "publish"

    result = _run(repo_name, workspace, publish_root, tmp_path, "-Publish")

    output = _console_text(result)
    assert result.returncode != 0, output
    assert "Hand-Made.md" in output
    assert (publish_root / f"{repo_name}-wiki" / "Hand-Made.md").exists()

def test_two_published_pages_cannot_both_rename_into_one(tmp_path: Path) -> None:
    """One source-only page cannot absorb two published-only pages.

    Taking the first source-only content match allows a fan-in: two published
    pages holding the same bytes both match the single source page that
    replaced one of them, both are classified as renames, and publishing
    replaces two distinct pages with one without asking for the override.

    Counting the counterparts refuses that while still accepting an ordinary
    one-for-one move, and it needs no arbitrary choice about which published
    page the survivor is.
    """
    repo_name = "lotus-platform"
    shared = "# Same bytes"
    workspace = _workspace_with_source(
        tmp_path, repo_name, {"Home.md": "# Home", "Merged.md": shared}
    )
    _init_wiki_remote_with_files(
        tmp_path,
        repo_name,
        {"Home.md": "# Home", "First.md": shared, "Second.md": shared},
    )
    publish_root = tmp_path / "publish"

    result = _run(repo_name, workspace, publish_root, tmp_path, "-Publish")

    output = _console_text(result)
    assert result.returncode != 0, output
    assert (publish_root / f"{repo_name}-wiki" / "First.md").exists()
    assert (publish_root / f"{repo_name}-wiki" / "Second.md").exists()

def test_a_local_deletion_in_the_clone_cannot_reach_the_wiki(tmp_path: Path) -> None:
    """A leftover deletion in the reusable clone must not publish silently.

    The comparison read the clone working tree, so a page deleted there -- an
    interrupted publish leaves exactly this -- was absent from the published
    map, no PublishedOnly refusal fired, and the unconditional push sent the
    deletion to the live wiki with no override ever requested.

    `pull --ff-only` does not prevent it: it succeeds when the local branch is
    merely ahead. Resetting to origin/<branch> makes the comparison read what
    the wiki actually holds.
    """
    repo_name = "lotus-platform"
    workspace = _workspace_with_source(
        tmp_path, repo_name, {"Home.md": "# Home"}
    )
    _init_wiki_remote_with_files(
        tmp_path,
        repo_name,
        {"Home.md": "# Home", "Hand-Edited.md": "# Only on the wiki"},
    )
    publish_root = tmp_path / "publish"

    # First run populates the clone and refuses, as it should.
    _run(repo_name, workspace, publish_root, tmp_path, "-Publish")
    clone = publish_root / f"{repo_name}-wiki"
    assert (clone / "Hand-Edited.md").exists()

    # The leftover must be COMMITTED, which is the case the map cannot see.
    # An uncommitted deletion is already safe: Get-WikiFileMap reads
    # `git ls-files`, so a tracked-but-missing file still appears, with a
    # sentinel hash, and is refused. My first version of this test deleted the
    # file without committing and therefore proved nothing -- it passed with and
    # without the fix, because it exercised the path that already worked.
    (clone / "Hand-Edited.md").unlink()
    for arguments in (
        ["add", "-A"],
        ["-c", "user.email=t@example.invalid", "-c", "user.name=T",
         "commit", "--quiet", "-m", "leftover deletion"],
    ):
        subprocess.run(["git", *arguments], cwd=clone, check=True, capture_output=True)

    result = _run(repo_name, workspace, publish_root, tmp_path, "-Publish")

    output = _console_text(result)
    assert result.returncode != 0, output
    assert "Hand-Edited.md" in output

def test_a_shallow_checkout_refuses_to_classify(tmp_path: Path) -> None:
    """A depth-1 checkout cannot tell an authored deletion from a stray page.

    `git log -- wiki/X.md` exits successfully and returns nothing when the
    page existed only in an unfetched parent, so the deletion check silently
    answered no and the gate rejected every deliberate page-removal PR. The
    platform lanes checked out at depth 1, so this was the CI behaviour, not a
    corner case.

    An unanswerable question must not be answered. Refusing loudly is what
    makes the missing fetch-depth visible instead of looking like content loss.
    """
    repo_name = "lotus-platform"
    workspace = _git_workspace_with_wiki_change(
        tmp_path,
        repo_name,
        {"Home.md": "# Home", "Obsolete.md": "# Retired"},
        {"Home.md": "# Home"},
    )
    _init_wiki_remote_with_files(
        tmp_path,
        repo_name,
        {"Home.md": "# Home", "Obsolete.md": "# Retired"},
    )
    # Make the workspace repository shallow, as a depth-1 CI checkout is.
    repository_root = workspace / repo_name
    subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository_root, check=True, capture_output=True, text=True,
    )
    (repository_root / ".git" / "shallow").write_text("", encoding="utf-8")

    result = _run(
        repo_name, workspace, tmp_path / "publish", tmp_path, "-CheckOnly",
    )

    output = _console_text(result)
    assert result.returncode != 0, output
    # Anchored on the refusal's own words, not on "shallow": git emits its own
    # messages mentioning shallow repositories, and asserting that substring
    # passed even with the guard disabled -- the drift refusal fires either way,
    # so only the wording distinguishes them.
    assert "Cannot classify" in output, output

def test_a_deleted_path_recreated_on_the_wiki_still_blocks(tmp_path: Path) -> None:
    """Having existed in source is not enough to call a removal authored.

    A page whose path was authored and later removed, but whose published copy
    was afterwards hand-edited or recreated, still has history under `wiki/`.
    Treating that as an authored removal deletes live content nobody authored,
    with no override -- the exact failure this change exists to prevent,
    reintroduced by the deletion allowance itself.

    The live bytes must match the last version source actually authored.
    """
    repo_name = "lotus-platform"
    workspace = _git_workspace_with_wiki_change(
        tmp_path,
        repo_name,
        {"Home.md": "# Home", "Obsolete.md": "# Original retired text"},
        {"Home.md": "# Home"},
    )
    # The live wiki carries the same PATH with different content: someone
    # recreated or edited it after the authored removal.
    _init_wiki_remote_with_files(
        tmp_path,
        repo_name,
        {"Home.md": "# Home", "Obsolete.md": "# Rewritten by hand on the wiki"},
    )
    publish_root = tmp_path / "publish"

    result = _run(repo_name, workspace, publish_root, tmp_path, "-Publish")

    output = _console_text(result)
    assert result.returncode != 0, output
    assert "Obsolete.md" in output
    assert (publish_root / f"{repo_name}-wiki" / "Obsolete.md").exists()

