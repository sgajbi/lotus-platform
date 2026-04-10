from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_rfc_0072_foundation_artifacts_are_present_and_cross_referenced() -> None:
    rfc = (ROOT / "rfcs" / "RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md").read_text(
        encoding="utf-8"
    )
    standard = (ROOT / "Continuous Integration, Validation, and Release Governance Standard.md").read_text(
        encoding="utf-8"
    )
    checklist = (ROOT / "rfcs" / "RFC-0072-implementation-checklist.md").read_text(encoding="utf-8")
    mapping = (ROOT / "platform-standards" / "Repository-CI-Lane-Mapping-Baseline.md").read_text(
        encoding="utf-8"
    )

    assert "Scaffolding-by-Default Requirement" in rfc
    assert "Remote Feature Lane" in rfc
    assert "Pull Request Merge Gate" in rfc
    assert "Main Releasability Gate" in rfc
    assert "Platform End-to-End Validation Lane" in rfc

    assert "Scaffold-by-Default Policy" in standard
    assert "Skill Alignment Requirement" in standard

    assert "Slice 1 | Governance and documentation foundation | Complete" in checklist
    assert "Current scaffold source of truth" in checklist

    assert "lotus-workbench" in mapping
    assert "lotus-gateway" in mapping
    assert "lotus-platform" in mapping
    assert "ci.backend.template.yml" in mapping


def test_platform_standards_and_runbook_point_to_rfc_0072_sources() -> None:
    standards_readme = (ROOT / "platform-standards" / "README.md").read_text(encoding="utf-8")
    workflow_standard = (ROOT / "platform-standards" / "Development-Workflow-and-CI-Strategy-Standard.md").read_text(
        encoding="utf-8"
    )
    local_runbook = (ROOT / "Local Development Runbook.md").read_text(encoding="utf-8")

    assert "Continuous Integration, Validation, and Release Governance Standard.md" in standards_readme
    assert "RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md" in standards_readme
    assert "Repository-CI-Lane-Mapping-Baseline.md" in standards_readme

    assert "Authoritative CI governance now lives in" in workflow_standard
    assert "Remote Feature Lane" in workflow_standard
    assert "Platform End-to-End Validation Lane" in workflow_standard

    assert "RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md" in local_runbook
