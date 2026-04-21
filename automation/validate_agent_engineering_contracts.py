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
DELEGATION_POLICY_PATH = (
    ROOT
    / "platform-contracts"
    / "agent-engineering"
    / "delegation-policy-contract.v1.json"
)
DELEGATION_EXAMPLES_DIR = (
    ROOT / "platform-contracts" / "agent-engineering" / "examples"
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
    "DELEGATED_VALIDATION",
    "DELEGATED_REVIEW",
    "DELEGATED_DOCUMENTATION",
    "DELEGATED_CI_TRIAGE",
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
REQUIRED_DELEGATION_PROFILES = {
    "exploration",
    "implementation",
    "validation",
    "review_support",
    "documentation",
    "ci_triage",
}
REQUIRED_DISALLOWED_PROFILES = {
    "general_helper",
    "best_effort_worker",
    "do_everything",
}
REQUIRED_DELEGATION_INPUT_FIELDS = {
    "delegation_task_id",
    "parent_task_id",
    "profile",
    "repository",
    "branch",
    "problem_statement",
    "expected_output",
    "read_scope",
    "write_scope",
    "forbidden_actions",
    "evidence_requirements",
    "coordination_notes",
    "return_envelope",
}
REQUIRED_DELEGATION_OUTPUT_FIELDS = {
    "outcome_summary",
    "files_changed",
    "checks_run",
    "evidence_refs",
    "blockers_or_assumptions",
    "remaining_risks",
    "follow_up_required",
    "unrelated_work_preserved",
    "patch_summary_by_write_scope",
}
REQUIRED_FORBIDDEN_ACTIONS = {
    "no_unrelated_reverts",
    "no_broad_cleanup",
    "no_pr_merge",
    "no_wiki_publish_without_main_agent_review",
}
REQUIRED_HEARTBEAT_CONDITIONS = {
    "delegated_task_stale",
    "delegated_task_failed",
    "delegated_task_lost",
    "delegated_task_missing_evidence",
    "delegated_task_write_scope_overlap",
    "delegated_task_unresolved_blocker",
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


def _as_list(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_delegation_policy_contract(path: Path = DELEGATION_POLICY_PATH) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        display_path = path
        try:
            display_path = path.relative_to(ROOT)
        except ValueError:
            pass
        return [f"missing delegation policy contract: {display_path}"]

    contract = _load_contract(path)
    if contract.get("contract_id") != "lotus-platform:delegation-policy-contract:v1":
        errors.append("delegation policy contract_id must be lotus-platform:delegation-policy-contract:v1")
    if contract.get("source_rfc") != "RFC-0096":
        errors.append("delegation policy source_rfc must be RFC-0096")
    if contract.get("depends_on_contract") != "lotus-platform:engineering-task-ledger-contract:v1":
        errors.append("delegation policy depends_on_contract must reference the task-ledger contract")
    if contract.get("owner") != "lotus-platform":
        errors.append("delegation policy owner must be lotus-platform")
    if contract.get("status") != "active":
        errors.append("delegation policy status must be active")

    authority = contract.get("authority")
    if not isinstance(authority, dict):
        errors.append("delegation policy authority must be an object")
    else:
        authority_text = " ".join(str(value).lower() for value in authority.values())
        for expected in ("main agent", "source truth", "evidence, not review", "write_scope"):
            if expected not in authority_text:
                errors.append(f"delegation policy authority missing `{expected}`")

    _require_set(
        errors,
        "delegation_profiles",
        contract.get("delegation_profiles"),
        REQUIRED_DELEGATION_PROFILES,
    )
    _require_set(
        errors,
        "no_write_profiles",
        contract.get("no_write_profiles"),
        {"exploration", "validation", "review_support", "ci_triage"},
    )
    _require_set(
        errors,
        "write_scope_required_profiles",
        contract.get("write_scope_required_profiles"),
        {"implementation", "documentation"},
    )
    _require_set(
        errors,
        "disallowed_profiles",
        contract.get("disallowed_profiles"),
        REQUIRED_DISALLOWED_PROFILES,
    )
    _require_set(
        errors,
        "required_input_fields",
        contract.get("required_input_fields"),
        REQUIRED_DELEGATION_INPUT_FIELDS,
    )
    _require_set(
        errors,
        "required_output_fields",
        contract.get("required_output_fields"),
        REQUIRED_DELEGATION_OUTPUT_FIELDS,
    )
    _require_set(
        errors,
        "required_forbidden_actions",
        contract.get("required_forbidden_actions"),
        REQUIRED_FORBIDDEN_ACTIONS,
    )
    _require_set(
        errors,
        "heartbeat_attention_conditions",
        contract.get("heartbeat_attention_conditions"),
        REQUIRED_HEARTBEAT_CONDITIONS,
    )
    _require_set(
        errors,
        "required_heartbeat_identifiers",
        contract.get("required_heartbeat_identifiers"),
        {
            "engineering_task_id",
            "parent_engineering_task_id",
            "repository",
            "branch",
            "delegation_profile",
            "source_ref",
            "write_scope",
        },
    )

    lifecycle_mapping = contract.get("lifecycle_mapping")
    if not isinstance(lifecycle_mapping, dict):
        errors.append("delegation policy lifecycle_mapping must be an object")
    else:
        missing_statuses = sorted(REQUIRED_TASK_STATES - set(lifecycle_mapping.values()))
        if missing_statuses:
            errors.append(
                "delegation policy lifecycle_mapping missing task states: "
                + ", ".join(missing_statuses)
            )

    invariants = contract.get("invariants")
    if not isinstance(invariants, list) or not invariants:
        errors.append("delegation policy invariants must be a non-empty list")
    else:
        invariant_text = " ".join(item for item in invariants if isinstance(item, str)).lower()
        for expected in (
            "one accountable main agent",
            "evidence and not review",
            "explicit bounded write_scope",
            "write_scope as none",
            "not revert unrelated work",
            "not merge prs or publish wiki",
            "lost delegated work",
            "must not inspect hidden model state",
        ):
            if expected not in invariant_text:
                errors.append(f"delegation policy invariants missing `{expected}`")
    return errors


def validate_delegation_record(
    record: dict[str, Any],
    policy: dict[str, Any] | None = None,
) -> list[str]:
    policy = policy or _load_contract(DELEGATION_POLICY_PATH)
    errors: list[str] = []
    for field in policy["required_input_fields"]:
        if field not in record:
            errors.append(f"delegation record missing {field}")

    profile = record.get("profile")
    if profile in set(policy["disallowed_profiles"]):
        errors.append(f"profile {profile} is disallowed")
    if profile not in set(policy["delegation_profiles"]):
        errors.append("profile must be a governed delegation profile")

    for field in (
        "delegation_task_id",
        "parent_task_id",
        "repository",
        "branch",
        "problem_statement",
        "expected_output",
    ):
        if not _non_empty_string(record.get(field)):
            errors.append(f"{field} must be a non-empty string")

    read_scope = record.get("read_scope")
    if not isinstance(read_scope, list) or not read_scope:
        errors.append("read_scope must be a non-empty list")
    elif "." in read_scope:
        errors.append("read_scope must not be broad repo root")

    write_scope = record.get("write_scope")
    no_write_profiles = set(policy["no_write_profiles"])
    write_required_profiles = set(policy["write_scope_required_profiles"])
    if profile in no_write_profiles and write_scope != "none":
        errors.append("no-write delegation profiles must declare write_scope as none")
    if profile in write_required_profiles:
        if not isinstance(write_scope, list) or not write_scope:
            errors.append("write delegation profiles require a non-empty write_scope list")
        elif "." in write_scope:
            errors.append("write_scope must not be broad repo root")
    elif isinstance(write_scope, list) and "." in write_scope:
        errors.append("write_scope must not be broad repo root")

    forbidden_actions = set(
        item for item in _as_list(record.get("forbidden_actions")) if isinstance(item, str)
    )
    missing_actions = sorted(REQUIRED_FORBIDDEN_ACTIONS - forbidden_actions)
    if missing_actions:
        errors.append(
            "forbidden_actions missing required values: " + ", ".join(missing_actions)
        )

    evidence_requirements = record.get("evidence_requirements")
    if not isinstance(evidence_requirements, list) or not evidence_requirements:
        errors.append("evidence_requirements must be a non-empty list")

    return_envelope = set(
        item for item in _as_list(record.get("return_envelope")) if isinstance(item, str)
    )
    missing_return_fields = sorted(REQUIRED_DELEGATION_OUTPUT_FIELDS - return_envelope)
    if missing_return_fields:
        errors.append(
            "return_envelope missing required values: " + ", ".join(missing_return_fields)
        )
    return errors


def validate_delegation_examples(
    examples_dir: Path = DELEGATION_EXAMPLES_DIR,
) -> list[str]:
    errors: list[str] = []
    if not examples_dir.exists():
        return [f"missing delegation examples directory: {examples_dir.relative_to(ROOT)}"]
    policy = _load_contract(DELEGATION_POLICY_PATH)
    for path in sorted(examples_dir.glob("delegation-*.json")):
        record = _load_contract(path)
        record_errors = validate_delegation_record(record, policy)
        if path.name.endswith("-valid.json"):
            errors.extend(f"{path.name}: {error}" for error in record_errors)
        elif path.name.endswith("-invalid.json") and not record_errors:
            errors.append(f"{path.name}: invalid example must fail validation")
    return errors


def validate_all_agent_engineering_contracts() -> list[str]:
    errors = validate_agent_engineering_contracts(CONTRACT_PATH)
    errors.extend(validate_delegation_policy_contract(DELEGATION_POLICY_PATH))
    errors.extend(validate_delegation_examples(DELEGATION_EXAMPLES_DIR))
    return errors


def main() -> int:
    errors = validate_all_agent_engineering_contracts()
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Agent engineering contracts validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
