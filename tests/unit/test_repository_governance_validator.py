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
