from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT_PATH = (
    ROOT
    / "codex"
    / "skills"
    / "lotus-readme-wiki-governance"
    / "scripts"
    / "audit_wiki_quality.py"
)


def _load_audit_module():
    spec = importlib.util.spec_from_file_location("audit_wiki_quality", AUDIT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    previous_bytecode_setting = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous_bytecode_setting
    return module


def test_wiki_quality_audit_accepts_navigation_and_repo_evidence_links(tmp_path: Path) -> None:
    audit = _load_audit_module()
    repo_root = tmp_path / "repo"
    wiki_dir = repo_root / "wiki"
    evidence_dir = repo_root / "docs" / "operations"
    wiki_dir.mkdir(parents=True)
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "runbook.md").write_text("# Runbook\n", encoding="utf-8")

    (wiki_dir / "Home.md").write_text(
        "\n".join(
            [
                "# Home",
                "",
                "| Audience | Path |",
                "| --- | --- |",
                "| Operations | [Operations Runbook](Operations-Runbook.md) |",
                "",
                "Evidence: [Runbook](docs/operations/runbook.md)",
            ]
        ),
        encoding="utf-8",
    )
    (wiki_dir / "_Sidebar.md").write_text(
        "\n".join(
            [
                "# Navigation",
                "",
                "- [Home](Home.md)",
                "- [Operations Runbook](Operations-Runbook.md)",
            ]
        ),
        encoding="utf-8",
    )
    (wiki_dir / "Operations-Runbook.md").write_text(
        "# Operations Runbook\n\nCurrent-state support path.\n",
        encoding="utf-8",
    )

    assert audit.audit_wiki(wiki_dir, repo_root) == []


def test_wiki_quality_audit_rejects_unprofessional_structure(tmp_path: Path) -> None:
    audit = _load_audit_module()
    repo_root = tmp_path / "repo"
    wiki_dir = repo_root / "wiki"
    wiki_dir.mkdir(parents=True)
    (wiki_dir / "Home.md").write_text("# Home\n\n[Missing](Missing.md)\n", encoding="utf-8")
    (wiki_dir / "_Sidebar.md").write_text("# Navigation\n\n- [Home](Home.md)\n", encoding="utf-8")
    (wiki_dir / "Orphan.md").write_text(
        "# Orphan\n\n# Duplicate\n\nTODO: use https://example.com later.\n",
        encoding="utf-8",
    )

    failures = audit.audit_wiki(wiki_dir, repo_root)

    assert "Home.md: broken local or repo-relative link: Missing.md" in failures
    assert "Orphan.md: expected exactly one H1, found 2" in failures
    assert "Orphan.md: contains bare URL; use a named Markdown link" in failures
    assert "Orphan.md: contains scratch-note terms: TODO" in failures
    assert "Orphan.md: page is not reachable from Home.md or _Sidebar.md" in failures
