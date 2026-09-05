"""Fail when a workflow step hides a gate's exit code behind a pipe.

A shell pipeline exits with the status of its **last** command. A step written
as ``gate.py 2>&1 | tee log.txt`` therefore reports ``tee``'s success no matter
what the gate decided, and ``bash -e`` does not help because the pipeline itself
succeeded. Such a step is configured, runs on every push, produces a log — and
cannot fail.

This is measured, not theoretical: on 2026-09-06 six steps in ``lotus-gateway``
carried this shape, including ``make test-coverage`` and ``make security-audit``.
Its branch-protection gate had raised ``CalledProcessError`` on every run since
it landed, each traceback sitting beneath a green check.

The guard is estate-wide because the defect is domain-agnostic: any repository
can reintroduce it, and a per-repository copy of the rule would drift.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "automation" / "repository-governance-policy.json"

# Commands that report their own success no matter what fed them. A pipeline
# ending in one of these replaces the gate's status with the sink's, which is
# how a gate becomes incapable of failing. `grep` and `jq` are deliberately
# absent: as a terminal stage they are usually the assertion itself.
PASSIVE_SINKS = frozenset(
    {
        "tee",
        "tail",
        "head",
        "cat",
        "sort",
        "uniq",
        "tr",
        "sed",
        "awk",
        "fold",
        "column",
        "more",
        "less",
        "wc",
    }
)

# Constructs that consume a pipeline's status themselves, so the step's exit
# code never depended on it. Flagging these would be noise, not a finding.
_CONDITION_PREFIXES = ("if ", "if!", "while ", "until ", "elif ", "! ")

_STEPS_KEY = re.compile(r"^\s*steps:\s*$")
_NAME = re.compile(r"(?:^|-\s+)name:\s*(?P<name>.+?)\s*$")
_RUN_KEY = re.compile(r"^\s*(?:-\s+)?run:\s*(?P<inline>.*)$")
_SET_PIPEFAIL = re.compile(r"^\s*set\s+[-\w\s]*-?o\s+pipefail")
_QUOTED = re.compile(r"'[^']*'|\"[^\"]*\"")


@dataclass(frozen=True)
class Offender:
    repository: str
    workflow: str
    step: str

    def __str__(self) -> str:
        return f"{self.repository}: {self.workflow} :: {self.step}"


@dataclass(frozen=True)
class RepositoryResult:
    repository: str
    status: str
    workflows_scanned: int
    steps_scanned: int
    offenders: tuple[Offender, ...]


def policy_repositories(policy_path: Path = POLICY_PATH) -> list[str]:
    payload = json.loads(policy_path.read_text(encoding="utf-8"))
    return [str(repo["name"]) for repo in payload.get("repos", [])]


def iter_steps(workflow_text: str):
    """Yield (step name, step body) for each step in a workflow document.

    Steps are found by list structure, not by a ``name:`` key: ``- run: gate.py
    | tee log.txt`` is a valid unnamed step, and a scanner keyed to ``- name:``
    would skip exactly the pipeline it exists to catch.
    """
    lines = workflow_text.splitlines()
    in_steps = False
    steps_indent = 0
    item_indent: int | None = None
    current: list[str] | None = None

    def name_of(block: list[str]) -> str:
        for line in block:
            match = _NAME.search(line)
            if match:
                return match.group("name").strip().strip("\"'")
        return "(unnamed step)"

    for line in lines:
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())

        if not stripped:
            if current is not None:
                current.append(line)
            continue

        if _STEPS_KEY.match(line):
            if current is not None:
                yield name_of(current), "\n".join(current)
                current = None
            in_steps = True
            steps_indent = indent
            item_indent = None
            continue

        if not in_steps:
            continue

        if indent <= steps_indent:
            # Dedented out of the steps block entirely.
            if current is not None:
                yield name_of(current), "\n".join(current)
                current = None
            in_steps = False
            item_indent = None
            continue

        is_item = stripped.startswith("- ")
        if is_item and item_indent is None:
            item_indent = indent

        if is_item and indent == item_indent:
            if current is not None:
                yield name_of(current), "\n".join(current)
            current = [line]
        elif current is not None:
            current.append(line)

    if current is not None:
        yield name_of(current), "\n".join(current)


def _run_lines(step_body: str) -> list[str]:
    """Return the shell lines of a step's run: block, in execution order."""
    lines: list[str] = []
    collecting = False
    block_indent: int | None = None
    for line in step_body.splitlines():
        match = _RUN_KEY.match(line)
        if match:
            inline = match.group("inline").strip()
            if inline and inline not in {"|", ">", "|-", ">-", "|+", ">+"}:
                lines.append(inline)
                collecting = False
            else:
                collecting = True
                block_indent = None
            continue
        if not collecting:
            continue
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        if block_indent is None:
            block_indent = indent
        if indent < block_indent:
            collecting = False
            continue
        lines.append(line.strip())
    return lines


def _terminal_sink(shell_line: str) -> str | None:
    """Return the passive sink a top-level pipeline ends in, if any."""
    stripped = shell_line.strip()
    if stripped.startswith("#"):
        return None
    if any(stripped.startswith(prefix) for prefix in _CONDITION_PREFIXES):
        return None
    probe = _QUOTED.sub("", stripped).replace("||", "")
    if "|" in probe and ("&&" in probe or ";" in probe):
        # Compound line: judge only the segment the step's status comes from.
        probe = re.split(r"&&|;", probe)[-1]
    if "|" not in probe:
        return None
    last_stage = probe.rsplit("|", 1)[1].strip()
    if not last_stage:
        return None
    command = last_stage.split()[0].lstrip("$(").split("/")[-1]
    return command if command in PASSIVE_SINKS else None


def unguarded_pipelines(step_body: str) -> list[str]:
    """Return each pipeline whose gate status never reaches the step.

    Guards are evaluated per pipeline in execution order: ``set -o pipefail``
    counts only for pipelines that follow it, and a ``${PIPESTATUS[0]}`` capture
    counts only for the pipeline it immediately follows. A step that guards its
    first pipeline and not its second is reported, because the second one still
    cannot fail.
    """
    shell = _run_lines(step_body)
    pipefail_from: int | None = None
    offenders: list[str] = []

    for index, line in enumerate(shell):
        if pipefail_from is None and _SET_PIPEFAIL.match(line):
            pipefail_from = index
            continue
        sink = _terminal_sink(line)
        if sink is None:
            continue
        if pipefail_from is not None and index > pipefail_from:
            continue
        following = " ".join(shell[index + 1 : index + 3])
        if "PIPESTATUS" in following:
            continue
        offenders.append(line.strip())

    return offenders


def step_hides_exit_code(body: str) -> bool:
    """True when any pipeline in the step cannot report its gate's failure."""
    return bool(unguarded_pipelines(body))


def validate_repository(repository: str, *, repos_root: Path) -> RepositoryResult:
    workflow_dir = repos_root / repository / ".github" / "workflows"
    if not workflow_dir.is_dir():
        return RepositoryResult(repository, "missing-local-repo", 0, 0, ())

    offenders: list[Offender] = []
    workflows = sorted(workflow_dir.glob("*.yml")) + sorted(workflow_dir.glob("*.yaml"))
    steps_scanned = 0
    for workflow in workflows:
        text = workflow.read_text(encoding="utf-8", errors="replace")
        for name, body in iter_steps(text):
            steps_scanned += 1
            if step_hides_exit_code(body):
                offenders.append(Offender(repository, workflow.name, name))

    status = "drift" if offenders else "clean"
    return RepositoryResult(repository, status, len(workflows), steps_scanned, tuple(offenders))


def validate_repositories(
    repositories: list[str],
    *,
    repos_root: Path,
    require_local_repos: bool,
) -> tuple[list[RepositoryResult], list[str]]:
    results = [validate_repository(repo, repos_root=repos_root) for repo in repositories]
    failures = [str(offender) for result in results for offender in result.offenders]
    if require_local_repos:
        failures.extend(
            f"{result.repository}: repository workflows not available for scanning"
            for result in results
            if result.status == "missing-local-repo"
        )
    return results, failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repos-root", type=Path, default=ROOT.parent)
    parser.add_argument("--policy", type=Path, default=POLICY_PATH)
    parser.add_argument(
        "--require-local-repos",
        action="store_true",
        help="treat an unavailable repository as a failure rather than a skip",
    )
    args = parser.parse_args()

    repositories = policy_repositories(args.policy)
    results, failures = validate_repositories(
        repositories,
        repos_root=args.repos_root,
        require_local_repos=args.require_local_repos,
    )

    scanned = sum(result.steps_scanned for result in results)
    covered = [result for result in results if result.status != "missing-local-repo"]

    if failures:
        print("Workflow pipeline exit-code gate failed:")
        for failure in failures:
            print(f"  - {failure}")
        print(
            "\nA piped step exits with the pipe's status, not the gate's. "
            "Add 'set -o pipefail', or capture ${PIPESTATUS[0]} and exit with it."
        )
        return 1

    print(
        "Workflow pipeline exit-code gate passed: "
        f"{scanned} steps across {len(covered)}/{len(repositories)} repositories, "
        "no step hides a gate's exit code."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
