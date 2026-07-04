from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "automation" / "validate_lotus_skill_alignment.py"


def _load_validator_module():
    spec = importlib.util.spec_from_file_location("validate_lotus_skill_alignment", VALIDATOR_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_skill_alignment_validator_reports_gaps_and_skips(tmp_path: Path) -> None:
    validator = _load_validator_module()
    skills_root = tmp_path / "skills"
    skills_root.mkdir()

    backend_skill_dir = skills_root / "lotus-backend-delivery-governance"
    backend_skill_dir.mkdir()
    (backend_skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: lotus-backend-delivery-governance",
                'description: "fixture"',
                "---",
                "LOTUS-ENGINEERING-CONTEXT.md",
                "PROCEDURAL-MEMORY-INDEX.md",
                "CHANGE-PLAYBOOKS.md",
            ]
        ),
        encoding="utf-8",
    )

    results = validator.validate_lotus_skill_alignment(skills_root)
    result_by_skill = {result.skill: result for result in results}

    assert result_by_skill["lotus-backend-delivery-governance"].status == "gap"
    assert result_by_skill["lotus-backend-delivery-governance"].missing_references == [
        "Continuous Skill Improvement",
        "VALIDATION-PLAYBOOK.md",
    ]
    assert result_by_skill["lotus-frontend-delivery-governance"].status == "skipped"

    markdown = validator.build_markdown(results, skills_root)
    assert "Lotus Skill Alignment Validation" in markdown
    assert "lotus-backend-delivery-governance" in markdown
    assert "Continuous Skill Improvement" in markdown
    assert "VALIDATION-PLAYBOOK.md" in markdown
