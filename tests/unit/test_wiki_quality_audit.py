from __future__ import annotations

import importlib.util
import subprocess
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


def _set_github_origin(repo_root: Path, url: str) -> None:
    subprocess.run(["git", "init", "--quiet", str(repo_root)], check=True)
    subprocess.run(
        ["git", "-C", str(repo_root), "remote", "add", "origin", url], check=True
    )


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


def test_wiki_quality_audit_rejects_parent_relative_publication_links(
    tmp_path: Path,
) -> None:
    audit = _load_audit_module()
    repo_root = tmp_path / "repo"
    wiki_dir = repo_root / "wiki"
    docs_dir = repo_root / "docs"
    wiki_dir.mkdir(parents=True)
    docs_dir.mkdir()
    (docs_dir / "runbook.md").write_text("# Runbook\n", encoding="utf-8")
    (wiki_dir / "Home.md").write_text(
        "# Home\n\n[Runbook](../docs/runbook.md)\n", encoding="utf-8"
    )
    (wiki_dir / "_Sidebar.md").write_text(
        "# Navigation\n\n- [Home](Home.md)\n", encoding="utf-8"
    )

    failures = audit.audit_wiki(wiki_dir, repo_root)

    assert (
        "Home.md: publication-unsafe parent-relative link: ../docs/runbook.md"
        in failures
    )

    (wiki_dir / "Home.md").write_text(
        "# Home\n\n[Prefixed](./../docs/runbook.md)\n"
        "[Embedded](wiki/../docs/runbook.md)\n",
        encoding="utf-8",
    )

    failures = audit.audit_wiki(wiki_dir, repo_root)

    assert any("./../docs/runbook.md" in failure for failure in failures)
    assert any("wiki/../docs/runbook.md" in failure for failure in failures)


def test_wiki_quality_audit_validates_decoded_repository_github_links(
    tmp_path: Path,
) -> None:
    audit = _load_audit_module()
    repo_root = tmp_path / "repo"
    wiki_dir = repo_root / "wiki"
    docs_dir = repo_root / "docs"
    wiki_dir.mkdir(parents=True)
    docs_dir.mkdir()
    _set_github_origin(repo_root, "https://github.com/example/repo.git")
    (docs_dir / "Runbook Guide.md").write_text("# Runbook\n", encoding="utf-8")
    (docs_dir / "A_(B).md").write_text("# Parenthesized guide\n", encoding="utf-8")
    (wiki_dir / "Home.md").write_text(
        "\n".join(
            [
                "# Home",
                "",
                "[Runbook](https://github.com/example/repo/blob/main/docs/Runbook%20Guide.md)",
                "[Docs](https://github.com/example/repo/tree/main/docs)",
                "[Parenthesized](https://github.com/example/repo/blob/main/docs/A_(B).md)",
            ]
        ),
        encoding="utf-8",
    )
    (wiki_dir / "_Sidebar.md").write_text(
        "# Navigation\n\n- [Home](Home.md)\n", encoding="utf-8"
    )

    assert audit.audit_wiki(wiki_dir, repo_root) == []

    wrong_ref = "https://github.com/example/repo/blob/typo/docs/Runbook%20Guide.md"
    (wiki_dir / "Home.md").write_text(
        f"# Home\n\n[Wrong ref]({wrong_ref})\n",
        encoding="utf-8",
    )

    failures = audit.audit_wiki(wiki_dir, repo_root)

    assert f"Home.md: repository GitHub link must target main: {wrong_ref}" in failures

    (wiki_dir / "Home.md").write_text(
        "# Home\n\n[Missing](https://github.com/example/repo/blob/main/docs/Missing%20Guide.md)\n",
        encoding="utf-8",
    )

    failures = audit.audit_wiki(wiki_dir, repo_root)

    assert (
        "Home.md: broken repository GitHub blob link: docs/Missing Guide.md"
        in failures
    )

    malformed_route = "https://github.com/example/repo/blbo/main/docs/Runbook%20Guide.md"
    (wiki_dir / "Home.md").write_text(
        f"# Home\n\n[Malformed]({malformed_route})\n", encoding="utf-8"
    )

    failures = audit.audit_wiki(wiki_dir, repo_root)

    assert (
        f"Home.md: repository GitHub file link must use blob or tree: {malformed_route}"
        in failures
    )


def test_wiki_quality_audit_uses_origin_identity_when_checkout_name_differs(
    tmp_path: Path,
) -> None:
    audit = _load_audit_module()
    repo_root = tmp_path / "checkout"
    wiki_dir = repo_root / "wiki"
    wiki_dir.mkdir(parents=True)
    _set_github_origin(repo_root, "https://github.com/example/repo.git")
    (wiki_dir / "Home.md").write_text(
        "# Home\n\n[Missing](https://github.com/example/repo/blob/main/missing.md)\n",
        encoding="utf-8",
    )
    (wiki_dir / "_Sidebar.md").write_text(
        "# Navigation\n\n- [Home](Home.md)\n", encoding="utf-8"
    )

    failures = audit.audit_wiki(wiki_dir, repo_root)

    assert "Home.md: broken repository GitHub blob link: missing.md" in failures


def test_wiki_quality_audit_rejects_wrong_owner_and_escaping_github_paths(
    tmp_path: Path,
) -> None:
    audit = _load_audit_module()
    repo_root = tmp_path / "repo"
    wiki_dir = repo_root / "wiki"
    wiki_dir.mkdir(parents=True)
    _set_github_origin(repo_root, "git@github.com:example/repo.git")
    (wiki_dir / "Home.md").write_text(
        "\n".join(
            [
                "# Home",
                "",
                '[Titled](https://github.com/example/repo/blob/main/AGENTS.md "Agent contract")',
                "[Fork](https://github.com/attacker/repo/blob/main/AGENTS.md)",
                "[Absolute](https://github.com/example/repo/blob/main/%2Fetc/passwd)",
                "[Traversal](https://github.com/example/repo/blob/main/docs/%2E%2E/AGENTS.md)",
            ]
        ),
        encoding="utf-8",
    )
    (wiki_dir / "_Sidebar.md").write_text(
        "# Navigation\n\n- [Home](Home.md)\n", encoding="utf-8"
    )
    (repo_root / "AGENTS.md").write_text("# Contract\n", encoding="utf-8")

    failures = audit.audit_wiki(wiki_dir, repo_root)

    assert not any("Titled" in failure for failure in failures)
    assert any("must target example/repo" in failure for failure in failures)
    assert sum("escapes repository root" in failure for failure in failures) == 2


def test_wiki_quality_audit_allows_urls_and_scratch_tokens_in_executable_examples(
    tmp_path: Path,
) -> None:
    audit = _load_audit_module()
    repo_root = tmp_path / "repo"
    wiki_dir = repo_root / "wiki"
    wiki_dir.mkdir(parents=True)
    (wiki_dir / "Home.md").write_text(
        "# Home\n\n[Getting Started](Getting-Started.md)\n",
        encoding="utf-8",
    )
    (wiki_dir / "_Sidebar.md").write_text(
        "# Navigation\n\n- [Getting Started](Getting-Started.md)\n",
        encoding="utf-8",
    )
    (wiki_dir / "Getting-Started.md").write_text(
        "\n".join(
            (
                "# Getting Started",
                "",
                "Current-state local setup.",
                "",
                "```powershell",
                "$env:SERVICE_URL = 'http://service.dev.lotus'",
                "$env:TEMP_DIRECTORY = './output/temp'",
                "```",
            )
        ),
        encoding="utf-8",
    )

    assert audit.audit_wiki(wiki_dir, repo_root) == []


def test_wiki_quality_audit_accepts_professional_long_page_structure(
    tmp_path: Path,
) -> None:
    audit = _load_audit_module()
    repo_root = tmp_path / "repo"
    wiki_dir = repo_root / "wiki"
    wiki_dir.mkdir(parents=True)
    (wiki_dir / "Home.md").write_text(
        "# Home\n\n[Operations Runbook](Operations-Runbook.md)\n",
        encoding="utf-8",
    )
    (wiki_dir / "_Sidebar.md").write_text(
        "# Navigation\n\n- [Operations Runbook](Operations-Runbook.md)\n",
        encoding="utf-8",
    )
    long_sections = "\n".join(
        f"## Evidence Area {index}\n\nImplementation-backed operator evidence for area {index}."
        for index in range(1, 35)
    )
    (wiki_dir / "Operations-Runbook.md").write_text(
        "\n".join(
            [
                "# Operations Runbook",
                "",
                "Current-state support posture for the repository operator surface.",
                "",
                "## First Response Matrix",
                "",
                "| Situation | Evidence | Action |",
                "| --- | --- | --- |",
                "| CI drift | Repo-native gate output | Fix forward from the failing lane |",
                "",
                long_sections,
            ]
        ),
        encoding="utf-8",
    )

    assert audit.audit_wiki(
        wiki_dir,
        repo_root,
        professional_pages={"Operations-Runbook.md"},
    ) == []


def test_wiki_quality_audit_rejects_long_text_dump_without_reader_structure(
    tmp_path: Path,
) -> None:
    audit = _load_audit_module()
    repo_root = tmp_path / "repo"
    wiki_dir = repo_root / "wiki"
    wiki_dir.mkdir(parents=True)
    (wiki_dir / "Home.md").write_text(
        "# Home\n\n[Architecture](Architecture.md)\n",
        encoding="utf-8",
    )
    (wiki_dir / "_Sidebar.md").write_text(
        "# Navigation\n\n- [Architecture](Architecture.md)\n",
        encoding="utf-8",
    )
    dense_intro = " ".join(
        f"This page repeats background detail {index} without giving a reader path or evidence structure."
        for index in range(1, 30)
    )
    filler = "\n".join(
        f"## Detail {index}\n\nHistorical background paragraph {index}."
        for index in range(1, 35)
    )
    (wiki_dir / "Architecture.md").write_text(
        f"# Architecture\n\n{dense_intro}\n\n{filler}\n",
        encoding="utf-8",
    )

    failures = audit.audit_wiki(
        wiki_dir,
        repo_root,
        professional_pages={"Architecture.md"},
    )

    assert (
        "Architecture.md: long wiki page must state current scope or evidence posture near the top"
        in failures
    )
    assert (
        "Architecture.md: long wiki page needs an early reader map, decision/evidence table, or equivalent first-screen structure"
        in failures
    )
    assert (
        "Architecture.md: opening section is too dense before the first H2; add current-state framing and reader structure"
        in failures
    )


def test_wiki_quality_audit_rejects_large_command_dump(tmp_path: Path) -> None:
    audit = _load_audit_module()
    repo_root = tmp_path / "repo"
    wiki_dir = repo_root / "wiki"
    wiki_dir.mkdir(parents=True)
    (wiki_dir / "Home.md").write_text(
        "# Home\n\n[Validation and CI](Validation-and-CI.md)\n",
        encoding="utf-8",
    )
    (wiki_dir / "_Sidebar.md").write_text(
        "# Navigation\n\n- [Validation and CI](Validation-and-CI.md)\n",
        encoding="utf-8",
    )
    commands = "\n".join(f"make validation-check-{index}" for index in range(1, 30))
    (wiki_dir / "Validation-and-CI.md").write_text(
        "\n".join(
            [
                "# Validation and CI",
                "",
                "Current-state validation posture.",
                "",
                "## Quality Signal Map",
                "",
                "| Gate | Purpose |",
                "| --- | --- |",
                "| Feature lane | Fast proof |",
                "",
                "```powershell",
                commands,
                "```",
            ]
        ),
        encoding="utf-8",
    )

    failures = audit.audit_wiki(
        wiki_dir,
        repo_root,
        professional_pages={"Validation-and-CI.md"},
    )

    assert (
        "Validation-and-CI.md: command dump is too large; group commands by purpose and link to the authoritative Makefile or runbook"
        in failures
    )


def test_wiki_quality_audit_scopes_professional_checks_to_changed_pages(
    tmp_path: Path,
) -> None:
    audit = _load_audit_module()
    repo_root = tmp_path / "repo"
    wiki_dir = repo_root / "wiki"
    wiki_dir.mkdir(parents=True)
    (wiki_dir / "Home.md").write_text(
        "# Home\n\n[Architecture](Architecture.md)\n[Operations Runbook](Operations-Runbook.md)\n",
        encoding="utf-8",
    )
    (wiki_dir / "_Sidebar.md").write_text(
        "# Navigation\n\n- [Architecture](Architecture.md)\n- [Operations Runbook](Operations-Runbook.md)\n",
        encoding="utf-8",
    )
    dense_intro = " ".join(
        f"Legacy background paragraph {index} without a current-state reader map."
        for index in range(1, 30)
    )
    filler = "\n".join(
        f"## Detail {index}\n\nHistorical background paragraph {index}."
        for index in range(1, 35)
    )
    (wiki_dir / "Architecture.md").write_text(
        f"# Architecture\n\n{dense_intro}\n\n{filler}\n",
        encoding="utf-8",
    )
    (wiki_dir / "Operations-Runbook.md").write_text(
        "\n".join(
            [
                "# Operations Runbook",
                "",
                "Current-state support posture.",
                "",
                "## First Response Matrix",
                "",
                "| Situation | Action |",
                "| --- | --- |",
                "| Ready | Continue |",
            ]
        ),
        encoding="utf-8",
    )

    assert audit.audit_wiki(
        wiki_dir,
        repo_root,
        professional_pages={"Operations-Runbook.md"},
    ) == []
