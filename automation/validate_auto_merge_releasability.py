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
# Each form carries its own bound, and the bound is only trustworthy when it
# comes from the merge event. A hard-coded `COMMIT_COUNT` enumerates too few
# revisions; a `BASE_SHA` from anywhere else enumerates unrelated ones. Either
# way commits reach main without an individual releasability verdict, so the
# pattern and the source of its bound are checked together rather than apart.
_REVISION_ENUMERATIONS = (
    (
        r'revisions="\$\(git rev-list -n "\$COMMIT_COUNT" "\$MERGE_COMMIT_SHA"(?:\s*\|\s*tac)?\)"',
        "COMMIT_COUNT",
        "github.event.pull_request.commits",
    ),
    (
        r'revisions="\$\(git rev-list --reverse "\$BASE_SHA\.\.\$MERGE_COMMIT_SHA"\)"',
        "BASE_SHA",
        "github.event.pull_request.base.sha",
    ),
)


def _step_enumerates_exact_rebase_revisions(step: dict[str, Any]) -> bool:
    merge_commit_sha = _step_env_value(step, "MERGE_COMMIT_SHA")
    run = _step_run(step)
    enumerates = any(
        re.search(pattern, run) is not None
        and expected_source in _step_env_value(step, bound)
        for pattern, bound, expected_source in _REVISION_ENUMERATIONS
    )
    return (
        "github.event.pull_request.merge_commit_sha" in merge_commit_sha
        and enumerates
        and re.search(r"^\s*for\s+revision\s+in\s+\$revisions;\s*do", run, re.MULTILINE)
        is not None
        and 'git merge-base --is-ancestor "$revision" HEAD' in run
    )


# GitHub accepts `fromJson` and `fromJSON`, and the output name is the workflow
# author's choice. Pinning either turned a naming preference into a requirement
# and rejected a correct implementation, so the job and the output are captured
# and checked against what that job actually declares.
_MATRIX_COMMIT_SOURCE = re.compile(
    r"fromJSON\(\s*needs\.([A-Za-z0-9_-]+)\.outputs\.([A-Za-z0-9_-]+)\s*\)",
    re.IGNORECASE,
)


def _job_steps(job: dict[str, Any]) -> list[dict[str, Any]]:
    steps = job.get("steps")
    if not isinstance(steps, list):
        return []
    return [step for step in steps if isinstance(step, dict)]


def _step_enumerates_by_commits_api(step: dict[str, Any]) -> bool:
    """The paginated commits-API form, with an explicit page size and a count check."""
    run = _step_run(step)
    commit_count = _step_env_value(step, "PR_COMMIT_COUNT") or _step_env_value(
        step, "COMMIT_COUNT"
    )
    return (
        "github.event.pull_request.commits" in commit_count
        and "commits?sha=$MERGE_COMMIT_SHA&per_page=$PR_COMMIT_COUNT" in run
        and re.search(r'-ne\s+"\$(?:PR_)?COMMIT_COUNT"', run) is not None
    )


def _step_enumerates_by_rev_list(step: dict[str, Any]) -> bool:
    """The `git rev-list` form, bounded by the event's own commit count.

    Already trusted by the single-step path through `_REVISION_ENUMERATIONS`;
    the matrix path rejected it only because it looked for the API form. Bounding
    by the event's commit count is what makes it exact, and it cannot truncate
    the way an unpaginated API call can.
    """
    run = _step_run(step)
    return any(
        re.search(pattern, run) is not None
        and expected_source in _step_env_value(step, bound)
        for pattern, bound, expected_source in _REVISION_ENUMERATIONS
    )


def _logical_lines(run: str) -> list[str]:
    """Shell lines with backslash continuations joined.

    An author may split the enumeration or its emission across lines, and a
    line-by-line reader would then see neither the assignment nor the value.
    """
    joined: list[str] = []
    pending = ""
    for line in run.splitlines():
        stripped = line.rstrip()
        if stripped.endswith("\\"):
            pending += stripped[:-1]
            continue
        joined.append(pending + line)
        pending = ""
    if pending:
        joined.append(pending)
    return joined


_ASSIGNMENT = re.compile(r"\s*([A-Za-z_][A-Za-z0-9_]*)=(.*)$")


def _references(value: str, names: set[str]) -> bool:
    return any(
        re.search(r"\$\{?" + re.escape(name) + r"\b", value) is not None
        for name in names
    )


def _enumeration_variable(step: dict[str, Any]) -> str | None:
    """The variable the trusted enumeration command assigns, if any.

    Everything downstream is judged against this name, so the value the matrix
    consumes can be tied back to the enumeration that was proven rather than to
    a key that merely shares its spelling.
    """
    for line in _logical_lines(_step_run(step)):
        assignment = _ASSIGNMENT.match(line)
        if assignment is None:
            continue
        if any(
            re.search(pattern, line) is not None
            for pattern, _bound, _source in _REVISION_ENUMERATIONS
        ):
            return assignment.group(1)
        if "commits?sha=$MERGE_COMMIT_SHA&per_page=$PR_COMMIT_COUNT" in line:
            return assignment.group(1)
    return None


def _values_derived_from(run: str, seed: str) -> set[str]:
    """The seed plus every variable transitively assigned from it.

    The estate's two implementations differ here: one publishes the enumeration
    variable directly, the other reshapes it into a JSON payload first. Both are
    correct, so the binding follows the derivation rather than demanding the
    enumeration variable appear verbatim in the emission.
    """
    derived = {seed}
    for line in _logical_lines(run):
        assignment = _ASSIGNMENT.match(line)
        if assignment is None:
            continue
        name, value = assignment.group(1), assignment.group(2)
        if name not in derived and _references(value, derived):
            derived.add(name)
    return derived


def _step_emits_derived_value(
    step: dict[str, Any], key: str, derived: set[str]
) -> bool:
    """The step writes `key` to GITHUB_OUTPUT carrying the enumerated revisions.

    Checking only that the key is written accepted a step that enumerated every
    revision correctly and then published a constant or a subset under that key,
    such as the merge commit alone. The matrix would gate one revision while the
    validator reported the dispatcher as aligned.
    """
    for line in _logical_lines(_step_run(step)):
        if "GITHUB_OUTPUT" not in line:
            continue
        emission = re.search(re.escape(key) + r"=(.*?)\"?\s*>>", line)
        if emission is not None and _references(emission.group(1), derived):
            return True
    return False


def _shell_if_blocks(run: str) -> list[tuple[str, str]]:
    """(condition, body) for each `if` block, single-line or multi-line.

    A guard is only a guard if its body does something, so the condition and the
    body have to be read together.
    """
    blocks: list[tuple[str, str]] = []
    lines = _logical_lines(run)
    index = 0
    while index < len(lines):
        opener = re.match(r"\s*if\s+(?P<cond>.*?);\s*then\b(?P<rest>.*)$", lines[index])
        if opener is None:
            index += 1
            continue
        condition, rest = opener.group("cond"), opener.group("rest")
        if re.search(r"\bfi\s*;?\s*$", rest):
            blocks.append((condition, rest))
            index += 1
            continue
        body, depth = [rest], 1
        index += 1
        while index < len(lines) and depth:
            line = lines[index]
            if re.match(r"\s*if\s+.*;\s*then\b", line):
                depth += 1
            if re.match(r"\s*fi\s*$", line):
                depth -= 1
                if depth == 0:
                    index += 1
                    break
            body.append(line)
            index += 1
        blocks.append((condition, chr(10).join(body)))
    return blocks


def _terminates_unsuccessfully(body: str) -> bool:
    return re.search(r"\bexit\s+[1-9][0-9]*\b", body) is not None


def _step_refuses_an_empty_enumeration(
    step: dict[str, Any], derived: set[str]
) -> bool:
    """The step must fail rather than publish nothing.

    An empty list expands to zero matrix jobs, and zero jobs is a success: the
    dispatch job reports green having gated no commit at all. That is the
    silent-pass shape this control exists to prevent.

    Both halves are load-bearing. Accepting any emptiness test let a guard on an
    unrelated variable stand in for one on the enumeration; accepting a guard
    whose branch only logs let the empty list be published anyway. Either an
    emptiness test on the enumeration or a comparison against the event's own
    commit count is sufficient, because the estate's two implementations use one
    each, but the branch has to terminate unsuccessfully.
    """
    for condition, body in _shell_if_blocks(_step_run(step)):
        if not _terminates_unsuccessfully(body):
            continue
        tests_enumeration_empty = any(
            re.search(r"-z\s+\"?\$\{?" + re.escape(name) + r"\b", condition)
            is not None
            for name in derived
        )
        compares_event_commit_count = (
            re.search(r"-ne\s+\"?\$\{?(?:PR_)?COMMIT_COUNT\b", condition) is not None
        )
        if tests_enumeration_empty or compares_event_commit_count:
            return True
    return False


def _verified_enumeration_step(job: dict[str, Any]) -> dict[str, Any] | None:
    """This job's proven enumeration step, or None.

    The enumeration must run only for PRs merged into main, assert rebase-only
    merge settings, enumerate exactly the commits the event names, refuse an
    empty result, and publish through the job's declared output.

    Returns the step rather than a boolean so the caller can require that the
    value the matrix consumes is the one this step publishes. Checking only that
    some step was verified, and separately that some output mentioned a step
    reference, accepted a matrix fed by an unrelated step -- or by a step that
    does not exist.
    """
    condition = str(job.get("if") or "")
    if "github.event.pull_request.merged == true" not in condition:
        return None
    if "github.event.pull_request.base.ref == 'main'" not in condition:
        return None
    for step in _job_steps(job):
        merge_commit_sha = _step_env_value(step, "MERGE_COMMIT_SHA")
        run = _step_run(step)
        seed = _enumeration_variable(step)
        if seed is None:
            continue
        step_id = step.get("id")
        if (
            "github.event.pull_request.merge_commit_sha" in merge_commit_sha
            # Rebase-only, asserted against the repository's own merge settings.
            and '"false,false,true"' in run
            # Exactly the commits this PR put on main, by either trusted form.
            and (
                _step_enumerates_by_commits_api(step)
                or _step_enumerates_by_rev_list(step)
            )
            # An empty result must fail rather than produce zero matrix jobs.
            and _step_refuses_an_empty_enumeration(
                step, _values_derived_from(run, seed)
            )
            # Published through the job's declared output rather than logged.
            and "GITHUB_OUTPUT" in run
            # Addressable, so the consumed output can be bound to this step.
            and isinstance(step_id, str)
            and step_id
        ):
            return step
    return None


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
        if not isinstance(matrix, dict):
            continue
        for matrix_key, matrix_value in matrix.items():
            source = _MATRIX_COMMIT_SOURCE.search(str(matrix_value or ""))
            if source is None:
                continue
            source_name, output_name = source.group(1), source.group(2)
            needs = job.get("needs")
            needs_list = [needs] if isinstance(needs, str) else (
                needs if isinstance(needs, list) else []
            )
            source_job = jobs.get(source_name)
            if source_name not in needs_list or not isinstance(source_job, dict):
                continue
            # The consumed output must be the one the *proven* enumeration
            # step publishes. Accepting any expression containing "steps." let a
            # matrix be fed by an unrelated step emitting an empty list, and by a
            # step that does not exist at all -- both reported as verified while
            # gating nothing.
            enumeration_step = _verified_enumeration_step(source_job)
            if enumeration_step is None:
                continue
            outputs = (
                source_job.get("outputs")
                if isinstance(source_job.get("outputs"), dict)
                else {}
            )
            reference = re.search(
                r"steps\.([A-Za-z0-9_-]+)\.outputs\.([A-Za-z0-9_-]+)",
                str(outputs.get(output_name) or ""),
            )
            if reference is None or reference.group(1) != enumeration_step.get("id"):
                continue
            # Naming the proven step is still not enough: the key it publishes
            # has to carry that step's enumerated revisions. A step can walk
            # every commit correctly and then emit a constant under the expected
            # key, gating one revision while reporting the whole PR aligned.
            seed = _enumeration_variable(enumeration_step)
            if seed is None or not _step_emits_derived_value(
                enumeration_step,
                reference.group(2),
                _values_derived_from(_step_run(enumeration_step), seed),
            ):
                continue
            if _job_dispatches_matrix_revision(job, matrix_key):
                return True
    return False


def _job_dispatches_matrix_revision(job: dict[str, Any], matrix_key: str) -> bool:
    """Every dispatch must name the matrix revision as both ref and expected SHA.

    Both halves matter and neither substitutes for the other. An immutable ref
    without a matching `expected_sha` gates a commit the caller did not name, and
    an `expected_sha` dispatched on a mutable ref gates whatever that ref points
    at when the run starts. The variable is whatever the workflow binds the
    matrix value to, so it is read from the step rather than assumed.
    """
    for step in _job_steps(job):
        env = step.get("env") if isinstance(step.get("env"), dict) else {}
        bound = [
            name
            for name, value in env.items()
            if f"matrix.{matrix_key}" in str(value or "")
        ]
        if not bound:
            continue
        run = _step_run(step)
        for name in bound:
            variable = re.escape(name)
            passes_sha = re.search(
                rf"-(?:f|F)\s+expected_sha=\"?\$\{{?{variable}\}}?\"?", run
            )
            immutable_ref = re.search(
                rf"dispatch_ref=\"[^\"]*\$\{{?{variable}\}}?[^\"]*\"", run
            )
            creates_ref = re.search(
                rf"-(?:f|F)\s+sha=\"?\$\{{?{variable}\}}?\"?", run
            )
            if (
                passes_sha
                and immutable_ref
                and creates_ref
                # The ref must be looked up before it is created and used, or a
                # ref already pointing elsewhere would be dispatched as if it
                # named this revision.
                and 'gh api "repos/$GITHUB_REPOSITORY/git/ref/tags/$dispatch_ref"' in run
                and 'gh api "repos/$GITHUB_REPOSITORY/git/refs"' in run
                and "gh workflow run main-releasability.yml" in run
                and '--ref "$dispatch_ref"' in run
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
    # A matrix design proves the same property across two jobs rather than in
    # one step: the enumeration is verified where it happens, and the dispatch
    # is verified against the matrix it consumes. Checking it step-locally
    # rejected that shape for having moved the enumeration, not for being weaker.
    return _matrix_dispatch_is_verified(payload)


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
