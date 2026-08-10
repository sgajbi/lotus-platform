"""Launch and execute governed repository-native background tasks.

The launcher accepts a repository from ``automation/repos.json`` and a typed target. It never
evaluates a caller-provided shell command. The detached runner receives a JSON job specification
and invokes the selected executable with an argument vector.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterator, Sequence

try:
    from automation.background_task_cancellation import (
        SystemProcessController,
        build_cleanup_contract,
    )
except ModuleNotFoundError:  # direct ``python automation/...`` execution
    from background_task_cancellation import (  # type: ignore[no-redef]
        SystemProcessController,
        build_cleanup_contract,
    )


TARGET_TYPES = ("make", "npm", "python", "powershell")
SAFE_TARGET_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
SAFE_RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
WILDCARD_CHARACTERS = frozenset("*?[")
WINDOWS_DLL_INITIALIZATION_FAILURES = frozenset({0xC0000142, -1073741502})


class BackgroundTaskError(RuntimeError):
    """Raised when a repository-native task violates its launch contract."""


@dataclass(frozen=True)
class RepositoryIdentity:
    name: str
    path: Path
    branch: str
    head: str
    tree_state: str


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BackgroundTaskError(f"Cannot read JSON contract {path}: {exc}") from exc


def _atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _run_git(repository_path: Path, *arguments: str) -> str:
    completed: subprocess.CompletedProcess[str] | None = None
    for attempt in range(3):
        completed = subprocess.run(
            ["git", "-C", str(repository_path), *arguments],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if completed.returncode not in WINDOWS_DLL_INITIALIZATION_FAILURES:
            break
        time.sleep(0.2 * (attempt + 1))
    assert completed is not None
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise BackgroundTaskError(
            f"Git identity check failed for {repository_path}: {detail or completed.returncode}"
        )
    return completed.stdout.strip()


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def resolve_repository_path(
    repository_name: str, repository_path: Path
) -> RepositoryIdentity:
    repository_path = repository_path.expanduser().resolve()
    if not repository_path.is_dir():
        raise BackgroundTaskError(
            f"Repository '{repository_name}' path does not exist: {repository_path}"
        )

    git_root = Path(_run_git(repository_path, "rev-parse", "--show-toplevel")).resolve()
    if os.path.normcase(str(git_root)) != os.path.normcase(str(repository_path)):
        raise BackgroundTaskError(
            f"Configured path must be the exact Git root: configured={repository_path}, git={git_root}"
        )

    head = _run_git(repository_path, "rev-parse", "HEAD")
    branch = (
        _run_git(repository_path, "branch", "--show-current") or f"detached:{head[:12]}"
    )
    tree_state = (
        "clean" if not _run_git(repository_path, "status", "--porcelain") else "dirty"
    )
    return RepositoryIdentity(
        repository_name, repository_path, branch, head, tree_state
    )


def resolve_repository(
    repos_config_path: Path, repository_name: str
) -> RepositoryIdentity:
    configured = _read_json(repos_config_path)
    if not isinstance(configured, list):
        raise BackgroundTaskError("Repository config must contain a JSON array")

    matches = [item for item in configured if item.get("name") == repository_name]
    if len(matches) != 1:
        raise BackgroundTaskError(
            f"Repository '{repository_name}' must resolve exactly once; found {len(matches)}"
        )

    raw_path = matches[0].get("path")
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise BackgroundTaskError(
            f"Repository '{repository_name}' has no configured path"
        )
    return resolve_repository_path(repository_name, Path(raw_path))


def validate_launch_fences(
    identity: RepositoryIdentity,
    *,
    expected_head: str | None,
    require_clean: bool,
) -> None:
    if expected_head and identity.head != expected_head:
        raise BackgroundTaskError(
            f"Expected HEAD {expected_head} but repository is at {identity.head}"
        )
    if require_clean and identity.tree_state != "clean":
        raise BackgroundTaskError("Repository worktree is not clean")


def _normalize_relative_path(value: str, *, field: str) -> str:
    normalized = value.replace("\\", "/")
    candidate = PurePosixPath(normalized)
    if not value.strip() or candidate.is_absolute() or ".." in candidate.parts:
        raise BackgroundTaskError(
            f"{field} must be a non-parent relative path: {value!r}"
        )
    if candidate.parts and ":" in candidate.parts[0]:
        raise BackgroundTaskError(f"{field} must not contain a drive prefix: {value!r}")
    return candidate.as_posix()


def validate_required_artifact_pattern(pattern: str) -> str:
    return _normalize_relative_path(pattern, field="Required artifact")


def resolve_script_target(repository_path: Path, target_type: str, target: str) -> Path:
    normalized = _normalize_relative_path(target, field="Script target")
    if any(character in normalized for character in WILDCARD_CHARACTERS):
        raise BackgroundTaskError("Script target must not contain wildcards")

    expected_suffix = ".py" if target_type == "python" else ".ps1"
    if Path(normalized).suffix.lower() != expected_suffix:
        raise BackgroundTaskError(
            f"{target_type} target must use the {expected_suffix} extension"
        )

    resolved = (repository_path / normalized).resolve()
    if not _is_within(resolved, repository_path) or not resolved.is_file():
        raise BackgroundTaskError(
            f"Script target must be an existing file inside {repository_path}: {target}"
        )
    return resolved


def build_command(
    repository_path: Path,
    target_type: str,
    target: str,
    target_arguments: Sequence[str],
) -> list[str]:
    if target_type not in TARGET_TYPES:
        raise BackgroundTaskError(
            f"Unsupported target type '{target_type}'; expected one of {', '.join(TARGET_TYPES)}"
        )

    if target_type in {"make", "npm"}:
        if not SAFE_TARGET_PATTERN.fullmatch(target):
            raise BackgroundTaskError(
                f"{target_type} target contains unsupported characters: {target!r}"
            )
        executable_name = "make" if target_type == "make" else "npm"
        executable = shutil.which(executable_name)
        if executable is None:
            raise BackgroundTaskError(
                f"Required executable is unavailable: {executable_name}"
            )
        if target_type == "make":
            return [executable, target, *target_arguments]
        separator = ["--"] if target_arguments else []
        return [executable, "run", target, *separator, *target_arguments]

    script_path = resolve_script_target(repository_path, target_type, target)
    if target_type == "python":
        return [sys.executable, str(script_path), *target_arguments]

    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if powershell is None:
        raise BackgroundTaskError(
            "Required executable is unavailable: powershell or pwsh"
        )
    return [
        powershell,
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script_path),
        *target_arguments,
    ]


def _artifact_matches(
    repository_path: Path,
    patterns: Sequence[str],
    started_epoch_seconds: float,
) -> tuple[list[str], list[str]]:
    observed: list[str] = []
    missing: list[str] = []
    for raw_pattern in patterns:
        pattern = validate_required_artifact_pattern(raw_pattern)
        matches: list[str] = []
        for candidate in repository_path.glob(pattern):
            resolved = candidate.resolve()
            if (
                candidate.is_file()
                and _is_within(resolved, repository_path)
                and candidate.stat().st_mtime >= started_epoch_seconds - 1.0
            ):
                matches.append(str(resolved))
        if matches:
            observed.extend(sorted(matches))
        else:
            missing.append(pattern)
    return sorted(set(observed)), missing


def _load_ledger(state_path: Path) -> list[dict[str, Any]]:
    if (
        not state_path.exists()
        or not state_path.read_text(encoding="utf-8-sig").strip()
    ):
        return []
    parsed = _read_json(state_path)
    if isinstance(parsed, dict):
        return [parsed]
    if not isinstance(parsed, list) or not all(
        isinstance(item, dict) for item in parsed
    ):
        raise BackgroundTaskError(
            "Background-run ledger must contain an object or array of objects"
        )
    return parsed


def validate_new_ledger_identity(
    entries: Sequence[dict[str, Any]],
    *,
    engineering_task_id: str,
    correlation_ref: str,
    process_id: int | None = None,
) -> None:
    if any(
        entry.get("engineering_task_id") == engineering_task_id
        or entry.get("correlation_ref") == correlation_ref
        for entry in entries
    ):
        raise BackgroundTaskError(
            f"Background task identity already exists: {engineering_task_id}"
        )
    if process_id is not None and any(
        entry.get("pid") == process_id for entry in entries
    ):
        raise BackgroundTaskError(
            f"Background process id already exists in ledger: {process_id}"
        )


@contextlib.contextmanager
def _exclusive_ledger_lock(state_path: Path) -> Iterator[None]:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = state_path.with_suffix(f"{state_path.suffix}.lock")
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise BackgroundTaskError(
            f"Background-run ledger is locked: {lock_path}"
        ) from exc
    try:
        os.write(descriptor, f"pid={os.getpid()}\n".encode())
        os.close(descriptor)
        yield
    finally:
        with contextlib.suppress(FileNotFoundError):
            lock_path.unlink()


def _task_slug(repository: str, target_type: str, target: str) -> str:
    raw = f"{repository}-{target_type}-{target}"
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", raw).strip("-.").lower()
    if not slug:
        raise BackgroundTaskError("Cannot derive a safe task identifier")
    return slug[:96]


def _detached_process_options() -> dict[str, Any]:
    if os.name == "nt":
        return {
            "creationflags": subprocess.CREATE_NEW_PROCESS_GROUP
            | subprocess.DETACHED_PROCESS,
            "close_fds": True,
        }
    return {"start_new_session": True, "close_fds": True}


def _target_process_options() -> dict[str, Any]:
    if os.name == "nt":
        return {"creationflags": subprocess.CREATE_NO_WINDOW}
    return {}


def _start_detached_runner(
    *,
    job_spec_path: Path,
    out_log_path: Path,
    err_log_path: Path,
    result_path: Path,
) -> subprocess.Popen[str]:
    runner_command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "run",
        "--job-spec",
        str(job_spec_path),
    ]
    last_return_code: int | None = None
    for attempt in range(3):
        log_mode = "w" if attempt == 0 else "a"
        with (
            out_log_path.open(log_mode, encoding="utf-8") as out_log,
            err_log_path.open(log_mode, encoding="utf-8") as err_log,
        ):
            process = subprocess.Popen(
                runner_command,
                cwd=Path(__file__).resolve().parents[1],
                stdin=subprocess.DEVNULL,
                stdout=out_log,
                stderr=err_log,
                text=True,
                **_detached_process_options(),
            )
        time.sleep(0.3)
        last_return_code = process.poll()
        if last_return_code is None or result_path.exists():
            return process
        if last_return_code not in WINDOWS_DLL_INITIALIZATION_FAILURES:
            raise BackgroundTaskError(
                f"Detached runner exited before writing result evidence: {last_return_code}"
            )
        time.sleep(0.2 * (attempt + 1))
    raise BackgroundTaskError(
        f"Detached runner failed Windows process initialization: {last_return_code}"
    )


def launch_repository_task(args: argparse.Namespace) -> int:
    identity = resolve_repository(Path(args.repos_config).resolve(), args.repository)
    validate_launch_fences(
        identity,
        expected_head=args.expected_head,
        require_clean=args.require_clean,
    )
    command = build_command(
        identity.path, args.target_type, args.target, args.target_argument
    )
    required_artifacts = [
        validate_required_artifact_pattern(item) for item in args.required_artifact
    ]
    cleanup_contract = build_cleanup_contract(
        plan_path=(
            Path(args.compose_cleanup_plan).resolve()
            if args.compose_cleanup_plan
            else None
        ),
        no_external_cleanup_required=args.no_external_cleanup_required,
        allowed_repository_root=identity.path,
    )

    run_id = args.run_id or datetime.now().strftime("%Y%m%d-%H%M%S")
    if not SAFE_RUN_ID_PATTERN.fullmatch(run_id):
        raise BackgroundTaskError(f"Run id contains unsupported characters: {run_id!r}")
    slug = _task_slug(identity.name, args.target_type, args.target)
    correlation_ref = f"{run_id}-{slug}"
    engineering_task_id = f"eng-task-{correlation_ref}"

    state_path = Path(args.state_path).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    out_log_path = output_dir / f"bg-{correlation_ref}.out.log"
    err_log_path = output_dir / f"bg-{correlation_ref}.err.log"
    result_path = output_dir / f"{correlation_ref}.result.json"
    job_spec_path = output_dir / f"{correlation_ref}.job.json"
    requested_at = _utc_now()

    job_spec = {
        "schema_version": "lotus.repository-background-task.v1",
        "engineering_task_id": engineering_task_id,
        "repository": identity.name,
        "repository_path": str(identity.path),
        "branch": identity.branch,
        "commit_sha": identity.head,
        "source_tree_state": identity.tree_state,
        "target_type": args.target_type,
        "target": args.target,
        "target_arguments": list(args.target_argument),
        "command": command,
        "expected_head": args.expected_head,
        "require_clean": args.require_clean,
        "required_artifacts": required_artifacts,
        "cleanup_contract": cleanup_contract,
        "result_path": str(result_path),
        "requested_at": requested_at,
    }

    process: subprocess.Popen[str] | None = None
    with _exclusive_ledger_lock(state_path):
        state = _load_ledger(state_path)
        validate_new_ledger_identity(
            state,
            engineering_task_id=engineering_task_id,
            correlation_ref=correlation_ref,
        )

        _atomic_write_json(job_spec_path, job_spec)
        process = _start_detached_runner(
            job_spec_path=job_spec_path,
            out_log_path=out_log_path,
            err_log_path=err_log_path,
            result_path=result_path,
        )
        observed_process_tree = SystemProcessController().inspect_tree(process.pid)
        process_started_at = (
            observed_process_tree[0].started_at.isoformat()
            if observed_process_tree
            else None
        )

        entry = {
            "engineering_task_id": engineering_task_id,
            "task_kind": "VALIDATION_RUN",
            "repository": identity.name,
            "branch": identity.branch,
            "owner": args.owner
            or os.getenv("USERNAME")
            or os.getenv("USER")
            or "unknown",
            "requested_at": requested_at,
            "origin": "automation/Start-Background-Run.ps1:repository-target",
            "correlation_ref": correlation_ref,
            "summary": f"Repository-native background target {identity.name}:{args.target_type}:{args.target}",
            "pid": process.pid,
            "profile": None,
            "display_name": f"{identity.name}/{args.target_type}/{args.target}",
            "mode": "repository-target",
            "runId": run_id,
            "started_at": requested_at,
            "startedAt": requested_at,
            "status": "RUNNING",
            "runtime": {
                "kind": "python",
                "runner": "automation/repository_background_task.py",
                "pid": process.pid,
                "process_started_at": process_started_at,
                "process_start_identity_state": (
                    "OBSERVED" if process_started_at else "UNAVAILABLE"
                ),
            },
            "scope": {
                "repository_root": str(identity.path),
                "commit_sha": identity.head,
                "source_tree_state": identity.tree_state,
                "target_type": args.target_type,
                "target": args.target,
                "target_arguments": list(args.target_argument),
                "required_artifacts": required_artifacts,
                "expected_head": args.expected_head,
                "require_clean": args.require_clean,
                "cleanup_contract": cleanup_contract,
            },
            "artifacts": [
                str(out_log_path),
                str(err_log_path),
                str(job_spec_path),
                str(result_path),
            ],
            "evidence_refs": [
                {"type": "LOG_FILE", "path": str(out_log_path)},
                {"type": "LOG_FILE", "path": str(err_log_path)},
                {"type": "LOCAL_JSON_ARTIFACT", "path": str(job_spec_path)},
                {"type": "LOCAL_JSON_ARTIFACT", "path": str(result_path)},
            ],
            "cleanup_state": "PENDING",
            "outLogPath": str(out_log_path),
            "errLogPath": str(err_log_path),
            "jobSpecPath": str(job_spec_path),
            "expectedResultPath": str(result_path),
            "expectedSummaryPath": None,
        }
        try:
            validate_new_ledger_identity(
                state,
                engineering_task_id=engineering_task_id,
                correlation_ref=correlation_ref,
                process_id=process.pid,
            )
        except BackgroundTaskError:
            process.terminate()
            raise
        try:
            _atomic_write_json(state_path, [*state, entry])
        except Exception:
            process.terminate()
            raise

    print(f"engineering_task_id={engineering_task_id}")
    print(f"pid={process.pid}")
    print(f"repository={identity.name}")
    print(f"branch={identity.branch}")
    print(f"commit_sha={identity.head}")
    print(f"result={result_path}")
    return 0


def execute_job(job_spec_path: Path) -> int:
    spec = _read_json(job_spec_path)
    result_path = Path(spec["result_path"])
    started_at = _utc_now()
    started_epoch_seconds = time.time()
    exit_code = 1
    error_summary: str | None = None
    observed_artifacts: list[str] = []
    target_pid: int | None = None

    try:
        repository_path = Path(spec["repository_path"]).resolve()
        identity = resolve_repository_path(spec["repository"], repository_path)
        validate_launch_fences(
            identity,
            expected_head=spec.get("expected_head") or spec["commit_sha"],
            require_clean=bool(spec.get("require_clean")),
        )
        if identity.head != spec["commit_sha"]:
            raise BackgroundTaskError(
                f"Repository moved after launch: expected {spec['commit_sha']}, found {identity.head}"
            )

        command = build_command(
            repository_path,
            spec["target_type"],
            spec["target"],
            spec.get("target_arguments", []),
        )
        if command != spec["command"]:
            raise BackgroundTaskError(
                "Serialized command identity changed after launch"
            )

        target_process = subprocess.Popen(
            command,
            cwd=repository_path,
            **_target_process_options(),
        )
        target_pid = target_process.pid
        exit_code = target_process.wait()
        observed_artifacts, missing = _artifact_matches(
            repository_path,
            spec.get("required_artifacts", []),
            started_epoch_seconds,
        )
        if exit_code == 0 and missing:
            exit_code = 1
            error_summary = (
                f"Required artifacts were not produced: {', '.join(missing)}"
            )
        elif exit_code != 0:
            error_summary = f"Repository target exited with code {exit_code}"
    except (
        Exception
    ) as exc:  # terminal result must survive every governed validation failure
        exit_code = 1
        error_summary = str(exc)
        print(error_summary, file=sys.stderr)

    result = [
        {
            "engineering_task_id": spec.get("engineering_task_id"),
            "id": f"{spec.get('repository')}:{spec.get('target_type')}:{spec.get('target')}",
            "repo": spec.get("repository"),
            "repoPath": spec.get("repository_path"),
            "branch": spec.get("branch"),
            "commit_sha": spec.get("commit_sha"),
            "source_tree_state": spec.get("source_tree_state"),
            "command": {
                "target_type": spec.get("target_type"),
                "target": spec.get("target"),
                "arguments": spec.get("target_arguments", []),
            },
            "process_tree": {
                "runner_pid": os.getpid(),
                "target_pid": target_pid,
            },
            "exitCode": exit_code,
            "startedAt": started_at,
            "finishedAt": _utc_now(),
            "observed_artifacts": observed_artifacts,
            "error_summary": error_summary,
        }
    ]
    _atomic_write_json(result_path, result)
    return exit_code


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="operation", required=True)

    launch = subparsers.add_parser("launch", help="Launch a detached repository target")
    launch.add_argument("--repository", required=True)
    launch.add_argument("--target-type", required=True, choices=TARGET_TYPES)
    launch.add_argument("--target", required=True)
    launch.add_argument("--target-argument", action="append", default=[])
    launch.add_argument("--required-artifact", action="append", default=[])
    launch.add_argument("--expected-head")
    launch.add_argument("--require-clean", action="store_true")
    launch.add_argument("--repos-config", default="automation/repos.json")
    launch.add_argument("--state-path", default="output/background-runs.json")
    launch.add_argument("--output-dir", default="output/task-runs")
    launch.add_argument("--run-id")
    launch.add_argument("--owner")
    launch.add_argument("--compose-cleanup-plan")
    launch.add_argument("--no-external-cleanup-required", action="store_true")

    run = subparsers.add_parser("run", help="Execute a serialized repository target")
    run.add_argument("--job-spec", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.operation == "launch":
            return launch_repository_task(args)
        return execute_job(Path(args.job_spec).resolve())
    except BackgroundTaskError as exc:
        print(f"repository background task rejected: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
