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
    assert "foreach ($entry in @($repoEntries))" in script
    assert "$entry.PSObject.Properties['name']" in script
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


def test_enterprise_backend_refactor_instructions_pin_proof_artifact_guardrails() -> None:
    instructions = (
        ROOT / "context" / "playbooks" / "ENTERPRISE-BACKEND-REFACTORING-INSTRUCTIONS.md"
    ).read_text(encoding="utf-8")

    required_fragments = (
        "LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md",
        "Lotus Data Mesh Standard.md",
        "Lotus Client Demo Certification Standard.md",
        "LOTUS-BACKEND-SERVICE-SCAFFOLD-GUIDE.md",
        "## 12A. Agentic Quality Gate Pack",
        "## 12B. Bounded Proof Artifact Pattern",
        "exact blockers cleared",
        "remaining blockers",
        "source-safety checks",
        "report materialization proof must not become client-publication proof",
        "data-mesh onboarding proof must not become mesh certification",
        "AI workflow-pack registration proof must not become live-provider proof",
        "sync enterprise refactor instructions to app-local copies",
    )

    for fragment in required_fragments:
        assert fragment in instructions


def test_ci_enforcement_skill_mentions_bounded_proof_artifacts() -> None:
    skill = (
        ROOT / "codex" / "skills" / "lotus-ci-enforcement-governance" / "SKILL.md"
    ).read_text(encoding="utf-8")

    required_fragments = (
        "## Proof Artifact Enforcement",
        "exact blocker codes cleared",
        "exact blocker codes that intentionally remain",
        "route-foundation proof is not downstream execution proof",
        "report materialization proof is not client-publication proof",
        "data-mesh onboarding proof is not mesh certification",
        "AI workflow-pack registration proof is not live-provider proof",
        "Workbench read-path proof is not full product-surface certification",
    )

    for fragment in required_fragments:
        assert fragment in skill
