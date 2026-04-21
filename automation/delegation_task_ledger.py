from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

AUTOMATION_DIR = Path(__file__).resolve().parent
if str(AUTOMATION_DIR) not in sys.path:
    sys.path.insert(0, str(AUTOMATION_DIR))

from validate_agent_engineering_contracts import (  # noqa: E402
    REQUIRED_TASK_STATES,
    validate_delegation_record,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER_PATH = ROOT / "output" / "delegated-tasks.json"
PROFILE_TASK_KIND = {
    "exploration": "DELEGATED_EXPLORATION",
    "implementation": "DELEGATED_IMPLEMENTATION",
    "validation": "DELEGATED_VALIDATION",
    "review_support": "DELEGATED_REVIEW",
    "documentation": "DELEGATED_DOCUMENTATION",
    "ci_triage": "DELEGATED_CI_TRIAGE",
}
TERMINAL_STATES = {
    "SUCCEEDED",
    "FAILED",
    "TIMED_OUT",
    "CANCELLED",
    "LOST",
    "SUPERSEDED",
}


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def _load_ledger(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    payload = _read_json(path)
    if isinstance(payload, list):
        return [entry for entry in payload if isinstance(entry, dict)]
    raise ValueError("delegated task ledger must be a JSON array")


def _record_artifact_ref(path: Path) -> dict[str, str]:
    ref = _display_path(path)
    return {"type": "LOCAL_JSON_ARTIFACT", "path": ref, "ref": ref}


def build_delegated_task_entry(
    *,
    delegation_record: dict[str, Any],
    owner: str,
    requested_at: str,
    status: str = "QUEUED",
    origin: str = "automation/delegation_task_ledger.py",
) -> dict[str, Any]:
    errors = validate_delegation_record(delegation_record)
    if errors:
        raise ValueError("; ".join(errors))
    if status not in REQUIRED_TASK_STATES:
        raise ValueError(f"status must be a governed task state: {status}")

    delegation_task_id = delegation_record["delegation_task_id"]
    profile = delegation_record["profile"]
    engineering_task_id = f"eng-task-{delegation_task_id}"
    write_scope = delegation_record["write_scope"]
    scope = {
        "delegation_profile": profile,
        "parent_engineering_task_id": delegation_record["parent_task_id"],
        "read_scope": delegation_record["read_scope"],
        "write_scope": write_scope,
        "forbidden_actions": delegation_record["forbidden_actions"],
        "evidence_requirements": delegation_record["evidence_requirements"],
        "coordination_notes": delegation_record["coordination_notes"],
        "return_envelope": delegation_record["return_envelope"],
        "return_envelope_received": False,
        "main_agent_review_status": "PENDING",
    }
    return {
        "engineering_task_id": engineering_task_id,
        "task_kind": PROFILE_TASK_KIND[profile],
        "repository": delegation_record["repository"],
        "branch": delegation_record["branch"],
        "owner": owner,
        "requested_at": requested_at,
        "origin": origin,
        "correlation_ref": delegation_task_id,
        "summary": delegation_record["problem_statement"],
        "status": status,
        "runtime": {
            "kind": "agent",
            "runner": "codex-delegation",
        },
        "scope": scope,
        "artifacts": [],
        "evidence_refs": [],
        "cleanup_state": "NOT_REQUIRED",
        "started_at": requested_at if status != "QUEUED" else None,
        "ended_at": requested_at if status in TERMINAL_STATES else None,
        "error_summary": None,
    }


def upsert_delegated_task(
    *,
    ledger_path: Path,
    delegation_record: dict[str, Any],
    owner: str,
    requested_at: str | None = None,
    status: str = "QUEUED",
) -> dict[str, Any]:
    requested_at = requested_at or _utc_now()
    entry = build_delegated_task_entry(
        delegation_record=delegation_record,
        owner=owner,
        requested_at=requested_at,
        status=status,
    )
    ledger = [
        existing
        for existing in _load_ledger(ledger_path)
        if existing.get("engineering_task_id") != entry["engineering_task_id"]
    ]
    entry["artifacts"] = [_display_path(ledger_path)]
    entry["evidence_refs"] = [_record_artifact_ref(ledger_path)]
    ledger.append(entry)
    _write_json(ledger_path, ledger)
    return entry


def update_delegated_task_status(
    *,
    ledger_path: Path,
    engineering_task_id: str,
    status: str,
    ended_at: str | None = None,
    error_summary: str | None = None,
    superseded_by_task_id: str | None = None,
) -> dict[str, Any]:
    if status not in REQUIRED_TASK_STATES:
        raise ValueError(f"status must be a governed task state: {status}")
    ledger = _load_ledger(ledger_path)
    for entry in ledger:
        if entry.get("engineering_task_id") != engineering_task_id:
            continue
        entry["status"] = status
        if status == "RUNNING" and not entry.get("started_at"):
            entry["started_at"] = _utc_now()
        if status in TERMINAL_STATES:
            entry["ended_at"] = ended_at or _utc_now()
        if status in {"FAILED", "TIMED_OUT", "CANCELLED", "LOST"}:
            if not error_summary:
                raise ValueError(f"error_summary is required for {status}")
            entry["error_summary"] = error_summary
        if status == "SUPERSEDED":
            if not superseded_by_task_id:
                raise ValueError("superseded_by_task_id is required for SUPERSEDED")
            entry["superseded_by_task_id"] = superseded_by_task_id
            entry["cleanup_state"] = "SUPERSEDED"
            entry["error_summary"] = error_summary
        _write_json(ledger_path, ledger)
        return entry
    raise ValueError(f"delegated task not found: {engineering_task_id}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Record RFC-0096 delegated task ledger entries."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create")
    create.add_argument("--record", type=Path, required=True)
    create.add_argument("--ledger-path", type=Path, default=DEFAULT_LEDGER_PATH)
    create.add_argument("--owner", required=True)
    create.add_argument("--requested-at", default=None)
    create.add_argument("--status", default="QUEUED")

    update = subparsers.add_parser("update-status")
    update.add_argument("--ledger-path", type=Path, default=DEFAULT_LEDGER_PATH)
    update.add_argument("--engineering-task-id", required=True)
    update.add_argument("--status", required=True)
    update.add_argument("--ended-at", default=None)
    update.add_argument("--error-summary", default=None)
    update.add_argument("--superseded-by-task-id", default=None)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    try:
        if args.command == "create":
            entry = upsert_delegated_task(
                ledger_path=args.ledger_path,
                delegation_record=_read_json(args.record),
                owner=args.owner,
                requested_at=args.requested_at,
                status=args.status,
            )
        else:
            entry = update_delegated_task_status(
                ledger_path=args.ledger_path,
                engineering_task_id=args.engineering_task_id,
                status=args.status,
                ended_at=args.ended_at,
                error_summary=args.error_summary,
                superseded_by_task_id=args.superseded_by_task_id,
            )
    except ValueError as exc:
        print(f"delegated task ledger error: {exc}")
        return 2
    print(json.dumps(entry, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
