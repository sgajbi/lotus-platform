from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_GITIGNORE_PATTERNS = (
    ".venv/",
    "__pycache__/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
    ".coverage",
    ".coverage.*",
    "dist/",
    "build/",
    "output/",
    ".env",
    ".env.*",
)

REQUIRED_EDITORCONFIG_PATTERNS = (
    "root = true",
    "charset = utf-8",
    "end_of_line = lf",
    "insert_final_newline = true",
)

REQUIRED_GITATTRIBUTES_PATTERNS = (
    "* text=auto eol=lf",
    "*.png binary",
)

REQUIRED_DOCKERIGNORE_PATTERNS = (
    ".git",
    ".venv",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "output",
    "docs",
    "tests",
)
REQUIRED_EXISTENCE_RESULT_FIELDS = (
    "editorconfig_exists",
    "gitattributes_exists",
    "gitignore_exists",
    "dockerignore_exists",
    "readme_exists",
    "shared_runtime_lock_exists",
    "ci_tooling_lock_exists",
)
REQUIRED_EMPTY_RESULT_FIELDS = (
    "editorconfig_missing_patterns",
    "gitattributes_missing_patterns",
    "gitignore_missing_patterns",
    "dockerignore_missing_patterns",
)
REQUIRED_README_COMMAND_FIELDS = (
    "readme_has_make_check",
    "readme_has_make_ci",
)


def _read_text_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _missing_patterns(content: str, patterns: tuple[str, ...]) -> list[str]:
    return [pattern for pattern in patterns if pattern not in content]


def determine_dependency_authority(repo_root: Path) -> str:
    has_pyproject = (repo_root / "pyproject.toml").exists()
    has_requirements = (repo_root / "requirements.txt").exists()
    if has_pyproject and not has_requirements:
        return "pyproject"
    if has_requirements and not has_pyproject:
        return "requirements"
    if has_pyproject and has_requirements:
        return "hybrid"
    return "missing"


def _hygiene_paths(repo_root: Path) -> dict[str, Path]:
    return {
        "editorconfig": repo_root / ".editorconfig",
        "gitattributes": repo_root / ".gitattributes",
        "gitignore": repo_root / ".gitignore",
        "dockerignore": repo_root / ".dockerignore",
        "readme": repo_root / "README.md",
        "shared_runtime_lock": repo_root / "requirements" / "shared-runtime.lock.txt",
        "ci_tooling_lock": repo_root / "requirements" / "ci-tooling.lock.txt",
    }


def _build_hygiene_result(repo_root: Path, paths: dict[str, Path]) -> dict[str, object]:
    readme_content = _read_text_if_exists(paths["readme"])
    result = {
        "repo_root": str(repo_root),
        "editorconfig_exists": paths["editorconfig"].exists(),
        "gitattributes_exists": paths["gitattributes"].exists(),
        "gitignore_exists": paths["gitignore"].exists(),
        "dockerignore_exists": paths["dockerignore"].exists(),
        "readme_exists": paths["readme"].exists(),
        "dependency_authority": determine_dependency_authority(repo_root),
        "shared_runtime_lock_exists": paths["shared_runtime_lock"].exists(),
        "ci_tooling_lock_exists": paths["ci_tooling_lock"].exists(),
        "editorconfig_missing_patterns": _missing_patterns(
            _read_text_if_exists(paths["editorconfig"]),
            REQUIRED_EDITORCONFIG_PATTERNS,
        ),
        "gitattributes_missing_patterns": _missing_patterns(
            _read_text_if_exists(paths["gitattributes"]),
            REQUIRED_GITATTRIBUTES_PATTERNS,
        ),
        "gitignore_missing_patterns": _missing_patterns(
            _read_text_if_exists(paths["gitignore"]),
            REQUIRED_GITIGNORE_PATTERNS,
        ),
        "dockerignore_missing_patterns": _missing_patterns(
            _read_text_if_exists(paths["dockerignore"]),
            REQUIRED_DOCKERIGNORE_PATTERNS,
        ),
        "readme_has_make_check": "make check" in readme_content,
        "readme_has_make_ci": "make ci" in readme_content,
    }
    result["ok"] = _repository_hygiene_is_ok(result)
    return result


def _repository_hygiene_is_ok(result: dict[str, object]) -> bool:
    required_files_exist = all(
        bool(result[field_name]) for field_name in REQUIRED_EXISTENCE_RESULT_FIELDS
    )
    required_patterns_present = all(
        not result[field_name] for field_name in REQUIRED_EMPTY_RESULT_FIELDS
    )
    required_readme_commands_present = all(
        bool(result[field_name]) for field_name in REQUIRED_README_COMMAND_FIELDS
    )
    return (
        required_files_exist
        and result["dependency_authority"] == "pyproject"
        and required_patterns_present
        and required_readme_commands_present
    )


def validate_repository_hygiene(repo_root: Path) -> dict[str, object]:
    return _build_hygiene_result(repo_root, _hygiene_paths(repo_root))


def build_markdown_report(result: dict[str, object]) -> str:
    lines = [
        "# Repository Hygiene Validation",
        "",
        f"- Repo Root: `{result['repo_root']}`",
        f"- Dependency Authority: `{result['dependency_authority']}`",
        f"- Status: `{'ok' if result['ok'] else 'gap'}`",
        "",
        "| Check | Result |",
        "| --- | --- |",
        f"| `.editorconfig` present | `{result['editorconfig_exists']}` |",
        f"| `.gitattributes` present | `{result['gitattributes_exists']}` |",
        f"| `.gitignore` present | `{result['gitignore_exists']}` |",
        f"| `.dockerignore` present | `{result['dockerignore_exists']}` |",
        f"| `README.md` present | `{result['readme_exists']}` |",
        f"| `requirements/shared-runtime.lock.txt` present | `{result['shared_runtime_lock_exists']}` |",
        f"| `requirements/ci-tooling.lock.txt` present | `{result['ci_tooling_lock_exists']}` |",
        f"| `README.md` includes `make check` | `{result['readme_has_make_check']}` |",
        f"| `README.md` includes `make ci` | `{result['readme_has_make_ci']}` |",
        f"| `.editorconfig` missing patterns | `{', '.join(result['editorconfig_missing_patterns']) or '-'}` |",
        f"| `.gitattributes` missing patterns | `{', '.join(result['gitattributes_missing_patterns']) or '-'}` |",
        f"| `.gitignore` missing patterns | `{', '.join(result['gitignore_missing_patterns']) or '-'}` |",
        f"| `.dockerignore` missing patterns | `{', '.join(result['dockerignore_missing_patterns']) or '-'}` |",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate repository hygiene baseline.")
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--output-json", type=Path, default=Path("output/repository-hygiene-validation.json"))
    parser.add_argument(
        "--output-markdown",
        type=Path,
        default=Path("output/repository-hygiene-validation.md"),
    )
    args = parser.parse_args()

    result = validate_repository_hygiene(args.repo_root.resolve())
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, indent=2), encoding="utf-8")
    args.output_markdown.write_text(build_markdown_report(result), encoding="utf-8")

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
