from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
AUDIT_PATH = (
    ROOT
    / "codex"
    / "skills"
    / "lotus-readme-wiki-governance"
    / "scripts"
    / "audit_wiki_quality.py"
)

FORMATTED_DIRECTORY_SCRATCH_PROSE = [
    "temporary directory: *notes*", "temporary directory: **NOTES**",
    "temporary directories — _notes_", "temporary directories — __workaround__",
    "temporary directory — `workaround`", "TEMPORARY DIRECTORIES: ``NOTES``",
    "temporary directory (**workaround**)", "temporary directories [__NOTES__]",
    "temporary directory: *_notes_*", "temporary directory: `**workaround**`",
    "temporary directory: **notes", "temporary directories — _workaround",
    "temporary directory: __NOTES_", "temporary directories: `workaround",
    "Use the OS temporary directory, with mode 0700; temporary directory: **notes** remain.",
    "temporary directory: ~~notes~~", "temporary directory: ~workaround~",
    "TEMPORARY DIRECTORIES: ~~NOTES~~",
    "temporary directories: ~~**_workaround_**~~", "temporary directory: ~~notes",
    "temporary directory: 'notes'", 'temporary directories: "workaround"',
    "temporary directory: “notes”", r"temporary directory: \*\*notes\*\*",
    "temporary directory / notes", "temporary directories | workaround",
    r"temporary directory: \`notes\`",
]

HTML_DIRECTORY_SCRATCH_PROSE = [
    "temporary directory: <em>notes</em>",
    "temporary directory: <strong>workaround</strong>",
    "temporary directories: <span title='permissions'>notes</span>",
    "TEMPORARY DIRECTORIES: <span><strong>WORKAROUND</strong></span>",
    "temporary directory: n<em>o</em>tes",
    "temporary directory: <!-- explanation --><em>notes</em>",
    "temporary directory: <em>notes",
    'temporary directory: <em title="a > b">notes</em>',
    "temporary directory:&nbsp;notes",
    "temporary directory: &#110;otes",
    "temporary directories: &#x77;orkaround",
    "temporary directory: &ast;&ast;notes&ast;&ast;",
    "Use the OS temporary directory for mode 0700; temporary directory: <em>notes</em> remain.",
    "temporary directories — <span>_notes_</span>",
    "temporary directory: <code>workaround</code>",
]

# Independent policy inventory: default flow/list/text-bearing table boundaries,
# not CommonMark HTML-block syntax names or a general browser layout model.
DIRECTORY_HTML_BOUNDARY_TAGS = (
    "address article aside blockquote body br caption center dd details dialog dir div "
    "dl dt fieldset figcaption figure footer form h1 h2 h3 h4 h5 h6 header hgroup hr "
    "html legend li listing main menu nav ol p plaintext pre search section summary "
    "table tbody td tfoot th thead tr ul xmp"
).split()

DIRECTORY_HTML_BOUNDARY_CASES = [
    (f"temporary directory: <{tag} title='notes > workaround'><em>notes</em></{tag}>", True)
    for tag in DIRECTORY_HTML_BOUNDARY_TAGS
] + [
    (f"<{tag.upper()} title='mode 0700'><span>technical</span> temporary directory: "
     f"</{tag.upper()}><strong>workaround</strong>", True)
    for tag in DIRECTORY_HTML_BOUNDARY_TAGS
] + [
    (f"temporary directory: <{tag} title='mode 0700'>notes</{tag}>", False)
    for tag in ("em", "strong", "code", "span", "a", "wbr", "base", "link", "param", "title", "col", "colgroup")
] + [
    (f"temporary directory:{newline}<em>notes</em>", True)
    for newline in ("\r", "\n", "\r\n")
]

DIRECTORY_LINK_CASES = [
    (f"[temporary directory]{metadata} {qualifier}", False)
    for metadata in (
        "(Operations-Runbook)", "(<Operations-Runbook>)", "()", "(<>)",
        '(Operations-Runbook "operator notes")', "(Operations-Runbook 'operator notes')",
        "(Operations-Runbook (operator notes))", '( "operator notes" )',
    )
    for qualifier in ("notes", "**workaround**")
] + [
    (f"[temporary directory]{metadata} mode 0700 protects diagnostics.", True)
    for metadata in ("(Operations-Runbook)", "[target]", "[]", "")
] + [
    (f"[temporary directory]{suffix} {qualifier}\n\n[{label}]: Operations-Runbook", False)
    for suffix, label in (("[target]", "target"), ("[]", "temporary directory"), ("", "temporary directory"))
    for qualifier in ("notes", "<em>workaround</em>")
] + [
    ("[temporary directory][TARGET  label] notes\n\n[target label]: Operations-Runbook", False),
    ("[temporary directory][StraSSe] notes\n\n[straße]: Operations-Runbook", False),
    ("[temporary directory][target] notes\n\n[target]: Operations-Runbook\n[target]: <Home>", False),
    ("[temporary directory][missing] notes", True),
    ("[temporary directory][] notes", False),
    ("[temporary directory] notes", False),
    ("[temporary directory][target] notes\n\n[target]: Operations-Runbook invalid title", True),
    ("[temporary directory][target] notes\n```\n[target]: Operations-Runbook\n```", True),
    ("[temporary directory](Operations-Runbook notes", True),
    ("[temporary directory](Operations-Runbook \"unclosed) notes", True),
    (r"\[temporary directory](Operations-Runbook) notes", True),
    (r"\\[temporary directory](Operations-Runbook) notes", False),
    (r"[temporary directory\](Operations-Runbook) notes", True),
    ("`[temporary directory](Operations-Runbook) notes`", True),
    ("![temporary directory](Operations-Runbook) notes", True),
    ("[temporary directory with mode 0700](Operations-Runbook) notes explain permissions.", True),
    ("[temporary directory **notes**](Operations-Runbook)", False),
    ("[**temporary directory**](Operations-Runbook) ~~notes~~", False),
    ("[OS [private] temporary directory](Operations-Runbook) notes", False),
    ("[prefix [page](Home) temporary directory](Operations-Runbook) notes", True),
    ("[outer [temporary directory](Operations-Runbook)](Home) notes", True),
    ("[temporary directory](Operations-Runbook) using mode 0700; notes explain permissions.", True),
    ("temporary [directory](Operations-Runbook) notes", False),
    ("[temporary table](Operations-Runbook) notes", True),
    ("[temporary relation](Operations-Runbook) mode 0700", True),
    ("[temporary directory](Operations-Runbook(a(b(c)))) notes", False),
    (r"[temporary directory](Operations-Runbook\(private\)) notes", False),
    (r"[temporary directory](Operations-Runbook \"operator\") notes", True),
    ('[temporary directory](Operations-Runbook "operator \\"notes\\"") workaround', False),
    ("[temporary directory](<Operations-Runbook>) **mode 0700**", True),
    ("[temporary directory][target] mode 0700\n\n[target]: Operations-Runbook 'permissions'", True),
    ("[temporary directory][] mode 0700\n\n[temporary directory]: Operations-Runbook", True),
    ("[temporary directory] mode 0700\n\n[temporary directory]: Operations-Runbook", True),
    ("[temporary directory] [target] notes\n\n[target]: Operations-Runbook", True),
    ("[temporary directory][target] notes\nparagraph\n[target]: Operations-Runbook", True),
    ("[temporary directory](Operations-Runbook (invalid(nested))) notes", True),
    ("[temporary directory](Operations-Runbook) <p>notes</p>", True),
    ("[temporary directory](Operations-Runbook) &#110;otes", False),
    ("[temporary directory](Operations-Runbook) `<em>notes</em>`", True),
    ("[temporary directory](Operations-Runbook) notes_directory", True),
] + [
    (f"[temporary directory](Operations-Runbook){newline}notes", True)
    for newline in ("\r", "\n", "\r\n")
] + [
    (f"[temporary directory]({newline}Operations-Runbook) notes", True)
    for newline in ("\r", "\n", "\r\n")
] + [
    (f"[temporary directory][target] notes\n\n[target]: Operations-Runbook\\{separator}invalid", True)
    for separator in (" ", "\t")
] + [
    (r"[temporary directory](Operations-Runbook\(private\)) **workaround**", False),
    (r'[temporary directory](Operations-Runbook "operator\"notes") notes', False),
    (r'[temporary directory](Operations-Runbook "operator\ notes") notes', False),
    (r"[temporary directory\!](Operations-Runbook) notes", False),
    (r"[temporary directory\a](Operations-Runbook) notes", True),
    (r"[temporary directory\\](Operations-Runbook) notes", False),
]


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


@pytest.mark.parametrize("prose", [
    "The migration scans immutable outbox evidence into an indexed temporary relation before bounded ledger batches.",
    "PostgreSQL uses a temporary table for migration evidence.",
    "The indexed TEMPORARY RELATIONS hold database evidence.",
])
def test_temporary_database_terms_are_operator_prose(prose: str) -> None:
    assert _load_audit_module()._page_prose_failures("Persistence-Service.md", prose) == []


@pytest.mark.parametrize("prose", [
    "TODO finalize", "TBD", "FIXME", "temp notes", "temporary workaround",
    "maybe implement later", "rough notes", "temporary\ntable of unfinished notes",
    "temporary table workaround", "temporary relation notes",
    "Use a temporary relation; temporary workaround remains.",
    "Use a temporary table; TODO finish migration.",
])
def test_database_terms_do_not_waive_scratch_notes(prose: str) -> None:
    assert "contains scratch-note terms" in " ".join(
        _load_audit_module()._page_prose_failures("Persistence-Service.md", prose)
    )


@pytest.mark.parametrize("prose, accepted", DIRECTORY_HTML_BOUNDARY_CASES)
def test_directory_html_boundary_policy_actual_and_cli(
    tmp_path: Path, prose: str, accepted: bool,
) -> None:
    _assert_directory_prose_actual_and_cli(tmp_path, prose, accepted)


@pytest.mark.parametrize("prose, accepted", DIRECTORY_LINK_CASES)
def test_directory_link_policy_actual_and_cli(
    tmp_path: Path, prose: str, accepted: bool,
) -> None:
    _assert_directory_prose_actual_and_cli(tmp_path, prose, accepted)


@pytest.mark.parametrize("separator", (" ", "\t", "\x01", "\x7f"))
def test_invalid_directory_link_metadata_preserves_navigation_guard(
    tmp_path: Path, separator: str,
) -> None:
    prose = f"[temporary directory](Operations-Runbook\\{separator}invalid) notes"
    _assert_directory_prose_actual_and_cli(tmp_path, prose, True, link_failure_expected=True)


def _assert_directory_prose_actual_and_cli(
    tmp_path: Path, prose: str, accepted: bool, *, link_failure_expected: bool = False,
) -> None:
    findings = _load_audit_module()._page_prose_failures("Operations-Runbook.md", prose)
    assert (findings == []) is accepted
    repo_root = tmp_path / "repo"
    _set_github_origin(repo_root, "https://github.com/example/repo.git")
    wiki = repo_root / "wiki"
    wiki.mkdir()
    (wiki / "Home.md").write_text("# Home\n\n[Operations](Operations-Runbook)\n", encoding="utf-8")
    (wiki / "_Sidebar.md").write_text(
        "# Navigation\n\n[Home](Home)\n[Operations](Operations-Runbook)\n", encoding="utf-8"
    )
    (wiki / "Operations-Runbook.md").write_text(
        "# Operations Runbook\n\nCurrent-state support requires owner-only OS directory permissions.\n"
        f"{prose}\n", encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(AUDIT_PATH), "--wiki-dir", str(wiki), "--repo-root",
         str(repo_root), "--changed-page", "Operations-Runbook.md"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == (0 if accepted and not link_failure_expected else 1), result.stdout + result.stderr
    assert ("contains scratch-note terms" not in result.stdout) is accepted
    if link_failure_expected:
        assert "broken local or repo-relative link" in result.stdout


@pytest.mark.parametrize("prose", [
    "The worker creates an owner-only POSIX directory under the OS temporary directory, "
    "with mode 0700 and no-follow opens.",
    "Operating-system TEMPORARY DIRECTORIES contain mode 0600 diagnostic files.",
    "Use the OS temporary directory: mode 0700 is required.",
    "OS temporary directories (mode 0700) hold private diagnostic files.",
    "OS temporary directories: **mode 0700** protects private files.",
    "Use the OS temporary directory, with _mode 0700_ and `no-follow` opens.",
    "Use the OS temporary directory: __mode 0700__ is required.",
    "Use the OS temporary directory: `mode 0700` is required.",
    "Use the OS temporary directory: notes_directory contains private files.",
    "Use the OS temporary directory.\n**notes** describe its permissions.",
    "Use the OS temporary directory: ~~mode 0700~~ was replaced by mode 0600.",
    "Use the OS temporary directory: ~~notes_directory~~ contains private files.",
    "Use the OS temporary directory:\n~~notes~~ describe its permissions.",
    "Use the OS temporary directory:\r\n'workaround' describes a different step.",
    "Use the OS temporary directory: <em>mode 0700</em> protects private files.",
    'Use the OS temporary directory: <span title="notes > workaround">mode 0700</span>.',
    "Use the OS temporary directory: <!-- notes --><strong>mode 0700</strong>.",
    "Use the OS temporary directory: <em>notes_directory</em> holds private files.",
    "Use the OS temporary directory: <br>notes describe another line.",
    "Use the OS temporary directory: <p>workaround describes another paragraph.</p>",
    "Use the OS temporary directory: &#10;notes describe another line.",
    "Use the OS temporary directory: &lt;em&gt;notes&lt;/em&gt; is literal markup.",
    r"Use the OS temporary directory: \<em>notes\</em> is literal markup.",
    "Use the OS temporary directory: `<em>notes</em>` is literal code.",
    "Use the OS temporary directory: `&#110;otes` is literal code.",
])
def test_temporary_directory_terms_are_operator_prose(prose: str) -> None:
    assert _load_audit_module()._page_prose_failures("Operations-Runbook.md", prose) == []


@pytest.mark.parametrize("prose", [
    "temporary directory notes", "temporary directory workaround",
    "temporary directories notes", "temporary directories workaround",
    "temporary directory: notes", "temporary directory — notes",
    "temporary directory (workaround)", "TEMPORARY DIRECTORIES: NOTES",
    "temporary directories — workaround", "temporary directories (NOTES)",
    "temporary directory; notes", "temporary directory, workaround",
    "temporary directory [notes]", "temporary directory - workaround",
    "temporary directory – notes", "temporary directory. workaround",
    *FORMATTED_DIRECTORY_SCRATCH_PROSE,
    *HTML_DIRECTORY_SCRATCH_PROSE,
    "temporary\ndirectory notes", "temporary directoryname",
    "Use an OS temporary directory; TODO finish the operator notes.",
    "Use an OS temporary directory; TBD.",
    "Use an OS temporary directory; FIXME.",
    "Use an OS temporary directory; temporary workaround remains.",
    "Use an OS temporary directory; rough notes remain.",
])
def test_directory_terms_do_not_waive_scratch_notes(prose: str) -> None:
    assert "contains scratch-note terms" in " ".join(
        _load_audit_module()._page_prose_failures("Operations-Runbook.md", prose)
    )


@pytest.mark.parametrize("bad_prose", [
    "", "temporary directory notes", "temporary directory workaround",
    "temporary directory: notes", "temporary directory — notes",
    "temporary directory (workaround)", "TEMPORARY DIRECTORIES: NOTES",
    "temporary directories — workaround", "temporary directories (NOTES)",
    *FORMATTED_DIRECTORY_SCRATCH_PROSE,
    *HTML_DIRECTORY_SCRATCH_PROSE,
    "Use an OS temporary directory; TODO finish.",
    "Use an OS temporary directory; TBD.",
    "Use an OS temporary directory; FIXME.",
    "Use an OS temporary directory; temporary workaround remains.",
])
def test_directory_fixture_cli_preserves_prose_and_changed_page_scope(
    tmp_path: Path, bad_prose: str,
) -> None:
    repo_root = tmp_path / "repo"
    _set_github_origin(repo_root, "https://github.com/example/repo.git")
    wiki = repo_root / "wiki"
    wiki.mkdir()
    (wiki / "Home.md").write_text(
        "# Home\n\n[Operations](Operations-Runbook)\n", encoding="utf-8"
    )
    (wiki / "_Sidebar.md").write_text(
        "# Navigation\n\n[Home](Home)\n[Operations](Operations-Runbook)\n", encoding="utf-8"
    )
    (wiki / "Operations-Runbook.md").write_text(
        "# Operations Runbook\n\nCurrent-state support creates an owner-only POSIX "
        "directory under the worker OS temporary directory, with <strong title='notes'>mode 0700</strong>, "
        "_owner-only_ access and `no-follow` opens.\n"
        "[Run](https://github.com/example/repo/actions/runs/12)\n"
        f"{bad_prose}\n", encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(AUDIT_PATH), "--wiki-dir", str(wiki), "--repo-root",
         str(repo_root), "--changed-page", "Operations-Runbook.md"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == (1 if bad_prose else 0), result.stdout + result.stderr
    if bad_prose:
        assert "Operations-Runbook.md: contains scratch-note terms" in result.stdout


@pytest.mark.parametrize("route", [
    "actions/runs/37190131449", "actions/runs/37190131449/job/111400413011",
    "actions/workflows/feature-lane.yml", "issues/929#issuecomment-123",
    "pull/926", "pull/926/files", "commit/2830c46efa41eb4a8426ee97af7bad33585f80b7",
    "releases", "releases/latest", "releases/tag/v1.0.0", "compare/main...release",
])
def test_repository_evidence_routes_are_not_file_links(tmp_path: Path, route: str) -> None:
    _set_github_origin(tmp_path, "https://github.com/example/repo.git")
    assert _load_audit_module()._repository_github_link_failures(
        "Evidence.md", f"[Evidence](https://github.com/example/repo/{route})",
        repo_root=tmp_path,
    ) == []


@pytest.mark.parametrize("route", [
    "actions/runs/no-number", "actions/runs/12/other/3", "actions/workflows",
    "actions/workflows/../AGENTS.md", "issues/not-a-number", "pull/12/unknown",
    "commit/not-a-sha", "releases/unknown", "compare/main", "blbo/main/AGENTS.md",
    "blob/feature/AGENTS.md", "blob/main/%2e%2e/AGENTS.md", "blob/main",
])
def test_malformed_repository_routes_fail(tmp_path: Path, route: str) -> None:
    _set_github_origin(tmp_path, "https://github.com/example/repo.git")
    assert _load_audit_module()._repository_github_link_failures(
        "Evidence.md", f"[Evidence](https://github.com/example/repo/{route})",
        repo_root=tmp_path,
    )


@pytest.mark.parametrize("owner", ["example", "attacker"])
def test_repository_evidence_origin_is_verified(tmp_path: Path, owner: str) -> None:
    _set_github_origin(tmp_path, "https://github.com/example/repo.git")
    failures = _load_audit_module()._repository_github_link_failures(
        "Evidence.md", f"[Run](https://github.com/{owner}/repo/actions/runs/12)",
        repo_root=tmp_path,
    )
    assert bool(failures) == (owner == "attacker")


@pytest.mark.parametrize("bad_prose", [
    "", "temporary workaround", "TODO finish",
    "[Branch](https://github.com/example/repo/blob/feature/AGENTS.md)",
    "[Malformed](https://github.com/example/repo/actions/runs/not-a-number)",
    "[Fork](https://github.com/attacker/repo/actions/runs/12)",
    "[Traversal](https://github.com/example/repo/blob/main/%2e%2e/AGENTS.md)",
])
def test_fixture_cli_preserves_base_checks_outside_changed_scope(
    tmp_path: Path, bad_prose: str,
) -> None:
    repo_root = tmp_path / "repo"
    _set_github_origin(repo_root, "https://github.com/example/repo.git")
    wiki = repo_root / "wiki"
    wiki.mkdir()
    # A real repository directory must not shadow an existing bare wiki-page link.
    (repo_root / "Supported-Features").mkdir()
    (wiki / "Home.md").write_text(
        "# Home\n\n[Features](Supported-Features)\n", encoding="utf-8"
    )
    (wiki / "_Sidebar.md").write_text(
        "# Navigation\n\n[Home](Home)\n[Features](Supported-Features)\n", encoding="utf-8"
    )
    (wiki / "Supported-Features.md").write_text(
        "# Features\n\nCurrent-state support uses an indexed temporary relation.\n"
        "[Run](https://github.com/example/repo/actions/runs/12)\n"
        f"{bad_prose}\n```text\nTODO temporary workaround\n```\n", encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(AUDIT_PATH), "--wiki-dir", str(wiki), "--repo-root",
         str(repo_root), "--changed-page", "Home.md"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == (1 if bad_prose else 0), result.stdout + result.stderr
    if bad_prose:
        assert "Supported-Features.md:" in result.stdout


def test_bare_wiki_links_require_existing_pages(tmp_path: Path) -> None:
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (tmp_path / "Missing-Page").mkdir()
    failures = _load_audit_module()._page_link_failures(
        "Home.md", "[Missing](Missing-Page)", wiki_dir=wiki, repo_root=tmp_path,
        known_pages={"Home.md"},
    )
    assert any("repository-relative link" in failure for failure in failures)
    assert any("broken local" in failure for failure in failures)


def test_wiki_quality_audit_accepts_navigation_and_repo_evidence_links(tmp_path: Path) -> None:
    audit = _load_audit_module()
    repo_root = tmp_path / "repo"
    wiki_dir = repo_root / "wiki"
    evidence_dir = repo_root / "docs" / "operations"
    wiki_dir.mkdir(parents=True)
    evidence_dir.mkdir(parents=True)
    _set_github_origin(repo_root, "https://github.com/example/repo.git")
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
                "Evidence: [Runbook](https://github.com/example/repo/blob/main/docs/operations/runbook.md)",
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

    (wiki_dir / "Home.md").write_text(
        "# Home\n\n[Runbook](docs/runbook.md)\n\n"
        "[Reference runbook][runbook]\n\n[runbook]: ../docs/runbook.md\n"
        "[Root runbook](/docs/runbook.md)\n",
        encoding="utf-8",
    )

    failures = audit.audit_wiki(wiki_dir, repo_root)

    assert (
        "Home.md: repository-relative link must use a main-anchored GitHub blob/tree URL: docs/runbook.md"
        in failures
    )
    assert (
        "Home.md: publication-unsafe parent-relative link: ../docs/runbook.md"
        in failures
    )

    assert (
        "Home.md: publication-unsafe root-relative link: /docs/runbook.md"
        in failures
    )


def test_wiki_quality_audit_ignores_unused_reference_definitions_for_navigation(
    tmp_path: Path,
) -> None:
    audit = _load_audit_module()
    repo_root = tmp_path / "repo"
    wiki_dir = repo_root / "wiki"
    wiki_dir.mkdir(parents=True)
    (wiki_dir / "Home.md").write_text(
        "# Home\n\n[old]: Orphan.md\n", encoding="utf-8"
    )
    (wiki_dir / "_Sidebar.md").write_text(
        "# Navigation\n\n- [Home](Home.md)\n", encoding="utf-8"
    )
    (wiki_dir / "Orphan.md").write_text("# Orphan\n", encoding="utf-8")

    failures = audit.audit_wiki(wiki_dir, repo_root)

    assert "Orphan.md: page is not reachable from Home.md or _Sidebar.md" in failures


def test_wiki_quality_audit_uses_shortcut_colons_and_first_reference_definition(
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
        "# Home\n\nSee [runbook]: operational details.\n\n"
        "[runbook]: ../docs/runbook.md\n"
        "[RUNBOOK]: Home.md\n",
        encoding="utf-8",
    )
    (wiki_dir / "_Sidebar.md").write_text(
        "# Navigation\n\n- [Home](Home.md)\n", encoding="utf-8"
    )

    failures = audit.audit_wiki(wiki_dir, repo_root)

    assert (
        "Home.md: publication-unsafe parent-relative link: ../docs/runbook.md"
        in failures
    )

    for invalid_destination in ("operational(details", "operational)details"):
        (wiki_dir / "Home.md").write_text(
            f"# Home\n\n[runbook]: {invalid_destination}\n\n"
            "[runbook]: ../docs/runbook.md\n",
            encoding="utf-8",
        )

        failures = audit.audit_wiki(wiki_dir, repo_root)

        assert (
            "Home.md: publication-unsafe parent-relative link: ../docs/runbook.md"
            in failures
        )

    (wiki_dir / "Home.md").write_text(
        "# Home\n\n[Runbook][runbook]\n\n[runbook]: ../docs\\\n",
        encoding="utf-8",
    )

    failures = audit.audit_wiki(wiki_dir, repo_root)

    assert (
        "Home.md: publication-unsafe parent-relative link: ../docs/" in failures
    )

    (wiki_dir / "Home.md").write_text(
        "# Home\n\n[runbook]: operational details.\n\n"
        "[runbook]: ../docs/runbook.md\n",
        encoding="utf-8",
    )

    failures = audit.audit_wiki(wiki_dir, repo_root)

    assert (
        "Home.md: publication-unsafe parent-relative link: ../docs/runbook.md"
        in failures
    )


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
