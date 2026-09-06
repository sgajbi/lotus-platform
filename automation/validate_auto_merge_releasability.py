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
GITHUB_SHA_VALUE_EXPRESSION = re.compile(
    r"\$\{\{\s*(?:github\.sha|inputs\.expected_sha\s*\|\|\s*github\.sha)\s*\}\}",
    re.IGNORECASE,
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


def _workflow_dispatch_inputs(payload: dict[str, Any]) -> dict[str, Any]:
    triggers = _workflow_triggers(payload)
    if not isinstance(triggers, dict):
        return {}
    workflow_dispatch = triggers.get("workflow_dispatch")
    if not isinstance(workflow_dispatch, dict):
        return {}
    inputs = workflow_dispatch.get("inputs")
    return inputs if isinstance(inputs, dict) else {}


def _workflow_concurrency_group(payload: dict[str, Any]) -> str:
    concurrency = payload.get("concurrency")
    if isinstance(concurrency, str):
        return concurrency
    if not isinstance(concurrency, dict):
        return ""
    group = concurrency.get("group")
    return group if isinstance(group, str) else ""


def _references_github_sha(group: str) -> bool:
    return GITHUB_SHA_VALUE_EXPRESSION.search(group) is not None


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


def _workflow_steps(payload: dict[str, Any]) -> list[dict[str, Any]]:
    jobs = payload.get("jobs")
    if not isinstance(jobs, dict):
        return []
    steps: list[dict[str, Any]] = []
    for job in jobs.values():
        if not isinstance(job, dict):
            continue
        job_steps = job.get("steps")
        if not isinstance(job_steps, list):
            continue
        steps.extend(step for step in job_steps if isinstance(step, dict))
    return steps


def _step_env_value(step: dict[str, Any], name: str) -> str:
    env = step.get("env")
    if not isinstance(env, dict):
        return ""
    return str(env.get(name) or "")


def _step_run(step: dict[str, Any]) -> str:
    run = step.get("run")
    return run if isinstance(run, str) else ""


# Two ways to enumerate exactly the revisions a merge added, both of which
# name each one and gate it individually.
#
# By count, oldest-first: `rev-list -n "$COMMIT_COUNT" "$MERGE_COMMIT_SHA"`,
# reversed with `tac`.
#
# By range: `rev-list --reverse "$BASE_SHA..$MERGE_COMMIT_SHA"`. This is the
# stronger of the two, because a count taken from the pull request can be wrong
# after a rebase while the range is derived from the merge itself.
#
# Recognising only the first rejected a dispatcher that had moved to the
# second, which is the hazard in asserting a command's spelling rather than
# what it enumerates: the check reports a defect when a repository improves.
_REVISION_ENUMERATIONS = (
    r'revisions="\$\(git rev-list -n "\$COMMIT_COUNT" "\$MERGE_COMMIT_SHA"(?:\s*\|\s*tac)?\)"',
    r'revisions="\$\(git rev-list --reverse "\$BASE_SHA\.\.\$MERGE_COMMIT_SHA"\)"',
)


def _step_enumerates_exact_rebase_revisions(step: dict[str, Any]) -> bool:
    merge_commit_sha = _step_env_value(step, "MERGE_COMMIT_SHA")
    run = _step_run(step)
    enumerates = any(
        re.search(pattern, run) is not None for pattern in _REVISION_ENUMERATIONS
    )
    return (
        "github.event.pull_request.merge_commit_sha" in merge_commit_sha
        and enumerates
        and re.search(r"^\s*for\s+revision\s+in\s+\$revisions;\s*do", run, re.MULTILINE)
        is not None
        and 'git merge-base --is-ancestor "$revision" HEAD' in run
    )


_MATRIX_COMMIT_SOURCE = re.compile(
    r"fromJSON\(needs\.([A-Za-z0-9_-]+)\.outputs\.commit_shas\)"
)


def _job_steps(job: dict[str, Any]) -> list[dict[str, Any]]:
    steps = job.get("steps")
    if not isinstance(steps, list):
        return []
    return [step for step in steps if isinstance(step, dict)]


def _job_has_verified_enumeration_step(job: dict[str, Any]) -> bool:
    # The enumeration must run only for PRs merged into main, assert rebase-only
    # merge settings, walk the commits endpoint anchored at the event's merge
    # SHA with an explicit page size covering the whole PR (a default page
    # would silently truncate large PRs; the count equality then fails closed),
    # compare the resolved count to the event's commit count, and publish the
    # enumerated SHAs through the job's declared output.
    condition = str(job.get("if") or "")
    if "github.event.pull_request.merged == true" not in condition:
        return False
    if "github.event.pull_request.base.ref == 'main'" not in condition:
        return False
    outputs = job.get("outputs") if isinstance(job.get("outputs"), dict) else {}
    if "outputs.commit_shas" not in str(outputs.get("commit_shas") or ""):
        return False
    for step in _job_steps(job):
        merge_commit_sha = _step_env_value(step, "MERGE_COMMIT_SHA")
        commit_count = _step_env_value(step, "PR_COMMIT_COUNT") or _step_env_value(
            step, "COMMIT_COUNT"
        )
        run = _step_run(step)
        if (
            "github.event.pull_request.merge_commit_sha" in merge_commit_sha
            and "github.event.pull_request.commits" in commit_count
            and '"false,false,true"' in run
            and "commits?sha=$MERGE_COMMIT_SHA&per_page=$PR_COMMIT_COUNT" in run
            and re.search(r'-ne\s+"\$(?:PR_)?COMMIT_COUNT"', run)
            and "commit_shas=" in run
            and "GITHUB_OUTPUT" in run
        ):
            return True
    return False


def _matrix_dispatch_is_verified(payload: dict[str, Any]) -> bool:
    """Recognize a two-job design: an integrity-verified enumeration job and a
    matrix dispatch job whose matrix is provably fed from that job's output.

    The dispatch job must consume ``fromJSON(needs.<job>.outputs.commit_shas)``
    and declare that exact job in ``needs`` — a disconnected or hard-coded
    matrix never qualifies, whatever else the workflow contains."""

    jobs = payload.get("jobs") if isinstance(payload.get("jobs"), dict) else {}
    for job in jobs.values():
        if not isinstance(job, dict):
            continue
        strategy = job.get("strategy") if isinstance(job.get("strategy"), dict) else {}
        matrix = strategy.get("matrix") if isinstance(strategy.get("matrix"), dict) else {}
        source = _MATRIX_COMMIT_SOURCE.search(str(matrix.get("commit_sha") or ""))
        if source is None:
            continue
        needs = job.get("needs")
        needs_list = [needs] if isinstance(needs, str) else (
            needs if isinstance(needs, list) else []
        )
        source_job = jobs.get(source.group(1))
        if source.group(1) not in needs_list or not isinstance(source_job, dict):
            continue
        if not _job_has_verified_enumeration_step(source_job):
            continue
        for step in _job_steps(job):
            if "matrix.commit_sha" in _step_env_value(
                step, "MERGE_COMMIT_SHA"
            ) and re.search(
                r"-(?:f|F)\s+expected_sha=\"?\$MERGE_COMMIT_SHA\"?", _step_run(step)
            ):
                return True
    return False


def _merged_pr_dispatch_passes_exact_sha(payload: dict[str, Any]) -> bool:
    for step in _workflow_steps(payload):
        merge_commit_sha = _step_env_value(step, "MERGE_COMMIT_SHA")
        run = _step_run(step)
        if (
            "github.event.pull_request.merge_commit_sha" in merge_commit_sha
            and re.search(r"-(?:f|F)\s+expected_sha=\"?\$MERGE_COMMIT_SHA\"?", run)
        ):
            return True
        if _step_enumerates_exact_rebase_revisions(step) and re.search(
            r"-(?:f|F)\s+expected_sha=\"?\$revision\"?", run
        ):
            return True
    return _matrix_dispatch_is_verified(payload)


def _merged_pr_dispatch_has_immutable_ref(payload: dict[str, Any]) -> bool:
    for step in _workflow_steps(payload):
        run = _step_run(step)
        merge_commit_strategy = (
            'dispatch_ref="main-releasability-${MERGE_COMMIT_SHA}"' in run
            and '-f sha="$MERGE_COMMIT_SHA"' in run
        )
        revision_strategy = (
            _step_enumerates_exact_rebase_revisions(step)
            and 'dispatch_ref="main-releasability-${revision}"' in run
            and '-f sha="$revision"' in run
        )
        if (
            (merge_commit_strategy or revision_strategy)
            and 'gh api "repos/$GITHUB_REPOSITORY/git/ref/tags/$dispatch_ref"' in run
            and 'gh api "repos/$GITHUB_REPOSITORY/git/refs"' in run
            and "gh workflow run main-releasability.yml" in run
            and '--ref "$dispatch_ref"' in run
        ):
            return True
    return False


def _main_releasability_has_exact_sha_assertion(payload: dict[str, Any]) -> bool:
    for step in _workflow_steps(payload):
        expected_sha = _step_env_value(step, "EXPECTED_SHA")
        run = _step_run(step)
        mismatch_fails = re.search(
            r'^\s*if\s+\[\s+"\$actual_sha"\s+!=\s+"\$EXPECTED_SHA"\s+\];\s*then'
            r".*?^\s*exit\s+1\b",
            run,
            re.DOTALL | re.MULTILINE,
        )
        if (
            "inputs.expected_sha" in expected_sha
            and 'actual_sha="$(git rev-parse HEAD)"' in run
            and mismatch_fails
        ):
            return True
    return False


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
    expected_violations = tuple(
        sorted(str(item) for item in entry.get("violations", []))
    )
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
    if _permissions(payload).get("contents") != "write":
        violations.append("merged-pr-dispatch.missing-contents-write")
    has_immutable_dispatch_ref = _merged_pr_dispatch_has_immutable_ref(payload)
    if (
        "gh workflow run main-releasability.yml" not in text
        or not has_immutable_dispatch_ref
    ):
        violations.append("merged-pr-dispatch.wrong-main-releasability-target")
    if "git/ref/tags/$dispatch_ref" in text and "|| true" in text:
        violations.append("merged-pr-dispatch.masked-immutable-ref-lookup")
    if not _merged_pr_dispatch_passes_exact_sha(payload):
        violations.append("merged-pr-dispatch.missing-expected-sha-input")
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
    if merged_pr_dispatch_exists:
        inputs = _workflow_dispatch_inputs(payload)
        has_expected_sha_input = "expected_sha" in inputs
        has_exact_sha_assertion = _main_releasability_has_exact_sha_assertion(payload)
        if not has_expected_sha_input or not has_exact_sha_assertion:
            violations.append("main-releasability.missing-expected-sha-assertion")
        concurrency_group = _workflow_concurrency_group(payload)
        if not _references_github_sha(concurrency_group):
            violations.append("main-releasability.missing-revision-aware-concurrency")
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
        exception_expires_on=str(exception.get("expires_on_utc"))
        if exception
        else None,
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
