from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STANDARDS_ROOT = ROOT / "platform-standards"
TEMPLATES_ROOT = STANDARDS_ROOT / "templates"
WORKFLOW_TEMPLATES_ROOT = TEMPLATES_ROOT / "workflows"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _require(text: str, needle: str, label: str, errors: list[str]) -> None:
    if needle not in text:
        errors.append(f"{label}: missing `{needle}`")


def validate_container_build_baseline() -> list[str]:
    errors: list[str] = []

    dockerignore_template = _read(TEMPLATES_ROOT / ".dockerignore.backend.template")
    dockerfile_template = _read(TEMPLATES_ROOT / "Dockerfile.python-service.template")
    pr_merge_gate_template = _read(WORKFLOW_TEMPLATES_ROOT / "pr-merge-gate.backend.template.yml")
    main_releasability_template = _read(
        WORKFLOW_TEMPLATES_ROOT / "main-releasability.backend.template.yml"
    )
    standard = _read(STANDARDS_ROOT / "Container-Build-and-Image-Engineering-Standard.md")

    for pattern in (
        ".git",
        ".venv",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        ".coverage",
        "htmlcov",
        "output",
        "docs",
        "tests",
        "node_modules",
    ):
        _require(dockerignore_template, pattern, ".dockerignore backend template", errors)

    for needle in (
        "# syntax=docker/dockerfile:1.7",
        "@sha256:",
        "FROM ${PYTHON_IMAGE} AS runtime-base",
        "FROM ${PYTHON_IMAGE} AS wheel-builder",
        "FROM runtime-base AS final",
        "PIP_ROOT_USER_ACTION=ignore",
        "RUN --mount=type=cache,target=/root/.cache/pip",
        "USER appuser",
    ):
        _require(dockerfile_template, needle, "Dockerfile backend template", errors)

    for workflow_name, workflow_text in (
        ("PR merge gate template", pr_merge_gate_template),
        ("Main releasability template", main_releasability_template),
    ):
        for needle in (
            'DOCKER_BUILDKIT: "1"',
            'COMPOSE_DOCKER_CLI_BUILD: "1"',
            "docker/setup-buildx-action@v4",
            "Validate Docker Build",
        ):
            _require(workflow_text, needle, workflow_name, errors)

    for needle in (
        "BuildKit Cache Mounts",
        "docker/setup-buildx-action",
        "run as non-root",
        "multi-stage",
    ):
        _require(standard, needle, "Container build standard", errors)

    return errors


def main() -> int:
    errors = validate_container_build_baseline()
    if errors:
        print("Container build baseline validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Container build baseline validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
