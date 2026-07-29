from __future__ import annotations

import json
from datetime import UTC, datetime

from automation import detect_stalled_workflow_runs as detector


def _payload(
    *,
    run_id: int,
    name: str,
    status: str,
    created_at: str,
    updated_at: str | None = None,
    conclusion: str = "",
) -> dict[str, object]:
    return {
        "databaseId": run_id,
        "name": name,
        "status": status,
        "conclusion": conclusion,
        "headSha": "f8a22619ef5161176b8f84a460df287044069830",
        "headBranch": "main",
        "event": "schedule",
        "url": f"https://github.com/sgajbi/lotus-platform/actions/runs/{run_id}",
        "createdAt": created_at,
        "updatedAt": updated_at or created_at,
    }


def test_classifies_stale_queued_workflow_run() -> None:
    now = datetime(2026, 7, 30, 0, 0, tzinfo=UTC)
    run = detector.workflow_run_from_payload(
        "sgajbi/lotus-platform",
        _payload(
            run_id=30420991452,
            name="Platform End-to-End Validation",
            status="queued",
            created_at="2026-07-29T03:58:29Z",
        ),
    )

    rows = detector.classify_runs([run], now=now, stale_minutes=60, workflow_names=[])

    assert rows == [
        {
            "repository": "sgajbi/lotus-platform",
            "workflow_name": "Platform End-to-End Validation",
            "run_id": 30420991452,
            "event": "schedule",
            "branch": "main",
            "head_sha": "f8a22619ef5161176b8f84a460df287044069830",
            "status": "queued",
            "conclusion": "",
            "created_at": "2026-07-29T03:58:29Z",
            "updated_at": "2026-07-29T03:58:29Z",
            "age_minutes": 1201.52,
            "updated_age_minutes": 1201.52,
            "stale": True,
            "url": "https://github.com/sgajbi/lotus-platform/actions/runs/30420991452",
        }
    ]


def test_ignores_completed_workflow_runs() -> None:
    now = datetime(2026, 7, 30, 0, 0, tzinfo=UTC)
    run = detector.workflow_run_from_payload(
        "sgajbi/lotus-platform",
        _payload(
            run_id=30462522963,
            name="Main Releasability Gate",
            status="completed",
            conclusion="success",
            created_at="2026-07-29T14:46:16Z",
        ),
    )

    assert detector.classify_runs([run], now=now, stale_minutes=60, workflow_names=[]) == []


def test_marks_recent_active_run_as_not_stale() -> None:
    now = datetime(2026, 7, 30, 0, 0, tzinfo=UTC)
    run = detector.workflow_run_from_payload(
        "sgajbi/lotus-platform",
        _payload(
            run_id=30470702855,
            name="Main Releasability Gate",
            status="in_progress",
            created_at="2026-07-29T23:45:00Z",
            updated_at="2026-07-29T23:55:00Z",
        ),
    )

    rows = detector.classify_runs([run], now=now, stale_minutes=60, workflow_names=[])

    assert rows[0]["stale"] is False
    assert rows[0]["age_minutes"] == 15.0
    assert rows[0]["updated_age_minutes"] == 5.0


def test_workflow_name_filter_limits_output() -> None:
    now = datetime(2026, 7, 30, 0, 0, tzinfo=UTC)
    platform_e2e = detector.workflow_run_from_payload(
        "sgajbi/lotus-platform",
        _payload(
            run_id=1,
            name="Platform End-to-End Validation",
            status="queued",
            created_at="2026-07-29T22:00:00Z",
        ),
    )
    main_releasability = detector.workflow_run_from_payload(
        "sgajbi/lotus-platform",
        _payload(
            run_id=2,
            name="Main Releasability Gate",
            status="queued",
            created_at="2026-07-29T22:00:00Z",
        ),
    )

    rows = detector.classify_runs(
        [platform_e2e, main_releasability],
        now=now,
        stale_minutes=60,
        workflow_names=["Platform End-to-End Validation"],
    )

    assert [row["run_id"] for row in rows] == [1]


def test_writes_json_and_markdown_outputs(tmp_path) -> None:
    generated_at = datetime(2026, 7, 30, 0, 0, tzinfo=UTC)
    rows = [
        {
            "repository": "sgajbi/lotus-platform",
            "workflow_name": "Platform End-to-End Validation",
            "run_id": 30420991452,
            "event": "schedule",
            "branch": "main",
            "head_sha": "f8a22619ef5161176b8f84a460df287044069830",
            "status": "queued",
            "conclusion": "",
            "created_at": "2026-07-29T03:58:29Z",
            "updated_at": "2026-07-29T03:58:29Z",
            "age_minutes": 1201.52,
            "updated_age_minutes": 1201.52,
            "stale": True,
            "url": "https://github.com/sgajbi/lotus-platform/actions/runs/30420991452",
        }
    ]
    output_json = tmp_path / "stalled-workflow-runs.json"
    output_md = tmp_path / "stalled-workflow-runs.md"

    detector.write_outputs(
        rows,
        output_json_path=output_json,
        output_markdown_path=output_md,
        generated_at=generated_at,
        stale_minutes=60,
    )

    assert json.loads(output_json.read_text(encoding="utf-8")) == rows
    markdown = output_md.read_text(encoding="utf-8")
    assert "# Stalled GitHub Workflow Runs" in markdown
    assert "Platform End-to-End Validation" in markdown
    assert "30420991452" in markdown
