from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


DEFAULT_WARNING_AT = 40
DEFAULT_SPLIT_REQUIRED_AT = 60
DEFAULT_FAIL_ABOVE = 90


class BranchCommitBudgetError(ValueError):
    pass


@dataclass(frozen=True)
class BranchCommitBudgetResult:
    commit_count: int
    status: str
    severity: str
    message: str
    warning_at: int
    split_required_at: int
    fail_above: int
    tranche_decision: str | None

    @property
    def exit_code(self) -> int:
        return 0 if self.severity in {"ok", "warning"} else 1

    def to_payload(self) -> dict[str, object]:
        payload = asdict(self)
        payload["exit_code"] = self.exit_code
        return payload


def validate_thresholds(warning_at: int, split_required_at: int, fail_above: int) -> None:
    if warning_at <= 0:
        raise BranchCommitBudgetError("warning_at must be positive")
    if split_required_at <= warning_at:
        raise BranchCommitBudgetError("split_required_at must be greater than warning_at")
    if fail_above < split_required_at:
        raise BranchCommitBudgetError("fail_above must be greater than or equal to split_required_at")


def classify_commit_budget(
    commit_count: int,
    *,
    warning_at: int = DEFAULT_WARNING_AT,
    split_required_at: int = DEFAULT_SPLIT_REQUIRED_AT,
    fail_above: int = DEFAULT_FAIL_ABOVE,
    tranche_decision: str | None = None,
) -> BranchCommitBudgetResult:
    validate_thresholds(warning_at, split_required_at, fail_above)
    if commit_count < 0:
        raise BranchCommitBudgetError("commit_count must not be negative")

    normalized_decision = (tranche_decision or "").strip() or None
    if commit_count > fail_above:
        return BranchCommitBudgetResult(
            commit_count=commit_count,
            status="blocked_over_commit_budget",
            severity="fail",
            message=(
                f"Branch has {commit_count} commits, above the governed rebase-safe budget of "
                f"{fail_above}. Split into independently releasable tranches before PR merge."
            ),
            warning_at=warning_at,
            split_required_at=split_required_at,
            fail_above=fail_above,
            tranche_decision=normalized_decision,
        )
    if commit_count >= split_required_at and normalized_decision is None:
        return BranchCommitBudgetResult(
            commit_count=commit_count,
            status="split_decision_required",
            severity="fail",
            message=(
                f"Branch has {commit_count} commits. Record an explicit tranche/split decision "
                f"before continuing past {split_required_at} commits."
            ),
            warning_at=warning_at,
            split_required_at=split_required_at,
            fail_above=fail_above,
            tranche_decision=None,
        )
    if commit_count >= split_required_at:
        return BranchCommitBudgetResult(
            commit_count=commit_count,
            status="split_decision_recorded",
            severity="warning",
            message=(
                f"Branch has {commit_count} commits and has a recorded tranche decision. Keep "
                f"headroom below {fail_above} commits for review and CI fix-forward."
            ),
            warning_at=warning_at,
            split_required_at=split_required_at,
            fail_above=fail_above,
            tranche_decision=normalized_decision,
        )
    if commit_count >= warning_at:
        return BranchCommitBudgetResult(
            commit_count=commit_count,
            status="approaching_split_threshold",
            severity="warning",
            message=(
                f"Branch has {commit_count} commits. Start planning a capability tranche before "
                f"{split_required_at} commits."
            ),
            warning_at=warning_at,
            split_required_at=split_required_at,
            fail_above=fail_above,
            tranche_decision=None,
        )
    return BranchCommitBudgetResult(
        commit_count=commit_count,
        status="within_budget",
        severity="ok",
        message=f"Branch has {commit_count} commits and is within the governed rebase-safe budget.",
        warning_at=warning_at,
        split_required_at=split_required_at,
        fail_above=fail_above,
        tranche_decision=None,
    )


def count_branch_commits(repo_root: Path, base_ref: str, head_ref: str) -> int:
    command = ["git", "-C", str(repo_root), "rev-list", "--count", f"{base_ref}..{head_ref}"]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        message = (completed.stderr or completed.stdout).strip()
        raise BranchCommitBudgetError(
            f"Unable to count commits for {base_ref}..{head_ref}: {message}"
        )
    try:
        return int(completed.stdout.strip())
    except ValueError as exc:
        raise BranchCommitBudgetError(
            f"Git returned a non-integer commit count: {completed.stdout.strip()!r}"
        ) from exc


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate branch commit count against Lotus rebase-safe PR budgets."
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--base-ref", default="origin/main")
    parser.add_argument("--head-ref", default="HEAD")
    parser.add_argument("--warning-at", type=int, default=DEFAULT_WARNING_AT)
    parser.add_argument("--split-required-at", type=int, default=DEFAULT_SPLIT_REQUIRED_AT)
    parser.add_argument("--fail-above", type=int, default=DEFAULT_FAIL_ABOVE)
    parser.add_argument(
        "--tranche-decision",
        help="Explicit branch split/tranche decision required at or above split-required-at.",
    )
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--json", action="store_true", help="Emit only JSON to stdout.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        commit_count = count_branch_commits(args.repo_root, args.base_ref, args.head_ref)
        result = classify_commit_budget(
            commit_count,
            warning_at=args.warning_at,
            split_required_at=args.split_required_at,
            fail_above=args.fail_above,
            tranche_decision=args.tranche_decision,
        )
    except BranchCommitBudgetError as exc:
        result = BranchCommitBudgetResult(
            commit_count=-1,
            status="invalid_base_or_thresholds",
            severity="fail",
            message=str(exc),
            warning_at=args.warning_at,
            split_required_at=args.split_required_at,
            fail_above=args.fail_above,
            tranche_decision=args.tranche_decision,
        )

    payload = result.to_payload()
    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"{payload['status']}: {payload['message']}")
    return result.exit_code


if __name__ == "__main__":
    sys.exit(main())
