from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

EXPECTED_ROOT_MARKDOWN = {
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "REPOSITORY-ENGINEERING-CONTEXT.md",
}


def test_repo_root_markdown_is_limited_to_entrypoint_documents() -> None:
    root_markdown = {path.name for path in ROOT.glob("*.md")}

    assert root_markdown == EXPECTED_ROOT_MARKDOWN


def test_legacy_root_documents_have_governed_doc_homes() -> None:
    expected_paths = [
        ROOT / "docs" / "standards" / "Continuous Integration, Validation, and Release Governance Standard.md",
        ROOT / "docs" / "standards" / "Domain Vocabulary Glossary.md",
        ROOT / "docs" / "operations" / "Local Development Runbook.md",
        ROOT / "docs" / "architecture" / "Platform Integration Architecture Bible.md",
        ROOT / "docs" / "reports" / "Backend Standardization Completion Tracker.md",
        ROOT / "docs" / "archive" / "legacy" / "Private Banking Wealth Management UI Platform.txt",
    ]

    for path in expected_paths:
        assert path.exists(), f"Missing governed document home: {path.relative_to(ROOT)}"
