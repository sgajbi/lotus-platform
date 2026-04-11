from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_GLOBS = (
    ROOT / ".github" / "workflows",
    ROOT / "platform-standards" / "templates" / "workflows",
)
ACTION_MAJOR_BASELINE = {
    "actions/checkout": 6,
    "actions/setup-python": 6,
    "actions/setup-node": 5,
    "actions/upload-artifact": 5,
}
VERSION_PATTERN = re.compile(r"^(?P<action>[^@]+)@v(?P<major>\d+)$")


@dataclass
class WorkflowActionRuntimeResult:
    workflow_path: str
    ok: bool
    findings: list[str]


def iter_workflow_paths() -> list[Path]:
    workflow_paths: list[Path] = []
    for base in WORKFLOW_GLOBS:
        workflow_paths.extend(sorted(base.glob("*.yml")))
        workflow_paths.extend(sorted(base.glob("*.yaml")))
    return workflow_paths


def relative_workflow_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _collect_uses(payload: Any) -> list[str]:
    uses_values: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key == "uses" and isinstance(value, str):
                uses_values.append(value)
            else:
                uses_values.extend(_collect_uses(value))
    elif isinstance(payload, list):
        for item in payload:
            uses_values.extend(_collect_uses(item))
    return uses_values


def validate_workflow(path: Path) -> WorkflowActionRuntimeResult:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    findings: list[str] = []
    for uses_value in _collect_uses(payload):
        match = VERSION_PATTERN.match(uses_value)
        if not match:
            continue
        action = match.group("action")
        required_major = ACTION_MAJOR_BASELINE.get(action)
        if required_major is None:
            continue
        actual_major = int(match.group("major"))
        if actual_major < required_major:
            findings.append(
                f"{uses_value} is below the required baseline {action}@v{required_major}"
            )

    return WorkflowActionRuntimeResult(
        workflow_path=relative_workflow_path(path),
        ok=not findings,
        findings=findings,
    )


def build_markdown(results: list[WorkflowActionRuntimeResult]) -> str:
    lines = [
        "# Workflow Action Runtime Validation",
        "",
        "| Workflow | Status | Findings |",
        "| --- | --- | --- |",
    ]
    for result in results:
        lines.append(
            f"| `{result.workflow_path}` | `{'ok' if result.ok else 'gap'}` | "
            f"`{' ; '.join(result.findings) or '-'}` |"
        )
    return "\n".join(lines)


def main() -> int:
    results = [validate_workflow(path) for path in iter_workflow_paths()]
    output_dir = ROOT / "output"
    output_dir.mkdir(exist_ok=True)
    (output_dir / "workflow-action-runtime-validation.json").write_text(
        json.dumps([result.__dict__ for result in results], indent=2),
        encoding="utf-8",
    )
    (output_dir / "workflow-action-runtime-validation.md").write_text(
        build_markdown(results),
        encoding="utf-8",
    )
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
