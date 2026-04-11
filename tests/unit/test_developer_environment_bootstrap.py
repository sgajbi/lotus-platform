from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _powershell_executable() -> str:
    executable = shutil.which("pwsh") or shutil.which("powershell")
    assert executable is not None, "pwsh or powershell is required for bootstrap script tests"
    return executable


def _powershell_base_args() -> list[str]:
    args = [_powershell_executable(), "-NoProfile"]
    if os.name == "nt":
        args.extend(["-ExecutionPolicy", "Bypass"])
    return args


def _run_script(script_name: str, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    command = [
        *_powershell_base_args(),
        "-File",
        str(ROOT / "automation" / script_name),
        *args,
    ]
    return subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        check=True,
        text=True,
        capture_output=True,
    )


def test_developer_environment_inspect_report_is_redacted_and_structured(tmp_path: Path) -> None:
    output_dir = tmp_path / "readiness"
    skill_target = tmp_path / "skills"
    agents_target = tmp_path / "AGENTS.md"
    secret_dsn = "postgresql://lotus_user:super-secret-password@localhost:5432/lotus"
    env = os.environ.copy()
    env["DATABASE_URL"] = secret_dsn

    _run_script(
        "Validate-LotusDeveloperEnvironment.ps1",
        "-Mode",
        "Inspect",
        "-Profile",
        "fast",
        "-OutputDirectory",
        str(output_dir),
        "-SkillTargetPath",
        str(skill_target),
        "-AgentsTargetPath",
        str(agents_target),
        "-NoExitOnBlocked",
        env=env,
    )

    report_path = output_dir / "developer-environment-readiness.json"
    markdown_path = output_dir / "developer-environment-readiness.md"
    assert report_path.exists()
    assert markdown_path.exists()

    raw_report = report_path.read_text(encoding="utf-8")
    assert secret_dsn not in raw_report
    assert "[redacted]" in raw_report

    report = json.loads(raw_report)
    assert report["schema_version"] == "1.0"
    assert report["mode"] == "Inspect"
    assert report["profile"] == "fast"
    assert report["overall_status"] in {"ready", "warning", "blocked"}
    assert isinstance(report["checks"], list)

    check_names = {check["name"] for check in report["checks"]}
    assert {
        "github-auth",
        "docker-posture",
        "repository-presence",
        "context-docs",
        "skill-sync",
        "agents-sync",
        "ingress-posture",
        "dsn-posture",
    } <= check_names

    markdown = markdown_path.read_text(encoding="utf-8")
    assert "Lotus Developer Environment Readiness" in markdown
    assert "Secret-bearing values are redacted" in markdown


def test_developer_environment_bootstrap_sync_is_idempotent_and_scoped(tmp_path: Path) -> None:
    output_dir = tmp_path / "readiness"
    skill_target = tmp_path / "skills"
    agents_target = tmp_path / "AGENTS.md"

    _run_script(
        "Bootstrap-LotusDeveloperEnvironment.ps1",
        "-Profile",
        "fast",
        "-OutputDirectory",
        str(output_dir),
        "-SkillTargetPath",
        str(skill_target),
        "-AgentsTargetPath",
        str(agents_target),
    )

    unknown_skill = skill_target / "local-private-skill"
    unknown_skill.mkdir(parents=True)
    (unknown_skill / "SKILL.md").write_text("name: local-private-skill\n", encoding="utf-8")

    _run_script(
        "Bootstrap-LotusDeveloperEnvironment.ps1",
        "-Profile",
        "fast",
        "-OutputDirectory",
        str(output_dir),
        "-SkillTargetPath",
        str(skill_target),
        "-AgentsTargetPath",
        str(agents_target),
    )

    assert agents_target.exists()
    assert (skill_target / "lotus-backend-delivery-governance" / "SKILL.md").exists()
    assert (unknown_skill / "SKILL.md").read_text(encoding="utf-8") == "name: local-private-skill\n"

    report = json.loads((output_dir / "developer-environment-readiness.json").read_text(encoding="utf-8"))
    skill_sync = next(check for check in report["checks"] if check["name"] == "skill-sync")
    assert "local-private-skill" in skill_sync["evidence"]["unknown_local_skills"]
