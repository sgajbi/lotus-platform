from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = ROOT / "codex" / "skills" / "gh-issue-fix-qa-loop"
UPDATE_SCRIPT = SKILL_ROOT / "scripts" / "update-issue-loop.ps1"
AUDIT_SCRIPT = SKILL_ROOT / "scripts" / "audit-issue-loop.ps1"
DEFAULT_CONTRACT = SKILL_ROOT / "references" / "issue-status-label-contract.json"
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell")
POWERSHELL_EXECUTABLES = list(
    dict.fromkeys(
        executable
        for executable in (shutil.which("pwsh"), shutil.which("powershell"))
        if executable is not None
    )
)

CANONICAL_LABELS = [
    "status/in-progress",
    "status/fixed-local",
    "status/pr-open",
    "status/merged-main",
    "status/blocked",
]


@pytest.fixture()
def fake_github(tmp_path: Path) -> tuple[Path, Path, dict[str, str]]:
    fake = tmp_path / "fake-gh"
    fake.mkdir()
    state_path = tmp_path / "github-state.json"
    driver = fake / "fake_gh.py"
    driver.write_text(
        r'''#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys

state_path = Path(os.environ["FAKE_GH_STATE"])
state = json.loads(state_path.read_text(encoding="utf-8"))
args = sys.argv[1:]

def value(flag):
    return args[args.index(flag) + 1]

def save():
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

def issue_payload(number):
    issue = state["issues"][str(number)]
    return {
        "number": int(number),
        "state": issue["state"],
        "labels": [{"name": name} for name in issue["labels"]],
        "url": f"https://example.test/issues/{number}",
    }

state.setdefault("calls", []).append(args)
save()

if args[:2] == ["label", "list"]:
    print(json.dumps([{"name": name} for name in state["labels"]]))
elif args[:2] == ["label", "create"]:
    print("label creation is forbidden in tests", file=sys.stderr)
    sys.exit(91)
elif args[:2] == ["issue", "view"]:
    print(json.dumps(issue_payload(args[2])))
elif args[:2] == ["issue", "list"]:
    print(json.dumps([issue_payload(number) for number in state["issues"]]))
elif args[:2] == ["issue", "edit"]:
    issue = state["issues"][args[2]]
    if "--add-label" in args:
        label = value("--add-label")
        if label not in state["labels"]:
            print(f"label not found: {label}", file=sys.stderr)
            sys.exit(1)
        if label not in issue["labels"]:
            issue["labels"].append(label)
    if "--remove-label" in args:
        label = value("--remove-label")
        issue["labels"] = [item for item in issue["labels"] if item != label]
    save()
elif args[:2] == ["issue", "comment"]:
    state.setdefault("comments", []).append({"issue": int(args[2]), "body": value("--body")})
    save()
elif args[:2] == ["issue", "close"]:
    state["issues"][args[2]]["state"] = "CLOSED"
    save()
elif args[:2] == ["issue", "reopen"]:
    state["issues"][args[2]]["state"] = "OPEN"
    save()
    print(f"reopened issue {args[2]}", file=sys.stderr)
elif args[:2] == ["pr", "view"]:
    pr = state["prs"][args[2]]
    print(json.dumps({
        "state": pr["state"],
        "mergeCommit": {"oid": pr.get("mergeCommit")},
        "url": f"https://example.test/pull/{args[2]}",
    }))
elif args[:2] == ["run", "view"]:
    run = state["runs"][args[2]]
    print(json.dumps({
        "conclusion": run["conclusion"],
        "headSha": run["headSha"],
        "name": run["name"],
        "url": f"https://example.test/runs/{args[2]}",
    }))
else:
    print(f"unsupported fake gh call: {args}", file=sys.stderr)
    sys.exit(92)
''',
        encoding="utf-8",
    )

    if os.name == "nt":
        (fake / "gh.cmd").write_text(
            '@python "%~dp0fake_gh.py" %*\r\n', encoding="ascii"
        )
    else:
        gh = fake / "gh"
        gh.write_text(f"#!/bin/sh\nexec python3 '{driver}' \"$@\"\n", encoding="utf-8")
        gh.chmod(gh.stat().st_mode | stat.S_IXUSR)

    env = os.environ.copy()
    env["PATH"] = str(fake) + os.pathsep + env["PATH"]
    env["FAKE_GH_STATE"] = str(state_path)
    return state_path, fake, env


def _state(*, labels: list[str] | None = None) -> dict[str, object]:
    sha = "a" * 40
    return {
        "labels": labels if labels is not None else CANONICAL_LABELS.copy(),
        "issues": {"1": {"state": "OPEN", "labels": ["bug"]}},
        "prs": {
            "10": {"state": "OPEN", "mergeCommit": None},
            "11": {"state": "MERGED", "mergeCommit": sha},
        },
        "runs": {
            "101": {"conclusion": "success", "headSha": sha, "name": "Main Releasability"},
            "102": {"conclusion": "success", "headSha": sha, "name": "CodeQL"},
            "103": {"conclusion": "failure", "headSha": sha, "name": "Main Releasability"},
        },
        "comments": [],
        "calls": [],
    }


def _write_state(path: Path, state: dict[str, object]) -> None:
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _read_state(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _run_script(
    script: Path,
    arguments: list[str],
    env: dict[str, str],
    powershell: str | None = POWERSHELL,
) -> subprocess.CompletedProcess[str]:
    if powershell is None:
        pytest.skip("PowerShell is required for issue-loop automation tests")
    return subprocess.run(
        [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), *arguments],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_default_contract_and_skill_use_one_canonical_vocabulary() -> None:
    contract = json.loads(DEFAULT_CONTRACT.read_text(encoding="utf-8"))
    primary = [definition["label"] for definition in contract["states"].values()]
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    normalized_skill = " ".join(skill.split())
    state_machine = (SKILL_ROOT / "references" / "state-machine.md").read_text(
        encoding="utf-8"
    )

    assert primary == CANONICAL_LABELS
    for label in CANONICAL_LABELS:
        assert label in skill
        assert label in state_machine
    assert "status:qa-" not in skill
    assert "label create" not in skill
    assert "Keep #<issue> open" in skill
    assert "Do not use `Closes`, `Fixes`, or `Resolves`" in normalized_skill
    assert (
        "partial fixes, blocker-proving PRs, or evidence-consumption PRs" in normalized_skill
    )


def test_missing_repository_labels_fail_closed_without_creating_labels(fake_github) -> None:
    state_path, _, env = fake_github
    state = _state(
        labels=[
            "status/in-progress",
            "status/pr-open",
            "status/merged-main",
            "status/blocked",
        ]
    )
    _write_state(state_path, state)

    result = _run_script(
        UPDATE_SCRIPT,
        ["-Repo", "owner/repo", "-IssueNumber", "1", "-Status", "dev_in_progress"],
        env,
    )

    assert result.returncode != 0
    assert "missing configured issue status labels" in (result.stderr + result.stdout)
    after = _read_state(state_path)
    assert after["issues"]["1"]["labels"] == ["bug"]
    assert not any(call[:2] == ["label", "create"] for call in after["calls"])


def test_unsupported_blocked_transition_fails_before_mutating_labels(fake_github) -> None:
    state_path, _, env = fake_github
    state = _state(labels=CANONICAL_LABELS[:-1])
    state["issues"]["1"]["labels"] = ["status/pr-open"]
    _write_state(state_path, state)

    result = _run_script(
        UPDATE_SCRIPT,
        [
            "-Repo", "owner/repo", "-IssueNumber", "1", "-Status", "blocked",
            "-Summary", "external approval pending",
        ],
        env,
    )

    assert result.returncode != 0
    output = re.sub(r"\s+", " ", result.stderr + result.stdout)
    assert "labels are never created" in output
    assert "automatically" in output
    after = _read_state(state_path)
    assert after["issues"]["1"]["labels"] == ["status/pr-open"]
    assert not any(call[:2] == ["label", "create"] for call in after["calls"])


def test_unsupported_blocked_transition_does_not_reopen_closed_issue(fake_github) -> None:
    state_path, _, env = fake_github
    state = _state(labels=CANONICAL_LABELS[:-1])
    state["issues"]["1"] = {"state": "CLOSED", "labels": ["status/pr-open"]}
    _write_state(state_path, state)

    result = _run_script(
        UPDATE_SCRIPT,
        [
            "-Repo", "owner/repo", "-IssueNumber", "1", "-Status", "blocked",
            "-Summary", "external approval pending",
        ],
        env,
    )

    assert result.returncode != 0
    after = _read_state(state_path)
    assert after["issues"]["1"] == {"state": "CLOSED", "labels": ["status/pr-open"]}
    assert not any(call[:2] == ["issue", "reopen"] for call in after["calls"])


def test_configured_alternate_vocabulary_removes_aliases(tmp_path: Path, fake_github) -> None:
    state_path, _, env = fake_github
    contract = json.loads(DEFAULT_CONTRACT.read_text(encoding="utf-8"))
    for definition in contract["states"].values():
        old_primary = definition["label"]
        colon_primary = old_primary.replace("status/", "status:")
        definition["label"] = colon_primary
        definition["aliases"] = [old_primary]
    contract_path = tmp_path / "colon-contract.json"
    contract_path.write_text(json.dumps(contract), encoding="utf-8")
    colon_labels = [definition["label"] for definition in contract["states"].values()]
    state = _state(labels=colon_labels)
    state["issues"]["1"]["labels"] = ["status/in-progress"]
    _write_state(state_path, state)

    result = _run_script(
        UPDATE_SCRIPT,
        [
            "-Repo", "owner/repo", "-IssueNumber", "1", "-Status", "blocked",
            "-Summary", "external approval pending", "-LabelContractPath", str(contract_path),
        ],
        env,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert _read_state(state_path)["issues"]["1"]["labels"] == ["status:blocked"]


def test_default_contract_accepts_repository_alias_vocabulary(fake_github) -> None:
    state_path, _, env = fake_github
    labels = [
        "status/in-progress",
        "status/fixed-locally",
        "status/pr-open",
        "status/merged-to-main",
        "status/blocked",
    ]
    state = _state(labels=labels)
    state["issues"]["1"]["labels"] = ["status/pr-open"]
    _write_state(state_path, state)

    result = _run_script(
        UPDATE_SCRIPT,
        [
            "-Repo", "owner/repo", "-IssueNumber", "1", "-Status", "fixed_local",
            "-CommitSha", "abc123", "-LocalValidationRef", "pytest passed",
        ],
        env,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    issue = _read_state(state_path)["issues"]["1"]
    assert issue["labels"] == ["status/fixed-locally"]


def test_audit_accepts_repository_alias_vocabulary_as_configured_state(fake_github) -> None:
    state_path, _, env = fake_github
    labels = [
        "status/in-progress",
        "status/fixed-locally",
        "status/pr-open",
        "status/merged-to-main",
    ]
    state = _state(labels=labels)
    state["issues"] = {
        "1": {"state": "CLOSED", "labels": ["status/merged-to-main"]},
        "2": {"state": "OPEN", "labels": ["status/pr-open"]},
    }
    _write_state(state_path, state)

    result = _run_script(AUDIT_SCRIPT, ["-Repo", "owner/repo"], env)

    assert result.returncode == 0, result.stderr + result.stdout
    payload = json.loads(result.stdout)
    assert payload["issueCount"] == 2
    assert payload["violationCount"] == 0


def test_failed_exact_main_validation_does_not_promote_issue(fake_github) -> None:
    state_path, _, env = fake_github
    state = _state()
    state["issues"]["1"]["labels"] = ["status/pr-open"]
    _write_state(state_path, state)
    sha = "a" * 40

    result = _run_script(
        UPDATE_SCRIPT,
        [
            "-Repo", "owner/repo", "-IssueNumber", "1", "-Status", "merged_main",
            "-PrNumber", "11", "-MainSha", sha,
            "-PrimaryValidationRunId", "103", "-SecurityValidationRunId", "102",
            "-WikiEvidence", "no change", "-BranchCleanupEvidence", "verified",
        ],
        env,
    )

    assert result.returncode != 0
    assert "must have conclusion success" in (result.stderr + result.stdout)
    assert _read_state(state_path)["issues"]["1"]["labels"] == ["status/pr-open"]


def test_merged_pending_main_reopens_github_auto_closed_issue(fake_github) -> None:
    state_path, _, env = fake_github
    state = _state()
    state["issues"]["1"] = {"state": "CLOSED", "labels": ["status/pr-open"]}
    _write_state(state_path, state)

    result = _run_script(
        UPDATE_SCRIPT,
        [
            "-Repo", "owner/repo", "-IssueNumber", "1",
            "-Status", "merged_pending_main_validation",
            "-PrNumber", "11", "-MainSha", "a" * 40,
        ],
        env,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert _read_state(state_path)["issues"]["1"] == {
        "state": "OPEN",
        "labels": ["status/in-progress"],
    }


def test_merged_main_replay_does_not_reopen_verified_closed_issue(fake_github) -> None:
    state_path, _, env = fake_github
    state = _state()
    state["issues"]["1"] = {"state": "CLOSED", "labels": ["status/merged-main"]}
    _write_state(state_path, state)

    result = _run_script(
        UPDATE_SCRIPT,
        [
            "-Repo", "owner/repo", "-IssueNumber", "1", "-Status", "merged_main",
            "-PrNumber", "11", "-MainSha", "a" * 40,
            "-PrimaryValidationRunId", "101", "-SecurityValidationRunId", "102",
            "-WikiEvidence", "explicit no-wiki-change",
            "-BranchCleanupEvidence", "verified clean",
        ],
        env,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert _read_state(state_path)["issues"]["1"] == {
        "state": "CLOSED",
        "labels": ["status/merged-main"],
    }


def test_qa_failure_reopens_and_returns_to_active_state(fake_github) -> None:
    state_path, _, env = fake_github
    state = _state()
    state["issues"]["1"] = {"state": "CLOSED", "labels": ["status/merged-main"]}
    _write_state(state_path, state)

    result = _run_script(
        UPDATE_SCRIPT,
        [
            "-Repo", "owner/repo", "-IssueNumber", "1", "-Status", "qa_failed",
            "-QaRunRef", "qa-44", "-Summary", "expected 200; received 500",
        ],
        env,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    issue = _read_state(state_path)["issues"]["1"]
    assert issue == {"state": "OPEN", "labels": ["status/in-progress"]}


def test_successful_main_proof_and_qa_close_retain_terminal_state(fake_github) -> None:
    state_path, _, env = fake_github
    state = _state()
    state["issues"]["1"]["labels"] = ["status/pr-open"]
    _write_state(state_path, state)
    sha = "a" * 40

    merged = _run_script(
        UPDATE_SCRIPT,
        [
            "-Repo", "owner/repo", "-IssueNumber", "1", "-Status", "merged_main",
            "-PrNumber", "11", "-MainSha", sha,
            "-PrimaryValidationRunId", "101", "-SecurityValidationRunId", "102",
            "-WikiEvidence", "explicit no-wiki-change", "-BranchCleanupEvidence", "verified clean",
        ],
        env,
    )
    after_merge = _read_state(state_path)
    after_merge["issues"]["1"]["labels"].extend(
        ["status/pr-open", "status:pr-open"]
    )
    _write_state(state_path, after_merge)
    closed = _run_script(
        UPDATE_SCRIPT,
        [
            "-Repo", "owner/repo", "-IssueNumber", "1", "-Status", "qa_passed_closed",
            "-QaRunRef", "qa-45",
        ],
        env,
    )

    assert merged.returncode == 0, merged.stderr + merged.stdout
    assert closed.returncode == 0, closed.stderr + closed.stdout
    issue = _read_state(state_path)["issues"]["1"]
    assert issue == {"state": "CLOSED", "labels": ["status/merged-main"]}


def test_batch_reconciliation_removes_every_prior_state_alias(fake_github) -> None:
    state_path, _, env = fake_github
    state = _state()
    state["issues"] = {
        "1": {"state": "OPEN", "labels": ["status:dev-in-progress", "status/pr-open"]},
        "2": {"state": "OPEN", "labels": ["status/fixed-locally", "status/blocked"]},
    }
    _write_state(state_path, state)

    result = _run_script(
        UPDATE_SCRIPT,
        [
            "-Repo", "owner/repo", "-IssueNumber", "1,2", "-Status", "fixed_local",
            "-CommitSha", "abc123", "-LocalValidationRef", "pytest passed",
        ],
        env,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    issues = _read_state(state_path)["issues"]
    assert issues["1"]["labels"] == ["status/fixed-local"]
    assert issues["2"]["labels"] == ["status/fixed-local"]


def test_audit_detects_lifecycle_and_vocabulary_drift(fake_github) -> None:
    state_path, _, env = fake_github
    labels = CANONICAL_LABELS + ["status:pr-open"]
    state = _state(labels=labels)
    state["issues"] = {
        "1": {"state": "CLOSED", "labels": ["status/pr-open"]},
        "2": {
            "state": "OPEN",
            "labels": ["status/merged-main", "status/pr-open", "status:pr-open"],
        },
    }
    _write_state(state_path, state)

    result = _run_script(AUDIT_SCRIPT, ["-Repo", "owner/repo"], env)

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    kinds = {item["kind"] for item in payload["violations"]}
    assert kinds == {
        "repository_alias_label_present",
        "closed_issue_has_active_label",
        "issue_has_multiple_lifecycle_labels",
        "issue_alias_label_present",
    }


@pytest.mark.parametrize(
    "powershell",
    POWERSHELL_EXECUTABLES or [None],
    ids=lambda executable: Path(executable).name if executable else "unavailable",
)
def test_audit_accepts_clean_closed_and_open_issue_states(fake_github, powershell) -> None:
    state_path, _, env = fake_github
    state = _state()
    state["issues"] = {
        "1": {"state": "CLOSED", "labels": ["status/merged-main"]},
        "2": {"state": "OPEN", "labels": ["status/blocked"]},
        "3": {"state": "OPEN", "labels": ["status/merged-main"]},
    }
    _write_state(state_path, state)

    result = _run_script(
        AUDIT_SCRIPT,
        ["-Repo", "owner/repo"],
        env,
        powershell=powershell,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    payload = json.loads(result.stdout)
    assert payload["issueCount"] == 3
    assert payload["violationCount"] == 0
