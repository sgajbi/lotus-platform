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


def validate_repository_hygiene(repo_root: Path) -> dict[str, object]:
    gitignore = repo_root / ".gitignore"
    dockerignore = repo_root / ".dockerignore"
    readme = repo_root / "README.md"

    gitignore_content = _read_text_if_exists(gitignore)
    dockerignore_content = _read_text_if_exists(dockerignore)
    readme_content = _read_text_if_exists(readme)
    dependency_authority = determine_dependency_authority(repo_root)

    result = {
        "repo_root": str(repo_root),
        "gitignore_exists": gitignore.exists(),
        "dockerignore_exists": dockerignore.exists(),
        "readme_exists": readme.exists(),
        "dependency_authority": dependency_authority,
        "gitignore_missing_patterns": _missing_patterns(gitignore_content, REQUIRED_GITIGNORE_PATTERNS),
        "dockerignore_missing_patterns": _missing_patterns(dockerignore_content, REQUIRED_DOCKERIGNORE_PATTERNS),
        "readme_has_make_check": "make check" in readme_content,
        "readme_has_make_ci": "make ci" in readme_content,
    }
    result["ok"] = (
        result["gitignore_exists"]
        and result["dockerignore_exists"]
        and result["readme_exists"]
        and result["dependency_authority"] == "pyproject"
        and not result["gitignore_missing_patterns"]
        and not result["dockerignore_missing_patterns"]
        and result["readme_has_make_check"]
        and result["readme_has_make_ci"]
    )
    return result


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
        f"| `.gitignore` present | `{result['gitignore_exists']}` |",
        f"| `.dockerignore` present | `{result['dockerignore_exists']}` |",
        f"| `README.md` present | `{result['readme_exists']}` |",
        f"| `README.md` includes `make check` | `{result['readme_has_make_check']}` |",
        f"| `README.md` includes `make ci` | `{result['readme_has_make_ci']}` |",
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
