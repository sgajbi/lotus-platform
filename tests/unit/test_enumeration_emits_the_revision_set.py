"""Execute the enumeration shell and read what it actually publishes.

The validator reads workflow YAML and reasons about it. That is necessary --
it must judge dispatchers it cannot run -- but it is not sufficient, because
every question it answers is about the *text* of a shell script. Reviewing
`#847` found the gap that shape leaves: a step could compute every revision,
overwrite the variable with `[]`, publish that, and satisfy a validator
tracking variable names.

So these tests run the enumeration with controlled inputs, capture the real
`GITHUB_OUTPUT`, and assert the emitted value is JSON holding exactly the
revisions the enumeration was given -- the set and the count, not merely that
something was written.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

# The revisions the stubbed `git rev-list` will return, newest first, which the
# enumeration reverses. Three, so a truncated result is distinguishable from a
# reordered one.
REVISIONS_NEWEST_FIRST = [
    "cccccccccccccccccccccccccccccccccccccccc",
    "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
]
EXPECTED_OLDEST_FIRST = list(reversed(REVISIONS_NEWEST_FIRST))

ENUMERATION = """
set -euo pipefail
merge_methods="$(gh api "repos/$GITHUB_REPOSITORY" --jq join)"
if [ "$merge_methods" != "false,false,true" ]; then exit 1; fi
revisions="$(git rev-list -n "$COMMIT_COUNT" "$MERGE_COMMIT_SHA" | tac)"
if [ -z "$revisions" ]; then exit 1; fi
payload="$(printf %s "$revisions" | jq -R . | jq -sc .)"
echo "list=$payload" >> "$GITHUB_OUTPUT"
"""

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


def _bash() -> str:
    executable = shutil.which("bash")
    if executable is None:  # pragma: no cover - environment guard
        pytest.fail("bash is required to execute the enumeration under test")
    return executable


def _toolchain(tmp_path: Path, revisions: list[str]) -> Path:
    """A PATH holding stubbed `git` and `gh`, and `jq` when the real one is absent."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()

    (bin_dir / "git").write_text(
        "#!/usr/bin/env bash\n"
        'if [ "$1" = "rev-list" ]; then\n'
        + "".join(f'  echo "{sha}"\n' for sha in revisions)
        + "  exit 0\nfi\nexit 0\n",
        encoding="utf-8",
    )
    (bin_dir / "gh").write_text(
        "#!/usr/bin/env bash\necho 'false,false,true'\n", encoding="utf-8"
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
        )
        (bin_dir / "jq.py").write_text(JQ_SHIM, encoding="utf-8")
    for path in bin_dir.iterdir():
        path.chmod(0o755)
    return bin_dir


def _run_enumeration(tmp_path: Path, script: str, revisions: list[str]):
    """Execute the enumeration and return (exit code, GITHUB_OUTPUT contents)."""
    bin_dir = _toolchain(tmp_path, revisions)
    output_file = tmp_path / "github_output"
    output_file.touch()
    environment = {
        **os.environ,
        "PATH": f"{bin_dir.as_posix()}{os.pathsep}{os.environ['PATH']}",
        "GITHUB_OUTPUT": output_file.as_posix(),
        "GITHUB_REPOSITORY": "sgajbi/lotus-platform",
        "COMMIT_COUNT": str(len(revisions)),
        "MERGE_COMMIT_SHA": revisions[0] if revisions else "",
    }
    completed = subprocess.run(
        [_bash(), "-c", textwrap.dedent(script)],
        env=environment,
        capture_output=True,
        text=True,
    )
    return completed, output_file.read_text(encoding="utf-8")


def _emitted(output: str, key: str = "list") -> str | None:
    for line in output.splitlines():
        name, separator, value = line.partition("=")
        if separator and name == key:
            return value
    return None


def test_enumeration_emits_json_with_the_complete_revision_set(tmp_path: Path) -> None:
    completed, output = _run_enumeration(tmp_path, ENUMERATION, REVISIONS_NEWEST_FIRST)

    assert completed.returncode == 0, completed.stderr
    emitted = _emitted(output)
    assert emitted is not None, f"nothing published under 'list': {output!r}"

    parsed = json.loads(emitted)
    assert isinstance(parsed, list), "fromJson requires an array, not raw lines"
    assert parsed == EXPECTED_OLDEST_FIRST
    assert len(parsed) == len(REVISIONS_NEWEST_FIRST)


def test_an_overwritten_variable_publishes_an_empty_set(tmp_path: Path) -> None:
    """The reviewed defect, executed rather than argued.

    The enumeration is untouched and correct; one assignment after it replaces
    the value. A validator tracking the variable *name* sees no difference. The
    dispatcher expands `fromJson("[]")` to zero matrix jobs, and zero jobs is a
    success -- so the workflow reports green having gated nothing.
    """
    overwritten = ENUMERATION.replace(
        'payload="$(printf %s "$revisions" | jq -R . | jq -sc .)"',
        'payload="[]"',
    )

    completed, output = _run_enumeration(tmp_path, overwritten, REVISIONS_NEWEST_FIRST)

    assert completed.returncode == 0
    assert json.loads(_emitted(output) or "null") == []


def test_a_truncated_enumeration_is_visible_in_the_emitted_count(tmp_path: Path) -> None:
    """Count is asserted separately from membership.

    A subset is valid JSON holding real revisions, so a membership-only check
    passes on it. This is the shape a paging bug produces.
    """
    completed, output = _run_enumeration(
        tmp_path, ENUMERATION, REVISIONS_NEWEST_FIRST[:2]
    )

    parsed = json.loads(_emitted(output) or "null")
    assert completed.returncode == 0
    assert len(parsed) == 2
    assert set(parsed) < set(EXPECTED_OLDEST_FIRST)


def test_an_empty_enumeration_fails_rather_than_publishing_nothing(tmp_path: Path) -> None:
    """The guard the validator requires, proven by running it."""
    completed, output = _run_enumeration(tmp_path, ENUMERATION, [])

    assert completed.returncode != 0
    assert _emitted(output) is None


def test_the_jq_shim_matches_the_two_invocations_used(tmp_path: Path) -> None:
    """Pin the stand-in, so the harness is not validating against an unknown.

    When the real `jq` is present this asserts the real one. When it is absent
    the shim answers, and the expectation is identical either way -- which is
    the only thing that makes substituting it acceptable.
    """
    bin_dir = _toolchain(tmp_path, REVISIONS_NEWEST_FIRST)
    environment = {
        **os.environ,
        "PATH": f"{bin_dir.as_posix()}{os.pathsep}{os.environ['PATH']}",
    }
    completed = subprocess.run(
        [_bash(), "-c", 'printf %s "one\ntwo" | jq -R . | jq -sc .'],
        env=environment,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == ["one", "two"]


DISPATCHER = ROOT / ".github" / "workflows" / "merged-pr-main-releasability.yml"


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
