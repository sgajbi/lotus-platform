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

# `gate | tee log || true` reaches the step with the gate's status and then
# discards it. Only commands that always succeed and never exit are counted:
# `|| exit 1` and `|| echo failed; exit 1` are handlers that propagate, and
# reporting those would reject the ordinary way a step reports a failure
# before failing.
_RECOVERY_COMMANDS = frozenset({"true", ":"})

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
    return _join_subshells(_join_continuations(lines))


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


def _join_block(pending: list[str]) -> str:
    """Join a folded block, without putting a separator after an opening paren.

    `result=$(` followed by `set -o pipefail` reads as `result=$(; set …` if the
    separator is inserted unconditionally, which is not shell anyone writes.
    """
    joined = ""
    for line in pending:
        if not joined:
            joined = line
            continue
        joined = (
            f"{joined} {line}" if joined.rstrip().endswith("(") else f"{joined}; {line}"
        )
    return joined


def _join_subshells(lines: list[str]) -> list[str]:
    """Fold a `( ... )` written across several lines into one logical command.

    Read line by line, a multiline subshell falls apart: `(` alone is an empty
    subshell, the `set -o pipefail` on the next line looks like a top-level
    command, and the option it sets is then credited to every pipeline after
    the closing paren. Measured with a gate exiting 7:

        (
          set -o pipefail
        )
        gate.py | tee log      # step status 0, and nothing was reported

    Joining the block with `;` — which Bash treats as the same separator as a
    newline — turns it into the single-line form the scope rules already handle
    correctly, rather than adding a second set of rules for the same grammar.
    """
    joined: list[str] = []
    pending: list[str] = []
    depth = 0
    for line in lines:
        # Comments and quoted text are counted by neither Bash nor this fold.
        # `# phase (` used as a visual delimiter would otherwise swallow every
        # command after it into one line beginning with `#`, which the scanner
        # skips wholesale, hiding the very pipelines it exists to judge.
        probe = _QUOTED.sub("", _strip_comment(line))
        depth += probe.count("(") - probe.count(")")
        if pending or depth > 0:
            pending.append(line)
            if depth <= 0:
                joined.append(_join_block(pending))
                pending = []
                depth = 0
            continue
        joined.append(line)
    if pending:
        # Unbalanced parentheses: the grammar is not one this guard models, so
        # the lines are returned unfolded rather than guessed at.
        joined.extend(pending)
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

    Three Bash facts shape the guard rules. ``PIPESTATUS`` describes only the
    most recently executed pipeline, so a capture on the next line vouches for
    the **last** pipeline of the previous line and no earlier one. Gaining the
    guard requires certainty: a ``set -o pipefail`` inside a conditional block,
    behind ``&&``, or in a function that is reached only conditionally, may
    never run. Losing the guard requires none: a ``set +o pipefail`` that
    *might* run is enough to stop trusting it, because the pipelines after it
    are then no longer guaranteed to report their gate's status.
    """
    return _scan_shell(_run_lines(step_body))


def _scan_shell(
    shell: list[str],
    pipefail: bool = False,
    inherited_enabling: frozenset[str] = frozenset(),
    inherited_disabling: frozenset[str] = frozenset(),
) -> list[str]:
    """Report the unguarded pipelines in one shell scope.

    ``pipefail`` is the option state inherited from the enclosing scope. That
    parameter is what lets a ``( subshell )`` be judged correctly: it inherits
    the outer setting, its own pipelines are measured against it, and whatever
    it sets is discarded at the closing paren instead of leaking outwards.

    Functions are inherited the same way, and for the same reason: a subshell
    can call a function defined outside it. Recomputing the tables from the
    subshell body alone made ``relax`` invisible inside
    ``( relax; gate | tee log )``, so a subshell that really does turn the
    guard off was accepted.

    A subshell written across several physical lines is folded into its
    single-line form before any of this runs, so its options are scoped the
    same way. Reading those lines separately did not merely over-report, as an
    earlier revision of this docstring claimed: it credited the subshell's
    ``set -o pipefail`` to the outer shell and accepted a step whose gate could
    not fail.
    """
    function_bodies = _function_bodies(shell)
    local_enabling = _pipefail_enabling_functions(shell)
    local_disabling = _pipefail_disabling_functions(shell)
    # Bash resolves a call to the most recent definition, so a function defined
    # in this scope replaces an inherited one of the same name rather than
    # joining it. Keeping both summaries let a redefined `relax` go on
    # disabling the guard it no longer touches, and rejected a valid pipeline.
    locally_defined = set(function_bodies)
    enabling_functions = local_enabling | (inherited_enabling - locally_defined)
    disabling_functions = local_disabling | (inherited_disabling - locally_defined)
    function_lines = {id(line) for body in function_bodies.values() for line in body}
    depth = 0
    offenders: list[str] = []

    for index, line in enumerate(shell):
        probe = _QUOTED.sub("", line)
        if probe.strip().startswith("#"):
            continue
        if id(line) in function_lines:
            # Inside a function definition: not executed here.
            continue

        # Substitutions are judged in their own scope, so they are taken out
        # of the line-level view before it is split. The unmasked pieces are
        # kept alongside, because that is where the substitutions still are.
        pieces = _split_top_level(_mask_substitutions(probe), ("&&", "||", ";"))
        # Split the raw line, not the quote-stripped probe: a substitution is
        # frequently written inside quotes, and stripping them removes it.
        raw_pieces = _split_top_level(line, ("&&", "||", ";"))
        segments = [(piece, preceding in ("", ";")) for piece, preceding in pieces]
        piped = [
            position
            for position, (segment, _) in enumerate(segments)
            if _terminal_sink(segment) is not None
        ]
        last_piped = piped[-1] if piped else None
        reported = False

        def _substitution_offends(segment_text: str, option_state: bool) -> bool:
            """True when a pipeline inside this segment's `$( )` loses its gate.

            A pipeline inside `$( )` runs, and its status reaches only the
            assignment; a later PIPESTATUS capture describes the outer command,
            so nothing but pipefail can guard it.

            The substitution is its own scope, exactly as a subshell is. It
            inherits the option state *as of the point it runs* and may change
            it for itself, so a `set -o pipefail` written inside one guards the
            pipeline that follows it there.
            """
            for body in _substitution_bodies(segment_text):
                local_pipefail = option_state
                local_depth = 0
                for inner, certain in _split_segments(body):
                # A substitution can contain a conditional exactly as the outer
                # shell can, so `$(if false; then set -o pipefail; fi; gate |
                # tee log)` must not credit a guard that never runs. Following
                # a `;` makes a command certain to be *reached*, not certain to
                # be *executed*.
                    for word in inner.split():
                        if word in _BLOCK_OPENERS:
                            local_depth += 1
                        elif word in _BLOCK_CLOSERS:
                            local_depth = max(0, local_depth - 1)
                    command = _strip_control_words(inner)
                    if _PIPEFAIL_OFF.match(command):
                        local_pipefail = False
                        continue
                    if _PIPEFAIL_ON.match(command):
                        if certain and local_depth == 0:
                            local_pipefail = True
                        continue
                    if (
                        _terminal_sink(inner) in _SUBSTITUTION_SINKS
                        and not local_pipefail
                    ):
                        return True
            return False


        for position, (segment, certain) in enumerate(segments):
            for word in segment.split():
                if word in _BLOCK_OPENERS:
                    depth += 1
                elif word in _BLOCK_CLOSERS:
                    depth = max(0, depth - 1)

            command = _strip_control_words(segment)
            head = command.split()[:1]
            if head and head[0] in disabling_functions:
                # No certainty is needed to lose the guard: a call that may
                # turn pipefail off leaves every later pipeline unprotected.
                pipefail = False
                continue
            if head and head[0] in enabling_functions:
                if depth == 0 and certain:
                    pipefail = True
                continue
            if _is_subshell(segment):
                # Options set inside `( )` die with it, but the pipelines
                # inside still run and still drop their gate's status.
                if not reported and _scan_shell(
                    _subshell_lines(segment),
                    pipefail,
                    frozenset(enabling_functions),
                    frozenset(disabling_functions),
                ):
                    offenders.append(line)
                    reported = True
                # A subshell is also an ordinary producer, so it can be piped
                # into a sink itself: `( set -o pipefail; gate | tee a ) | tee b`
                # guards its inner pipeline and then loses the whole subshell's
                # status to the outer `tee`. Judging only the inside would
                # accept a step that cannot fail.
                if (
                    not reported
                    and not pipefail
                    and _subshell_outer_sink(segment) is not None
                    and not (
                        position == last_piped
                        and _status_is_propagated(shell, index)
                    )
                ):
                    offenders.append(line)
                    reported = True
                # A subshell that guards itself internally still hands its own
                # status to whatever follows. `( set -o pipefail; gate | tee log
                # ) || true` propagates correctly inside the parentheses and is
                # then discarded outside them, so the inner scan is clean and the
                # step still cannot fail. Trivial subshells are exempt: `( echo
                # hi ) || true` has no verdict to lose.
                if (
                    not reported
                    and _failure_is_consumed(pieces, position)
                    and not _is_trivial_subshell("; ".join(_subshell_lines(segment)))
                ):
                    offenders.append(line)
                    reported = True
                continue
            if _PIPEFAIL_OFF.match(command):
                pipefail = False
                continue
            if _PIPEFAIL_ON.match(command):
                if depth == 0 and certain:
                    pipefail = True
                continue
            if not reported and position < len(raw_pieces):
                # Judged here rather than before the loop, so a `set +o pipefail`
                # earlier on the same line has already taken effect. Reading the
                # line's incoming state let `set +o pipefail; result=$(gate |
                # tee log)` pass.
                if _substitution_offends(raw_pieces[position][0], pipefail):
                    offenders.append(line)
                    reported = True
                    continue
            if position not in piped or reported:
                continue
            if pipefail and not _failure_is_consumed(pieces, position):
                continue
            if _failure_is_consumed(pieces, position):
                # The status reaches the step and is then thrown away, so the
                # step passes whatever the gate decided. Reported regardless of
                # pipefail, because pipefail delivers the status to something
                # that discards it.
                offenders.append(line)
                reported = True
                continue
            if position == last_piped and _status_is_propagated(shell, index):
                continue
            offenders.append(line)
            reported = True

    return offenders


def _failure_is_consumed(pieces: list[tuple[str, str]], position: int) -> bool:
    """True when a recovery operator immediately discards this segment's status."""
    if position + 1 >= len(pieces):
        return False
    following, preceding_operator = pieces[position + 1]
    if preceding_operator != "||":
        return False
    command = _command_of(_strip_control_words(following))
    return command in _RECOVERY_COMMANDS


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


def _mask_substitutions(line: str) -> str:
    """Replace each ``$( ... )`` with a placeholder of no consequence.

    A pipeline inside a substitution is judged in the substitution's own scope,
    which can enable ``pipefail`` for itself. Leaving the text in place meant
    the line-level scan judged the same pipeline a second time against the
    outer state and reported a substitution Bash propagates correctly. Each
    pipeline is judged once, by the scope that actually runs it.
    """
    masked = line
    while True:
        start = masked.find("$(")
        if start == -1:
            return masked
        depth = 0
        for position in range(start + 1, len(masked)):
            if masked[position] == "(":
                depth += 1
            elif masked[position] == ")":
                depth -= 1
                if depth == 0:
                    masked = f"{masked[:start]}SUBSTITUTION{masked[position + 1 :]}"
                    break
        else:
            # Unbalanced: leave it alone rather than guess at the grammar.
            return masked


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
                    body = line[start + 2 : position]
                    bodies.append(body)
                    # `$(echo $(gate | tee log))` hides the gate one level down:
                    # read as a single body, its upstream is `echo`, which has no
                    # verdict to lose. The nested substitution runs on its own
                    # and drops the gate's status exactly as the outer one would.
                    bodies.extend(_substitution_bodies(body))
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
    """Functions whose body is *certain* to enable pipefail when called.

    A `set -o pipefail` wrapped in an `if` inside the body, or placed behind
    `&&`, may never execute, so calling that function establishes nothing and
    a pipeline after the call is still unguarded.
    """
    enabling: set[str] = set()
    for name, body in _function_bodies(shell).items():
        depth = 0
        for line in body:
            # `name() { set -o pipefail; }` puts the definition and the body on
            # one line; the body starts after the opening brace.
            text = (
                line.split("{", 1)[1]
                if _FUNCTION_DEF.match(line) and "{" in line
                else line
            )
            for segment, certain in _split_segments(text):
                for word in segment.split():
                    if word in _BLOCK_OPENERS:
                        depth += 1
                    elif word in _BLOCK_CLOSERS:
                        depth = max(0, depth - 1)
                candidate = _strip_control_words(segment.strip().lstrip("{}").strip())
                if _PIPEFAIL_ON.match(candidate) and depth == 0 and certain:
                    enabling.add(name)
    return enabling


def _pipefail_disabling_functions(shell: list[str]) -> set[str]:
    """Functions whose pipefail state is off by the time they return.

    The body is read in order, because what matters to the caller is the state
    the function leaves behind, not every state it passes through. A function
    that disables pipefail and then unconditionally restores it —
    `reset() { set +o pipefail; set -o pipefail; }` — returns with the guard
    intact, and Bash propagates the next pipeline's failure normally.

    The two directions stay asymmetric within that walk. Any `set +o pipefail`
    turns the tracked state off, conditional or not, because a disable that
    might run is enough to stop trusting the guard. Only a `set -o pipefail`
    that is certain to run — unconditional, and not inside a block — turns it
    back on.
    """
    disabling: set[str] = set()
    for name, body in _function_bodies(shell).items():
        state_is_off = False
        depth = 0
        for line in body:
            text = (
                line.split("{", 1)[1]
                if _FUNCTION_DEF.match(line) and "{" in line
                else line
            )
            for segment, certain in _split_segments(text):
                for word in segment.split():
                    if word in _BLOCK_OPENERS:
                        depth += 1
                    elif word in _BLOCK_CLOSERS:
                        depth = max(0, depth - 1)
                candidate = _strip_control_words(segment.strip().lstrip("{}").strip())
                if _PIPEFAIL_OFF.match(candidate):
                    state_is_off = True
                elif _PIPEFAIL_ON.match(candidate) and certain and depth == 0:
                    state_is_off = False
        if state_is_off:
            disabling.add(name)
    return disabling


def _split_top_level(text: str, operators: tuple[str, ...]) -> list[tuple[str, str]]:
    """Split on shell operators that are not nested inside parentheses.

    A plain regex split cuts ``( set -o pipefail; gate.py | tee log )`` in half
    and then reports its correctly guarded remainder as an offender, so nesting
    is tracked. Each piece is returned with the operator that preceded it, an
    empty string for the first.
    """
    pieces: list[tuple[str, str]] = []
    depth = 0
    start = 0
    preceding = ""
    index = 0
    while index < len(text):
        character = text[index]
        if character == "(":
            depth += 1
        elif character == ")":
            depth = max(0, depth - 1)
        elif depth == 0:
            operator = next(
                (item for item in operators if text.startswith(item, index)), None
            )
            if operator is not None:
                pieces.append((text[start:index], preceding))
                preceding = operator
                index += len(operator)
                start = index
                continue
        index += 1
    pieces.append((text[start:], preceding))
    return pieces


def _split_segments(line: str) -> list[tuple[str, bool]]:
    """Return each command on the line with whether Bash is certain to run it.

    A segment reached only after ``&&`` or ``||`` depends on the exit status of
    what ran before it, so a guard found there is not a guard.
    """
    return [
        (segment, preceding in ("", ";"))
        for segment, preceding in _split_top_level(line, ("&&", "||", ";"))
    ]


def _is_subshell(segment: str) -> bool:
    """True when the segment runs inside `( ... )`, whose options do not escape."""
    return segment.strip().startswith("(")


def _subshell_outer_sink(segment: str) -> str | None:
    """The passive sink a `( ... )` subshell is piped into, if any.

    Only the text after the matching close paren counts. A pipe *inside* the
    parentheses belongs to the subshell's own scope and is judged there, so
    reading the segment as a whole would report `( set -o pipefail; gate |
    tee log )` as unguarded when Bash propagates its failure correctly.
    """
    text = segment.strip()
    depth = 0
    for position, character in enumerate(text):
        if character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if depth == 0:
                tail = text[position + 1 :]
                if "|" not in tail:
                    return None
                # The subshell stands in as the producer feeding that tail, and
                # it inherits its contents' classification. `( printf x ) | tee
                # log` hides no verdict for the same reason `printf x | tee log`
                # does not, so a subshell containing only trivial producers must
                # not become a gate merely by being wrapped in parentheses.
                producer = "echo" if _is_trivial_subshell(text[1:position]) else "subshell"
                return _terminal_sink(f"{producer} {tail}")
    return None


def _is_trivial_subshell(body: str) -> bool:
    """True when every command inside the subshell is a producer with no verdict."""
    commands = [
        _command_of(stage)
        for piece, _ in _split_top_level(body, (";",))
        for part, _ in _split_segments(piece)
        for stage in part.split("|")
        if _command_of(stage)
    ]
    return bool(commands) and all(
        command in _TRIVIAL_SOURCES for command in commands
    )


def _subshell_lines(segment: str) -> list[str]:
    """Return a `( ... )` subshell body as its separately executed commands.

    Splitting on `;` keeps the PIPESTATUS rule working inside the subshell:
    `( gate.py | tee log; exit ${PIPESTATUS[0]} )` does propagate the gate's
    status and must not be reported.
    """
    text = segment.strip()
    body = text[1:]
    depth = 0
    for position, character in enumerate(text):
        if character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if depth == 0:
                body = text[1:position]
                break
    return [piece for piece, _ in _split_top_level(body, (";",))]


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
