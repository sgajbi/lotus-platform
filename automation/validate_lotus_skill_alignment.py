from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path


DEFAULT_SKILLS_ROOT = Path.home() / ".codex" / "skills"
PLATFORM_ROOT = Path(__file__).resolve().parents[1]
SKILL_MANIFEST_PATH = PLATFORM_ROOT / "codex" / "skills" / "lotus-skill-manifest.json"
UNIVERSAL_SKILL_REQUIREMENTS = ["Continuous Skill Improvement"]
REQUIRED_SKILL_REFERENCES = {
    "lotus-backend-delivery-governance": [
        "LOTUS-ENGINEERING-CONTEXT.md",
        "PROCEDURAL-MEMORY-INDEX.md",
        "CHANGE-PLAYBOOKS.md",
        "VALIDATION-PLAYBOOK.md",
    ],
    "lotus-frontend-delivery-governance": [
        "LOTUS-ENGINEERING-CONTEXT.md",
        "PROCEDURAL-MEMORY-INDEX.md",
        "CHANGE-PLAYBOOKS.md",
        "VALIDATION-PLAYBOOK.md",
        "FIX-FORWARD-PATTERNS.md",
    ],
    "lotus-pr-premerge-gate": [
        "LOTUS-ENGINEERING-CONTEXT.md",
        "PROCEDURAL-MEMORY-INDEX.md",
        "PR-LOOP-PLAYBOOK.md",
        "FIX-FORWARD-PATTERNS.md",
    ],
    "lotus-qa-platform-validator": [
        "LOTUS-ENGINEERING-CONTEXT.md",
        "PROCEDURAL-MEMORY-INDEX.md",
        "VALIDATION-PLAYBOOK.md",
        "FIX-FORWARD-PATTERNS.md",
    ],
    "lotus-validation-resolution-lifecycle": [
        "LOTUS-ENGINEERING-CONTEXT.md",
        "PROCEDURAL-MEMORY-INDEX.md",
        "VALIDATION-PLAYBOOK.md",
        "PR-LOOP-PLAYBOOK.md",
        "FIX-FORWARD-PATTERNS.md",
    ],
    "lotus-app-issue-discovery": [
        "LOTUS-QUICKSTART-CONTEXT.md",
        "LOTUS-ENGINEERING-CONTEXT.md",
        "REPOSITORY-ENGINEERING-CONTEXT.md",
        "CONTEXT-REFERENCE-MAP.md",
        "PROCEDURAL-MEMORY-INDEX.md",
        "ENTERPRISE-BACKEND-REFACTORING-INSTRUCTIONS.md",
        "LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md",
        "docs repo knowledge base",
        "references/review-lenses.md",
        "references/lens-coverage-ledger-template.md",
        "references/campaign-playbook.md",
        "scripts/ensure_issue_discovery_labels.py",
    ],
    "platform-automation-ops": [
        "AGENT-CONTEXT-AND-TASK-LEDGER.md",
        "engineering-task-ledger-contract.v1.json",
        "Start-Background-Run.ps1",
        "Check-Background-Runs.ps1",
        "engineering_task_id",
        "LOST",
    ],
}


@dataclass
class SkillAlignmentResult:
    skill: str
    status: str
    missing_references: list[str]
    notes: list[str]


def _load_manifest_skill_names() -> list[str]:
    if not SKILL_MANIFEST_PATH.exists():
        return sorted(REQUIRED_SKILL_REFERENCES)

    manifest = json.loads(SKILL_MANIFEST_PATH.read_text(encoding="utf-8"))
    return sorted(skill["name"] for skill in manifest.get("skills", []))


def validate_lotus_skill_alignment(skills_root: Path = DEFAULT_SKILLS_ROOT) -> list[SkillAlignmentResult]:
    results: list[SkillAlignmentResult] = []
    for skill_name in _load_manifest_skill_names():
        required_references = [
            *UNIVERSAL_SKILL_REQUIREMENTS,
            *REQUIRED_SKILL_REFERENCES.get(skill_name, []),
        ]
        skill_path = skills_root / skill_name / "SKILL.md"
        if not skill_path.exists():
            results.append(
                SkillAlignmentResult(
                    skill=skill_name,
                    status="skipped",
                    missing_references=[],
                    notes=[f"skill not present under {skills_root}"],
                )
            )
            continue

        content = skill_path.read_text(encoding="utf-8")
        missing_references = [reference for reference in required_references if reference not in content]
        results.append(
            SkillAlignmentResult(
                skill=skill_name,
                status="ok" if not missing_references else "gap",
                missing_references=missing_references,
                notes=[] if not missing_references else ["skill is missing required context-system references"],
            )
        )
    return results


def build_markdown(results: list[SkillAlignmentResult], skills_root: Path) -> str:
    lines = [
        "# Lotus Skill Alignment Validation",
        "",
        f"- Skills root: `{skills_root}`",
        "",
        "| Skill | Status | Missing References | Notes |",
        "| --- | --- | --- | --- |",
    ]
    for result in results:
        missing = ", ".join(result.missing_references) if result.missing_references else "-"
        notes = " ; ".join(result.notes) if result.notes else "-"
        lines.append(f"| `{result.skill}` | `{result.status}` | `{missing}` | `{notes}` |")
    return "\n".join(lines)


def main() -> int:
    skills_root = DEFAULT_SKILLS_ROOT
    results = validate_lotus_skill_alignment(skills_root)
    output_dir = Path(__file__).resolve().parents[1] / "output"
    output_dir.mkdir(exist_ok=True)
    (output_dir / "lotus-skill-alignment-validation.json").write_text(
        json.dumps([result.__dict__ for result in results], indent=2),
        encoding="utf-8",
    )
    (output_dir / "lotus-skill-alignment-validation.md").write_text(
        build_markdown(results, skills_root),
        encoding="utf-8",
    )

    gaps = [result for result in results if result.status == "gap"]
    if gaps:
        print("Lotus skill alignment validation failed:", file=sys.stderr)
        for gap in gaps:
            print(f"- {gap.skill}: missing {', '.join(gap.missing_references)}", file=sys.stderr)
        return 1

    if all(result.status == "skipped" for result in results):
        print("Lotus skill alignment validation skipped because governed skills are not present on this machine.")
        return 0

    print("Lotus skill alignment validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
