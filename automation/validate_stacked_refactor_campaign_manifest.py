from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


AUTOMATION_DIR = Path(__file__).resolve().parent
if str(AUTOMATION_DIR) not in sys.path:
    sys.path.insert(0, str(AUTOMATION_DIR))

from json_contract_validation import validate_json_schema_subset_document  # noqa: E402
from validate_branch_commit_budget import (  # noqa: E402
    BranchCommitBudgetError,
    classify_commit_budget,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST_PATH = (
    ROOT
    / "platform-contracts"
    / "agent-engineering"
    / "examples"
    / "stacked-refactor-campaign-valid.json"
)
SCHEMA_PATH = (
    ROOT
    / "platform-contracts"
    / "agent-engineering"
    / "stacked-refactor-campaign-manifest.schema.json"
)

SCHEMA_VERSION = "lotus.stacked-refactor-campaign.v1"
ISSUE_CLOSURE_POLICY = "final_validated_main_only"
NON_FINAL_ISSUE_DECISION = "keep_campaign_issues_open"
FINAL_ISSUE_DECISION = "close_after_final_validated_main"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _schema_validation_errors(
    manifest: dict[str, Any],
    schema_path: Path = SCHEMA_PATH,
) -> list[str]:
    return [
        f"schema {error}"
        for error in validate_json_schema_subset_document(schema_path, manifest)
    ]


def _as_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def _validate_required_fields(
    errors: list[str],
    payload: dict[str, Any],
    required_fields: tuple[str, ...],
    prefix: str,
) -> None:
    for field in required_fields:
        if field not in payload:
            errors.append(f"{prefix} missing {field}")


def _issue_key(issue: dict[str, Any]) -> str:
    return f"{issue.get('repo')}#{issue.get('number')}"


def _validate_manifest_identity(manifest: dict[str, Any], errors: list[str]) -> None:
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    for field in ("campaign_id", "repository", "base_branch"):
        if not _string(manifest.get(field)).strip():
            errors.append(f"{field} must be a non-empty string")
    if manifest.get("issue_closure_policy") != ISSUE_CLOSURE_POLICY:
        errors.append(f"issue_closure_policy must be {ISSUE_CLOSURE_POLICY}")


def _validate_campaign_issues(manifest: dict[str, Any], errors: list[str]) -> None:
    issues = _as_list(manifest.get("campaign_issues"))
    if not issues:
        errors.append("campaign_issues must contain at least one issue")
        return

    seen: set[str] = set()
    for index, issue in enumerate(issues):
        if not isinstance(issue, dict):
            errors.append(f"campaign_issues[{index}] must be an object")
            continue
        if not _string(issue.get("repo")).strip():
            errors.append(f"campaign_issues[{index}].repo must be non-empty")
        if not isinstance(issue.get("number"), int) or issue["number"] <= 0:
            errors.append(f"campaign_issues[{index}].number must be a positive integer")
        if issue.get("final_close_required") is not True:
            errors.append(
                f"campaign_issues[{index}].final_close_required must be true"
            )
        key = _issue_key(issue)
        if key in seen:
            errors.append(f"duplicate campaign issue: {key}")
        seen.add(key)


def _validate_commit_budget(
    tranche: dict[str, Any],
    budget: dict[str, Any],
    errors: list[str],
) -> None:
    try:
        result = classify_commit_budget(
            int(tranche.get("commit_count", -1)),
            warning_at=int(budget.get("warning_at", 0)),
            split_required_at=int(budget.get("split_required_at", 0)),
            fail_above=int(budget.get("fail_above", 0)),
            tranche_decision=_string(tranche.get("tranche_decision")) or None,
        )
    except (BranchCommitBudgetError, TypeError, ValueError) as exc:
        errors.append(f"{tranche.get('tranche_id')}: invalid commit budget: {exc}")
        return

    if result.severity == "fail":
        errors.append(f"{tranche.get('tranche_id')}: {result.message}")


def _validate_tranche_required_fields(
    tranche: dict[str, Any], index: int, errors: list[str]
) -> None:
    _validate_required_fields(
        errors,
        tranche,
        (
            "tranche_id",
            "branch",
            "base_sha",
            "head_sha",
            "post_merge_main_sha",
            "capability_boundary",
            "commit_count",
            "issue_closure_decision",
            "local_evidence",
            "remote_evidence",
        ),
        f"tranches[{index}]",
    )
    for field in (
        "tranche_id",
        "branch",
        "base_sha",
        "head_sha",
        "post_merge_main_sha",
        "capability_boundary",
    ):
        if not _string(tranche.get(field)).strip():
            errors.append(f"tranches[{index}].{field} must be non-empty")
    for field in ("local_evidence", "remote_evidence"):
        if not _as_list(tranche.get(field)):
            errors.append(f"tranches[{index}].{field} must contain evidence")


def _validate_tranches(manifest: dict[str, Any], errors: list[str]) -> None:
    tranches = _as_list(manifest.get("tranches"))
    budget = manifest.get("commit_budget", {})
    if not isinstance(budget, dict):
        errors.append("commit_budget must be an object")
        budget = {}
    if not tranches:
        errors.append("tranches must contain at least one tranche")
        return

    seen_ids: set[str] = set()
    for index, tranche in enumerate(tranches):
        if not isinstance(tranche, dict):
            errors.append(f"tranches[{index}] must be an object")
            continue
        tranche_id = _string(tranche.get("tranche_id"))
        if tranche_id in seen_ids:
            errors.append(f"duplicate tranche_id: {tranche_id}")
        seen_ids.add(tranche_id)
        _validate_tranche_required_fields(tranche, index, errors)
        _validate_commit_budget(tranche, budget, errors)

        is_final = index == len(tranches) - 1
        decision = tranche.get("issue_closure_decision")
        if is_final:
            if decision != FINAL_ISSUE_DECISION:
                errors.append(
                    f"{tranche_id}: final tranche must use {FINAL_ISSUE_DECISION}"
                )
        elif decision != NON_FINAL_ISSUE_DECISION:
            errors.append(
                f"{tranche_id}: non-final tranches must keep campaign issues open"
            )

        if index == 0:
            if tranche.get("required_predecessor_main_sha"):
                errors.append(f"{tranche_id}: first tranche must not require predecessor SHA")
            continue

        predecessor = tranches[index - 1]
        expected_sha = predecessor.get("post_merge_main_sha")
        actual_sha = tranche.get("required_predecessor_main_sha")
        if actual_sha != expected_sha:
            errors.append(
                f"{tranche_id}: required_predecessor_main_sha must equal previous "
                f"post_merge_main_sha {expected_sha}"
            )
        if tranche.get("base_sha") != expected_sha:
            errors.append(f"{tranche_id}: base_sha must equal predecessor main SHA")


def _validate_final_closure(manifest: dict[str, Any], errors: list[str]) -> None:
    closure = manifest.get("final_aggregate_closure")
    tranches = _as_list(manifest.get("tranches"))
    if not isinstance(closure, dict):
        errors.append("final_aggregate_closure must be an object")
        return
    _validate_required_fields(
        errors,
        closure,
        (
            "status",
            "final_tranche_id",
            "exact_main_sha",
            "main_validation_refs",
            "campaign_issues_closed",
            "branch_cleanup_evidence",
        ),
        "final_aggregate_closure",
    )
    if not tranches or not isinstance(tranches[-1], dict):
        return

    final_tranche = tranches[-1]
    if closure.get("status") == "closed":
        if closure.get("final_tranche_id") != final_tranche.get("tranche_id"):
            errors.append("final_aggregate_closure.final_tranche_id must name the last tranche")
        if closure.get("exact_main_sha") != final_tranche.get("post_merge_main_sha"):
            errors.append("final_aggregate_closure.exact_main_sha must equal final main SHA")
        if not _as_list(closure.get("main_validation_refs")):
            errors.append("closed campaign requires main_validation_refs")
        if closure.get("campaign_issues_closed") is not True:
            errors.append("closed campaign requires campaign_issues_closed true")
        if not _as_list(closure.get("branch_cleanup_evidence")):
            errors.append("closed campaign requires branch_cleanup_evidence")
    elif closure.get("status") == "open":
        if closure.get("campaign_issues_closed") is True:
            errors.append("open campaign must not mark campaign_issues_closed true")
    else:
        errors.append("final_aggregate_closure.status must be open or closed")


def validate_stacked_refactor_campaign_manifest(
    manifest: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    errors.extend(_schema_validation_errors(manifest))
    _validate_manifest_identity(manifest, errors)
    _validate_campaign_issues(manifest, errors)
    _validate_tranches(manifest, errors)
    _validate_final_closure(manifest, errors)
    return errors


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a Lotus stacked refactor campaign manifest."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    errors: list[str] = []
    if not SCHEMA_PATH.exists():
        errors.append(f"missing schema: {SCHEMA_PATH.relative_to(ROOT)}")
    try:
        manifest = _load_json(args.manifest)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"unable to load manifest: {exc}")
    else:
        errors.extend(validate_stacked_refactor_campaign_manifest(manifest))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Stacked refactor campaign manifest validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
