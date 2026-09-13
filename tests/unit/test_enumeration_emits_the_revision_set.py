"""Execute the enumeration the dispatcher ships, and read what it publishes.

The validator reads workflow YAML and reasons about it. That is necessary --
it must judge dispatchers it cannot run -- but it is not sufficient, because
every question it answers is about the *text* of a shell script. Reviewing
`#847` found the gap that shape leaves: a step could compute every revision,
overwrite the variable with `[]`, publish that, and satisfy a validator
tracking variable names.

An earlier version of this file answered that with a hand-written model of
the enumeration and a stubbed `git`. `#860` found the gap *that* leaves: the
model was a copy, the copy drifted from the workflow when `#857` moved this
repository from a count-bounded walk to the base..tip range, and every
assertion stayed green against a form the repository no longer ships.

So these tests extract the enumeration step's `run` block from the workflow
at test time, execute it with the runner's own shell invocation against real
throwaway Git histories, capture the real `GITHUB_OUTPUT`, and assert the
emitted value is JSON holding exactly the revisions the merge landed. When
the workflow changes and this file does not, the extraction or the behaviour
fails; nothing here can keep passing against a stale copy.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
DISPATCHER = ROOT / ".github" / "workflows" / "merged-pr-main-releasability.yml"
ENUMERATION_JOB = "enumerate-merged-revisions"
ENUMERATION_STEP_ID = "enumerate"
OUTPUT_KEY = "revisions"

# `jq` is absent from the Git Bash toolchain this repository is developed on and
# present on the CI runner. Rather than skip locally -- a test that cannot fail
# is the thing this file exists to stop -- a shim stands in, and
# `test_the_jq_shim_matches_the_two_invocations_used` pins its behaviour so the
# harness is not validating against an unexamined stand-in.
JQ_SHIM = """#!/usr/bin/env python3
import json, sys
args = sys.argv[1:]
data = sys.stdin.read()
if "-R" in args:
    for line in data.splitlines():
        print(json.dumps(line))
elif "-sc" in args or "-s" in args:
    print(json.dumps([json.loads(l) for l in data.splitlines() if l.strip()], separators=(",", ":")))
else:
    sys.exit("unsupported jq invocation: " + " ".join(args))
"""


def _shipped_enumeration() -> str:
    """The enumeration step's `run` block, read from the workflow at test time.

    Nothing here is a copy. The step is located by job and id, and the job
    must publish that step's `revisions` output, because that is the value the
    dispatch matrix expands. If the workflow changes shape so this lookup no
    longer resolves, the test fails rather than continuing against a model.
    """
    workflow = yaml.safe_load(DISPATCHER.read_text(encoding="utf-8"))
    job = workflow["jobs"][ENUMERATION_JOB]
    steps = [step for step in job["steps"] if step.get("id") == ENUMERATION_STEP_ID]
    assert len(steps) == 1, f"expected one step with id {ENUMERATION_STEP_ID!r}: {steps}"
    assert job["outputs"][OUTPUT_KEY] == (
        f"${{{{ steps.{ENUMERATION_STEP_ID}.outputs.{OUTPUT_KEY} }}}}"
    ), "the dispatch matrix must expand the enumeration step's own output"
    run = steps[0]["run"]
    assert isinstance(run, str) and run.strip(), "the enumeration step ships no run block"
    return run


def _shipped_shell() -> str:
    """The POSIX shell that executes the extracted block.

    On Windows the `bash` on PATH can be the WSL launcher, which need not have
    a distribution behind it, so PATH is never consulted there. Git for Windows
    ships its own bash beside git, and git is already a hard requirement of
    these tests, so that bash exists wherever they can run at all. A test that
    only runs in CI is a test that stops being read.
    """
    if sys.platform != "win32":
        executable = shutil.which("bash")
        if executable is None:  # pragma: no cover - environment guard
            pytest.fail("bash is required to execute the shipped enumeration")
        return executable

    git = shutil.which("git")
    if git is None:  # pragma: no cover - environment guard
        pytest.fail("git is required to execute the shipped enumeration")
    exec_path = subprocess.run(
        [git, "--exec-path"], capture_output=True, text=True, check=True
    ).stdout.strip()
    for origin in (Path(git).resolve(), Path(exec_path)):
        for ancestor in origin.parents:
            for candidate in (ancestor / "bin" / "bash.exe", ancestor / "usr" / "bin" / "bash.exe"):
                if candidate.exists():
                    return str(candidate)
    pytest.fail(f"no Git for Windows bash found beside {git}")  # pragma: no cover


def _toolchain(tmp_path: Path) -> Path:
    """A PATH prefix holding a stubbed `gh`, and `jq` when the real one is absent.

    `git` is deliberately not stubbed: the range form needs real commits to
    enumerate, and a stub would return whatever it was told and prove nothing
    about the range.
    """
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()

    # The only `gh` call in the enumeration reads the repository's merge
    # methods; the dispatcher refuses anything but rebase-only merging.
    (bin_dir / "gh").write_text(
        "#!/usr/bin/env bash\necho 'false,false,true'\n", encoding="utf-8", newline="\n"
    )
    if shutil.which("jq") is None:
        # The interpreter path must be POSIX-style and quoted. A Windows path
        # written into a bash script has its separators consumed as escapes, and
        # the wrapper then reports "command not found" for a file that exists.
        interpreter = Path(sys.executable).as_posix()
        shim = (bin_dir / "jq.py").as_posix()
        (bin_dir / "jq").write_text(
            f'#!/usr/bin/env bash\n"{interpreter}" "{shim}" "$@"\n',
            encoding="utf-8",
            newline="\n",
        )
        (bin_dir / "jq.py").write_text(JQ_SHIM, encoding="utf-8", newline="\n")
    for path in bin_dir.iterdir():
        path.chmod(0o755)
    return bin_dir


def _git_environment(tmp_path: Path) -> dict[str, str]:
    """An environment in which git reads no developer configuration.

    The developer's global config can require signed commits, route hooks, or
    rewrite line endings. None of that is part of the enumeration under test,
    and a signing prompt would hang the suite. Identity comes from the
    environment so no per-repository `git config` round trips are needed.
    """
    empty_config = tmp_path / "gitconfig"
    empty_config.touch()
    return {
        **os.environ,
        "GIT_CONFIG_GLOBAL": str(empty_config),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "test",
        "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "test",
        "GIT_COMMITTER_EMAIL": "test@example.com",
    }


@dataclass(frozen=True)
class History:
    """A throwaway origin and the clone the enumeration runs in."""

    origin: Path
    clone: Path
    environment: dict[str, str]

    def git(self, repository: Path, *args: str) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=repository,
            env=self.environment,
            capture_output=True,
            text=True,
            check=True,
        )
        return completed.stdout.strip()

    def commit(self, message: str) -> str:
        """A commit on origin's current branch. Content is irrelevant to the
        enumeration, so the commit is empty and costs one process, not three."""
        self.git(self.origin, "commit", "-q", "--allow-empty", "-m", message)
        return self.git(self.origin, "rev-parse", "HEAD")

    def clone_origin(self) -> None:
        """Take the clone the enumeration will run in, at origin's current state."""
        self.git(self.origin.parent, "clone", "-q", self.origin.as_posix(), self.clone.as_posix())


def _history(tmp_path: Path) -> History:
    origin = tmp_path / "origin"
    origin.mkdir()
    history = History(origin=origin, clone=tmp_path / "clone", environment=_git_environment(tmp_path))
    history.git(origin, "init", "-q", "-b", "main")
    return history


def _run_shipped_enumeration(
    tmp_path: Path,
    history: History,
    *,
    base_sha: str,
    merge_commit_sha: str,
    commit_count: int,
    script: str | None = None,
) -> tuple[subprocess.CompletedProcess[str], str]:
    """Execute the enumeration in the clone and return (result, GITHUB_OUTPUT).

    The invocation mirrors the runner's default for a `run` step on Linux --
    `bash --noprofile --norc -eo pipefail <file>` -- rather than `bash -c`, so
    the block runs exactly as the workflow would run it.
    """
    bin_dir = _toolchain(tmp_path)
    output_file = tmp_path / "github_output"
    output_file.touch()
    script_file = tmp_path / "enumerate.sh"
    script_file.write_text(script or _shipped_enumeration(), encoding="utf-8", newline="\n")
    environment = {
        **history.environment,
        "PATH": f"{bin_dir.as_posix()}{os.pathsep}{os.environ['PATH']}",
        "GITHUB_OUTPUT": output_file.as_posix(),
        "GITHUB_REPOSITORY": "sgajbi/lotus-platform",
        "MERGE_COMMIT_SHA": merge_commit_sha,
        "BASE_SHA": base_sha,
        "COMMIT_COUNT": str(commit_count),
        "PR_NUMBER": "860",
    }
    completed = subprocess.run(
        [_shipped_shell(), "--noprofile", "--norc", "-eo", "pipefail", script_file.as_posix()],
        cwd=history.clone,
        env=environment,
        capture_output=True,
        text=True,
    )
    return completed, output_file.read_text(encoding="utf-8")


def _emitted(output: str, key: str = OUTPUT_KEY) -> str | None:
    for line in output.splitlines():
        name, separator, value = line.partition("=")
        if separator and name == key:
            return value
    return None


def test_enumeration_emits_json_with_the_complete_revision_set(tmp_path: Path) -> None:
    """Three revisions land; three are published, oldest first, as a JSON array."""
    history = _history(tmp_path)
    base = history.commit("root")
    landed = [history.commit(f"this PR, revision {n}") for n in (1, 2, 3)]
    history.clone_origin()

    completed, output = _run_shipped_enumeration(
        tmp_path, history, base_sha=base, merge_commit_sha=landed[-1], commit_count=3
    )

    assert completed.returncode == 0, completed.stderr
    emitted = _emitted(output)
    assert emitted is not None, f"nothing published under {OUTPUT_KEY!r}: {output!r}"

    parsed = json.loads(emitted)
    assert isinstance(parsed, list), "fromJson requires an array, not raw lines"
    assert parsed == landed
    assert len(parsed) == len(landed)


def test_a_dropped_duplicate_leaves_the_count_stale_and_the_window_complete(
    tmp_path: Path,
) -> None:
    """The mechanism behind #859 and gateway#744, reproduced rather than argued.

    A branch of four commits carried one that main already had; the rebase
    dropped it and three landed. `pull_request.commits` still says four. The
    shipped range enumerates exactly the three, tolerates the stale count with
    a notice, and publishes a complete window.

    The count-bounded walk the estate used to ship is run beside it with the
    same real git: it reaches the earlier PR's commit, and that commit is a
    genuine ancestor of the tip and genuinely makes the count -- which is why
    an ancestry guard and a count assertion both accepted the wrong window.
    """
    history = _history(tmp_path)
    history.commit("root")
    earlier_pr_commit = history.commit("landed by an earlier PR")
    landed = [history.commit(f"this PR, revision {n}") for n in (1, 2, 3)]
    history.clone_origin()
    declared = len(landed) + 1

    completed, output = _run_shipped_enumeration(
        tmp_path,
        history,
        base_sha=earlier_pr_commit,
        merge_commit_sha=landed[-1],
        commit_count=declared,
    )

    assert completed.returncode == 0, completed.stderr
    assert json.loads(_emitted(output) or "null") == landed
    assert "::notice::" in completed.stdout, "a stale count over a complete window must not fail"
    assert "::error::" not in completed.stdout

    by_count = list(
        reversed(history.git(history.clone, "rev-list", "-n", str(declared), landed[-1]).splitlines())
    )
    assert earlier_pr_commit in by_count, (
        "the count-bounded walk must reach the earlier PR's commit -- if it does not, "
        "this test no longer reproduces the defect it exists for"
    )
    assert len(by_count) == declared, "a count assertion accepts the wrong window"
    ancestry = subprocess.run(
        ["git", "merge-base", "--is-ancestor", earlier_pr_commit, landed[-1]],
        cwd=history.clone,
        env=history.environment,
        capture_output=True,
        check=False,  # the exit status IS the assertion here
    )
    assert ancestry.returncode == 0, "an ancestry check also accepts the wrong window"


def test_a_base_that_main_moved_past_is_refused_before_anything_is_published(
    tmp_path: Path,
) -> None:
    """More revisions than declared means the range spans another PR's commits.

    `base.sha` was never re-synchronised while main advanced, so base..tip
    holds a revision an earlier merge landed. Dispatching it would stamp this
    PR's number onto that PR's commit. The over-claim is refused, and nothing
    reaches `GITHUB_OUTPUT`.
    """
    history = _history(tmp_path)
    stale_base = history.commit("root")
    history.commit("landed by an earlier PR after base.sha was taken")
    landed = [history.commit(f"this PR, revision {n}") for n in (1, 2)]
    history.clone_origin()

    completed, output = _run_shipped_enumeration(
        tmp_path, history, base_sha=stale_base, merge_commit_sha=landed[-1], commit_count=2
    )

    assert completed.returncode != 0
    assert "::error::" in completed.stdout
    assert _emitted(output) is None


def test_an_empty_interval_fails_rather_than_publishing_nothing(tmp_path: Path) -> None:
    """The guard the validator requires, proven by running it.

    base..tip is empty when the two are the same commit. An empty matrix is
    zero jobs, and zero jobs is a success, so the enumeration must fail here
    instead of publishing `[]`.
    """
    history = _history(tmp_path)
    tip = history.commit("root")
    history.clone_origin()

    completed, output = _run_shipped_enumeration(
        tmp_path, history, base_sha=tip, merge_commit_sha=tip, commit_count=1
    )

    assert completed.returncode != 0
    assert "::error::" in completed.stdout
    assert _emitted(output) is None


def test_a_revision_no_longer_on_main_is_refused(tmp_path: Path) -> None:
    """Ancestry is judged against the freshly fetched main, not the event snapshot.

    Between the merge event and this job, main was force-moved onto other
    history. The merged revisions still exist as objects, but they are not
    main history any more and must not be tagged or gated as if they were.
    """
    history = _history(tmp_path)
    base = history.commit("root")
    landed = [history.commit(f"this PR, revision {n}") for n in (1, 2, 3)]
    history.clone_origin()
    history.git(history.clone, "branch", "merged-pr-head", landed[-1])
    history.git(history.origin, "reset", "-q", "--hard", base)
    history.commit("main rewritten after the merge event")

    completed, output = _run_shipped_enumeration(
        tmp_path, history, base_sha=base, merge_commit_sha=landed[-1], commit_count=3
    )

    assert completed.returncode != 0
    assert "not an ancestor of main" in completed.stdout
    assert _emitted(output) is None


def test_a_merge_commit_inside_the_window_is_refused(tmp_path: Path) -> None:
    """The enumerated window must be linear; a second parent means the walk
    would descend into main's own history."""
    history = _history(tmp_path)
    base = history.commit("root")
    history.git(history.origin, "checkout", "-q", "-b", "feature")
    history.commit("feature work")
    history.git(history.origin, "checkout", "-q", "main")
    history.commit("main work")
    history.git(history.origin, "merge", "-q", "--no-ff", "-m", "merge feature", "feature")
    tip = history.git(history.origin, "rev-parse", "HEAD")
    history.clone_origin()

    completed, output = _run_shipped_enumeration(
        tmp_path, history, base_sha=base, merge_commit_sha=tip, commit_count=3
    )

    assert completed.returncode != 0
    assert "::error::" in completed.stdout
    assert _emitted(output) is None


def test_an_overwritten_variable_publishes_an_empty_set(tmp_path: Path) -> None:
    """The reviewed defect (#847), executed rather than argued.

    The enumeration is untouched and correct; one assignment after it replaces
    the value. A validator tracking the variable *name* sees no difference. The
    dispatcher expands `fromJson("[]")` to zero matrix jobs, and zero jobs is a
    success -- so the workflow reports green having gated nothing.

    The mutation is applied to the extracted block, anchored on the shipped
    assignment rather than on a copy of it, and the complete-set assertion
    above is what tells the two apart.
    """
    shipped = _shipped_enumeration()
    payload_lines = [line for line in shipped.splitlines() if line.strip().startswith("payload=")]
    assert len(payload_lines) == 1, f"expected one payload assignment: {payload_lines}"
    overwritten = shipped.replace(payload_lines[0].strip(), 'payload="[]"')

    history = _history(tmp_path)
    base = history.commit("root")
    landed = [history.commit(f"this PR, revision {n}") for n in (1, 2, 3)]
    history.clone_origin()

    completed, output = _run_shipped_enumeration(
        tmp_path,
        history,
        base_sha=base,
        merge_commit_sha=landed[-1],
        commit_count=3,
        script=overwritten,
    )

    assert completed.returncode == 0, completed.stderr
    parsed = json.loads(_emitted(output) or "null")
    assert parsed == []
    assert parsed != landed, "only a value assertion distinguishes this from a correct run"


def test_the_jq_shim_matches_the_two_invocations_used(tmp_path: Path) -> None:
    """Pin the stand-in, so the harness is not validating against an unknown.

    When the real `jq` is present this asserts the real one. When it is absent
    the shim answers, and the expectation is identical either way -- which is
    the only thing that makes substituting it acceptable.
    """
    bin_dir = _toolchain(tmp_path)
    script_file = tmp_path / "jq_probe.sh"
    script_file.write_text('printf %s "one\ntwo" | jq -R . | jq -sc .\n', encoding="utf-8", newline="\n")
    environment = {
        **os.environ,
        "PATH": f"{bin_dir.as_posix()}{os.pathsep}{os.environ['PATH']}",
    }
    completed = subprocess.run(
        [_shipped_shell(), "--noprofile", "--norc", "-eo", "pipefail", script_file.as_posix()],
        env=environment,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == ["one", "two"]


def _dispatcher() -> str:
    return DISPATCHER.read_text(encoding="utf-8")


def test_the_window_is_the_merge_range_not_a_commit_count() -> None:
    """The estate permits two enumeration forms; this repository requires one.

    `validate_auto_merge_releasability.py` accepts both `rev-list -n
    "$COMMIT_COUNT"` and `rev-list --reverse "$BASE_SHA..$MERGE_COMMIT_SHA"`,
    so reverting this file to the count-bounded form passes every governed
    check -- measured, not assumed. Nothing else in the repository would notice.

    The count is not the window. `pull_request.commits` describes the branch
    when the event fired, not what landed, so a rebase that drops a commit
    already on main leaves the count larger than the window and the walk runs
    past this PR's history into commits earlier merges put there. Those are
    real ancestors of main and they really do number COMMIT_COUNT, so the
    ancestry guard and the count assertion both pass on a wrong enumeration.

    lotus-gateway hit this on its PR #744: count 3, two revisions landed, the
    walk reached base.sha, and because a commit is its own ancestor the guard
    refused the entire dispatch -- nothing was gated.
    """
    run = _dispatcher()

    assert 'git rev-list --reverse "$BASE_SHA..$MERGE_COMMIT_SHA"' in run
    assert 'rev-list -n "$COMMIT_COUNT"' not in run
    assert "BASE_SHA: ${{ github.event.pull_request.base.sha }}" in run


def test_a_count_mismatch_is_refused_upward_and_tolerated_downward() -> None:
    """The two directions mean opposite things and must not be treated alike.

    Fewer revisions than the count is a stale count over a complete window --
    everything that landed is still gated. More means the range spans revisions
    this PR did not add, and dispatching them stamps this PR's number onto
    another PR's commits. Refusing both would make ordinary rebases fail;
    tolerating both would let the over-claim through.
    """
    run = _dispatcher()

    assert '"$enumerated" -gt "$COMMIT_COUNT"' in run
    assert '"$enumerated" -lt "$COMMIT_COUNT"' in run
    upward = run.index('"$enumerated" -gt "$COMMIT_COUNT"')
    downward = run.index('"$enumerated" -lt "$COMMIT_COUNT"')
    assert "exit 1" in run[upward : upward + 400], "over-claiming must be refused"
    assert "::notice::" in run[downward : downward + 400], "a stale count must not fail"


def test_a_squashed_merge_cannot_claim_earlier_revisions() -> None:
    """Linearity and contiguity pass on a squash; reachability from base does not.

    A squash lands one commit while `pull_request.commits` still reports many,
    so the window picks up older main commits. Those are single-parent and
    perfectly contiguous -- every structural check accepts them. What separates
    them is that an earlier merge put them there, so they are reachable from
    the base, while a rebased commit never is however far main moved.
    """
    run = _dispatcher()

    assert 'git merge-base --is-ancestor "$revision" "$BASE_SHA"' in run
    assert 'git merge-base --is-ancestor "$revision" HEAD' in run
