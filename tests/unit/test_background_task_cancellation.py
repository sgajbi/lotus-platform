from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Sequence

import pytest

from automation import background_task_cancellation as cancellation


ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 8, 10, 12, 0, 0, tzinfo=UTC)


class FakeProcessController:
    def __init__(
        self,
        tree: Sequence[cancellation.ObservedProcess],
        termination: cancellation.ProcessTermination | None = None,
    ) -> None:
        self.tree = tuple(tree)
        self.termination = termination or cancellation.ProcessTermination(
            disposition="TERMINATED",
            strategy="fake-owned-tree",
            requested_pids=tuple(item.pid for item in tree),
            terminated_pids=tuple(item.pid for item in tree),
            remaining_owned_pids=(),
            detail="owned process tree terminated",
        )
        self.inspected: list[int] = []
        self.terminated: list[tuple[int, ...]] = []

    def inspect_tree(self, root_pid: int) -> tuple[cancellation.ObservedProcess, ...]:
        self.inspected.append(root_pid)
        return self.tree if self.tree and self.tree[0].pid == root_pid else ()

    def terminate_tree(
        self, expected_tree: Sequence[cancellation.ObservedProcess]
    ) -> cancellation.ProcessTermination:
        self.terminated.append(tuple(item.pid for item in expected_tree))
        return self.termination


class FakeComposeController:
    def __init__(
        self, outcomes: dict[str, cancellation.ComposeCleanup] | None = None
    ) -> None:
        self.outcomes = outcomes or {}
        self.requested: list[cancellation.ComposeProject] = []

    def cleanup(
        self, project: cancellation.ComposeProject
    ) -> cancellation.ComposeCleanup:
        self.requested.append(project)
        return self.outcomes[project.project_name]


def _entry(
    *,
    mode: str,
    cleanup_contract: dict[str, object],
    task_id: str = "eng-task-target",
    pid: int = 4100,
    started_at: datetime = NOW,
) -> dict[str, object]:
    profile = "fast-feedback" if mode == "profile" else None
    return {
        "engineering_task_id": task_id,
        "task_kind": (
            "LOCAL_BACKGROUND_RUN" if mode == "profile" else "VALIDATION_RUN"
        ),
        "repository": "lotus-platform" if mode == "profile" else "lotus-core",
        "branch": "feature/test",
        "owner": "unit-test",
        "requested_at": started_at.isoformat(),
        "origin": "unit-test",
        "correlation_ref": task_id.removeprefix("eng-task-"),
        "summary": "test task",
        "pid": pid,
        "profile": profile,
        "display_name": f"task/{task_id}",
        "mode": mode,
        "runId": "test",
        "started_at": started_at.isoformat(),
        "startedAt": started_at.isoformat(),
        "status": "RUNNING",
        "runtime": {
            "kind": "powershell" if mode == "profile" else "python",
            "runner": "unit-test",
            "pid": pid,
            "process_started_at": started_at.isoformat(),
        },
        "scope": {"cleanup_contract": cleanup_contract},
        "artifacts": [],
        "evidence_refs": [],
        "cleanup_state": "PENDING",
        "expectedResultPath": None,
        "expectedSummaryPath": None,
    }


def _write_ledger(path: Path, entries: Sequence[dict[str, object]]) -> None:
    path.write_text(json.dumps(list(entries)), encoding="utf-8")


def _cancel(
    tmp_path: Path,
    *,
    entries: Sequence[dict[str, object]],
    processes: FakeProcessController,
    compose: FakeComposeController | None = None,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    state_path = tmp_path / "background-runs.json"
    receipt_dir = tmp_path / "receipts"
    _write_ledger(state_path, entries)
    receipt = cancellation.cancel_background_task(
        state_path=state_path,
        receipt_dir=receipt_dir,
        engineering_task_id="eng-task-target",
        reason="operator requested bounded cancellation",
        actor="agent-1",
        process_controller=processes,
        compose_controller=compose or FakeComposeController(),
        now=lambda: NOW,
    )
    return receipt, json.loads(state_path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("mode", ["profile", "repository-target"])
def test_exact_task_cancellation_supports_both_launcher_modes(
    tmp_path: Path, mode: str
) -> None:
    root = cancellation.ObservedProcess(4100, 100, NOW)
    child = cancellation.ObservedProcess(4101, 4100, NOW)
    process_controller = FakeProcessController((root, child))
    target = _entry(
        mode=mode,
        cleanup_contract={
            "ownership_state": "NONE",
            "compose_projects": [],
            "source_plan": None,
        },
    )
    unrelated = _entry(
        mode="repository-target",
        cleanup_contract={"ownership_state": "UNKNOWN", "compose_projects": []},
        task_id="eng-task-unrelated",
        pid=5100,
    )

    receipt, entries = _cancel(
        tmp_path, entries=[unrelated, target], processes=process_controller
    )

    assert entries[0] == unrelated
    cancelled = entries[1]
    assert cancelled["status"] == "CANCELLED"
    assert cancelled["cleanup_state"] == "DONE"
    assert cancelled["ended_at"] == NOW.isoformat()
    assert process_controller.inspected == [4100]
    assert process_controller.terminated == [(4100, 4101)]
    assert receipt["counts"] == {
        "process_targets": 2,
        "process_terminated": 2,
        "process_remaining": 0,
        "compose_projects_declared": 0,
        "compose_projects_attempted": 0,
        "compose_projects_clean": 0,
        "compose_resources_before": 0,
        "compose_resources_removed": 0,
        "compose_resources_remaining": 0,
    }
    receipt_path = Path(cancelled["cancellation"]["receipt_path"])
    assert (
        json.loads(receipt_path.read_text(encoding="utf-8"))["engineering_task_id"]
        == "eng-task-target"
    )


def test_vanished_task_remains_lost_and_external_cleanup_is_not_run(
    tmp_path: Path,
) -> None:
    compose_file = tmp_path / "compose.yml"
    compose_file.write_text("services: {}\n", encoding="utf-8")
    compose = FakeComposeController()
    receipt, [entry] = _cancel(
        tmp_path,
        entries=[
            _entry(
                mode="repository-target",
                cleanup_contract={
                    "ownership_state": "COMPOSE",
                    "compose_projects": [
                        {
                            "project_name": "owned-project",
                            "working_directory": str(tmp_path),
                            "compose_files": [str(compose_file)],
                        }
                    ],
                },
            )
        ],
        processes=FakeProcessController(()),
        compose=compose,
    )

    assert entry["status"] == "LOST"
    assert entry["cleanup_state"] == "BLOCKED"
    assert receipt["outcomes"]["process"]["disposition"] == "VANISHED"
    assert compose.requested == []


def test_reused_pid_is_not_terminated(tmp_path: Path) -> None:
    reused = cancellation.ObservedProcess(
        4100, 100, datetime(2026, 8, 10, 13, 0, 0, tzinfo=UTC)
    )
    processes = FakeProcessController((reused,))

    receipt, [entry] = _cancel(
        tmp_path,
        entries=[
            _entry(
                mode="profile",
                cleanup_contract={"ownership_state": "NONE", "compose_projects": []},
            )
        ],
        processes=processes,
    )

    assert entry["status"] == "LOST"
    assert entry["cleanup_state"] == "BLOCKED"
    assert processes.terminated == []
    assert receipt["outcomes"]["process"]["disposition"] == "OWNERSHIP_MISMATCH"


def test_unknown_launch_cleanup_provenance_cannot_be_marked_done(
    tmp_path: Path,
) -> None:
    root = cancellation.ObservedProcess(4100, 100, NOW)
    receipt, [entry] = _cancel(
        tmp_path,
        entries=[
            _entry(
                mode="repository-target",
                cleanup_contract={
                    "ownership_state": "UNKNOWN",
                    "compose_projects": [],
                },
            )
        ],
        processes=FakeProcessController((root,)),
    )

    assert entry["status"] == "CANCELLED"
    assert entry["cleanup_state"] == "BLOCKED"
    assert "did not declare" in receipt["outcomes"]["cleanup_detail"]


def test_declared_compose_cleanup_does_not_touch_unrelated_project(
    tmp_path: Path,
) -> None:
    compose_file = tmp_path / "compose.yml"
    compose_file.write_text("services: {}\n", encoding="utf-8")
    owned_outcome = cancellation.ComposeCleanup(
        project_name="owned-project",
        disposition="CLEANED",
        passed=True,
        before={"containers": 2, "volumes": 1, "networks": 1, "total": 4},
        after={"containers": 0, "volumes": 0, "networks": 0, "total": 0},
        command=("docker", "compose", "--project-name", "owned-project", "down"),
        detail="exact project cleaned",
    )
    compose = FakeComposeController({"owned-project": owned_outcome})
    root = cancellation.ObservedProcess(4100, 100, NOW)
    cleanup_contract = {
        "ownership_state": "COMPOSE",
        "compose_projects": [
            {
                "project_name": "owned-project",
                "working_directory": str(tmp_path),
                "compose_files": [str(compose_file)],
            }
        ],
        "source_plan": str(tmp_path / "cleanup-plan.json"),
    }

    receipt, [entry] = _cancel(
        tmp_path,
        entries=[_entry(mode="repository-target", cleanup_contract=cleanup_contract)],
        processes=FakeProcessController((root,)),
        compose=compose,
    )

    assert [project.project_name for project in compose.requested] == ["owned-project"]
    assert "unrelated-project" not in json.dumps(receipt)
    assert entry["status"] == "CANCELLED"
    assert entry["cleanup_state"] == "DONE"
    assert receipt["counts"]["compose_resources_removed"] == 4


def test_compose_cleanup_failure_is_terminal_but_not_clean(
    tmp_path: Path,
) -> None:
    compose_file = tmp_path / "compose.yml"
    compose_file.write_text("services: {}\n", encoding="utf-8")
    blocked = cancellation.ComposeCleanup(
        project_name="owned-project",
        disposition="PROVENANCE_BLOCKED",
        passed=False,
        before={"containers": 0, "volumes": 1, "networks": 0, "total": 1},
        after={"containers": 0, "volumes": 1, "networks": 0, "total": 1},
        command=(),
        detail="no live container provenance",
    )
    compose = FakeComposeController({"owned-project": blocked})
    root = cancellation.ObservedProcess(4100, 100, NOW)
    receipt, [entry] = _cancel(
        tmp_path,
        entries=[
            _entry(
                mode="repository-target",
                cleanup_contract={
                    "ownership_state": "COMPOSE",
                    "compose_projects": [
                        {
                            "project_name": "owned-project",
                            "working_directory": str(tmp_path),
                            "compose_files": [str(compose_file)],
                        }
                    ],
                },
            )
        ],
        processes=FakeProcessController((root,)),
        compose=compose,
    )

    assert entry["status"] == "CANCELLED"
    assert entry["cleanup_state"] == "BLOCKED"
    assert receipt["counts"]["compose_resources_remaining"] == 1


def test_cleanup_plan_requires_exact_repository_root_and_existing_files(
    tmp_path: Path,
) -> None:
    repository_root = tmp_path / "repo"
    repository_root.mkdir()
    compose_file = repository_root / "compose.yml"
    compose_file.write_text("services: {}\n", encoding="utf-8")
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(
        json.dumps(
            {
                "schema_version": "lotus.background-task-compose-cleanup-plan.v1",
                "projects": [
                    {
                        "project_name": "owned-project",
                        "working_directory": str(repository_root),
                        "compose_files": ["compose.yml"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    contract = cancellation.build_cleanup_contract(
        plan_path=plan_path,
        no_external_cleanup_required=False,
        allowed_repository_root=repository_root,
    )

    assert contract["ownership_state"] == "COMPOSE"
    assert contract["compose_projects"][0]["compose_files"] == (str(compose_file),)
    with pytest.raises(cancellation.CancellationError, match="exact task repository"):
        cancellation.build_cleanup_contract(
            plan_path=plan_path,
            no_external_cleanup_required=False,
            allowed_repository_root=tmp_path / "other",
        )


@pytest.mark.skipif(os.name != "nt", reason="Windows process-tree strategy")
def test_windows_termination_uses_taskkill_tree_without_shell(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    controller = cancellation.SystemProcessController()
    root = cancellation.ObservedProcess(4100, 100, NOW)
    child = cancellation.ObservedProcess(4101, 4100, NOW)
    inventories = iter(((root, child), ()))
    monkeypatch.setattr(controller, "_all_processes", lambda: next(inventories))
    commands: list[list[str]] = []

    def fake_run(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
        commands.append(list(command))
        return subprocess.CompletedProcess(command, 0, stdout="SUCCESS", stderr="")

    monkeypatch.setattr(controller, "_run", fake_run)
    monkeypatch.setattr(cancellation.time, "sleep", lambda _: None)

    outcome = controller.terminate_tree((root, child))

    assert commands == [["taskkill.exe", "/PID", "4100", "/T", "/F"]]
    assert outcome.passed
    assert outcome.strategy == "windows-taskkill-tree"


@pytest.mark.skipif(os.name != "nt", reason="Windows process-tree strategy")
def test_windows_termination_detects_reparented_owned_descendant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    controller = cancellation.SystemProcessController()
    root = cancellation.ObservedProcess(4100, 100, NOW)
    child = cancellation.ObservedProcess(4101, 4100, NOW)
    reparented_child = cancellation.ObservedProcess(4101, 1, NOW)
    inventories = iter(((root, child), (reparented_child,)))
    monkeypatch.setattr(controller, "_all_processes", lambda: next(inventories))
    monkeypatch.setattr(
        controller,
        "_run",
        lambda command: subprocess.CompletedProcess(
            command, 0, stdout="SUCCESS", stderr=""
        ),
    )
    monkeypatch.setattr(cancellation.time, "sleep", lambda _: None)

    outcome = controller.terminate_tree((root, child))

    assert not outcome.passed
    assert outcome.disposition == "TERMINATION_FAILED"
    assert outcome.terminated_pids == (4100,)
    assert outcome.remaining_owned_pids == (4101,)


@pytest.mark.skipif(os.name != "nt", reason="Windows process-tree strategy")
def test_windows_termination_retains_descendant_missing_from_second_tree_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    controller = cancellation.SystemProcessController()
    root = cancellation.ObservedProcess(4100, 100, NOW)
    child = cancellation.ObservedProcess(4101, 4100, NOW)
    reparented_child = cancellation.ObservedProcess(4101, 1, NOW)
    inventories = iter(((root,), (reparented_child,)))
    monkeypatch.setattr(controller, "_all_processes", lambda: next(inventories))
    monkeypatch.setattr(
        controller,
        "_run",
        lambda command: subprocess.CompletedProcess(
            command, 0, stdout="SUCCESS", stderr=""
        ),
    )
    monkeypatch.setattr(cancellation.time, "sleep", lambda _: None)

    outcome = controller.terminate_tree((root, child))

    assert outcome.requested_pids == (4100, 4101)
    assert outcome.disposition == "TERMINATION_FAILED"
    assert outcome.terminated_pids == (4100,)
    assert outcome.remaining_owned_pids == (4101,)


def test_docker_adapter_uses_only_exact_project_command(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    compose_file = tmp_path / "compose.yml"
    compose_file.write_text("services: {}\n", encoding="utf-8")
    project = cancellation.ComposeProject(
        "owned-project", str(tmp_path), (str(compose_file),)
    )
    controller = cancellation.DockerComposeController()
    inventories = iter(
        (
            cancellation.ComposeInventory(
                ("container-1",), ("volume-1",), ("network-1",)
            ),
            cancellation.ComposeInventory((), (), ()),
        )
    )
    monkeypatch.setattr(controller, "_inventory", lambda _: next(inventories))
    monkeypatch.setattr(
        controller,
        "_verify_container_provenance",
        lambda declared, containers: (True, "verified"),
    )
    commands: list[list[str]] = []

    def fake_run(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
        commands.append(list(command))
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(controller, "_run", fake_run)

    outcome = controller.cleanup(project)

    assert outcome.passed
    assert len(commands) == 1
    assert commands[0] == [
        "docker",
        "compose",
        "--project-name",
        "owned-project",
        "--project-directory",
        str(tmp_path),
        "--file",
        str(compose_file),
        "down",
        "--remove-orphans",
        "--volumes",
    ]
    assert "unrelated-project" not in commands[0]
    assert "prune" not in commands[0]


def _powershell() -> str:
    executable = shutil.which("powershell")
    if executable is None:
        pytest.skip("PowerShell is required")
    return executable


def test_checker_preserves_cancelled_status_and_cleanup_receipt(tmp_path: Path) -> None:
    state_path = tmp_path / "background-runs.json"
    entry = _entry(
        mode="repository-target",
        cleanup_contract={"ownership_state": "NONE", "compose_projects": []},
    )
    entry["status"] = "CANCELLED"
    entry["cleanup_state"] = "DONE"
    entry["ended_at"] = NOW.isoformat()
    entry["error_summary"] = "Cancelled by unit-test: no longer required"
    entry["cancellation"] = {"receipt_path": str(tmp_path / "receipt.json")}
    _write_ledger(state_path, [entry])
    process_options = (
        {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
    )

    checked = subprocess.run(
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
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        **process_options,
    )

    assert checked.returncode == 0, checked.stderr
    [reconciled] = json.loads(state_path.read_text(encoding="utf-8"))
    assert reconciled["status"] == "CANCELLED"
    assert reconciled["cleanup_state"] == "DONE"
    assert reconciled["error_summary"] == entry["error_summary"]
    assert reconciled["cancellation"] == entry["cancellation"]


def test_checker_defers_when_cancellation_holds_ledger_lock(tmp_path: Path) -> None:
    state_path = tmp_path / "background-runs.json"
    entry = _entry(
        mode="repository-target",
        cleanup_contract={"ownership_state": "NONE", "compose_projects": []},
    )
    _write_ledger(state_path, [entry])
    original = state_path.read_bytes()
    state_path.with_suffix(".json.lock").write_text("pid=99999\n", encoding="utf-8")
    process_options = (
        {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
    )

    checked = subprocess.run(
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
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        **process_options,
    )

    assert checked.returncode == 0, checked.stderr
    assert "reconciliation deferred" in checked.stdout
    assert state_path.read_bytes() == original
