from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
QUALITY_DIR = ROOT / "quality"

SOURCE_ROOTS = (
    "automation",
    "codex",
    "context",
    "docs",
    "platform-contracts",
    "platform-stack",
    "platform-standards",
    "rfcs",
    "tests",
    "wiki",
)

TEXT_SUFFIXES = {
    ".cfg",
    ".css",
    ".env",
    ".html",
    ".ini",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

EXCLUDED_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    ".venv-platform-automation",
    "__pycache__",
    "generated",
    "output",
}

QUALITY_DOCS = {
    "architecture_rules.md": """# Architecture Rules

`lotus-platform` is a platform governance and automation backend. Its executable backend surface is
Python and PowerShell automation, validators, contracts, and CI lane entrypoints rather than a
business-domain HTTP API.

Rules for this refactor:

1. validators and generators should keep parsing, policy, rendering, and file-writing concerns explicit,
2. reusable policy should live in platform contracts, standards, or shared automation modules,
3. generated artifacts must not become hand-edited source truth,
4. repo-check entrypoints must stay aligned with GitHub workflow lanes,
5. broad framework or runtime dependencies require a documented enterprise-readiness reason.
""",
    "api_governance_rules.md": """# API Governance Rules

`lotus-platform` does not own a business-domain API. API governance work in this repository applies
to generated service scaffolds, OpenAPI validators, vocabulary contracts, gateway-facing governance
artifacts, and cross-repository certification evidence.

Rules for this refactor:

1. platform OpenAPI checks should remain reusable by service repositories,
2. API vocabulary and no-alias truth should live in platform contracts and generated inventories,
3. scaffolds must create Swagger/OpenAPI documentation that is useful by default,
4. platform docs must not claim implementation-backed APIs owned by another repository.
""",
    "ci_quality_gates.md": """# CI Quality Gates

The enterprise refactor starts with report-only quality measurement. Gates should become blocking
only after the signal is deterministic, low-noise, locally runnable, and tied to a clear engineering
failure mode.

Initial gate posture:

1. `automation/generate_enterprise_backend_quality_baseline.py --check` is wired into
   `automation/Invoke-PlatformRepoChecks.ps1` to keep the quality reporting surface present,
2. baseline metrics remain report-only while the refactor identifies stable thresholds,
3. future blocking gates should prefer architecture-boundary drift, first-party security findings,
   OpenAPI/vocabulary drift, duplicate implementation hotspots, and unsafe production patterns.
""",
    "security_findings.md": """# Security Findings

This file tracks security findings discovered during the enterprise backend refactor.

Current baseline posture:

1. no new vulnerability scanner dependency is introduced in the baseline slice,
2. first-party secret keyword scanning is measured by the baseline generator as a planning signal,
3. dependency vulnerability scanning remains a follow-up gate until the repository dependency model
   is expanded beyond the existing platform automation lock file.
""",
    "refactor_decisions.md": """# Refactor Decisions

## Baseline Slice

Decision: start with a stdlib-only platform quality baseline generator instead of adding Radon,
Vulture, Bandit, pip-audit, or OpenAPI lint dependencies immediately.

Reason: `lotus-platform` currently uses a locked platform automation runtime with only `pytest`,
`requests`, and `PyYAML`. The first slice must establish measured baseline evidence without
expanding the dependency surface before scanner policy, false positives, and lane placement are
understood.
""",
}
FRESHNESS_METRICS = {
    "code_size.source_file_count": ("code_size", "source_file_count"),
    "code_size.python_file_count": ("code_size", "python_file_count"),
    "function_hotspots.python_function_count": (
        "function_hotspots",
        "python_function_count",
    ),
    "function_hotspots.max_complexity": ("function_hotspots", "max_complexity"),
    "function_hotspots.max_function_lines": ("function_hotspots", "max_function_lines"),
    "tests.collected_tests": ("tests", "collected_tests"),
}


@dataclass(frozen=True)
class FileMetric:
    path: str
    suffix: str
    lines: int


@dataclass(frozen=True)
class FunctionMetric:
    path: str
    name: str
    line: int
    end_line: int
    lines: int
    complexity: int


class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.score = 1

    def visit_If(self, node: ast.If) -> None:  # noqa: N802
        self.score += 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:  # noqa: N802
        self.score += 1
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:  # noqa: N802
        self.score += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:  # noqa: N802
        self.score += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:  # noqa: N802
        self.score += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:  # noqa: N802
        self.score += max(0, len(node.values) - 1)
        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> None:  # noqa: N802
        self.score += 1
        self.generic_visit(node)


def _is_source_file(path: Path) -> bool:
    if any(part in EXCLUDED_PARTS for part in path.parts):
        return False
    return path.is_file() and path.suffix.lower() in TEXT_SUFFIXES


def _iter_source_files() -> Iterable[Path]:
    for root_name in SOURCE_ROOTS:
        root = ROOT / root_name
        if root.exists():
            yield from (path for path in root.rglob("*") if _is_source_file(path))


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def _line_count(text: str) -> int:
    return 0 if text == "" else text.count("\n") + (0 if text.endswith("\n") else 1)


def collect_file_metrics(files: Iterable[Path]) -> list[FileMetric]:
    metrics: list[FileMetric] = []
    for path in files:
        metrics.append(
            FileMetric(
                path=path.relative_to(ROOT).as_posix(),
                suffix=path.suffix.lower(),
                lines=_line_count(_read_text(path)),
            )
        )
    return sorted(metrics, key=lambda metric: (-metric.lines, metric.path))


def collect_python_function_metrics(files: Iterable[Path]) -> list[FunctionMetric]:
    metrics: list[FunctionMetric] = []
    for path in files:
        if path.suffix.lower() != ".py":
            continue
        try:
            tree = ast.parse(_read_text(path), filename=str(path))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            visitor = ComplexityVisitor()
            visitor.visit(node)
            end_line = getattr(node, "end_lineno", node.lineno)
            metrics.append(
                FunctionMetric(
                    path=path.relative_to(ROOT).as_posix(),
                    name=node.name,
                    line=node.lineno,
                    end_line=end_line,
                    lines=end_line - node.lineno + 1,
                    complexity=visitor.score,
                )
            )
    return sorted(
        metrics,
        key=lambda metric: (
            -metric.complexity,
            -metric.lines,
            metric.path,
            metric.name,
        ),
    )


def _run_command(args: list[str]) -> dict[str, object]:
    try:
        result = subprocess.run(
            args,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=120,
            check=False,
        )
    except FileNotFoundError:
        return {
            "available": False,
            "command": args,
            "returncode": None,
            "summary": "tool not installed",
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "available": True,
            "command": args,
            "returncode": None,
            "summary": f"timed out after {exc.timeout} seconds",
        }

    output_lines = [line for line in result.stdout.splitlines() if line.strip()]
    return {
        "available": True,
        "command": args,
        "returncode": result.returncode,
        "summary": output_lines[-1] if output_lines else "no output",
    }


def _count_pytest_tests() -> dict[str, object]:
    result = _run_command(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "tests/unit"]
    )
    summary = str(result["summary"])
    collected = 0
    for token in summary.split():
        if token.isdigit():
            collected = int(token)
            break
    result["collected_tests"] = collected
    return result


def _scan_secret_keyword_candidates(files: Iterable[Path]) -> list[dict[str, object]]:
    sensitive_tokens = (
        "password",
        "secret",
        "token",
        "credential",
        "api_key",
        "private_key",
    )
    candidates: list[dict[str, object]] = []
    for path in files:
        if path.suffix.lower() not in {
            ".py",
            ".ps1",
            ".yml",
            ".yaml",
            ".json",
            ".md",
            ".txt",
        }:
            continue
        for line_number, line in enumerate(_read_text(path).splitlines(), start=1):
            normalized = line.lower()
            if any(token in normalized for token in sensitive_tokens):
                candidates.append(
                    {
                        "path": path.relative_to(ROOT).as_posix(),
                        "line": line_number,
                        "signal": "sensitive-keyword-review",
                    }
                )
    return candidates[:50]


def build_baseline() -> dict[str, object]:
    files = list(_iter_source_files())
    file_metrics = collect_file_metrics(files)
    function_metrics = collect_python_function_metrics(files)
    suffix_counts = Counter(metric.suffix for metric in file_metrics)

    total_lines = sum(metric.lines for metric in file_metrics)
    python_files = [metric for metric in file_metrics if metric.suffix == ".py"]
    powershell_files = [metric for metric in file_metrics if metric.suffix == ".ps1"]
    docs_files = [metric for metric in file_metrics if metric.suffix == ".md"]
    complexity_scores = [metric.complexity for metric in function_metrics]
    largest_function_lines = [metric.lines for metric in function_metrics]

    return {
        "generated_at_utc": datetime.now(UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "repository": "lotus-platform",
        "scope": {
            "included_roots": list(SOURCE_ROOTS),
            "excluded_parts": sorted(EXCLUDED_PARTS),
            "note": "Generated and output directories are excluded because they are derived evidence, not source truth.",
        },
        "code_size": {
            "source_file_count": len(file_metrics),
            "total_source_lines": total_lines,
            "python_file_count": len(python_files),
            "powershell_file_count": len(powershell_files),
            "markdown_file_count": len(docs_files),
            "suffix_counts": dict(sorted(suffix_counts.items())),
        },
        "largest_files": [metric.__dict__ for metric in file_metrics[:20]],
        "function_hotspots": {
            "python_function_count": len(function_metrics),
            "max_complexity": max(complexity_scores, default=0),
            "max_function_lines": max(largest_function_lines, default=0),
            "largest_functions": [
                metric.__dict__
                for metric in sorted(
                    function_metrics, key=lambda item: (-item.lines, item.path)
                )[:20]
            ],
            "highest_complexity_functions": [
                metric.__dict__ for metric in function_metrics[:20]
            ],
        },
        "quality_tooling": {
            "ruff": _run_command(["ruff", "--version"]),
            "mypy": _run_command(["mypy", "--version"]),
            "bandit": _run_command(["bandit", "--version"]),
            "pip_audit": _run_command(["pip-audit", "--version"]),
        },
        "tests": _count_pytest_tests(),
        "security": {
            "secret_keyword_review_candidates_sample": _scan_secret_keyword_candidates(
                files
            ),
            "candidate_sample_limit": 50,
            "note": "Keyword matches are planning signals and require human review before being treated as findings.",
        },
        "openapi": {
            "platform_business_api_owned": False,
            "note": "lotus-platform governs OpenAPI scaffolds and validators but does not own a business-domain API.",
        },
        "architecture": {
            "boundary_gate_status": "report-only",
            "note": "Initial baseline records hotspots before introducing import-boundary enforcement.",
        },
        "documentation": {
            "quality_docs_required": sorted(QUALITY_DOCS),
            "baseline_report": "quality/baseline_report.md",
            "scorecard": "quality/quality_scorecard.md",
            "health_report": "quality/refactor_health_report.md",
        },
    }


def _markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    rendered = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        rendered.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(rendered)


def render_baseline_report(baseline: dict[str, object]) -> str:
    code_size = baseline["code_size"]
    function_hotspots = baseline["function_hotspots"]
    tests = baseline["tests"]
    security = baseline["security"]

    largest_file_rows = [
        [item["path"], item["lines"], item["suffix"]]
        for item in baseline["largest_files"][:10]
    ]
    complexity_rows = [
        [item["path"], item["name"], item["line"], item["complexity"], item["lines"]]
        for item in function_hotspots["highest_complexity_functions"][:10]
    ]
    tooling_rows = [
        [
            name,
            "yes" if details["available"] else "no",
            details["returncode"],
            details["summary"],
        ]
        for name, details in baseline["quality_tooling"].items()
    ]

    return f"""# Enterprise Backend Quality Baseline

Generated: `{baseline["generated_at_utc"]}`

Repository: `lotus-platform`

This is the pre-refactor measurement baseline for the enterprise backend refactor. It is generated
from repository source files and is report-only until individual signals are proven deterministic,
low-noise, and suitable for a blocking CI lane.

## Scope

Included roots: `{", ".join(baseline["scope"]["included_roots"])}`

Excluded parts: `{", ".join(baseline["scope"]["excluded_parts"])}`

## Code Size

- Source files: `{code_size["source_file_count"]}`
- Total source lines: `{code_size["total_source_lines"]}`
- Python files: `{code_size["python_file_count"]}`
- PowerShell files: `{code_size["powershell_file_count"]}`
- Markdown files: `{code_size["markdown_file_count"]}`

## Largest Files

{_markdown_table(["Path", "Lines", "Type"], largest_file_rows)}

## Function And Complexity Hotspots

- Python functions: `{function_hotspots["python_function_count"]}`
- Highest measured cyclomatic complexity: `{function_hotspots["max_complexity"]}`
- Largest Python function length: `{function_hotspots["max_function_lines"]}`

{_markdown_table(["Path", "Function", "Line", "Complexity", "Lines"], complexity_rows)}

## Tooling Baseline

{_markdown_table(["Tool", "Available", "Return Code", "Summary"], tooling_rows)}

## Test Baseline

- Unit tests collected: `{tests["collected_tests"]}`
- Collection command return code: `{tests["returncode"]}`
- Collection summary: `{tests["summary"]}`

## Security Baseline

- Sensitive-keyword review candidate sample size: `{len(security["secret_keyword_review_candidates_sample"])}`
- Candidate interpretation: `{security["note"]}`

## OpenAPI And API Governance

`lotus-platform` does not own a business-domain API. API governance improvement applies to service
scaffolding, validators, vocabulary contracts, generated inventories, and cross-repository
certification evidence.

## Baseline Decision

No new scanner dependency is introduced in this slice. The next refactor slices should either
promote a deterministic signal into a blocking gate or record why it remains report-only.
"""


def render_scorecard(baseline: dict[str, object]) -> str:
    function_hotspots = baseline["function_hotspots"]
    rows = [
        [
            "Code health",
            (
                f"Current max complexity {function_hotspots['max_complexity']} and largest function "
                f"{function_hotspots['max_function_lines']} lines"
            ),
            "Reduce current hotspots without behavior drift",
            (
                "Largest files, highest-complexity functions, and completed extraction history are "
                "recorded in the baseline and health report."
            ),
        ],
        [
            "Architecture",
            "Report-only",
            "Boundary rules enforced where practical",
            "Architecture rules documented.",
        ],
        [
            "OpenAPI quality",
            "Parseable examples could drift from runtime response truth",
            "Generated services bind certified examples to deterministic response producers",
            (
                "A versioned parity contract, fail-closed comparator, scaffold gate, and mutation "
                "tests cover stale fields, blockers, aliases, types, and governed normalization."
            ),
        ],
        [
            "Tests",
            f"{baseline['tests']['collected_tests']} unit tests collected",
            "Focused coverage added per slice",
            "Collection result recorded.",
        ],
        [
            "Security",
            "Keyword review sample measured",
            "Scanner-backed findings clean or governed",
            "No new dependency added yet.",
        ],
        [
            "Observability",
            "Not yet assessed",
            "Operational diagnostics measured and improved",
            "Future slices should add concrete checks.",
        ],
        [
            "Documentation",
            "Quality docs created",
            "Scorecard updated per slice",
            "Docs are implementation-backed.",
        ],
    ]
    return f"""# Enterprise Refactor Quality Scorecard

Generated: `{baseline["generated_at_utc"]}`

This scorecard tracks before/after movement for the enterprise backend refactor. Update it after
meaningful slices with measured evidence, not narrative-only claims.

{_markdown_table(["Area", "Before", "Target After", "Evidence"], rows)}
"""


def render_health_report(baseline: dict[str, object]) -> str:
    return f"""# Enterprise Refactor Health Report

Generated: `{baseline["generated_at_utc"]}`

## Completed Slices

1. Baseline and CI/reporting foundation.
2. Skill guidance hardening so backend, frontend, CI, documentation, and code-review workflows
   default to the Lotus Bank-Buyable Engineering Contract and non-degradation posture.
3. New-service scaffold hardening so freshly generated Lotus apps start with bank-buyable
   quality scorecards, architecture rules, CI-quality notes, refactor decisions, and
   README/repo-context/wiki references.
4. Enterprise refactoring instruction sync repair so deployed app-local copies come from the
   platform canonical playbook, support `-CheckOnly` drift checks, and use registry/discovery
   default scope rather than a single app-specific source.
5. Automation discoverability inventory so cleanup work can distinguish dead automation from
   under-documented maintained scripts before removal.
6. Automation cleanup pass documented maintained supported-claim and rounding-governance commands,
   reducing the inventory `review` bucket to zero without deleting live automation.
7. Guidance path synchronization after docs-root organization so platform-owned skills, standards,
   local skill sync, and contract tests point future agents to `docs/standards/` and
   `docs/operations/` instead of stale repo-root Markdown paths.
8. Engineering context validator modularity improvement by extracting manifest and registry
   validation out of the monolithic validator, reducing the top measured complexity hotspot while
   preserving behavior.
9. Engineering context validator agent-contract extraction so repo-wide AGENTS guidance checks are
   isolated behind a named helper, reducing the top measured complexity hotspot while preserving
   synchronization and front-office runtime routing assertions.
10. Engineering context validator onboarding-guidance extraction so developer bootstrap and agent
    ramp-up assertions are isolated behind a named helper, moving the validator out of the top
    complexity hotspot position while preserving context-currentness checks.
11. Analytics UI observability validator supported-feature extraction so lifecycle promotion rules
    are isolated behind a named helper, removing that validator from the top measured complexity
    hotspot list while preserving RFC-0108 contract behavior.
12. Domain data product producer validator extraction so product identity, approved-consumer,
    registry-reference, lineage, and deprecation checks are isolated behind focused helpers,
    reducing the highest measured complexity hotspot while preserving RFC-0084 contract behavior.
13. Heartbeat status validator extraction so source-inventory and attention-item validation are
    isolated behind focused helpers, reducing the highest measured complexity hotspot while
    preserving RFC-0095 heartbeat contract behavior.
14. Analytics UI ecosystem completion supported-feature extraction so lifecycle milestone,
    protected-feature, and matrix-feature checks are isolated behind focused helpers, reducing the
    highest measured complexity hotspot while preserving RFC-0108 ecosystem completion behavior.
15. Supported-claim register validator extraction so header, front-office, artifact, and per-claim
    checks are isolated behind focused helpers, reducing the highest measured complexity hotspot
    while preserving supported-claim governance behavior.
16. Lotus AI heartbeat adapter extraction so run-summary, queue backlog, and per-run attention
    handling are isolated behind focused helpers, removing the adapter from the top measured
    complexity hotspot list while preserving RFC-0095 heartbeat behavior.
17. Engineering context validator entrypoint extraction so RFC completion, context entrypoint,
    playbook-content, developer-environment automation, and repository-context contract checks are
    isolated behind focused helpers, reducing the highest measured complexity hotspot while
    preserving RFC-0073 context-system behavior.
18. Delegated task ledger heartbeat extraction so task attention generation and active write-scope
    overlap detection are isolated behind focused helpers, removing the adapter from the top
    measured complexity hotspot list while preserving RFC-0095 heartbeat behavior.
19. Analytics UI rollout readiness validator extraction so contract identity, source proof,
    certified route groups, evidence-required panels, rollout checklist, validator proof cases, and
    residual feature checks are isolated behind focused helpers, reducing the highest measured
    complexity hotspot while preserving RFC-0108 rollout-readiness behavior.
20. Domain product onboarding validator extraction so required path discovery, JSON payload
    loading, product declaration checks, policy identity checks, source API profile checks,
    analytics profile checks, and markdown checklist checks are isolated behind focused helpers,
    reducing the highest measured complexity hotspot while preserving generated bundle behavior.
21. Domain data product consumer-contract validator extraction so contract identity, dependency
    identity, required trust metadata, and migration-posture checks are isolated behind focused
    helpers, removing the consumer validator from the top measured complexity hotspot list while
    preserving RFC-0084 consumer-declaration behavior.
22. Domain data product trust-metadata registry extraction so registry identity, trust metadata
    field checks, lineage bundle class checks, and required lineage-field checks are isolated
    behind focused helpers, removing the registry validator from the top measured complexity
    hotspot list while preserving RFC-0084 trust registry behavior.
23. Domain product discovery source-manifest extraction so manifest identity, repository identity,
    governed posture, repo-native directory, and platform declaration path checks are isolated
    behind focused helpers, removing the source-manifest validator from the top measured complexity
    hotspot list while preserving generated catalog freshness behavior.
24. Mesh SLO policy validator extraction so product identity, contract identity, freshness, status
    sections, lineage, and escalation checks are isolated behind focused helpers, reducing the
    highest measured complexity hotspot while preserving RFC-0091 mesh SLO policy behavior.
25. Analytics UI observability supported-feature extraction so lifecycle milestone sets and
    per-feature status policy are isolated behind named helpers, reducing the highest measured
    complexity hotspot while preserving RFC-0108 supported-feature promotion behavior.
26. Analytics UI ecosystem completion slice-status extraction so lifecycle-to-slice expected
    status rules and per-slice required-field checks are isolated behind focused helpers, reducing
    the highest measured complexity hotspot while preserving RFC-0108 ecosystem completion behavior.
27. Mesh access policy validator extraction so product identity, contract identity, allowed
    consumer, denial-posture, and audit checks are isolated behind focused helpers, removing the
    access validator from the top measured complexity hotspot list while preserving RFC-0091 mesh
    access behavior.
28. Analytics UI observability milestone-status extraction so Slice 12, Slice 13, and single-feature
    milestone status checks are isolated behind focused helpers, removing the supported-feature
    status helper from the top measured complexity hotspot list while preserving RFC-0108
    supported-feature promotion behavior.
29. Delegation task output validator extraction so required output fields, write-scope enforcement,
    evidence references, and follow-up checks are isolated behind focused helpers, removing the
    output validator from the top measured complexity hotspot list while preserving RFC-0094/RFC-0096
    delegation return-envelope behavior.
30. Agent engineering task-ledger contract validator extraction so contract identity, authority,
    required sets, conditional fields, delegation requirements, context preservation, and invariants
    are isolated behind focused helpers, lowering the highest measured complexity hotspot while
    preserving RFC-0093/RFC-0094 contract governance behavior.
31. Platform validation coverage validator extraction so profile target checks, manifest references,
    and manifest-driven entrypoint checks are isolated behind focused helpers, removing the coverage
    validator from the top measured complexity hotspot list while preserving CI validation-lane
    governance behavior.
32. Agent delegation-record validator extraction so required input fields, profile policy, identity
    strings, read/write scope policy, forbidden actions, evidence requirements, and return-envelope
    checks are isolated behind focused helpers, removing the delegation-record validator from the
    top measured complexity hotspot list while preserving RFC-0096 delegation guardrail behavior.
33. Engineering context entrypoint validator extraction so context index, quickstart, engineering
    context, reference-map, task-routing, and procedural-memory checks are isolated behind focused
    helpers, removing the context-entrypoint validator from the top measured complexity hotspot
    list while preserving RFC-0073 context-system behavior.
34. Analytics UI observability contract coordinator extraction so contract identity, lifecycle,
    label policy, metric families, dashboard and alert references, state vocabulary, evidence, and
    scaffold requirements are isolated behind focused helpers, lowering the highest measured
    complexity hotspot while preserving RFC-0108 observability contract behavior.
35. Heartbeat status validator extraction so top-level identity, contract-derived sets, summary
    counts, source-read errors, suppression decisions, and missing-source attention invariants are
    isolated behind focused helpers, removing the status validator from the top measured complexity
    hotspot list while preserving RFC-0095 heartbeat behavior.
36. Analytics ecosystem matrix feature-status extraction so lifecycle-to-feature implementation
    rules and per-feature status checks are isolated behind focused helpers, lowering the highest
    measured complexity hotspot while preserving RFC-0108 ecosystem completion behavior.
37. Core-performance attribution validator extraction so source polling, stateful attribution
    request construction, async attribution result following, and acquisition/supported-window
    failure handling are isolated behind focused helpers, removing the live attribution validator
    from the top measured complexity hotspot list while preserving cross-app validation behavior.
38. Engineering context manifest validator extraction so application registry matching, AGENTS
    synchronization, context/procedural path maps, standards registry checks, RFC posture checks,
    and rendered ecosystem-registry drift are isolated behind focused helpers, lowering the highest
    measured complexity hotspot while preserving RFC-0073 context validation behavior.
39. Mesh evidence policy validator extraction so catalog product identity, contract metadata,
    field-access classification, required manifest sections, and required policy coverage are
    isolated behind focused helpers, lowering the highest measured complexity ceiling while
    preserving RFC-0091 mesh evidence-pack policy behavior.
40. Core-performance contribution validator extraction so stateful Core polling, contribution and
    TWR submission, defect recording, return reconciliation, position coverage, and by-position
    timeseries checks are isolated behind focused helpers, removing the live contribution validator
    from the top measured complexity hotspot list while preserving cross-app validation behavior.
41. Domain data product cross-reference validator extraction so producer indexing, latest-version
    selection, dependency product lookup, consumer approval, trust metadata matching, and migration
    posture checks are isolated behind focused helpers, removing the RFC-0084 cross-reference
    validator from the top measured complexity hotspot list while preserving contract issue text.
42. Core-performance baseline validator extraction so CLI parsing, reused-scenario suffix
    enforcement, per-validator scenario routing, defect collection, validator-run summarization, and
    output-summary construction are isolated behind focused helpers, removing the baseline
    orchestrator from the top measured complexity hotspot list while preserving CLI behavior.
43. Analytics UI canonical proof live-summary extraction so canonical identity, screenshot file
    evidence, live check sections, panel-state classification, and SHOT-INDEX validation are
    isolated behind focused helpers, lowering the highest measured complexity ceiling while
    preserving RFC-0108 proof-review behavior.
44. Heartbeat attention-item validator extraction so identity uniqueness, source/severity
    governance, suppression limits, deduplication keys, timestamps, and evidence references are
    isolated behind focused helpers, removing the attention-item validator from the top measured
    complexity hotspot list while preserving RFC-0095 heartbeat contract behavior.
45. Heartbeat runner-config validator extraction so contract identity, path fields, enabled-source
    governance, source-config governance, and threshold validation are isolated behind focused
    helpers, lowering the highest measured complexity ceiling while preserving RFC-0095 runner
    config behavior.
46. Agent delegation-policy validator extraction so contract identity, authority text, required
    policy sets, lifecycle mapping, and invariant checks are isolated behind focused helpers,
    removing the RFC-0096 delegation-policy validator from the top measured complexity hotspot list
    while preserving agent-engineering contract behavior.
47. Heartbeat contract validator extraction so RFC-0095 contract identity, governed vocabulary
    sets, artifact paths, authority policy text, and invariant checks are isolated behind focused
    helpers, removing the heartbeat contract validator from the top measured complexity hotspot
    list while preserving heartbeat contract behavior.
48. Analytics UI final-closure downstream-boundary extraction so Gateway evidence, lotus-manage
    allowed paths, lotus-advise proposal paths, forbidden gateway patterns, ownership decisions,
    local proof, and GitHub check validation are isolated behind focused helpers, removing the
    downstream boundary validator from the top measured complexity hotspot list while preserving
    RFC-0108 final-closure behavior.
49. Heartbeat background-run ledger adapter extraction so run-record projection, run identity,
    failed/lost attention, and stale active-run attention are isolated behind focused helpers,
    removing the background-run ledger adapter from the top measured complexity hotspot list while
    preserving RFC-0095/RFC-0094 heartbeat behavior.
50. Trust telemetry status validator extraction so freshness vocabulary, freshness age consistency,
    and governed status registry checks are isolated behind focused helpers, lowering the highest
    measured complexity ceiling while preserving RFC-0087 trust telemetry behavior.
51. Dev ingress status explainer extraction so missing-smoke, healthy, DNS, HTTP, and unknown
    failure payloads are built by focused helpers with isolated service and ingress classification,
    removing the operator explainer from the top measured complexity hotspot list while preserving
    dev ingress automation behavior.
52. Heartbeat GitHub adapter extraction so PR monitor entry projection, query-error attention,
    failing-check detection, and stale PR attention are isolated behind focused helpers, removing
    the GitHub adapter from the top measured complexity hotspot list while preserving RFC-0095
    heartbeat behavior.
53. Analytics UI ecosystem hardening supported-features extraction so lifecycle status checks,
    reviewed-feature audits, missing-review detection, and residual-scope reconciliation are
    isolated behind focused helpers, removing the hardening supported-features validator from the
    top measured complexity hotspot list while preserving RFC-0108 hardening behavior.
54. Domain data-product semantics registry extraction so registry identity, identifier and temporal
    list validation, semantic-id checks, and trust-vocabulary validation are isolated behind focused
    helpers, removing the semantics registry validator from the top measured complexity hotspot list
    while preserving RFC-0084 contract behavior.
55. Workflow security validator extraction so workflow payload parsing, pull-request-target
    exception checks, write-permission drift checks, note construction, and final pass/fail
    evaluation are isolated behind focused helpers, lowering the highest measured complexity ceiling
    while preserving workflow security gate behavior.
56. Core-performance attribution validator extraction so stateful TWR request/following, TWR
    relative-return extraction, attribution input-mode checks, benchmark-context validation,
    supported-window attribution summarization, reconciliation defect checks, and result assembly are
    isolated behind focused helpers, removing the live attribution validator from the top measured
    complexity hotspot list while preserving cross-app attribution validation behavior.
57. Engineering context onboarding validator extraction so developer onboarding requirements,
    developer stale-boundary checks, agent ramp-up requirements, agent stale-boundary checks, and
    front-office routing checks are isolated behind focused helpers, removing the onboarding
    guidance validator from the top measured complexity hotspot list while preserving context-system
    validation behavior.
58. Analytics UI scaffold CI feature-promotion validator extraction so runtime feature
    classification, scaffold feature status enforcement, and runtime promotion policy checks are
    isolated behind focused helpers, removing the scaffold CI promotion validator from the top
    measured complexity hotspot list while preserving RFC-0108 Slice 11 validation behavior.
59. Supported-claim register claim validator extraction so claim identity, classification, wording,
    implementation-backed proof, client-facing material, backend-only screenshot, and promotion-gate
    checks are isolated behind focused helpers, removing the supported-claim validator from the top
    measured complexity hotspot list while preserving claim-governance validation behavior.
60. Trust telemetry identity validator extraction so snapshot contract header checks, required
    identity fields, catalog lookup, catalog identity matching, and product identity shape checks are
    isolated behind focused helpers, reducing the measured repository complexity ceiling from 15 to
    14 while preserving RFC-0087 trust telemetry validation behavior.
61. Repository hygiene validator extraction so hygiene paths, result assembly, required file
    existence, required pattern coverage, and README command checks are isolated behind focused
    helpers, removing repository hygiene validation from the top measured complexity hotspot list
    while preserving scaffolded-service hygiene validation behavior.
62. API vocabulary cross-app validator extraction so attribute reference collection, cross-app
    indexing, semantic-id drift checks, canonical-term drift checks, and legacy/canonical conflict
    checks are isolated behind focused helpers, removing API vocabulary cross-app validation from
    the top measured complexity hotspot list and adding direct tests for vocabulary drift behavior.
63. Analytics UI telemetry contract validator extraction so severity-level checks, event-type list
    checks, telemetry event section checks, attribute-group checks, dashboard/alert reference
    policies, and protected diagnostics policy checks are isolated behind focused helpers, reducing
    the measured repository complexity ceiling from 14 to 13 while preserving RFC-0108 validation.
64. Live trust certification snapshot evaluator extraction so telemetry validation issue mapping,
    freshness checks, status attention checks, lineage/blocking checks, and certification assembly
    are isolated behind focused helpers, removing live trust certification evaluation from the top
    measured complexity hotspot list while preserving RFC-0087 certification behavior.
65. Analytics UI observation-boundary validator extraction so mutation hydration boundary lookup,
    identity checks, mutation-surface checks, metric-family checks, and evidence-fragment checks are
    isolated behind focused helpers, removing the RFC-0108 observation-boundary validator from the
    top measured complexity hotspot list while preserving contract drift detection behavior.
66. Heartbeat delegated-task ledger adapter extraction so per-task ledger parsing, evidence
    reference assembly, and delegated-task attention collection are isolated behind a focused
    helper, removing the RFC-0096 delegated-task heartbeat adapter from the top measured complexity
    hotspot list while preserving stale/lost/missing-evidence/review-blocker/overlap behavior.
67. Domain data product registry-reference validator extraction so trust metadata, identifier,
    temporal semantic, freshness, and completeness registry checks are isolated behind focused
    helpers, removing registry-reference validation from the top measured complexity hotspot list
    while preserving RFC-0084 declaration drift detection behavior.
68. Domain data product lineage-policy validator extraction so evidence access-class validation,
    lineage bundle-class validation, and optional route-list validation are isolated behind focused
    helpers, removing lineage-policy validation from the top measured complexity hotspot list while
    preserving RFC-0084 declaration drift detection behavior.
69. Cross-app workflow summary renderer extraction so scenario, core, performance, and defect
    rendering are isolated behind focused helpers, removing single-target markdown rendering from
    the top measured complexity hotspot list and adding unit coverage for baseline and single-target
    summary output.
70. Analytics UI ecosystem completion matrix feature-rule extraction so slice-specific
    implementation requirements are isolated behind focused helpers, removing matrix feature rule
    resolution from the top measured complexity hotspot list while preserving RFC-0108 supported
    feature validation behavior.
71. Platform demo-readiness certification command so core/performance green-lane validation can
    seed deterministic scenarios, call real cross-app APIs and calculations, assert expected
    domain figures, write machine-readable demo-readiness evidence, and run in CI as report-only
    evidence until CI governance promotes the signal.
72. Delegated task ledger status-update extraction so RFC-0096 running, terminal, failure, and
    superseded transitions are isolated behind focused helpers, reducing the measured repository
    complexity ceiling from 13 to 12 while preserving delegated-task ledger behavior.
73. Core/performance returns-series validation extraction so cumulative return comparison,
    benchmark-context checking, active-return arithmetic checks, and evidence summary assembly are
    isolated behind focused helpers, removing the 225-line live validator from the top measured
    complexity hotspot list and adding unit coverage for the extracted arithmetic checks.
74. Domain product certification dependency-check extraction so consumer dependency existence,
    reciprocal approval, trust metadata, graph-edge, validation-lane, and failure-posture checks
    are isolated behind focused helpers, removing consumer certification from the top measured
    complexity hotspot list and adding unit coverage for dependency-level issue classification.
75. Mesh SLO violation evaluator extraction so policy context, freshness, status, and lineage
    violation checks are isolated behind focused helpers, removing the RFC-0091 SLO evaluator from
    the top measured complexity hotspot list and adding focused freshness violation coverage.
76. Lotus AI heartbeat queue-item attention extraction so action-required, stale-review,
    terminal-runtime, and lineage-conflict workflow-pack attention rules are isolated behind
    focused helpers, removing queue-item attention generation from the top measured complexity
    hotspot list while preserving RFC-0095 heartbeat behavior.
77. Core/performance expected-posture extraction so pass-scenario and known-core-issue posture
    classification is isolated behind focused helpers, removing the cross-app validation posture
    evaluator from the top measured complexity hotspot list while preserving known-issue review
    behavior.
78. Analytics UI canonical proof reviewer extraction so source loading, QA status validation,
    live-summary evidence validation, sensitive scan path assembly, and result writing are isolated
    behind focused helpers, removing the canonical proof reviewer from the top measured complexity
    hotspot list while preserving RFC-0108 proof review output.
79. Analytics UI ecosystem proof journey validator extraction so API check lookup, failed API
    detection, panel-state policy, and per-journey evidence assembly are isolated behind focused
    helpers, removing the ecosystem proof journey validator from the top measured complexity
    hotspot list while preserving RFC-0108 ecosystem proof review behavior.
80. Analytics UI entitlement implementation-evidence validator extraction so certified path
    identity, owner repository, PR/SHA evidence, and observed proof-reference assembly are isolated
    behind focused helpers, removing entitlement implementation evidence validation from the top
    measured complexity hotspot list while preserving RFC-0108 certification behavior.
81. Analytics UI ecosystem hardening API/proof validator extraction so proof reconciliation flags,
    OpenAPI path review, API certification status, and evidence checks are isolated behind focused
    helpers, removing hardening API/proof validation from the top measured complexity hotspot list
    while preserving RFC-0108 hardening certification behavior.
82. Delegated task overlap heartbeat extraction so active write-scope overlap pair discovery and
    overlap attention-item construction are isolated behind focused helpers, removing delegated
    task overlap attention generation from the top measured complexity hotspot list while
    preserving RFC-0095/RFC-0096 heartbeat attention behavior.
83. Analytics UI ecosystem proof screenshot validator extraction so screenshot-count validation,
    missing screenshot path detection, and SHOT-INDEX evidence validation are isolated behind
    focused helpers, removing ecosystem screenshot validation from the top measured complexity
    hotspot list while preserving RFC-0108 proof review behavior.
84. Engineering context AGENTS contract validator extraction so required section checks and
    required guidance cross-link checks are data-driven through focused helpers, removing the
    AGENTS operating contract validator from the top measured complexity hotspot list while
    preserving exact context validation failure messages.
85. Mesh access allowed-consumer validator extraction so product-catalog consumer approval and
    tenant/role/use-case string-list validation are isolated behind focused predicates, removing
    the mesh access allowed-consumer validator from the top measured complexity hotspot list while
    preserving RFC-0091 access-policy validation behavior.
86. Supported-claim register header validator extraction so contract identity, required string,
    header pattern, and claim-taxonomy checks are isolated behind focused helpers, removing the
    supported-claim register header validator from the top measured complexity hotspot list while
    preserving supported-claim validation error behavior.
87. Analytics UI canonical proof live-summary resolver extraction so embedded summary selection,
    embedded path lookup, fallback path lookup, and file loading are isolated behind focused
    helpers, removing the canonical proof live-summary resolver from the top measured complexity
    hotspot list while preserving RFC-0108 canonical proof review behavior.
88. Heartbeat suppressions validator extraction so contract identity, suppression-list shape,
    required string fields, and expiry checks are isolated behind focused helpers, removing the
    suppressions validator from the top measured complexity hotspot list while preserving RFC-0095
    suppression policy behavior.
89. Analytics UI ecosystem proof reviewer extraction so artifact loading, QA status validation,
    live-summary evidence assembly, sensitive-content path selection, static evidence validation,
    and output writing are isolated behind focused helpers, removing the proof reviewer
    coordinator from the top measured complexity hotspot list while preserving RFC-0108 proof
    review behavior.
90. Domain data-product producer validator extraction so producer contract identity, product-list
    shape, and per-product validation orchestration are isolated behind focused helpers, removing
    the producer contract validator from the top measured complexity hotspot list while preserving
    RFC-0084 issue behavior.
91. Heartbeat delegated-task attention extraction so terminal status, stale active task,
    missing return-envelope, and review-blocker attention rules are isolated behind focused
    helpers, removing delegated-task attention collection from the top measured complexity hotspot
    list while preserving RFC-0095/RFC-0096 heartbeat behavior.
92. Analytics UI telemetry-field hardening extraction so metric label policy, implemented event
    review coverage, and telemetry attribute checks are isolated behind focused helpers, removing
    telemetry-field hardening review from the top measured complexity hotspot list while adding
    direct sensitive-label and sensitive-attribute regression coverage.
93. Analytics UI ecosystem gap-matrix extraction so row shape, feature-key, and implemented-posture
    checks are isolated behind focused helpers, removing gap-matrix validation from the top
    measured complexity hotspot list while adding direct invalid-posture and missing-field
    regression coverage.
94. Domain-product discovery query extraction so product filters, search matching, and result
    sorting are isolated behind focused helpers, removing the query helper from the top measured
    complexity hotspot list while adding lifecycle-filter and search-miss regression coverage.
95. Domain-data-product dependency migration-posture extraction so current-dependency and
    approved-transition validation are isolated behind focused helpers, removing migration-posture
    validation from the top measured complexity hotspot list while adding direct regression
    coverage for invalid current targets and incomplete approved transitions.
96. Dev ingress hosts sync extraction so hosts-file reading, backup writing, staged fallback, and
    result rendering are isolated behind focused helpers, removing the Windows hosts sync
    coordinator from the top measured complexity hotspot list while adding first-time-create
    regression coverage.
97. Analytics UI rollout route-group extraction so malformed group detection, status checks,
    evidence checks, and registry route matching are isolated behind focused helpers, removing
    certified route-group validation from the top measured complexity hotspot list while adding
    malformed-entry regression coverage.
98. Trust telemetry freshness-age extraction so age shape validation, maximum-age validation, and
    current-state conflict checks are isolated behind focused helpers, removing freshness-age
    validation from the top measured complexity hotspot list while adding boolean numeric-field
    hardening coverage.
99. Shared infrastructure ownership validator extraction so lotus-core evidence loading and
    app-local ownership checks are isolated behind focused helpers, removing the lotus-core
    validator from the top measured complexity hotspot list while adding app-local stack guide
    boundary-drift coverage.
100. Heartbeat mesh-certification adapter extraction so stale evidence and operating-state
    attention checks are isolated behind focused helpers, removing the mesh-certification adapter
    from the top measured complexity hotspot list while adding attention-required regression
    coverage.
101. Analytics UI hardening dashboard-review extraction so dashboard metric reconciliation and
    alert-rule reconciliation are isolated behind focused helpers, removing the dashboard review
    validator from the top measured complexity hotspot list while adding alert-rule drift
    regression coverage.
102. RFC-0086 catalog closure test extraction so catalog source-path collection, product presence
     matching, and first-wave certification-posture assertions are isolated behind focused helpers,
     reducing the measured repository complexity ceiling from 11 to 10 while preserving
     repo-native domain-product rollout closure behavior.
103. Trust telemetry lineage and blocking extraction so lineage metadata checks and blocking-state
     checks are isolated behind focused helpers, removing the trust telemetry validator from the top
     measured complexity hotspot list while adding malformed-lineage regression coverage.
104. Repository-governance normalizer extraction so unprotected defaults, status-check parsing, pull
     request review parsing, and branch-protection booleans are isolated behind focused helpers,
     removing the governance normalizer from the top measured complexity hotspot list while adding
     protected-branch payload regression coverage.
105. Domain-data-product registry-entry extraction so key validation, object-shape validation, and
     required-string validation are isolated behind focused helpers, removing the registry-entry
     validator from the top measured complexity hotspot list while adding malformed-registry
     regression coverage.
106. Enterprise quality-surface validator extraction so required artifact checks, baseline JSON
     loading, baseline key validation, and repo-check wiring validation are isolated behind focused
     helpers, removing the quality-surface validator from the top measured complexity hotspot list
     while adding invalid-JSON and missing-key regression coverage.
107. Delegation evidence-ref validator extraction so governed evidence-ref type validation and
     evidence location validation are isolated behind focused helpers, removing delegation
     output-evidence validation from the top measured complexity hotspot list while adding empty-list
     and path-only evidence-ref regression coverage.
108. Analytics UI feature-milestone validator extraction so single-feature and feature-set milestone
     enforcement are isolated behind focused helpers, removing the final complexity-10 hotspot and
     reducing the measured repository complexity ceiling to 9 while adding Slice 10 and Slice 11
     milestone regression coverage.
109. Proof-artifact guardrail hardening so enterprise refactor instructions, CI-enforcement skill
     guidance, and instruction-sync tests pin bounded proof artifacts, exact blocker semantics,
     source-safety checks, and anti-overclaim examples before app-local rollout.
110. Certified endpoint response-example parity enforcement so generated services compare authored
     examples structurally with deterministic code-owned producers, fail closed on stale fields,
     blocker vocabulary, aliases, and types, and permit dynamic values only through explicit
     field-level normalizers.
111. Governance complexity and baseline freshness hardening so skill-context audit, lifecycle
     authority validation, and deployment-promotion validation responsibilities are isolated behind
     focused helpers, while `--check` compares material current metrics against the accepted
     quality baseline and fails stale report-only evidence without timestamp-only rewrites.

## Evidence

1. Baseline generator: `automation/generate_enterprise_backend_quality_baseline.py`
2. Baseline report: `quality/baseline_report.md`
3. Scorecard: `quality/quality_scorecard.md`
4. Repo check hook: `automation/Invoke-PlatformRepoChecks.ps1`
5. Skill guidance: `codex/skills/lotus-backend-delivery-governance/SKILL.md`
6. Skill guidance: `codex/skills/lotus-frontend-delivery-governance/SKILL.md`
7. Skill guidance: `codex/skills/lotus-ci-enforcement-governance/SKILL.md`
8. Skill guidance: `codex/skills/lotus-readme-wiki-governance/SKILL.md`
9. Skill guidance: `codex/skills/lotus-codebase-review-ledger/SKILL.md`
10. Scaffold automation: `automation/New-Lotus-Service.ps1`
11. Scaffold contract tests: `tests/unit/test_repository_hygiene_scaffold_contract.py`
12. Refactor instruction sync: `automation/Sync-EnterpriseBackendRefactoringInstructions.ps1`
13. Refactor instruction sync tests: `tests/unit/test_enterprise_backend_refactor_instruction_sync.py`
14. Automation inventory: `automation/generate_automation_inventory.py`
15. Automation inventory report: `quality/automation_inventory.md`
16. Supported-claim validator: `automation/validate_supported_claim_register.py`
17. Rounding governance matrix: `automation/Validate-Rounding-Governance.ps1`
18. Skill path contract tests: `tests/unit/test_lotus_skill_routing_behavior_contract.py`
19. Standards path contract tests: `tests/unit/test_ci_governance_documentation_contract.py`
20. Context validator refactor: `automation/validate_engineering_context_system.py`
21. Context validator tests: `tests/unit/test_engineering_context_validator.py`
22. Endpoint-example parity contract:
    `platform-contracts/api-governance/endpoint-example-parity-contract.v1.json`
23. Endpoint-example parity comparator:
    `codex/skills/lotus-ci-enforcement-governance/scripts/endpoint_example_parity.py`
24. Endpoint-example parity tests: `tests/unit/test_endpoint_example_parity.py`

## Current Gate Posture

The quality baseline is report-only. `--check` validates that the required reporting surface exists
and remains wired into the platform repo checks.

## Conscious Guidance Review

The enterprise refactor requires keeping README, docs, wiki, repo context, central agent context,
and relevant skill guidance synchronized as code truth changes. This baseline slice updates
`lotus-ci-enforcement-governance` to point future agents at the measured baseline, scorecard, and
health report before any quality signal is promoted from report-only to blocking.
"""


def write_quality_artifacts(baseline: dict[str, object]) -> None:
    accepted_errors: list[str] = []
    accepted = _load_baseline_report(accepted_errors)
    baseline = _preserve_generated_at_when_metrics_match(
        baseline,
        accepted if not accepted_errors else None,
    )
    QUALITY_DIR.mkdir(exist_ok=True)
    (QUALITY_DIR / "baseline_report.json").write_text(
        json.dumps(baseline, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (QUALITY_DIR / "baseline_report.md").write_text(
        render_baseline_report(baseline), encoding="utf-8"
    )
    (QUALITY_DIR / "quality_scorecard.md").write_text(
        render_scorecard(baseline), encoding="utf-8"
    )
    (QUALITY_DIR / "refactor_health_report.md").write_text(
        render_health_report(baseline), encoding="utf-8"
    )
    for name, content in QUALITY_DOCS.items():
        path = QUALITY_DIR / name
        if not path.exists():
            path.write_text(content, encoding="utf-8")


def _required_quality_files() -> set[str]:
    return {
        "baseline_report.json",
        "baseline_report.md",
        "quality_scorecard.md",
        "refactor_health_report.md",
        *QUALITY_DOCS.keys(),
    }


def _validate_required_quality_files(errors: list[str]) -> None:
    for file_name in sorted(_required_quality_files()):
        path = QUALITY_DIR / file_name
        if not path.exists():
            errors.append(f"Missing quality artifact: quality/{file_name}")
            continue
        if path.stat().st_size == 0:
            errors.append(f"Empty quality artifact: quality/{file_name}")


def _load_baseline_report(errors: list[str]) -> dict[str, object] | None:
    baseline_path = QUALITY_DIR / "baseline_report.json"
    if not baseline_path.exists():
        return None
    try:
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid quality/baseline_report.json: {exc}")
        return None
    if not isinstance(baseline, dict):
        errors.append("quality/baseline_report.json must be an object")
        return None
    return baseline


def _validate_baseline_report_keys(
    errors: list[str],
    baseline: dict[str, object] | None,
) -> None:
    if baseline is None:
        return
    for key in (
        "code_size",
        "function_hotspots",
        "quality_tooling",
        "tests",
        "security",
    ):
        if key not in baseline:
            errors.append(f"quality/baseline_report.json missing `{key}`")


def _metric_value(baseline: dict[str, object], path: tuple[str, str]) -> object:
    parent = baseline.get(path[0])
    if not isinstance(parent, dict):
        return None
    return parent.get(path[1])


def _baseline_freshness_differences(
    accepted: dict[str, object],
    current: dict[str, object],
) -> list[str]:
    differences: list[str] = []
    for metric_name, metric_path in FRESHNESS_METRICS.items():
        accepted_value = _metric_value(accepted, metric_path)
        current_value = _metric_value(current, metric_path)
        if accepted_value != current_value:
            differences.append(
                f"`{metric_name}`: accepted={accepted_value!r}, current={current_value!r}"
            )
    return differences


def _preserve_generated_at_when_metrics_match(
    baseline: dict[str, object],
    accepted: dict[str, object] | None,
) -> dict[str, object]:
    if accepted is None or _baseline_freshness_differences(accepted, baseline):
        return baseline
    preserved = dict(baseline)
    preserved["generated_at_utc"] = accepted.get(
        "generated_at_utc", baseline.get("generated_at_utc")
    )
    return preserved


def _validate_baseline_freshness(
    errors: list[str],
    accepted: dict[str, object] | None,
) -> None:
    if accepted is None:
        return
    current = build_baseline()
    for difference in _baseline_freshness_differences(accepted, current):
        errors.append(
            "quality/baseline_report.json stale "
            f"{difference}. "
            "Run generate_enterprise_backend_quality_baseline.py --write after "
            "material quality metric changes."
        )


def _validate_repo_check_wiring(errors: list[str]) -> None:
    repo_checks = ROOT / "automation" / "Invoke-PlatformRepoChecks.ps1"
    if not repo_checks.exists():
        return
    text = repo_checks.read_text(encoding="utf-8")
    if "generate_enterprise_backend_quality_baseline.py --check" not in text:
        errors.append(
            "Platform repo checks do not validate the enterprise backend quality baseline."
        )


def validate_quality_surface() -> list[str]:
    errors: list[str] = []
    _validate_required_quality_files(errors)
    baseline = _load_baseline_report(errors)
    _validate_baseline_report_keys(errors, baseline)
    if not errors:
        _validate_baseline_freshness(errors, baseline)
    _validate_repo_check_wiring(errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate or validate the Lotus platform quality baseline."
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write quality baseline and scorecard artifacts.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate that quality baseline artifacts exist.",
    )
    args = parser.parse_args()

    if args.write:
        baseline = build_baseline()
        write_quality_artifacts(baseline)
        print("Enterprise backend quality baseline generated.")

    if args.check:
        errors = validate_quality_surface()
        if errors:
            print(
                "Enterprise backend quality baseline validation failed:",
                file=sys.stderr,
            )
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
        print("Enterprise backend quality baseline validation passed.")

    if not args.write and not args.check:
        parser.error("Specify --write, --check, or both.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
