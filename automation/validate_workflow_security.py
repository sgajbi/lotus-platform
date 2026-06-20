from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_GLOBS = (
    ROOT / ".github" / "workflows",
    ROOT / "platform-standards" / "templates" / "workflows",
)

WRITE_SUFFIX = ": write"
ALLOWLIST = {
    "platform-standards/templates/workflows/pr-auto-merge.template.yml": {
        "allow_pull_request_target": True,
        "required_permissions": {
            "contents": "write",
            "pull-requests": "write",
        },
    }
}


@dataclass
class WorkflowSecurityResult:
    workflow_path: str
    ok: bool
    missing_permissions: bool
    has_pull_request_target: bool
    unexpected_pull_request_target: bool
    write_permissions: dict[str, str]
    unexpected_write_permissions: dict[str, str]
    notes: list[str]


def iter_workflow_paths() -> list[Path]:
    workflow_paths: list[Path] = []
    for base in WORKFLOW_GLOBS:
        workflow_paths.extend(sorted(base.glob("*.yml")))
        workflow_paths.extend(sorted(base.glob("*.yaml")))
    return workflow_paths


def relative_workflow_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def normalize_permissions(raw_permissions: object) -> dict[str, str]:
    if isinstance(raw_permissions, dict):
        return {str(key): str(value) for key, value in raw_permissions.items()}
    if isinstance(raw_permissions, str):
        return {"__scalar__": raw_permissions}
    return {}


def extract_write_permissions(permissions: dict[str, str]) -> dict[str, str]:
    return {
        key: value
        for key, value in permissions.items()
        if value == "write" or value == "write-all" or value.endswith(WRITE_SUFFIX)
    }


def _load_workflow_payload(path: Path) -> dict:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return payload if isinstance(payload, dict) else {}


def _workflow_triggers(payload: dict) -> object:
    return payload.get("on", payload.get(True, {})) or {}


def _has_pull_request_target(payload: dict) -> bool:
    triggers = _workflow_triggers(payload)
    return "pull_request_target" in triggers


def _unexpected_pull_request_target(
    *,
    has_pull_request_target: bool,
    allowlist_entry: dict | None,
) -> bool:
    return has_pull_request_target and not (
        allowlist_entry and allowlist_entry.get("allow_pull_request_target")
    )


def _unexpected_write_permissions(
    *,
    write_permissions: dict[str, str],
    allowlist_entry: dict | None,
) -> dict[str, str]:
    unexpected = dict(write_permissions)
    if not allowlist_entry:
        return unexpected
    required_permissions = allowlist_entry.get("required_permissions", {})
    for key, value in list(unexpected.items()):
        if required_permissions.get(key) == value:
            unexpected.pop(key)
    return unexpected


def _workflow_security_notes(
    *,
    missing_permissions: bool,
    unexpected_pull_request_target: bool,
    write_permissions: dict[str, str],
    allowlist_entry: dict | None,
) -> list[str]:
    notes: list[str] = []
    if allowlist_entry:
        required_permissions = allowlist_entry.get("required_permissions", {})
        if write_permissions != required_permissions:
            notes.append("allowlisted workflow permissions drifted from approved set")
    elif write_permissions:
        notes.append("workflow requests write permissions without allowlist approval")

    if missing_permissions:
        notes.append("workflow missing top-level permissions")
    if unexpected_pull_request_target:
        notes.append("workflow uses pull_request_target without allowlist approval")
    return notes


def _workflow_security_ok(
    *,
    missing_permissions: bool,
    unexpected_pull_request_target: bool,
    unexpected_write_permissions: dict[str, str],
    write_permissions: dict[str, str],
    allowlist_entry: dict | None,
) -> bool:
    return (
        not missing_permissions
        and not unexpected_pull_request_target
        and not unexpected_write_permissions
        and (not allowlist_entry or write_permissions == allowlist_entry["required_permissions"])
    )


def validate_workflow(path: Path) -> WorkflowSecurityResult:
    relative_path = relative_workflow_path(path)
    allowlist_entry = ALLOWLIST.get(relative_path)

    payload = _load_workflow_payload(path)
    permissions = normalize_permissions(payload.get("permissions"))
    has_pull_request_target = _has_pull_request_target(payload)
    write_permissions = extract_write_permissions(permissions)

    missing_permissions = not permissions
    unexpected_pull_request_target = _unexpected_pull_request_target(
        has_pull_request_target=has_pull_request_target,
        allowlist_entry=allowlist_entry,
    )
    unexpected_write_permissions = _unexpected_write_permissions(
        write_permissions=write_permissions,
        allowlist_entry=allowlist_entry,
    )
    notes = _workflow_security_notes(
        missing_permissions=missing_permissions,
        unexpected_pull_request_target=unexpected_pull_request_target,
        write_permissions=write_permissions,
        allowlist_entry=allowlist_entry,
    )
    ok = _workflow_security_ok(
        missing_permissions=missing_permissions,
        unexpected_pull_request_target=unexpected_pull_request_target,
        unexpected_write_permissions=unexpected_write_permissions,
        write_permissions=write_permissions,
        allowlist_entry=allowlist_entry,
    )

    return WorkflowSecurityResult(
        workflow_path=relative_path,
        ok=ok,
        missing_permissions=missing_permissions,
        has_pull_request_target=has_pull_request_target,
        unexpected_pull_request_target=unexpected_pull_request_target,
        write_permissions=write_permissions,
        unexpected_write_permissions=unexpected_write_permissions,
        notes=notes,
    )


def build_markdown(results: list[WorkflowSecurityResult]) -> str:
    lines = [
        "# Workflow Security Validation",
        "",
        "| Workflow | Status | Permissions | pull_request_target | Notes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for result in results:
        lines.append(
            f"| `{result.workflow_path}` | `{'ok' if result.ok else 'gap'}` | "
            f"`{result.write_permissions or '-'}` | `{result.has_pull_request_target}` | "
            f"`{' ; '.join(result.notes) or '-'}` |"
        )
    return "\n".join(lines)


def main() -> int:
    results = [validate_workflow(path) for path in iter_workflow_paths()]
    output_dir = ROOT / "output"
    output_dir.mkdir(exist_ok=True)
    (output_dir / "workflow-security-validation.json").write_text(
        json.dumps([result.__dict__ for result in results], indent=2),
        encoding="utf-8",
    )
    (output_dir / "workflow-security-validation.md").write_text(
        build_markdown(results),
        encoding="utf-8",
    )
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
