"""Audit whether a repository's quality gates can actually fail.

The estate has a well-developed answer to *which* signals deserve a gate
(`lotus-ci-enforcement-governance`), and no answer at all to whether a gate that exists is alive.
A gate is alive only if all five hold:

1. **Reachable** - some blocking lane invokes it. A `*-gate` target nothing calls is dead
   governance: a reader of the Makefile concludes the rule is enforced, and it never runs.
2. **Capable of failing** - the command it runs returns non-zero on a finding. `radon cc` has no
   failing exit code in any mode, so a `complexity-gate` built on it reports complexity and passes
   unconditionally.
3. **Fail-closed on empty input** - a gate that inspected zero files must fail. Silence is never a
   pass.
4. **Observed to have run** - a correct blocking gate on a trigger that never fires has produced no
   verdict.
5. **Ordered before the act it governs** - a gate whose verdict arrives after the irreversible step
   reports rather than prevents. Failing the run afterwards does not un-publish an image.

This script detects rules 1 and 2, which are decidable from the Makefile and the workflows. Rules 3,
4 and 5 are deliberately **not** implemented: rule 3 needs the gate executed against an empty input,
rule 4 needs GitHub run history, and rule 5 needs to know which step in a lane is irreversible, which
is a judgement rather than a pattern. All three stay review obligations, recorded in the Gate
Liveness Standard in `lotus-ci-enforcement-governance`. Claiming to cover them would reproduce the
defect this tool exists to find.

This script is itself a gate, so it fails when it inspected nothing - per repository, not only in
aggregate. A fleet run where one path is missing or one repository declares no gates is a run that
did not inspect what it was asked to, and reporting that as clean would be the exact class of
defect the audit reports on others.

**It reads local working trees, not `main`.** A fleet count therefore reflects whatever branch each
checkout happens to be on: a repository sitting on a fix branch reports the fixed state, and the
same command run elsewhere gives a different answer. That is fine for a developer checking their own
change and wrong for an estate measurement, so any number quoted as fleet truth must say which
revision each repository was on - or the run must be done against clean `main` checkouts. Treating
the output as authoritative without that is the same mistake the audit reports on others: a
measurement that looks like it describes one thing and describes another.
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

# Targets a blocking lane is rooted at. `lint` is included because several repositories hang gates
# off it, but it is only *seeded* when something actually invokes it - see `blocking_roots_for`.
CANONICAL_ROOTS = ("ci", "check", "check-all")
CONDITIONAL_ROOTS = ("lint",)

# Suffixes that declare intent to block. A target named `*-gate` or `*-guard` is a promise.
GATE_SUFFIXES = ("-gate", "-guard")

# Report-only invocations. Each returns 0 whatever it finds, so a target built on one cannot fail
# no matter what the tree contains.
CANNOT_FAIL_PATTERNS: tuple[tuple[str, str], ...] = (
    (
        r"\bradon\s+(?:cc|mi|raw|hal)\b",
        "radon has no failing exit code in any mode - it prints and returns 0",
    ),
    (
        r"\btrivy\b(?![\s\S]*--exit-code[= ]1)",
        "trivy without --exit-code 1 reports findings and returns 0",
    ),
    (r"--exit-code[= ]0\b", "--exit-code 0 explicitly discards the verdict"),
    (
        r"\bruff\b[\s\S]*--exit-zero\b",
        "ruff --exit-zero explicitly discards the verdict",
    ),
    (r"\|\|\s*true\s*$", "|| true discards the exit status of the final command"),
    (r"\|\|\s*:\s*$", "|| : discards the exit status of the final command"),
    (
        r"\|\|\s*echo(?:\s+[^;&|]*)?\s*$",
        "a terminal || echo fallback discards the preceding command's exit status",
    ),
    (r";\s*true\s*$", "; true discards the exit status"),
    (r"\|\|\s*exit\s+0\s*$", "|| exit 0 discards the exit status of the final command"),
)

# Commands that always succeed. When one of these is the *last* command on a recipe line it
# supplies the line's exit status, so whatever ran before it cannot fail the gate.
ALWAYS_SUCCEEDS = re.compile(r"^(?::(?:\s|$)|(?:echo|true|exit\s+0)\b)")

# `set -o pipefail` / `bash -o pipefail -c ...` makes a pipeline return the first non-zero stage,
# so a piped gate under it does fail. Checked against the whole recipe line, not the final segment,
# because the option is usually enabled before the pipeline it protects.
PIPEFAIL_ENABLED = re.compile(r"-o\s+pipefail\b|set\s+-[a-z]*o\s+pipefail\b")
ERREXIT_ENABLED = re.compile(
    r"(?:^|[;&]\s*)set\s+-[a-z]*e[a-z]*\b|\bbash\s+-[^\s]*e[^\s]*"
)

# Make recipe prefixes. `-` ignores the command's failure; `@` only silences echo; `+` forces
# execution. They combine in any order, so `@-python g.py` ignores errors just as `-python g.py`.
_RECIPE_PREFIXES = re.compile(r"^[@+-]+")
_IGNORES_ERRORS = re.compile(r"^[@+]*-")

_TARGET = re.compile(r"^([A-Za-z0-9_.%+-]+(?:\s+[A-Za-z0-9_.%+-]+)*):\s*(.*)$")
_MAKE_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
_MAKE_OPTIONS_REQUIRING_VALUES = {
    "-C",
    "--directory",
    "-f",
    "--file",
    "-I",
    "--include-dir",
    "-o",
    "--old-file",
    "-W",
    "--what-if",
    "--eval",
    "--jobserver-auth",
}
_MAKE_NON_ENFORCING_OPTIONS = {
    "-i",
    "--ignore-errors",
    "-n",
    "--dry-run",
    "--just-print",
    "--recon",
    "-q",
    "--question",
    "-t",
    "--touch",
}
_SHELL_BOUNDARY = re.compile(r"^[;&|]+$")
_PIPELINE_ENFORCING_STAGE = re.compile(
    r"^(?:(?:python(?:\d+(?:\.\d+)?)?|bash|sh)\b[\s\S]*\b(?:gate|check|scan|validate)\b|"
    r"(?:pytest|ruff|mypy|trivy)\b)",
    re.IGNORECASE,
)
_MAKE_COMMAND_PREFIXES = {
    "!",
    "command",
    "do",
    "else",
    "env",
    "if",
    "sudo",
    "then",
    "until",
    "while",
}


@dataclass(frozen=True)
class Finding:
    repository: str
    kind: str
    target: str
    detail: str
    evidence: str

    def render(self) -> str:
        return f"{self.repository}: [{self.kind}] {self.target} - {self.detail}\n    {self.evidence}"


@dataclass(frozen=True)
class MakeTarget:
    prerequisites: tuple[str, ...]
    recipe: tuple[str, ...]


def _strip_shell_comments(command: str) -> str:
    """Remove unquoted shell comments without discarding later physical lines."""

    uncommented: list[str] = []
    quote: str | None = None
    escaped = False
    in_comment = False
    for index, character in enumerate(command):
        if in_comment:
            if character == "\n":
                uncommented.append(character)
                in_comment = False
            continue
        if escaped:
            uncommented.append(character)
            escaped = False
            continue
        if character == "\\":
            uncommented.append(character)
            escaped = True
            continue
        if character in {'"', "'"}:
            quote = None if quote == character else character if quote is None else quote
            uncommented.append(character)
            continue
        if (
            character == "#"
            and quote is None
            and (index == 0 or command[index - 1].isspace() or command[index - 1] in ";|&")
        ):
            in_comment = True
            continue
        uncommented.append(character)
    return "".join(uncommented)


def _make_invoked_targets(
    command: str, *, default_errexit: bool = False
) -> tuple[str, ...]:
    """Return targets from make invocations, skipping options and assignments.

    GNU Make accepts options before targets, so a textual ``make <word>`` regex interprets
    ``make --silent release-gate`` as a request for ``--silent`` and misses the gate. Parse each
    shell-bounded make invocation instead. Candidate words are still intersected with parsed
    Makefile targets by callers, which prevents command arguments from becoming graph nodes.
    """

    # Strip shell comments before tokenization.  A comment in a workflow command can mention a
    # gate without invoking it (``make ci # make release-gate manually``); crediting the text after
    # ``#`` would conceal a real orphan.  Quoted ``#`` and escaped ``\#`` remain command data.
    command = command.strip()
    uncommented = _strip_shell_comments(command)

    # Quoted prose such as ``echo "run make release-gate manually"`` is data, not a nested
    # invocation. Replace quoted segments before tokenization; make target names do not need quotes.
    unquoted: list[str] = []
    quote: str | None = None
    escaped = False
    for character in uncommented:
        if escaped:
            unquoted.append(" " if quote else character)
            escaped = False
        elif character == "\\":
            escaped = True
            unquoted.append(" " if quote else character)
        elif quote:
            if character == quote:
                quote = None
            unquoted.append(" ")
        elif character in {'"', "'"}:
            quote = character
            unquoted.append(" ")
        else:
            unquoted.append(character)
    sanitized = re.sub(r"(?m)(?<!\S)#.*$", "", "".join(unquoted))
    # GitHub's default Bash runner uses `-e`; a literal YAML line break therefore stops the step
    # after a failed gate. Represent those boundaries as `&&` while retaining explicit `;` as a
    # status-masking shell separator.
    sanitized = sanitized.replace("\n", " && " if default_errexit else ";")

    try:
        lexer = shlex.shlex(sanitized, posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True
        lexer.commenters = ""
        tokens = list(lexer)
    except ValueError:
        tokens = sanitized.split()

    invoked: list[str] = []
    for index, command_token in enumerate(tokens):
        normalized_command = command_token.lstrip("@+-")
        if normalized_command not in {
            "make",
            "$(MAKE)",
        } and not normalized_command.endswith("/make"):
            continue
        segment_start = index
        while segment_start > 0 and not _SHELL_BOUNDARY.match(
            tokens[segment_start - 1]
        ):
            segment_start -= 1
        prefix = [token.lstrip("@+-") for token in tokens[segment_start:index]]
        if any(
            token not in _MAKE_COMMAND_PREFIXES and not _MAKE_ASSIGNMENT.match(token)
            for token in prefix
        ):
            # `echo make release-gate` and step labels containing the word make are data, not
            # invocations. Only credit make at a shell command position (optionally after wrappers
            # such as `env`/`sudo` or environment assignments).
            continue
        pending_option: str | None = None
        options_ended = False
        candidates: list[str] = []
        uses_root_makefile = True
        non_enforcing = False
        boundary_index: int | None = None
        for token_index, token in enumerate(tokens[index + 1 :], start=index + 1):
            if _SHELL_BOUNDARY.match(token):
                boundary_index = token_index
                break
            if pending_option is not None:
                if pending_option in {"-C", "--directory"} and Path(token) != Path("."):
                    uses_root_makefile = False
                if pending_option in {"-f", "--file"} and Path(token) != Path(
                    "Makefile"
                ):
                    uses_root_makefile = False
                pending_option = None
                continue
            if not options_ended and token == "--":
                options_ended = True
                continue
            if not options_ended and token.startswith("-"):
                option_name = token.split("=", 1)[0]
                if token in _MAKE_NON_ENFORCING_OPTIONS:
                    non_enforcing = True
                option_value = token.split("=", 1)[1] if "=" in token else None
                if (
                    option_name in {"--directory", "--file"}
                    and option_value is not None
                ):
                    expected = (
                        Path(".") if option_name == "--directory" else Path("Makefile")
                    )
                    if Path(option_value) != expected:
                        uses_root_makefile = False
                elif token.startswith("-C") and token != "-C":
                    if Path(token[2:]) != Path("."):
                        uses_root_makefile = False
                elif token.startswith("-f") and token != "-f":
                    if Path(token[2:]) != Path("Makefile"):
                        uses_root_makefile = False
                if (
                    option_name in _MAKE_OPTIONS_REQUIRING_VALUES
                    and "=" not in token
                    and token == option_name
                ):
                    # Joined short forms such as ``-Csrc`` and ``-j4`` already carry the value.
                    pending_option = option_name
                continue
            if _MAKE_ASSIGNMENT.match(token):
                continue
            candidates.append(token)
        if boundary_index is not None:
            boundaries = [
                token for token in tokens[boundary_index:] if _SHELL_BOUNDARY.match(token)
            ]
            # A later fallback can mask the gate even if the first boundary is `&&`, as in
            # `make gate && report || true`, so inspect the complete remaining list.
            if "||" in boundaries or (
                ";" in boundaries and not ERREXIT_ENABLED.search(command)
            ) or ("|" in boundaries and not PIPEFAIL_ENABLED.search(command)):
                non_enforcing = True
        if "!" in prefix:
            non_enforcing = True
        if uses_root_makefile and not non_enforcing:
            invoked.extend(candidates)
    return tuple(invoked)


def _join_continuations(lines: list[str]) -> list[str]:
    """Fold backslash-continued recipe lines into one logical command.

    A valid gate written as `trivy image \\` / `--exit-code 1 app:ci` is a single command to the
    shell. Examining the first physical line alone reports it as unable to fail, which would make
    the audit punish a correct gate.
    """

    joined: list[str] = []
    buffer = ""
    for line in lines:
        stripped = line.rstrip("\n")
        if stripped.endswith("\\"):
            buffer += stripped[:-1].rstrip() + " "
            continue
        joined.append(buffer + stripped.strip())
        buffer = ""
    if buffer:
        joined.append(buffer.strip())
    return joined


def _join_makefile_declarations(lines: list[str]) -> list[str]:
    """Fold continued non-recipe declarations before parsing target prerequisites."""

    joined: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("\t") or not line.rstrip().endswith("\\"):
            joined.append(line)
            index += 1
            continue

        logical = line.rstrip()[:-1].rstrip()
        index += 1
        while index < len(lines):
            continuation = lines[index].strip()
            continued = continuation.endswith("\\")
            logical += " " + (continuation[:-1].rstrip() if continued else continuation)
            index += 1
            if not continued:
                break
        joined.append(logical)
    return joined


def parse_makefile(text: str) -> dict[str, MakeTarget]:
    """Parse target -> (prerequisites, recipe lines), with continuations folded.

    `.PHONY` is parsed like any other target, which matters: a name appearing *only* in `.PHONY`
    and its own definition is exactly the orphan signature.
    """

    targets: dict[str, tuple[list[str], list[str]]] = {}
    current: tuple[str, ...] = ()
    for line in _join_makefile_declarations(text.splitlines()):
        if line.startswith("\t"):
            for name in current:
                targets[name][1].append(line[1:])
            continue
        match = _TARGET.match(line)
        if match:
            current = tuple(match.group(1).split())
            for name in current:
                targets.setdefault(name, ([], []))
            # GNU Make allows an inline recipe after a semicolon: `security-gate: ; trivy ...`.
            # Treating the whole tail as prerequisites stores `;` and the command as prerequisite
            # names, leaves the recipe empty, and so never inspects the command - the target counts
            # as a gate and looks reachable while its non-failing command goes unexamined.
            prerequisites, separator, inline_recipe = match.group(2).partition(";")
            for name in current:
                targets[name][0].extend(prerequisites.split())
                if separator and inline_recipe.strip():
                    targets[name][1].append(inline_recipe.strip())
        elif not line.strip():
            current = ()
    return {
        name: MakeTarget(tuple(prerequisites), tuple(_join_continuations(recipe)))
        for name, (prerequisites, recipe) in targets.items()
    }


def reachable_targets(
    targets: dict[str, MakeTarget], roots: tuple[str, ...]
) -> set[str]:
    """Every target reachable from `roots` through prerequisites and recursive make calls."""

    seen: set[str] = set()
    stack = [root for root in roots if root in targets]
    while stack:
        name = stack.pop()
        if name in seen:
            continue
        seen.add(name)
        target = targets[name]
        stack.extend(p for p in target.prerequisites if p in targets)
        for line in target.recipe:
            stack.extend(
                target for target in _make_invoked_targets(line) if target in targets
            )
    return seen


def blocking_workflow_invocations(
    workflow_text: str, targets: dict[str, MakeTarget]
) -> set[str]:
    """Targets invoked by a workflow step whose failure actually fails the job.

    A raw text match over the whole file counts a target named in a comment, or in a step carrying
    `continue-on-error: true`, as reachable from a blocking lane. Neither enforces anything, so
    both would hide a dead gate behind an invocation that cannot fail the run.
    """

    try:
        document = yaml.safe_load(workflow_text)
    except yaml.YAMLError:
        return set()

    if isinstance(document, list):
        jobs: dict[str, object] = {"standalone": {"steps": document}}
    elif isinstance(document, dict) and isinstance(document.get("jobs"), dict):
        jobs = document["jobs"]
    else:
        return set()

    workflow_defaults = document.get("defaults", {}) if isinstance(document, dict) else {}
    workflow_run_defaults = (
        workflow_defaults.get("run", {})
        if isinstance(workflow_defaults, dict)
        else {}
    )
    workflow_directory = (
        workflow_run_defaults.get("working-directory")
        if isinstance(workflow_run_defaults, dict)
        else None
    )

    def is_root_directory(value: object) -> bool:
        return value is None or str(value).strip() in {"", ".", "./"}

    invoked: set[str] = set()
    for job in jobs.values():
        if (
            not isinstance(job, dict)
            or job.get("continue-on-error") is True
            or job.get("if") is False
        ):
            continue
        job_defaults = job.get("defaults", {})
        job_run_defaults = (
            job_defaults.get("run", {}) if isinstance(job_defaults, dict) else {}
        )
        job_directory = (
            job_run_defaults.get("working-directory")
            if isinstance(job_run_defaults, dict)
            else workflow_directory
        )
        steps = job.get("steps")
        if not isinstance(steps, list):
            continue
        for step in steps:
            if (
                not isinstance(step, dict)
                or step.get("continue-on-error") is True
                or step.get("if") is False
            ):
                continue
            command = step.get("run")
            working_directory = step.get("working-directory", job_directory)
            if isinstance(command, str) and is_root_directory(working_directory):
                invoked.update(_make_invoked_targets(command, default_errexit=True))
    return invoked & set(targets)


def blocking_roots_for(
    targets: dict[str, MakeTarget], workflow_invoked: set[str]
) -> tuple[str, ...]:
    """Seed reachability from `lint` only when something actually invokes it.

    Treating `lint` as a root unconditionally marks every gate hanging off it as reachable, even in
    a repository where nothing runs `lint` at all - which is precisely the orphan case.
    """

    roots = [root for root in CANONICAL_ROOTS if root in targets]
    canonical_reach = reachable_targets(targets, tuple(roots))
    for root in CONDITIONAL_ROOTS:
        if root in targets and (root in canonical_reach or root in workflow_invoked):
            roots.append(root)
    return tuple(roots)


def _is_comment_or_noise(recipe_line: str) -> bool:
    stripped = _RECIPE_PREFIXES.sub("", recipe_line.strip()).strip()
    if not stripped or stripped.startswith("#"):
        return True
    commands = [
        segment.strip()
        for segment in re.split(r"&&|\|\||(?<!\|)\|(?!\|)|;", stripped)
        if segment.strip()
    ]
    return bool(commands) and all(
        re.match(r"^(?:echo|mkdir|true|:|exit\s+0)\b", segment)
        for segment in commands
    )


def _final_command(command: str) -> str:
    """The command whose exit status make actually sees.

    Make reports the status of the *last* command on the line, so `cleanup || true; python gate.py`
    still returns the gate's verdict, while `python gate.py; echo done` does not. Judging the whole
    line would flag the first as unable to fail, which punishes a correct recipe.
    """

    segments: list[str] = []
    current: list[str] = []
    quote: str | None = None
    escaped = False
    for character in _strip_shell_comments(command):
        if escaped:
            current.append(character)
            escaped = False
        elif character == "\\":
            current.append(character)
            escaped = True
        elif character in {'"', "'"}:
            quote = None if quote == character else character if quote is None else quote
            current.append(character)
        elif character in ";\n" and quote is None:
            segment = "".join(current).strip()
            if segment:
                segments.append(segment)
            current = []
        else:
            current.append(character)
    segment = "".join(current).strip()
    if segment:
        segments.append(segment)
    return segments[-1] if segments else ""


def _cannot_fail_reason(recipe_line: str) -> str | None:
    stripped = recipe_line.strip()
    if _IGNORES_ERRORS.match(stripped):
        return "a make `-` prefix tells make to ignore this command's failure"

    command = _strip_shell_comments(_RECIPE_PREFIXES.sub("", stripped)).strip()
    final = _final_command(command)
    if not final:
        return None

    if ALWAYS_SUCCEEDS.match(final):
        return "the last command on this line always succeeds, so it supplies the exit status"

    # A pipeline reports its last stage's status. Without pipefail, any non-enforcing consumer can
    # mask an earlier verdict (`python gate.py | sed ...`), not only common `tee`/`cat` sinks.
    if re.search(r"(?<!\|)\|(?!\|)", final) and not PIPEFAIL_ENABLED.search(command):
        pipeline_tail = re.split(r"(?<!\|)\|(?!\|)", final)[-1].strip()
        if not _PIPELINE_ENFORCING_STAGE.match(pipeline_tail):
            return "the pipeline's status comes from a reporting sink, not the earlier gate"

    for pattern, detail in CANNOT_FAIL_PATTERNS:
        if re.search(pattern, final):
            return detail
    return None


def _target_can_fail(
    name: str,
    targets: dict[str, MakeTarget],
    memo: dict[str, bool],
    visiting: set[str] | None = None,
    *,
    oneshell: bool = False,
) -> bool:
    """Whether a target has at least one failure-propagating prerequisite or recipe.

    Make stops when any prerequisite or recipe line fails. Capability is therefore a target-level
    property: a reporting line cannot make a valid failing prerequisite inert, and one valid gate
    command is enough even when a later line writes best-effort evidence.
    """

    if name in memo:
        return memo[name]
    active = set() if visiting is None else visiting
    if name in active:
        return False
    active.add(name)
    target = targets[name]

    if any(
        prerequisite in targets
        and _target_can_fail(prerequisite, targets, memo, active, oneshell=oneshell)
        for prerequisite in target.prerequisites
    ):
        active.remove(name)
        memo[name] = True
        return True

    if oneshell:
        combined = "\n".join(
            _RECIPE_PREFIXES.sub("", recipe_line.strip())
            for recipe_line in target.recipe
            if recipe_line.strip()
        )
        if ERREXIT_ENABLED.search(combined):
            can_fail = any(
                not _is_comment_or_noise(recipe_line)
                and _cannot_fail_reason(recipe_line) is None
                for recipe_line in target.recipe
            )
        else:
            can_fail = bool(combined) and _cannot_fail_reason(combined) is None
    else:
        can_fail = any(
            not _is_comment_or_noise(recipe_line)
            and _cannot_fail_reason(recipe_line) is None
            for recipe_line in target.recipe
        )
    if can_fail:
        active.remove(name)
        memo[name] = True
        return True

    active.remove(name)
    memo[name] = False
    return False


def _incapable_target_evidence(
    target: MakeTarget, *, oneshell: bool = False
) -> tuple[str, str]:
    """Summarize why no recipe owned by a target can supply an enforcement verdict."""

    reasons: list[str] = []
    evidence: list[str] = []
    recipe_lines = (("\n".join(target.recipe),) if oneshell else target.recipe)
    for recipe_line in recipe_lines:
        if _is_comment_or_noise(recipe_line):
            if recipe_line.strip():
                evidence.append(recipe_line.strip())
            continue
        reason = _cannot_fail_reason(recipe_line)
        if reason is not None:
            reasons.append(reason)
            evidence.append(recipe_line.strip())

    if not reasons:
        reasons.append("the target contains only comments, setup, or no-op recipes")
    detail = (
        "no prerequisite or recipe propagates a non-zero enforcement verdict; "
        + "; ".join(dict.fromkeys(reasons))
    )
    rendered_evidence = " | ".join(evidence)[:320] or "no executable enforcement recipe"
    return detail, rendered_evidence


def audit_repository(repository: str, root: Path) -> tuple[list[Finding], int]:
    """Return (findings, number of gate targets inspected)."""

    makefile = root / "Makefile"
    if not makefile.is_file():
        return [], 0

    targets = parse_makefile(makefile.read_text(encoding="utf-8", errors="ignore"))
    oneshell = ".ONESHELL" in targets
    workflow_dir = root / ".github" / "workflows"
    from_workflows: set[str] = set()
    if workflow_dir.is_dir():
        for path in sorted(workflow_dir.glob("*.y*ml")):
            from_workflows.update(
                blocking_workflow_invocations(
                    path.read_text(encoding="utf-8", errors="ignore"), targets
                )
            )
    roots = blocking_roots_for(targets, from_workflows)
    blocking = reachable_targets(targets, tuple(set(roots) | from_workflows))

    # Every declared gate is audited. That includes prerequisite-only aggregates and completely
    # empty declarations: filtering on content lets an inert `security-gate:` disappear whenever
    # another gate keeps the repository-level count non-zero.
    gates = sorted(
        name for name in targets if name.endswith(GATE_SUFFIXES) and name != ".PHONY"
    )

    findings: list[Finding] = []

    for gate in gates:
        if gate not in blocking:
            findings.append(
                Finding(
                    repository=repository,
                    kind="ORPHAN",
                    target=gate,
                    detail=(
                        "declared as a gate but reachable from no blocking lane and invoked by no "
                        "workflow step that can fail the job, so it never runs"
                    ),
                    evidence=f"Makefile defines {gate}; no path from {list(roots)} or .github/workflows",
                )
            )

    capability_memo: dict[str, bool] = {}
    for name in sorted(blocking):
        target = targets[name]
        direct_cannot_fail = any(
            not _is_comment_or_noise(recipe_line)
            and _cannot_fail_reason(recipe_line) is not None
            for recipe_line in target.recipe
        )
        # Declared gates must own or inherit a verdict. Also retain the original audit's ability to
        # catch report-named blocking targets such as `container-vulnerability-report` when their
        # scanner is explicitly configured never to fail.
        should_evaluate = name.endswith(GATE_SUFFIXES) or direct_cannot_fail
        if should_evaluate and not _target_can_fail(
            name, targets, capability_memo, oneshell=oneshell
        ):
            detail, evidence = _incapable_target_evidence(target, oneshell=oneshell)
            findings.append(
                Finding(
                    repository=repository,
                    kind="CANNOT_FAIL",
                    target=name,
                    detail=detail,
                    evidence=evidence,
                )
            )

    return findings, len(gates)


def load_fleet(repos_json: Path) -> list[tuple[str, Path]]:
    entries = json.loads(repos_json.read_text(encoding="utf-8"))
    return [
        (entry["name"], Path(entry["path"])) for entry in entries if entry.get("path")
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit whether quality gates can actually fail"
    )
    parser.add_argument("--repo-path", action="append", dest="repo_paths", default=[])
    parser.add_argument("--repos-json", type=Path, default=None)
    parser.add_argument(
        "--fail-on-findings",
        action="store_true",
        help="Exit non-zero when any gate-liveness finding is present",
    )
    args = parser.parse_args(argv)

    pairs: list[tuple[str, Path]] = [(Path(p).name, Path(p)) for p in args.repo_paths]
    if args.repos_json is not None:
        pairs.extend(load_fleet(args.repos_json))
    if not pairs:
        print(
            "No repositories supplied; pass --repo-path or --repos-json.",
            file=sys.stderr,
        )
        return 1

    findings: list[Finding] = []
    uninspectable: list[str] = []
    gateless: list[str] = []
    inspected_gates = 0
    for name, path in pairs:
        if not (path / "Makefile").is_file():
            uninspectable.append(f"{name}: no Makefile at {path}")
            continue
        repository_findings, gate_count = audit_repository(name, path)
        if gate_count == 0:
            gateless.append(name)
        inspected_gates += gate_count
        findings.extend(repository_findings)

    for finding in findings:
        print(finding.render())

    # Every requested repository must have been inspected and must have contributed at least one
    # gate. Skipping a missing path, or letting one repository's gates stand in for another's
    # silence, is the same fail-open the audit exists to report.
    if uninspectable or gateless:
        if uninspectable:
            print(
                f"Repositories that could not be inspected: {uninspectable}",
                file=sys.stderr,
            )
        if gateless:
            print(
                f"Repositories declaring no gate targets: {gateless}", file=sys.stderr
            )
        print("A gate that inspected nothing must fail.", file=sys.stderr)
        return 1

    orphans = sum(1 for f in findings if f.kind == "ORPHAN")
    cannot_fail = sum(1 for f in findings if f.kind == "CANNOT_FAIL")
    print(
        f"\nInspected {inspected_gates} gate targets across {len(pairs)} repositories: "
        f"{orphans} orphaned, {cannot_fail} unable to fail."
    )

    if findings and args.fail_on_findings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
