from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_repository_hygiene_standard_and_templates_exist() -> None:
    standards_readme = (ROOT / "platform-standards" / "README.md").read_text(encoding="utf-8")
    hygiene_standard = (
        ROOT / "platform-standards" / "Repository-Hygiene-and-Dependency-Model-Standard.md"
    ).read_text(encoding="utf-8")
    scaffold_script = (ROOT / "automation" / "New-Lotus-Service.ps1").read_text(encoding="utf-8")

    assert "Repository-Hygiene-and-Dependency-Model-Standard.md" in standards_readme
    assert ".gitignore" in hygiene_standard
    assert ".dockerignore" in hygiene_standard
    assert "pyproject.toml" in hygiene_standard
    assert 'preflight_fast_command = "make check"' in scaffold_script
    assert 'preflight_full_command = "make ci"' in scaffold_script
    assert 'Copy-Item (Join-Path $templateRoot ".gitignore.backend.template")' in scaffold_script
    assert 'Copy-Item (Join-Path $templateRoot ".dockerignore.backend.template")' in scaffold_script
    assert 'Set-Content -Path (Join-Path $target ".gitignore")' not in scaffold_script


def test_scaffolded_repo_matches_repository_hygiene_baseline(tmp_path: Path) -> None:
    destination_root = tmp_path / "generated"
    destination_root.mkdir()
    service_name = "lotus-hygiene-demo"
    scaffold_script = ROOT / "automation" / "New-Lotus-Service.ps1"
    validator_script = ROOT / "automation" / "validate_repository_hygiene.py"
    repo_root = destination_root / service_name
    output_json = tmp_path / "repository-hygiene-validation.json"

    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(scaffold_script),
            "-ServiceName",
            service_name,
            "-DestinationRoot",
            str(destination_root),
            "-SkipAutomationRegistration",
            "-Force",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        [
            sys.executable,
            str(validator_script),
            "--repo-root",
            str(repo_root),
            "--output-json",
            str(output_json),
            "--output-markdown",
            str(tmp_path / "repository-hygiene-validation.md"),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    result = json.loads(output_json.read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert result["dependency_authority"] == "pyproject"
    assert result["gitignore_missing_patterns"] == []
    assert result["dockerignore_missing_patterns"] == []
