from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY_PATH = ROOT / "automation" / "repository-governance-policy.json"
DEFAULT_EXCEPTION_PATH = (
    ROOT
    / "platform-contracts"
    / "ci-governance"
    / "auto-merge-releasability-exceptions.v1.json"
)
OUTPUT_JSON = ROOT / "output" / "auto-merge-releasability-validation.json"
OUTPUT_MD = ROOT / "output" / "auto-merge-releasability-validation.md"

GITHUB_TOKEN_EXPRESSION = re.compile(
    r"\$\{\{\s*(github\.token|secrets\.GITHUB_TOKEN)\s*\}\}", re.IGNORECASE
)
LOTUS_AUTOMERGE_TOKEN_EXPRESSION = re.compile(
    r"\$\{\{\s*secrets\.LOTUS_AUTOMERGE_TOKEN\s*\}\}", re.IGNORECASE
)


@dataclass(frozen=True)
class RepositoryAutoMergeResult:
    repository: str
    status: str
    repo_root: str
    violations: tuple[str, ...]
    exception_owner: str | None
    exception_expires_on: str | None
    exception_reason: str | None


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return payload if isinstance(payload, dict) else {}


def _workflow_triggers(payload: dict[str, Any]) -> object:
    return payload.get("on", payload.get(True, {})) or {}


def _has_trigger(payload: dict[str, Any], trigger: str) -> bool:
    triggers = _workflow_triggers(payload)
    return isinstance(triggers, dict) and trigger in triggers


def _permissions(payload: dict[str, Any]) -> dict[str, str]:
    permissions = payload.get("permissions")
    if isinstance(permissions, str):
        return {"*": permissions}
    if not isinstance(permissions, dict):
        return {}
    return {str(key): str(value) for key, value in permissions.items()}


def _write_permissions(payload: dict[str, Any]) -> dict[str, str]:
    return {
        key: value
        for key, value in _permissions(payload).items()
        if value == "write" or value == "write-all" or value.endswith(": write")
    }


def _policy_repositories(policy_path: Path) -> list[str]:
    payload = _load_json(policy_path)
    return [str(repo["name"]) for repo in payload.get("repos", [])]


def _exception_entries(exception_path: Path) -> dict[str, dict[str, Any]]:
    payload = _load_json(exception_path)
    return {
        str(entry["repository"]): entry
        for entry in payload.get("exceptions", [])
        if isinstance(entry, dict) and "repository" in entry
    }


def _expired(expires_on: object, *, today: datetime) -> bool:
    if not isinstance(expires_on, str):
        return True
    try:
        expiry = datetime.fromisoformat(expires_on.replace("Z", "+00:00"))
    except ValueError:
        return True
    return expiry < today


def _exception_for(
    repository: str,
    violations: tuple[str, ...],
    exceptions: dict[str, dict[str, Any]],
    *,
    today: datetime,
) -> dict[str, Any] | None:
    entry = exceptions.get(repository)
    if not entry or _expired(entry.get("expires_on_utc"), today=today):
        return None
    expected_violations = tuple(sorted(str(item) for item in entry.get("violations", [])))
    return entry if expected_violations == tuple(sorted(violations)) else None


def _auto_merge_violations(workflow_path: Path) -> list[str]:
    if not workflow_path.exists():
        return ["pr-auto-merge.missing"]
    text = workflow_path.read_text(encoding="utf-8")
    payload = _load_yaml(workflow_path)
    violations: list[str] = []
    if not _has_trigger(payload, "pull_request_target"):
        violations.append("pr-auto-merge.missing-pull-request-target")
    if GITHUB_TOKEN_EXPRESSION.search(text):
        violations.append("pr-auto-merge.github-token")
    if not LOTUS_AUTOMERGE_TOKEN_EXPRESSION.search(text):
        violations.append("pr-auto-merge.missing-lotus-token")
    if "--auto --rebase --delete-branch" not in text:
        violations.append("pr-auto-merge.missing-rebase-merge")
    if _write_permissions(payload):
        violations.append("pr-auto-merge.write-permissions")
    return violations


def _merged_pr_dispatch_violations(workflow_path: Path) -> list[str]:
    if not workflow_path.exists():
        return ["merged-pr-dispatch.missing"]
    text = workflow_path.read_text(encoding="utf-8")
    payload = _load_yaml(workflow_path)
    violations: list[str] = []
    if not _has_trigger(payload, "pull_request_target"):
        violations.append("merged-pr-dispatch.missing-pull-request-target")
    if "types: [closed]" not in text and "closed" not in text:
        violations.append("merged-pr-dispatch.missing-closed-trigger")
    if _permissions(payload).get("actions") != "write":
        violations.append("merged-pr-dispatch.missing-actions-write")
    if "gh workflow run main-releasability.yml" not in text or "--ref main" not in text:
        violations.append("merged-pr-dispatch.wrong-main-releasability-target")
    return violations


def _main_releasability_violations(
    workflow_path: Path, *, merged_pr_dispatch_exists: bool
) -> list[str]:
    if not workflow_path.exists():
        return ["main-releasability.missing"]
    payload = _load_yaml(workflow_path)
    violations: list[str] = []
    if not _has_trigger(payload, "workflow_dispatch"):
        violations.append("main-releasability.missing-workflow-dispatch")
    if merged_pr_dispatch_exists and _has_trigger(payload, "push"):
        violations.append("main-releasability.duplicate-automatic-trigger")
    return violations


def validate_repository(
    repository: str,
    *,
    repos_root: Path,
    exceptions: dict[str, dict[str, Any]],
    today: datetime,
    require_local_repos: bool,
) -> RepositoryAutoMergeResult:
    repo_root = repos_root / repository
    if not repo_root.exists():
        violations = ("repository-root.missing",) if require_local_repos else ()
        status = "missing-local-repo" if not require_local_repos else "drift"
        return RepositoryAutoMergeResult(
            repository=repository,
            status=status,
            repo_root=str(repo_root),
            violations=violations,
            exception_owner=None,
            exception_expires_on=None,
            exception_reason=None,
        )

    workflow_dir = repo_root / ".github" / "workflows"
    merged_pr_dispatch_path = workflow_dir / "merged-pr-main-releasability.yml"
    violations = tuple(
        sorted(
            [
                *_auto_merge_violations(workflow_dir / "pr-auto-merge.yml"),
                *_merged_pr_dispatch_violations(merged_pr_dispatch_path),
                *_main_releasability_violations(
                    workflow_dir / "main-releasability.yml",
                    merged_pr_dispatch_exists=merged_pr_dispatch_path.exists(),
                ),
            ]
        )
    )
    exception = _exception_for(repository, violations, exceptions, today=today)
    status = "aligned" if not violations else "excepted" if exception else "drift"
    return RepositoryAutoMergeResult(
        repository=repository,
        status=status,
        repo_root=str(repo_root),
        violations=violations,
        exception_owner=str(exception.get("owner")) if exception else None,
        exception_expires_on=str(exception.get("expires_on_utc")) if exception else None,
        exception_reason=str(exception.get("reason")) if exception else None,
    )


def validate_repositories(
    *,
    policy_path: Path = DEFAULT_POLICY_PATH,
    exception_path: Path = DEFAULT_EXCEPTION_PATH,
    repos_root: Path = ROOT.parent,
    require_local_repos: bool = False,
    today: datetime | None = None,
) -> list[RepositoryAutoMergeResult]:
    exceptions = _exception_entries(exception_path)
    effective_today = today or datetime.now(UTC)
    return [
        validate_repository(
            repository,
            repos_root=repos_root,
            exceptions=exceptions,
            today=effective_today,
            require_local_repos=require_local_repos,
        )
        for repository in _policy_repositories(policy_path)
    ]


def _write_outputs(results: list[RepositoryAutoMergeResult]) -> None:
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(
        json.dumps([asdict(result) for result in results], indent=2),
        encoding="utf-8",
    )
    lines = [
        "# Auto-Merge Releasability Validation",
        "",
        "| Repository | Status | Violations | Exception Expires |",
        "| --- | --- | --- | --- |",
    ]
    for result in results:
        lines.append(
            f"| `{result.repository}` | `{result.status}` | "
            f"`{', '.join(result.violations) or '-'}` | "
            f"`{result.exception_expires_on or '-'}` |"
        )
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Lotus auto-merge and exact-main releasability workflow posture."
    )
    parser.add_argument("--policy-path", type=Path, default=DEFAULT_POLICY_PATH)
    parser.add_argument("--exception-path", type=Path, default=DEFAULT_EXCEPTION_PATH)
    parser.add_argument("--repos-root", type=Path, default=ROOT.parent)
    parser.add_argument("--require-local-repos", action="store_true")
    args = parser.parse_args()

    results = validate_repositories(
        policy_path=args.policy_path,
        exception_path=args.exception_path,
        repos_root=args.repos_root,
        require_local_repos=args.require_local_repos,
    )
    _write_outputs(results)
    failures = [result for result in results if result.status == "drift"]
    if failures:
        print("Auto-merge releasability validation failed:")
        for result in failures:
            print(f"- {result.repository}: {', '.join(result.violations)}")
        return 1
    print("Auto-merge releasability validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
