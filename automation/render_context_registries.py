from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "context" / "lotus-context-manifest.json"
OUTPUT_PATH = ROOT / "context" / "ECOSYSTEM-REGISTRIES.md"


def _format_bool(value: bool) -> str:
    return "Yes" if value else "No"


def _format_list(values: list[str]) -> str:
    return ", ".join(values) if values else "-"


def render_registry_document(manifest: dict) -> str:
    lines: list[str] = [
        "# Ecosystem Registries",
        "",
        "This file is generated from [lotus-context-manifest.json](./lotus-context-manifest.json) by `automation/render_context_registries.py`.",
        "",
        f"- Last reviewed on: `{manifest['last_reviewed_on']}`",
        "",
        "## Application Registry",
        "",
        "| Repository | Category | Business Role | Runtime | Repo Context | Quality Commands | Platform E2E |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    for app in manifest["applications"]:
        quality_commands = ", ".join(f"`{name}: {command}`" for name, command in app["canonical_commands"].items())
        lines.append(
            f"| `{app['repository']}` | `{app['category']}` | {app['business_role']} | `{app['primary_runtime']}` | `{app['repo_context_path']}` | {quality_commands} | {_format_bool(app['requires_platform_end_to_end_validation'])} |"
        )

    lines.extend(
        [
            "",
            "## Domain Authority Map",
            "",
            "| Domain | Authoritative Repository | Composition Layers |",
            "| --- | --- | --- |",
        ]
    )

    for domain_entry in manifest["domain_authority_map"]:
        lines.append(
            f"| `{domain_entry['domain']}` | `{domain_entry['authoritative_repository']}` | {_format_list(domain_entry['composition_layers'])} |"
        )

    lines.extend(
        [
            "",
            "## Standards Registry",
            "",
            "| Standard | Scope | Source Path |",
            "| --- | --- | --- |",
        ]
    )

    for standard in manifest["standards_registry"]:
        lines.append(f"| {standard['name']} | `{standard['scope']}` | `{standard['path']}` |")

    lines.extend(
        [
            "",
            "## Active RFC Registry",
            "",
            "| RFC | Status | Implementation Posture | Title |",
            "| --- | --- | --- | --- |",
        ]
    )

    for rfc in manifest["active_rfc_registry"]:
        lines.append(
            f"| `{rfc['id']}` | `{rfc['status']}` | {rfc['implementation_posture']} | {rfc['title']} |"
        )

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    OUTPUT_PATH.write_text(render_registry_document(manifest), encoding="utf-8")


if __name__ == "__main__":
    main()
