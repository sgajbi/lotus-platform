from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = ROOT / "automation" / "delegation_task_ledger.py"
EXAMPLES_DIR = ROOT / "platform-contracts" / "agent-engineering" / "examples"


def _load_module():
    spec = importlib.util.spec_from_file_location("delegation_task_ledger", LEDGER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _example(name: str) -> dict:
    return json.loads((EXAMPLES_DIR / name).read_text(encoding="utf-8"))


def test_delegated_task_entry_maps_profile_to_rfc0094_task_shape() -> None:
    ledger = _load_module()
    record = _example("delegation-implementation-valid.json")

    entry = ledger.build_delegated_task_entry(
        delegation_record=record,
        owner="lotus-platform",
        requested_at="2026-04-21T00:00:00Z",
    )

    assert entry["engineering_task_id"] == "eng-task-delegation-rfc0096-slice1-validator"
    assert entry["task_kind"] == "DELEGATED_IMPLEMENTATION"
    assert entry["repository"] == "lotus-platform"
    assert entry["branch"] == "feature/rfc0096-delegation-implementation"
    assert entry["status"] == "QUEUED"
    assert entry["cleanup_state"] == "NOT_REQUIRED"
    assert entry["scope"]["delegation_profile"] == "implementation"
    assert entry["scope"]["parent_engineering_task_id"] == "rfc-0096-slice-1"
    assert entry["scope"]["write_scope"] == [
        "automation/validate_agent_engineering_contracts.py",
        "tests/unit/test_agent_engineering_contracts.py",
    ]
    assert entry["scope"]["return_envelope_received"] is False
    assert entry["scope"]["main_agent_review_status"] == "PENDING"


def test_upsert_delegated_task_writes_rfc0094_compatible_ledger(tmp_path: Path) -> None:
    ledger = _load_module()
    ledger_path = tmp_path / "delegated-tasks.json"
    record = _example("delegation-exploration-valid.json")

    entry = ledger.upsert_delegated_task(
        ledger_path=ledger_path,
        delegation_record=record,
        owner="lotus-platform",
        requested_at="2026-04-21T00:00:00Z",
    )

    persisted = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert persisted == [entry]
    assert entry["task_kind"] == "DELEGATED_EXPLORATION"
    assert entry["artifacts"] == [str(ledger_path)]
    assert entry["evidence_refs"] == [
        {"type": "LOCAL_JSON_ARTIFACT", "path": str(ledger_path), "ref": str(ledger_path)}
    ]


def test_delegated_task_status_requires_error_context_for_lost(tmp_path: Path) -> None:
    ledger = _load_module()
    ledger_path = tmp_path / "delegated-tasks.json"
    record = _example("delegation-exploration-valid.json")
    entry = ledger.upsert_delegated_task(
        ledger_path=ledger_path,
        delegation_record=record,
        owner="lotus-platform",
        requested_at="2026-04-21T00:00:00Z",
    )

    try:
        ledger.update_delegated_task_status(
            ledger_path=ledger_path,
            engineering_task_id=entry["engineering_task_id"],
            status="LOST",
        )
    except ValueError as exc:
        assert "error_summary is required for LOST" in str(exc)
    else:
        raise AssertionError("expected LOST delegated task to require error_summary")


def test_delegated_task_status_records_terminal_failure_context(tmp_path: Path) -> None:
    ledger = _load_module()
    ledger_path = tmp_path / "delegated-tasks.json"
    record = _example("delegation-exploration-valid.json")
    entry = ledger.upsert_delegated_task(
        ledger_path=ledger_path,
        delegation_record=record,
        owner="lotus-platform",
        requested_at="2026-04-21T00:00:00Z",
    )

    updated = ledger.update_delegated_task_status(
        ledger_path=ledger_path,
        engineering_task_id=entry["engineering_task_id"],
        status="LOST",
        ended_at="2026-04-21T00:30:00Z",
        error_summary="Delegated agent result was not returned.",
    )

    assert updated["status"] == "LOST"
    assert updated["ended_at"] == "2026-04-21T00:30:00Z"
    assert updated["error_summary"] == "Delegated agent result was not returned."


def test_delegated_task_status_records_superseded_replacement_link(tmp_path: Path) -> None:
    ledger = _load_module()
    ledger_path = tmp_path / "delegated-tasks.json"
    record = _example("delegation-implementation-valid.json")
    entry = ledger.upsert_delegated_task(
        ledger_path=ledger_path,
        delegation_record=record,
        owner="lotus-platform",
        requested_at="2026-04-21T00:00:00Z",
    )

    updated = ledger.update_delegated_task_status(
        ledger_path=ledger_path,
        engineering_task_id=entry["engineering_task_id"],
        status="SUPERSEDED",
        ended_at="2026-04-21T00:45:00Z",
        error_summary="Replaced by narrower validator-only task.",
        superseded_by_task_id="eng-task-delegation-rfc0096-slice1-validator-v2",
    )

    assert updated["status"] == "SUPERSEDED"
    assert updated["cleanup_state"] == "SUPERSEDED"
    assert (
        updated["superseded_by_task_id"]
        == "eng-task-delegation-rfc0096-slice1-validator-v2"
    )


def test_delegated_task_cli_create_and_update_status(tmp_path: Path) -> None:
    ledger_path = tmp_path / "delegated-tasks.json"
    record_path = EXAMPLES_DIR / "delegation-exploration-valid.json"

    create = subprocess.run(
        [
            sys.executable,
            str(LEDGER_PATH),
            "create",
            "--record",
            str(record_path),
            "--ledger-path",
            str(ledger_path),
            "--owner",
            "lotus-platform",
            "--requested-at",
            "2026-04-21T00:00:00Z",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    created = json.loads(create.stdout)

    subprocess.run(
        [
            sys.executable,
            str(LEDGER_PATH),
            "update-status",
            "--ledger-path",
            str(ledger_path),
            "--engineering-task-id",
            created["engineering_task_id"],
            "--status",
            "CANCELLED",
            "--ended-at",
            "2026-04-21T01:00:00Z",
            "--error-summary",
            "Main agent handled the work locally.",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    [updated] = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert updated["status"] == "CANCELLED"
    assert updated["error_summary"] == "Main agent handled the work locally."
