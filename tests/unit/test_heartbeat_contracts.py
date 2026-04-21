from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "platform-contracts" / "heartbeat" / "heartbeat-status.schema.json"
EXAMPLES_DIR = ROOT / "platform-contracts" / "heartbeat" / "examples"
VALIDATOR_PATH = ROOT / "automation" / "validate_heartbeat_contracts.py"


def _load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_heartbeat_contracts", VALIDATOR_PATH
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_heartbeat_contract_is_governed_and_source_truth_preserving() -> None:
    contract = _load_json(CONTRACT_PATH)

    assert contract["contract_id"] == "lotus-platform:heartbeat-status:v1"
    assert contract["source_rfc"] == "RFC-0095"
    assert contract["owner"] == "lotus-platform"
    assert contract["artifact_paths"]["json"] == "output/heartbeat/heartbeat-status.json"
    assert contract["artifact_paths"]["markdown"] == "output/heartbeat/heartbeat-status.md"
    assert "source truth" in contract["authority"]["source_truth"].lower()
    assert "read-only" in contract["authority"]["first_wave_mutation_policy"].lower()
    assert "Missing, unreadable, or malformed source evidence is never healthy" in contract[
        "authority"
    ]["missing_evidence_policy"]

    assert set(contract["severities"]) == {
        "info",
        "warning",
        "action_required",
        "blocking",
    }
    assert set(contract["read_statuses"]) == {"healthy", "degraded", "missing", "error"}
    assert "WORKFLOW_PACK_RUN" in contract["evidence_ref_types"]
    assert "delegated_task_ledger" in contract["source_systems"]
    assert "deduplication_key" in contract["required_attention_item_fields"]


def test_heartbeat_contract_validator_accepts_contract_and_examples() -> None:
    validator = _load_validator()

    assert validator.validate_heartbeat_contracts() == []


def test_heartbeat_validator_accepts_default_config_and_suppressions() -> None:
    validator = _load_validator()

    assert validator.validate_heartbeat_runner_config() == []
    assert validator.validate_heartbeat_suppressions() == []


def test_heartbeat_examples_cover_required_first_wave_postures() -> None:
    examples = {
        path.name: _load_json(path)
        for path in EXAMPLES_DIR.glob("*.json")
    }

    assert {
        "healthy-heartbeat-status.json",
        "warning-heartbeat-status.json",
        "action-required-heartbeat-status.json",
        "blocking-heartbeat-status.json",
        "suppressed-heartbeat-status.json",
        "degraded-source-heartbeat-status.json",
    }.issubset(examples)

    severities = {
        item["severity"]
        for example in examples.values()
        for item in example["attention_items"]
    }
    assert {"warning", "action_required", "blocking"}.issubset(severities)
    assert any(example["run_status"] == "healthy" for example in examples.values())
    assert any(example["suppression_decisions"] for example in examples.values())
    assert any(example["source_read_errors"] for example in examples.values())


def test_heartbeat_status_rejects_missing_evidence_as_healthy() -> None:
    validator = _load_validator()
    status = _load_json(EXAMPLES_DIR / "degraded-source-heartbeat-status.json")
    status["attention_items"] = []
    status["summary_counts"]["action_required"] = 0

    errors = validator.validate_heartbeat_status(status)

    assert "missing or errored source evidence must produce an attention item" in errors


def test_heartbeat_status_rejects_suppressed_blocking_items() -> None:
    validator = _load_validator()
    status = _load_json(EXAMPLES_DIR / "blocking-heartbeat-status.json")
    status["attention_items"][0]["suppression"] = {
        "owner": "lotus-platform",
        "reason": "temporary",
        "expires_at_utc": "2026-04-22T00:00:00Z",
    }

    errors = validator.validate_heartbeat_status(status)

    assert any("blocking item cannot be suppressed" in error for error in errors)


def test_heartbeat_status_rejects_summary_count_drift() -> None:
    validator = _load_validator()
    status = _load_json(EXAMPLES_DIR / "warning-heartbeat-status.json")
    status["summary_counts"]["warning"] = 0

    errors = validator.validate_heartbeat_status(status)

    assert "summary_counts.warning must equal attention item count 1" in errors


def test_heartbeat_status_rejects_malformed_utc_timestamps() -> None:
    validator = _load_validator()
    status = _load_json(EXAMPLES_DIR / "warning-heartbeat-status.json")
    status["generated_at_utc"] = "not-a-dateZ"
    status["attention_items"][0]["first_seen_at_utc"] = "also-not-a-dateZ"
    status["attention_items"][0]["last_seen_at_utc"] = "2026-04-21T00:00:00+08:00"

    errors = validator.validate_heartbeat_status(status)

    assert "generated_at_utc must be an RFC-3339 UTC string ending with Z" in errors
    assert (
        "attention_items[0].first_seen_at_utc must be an RFC-3339 UTC string ending with Z"
        in errors
    )
    assert (
        "attention_items[0].last_seen_at_utc must be an RFC-3339 UTC string ending with Z"
        in errors
    )


def test_heartbeat_config_rejects_unknown_enabled_source(tmp_path: Path) -> None:
    validator = _load_validator()
    config = _load_json(ROOT / "automation" / "heartbeat-config.json")
    config["enabled_sources"] = ["not_a_source"]
    path = tmp_path / "heartbeat-config.json"
    path.write_text(json.dumps(config), encoding="utf-8")

    errors = validator.validate_heartbeat_runner_config(path)

    assert (
        "heartbeat config enabled_sources contains unknown source systems: not_a_source"
        in errors
    )


def test_heartbeat_suppressions_reject_invalid_expiry(tmp_path: Path) -> None:
    validator = _load_validator()
    path = tmp_path / "heartbeat-suppressions.json"
    path.write_text(
        json.dumps(
            {
                "contract_id": "lotus-platform:heartbeat-suppressions:v1",
                "source_rfc": "RFC-0095",
                "suppressions": [
                    {
                        "deduplication_key": "github:pr:stale",
                        "owner": "lotus-platform",
                        "reason": "temporary",
                        "expires_at_utc": "2026-04-22T00:00:00+08:00",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    errors = validator.validate_heartbeat_suppressions(path)

    assert (
        "heartbeat suppressions[0].expires_at_utc must be an RFC-3339 UTC string ending with Z"
        in errors
    )


def test_heartbeat_suppressions_reject_malformed_utc_expiry(tmp_path: Path) -> None:
    validator = _load_validator()
    path = tmp_path / "heartbeat-suppressions.json"
    path.write_text(
        json.dumps(
            {
                "contract_id": "lotus-platform:heartbeat-suppressions:v1",
                "source_rfc": "RFC-0095",
                "suppressions": [
                    {
                        "deduplication_key": "github:pr:stale",
                        "owner": "lotus-platform",
                        "reason": "temporary",
                        "expires_at_utc": "not-a-dateZ",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    errors = validator.validate_heartbeat_suppressions(path)

    assert (
        "heartbeat suppressions[0].expires_at_utc must be an RFC-3339 UTC string ending with Z"
        in errors
    )
