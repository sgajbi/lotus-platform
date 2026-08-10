from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

import pytest

from automation import repository_background_task


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


def _run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    process_options = (
        {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
    )
    return subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        **process_options,
    )


def _initialize_repository(repository_path: Path) -> str:
    repository_path.mkdir(parents=True)
    assert (
        _run(
            ["git", "init", "--initial-branch", "main"], cwd=repository_path
        ).returncode
        == 0
    )
    assert (
        _run(
            ["git", "config", "user.email", "test@example.com"], cwd=repository_path
        ).returncode
        == 0
    )
    assert (
        _run(
            ["git", "config", "user.name", "Test User"], cwd=repository_path
        ).returncode
        == 0
    )
    script_path = repository_path / "scripts" / "task script.py"
    script_path.parent.mkdir(parents=True)
    script_path.write_text(
        """from pathlib import Path
import sys

mode, value = sys.argv[1:]
if mode == "fail":
    raise SystemExit(7)
if mode == "write":
    output = Path("result folder/result.txt")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(value, encoding="utf-8")
""",
        encoding="utf-8",
    )
    assert _run(["git", "add", "."], cwd=repository_path).returncode == 0
    assert (
        _run(["git", "commit", "-m", "test fixture"], cwd=repository_path).returncode
        == 0
    )
    return _run(["git", "rev-parse", "HEAD"], cwd=repository_path).stdout.strip()


def _repository_config(path: Path, repository_path: Path) -> None:
    path.write_text(
        json.dumps([{"name": "sandbox", "path": str(repository_path)}]),
        encoding="utf-8",
    )


def _wait_for_result(state_path: Path, *, timeout_seconds: float = 30) -> Path:
    deadline = time.monotonic() + timeout_seconds
    result_path: Path | None = None
    while time.monotonic() < deadline:
        if state_path.exists():
            entries = json.loads(state_path.read_text(encoding="utf-8"))
            if entries:
                result_path = Path(entries[-1]["expectedResultPath"])
                if result_path.exists():
                    return result_path
        time.sleep(0.1)
    raise AssertionError(f"Background result was not written: {result_path}")


def _start_repository_task(
    *,
    config_path: Path,
    state_path: Path,
    output_dir: Path,
    head: str,
    run_id: str,
    target_arguments: list[str],
    required_artifact: str | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [
        _powershell(),
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(ROOT / "automation" / "Start-Background-Run.ps1"),
        "-Repository",
        "sandbox",
        "-TargetType",
        "python",
        "-Target",
        "scripts/task script.py",
        "-ExpectedHead",
        head,
        "-RequireClean",
        "-ReposConfigPath",
        str(config_path),
        "-StatePath",
        str(state_path),
        "-OutputDir",
        str(output_dir),
        "-RunId",
        run_id,
        "-Owner",
        "unit-test",
    ]
    if target_arguments:
        command.extend(["-TargetArgumentsJson", json.dumps(target_arguments)])
    if required_artifact:
        command.extend(["-RequiredArtifact", required_artifact])
    return _run(command, cwd=ROOT)


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

    checked = _run(
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
    )
    assert checked.returncode == 0, checked.stderr

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
    assert entry["terminal_exit_code"] == 0


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

    checked = _run(
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
    )
    assert checked.returncode == 0, checked.stderr

    [entry] = json.loads(state_path.read_text(encoding="utf-8"))
    assert entry["engineering_task_id"] == "eng-task-existing"
    assert entry["status"] == "FAILED"
    assert entry["cleanup_state"] == "PENDING"
    assert entry["error_summary"] == (
        "Expected result artifact indicates failure or could not be parsed."
    )
    assert entry["terminal_exit_code"] == 1


def test_check_background_runs_flattens_legacy_wrapped_state_entries(
    tmp_path: Path,
) -> None:
    result_path = tmp_path / "run.json"
    state_path = tmp_path / "background-runs.json"
    _write_result(result_path, exit_code=0)
    state_path.write_text(
        json.dumps(
            [
                {
                    "value": [
                        {
                            "engineering_task_id": "eng-task-wrapped",
                            "task_kind": "LOCAL_BACKGROUND_RUN",
                            "repository": "lotus-platform",
                            "branch": "main",
                            "owner": "tester",
                            "requested_at": "2026-04-21T00:00:00",
                            "origin": "automation/Start-Background-Run.ps1",
                            "correlation_ref": "wrapped",
                            "summary": "wrapped historical state",
                            "pid": None,
                            "profile": "platform-unit",
                            "maxParallel": 1,
                            "runId": "wrapped",
                            "startedAt": "2026-04-21T00:00:00",
                            "status": "RUNNING",
                            "runtime": {
                                "kind": "powershell",
                                "runner": "automation/Run-Parallel-Tasks.ps1",
                                "pid": None,
                            },
                            "scope": {"profile": "platform-unit", "maxParallel": 1},
                            "artifacts": [str(result_path)],
                            "evidence_refs": [
                                {
                                    "type": "LOCAL_JSON_ARTIFACT",
                                    "path": str(result_path),
                                }
                            ],
                            "cleanup_state": "PENDING",
                            "expectedResultPath": str(result_path),
                            "expectedSummaryPath": None,
                        }
                    ],
                    "Count": 1,
                }
            ]
        ),
        encoding="utf-8",
    )

    checked = _run(
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
    )
    assert checked.returncode == 0, checked.stderr

    [entry] = json.loads(state_path.read_text(encoding="utf-8"))
    assert entry["engineering_task_id"] == "eng-task-wrapped"
    assert entry["status"] == "SUCCEEDED"
    assert entry["cleanup_state"] == "DONE"
    assert "value" not in entry
    _assert_contract_required_fields(entry)


def test_repository_target_passes_metacharacters_without_shell_interpolation(
    tmp_path: Path,
) -> None:
    repository_path = tmp_path / "repository with spaces"
    head = _initialize_repository(repository_path)
    config_path = tmp_path / "repos.json"
    state_path = tmp_path / "background-runs.json"
    output_dir = tmp_path / "task runs"
    _repository_config(config_path, repository_path)
    literal_argument = "portfolio=A&B; $(not-executed)"

    launched = _start_repository_task(
        config_path=config_path,
        state_path=state_path,
        output_dir=output_dir,
        head=head,
        run_id="repository-success",
        target_arguments=["write", literal_argument],
        required_artifact="result folder/result.txt",
    )

    assert launched.returncode == 0, launched.stderr
    result_path = _wait_for_result(state_path)
    checked = _run(
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
    )
    assert checked.returncode == 0, checked.stderr

    [entry] = json.loads(state_path.read_text(encoding="utf-8"))
    [result] = json.loads(result_path.read_text(encoding="utf-8"))
    assert entry["status"] == "SUCCEEDED"
    assert entry["repository"] == "sandbox"
    assert entry["branch"] == "main"
    assert entry["mode"] == "repository-target"
    assert entry["scope"]["commit_sha"] == head
    assert entry["scope"]["source_tree_state"] == "clean"
    assert entry["scope"]["target_arguments"] == ["write", literal_argument]
    assert entry["runtime"]["process_started_at"]
    assert entry["runtime"]["process_start_identity_state"] == "OBSERVED"
    assert entry["terminal_exit_code"] == 0
    assert entry["process_tree"] == result["process_tree"]
    assert result["process_tree"]["runner_pid"] > 0
    assert result["process_tree"]["target_pid"] > 0
    assert result["exitCode"] == 0
    assert result["command"] == {
        "target_type": "python",
        "target": "scripts/task script.py",
        "arguments": ["write", literal_argument],
    }
    assert (repository_path / "result folder" / "result.txt").read_text(
        encoding="utf-8"
    ) == literal_argument
    _assert_contract_required_fields(entry)


@pytest.mark.parametrize(
    ("target_arguments", "required_artifact", "expected_error"),
    [
        (["fail", "unused"], None, "exited with code 7"),
        (
            ["noop", "unused"],
            "missing/result.json",
            "Required artifacts were not produced",
        ),
    ],
)
def test_repository_target_records_command_and_artifact_failures(
    tmp_path: Path,
    target_arguments: list[str],
    required_artifact: str | None,
    expected_error: str,
) -> None:
    repository_path = tmp_path / "repository"
    head = _initialize_repository(repository_path)
    config_path = tmp_path / "repos.json"
    state_path = tmp_path / "background-runs.json"
    output_dir = tmp_path / "task-runs"
    _repository_config(config_path, repository_path)

    launched = _start_repository_task(
        config_path=config_path,
        state_path=state_path,
        output_dir=output_dir,
        head=head,
        run_id=f"repository-failure-{target_arguments[0]}",
        target_arguments=target_arguments,
        required_artifact=required_artifact,
    )

    assert launched.returncode == 0, launched.stderr
    result_path = _wait_for_result(state_path)
    [result] = json.loads(result_path.read_text(encoding="utf-8"))
    assert result["exitCode"] != 0
    assert expected_error in result["error_summary"]


def test_repository_target_rejects_unknown_repo_unsafe_target_and_parent_artifact(
    tmp_path: Path,
) -> None:
    repository_path = tmp_path / "repository"
    _initialize_repository(repository_path)
    config_path = tmp_path / "repos.json"
    _repository_config(config_path, repository_path)

    with pytest.raises(repository_background_task.BackgroundTaskError, match="found 0"):
        repository_background_task.resolve_repository(config_path, "missing")
    with pytest.raises(
        repository_background_task.BackgroundTaskError,
        match="unsupported characters",
    ):
        repository_background_task.build_command(
            repository_path, "make", "test & erase", []
        )
    with pytest.raises(
        repository_background_task.BackgroundTaskError,
        match="non-parent relative path",
    ):
        repository_background_task.validate_required_artifact_pattern("../outside.json")
    with pytest.raises(
        repository_background_task.BackgroundTaskError,
        match="existing file inside",
    ):
        repository_background_task.build_command(
            repository_path, "python", "scripts/missing.py", []
        )


def test_repository_target_rejects_source_fence_and_ledger_identity_drift() -> None:
    clean = repository_background_task.RepositoryIdentity(
        name="lotus-core",
        path=ROOT,
        branch="main",
        head="abc123",
        tree_state="clean",
    )
    dirty = repository_background_task.RepositoryIdentity(
        name="lotus-core",
        path=ROOT,
        branch="main",
        head="abc123",
        tree_state="dirty",
    )

    with pytest.raises(
        repository_background_task.BackgroundTaskError, match="Expected HEAD"
    ):
        repository_background_task.validate_launch_fences(
            clean, expected_head="different", require_clean=True
        )
    with pytest.raises(
        repository_background_task.BackgroundTaskError, match="not clean"
    ):
        repository_background_task.validate_launch_fences(
            dirty, expected_head="abc123", require_clean=True
        )
    with pytest.raises(
        repository_background_task.BackgroundTaskError, match="identity already"
    ):
        repository_background_task.validate_new_ledger_identity(
            [
                {
                    "engineering_task_id": "eng-task-1",
                    "correlation_ref": "run-1",
                    "pid": 10,
                }
            ],
            engineering_task_id="eng-task-1",
            correlation_ref="new-run",
        )
    with pytest.raises(
        repository_background_task.BackgroundTaskError, match="process id"
    ):
        repository_background_task.validate_new_ledger_identity(
            [
                {
                    "engineering_task_id": "eng-task-1",
                    "correlation_ref": "run-1",
                    "pid": 10,
                }
            ],
            engineering_task_id="eng-task-2",
            correlation_ref="run-2",
            process_id=10,
        )


def test_repository_target_rejects_duplicate_task_identity(tmp_path: Path) -> None:
    repository_path = tmp_path / "repository"
    head = _initialize_repository(repository_path)
    config_path = tmp_path / "repos.json"
    state_path = tmp_path / "background-runs.json"
    output_dir = tmp_path / "task-runs"
    _repository_config(config_path, repository_path)

    first = _start_repository_task(
        config_path=config_path,
        state_path=state_path,
        output_dir=output_dir,
        head=head,
        run_id="duplicate-identity",
        target_arguments=["noop", "unused"],
    )
    assert first.returncode == 0, first.stderr
    _wait_for_result(state_path)

    duplicate = _start_repository_task(
        config_path=config_path,
        state_path=state_path,
        output_dir=output_dir,
        head=head,
        run_id="duplicate-identity",
        target_arguments=["noop", "unused"],
    )

    assert duplicate.returncode == 2
    assert "already exists" in duplicate.stderr
    assert len(json.loads(state_path.read_text(encoding="utf-8"))) == 1


def test_check_background_runs_rejects_reused_pid_with_wrong_start_time(
    tmp_path: Path,
) -> None:
    state_path = tmp_path / "background-runs.json"
    state_path.write_text(
        json.dumps(
            [
                {
                    "engineering_task_id": "eng-task-stale-pid",
                    "task_kind": "VALIDATION_RUN",
                    "repository": "lotus-core",
                    "branch": "feature/test",
                    "owner": "tester",
                    "requested_at": "2026-04-21T00:00:00Z",
                    "origin": "test",
                    "correlation_ref": "stale-pid",
                    "summary": "stale pid",
                    "pid": os.getpid(),
                    "profile": None,
                    "display_name": "lotus-core/make/check",
                    "mode": "repository-target",
                    "runId": "stale-pid",
                    "startedAt": "2026-04-21T00:00:00Z",
                    "status": "RUNNING",
                    "runtime": {
                        "kind": "python",
                        "runner": "automation/repository_background_task.py",
                        "pid": os.getpid(),
                        "process_started_at": "2000-01-01T00:00:00Z",
                    },
                    "scope": {"target_type": "make", "target": "check"},
                    "artifacts": [],
                    "evidence_refs": [],
                    "cleanup_state": "PENDING",
                    "expectedResultPath": str(tmp_path / "absent.json"),
                    "expectedSummaryPath": None,
                }
            ]
        ),
        encoding="utf-8",
    )

    checked = _run(
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
    )
    assert checked.returncode == 0, checked.stderr

    [entry] = json.loads(state_path.read_text(encoding="utf-8"))
    assert entry["status"] == "LOST"
    assert entry["error_summary"] == (
        "Process ended before the expected result artifact was written."
    )


def test_check_background_runs_preserves_live_pid_with_deserialized_datetime(
    tmp_path: Path,
) -> None:
    process_options = (
        {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
    )
    sleeper = subprocess.Popen(
        [_powershell(), "-NoProfile", "-Command", "Start-Sleep -Seconds 30"],
        cwd=ROOT,
        **process_options,
    )
    try:
        state_path = tmp_path / "background-runs.json"
        started_at = datetime.now().astimezone().isoformat()
        state_path.write_text(
            json.dumps(
                [
                    {
                        "engineering_task_id": "eng-task-live-pid",
                        "task_kind": "VALIDATION_RUN",
                        "repository": "lotus-core",
                        "branch": "feature/test",
                        "owner": "tester",
                        "requested_at": started_at,
                        "origin": "test",
                        "correlation_ref": "live-pid",
                        "summary": "live pid",
                        "pid": sleeper.pid,
                        "profile": None,
                        "display_name": "lotus-core/make/check",
                        "mode": "repository-target",
                        "runId": "live-pid",
                        "startedAt": started_at,
                        "status": "RUNNING",
                        "runtime": {
                            "kind": "python",
                            "runner": "automation/repository_background_task.py",
                            "pid": sleeper.pid,
                            "process_started_at": started_at,
                        },
                        "scope": {"target_type": "make", "target": "check"},
                        "artifacts": [],
                        "evidence_refs": [],
                        "cleanup_state": "PENDING",
                        "expectedResultPath": str(tmp_path / "absent.json"),
                        "expectedSummaryPath": None,
                    }
                ]
            ),
            encoding="utf-8",
        )

        checked = _run(
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
        )
        assert checked.returncode == 0, checked.stderr

        [entry] = json.loads(state_path.read_text(encoding="utf-8"))
        assert entry["status"] == "RUNNING"
        assert entry["ended_at"] is None
        assert entry["error_summary"] is None
    finally:
        sleeper.terminate()
        sleeper.wait(timeout=10)


def test_repository_target_mode_is_documented_as_typed_and_shell_free() -> None:
    launcher = (ROOT / "automation" / "Start-Background-Run.ps1").read_text(
        encoding="utf-8"
    )
    runner = (ROOT / "automation" / "repository_background_task.py").read_text(
        encoding="utf-8"
    )
    playbook = (
        ROOT / "context" / "playbooks" / "AGENT-CONTEXT-AND-TASK-LEDGER.md"
    ).read_text(encoding="utf-8")
    skill = (
        ROOT / "codex" / "skills" / "platform-automation-ops" / "SKILL.md"
    ).read_text(encoding="utf-8")

    assert 'ParameterSetName = "RepositoryTarget"' in launcher
    assert 'ValidateSet("make", "npm", "python", "powershell")' in launcher
    assert "TargetArgumentsJson" in launcher
    assert "cmd /c" not in runner
    assert "shell=True" not in runner
    assert "argv" in playbook
    assert "Do not pass a shell command" in skill
