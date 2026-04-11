from __future__ import annotations

from datetime import UTC, datetime, timedelta

from automation.prune_merged_remote_branches import (
    PullRequestSummary,
    classify_branch,
    is_protected_branch,
    latest_pr_by_branch,
)


NOW = datetime(2026, 4, 11, tzinfo=UTC)


def pr(
    *,
    number: int,
    state: str,
    branch: str,
    merged_days_ago: int | None = None,
    closed_days_ago: int | None = None,
) -> PullRequestSummary:
    return PullRequestSummary(
        number=number,
        state=state,
        head_ref_name=branch,
        merged_at=NOW - timedelta(days=merged_days_ago) if merged_days_ago is not None else None,
        closed_at=NOW - timedelta(days=closed_days_ago) if closed_days_ago is not None else None,
        title="test",
    )


def test_protected_branch_patterns_are_never_deleted() -> None:
    assert is_protected_branch("main")
    assert is_protected_branch("release/2026-04")
    assert is_protected_branch("hotfix/incident-123")
    assert is_protected_branch("env/demo")
    assert not is_protected_branch("feat/client-reporting")


def test_merged_pull_request_branch_is_deleted() -> None:
    pull_requests = latest_pr_by_branch(
        [pr(number=42, state="MERGED", branch="feat/client-reporting", merged_days_ago=1)]
    )

    disposition = classify_branch(
        "feat/client-reporting",
        pull_requests,
        now=NOW,
        closed_branch_retention_days=30,
    )

    assert disposition.action == "delete"
    assert disposition.reason == "pull request merged"
    assert disposition.pull_request_number == 42


def test_open_pull_request_branch_is_kept() -> None:
    pull_requests = latest_pr_by_branch([pr(number=43, state="OPEN", branch="feat/client-reporting")])

    disposition = classify_branch(
        "feat/client-reporting",
        pull_requests,
        now=NOW,
        closed_branch_retention_days=30,
    )

    assert disposition.action == "keep"
    assert disposition.reason == "open pull request"


def test_recent_closed_unmerged_branch_is_retained_for_review_window() -> None:
    pull_requests = latest_pr_by_branch(
        [pr(number=44, state="CLOSED", branch="fix/abandoned", closed_days_ago=7)]
    )

    disposition = classify_branch(
        "fix/abandoned",
        pull_requests,
        now=NOW,
        closed_branch_retention_days=30,
    )

    assert disposition.action == "keep"
    assert disposition.reason == "closed pull request retained for 30 days"


def test_old_closed_unmerged_branch_is_deleted_after_retention_window() -> None:
    pull_requests = latest_pr_by_branch(
        [pr(number=45, state="CLOSED", branch="fix/abandoned", closed_days_ago=31)]
    )

    disposition = classify_branch(
        "fix/abandoned",
        pull_requests,
        now=NOW,
        closed_branch_retention_days=30,
    )

    assert disposition.action == "delete"
    assert disposition.reason == "pull request closed for at least 30 days"


def test_branch_without_pull_request_requires_manual_review() -> None:
    disposition = classify_branch(
        "feat/no-pr",
        {},
        now=NOW,
        closed_branch_retention_days=30,
    )

    assert disposition.action == "review"
    assert disposition.reason == "no pull request found for branch"


def test_latest_pull_request_for_branch_wins_when_branch_was_reused() -> None:
    pull_requests = latest_pr_by_branch(
        [
            pr(number=40, state="MERGED", branch="fix/reused", merged_days_ago=10),
            pr(number=41, state="OPEN", branch="fix/reused"),
        ]
    )

    disposition = classify_branch(
        "fix/reused",
        pull_requests,
        now=NOW,
        closed_branch_retention_days=30,
    )

    assert disposition.action == "keep"
    assert disposition.pull_request_number == 41
