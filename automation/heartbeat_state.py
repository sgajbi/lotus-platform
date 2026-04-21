from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE_PATH = ROOT / "output" / "heartbeat" / "heartbeat-state.json"


def _resolve_repo_path(path_value: str | Path | None, default: Path) -> Path:
    if path_value is None:
        return default
    path = Path(path_value)
    if path.is_absolute():
        return path
    return ROOT / path


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_time(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _state_path(config: dict[str, Any]) -> Path:
    return _resolve_repo_path(config.get("state_path"), DEFAULT_STATE_PATH)


def _suppression_path(config: dict[str, Any]) -> Path | None:
    value = config.get("suppression_file_path")
    if not isinstance(value, str) or not value.strip():
        return None
    return _resolve_repo_path(value, DEFAULT_STATE_PATH)


def _load_previous_items(state_path: Path) -> dict[str, dict[str, Any]]:
    if not state_path.exists():
        return {}
    try:
        state = _read_json(state_path)
    except json.JSONDecodeError:
        return {}
    items = state.get("attention_items", [])
    if not isinstance(items, list):
        return {}
    previous: dict[str, dict[str, Any]] = {}
    for item in items:
        if isinstance(item, dict) and isinstance(item.get("deduplication_key"), str):
            previous[item["deduplication_key"]] = item
    return previous


def _load_suppressions(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []
    try:
        payload = _read_json(path)
    except json.JSONDecodeError:
        return []
    suppressions = payload.get("suppressions", [])
    if not isinstance(suppressions, list):
        return []
    return [item for item in suppressions if isinstance(item, dict)]


def _active_suppression(
    item: dict[str, Any],
    suppressions: list[dict[str, Any]],
    generated_at_utc: str,
) -> dict[str, Any] | None:
    generated_at = _parse_time(generated_at_utc)
    if generated_at is None:
        return None
    for suppression in suppressions:
        if suppression.get("deduplication_key") != item.get("deduplication_key"):
            continue
        expires_at = _parse_time(suppression.get("expires_at_utc"))
        if expires_at is None or expires_at <= generated_at:
            continue
        return {
            "deduplication_key": suppression["deduplication_key"],
            "owner": str(suppression.get("owner") or "unassigned"),
            "reason": str(suppression.get("reason") or "No suppression reason recorded."),
            "expires_at_utc": suppression["expires_at_utc"],
        }
    return None


def apply_attention_state(status: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    generated_at_utc = str(status["generated_at_utc"])
    previous_items = _load_previous_items(_state_path(config))
    suppressions = _load_suppressions(_suppression_path(config))
    suppression_decisions: list[dict[str, Any]] = []

    for item in status.get("attention_items", []):
        if not isinstance(item, dict):
            continue
        previous = previous_items.get(str(item.get("deduplication_key")))
        if previous and previous.get("first_seen_at_utc"):
            item["first_seen_at_utc"] = previous["first_seen_at_utc"]
        item["last_seen_at_utc"] = generated_at_utc

        suppression = _active_suppression(item, suppressions, generated_at_utc)
        if suppression is not None and item.get("severity") != "blocking":
            item["suppression"] = {
                "owner": suppression["owner"],
                "reason": suppression["reason"],
                "expires_at_utc": suppression["expires_at_utc"],
            }
            suppression_decisions.append(suppression)

    status["suppression_decisions"] = suppression_decisions
    return status


def write_attention_state(status: dict[str, Any], config: dict[str, Any]) -> None:
    path = _state_path(config)
    path.parent.mkdir(parents=True, exist_ok=True)
    state = {
        "contract_id": "lotus-platform:heartbeat-attention-state:v1",
        "generated_at_utc": status["generated_at_utc"],
        "heartbeat_run_id": status["heartbeat_run_id"],
        "attention_items": [
            {
                "deduplication_key": item["deduplication_key"],
                "first_seen_at_utc": item["first_seen_at_utc"],
                "last_seen_at_utc": item["last_seen_at_utc"],
                "severity": item["severity"],
                "source_ref": item["source_ref"],
                "condition": item["condition"],
            }
            for item in status.get("attention_items", [])
            if isinstance(item, dict)
        ],
    }
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
