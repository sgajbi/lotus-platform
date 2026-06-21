from __future__ import annotations

from automation.validate_repository_governance import (
    ExpectedRepositoryGovernance,
    compare_governance,
    expected_governance,
    normalize_actual_governance,
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
        required_checks=("PR Merge Gate / Workflow Lint", "PR Merge Gate / Platform Repo Contracts"),
    )
    drift = compare_governance(expected_governance(expected_repo), normalize_actual_governance(None))

    assert any(item.startswith("protected:") for item in drift)
    assert any(item.startswith("required_checks:") for item in drift)
    assert any(item.startswith("allow_auto_merge:") for item in drift)


def test_single_developer_governance_keeps_ci_gates_without_human_approval() -> None:
    expected_repo = ExpectedRepositoryGovernance(
        name="lotus-platform",
        default_branch="main",
        required_checks=("PR Merge Gate / Workflow Lint", "PR Merge Gate / Platform Repo Contracts"),
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
