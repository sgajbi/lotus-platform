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
    "wiki_publication",
    "agent_context",
    "mesh_certification",
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
    entries = payload if isinstance(payload, list) else []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        repo = str(entry.get("repo") or repository)
        query_error = entry.get("query_error")
        if query_error:
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
                    repository=repo.split("/")[-1],
                    condition="github_pr_query_error",
                    severity="action_required",
                    owner=repo.split("/")[-1],
                    generated_at_utc=generated_at_utc,
                    evidence_refs=evidence_refs,
                    recommended_next_action=f"Regenerate PR monitor evidence for {repo}.",
                )
            )
            continue
        for pr in _normalize_pulls(entry.get("pulls")):
            pr_number = pr.get("number")
            pr_ref = str(pr.get("url") or f"{repo}#{pr_number}")
            repo_name = repo.split("/")[-1]
            checks = _normalize_pulls(pr.get("checks"))
            failing_checks = [
                check
                for check in checks
                if str(check.get("state", "")).upper() in {"FAILURE", "ERROR"}
            ]
            if pr.get("hasFailingChecks") or failing_checks:
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
            age = _age_hours(generated_at_utc, pr.get("updatedAt"))
            if age is not None and age > stale_hours:
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
    runs = payload if isinstance(payload, list) else []
    for run in runs:
        if not isinstance(run, dict):
            continue
        status = str(run.get("status", "")).upper()
        task_id = str(run.get("engineering_task_id") or run.get("runId") or "unknown")
        source_ref = f"{_display_path(path)}#{task_id}"
        if status in {"FAILED", "TIMED_OUT", "LOST"}:
            attention_items.append(
                _attention_item(
                    source_system="background_run_ledger",
                    source_ref=source_ref,
                    repository=str(run.get("repository") or repository),
                    condition="background_run_failed",
                    severity="blocking" if status == "LOST" else "action_required",
                    owner=str(run.get("owner") or repository),
                    generated_at_utc=generated_at_utc,
                    evidence_refs=evidence_refs,
                    recommended_next_action=f"Inspect background run `{task_id}` with status `{status}`.",
                )
            )
        if status in {"RUNNING", "QUEUED"}:
            age = _age_hours(generated_at_utc, run.get("started_at") or run.get("startedAt"))
            if age is not None and age > stale_hours:
                attention_items.append(
                    _attention_item(
                        source_system="background_run_ledger",
                        source_ref=source_ref,
                        repository=str(run.get("repository") or repository),
                        condition="background_run_stale",
                        severity="warning",
                        owner=str(run.get("owner") or repository),
                        generated_at_utc=generated_at_utc,
                        evidence_refs=evidence_refs,
                        recommended_next_action=f"Refresh or cancel stale background run `{task_id}`.",
                    )
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
        "wiki_publication": _wiki_publication_adapter,
        "agent_context": _agent_context_adapter,
        "mesh_certification": _mesh_certification_adapter,
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

