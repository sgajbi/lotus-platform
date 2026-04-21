from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "platform-contracts" / "heartbeat" / "heartbeat-status.schema.json"
EXAMPLES_DIR = ROOT / "platform-contracts" / "heartbeat" / "examples"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _as_set(value: object) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if isinstance(item, str)}


def _require_keys(errors: list[str], label: str, data: object, required: set[str]) -> None:
    if not isinstance(data, dict):
        errors.append(f"{label} must be an object")
        return
    missing = sorted(required - set(data))
    if missing:
        errors.append(f"{label} missing required fields: {', '.join(missing)}")


def _validate_evidence_refs(
    errors: list[str], label: str, refs: object, evidence_ref_types: set[str]
) -> None:
    if not isinstance(refs, list) or not refs:
        errors.append(f"{label}.evidence_refs must be a non-empty list")
        return
    for index, ref in enumerate(refs):
        ref_label = f"{label}.evidence_refs[{index}]"
        if not isinstance(ref, dict):
            errors.append(f"{ref_label} must be an object")
            continue
        if ref.get("type") not in evidence_ref_types:
            errors.append(f"{ref_label}.type must be a governed evidence ref type")
        if not isinstance(ref.get("ref"), str) or not ref["ref"].strip():
            errors.append(f"{ref_label}.ref must be non-empty")


def validate_heartbeat_contract(path: Path = CONTRACT_PATH) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"missing heartbeat contract: {path}"]

    contract = _load_json(path)
    if contract.get("contract_id") != "lotus-platform:heartbeat-status:v1":
        errors.append("contract_id must be lotus-platform:heartbeat-status:v1")
    if contract.get("source_rfc") != "RFC-0095":
        errors.append("source_rfc must be RFC-0095")
    if contract.get("owner") != "lotus-platform":
        errors.append("owner must be lotus-platform")
    if contract.get("status") != "active":
        errors.append("status must be active")

    required_sets = {
        "run_statuses": {"healthy", "attention_required", "blocked", "degraded"},
        "source_systems": {
            "github",
            "background_run_ledger",
            "lotus_ai",
            "mesh_certification",
            "wiki_publication",
            "agent_context",
        },
        "read_statuses": {"healthy", "degraded", "missing", "error"},
        "severities": {"info", "warning", "action_required", "blocking"},
        "evidence_ref_types": {
            "GITHUB_ACTIONS_RUN",
            "GITHUB_PR",
            "LOCAL_JSON_ARTIFACT",
            "LOCAL_MARKDOWN_ARTIFACT",
            "LOG_FILE",
            "TEST_COMMAND",
            "CHANGED_FILE_LIST",
            "BRANCH_AUDIT",
            "WIKI_SYNC_CHECK",
            "MESH_CERTIFICATION_ARTIFACT",
            "WORKFLOW_PACK_RUN",
        },
    }
    for key, required in required_sets.items():
        actual = _as_set(contract.get(key))
        missing = sorted(required - actual)
        if missing:
            errors.append(f"{key} missing required values: {', '.join(missing)}")

    artifact_paths = contract.get("artifact_paths")
    if not isinstance(artifact_paths, dict):
        errors.append("artifact_paths must be an object")
    else:
        expected_artifacts = {
            "json": "output/heartbeat/heartbeat-status.json",
            "markdown": "output/heartbeat/heartbeat-status.md",
            "issues": "output/heartbeat/heartbeat-issues.json",
        }
        for key, expected in expected_artifacts.items():
            if artifact_paths.get(key) != expected:
                errors.append(f"artifact_paths.{key} must be {expected}")

    authority = contract.get("authority")
    if not isinstance(authority, dict):
        errors.append("authority must be an object")
    else:
        authority_text = " ".join(str(value).lower() for value in authority.values())
        for expected in ("source truth", "read-only", "missing"):
            if expected not in authority_text:
                errors.append(f"authority must preserve `{expected}` policy")

    invariants = contract.get("required_invariants")
    if not isinstance(invariants, list):
        errors.append("required_invariants must be a list")
    else:
        invariant_text = " ".join(item.lower() for item in invariants if isinstance(item, str))
        for expected in (
            "stable",
            "blocking",
            "missing evidence is not healthy",
            "source_truth remains external",
            "derived evidence",
        ):
            if expected not in invariant_text:
                errors.append(f"required_invariants missing `{expected}`")

    return errors


def validate_heartbeat_status(
    status: dict[str, Any], contract: dict[str, Any] | None = None
) -> list[str]:
    contract = contract or _load_json(CONTRACT_PATH)
    errors: list[str] = []
    required_top_level = _as_set(contract.get("required_top_level_fields"))
    _require_keys(errors, "heartbeat status", status, required_top_level)
    if errors:
        return errors

    if status.get("contract_id") != contract.get("contract_id"):
        errors.append("contract_id must match heartbeat contract")
    if status.get("run_status") not in _as_set(contract.get("run_statuses")):
        errors.append("run_status must be a governed heartbeat run status")
    if not str(status.get("heartbeat_run_id", "")).strip():
        errors.append("heartbeat_run_id must be non-empty")
    if not str(status.get("generated_at_utc", "")).endswith("Z"):
        errors.append("generated_at_utc must be an RFC-3339 UTC string ending with Z")

    source_systems = _as_set(contract.get("source_systems"))
    read_statuses = _as_set(contract.get("read_statuses"))
    severities = _as_set(contract.get("severities"))
    evidence_ref_types = _as_set(contract.get("evidence_ref_types"))
    required_source_fields = _as_set(contract.get("required_source_fields"))
    required_attention_fields = _as_set(contract.get("required_attention_item_fields"))
    required_suppression_fields = _as_set(contract.get("required_suppression_fields"))

    inventory = status.get("source_inventory")
    if not isinstance(inventory, list):
        errors.append("source_inventory must be a list")
    else:
        for index, source in enumerate(inventory):
            label = f"source_inventory[{index}]"
            _require_keys(errors, label, source, required_source_fields)
            if not isinstance(source, dict):
                continue
            if source.get("source_system") not in source_systems:
                errors.append(f"{label}.source_system must be governed")
            if source.get("read_status") not in read_statuses:
                errors.append(f"{label}.read_status must be governed")
            if source.get("read_status") == "healthy" and not source.get("evidence_refs"):
                errors.append(f"{label} healthy source must carry evidence_refs")
            _validate_evidence_refs(errors, label, source.get("evidence_refs"), evidence_ref_types)

    attention_items = status.get("attention_items")
    if not isinstance(attention_items, list):
        errors.append("attention_items must be a list")
        attention_items = []

    severity_counts = {severity: 0 for severity in severities}
    seen_ids: set[str] = set()
    for index, item in enumerate(attention_items):
        label = f"attention_items[{index}]"
        _require_keys(errors, label, item, required_attention_fields)
        if not isinstance(item, dict):
            continue
        item_id = item.get("attention_item_id")
        if item_id in seen_ids:
            errors.append(f"{label}.attention_item_id must be unique")
        if isinstance(item_id, str):
            seen_ids.add(item_id)
        if item.get("source_system") not in source_systems:
            errors.append(f"{label}.source_system must be governed")
        severity = item.get("severity")
        if severity not in severities:
            errors.append(f"{label}.severity must be governed")
        else:
            severity_counts[severity] += 1
        if severity == "blocking" and item.get("suppression"):
            errors.append(f"{label} blocking item cannot be suppressed")
        if not isinstance(item.get("deduplication_key"), str) or not item["deduplication_key"]:
            errors.append(f"{label}.deduplication_key must be non-empty")
        if item.get("deduplication_key") == item.get("attention_item_id"):
            errors.append(f"{label}.deduplication_key must be distinct from attention_item_id")
        if not str(item.get("first_seen_at_utc", "")).endswith("Z"):
            errors.append(f"{label}.first_seen_at_utc must end with Z")
        if not str(item.get("last_seen_at_utc", "")).endswith("Z"):
            errors.append(f"{label}.last_seen_at_utc must end with Z")
        _validate_evidence_refs(errors, label, item.get("evidence_refs"), evidence_ref_types)

        suppression = item.get("suppression")
        if suppression is not None:
            _require_keys(errors, f"{label}.suppression", suppression, required_suppression_fields - {"deduplication_key"})
            if isinstance(suppression, dict) and not str(suppression.get("expires_at_utc", "")).endswith("Z"):
                errors.append(f"{label}.suppression.expires_at_utc must end with Z")

    summary_counts = status.get("summary_counts")
    if not isinstance(summary_counts, dict):
        errors.append("summary_counts must be an object")
    else:
        for severity in severities:
            if summary_counts.get(severity) != severity_counts[severity]:
                errors.append(
                    f"summary_counts.{severity} must equal attention item count {severity_counts[severity]}"
                )

    source_read_errors = status.get("source_read_errors")
    if not isinstance(source_read_errors, list):
        errors.append("source_read_errors must be a list")
    else:
        for index, source_error in enumerate(source_read_errors):
            label = f"source_read_errors[{index}]"
            _require_keys(
                errors,
                label,
                source_error,
                {"source_system", "source_ref", "error_summary", "evidence_refs"},
            )
            if not isinstance(source_error, dict):
                continue
            if source_error.get("source_system") not in source_systems:
                errors.append(f"{label}.source_system must be governed")
            _validate_evidence_refs(
                errors, label, source_error.get("evidence_refs"), evidence_ref_types
            )

    suppression_decisions = status.get("suppression_decisions")
    if not isinstance(suppression_decisions, list):
        errors.append("suppression_decisions must be a list")
    else:
        for index, decision in enumerate(suppression_decisions):
            label = f"suppression_decisions[{index}]"
            _require_keys(errors, label, decision, required_suppression_fields)
            if isinstance(decision, dict) and not str(decision.get("expires_at_utc", "")).endswith("Z"):
                errors.append(f"{label}.expires_at_utc must end with Z")

    unhealthy_source = any(
        isinstance(source, dict) and source.get("read_status") in {"missing", "error"}
        for source in inventory or []
    )
    if unhealthy_source and not attention_items:
        errors.append("missing or errored source evidence must produce an attention item")

    return errors


def validate_heartbeat_status_path(path: Path) -> list[str]:
    try:
        status = _load_json(path)
    except json.JSONDecodeError as exc:
        return [f"{path}: invalid JSON: {exc}"]
    return validate_heartbeat_status(status)


def validate_heartbeat_examples(examples_dir: Path = EXAMPLES_DIR) -> list[str]:
    errors: list[str] = []
    if not examples_dir.exists():
        return [f"missing heartbeat examples directory: {examples_dir}"]
    for path in sorted(examples_dir.glob("*.json")):
        for error in validate_heartbeat_status_path(path):
            errors.append(f"{path.name}: {error}")
    return errors


def validate_heartbeat_contracts() -> list[str]:
    errors = validate_heartbeat_contract(CONTRACT_PATH)
    errors.extend(validate_heartbeat_examples(EXAMPLES_DIR))
    return errors


def main() -> int:
    errors = validate_heartbeat_contracts()
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Heartbeat contracts validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
