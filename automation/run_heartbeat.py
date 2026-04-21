from __future__ import annotations

import argparse
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "platform-contracts" / "heartbeat" / "heartbeat-status.schema.json"
DEFAULT_CONFIG_PATH = ROOT / "automation" / "heartbeat-config.json"
DEFAULT_OUTPUT_DIR = ROOT / "output" / "heartbeat"
STATUS_FILENAME = "heartbeat-status.json"
MARKDOWN_FILENAME = "heartbeat-status.md"
ISSUES_FILENAME = "heartbeat-issues.json"

RUNNER_CONFIG_CONTRACT_ID = "lotus-platform:heartbeat-runner-config:v1"
HEARTBEAT_STATUS_CONTRACT_ID = "lotus-platform:heartbeat-status:v1"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _heartbeat_run_id(generated_at_utc: str) -> str:
    compact_timestamp = generated_at_utc.replace("-", "").replace(":", "").replace(".", "")
    return f"heartbeat-{compact_timestamp}"


def _validate_generated_at_utc(generated_at_utc: str) -> None:
    if not generated_at_utc.endswith("Z"):
        raise ValueError("generated_at_utc must be an RFC-3339 UTC string ending with Z")


def _git_branch(root: Path = ROOT) -> str:
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "unknown"
    return result.stdout.strip() or "unknown"


def _governed_source_systems() -> set[str]:
    contract = _read_json(CONTRACT_PATH)
    return set(contract["source_systems"])


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    config = _read_json(path)
    errors: list[str] = []
    if config.get("contract_id") != RUNNER_CONFIG_CONTRACT_ID:
        errors.append(f"contract_id must be {RUNNER_CONFIG_CONTRACT_ID}")
    if config.get("mutation_policy") != "read_only":
        errors.append("mutation_policy must be read_only")
    if config.get("mode") != "advisory":
        errors.append("mode must be advisory")
    enabled_sources = config.get("enabled_sources")
    if not isinstance(enabled_sources, list):
        errors.append("enabled_sources must be a list")
    else:
        governed_sources = _governed_source_systems()
        unknown_sources = sorted(set(enabled_sources) - governed_sources)
        if unknown_sources:
            errors.append(f"enabled_sources contains unknown source systems: {', '.join(unknown_sources)}")
    output_directory = config.get("output_directory")
    if not isinstance(output_directory, str) or not output_directory.strip():
        errors.append("output_directory must be a non-empty string")
    if errors:
        raise ValueError("; ".join(errors))
    return config


def _severity_counts(attention_items: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"info": 0, "warning": 0, "action_required": 0, "blocking": 0}
    for item in attention_items:
        severity = str(item.get("severity", ""))
        if severity in counts:
            counts[severity] += 1
    return counts


def _run_status(attention_items: list[dict[str, Any]], source_read_errors: list[dict[str, Any]]) -> str:
    severities = {item.get("severity") for item in attention_items}
    if "blocking" in severities:
        return "blocked"
    if "action_required" in severities:
        return "attention_required"
    if source_read_errors:
        return "degraded"
    if "warning" in severities:
        return "attention_required"
    return "healthy"


def _evidence_ref(ref_type: str, ref: str) -> dict[str, str]:
    return {"type": ref_type, "ref": ref}


def _task_evidence_ref(ref_type: str, path: str) -> dict[str, str]:
    return {"type": ref_type, "path": path, "ref": path}


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def _not_implemented_source(
    *,
    source_system: str,
    config_path: Path,
    repository: str,
    generated_at_utc: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    source_ref = f"configured_source:{source_system}"
    evidence_refs = [_evidence_ref("LOCAL_JSON_ARTIFACT", str(config_path))]
    source = {
        "source_system": source_system,
        "source_ref": source_ref,
        "read_status": "degraded",
        "owner": repository,
        "freshness_at_utc": generated_at_utc,
        "evidence_refs": evidence_refs,
    }
    item = {
        "attention_item_id": f"{source_system}:source_adapter_not_implemented",
        "condition": "source_adapter_not_implemented",
        "source_system": source_system,
        "source_ref": source_ref,
        "repository": repository,
        "severity": "action_required",
        "owner": repository,
        "first_seen_at_utc": generated_at_utc,
        "last_seen_at_utc": generated_at_utc,
        "evidence_refs": evidence_refs,
        "recommended_next_action": (
            f"Implement the RFC-0095 heartbeat adapter for {source_system} before enabling it routinely."
        ),
        "deduplication_key": f"{source_system}:{source_ref}:source_adapter_not_implemented",
    }
    source_error = {
        "source_system": source_system,
        "source_ref": source_ref,
        "error_summary": "Heartbeat source is configured but no read adapter is implemented yet.",
        "evidence_refs": evidence_refs,
    }
    return source, item, source_error


def _task_ledger_metadata(
    *,
    heartbeat_run_id: str,
    repository: str,
    branch: str,
    owner: str,
    generated_at_utc: str,
    output_dir: Path,
    enabled_sources: list[str],
    run_status: str,
) -> dict[str, Any]:
    artifact_refs = [
        _display_path(output_dir / STATUS_FILENAME),
        _display_path(output_dir / MARKDOWN_FILENAME),
        _display_path(output_dir / ISSUES_FILENAME),
    ]
    return {
        "engineering_task_id": f"eng-task-{heartbeat_run_id}",
        "task_kind": "VALIDATION_RUN",
        "repository": repository,
        "branch": branch,
        "owner": owner,
        "requested_at": generated_at_utc,
        "origin": "automation/run_heartbeat.py",
        "correlation_ref": heartbeat_run_id,
        "summary": f"RFC-0095 heartbeat run for {repository}",
        "status": "SUCCEEDED",
        "runtime": {
            "kind": "python",
            "runner": "automation/run_heartbeat.py",
        },
        "scope": {
            "enabled_sources": enabled_sources,
            "output_directory": _display_path(output_dir),
            "run_status": run_status,
        },
        "artifacts": artifact_refs,
        "evidence_refs": [
            _task_evidence_ref("LOCAL_JSON_ARTIFACT", artifact_refs[0]),
            _task_evidence_ref("LOCAL_MARKDOWN_ARTIFACT", artifact_refs[1]),
            _task_evidence_ref("LOCAL_JSON_ARTIFACT", artifact_refs[2]),
        ],
        "cleanup_state": "NOT_REQUIRED",
        "started_at": generated_at_utc,
        "ended_at": generated_at_utc,
        "error_summary": None,
    }


def build_heartbeat_status(
    *,
    config: dict[str, Any],
    config_path: Path,
    output_dir: Path,
    generated_at_utc: str,
    branch: str | None = None,
) -> dict[str, Any]:
    repository = str(config.get("repository") or "lotus-platform")
    owner = str(config.get("owner") or repository)
    enabled_sources = sorted(str(source) for source in config.get("enabled_sources", []))

    source_inventory: list[dict[str, Any]] = []
    attention_items: list[dict[str, Any]] = []
    source_read_errors: list[dict[str, Any]] = []
    for source_system in enabled_sources:
        source, item, source_error = _not_implemented_source(
            source_system=source_system,
            config_path=config_path,
            repository=repository,
            generated_at_utc=generated_at_utc,
        )
        source_inventory.append(source)
        attention_items.append(item)
        source_read_errors.append(source_error)

    summary_counts = _severity_counts(attention_items)
    run_status = _run_status(attention_items, source_read_errors)
    heartbeat_run_id = _heartbeat_run_id(generated_at_utc)

    status: dict[str, Any] = {
        "contract_id": HEARTBEAT_STATUS_CONTRACT_ID,
        "contract_version": "1.0",
        "heartbeat_run_id": heartbeat_run_id,
        "generated_at_utc": generated_at_utc,
        "run_status": run_status,
        "source_truth": "external",
        "mode": str(config.get("mode", "advisory")),
        "mutation_policy": str(config.get("mutation_policy", "read_only")),
        "source_inventory": source_inventory,
        "summary_counts": summary_counts,
        "attention_items": attention_items,
        "source_read_errors": source_read_errors,
        "suppression_decisions": [],
        "configured_sources": enabled_sources,
    }
    status["task_ledger"] = _task_ledger_metadata(
        heartbeat_run_id=heartbeat_run_id,
        repository=repository,
        branch=branch or _git_branch(),
        owner=owner,
        generated_at_utc=generated_at_utc,
        output_dir=output_dir,
        enabled_sources=enabled_sources,
        run_status=run_status,
    )
    return status


def render_markdown(status: dict[str, Any]) -> str:
    lines = [
        "# Heartbeat Status",
        "",
        f"- Contract: `{status['contract_id']}`",
        f"- Heartbeat run: `{status['heartbeat_run_id']}`",
        f"- Generated at UTC: `{status['generated_at_utc']}`",
        f"- Run status: `{status['run_status']}`",
        f"- Source truth: `{status['source_truth']}`",
        f"- Mode: `{status['mode']}`",
        f"- Mutation policy: `{status['mutation_policy']}`",
        "",
        "## Summary Counts",
        "",
    ]
    for severity, count in status["summary_counts"].items():
        lines.append(f"- `{severity}`: {count}")
    lines.extend(["", "## Source Inventory", ""])
    if status["source_inventory"]:
        for source in status["source_inventory"]:
            lines.append(
                "- "
                f"`{source['source_system']}` `{source['source_ref']}` "
                f"is `{source['read_status']}`"
            )
    else:
        lines.append("No source adapters were enabled for this heartbeat run.")

    lines.extend(["", "## Attention Items", ""])
    if status["attention_items"]:
        for item in status["attention_items"]:
            lines.extend(
                [
                    f"### `{item['attention_item_id']}`",
                    "",
                    f"- Condition: `{item['condition']}`",
                    f"- Source: `{item['source_system']}` `{item['source_ref']}`",
                    f"- Repository: `{item['repository']}`",
                    f"- Severity: `{item['severity']}`",
                    f"- Owner: `{item['owner']}`",
                    f"- Deduplication key: `{item['deduplication_key']}`",
                    f"- Recommended next action: {item['recommended_next_action']}",
                    "",
                ]
            )
    else:
        lines.append("No attention items were produced.")

    task_ledger = status["task_ledger"]
    lines.extend(
        [
            "",
            "## Task Ledger Metadata",
            "",
            f"- Engineering task: `{task_ledger['engineering_task_id']}`",
            f"- Task kind: `{task_ledger['task_kind']}`",
            f"- Repository: `{task_ledger['repository']}`",
            f"- Branch: `{task_ledger['branch']}`",
            f"- Status: `{task_ledger['status']}`",
            "",
            "Heartbeat output is derived evidence. It does not replace GitHub, local automation ledgers, runtime APIs, mesh certification artifacts, wiki source, or context validators as source truth.",
            "",
        ]
    )
    return "\n".join(lines)


def write_heartbeat_artifacts(status: dict[str, Any], output_dir: Path) -> None:
    _write_json(output_dir / STATUS_FILENAME, status)
    (output_dir / MARKDOWN_FILENAME).write_text(render_markdown(status), encoding="utf-8")
    _write_json(output_dir / ISSUES_FILENAME, status["attention_items"])


def run_heartbeat(
    *,
    config_path: Path = DEFAULT_CONFIG_PATH,
    output_dir: Path | None = None,
    generated_at_utc: str | None = None,
    branch: str | None = None,
) -> dict[str, Any]:
    config = load_config(config_path)
    resolved_output_dir = output_dir or ROOT / str(config["output_directory"])
    generated_at = generated_at_utc or _utc_now()
    _validate_generated_at_utc(generated_at)
    status = build_heartbeat_status(
        config=config,
        config_path=config_path,
        output_dir=resolved_output_dir,
        generated_at_utc=generated_at,
        branch=branch,
    )
    write_heartbeat_artifacts(status, resolved_output_dir)
    return status


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate RFC-0095 heartbeat status artifacts."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Heartbeat runner configuration JSON.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Override output directory for heartbeat artifacts.",
    )
    parser.add_argument(
        "--generated-at-utc",
        default=None,
        help="Deterministic generated_at_utc value for tests and GitHub runners.",
    )
    parser.add_argument(
        "--branch",
        default=None,
        help="Explicit branch name to record in task-ledger metadata.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    try:
        status = run_heartbeat(
            config_path=args.config,
            output_dir=args.output_dir,
            generated_at_utc=args.generated_at_utc,
            branch=args.branch,
        )
    except ValueError as exc:
        print(f"heartbeat configuration error: {exc}")
        return 2
    print(
        f"Wrote heartbeat artifacts for {status['heartbeat_run_id']} "
        f"with run_status={status['run_status']}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
