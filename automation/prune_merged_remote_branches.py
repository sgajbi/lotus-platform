from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable


DEFAULT_PROTECTED_PATTERNS = ("main", "master", "release/", "hotfix/", "env/")


@dataclass(frozen=True)
class PullRequestSummary:
    number: int
    state: str
    head_ref_name: str
    merged_at: datetime | None
    closed_at: datetime | None
    title: str


@dataclass(frozen=True)
class BranchDisposition:
    branch: str
    action: str
    reason: str
    pull_request_number: int | None = None


def parse_github_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def is_protected_branch(branch: str, protected_patterns: Iterable[str] = DEFAULT_PROTECTED_PATTERNS) -> bool:
    for pattern in protected_patterns:
        if pattern.endswith("/") and branch.startswith(pattern):
            return True
        if branch == pattern:
            return True
    return False


def latest_pr_by_branch(pull_requests: Iterable[PullRequestSummary]) -> dict[str, PullRequestSummary]:
    latest: dict[str, PullRequestSummary] = {}
    for pull_request in pull_requests:
        existing = latest.get(pull_request.head_ref_name)
        if existing is None or pull_request.number > existing.number:
            latest[pull_request.head_ref_name] = pull_request
    return latest


def classify_branch(
    branch: str,
    pull_requests_by_branch: dict[str, PullRequestSummary],
    *,
    now: datetime,
    closed_branch_retention_days: int,
) -> BranchDisposition:
    if is_protected_branch(branch):
        return BranchDisposition(branch=branch, action="keep", reason="protected branch")

    pull_request = pull_requests_by_branch.get(branch)
    if pull_request is None:
        return BranchDisposition(branch=branch, action="review", reason="no pull request found for branch")

    if pull_request.state == "OPEN":
        return BranchDisposition(
            branch=branch,
            action="keep",
            reason="open pull request",
            pull_request_number=pull_request.number,
        )

    if pull_request.state == "MERGED" or pull_request.merged_at is not None:
        return BranchDisposition(
            branch=branch,
            action="delete",
            reason="pull request merged",
            pull_request_number=pull_request.number,
        )

    if pull_request.state == "CLOSED" and pull_request.closed_at is not None:
        age = now - pull_request.closed_at
        if age >= timedelta(days=closed_branch_retention_days):
            return BranchDisposition(
                branch=branch,
                action="delete",
                reason=f"pull request closed for at least {closed_branch_retention_days} days",
                pull_request_number=pull_request.number,
            )
        return BranchDisposition(
            branch=branch,
            action="keep",
            reason=f"closed pull request retained for {closed_branch_retention_days} days",
            pull_request_number=pull_request.number,
        )

    return BranchDisposition(
        branch=branch,
        action="review",
        reason=f"unsupported pull request state: {pull_request.state}",
        pull_request_number=pull_request.number,
    )


def run_gh_json(arguments: list[str]) -> Any:
    completed = subprocess.run(
        ["gh", *arguments],
        check=True,
        capture_output=True,
        encoding="utf-8",
    )
    if not completed.stdout.strip():
        return None
    return json.loads(completed.stdout)


def fetch_branch_names(repo: str) -> list[str]:
    branches: list[str] = []
    page = 1
    while True:
        payload = run_gh_json(
            [
                "api",
                f"repos/{repo}/branches",
                "--method",
                "GET",
                "-f",
                "per_page=100",
                "-f",
                f"page={page}",
            ]
        )
        if not payload:
            break
        branches.extend(item["name"] for item in payload)
        if len(payload) < 100:
            break
        page += 1
    return sorted(branches)


def fetch_pull_requests(repo: str) -> list[PullRequestSummary]:
    payload = run_gh_json(
        [
            "pr",
            "list",
            "--repo",
            repo,
            "--state",
            "all",
            "--limit",
            "500",
            "--json",
            "number,state,headRefName,mergedAt,closedAt,title",
        ]
    )
    return [
        PullRequestSummary(
            number=item["number"],
            state=item["state"],
            head_ref_name=item["headRefName"],
            merged_at=parse_github_timestamp(item.get("mergedAt")),
            closed_at=parse_github_timestamp(item.get("closedAt")),
            title=item.get("title", ""),
        )
        for item in payload
    ]


def load_governed_repositories(policy_path: Path, owner: str) -> list[str]:
    payload = json.loads(policy_path.read_text(encoding="utf-8"))
    return [f"{owner}/{repo['name']}" for repo in payload["repos"]]


def delete_remote_branch(repo: str, branch: str) -> None:
    subprocess.run(["gh", "api", "--method", "DELETE", f"repos/{repo}/git/refs/heads/{branch}"], check=True)


def build_dispositions(repo: str, closed_branch_retention_days: int) -> list[BranchDisposition]:
    branches = fetch_branch_names(repo)
    pull_requests = latest_pr_by_branch(fetch_pull_requests(repo))
    now = datetime.now(UTC)
    return [
        classify_branch(
            branch,
            pull_requests,
            now=now,
            closed_branch_retention_days=closed_branch_retention_days,
        )
        for branch in branches
    ]


def emit_report(repo: str, dispositions: list[BranchDisposition], *, apply: bool) -> None:
    print(f"Repository: {repo}")
    print(f"Mode: {'apply' if apply else 'dry-run'}")
    for disposition in dispositions:
        pr = f" PR #{disposition.pull_request_number}" if disposition.pull_request_number else ""
        print(f"- {disposition.action.upper():6} {disposition.branch}{pr}: {disposition.reason}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prune merged or stale closed remote Lotus branches safely.")
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--repo", help="Single repository in owner/name form.")
    scope.add_argument("--all-lotus-repos", action="store_true", help="Use automation/repository-governance-policy.json.")
    parser.add_argument("--owner", default="sgajbi", help="GitHub owner used with --all-lotus-repos.")
    parser.add_argument("--policy-path", default="automation/repository-governance-policy.json")
    parser.add_argument("--closed-branch-retention-days", type=int, default=30)
    parser.add_argument("--apply", action="store_true", help="Delete eligible branches. Omit for dry-run.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repos = (
        load_governed_repositories(Path(args.policy_path), args.owner)
        if args.all_lotus_repos
        else [args.repo]
    )
    assert repos

    for repo in repos:
        dispositions = build_dispositions(repo, args.closed_branch_retention_days)
        emit_report(repo, dispositions, apply=args.apply)
        if args.apply:
            for disposition in dispositions:
                if disposition.action == "delete":
                    delete_remote_branch(repo, disposition.branch)
                    print(f"Deleted {repo}:{disposition.branch}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
