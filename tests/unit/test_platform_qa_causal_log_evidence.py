"""Behavioural proof that a log invariant is decided by a causal event.

These exercise `Get-CausalLogEvidence` in the shipped script through PowerShell,
with synthetic log windows. The two cases from #828 are the ones that matter:
`service` present in unrelated output must not prove anything, and `audit`
absent from a service nobody asked to audit must not be reported as a defect
without evidence that the request path was exercised.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "automation" / "Invoke-Platform-QA.ps1"
MARKER = "lotus-qa-20260907-031500-lotus-report-correlation"


def _powershell() -> str:
    executable = shutil.which("pwsh") or shutil.which("powershell")
    assert executable is not None, "pwsh or powershell is required for QA evidence tests"
    return executable


def _verdict(log_text: str, pattern: str, marker: str = MARKER) -> str:
    """Dot-source the shipped script and ask it about one log window.

    `-WhatIfPreview` is not available, so the script is dot-sourced inside a
    scriptblock guarded by a parameter that makes it define functions and stop.
    """
    command = (
        "$ErrorActionPreference='Stop';"
        f"$text = [Console]::In.ReadToEnd();"
        f"$src = Get-Content -Raw '{SCRIPT.as_posix()}';"
        "$start = $src.IndexOf('function Get-CausalLogEvidence');"
        "$end = $src.IndexOf('function Add-Finding');"
        "Invoke-Expression $src.Substring($start, $end - $start);"
        f"(Get-CausalLogEvidence -LogText $text -Marker '{marker}' -Pattern '{pattern}').verdict"
    )
    completed = subprocess.run(
        [_powershell(), "-NoProfile", "-Command", command],
        input=log_text,
        text=True,
        capture_output=True,
    )
    assert completed.returncode == 0, completed.stderr
    return completed.stdout.strip()


def test_an_unrelated_line_containing_the_pattern_proves_nothing() -> None:
    """`service` appears in almost every structured line.

    This is the silent pass the old check produced: the word was present in
    startup output, so the invariant was satisfied without the request path
    emitting anything at all.
    """
    startup_noise = (
        '{"event":"startup.complete","service":"lotus-report","level":"info"}\n'
        '{"event":"health.checked","service":"lotus-report","level":"info"}\n'
    )

    assert _verdict(startup_noise, "service") == "uncorrelated"


def test_a_correlated_line_matching_the_pattern_is_the_proof() -> None:
    """The paired acceptance: same pattern, now carried by the request's own event."""
    logs = (
        '{"event":"startup.complete","service":"lotus-report"}\n'
        f'{{"event":"request.completed","service":"lotus-report","correlation_id":"{MARKER}"}}\n'
    )

    assert _verdict(logs, "service") == "correlated"


def test_a_request_logged_without_the_pattern_is_reported_as_unmatched() -> None:
    """A real observability defect: the request was logged, and the field is absent.

    This is distinct from the request never being logged, and the distinction is
    the point -- one is a missing field, the other is a missing event.
    """
    logs = f'{{"event":"request.completed","correlation_id":"{MARKER}"}}\n'

    assert _verdict(logs, "latency_ms") == "unmatched"


def test_an_unexercised_path_is_uncorrelated_rather_than_a_defect() -> None:
    """#828's reproduction: `audit` absent from a service nobody asked to audit.

    The old check reported `logs-pattern-audit` against a healthy service. The
    verdict here is `uncorrelated`, which says the request was not exercised
    rather than that the service is defective.
    """
    healthy_but_unexercised = (
        '{"event":"startup.complete","service":"lotus-report"}\n'
        '{"event":"health.checked","service":"lotus-report"}\n'
    )

    assert _verdict(healthy_but_unexercised, "audit") == "uncorrelated"


def test_another_runs_marker_does_not_satisfy_this_run() -> None:
    """The marker is run-scoped, so a previous run's output cannot stand in."""
    previous_run = (
        '{"event":"request.completed","service":"lotus-report",'
        '"correlation_id":"lotus-qa-20260101-000000-lotus-report-correlation"}\n'
    )

    assert _verdict(previous_run, "service") == "uncorrelated"


def _matrix() -> dict:
    return json.loads((ROOT / "automation" / "qa-matrix.json").read_text(encoding="utf-8"))


def _invariants(repo: str) -> list:
    entry = next(item for item in _matrix()["repositories"] if item["repo"] == repo)
    return entry["checks"]["observability"]["required_log_patterns"]


@pytest.mark.parametrize(
    "repo",
    [
        "lotus-gateway",
        "lotus-advise",
        "lotus-performance",
        "lotus-core",
        "lotus-report",
        "lotus-render",
        "lotus-risk",
        "lotus-manage",
        "lotus-archive",
        "lotus-idea",
    ],
)
def test_every_probe_backed_invariant_carries_a_correlation_header(repo: str) -> None:
    """A probe without a marker cannot produce causal evidence."""
    for invariant in _invariants(repo):
        if isinstance(invariant, str):
            continue
        probe = invariant["probe"]

        assert probe["correlation_header"], invariant
        assert probe["method"] == "GET", (
            f"{repo}:{invariant['id']} must be provoked by a side-effect-free request"
        )


def test_domain_invariants_are_left_unproven_rather_than_given_a_false_probe() -> None:
    """A health request does not audit, render or score risk.

    Giving these a health probe would restore the keyword search under a better
    name: the probe would run, emit nothing relevant, and the invariant would
    fail for a reason unrelated to the service. Leaving them without a probe
    makes the validator name the gap instead.
    """
    unproven = {
        (repo, invariant)
        for repo in ("lotus-report", "lotus-render", "lotus-risk")
        for invariant in _invariants(repo)
        if isinstance(invariant, str)
    }

    assert unproven == {
        ("lotus-report", "audit"),
        ("lotus-render", "render"),
        ("lotus-risk", "risk"),
    }, unproven
