from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


PLATFORM_ROOT = Path(__file__).resolve().parents[4]
SKILLS_ROOT = PLATFORM_ROOT / "codex" / "skills"
MANIFEST_PATH = SKILLS_ROOT / "lotus-skill-manifest.json"
ROUTING_MAP_PATH = PLATFORM_ROOT / "context" / "LOTUS-SKILL-ROUTING-MAP.md"
OUTPUT_JSON = PLATFORM_ROOT / "output" / "lotus-skill-context-audit.json"
OUTPUT_MD = PLATFORM_ROOT / "output" / "lotus-skill-context-audit.md"


@dataclass
class Finding:
    skill: str
    severity: str
    code: str
    message: str
    path: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(skill_path: Path) -> dict[str, str]:
    text = read_text(skill_path)
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    frontmatter = text[4:end].strip().splitlines()
    parsed: dict[str, str] = {}
    for line in frontmatter:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        parsed[key.strip()] = value.strip().strip('"')
    return parsed


def manifest_skills() -> dict[str, dict[str, object]]:
    manifest = json.loads(read_text(MANIFEST_PATH))
    return {skill["name"]: skill for skill in manifest.get("skills", [])}


def skill_dirs() -> list[Path]:
    return sorted(
        path
        for path in SKILLS_ROOT.iterdir()
        if path.is_dir() and (path / "SKILL.md").exists()
    )


def has_toc(text: str) -> bool:
    return "## Contents" in text or "## Table Of Contents" in text or "## Table of Contents" in text


def _finding(
    skill: str,
    severity: str,
    code: str,
    message: str,
    path: Path,
) -> Finding:
    return Finding(skill, severity, code, message, str(path))


def _frontmatter_findings(
    *,
    skill_name: str,
    skill_path: Path,
    frontmatter: dict[str, str],
    description: str,
) -> list[Finding]:
    findings: list[Finding] = []
    extra_keys = sorted(set(frontmatter) - {"name", "description"})
    if extra_keys:
        findings.append(
            _finding(
                skill_name,
                "medium",
                "frontmatter-extra",
                f"Frontmatter has non-standard keys: {', '.join(extra_keys)}.",
                skill_path,
            )
        )
    if frontmatter.get("name") != skill_name:
        findings.append(
            _finding(
                skill_name,
                "high",
                "frontmatter-name",
                "Frontmatter name does not match folder name.",
                skill_path,
            )
        )
    if len(description) < 120:
        findings.append(
            _finding(
                skill_name,
                "medium",
                "description-short",
                "Description may be too short to route reliably.",
                skill_path,
            )
        )
    if len(description) > 1024:
        findings.append(
            _finding(
                skill_name,
                "critical",
                "description-long",
                "Description exceeds 1024 characters.",
                skill_path,
            )
        )
    if "use when" not in description.lower() and "apply when" not in description.lower():
        findings.append(
            _finding(
                skill_name,
                "medium",
                "description-trigger",
                "Description does not clearly include use/apply trigger wording.",
                skill_path,
            )
        )
    return findings


def _skill_body_findings(
    *, skill_name: str, skill_path: Path, skill_text: str
) -> list[Finding]:
    findings: list[Finding] = []
    line_count = skill_text.count("\n") + 1
    if line_count > 500:
        findings.append(
            _finding(
                skill_name,
                "medium",
                "skill-body-large",
                f"SKILL.md has {line_count} lines; consider moving details to references.",
                skill_path,
            )
        )
    if "Continuous Skill Improvement" not in skill_text:
        findings.append(
            _finding(
                skill_name,
                "high",
                "continuous-improvement-missing",
                "Skill lacks Continuous Skill Improvement section.",
                skill_path,
            )
        )
    return findings


def _metadata_findings(
    *,
    skill_name: str,
    skill_dir: Path,
    manifest_entry: dict[str, object] | None,
    routing_text: str,
) -> list[Finding]:
    findings: list[Finding] = []
    agents_yaml = skill_dir / "agents" / "openai.yaml"
    directly_owned = bool(manifest_entry and manifest_entry.get("directly_lotus_owned"))
    if directly_owned and not agents_yaml.exists():
        findings.append(
            _finding(
                skill_name,
                "medium",
                "openai-metadata-missing",
                "Directly Lotus-owned skill lacks agents/openai.yaml.",
                agents_yaml,
            )
        )
    if agents_yaml.exists():
        agent_text = read_text(agents_yaml)
        if "default_prompt:" not in agent_text or "short_description:" not in agent_text:
            findings.append(
                _finding(
                    skill_name,
                    "medium",
                    "openai-metadata-incomplete",
                    "agents/openai.yaml is missing expected interface fields.",
                    agents_yaml,
                )
            )
    if directly_owned and skill_name not in routing_text:
        findings.append(
            _finding(
                skill_name,
                "medium",
                "routing-missing",
                "Directly Lotus-owned skill is not referenced in LOTUS-SKILL-ROUTING-MAP.md.",
                ROUTING_MAP_PATH,
            )
        )
    return findings


def _reference_findings(
    *, skill_name: str, skill_dir: Path, skill_text: str
) -> list[Finding]:
    findings: list[Finding] = []
    for reference_path in sorted((skill_dir / "references").glob("*.md")):
        reference_text = read_text(reference_path)
        reference_lines = reference_text.count("\n") + 1
        if reference_lines > 100 and not has_toc(reference_text):
            findings.append(
                _finding(
                    skill_name,
                    "low",
                    "reference-toc-missing",
                    f"Reference has {reference_lines} lines without a contents section.",
                    reference_path,
                )
            )
        if reference_path.name not in skill_text:
            findings.append(
                _finding(
                    skill_name,
                    "low",
                    "reference-undiscoverable",
                    "Reference file is not named from SKILL.md.",
                    reference_path,
                )
            )
    return findings


def _script_findings(
    *, skill_name: str, skill_dir: Path, skill_text: str
) -> list[Finding]:
    findings: list[Finding] = []
    for script_path in sorted((skill_dir / "scripts").glob("*")):
        if not script_path.is_file() or script_path.suffix not in {".py", ".ps1"}:
            continue
        if script_path.name not in skill_text:
            findings.append(
                _finding(
                    skill_name,
                    "low",
                    "script-undiscoverable",
                    "Script is not named from SKILL.md.",
                    script_path,
                )
            )
    return findings


def _audit_skill_dir(
    skill_dir: Path,
    *,
    manifest: dict[str, dict[str, object]],
    routing_text: str,
) -> list[Finding]:
    skill_name = skill_dir.name
    skill_path = skill_dir / "SKILL.md"
    skill_text = read_text(skill_path)
    frontmatter = parse_frontmatter(skill_path)
    manifest_entry = manifest.get(skill_name)
    findings: list[Finding] = []

    if manifest_entry is None:
        findings.append(
            _finding(
                skill_name,
                "high",
                "manifest-missing",
                "Skill folder is absent from lotus-skill-manifest.json.",
                skill_path,
            )
        )
    findings.extend(
        _frontmatter_findings(
            skill_name=skill_name,
            skill_path=skill_path,
            frontmatter=frontmatter,
            description=frontmatter.get("description", ""),
        )
    )
    findings.extend(_skill_body_findings(skill_name=skill_name, skill_path=skill_path, skill_text=skill_text))
    findings.extend(
        _metadata_findings(
            skill_name=skill_name,
            skill_dir=skill_dir,
            manifest_entry=manifest_entry,
            routing_text=routing_text,
        )
    )
    findings.extend(
        _reference_findings(
            skill_name=skill_name, skill_dir=skill_dir, skill_text=skill_text
        )
    )
    findings.extend(
        _script_findings(skill_name=skill_name, skill_dir=skill_dir, skill_text=skill_text)
    )
    return findings


def _manifest_path_findings(
    manifest: dict[str, dict[str, object]],
) -> list[Finding]:
    findings: list[Finding] = []
    for manifest_name, entry in manifest.items():
        skill_path = (
            PLATFORM_ROOT
            / str(entry.get("path", f"codex/skills/{manifest_name}"))
            / "SKILL.md"
        )
        if not skill_path.exists():
            findings.append(
                _finding(
                    manifest_name,
                    "critical",
                    "manifest-path-missing",
                    "Manifest points to a missing skill path.",
                    skill_path,
                )
            )
    return findings


def audit() -> list[Finding]:
    manifest = manifest_skills()
    routing_text = read_text(ROUTING_MAP_PATH) if ROUTING_MAP_PATH.exists() else ""
    findings = [
        finding
        for skill_dir in skill_dirs()
        for finding in _audit_skill_dir(
            skill_dir, manifest=manifest, routing_text=routing_text
        )
    ]
    findings.extend(_manifest_path_findings(manifest))

    return sorted(findings, key=lambda item: (["critical", "high", "medium", "low"].index(item.severity), item.skill, item.code))


def render_markdown(findings: list[Finding]) -> str:
    counts = {severity: sum(1 for finding in findings if finding.severity == severity) for severity in ["critical", "high", "medium", "low"]}
    lines = [
        "# Lotus Skill Context Audit",
        "",
        f"- Skills root: `{SKILLS_ROOT}`",
        f"- Findings: critical={counts['critical']}, high={counts['high']}, medium={counts['medium']}, low={counts['low']}",
        "",
        "| Severity | Skill | Code | Finding | Path |",
        "| --- | --- | --- | --- | --- |",
    ]
    if findings:
        for finding in findings:
            path = finding.path.replace("\\", "/")
            message = re.sub(r"\s+", " ", finding.message)
            lines.append(f"| `{finding.severity}` | `{finding.skill}` | `{finding.code}` | {message} | `{path}` |")
    else:
        lines.append("| - | - | - | No findings. | - |")
    return "\n".join(lines) + "\n"


def main() -> int:
    findings = audit()
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps([asdict(finding) for finding in findings], indent=2), encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(findings), encoding="utf-8")
    print(f"Wrote {OUTPUT_MD}")
    high_or_worse = [finding for finding in findings if finding.severity in {"critical", "high"}]
    return 1 if high_or_worse else 0


if __name__ == "__main__":
    raise SystemExit(main())
