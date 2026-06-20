from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "platform-contracts" / "heartbeat" / "heartbeat-status.schema.json"
DEFAULT_CONFIG_PATH = ROOT / "automation" / "heartbeat-config.json"
RUNNER_CONFIG_CONTRACT_ID = "lotus-platform:heartbeat-runner-config:v1"

IMPLEMENTED_SOURCE_ADAPTERS = {
    "github",
    "background_run_ledger",
    "delegated_task_ledger",
    "wiki_publication",
    "agent_context",
    "mesh_certification",
    "lotus_ai",
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_repo_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return ROOT / path


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


def _age_hours(now_utc: str, timestamp: object) -> float | None:
    now = _parse_time(now_utc)
    then = _parse_time(timestamp)
    if now is None or then is None:
        return None
    return (now - then).total_seconds() / 3600


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


def _attention_item(
    *,
    source_system: str,
    source_ref: str,
    repository: str,
    condition: str,
    severity: str,
    owner: str,
    generated_at_utc: str,
    evidence_refs: list[dict[str, str]],
    recommended_next_action: str,
    pr_number: int | None = None,
) -> dict[str, Any]:
    deduplication_key = f"{source_system}:{source_ref}:{condition}"
    item: dict[str, Any] = {
        "attention_item_id": f"{deduplication_key}:item",
        "condition": condition,
        "source_system": source_system,
        "source_ref": source_ref,
        "repository": repository,
        "severity": severity,
        "owner": owner,
        "first_seen_at_utc": generated_at_utc,
        "last_seen_at_utc": generated_at_utc,
        "evidence_refs": evidence_refs,
        "recommended_next_action": recommended_next_action,
        "deduplication_key": deduplication_key,
    }
    if pr_number is not None:
        item["pr_number"] = pr_number
    return item


def _source_inventory(
    *,
    source_system: str,
    source_ref: str,
    read_status: str,
    owner: str,
    evidence_refs: list[dict[str, str]],
    freshness_at_utc: str | None = None,
) -> dict[str, Any]:
    source = {
        "source_system": source_system,
        "source_ref": source_ref,
        "read_status": read_status,
        "owner": owner,
        "evidence_refs": evidence_refs,
    }
    if freshness_at_utc:
        source["freshness_at_utc"] = freshness_at_utc
    return source


def _source_read_error(
    *,
    source_system: str,
    source_ref: str,
    error_summary: str,
    evidence_refs: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "source_system": source_system,
        "source_ref": source_ref,
        "error_summary": error_summary,
        "evidence_refs": evidence_refs,
    }


def _missing_artifact_result(
    *,
    source_system: str,
    path: Path,
    repository: str,
    generated_at_utc: str,
    recommended_next_action: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    source_ref = _display_path(path)
    evidence_refs = [_evidence_ref("LOCAL_JSON_ARTIFACT", source_ref)]
    item = _attention_item(
        source_system=source_system,
        source_ref=source_ref,
        repository=repository,
        condition="source_evidence_missing",
        severity="action_required",
        owner=repository,
        generated_at_utc=generated_at_utc,
        evidence_refs=evidence_refs,
        recommended_next_action=recommended_next_action,
    )
    return (
        _source_inventory(
            source_system=source_system,
            source_ref=source_ref,
            read_status="missing",
            owner=repository,
            evidence_refs=evidence_refs,
        ),
        [item],
        [
            _source_read_error(
                source_system=source_system,
                source_ref=source_ref,
                error_summary="Expected heartbeat source evidence artifact is missing.",
                evidence_refs=evidence_refs,
            )
        ],
    )


def _load_source_json(
    *,
    source_system: str,
    path: Path,
    repository: str,
    generated_at_utc: str,
) -> tuple[dict[str, Any] | list[Any] | None, dict[str, Any] | None, list[dict[str, Any]], list[dict[str, Any]]]:
    if not path.exists():
        source, items, errors = _missing_artifact_result(
            source_system=source_system,
            path=path,
            repository=repository,
            generated_at_utc=generated_at_utc,
            recommended_next_action=f"Generate {_display_path(path)} before enabling {source_system} heartbeat checks.",
        )
        return None, source, items, errors
    source_ref = _display_path(path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        evidence_refs = [_evidence_ref("LOCAL_JSON_ARTIFACT", source_ref)]
        item = _attention_item(
            source_system=source_system,
            source_ref=source_ref,
            repository=repository,
            condition="source_evidence_malformed",
            severity="action_required",
            owner=repository,
            generated_at_utc=generated_at_utc,
            evidence_refs=evidence_refs,
            recommended_next_action=f"Regenerate {_display_path(path)}; heartbeat could not parse JSON.",
        )
        return (
            None,
            _source_inventory(
                source_system=source_system,
                source_ref=source_ref,
                read_status="error",
                owner=repository,
                evidence_refs=evidence_refs,
            ),
            [item],
            [
                _source_read_error(
                    source_system=source_system,
                    source_ref=source_ref,
                    error_summary=f"Invalid JSON: {exc}",
                    evidence_refs=evidence_refs,
                )
            ],
        )
    return payload, None, [], []


def _not_implemented_source(
    *,
    source_system: str,
    config_path: Path,
    repository: str,
    generated_at_utc: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    source_ref = f"configured_source:{source_system}"
    evidence_refs = [_evidence_ref("LOCAL_JSON_ARTIFACT", str(config_path))]
    source = _source_inventory(
        source_system=source_system,
        source_ref=source_ref,
        read_status="degraded",
        owner=repository,
        freshness_at_utc=generated_at_utc,
        evidence_refs=evidence_refs,
    )
    item = _attention_item(
        source_system=source_system,
        source_ref=source_ref,
        repository=repository,
        condition="source_adapter_not_implemented",
        severity="action_required",
        owner=repository,
        generated_at_utc=generated_at_utc,
        evidence_refs=evidence_refs,
        recommended_next_action=(
            f"Implement the RFC-0095 heartbeat adapter for {source_system} before enabling it routinely."
        ),
    )
    source_error = _source_read_error(
        source_system=source_system,
        source_ref=source_ref,
        error_summary="Heartbeat source is configured but no read adapter is implemented yet.",
        evidence_refs=evidence_refs,
    )
    return source, item, source_error


def _source_path(
    config: dict[str, Any],
    source_system: str,
    key: str,
    default: str,
) -> Path:
    source_config = config.get("source_config")
    if not isinstance(source_config, dict):
        source_config = {}
    settings = source_config.get(source_system)
    if not isinstance(settings, dict):
        settings = {}
    return _resolve_repo_path(str(settings.get(key, default)))


def _threshold(config: dict[str, Any], key: str, default: float) -> float:
    thresholds = config.get("thresholds")
    if not isinstance(thresholds, dict):
        return default
    value = thresholds.get(key, default)
    if isinstance(value, int | float):
        return float(value)
    return default


def _normalize_pulls(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        nested = value.get("value")
        if isinstance(nested, list):
            return [item for item in nested if isinstance(item, dict)]
    return []


def _github_entries(payload: dict[str, Any] | list[Any] | None) -> list[Any]:
    return payload if isinstance(payload, list) else []


def _append_github_query_error_attention(
    *,
    attention_items: list[dict[str, Any]],
    source_errors: list[dict[str, Any]],
    repo: str,
    query_error: object,
    generated_at_utc: str,
    evidence_refs: list[dict[str, str]],
) -> None:
    repo_name = repo.split("/")[-1]
    source_errors.append(
        _source_read_error(
            source_system="github",
            source_ref=repo,
            error_summary=str(query_error),
            evidence_refs=evidence_refs,
        )
    )
    attention_items.append(
        _attention_item(
            source_system="github",
            source_ref=repo,
            repository=repo_name,
            condition="github_pr_query_error",
            severity="action_required",
            owner=repo_name,
            generated_at_utc=generated_at_utc,
            evidence_refs=evidence_refs,
            recommended_next_action=f"Regenerate PR monitor evidence for {repo}.",
        )
    )


def _github_failing_checks(pr: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        check
        for check in _normalize_pulls(pr.get("checks"))
        if str(check.get("state", "")).upper() in {"FAILURE", "ERROR"}
    ]


def _append_github_failing_check_attention(
    *,
    attention_items: list[dict[str, Any]],
    pr: dict[str, Any],
    repo: str,
    repo_name: str,
    pr_ref: str,
    pr_number: object,
    generated_at_utc: str,
    evidence_refs: list[dict[str, str]],
) -> None:
    if not pr.get("hasFailingChecks") and not _github_failing_checks(pr):
        return
    attention_items.append(
        _attention_item(
            source_system="github",
            source_ref=pr_ref,
            repository=repo_name,
            condition="github_pr_check_failed",
            severity="action_required",
            owner=repo_name,
            generated_at_utc=generated_at_utc,
            evidence_refs=evidence_refs,
            recommended_next_action=f"Inspect failing GitHub checks for {repo} PR #{pr_number}.",
            pr_number=pr_number if isinstance(pr_number, int) else None,
        )
    )


def _append_github_stale_pr_attention(
    *,
    attention_items: list[dict[str, Any]],
    pr: dict[str, Any],
    repo: str,
    repo_name: str,
    pr_ref: str,
    pr_number: object,
    generated_at_utc: str,
    evidence_refs: list[dict[str, str]],
    stale_hours: float,
) -> None:
    age = _age_hours(generated_at_utc, pr.get("updatedAt"))
    if age is None or age <= stale_hours:
        return
    attention_items.append(
        _attention_item(
            source_system="github",
            source_ref=pr_ref,
            repository=repo_name,
            condition="github_pr_stale",
            severity="warning",
            owner=repo_name,
            generated_at_utc=generated_at_utc,
            evidence_refs=evidence_refs,
            recommended_next_action=f"Review stale PR #{pr_number} in {repo}.",
            pr_number=pr_number if isinstance(pr_number, int) else None,
        )
    )


def _collect_github_pr_attention(
    *,
    attention_items: list[dict[str, Any]],
    pr: dict[str, Any],
    repo: str,
    generated_at_utc: str,
    evidence_refs: list[dict[str, str]],
    stale_hours: float,
) -> None:
    pr_number = pr.get("number")
    pr_ref = str(pr.get("url") or f"{repo}#{pr_number}")
    repo_name = repo.split("/")[-1]
    _append_github_failing_check_attention(
        attention_items=attention_items,
        pr=pr,
        repo=repo,
        repo_name=repo_name,
        pr_ref=pr_ref,
        pr_number=pr_number,
        generated_at_utc=generated_at_utc,
        evidence_refs=evidence_refs,
    )
    _append_github_stale_pr_attention(
        attention_items=attention_items,
        pr=pr,
        repo=repo,
        repo_name=repo_name,
        pr_ref=pr_ref,
        pr_number=pr_number,
        generated_at_utc=generated_at_utc,
        evidence_refs=evidence_refs,
        stale_hours=stale_hours,
    )


def _github_adapter(
    *,
    config: dict[str, Any],
    repository: str,
    generated_at_utc: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    path = _source_path(config, "github", "pr_monitor_path", "output/pr-monitor.json")
    payload, missing_source, missing_items, missing_errors = _load_source_json(
        source_system="github",
        path=path,
        repository=repository,
        generated_at_utc=generated_at_utc,
    )
    if missing_source is not None:
        return missing_source, missing_items, missing_errors

    evidence_refs = [_evidence_ref("LOCAL_JSON_ARTIFACT", _display_path(path))]
    attention_items: list[dict[str, Any]] = []
    source_errors: list[dict[str, Any]] = []
    stale_hours = _threshold(config, "stale_pr_review_hours", 48)
    for entry in _github_entries(payload):
        if not isinstance(entry, dict):
            continue
        repo = str(entry.get("repo") or repository)
        query_error = entry.get("query_error")
        if query_error:
            _append_github_query_error_attention(
                attention_items=attention_items,
                source_errors=source_errors,
                repo=repo,
                query_error=query_error,
                generated_at_utc=generated_at_utc,
                evidence_refs=evidence_refs,
            )
            continue
        for pr in _normalize_pulls(entry.get("pulls")):
            _collect_github_pr_attention(
                attention_items=attention_items,
                pr=pr,
                repo=repo,
                generated_at_utc=generated_at_utc,
                evidence_refs=evidence_refs,
                stale_hours=stale_hours,
            )

    read_status = "error" if source_errors else "healthy"
    return (
        _source_inventory(
            source_system="github",
            source_ref=_display_path(path),
            read_status=read_status,
            owner=repository,
            evidence_refs=evidence_refs,
        ),
        attention_items,
        source_errors,
    )


def _background_run_records(payload: dict[str, Any] | list[Any] | None) -> list[Any]:
    return payload if isinstance(payload, list) else []


def _background_run_identity(
    *,
    run: dict[str, Any],
    repository: str,
    path: Path,
) -> tuple[str, str, str, str]:
    task_id = str(run.get("engineering_task_id") or run.get("runId") or "unknown")
    source_ref = f"{_display_path(path)}#{task_id}"
    run_repository = str(run.get("repository") or repository)
    owner = str(run.get("owner") or repository)
    return task_id, source_ref, run_repository, owner


def _append_failed_background_run_attention(
    *,
    attention_items: list[dict[str, Any]],
    status: str,
    task_id: str,
    source_ref: str,
    run_repository: str,
    owner: str,
    generated_at_utc: str,
    evidence_refs: list[dict[str, str]],
) -> None:
    if status not in {"FAILED", "TIMED_OUT", "LOST"}:
        return
    attention_items.append(
        _attention_item(
            source_system="background_run_ledger",
            source_ref=source_ref,
            repository=run_repository,
            condition="background_run_failed",
            severity="blocking" if status == "LOST" else "action_required",
            owner=owner,
            generated_at_utc=generated_at_utc,
            evidence_refs=evidence_refs,
            recommended_next_action=f"Inspect background run `{task_id}` with status `{status}`.",
        )
    )


def _append_stale_background_run_attention(
    *,
    attention_items: list[dict[str, Any]],
    run: dict[str, Any],
    status: str,
    task_id: str,
    source_ref: str,
    run_repository: str,
    owner: str,
    generated_at_utc: str,
    evidence_refs: list[dict[str, str]],
    stale_hours: int,
) -> None:
    if status not in {"RUNNING", "QUEUED"}:
        return
    age = _age_hours(generated_at_utc, run.get("started_at") or run.get("startedAt"))
    if age is None or age <= stale_hours:
        return
    attention_items.append(
        _attention_item(
            source_system="background_run_ledger",
            source_ref=source_ref,
            repository=run_repository,
            condition="background_run_stale",
            severity="warning",
            owner=owner,
            generated_at_utc=generated_at_utc,
            evidence_refs=evidence_refs,
            recommended_next_action=f"Refresh or cancel stale background run `{task_id}`.",
        )
    )


def _collect_background_run_attention(
    *,
    attention_items: list[dict[str, Any]],
    run: dict[str, Any],
    repository: str,
    path: Path,
    generated_at_utc: str,
    evidence_refs: list[dict[str, str]],
    stale_hours: int,
) -> None:
    status = str(run.get("status", "")).upper()
    task_id, source_ref, run_repository, owner = _background_run_identity(
        run=run,
        repository=repository,
        path=path,
    )
    _append_failed_background_run_attention(
        attention_items=attention_items,
        status=status,
        task_id=task_id,
        source_ref=source_ref,
        run_repository=run_repository,
        owner=owner,
        generated_at_utc=generated_at_utc,
        evidence_refs=evidence_refs,
    )
    _append_stale_background_run_attention(
        attention_items=attention_items,
        run=run,
        status=status,
        task_id=task_id,
        source_ref=source_ref,
        run_repository=run_repository,
        owner=owner,
        generated_at_utc=generated_at_utc,
        evidence_refs=evidence_refs,
        stale_hours=stale_hours,
    )


def _background_run_ledger_adapter(
    *,
    config: dict[str, Any],
    repository: str,
    generated_at_utc: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    path = _source_path(
        config, "background_run_ledger", "ledger_path", "output/background-runs.json"
    )
    payload, missing_source, missing_items, missing_errors = _load_source_json(
        source_system="background_run_ledger",
        path=path,
        repository=repository,
        generated_at_utc=generated_at_utc,
    )
    if missing_source is not None:
        return missing_source, missing_items, missing_errors

    evidence_refs = [_evidence_ref("LOCAL_JSON_ARTIFACT", _display_path(path))]
    attention_items: list[dict[str, Any]] = []
    stale_hours = _threshold(config, "stale_background_run_hours", 6)
    for run in _background_run_records(payload):
        if not isinstance(run, dict):
            continue
        _collect_background_run_attention(
            attention_items=attention_items,
            run=run,
            repository=repository,
            path=path,
            generated_at_utc=generated_at_utc,
            evidence_refs=evidence_refs,
            stale_hours=stale_hours,
        )

    return (
        _source_inventory(
            source_system="background_run_ledger",
            source_ref=_display_path(path),
            read_status="healthy",
            owner=repository,
            evidence_refs=evidence_refs,
        ),
        attention_items,
        [],
    )


def _write_scopes_overlap(left: object, right: object) -> bool:
    if not isinstance(left, list) or not isinstance(right, list):
        return False
    left_values = [item.rstrip("/") for item in left if isinstance(item, str)]
    right_values = [item.rstrip("/") for item in right if isinstance(item, str)]
    for left_value in left_values:
        for right_value in right_values:
            if (
                left_value == right_value
                or left_value.startswith(f"{right_value}/")
                or right_value.startswith(f"{left_value}/")
            ):
                return True
    return False


def _append_delegated_task_attention(
    attention_items: list[dict[str, Any]],
    *,
    source_ref: str,
    task_repository: str,
    condition: str,
    severity: str,
    owner: str,
    generated_at_utc: str,
    task_evidence: list[dict[str, Any]],
    action: str,
    task_id: str,
    scope: dict[str, Any],
    profile: str,
) -> None:
    item = _attention_item(
        source_system="delegated_task_ledger",
        source_ref=source_ref,
        repository=task_repository,
        condition=condition,
        severity=severity,
        owner=owner,
        generated_at_utc=generated_at_utc,
        evidence_refs=task_evidence,
        recommended_next_action=action,
    )
    item["engineering_task_id"] = task_id
    item["parent_engineering_task_id"] = str(scope.get("parent_engineering_task_id") or "")
    item["delegation_profile"] = profile
    if "write_scope" in scope:
        item["write_scope"] = scope["write_scope"]
    attention_items.append(item)


def _collect_delegated_task_attention(
    *,
    attention_items: list[dict[str, Any]],
    task: dict[str, Any],
    task_id: str,
    task_repository: str,
    source_ref: str,
    owner: str,
    generated_at_utc: str,
    task_evidence: list[dict[str, Any]],
    scope: dict[str, Any],
    profile: str,
    stale_hours: int,
) -> bool:
    status = str(task.get("status") or "").upper()
    is_active = status in {"QUEUED", "RUNNING"}

    def add_attention(condition: str, severity: str, action: str) -> None:
        _append_delegated_task_attention(
            attention_items,
            source_ref=source_ref,
            task_repository=task_repository,
            condition=condition,
            severity=severity,
            owner=owner,
            generated_at_utc=generated_at_utc,
            task_evidence=task_evidence,
            action=action,
            task_id=task_id,
            scope=scope,
            profile=profile,
        )

    if status in {"FAILED", "TIMED_OUT"}:
        add_attention(
            "delegated_task_failed",
            "action_required",
            f"Review delegated task `{task_id}` failure before using its output.",
        )
    elif status == "LOST":
        add_attention(
            "delegated_task_lost",
            "blocking",
            f"Recover, cancel, or rerun lost delegated task `{task_id}`.",
        )

    if is_active:
        age = _age_hours(
            generated_at_utc,
            task.get("started_at") or task.get("requested_at"),
        )
        if age is not None and age > stale_hours:
            add_attention(
                "delegated_task_stale",
                "warning",
                f"Refresh or cancel stale delegated task `{task_id}`.",
            )

    if status == "SUCCEEDED" and not scope.get("return_envelope_received"):
        add_attention(
            "delegated_task_missing_evidence",
            "action_required",
            f"Record return-envelope evidence for delegated task `{task_id}`.",
        )

    if scope.get("main_agent_review_status") in {"REJECTED", "NEEDS_CHANGES"}:
        add_attention(
            "delegated_task_unresolved_blocker",
            "action_required",
            f"Resolve main-agent review blocker for delegated task `{task_id}`.",
        )

    return is_active


def _append_delegated_task_overlap_attention(
    *,
    attention_items: list[dict[str, Any]],
    active_tasks: list[dict[str, Any]],
    repository: str,
    generated_at_utc: str,
    evidence_refs: list[dict[str, Any]],
) -> None:
    for index, left in enumerate(active_tasks):
        left_scope = left.get("scope") if isinstance(left.get("scope"), dict) else {}
        left_write_scope = left_scope.get("write_scope")
        if left_write_scope == "none":
            continue
        for right in active_tasks[index + 1 :]:
            right_scope = right.get("scope") if isinstance(right.get("scope"), dict) else {}
            if not _write_scopes_overlap(left_write_scope, right_scope.get("write_scope")):
                continue
            left_id = str(left.get("engineering_task_id") or "unknown-task")
            right_id = str(right.get("engineering_task_id") or "unknown-task")
            item = _attention_item(
                source_system="delegated_task_ledger",
                source_ref=f"delegated_task_overlap:{left_id}:{right_id}",
                repository=str(left.get("repository") or repository),
                condition="delegated_task_write_scope_overlap",
                severity="action_required",
                owner=str(left.get("owner") or repository),
                generated_at_utc=generated_at_utc,
                evidence_refs=evidence_refs,
                recommended_next_action=(
                    f"Pause or supersede one delegated task before integrating `{left_id}` and `{right_id}`."
                ),
            )
            item["engineering_task_id"] = left_id
            item["related_engineering_task_id"] = right_id
            item["delegation_profile"] = str(left_scope.get("delegation_profile") or "")
            item["write_scope"] = left_write_scope
            attention_items.append(item)


def _delegated_task_ledger_adapter(
    *,
    config: dict[str, Any],
    repository: str,
    generated_at_utc: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    path = _source_path(
        config, "delegated_task_ledger", "ledger_path", "output/delegated-tasks.json"
    )
    payload, missing_source, missing_items, missing_errors = _load_source_json(
        source_system="delegated_task_ledger",
        path=path,
        repository=repository,
        generated_at_utc=generated_at_utc,
    )
    if missing_source is not None:
        return missing_source, missing_items, missing_errors

    evidence_refs = [_evidence_ref("LOCAL_JSON_ARTIFACT", _display_path(path))]
    attention_items: list[dict[str, Any]] = []
    stale_hours = _threshold(config, "stale_delegated_task_hours", 6)
    tasks = payload if isinstance(payload, list) else []
    active_tasks: list[dict[str, Any]] = []

    for task in tasks:
        if not isinstance(task, dict):
            continue
        task_id = str(task.get("engineering_task_id") or "unknown-task")
        source_ref = f"delegated_task:{task_id}"
        task_repository = str(task.get("repository") or repository)
        scope = task.get("scope") if isinstance(task.get("scope"), dict) else {}
        profile = str(scope.get("delegation_profile") or task.get("task_kind") or "")
        owner = str(task.get("owner") or task_repository)
        task_evidence = [
            *evidence_refs,
            _evidence_ref("LOCAL_JSON_ARTIFACT", f"{_display_path(path)}#{task_id}"),
        ]
        if _collect_delegated_task_attention(
            attention_items=attention_items,
            task=task,
            task_id=task_id,
            task_repository=task_repository,
            source_ref=source_ref,
            owner=owner,
            generated_at_utc=generated_at_utc,
            task_evidence=task_evidence,
            scope=scope,
            profile=profile,
            stale_hours=stale_hours,
        ):
            active_tasks.append(task)

    _append_delegated_task_overlap_attention(
        attention_items=attention_items,
        active_tasks=active_tasks,
        repository=repository,
        generated_at_utc=generated_at_utc,
        evidence_refs=evidence_refs,
    )

    return (
        _source_inventory(
            source_system="delegated_task_ledger",
            source_ref=_display_path(path),
            read_status="healthy" if not attention_items else "degraded",
            owner=repository,
            evidence_refs=evidence_refs,
        ),
        attention_items,
        [],
    )


def _wiki_publication_adapter(
    *,
    config: dict[str, Any],
    repository: str,
    generated_at_utc: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    path = _source_path(
        config, "wiki_publication", "wiki_sync_status_path", "output/wiki-sync-status.json"
    )
    payload, missing_source, missing_items, missing_errors = _load_source_json(
        source_system="wiki_publication",
        path=path,
        repository=repository,
        generated_at_utc=generated_at_utc,
    )
    if missing_source is not None:
        return missing_source, missing_items, missing_errors

    evidence_refs = [_evidence_ref("WIKI_SYNC_CHECK", _display_path(path))]
    attention_items: list[dict[str, Any]] = []
    entries = payload if isinstance(payload, list) else [payload]
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        repo = str(entry.get("Repository") or entry.get("repository") or repository)
        diff_count = entry.get("DiffCount", entry.get("diff_count", 0))
        try:
            diff_count_int = int(diff_count)
        except (TypeError, ValueError):
            diff_count_int = 0
        if diff_count_int > 0:
            attention_items.append(
                _attention_item(
                    source_system="wiki_publication",
                    source_ref=repo,
                    repository=repo,
                    condition="wiki_publication_drift",
                    severity="action_required",
                    owner=repo,
                    generated_at_utc=generated_at_utc,
                    evidence_refs=evidence_refs,
                    recommended_next_action=f"Publish repo-authored wiki source for {repo}.",
                )
            )

    return (
        _source_inventory(
            source_system="wiki_publication",
            source_ref=_display_path(path),
            read_status="healthy",
            owner=repository,
            evidence_refs=evidence_refs,
        ),
        attention_items,
        [],
    )


def _agent_context_adapter(
    *,
    config: dict[str, Any],
    repository: str,
    generated_at_utc: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    path = _source_path(
        config,
        "agent_context",
        "validation_status_path",
        "output/engineering-context-system-validation.json",
    )
    payload, missing_source, missing_items, missing_errors = _load_source_json(
        source_system="agent_context",
        path=path,
        repository=repository,
        generated_at_utc=generated_at_utc,
    )
    if missing_source is not None:
        return missing_source, missing_items, missing_errors

    evidence_refs = [_evidence_ref("LOCAL_JSON_ARTIFACT", _display_path(path))]
    errors = payload.get("errors", []) if isinstance(payload, dict) else []
    attention_items: list[dict[str, Any]] = []
    if errors:
        attention_items.append(
            _attention_item(
                source_system="agent_context",
                source_ref=_display_path(path),
                repository=repository,
                condition="agent_context_validation_failed",
                severity="action_required",
                owner=repository,
                generated_at_utc=generated_at_utc,
                evidence_refs=evidence_refs,
                recommended_next_action="Fix context validation errors before relying on agent guidance.",
            )
        )
    return (
        _source_inventory(
            source_system="agent_context",
            source_ref=_display_path(path),
            read_status="healthy" if not errors else "degraded",
            owner=repository,
            evidence_refs=evidence_refs,
        ),
        attention_items,
        [],
    )


def _mesh_certification_adapter(
    *,
    config: dict[str, Any],
    repository: str,
    generated_at_utc: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    path = _source_path(
        config,
        "mesh_certification",
        "operating_report_path",
        "output/mesh-certification/enterprise-mesh-operating-report.json",
    )
    payload, missing_source, missing_items, missing_errors = _load_source_json(
        source_system="mesh_certification",
        path=path,
        repository=repository,
        generated_at_utc=generated_at_utc,
    )
    if missing_source is not None:
        return missing_source, missing_items, missing_errors

    evidence_refs = [_evidence_ref("MESH_CERTIFICATION_ARTIFACT", _display_path(path))]
    attention_items: list[dict[str, Any]] = []
    report_generated_at = payload.get("generated_at_utc") if isinstance(payload, dict) else None
    stale_hours = _threshold(config, "stale_mesh_evidence_hours", 24)
    age = _age_hours(generated_at_utc, report_generated_at)
    if age is not None and age > stale_hours:
        attention_items.append(
            _attention_item(
                source_system="mesh_certification",
                source_ref=_display_path(path),
                repository=repository,
                condition="mesh_certification_stale",
                severity="action_required",
                owner=repository,
                generated_at_utc=generated_at_utc,
                evidence_refs=evidence_refs,
                recommended_next_action="Regenerate enterprise mesh certification evidence.",
            )
        )

    operating_state = payload.get("operating_state") if isinstance(payload, dict) else None
    if operating_state == "blocked":
        severity = "blocking"
    elif operating_state == "attention_required":
        severity = "action_required"
    else:
        severity = ""
    if severity:
        attention_items.append(
            _attention_item(
                source_system="mesh_certification",
                source_ref=_display_path(path),
                repository=repository,
                condition="mesh_certification_attention",
                severity=severity,
                owner=repository,
                generated_at_utc=generated_at_utc,
                evidence_refs=evidence_refs,
                recommended_next_action="Review enterprise mesh operating report escalation queue.",
            )
        )

    return (
        _source_inventory(
            source_system="mesh_certification",
            source_ref=_display_path(path),
            read_status="healthy" if not attention_items else "degraded",
            owner=repository,
            freshness_at_utc=report_generated_at,
            evidence_refs=evidence_refs,
        ),
        attention_items,
        [],
    )


def _lotus_ai_run_summary_attention(
    *,
    run_summary: dict[str, Any],
    evidence_refs: list[dict[str, str]],
    generated_at_utc: str,
) -> list[dict[str, Any]]:
    attention_items: list[dict[str, Any]] = []
    for count_field, condition in (
        ("failed_count", "workflow_pack_failed_runs"),
        ("expired_count", "workflow_pack_expired_runs"),
        ("action_required_count", "workflow_pack_action_required_runs"),
    ):
        count = run_summary.get(count_field, 0)
        if isinstance(count, int) and count > 0:
            attention_items.append(
                _attention_item(
                    source_system="lotus_ai",
                    source_ref=f"run_summary:{count_field}",
                    repository="lotus-ai",
                    condition=condition,
                    severity="action_required",
                    owner="lotus-ai",
                    generated_at_utc=generated_at_utc,
                    evidence_refs=evidence_refs,
                    recommended_next_action=(
                        "Inspect lotus-ai workflow-pack run catalog and operator profiles."
                    ),
                )
            )
    status_summary = " ".join(
        str(line).lower() for line in run_summary.get("status_summary", [])
    )
    if "unavailable" in status_summary or "not ready" in status_summary:
        attention_items.append(
            _attention_item(
                source_system="lotus_ai",
                source_ref="run_summary:readiness",
                repository="lotus-ai",
                condition="workflow_pack_runtime_degraded",
                severity="action_required",
                owner="lotus-ai",
                generated_at_utc=generated_at_utc,
                evidence_refs=evidence_refs,
                recommended_next_action=(
                    "Confirm lotus-ai workflow-pack registry and run ledger readiness."
                ),
            )
        )
    return attention_items


def _lotus_ai_run_attention_item(
    *,
    item: dict[str, Any],
    source_ref: str,
    condition: str,
    generated_at_utc: str,
    evidence_refs: list[dict[str, str]],
    recommended_next_action: str,
    owner: str | None = None,
) -> dict[str, Any]:
    run_id = str(item.get("run_id") or "unknown-run")
    pack_id = str(item.get("pack_id") or item.get("registration_ref") or "")
    attention = _attention_item(
        source_system="lotus_ai",
        source_ref=source_ref,
        repository="lotus-ai",
        condition=condition,
        severity="action_required",
        owner=owner or str(item.get("workflow_authority_owner") or "lotus-ai"),
        generated_at_utc=generated_at_utc,
        evidence_refs=evidence_refs,
        recommended_next_action=recommended_next_action,
    )
    attention["run_id"] = run_id
    if pack_id:
        attention["workflow_pack_id"] = pack_id
    return attention


def _lotus_ai_attention_queue_items(
    *,
    attention_queue: object,
    config: dict[str, Any],
    evidence_refs: list[dict[str, str]],
    generated_at_utc: str,
) -> list[dict[str, Any]]:
    attention_items: list[dict[str, Any]] = []
    queue_depth = (
        attention_queue.get("queue_depth", 0) if isinstance(attention_queue, dict) else 0
    )
    if isinstance(queue_depth, int) and queue_depth > 0:
        attention_items.append(
            _attention_item(
                source_system="lotus_ai",
                source_ref="attention_queue:queue_depth",
                repository="lotus-ai",
                condition="workflow_pack_attention_queue_backlog",
                severity="action_required",
                owner="lotus-ai",
                generated_at_utc=generated_at_utc,
                evidence_refs=evidence_refs,
                recommended_next_action=(
                    "Use lotus-ai workflow-pack run catalog when queue_depth exceeds zero."
                ),
            )
        )

    queue_items = attention_queue.get("items", []) if isinstance(attention_queue, dict) else []
    stale_hours = _threshold(config, "stale_workflow_pack_review_hours", 24)
    for item in queue_items if isinstance(queue_items, list) else []:
        if not isinstance(item, dict):
            continue
        attention_items.extend(
            _lotus_ai_queue_item_attention(
                item=item,
                stale_hours=stale_hours,
                evidence_refs=evidence_refs,
                generated_at_utc=generated_at_utc,
            )
        )
    return attention_items


def _lotus_ai_queue_item_attention(
    *,
    item: dict[str, Any],
    stale_hours: float,
    evidence_refs: list[dict[str, str]],
    generated_at_utc: str,
) -> list[dict[str, Any]]:
    run_id = str(item.get("run_id") or "unknown-run")
    item_evidence_refs = [
        *evidence_refs,
        _evidence_ref("WORKFLOW_PACK_RUN", run_id),
    ]
    source_ref = f"workflow_pack_run:{run_id}"
    review_state = str(item.get("review_state") or "")
    runtime_state = str(item.get("runtime_state") or "")
    supportability_status = str(item.get("supportability_status") or "")
    attention_items = [
        _lotus_ai_run_attention_item(
            item=item,
            source_ref=source_ref,
            condition="workflow_pack_run_action_required",
            generated_at_utc=generated_at_utc,
            evidence_refs=item_evidence_refs,
            recommended_next_action=(
                f"Inspect lotus-ai workflow-pack run `{run_id}` operator profile."
            ),
        )
    ]

    if review_state == "AWAITING_REVIEW":
        age = _age_hours(generated_at_utc, item.get("created_at"))
        if age is not None and age > stale_hours:
            attention_items.append(
                _lotus_ai_run_attention_item(
                    item=item,
                    source_ref=source_ref,
                    condition="workflow_pack_review_stale",
                    generated_at_utc=generated_at_utc,
                    evidence_refs=item_evidence_refs,
                    recommended_next_action=(
                        f"Review stale workflow-pack run `{run_id}` before downstream use."
                    ),
                )
            )

    if runtime_state in {"FAILED", "EXPIRED"}:
        attention_items.append(
            _lotus_ai_run_attention_item(
                item=item,
                source_ref=source_ref,
                condition="workflow_pack_run_terminal_failure",
                generated_at_utc=generated_at_utc,
                evidence_refs=item_evidence_refs,
                recommended_next_action=(
                    f"Inspect terminal workflow-pack runtime state `{runtime_state}` for `{run_id}`."
                ),
            )
        )

    lineage_states = {"REVISED", "SUPERSEDED"}
    if (
        review_state in lineage_states or runtime_state == "SUPERSEDED"
    ) and supportability_status != "HISTORICAL":
        attention_items.append(
            _lotus_ai_run_attention_item(
                item=item,
                source_ref=source_ref,
                condition="workflow_pack_lineage_conflict",
                generated_at_utc=generated_at_utc,
                evidence_refs=item_evidence_refs,
                recommended_next_action=(
                    f"Confirm superseded workflow-pack run `{run_id}` is historical, not active-ready."
                ),
                owner="lotus-ai",
            )
        )
    return attention_items


def _lotus_ai_adapter(
    *,
    config: dict[str, Any],
    repository: str,
    generated_at_utc: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    path = _source_path(
        config,
        "lotus_ai",
        "runtime_status_path",
        "../lotus-ai/output/workflow-pack-runtime-status.json",
    )
    payload, missing_source, missing_items, missing_errors = _load_source_json(
        source_system="lotus_ai",
        path=path,
        repository=repository,
        generated_at_utc=generated_at_utc,
    )
    if missing_source is not None:
        return missing_source, missing_items, missing_errors

    evidence_refs = [_evidence_ref("LOCAL_JSON_ARTIFACT", _display_path(path))]
    runtime = payload.get("workflow_pack_runtime", payload) if isinstance(payload, dict) else {}
    if not isinstance(runtime, dict):
        source_ref = _display_path(path)
        item = _attention_item(
            source_system="lotus_ai",
            source_ref=source_ref,
            repository="lotus-ai",
            condition="workflow_pack_runtime_status_malformed",
            severity="action_required",
            owner="lotus-ai",
            generated_at_utc=generated_at_utc,
            evidence_refs=evidence_refs,
            recommended_next_action="Regenerate lotus-ai workflow-pack runtime status evidence.",
        )
        return (
            _source_inventory(
                source_system="lotus_ai",
                source_ref=source_ref,
                read_status="error",
                owner="lotus-ai",
                evidence_refs=evidence_refs,
            ),
            [item],
            [
                _source_read_error(
                    source_system="lotus_ai",
                    source_ref=source_ref,
                    error_summary="Workflow-pack runtime status artifact is not an object.",
                    evidence_refs=evidence_refs,
                )
            ],
    )

    attention_items: list[dict[str, Any]] = []
    run_summary = runtime.get("run_summary", {})
    if isinstance(run_summary, dict):
        attention_items.extend(
            _lotus_ai_run_summary_attention(
                run_summary=run_summary,
                evidence_refs=evidence_refs,
                generated_at_utc=generated_at_utc,
            )
        )

    attention_queue = runtime.get("attention_queue", {})
    attention_items.extend(
        _lotus_ai_attention_queue_items(
            attention_queue=attention_queue,
            config=config,
            evidence_refs=evidence_refs,
            generated_at_utc=generated_at_utc,
        )
    )

    return (
        _source_inventory(
            source_system="lotus_ai",
            source_ref=_display_path(path),
            read_status="healthy" if not attention_items else "degraded",
            owner="lotus-ai",
            evidence_refs=evidence_refs,
        ),
        attention_items,
        [],
    )


def _read_source(
    *,
    source_system: str,
    config: dict[str, Any],
    config_path: Path,
    repository: str,
    generated_at_utc: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    if source_system not in IMPLEMENTED_SOURCE_ADAPTERS:
        source, item, source_error = _not_implemented_source(
            source_system=source_system,
            config_path=config_path,
            repository=repository,
            generated_at_utc=generated_at_utc,
        )
        return source, [item], [source_error]

    adapters = {
        "github": _github_adapter,
        "background_run_ledger": _background_run_ledger_adapter,
        "delegated_task_ledger": _delegated_task_ledger_adapter,
        "wiki_publication": _wiki_publication_adapter,
        "agent_context": _agent_context_adapter,
        "mesh_certification": _mesh_certification_adapter,
        "lotus_ai": _lotus_ai_adapter,
    }
    return adapters[source_system](
        config=config,
        repository=repository,
        generated_at_utc=generated_at_utc,
    )


display_path = _display_path
read_source = _read_source
severity_counts = _severity_counts
run_status = _run_status
task_evidence_ref = _task_evidence_ref

