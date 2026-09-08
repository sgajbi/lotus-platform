"""The coverage audit must fail on the states it exists to detect.

This repository dispatched the releasability gate on `merge_commit_sha` alone,
so under rebase-only merging a PR of N commits gated one revision and left N-1
with no verdict. Measured before the fix: 268 commits on main over fourteen
days, 212 of them with no verdict-bearing run.

Nothing reported that, because *a run that is never created is not a failure*.
There is no red anywhere -- the absence is the defect, and only something that
looks for absence can see it.

So the audit is the watchdog, and a watchdog that passes while verifying
nothing is the same liveness defect one radius out. These cases pin the
fail-closed behaviour: unknown is not fine, a cancelled run is not a verdict,
and a truncated window is not the window.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from automation import audit_main_gate_coverage as audit

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "main-gate-coverage-audit.yml"

SHA_A = "a" * 40
SHA_B = "b" * 40


class _Completed:
    def __init__(self, stdout: str = "", returncode: int = 0) -> None:
        self.stdout = stdout
        self.returncode = returncode
        self.stderr = ""


def _install_transport(
    monkeypatch: pytest.MonkeyPatch,
    commits: list[str],
    runs_by_sha: dict[str, Any],
    *,
    gh_present: bool = True,
) -> None:
    """Fake the process transport, leaving the module's real logic in place.

    Argument construction, JSON parsing and return-code handling all still run;
    only the boundary is replaced. Stubbing `_run_conclusions` instead would
    leave exactly the code most likely to be wrong untested.
    """

    monkeypatch.setattr(
        audit.shutil, "which", lambda name: "/usr/bin/gh" if gh_present else None
    )

    def fake_run(command: list[str], **_: Any) -> _Completed:
        if command[0] == "git":
            return _Completed(stdout="".join(f"{line}\n" for line in commits))
        assert command[0] == "gh", command
        # Pin the real query shape: a different workflow name or a missing
        # --commit would audit something other than this commit's runs.
        assert "--workflow" in command and audit.WORKFLOW in command
        sha = command[command.index("--commit") + 1]
        entry = runs_by_sha.get(sha, [])
        if entry == "unfetchable":
            return _Completed(stdout="", returncode=1)
        return _Completed(stdout=json.dumps(entry))

    monkeypatch.setattr(subprocess, "run", fake_run)


def _commit_line(sha: str, subject: str = "some change") -> str:
    return f"{sha} {sha[:7]} {subject}"


def _audit(monkeypatch: pytest.MonkeyPatch, argv: list[str]) -> int:
    monkeypatch.setattr("sys.argv", ["audit_main_gate_coverage.py", *argv])
    return audit.main()


def test_full_coverage_passes(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_transport(
        monkeypatch,
        [_commit_line(SHA_A), _commit_line(SHA_B)],
        {
            SHA_A: [{"conclusion": "success", "status": "completed"}],
            SHA_B: [{"conclusion": "success", "status": "completed"}],
        },
    )

    assert _audit(monkeypatch, ["--fail-on-gap"]) == 0


def test_a_commit_with_no_run_fails_the_audit(monkeypatch: pytest.MonkeyPatch) -> None:
    """The measured state of this repository before the dispatcher was fixed."""
    _install_transport(
        monkeypatch,
        [_commit_line(SHA_A), _commit_line(SHA_B)],
        {SHA_A: [{"conclusion": "success", "status": "completed"}], SHA_B: []},
    )

    assert _audit(monkeypatch, ["--fail-on-gap"]) == 1


def test_a_cancelled_run_is_not_a_verdict(monkeypatch: pytest.MonkeyPatch) -> None:
    """A run that was cancelled evaluated nothing, and must not read as coverage.

    This is not hypothetical here: `Platform End-to-End Validation` has 99
    cancelled runs and zero successes (#647), and in any listing that counts
    runs rather than verdicts it looks like a lane that runs daily.
    """
    _install_transport(
        monkeypatch,
        [_commit_line(SHA_A)],
        {SHA_A: [{"conclusion": "cancelled", "status": "completed"}]},
    )

    assert _audit(monkeypatch, ["--fail-on-gap"]) == 1


def test_an_in_progress_run_is_pending_not_coverage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_transport(
        monkeypatch,
        [_commit_line(SHA_A)],
        {SHA_A: [{"conclusion": None, "status": "in_progress"}]},
    )

    assert _audit(monkeypatch, ["--fail-on-gap"]) == 1


def test_an_unfetchable_listing_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Rate limit, token scope, transient API failure: unverified, not fine."""
    _install_transport(
        monkeypatch, [_commit_line(SHA_A)], {SHA_A: "unfetchable"}
    )

    assert _audit(monkeypatch, ["--fail-on-gap"]) == 1


def test_a_missing_gh_binary_fails_rather_than_skipping(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A watchdog that skips when it cannot look is a watchdog that cannot fail."""
    _install_transport(monkeypatch, [_commit_line(SHA_A)], {}, gh_present=False)

    assert _audit(monkeypatch, ["--fail-on-gap"]) == 1
    assert _audit(monkeypatch, []) == 0


def test_a_truncated_window_is_not_the_window(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reaching the cap means older commits inside the span went unexamined.

    Every commit the audit *did* examine is fully covered here, so a check that
    only counted gaps would pass. The claim being made is about the window, and
    a prefix of it does not support that claim.
    """
    shas = [f"{index:040x}" for index in range(1, 4)]
    _install_transport(
        monkeypatch,
        [_commit_line(sha) for sha in shas],
        {sha: [{"conclusion": "success", "status": "completed"}] for sha in shas},
    )

    assert _audit(monkeypatch, ["--fail-on-gap", "--limit", "2"]) == 1


def test_a_failing_verdict_is_reported_but_does_not_fail_the_audit(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Coverage is the invariant; a red verdict is information beside it.

    A backfilled historical tree measured against today's environment can fail
    honestly. Conflating that with missing coverage would make the audit
    permanently red after any backfill, and a permanently red gate gets routed
    around -- which would cost the coverage guarantee entirely.
    """
    _install_transport(
        monkeypatch,
        [_commit_line(SHA_A, "a commit whose own tests fail")],
        {SHA_A: [{"conclusion": "failure", "status": "completed"}]},
    )

    assert _audit(monkeypatch, ["--fail-on-gap"]) == 0
    assert "FAILING" in capsys.readouterr().out


def test_the_window_is_filtered_not_stopped_at_the_first_older_commit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`--since` stops traversal; `--since-as-filter` visits and filters.

    With plain `--since`, a newer-dated commit sitting behind an older-dated
    ancestor is never visited, so its coverage is never examined and the audit
    reports a clean window it did not walk. Four of the nine sibling
    repositories carrying a copy of this script lack this flag.
    """
    captured: list[list[str]] = []
    real_run = subprocess.run

    def recording_run(command: list[str], **kwargs: Any) -> Any:
        if command and command[0] == "git":
            captured.append(command)
            return _Completed(stdout="")
        return real_run(command, **kwargs)

    monkeypatch.setattr(audit.shutil, "which", lambda name: "/usr/bin/gh")
    monkeypatch.setattr(subprocess, "run", recording_run)
    _audit(monkeypatch, [])

    assert captured, "the audit never asked git for the commit window"
    assert any("--since-as-filter=7 days ago" in part for part in captured[0])


def test_the_workflow_invokes_the_audit_bare(monkeypatch: pytest.MonkeyPatch) -> None:
    """Wiring, not logic: a correct audit dies in the step that runs it.

    Piping into a sink returns the sink's status, so the step passes while the
    audit fails on every run -- the cannot-fail defect the audit detects,
    reproduced in the audit's own wiring.
    """
    text = WORKFLOW.read_text(encoding="utf-8")
    invocation = [
        line.strip()
        for line in text.splitlines()
        if "audit_main_gate_coverage.py" in line
    ]

    assert invocation, "no workflow step invokes the audit"
    for line in invocation:
        assert "|" not in line, f"audit is piped and cannot fail the step: {line}"
        assert "--fail-on-gap" in line, f"audit runs in report-only mode: {line}"


def test_the_workflow_points_at_a_script_that_exists() -> None:
    """The path is repository-specific and is the half a lift gets wrong.

    Nine siblings keep this script under `scripts/`; this repository's
    convention is `automation/` -- 91 modules there and an empty `scripts/`,
    with every workflow invoking `python automation/...`. A copied path would
    reference nothing, and a step whose script is absent fails loudly here
    only because it is invoked bare.
    """
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "python automation/audit_main_gate_coverage.py" in text
    assert (ROOT / "automation" / "audit_main_gate_coverage.py").is_file()
