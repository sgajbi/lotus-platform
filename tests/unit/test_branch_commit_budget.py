from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from automation import validate_branch_commit_budget as budget


ROOT = Path(__file__).resolve().parents[2]


def test_branch_commit_budget_passes_below_warning_threshold() -> None:
    result = budget.classify_commit_budget(12)

    assert result.status == "within_budget"
    assert result.severity == "ok"
    assert result.exit_code == 0


def test_branch_commit_budget_warns_at_planning_threshold() -> None:
    result = budget.classify_commit_budget(40)

    assert result.status == "approaching_split_threshold"
    assert result.severity == "warning"
    assert result.exit_code == 0
    assert "Start planning" in result.message


def test_branch_commit_budget_requires_split_decision_at_sixty_commits() -> None:
    result = budget.classify_commit_budget(60)

    assert result.status == "split_decision_required"
    assert result.severity == "fail"
    assert result.exit_code == 1
    assert "Record an explicit tranche/split decision" in result.message


def test_branch_commit_budget_allows_recorded_split_decision_below_hard_limit() -> None:
    result = budget.classify_commit_budget(60, tranche_decision="tranche-2 after API cleanup")

    assert result.status == "split_decision_recorded"
    assert result.severity == "warning"
    assert result.exit_code == 0
    assert result.tranche_decision == "tranche-2 after API cleanup"


def test_branch_commit_budget_blocks_above_rebase_safe_limit() -> None:
    result = budget.classify_commit_budget(91, tranche_decision="continue current branch")

    assert result.status == "blocked_over_commit_budget"
    assert result.severity == "fail"
    assert result.exit_code == 1
    assert "Split into independently releasable tranches" in result.message


def test_branch_commit_budget_rejects_invalid_thresholds() -> None:
    with pytest.raises(budget.BranchCommitBudgetError):
        budget.classify_commit_budget(10, warning_at=60, split_required_at=40)


def test_branch_commit_count_reports_invalid_base(monkeypatch: pytest.MonkeyPatch) -> None:
    completed = subprocess.CompletedProcess(
        args=["git"],
        returncode=128,
        stdout="",
        stderr="fatal: ambiguous argument 'missing..HEAD'",
    )

    def fake_run(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return completed

    monkeypatch.setattr(budget.subprocess, "run", fake_run)

    with pytest.raises(budget.BranchCommitBudgetError) as exc_info:
        budget.count_branch_commits(Path("."), "missing", "HEAD")

    assert "Unable to count commits" in str(exc_info.value)


def test_branch_commit_budget_is_wired_into_pr_guidance_and_preflight() -> None:
    preflight = (ROOT / "automation/Preflight-PR.ps1").read_text(encoding="utf-8")
    playbook = (ROOT / "context/playbooks/PR-LOOP-PLAYBOOK.md").read_text(encoding="utf-8")
    engineering_context = (ROOT / "context/LOTUS-ENGINEERING-CONTEXT.md").read_text(
        encoding="utf-8"
    )
    skill = (ROOT / "codex/skills/lotus-pr-premerge-gate/SKILL.md").read_text(
        encoding="utf-8"
    )
    automation_readme = (ROOT / "automation/README.md").read_text(encoding="utf-8")

    for content in (preflight, playbook, engineering_context, skill, automation_readme):
        assert "validate_branch_commit_budget.py" in content

    assert "[string]$TrancheDecision" in preflight
    assert "branch_commit_budget" in preflight
    assert "Branch Commit Budget:" in preflight
    assert "Branch Commit Count:" in preflight
    assert "--tranche-decision" in playbook
    assert "warns at 40 commits" in skill
    assert "blocks\nabove 90 commits" in automation_readme
