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
and 4 are deliberately **not** implemented here: rule 3 needs the gate executed against an empty
input, and rule 4 needs GitHub run history. Both stay review obligations, recorded in the Gate
Liveness Standard in `lotus-ci-enforcement-governance`. Claiming to cover them would reproduce the
defect this tool exists to find.

Measured instances that motivated each rule are recorded in `lotus-platform#595`, `#713`, `#728`,
`#734`, `#737`, `lotus-performance#477`, `lotus-risk#216`, `#225` and `#232`.

This script is itself a gate, so it fails when it inspected nothing.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Targets that a blocking lane is expected to be rooted at. A gate reachable from none of these and
# from no workflow is orphaned.
BLOCKING_ROOTS = ("ci", "check", "check-all", "lint")

# Suffixes that declare intent to block. A target named `*-gate` or `*-guard` is a promise.
GATE_SUFFIXES = ("-gate", "-guard")

# Report-only invocations. Each of these returns 0 whatever it finds, so a target built on one
# cannot fail no matter what the tree contains.
CANNOT_FAIL_PATTERNS: tuple[tuple[str, str], ...] = (
    (
        r"\bradon\s+(?:cc|mi|raw|hal)\b",
        "radon has no failing exit code in any mode - it prints and returns 0",
    ),
    (
        r"\btrivy\b(?![^\n]*--exit-code[= ]1)",
        "trivy without --exit-code 1 reports findings and returns 0",
    ),
    (r"--exit-code[= ]0\b", "--exit-code 0 explicitly discards the verdict"),
    (r"\|\|\s*true\b", "|| true discards the exit status"),
    (r";\s*true\s*$", "; true discards the exit status"),
    (r"\|\|\s*exit\s+0\b", "|| exit 0 discards the exit status"),
)

# A make recipe line starting with `-` tells make to ignore the command's failure.
MAKE_IGNORE_ERRORS = re.compile(r"^\t-\s*\S")

_TARGET = re.compile(r"^([A-Za-z0-9_.-]+):\s*(.*)$")
_SUBMAKE = re.compile(r"(?:\$\(MAKE\)|\bmake)\s+([A-Za-z0-9_.-]+)")
_WORKFLOW_MAKE = re.compile(r"\bmake\s+([A-Za-z0-9_.-]+)")


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


def parse_makefile(text: str) -> dict[str, MakeTarget]:
    """Parse target -> (prerequisites, recipe lines).

    Deliberately simple: the estate's Makefiles are plain. `.PHONY` is parsed like any other
    target, which matters - a name appearing *only* in `.PHONY` and its own definition is exactly
    the orphan signature.
    """

    targets: dict[str, tuple[list[str], list[str]]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("\t"):
            if current is not None:
                targets[current][1].append(line)
            continue
        match = _TARGET.match(line)
        if match:
            current = match.group(1)
            targets.setdefault(current, ([], []))
            targets[current][0].extend(match.group(2).split())
        elif not line.strip():
            current = None
    return {
        name: MakeTarget(tuple(prerequisites), tuple(recipe))
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


def workflow_invoked_targets(
    workflow_text: str, targets: dict[str, MakeTarget]
) -> set[str]:
    return {m.group(1) for m in _WORKFLOW_MAKE.finditer(workflow_text)} & set(targets)


def _is_comment_or_noise(recipe_line: str) -> bool:
    stripped = recipe_line.strip().lstrip("@-").strip()
    return (
        not stripped
        or stripped.startswith("#")
        or stripped.startswith("echo")
        or stripped.startswith("mkdir")
    )


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

    from_lanes = reachable_targets(targets, BLOCKING_ROOTS)
    from_workflows = workflow_invoked_targets(workflow_text, targets)
    blocking = reachable_targets(targets, tuple(from_lanes | from_workflows))

    gates = sorted(
        name
        for name in targets
        if name.endswith(GATE_SUFFIXES) and name != ".PHONY" and targets[name].recipe
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
                        "workflow, so it never runs"
                    ),
                    evidence=f"Makefile defines {gate}; no path from {list(BLOCKING_ROOTS)} or .github/workflows",
                )
            )

    for name in sorted(blocking):
        for recipe_line in targets[name].recipe:
            if _is_comment_or_noise(recipe_line):
                continue
            if MAKE_IGNORE_ERRORS.match(recipe_line):
                findings.append(
                    Finding(
                        repository=repository,
                        kind="CANNOT_FAIL",
                        target=name,
                        detail="make '-' prefix tells make to ignore this command's failure",
                        evidence=recipe_line.strip()[:160],
                    )
                )
                continue
            for pattern, detail in CANNOT_FAIL_PATTERNS:
                if re.search(pattern, recipe_line):
                    findings.append(
                        Finding(
                            repository=repository,
                            kind="CANNOT_FAIL",
                            target=name,
                            detail=detail,
                            evidence=recipe_line.strip()[:160],
                        )
                    )
                    break

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
    inspected_repositories = 0
    inspected_gates = 0
    for name, path in pairs:
        if not (path / "Makefile").is_file():
            continue
        repository_findings, gate_count = audit_repository(name, path)
        inspected_repositories += 1
        inspected_gates += gate_count
        findings.extend(repository_findings)

    # This script is a gate, so it obeys the rule it enforces: having inspected nothing is a
    # failure, not a pass.
    if inspected_repositories == 0 or inspected_gates == 0:
        print(
            f"Gate liveness audit inspected {inspected_repositories} repositories and "
            f"{inspected_gates} gate targets. A gate that inspected nothing must fail.",
            file=sys.stderr,
        )
        return 1

    for finding in findings:
        print(finding.render())

    orphans = sum(1 for f in findings if f.kind == "ORPHAN")
    cannot_fail = sum(1 for f in findings if f.kind == "CANNOT_FAIL")
    print(
        f"\nInspected {inspected_gates} gate targets across {inspected_repositories} repositories: "
        f"{orphans} orphaned, {cannot_fail} unable to fail."
    )

    if findings and args.fail_on_findings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
