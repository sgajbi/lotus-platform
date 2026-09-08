from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from automation import validate_auto_merge_releasability as validator
from automation.validate_auto_merge_releasability import validate_repositories


def _write_policy(path: Path, repositories: list[str]) -> None:
    path.write_text(
        json.dumps(
            {
                "repos": [
                    {
                        "name": repository,
                        "default_branch": "main",
                        "required_checks": [],
                    }
                    for repository in repositories
                ]
            }
        ),
        encoding="utf-8",
    )


def _write_exceptions(path: Path, exceptions: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": "lotus.auto-merge-releasability-exceptions.v1",
                "exceptions": exceptions,
            }
        ),
        encoding="utf-8",
    )


def _write_aligned_workflows(repo_root: Path) -> None:
    workflow_dir = repo_root / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    (workflow_dir / "pr-auto-merge.yml").write_text(
        """
name: PR Auto Merge
on:
  pull_request_target:
    types: [opened, ready_for_review]
permissions:
  contents: read
jobs:
  queue:
    runs-on: ubuntu-latest
    steps:
      - env:
          GH_TOKEN: ${{ secrets.LOTUS_AUTOMERGE_TOKEN }}
        run: gh pr merge "$PR_NUMBER" --repo "$GITHUB_REPOSITORY" --auto --rebase --delete-branch
""",
        encoding="utf-8",
    )
    (workflow_dir / "merged-pr-main-releasability.yml").write_text(
        """
name: Merged PR Main Releasability Dispatch
on:
  pull_request_target:
    types: [closed]
permissions:
  actions: write
  contents: write
jobs:
  dispatch:
    runs-on: ubuntu-latest
    steps:
      - env:
          MERGE_COMMIT_SHA: ${{ github.event.pull_request.merge_commit_sha }}
        run: |
          dispatch_ref="main-releasability-${MERGE_COMMIT_SHA}"
          existing_ref_sha=""
          if existing_ref_sha="$(gh api "repos/$GITHUB_REPOSITORY/git/ref/tags/$dispatch_ref" --jq .object.sha 2>/dev/null)"; then
            if [ "$existing_ref_sha" != "$MERGE_COMMIT_SHA" ]; then
              exit 1
            fi
          else
            existing_ref_sha=""
          fi
          if [ -z "$existing_ref_sha" ]; then
            gh api "repos/$GITHUB_REPOSITORY/git/refs" -f ref="refs/tags/$dispatch_ref" -f sha="$MERGE_COMMIT_SHA"
          fi
          gh workflow run main-releasability.yml \\
            --repo "$GITHUB_REPOSITORY" \\
            --ref "$dispatch_ref" \\
            -f expected_sha="$MERGE_COMMIT_SHA"
""",
        encoding="utf-8",
    )
    (workflow_dir / "main-releasability.yml").write_text(
        """
name: Main Releasability Gate
on:
  workflow_dispatch:
    inputs:
      expected_sha:
        required: false
        type: string
permissions:
  contents: read
concurrency:
  group: ${{ github.workflow }}-${{ github.sha }}
  cancel-in-progress: true
jobs:
  exact-revision-assertion:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - env:
          EXPECTED_SHA: ${{ inputs.expected_sha }}
        run: |
          actual_sha="$(git rev-parse HEAD)"
          if [ -z "$EXPECTED_SHA" ]; then
            exit 0
          fi
          if [ "$actual_sha" != "$EXPECTED_SHA" ]; then
            exit 1
          fi
""",
        encoding="utf-8",
    )


def _write_per_revision_dispatch(repo_root: Path) -> Path:
    workflow_path = (
        repo_root / ".github" / "workflows" / "merged-pr-main-releasability.yml"
    )
    workflow_path.write_text(
        """
name: Merged PR Main Releasability Dispatch
on:
  pull_request_target:
    types: [closed]
permissions:
  actions: write
  contents: write
jobs:
  dispatch:
    runs-on: ubuntu-latest
    steps:
      - env:
          MERGE_COMMIT_SHA: ${{ github.event.pull_request.merge_commit_sha }}
          COMMIT_COUNT: ${{ github.event.pull_request.commits }}
        run: |
          revisions="$(git rev-list -n "$COMMIT_COUNT" "$MERGE_COMMIT_SHA" | tac)"
          for revision in $revisions; do
            if ! git merge-base --is-ancestor "$revision" HEAD; then
              exit 1
            fi
            dispatch_ref="main-releasability-${revision}"
            existing_ref_sha=""
            if existing_ref_sha="$(gh api "repos/$GITHUB_REPOSITORY/git/ref/tags/$dispatch_ref" --jq .object.sha 2>/dev/null)"; then
              if [ "$existing_ref_sha" != "$revision" ]; then
                exit 1
              fi
            else
              existing_ref_sha=""
            fi
            if [ -z "$existing_ref_sha" ]; then
              gh api "repos/$GITHUB_REPOSITORY/git/refs" -f ref="refs/tags/$dispatch_ref" -f sha="$revision"
            fi
            gh workflow run main-releasability.yml \\
              --repo "$GITHUB_REPOSITORY" \\
              --ref "$dispatch_ref" \\
              -f expected_sha="$revision"
          done
""",
        encoding="utf-8",
    )
    return workflow_path


def test_auto_merge_releasability_accepts_aligned_repository(tmp_path: Path) -> None:
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    _write_policy(policy, ["lotus-example"])
    _write_exceptions(exceptions, [])
    _write_aligned_workflows(repo_root)

    results = validate_repositories(
        policy_path=policy,
        exception_path=exceptions,
        repos_root=repos_root,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert results[0].status == "aligned"
    assert results[0].violations == ()


def test_auto_merge_releasability_accepts_exact_per_revision_rebase_dispatch(
    tmp_path: Path,
) -> None:
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    _write_policy(policy, ["lotus-example"])
    _write_exceptions(exceptions, [])
    _write_aligned_workflows(repo_root)
    _write_per_revision_dispatch(repo_root)

    results = validate_repositories(
        policy_path=policy,
        exception_path=exceptions,
        repos_root=repos_root,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert results[0].status == "aligned"
    assert results[0].violations == ()


def test_auto_merge_releasability_rejects_unbound_per_revision_dispatch(
    tmp_path: Path,
) -> None:
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    _write_policy(policy, ["lotus-example"])
    _write_exceptions(exceptions, [])
    _write_aligned_workflows(repo_root)
    workflow_path = _write_per_revision_dispatch(repo_root)
    workflow_path.write_text(
        workflow_path.read_text(encoding="utf-8").replace(
            'revisions="$(git rev-list -n "$COMMIT_COUNT" "$MERGE_COMMIT_SHA" | tac)"',
            'revisions="$(git rev-list origin/main)"',
        ),
        encoding="utf-8",
    )

    results = validate_repositories(
        policy_path=policy,
        exception_path=exceptions,
        repos_root=repos_root,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert results[0].status == "drift"
    assert results[0].violations == (
        "merged-pr-dispatch.missing-expected-sha-input",
        "merged-pr-dispatch.wrong-main-releasability-target",
    )


def test_auto_merge_releasability_rejects_per_revision_dispatch_without_ancestry_proof(
    tmp_path: Path,
) -> None:
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    _write_policy(policy, ["lotus-example"])
    _write_exceptions(exceptions, [])
    _write_aligned_workflows(repo_root)
    workflow_path = _write_per_revision_dispatch(repo_root)
    workflow_path.write_text(
        workflow_path.read_text(encoding="utf-8").replace(
            'git merge-base --is-ancestor "$revision" HEAD',
            'git rev-parse "$revision"',
        ),
        encoding="utf-8",
    )

    results = validate_repositories(
        policy_path=policy,
        exception_path=exceptions,
        repos_root=repos_root,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert results[0].status == "drift"
    assert results[0].violations == (
        "merged-pr-dispatch.missing-expected-sha-input",
        "merged-pr-dispatch.wrong-main-releasability-target",
    )


def test_auto_merge_releasability_accepts_checked_out_revision_fallback(
    tmp_path: Path,
) -> None:
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    _write_policy(policy, ["lotus-example"])
    _write_exceptions(exceptions, [])
    _write_aligned_workflows(repo_root)
    workflow_path = repo_root / ".github" / "workflows" / "main-releasability.yml"
    workflow_path.write_text(
        workflow_path.read_text(encoding="utf-8").replace(
            "${{ github.sha }}",
            "${{ inputs.expected_sha || github.sha }}",
        ),
        encoding="utf-8",
    )

    results = validate_repositories(
        policy_path=policy,
        exception_path=exceptions,
        repos_root=repos_root,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert results[0].status == "aligned"
    assert results[0].violations == ()


def test_auto_merge_releasability_rejects_duplicate_main_releasability_automatic_trigger(
    tmp_path: Path,
) -> None:
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    _write_policy(policy, ["lotus-example"])
    _write_exceptions(exceptions, [])
    _write_aligned_workflows(repo_root)
    (repo_root / ".github" / "workflows" / "main-releasability.yml").write_text(
        """
name: Main Releasability Gate
on:
  workflow_dispatch:
  push:
    branches: [main]
permissions:
  contents: read
""",
        encoding="utf-8",
    )

    results = validate_repositories(
        policy_path=policy,
        exception_path=exceptions,
        repos_root=repos_root,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert results[0].status == "drift"
    assert results[0].violations == (
        "main-releasability.duplicate-automatic-trigger",
        "main-releasability.missing-expected-sha-assertion",
        "main-releasability.missing-revision-aware-concurrency",
    )


def test_auto_merge_releasability_rejects_legacy_unpinned_dispatch(
    tmp_path: Path,
) -> None:
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    _write_policy(policy, ["lotus-example"])
    _write_exceptions(exceptions, [])
    _write_aligned_workflows(repo_root)
    (
        repo_root / ".github" / "workflows" / "merged-pr-main-releasability.yml"
    ).write_text(
        """
name: Merged PR Main Releasability Dispatch
on:
  pull_request_target:
    types: [closed]
permissions:
  actions: write
  contents: write
jobs:
  dispatch:
    runs-on: ubuntu-latest
    steps:
      - run: gh workflow run main-releasability.yml --repo "$GITHUB_REPOSITORY" --ref main
""",
        encoding="utf-8",
    )

    results = validate_repositories(
        policy_path=policy,
        exception_path=exceptions,
        repos_root=repos_root,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert results[0].status == "drift"
    assert results[0].violations == (
        "merged-pr-dispatch.missing-expected-sha-input",
        "merged-pr-dispatch.wrong-main-releasability-target",
    )


def test_auto_merge_releasability_rejects_branch_ref_dispatch_even_with_expected_sha(
    tmp_path: Path,
) -> None:
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    _write_policy(policy, ["lotus-example"])
    _write_exceptions(exceptions, [])
    _write_aligned_workflows(repo_root)
    (
        repo_root / ".github" / "workflows" / "merged-pr-main-releasability.yml"
    ).write_text(
        """
name: Merged PR Main Releasability Dispatch
on:
  pull_request_target:
    types: [closed]
permissions:
  actions: write
  contents: read
jobs:
  dispatch:
    runs-on: ubuntu-latest
    steps:
      - env:
          MERGE_COMMIT_SHA: ${{ github.event.pull_request.merge_commit_sha }}
        run: gh workflow run main-releasability.yml --repo "$GITHUB_REPOSITORY" --ref main -f expected_sha="$MERGE_COMMIT_SHA"
""",
        encoding="utf-8",
    )

    results = validate_repositories(
        policy_path=policy,
        exception_path=exceptions,
        repos_root=repos_root,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert results[0].status == "drift"
    assert results[0].violations == (
        "merged-pr-dispatch.missing-contents-write",
        "merged-pr-dispatch.wrong-main-releasability-target",
    )


def test_auto_merge_releasability_rejects_head_sha_dispatched_as_expected_sha(
    tmp_path: Path,
) -> None:
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    _write_policy(policy, ["lotus-example"])
    _write_exceptions(exceptions, [])
    _write_aligned_workflows(repo_root)
    workflow_path = (
        repo_root / ".github" / "workflows" / "merged-pr-main-releasability.yml"
    )
    workflow_path.write_text(
        workflow_path.read_text(encoding="utf-8").replace(
            '-f expected_sha="$MERGE_COMMIT_SHA"',
            '-f expected_sha="${{ github.event.pull_request.head.sha }}"',
        ),
        encoding="utf-8",
    )

    results = validate_repositories(
        policy_path=policy,
        exception_path=exceptions,
        repos_root=repos_root,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert results[0].status == "drift"
    assert results[0].violations == ("merged-pr-dispatch.missing-expected-sha-input",)


def test_auto_merge_releasability_rejects_masked_immutable_ref_lookup(
    tmp_path: Path,
) -> None:
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    _write_policy(policy, ["lotus-example"])
    _write_exceptions(exceptions, [])
    _write_aligned_workflows(repo_root)
    workflow_path = (
        repo_root / ".github" / "workflows" / "merged-pr-main-releasability.yml"
    )
    workflow_path.write_text(
        workflow_path.read_text(encoding="utf-8").replace(
            '2>/dev/null)"; then',
            '2>/dev/null || true)"; then',
        ),
        encoding="utf-8",
    )

    results = validate_repositories(
        policy_path=policy,
        exception_path=exceptions,
        repos_root=repos_root,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert results[0].status == "drift"
    assert results[0].violations == ("merged-pr-dispatch.masked-immutable-ref-lookup",)


def test_a_mask_split_after_a_pipeline_operator_is_still_a_mask(
    tmp_path: Path,
) -> None:
    """A split after `|` is a third encoding of the same masked command.

    Bash treats the two lines as one pipeline. Backslash rejoining does not
    apply and YAML folding is not involved, so both earlier fixes miss it --
    and the original whole-file check caught it, which is what made the
    line-scoped version a regression rather than a refinement.

    Scoping to the step ends the sequence: however a command is wrapped, both
    halves remain inside the step that runs it.
    """
    from automation.validate_auto_merge_releasability import (
        _masks_the_immutable_ref_lookup,
    )

    piped = (
        'gh api "repos/$GITHUB_REPOSITORY/git/ref/tags/$dispatch_ref" |'
        + chr(10)
        + 'jq .object.sha || true'
    )
    payload = {
        "jobs": {"dispatch": {"steps": [{"run": piped}]}}
    }

    assert _masks_the_immutable_ref_lookup("", payload)

def test_a_mask_folded_by_yaml_is_still_a_mask(tmp_path: Path) -> None:
    """A folded scalar joins the lines before the shell ever sees them.

    `_logical_lines` rejoins backslash continuations, which is the opposite
    problem: with `run: >` the lookup and its `|| true` sit on separate YAML
    lines that YAML folds into ONE shell command, so the raw text never shows
    them together while the shell runs them together.

    Reading the parsed step command resolves the folding first. Found in
    review of the continuation fix, which is what made the raw-text scan look
    sufficient.
    """
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    _write_policy(policy, ["lotus-example"])
    _write_exceptions(exceptions, [])
    _write_aligned_workflows(repo_root)
    workflow_path = (
        repo_root / ".github" / "workflows" / "merged-pr-main-releasability.yml"
    )
    original = workflow_path.read_text(encoding="utf-8")
    needle = '2>/dev/null)"; then'
    assert needle in original, "fixture no longer contains the lookup tail"
    # A folded step whose two YAML lines become one shell command.
    folded = original.replace(
        needle,
        '2>/dev/null)"; then'
        + chr(10)
        + '          # yaml-folded continuation follows',
        1,
    )
    assert folded != original, "fixture was not modified"
    folded = folded.replace(
        "        run: |",
        "        run: >" + chr(10) + "          ",
        1,
    )
    workflow_path.write_text(folded, encoding="utf-8")

    # The assertion is about the helper, not this particular fixture: the
    # parsed command must be what is scanned.
    from automation.validate_auto_merge_releasability import (
        _masks_the_immutable_ref_lookup,
        _load_yaml,
    )

    masked_text = (
        'gh api "repos/$GITHUB_REPOSITORY/git/ref/tags/$dispatch_ref"'
        + chr(10)
        + '--jq .object.sha || true'
    )
    payload = {
        "jobs": {
            "dispatch": {
                "steps": [
                    {"name": "Dispatch main releasability gate",
                     "run": masked_text.replace(chr(10), " ")},
                ]
            }
        }
    }

    assert _masks_the_immutable_ref_lookup("unrelated raw text", payload)
    assert not _masks_the_immutable_ref_lookup(
        "unrelated raw text", {"jobs": {}}
    )

def test_a_mask_split_across_a_continuation_is_still_a_mask(
    tmp_path: Path,
) -> None:
    """A backslash continuation must not hide the mask from the check.

    Scoping the check to physical lines fixed one defect and introduced its
    mirror, which review of that same change caught: with the lookup wrapped
    across a continuation, no physical line holds both the command and its
    tolerated failure, while the command is masked exactly as before.

    The unit under test is the shell command, not the line the author
    happened to wrap it on.
    """
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    _write_policy(policy, ["lotus-example"])
    _write_exceptions(exceptions, [])
    _write_aligned_workflows(repo_root)
    workflow_path = (
        repo_root / ".github" / "workflows" / "merged-pr-main-releasability.yml"
    )
    original = workflow_path.read_text(encoding="utf-8")
    needle = '2>/dev/null)"; then'
    assert needle in original, "fixture no longer contains the lookup tail"
    continuation = chr(92)
    wrapped = (
        continuation
        + chr(10)
        + '            2>/dev/null || true)"; then'
    )
    split = original.replace(needle, wrapped, 1)
    assert split != original, "fixture was not modified"
    workflow_path.write_text(split, encoding="utf-8")

    results = validate_repositories(
        policy_path=policy,
        exception_path=exceptions,
        repos_root=repos_root,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert (
        "merged-pr-dispatch.masked-immutable-ref-lookup" in results[0].violations
    )

def test_an_unrelated_tolerated_command_is_not_a_masked_lookup(
    tmp_path: Path,
) -> None:
    """`|| true` elsewhere in the file is not a masked dispatch-ref lookup.

    The check used to ask whether the file contained the lookup path anywhere
    and `|| true` anywhere -- two independent substrings, so any tolerated
    command in the workflow implicated a lookup it had not touched.

    This is the shape that actually occurred. `lotus-manage` adopted the range
    enumeration this repository recommended and added a defensive
    `git fetch origin --quiet "$BASE_SHA" || true` in its enumeration job, while
    the lookup lives in its dispatch job; the validator reported it as masking,
    and that blocked an unrelated platform pull request. A check that flags the
    fix it asked for teaches operators to read its findings as noise, which
    costs more than the finding was worth.

    The separation is the point. A tolerated failure in the step that performs
    the lookup IS suspicious, however it is laid out, and is asserted elsewhere.

    The genuine case is asserted directly above and must keep failing: the two
    together are what make this a scope fix rather than a weakening.
    """
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    _write_policy(policy, ["lotus-example"])
    _write_exceptions(exceptions, [])
    _write_aligned_workflows(repo_root)
    workflow_path = (
        repo_root / ".github" / "workflows" / "merged-pr-main-releasability.yml"
    )
    original = workflow_path.read_text(encoding="utf-8")
    # The tolerated command goes in a SEPARATE step, which is where the real one
    # was: lotus-manage put `git fetch ... || true` in its enumeration job and
    # the lookup in its dispatch job. Placing both in one step would model a
    # different situation -- a tolerated failure sitting beside the lookup that
    # runs it -- which the step-scoped check flags, correctly.
    anchor = "    steps:\n"
    separate_step = (
        "    steps:\n"
        "      - name: Enumerate merged revisions\n"
        "        run: |\n"
        '          git fetch origin --quiet "$BASE_SHA" || true\n'
        '          revisions="$(git rev-list --reverse "$BASE_SHA..$MERGE_COMMIT_SHA")"\n'
    )
    mutated = original.replace(anchor, separate_step, 1)
    # Assert the fixture actually changed. A `replace` that matches nothing
    # leaves a workflow with no `|| true` at all, and the assertion below then
    # passes under any check -- a test that cannot fail.
    assert mutated != original, "fixture anchor did not match"
    assert "|| true" in mutated
    workflow_path.write_text(mutated, encoding="utf-8")

    results = validate_repositories(
        policy_path=policy,
        exception_path=exceptions,
        repos_root=repos_root,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert "merged-pr-dispatch.masked-immutable-ref-lookup" not in results[0].violations


def test_auto_merge_releasability_rejects_dispatch_without_main_assertion(
    tmp_path: Path,
) -> None:
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    _write_policy(policy, ["lotus-example"])
    _write_exceptions(exceptions, [])
    _write_aligned_workflows(repo_root)
    (repo_root / ".github" / "workflows" / "main-releasability.yml").write_text(
        """
name: Main Releasability Gate
on:
  workflow_dispatch:
permissions:
  contents: read
concurrency:
  group: ${{ github.workflow }}-${{ github.sha }}
  cancel-in-progress: true
""",
        encoding="utf-8",
    )

    results = validate_repositories(
        policy_path=policy,
        exception_path=exceptions,
        repos_root=repos_root,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert results[0].status == "drift"
    assert results[0].violations == (
        "main-releasability.missing-expected-sha-assertion",
    )


def test_auto_merge_releasability_rejects_assertion_without_mismatch_exit(
    tmp_path: Path,
) -> None:
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    _write_policy(policy, ["lotus-example"])
    _write_exceptions(exceptions, [])
    _write_aligned_workflows(repo_root)
    workflow_path = repo_root / ".github" / "workflows" / "main-releasability.yml"
    workflow_path.write_text(
        workflow_path.read_text(encoding="utf-8").replace(
            'if [ "$actual_sha" != "$EXPECTED_SHA" ]; then\n            exit 1\n          fi',
            'echo "if [ "$actual_sha" != "$EXPECTED_SHA" ]; then exit 1"',
        ),
        encoding="utf-8",
    )

    results = validate_repositories(
        policy_path=policy,
        exception_path=exceptions,
        repos_root=repos_root,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert results[0].status == "drift"
    assert results[0].violations == (
        "main-releasability.missing-expected-sha-assertion",
    )


def test_auto_merge_releasability_rejects_sha_insensitive_main_concurrency(
    tmp_path: Path,
) -> None:
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    _write_policy(policy, ["lotus-example"])
    _write_exceptions(exceptions, [])
    _write_aligned_workflows(repo_root)
    workflow_path = repo_root / ".github" / "workflows" / "main-releasability.yml"
    workflow_path.write_text(
        workflow_path.read_text(encoding="utf-8").replace(
            "${{ github.sha }}",
            "${{ github.ref }}",
        ),
        encoding="utf-8",
    )

    results = validate_repositories(
        policy_path=policy,
        exception_path=exceptions,
        repos_root=repos_root,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert results[0].status == "drift"
    assert results[0].violations == (
        "main-releasability.missing-revision-aware-concurrency",
    )


def test_auto_merge_releasability_rejects_literal_sha_text_in_main_concurrency(
    tmp_path: Path,
) -> None:
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    _write_policy(policy, ["lotus-example"])
    _write_exceptions(exceptions, [])
    _write_aligned_workflows(repo_root)
    workflow_path = repo_root / ".github" / "workflows" / "main-releasability.yml"
    workflow_path.write_text(
        workflow_path.read_text(encoding="utf-8").replace(
            "${{ github.sha }}",
            "release-github.sha",
        ),
        encoding="utf-8",
    )

    results = validate_repositories(
        policy_path=policy,
        exception_path=exceptions,
        repos_root=repos_root,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert results[0].status == "drift"
    assert results[0].violations == (
        "main-releasability.missing-revision-aware-concurrency",
    )


def test_auto_merge_releasability_rejects_quoted_sha_literal_expression(
    tmp_path: Path,
) -> None:
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    _write_policy(policy, ["lotus-example"])
    _write_exceptions(exceptions, [])
    _write_aligned_workflows(repo_root)
    workflow_path = repo_root / ".github" / "workflows" / "main-releasability.yml"
    workflow_path.write_text(
        workflow_path.read_text(encoding="utf-8").replace(
            "${{ github.sha }}",
            "${{ 'github.sha' }}",
        ),
        encoding="utf-8",
    )

    results = validate_repositories(
        policy_path=policy,
        exception_path=exceptions,
        repos_root=repos_root,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert results[0].status == "drift"
    assert results[0].violations == (
        "main-releasability.missing-revision-aware-concurrency",
    )


def test_auto_merge_releasability_rejects_non_value_preserving_sha_expressions(
    tmp_path: Path,
) -> None:
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    _write_policy(policy, ["lotus-example"])
    _write_exceptions(exceptions, [])
    _write_aligned_workflows(repo_root)
    workflow_path = repo_root / ".github" / "workflows" / "main-releasability.yml"
    aligned_workflow = workflow_path.read_text(encoding="utf-8")

    for expression in (
        "${{ 'release' || github.sha }}",
        "${{ github.sha == 'never' }}",
        "${{ format('{0}', github.sha) }}",
    ):
        workflow_path.write_text(
            aligned_workflow.replace(
                "${{ github.sha }}",
                expression,
            ),
            encoding="utf-8",
        )

        results = validate_repositories(
            policy_path=policy,
            exception_path=exceptions,
            repos_root=repos_root,
            today=datetime(2026, 7, 14, tzinfo=UTC),
        )

        assert results[0].status == "drift", expression
        assert results[0].violations == (
            "main-releasability.missing-revision-aware-concurrency",
        ), expression


def test_auto_merge_releasability_fails_undeclared_drift(tmp_path: Path) -> None:
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    _write_policy(policy, ["lotus-example"])
    _write_exceptions(exceptions, [])
    _write_aligned_workflows(repo_root)
    (repo_root / ".github" / "workflows" / "merged-pr-main-releasability.yml").unlink()

    results = validate_repositories(
        policy_path=policy,
        exception_path=exceptions,
        repos_root=repos_root,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert results[0].status == "drift"
    assert results[0].violations == ("merged-pr-dispatch.missing",)


def test_auto_merge_releasability_accepts_exact_unexpired_exception(
    tmp_path: Path,
) -> None:
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    _write_policy(policy, ["lotus-example"])
    _write_aligned_workflows(repo_root)
    (repo_root / ".github" / "workflows" / "merged-pr-main-releasability.yml").unlink()
    _write_exceptions(
        exceptions,
        [
            {
                "repository": "lotus-example",
                "owner": "platform-ci-governance",
                "expires_on_utc": "2026-08-14T00:00:00Z",
                "reason": "Temporary rollout gap.",
                "violations": ["merged-pr-dispatch.missing"],
            }
        ],
    )

    results = validate_repositories(
        policy_path=policy,
        exception_path=exceptions,
        repos_root=repos_root,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert results[0].status == "excepted"
    assert results[0].exception_owner == "platform-ci-governance"


def test_auto_merge_releasability_rejects_expired_exception(tmp_path: Path) -> None:
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    _write_policy(policy, ["lotus-example"])
    _write_aligned_workflows(repo_root)
    (repo_root / ".github" / "workflows" / "merged-pr-main-releasability.yml").unlink()
    _write_exceptions(
        exceptions,
        [
            {
                "repository": "lotus-example",
                "owner": "platform-ci-governance",
                "expires_on_utc": "2026-07-01T00:00:00Z",
                "reason": "Expired rollout gap.",
                "violations": ["merged-pr-dispatch.missing"],
            }
        ],
    )

    results = validate_repositories(
        policy_path=policy,
        exception_path=exceptions,
        repos_root=repos_root,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert results[0].status == "drift"
    assert results[0].exception_owner is None


def test_auto_merge_releasability_can_skip_or_require_missing_local_repos(
    tmp_path: Path,
) -> None:
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    _write_policy(policy, ["lotus-example"])
    _write_exceptions(exceptions, [])

    skipped = validate_repositories(
        policy_path=policy,
        exception_path=exceptions,
        repos_root=tmp_path / "missing",
        require_local_repos=False,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )
    required = validate_repositories(
        policy_path=policy,
        exception_path=exceptions,
        repos_root=tmp_path / "missing",
        require_local_repos=True,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert skipped[0].status == "missing-local-repo"
    assert skipped[0].violations == ()
    assert required[0].status == "drift"
    assert required[0].violations == ("repository-root.missing",)


def test_auto_merge_releasability_rejects_scalar_write_all_permissions(
    tmp_path: Path,
) -> None:
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    _write_policy(policy, ["lotus-example"])
    _write_exceptions(exceptions, [])
    _write_aligned_workflows(repo_root)
    (repo_root / ".github" / "workflows" / "pr-auto-merge.yml").write_text(
        """
name: PR Auto Merge
on:
  pull_request_target:
    types: [opened, ready_for_review]
permissions: write-all
jobs:
  queue:
    runs-on: ubuntu-latest
    steps:
      - env:
          GH_TOKEN: ${{ secrets.LOTUS_AUTOMERGE_TOKEN }}
        run: gh pr merge "$PR_NUMBER" --repo "$GITHUB_REPOSITORY" --auto --rebase --delete-branch
""",
        encoding="utf-8",
    )

    results = validate_repositories(
        policy_path=policy,
        exception_path=exceptions,
        repos_root=repos_root,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert results[0].status == "drift"
    assert "pr-auto-merge.write-permissions" in results[0].violations


def _write_matrix_enumeration_dispatch(
    repo_root: Path,
    *,
    assert_merge_settings: bool = True,
    main_only_condition: bool = True,
    matrix_fed_from_enumeration: bool = True,
    paginated_enumeration: bool = True,
) -> Path:
    workflow_path = (
        repo_root / ".github" / "workflows" / "merged-pr-main-releasability.yml"
    )
    merge_settings_assertion = (
        """
          merge_settings="$(gh api "repos/$GITHUB_REPOSITORY" --jq '[.allow_squash_merge, .allow_merge_commit, .allow_rebase_merge] | join(",")')"
          if [ "$merge_settings" != "false,false,true" ]; then
            exit 1
          fi
"""
        if assert_merge_settings
        else ""
    )
    condition = (
        """
    if: >
      github.event.pull_request.merged == true &&
      github.event.pull_request.base.ref == 'main'
"""
        if main_only_condition
        else ""
    )
    matrix_source = (
        "${{ fromJSON(needs.enumerate-merged-commits.outputs.commit_shas) }}"
        if matrix_fed_from_enumeration
        else '["deadbeef"]'
    )
    commits_query = (
        "commits?sha=$MERGE_COMMIT_SHA&per_page=$PR_COMMIT_COUNT"
        if paginated_enumeration
        else "commits?sha=$MERGE_COMMIT_SHA"
    )
    workflow_path.write_text(
        f"""
name: Merged PR Main Releasability Dispatch
on:
  pull_request_target:
    types: [closed]
permissions:
  actions: write
  contents: write
jobs:
  enumerate-merged-commits:
{condition}
    runs-on: ubuntu-latest
    outputs:
      commit_shas: ${{{{ steps.enumerate.outputs.commit_shas }}}}
    steps:
      - id: enumerate
        env:
          MERGE_COMMIT_SHA: ${{{{ github.event.pull_request.merge_commit_sha }}}}
          PR_COMMIT_COUNT: ${{{{ github.event.pull_request.commits }}}}
        run: |
{merge_settings_assertion}
          commit_shas="$(gh api "repos/$GITHUB_REPOSITORY/{commits_query}" --jq '[.[].sha]')"
          resolved_count="$(printf '%s' "$commit_shas" | jq 'length')"
          if [ "$resolved_count" -ne "$PR_COMMIT_COUNT" ]; then
            exit 1
          fi
          echo "commit_shas=$commit_shas" >> "$GITHUB_OUTPUT"
  dispatch-main-releasability:
    needs: enumerate-merged-commits
    runs-on: ubuntu-latest
    strategy:
      matrix:
        commit_sha: {matrix_source}
    steps:
      - env:
          MERGE_COMMIT_SHA: ${{{{ matrix.commit_sha }}}}
        run: |
          dispatch_ref="main-releasability-${{MERGE_COMMIT_SHA}}"
          if existing_ref_sha="$(gh api "repos/$GITHUB_REPOSITORY/git/ref/tags/$dispatch_ref" --jq .object.sha 2>/dev/null)"; then
            if [ "$existing_ref_sha" != "$MERGE_COMMIT_SHA" ]; then
              exit 1
            fi
          else
            gh api "repos/$GITHUB_REPOSITORY/git/refs" -f ref="refs/tags/$dispatch_ref" -f sha="$MERGE_COMMIT_SHA"
          fi
          gh workflow run main-releasability.yml \
            --repo "$GITHUB_REPOSITORY" \
            --ref "$dispatch_ref" \
            -f expected_sha="$MERGE_COMMIT_SHA"
""",
        encoding="utf-8",
    )
    return workflow_path


def test_auto_merge_releasability_accepts_verified_matrix_enumeration_dispatch(
    tmp_path: Path,
) -> None:
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    _write_policy(policy, ["lotus-example"])
    _write_exceptions(exceptions, [])
    _write_aligned_workflows(repo_root)
    _write_matrix_enumeration_dispatch(repo_root)

    results = validate_repositories(
        policy_path=policy,
        exception_path=exceptions,
        repos_root=repos_root,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert results[0].status == "aligned"
    assert results[0].violations == ()


@pytest.mark.parametrize(
    "weakness",
    [
        # No rebase-only assertion: squash/merge-commit settings would make the
        # enumeration walk the wrong trees.
        {"assert_merge_settings": False},
        # No main-only condition: a PR merged to a release or feature branch
        # could dispatch and certify commits that never reached main.
        {"main_only_condition": False},
        # Matrix not fed from the verified enumeration output: a hard-coded or
        # disconnected matrix could dispatch arbitrary revisions.
        {"matrix_fed_from_enumeration": False},
        # No explicit page size covering the whole PR: the commits endpoint
        # returns one default page and larger PRs would be silently truncated
        # before the count equality can fail closed.
        {"paginated_enumeration": False},
    ],
)
def test_auto_merge_releasability_rejects_unverified_matrix_dispatch(
    tmp_path: Path, weakness: dict
) -> None:
    policy = tmp_path / "policy.json"
    exceptions = tmp_path / "exceptions.json"
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    _write_policy(policy, ["lotus-example"])
    _write_exceptions(exceptions, [])
    _write_aligned_workflows(repo_root)
    _write_matrix_enumeration_dispatch(repo_root, **weakness)

    results = validate_repositories(
        policy_path=policy,
        exception_path=exceptions,
        repos_root=repos_root,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert "merged-pr-dispatch.missing-expected-sha-input" in results[0].violations


# --- Revision enumeration: two forms, one meaning ----------------------------

_DISPATCH_BY_RANGE = """\
name: Merged PR Main Releasability
on:
  pull_request_target:
    types: [closed]
permissions:
  actions: write
  contents: write
jobs:
  dispatch:
    runs-on: ubuntu-latest
    steps:
      - name: Dispatch
        env:
          MERGE_COMMIT_SHA: ${{ github.event.pull_request.merge_commit_sha }}
          BASE_SHA: ${{ github.event.pull_request.base.sha }}
        run: |
          revisions="$(git rev-list --reverse "$BASE_SHA..$MERGE_COMMIT_SHA")"
          for revision in $revisions; do
            git merge-base --is-ancestor "$revision" HEAD
            dispatch_ref="main-releasability-${revision}"
            gh api "repos/$GITHUB_REPOSITORY/git/ref/tags/$dispatch_ref"
            gh api "repos/$GITHUB_REPOSITORY/git/refs" -f sha="$revision"
            gh workflow run main-releasability.yml --ref "$dispatch_ref" -f expected_sha="$revision"
          done
"""


def _dispatch_file(tmp_path: Path, text: str) -> Path:
    workflow = tmp_path / "merged-pr-main-releasability.yml"
    workflow.write_text(text, encoding="utf-8")
    return workflow


def test_enumeration_by_range_is_accepted(tmp_path: Path) -> None:
    """`rev-list --reverse "$BASE_SHA..$MERGE_COMMIT_SHA"` names the same revisions.

    It is the stronger of the two forms: a commit count taken from the pull
    request can be wrong after a rebase, while the range is derived from the
    merge itself. Recognising only the count form reported a defect against a
    repository that had improved its dispatcher.
    """
    workflow = _dispatch_file(tmp_path, _DISPATCH_BY_RANGE)

    assert validator._merged_pr_dispatch_violations(workflow) == []


def test_a_hard_coded_range_bound_is_rejected(tmp_path: Path) -> None:
    """A bound that does not come from the merge event enumerates the wrong revisions.

    The pattern and the source of its bound are checked together: recognising
    the command text alone would approve a dispatcher whose `BASE_SHA` is
    hard-coded, which enumerates unrelated revisions and lets added commits
    reach main without an individual releasability verdict.
    """
    workflow = _dispatch_file(
        tmp_path,
        _DISPATCH_BY_RANGE.replace(
            "BASE_SHA: ${{ github.event.pull_request.base.sha }}", "BASE_SHA: deadbeef"
        ),
    )

    violations = validator._merged_pr_dispatch_violations(workflow)

    assert "merged-pr-dispatch.missing-expected-sha-input" in violations


def test_a_range_bound_from_another_event_field_is_rejected(tmp_path: Path) -> None:
    """`head.sha` is a plausible-looking substitution that enumerates nothing useful."""
    workflow = _dispatch_file(
        tmp_path,
        _DISPATCH_BY_RANGE.replace(
            "BASE_SHA: ${{ github.event.pull_request.base.sha }}",
            "BASE_SHA: ${{ github.event.pull_request.head.sha }}",
        ),
    )

    violations = validator._merged_pr_dispatch_violations(workflow)

    assert "merged-pr-dispatch.missing-expected-sha-input" in violations


def test_a_dispatcher_that_enumerates_everything_is_rejected(tmp_path: Path) -> None:
    """The acceptance above must not become an acceptance of any rev-list at all."""
    workflow = _dispatch_file(
        tmp_path,
        _DISPATCH_BY_RANGE.replace(
            'revisions="$(git rev-list --reverse "$BASE_SHA..$MERGE_COMMIT_SHA")"',
            'revisions="$(git rev-list HEAD)"',
        ),
    )

    violations = validator._merged_pr_dispatch_violations(workflow)

    assert "merged-pr-dispatch.missing-expected-sha-input" in violations


def test_dropping_the_expected_sha_input_is_still_rejected(tmp_path: Path) -> None:
    workflow = _dispatch_file(
        tmp_path, _DISPATCH_BY_RANGE.replace(' -f expected_sha="$revision"', "")
    )

    violations = validator._merged_pr_dispatch_violations(workflow)

    assert "merged-pr-dispatch.missing-expected-sha-input" in violations


def test_dropping_the_ancestor_guard_is_still_rejected(tmp_path: Path) -> None:
    """A revision not on main must never be tagged and gated as main history."""
    workflow = _dispatch_file(
        tmp_path,
        _DISPATCH_BY_RANGE.replace(
            'git merge-base --is-ancestor "$revision" HEAD', "true"
        ),
    )

    violations = validator._merged_pr_dispatch_violations(workflow)

    assert "merged-pr-dispatch.missing-expected-sha-input" in violations


# An empty enumeration expands to zero matrix jobs, and zero jobs is a
# success, so a valid workflow has to refuse one. The fixture carries that
# guard because a fixture without it is not a workflow this control accepts.
_ENUMERATION_RUN = chr(10).join(['set -euo pipefail', 'merge_methods="$(gh api repos/$GITHUB_REPOSITORY --jq join)"', 'if [ "$merge_methods" != "false,false,true" ]; then exit 1; fi', 'revisions="$(git rev-list -n "$COMMIT_COUNT" "$MERGE_COMMIT_SHA" | tac)"', 'if [ -z "$revisions" ]; then exit 1; fi', 'payload="$(printf %s "$revisions" | jq -R . | jq -sc .)"', 'echo "list=$payload" >> "$GITHUB_OUTPUT"']) + chr(10)
_DISPATCH_RUN = chr(10).join(['set -euo pipefail', 'dispatch_ref="main-releasability-${revision}"', 'gh api "repos/$GITHUB_REPOSITORY/git/ref/tags/$dispatch_ref" --jq .object.sha', 'gh api "repos/$GITHUB_REPOSITORY/git/refs" -f ref="refs/tags/$dispatch_ref" -f sha="$revision"', 'gh workflow run main-releasability.yml --ref "$dispatch_ref" -f expected_sha="$revision"']) + chr(10)


def _matrix_dispatch_workflow(
    *,
    output_name: str = "revisions",
    matrix_key: str = "revision",
    from_json: str = "fromJson",
    enumeration: str | None = None,
    dispatch: str | None = None,
) -> dict:
    """A two-job matrix dispatch, parameterised so a breach can be injected.

    The names are parameters on purpose. The defect this replaced pinned the
    output name, the matrix key and the casing of `fromJson`, so a workflow that
    gated every commit correctly was reported as a violation for choosing other
    words, and that blocked every pull request in this repository.
    """
    matrix_expression = (
        "${{ " + from_json + "(needs.enumerate.outputs." + output_name + ") }}"
    )
    return {
        "on": {"pull_request_target": {"types": ["closed"]}},
        "permissions": {"actions": "write", "contents": "write"},
        "jobs": {
            "enumerate": {
                "if": (
                    "github.event.pull_request.merged == true && "
                    "github.event.pull_request.base.ref == 'main'"
                ),
                "outputs": {output_name: "${{ steps.enumerate.outputs.list }}"},
                "steps": [
                    {
                        "id": "enumerate",
                        "env": {
                            "MERGE_COMMIT_SHA": (
                                "${{ github.event.pull_request.merge_commit_sha }}"
                            ),
                            "COMMIT_COUNT": "${{ github.event.pull_request.commits }}",
                        },
                        "run": _ENUMERATION_RUN if enumeration is None else enumeration,
                    }
                ],
            },
            "dispatch": {
                "needs": ["enumerate"],
                "strategy": {"matrix": {matrix_key: matrix_expression}},
                "steps": [
                    {
                        "env": {"revision": "${{ matrix." + matrix_key + " }}"},
                        "run": _DISPATCH_RUN if dispatch is None else dispatch,
                    }
                ],
            },
        },
    }


def _matrix_is_accepted(workflow: dict) -> bool:
    return validator._merged_pr_dispatch_passes_exact_sha(
        workflow
    ) and validator._merged_pr_dispatch_has_immutable_ref(workflow)


def _dispatch_without(line_to_replace: str, replacement: str) -> str:
    return chr(10).join(
        replacement if line == line_to_replace else line for line in DISPATCH_SOURCE
    ) + chr(10)


DISPATCH_SOURCE = ['set -euo pipefail', 'dispatch_ref="main-releasability-${revision}"', 'gh api "repos/$GITHUB_REPOSITORY/git/ref/tags/$dispatch_ref" --jq .object.sha', 'gh api "repos/$GITHUB_REPOSITORY/git/refs" -f ref="refs/tags/$dispatch_ref" -f sha="$revision"', 'gh workflow run main-releasability.yml --ref "$dispatch_ref" -f expected_sha="$revision"']


def test_matrix_dispatch_is_accepted_whatever_it_names_things() -> None:
    """The property is the immutable ref and the bound expected SHA, not the words.

    The recogniser required the literal `fromJSON`, an output named
    `commit_shas` and a matrix key named `commit_sha`. Both spellings must be
    accepted, because both describe the same gating behaviour.
    """
    assert _matrix_is_accepted(_matrix_dispatch_workflow())
    assert _matrix_is_accepted(
        _matrix_dispatch_workflow(
            output_name="commit_shas", matrix_key="commit_sha", from_json="fromJSON"
        )
    )


def test_matrix_dispatch_on_a_mutable_ref_is_rejected() -> None:
    """Without an immutable ref the run gates whatever that ref points at."""
    workflow = _matrix_dispatch_workflow(
        dispatch=_dispatch_without(
            DISPATCH_SOURCE[4],
            "gh workflow run main-releasability.yml --ref main "
            '-f expected_sha="$revision"',
        )
    )

    assert not _matrix_is_accepted(workflow)


def test_matrix_dispatch_with_an_unbound_expected_sha_is_rejected() -> None:
    """The other half: a ref naming a revision the caller did not assert."""
    workflow = _matrix_dispatch_workflow(
        dispatch=_dispatch_without(
            DISPATCH_SOURCE[4],
            'gh workflow run main-releasability.yml --ref "$dispatch_ref" '
            "-f expected_sha=main",
        )
    )

    assert not _matrix_is_accepted(workflow)


def test_matrix_dispatch_creating_a_ref_from_another_sha_is_rejected() -> None:
    """The tag must name the revision it will be used to gate."""
    workflow = _matrix_dispatch_workflow(
        dispatch=_dispatch_without(
            DISPATCH_SOURCE[3],
            'gh api "repos/$GITHUB_REPOSITORY/git/refs" '
            '-f ref="refs/tags/$dispatch_ref" -f sha=main',
        )
    )

    assert not _matrix_is_accepted(workflow)


def test_matrix_enumeration_without_a_count_bound_is_rejected() -> None:
    """An unbounded enumeration can return fewer commits than the PR contained,
    and every commit it omits is one that nothing gates."""
    unbounded = list(['set -euo pipefail', 'merge_methods="$(gh api repos/$GITHUB_REPOSITORY --jq join)"', 'if [ "$merge_methods" != "false,false,true" ]; then exit 1; fi', 'revisions="$(git rev-list -n "$COMMIT_COUNT" "$MERGE_COMMIT_SHA" | tac)"', 'if [ -z "$revisions" ]; then exit 1; fi', 'payload="$(printf %s "$revisions" | jq -R . | jq -sc .)"', 'echo "list=$payload" >> "$GITHUB_OUTPUT"'])
    unbounded[3] = 'revisions="$(git rev-list "$MERGE_COMMIT_SHA")"'

    assert not _matrix_is_accepted(
        _matrix_dispatch_workflow(enumeration=chr(10).join(unbounded) + chr(10))
    )


def test_matrix_enumeration_without_the_rebase_only_assertion_is_rejected() -> None:
    """Squash and merge commits make per-commit enumeration describe history
    that was never put on main."""
    unasserted = [line for line in ['set -euo pipefail', 'merge_methods="$(gh api repos/$GITHUB_REPOSITORY --jq join)"', 'if [ "$merge_methods" != "false,false,true" ]; then exit 1; fi', 'revisions="$(git rev-list -n "$COMMIT_COUNT" "$MERGE_COMMIT_SHA" | tac)"', 'if [ -z "$revisions" ]; then exit 1; fi', 'payload="$(printf %s "$revisions" | jq -R . | jq -sc .)"', 'echo "list=$payload" >> "$GITHUB_OUTPUT"'] if "false,false,true" not in line]

    assert not _matrix_is_accepted(
        _matrix_dispatch_workflow(enumeration=chr(10).join(unasserted) + chr(10))
    )


def test_a_matrix_fed_from_a_literal_is_rejected() -> None:
    """A hard-coded matrix is not an enumeration, whatever it is named."""
    workflow = _matrix_dispatch_workflow()
    workflow["jobs"]["enumerate"]["outputs"]["revisions"] = "abc123 def456"

    assert not _matrix_is_accepted(workflow)


def test_widening_did_not_drop_the_single_step_shape(tmp_path: Path) -> None:
    """Eleven repositories use the single-step form and two use the matrix form.

    A change accepting only the newly recognised shape would pass its own
    fixtures and fail the estate, so the shape that already worked is asserted
    from the same aligned fixture the rest of this suite uses.
    """
    repo_root = tmp_path / "lotus-example"
    repo_root.mkdir()
    _write_aligned_workflows(repo_root)
    aligned = validator._load_yaml(
        repo_root / ".github" / "workflows" / "merged-pr-main-releasability.yml"
    )

    assert validator._merged_pr_dispatch_passes_exact_sha(aligned)
    assert validator._merged_pr_dispatch_has_immutable_ref(aligned)
    assert _matrix_is_accepted(_matrix_dispatch_workflow())


def test_a_matrix_fed_by_a_nonexistent_step_is_rejected() -> None:
    """The consumed output must come from the step that was proven.

    Accepting any expression containing `steps.` meant a job could declare an
    output referencing a step that does not exist, and the matrix built from it
    was reported as a verified enumeration. Reported as C5-PLAT-01.
    """
    workflow = _matrix_dispatch_workflow()
    workflow["jobs"]["enumerate"]["outputs"]["revisions"] = (
        "${{ steps.does-not-exist.outputs.list }}"
    )

    assert not _matrix_is_accepted(workflow)


def test_a_matrix_fed_by_an_unrelated_step_is_rejected() -> None:
    """A second step publishing an empty list is not the enumeration.

    This is the sharper half of C5-PLAT-01: the enumeration step is present and
    correct, so every other check passes, and the matrix consumes something else
    entirely. The dispatch then gates whatever that other step emitted, which
    here is nothing.
    """
    workflow = _matrix_dispatch_workflow()
    workflow["jobs"]["enumerate"]["steps"].append(
        {"id": "unrelated", "run": 'echo "empty=[]" >> "$GITHUB_OUTPUT"' + chr(10)}
    )
    workflow["jobs"]["enumerate"]["outputs"]["revisions"] = (
        "${{ steps.unrelated.outputs.empty }}"
    )

    assert not _matrix_is_accepted(workflow)


def test_a_matrix_fed_by_a_key_the_step_never_emits_is_rejected() -> None:
    """Naming the right step is not enough if it never writes that key."""
    workflow = _matrix_dispatch_workflow()
    workflow["jobs"]["enumerate"]["outputs"]["revisions"] = (
        "${{ steps.enumerate.outputs.not_emitted }}"
    )

    assert not _matrix_is_accepted(workflow)


def test_an_enumeration_that_can_publish_nothing_is_rejected() -> None:
    """Zero matrix jobs is a success, so an empty enumeration is a silent pass.

    The dispatch job reports green having gated no commit at all, which is
    indistinguishable from having gated them successfully.
    """
    enumeration = chr(10).join(
        line
        for line in _ENUMERATION_RUN.split(chr(10))
        if '-z "$revisions"' not in line
    )

    assert not _matrix_is_accepted(
        _matrix_dispatch_workflow(enumeration=enumeration)
    )


def test_valid_renamed_matrix_forms_are_still_accepted() -> None:
    """The correction must not regress into the spelling checks #844 removed.

    Both spellings in use across the estate stay accepted: eleven repositories
    use the single-step form, and the two matrix repositories name their output
    and matrix key differently from each other.
    """
    assert _matrix_is_accepted(_matrix_dispatch_workflow())
    assert _matrix_is_accepted(
        _matrix_dispatch_workflow(
            output_name="commit_shas", matrix_key="commit_sha", from_json="fromJSON"
        )
    )


def test_a_verified_step_emitting_a_constant_is_rejected() -> None:
    """The published value must be the revisions the step enumerated.

    Binding the matrix to the proven step's output key was not enough: a step
    could walk every revision correctly and then publish a constant under that
    key. The matrix would gate the merge commit alone while the validator
    reported the whole PR as aligned.
    """
    constant = _ENUMERATION_RUN.replace(
        'echo "list=$payload" >> "$GITHUB_OUTPUT"',
        'echo "list=[\\"$MERGE_COMMIT_SHA\\"]" >> "$GITHUB_OUTPUT"',
    )

    assert not _matrix_is_accepted(_matrix_dispatch_workflow(enumeration=constant))


def test_an_emptiness_guard_on_an_unrelated_variable_is_rejected() -> None:
    """A guard has to test the enumeration, not merely exist in the step."""
    unrelated = _ENUMERATION_RUN.replace(
        'if [ -z "$revisions" ]; then exit 1; fi',
        'if [ -z "$UNRELATED" ]; then exit 1; fi',
    )

    assert not _matrix_is_accepted(_matrix_dispatch_workflow(enumeration=unrelated))


def test_an_emptiness_guard_that_only_logs_is_rejected() -> None:
    """Detecting the empty list and continuing publishes it anyway.

    The revisions are still emitted, the matrix still expands to zero jobs, and
    the dispatch still reports green having gated nothing -- with a log line
    that reads like the guard worked.
    """
    logs_only = _ENUMERATION_RUN.replace(
        'if [ -z "$revisions" ]; then exit 1; fi',
        'if [ -z "$revisions" ]; then echo "none"; fi',
    )

    assert not _matrix_is_accepted(_matrix_dispatch_workflow(enumeration=logs_only))


def test_an_emission_derived_from_the_enumeration_is_accepted() -> None:
    """The shipped form reshapes the revisions before publishing them.

    One of the estate's two implementations emits `revisions=$payload`, where
    `payload` is the enumeration rendered as JSON. Demanding the enumeration
    variable appear verbatim in the emission would reject that correct workflow,
    so the binding follows the derivation and this pins it.
    """
    derived = _ENUMERATION_RUN.replace(
        'echo "list=$payload" >> "$GITHUB_OUTPUT"',
        "payload=\"$(printf '%s' $revisions | jq -R . | jq -sc .)\""
        + chr(10)
        + 'echo "list=$payload" >> "$GITHUB_OUTPUT"',
    )

    assert _matrix_is_accepted(_matrix_dispatch_workflow(enumeration=derived))


def test_a_multi_line_guard_that_terminates_is_accepted() -> None:
    """Real workflows write the guard as a block, not a one-liner.

    Reading the condition without its body cannot tell a terminating guard from
    a logging one, so the reader pairs them -- and it has to handle the block
    form both shipped workflows actually use.
    """
    block = _ENUMERATION_RUN.replace(
        'if [ -z "$revisions" ]; then exit 1; fi',
        'if [ -z "$revisions" ]; then'
        + chr(10)
        + '  echo "::error::No revisions enumerated"'
        + chr(10)
        + "  exit 1"
        + chr(10)
        + "fi",
    )

    assert _matrix_is_accepted(_matrix_dispatch_workflow(enumeration=block))
