from __future__ import annotations

import ast
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
PLATFORM_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_JSON = PLATFORM_ROOT / "output" / "issue-discovery-skill-validation.json"
OUTPUT_MD = PLATFORM_ROOT / "output" / "issue-discovery-skill-validation.md"
CONTROL_CATALOG_RELATIVE_PATH = (
    "platform-contracts/bank-readiness/bank-ready-control-catalog.v1.json"
)
REQUIRED_BANK_READINESS_LENSES = {
    "lens/secure-development-threat-modeling",
    "lens/identity-access-management",
    "lens/container-runtime-hardening",
    "lens/vulnerability-management",
    "lens/incident-response",
}


@dataclass
class Finding:
    severity: str
    code: str
    message: str
    path: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def labels_from_review_catalog() -> tuple[set[str], set[str]]:
    text = read_text(SKILL_ROOT / "references" / "review-lenses.md")
    lens_labels = set(re.findall(r"`(lens/[a-z0-9-]+)`", text))
    impact_labels = set(re.findall(r"`(impact/[a-z0-9-]+)`", text))
    return lens_labels, impact_labels


def labels_from_label_script() -> set[str]:
    script_path = SKILL_ROOT / "scripts" / "ensure_issue_discovery_labels.py"
    module = ast.parse(read_text(script_path), filename=str(script_path))
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "LABELS":
                    labels: set[str] = set()
                    for entry in ast.literal_eval(node.value):
                        labels.add(entry[0])
                    return labels
    raise ValueError("LABELS assignment not found")


def labels_from_ledger_template() -> set[str]:
    text = read_text(SKILL_ROOT / "references" / "lens-coverage-ledger-template.md")
    return set(re.findall(r"`(lens/[a-z0-9-]+)`", text))


def validate() -> list[Finding]:
    findings: list[Finding] = []
    review_lens_labels, review_impact_labels = labels_from_review_catalog()
    script_labels = labels_from_label_script()
    ledger_lens_labels = labels_from_ledger_template()

    required_non_lens = {"issue-discovery", *review_impact_labels}
    missing_from_script = sorted((review_lens_labels | required_non_lens) - script_labels)
    if missing_from_script:
        findings.append(
            Finding(
                "high",
                "label-script-missing",
                f"Catalog labels missing from ensure_issue_discovery_labels.py: {', '.join(missing_from_script)}",
                str(SKILL_ROOT / "scripts" / "ensure_issue_discovery_labels.py"),
            )
        )

    missing_from_ledger = sorted(review_lens_labels - ledger_lens_labels)
    if missing_from_ledger:
        findings.append(
            Finding(
                "medium",
                "ledger-template-missing",
                f"Catalog lens labels missing from lens-coverage-ledger-template.md: {', '.join(missing_from_ledger)}",
                str(SKILL_ROOT / "references" / "lens-coverage-ledger-template.md"),
            )
        )

    review_text = read_text(SKILL_ROOT / "references" / "review-lenses.md")
    for phrase in ["Acceptance criteria", "Evaluation condition", "AI readiness", "Enterprise readiness"]:
        if phrase not in review_text:
            findings.append(
                Finding(
                    "medium",
                    "catalog-standard-gap",
                    f"Review lens catalog is missing expected phrase: {phrase}",
                    str(SKILL_ROOT / "references" / "review-lenses.md"),
                )
            )

    missing_bank_lenses = sorted(REQUIRED_BANK_READINESS_LENSES - review_lens_labels)
    if missing_bank_lenses:
        findings.append(
            Finding(
                "high",
                "bank-readiness-lens-missing",
                "Required bank-readiness lenses missing from the review catalog: "
                + ", ".join(missing_bank_lenses),
                str(SKILL_ROOT / "references" / "review-lenses.md"),
            )
        )

    skill_text = read_text(SKILL_ROOT / "SKILL.md")
    for script_name in [
        "ensure_issue_discovery_labels.py",
        "validate_issue_discovery_skill.py",
        "plan_issue_discovery_campaign.py",
    ]:
        if script_name not in skill_text:
            findings.append(
                Finding(
                    "low",
                    "script-undiscoverable",
                    f"SKILL.md does not mention {script_name}.",
                    str(SKILL_ROOT / "SKILL.md"),
                )
            )

    for required_reference in (
        CONTROL_CATALOG_RELATIVE_PATH,
        "LOTUS_BANK_READY_ENGINEERING_IMPLEMENTATION_PLAYBOOK.md",
        "--include-bank-readiness",
    ):
        if required_reference not in skill_text:
            findings.append(
                Finding(
                    "high",
                    "bank-readiness-routing-missing",
                    f"SKILL.md does not route through {required_reference}.",
                    str(SKILL_ROOT / "SKILL.md"),
                )
            )

    planner_text = read_text(SKILL_ROOT / "scripts" / "plan_issue_discovery_campaign.py")
    for required_planner_contract in (
        "--include-bank-readiness",
        "CATALOG_PROFILE_BY_DISCOVERY_PROFILE",
        "minimum_evidence_class",
    ):
        if required_planner_contract not in planner_text:
            findings.append(
                Finding(
                    "high",
                    "bank-readiness-planner-missing",
                    f"Campaign planner does not preserve {required_planner_contract}.",
                    str(
                        SKILL_ROOT
                        / "scripts"
                        / "plan_issue_discovery_campaign.py"
                    ),
                )
            )

    return findings


def render_markdown(findings: list[Finding]) -> str:
    lines = [
        "# Lotus Issue-Discovery Skill Validation",
        "",
        f"- Skill root: `{SKILL_ROOT}`",
        f"- Findings: {len(findings)}",
        "",
        "| Severity | Code | Finding | Path |",
        "| --- | --- | --- | --- |",
    ]
    if not findings:
        lines.append("| - | - | No findings. | - |")
    else:
        for finding in findings:
            path = finding.path.replace("\\", "/")
            lines.append(f"| `{finding.severity}` | `{finding.code}` | {finding.message} | `{path}` |")
    return "\n".join(lines) + "\n"


def main() -> int:
    findings = validate()
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps([asdict(finding) for finding in findings], indent=2), encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(findings), encoding="utf-8")
    print(f"Wrote {OUTPUT_MD}")
    return 1 if any(finding.severity in {"critical", "high"} for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
