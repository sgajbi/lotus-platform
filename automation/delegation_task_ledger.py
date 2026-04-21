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
    REQUIRED_DELEGATION_OUTPUT_FIELDS,
    REQUIRED_MAIN_AGENT_REVIEW_STATUSES,
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
REVIEW_TERMINAL_STATUS = {
    "ACCEPTED": "SUCCEEDED",
    "REJECTED": "FAILED",
    "NEEDS_CHANGES": "FAILED",
}


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _validate_utc_timestamp(value: str, field_name: str) -> None:
    if value != value.strip() or not value.endswith("Z"):
        raise ValueError(f"{field_name} must be an RFC-3339 UTC string ending with Z")
    try:
        datetime.fromisoformat(f"{value[:-1]}+00:00")
    except ValueError:
        raise ValueError(f"{field_name} must be an RFC-3339 UTC string ending with Z")


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


def _as_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


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
    _validate_utc_timestamp(requested_at, "requested_at")

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
    if ended_at is not None:
        _validate_utc_timestamp(ended_at, "ended_at")
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


def validate_delegation_output(
    output: dict[str, Any],
    *,
    write_scope: object,
) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_DELEGATION_OUTPUT_FIELDS:
        if field not in output:
            errors.append(f"delegation output missing {field}")

    if output.get("unrelated_work_preserved") is not True:
        errors.append("delegation output must confirm unrelated_work_preserved=true")

    files_changed = output.get("files_changed")
    if not isinstance(files_changed, list):
        errors.append("delegation output files_changed must be a list")
        files_changed = []

    if write_scope == "none" and files_changed:
        errors.append("no-write delegated work must not return changed files")
    elif isinstance(write_scope, list):
        allowed_prefixes = _as_string_list(write_scope)
        for changed_file in _as_string_list(files_changed):
            if changed_file not in allowed_prefixes and not any(
                changed_file.startswith(f"{prefix.rstrip('/')}/")
                for prefix in allowed_prefixes
            ):
                errors.append(f"changed file outside delegated write_scope: {changed_file}")

    checks_run = output.get("checks_run")
    if not isinstance(checks_run, list) or not checks_run:
        errors.append("delegation output checks_run must be a non-empty list")

    evidence_refs = output.get("evidence_refs")
    if not isinstance(evidence_refs, list) or not evidence_refs:
        errors.append("delegation output evidence_refs must be a non-empty list")

    follow_up = output.get("follow_up_required")
    if not isinstance(follow_up, str) or not follow_up.strip():
        errors.append("delegation output follow_up_required must be a non-empty string")
    return errors


def record_delegation_return(
    *,
    ledger_path: Path,
    engineering_task_id: str,
    output_path: Path,
) -> dict[str, Any]:
    output = _read_json(output_path)
    if not isinstance(output, dict):
        raise ValueError("delegation output must be a JSON object")
    ledger = _load_ledger(ledger_path)
    for entry in ledger:
        if entry.get("engineering_task_id") != engineering_task_id:
            continue
        errors = validate_delegation_output(
            output,
            write_scope=entry.get("scope", {}).get("write_scope"),
        )
        if errors:
            raise ValueError("; ".join(errors))
        entry["scope"]["return_envelope_received"] = True
        entry["scope"]["main_agent_review_status"] = "PENDING"
        entry["delegation_output_ref"] = _display_path(output_path)
        entry["artifacts"] = sorted(
            set(_as_string_list(entry.get("artifacts")) + [_display_path(output_path)])
        )
        entry["evidence_refs"] = [
            *[
                ref
                for ref in entry.get("evidence_refs", [])
                if isinstance(ref, dict)
            ],
            _record_artifact_ref(output_path),
        ]
        _write_json(ledger_path, ledger)
        return entry
    raise ValueError(f"delegated task not found: {engineering_task_id}")


def record_main_agent_review(
    *,
    ledger_path: Path,
    engineering_task_id: str,
    review_status: str,
    reviewed_by: str,
    review_summary: str,
    reviewed_at: str | None = None,
) -> dict[str, Any]:
    if review_status not in REQUIRED_MAIN_AGENT_REVIEW_STATUSES - {"PENDING"}:
        raise ValueError("review_status must be ACCEPTED, REJECTED, or NEEDS_CHANGES")
    if not reviewed_by.strip() or not review_summary.strip():
        raise ValueError("reviewed_by and review_summary are required")
    reviewed_at = reviewed_at or _utc_now()
    _validate_utc_timestamp(reviewed_at, "reviewed_at")
    ledger = _load_ledger(ledger_path)
    for entry in ledger:
        if entry.get("engineering_task_id") != engineering_task_id:
            continue
        if not entry.get("scope", {}).get("return_envelope_received"):
            raise ValueError("delegation return envelope must be recorded before review")
        entry["scope"]["main_agent_review_status"] = review_status
        entry["main_agent_review"] = {
            "review_status": review_status,
            "reviewed_by": reviewed_by,
            "reviewed_at": reviewed_at,
            "review_summary": review_summary,
        }
        entry["status"] = REVIEW_TERMINAL_STATUS[review_status]
        entry["ended_at"] = reviewed_at
        if review_status != "ACCEPTED":
            entry["error_summary"] = review_summary
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

    returned = subparsers.add_parser("record-return")
    returned.add_argument("--ledger-path", type=Path, default=DEFAULT_LEDGER_PATH)
    returned.add_argument("--engineering-task-id", required=True)
    returned.add_argument("--output", type=Path, required=True)

    review = subparsers.add_parser("record-review")
    review.add_argument("--ledger-path", type=Path, default=DEFAULT_LEDGER_PATH)
    review.add_argument("--engineering-task-id", required=True)
    review.add_argument("--review-status", required=True)
    review.add_argument("--reviewed-by", required=True)
    review.add_argument("--review-summary", required=True)
    review.add_argument("--reviewed-at", default=None)
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
        elif args.command == "record-return":
            entry = record_delegation_return(
                ledger_path=args.ledger_path,
                engineering_task_id=args.engineering_task_id,
                output_path=args.output,
            )
        elif args.command == "record-review":
            entry = record_main_agent_review(
                ledger_path=args.ledger_path,
                engineering_task_id=args.engineering_task_id,
                review_status=args.review_status,
                reviewed_by=args.reviewed_by,
                review_summary=args.review_summary,
                reviewed_at=args.reviewed_at,
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
