from __future__ import annotations

import argparse
import base64
import binascii
import itertools
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY_PATH = ROOT / "automation" / "repository-governance-policy.json"
OUTPUT_JSON = ROOT / "output" / "repository-governance-validation.json"
OUTPUT_MD = ROOT / "output" / "repository-governance-validation.md"


@dataclass(frozen=True)
class ExpectedRepositoryGovernance:
    name: str
    default_branch: str
    required_checks: tuple[str, ...]
    external_check_providers: tuple[tuple[str, str], ...] = ()


def load_policy(policy_path: Path) -> list[ExpectedRepositoryGovernance]:
    payload = json.loads(policy_path.read_text(encoding="utf-8"))
    repositories: list[ExpectedRepositoryGovernance] = []
    for repo in payload["repos"]:
        external_check_providers = repo.get("external_required_checks") or {}
        if not isinstance(external_check_providers, dict):
            raise ValueError(
                f"{repo['name']}: external_required_checks must map contexts to providers"
            )
        invalid_providers = {
            context: provider
            for context, provider in external_check_providers.items()
            if not isinstance(context, str)
            or not context.strip()
            or not isinstance(provider, str)
            or not provider.strip()
        }
        if invalid_providers:
            raise ValueError(
                f"{repo['name']}: external_required_checks must use non-empty string "
                "contexts and providers"
            )
        repositories.append(
            ExpectedRepositoryGovernance(
                name=repo["name"],
                default_branch=repo["default_branch"],
                required_checks=tuple(repo["required_checks"]),
                external_check_providers=tuple(
                    sorted(external_check_providers.items())
                ),
            )
        )
    return repositories


def run_gh_json(*args: str) -> Any:
    completed = subprocess.run(
        ["gh", "api", *args],
        check=False,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    if completed.returncode != 0:
        if "Branch not protected" in completed.stderr:
            return None
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())
    return json.loads(completed.stdout)


MATRIX_EXPRESSION = re.compile(r"\$\{\{\s*matrix\.([A-Za-z0-9_-]+)\s*\}\}")


def _matrix_rows(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    """Expand a job matrix with GitHub's original-combination include semantics."""

    axes = {
        key: values
        for key, values in matrix.items()
        if key not in {"include", "exclude"} and isinstance(values, list)
    }
    original_rows: list[dict[str, Any]] = []
    if axes:
        original_rows = [
            dict(zip(axes, combination, strict=True))
            for combination in itertools.product(*(axes[key] for key in axes))
        ]

    exclusions = [
        item for item in (matrix.get("exclude") or []) if isinstance(item, dict)
    ]
    original_rows = [
        row
        for row in original_rows
        if not any(
            all(row.get(key) == value for key, value in exclusion.items())
            for exclusion in exclusions
        )
    ]

    rows = [dict(row) for row in original_rows]
    additional_rows: list[dict[str, Any]] = []
    includes = matrix.get("include") or []
    for include in (item for item in includes if isinstance(item, dict)):
        # Includes match immutable originals, while their values update the corresponding
        # accumulated row. Standalone combinations are not candidates for later includes.
        compatible_indexes = [
            index
            for index, row in enumerate(original_rows)
            if all(
                key not in axes or row.get(key) == value
                for key, value in include.items()
            )
        ]
        if compatible_indexes:
            for index in compatible_indexes:
                rows[index].update(include)
        else:
            additional_rows.append(dict(include))
    return [*rows, *additional_rows]


def _expand_job_name(job: dict[str, Any]) -> set[str]:
    name = job.get("name")
    if not isinstance(name, str) or not name.strip():
        return set()
    matrix_keys = MATRIX_EXPRESSION.findall(name)
    if not matrix_keys:
        return {name}

    matrix = (job.get("strategy") or {}).get("matrix") or {}
    if not isinstance(matrix, dict):
        return set()

    expanded: set[str] = set()
    for row in _matrix_rows(matrix):
        if any(key not in row for key in matrix_keys):
            continue
        rendered = MATRIX_EXPRESSION.sub(lambda match: str(row[match.group(1)]), name)
        if "${{ matrix." not in rendered:
            expanded.add(rendered)
    return expanded


def extract_emitted_workflow_checks(workflow_documents: dict[str, str]) -> set[str]:
    emitted: set[str] = set()
    for path, source in workflow_documents.items():
        payload = yaml.safe_load(source) or {}
        if not isinstance(payload, dict):
            raise ValueError(f"{path}: workflow document must be a mapping")
        jobs = payload.get("jobs") or {}
        if not isinstance(jobs, dict):
            raise ValueError(f"{path}: workflow jobs must be a mapping")
        for job in jobs.values():
            if isinstance(job, dict):
                emitted.update(_expand_job_name(job))
    return emitted


def compare_required_check_sources(
    expected: ExpectedRepositoryGovernance,
    workflow_documents: dict[str, str],
) -> list[str]:
    required_checks = set(expected.required_checks)
    external_providers = dict(expected.external_check_providers)
    drifts: list[str] = []

    for context, provider in external_providers.items():
        if context not in required_checks:
            drifts.append(f"external check is not required: {context}")
        if not isinstance(provider, str) or not provider.strip():
            drifts.append(f"external check provider is empty: {context}")
    emitted = extract_emitted_workflow_checks(workflow_documents)
    workflow_required_checks = required_checks - set(external_providers)
    for context in sorted(workflow_required_checks - emitted):
        drifts.append(
            f"required check is not emitted by a governed workflow: {context}"
        )
    return drifts


def fetch_repository_workflow_documents(
    org: str,
    expected: ExpectedRepositoryGovernance,
) -> dict[str, str]:
    workflow_items = run_gh_json(
        f"repos/{org}/{expected.name}/contents/.github/workflows?ref={expected.default_branch}"
    )
    if not isinstance(workflow_items, list):
        raise RuntimeError(f"{expected.name}: GitHub workflow inventory is not a list")

    documents: dict[str, str] = {}
    for item in workflow_items:
        path = item.get("path") if isinstance(item, dict) else None
        if not isinstance(path, str) or Path(path).suffix not in {".yml", ".yaml"}:
            continue
        payload = run_gh_json(
            f"repos/{org}/{expected.name}/contents/{path}?ref={expected.default_branch}"
        )
        if (
            not isinstance(payload, dict)
            or payload.get("encoding") != "base64"
            or not isinstance(payload.get("content"), str)
        ):
            raise RuntimeError(
                f"{expected.name}: workflow content is unavailable for {path}"
            )
        encoded_content = re.sub(r"\s+", "", payload["content"])
        try:
            documents[path] = base64.b64decode(encoded_content, validate=True).decode(
                "utf-8"
            )
        except (binascii.Error, UnicodeDecodeError) as error:
            raise RuntimeError(
                f"{expected.name}: workflow content is invalid for {path}"
            ) from error
    return documents


def select_repositories(
    repositories: list[ExpectedRepositoryGovernance],
    requested_names: list[str] | None,
) -> list[ExpectedRepositoryGovernance]:
    if not requested_names:
        return repositories

    requested = set(requested_names)
    available = {repo.name for repo in repositories}
    unknown = sorted(requested - available)
    if unknown:
        raise ValueError(
            f"repositories are not present in policy: {', '.join(unknown)}"
        )
    return [repo for repo in repositories if repo.name in requested]


def _merge_policy_defaults() -> dict[str, bool]:
    return {
        "allow_auto_merge": False,
        "allow_squash_merge": False,
        "allow_merge_commit": False,
        "allow_rebase_merge": False,
    }


def _unprotected_branch_governance() -> dict[str, Any]:
    return {
        "protected": False,
        "required_checks": [],
        "strict": False,
        "approvals": 0,
        "dismiss_stale_reviews": False,
        "require_conversation_resolution": False,
        "required_linear_history": False,
        "allow_force_pushes": False,
        "allow_deletions": False,
        **_merge_policy_defaults(),
    }


def _feature_enabled(payload: dict[str, Any], key: str) -> bool:
    feature = payload.get(key) or {}
    return bool(feature.get("enabled"))


def _pull_request_review_governance(payload: dict[str, Any]) -> dict[str, Any]:
    review_requirements = payload.get("required_pull_request_reviews") or {}
    return {
        "approvals": int(
            review_requirements.get("required_approving_review_count") or 0
        ),
        "dismiss_stale_reviews": bool(review_requirements.get("dismiss_stale_reviews")),
    }


def _required_status_check_governance(payload: dict[str, Any]) -> dict[str, Any]:
    required_status_checks = payload.get("required_status_checks") or {}
    return {
        "required_checks": sorted(required_status_checks.get("contexts") or []),
        "strict": bool(required_status_checks.get("strict")),
    }


def normalize_actual_governance(payload: dict[str, Any] | None) -> dict[str, Any]:
    if payload is None:
        return _unprotected_branch_governance()

    return {
        "protected": True,
        **_required_status_check_governance(payload),
        **_pull_request_review_governance(payload),
        "require_conversation_resolution": _feature_enabled(
            payload, "required_conversation_resolution"
        ),
        "required_linear_history": _feature_enabled(payload, "required_linear_history"),
        "allow_force_pushes": _feature_enabled(payload, "allow_force_pushes"),
        "allow_deletions": _feature_enabled(payload, "allow_deletions"),
        **_merge_policy_defaults(),
    }


def fetch_repository_governance(
    org: str, expected: ExpectedRepositoryGovernance
) -> dict[str, Any]:
    protection = run_gh_json(
        f"repos/{org}/{expected.name}/branches/{expected.default_branch}/protection"
    )
    repository = run_gh_json(f"repos/{org}/{expected.name}")
    normalized = normalize_actual_governance(protection)
    normalized["allow_auto_merge"] = bool(repository["allow_auto_merge"])
    normalized["allow_squash_merge"] = bool(repository["allow_squash_merge"])
    normalized["allow_merge_commit"] = bool(repository["allow_merge_commit"])
    normalized["allow_rebase_merge"] = bool(repository["allow_rebase_merge"])
    return normalized


def expected_governance(expected: ExpectedRepositoryGovernance) -> dict[str, Any]:
    return {
        "protected": True,
        "required_checks": sorted(expected.required_checks),
        "strict": True,
        "approvals": 0,
        "dismiss_stale_reviews": True,
        "require_conversation_resolution": True,
        "required_linear_history": True,
        "allow_force_pushes": False,
        "allow_deletions": False,
        "allow_auto_merge": True,
        "allow_squash_merge": False,
        "allow_merge_commit": False,
        "allow_rebase_merge": True,
    }


def compare_governance(expected: dict[str, Any], actual: dict[str, Any]) -> list[str]:
    drifts: list[str] = []
    for key, expected_value in expected.items():
        actual_value = actual.get(key)
        if actual_value != expected_value:
            drifts.append(f"{key}: expected={expected_value!r} actual={actual_value!r}")
    return drifts


def write_outputs(results: list[dict[str, Any]]) -> None:
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")

    lines = [
        "# Repository Governance Validation",
        "",
        "| Repository | Branch | Status | Drift Count |",
        "|---|---|---|---:|",
    ]
    for result in results:
        lines.append(
            f"| {result['repository']} | {result['branch']} | {result['status']} | {len(result['drift'])} |"
        )
        if result["drift"]:
            lines.append("")
            for drift in result["drift"]:
                lines.append(f"- `{result['repository']}`: {drift}")
            lines.append("")

    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate emitted workflow checks and GitHub branch protection against "
            "Lotus repository governance policy."
        )
    )
    parser.add_argument("--org", default="sgajbi")
    parser.add_argument("--policy-path", type=Path, default=DEFAULT_POLICY_PATH)
    parser.add_argument(
        "--repository",
        action="append",
        help="Validate one governed repository; repeat to validate a bounded set.",
    )
    parser.add_argument(
        "--source-only",
        action="store_true",
        help="Validate that required checks are emitted without reading live settings.",
    )
    args = parser.parse_args()

    results: list[dict[str, Any]] = []
    has_drift = False
    repositories = select_repositories(load_policy(args.policy_path), args.repository)
    for repo in repositories:
        workflow_documents = fetch_repository_workflow_documents(args.org, repo)
        source_drift = compare_required_check_sources(repo, workflow_documents)
        live_drift: list[str] = []
        if not args.source_only:
            actual = fetch_repository_governance(args.org, repo)
            live_drift = compare_governance(expected_governance(repo), actual)
        drift = source_drift + live_drift
        if drift:
            has_drift = True
        results.append(
            {
                "repository": repo.name,
                "branch": repo.default_branch,
                "status": "drift" if drift else "aligned",
                "drift": drift,
            }
        )

    write_outputs(results)
    return 1 if has_drift else 0


if __name__ == "__main__":
    raise SystemExit(main())
