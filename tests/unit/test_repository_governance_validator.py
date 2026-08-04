from __future__ import annotations

import pytest

from automation.validate_repository_governance import (
    DEFAULT_POLICY_PATH,
    ExpectedRepositoryGovernance,
    _matrix_rows,
    compare_required_check_sources,
    compare_governance,
    extract_emitted_workflow_checks,
    expected_governance,
    load_policy,
    normalize_actual_governance,
    select_repositories,
)


def test_normalize_actual_governance_for_unprotected_branch() -> None:
    actual = normalize_actual_governance(None)

    assert actual["protected"] is False
    assert actual["required_checks"] == []
    assert actual["approvals"] == 0


def test_normalize_actual_governance_for_protected_branch_payload() -> None:
    actual = normalize_actual_governance(
        {
            "required_status_checks": {
                "contexts": [
                    "PR Merge Gate / Workflow Lint",
                    "PR Merge Gate / Platform Repo Contracts",
                ],
                "strict": True,
            },
            "required_pull_request_reviews": {
                "required_approving_review_count": 0,
                "dismiss_stale_reviews": True,
            },
            "required_conversation_resolution": {"enabled": True},
            "required_linear_history": {"enabled": True},
            "allow_force_pushes": {"enabled": False},
            "allow_deletions": {"enabled": False},
        }
    )

    assert actual == {
        "protected": True,
        "required_checks": [
            "PR Merge Gate / Platform Repo Contracts",
            "PR Merge Gate / Workflow Lint",
        ],
        "strict": True,
        "approvals": 0,
        "dismiss_stale_reviews": True,
        "require_conversation_resolution": True,
        "required_linear_history": True,
        "allow_force_pushes": False,
        "allow_deletions": False,
        "allow_auto_merge": False,
        "allow_squash_merge": False,
        "allow_merge_commit": False,
        "allow_rebase_merge": False,
    }


def test_compare_governance_reports_drift_for_missing_branch_protection() -> None:
    expected_repo = ExpectedRepositoryGovernance(
        name="lotus-platform",
        default_branch="main",
        required_checks=(
            "PR Merge Gate / Workflow Lint",
            "PR Merge Gate / Platform Repo Contracts",
        ),
    )
    drift = compare_governance(
        expected_governance(expected_repo), normalize_actual_governance(None)
    )

    assert any(item.startswith("protected:") for item in drift)
    assert any(item.startswith("required_checks:") for item in drift)
    assert any(item.startswith("allow_auto_merge:") for item in drift)


def test_single_developer_governance_keeps_ci_gates_without_human_approval() -> None:
    expected_repo = ExpectedRepositoryGovernance(
        name="lotus-platform",
        default_branch="main",
        required_checks=(
            "PR Merge Gate / Workflow Lint",
            "PR Merge Gate / Platform Repo Contracts",
        ),
    )

    expected = expected_governance(expected_repo)

    assert expected["approvals"] == 0
    assert expected["protected"] is True
    assert expected["strict"] is True
    assert expected["require_conversation_resolution"] is True
    assert expected["required_checks"] == [
        "PR Merge Gate / Platform Repo Contracts",
        "PR Merge Gate / Workflow Lint",
    ]


def test_extract_emitted_workflow_checks_expands_matrix_job_names() -> None:
    emitted = extract_emitted_workflow_checks(
        {
            ".github/workflows/pr-merge-gate.yml": """
jobs:
  workflow-lint:
    name: PR Merge Gate / Workflow Lint
  tests:
    name: PR Merge Gate / Tests (${{ matrix.suite }})
    strategy:
      matrix:
        include:
          - suite: unit
          - suite: integration
"""
        }
    )

    assert emitted == {
        "PR Merge Gate / Workflow Lint",
        "PR Merge Gate / Tests (unit)",
        "PR Merge Gate / Tests (integration)",
    }


def test_extract_emitted_workflow_checks_honors_matrix_axes_and_exclusions() -> None:
    emitted = extract_emitted_workflow_checks(
        {
            ".github/workflows/pr-merge-gate.yml": """
jobs:
  tests:
    name: PR Merge Gate / Tests (${{ matrix.suite }}, ${{ matrix.python }})
    strategy:
      matrix:
        suite: [unit, integration]
        python: ['3.12', '3.13']
        exclude:
          - suite: integration
            python: '3.13'
"""
        }
    )

    assert emitted == {
        "PR Merge Gate / Tests (unit, 3.12)",
        "PR Merge Gate / Tests (unit, 3.13)",
        "PR Merge Gate / Tests (integration, 3.12)",
    }


def test_matrix_rows_follow_github_sequential_include_semantics() -> None:
    rows = _matrix_rows(
        {
            "fruit": ["apple", "pear"],
            "animal": ["cat", "dog"],
            "include": [
                {"color": "green"},
                {"color": "pink", "animal": "cat"},
                {"fruit": "apple", "shape": "circle"},
                {"fruit": "banana"},
                {"fruit": "banana", "animal": "cat"},
            ],
        }
    )

    assert rows == [
        {"fruit": "apple", "animal": "cat", "color": "pink", "shape": "circle"},
        {"fruit": "apple", "animal": "dog", "color": "green", "shape": "circle"},
        {"fruit": "pear", "animal": "cat", "color": "pink"},
        {"fruit": "pear", "animal": "dog", "color": "green"},
        {"fruit": "banana"},
        {"fruit": "banana", "animal": "cat"},
    ]


def test_extract_emitted_workflow_checks_uses_final_include_values() -> None:
    emitted = extract_emitted_workflow_checks(
        {
            ".github/workflows/pr-merge-gate.yml": """
jobs:
  tests:
    name: PR Merge Gate / Tests (${{ matrix.fruit }}, ${{ matrix.animal }}, ${{ matrix.color }})
    strategy:
      matrix:
        fruit: [apple, pear]
        animal: [cat, dog]
        include:
          - color: green
          - color: pink
            animal: cat
"""
        }
    )

    assert emitted == {
        "PR Merge Gate / Tests (apple, cat, pink)",
        "PR Merge Gate / Tests (apple, dog, green)",
        "PR Merge Gate / Tests (pear, cat, pink)",
        "PR Merge Gate / Tests (pear, dog, green)",
    }


def test_compare_required_check_sources_reports_non_emitted_policy_context() -> None:
    expected_repo = ExpectedRepositoryGovernance(
        name="lotus-workbench",
        default_branch="main",
        required_checks=(
            "PR Merge Gate / Workflow Lint",
            "PR Merge Gate / Validate Docker Build",
        ),
    )

    drift = compare_required_check_sources(
        expected_repo,
        {
            ".github/workflows/pr-merge-gate.yml": """
jobs:
  workflow-lint:
    name: PR Merge Gate / Workflow Lint
  docker-build:
    name: PR Merge Gate / Docker Build And Security
"""
        },
    )

    assert drift == [
        "required check is not emitted by a governed workflow: "
        "PR Merge Gate / Validate Docker Build"
    ]


def test_compare_required_check_sources_accepts_documented_external_provider() -> None:
    expected_repo = ExpectedRepositoryGovernance(
        name="lotus-platform",
        default_branch="main",
        required_checks=(
            "PR Merge Gate / Workflow Lint",
            "Cross-App Vocabulary Gate",
        ),
        external_check_providers=(
            ("Cross-App Vocabulary Gate", "cross-repository vocabulary workflow"),
        ),
    )

    assert (
        compare_required_check_sources(
            expected_repo,
            {
                ".github/workflows/pr-merge-gate.yml": """
jobs:
  workflow-lint:
    name: PR Merge Gate / Workflow Lint
"""
            },
        )
        == []
    )


def test_load_policy_rejects_blank_external_provider(tmp_path) -> None:
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(
        """
{
  "repos": [{
    "name": "lotus-platform",
    "default_branch": "main",
    "required_checks": ["Cross-App Vocabulary Gate"],
    "external_required_checks": {"Cross-App Vocabulary Gate": ""}
  }]
}
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="non-empty string contexts and providers"):
        load_policy(policy_path)


def test_select_repositories_preserves_policy_order_and_rejects_unknown_names() -> None:
    repositories = [
        ExpectedRepositoryGovernance("lotus-core", "main", ("Core Gate",)),
        ExpectedRepositoryGovernance("lotus-workbench", "main", ("Workbench Gate",)),
    ]

    assert select_repositories(repositories, ["lotus-workbench"]) == [repositories[1]]
    with pytest.raises(ValueError, match="lotus-unknown"):
        select_repositories(repositories, ["lotus-unknown"])


def test_policy_names_only_current_repository_specific_container_checks() -> None:
    policy = {repo.name: repo for repo in load_policy(DEFAULT_POLICY_PATH)}

    assert (
        "PR Merge Gate / Docker Image Evidence"
        in policy["lotus-manage"].required_checks
    )
    assert (
        "PR Merge Gate / Container Supply Chain Evidence"
        in policy["lotus-performance"].required_checks
    )
    assert (
        "PR Merge Gate / Docker Build And Security"
        in policy["lotus-workbench"].required_checks
    )
    assert (
        "PR Merge Gate / Validate Docker Build"
        not in policy["lotus-workbench"].required_checks
    )
    assert (
        "PR Merge Gate / PostgreSQL Runtime Proof"
        in policy["lotus-idea"].required_checks
    )
    assert policy["lotus-platform"].external_check_providers == ()
