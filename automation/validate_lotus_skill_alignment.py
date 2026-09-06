from __future__ import annotations

import hashlib
import json
import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path


PLATFORM_ROOT = Path(__file__).resolve().parents[1]
PLATFORM_SKILLS_ROOT = PLATFORM_ROOT / "codex" / "skills"
DEFAULT_LOCAL_SKILLS_ROOT = Path.home() / ".codex" / "skills"
SKILL_MANIFEST_PATH = PLATFORM_ROOT / "codex" / "skills" / "lotus-skill-manifest.json"
UNIVERSAL_SKILL_REQUIREMENTS = [
    "Continuous Skill Improvement",
    "At the end of any meaningful use of this skill",
    "repeatable failure",
    "platform-owned skill source",
]
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
    "lotus-skill-context-governance": [
        "LOTUS-QUICKSTART-CONTEXT.md",
        "LOTUS-ENGINEERING-CONTEXT.md",
        "REPOSITORY-ENGINEERING-CONTEXT.md",
        "CONTEXT-REFERENCE-MAP.md",
        "PROCEDURAL-MEMORY-INDEX.md",
        "LOTUS-SKILL-ROUTING-MAP.md",
        "lotus-skill-manifest.json",
        "codex/skills/README.md",
        "references/skill-context-audit-standard.md",
        "scripts/audit_lotus_skills.py",
        "Bootstrap-LotusDeveloperEnvironment.ps1",
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
    checked_path: str | None = None


def _load_manifest_skills() -> list[dict[str, str]]:
    if not SKILL_MANIFEST_PATH.exists():
        return [
            {"name": skill_name, "path": f"codex/skills/{skill_name}"}
            for skill_name in sorted(REQUIRED_SKILL_REFERENCES)
        ]

    manifest = json.loads(SKILL_MANIFEST_PATH.read_text(encoding="utf-8"))
    return sorted(
        (
            {
                "name": skill["name"],
                "path": skill.get("path", f"codex/skills/{skill['name']}"),
            }
            for skill in manifest.get("skills", [])
        ),
        key=lambda skill: skill["name"],
    )


def _skill_path(skills_root: Path, manifest_skill: dict[str, str]) -> Path:
    if skills_root.resolve() == PLATFORM_SKILLS_ROOT.resolve():
        return PLATFORM_ROOT / manifest_skill["path"] / "SKILL.md"
    return skills_root / manifest_skill["name"] / "SKILL.md"


def validate_lotus_skill_alignment(skills_root: Path = PLATFORM_SKILLS_ROOT) -> list[SkillAlignmentResult]:
    results: list[SkillAlignmentResult] = []
    for manifest_skill in _load_manifest_skills():
        skill_name = manifest_skill["name"]
        required_references = [
            *UNIVERSAL_SKILL_REQUIREMENTS,
            *REQUIRED_SKILL_REFERENCES.get(skill_name, []),
        ]
        skill_path = _skill_path(skills_root, manifest_skill)
        if not skill_path.exists():
            results.append(
                SkillAlignmentResult(
                    skill=skill_name,
                    status="skipped",
                    missing_references=[],
                    notes=[f"skill not present under {skills_root}"],
                    checked_path=str(skill_path),
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
                checked_path=str(skill_path),
            )
        )
    return results



def compare_deployed_to_platform(local_root: Path = DEFAULT_LOCAL_SKILLS_ROOT) -> list[str]:
    """Report skills whose deployed copy differs from the platform source.

    A running agent loads the DEPLOYED copy, so platform content that has not
    been synced has no effect however correct it is. Checking that a skill
    contains required phrases cannot see this: both copies contain them while
    one is missing whole paragraphs. Content is compared by digest, with line
    endings normalised so a checkout convention is not reported as drift.
    """
    if not local_root.exists():
        return []

    findings: list[str] = []
    for source in sorted(PLATFORM_SKILLS_ROOT.glob("*/SKILL.md")):
        skill = source.parent.name
        deployed = local_root / skill / "SKILL.md"
        if not deployed.exists():
            findings.append(f"{skill}: deployed copy is missing")
            continue
        source_digest = hashlib.sha256(source.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        deployed_digest = hashlib.sha256(
            deployed.read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        if source_digest != deployed_digest:
            findings.append(
                f"{skill}: deployed copy differs from the platform source "
                f"(deployed {len(deployed.read_text(encoding='utf-8').splitlines())} lines, "
                f"platform {len(source.read_text(encoding='utf-8').splitlines())} lines)"
            )
    return findings


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
    parser = ArgumentParser(description="Validate Lotus skill alignment requirements.")
    parser.add_argument(
        "--skills-root",
        type=Path,
        default=PLATFORM_SKILLS_ROOT,
        help="Skill root to validate. Defaults to the platform-owned source under codex/skills.",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Validate the deployed local Codex skill consumer instead of the platform-owned source.",
    )
    args = parser.parse_args()

    skills_root = DEFAULT_LOCAL_SKILLS_ROOT if args.local else args.skills_root
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

    # Parity is the check this validator's name promises and did not perform:
    # phrase presence passes on both copies while one lacks whole paragraphs.
    parity_findings = compare_deployed_to_platform()
    if parity_findings:
        print(
            "Lotus skill alignment validation failed: deployed skills differ from the "
            "platform source, so agents are loading stale guidance:",
            file=sys.stderr,
        )
        for finding in parity_findings:
            print(f"- {finding}", file=sys.stderr)
        return 1

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
