"""Execute the shipped fleet runner; source-text assertions cannot prove control flow."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "automation" / "Invoke-PlatformRepoChecks.ps1"
FIXTURES = ROOT / "tests" / "fixtures" / "fleet-runner"


def _run_fleet(tmp_path: Path, validators: list[tuple[str, Path]]) -> subprocess.CompletedProcess[str]:
    manifest = tmp_path / "validators.json"
    evidence = tmp_path / "evidence"
    manifest.write_text(
        json.dumps(
            {
                "validators": [
                    {"name": name, "arguments": [str(path)]}
                    for name, path in validators
                ]
            }
        ),
        encoding="utf-8",
    )
    return subprocess.run(
        [
            "pwsh",
            "-NoProfile",
            "-File",
            str(RUNNER),
            "-Lane",
            "fleet-conformance",
            "-FleetValidatorManifest",
            str(manifest),
            "-FleetEvidenceDirectory",
            str(evidence),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


@pytest.mark.skipif(shutil.which("pwsh") is None, reason="PowerShell is required for the shipped runner")
def test_fleet_runner_records_later_successes_after_an_early_failure(tmp_path: Path) -> None:
    """A first red validator must not hide later outcomes or their logs."""
    result = _run_fleet(
        tmp_path,
        [
            ("first-failure", FIXTURES / "fails.py"),
            ("second-success", FIXTURES / "succeeds.py"),
            ("third-success", FIXTURES / "succeeds.py"),
        ],
    )
    evidence = tmp_path / "evidence"

    assert result.returncode != 0
    assert "Fleet conformance failed: first-failure" in (result.stdout + result.stderr)
    assert (evidence / "first-failure.log").read_text(encoding="utf-8").strip() == "controlled early validator failure"
    assert (evidence / "second-success.log").read_text(encoding="utf-8").strip() == "controlled validator success"
    assert (evidence / "third-success.log").read_text(encoding="utf-8").strip() == "controlled validator success"
    summary = (evidence / "outcomes.md").read_text(encoding="utf-8")
    assert "| first-failure | 17 | FAIL |" in summary
    assert "| second-success | 0 | pass |" in summary
    assert "| third-success | 0 | pass |" in summary


@pytest.mark.skipif(shutil.which("pwsh") is None, reason="PowerShell is required for the shipped runner")
def test_fleet_runner_returns_success_only_when_every_validator_succeeds(tmp_path: Path) -> None:
    result = _run_fleet(
        tmp_path,
        [
            ("first-success", FIXTURES / "succeeds.py"),
            ("second-success", FIXTURES / "succeeds.py"),
        ],
    )
    summary = (tmp_path / "evidence" / "outcomes.md").read_text(encoding="utf-8")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "FAIL" not in summary
    assert "| first-success | 0 | pass |" in summary
    assert "| second-success | 0 | pass |" in summary


@pytest.mark.skipif(shutil.which("pwsh") is None, reason="PowerShell is required for the shipped runner")
def test_fleet_runner_rejects_duplicate_manifest_names_before_execution(tmp_path: Path) -> None:
    """A later result must never overwrite a failed result under the same key."""
    result = _run_fleet(
        tmp_path,
        [
            ("same-name", FIXTURES / "fails.py"),
            ("same-name", FIXTURES / "succeeds.py"),
        ],
    )

    assert result.returncode != 0
    assert "Fleet validator manifest contains duplicate name: same-name" in (
        result.stdout + result.stderr
    )
    assert not (tmp_path / "evidence" / "same-name.log").exists()
