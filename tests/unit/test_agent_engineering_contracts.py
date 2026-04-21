from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = (
    ROOT
    / "platform-contracts"
    / "agent-engineering"
    / "engineering-task-ledger-contract.v1.json"
)
VALIDATOR_PATH = ROOT / "automation" / "validate_agent_engineering_contracts.py"


def _load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_agent_engineering_contracts", VALIDATOR_PATH
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_agent_engineering_contract_captures_task_ledger_authority_and_lifecycle() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    assert contract["contract_id"] == "lotus-platform:engineering-task-ledger-contract:v1"
    assert contract["source_rfc"] == "RFC-0094"
    assert contract["related_rfc"] == "RFC-0093"
    assert "source of truth" in contract["authority"]["github_actions"].lower()
    assert "working context" in contract["authority"]["session_summary"].lower()

    assert set(contract["lifecycle_states"]) == {
        "QUEUED",
        "RUNNING",
        "SUCCEEDED",
        "FAILED",
        "TIMED_OUT",
        "CANCELLED",
        "LOST",
        "SUPERSEDED",
    }
    assert "GITHUB_CHECK_MONITOR" in contract["task_kinds"]
    assert "MERGE_CLEANUP_WATCHER" in contract["task_kinds"]
    assert "evidence_refs" in contract["required_metadata_fields"]
    assert "cleanup_state" in contract["required_metadata_fields"]


def test_agent_engineering_contract_preserves_context_and_delegation_requirements() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    context_contract = contract["context_preservation_contract"]
    delegation_contract = contract["delegation_contract"]

    for required_identifier in [
        "repository",
        "branch",
        "pr_number",
        "commit_sha",
        "check_name",
        "rfc_id",
        "file_path",
        "endpoint",
        "contract_name",
        "portfolio_id",
        "task_status",
    ]:
        assert required_identifier in context_contract["required_identifiers"]

    assert set(context_contract["decision_states"]) == {
        "ACCEPTED",
        "REJECTED",
        "DEFERRED",
        "OPEN",
    }
    assert "skill_guidance" in context_contract["promotion_targets"]
    assert "validator_or_contract_test" in context_contract["promotion_targets"]

    for requirement in [
        "explicit_write_scope",
        "do_not_revert_unrelated_work",
        "changed_files_returned",
        "outcome_summary_returned",
    ]:
        assert requirement in delegation_contract["code_change_requirements"]


def test_agent_engineering_contract_validator_passes_for_governed_contract() -> None:
    validator = _load_validator()

    assert validator.validate_agent_engineering_contracts(CONTRACT_PATH) == []


def test_agent_engineering_contract_validator_rejects_missing_required_identifier(
    tmp_path: Path,
) -> None:
    validator = _load_validator()
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    contract["context_preservation_contract"]["required_identifiers"].remove("commit_sha")
    drifted_contract = tmp_path / "engineering-task-ledger-contract.v1.json"
    drifted_contract.write_text(json.dumps(contract), encoding="utf-8")

    errors = validator.validate_agent_engineering_contracts(drifted_contract)

    assert (
        "context_preservation_contract.required_identifiers missing required values: commit_sha"
        in errors
    )
