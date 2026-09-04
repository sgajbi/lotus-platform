from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

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
