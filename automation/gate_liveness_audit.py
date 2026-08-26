"""Audit whether a repository's quality gates can actually fail.

The estate has a well-developed answer to *which* signals deserve a gate
(`lotus-ci-enforcement-governance`), and no answer at all to whether a gate that exists is alive.
A gate is alive only if all four hold:

1. **Reachable** - some blocking lane invokes it. A `*-gate` target nothing calls is dead
   governance: a reader of the Makefile concludes the rule is enforced, and it never runs.
2. **Capable of failing** - the command it runs returns non-zero on a finding. `radon cc` has no
   failing exit code in any mode, so a `complexity-gate` built on it reports complexity and passes
   unconditionally.
3. **Fail-closed on empty input** - a gate that inspected zero files must fail. Silence is never a
   pass.
4. **Observed to have run** - a correct blocking gate on a trigger that never fires has produced no
   verdict.

This script detects rules 1 and 2, which are decidable from the Makefile and the workflows. Rules 3
and 4 are deliberately **not** implemented: rule 3 needs the gate executed against an empty input,
and rule 4 needs GitHub run history. Both stay review obligations, recorded in the Gate Liveness
Standard in `lotus-ci-enforcement-governance`. Claiming to cover them would reproduce the defect
this tool exists to find.

This script is itself a gate, so it fails when it inspected nothing - per repository, not only in
aggregate. A fleet run where one path is missing or one repository declares no gates is a run that
did not inspect what it was asked to, and reporting that as clean would be the exact class of
defect the audit reports on others.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

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
    (r"\|\|\s*true\s*$", "|| true discards the exit status of the final command"),
    (r";\s*true\s*$", "; true discards the exit status"),
    (r"\|\|\s*exit\s+0\s*$", "|| exit 0 discards the exit status of the final command"),
)

# Commands that always succeed. When one of these is the *last* command on a recipe line it
# supplies the line's exit status, so whatever ran before it cannot fail the gate.
ALWAYS_SUCCEEDS = re.compile(r"^(?:echo|true|:|exit\s+0)\b")

# Make recipe prefixes. `-` ignores the command's failure; `@` only silences echo; `+` forces
# execution. They combine in any order, so `@-python g.py` ignores errors just as `-python g.py`.
_RECIPE_PREFIXES = re.compile(r"^[@+-]+")
_IGNORES_ERRORS = re.compile(r"^[@+]*-")

_TARGET = re.compile(r"^([A-Za-z0-9_.-]+):\s*(.*)$")
_SUBMAKE = re.compile(r"(?:\$\(MAKE\)|\bmake)\s+([A-Za-z0-9_.-]+)")
_RUN_STEP_MAKE = re.compile(r"\bmake\s+([A-Za-z0-9_.-]+)")


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


def parse_makefile(text: str) -> dict[str, MakeTarget]:
    """Parse target -> (prerequisites, recipe lines), with continuations folded.

    `.PHONY` is parsed like any other target, which matters: a name appearing *only* in `.PHONY`
    and its own definition is exactly the orphan signature.
    """

    targets: dict[str, tuple[list[str], list[str]]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("\t"):
            if current is not None:
                targets[current][1].append(line[1:])
            continue
        match = _TARGET.match(line)
        if match:
            current = match.group(1)
            targets.setdefault(current, ([], []))
            targets[current][0].extend(match.group(2).split())
        elif not line.strip():
            current = None
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
                m.group(1) for m in _SUBMAKE.finditer(line) if m.group(1) in targets
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

    invoked: set[str] = set()
    for block in re.split(r"\n(?=\s*- )", workflow_text):
        lines = [
            line for line in block.splitlines() if not line.strip().startswith("#")
        ]
        cleaned = "\n".join(lines)
        if re.search(r"continue-on-error:\s*true", cleaned):
            continue
        invoked.update(m.group(1) for m in _RUN_STEP_MAKE.finditer(cleaned))
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
    return (
        not stripped
        or stripped.startswith("#")
        or stripped.startswith("echo")
        or stripped.startswith("mkdir")
    )


def _final_command(command: str) -> str:
    """The command whose exit status make actually sees.

    Make reports the status of the *last* command on the line, so `cleanup || true; python gate.py`
    still returns the gate's verdict, while `python gate.py; echo done` does not. Judging the whole
    line would flag the first as unable to fail, which punishes a correct recipe.
    """

    segments = [segment.strip() for segment in command.split(";") if segment.strip()]
    return segments[-1] if segments else ""


def _cannot_fail_reason(recipe_line: str) -> str | None:
    stripped = recipe_line.strip()
    if _IGNORES_ERRORS.match(stripped):
        return "a make `-` prefix tells make to ignore this command's failure"

    command = _RECIPE_PREFIXES.sub("", stripped).strip()
    final = _final_command(command)
    if not final:
        return None

    if ALWAYS_SUCCEEDS.match(final):
        return "the last command on this line always succeeds, so it supplies the exit status"

    # A pipeline reports the last stage's status, not the gate's. `||` is not a pipe.
    if re.search(r"(?<!\|)\|(?!\|)", final):
        return "the pipeline's status is the last stage's, not the gate's"

    for pattern, detail in CANNOT_FAIL_PATTERNS:
        if re.search(pattern, final):
            return detail
    return None


def audit_repository(repository: str, root: Path) -> tuple[list[Finding], int]:
    """Return (findings, number of gate targets inspected)."""

    makefile = root / "Makefile"
    if not makefile.is_file():
        return [], 0

    targets = parse_makefile(makefile.read_text(encoding="utf-8", errors="ignore"))
    workflow_dir = root / ".github" / "workflows"
    workflow_text = ""
    if workflow_dir.is_dir():
        workflow_text = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in sorted(workflow_dir.glob("*.y*ml"))
        )

    from_workflows = blocking_workflow_invocations(workflow_text, targets)
    roots = blocking_roots_for(targets, from_workflows)
    blocking = reachable_targets(targets, tuple(set(roots) | from_workflows))

    # A gate that delegates entirely through prerequisites - `orphan-gate: scan` with no recipe of
    # its own - is still a gate. Filtering on a non-empty recipe dropped it from both the count and
    # the orphan check.
    gates = sorted(
        name
        for name in targets
        if name.endswith(GATE_SUFFIXES)
        and name != ".PHONY"
        and (targets[name].recipe or targets[name].prerequisites)
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

    for name in sorted(blocking):
        for recipe_line in targets[name].recipe:
            if _is_comment_or_noise(recipe_line):
                continue
            reason = _cannot_fail_reason(recipe_line)
            if reason is not None:
                findings.append(
                    Finding(
                        repository=repository,
                        kind="CANNOT_FAIL",
                        target=name,
                        detail=reason,
                        evidence=recipe_line.strip()[:160],
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
