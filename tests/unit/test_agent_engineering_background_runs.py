from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = (
    ROOT
    / "platform-contracts"
    / "agent-engineering"
    / "engineering-task-ledger-contract.v1.json"
)


def _powershell() -> str:
    executable = shutil.which("powershell")
    if executable is None:
        pytest.skip("PowerShell is required for background-run automation tests")
    return executable


def _write_result(path: Path, exit_code: int) -> None:
    path.write_text(
        json.dumps(
            [
                {
                    "id": "platform-unit-check",
                    "repo": "lotus-platform",
                    "repoPath": str(ROOT),
                    "command": "unit",
                    "exitCode": exit_code,
                    "startedAt": "2026-04-21T00:00:00",
                    "finishedAt": "2026-04-21T00:00:01",
                    "durationSec": 1,
                    "output": "",
                }
            ]
        ),
        encoding="utf-8",
    )


def _assert_contract_required_fields(entry: dict[str, object]) -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    for field in contract["required_identity_fields"]:
        assert field in entry
    for field in contract["required_metadata_fields"]:
        assert field in entry


def test_check_background_runs_upgrades_legacy_state_to_task_ledger_shape(
    tmp_path: Path,
) -> None:
    result_path = tmp_path / "run.json"
    summary_path = tmp_path / "run.md"
    state_path = tmp_path / "background-runs.json"
    _write_result(result_path, exit_code=0)
    summary_path.write_text("# run", encoding="utf-8")
    state_path.write_text(
        json.dumps(
            [
                {
                    "pid": 999999,
                    "profile": "platform-unit",
                    "maxParallel": 2,
                    "runId": "20260421-000000",
                    "startedAt": "2026-04-21T00:00:00",
                    "status": "running",
                    "outLogPath": str(tmp_path / "run.out.log"),
                    "errLogPath": str(tmp_path / "run.err.log"),
                    "expectedResultPath": str(result_path),
                    "expectedSummaryPath": str(summary_path),
                }
            ]
        ),
        encoding="utf-8",
    )

    subprocess.run(
        [
            _powershell(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(ROOT / "automation" / "Check-Background-Runs.ps1"),
            "-StatePath",
            str(state_path),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    [entry] = json.loads(state_path.read_text(encoding="utf-8"))
    assert entry["engineering_task_id"] == "eng-task-20260421-000000-platform-unit"
    _assert_contract_required_fields(entry)
    assert entry["task_kind"] == "LOCAL_BACKGROUND_RUN"
    assert entry["repository"] == "lotus-platform"
    assert entry["correlation_ref"] == "20260421-000000-platform-unit"
    assert entry["status"] == "SUCCEEDED"
    assert entry["cleanup_state"] == "DONE"
    assert entry["runtime"]["runner"] == "automation/Run-Parallel-Tasks.ps1"
    assert entry["scope"] == {"profile": "platform-unit", "maxParallel": 2}
    assert {ref["type"] for ref in entry["evidence_refs"]} == {
        "LOG_FILE",
        "LOCAL_JSON_ARTIFACT",
        "LOCAL_MARKDOWN_ARTIFACT",
    }
    assert entry["ended_at"]
    assert entry["error_summary"] is None


def test_check_background_runs_marks_failed_result_artifact_truthfully(
    tmp_path: Path,
) -> None:
    result_path = tmp_path / "run.json"
    state_path = tmp_path / "background-runs.json"
    _write_result(result_path, exit_code=1)
    state_path.write_text(
        json.dumps(
            [
                {
                    "engineering_task_id": "eng-task-existing",
                    "task_kind": "LOCAL_BACKGROUND_RUN",
                    "repository": "lotus-platform",
                    "branch": "feature/test",
                    "owner": "tester",
                    "requested_at": "2026-04-21T00:00:00",
                    "origin": "automation/Start-Background-Run.ps1",
                    "correlation_ref": "existing",
                    "summary": "Background run for task profile 'platform-unit'",
                    "pid": 999999,
                    "profile": "platform-unit",
                    "maxParallel": 1,
                    "runId": "existing",
                    "startedAt": "2026-04-21T00:00:00",
                    "status": "RUNNING",
                    "runtime": {
                        "kind": "powershell",
                        "runner": "automation/Run-Parallel-Tasks.ps1",
                        "pid": 999999,
                    },
                    "scope": {"profile": "platform-unit", "maxParallel": 1},
                    "artifacts": [str(result_path)],
                    "evidence_refs": [
                        {"type": "LOCAL_JSON_ARTIFACT", "path": str(result_path)}
                    ],
                    "cleanup_state": "PENDING",
                    "outLogPath": str(tmp_path / "run.out.log"),
                    "errLogPath": str(tmp_path / "run.err.log"),
                    "expectedResultPath": str(result_path),
                    "expectedSummaryPath": str(tmp_path / "run.md"),
                }
            ]
        ),
        encoding="utf-8",
    )

    subprocess.run(
        [
            _powershell(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(ROOT / "automation" / "Check-Background-Runs.ps1"),
            "-StatePath",
            str(state_path),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    [entry] = json.loads(state_path.read_text(encoding="utf-8"))
    assert entry["engineering_task_id"] == "eng-task-existing"
    assert entry["status"] == "FAILED"
    assert entry["cleanup_state"] == "PENDING"
    assert entry["error_summary"] == (
        "Expected result artifact indicates failure or could not be parsed."
    )
