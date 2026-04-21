from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "automation" / "run_heartbeat.py"
VALIDATOR_PATH = ROOT / "automation" / "validate_heartbeat_contracts.py"
DEFAULT_CONFIG_PATH = ROOT / "automation" / "heartbeat-config.json"

GENERATED_AT_UTC = "2026-04-21T00:00:00Z"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_config(
    path: Path,
    *,
    enabled_sources: list[str],
    source_config: dict | None = None,
    thresholds: dict | None = None,
    state_path: Path | None = None,
    suppression_file_path: Path | None = None,
) -> None:
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
                "state_path": str(state_path) if state_path is not None else str(path.parent / "heartbeat-state.json"),
                "suppression_file_path": (
                    str(suppression_file_path)
                    if suppression_file_path is not None
                    else str(path.parent / "heartbeat-suppressions.json")
                ),
                "enabled_sources": enabled_sources,
                "source_config": source_config or {},
                "thresholds": thresholds or {
                    "stale_pr_check_hours": 24,
                    "stale_pr_review_hours": 48,
                    "stale_background_run_hours": 6,
                    "stale_mesh_evidence_hours": 24,
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


def test_default_heartbeat_config_enables_only_local_artifact_sources() -> None:
    config = json.loads(DEFAULT_CONFIG_PATH.read_text(encoding="utf-8"))

    assert config["mutation_policy"] == "read_only"
    assert config["mode"] == "advisory"
    assert config["state_path"] == "output/heartbeat/heartbeat-state.json"
    assert (
        config["suppression_file_path"]
        == "platform-contracts/heartbeat/heartbeat-suppressions.json"
    )
    assert config["enabled_sources"] == [
        "background_run_ledger",
        "mesh_certification",
        "agent_context",
    ]
    assert "github" not in config["enabled_sources"]
    assert "wiki_publication" not in config["enabled_sources"]


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


def test_heartbeat_runner_reports_missing_configured_source_artifact_as_attention_required(
    tmp_path: Path,
) -> None:
    runner = _load_module(RUNNER_PATH, "run_heartbeat")
    validator = _load_module(VALIDATOR_PATH, "validate_heartbeat_contracts")
    config_path = tmp_path / "heartbeat-config.json"
    output_dir = tmp_path / "heartbeat"
    _write_config(
        config_path,
        enabled_sources=["github"],
        source_config={"github": {"pr_monitor_path": str(tmp_path / "missing-pr-monitor.json")}},
    )

    status = runner.run_heartbeat(
        config_path=config_path,
        output_dir=output_dir,
        generated_at_utc=GENERATED_AT_UTC,
        branch="feature/rfc0095-heartbeat-monitoring",
    )

    assert status["run_status"] == "attention_required"
    assert status["source_inventory"][0]["source_system"] == "github"
    assert status["source_inventory"][0]["read_status"] == "missing"
    assert status["attention_items"][0]["condition"] == "source_evidence_missing"
    assert status["source_read_errors"][0]["error_summary"] == (
        "Expected heartbeat source evidence artifact is missing."
    )
    assert validator.validate_heartbeat_status(status) == []
    assert "Generate " in (output_dir / "heartbeat-status.md").read_text(encoding="utf-8")


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


def test_heartbeat_runner_rejects_malformed_utc_generation_timestamp(tmp_path: Path) -> None:
    runner = _load_module(RUNNER_PATH, "run_heartbeat")
    config_path = tmp_path / "heartbeat-config.json"
    _write_config(config_path, enabled_sources=[])

    try:
        runner.run_heartbeat(
            config_path=config_path,
            output_dir=tmp_path / "heartbeat",
            generated_at_utc="not-a-dateZ",
            branch="main",
        )
    except ValueError as exc:
        assert "generated_at_utc must be an RFC-3339 UTC string ending with Z" in str(exc)
    else:
        raise AssertionError("expected malformed generated_at_utc to be rejected")


def test_github_adapter_reports_failing_checks_and_stale_prs(tmp_path: Path) -> None:
    runner = _load_module(RUNNER_PATH, "run_heartbeat")
    pr_monitor = tmp_path / "pr-monitor.json"
    pr_monitor.write_text(
        json.dumps(
            [
                {
                    "repo": "sgajbi/lotus-platform",
                    "pulls": [
                        {
                            "number": 95,
                            "url": "https://github.com/sgajbi/lotus-platform/pull/95",
                            "updatedAt": "2026-04-18T00:00:00Z",
                            "hasFailingChecks": True,
                            "checks": [{"name": "feature", "state": "FAILURE"}],
                        }
                    ],
                    "query_error": None,
                }
            ]
        ),
        encoding="utf-8",
    )
    config_path = tmp_path / "heartbeat-config.json"
    _write_config(
        config_path,
        enabled_sources=["github"],
        source_config={"github": {"pr_monitor_path": str(pr_monitor)}},
        thresholds={"stale_pr_review_hours": 24},
    )

    status = runner.run_heartbeat(
        config_path=config_path,
        output_dir=tmp_path / "heartbeat",
        generated_at_utc=GENERATED_AT_UTC,
        branch="main",
    )

    assert {item["condition"] for item in status["attention_items"]} == {
        "github_pr_check_failed",
        "github_pr_stale",
    }
    assert all(item["pr_number"] == 95 for item in status["attention_items"])


def test_background_run_ledger_adapter_reports_lost_and_stale_runs(tmp_path: Path) -> None:
    runner = _load_module(RUNNER_PATH, "run_heartbeat")
    ledger = tmp_path / "background-runs.json"
    ledger.write_text(
        json.dumps(
            [
                {
                    "engineering_task_id": "eng-task-lost",
                    "status": "LOST",
                    "repository": "lotus-platform",
                    "owner": "lotus-platform",
                },
                {
                    "engineering_task_id": "eng-task-running",
                    "status": "RUNNING",
                    "started_at": "2026-04-20T00:00:00Z",
                    "repository": "lotus-platform",
                    "owner": "lotus-platform",
                },
            ]
        ),
        encoding="utf-8",
    )
    config_path = tmp_path / "heartbeat-config.json"
    _write_config(
        config_path,
        enabled_sources=["background_run_ledger"],
        source_config={"background_run_ledger": {"ledger_path": str(ledger)}},
        thresholds={"stale_background_run_hours": 6},
    )

    status = runner.run_heartbeat(
        config_path=config_path,
        output_dir=tmp_path / "heartbeat",
        generated_at_utc=GENERATED_AT_UTC,
        branch="main",
    )

    assert status["run_status"] == "blocked"
    assert {item["condition"] for item in status["attention_items"]} == {
        "background_run_failed",
        "background_run_stale",
    }
    assert any(item["severity"] == "blocking" for item in status["attention_items"])


def test_wiki_publication_adapter_reports_publication_drift(tmp_path: Path) -> None:
    runner = _load_module(RUNNER_PATH, "run_heartbeat")
    wiki_status = tmp_path / "wiki-sync-status.json"
    wiki_status.write_text(
        json.dumps([{"Repository": "lotus-platform", "DiffCount": 2}]),
        encoding="utf-8",
    )
    config_path = tmp_path / "heartbeat-config.json"
    _write_config(
        config_path,
        enabled_sources=["wiki_publication"],
        source_config={"wiki_publication": {"wiki_sync_status_path": str(wiki_status)}},
    )

    status = runner.run_heartbeat(
        config_path=config_path,
        output_dir=tmp_path / "heartbeat",
        generated_at_utc=GENERATED_AT_UTC,
        branch="main",
    )

    assert status["attention_items"][0]["condition"] == "wiki_publication_drift"
    assert status["attention_items"][0]["severity"] == "action_required"


def test_agent_context_adapter_reports_context_validation_errors(tmp_path: Path) -> None:
    runner = _load_module(RUNNER_PATH, "run_heartbeat")
    context_status = tmp_path / "engineering-context-system-validation.json"
    context_status.write_text(
        json.dumps({"status": "failed", "errors": ["missing context link"]}),
        encoding="utf-8",
    )
    config_path = tmp_path / "heartbeat-config.json"
    _write_config(
        config_path,
        enabled_sources=["agent_context"],
        source_config={"agent_context": {"validation_status_path": str(context_status)}},
    )

    status = runner.run_heartbeat(
        config_path=config_path,
        output_dir=tmp_path / "heartbeat",
        generated_at_utc=GENERATED_AT_UTC,
        branch="main",
    )

    assert status["source_inventory"][0]["read_status"] == "degraded"
    assert status["attention_items"][0]["condition"] == "agent_context_validation_failed"


def test_mesh_certification_adapter_reports_stale_blocked_operating_report(
    tmp_path: Path,
) -> None:
    runner = _load_module(RUNNER_PATH, "run_heartbeat")
    operating_report = tmp_path / "enterprise-mesh-operating-report.json"
    operating_report.write_text(
        json.dumps(
            {
                "generated_at_utc": "2026-04-19T00:00:00Z",
                "operating_state": "blocked",
                "escalation_queue": [{"owner": "lotus-platform"}],
            }
        ),
        encoding="utf-8",
    )
    config_path = tmp_path / "heartbeat-config.json"
    _write_config(
        config_path,
        enabled_sources=["mesh_certification"],
        source_config={
            "mesh_certification": {"operating_report_path": str(operating_report)}
        },
        thresholds={"stale_mesh_evidence_hours": 24},
    )

    status = runner.run_heartbeat(
        config_path=config_path,
        output_dir=tmp_path / "heartbeat",
        generated_at_utc=GENERATED_AT_UTC,
        branch="main",
    )

    assert status["run_status"] == "blocked"
    assert {item["condition"] for item in status["attention_items"]} == {
        "mesh_certification_stale",
        "mesh_certification_attention",
    }
    assert any(item["severity"] == "blocking" for item in status["attention_items"])


def test_lotus_ai_adapter_reports_review_backlog_without_collapsing_run_states(
    tmp_path: Path,
) -> None:
    runner = _load_module(RUNNER_PATH, "run_heartbeat")
    runtime_status = tmp_path / "workflow-pack-runtime-status.json"
    runtime_status.write_text(
        json.dumps(
            {
                "workflow_pack_runtime": {
                    "run_summary": {
                        "run_count": 2,
                        "awaiting_review_count": 1,
                        "failed_count": 1,
                        "expired_count": 0,
                        "action_required_count": 2,
                        "status_summary": [
                            "Run-ledger-backed activity posture is available."
                        ],
                    },
                    "attention_queue": {
                        "queue_depth": 2,
                        "queue_limit": 5,
                        "items": [
                            {
                                "run_id": "run-awaiting",
                                "registration_ref": "advisor_brief.pack@v1",
                                "pack_id": "advisor_brief.pack",
                                "workflow_authority_owner": "lotus-advise",
                                "review_state": "AWAITING_REVIEW",
                                "runtime_state": "COMPLETED",
                                "supportability_status": "ACTION_REQUIRED",
                                "created_at": "2026-04-19T00:00:00Z",
                            },
                            {
                                "run_id": "run-failed",
                                "registration_ref": "advisor_brief.pack@v1",
                                "pack_id": "advisor_brief.pack",
                                "workflow_authority_owner": "lotus-advise",
                                "review_state": "AWAITING_REVIEW",
                                "runtime_state": "FAILED",
                                "supportability_status": "ACTION_REQUIRED",
                                "created_at": "2026-04-21T00:00:00Z",
                            },
                        ],
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    config_path = tmp_path / "heartbeat-config.json"
    _write_config(
        config_path,
        enabled_sources=["lotus_ai"],
        source_config={"lotus_ai": {"runtime_status_path": str(runtime_status)}},
        thresholds={"stale_workflow_pack_review_hours": 24},
    )

    status = runner.run_heartbeat(
        config_path=config_path,
        output_dir=tmp_path / "heartbeat",
        generated_at_utc=GENERATED_AT_UTC,
        branch="main",
    )

    conditions = {item["condition"] for item in status["attention_items"]}
    assert "workflow_pack_attention_queue_backlog" in conditions
    assert "workflow_pack_action_required_runs" in conditions
    assert "workflow_pack_failed_runs" in conditions
    assert "workflow_pack_run_action_required" in conditions
    assert "workflow_pack_review_stale" in conditions
    assert "workflow_pack_run_terminal_failure" in conditions
    run_items = [
        item
        for item in status["attention_items"]
        if item["source_ref"] == "workflow_pack_run:run-awaiting"
    ]
    assert all(item["run_id"] == "run-awaiting" for item in run_items)
    assert all(item["workflow_pack_id"] == "advisor_brief.pack" for item in run_items)
    assert any(ref["type"] == "WORKFLOW_PACK_RUN" for ref in run_items[0]["evidence_refs"])


def test_lotus_ai_adapter_flags_superseded_runs_that_are_not_historical(
    tmp_path: Path,
) -> None:
    runner = _load_module(RUNNER_PATH, "run_heartbeat")
    runtime_status = tmp_path / "workflow-pack-runtime-status.json"
    runtime_status.write_text(
        json.dumps(
            {
                "workflow_pack_runtime": {
                    "run_summary": {
                        "run_count": 1,
                        "awaiting_review_count": 0,
                        "failed_count": 0,
                        "expired_count": 0,
                        "action_required_count": 1,
                    },
                    "attention_queue": {
                        "queue_depth": 1,
                        "queue_limit": 5,
                        "items": [
                            {
                                "run_id": "run-superseded",
                                "registration_ref": "advisor_brief.pack@v1",
                                "pack_id": "advisor_brief.pack",
                                "workflow_authority_owner": "lotus-ai",
                                "review_state": "SUPERSEDED",
                                "runtime_state": "SUPERSEDED",
                                "supportability_status": "READY",
                                "created_at": GENERATED_AT_UTC,
                            }
                        ],
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    config_path = tmp_path / "heartbeat-config.json"
    _write_config(
        config_path,
        enabled_sources=["lotus_ai"],
        source_config={"lotus_ai": {"runtime_status_path": str(runtime_status)}},
    )

    status = runner.run_heartbeat(
        config_path=config_path,
        output_dir=tmp_path / "heartbeat",
        generated_at_utc=GENERATED_AT_UTC,
        branch="main",
    )

    assert "workflow_pack_lineage_conflict" in {
        item["condition"] for item in status["attention_items"]
    }


def test_lotus_ai_adapter_reports_runtime_readiness_degradation(tmp_path: Path) -> None:
    runner = _load_module(RUNNER_PATH, "run_heartbeat")
    runtime_status = tmp_path / "workflow-pack-runtime-status.json"
    runtime_status.write_text(
        json.dumps(
            {
                "workflow_pack_runtime": {
                    "run_summary": {
                        "run_count": 0,
                        "awaiting_review_count": 0,
                        "failed_count": 0,
                        "expired_count": 0,
                        "action_required_count": 0,
                        "status_summary": [
                            "Workflow-pack run posture summary is unavailable until the configured run ledger store is ready.",
                            "Current workflow-pack run store status is `DEGRADED`.",
                        ],
                    },
                    "attention_queue": {
                        "queue_depth": 0,
                        "queue_limit": 5,
                        "items": [],
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    config_path = tmp_path / "heartbeat-config.json"
    _write_config(
        config_path,
        enabled_sources=["lotus_ai"],
        source_config={"lotus_ai": {"runtime_status_path": str(runtime_status)}},
    )

    status = runner.run_heartbeat(
        config_path=config_path,
        output_dir=tmp_path / "heartbeat",
        generated_at_utc=GENERATED_AT_UTC,
        branch="main",
    )

    assert status["source_inventory"][0]["read_status"] == "degraded"
    assert status["attention_items"][0]["condition"] == "workflow_pack_runtime_degraded"


def test_heartbeat_state_preserves_first_seen_across_repeated_runs(tmp_path: Path) -> None:
    runner = _load_module(RUNNER_PATH, "run_heartbeat")
    config_path = tmp_path / "heartbeat-config.json"
    state_path = tmp_path / "heartbeat-state.json"
    _write_config(
        config_path,
        enabled_sources=["github"],
        source_config={"github": {"pr_monitor_path": str(tmp_path / "missing.json")}},
        state_path=state_path,
    )

    first = runner.run_heartbeat(
        config_path=config_path,
        output_dir=tmp_path / "heartbeat",
        generated_at_utc="2026-04-20T00:00:00Z",
        branch="main",
    )
    second = runner.run_heartbeat(
        config_path=config_path,
        output_dir=tmp_path / "heartbeat",
        generated_at_utc=GENERATED_AT_UTC,
        branch="main",
    )

    assert first["attention_items"][0]["first_seen_at_utc"] == "2026-04-20T00:00:00Z"
    assert second["attention_items"][0]["first_seen_at_utc"] == "2026-04-20T00:00:00Z"
    assert second["attention_items"][0]["last_seen_at_utc"] == GENERATED_AT_UTC
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["attention_items"][0]["first_seen_at_utc"] == "2026-04-20T00:00:00Z"


def test_heartbeat_suppression_is_explicit_and_does_not_remove_attention_item(
    tmp_path: Path,
) -> None:
    runner = _load_module(RUNNER_PATH, "run_heartbeat")
    config_path = tmp_path / "heartbeat-config.json"
    suppression_path = tmp_path / "heartbeat-suppressions.json"
    missing_pr_monitor = tmp_path / "missing-pr-monitor.json"
    deduplication_key = f"github:{missing_pr_monitor}:source_evidence_missing"
    suppression_path.write_text(
        json.dumps(
            {
                "suppressions": [
                    {
                        "deduplication_key": deduplication_key,
                        "owner": "lotus-platform",
                        "reason": "Temporary upstream PR monitor outage.",
                        "expires_at_utc": "2026-04-22T00:00:00Z",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    _write_config(
        config_path,
        enabled_sources=["github"],
        source_config={"github": {"pr_monitor_path": str(missing_pr_monitor)}},
        suppression_file_path=suppression_path,
    )

    status = runner.run_heartbeat(
        config_path=config_path,
        output_dir=tmp_path / "heartbeat",
        generated_at_utc=GENERATED_AT_UTC,
        branch="main",
    )

    item = status["attention_items"][0]
    assert item["deduplication_key"] == deduplication_key
    assert item["suppression"]["reason"] == "Temporary upstream PR monitor outage."
    assert status["suppression_decisions"] == [
        {
            "deduplication_key": deduplication_key,
            "owner": "lotus-platform",
            "reason": "Temporary upstream PR monitor outage.",
            "expires_at_utc": "2026-04-22T00:00:00Z",
        }
    ]
    assert "Suppressed until: `2026-04-22T00:00:00Z`" in (
        tmp_path / "heartbeat" / "heartbeat-status.md"
    ).read_text(encoding="utf-8")


def test_heartbeat_suppression_cannot_hide_blocking_items(tmp_path: Path) -> None:
    runner = _load_module(RUNNER_PATH, "run_heartbeat")
    ledger = tmp_path / "background-runs.json"
    ledger.write_text(
        json.dumps(
            [
                {
                    "engineering_task_id": "eng-task-lost",
                    "status": "LOST",
                    "repository": "lotus-platform",
                    "owner": "lotus-platform",
                }
            ]
        ),
        encoding="utf-8",
    )
    source_ref = f"{ledger}#eng-task-lost"
    deduplication_key = (
        f"background_run_ledger:{source_ref}:background_run_failed"
    )
    suppression_path = tmp_path / "heartbeat-suppressions.json"
    suppression_path.write_text(
        json.dumps(
            {
                "suppressions": [
                    {
                        "deduplication_key": deduplication_key,
                        "owner": "lotus-platform",
                        "reason": "Cannot hide blocking evidence.",
                        "expires_at_utc": "2026-04-22T00:00:00Z",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    config_path = tmp_path / "heartbeat-config.json"
    _write_config(
        config_path,
        enabled_sources=["background_run_ledger"],
        source_config={"background_run_ledger": {"ledger_path": str(ledger)}},
        suppression_file_path=suppression_path,
    )

    status = runner.run_heartbeat(
        config_path=config_path,
        output_dir=tmp_path / "heartbeat",
        generated_at_utc=GENERATED_AT_UTC,
        branch="main",
    )

    assert status["run_status"] == "blocked"
    assert status["attention_items"][0]["severity"] == "blocking"
    assert "suppression" not in status["attention_items"][0]
    assert status["suppression_decisions"] == []
