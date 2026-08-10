"""Governed cancellation for RFC-0094 local background tasks.

Cancellation is an exact task-ledger operation.  It verifies the recorded root process identity
before terminating the owned process tree and only performs Docker Compose cleanup from provenance
declared when the task was launched.  Caller-provided names are never used to discover resources.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import signal
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping, Protocol, Sequence


TASK_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
COMPOSE_PROJECT_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
TERMINAL_STATES = frozenset(
    {"SUCCEEDED", "FAILED", "TIMED_OUT", "CANCELLED", "LOST", "SUPERSEDED"}
)


class CancellationError(RuntimeError):
    """Raised when a cancellation request violates the ownership contract."""


@dataclass(frozen=True)
class ObservedProcess:
    pid: int
    parent_pid: int
    started_at: datetime


@dataclass(frozen=True)
class ProcessTermination:
    disposition: str
    strategy: str
    requested_pids: tuple[int, ...]
    terminated_pids: tuple[int, ...]
    remaining_owned_pids: tuple[int, ...]
    detail: str

    @property
    def passed(self) -> bool:
        return self.disposition == "TERMINATED" and not self.remaining_owned_pids


@dataclass(frozen=True)
class ComposeProject:
    project_name: str
    working_directory: str
    compose_files: tuple[str, ...]


@dataclass(frozen=True)
class ComposeInventory:
    containers: tuple[str, ...]
    volumes: tuple[str, ...]
    networks: tuple[str, ...]

    @property
    def total(self) -> int:
        return len(self.containers) + len(self.volumes) + len(self.networks)

    def counts(self) -> dict[str, int]:
        return {
            "containers": len(self.containers),
            "volumes": len(self.volumes),
            "networks": len(self.networks),
            "total": self.total,
        }


@dataclass(frozen=True)
class ComposeCleanup:
    project_name: str
    disposition: str
    passed: bool
    before: Mapping[str, int]
    after: Mapping[str, int]
    command: tuple[str, ...]
    detail: str


class ProcessController(Protocol):
    def inspect_tree(self, root_pid: int) -> tuple[ObservedProcess, ...]: ...

    def terminate_tree(
        self, expected_tree: Sequence[ObservedProcess]
    ) -> ProcessTermination: ...


class ComposeController(Protocol):
    def cleanup(self, project: ComposeProject) -> ComposeCleanup: ...


def _hidden_process_options() -> dict[str, Any]:
    if os.name == "nt":
        return {"creationflags": subprocess.CREATE_NO_WINDOW}
    return {}


def _parse_timestamp(value: object) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str) and value.strip():
        normalized = value.strip().replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError as exc:
            raise CancellationError(
                f"Invalid process start timestamp: {value!r}"
            ) from exc
    else:
        raise CancellationError("Task runtime has no process start timestamp")
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _same_process_start(actual: datetime, expected: datetime) -> bool:
    return actual.astimezone(UTC) == expected.astimezone(UTC)


class SystemProcessController:
    """Inspect and terminate only the process tree rooted at a verified PID."""

    def _run(self, command: Sequence[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            list(command),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            **_hidden_process_options(),
        )

    def _windows_processes(self) -> tuple[ObservedProcess, ...]:
        powershell = "powershell" if os.name == "nt" else "pwsh"
        script = (
            "Get-CimInstance Win32_Process | Where-Object { $_.CreationDate } | "
            "ForEach-Object { "
            "[pscustomobject]@{pid=[int]$_.ProcessId; "
            "parent_pid=[int]$_.ParentProcessId; "
            "started_at=$_.CreationDate.ToUniversalTime().ToString('o')} } | "
            "ConvertTo-Json -Compress"
        )
        completed = self._run(
            [powershell, "-NoProfile", "-NonInteractive", "-Command", script]
        )
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip()
            raise CancellationError(
                f"Cannot inspect Windows process ownership: {detail}"
            )
        if not completed.stdout.strip():
            return ()
        raw = json.loads(completed.stdout)
        rows = raw if isinstance(raw, list) else [raw]
        return tuple(
            ObservedProcess(
                pid=int(row["pid"]),
                parent_pid=int(row["parent_pid"]),
                started_at=_parse_timestamp(row["started_at"]),
            )
            for row in rows
        )

    @staticmethod
    def _linux_processes() -> tuple[ObservedProcess, ...]:
        proc_root = Path("/proc")
        stat_path = proc_root / "stat"
        if not stat_path.is_file():
            raise CancellationError(
                "Process ownership inspection is unsupported on this host"
            )
        boot_line = next(
            (
                line
                for line in stat_path.read_text(encoding="utf-8").splitlines()
                if line.startswith("btime ")
            ),
            None,
        )
        if boot_line is None:
            raise CancellationError("Linux boot time is unavailable")
        boot_seconds = float(boot_line.split()[1])
        clock_ticks = os.sysconf("SC_CLK_TCK")
        observed: list[ObservedProcess] = []
        for candidate in proc_root.iterdir():
            if not candidate.name.isdigit():
                continue
            try:
                stat = (candidate / "stat").read_text(encoding="utf-8")
                closing = stat.rfind(")")
                fields = stat[closing + 2 :].split()
                parent_pid = int(fields[1])
                start_ticks = int(fields[19])
                observed.append(
                    ObservedProcess(
                        pid=int(candidate.name),
                        parent_pid=parent_pid,
                        started_at=datetime.fromtimestamp(
                            boot_seconds + (start_ticks / clock_ticks), tz=UTC
                        ),
                    )
                )
            except (FileNotFoundError, PermissionError, ValueError, IndexError):
                continue
        return tuple(observed)

    def _all_processes(self) -> tuple[ObservedProcess, ...]:
        if os.name == "nt":
            return self._windows_processes()
        return self._linux_processes()

    def inspect_tree(self, root_pid: int) -> tuple[ObservedProcess, ...]:
        processes = {process.pid: process for process in self._all_processes()}
        root = processes.get(root_pid)
        if root is None:
            return ()
        selected = {root_pid}
        changed = True
        while changed:
            changed = False
            for process in processes.values():
                if process.pid not in selected and process.parent_pid in selected:
                    selected.add(process.pid)
                    changed = True
        descendants = sorted(selected - {root_pid})
        return (root, *(processes[pid] for pid in descendants))

    def _inspect_owned_processes(
        self, expected: Sequence[ObservedProcess]
    ) -> tuple[ObservedProcess, ...]:
        """Reinspect every recorded PID without relying on the root still existing."""
        processes = {process.pid: process for process in self._all_processes()}
        return tuple(
            current
            for recorded in expected
            if (current := processes.get(recorded.pid)) is not None
            and _same_process_start(current.started_at, recorded.started_at)
        )

    def terminate_tree(
        self, expected_tree: Sequence[ObservedProcess]
    ) -> ProcessTermination:
        if not expected_tree:
            return ProcessTermination("VANISHED", "none", (), (), (), "No root process")
        root = expected_tree[0]
        current_tree = self.inspect_tree(root.pid)
        if not current_tree:
            return ProcessTermination(
                "VANISHED",
                "none",
                tuple(item.pid for item in expected_tree),
                (),
                (),
                "Root process vanished before termination",
            )
        if not _same_process_start(current_tree[0].started_at, root.started_at):
            return ProcessTermination(
                "OWNERSHIP_MISMATCH",
                "none",
                tuple(item.pid for item in expected_tree),
                (),
                (),
                "Root PID was reused before termination",
            )

        tracked_by_pid = {process.pid: process for process in expected_tree}
        for process in current_tree:
            tracked_by_pid.setdefault(process.pid, process)
        tracked_tree = tuple(tracked_by_pid.values())
        requested = tuple(item.pid for item in tracked_tree)
        if os.name == "nt":
            strategy = "windows-taskkill-tree"
            completed = self._run(["taskkill.exe", "/PID", str(root.pid), "/T", "/F"])
            detail = completed.stdout.strip() or completed.stderr.strip()
        else:
            strategy = "posix-process-group"
            try:
                process_group = os.getpgid(root.pid)
                if process_group != root.pid:
                    return ProcessTermination(
                        "TERMINATION_FAILED",
                        strategy,
                        requested,
                        (),
                        requested,
                        "Root process does not own an isolated process group",
                    )
                os.killpg(process_group, signal.SIGTERM)
                time.sleep(0.2)
                if self._inspect_owned_processes(tracked_tree):
                    os.killpg(process_group, signal.SIGKILL)
                detail = "Terminated isolated process group"
            except (ProcessLookupError, PermissionError) as exc:
                return ProcessTermination(
                    "TERMINATION_FAILED", strategy, requested, (), requested, str(exc)
                )

        time.sleep(0.1)
        remaining = tuple(
            process.pid for process in self._inspect_owned_processes(tracked_tree)
        )
        disposition = "TERMINATED" if not remaining else "TERMINATION_FAILED"
        terminated = tuple(pid for pid in requested if pid not in remaining)
        return ProcessTermination(
            disposition, strategy, requested, terminated, remaining, detail
        )


def _normalize_path(path: Path) -> str:
    return os.path.normcase(str(path.resolve()))


def _resolve_compose_files(
    *,
    project_name: str,
    working_directory: Path,
    raw_files: object,
) -> tuple[str, ...]:
    if not isinstance(raw_files, list) or not raw_files:
        raise CancellationError(f"Compose project {project_name} has no compose_files")
    compose_files: list[str] = []
    for raw_file in raw_files:
        if not isinstance(raw_file, str) or not raw_file.strip():
            raise CancellationError(
                f"Compose project {project_name} has an invalid compose file"
            )
        candidate = Path(raw_file).expanduser()
        if not candidate.is_absolute():
            candidate = working_directory / candidate
        resolved = candidate.resolve()
        try:
            resolved.relative_to(working_directory)
        except ValueError as exc:
            raise CancellationError(
                f"Compose file must be inside {working_directory}: {resolved}"
            ) from exc
        if not resolved.is_file():
            raise CancellationError(f"Compose file does not exist: {resolved}")
        compose_files.append(str(resolved))
    return tuple(compose_files)


def _parse_compose_project(
    raw: object,
    *,
    allowed_repository_root: Path | None,
) -> ComposeProject:
    if not isinstance(raw, dict):
        raise CancellationError("Compose cleanup project entries must be objects")
    name = raw.get("project_name")
    if not isinstance(name, str) or not COMPOSE_PROJECT_PATTERN.fullmatch(name):
        raise CancellationError(f"Unsafe Compose project name: {name!r}")
    working_value = raw.get("working_directory")
    if not isinstance(working_value, str) or not working_value.strip():
        raise CancellationError(f"Compose project {name} has no working_directory")
    working_directory = Path(working_value).expanduser().resolve()
    if not working_directory.is_dir():
        raise CancellationError(
            f"Compose project {name} working directory does not exist: {working_directory}"
        )
    if allowed_repository_root and _normalize_path(
        working_directory
    ) != _normalize_path(allowed_repository_root):
        raise CancellationError(
            f"Compose project {name} must use the exact task repository root"
        )
    compose_files = _resolve_compose_files(
        project_name=name,
        working_directory=working_directory,
        raw_files=raw.get("compose_files"),
    )
    return ComposeProject(name, str(working_directory), compose_files)


def load_compose_cleanup_plan(
    plan_path: Path, *, allowed_repository_root: Path | None = None
) -> tuple[ComposeProject, ...]:
    try:
        value = json.loads(plan_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CancellationError(
            f"Cannot read Compose cleanup plan {plan_path}: {exc}"
        ) from exc
    if not isinstance(value, dict) or value.get("schema_version") != (
        "lotus.background-task-compose-cleanup-plan.v1"
    ):
        raise CancellationError(
            "Compose cleanup plan has an unsupported schema_version"
        )
    raw_projects = value.get("projects")
    if not isinstance(raw_projects, list) or not raw_projects:
        raise CancellationError(
            "Compose cleanup plan must contain at least one project"
        )

    allowed_root = (
        allowed_repository_root.resolve() if allowed_repository_root else None
    )
    projects: list[ComposeProject] = []
    seen: set[str] = set()
    for raw in raw_projects:
        project = _parse_compose_project(
            raw,
            allowed_repository_root=allowed_root,
        )
        if project.project_name in seen:
            raise CancellationError(
                f"Duplicate Compose project name: {project.project_name}"
            )
        projects.append(project)
        seen.add(project.project_name)
    return tuple(projects)


def build_cleanup_contract(
    *,
    plan_path: Path | None,
    no_external_cleanup_required: bool,
    allowed_repository_root: Path | None = None,
) -> dict[str, Any]:
    if plan_path and no_external_cleanup_required:
        raise CancellationError(
            "Compose cleanup plan and no-external-cleanup declaration are mutually exclusive"
        )
    if plan_path:
        projects = load_compose_cleanup_plan(
            plan_path, allowed_repository_root=allowed_repository_root
        )
        return {
            "ownership_state": "COMPOSE",
            "compose_projects": [asdict(project) for project in projects],
            "source_plan": str(plan_path.resolve()),
        }
    if no_external_cleanup_required:
        return {
            "ownership_state": "NONE",
            "compose_projects": [],
            "source_plan": None,
        }
    return {
        "ownership_state": "UNKNOWN",
        "compose_projects": [],
        "source_plan": None,
    }


class DockerComposeController:
    """Remove one launch-declared Compose project after exact label verification."""

    def _run(self, command: Sequence[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            list(command),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            **_hidden_process_options(),
        )

    def _list(self, kind: str, project_name: str) -> tuple[str, ...]:
        label = f"com.docker.compose.project={project_name}"
        if kind == "containers":
            command = [
                "docker",
                "ps",
                "-a",
                "--filter",
                f"label={label}",
                "--format",
                "{{.ID}}",
            ]
        elif kind == "volumes":
            command = [
                "docker",
                "volume",
                "ls",
                "--filter",
                f"label={label}",
                "--format",
                "{{.Name}}",
            ]
        else:
            command = [
                "docker",
                "network",
                "ls",
                "--filter",
                f"label={label}",
                "--format",
                "{{.ID}}",
            ]
        completed = self._run(command)
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip()
            raise CancellationError(f"Docker {kind} inventory failed: {detail}")
        return tuple(
            line.strip() for line in completed.stdout.splitlines() if line.strip()
        )

    def _inventory(self, project_name: str) -> ComposeInventory:
        return ComposeInventory(
            containers=self._list("containers", project_name),
            volumes=self._list("volumes", project_name),
            networks=self._list("networks", project_name),
        )

    def _verify_container_provenance(
        self, project: ComposeProject, container_ids: Sequence[str]
    ) -> tuple[bool, str]:
        completed = self._run(["docker", "inspect", *container_ids])
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip()
            return False, f"Docker container inspection failed: {detail}"
        try:
            inspected = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            return False, f"Docker container inspection was not valid JSON: {exc}"
        expected_directory = _normalize_path(Path(project.working_directory))
        expected_files = {
            _normalize_path(Path(compose_file))
            for compose_file in project.compose_files
        }
        for container in inspected:
            labels = (container.get("Config") or {}).get("Labels") or {}
            if labels.get("com.docker.compose.project") != project.project_name:
                return (
                    False,
                    "Container project label does not match the declared project",
                )
            actual_directory = labels.get("com.docker.compose.project.working_dir")
            if not actual_directory or _normalize_path(Path(actual_directory)) != (
                expected_directory
            ):
                return False, "Container working-directory provenance does not match"
            raw_files = labels.get("com.docker.compose.project.config_files") or ""
            actual_files = {
                _normalize_path(Path(item.strip()))
                for item in raw_files.split(",")
                if item.strip()
            }
            if actual_files != expected_files:
                return False, "Container Compose-file provenance does not match"
        return True, "Exact Compose labels match the launch declaration"

    def cleanup(self, project: ComposeProject) -> ComposeCleanup:
        before = self._inventory(project.project_name)
        if before.total == 0:
            return ComposeCleanup(
                project.project_name,
                "ALREADY_ABSENT",
                True,
                before.counts(),
                before.counts(),
                (),
                "No exact project resources exist; no mutation was run",
            )
        if not before.containers:
            return ComposeCleanup(
                project.project_name,
                "PROVENANCE_BLOCKED",
                False,
                before.counts(),
                before.counts(),
                (),
                "Residual project resources have no live container working-directory provenance",
            )
        verified, detail = self._verify_container_provenance(project, before.containers)
        if not verified:
            return ComposeCleanup(
                project.project_name,
                "PROVENANCE_BLOCKED",
                False,
                before.counts(),
                before.counts(),
                (),
                detail,
            )
        command: list[str] = [
            "docker",
            "compose",
            "--project-name",
            project.project_name,
            "--project-directory",
            project.working_directory,
        ]
        for compose_file in project.compose_files:
            command.extend(["--file", compose_file])
        command.extend(["down", "--remove-orphans", "--volumes"])
        completed = self._run(command)
        if completed.returncode != 0:
            failed_after = self._inventory(project.project_name)
            failure = completed.stderr.strip() or completed.stdout.strip()
            return ComposeCleanup(
                project.project_name,
                "CLEANUP_FAILED",
                False,
                before.counts(),
                failed_after.counts(),
                tuple(command),
                failure,
            )
        after = self._inventory(project.project_name)
        passed = after.total == 0
        return ComposeCleanup(
            project.project_name,
            "CLEANED" if passed else "RESIDUAL_RESOURCES",
            passed,
            before.counts(),
            after.counts(),
            tuple(command),
            detail if passed else "Exact project resources remain after Compose down",
        )


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CancellationError(f"Cannot read JSON state {path}: {exc}") from exc


def _atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


@contextlib.contextmanager
def _ledger_lock(state_path: Path) -> Iterator[None]:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = state_path.with_suffix(f"{state_path.suffix}.lock")
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise CancellationError(
            f"Background-run ledger is locked: {lock_path}"
        ) from exc
    try:
        os.write(descriptor, f"pid={os.getpid()}\n".encode())
        os.close(descriptor)
        yield
    finally:
        with contextlib.suppress(FileNotFoundError):
            lock_path.unlink()


def _load_entries(state_path: Path) -> list[dict[str, Any]]:
    parsed = _read_json(state_path)
    if isinstance(parsed, dict):
        parsed = [parsed]
    if not isinstance(parsed, list) or not all(
        isinstance(item, dict) for item in parsed
    ):
        raise CancellationError("Background-run ledger must contain task objects")
    return parsed


def _projects_from_contract(contract: Mapping[str, Any]) -> tuple[ComposeProject, ...]:
    projects: list[ComposeProject] = []
    seen: set[str] = set()
    for raw in contract.get("compose_projects") or []:
        if not isinstance(raw, Mapping):
            raise CancellationError("Ledger cleanup project is not an object")
        project_name = str(raw.get("project_name") or "")
        if not COMPOSE_PROJECT_PATTERN.fullmatch(project_name):
            raise CancellationError(
                f"Ledger contains an unsafe Compose project name: {project_name!r}"
            )
        if project_name in seen:
            raise CancellationError(
                f"Ledger contains duplicate Compose project ownership: {project_name}"
            )
        working_directory = Path(str(raw.get("working_directory") or "")).resolve()
        if not working_directory.is_dir():
            raise CancellationError(
                f"Ledger Compose working directory does not exist: {working_directory}"
            )
        raw_files = raw.get("compose_files") or []
        if not raw_files:
            raise CancellationError(
                f"Ledger Compose project has no config files: {project_name}"
            )
        compose_files: list[str] = []
        for item in raw_files:
            compose_file = Path(str(item)).resolve()
            try:
                compose_file.relative_to(working_directory)
            except ValueError as exc:
                raise CancellationError(
                    f"Ledger Compose file is outside {working_directory}: {compose_file}"
                ) from exc
            if not compose_file.is_file():
                raise CancellationError(
                    f"Ledger Compose file does not exist: {compose_file}"
                )
            compose_files.append(str(compose_file))
        projects.append(
            ComposeProject(
                project_name=project_name,
                working_directory=str(working_directory),
                compose_files=tuple(compose_files),
            )
        )
        seen.add(project_name)
    return tuple(projects)


def _resolve_cancellable_task(
    entries: Sequence[dict[str, Any]], engineering_task_id: str
) -> tuple[int, dict[str, Any], str]:
    matches = [
        (index, entry)
        for index, entry in enumerate(entries)
        if entry.get("engineering_task_id") == engineering_task_id
    ]
    if len(matches) != 1:
        raise CancellationError(
            f"engineering_task_id must resolve exactly once; found {len(matches)}"
        )
    index, entry = matches[0]
    current_status = str(entry.get("status") or "").upper()
    if current_status in TERMINAL_STATES:
        raise CancellationError(
            f"Task is already terminal and cannot be cancelled: {current_status}"
        )
    if current_status not in {"QUEUED", "RUNNING"}:
        raise CancellationError(
            f"Task has unsupported lifecycle status: {current_status}"
        )
    return index, entry, current_status


def _declared_cleanup_ownership(
    entry: Mapping[str, Any],
) -> tuple[str, tuple[ComposeProject, ...]]:
    scope = entry.get("scope")
    cleanup_contract = (
        scope.get("cleanup_contract") if isinstance(scope, dict) else None
    )
    if not isinstance(cleanup_contract, dict):
        return "UNKNOWN", ()
    ownership_state = str(cleanup_contract.get("ownership_state") or "UNKNOWN")
    projects = (
        _projects_from_contract(cleanup_contract)
        if ownership_state == "COMPOSE"
        else ()
    )
    return ownership_state, projects


def _unreconciled_process(detail: str, *, pid: int | None = None) -> ProcessTermination:
    requested = (pid,) if pid is not None else ()
    return ProcessTermination(
        "OWNERSHIP_UNRECONCILED", "none", requested, (), (), detail
    )


def _cancel_running_process(
    entry: Mapping[str, Any], process_controller: ProcessController
) -> ProcessTermination:
    runtime = entry.get("runtime") if isinstance(entry.get("runtime"), dict) else {}
    raw_pid = runtime.get("pid", entry.get("pid"))
    raw_started_at = runtime.get("process_started_at")
    if raw_pid is None or raw_started_at is None:
        return _unreconciled_process("Recorded PID and process start time are required")
    pid = int(raw_pid)
    expected_start = _parse_timestamp(raw_started_at)
    try:
        observed_tree = process_controller.inspect_tree(pid)
    except Exception as exc:  # adapter failure must become durable evidence
        return _unreconciled_process(
            f"Process ownership inspection failed: {exc}", pid=pid
        )
    if not observed_tree:
        return ProcessTermination(
            "VANISHED",
            "none",
            (pid,),
            (),
            (),
            "Recorded root process is no longer present",
        )
    if not _same_process_start(observed_tree[0].started_at, expected_start):
        return ProcessTermination(
            "OWNERSHIP_MISMATCH",
            "none",
            (pid,),
            (),
            (),
            "Recorded PID now belongs to a different process start",
        )
    try:
        return process_controller.terminate_tree(observed_tree)
    except Exception as exc:  # adapter failure must become durable evidence
        owned_pids = tuple(item.pid for item in observed_tree)
        return ProcessTermination(
            "TERMINATION_FAILED",
            "unknown",
            owned_pids,
            (),
            owned_pids,
            f"Process-tree termination failed: {exc}",
        )


def _cancel_process(
    *,
    current_status: str,
    entry: Mapping[str, Any],
    process_controller: ProcessController,
) -> ProcessTermination:
    if current_status == "QUEUED":
        return ProcessTermination(
            "NOT_STARTED",
            "none",
            (),
            (),
            (),
            "Queued task had no process to terminate",
        )
    return _cancel_running_process(entry, process_controller)


def _cleanup_one_project(
    project: ComposeProject, compose_controller: ComposeController
) -> ComposeCleanup:
    try:
        return compose_controller.cleanup(project)
    except Exception as exc:  # adapter failure must become durable evidence
        empty = {"containers": 0, "volumes": 0, "networks": 0, "total": 0}
        return ComposeCleanup(
            project.project_name,
            "ADAPTER_FAILED",
            False,
            empty,
            empty,
            (),
            f"Compose cleanup adapter failed: {exc}",
        )


def _cleanup_owned_resources(
    *,
    process_outcome: ProcessTermination,
    ownership_state: str,
    declared_projects: Sequence[ComposeProject],
    compose_controller: ComposeController,
) -> tuple[tuple[ComposeCleanup, ...], bool, str]:
    if process_outcome.disposition == "NOT_STARTED":
        if ownership_state == "NONE":
            return (
                (),
                True,
                "Queued task never started and required no external cleanup",
            )
        return (
            (),
            False,
            "Queued task never started; external cleanup was not attempted",
        )
    if not process_outcome.passed:
        return (
            (),
            False,
            "Process termination did not pass; external cleanup was not attempted",
        )
    if ownership_state == "NONE":
        return (), True, "Launch contract declared that no external cleanup is required"
    if ownership_state != "COMPOSE":
        return (
            (),
            False,
            "Task launch did not declare external cleanup ownership; cleanup cannot be proven",
        )
    if not declared_projects:
        return (), False, "Compose ownership was declared without any projects"
    outcomes = tuple(
        _cleanup_one_project(project, compose_controller)
        for project in declared_projects
    )
    passed = all(outcome.passed for outcome in outcomes)
    detail = (
        "All launch-declared Compose projects are clean"
        if passed
        else "One or more launch-declared Compose projects failed cleanup"
    )
    return outcomes, passed, detail


def _final_status(process_outcome: ProcessTermination) -> str:
    if process_outcome.passed or process_outcome.disposition == "NOT_STARTED":
        return "CANCELLED"
    if process_outcome.disposition in {
        "VANISHED",
        "OWNERSHIP_MISMATCH",
        "OWNERSHIP_UNRECONCILED",
    }:
        return "LOST"
    return "RUNNING"


def _build_cancellation_receipt(
    *,
    engineering_task_id: str,
    reason: str,
    actor: str,
    requested_at: datetime,
    finished_at: datetime,
    current_status: str,
    final_status: str,
    cleanup_state: str,
    process_outcome: ProcessTermination,
    declared_projects: Sequence[ComposeProject],
    compose_outcomes: Sequence[ComposeCleanup],
    cleanup_detail: str,
) -> dict[str, Any]:
    resource_before = sum(
        outcome.before.get("total", 0) for outcome in compose_outcomes
    )
    resource_after = sum(outcome.after.get("total", 0) for outcome in compose_outcomes)
    return {
        "schema_version": "lotus.background-task-cancellation-receipt.v1",
        "engineering_task_id": engineering_task_id,
        "reason": reason,
        "actor": actor,
        "requested_at": requested_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "targets": {
            "process_pids": list(process_outcome.requested_pids),
            "compose_projects": [project.project_name for project in declared_projects],
        },
        "outcomes": {
            "process": asdict(process_outcome),
            "compose": [asdict(outcome) for outcome in compose_outcomes],
            "cleanup_detail": cleanup_detail,
        },
        "counts": {
            "process_targets": len(process_outcome.requested_pids),
            "process_terminated": len(process_outcome.terminated_pids),
            "process_remaining": len(process_outcome.remaining_owned_pids),
            "compose_projects_declared": len(declared_projects),
            "compose_projects_attempted": len(compose_outcomes),
            "compose_projects_clean": sum(
                1 for outcome in compose_outcomes if outcome.passed
            ),
            "compose_resources_before": resource_before,
            "compose_resources_removed": resource_before - resource_after,
            "compose_resources_remaining": resource_after,
        },
        "ledger_transition": {
            "from_status": current_status,
            "to_status": final_status,
            "cleanup_state": cleanup_state,
        },
    }


def _receipt_path(
    *,
    receipt_dir: Path,
    engineering_task_id: str,
    requested_at: datetime,
) -> Path:
    timestamp_slug = requested_at.strftime("%Y%m%dT%H%M%S%fZ")
    task_slug = re.sub(r"[^A-Za-z0-9._-]+", "-", engineering_task_id)
    return receipt_dir.resolve() / f"{timestamp_slug}-{task_slug}.cancellation.json"


def _update_cancelled_entry(
    *,
    entry: dict[str, Any],
    final_status: str,
    cleanup_state: str,
    cleanup_passed: bool,
    cleanup_detail: str,
    process_outcome: ProcessTermination,
    receipt_path: Path,
    reason: str,
    actor: str,
    requested_at: datetime,
    finished_at: datetime,
) -> None:
    entry["status"] = final_status
    entry["cleanup_state"] = cleanup_state
    if final_status in TERMINAL_STATES:
        entry["ended_at"] = finished_at.isoformat()
    if final_status == "CANCELLED":
        summary = f"Cancelled by {actor}: {reason}"
        if not cleanup_passed:
            summary += f"; cleanup blocked: {cleanup_detail}"
        entry["error_summary"] = summary
    else:
        entry["error_summary"] = process_outcome.detail
    entry["cancellation"] = {
        "receipt_path": str(receipt_path),
        "reason": reason,
        "actor": actor,
        "requested_at": requested_at.isoformat(),
        "process_disposition": process_outcome.disposition,
        "cleanup_detail": cleanup_detail,
    }
    entry["artifacts"] = list(
        dict.fromkeys([*(entry.get("artifacts") or []), str(receipt_path)])
    )
    entry["evidence_refs"] = [
        *(entry.get("evidence_refs") or []),
        {"type": "LOCAL_JSON_ARTIFACT", "path": str(receipt_path)},
    ]


def _validate_request(engineering_task_id: str, reason: str, actor: str) -> None:
    if not TASK_ID_PATTERN.fullmatch(engineering_task_id):
        raise CancellationError("engineering_task_id contains unsupported characters")
    if not reason:
        raise CancellationError("Cancellation reason is required")
    if not actor:
        raise CancellationError("Cancellation actor is required")


def cancel_background_task(
    *,
    state_path: Path,
    receipt_dir: Path,
    engineering_task_id: str,
    reason: str,
    actor: str,
    process_controller: ProcessController,
    compose_controller: ComposeController,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> dict[str, Any]:
    normalized_reason = reason.strip()
    normalized_actor = actor.strip()
    _validate_request(engineering_task_id, normalized_reason, normalized_actor)
    requested_at = now().astimezone(UTC)

    with _ledger_lock(state_path):
        entries = _load_entries(state_path)
        index, entry, current_status = _resolve_cancellable_task(
            entries, engineering_task_id
        )
        process_outcome = _cancel_process(
            current_status=current_status,
            entry=entry,
            process_controller=process_controller,
        )
        cleanup_contract_error: str | None = None
        try:
            ownership_state, declared_projects = _declared_cleanup_ownership(entry)
        except CancellationError as exc:
            ownership_state, declared_projects = "INVALID", ()
            cleanup_contract_error = str(exc)
        compose_outcomes, cleanup_passed, cleanup_detail = _cleanup_owned_resources(
            process_outcome=process_outcome,
            ownership_state=ownership_state,
            declared_projects=declared_projects,
            compose_controller=compose_controller,
        )
        if cleanup_contract_error:
            cleanup_detail = (
                f"Launch-declared cleanup contract is invalid: {cleanup_contract_error}"
            )
        final_status = _final_status(process_outcome)
        cleanup_state = "DONE" if cleanup_passed else "BLOCKED"
        finished_at = now().astimezone(UTC)
        receipt = _build_cancellation_receipt(
            engineering_task_id=engineering_task_id,
            reason=normalized_reason,
            actor=normalized_actor,
            requested_at=requested_at,
            finished_at=finished_at,
            current_status=current_status,
            final_status=final_status,
            cleanup_state=cleanup_state,
            process_outcome=process_outcome,
            declared_projects=declared_projects,
            compose_outcomes=compose_outcomes,
            cleanup_detail=cleanup_detail,
        )
        receipt_path = _receipt_path(
            receipt_dir=receipt_dir,
            engineering_task_id=engineering_task_id,
            requested_at=requested_at,
        )
        _atomic_write_json(receipt_path, receipt)
        _update_cancelled_entry(
            entry=entry,
            final_status=final_status,
            cleanup_state=cleanup_state,
            cleanup_passed=cleanup_passed,
            cleanup_detail=cleanup_detail,
            process_outcome=process_outcome,
            receipt_path=receipt_path,
            reason=normalized_reason,
            actor=normalized_actor,
            requested_at=requested_at,
            finished_at=finished_at,
        )
        entries[index] = entry
        _atomic_write_json(state_path, entries)

    receipt["receipt_path"] = str(receipt_path)
    return receipt


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="operation", required=True)
    cancel = subparsers.add_parser("cancel", help="Cancel one exact engineering task")
    cancel.add_argument("--engineering-task-id", required=True)
    cancel.add_argument("--reason", required=True)
    cancel.add_argument("--actor", required=True)
    cancel.add_argument("--state-path", default="output/background-runs.json")
    cancel.add_argument("--receipt-dir", default="output/task-runs")
    validate = subparsers.add_parser(
        "validate-compose-plan", help="Validate and normalize a Compose cleanup plan"
    )
    validate.add_argument("--plan-path", required=True)
    validate.add_argument("--allowed-repository-root")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.operation == "validate-compose-plan":
            allowed_root = (
                Path(args.allowed_repository_root)
                if args.allowed_repository_root
                else None
            )
            projects = load_compose_cleanup_plan(
                Path(args.plan_path).resolve(), allowed_repository_root=allowed_root
            )
            print(json.dumps({"projects": [asdict(item) for item in projects]}))
            return 0
        receipt = cancel_background_task(
            state_path=Path(args.state_path).resolve(),
            receipt_dir=Path(args.receipt_dir).resolve(),
            engineering_task_id=args.engineering_task_id,
            reason=args.reason,
            actor=args.actor,
            process_controller=SystemProcessController(),
            compose_controller=DockerComposeController(),
        )
        print(f"engineering_task_id={receipt['engineering_task_id']}")
        print(f"status={receipt['ledger_transition']['to_status']}")
        print(f"cleanup_state={receipt['ledger_transition']['cleanup_state']}")
        print(f"receipt={receipt['receipt_path']}")
        return 0 if receipt["ledger_transition"]["cleanup_state"] == "DONE" else 3
    except CancellationError as exc:
        print(f"background task cancellation rejected: {exc}", file=os.sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
