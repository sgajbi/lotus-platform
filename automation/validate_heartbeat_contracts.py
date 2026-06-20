from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "platform-contracts" / "heartbeat" / "heartbeat-status.schema.json"
EXAMPLES_DIR = ROOT / "platform-contracts" / "heartbeat" / "examples"
CONFIG_PATH = ROOT / "automation" / "heartbeat-config.json"
SUPPRESSIONS_PATH = (
    ROOT / "platform-contracts" / "heartbeat" / "heartbeat-suppressions.json"
)
HEARTBEAT_SUPPRESSION_REQUIRED_FIELDS = {
    "deduplication_key",
    "owner",
    "reason",
    "expires_at_utc",
}


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


def _is_rfc3339_utc(value: object) -> bool:
    if not isinstance(value, str) or value != value.strip() or not value.endswith("Z"):
        return False
    try:
        datetime.fromisoformat(f"{value[:-1]}+00:00")
    except ValueError:
        return False
    return True


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


def _validate_status_source_inventory(
    *,
    errors: list[str],
    status: dict[str, Any],
    source_systems: set[str],
    read_statuses: set[str],
    evidence_ref_types: set[str],
    required_source_fields: set[str],
) -> list[Any]:
    inventory = status.get("source_inventory")
    if not isinstance(inventory, list):
        errors.append("source_inventory must be a list")
        return []

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

    return inventory


def _validate_attention_item_identity(
    *,
    errors: list[str],
    label: str,
    item: dict[str, Any],
    seen_ids: set[str],
) -> None:
    item_id = item.get("attention_item_id")
    if item_id in seen_ids:
        errors.append(f"{label}.attention_item_id must be unique")
    if isinstance(item_id, str):
        seen_ids.add(item_id)


def _validate_attention_item_governance(
    *,
    errors: list[str],
    label: str,
    item: dict[str, Any],
    source_systems: set[str],
    severities: set[str],
    severity_counts: dict[str, int],
) -> object:
    if item.get("source_system") not in source_systems:
        errors.append(f"{label}.source_system must be governed")
    severity = item.get("severity")
    if severity not in severities:
        errors.append(f"{label}.severity must be governed")
    else:
        severity_counts[severity] += 1
    return severity


def _validate_attention_item_deduplication(
    *, errors: list[str], label: str, item: dict[str, Any]
) -> None:
    if not isinstance(item.get("deduplication_key"), str) or not item["deduplication_key"]:
        errors.append(f"{label}.deduplication_key must be non-empty")
    if item.get("deduplication_key") == item.get("attention_item_id"):
        errors.append(f"{label}.deduplication_key must be distinct from attention_item_id")


def _validate_attention_item_timestamps(
    *, errors: list[str], label: str, item: dict[str, Any]
) -> None:
    if not _is_rfc3339_utc(item.get("first_seen_at_utc")):
        errors.append(f"{label}.first_seen_at_utc must be an RFC-3339 UTC string ending with Z")
    if not _is_rfc3339_utc(item.get("last_seen_at_utc")):
        errors.append(f"{label}.last_seen_at_utc must be an RFC-3339 UTC string ending with Z")


def _validate_attention_item_suppression(
    *,
    errors: list[str],
    label: str,
    item: dict[str, Any],
    severity: object,
    required_suppression_fields: set[str],
) -> None:
    suppression = item.get("suppression")
    if severity == "blocking" and suppression:
        errors.append(f"{label} blocking item cannot be suppressed")
    if suppression is None:
        return
    _require_keys(
        errors,
        f"{label}.suppression",
        suppression,
        required_suppression_fields - {"deduplication_key"},
    )
    if isinstance(suppression, dict) and not _is_rfc3339_utc(suppression.get("expires_at_utc")):
        errors.append(
            f"{label}.suppression.expires_at_utc must be an RFC-3339 UTC string ending with Z"
        )


def _validate_attention_item(
    *,
    errors: list[str],
    label: str,
    item: dict[str, Any],
    seen_ids: set[str],
    source_systems: set[str],
    severities: set[str],
    evidence_ref_types: set[str],
    required_suppression_fields: set[str],
    severity_counts: dict[str, int],
) -> None:
    _validate_attention_item_identity(
        errors=errors, label=label, item=item, seen_ids=seen_ids
    )
    severity = _validate_attention_item_governance(
        errors=errors,
        label=label,
        item=item,
        source_systems=source_systems,
        severities=severities,
        severity_counts=severity_counts,
    )
    _validate_attention_item_suppression(
        errors=errors,
        label=label,
        item=item,
        severity=severity,
        required_suppression_fields=required_suppression_fields,
    )
    _validate_attention_item_deduplication(errors=errors, label=label, item=item)
    _validate_attention_item_timestamps(errors=errors, label=label, item=item)
    _validate_evidence_refs(errors, label, item.get("evidence_refs"), evidence_ref_types)


def _validate_status_attention_items(
    *,
    errors: list[str],
    status: dict[str, Any],
    source_systems: set[str],
    severities: set[str],
    evidence_ref_types: set[str],
    required_attention_fields: set[str],
    required_suppression_fields: set[str],
) -> tuple[list[Any], dict[str, int]]:
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
        _validate_attention_item(
            errors=errors,
            label=label,
            item=item,
            seen_ids=seen_ids,
            source_systems=source_systems,
            severities=severities,
            evidence_ref_types=evidence_ref_types,
            required_suppression_fields=required_suppression_fields,
            severity_counts=severity_counts,
        )

    return attention_items, severity_counts


def _heartbeat_status_contract_sets(contract: dict[str, Any]) -> dict[str, set[str]]:
    return {
        "source_systems": _as_set(contract.get("source_systems")),
        "read_statuses": _as_set(contract.get("read_statuses")),
        "severities": _as_set(contract.get("severities")),
        "evidence_ref_types": _as_set(contract.get("evidence_ref_types")),
        "required_source_fields": _as_set(contract.get("required_source_fields")),
        "required_attention_fields": _as_set(
            contract.get("required_attention_item_fields")
        ),
        "required_suppression_fields": _as_set(
            contract.get("required_suppression_fields")
        ),
    }


def _validate_status_identity(
    *,
    errors: list[str],
    status: dict[str, Any],
    contract: dict[str, Any],
) -> None:
    if status.get("contract_id") != contract.get("contract_id"):
        errors.append("contract_id must match heartbeat contract")
    if status.get("run_status") not in _as_set(contract.get("run_statuses")):
        errors.append("run_status must be a governed heartbeat run status")
    if not str(status.get("heartbeat_run_id", "")).strip():
        errors.append("heartbeat_run_id must be non-empty")
    if not _is_rfc3339_utc(status.get("generated_at_utc")):
        errors.append("generated_at_utc must be an RFC-3339 UTC string ending with Z")


def _validate_status_summary_counts(
    *,
    errors: list[str],
    status: dict[str, Any],
    severities: set[str],
    severity_counts: dict[str, int],
) -> None:
    summary_counts = status.get("summary_counts")
    if not isinstance(summary_counts, dict):
        errors.append("summary_counts must be an object")
        return

    for severity in severities:
        if summary_counts.get(severity) != severity_counts[severity]:
            errors.append(
                f"summary_counts.{severity} must equal attention item count {severity_counts[severity]}"
            )


def _validate_source_read_errors(
    *,
    errors: list[str],
    status: dict[str, Any],
    source_systems: set[str],
    evidence_ref_types: set[str],
) -> None:
    source_read_errors = status.get("source_read_errors")
    if not isinstance(source_read_errors, list):
        errors.append("source_read_errors must be a list")
        return

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


def _validate_status_suppression_decisions(
    *,
    errors: list[str],
    status: dict[str, Any],
    required_suppression_fields: set[str],
) -> None:
    suppression_decisions = status.get("suppression_decisions")
    if not isinstance(suppression_decisions, list):
        errors.append("suppression_decisions must be a list")
        return

    for index, decision in enumerate(suppression_decisions):
        label = f"suppression_decisions[{index}]"
        _require_keys(errors, label, decision, required_suppression_fields)
        if isinstance(decision, dict) and not _is_rfc3339_utc(decision.get("expires_at_utc")):
            errors.append(
                f"{label}.expires_at_utc must be an RFC-3339 UTC string ending with Z"
            )


def _validate_unhealthy_sources_emit_attention(
    *,
    errors: list[str],
    inventory: list[Any],
    attention_items: list[Any],
) -> None:
    unhealthy_source = any(
        isinstance(source, dict) and source.get("read_status") in {"missing", "error"}
        for source in inventory
    )
    if unhealthy_source and not attention_items:
        errors.append("missing or errored source evidence must produce an attention item")


def _validate_heartbeat_contract_identity(
    contract: dict[str, Any], errors: list[str]
) -> None:
    if contract.get("contract_id") != "lotus-platform:heartbeat-status:v1":
        errors.append("contract_id must be lotus-platform:heartbeat-status:v1")
    if contract.get("source_rfc") != "RFC-0095":
        errors.append("source_rfc must be RFC-0095")
    if contract.get("owner") != "lotus-platform":
        errors.append("owner must be lotus-platform")
    if contract.get("status") != "active":
        errors.append("status must be active")


def _validate_heartbeat_contract_required_sets(
    contract: dict[str, Any], errors: list[str]
) -> None:
    required_sets = {
        "run_statuses": {"healthy", "attention_required", "blocked", "degraded"},
        "source_systems": {
            "github",
            "background_run_ledger",
            "delegated_task_ledger",
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


def _validate_heartbeat_contract_artifact_paths(
    contract: dict[str, Any], errors: list[str]
) -> None:
    artifact_paths = contract.get("artifact_paths")
    if not isinstance(artifact_paths, dict):
        errors.append("artifact_paths must be an object")
        return
    expected_artifacts = {
        "json": "output/heartbeat/heartbeat-status.json",
        "markdown": "output/heartbeat/heartbeat-status.md",
        "issues": "output/heartbeat/heartbeat-issues.json",
    }
    for key, expected in expected_artifacts.items():
        if artifact_paths.get(key) != expected:
            errors.append(f"artifact_paths.{key} must be {expected}")


def _validate_heartbeat_contract_authority(
    contract: dict[str, Any], errors: list[str]
) -> None:
    authority = contract.get("authority")
    if not isinstance(authority, dict):
        errors.append("authority must be an object")
        return
    authority_text = " ".join(str(value).lower() for value in authority.values())
    for expected in ("source truth", "read-only", "missing"):
        if expected not in authority_text:
            errors.append(f"authority must preserve `{expected}` policy")


def _validate_heartbeat_contract_invariants(
    contract: dict[str, Any], errors: list[str]
) -> None:
    invariants = contract.get("required_invariants")
    if not isinstance(invariants, list):
        errors.append("required_invariants must be a list")
        return
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


def validate_heartbeat_contract(path: Path = CONTRACT_PATH) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"missing heartbeat contract: {path}"]

    contract = _load_json(path)
    _validate_heartbeat_contract_identity(contract, errors)
    _validate_heartbeat_contract_required_sets(contract, errors)
    _validate_heartbeat_contract_artifact_paths(contract, errors)
    _validate_heartbeat_contract_authority(contract, errors)
    _validate_heartbeat_contract_invariants(contract, errors)
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

    _validate_status_identity(errors=errors, status=status, contract=contract)
    contract_sets = _heartbeat_status_contract_sets(contract)

    inventory = _validate_status_source_inventory(
        errors=errors,
        status=status,
        source_systems=contract_sets["source_systems"],
        read_statuses=contract_sets["read_statuses"],
        evidence_ref_types=contract_sets["evidence_ref_types"],
        required_source_fields=contract_sets["required_source_fields"],
    )
    attention_items, severity_counts = _validate_status_attention_items(
        errors=errors,
        status=status,
        source_systems=contract_sets["source_systems"],
        severities=contract_sets["severities"],
        evidence_ref_types=contract_sets["evidence_ref_types"],
        required_attention_fields=contract_sets["required_attention_fields"],
        required_suppression_fields=contract_sets["required_suppression_fields"],
    )
    _validate_status_summary_counts(
        errors=errors,
        status=status,
        severities=contract_sets["severities"],
        severity_counts=severity_counts,
    )
    _validate_source_read_errors(
        errors=errors,
        status=status,
        source_systems=contract_sets["source_systems"],
        evidence_ref_types=contract_sets["evidence_ref_types"],
    )
    _validate_status_suppression_decisions(
        errors=errors,
        status=status,
        required_suppression_fields=contract_sets["required_suppression_fields"],
    )
    _validate_unhealthy_sources_emit_attention(
        errors=errors,
        inventory=inventory,
        attention_items=attention_items,
    )
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


def _validate_runner_config_identity(errors: list[str], config: dict[str, Any]) -> None:
    if config.get("contract_id") != "lotus-platform:heartbeat-runner-config:v1":
        errors.append("heartbeat config contract_id must be lotus-platform:heartbeat-runner-config:v1")
    if config.get("source_rfc") != "RFC-0095":
        errors.append("heartbeat config source_rfc must be RFC-0095")
    if config.get("mode") != "advisory":
        errors.append("heartbeat config mode must be advisory")
    if config.get("mutation_policy") != "read_only":
        errors.append("heartbeat config mutation_policy must be read_only")


def _validate_runner_config_paths(errors: list[str], config: dict[str, Any]) -> None:
    for key in ("output_directory", "state_path", "suppression_file_path"):
        if not isinstance(config.get(key), str) or not config[key].strip():
            errors.append(f"heartbeat config {key} must be a non-empty string")


def _validate_runner_config_enabled_sources(
    errors: list[str], config: dict[str, Any], *, source_systems: set[str]
) -> None:
    enabled_sources = config.get("enabled_sources")
    if not isinstance(enabled_sources, list):
        errors.append("heartbeat config enabled_sources must be a list")
        return
    unknown_sources = sorted(set(enabled_sources) - source_systems)
    if unknown_sources:
        errors.append(
            "heartbeat config enabled_sources contains unknown source systems: "
            + ", ".join(unknown_sources)
        )


def _validate_runner_config_source_config(
    errors: list[str], config: dict[str, Any], *, source_systems: set[str]
) -> None:
    source_config = config.get("source_config")
    if not isinstance(source_config, dict):
        errors.append("heartbeat config source_config must be an object")
        return
    unknown_config_sources = sorted(set(source_config) - source_systems)
    if unknown_config_sources:
        errors.append(
            "heartbeat config source_config contains unknown source systems: "
            + ", ".join(unknown_config_sources)
        )


def _validate_runner_config_thresholds(errors: list[str], config: dict[str, Any]) -> None:
    thresholds = config.get("thresholds")
    if not isinstance(thresholds, dict):
        errors.append("heartbeat config thresholds must be an object")
        return
    for key, value in thresholds.items():
        if not isinstance(value, int | float) or value <= 0:
            errors.append(f"heartbeat config thresholds.{key} must be a positive number")


def validate_heartbeat_runner_config(path: Path = CONFIG_PATH) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"missing heartbeat runner config: {path}"]
    try:
        config = _load_json(path)
    except json.JSONDecodeError as exc:
        return [f"{path}: invalid JSON: {exc}"]

    _validate_runner_config_identity(errors, config)
    _validate_runner_config_paths(errors, config)
    contract = _load_json(CONTRACT_PATH)
    source_systems = _as_set(contract.get("source_systems"))
    _validate_runner_config_enabled_sources(
        errors, config, source_systems=source_systems
    )
    _validate_runner_config_source_config(
        errors, config, source_systems=source_systems
    )
    _validate_runner_config_thresholds(errors, config)

    return errors


def _validate_heartbeat_suppressions_identity(
    errors: list[str], payload: dict[str, Any]
) -> None:
    if payload.get("contract_id") != "lotus-platform:heartbeat-suppressions:v1":
        errors.append(
            "heartbeat suppressions contract_id must be lotus-platform:heartbeat-suppressions:v1"
        )
    if payload.get("source_rfc") != "RFC-0095":
        errors.append("heartbeat suppressions source_rfc must be RFC-0095")


def _heartbeat_suppression_entries(
    errors: list[str], payload: dict[str, Any]
) -> list[Any] | None:
    suppressions = payload.get("suppressions")
    if not isinstance(suppressions, list):
        errors.append("heartbeat suppressions must be a list")
        return None
    return suppressions


def _validate_heartbeat_suppression_strings(
    errors: list[str], label: str, suppression: dict[str, Any]
) -> None:
    for key in sorted(HEARTBEAT_SUPPRESSION_REQUIRED_FIELDS):
        if not isinstance(suppression.get(key), str) or not suppression[key].strip():
            errors.append(f"{label}.{key} must be a non-empty string")


def _validate_heartbeat_suppression_expiry(
    errors: list[str], label: str, suppression: dict[str, Any]
) -> None:
    if not _is_rfc3339_utc(suppression.get("expires_at_utc")):
        errors.append(
            f"{label}.expires_at_utc must be an RFC-3339 UTC string ending with Z"
        )


def _validate_heartbeat_suppression_entry(
    errors: list[str], label: str, suppression: object
) -> None:
    _require_keys(errors, label, suppression, HEARTBEAT_SUPPRESSION_REQUIRED_FIELDS)
    if not isinstance(suppression, dict):
        return
    _validate_heartbeat_suppression_strings(errors, label, suppression)
    _validate_heartbeat_suppression_expiry(errors, label, suppression)


def validate_heartbeat_suppressions(path: Path = SUPPRESSIONS_PATH) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"missing heartbeat suppressions policy: {path}"]
    try:
        payload = _load_json(path)
    except json.JSONDecodeError as exc:
        return [f"{path}: invalid JSON: {exc}"]
    _validate_heartbeat_suppressions_identity(errors, payload)
    suppressions = _heartbeat_suppression_entries(errors, payload)
    if suppressions is None:
        return errors
    for index, suppression in enumerate(suppressions):
        _validate_heartbeat_suppression_entry(
            errors, f"heartbeat suppressions[{index}]", suppression
        )
    return errors


def validate_heartbeat_contracts() -> list[str]:
    errors = validate_heartbeat_contract(CONTRACT_PATH)
    errors.extend(validate_heartbeat_examples(EXAMPLES_DIR))
    errors.extend(validate_heartbeat_runner_config(CONFIG_PATH))
    errors.extend(validate_heartbeat_suppressions(SUPPRESSIONS_PATH))
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
