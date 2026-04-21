from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "automation" / "run_heartbeat.py"
VALIDATOR_PATH = ROOT / "automation" / "validate_heartbeat_contracts.py"

GENERATED_AT_UTC = "2026-04-21T00:00:00Z"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_config(path: Path, *, enabled_sources: list[str]) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "contract_id": "lotus-platform:heartbeat-runner-config:v1",
                "owner": "lotus-platform",
                "source_rfc": "RFC-0095",
                "repository": "lotus-platform",
                "mode": "advisory",
                "mutation_policy": "read_only",
                "output_directory": "output/heartbeat",
                "enabled_sources": enabled_sources,
                "thresholds": {
                    "stale_pr_check_hours": 24,
                    "stale_pr_review_hours": 48,
                },
            }
        ),
        encoding="utf-8",
    )


def test_heartbeat_runner_writes_valid_empty_state_artifacts(tmp_path: Path) -> None:
    runner = _load_module(RUNNER_PATH, "run_heartbeat")
    validator = _load_module(VALIDATOR_PATH, "validate_heartbeat_contracts")
    config_path = tmp_path / "heartbeat-config.json"
    output_dir = tmp_path / "heartbeat"
    _write_config(config_path, enabled_sources=[])

    status = runner.run_heartbeat(
        config_path=config_path,
        output_dir=output_dir,
        generated_at_utc=GENERATED_AT_UTC,
        branch="feature/rfc0095-heartbeat-monitoring",
    )

    assert status["run_status"] == "healthy"
    assert status["configured_sources"] == []
    assert status["attention_items"] == []
    assert validator.validate_heartbeat_status(status) == []
    assert json.loads((output_dir / "heartbeat-status.json").read_text(encoding="utf-8")) == status
    markdown = (output_dir / "heartbeat-status.md").read_text(encoding="utf-8")
    assert "No source adapters were enabled for this heartbeat run." in markdown
    assert "Source truth: `external`" in markdown
    assert "feature/rfc0095-heartbeat-monitoring" in markdown
    assert json.loads((output_dir / "heartbeat-issues.json").read_text(encoding="utf-8")) == []


def test_heartbeat_runner_records_rfc0094_compatible_task_metadata(tmp_path: Path) -> None:
    runner = _load_module(RUNNER_PATH, "run_heartbeat")
    config_path = tmp_path / "heartbeat-config.json"
    output_dir = tmp_path / "heartbeat"
    _write_config(config_path, enabled_sources=[])

    status = runner.run_heartbeat(
        config_path=config_path,
        output_dir=output_dir,
        generated_at_utc=GENERATED_AT_UTC,
        branch="main",
    )
    task_ledger = status["task_ledger"]

    assert task_ledger["engineering_task_id"] == "eng-task-heartbeat-20260421T000000Z"
    assert task_ledger["task_kind"] == "VALIDATION_RUN"
    assert task_ledger["repository"] == "lotus-platform"
    assert task_ledger["branch"] == "main"
    assert task_ledger["status"] == "SUCCEEDED"
    assert task_ledger["cleanup_state"] == "NOT_REQUIRED"
    assert task_ledger["runtime"]["runner"] == "automation/run_heartbeat.py"
    assert task_ledger["scope"]["enabled_sources"] == []
    assert task_ledger["scope"]["output_directory"] == str(output_dir)
    assert all("path" in ref for ref in task_ledger["evidence_refs"])
    assert {ref["type"] for ref in task_ledger["evidence_refs"]} == {
        "LOCAL_JSON_ARTIFACT",
        "LOCAL_MARKDOWN_ARTIFACT",
    }


def test_heartbeat_runner_reports_configured_but_unimplemented_source_as_degraded(
    tmp_path: Path,
) -> None:
    runner = _load_module(RUNNER_PATH, "run_heartbeat")
    validator = _load_module(VALIDATOR_PATH, "validate_heartbeat_contracts")
    config_path = tmp_path / "heartbeat-config.json"
    output_dir = tmp_path / "heartbeat"
    _write_config(config_path, enabled_sources=["github"])

    status = runner.run_heartbeat(
        config_path=config_path,
        output_dir=output_dir,
        generated_at_utc=GENERATED_AT_UTC,
        branch="feature/rfc0095-heartbeat-monitoring",
    )

    assert status["run_status"] == "attention_required"
    assert status["source_inventory"][0]["source_system"] == "github"
    assert status["source_inventory"][0]["read_status"] == "degraded"
    assert status["attention_items"][0]["condition"] == "source_adapter_not_implemented"
    assert status["source_read_errors"][0]["error_summary"] == (
        "Heartbeat source is configured but no read adapter is implemented yet."
    )
    assert validator.validate_heartbeat_status(status) == []
    assert "github:configured_source:github:source_adapter_not_implemented" in (
        output_dir / "heartbeat-status.md"
    ).read_text(encoding="utf-8")


def test_heartbeat_runner_rejects_unknown_source_system(tmp_path: Path) -> None:
    runner = _load_module(RUNNER_PATH, "run_heartbeat")
    config_path = tmp_path / "heartbeat-config.json"
    _write_config(config_path, enabled_sources=["not_a_source"])

    try:
        runner.run_heartbeat(
            config_path=config_path,
            output_dir=tmp_path / "heartbeat",
            generated_at_utc=GENERATED_AT_UTC,
            branch="main",
        )
    except ValueError as exc:
        assert "enabled_sources contains unknown source systems: not_a_source" in str(exc)
    else:
        raise AssertionError("expected unknown source systems to be rejected")


def test_heartbeat_runner_rejects_non_utc_generation_timestamp(tmp_path: Path) -> None:
    runner = _load_module(RUNNER_PATH, "run_heartbeat")
    config_path = tmp_path / "heartbeat-config.json"
    _write_config(config_path, enabled_sources=[])

    try:
        runner.run_heartbeat(
            config_path=config_path,
            output_dir=tmp_path / "heartbeat",
            generated_at_utc="2026-04-21T00:00:00+08:00",
            branch="main",
        )
    except ValueError as exc:
        assert "generated_at_utc must be an RFC-3339 UTC string ending with Z" in str(exc)
    else:
        raise AssertionError("expected non-UTC generated_at_utc to be rejected")
