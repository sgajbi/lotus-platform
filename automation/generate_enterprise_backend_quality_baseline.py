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
    return sorted(metrics, key=lambda metric: (-metric.complexity, -metric.lines, metric.path, metric.name))


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
        return {"available": False, "command": args, "returncode": None, "summary": "tool not installed"}
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
    result = _run_command([sys.executable, "-m", "pytest", "--collect-only", "-q", "tests/unit"])
    summary = str(result["summary"])
    collected = 0
    for token in summary.split():
        if token.isdigit():
            collected = int(token)
            break
    result["collected_tests"] = collected
    return result


def _scan_secret_keyword_candidates(files: Iterable[Path]) -> list[dict[str, object]]:
    sensitive_tokens = ("password", "secret", "token", "credential", "api_key", "private_key")
    candidates: list[dict[str, object]] = []
    for path in files:
        if path.suffix.lower() not in {".py", ".ps1", ".yml", ".yaml", ".json", ".md", ".txt"}:
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
        "generated_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
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
                metric.__dict__ for metric in sorted(function_metrics, key=lambda item: (-item.lines, item.path))[:20]
            ],
            "highest_complexity_functions": [metric.__dict__ for metric in function_metrics[:20]],
        },
        "quality_tooling": {
            "ruff": _run_command(["ruff", "--version"]),
            "mypy": _run_command(["mypy", "--version"]),
            "bandit": _run_command(["bandit", "--version"]),
            "pip_audit": _run_command(["pip-audit", "--version"]),
        },
        "tests": _count_pytest_tests(),
        "security": {
            "secret_keyword_review_candidates_sample": _scan_secret_keyword_candidates(files),
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
    rendered = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        rendered.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(rendered)


def render_baseline_report(baseline: dict[str, object]) -> str:
    code_size = baseline["code_size"]
    function_hotspots = baseline["function_hotspots"]
    tests = baseline["tests"]
    security = baseline["security"]

    largest_file_rows = [[item["path"], item["lines"], item["suffix"]] for item in baseline["largest_files"][:10]]
    complexity_rows = [
        [item["path"], item["name"], item["line"], item["complexity"], item["lines"]]
        for item in function_hotspots["highest_complexity_functions"][:10]
    ]
    tooling_rows = [
        [name, "yes" if details["available"] else "no", details["returncode"], details["summary"]]
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
    rows = [
        ["Code health", "Baseline measured", "Not yet measured", "Largest files and complexity hotspots recorded."],
        ["Architecture", "Report-only", "Boundary rules enforced where practical", "Architecture rules documented."],
        [
            "OpenAPI quality",
            "Platform governance only",
            "Scaffold and validator improvements measured",
            "No business API owned here.",
        ],
        [
            "Tests",
            f"{baseline['tests']['collected_tests']} unit tests collected",
            "Focused coverage added per slice",
            "Collection result recorded.",
        ],
        ["Security", "Keyword review sample measured", "Scanner-backed findings clean or governed", "No new dependency added yet."],
        ["Observability", "Not yet assessed", "Operational diagnostics measured and improved", "Future slices should add concrete checks."],
        ["Documentation", "Quality docs created", "Scorecard updated per slice", "Docs are implementation-backed."],
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
    QUALITY_DIR.mkdir(exist_ok=True)
    (QUALITY_DIR / "baseline_report.json").write_text(
        json.dumps(baseline, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (QUALITY_DIR / "baseline_report.md").write_text(render_baseline_report(baseline), encoding="utf-8")
    (QUALITY_DIR / "quality_scorecard.md").write_text(render_scorecard(baseline), encoding="utf-8")
    (QUALITY_DIR / "refactor_health_report.md").write_text(render_health_report(baseline), encoding="utf-8")
    for name, content in QUALITY_DOCS.items():
        path = QUALITY_DIR / name
        if not path.exists():
            path.write_text(content, encoding="utf-8")


def validate_quality_surface() -> list[str]:
    required_files = {
        "baseline_report.json",
        "baseline_report.md",
        "quality_scorecard.md",
        "refactor_health_report.md",
        *QUALITY_DOCS.keys(),
    }
    errors: list[str] = []
    for file_name in sorted(required_files):
        path = QUALITY_DIR / file_name
        if not path.exists():
            errors.append(f"Missing quality artifact: quality/{file_name}")
            continue
        if path.stat().st_size == 0:
            errors.append(f"Empty quality artifact: quality/{file_name}")

    baseline_path = QUALITY_DIR / "baseline_report.json"
    if baseline_path.exists():
        try:
            baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid quality/baseline_report.json: {exc}")
        else:
            for key in ("code_size", "function_hotspots", "quality_tooling", "tests", "security"):
                if key not in baseline:
                    errors.append(f"quality/baseline_report.json missing `{key}`")

    repo_checks = ROOT / "automation" / "Invoke-PlatformRepoChecks.ps1"
    if repo_checks.exists():
        text = repo_checks.read_text(encoding="utf-8")
        if "generate_enterprise_backend_quality_baseline.py --check" not in text:
            errors.append("Platform repo checks do not validate the enterprise backend quality baseline.")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate or validate the Lotus platform quality baseline.")
    parser.add_argument("--write", action="store_true", help="Write quality baseline and scorecard artifacts.")
    parser.add_argument("--check", action="store_true", help="Validate that quality baseline artifacts exist.")
    args = parser.parse_args()

    if args.write:
        baseline = build_baseline()
        write_quality_artifacts(baseline)
        print("Enterprise backend quality baseline generated.")

    if args.check:
        errors = validate_quality_surface()
        if errors:
            print("Enterprise backend quality baseline validation failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
        print("Enterprise backend quality baseline validation passed.")

    if not args.write and not args.check:
        parser.error("Specify --write, --check, or both.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
