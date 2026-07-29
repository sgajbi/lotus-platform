from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, Sequence


DEFAULT_REPOSITORY = "sgajbi/lotus-platform"
DEFAULT_OUTPUT_JSON = Path("output/stalled-workflow-runs.json")
DEFAULT_OUTPUT_MARKDOWN = Path("output/stalled-workflow-runs.md")
GITHUB_RUN_FIELDS = (
    "databaseId,name,status,conclusion,headSha,headBranch,event,url,createdAt,updatedAt"
)
ACTIVE_STATUSES = {"queued", "in_progress"}


@dataclass(frozen=True)
class WorkflowRun:
    repository: str
    workflow_name: str
    run_id: int
    event: str
    branch: str
    head_sha: str
    status: str
    conclusion: str
    created_at: datetime
    updated_at: datetime
    url: str


def parse_timestamp(value: str) -> datetime:
    if not value:
        raise ValueError("timestamp is required")
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _run_gh(args: Sequence[str]) -> str:
    completed = subprocess.run(
        ["gh", *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        details = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"gh command failed: gh {' '.join(args)}\n{details}")
    return completed.stdout


def fetch_workflow_runs(
    *,
    repository: str,
    branch: str,
    limit: int,
    workflow_names: Sequence[str],
) -> list[dict[str, Any]]:
    if workflow_names:
        results: list[dict[str, Any]] = []
        for workflow_name in workflow_names:
            output = _run_gh(
                [
                    "run",
                    "list",
                    "--repo",
                    repository,
                    "--workflow",
                    workflow_name,
                    "--branch",
                    branch,
                    "--limit",
                    str(limit),
                    "--json",
                    GITHUB_RUN_FIELDS,
                ]
            )
            results.extend(json.loads(output))
        return results

    output = _run_gh(
        [
            "run",
            "list",
            "--repo",
            repository,
            "--branch",
            branch,
            "--limit",
            str(limit),
            "--json",
            GITHUB_RUN_FIELDS,
        ]
    )
    return json.loads(output)


def workflow_run_from_payload(repository: str, payload: dict[str, Any]) -> WorkflowRun:
    return WorkflowRun(
        repository=repository,
        workflow_name=str(payload.get("name") or ""),
        run_id=int(payload["databaseId"]),
        event=str(payload.get("event") or ""),
        branch=str(payload.get("headBranch") or ""),
        head_sha=str(payload.get("headSha") or ""),
        status=str(payload.get("status") or ""),
        conclusion=str(payload.get("conclusion") or ""),
        created_at=parse_timestamp(str(payload.get("createdAt") or "")),
        updated_at=parse_timestamp(str(payload.get("updatedAt") or payload.get("createdAt") or "")),
        url=str(payload.get("url") or ""),
    )


def classify_runs(
    runs: Iterable[WorkflowRun],
    *,
    now: datetime,
    stale_minutes: int,
    workflow_names: Sequence[str],
) -> list[dict[str, Any]]:
    workflow_filter = {name.casefold() for name in workflow_names}
    rows: list[dict[str, Any]] = []
    for run in runs:
        if workflow_filter and run.workflow_name.casefold() not in workflow_filter:
            continue
        if run.status not in ACTIVE_STATUSES:
            continue

        age_minutes = round((now - run.created_at).total_seconds() / 60, 2)
        update_age_minutes = round((now - run.updated_at).total_seconds() / 60, 2)
        stale = age_minutes >= stale_minutes
        rows.append(
            {
                "repository": run.repository,
                "workflow_name": run.workflow_name,
                "run_id": run.run_id,
                "event": run.event,
                "branch": run.branch,
                "head_sha": run.head_sha,
                "status": run.status,
                "conclusion": run.conclusion,
                "created_at": run.created_at.isoformat().replace("+00:00", "Z"),
                "updated_at": run.updated_at.isoformat().replace("+00:00", "Z"),
                "age_minutes": age_minutes,
                "updated_age_minutes": update_age_minutes,
                "stale": stale,
                "url": run.url,
            }
        )
    return rows


def render_markdown(rows: Sequence[dict[str, Any]], *, generated_at: datetime, stale_minutes: int) -> str:
    lines = [
        "# Stalled GitHub Workflow Runs",
        "",
        f"- Generated: `{generated_at.isoformat().replace('+00:00', 'Z')}`",
        f"- Stale threshold: `{stale_minutes}` minutes",
        "",
        "| Repository | Workflow | Run | Event | Branch | SHA | Status | Age (min) | Stale | URL |",
        "| --- | --- | ---: | --- | --- | --- | --- | ---: | --- | --- |",
    ]
    if not rows:
        lines.append("| - | - | - | - | - | - | - | 0 | false | - |")
    else:
        for row in rows:
            sha = str(row["head_sha"])[:12]
            lines.append(
                "| {repository} | {workflow_name} | {run_id} | {event} | {branch} | {sha} | "
                "{status} | {age_minutes} | {stale} | {url} |".format(
                    repository=row["repository"],
                    workflow_name=row["workflow_name"],
                    run_id=row["run_id"],
                    event=row["event"],
                    branch=row["branch"],
                    sha=sha,
                    status=row["status"],
                    age_minutes=row["age_minutes"],
                    stale=str(row["stale"]).lower(),
                    url=row["url"],
                )
            )
    return "\n".join(lines) + "\n"


def write_outputs(
    rows: Sequence[dict[str, Any]],
    *,
    output_json_path: Path,
    output_markdown_path: Path,
    generated_at: datetime,
    stale_minutes: int,
) -> None:
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_markdown_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    output_markdown_path.write_text(
        render_markdown(rows, generated_at=generated_at, stale_minutes=stale_minutes),
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Detect stale queued or in-progress GitHub Actions workflow runs."
    )
    parser.add_argument("--repo", default=DEFAULT_REPOSITORY)
    parser.add_argument("--branch", default="main")
    parser.add_argument("--workflow", action="append", default=[])
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--stale-minutes", type=int, default=60)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-markdown", type=Path, default=DEFAULT_OUTPUT_MARKDOWN)
    parser.add_argument("--now-utc", help="Testing hook: fixed UTC timestamp.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    now = parse_timestamp(args.now_utc) if args.now_utc else datetime.now(tz=UTC)
    payloads = fetch_workflow_runs(
        repository=args.repo,
        branch=args.branch,
        limit=args.limit,
        workflow_names=args.workflow,
    )
    runs = [workflow_run_from_payload(args.repo, payload) for payload in payloads]
    rows = classify_runs(
        runs,
        now=now,
        stale_minutes=args.stale_minutes,
        workflow_names=args.workflow,
    )
    write_outputs(
        rows,
        output_json_path=args.output_json,
        output_markdown_path=args.output_markdown,
        generated_at=now,
        stale_minutes=args.stale_minutes,
    )
    print(f"Wrote {args.output_json}")
    print(f"Wrote {args.output_markdown}")
    stale_count = sum(1 for row in rows if row["stale"])
    print(f"Stale workflow runs: {stale_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
