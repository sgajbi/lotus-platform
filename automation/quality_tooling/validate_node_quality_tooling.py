"""Validate deterministic Node tooling used by blocking quality evidence."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


EXECUTABLE_SUFFIXES = {
    ".cjs",
    ".js",
    ".json",
    ".mjs",
    ".ps1",
    ".py",
    ".sh",
    ".ts",
    ".yaml",
    ".yml",
}
IGNORED_DIRECTORY_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "node_modules",
    "output",
}
BLOCKING_SCRIPT_TERMS = {
    "audit",
    "check",
    "contract",
    "gate",
    "governance",
    "lint",
    "openapi",
    "quality",
    "spectral",
    "validate",
}
REPORT_ONLY_TERMS = {"inventory", "report"}
NPX_PATTERN = re.compile(r"\bnpx(?:\.cmd)?\b", re.IGNORECASE)
GLOBAL_INSTALL_PATTERN = re.compile(
    r"\bnpm(?:\.cmd)?\s+(?:install|i)\b[^\r\n]*(?:\s-g\b|\s--global\b)",
    re.IGNORECASE,
)
NPM_INSTALL_PATTERN = re.compile(
    r"\bnpm(?:\.cmd)?\s+(?:install|i)\b", re.IGNORECASE
)
PYTHON_NPM_INSTALL_PATTERN = re.compile(
    r"[\"']npm(?:\.cmd)?[\"']\s*,\s*[\"'](?:install|i)[\"']", re.IGNORECASE
)
CLEAN_INSTALL_PATTERNS = (
    re.compile(r"\bnpm(?:\.cmd)?\s+ci\b", re.IGNORECASE),
    re.compile(r"[\"']npm(?:\.cmd)?[\"']\s*,\s*[\"']ci[\"']", re.IGNORECASE),
    re.compile(r"\bnpm_executable\([^)]*\)\s*,\s*[\"']ci[\"']", re.IGNORECASE),
)
LOCAL_BINARY_PATTERNS = (
    re.compile(r"node_modules.{0,80}\.bin", re.IGNORECASE | re.DOTALL),
    re.compile(r"\bnpm(?:\.cmd)?\s+run\b", re.IGNORECASE),
    re.compile(r"[\"']npm(?:\.cmd)?[\"']\s*,\s*[\"']run[\"']", re.IGNORECASE),
)
EXACT_VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")
EXACT_NODE_VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
LOWER_NODE_BOUND_PATTERN = re.compile(r">=\s*\d+(?:\.\d+){0,2}")
UPPER_NODE_BOUND_PATTERN = re.compile(r"<\s*\d+(?:\.\d+){0,2}")


@dataclass(frozen=True, slots=True)
class Finding:
    """One deterministic Node quality-tooling contract violation."""

    code: str
    path: str
    message: str
    line: int | None = None


def _relative_path(repository: Path, path: Path) -> str:
    return path.relative_to(repository).as_posix()


def _is_ignored(path: Path) -> bool:
    return any(part in IGNORED_DIRECTORY_NAMES for part in path.parts)


def _is_report_only_script(path: Path) -> bool:
    stem_terms = set(re.split(r"[^a-z0-9]+", path.stem.lower()))
    return bool(stem_terms & REPORT_ONLY_TERMS) and not bool(
        stem_terms & {"check", "gate", "validate"}
    )


def _is_blocking_script(path: Path) -> bool:
    if _is_report_only_script(path):
        return False
    terms = set(re.split(r"[^a-z0-9]+", path.as_posix().lower()))
    return bool(terms & BLOCKING_SCRIPT_TERMS)


def _iter_execution_sources(repository: Path) -> list[Path]:
    sources: set[Path] = set()
    workflow_root = repository / ".github" / "workflows"
    if workflow_root.exists():
        sources.update(workflow_root.rglob("*.yml"))
        sources.update(workflow_root.rglob("*.yaml"))

    for owned_root_name in ("scripts", "tools"):
        owned_root = repository / owned_root_name
        if not owned_root.exists():
            continue
        for path in owned_root.rglob("*"):
            if (
                path.is_file()
                and path.suffix.lower() in EXECUTABLE_SUFFIXES
                and not _is_ignored(path.relative_to(repository))
                and _is_blocking_script(path.relative_to(repository))
                and path.name != "package-lock.json"
            ):
                sources.add(path)
    return sorted(sources)


def _line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _source_findings(repository: Path, path: Path) -> list[Finding]:
    text = path.read_text(encoding="utf-8")
    relative_path = _relative_path(repository, path)
    findings: list[Finding] = []
    for pattern, code, message in (
        (
            NPX_PATTERN,
            "unbounded-npx",
            "blocking quality evidence must use a lock-installed local binary, not npx",
        ),
        (
            GLOBAL_INSTALL_PATTERN,
            "global-npm-install",
            "blocking quality evidence must not install global npm packages",
        ),
    ):
        for match in pattern.finditer(text):
            findings.append(
                Finding(
                    code=code,
                    path=relative_path,
                    line=_line_number(text, match.start()),
                    message=message,
                )
            )

    install_matches = list(NPM_INSTALL_PATTERN.finditer(text)) + list(
        PYTHON_NPM_INSTALL_PATTERN.finditer(text)
    )
    for match in install_matches:
        line_start = text.rfind("\n", 0, match.start()) + 1
        line_end = text.find("\n", match.end())
        line_text = text[line_start:] if line_end == -1 else text[line_start:line_end]
        if GLOBAL_INSTALL_PATTERN.search(line_text):
            continue
        findings.append(
            Finding(
                code="mutable-npm-install",
                path=relative_path,
                line=_line_number(text, match.start()),
                message="blocking quality evidence must restore dependencies with npm ci",
            )
        )
    return findings


def _iter_tool_manifests(repository: Path) -> list[Path]:
    tools_root = repository / "tools"
    if not tools_root.exists():
        return []
    return sorted(
        path
        for path in tools_root.rglob("package.json")
        if not _is_ignored(path.relative_to(repository))
        and _is_blocking_script(path.relative_to(repository))
    )


def _read_json_object(path: Path) -> tuple[dict[str, object] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)
    if not isinstance(payload, dict):
        return None, "top-level JSON value must be an object"
    return payload, None


def _dependency_entries(manifest: dict[str, object]) -> Iterable[tuple[str, object]]:
    for field_name in ("dependencies", "devDependencies"):
        values = manifest.get(field_name, {})
        if isinstance(values, dict):
            yield from values.items()


def _is_governed_node_range(value: object) -> bool:
    if not isinstance(value, str):
        return False
    normalized = value.strip()
    return bool(
        EXACT_NODE_VERSION_PATTERN.fullmatch(normalized)
        or (
            LOWER_NODE_BOUND_PATTERN.search(normalized)
            and UPPER_NODE_BOUND_PATTERN.search(normalized)
        )
    )


def _manifest_findings(repository: Path, path: Path) -> list[Finding]:
    relative_path = _relative_path(repository, path)
    manifest, error = _read_json_object(path)
    if manifest is None:
        return [
            Finding(
                code="invalid-tool-manifest",
                path=relative_path,
                message=f"dedicated Node quality-tool manifest is invalid: {error}",
            )
        ]

    findings: list[Finding] = []
    lock_path = path.with_name("package-lock.json")
    lock_payload, lock_error = _read_json_object(lock_path)
    if lock_payload is None:
        findings.append(
            Finding(
                code="missing-tool-lockfile",
                path=_relative_path(repository, lock_path),
                message=f"dedicated Node quality tooling requires package-lock.json: {lock_error}",
            )
        )
    elif not isinstance(lock_payload.get("lockfileVersion"), int):
        findings.append(
            Finding(
                code="invalid-tool-lockfile",
                path=_relative_path(repository, lock_path),
                message="package-lock.json must declare a numeric lockfileVersion",
            )
        )

    dependencies = list(_dependency_entries(manifest))
    for dependency_name, version in dependencies:
        if not isinstance(version, str) or not EXACT_VERSION_PATTERN.fullmatch(version):
            findings.append(
                Finding(
                    code="non-exact-tool-dependency",
                    path=relative_path,
                    message=(
                        f"quality-tool dependency {dependency_name!r} must use an exact version; "
                        f"found {version!r}"
                    ),
                )
            )

    engines = manifest.get("engines")
    node_range = engines.get("node") if isinstance(engines, dict) else None
    if not _is_governed_node_range(node_range):
        findings.append(
            Finding(
                code="ungoverned-node-runtime",
                path=relative_path,
                message=(
                    "dedicated Node quality tooling must declare an exact Node version or "
                    "bounded engines.node range"
                ),
            )
        )
    return findings


def validate_repository(repository: Path) -> list[Finding]:
    """Return deterministic quality-tooling findings for one repository."""

    repository = repository.resolve()
    sources = _iter_execution_sources(repository)
    manifests = _iter_tool_manifests(repository)
    findings = [
        finding
        for source in sources
        for finding in _source_findings(repository, source)
    ]
    findings.extend(
        finding
        for manifest in manifests
        for finding in _manifest_findings(repository, manifest)
    )

    if manifests:
        source_text = "\n".join(path.read_text(encoding="utf-8") for path in sources)
        if not any(pattern.search(source_text) for pattern in CLEAN_INSTALL_PATTERNS):
            findings.append(
                Finding(
                    code="missing-clean-install",
                    path="tools",
                    message="dedicated Node quality tooling must be restored with npm ci",
                )
            )
        if not any(pattern.search(source_text) for pattern in LOCAL_BINARY_PATTERNS):
            findings.append(
                Finding(
                    code="missing-local-binary",
                    path="tools",
                    message=(
                        "blocking quality evidence must invoke a node_modules/.bin executable "
                        "or a package script"
                    ),
                )
            )
    return sorted(
        findings,
        key=lambda finding: (finding.path, finding.line or 0, finding.code),
    )


def main(argv: list[str] | None = None) -> int:
    """Validate one repository and emit machine-readable findings when requested."""

    parser = argparse.ArgumentParser(
        description="Validate deterministic Node tooling used by blocking quality evidence."
    )
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true", dest="emit_json")
    args = parser.parse_args(argv)

    findings = validate_repository(args.repository)
    if args.emit_json:
        print(json.dumps([asdict(finding) for finding in findings], indent=2))
    elif findings:
        for finding in findings:
            location = f"{finding.path}:{finding.line}" if finding.line else finding.path
            print(f"{location}: [{finding.code}] {finding.message}")
    else:
        print("Node quality-tooling validation passed.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
