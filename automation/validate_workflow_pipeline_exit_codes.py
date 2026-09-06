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

# A condition does not make a sink safe: `if gate.py | tee log; then` takes the
# success branch whenever tee succeeds. Conditions are therefore analysed like
# any other pipeline; what keeps them quiet is that their terminal stage is
# normally an assertion (grep, jq, test), which is not a passive sink.
_CONDITION_KEYWORDS = ("if", "elif", "while", "until")

# Bash block structure: a `set -o pipefail` inside one of these may never
# execute, so only an unconditional setting is honoured.
_BLOCK_OPENERS = frozenset({"if", "while", "until", "for", "case"})
_BLOCK_CLOSERS = frozenset({"fi", "done", "esac"})
_CONTROL_WORDS = frozenset({"then", "do", "else", "elif", "if", "while", "until"})

# Wrappers that run another command; the sink is what follows them.
_STAGE_PREFIXES = frozenset(
    {"sudo", "env", "command", "exec", "nohup", "time", "stdbuf"}
)

# Producers with no verdict to lose. `echo "line" | sudo tee /etc/apt/x.list` is
# the ordinary privileged-write idiom: there is no gate upstream of the sink, so
# nothing is being hidden. Only pipelines that begin with something that can
# fail meaningfully are reported.
_TRIVIAL_SOURCES = frozenset({"echo", "printf", "true", ":", "yes"})

# Inside `$( )` the pipeline produces a value the caller then judges, so a
# transforming stage such as `wc` in `test "$(find … | wc -l)" -gt 0` is
# doing its job. `tee` is different: it passes data through while writing a
# log, so a gate piped into it inside a substitution has its status dropped.
_SUBSTITUTION_SINKS = frozenset({"tee"})

_STEPS_KEY = re.compile(r"^\s*steps:\s*$")
_NAME = re.compile(r"(?:^|-\s+)name:\s*(?P<name>.+?)\s*$")
_RUN_KEY = re.compile(r"^\s*(?:-\s+)?run:\s*(?P<inline>.*)$")
_PIPEFAIL_OFF = re.compile(r"^\s*set\s+(?:[-+]\w+\s+)*\+\w*o\s+pipefail\b")
_FUNCTION_DEF = re.compile(
    r"^\s*(?:function\s+)?(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\(\)\s*\{?"
)
_PIPEFAIL_ON = re.compile(r"^\s*set\s+(?:[-+]\w+\s+)*-\w*o\s+pipefail\b")
_QUOTED = re.compile(r"'[^']*'|\"[^\"]*\"")
_PIPESTATUS_CAPTURE = re.compile(
    r"(?P<var>[A-Za-z_][A-Za-z0-9_]*)=[\"']?\$\{PIPESTATUS\[0\]\}"
)
_PIPESTATUS_DIRECT = re.compile(r"^(?:exit|return)\s+\"?\$\{PIPESTATUS\[0\]\}")


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
    return _join_continuations(lines)


def _join_continuations(lines: list[str]) -> list[str]:
    """Join lines Bash treats as one command.

    A line ending in ``|`` or ``\\`` continues onto the next, and a line whose
    first token is a pipe continues the previous one. Analysing the physical
    lines separately would let ``gate.py |`` / ``tee gate.log`` through: neither
    half looks like a complete unguarded pipeline on its own.
    """
    joined: list[str] = []
    for line in lines:
        stripped = line.strip()
        if joined and (
            joined[-1].rstrip().endswith(("|", "\\")) or stripped.startswith("|")
        ):
            previous = joined.pop().rstrip().rstrip("\\").rstrip()
            joined.append(f"{previous} {stripped}".strip())
            continue
        joined.append(stripped)
    return joined


def _terminal_sink(segment: str) -> str | None:
    """Return the passive sink this single command segment ends in, if any.

    A segment is one command in a shell list; the caller splits on ``&&``,
    ``||`` and ``;``. ``|&`` is Bash shorthand for ``2>&1 |`` and is normalised
    first, or the ``&`` would be read as the sink's command name.
    """
    words = segment.replace("|&", "|").split()
    while words and (words[0] in _CONDITION_KEYWORDS or words[0] == "!"):
        words = words[1:]
    text = re.split(r"\b(?:then|do)\b", " ".join(words))[0]
    if "|" not in text:
        return None

    stages = [stage.strip() for stage in text.split("|")]
    last = _command_of(stages[-1])
    if last not in PASSIVE_SINKS:
        return None
    # Only harmless when *every* stage feeding the sink is a producer with no
    # verdict: `printf x | gate.py | tee log` still hides gate.py's failure.
    upstream = [_command_of(stage) for stage in stages[:-1]]
    if upstream and all(command in _TRIVIAL_SOURCES for command in upstream):
        return None
    return last


def _command_of(stage: str) -> str:
    """Return the command a pipeline stage runs, past prefixes and assignments."""
    words = stage.split()
    saw_prefix = False
    while words:
        head = words[0]
        if head in _STAGE_PREFIXES or "=" in head:
            saw_prefix = True
            words = words[1:]
            continue
        # `sudo -n tee log` and `sudo -- tee log` both run tee.
        if saw_prefix and (head == "--" or head.startswith("-")):
            words = words[1:]
            continue
        break
    if not words:
        return ""
    return words[0].lstrip("$(").split("/")[-1]


def unguarded_pipelines(step_body: str) -> list[str]:
    """Return each pipeline whose gate status never reaches the step.

    The step is read as command segments in execution order, so a ``set`` and a
    pipeline on the same line are handled in the order Bash runs them.

    Two Bash facts shape the guard rules. ``PIPESTATUS`` describes only the most
    recently executed pipeline, so a capture on the next line vouches for the
    **last** pipeline of the previous line and no earlier one. And a ``set -o
    pipefail`` inside a conditional or loop body may never execute, so only an
    unconditional one — at the top level of the block — is honoured.
    """
    shell = _run_lines(step_body)
    # A `set -o pipefail` inside a function body or a `( subshell )` does not
    # change the outer shell: the function's body has not run yet, and the
    # subshell's options die with it. Only a call to a function that enables it,
    # or a top-level `set`, establishes the outer state.
    function_bodies = _function_bodies(shell)
    enabling_functions = _pipefail_enabling_functions(shell)
    function_lines = {id(line) for body in function_bodies.values() for line in body}
    pipefail = False
    depth = 0
    offenders: list[str] = []

    for index, line in enumerate(shell):
        probe = _QUOTED.sub("", line)
        if probe.strip().startswith("#"):
            continue
        if id(line) in function_lines:
            # Inside a function definition: not executed here.
            continue

        segments = re.split(r"&&|\|\||;", probe)
        piped = [
            i
            for i, segment in enumerate(segments)
            if _terminal_sink(segment) is not None
        ]
        last_piped = piped[-1] if piped else None
        reported = False
        # A pipeline inside $( ) runs too, and its status reaches only the
        # assignment; a later PIPESTATUS capture describes the outer command,
        # so nothing but pipefail can guard it.
        for body in _substitution_bodies(line):
            for inner in re.split(r"&&|\|\||;", body):
                if _terminal_sink(inner) in _SUBSTITUTION_SINKS and not pipefail:
                    offenders.append(line)
                    reported = True
                    break
            if reported:
                break
        piped = [
            i
            for i, segment in enumerate(segments)
            if _terminal_sink(segment) is not None
        ]
        last_piped = piped[-1] if piped else None
        reported = False

        for position, segment in enumerate(segments):
            words = segment.split()
            for word in words:
                if word in _BLOCK_OPENERS:
                    depth += 1
                elif word in _BLOCK_CLOSERS:
                    depth = max(0, depth - 1)

            command = _strip_control_words(segment)
            if (
                command.split()[:1]
                and command.split()[0] in enabling_functions
                and depth == 0
            ):
                pipefail = True
                continue
            if _is_subshell(segment):
                continue
            if _PIPEFAIL_OFF.match(command):
                # A disable inside a branch may well execute, so it always
                # invalidates the guard; only enabling requires certainty.
                pipefail = False
                continue
            if _PIPEFAIL_ON.match(command):
                if depth == 0:
                    pipefail = True
                continue
            if position not in piped or reported:
                continue
            if pipefail:
                continue
            if position == last_piped and _status_is_propagated(shell, index):
                continue
            offenders.append(line)
            reported = True

    return offenders


def _status_is_propagated(shell: list[str], index: int) -> bool:
    """True when this pipeline's stage-0 status reaches an executed exit or return.

    Comments are stripped first: ``# exit ${PIPESTATUS[0]}`` propagates nothing.
    The capture must be a real command, and the ``exit``/``return`` that consumes
    it must start a command segment rather than merely appear in the text.
    """
    following = _strip_comment(shell[index + 1]) if index + 1 < len(shell) else ""
    # PIPESTATUS describes the most recently executed pipeline, so any command
    # run before the capture replaces it. The capture must therefore be the
    # FIRST command on the next line, not merely present somewhere on it.
    first_command = _unconditional_segments(following)[0] if following.strip() else ""

    if _PIPESTATUS_DIRECT.match(first_command.strip()):
        return True

    capture = _PIPESTATUS_CAPTURE.match(first_command.strip())
    if capture is None:
        return False

    variable = capture.group("var")
    exits = re.compile(rf"^(?:exit|return)\s+\"?\$\{{?{re.escape(variable)}\}}?")
    return any(
        exits.match(segment.strip())
        for line in shell[index + 2 :]
        for segment in _unconditional_segments(_strip_comment(line))
    )


def _strip_control_words(segment: str) -> str:
    """Drop leading `then`/`do`/`else` so `; then set +o pipefail` is seen as a set."""
    words = segment.split()
    while words and words[0] in _CONTROL_WORDS:
        words = words[1:]
    return " ".join(words)


def _substitution_bodies(line: str) -> list[str]:
    """Return the contents of each ``$( ... )`` command substitution.

    Quote stripping would otherwise hide them: ``result="$(gate.py | tee log)"``
    still executes the pipeline, and without pipefail the assignment takes
    ``tee``'s status.
    """
    bodies: list[str] = []
    index = 0
    while True:
        start = line.find("$(", index)
        if start == -1:
            return bodies
        depth = 0
        for position in range(start + 1, len(line)):
            if line[position] == "(":
                depth += 1
            elif line[position] == ")":
                depth -= 1
                if depth == 0:
                    bodies.append(line[start + 2 : position])
                    index = position + 1
                    break
        else:
            return bodies


def _unconditional_segments(line: str) -> list[str]:
    """Return only the segments Bash always runs on this line.

    ``false && exit ${{PIPESTATUS[0]}}`` never executes its exit, so a guard
    found there is not a guard. Within each ``;``-separated command, only the
    part before the first ``&&`` or ``||`` is certain to run.
    """
    return [re.split(r"&&|\|\|", part)[0] for part in line.split(";")]


def _function_bodies(shell: list[str]) -> dict[str, list[str]]:
    """Map each `name() { ... }` to the lines of its body.

    A function body does not execute where it is written, so a `set -o
    pipefail` inside one establishes nothing until the function is called.
    """
    bodies: dict[str, list[str]] = {}
    current: str | None = None
    depth = 0
    for line in shell:
        if current is None:
            match = _FUNCTION_DEF.match(line)
            if match:
                current = match.group("name")
                bodies[current] = []
                depth = line.count("{") - line.count("}")
                if depth <= 0:
                    bodies[current].append(line)
                    current = None
                else:
                    bodies[current].append(line)
            continue
        bodies[current].append(line)
        depth += line.count("{") - line.count("}")
        if depth <= 0:
            current = None
    return bodies


def _pipefail_enabling_functions(shell: list[str]) -> set[str]:
    """Functions whose body unconditionally enables pipefail."""
    enabling: set[str] = set()
    for name, body in _function_bodies(shell).items():
        for line in body:
            # `name() { set -o pipefail; }` puts the definition and the body on
            # one line; the body starts after the opening brace.
            text = (
                line.split("{", 1)[1]
                if _FUNCTION_DEF.match(line) and "{" in line
                else line
            )
            for segment in re.split(r"&&|\|\||;", text):
                candidate = _strip_control_words(segment.strip().lstrip("{}").strip())
                if _PIPEFAIL_ON.match(candidate):
                    enabling.add(name)
    return enabling


def _is_subshell(segment: str) -> bool:
    """True when the segment runs inside `( ... )`, whose options do not escape."""
    return segment.strip().startswith("(")


def _strip_comment(line: str) -> str:
    """Drop a trailing comment, leaving quoted `#` characters alone."""
    masked = _QUOTED.sub(lambda match: "\x00" * len(match.group()), line)
    position = masked.find("#")
    return line if position == -1 else line[:position]


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
    return RepositoryResult(
        repository, status, len(workflows), steps_scanned, tuple(offenders)
    )


def validate_repositories(
    repositories: list[str],
    *,
    repos_root: Path,
    require_local_repos: bool,
) -> tuple[list[RepositoryResult], list[str]]:
    results = [
        validate_repository(repo, repos_root=repos_root) for repo in repositories
    ]
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
