from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT_PATH = (
    ROOT
    / "codex"
    / "skills"
    / "lotus-skill-context-governance"
    / "scripts"
    / "audit_lotus_skills.py"
)


def _audit_module():
    spec = importlib.util.spec_from_file_location("audit_lotus_skills", AUDIT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_current_lotus_skill_inventory_has_no_context_audit_findings() -> None:
    assert _audit_module().audit() == []


def test_skill_audit_reports_undiscoverable_references(tmp_path: Path, monkeypatch) -> None:
    module = _audit_module()
    platform_root = tmp_path
    skills_root = platform_root / "codex" / "skills"
    skill_dir = skills_root / "example-skill"
    reference_dir = skill_dir / "references"
    agents_dir = skill_dir / "agents"
    reference_dir.mkdir(parents=True)
    agents_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        """---
name: example-skill
description: Use when validating that reference files are discoverable from skill body text during Lotus skill context governance reviews, audits, and reusable guardrail maintenance.
---

# Example Skill

## Continuous Skill Improvement

Keep future guidance reachable.
""",
        encoding="utf-8",
    )
    (reference_dir / "hidden-reference.md").write_text("# Hidden\n", encoding="utf-8")
    (agents_dir / "openai.yaml").write_text(
        'default_prompt: "Use the example skill."\nshort_description: "Example."\n',
        encoding="utf-8",
    )
    manifest_path = skills_root / "lotus-skill-manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "skills": [
                    {
                        "name": "example-skill",
                        "path": "codex/skills/example-skill",
                        "directly_lotus_owned": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    routing_map = platform_root / "context" / "LOTUS-SKILL-ROUTING-MAP.md"
    routing_map.parent.mkdir()
    routing_map.write_text("example-skill\n", encoding="utf-8")

    monkeypatch.setattr(module, "PLATFORM_ROOT", platform_root)
    monkeypatch.setattr(module, "SKILLS_ROOT", skills_root)
    monkeypatch.setattr(module, "MANIFEST_PATH", manifest_path)
    monkeypatch.setattr(module, "ROUTING_MAP_PATH", routing_map)

    findings = module.audit()

    assert [finding.code for finding in findings] == ["reference-undiscoverable"]
