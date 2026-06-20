from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_enterprise_backend_refactor_instruction_sync_uses_platform_source() -> None:
    script = (ROOT / "automation" / "Sync-EnterpriseBackendRefactoringInstructions.ps1").read_text(
        encoding="utf-8"
    )

    assert "context\\playbooks\\ENTERPRISE-BACKEND-REFACTORING-INSTRUCTIONS.md" in script
    assert "lotus-manage\\docs\\architecture\\ENTERPRISE_BACKEND_REFACTORING_INSTRUCTIONS.md" not in script
    assert "ConvertFrom-Json" in script
    assert "repos.json" in script
    assert "'lotus-manage'" not in script
    assert "'lotus-platform'" in script
    assert "'lotus-workbench'" in script
    assert "[switch]$CheckOnly" in script
    assert "Enterprise backend refactoring instruction drift detected" in script


def test_enterprise_backend_refactor_sync_is_documented_for_operators() -> None:
    automation_readme = (ROOT / "automation" / "README.md").read_text(encoding="utf-8")
    repo_context = (ROOT / "REPOSITORY-ENGINEERING-CONTEXT.md").read_text(encoding="utf-8")

    assert "Sync-EnterpriseBackendRefactoringInstructions.ps1 -CheckOnly" in automation_readme
    assert "Sync-EnterpriseBackendRefactoringInstructions.ps1" in repo_context
