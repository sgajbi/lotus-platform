from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _powershell_executable() -> str:
    if sys.platform.startswith("win"):
        return "powershell"
    candidate = shutil.which("pwsh") or shutil.which("powershell")
    if candidate is None:
        raise AssertionError("PowerShell executable not available for scaffold contract test")
    return candidate


def test_repository_hygiene_standard_and_templates_exist() -> None:
    standards_readme = (ROOT / "platform-standards" / "README.md").read_text(encoding="utf-8")
    hygiene_standard = (
        ROOT / "platform-standards" / "Repository-Hygiene-and-Dependency-Model-Standard.md"
    ).read_text(encoding="utf-8")
    scaffold_script = (ROOT / "automation" / "New-Lotus-Service.ps1").read_text(encoding="utf-8")
    makefile_template = (
        ROOT / "platform-standards" / "templates" / "Makefile.backend.template"
    ).read_text(encoding="utf-8")
    feature_lane_template = (
        ROOT / "platform-standards" / "templates" / "workflows" / "feature-lane.backend.template.yml"
    ).read_text(encoding="utf-8")
    pr_merge_template = (
        ROOT / "platform-standards" / "templates" / "workflows" / "pr-merge-gate.backend.template.yml"
    ).read_text(encoding="utf-8")

    assert "Repository-Hygiene-and-Dependency-Model-Standard.md" in standards_readme
    assert ".editorconfig" in hygiene_standard
    assert ".gitattributes" in hygiene_standard
    assert ".gitignore" in hygiene_standard
    assert ".dockerignore" in hygiene_standard
    assert "pyproject.toml" in hygiene_standard
    assert "requirements/shared-runtime.lock.txt" in hygiene_standard
    assert "requirements/ci-tooling.lock.txt" in hygiene_standard
    assert 'preflight_fast_command = "make check"' in scaffold_script
    assert 'preflight_full_command = "make ci"' in scaffold_script
    assert 'Copy-Item (Join-Path $templateRoot ".editorconfig.backend.template")' in scaffold_script
    assert 'Copy-Item (Join-Path $templateRoot ".gitattributes.backend.template")' in scaffold_script
    assert 'Copy-Item (Join-Path $templateRoot ".gitignore.backend.template")' in scaffold_script
    assert 'Copy-Item (Join-Path $templateRoot ".dockerignore.backend.template")' in scaffold_script
    assert 'Copy-Item (Join-Path $templateRoot "requirements.shared-runtime.lock.template.txt")' in scaffold_script
    assert 'Copy-Item (Join-Path $templateRoot "requirements.ci-tooling.lock.template.txt")' in scaffold_script
    assert "Ensure-GitInitialCommit" in scaffold_script
    assert "git -C $TargetRepoRoot push -u origin main" in scaffold_script
    assert "monetary-float-guard:" in makefile_template
    assert "$(MAKE) monetary-float-guard" in makefile_template
    assert "coverage-gate:" in makefile_template
    assert "$(VENV_PYTHON) scripts/coverage_gate.py" in makefile_template
    assert (
        "$(VENV_PYTHON) -m pip_audit -r requirements/shared-runtime.lock.txt -r requirements/ci-tooling.lock.txt"
        in makefile_template
    )
    assert "run: ./.venv/bin/python -m pytest tests/unit" in feature_lane_template
    assert "run: ./.venv/bin/python -m pytest ${{ matrix.path }} --cov=src --cov-report=" in pr_merge_template
    assert "./.venv/bin/python -m coverage combine coverage-data" in pr_merge_template
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
            _powershell_executable(),
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
    makefile = (repo_root / "Makefile").read_text(encoding="utf-8")
    assert result["ok"] is True
    assert result["dependency_authority"] == "pyproject"
    assert result["editorconfig_exists"] is True
    assert result["gitattributes_exists"] is True
    assert result["shared_runtime_lock_exists"] is True
    assert result["ci_tooling_lock_exists"] is True
    assert result["editorconfig_missing_patterns"] == []
    assert result["gitattributes_missing_patterns"] == []
    assert result["gitignore_missing_patterns"] == []
    assert result["dockerignore_missing_patterns"] == []
    assert "monetary-float-guard:" in makefile
    assert "$(MAKE) monetary-float-guard" in makefile
    assert "coverage-gate:" in makefile
    assert "$(VENV_PYTHON) scripts/coverage_gate.py" in makefile
    assert (
        "$(VENV_PYTHON) -m pip_audit -r requirements/shared-runtime.lock.txt -r requirements/ci-tooling.lock.txt"
        in makefile
    )
