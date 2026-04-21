from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT
    / "platform-contracts"
    / "agent-engineering"
    / "engineering-task-ledger-contract.v1.json"
)

REQUIRED_TASK_STATES = {
    "QUEUED",
    "RUNNING",
    "SUCCEEDED",
    "FAILED",
    "TIMED_OUT",
    "CANCELLED",
    "LOST",
    "SUPERSEDED",
}
REQUIRED_CLEANUP_STATES = {"NOT_REQUIRED", "PENDING", "DONE", "BLOCKED", "SUPERSEDED"}
REQUIRED_TASK_KINDS = {
    "GITHUB_CHECK_MONITOR",
    "LOCAL_BACKGROUND_RUN",
    "VALIDATION_RUN",
    "DELEGATED_EXPLORATION",
    "DELEGATED_IMPLEMENTATION",
    "DELEGATED_REVIEW",
    "MERGE_CLEANUP_WATCHER",
}
REQUIRED_IDENTITY_FIELDS = {
    "engineering_task_id",
    "task_kind",
    "repository",
    "branch",
    "owner",
    "requested_at",
    "origin",
    "correlation_ref",
}
REQUIRED_METADATA_FIELDS = {
    "summary",
    "status",
    "runtime",
    "scope",
    "artifacts",
    "evidence_refs",
    "cleanup_state",
}
REQUIRED_IDENTIFIER_PRESERVATION = {
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
}
REQUIRED_PROMOTION_TARGETS = {
    "repository_docs",
    "central_context",
    "onboarding_docs",
    "wiki_source",
    "skill_guidance",
    "validator_or_contract_test",
    "rfc_follow_up",
}


def _load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require_set(
    errors: list[str], label: str, actual_values: object, required_values: set[str]
) -> None:
    if not isinstance(actual_values, list):
        errors.append(f"{label} must be a list")
        return

    actual = {item for item in actual_values if isinstance(item, str)}
    missing = sorted(required_values - actual)
    if missing:
        errors.append(f"{label} missing required values: {', '.join(missing)}")


def validate_agent_engineering_contracts(path: Path = CONTRACT_PATH) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        display_path = path
        try:
            display_path = path.relative_to(ROOT)
        except ValueError:
            pass
        return [f"missing agent engineering contract: {display_path}"]

    contract = _load_contract(path)
    if contract.get("contract_id") != "lotus-platform:engineering-task-ledger-contract:v1":
        errors.append("contract_id must be lotus-platform:engineering-task-ledger-contract:v1")
    if contract.get("source_rfc") != "RFC-0094":
        errors.append("source_rfc must be RFC-0094")
    if contract.get("related_rfc") != "RFC-0093":
        errors.append("related_rfc must be RFC-0093")
    if contract.get("owner") != "lotus-platform":
        errors.append("owner must be lotus-platform")
    if contract.get("status") != "active":
        errors.append("status must be active")

    authority = contract.get("authority")
    if not isinstance(authority, dict):
        errors.append("authority must be an object")
    else:
        for key in ("github_actions", "local_automation", "task_ledger", "session_summary"):
            value = authority.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"authority.{key} must be non-empty")
        if "source of truth" not in str(authority.get("github_actions", "")).lower():
            errors.append("authority.github_actions must preserve GitHub as source of truth")
        if "working context" not in str(authority.get("session_summary", "")).lower():
            errors.append("authority.session_summary must keep compaction as working context")

    _require_set(errors, "task_kinds", contract.get("task_kinds"), REQUIRED_TASK_KINDS)
    _require_set(
        errors, "lifecycle_states", contract.get("lifecycle_states"), REQUIRED_TASK_STATES
    )
    _require_set(
        errors, "cleanup_states", contract.get("cleanup_states"), REQUIRED_CLEANUP_STATES
    )
    _require_set(
        errors,
        "required_identity_fields",
        contract.get("required_identity_fields"),
        REQUIRED_IDENTITY_FIELDS,
    )
    _require_set(
        errors,
        "required_metadata_fields",
        contract.get("required_metadata_fields"),
        REQUIRED_METADATA_FIELDS,
    )
    _require_set(
        errors,
        "terminal_states",
        contract.get("terminal_states"),
        REQUIRED_TASK_STATES - {"QUEUED", "RUNNING"},
    )

    conditional_fields = contract.get("conditional_fields")
    if not isinstance(conditional_fields, dict):
        errors.append("conditional_fields must be an object")
    else:
        for key in ("pr_number", "write_scope", "started_at", "ended_at", "error_summary"):
            if key not in conditional_fields:
                errors.append(f"conditional_fields missing {key}")

    delegation_contract = contract.get("delegation_contract")
    if not isinstance(delegation_contract, dict):
        errors.append("delegation_contract must be an object")
    else:
        _require_set(
            errors,
            "delegation_contract.required_fields",
            delegation_contract.get("required_fields"),
            {"problem_statement", "expected_output", "read_scope", "task_mode"},
        )
        _require_set(
            errors,
            "delegation_contract.code_change_requirements",
            delegation_contract.get("code_change_requirements"),
            {
                "explicit_write_scope",
                "do_not_revert_unrelated_work",
                "changed_files_returned",
                "outcome_summary_returned",
            },
        )

    context_contract = contract.get("context_preservation_contract")
    if not isinstance(context_contract, dict):
        errors.append("context_preservation_contract must be an object")
    else:
        if context_contract.get("source_rfc") != "RFC-0093":
            errors.append("context_preservation_contract.source_rfc must be RFC-0093")
        _require_set(
            errors,
            "context_preservation_contract.required_identifiers",
            context_contract.get("required_identifiers"),
            REQUIRED_IDENTIFIER_PRESERVATION,
        )
        _require_set(
            errors,
            "context_preservation_contract.decision_states",
            context_contract.get("decision_states"),
            {"ACCEPTED", "REJECTED", "DEFERRED", "OPEN"},
        )
        _require_set(
            errors,
            "context_preservation_contract.promotion_targets",
            context_contract.get("promotion_targets"),
            REQUIRED_PROMOTION_TARGETS,
        )

    invariants = contract.get("invariants")
    if not isinstance(invariants, list) or not invariants:
        errors.append("invariants must be a non-empty list")
    else:
        invariant_text = " ".join(item for item in invariants if isinstance(item, str)).lower()
        for expected in (
            "one durable owner",
            "terminal tasks carry evidence",
            "github status is referenced",
            "explicit write scope",
            "preserve operationally relevant identifiers exactly",
        ):
            if expected not in invariant_text:
                errors.append(f"invariants missing `{expected}`")

    return errors


def main() -> int:
    errors = validate_agent_engineering_contracts()
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Agent engineering contracts validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
