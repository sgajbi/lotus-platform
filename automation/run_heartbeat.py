from __future__ import annotations

import argparse
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import sys

AUTOMATION_DIR = Path(__file__).resolve().parent
if str(AUTOMATION_DIR) not in sys.path:
    sys.path.insert(0, str(AUTOMATION_DIR))

from heartbeat_sources import (  # noqa: E402
    display_path,
    load_config,
    read_source,
    run_status,
    severity_counts,
    task_evidence_ref,
)
from heartbeat_state import apply_attention_state, write_attention_state  # noqa: E402


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
        display_path(output_dir / STATUS_FILENAME),
        display_path(output_dir / MARKDOWN_FILENAME),
        display_path(output_dir / ISSUES_FILENAME),
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
            "output_directory": display_path(output_dir),
            "run_status": run_status,
        },
        "artifacts": artifact_refs,
        "evidence_refs": [
            task_evidence_ref("LOCAL_JSON_ARTIFACT", artifact_refs[0]),
            task_evidence_ref("LOCAL_MARKDOWN_ARTIFACT", artifact_refs[1]),
            task_evidence_ref("LOCAL_JSON_ARTIFACT", artifact_refs[2]),
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
        source, items, source_errors = read_source(
            source_system=source_system,
            config=config,
            config_path=config_path,
            repository=repository,
            generated_at_utc=generated_at_utc,
        )
        source_inventory.append(source)
        attention_items.extend(items)
        source_read_errors.extend(source_errors)

    summary_counts = severity_counts(attention_items)
    heartbeat_run_status = run_status(attention_items, source_read_errors)
    heartbeat_run_id = _heartbeat_run_id(generated_at_utc)

    status: dict[str, Any] = {
        "contract_id": HEARTBEAT_STATUS_CONTRACT_ID,
        "contract_version": "1.0",
        "heartbeat_run_id": heartbeat_run_id,
        "generated_at_utc": generated_at_utc,
        "run_status": heartbeat_run_status,
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
        run_status=heartbeat_run_status,
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
                    (
                        f"- Suppressed until: `{item['suppression']['expires_at_utc']}` "
                        f"by `{item['suppression']['owner']}`"
                        if item.get("suppression")
                        else "- Suppressed until: `not suppressed`"
                    ),
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
    apply_attention_state(status, config)
    write_heartbeat_artifacts(status, resolved_output_dir)
    write_attention_state(status, config)
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
