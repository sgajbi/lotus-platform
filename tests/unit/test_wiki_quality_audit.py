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


DIRECTORY_IMAGE_MARKER_CASES = [
    (
        "\\" * count + f"![temporary directory]{suffix} {qualifier}{definition}",
        count % 2 == 0 and suffix in {"(Operations-Runbook)", "[target]"},
    )
    for count in range(5)
    for suffix, definition in (
        ("(Operations-Runbook)", ""),
        ("[target]", "\n\n[target]: Operations-Runbook"),
        ("[]", "\n\n[temporary directory]: Operations-Runbook"),
        ("", "\n\n[temporary directory]: Operations-Runbook"),
    )
    for qualifier in ("notes", "**workaround**")
] + [
    ("\\" * count + f"![{label}]{suffix} {continuation}{definition}", True)
    for count in range(5)
    for suffix, definition in (
        ("(Operations-Runbook)", ""),
        ("[target]", "\n\n[target]: Operations-Runbook"),
    )
    for label, continuation in (
        ("temporary directory with mode 0700", "notes explain permissions."),
        ("temporary directory", "mode 0700 protects diagnostics."),
    )
] + [
    ("[prefix " + "\\" * count + "![page](Home) temporary directory](Operations-Runbook) notes", bool(count % 2))
    for count in range(5)
] + [
    ("\\" * count + "![prefix [temporary directory](Operations-Runbook)](Home) notes", True)
    for count in range(5)
] + [
    (r"\!\[temporary directory](Operations-Runbook) notes", True),
    (r"\![temporary directory\](Operations-Runbook) notes", True),
    (r"`\![temporary directory](Operations-Runbook) notes`", True),
    (r"\![temporary directory][missing] notes", True),
    (r"\![temporary directory](Operations-Runbook notes", True),
    (r"\![temporary directory **notes**](Operations-Runbook)", False),
    (r"![temporary directory **notes**](Operations-Runbook)", False),
] + [
    (f"\\![temporary directory](Operations-Runbook){newline}notes", True)
    for newline in ("\r", "\n", "\r\n")
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


SECURITY_DECISION_STATEMENT = (
    "A proposed temporary decision requires an accountable reviewed owner and at most "
    "seven days from approval, with earlier reassessment on published stable fixes, "
    "image/package changes or weaker controls."
)
SECURITY_DECISION_PERFORMANCE_PARAGRAPH = (
    "These controls reduce privilege exposure without fixing package advisories. Eight container\n"
    "acceptances expired on 2026-10-05; #624 retains fresh scan evidence and the pending decision.\n"
    "Do not extend dates or remove findings because a helper/module is currently unreachable. A\n"
    "proposed temporary decision requires an accountable reviewed owner and at most seven days from\n"
    "approval, with earlier reassessment on published stable fixes, image/package changes or weaker\n"
    "controls. Source ownership is not institutional risk approval. Read the\n"
    "[supply-chain report](https://github.com/sgajbi/lotus-performance/blob/main/quality/container_supply_chain_report.md)\n"
    "for per-advisory applicability, native commands and refusal boundaries."
)
SECURITY_DECISION_CASES = [
    (SECURITY_DECISION_PERFORMANCE_PARAGRAPH, True),
    (SECURITY_DECISION_STATEMENT + " Source ownership is not institutional risk approval.", True),
    (SECURITY_DECISION_STATEMENT.replace(" reviewed owner", " reviewed\nowner"), True),
    (SECURITY_DECISION_STATEMENT.replace(" from approval", " from\r\napproval"), True),
    (SECURITY_DECISION_STATEMENT.replace("seven days", "1 day"), True),
    (SECURITY_DECISION_STATEMENT.replace("seven days", "14 days"), True),
    (SECURITY_DECISION_STATEMENT.replace("seven days", "ten days"), True),
    (SECURITY_DECISION_STATEMENT.upper(), True),
    ("<!-- " + SECURITY_DECISION_STATEMENT + " -->", False),
    ('<span title="' + SECURITY_DECISION_STATEMENT + '">Pending decision.</span>', False),
    ("`" + SECURITY_DECISION_STATEMENT + "`", False),
    ("Unfinished decision notes: " + SECURITY_DECISION_STATEMENT, False),
    ("<!-- Explanation.\n\n" + SECURITY_DECISION_STATEMENT + " -->", False),
    ('<span title="Explanation. ' + SECURITY_DECISION_STATEMENT + '">Pending.</span>', False),
    ("`Explanation. " + SECURITY_DECISION_STATEMENT + "`", False),
    ("Decision **notes**: " + SECURITY_DECISION_STATEMENT, False),
    ('[Operations](Home "Context. ' + SECURITY_DECISION_STATEMENT + '")', False),
    ('[ops]: Home "Context. ' + SECURITY_DECISION_STATEMENT + '"', False),
    ("A proposed temporary decision remains pending.", False),
    (SECURITY_DECISION_STATEMENT.replace("an accountable reviewed owner and ", ""), False),
    (SECURITY_DECISION_STATEMENT.replace("at most seven days from approval", "a deadline"), False),
    (SECURITY_DECISION_STATEMENT.replace(
        ", with earlier reassessment on published stable fixes, image/package changes or weaker controls", ""
    ), False),
    (SECURITY_DECISION_STATEMENT.replace(" and at most", ". At most"), False),
    (SECURITY_DECISION_STATEMENT.replace(" reviewed owner", " reviewed\n\nowner"), False),
    (SECURITY_DECISION_STATEMENT.replace("seven days", "0 days"), False),
    (SECURITY_DECISION_STATEMENT.replace("seven days", "-1 days"), False),
    (SECURITY_DECISION_STATEMENT.replace("seven days", "07 days"), False),
    (SECURITY_DECISION_STATEMENT.replace("seven days", "1.5 days"), False),
    (SECURITY_DECISION_STATEMENT.replace("seven days", "eleven days"), False),
    (SECURITY_DECISION_STATEMENT.replace("decision requires", "decision notes require"), False),
    (SECURITY_DECISION_STATEMENT.replace("decision requires", "decision **notes** requires"), False),
    (SECURITY_DECISION_STATEMENT.replace("decision requires", "decision `workaround` requires"), False),
    (SECURITY_DECISION_STATEMENT.replace("weaker controls", "notes"), False),
    (SECURITY_DECISION_STATEMENT.replace("weaker controls", "**workaround**"), False),
    (SECURITY_DECISION_STATEMENT + " TODO finish the review.", False),
    (SECURITY_DECISION_STATEMENT + " TBD obtain approval.", False),
    (SECURITY_DECISION_STATEMENT + " FIXME record ownership.", False),
    (SECURITY_DECISION_STATEMENT + " A temporary workaround remains.", False),
    (SECURITY_DECISION_STATEMENT.replace(
        "an accountable reviewed owner", "[an accountable reviewed owner](Home)"
    ), False),
    (SECURITY_DECISION_STATEMENT.replace(
        "an accountable reviewed owner", "<span title='an accountable reviewed owner'>owner</span>"
    ), False),
    (SECURITY_DECISION_STATEMENT.replace(
        "an accountable reviewed owner", "<!-- an accountable reviewed owner -->owner"
    ), False),
    (SECURITY_DECISION_STATEMENT.replace(
        "an accountable reviewed owner", "`an accountable reviewed owner`"
    ), False),
    ("A proposed temporary decision requires ownership.\n```\n"
     "an accountable reviewed owner and at most seven days from approval, with earlier reassessment\n```", False),
]


@pytest.mark.parametrize("prose, accepted", SECURITY_DECISION_CASES)
def test_security_decision_prose_actual_and_cli(tmp_path: Path, prose: str, accepted: bool) -> None:
    _assert_directory_prose_actual_and_cli(tmp_path, prose, accepted)


SECURITY_DECISION_HTML_CONTEXT_CASES = [
    (f"<{tag}{attribute}>Context. {SECURITY_DECISION_STATEMENT}</{tag}>", False)
    for tag, attribute in (
        ("span", " hidden"), ("div", ""), ("script", ""), ("style", ""),
        ("span", ' title="Context. earlier statement"'),
        ("span", ' data-note="owner > Context." hidden'),
    )
] + [
    (f"<{tag}{attribute}>Context.\n\n{SECURITY_DECISION_STATEMENT}</{tag}>", False)
    for tag, attribute in (("span", " hidden"), ("div", ""), ("script", ""), ("style", ""))
] + [
    ("<div><span hidden>Context.</span>\n\n" + SECURITY_DECISION_STATEMENT + "</div>", False),
    ("<SPAN HIDDEN>Context. " + SECURITY_DECISION_STATEMENT + "</SPAN>", False),
    ("<span hidden/>Context. " + SECURITY_DECISION_STATEMENT, False),
    ("<div><span>Context.</div>\n\n" + SECURITY_DECISION_STATEMENT, False),
    ("<span hidden>Context.", True),
    (SECURITY_DECISION_STATEMENT, True),
    ("<span hidden>Earlier context.</span>\n\n" + SECURITY_DECISION_STATEMENT, True),
    ("<div><span>Earlier context.</span></div>\n\n" + SECURITY_DECISION_STATEMENT, True),
    ("<script>Earlier context.</script>\n\n" + SECURITY_DECISION_STATEMENT, True),
    ("<style>Earlier context.</style>\n\n" + SECURITY_DECISION_STATEMENT, True),
    ("<!-- <span hidden>Earlier context. -->\n\n" + SECURITY_DECISION_STATEMENT, True),
    ("`<span hidden>Earlier context.`\n\n" + SECURITY_DECISION_STATEMENT, True),
    (r"\<span hidden>Earlier context." + "\n\n" + SECURITY_DECISION_STATEMENT, True),
    ("<br>\n\n" + SECURITY_DECISION_STATEMENT, True),
    ('<img src="diagnostic.png">\n\n' + SECURITY_DECISION_STATEMENT, True),
    ("<span title=\"" + SECURITY_DECISION_STATEMENT + '\">Context.</span>', False),
    ("<!-- Context.\n\n" + SECURITY_DECISION_STATEMENT + " -->", False),
]


@pytest.mark.parametrize("prose, accepted", SECURITY_DECISION_HTML_CONTEXT_CASES)
def test_security_decision_html_context_actual_and_cli(tmp_path: Path, prose: str, accepted: bool) -> None:
    _assert_directory_prose_actual_and_cli(tmp_path, prose, accepted)


SECURITY_DECISION_MALFORMED_HTML_CASES = [
    ("</span>", False),
    ("Context.</span>", False),
    ("Context.\n\n</span>\n\n", False),
    ("</SPAN>", False),
    ("</br>", False),
    ("<div><span>Context.</div></span></div>", False),
    ("<span>Context.</div></span>", False),
    ("<span>Context.</span></span>", False),
    ("<div><span>Context.</span></div>", True),
    ("<span>Context.</span><div>More context.</div>", True),
    ("`</span>`", True),
    ("<!-- </span> -->", True),
    ('<span title="</div>">Context.</span>', True),
    (r"\</span>", True),
]


@pytest.mark.parametrize("prefix, accepted", SECURITY_DECISION_MALFORMED_HTML_CASES)
def test_security_decision_malformed_html_context_actual_and_cli(
    tmp_path: Path, prefix: str, accepted: bool,
) -> None:
    _assert_directory_prose_actual_and_cli(
        tmp_path, prefix + "\n\n" + SECURITY_DECISION_STATEMENT, accepted,
    )


SECURITY_DECISION_RAW_CONTEXT_CASES = [
    (f"{opening}Context.{separator}{SECURITY_DECISION_STATEMENT}{closing}", False)
    for opening, closing in (("<?instruction ", "?>"), ("<!DOCTYPE ", ">"),
                             ("<![CDATA[", "]]>"), ("<!--", "-->"))
    for separator in (" ", "\n\n")
] + [
    (opening + "Context.\n\n" + SECURITY_DECISION_STATEMENT, False)
    for opening in ("<?instruction ", "<!DOCTYPE ", "<![CDATA[", "<!--")
] + [
    (opening + "Context." + closing + "\n\n" + SECURITY_DECISION_STATEMENT, True)
    for opening, closing in (("<?instruction ", "?>"), ("<!DOCTYPE ", ">"),
                             ("<![CDATA[", "]]>"), ("<!--", "-->"))
] + [
    (opening + "Context." + closing + " Context. " + SECURITY_DECISION_STATEMENT, False)
    for opening, closing in (("<?instruction ", "?>"), ("<!DOCTYPE ", ">"),
                             ("<![CDATA[", "]]>"), ("<!--", "-->"))
] + [
    (f"<{tag}{opener_suffix}Context.\n\n{SECURITY_DECISION_STATEMENT}</{tag}>", False)
    for tag in ("pre", "script", "style", "textarea")
    for opener_suffix in (">", "\n")
] + [
    (f"<{tag}\nContext.\n\n{SECURITY_DECISION_STATEMENT}", False)
    for tag in ("pre", "script", "style", "textarea")
] + [
    (f"<{tag}\nContext.</{tag}>\n\n{SECURITY_DECISION_STATEMENT}", True)
    for tag in ("pre", "script", "style", "textarea")
] + [
    ("   <?instruction Context.\r\n\r\n" + SECURITY_DECISION_STATEMENT + "?>", False),
    ("<!A Context.\n\n" + SECURITY_DECISION_STATEMENT + ">", False),
    ("<SCRIPT\tContext.\n\n" + SECURITY_DECISION_STATEMENT + "</SCRIPT>", False),
    ("<textarea>Context.</textarea> Context. " + SECURITY_DECISION_STATEMENT, False),
    ("<?instruction Context.\n`?>` Context. " + SECURITY_DECISION_STATEMENT, False),
    ("<![CDATA[Context.\n<!-- ]]> Context. " + SECURITY_DECISION_STATEMENT, False),
    ("<script>Context.\n`</script>`\n\n" + SECURITY_DECISION_STATEMENT, True),
    ("<style>Context.\n<!-- </style>\n\n" + SECURITY_DECISION_STATEMENT, True),
    ("<?instruction <!-- <span> --> ?>\n\n" + SECURITY_DECISION_STATEMENT, True),
    ("<![CDATA[<? <span> --> ]]>\n\n" + SECURITY_DECISION_STATEMENT, True),
    ("<!DOCTYPE '<? <span>'>\n\n" + SECURITY_DECISION_STATEMENT, True),
    ("<!-- <? <![CDATA[ <!DOCTYPE <script -->\n\n" + SECURITY_DECISION_STATEMENT, True),
    ('<span title="<? <![CDATA[ <!DOCTYPE <!-- <script">Context.</span>\n\n'
     + SECURITY_DECISION_STATEMENT, True),
    ('<script title="</script>">Context.\n\n' + SECURITY_DECISION_STATEMENT, False),
    ("<!-->\n\n" + SECURITY_DECISION_STATEMENT, True),
    ("<!--->\n\n" + SECURITY_DECISION_STATEMENT, True),
    ("<instruction@example.test>\n\n" + SECURITY_DECISION_STATEMENT, True),
    ("Context.\n`<? <![CDATA[ <!DOCTYPE <!-- <script`\n\n" + SECURITY_DECISION_STATEMENT, True),
] + [
    ("\\" + opening + "Context.\n\n" + SECURITY_DECISION_STATEMENT, True)
    for opening in ("<?instruction ", "<!DOCTYPE ", "<![CDATA[", "<!--", "<script\n")
]


@pytest.mark.parametrize("prose, accepted", SECURITY_DECISION_RAW_CONTEXT_CASES)
def test_security_decision_raw_context_actual_and_cli(tmp_path: Path, prose: str, accepted: bool) -> None:
    _assert_directory_prose_actual_and_cli(tmp_path, prose, accepted)


SECURITY_DECISION_TRIGGER_CONTEXT_CASES = [
    (SECURITY_DECISION_STATEMENT.partition(" on ")[0] + suffix, accepted)
    for suffix, accepted in (
        (" on ,.", False), (" on /-.", False), (" on ,/-\t.", False),
        (" on ,\r\n/-. ", False), (" on   .", False), (" on\t\n.", False),
        (" on stable fixes.", True), (" on a.", True), (" on 0.", True),
        (" on 3/7.", True), (" on , a /-.", True), (" on ,0/-.", True),
        (".", True), (" on fixesé.", False), (" on K.", False),
        (" on Kx.", False), (" on İ.", False), (" on ı.", False), (" on ſ.", False),
    )
] + [
    (separator.join([SECURITY_DECISION_STATEMENT] * 3), True)
    for separator in (" ", "\n\n", "\r\r", "\r\n\r\n")
] + [
    (SECURITY_DECISION_STATEMENT + "\n\n" + suffix, accepted)
    for suffix, accepted in (
        ("A temporary decision remains pending.", False),
        ("temporary temporary temporary", False),
        ("</span>", True),
        ("</span>\n\n" + SECURITY_DECISION_STATEMENT, False),
        ("<span>Context. " + SECURITY_DECISION_STATEMENT + "</span>", False),
        ("<!-- Context.\n\n" + SECURITY_DECISION_STATEMENT + " -->", False),
        ("<?instruction Context.\n\n" + SECURITY_DECISION_STATEMENT + "?>", False),
        ("<![CDATA[Context.\n\n" + SECURITY_DECISION_STATEMENT + "]]>", False),
        ("<script\nContext.\n\n" + SECURITY_DECISION_STATEMENT, False),
        ("<div>Earlier context.</div>\n\n" + SECURITY_DECISION_STATEMENT, True),
        ("<?instruction Earlier context.?>\n\n" + SECURITY_DECISION_STATEMENT, True),
        ("<![CDATA[Earlier context.]]>\n\n" + SECURITY_DECISION_STATEMENT, True),
        ("`<? <![CDATA[ <!-- <script`\n\n" + SECURITY_DECISION_STATEMENT, True),
        ("[Operations](Home) Context. " + SECURITY_DECISION_STATEMENT, False),
        ("[Operations](Home) Context.\n\n" + SECURITY_DECISION_STATEMENT, True),
    )
] + [
    (SECURITY_DECISION_STATEMENT.replace(". ", ".") + "\nContext.\n" + SECURITY_DECISION_STATEMENT, True),
    (SECURITY_DECISION_STATEMENT + "\n\n"
     + SECURITY_DECISION_STATEMENT.partition(" on ")[0] + " on /-.", False),
    ("A proposed\n\ntemporary decision requires an accountable reviewed owner and at most seven days "
     "from approval, with earlier reassessment.", False),
    (SECURITY_DECISION_STATEMENT[:-1] + "\n\n" + SECURITY_DECISION_STATEMENT, False),
]


@pytest.mark.parametrize("prose, accepted", SECURITY_DECISION_TRIGGER_CONTEXT_CASES)
def test_security_decision_trigger_and_multiple_contexts_actual_and_cli(
    tmp_path: Path, prose: str, accepted: bool,
) -> None:
    _assert_directory_prose_actual_and_cli(tmp_path, prose, accepted)


@pytest.mark.parametrize("repetitions", [16, 32, 64])
@pytest.mark.parametrize("kind", ["valid", "unfinished", "incomplete_prefix"])
def test_security_decision_context_work_is_page_local(
    monkeypatch: pytest.MonkeyPatch, repetitions: int, kind: str,
) -> None:
    audit = _load_audit_module()
    statements = {
        "valid": SECURITY_DECISION_STATEMENT,
        "unfinished": "A temporary decision remains pending.",
        "incomplete_prefix": "A proposed temporary decision remains pending.",
    }
    prose = "\n\n".join([statements[kind]] * repetitions)
    original_context = audit._decision_plain_starts
    original_token = audit._directory_literal_token_end
    traversals: list[int] = []
    positions: list[int] = []
    scanning_context = False

    def token(text: str, start: int) -> int | None:
        if scanning_context:
            positions.append(start)
        return original_token(text, start)

    def context(text: str, candidates: list[int]) -> set[int]:
        nonlocal scanning_context
        traversals.append(len(candidates))
        scanning_context = True
        try:
            return original_context(text, candidates)
        finally:
            scanning_context = False

    monkeypatch.setattr(audit, "_directory_literal_token_end", token)
    monkeypatch.setattr(audit, "_decision_plain_starts", context)
    failures = audit._page_prose_failures("Operations-Runbook.md", prose)
    assert bool(failures) == (kind != "valid")
    assert traversals == ([repetitions] if kind == "valid" else [])
    assert positions == sorted(set(positions))
    assert len(positions) <= len(prose)
    # A separate page must start its own traversal; no context leaks between calls.
    positions.clear()
    traversals.clear()
    assert audit._page_prose_failures("Operations-Runbook.md", SECURITY_DECISION_STATEMENT) == []
    assert traversals == [1]
    assert positions and positions[0] == 0


def test_security_decision_preserves_navigation_and_all_page_scope(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    _set_github_origin(repo_root, "https://github.com/example/repo.git")
    wiki = repo_root / "wiki"
    wiki.mkdir()
    (wiki / "Home.md").write_text("# Home\n\n[Operations](Operations-Runbook)\n", encoding="utf-8")
    (wiki / "_Sidebar.md").write_text("# Navigation\n\n[Home](Home)\n", encoding="utf-8")
    (wiki / "Operations-Runbook.md").write_text(
        "# Operations Runbook\n\n" + SECURITY_DECISION_STATEMENT + "\n"
        "[Missing](Absent-Page)\nA temporary workaround remains TODO.\n", encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(AUDIT_PATH), "--wiki-dir", str(wiki), "--repo-root", str(repo_root),
         "--changed-page", "Home.md"], capture_output=True, text=True, check=False,
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "Operations-Runbook.md: contains scratch-note terms" in result.stdout
    assert "broken local or repo-relative link" in result.stdout


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


DIRECTORY_COMMENT_REFERENCE_CASES = [
    (f"{indent}<!--\n\n[{label}]: Operations-Runbook\n-->\n{noun} {qualifier}", "[target]" in noun)
    for indent in ("", " ", "  ", "   ")
    for noun, label in (
        ("[temporary directory][target]", "target"),
        ("[temporary directory][]", "temporary directory"),
        ("[temporary directory]", "temporary directory"),
    )
    for qualifier in ("notes", "**workaround**")
] + [
    (newline.join(("<!--", "", "[target]: Operations-Runbook", "-->",
                   "[temporary directory][target] notes")), True)
    for newline in ("\r", "\n", "\r\n")
] + [
    ("<!--\n\n[target]: Operations-Runbook\n-->\n[temporary directory][target] mode 0700", True),
    ("<!--\n\n[target]: Operations-Runbook\n-->\n[temporary directory][missing] notes", True),
    ("<!--\n\n[target]: Operations-Runbook\n[temporary directory][target] notes", True),
    ("<!--\n\n<!-- nested opener\n[target]: Operations-Runbook\n-->\n[temporary directory][target] notes", True),
    ("<!--\n\n[target]: Operations-Runbook\n-->\n<!-- second\n\n[other]: Operations-Runbook\n-->\n[temporary directory][other] notes", True),
    ("<!--\n\n--> [target]: Operations-Runbook\n[temporary directory][target] notes", True),
    ("<!--\n\n[target]: Operations-Runbook\n--> [other]: Operations-Runbook\n[temporary directory][other] notes", True),
    ("<!-- [target]: Operations-Runbook -->\n[temporary directory][target] notes", True),
    ("<!-- -->\n[target]: Operations-Runbook\n[temporary directory][target] notes", False),
    ("Intro paragraph.\n<!--\n\nignored\n-->\n[target]: Operations-Runbook\n[temporary directory][target] notes", False),
    ("<!--\nignored\nclosing -->\n[target]: Operations-Runbook\n[temporary directory][target] notes", False),
    ("<!--\nignored\n--> trailing raw content\n[target]: Operations-Runbook\n[temporary directory][target] notes", False),
    ("\n[target]: Operations-Runbook\n<!--\n\n[target]: Missing-Page\n-->\n[temporary directory][target] notes", False),
    ("<!-- -->\n[target]: Operations-Runbook invalid title\n[temporary directory][target] notes", True),
    ("<!-- -->\nOrdinary paragraph.\n[target]: Operations-Runbook\n[temporary directory][target] notes", True),
    ("<!-- -->\n```\n[target]: Operations-Runbook\n```\n[temporary directory][target] notes", True),
    ("\\<!--\n\n[target]: Operations-Runbook\n-->\n[temporary directory][target] notes", False),
    ("Intro <!-- inline opener -->\n\n[target]: Operations-Runbook\n[temporary directory][target] notes", False),
    ("    <!--\n\n[target]: Operations-Runbook\n-->\n[temporary directory][target] mode 0700", True),
    ("\t<!--\n\n[target]: Operations-Runbook\n-->\n[temporary directory][target] mode 0700", True),
]


@pytest.mark.parametrize("prose, accepted", DIRECTORY_COMMENT_REFERENCE_CASES)
def test_directory_comment_reference_policy_actual_and_cli(
    tmp_path: Path, prose: str, accepted: bool,
) -> None:
    _assert_directory_prose_actual_and_cli(tmp_path, prose, accepted)


DIRECTORY_REFERENCE_IDENTITY_SEPARATORS = ("\u00a0", "\u2003", "\v", "\f", "\x85", "\u2028", "\u2029", "\x1c")
DIRECTORY_REFERENCE_NORMALIZATION_CASES = [
    (label, label)
    for separator in DIRECTORY_REFERENCE_IDENTITY_SEPARATORS
    for label in (f"a{separator}b", f"{separator}a", f"a{separator}")
] + [
    (" \tA \t\r\n B\r ", "a b"), ("\rA\nB\t", "a b"),
    (" \t\r\n", ""), ("Straße", "strasse"), ("Kelvin", "kelvin"),
    ("A  B", "a b"),
]


@pytest.mark.parametrize("label, normalized", DIRECTORY_REFERENCE_NORMALIZATION_CASES)
def test_directory_reference_whitespace_normalization(label: str, normalized: str) -> None:
    assert _load_audit_module()._directory_reference_label(label) == normalized


DIRECTORY_REFERENCE_IDENTITY_CASES = [
    (use, definition, True)
    for separator in DIRECTORY_REFERENCE_IDENTITY_SEPARATORS
    for use, definition in (("a b", f"a{separator}b"), (f"a{separator}b", "a b"))
] + [
    (use, definition, True)
    for separator in ("\u00a0", "\u2003", "\f")
    for distinct in (f"{separator}ab", f"ab{separator}")
    for use, definition in (("ab", distinct), (distinct, "ab"))
] + [
    (f"a{separator}b", f"a{separator}b", False)
    for separator in DIRECTORY_REFERENCE_IDENTITY_SEPARATORS
] + [
    (" A\tb ", "a b", False), ("\ta b\t", " a\tb ", False),
    ("a b", " A B ", False), ("STRASSE", "Straße", False),
    ("KELVIN", "Kelvin", False), ("unknown", "known", True),
]


@pytest.mark.parametrize("use, definition, accepted", DIRECTORY_REFERENCE_IDENTITY_CASES)
def test_directory_reference_whitespace_identity_actual_and_cli(
    tmp_path: Path, use: str, definition: str, accepted: bool,
) -> None:
    prose = f"[temporary directory][{use}] notes\n\n[{definition}]: Operations-Runbook"
    _assert_directory_prose_actual_and_cli(tmp_path, prose, accepted)


@pytest.mark.parametrize("use, definition", [
    ("a b", "a\u00a0b"), ("a\u00a0b", "a b"),
    (" A\tb ", "a b"), ("a\u00a0b", "a\u00a0b"),
])
def test_directory_reference_whitespace_visible_scratch_actual_and_cli(
    tmp_path: Path, use: str, definition: str,
) -> None:
    prose = f"temporary directory: [notes][{use}]\n\n[{definition}]: Operations-Runbook"
    _assert_directory_prose_actual_and_cli(tmp_path, prose, False)


DIRECTORY_INLINE_TAG_GRAMMAR_CASES = [
    (f'<{name} title="temporary directory: notes">', True)
    for name in ("span", "SPAN", "s1", "custom-tag", "a--", "x2-y3")
] + [
    (f'<span {attribute} title="temporary directory: notes">', True)
    for attribute in (
        "hidden", "_hidden", ":hidden", "data.label", "xml:lang", "data-1",
        'x=""', "x=''", "x=plain", "x=plain/segment", 'x="a > <em>"',
        "x='a \" <em>'", 'x="a\n\nb"', 'x="back\\slash"',
        "x \t= \t'quoted'", "x\n=\n'quoted'", "x=literal&amp;entity",
    )
] + [
    (f'<span{separator}title="temporary directory: notes"{ending}>', True)
    for separator in (" ", "\t", "\n", "\r", "\r\n", " \t\n \t")
    for ending in ("", " ", "/", "\n/")
] + [
    (token, False)
    for token in (
        '<1span title="temporary directory: notes">',
        '<_span title="temporary directory: notes">',
        '<span.x title="temporary directory: notes">',
        '<span:x title="temporary directory: notes">',
        '< span title="temporary directory: notes">',
        '<span ="temporary directory: notes">',
        '<span 1title="temporary directory: notes">',
        '<span ti!tle="temporary directory: notes">',
        '<span x="hidden"title="temporary directory: notes">',
        '<span x= title="temporary directory: notes">',
        '<span x=bad`value title="temporary directory: notes">',
        '<span x=bad=value title="temporary directory: notes">',
        '<span x=bad\'value title="temporary directory: notes">',
        '<span title="temporary directory: notes> ',
        '<span title=\'temporary directory: notes> ',
        '<span title="temporary directory: notes"/ >',
        '<span title="temporary directory: notes"//>',
        '</span title="temporary directory: notes">',
        '<span\vtitle="temporary directory: notes">',
        '<span\ftitle="temporary directory: notes">',
        '<span\x85title="temporary directory: notes">',
        '<span\u2028title="temporary directory: notes">',
        '<span\n\ntitle="temporary directory: notes">',
        '<span x\n\n=hidden title="temporary directory: notes">',
        '<span x=\n\nhidden title="temporary directory: notes">',
        '<span title="temporary directory: notes"\n\n>',
    )
]


@pytest.mark.parametrize("token, recognized", DIRECTORY_INLINE_TAG_GRAMMAR_CASES)
def test_directory_inline_tag_complete_grammar(token: str, recognized: bool) -> None:
    audit = _load_audit_module()
    assert bool(audit.DIRECTORY_INLINE_TAG_PATTERN.fullmatch(token)) is recognized


@pytest.mark.parametrize("token, recognized", DIRECTORY_INLINE_TAG_GRAMMAR_CASES)
@pytest.mark.parametrize("consumer", ("hidden_noun", "qualifier"))
def test_directory_inline_tag_policy_actual_and_cli(
    tmp_path: Path, token: str, recognized: bool, consumer: str,
) -> None:
    if consumer == "hidden_noun":
        prose, accepted = token + "mode 0700", recognized
    else:
        prose = "temporary directory: " + token.replace("temporary directory: notes", "hidden metadata") + "notes"
        accepted = not recognized or "\n" in token or "\r" in token
    _assert_directory_prose_actual_and_cli(tmp_path, prose, accepted)


DIRECTORY_INLINE_TAG_CLOSING_CASES = [
    (f'</{name}{separator}>', True)
    for name in ("span", "CUSTOM-tag", "s1")
    for separator in ("", " ", "\t", "\n", "\r\n")
] + [(token, False) for token in (
    '</span extra>', '</span title="hidden">', '</span/>', '</ span>',
    '</1span>', '</span.x>', '</span\n\n>', '</span\v>',
)]


@pytest.mark.parametrize("token, recognized", DIRECTORY_INLINE_TAG_CLOSING_CASES)
def test_directory_inline_tag_closing_actual_and_cli(
    tmp_path: Path, token: str, recognized: bool,
) -> None:
    audit = _load_audit_module()
    assert bool(audit.DIRECTORY_INLINE_TAG_PATTERN.fullmatch(token)) is recognized
    accepted = not recognized or "\n" in token or "\r" in token
    _assert_directory_prose_actual_and_cli(tmp_path, "temporary directory: " + token + "notes", accepted)


DIRECTORY_INLINE_TAG_LITERAL_CASES = [
    (r'\<span title="temporary directory: notes">mode 0700', False),
    ('`<span title="temporary directory: notes">mode 0700`', False),
    ('Intro `<span title="temporary directory: notes\n">mode 0700`', False),
    ('<!-- temporary directory: notes -->mode 0700', True),
    ('<!--\ntemporary directory: notes\n-->mode 0700', True),
    ('<span title="temporary directory: notes">temporary directory: workaround</span>', False),
    ('<span title="temporary directory: notes">TODO finish</span>', False),
    ('temporary directory: <ops@example.com> notes', True),
    ('temporary directory: <span>n&#111;tes</span>', False),
    ('temporary directory: </span extra>notes', True),
    ('temporary directory: **<span>notes</span>**', False),
    ('temporary directory: [<span>notes</span>](Operations-Runbook)', False),
]


@pytest.mark.parametrize("prose, accepted", DIRECTORY_INLINE_TAG_LITERAL_CASES)
def test_directory_inline_tag_literal_policy_actual_and_cli(
    tmp_path: Path, prose: str, accepted: bool,
) -> None:
    _assert_directory_prose_actual_and_cli(tmp_path, prose, accepted)


DIRECTORY_MALFORMED_ANGLE_CASES = [
    (f"temporary directory: {token}{qualifier}", accepted)
    for token, accepted in (
        ("</ span>", True), ("< span>", True), ("</ /span>", True),
        ("</span extra>", True), ("<span", True), ("</span", True),
        ("<span title='unterminated>", True), ("<?span?>", True),
        ("<!DOCTYPE span>", True), ("<![CDATA[span]]>", True),
        ("</ >", False), ("<>", False), ("<!--", False),
        ("<span>", False), ("</span>", False), ("<!-- hidden -->", False),
        ('<span title="</ span>notes">', False),
    )
    for qualifier in ("notes", "workaround")
] + [
    ("temporary directory: **</ span>notes**", True),
    ("temporary directory: _</ span>workaround_", True),
    ("temporary directory: [</ span>notes](Operations-Runbook)", True),
    ("temporary directory: [<span>notes</span>](Operations-Runbook)", False),
    ("temporary directory: **<span>workaround</span>**", False),
    (r"temporary directory: \</ span>notes", True),
    (r"temporary directory: \<span>notes", True),
    ("temporary directory: `</ span>notes`", True),
    ("temporary directory: `<span>notes`", True),
    ("temporary directory: <ops@example.com> notes", True),
    ("temporary directory: n&#111;tes", False),
    ("temporary directory: work&#97;round", False),
    ("temporary directory: &#110;otes", False),
    ("temporary directory: &#60;/ span&#62;notes", True),
    ("temporary directory: &lt;span&gt;notes", True),
    ("temporary directory: &lt;&gt;notes", False),
    ("temporary directory: &amp;lt;span&amp;gt;notes", True),
    ("temporary directory: `n&#111;tes`", True),
    (r"temporary directory: n\&#111;tes", True),
    ("temporary directory: [n&#111;tes](Operations-Runbook)", False),
    ("temporary directory: **n&#111;tes**", False),
    ("temporary directory: notes_directory", True),
    ("temporary directory: workaround_mode", True),
    ("temporary directory: <span>mode 0700</span>", True),
    ("temporary directory: </ span>notes TODO finish", False),
] + [
    (f"temporary directory: </ span>{newline}notes", True)
    for newline in ("\r", "\n", "\r\n")
]


@pytest.mark.parametrize("prose, accepted", DIRECTORY_MALFORMED_ANGLE_CASES)
def test_directory_malformed_angle_policy_actual_and_cli(
    tmp_path: Path, prose: str, accepted: bool,
) -> None:
    _assert_directory_prose_actual_and_cli(tmp_path, prose, accepted)


def test_directory_malformed_angle_preserves_named_link_guard(tmp_path: Path) -> None:
    _assert_directory_prose_actual_and_cli(
        tmp_path, 'temporary directory: </ span>notes https://example.com',
        True, bare_url_failure_expected=True,
    )


DIRECTORY_MULTILINE_COMMENT_CASES = [
    (f"Intro <!--{separator}{noun}: {qualifier}{separator}--> mode 0700", True)
    for separator in ("\r", "\n", "\r\n", "\v", "\f", "\x85", "\u2028", "\u2029")
    for noun in ("temporary directory", "TEMPORARY DIRECTORIES")
    for qualifier in ("notes", "**workaround**")
] + [
    (f"Intro {ticks}<!--\ntemporary directory: notes\n-->{ticks}", False)
    for ticks in ("`", "``", "```", "````")
] + [
    (f"Intro {ticks}<!-- temporary directory: notes -->{ticks}", False)
    for ticks in ("`", "``", "```", "````")
] + [
    ("Intro `<!--\ntemporary directory: notes\n-->``", True),
    ("Intro ``<!--\ntemporary directory: notes\n-->`", True),
    ("Intro `literal\n` <!--\ntemporary directory: notes\n-->", True),
    ("Intro `<!--\ntemporary directory: notes\n-->` temporary directory: workaround", False),
    ("Intro \\<!--\ntemporary directory: notes\n-->", False),
    ("Intro \\\\<!--\ntemporary directory: notes\n-->", True),
    ("Intro <!--\ntemporary directory: notes", False),
    ("Intro <!--\ntemporary directory: notes\n-- >", False),
    ("Intro &lt;!--\ntemporary directory: notes\n--&gt;", False),
    ('<span title="<!--\ntemporary directory: notes\n-->">mode 0700</span>', True),
    ("<span title='<!--\ntemporary directory: workaround\n-->'>mode 0700</span>", True),
    ('Intro `<span title="<!--\ntemporary directory: notes\n-->">mode 0700</span>`', False),
    ('<span title="<!--\ntemporary directory: notes\n-->">temporary directory: notes</span>', False),
    ('<span title="<!--\nignored\n-->">temporary directory: notes</span>', False),
    ("<!--\ntemporary directory: notes\n-->temporary directory: workaround", False),
    ("temporary directory: notes <!--\ntemporary directory: workaround\n-->", False),
    ("temporary directory: <!--\nignored\n-->notes", True),
    ("temporary directory: <!-- ignored -->notes", False),
    ("<!--\ntemporary directory: notes; TODO finish\n-->", False),
    ("<!--\ntemporary directory: notes\n--> TODO finish", False),
    ("<!--\ntemporary directory: notes\n-->\n[target]: Operations-Runbook\n[temporary directory][target] notes", False),
    ("<!--\n[target]: Operations-Runbook\n-->\n[temporary directory][target] notes", True),
    ("Intro <!--\n```\ntemporary directory: notes\n```\n--> mode 0700", True),
    ("Intro <!--\n```\nignored\n```\n--> temporary directory: notes", False),
    ("```\n<!--\ntemporary directory: notes\n-->\n```\ntemporary directory: notes", False),
    ("Intro <!--\v```\ntemporary directory: notes\n--> mode 0700", True),
]


@pytest.mark.parametrize("prose, accepted", DIRECTORY_MULTILINE_COMMENT_CASES)
def test_directory_multiline_comment_policy_actual_and_cli(
    tmp_path: Path, prose: str, accepted: bool,
) -> None:
    _assert_directory_prose_actual_and_cli(tmp_path, prose, accepted)


def test_directory_multiline_comment_preserves_named_link_guard(tmp_path: Path) -> None:
    _assert_directory_prose_actual_and_cli(
        tmp_path, '<!--\ntemporary directory: notes; https://example.com\n-->',
        True, bare_url_failure_expected=True,
    )


DIRECTORY_RAW_SEPARATOR_CASES = [
    (f"temporary directory:{separator}{qualifier}", False)
    for separator in ("\v", "\f", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029")
    for qualifier in ("notes", "**workaround**")
] + [
    (f"temporary directory:{newline}{qualifier}", True)
    for newline in ("\r", "\n", "\r\n")
    for qualifier in ("notes", "**workaround**")
] + [
    (f"Intro.\n```\necho permissions\n```\ntemporary directory:{separator}notes", False)
    for separator in ("\v", "\f", "\x85", "\u2028")
] + [
    (f"Intro.{separator}[target]: Operations-Runbook\n[temporary directory][target] notes", True)
    for separator in ("\v", "\f", "\x85", "\u2028")
] + [
    (f"Intro.{separator}```\ntemporary directory: notes\n```", False)
    for separator in ("\v", "\f", "\x85", "\u2028")
] + [
    (f"Intro.\n<!-- hidden{separator}-->\n[target]: Operations-Runbook\n[temporary directory][target] notes", False)
    for separator in ("\v", "\f", "\x85", "\u2028")
] + [
    ("temporary directory:\vnotes_directory", True),
    ("temporary directory:\u2028mode 0700", True),
    ("temporary directory:\vnotes\n```\nTODO\n```", False),
]


DIRECTORY_HIDDEN_NOUN_CASES = [
    (token, True)
    for noun in ("temporary directory", "TEMPORARY DIRECTORIES")
    for qualifier in ("notes", "workaround")
    for token in (
        f'<span title="{noun}: {qualifier}">mode 0700</span>',
        f"<span title='{noun}: {qualifier}'>mode 0700</span>",
        f'<span data-label="{noun}: {qualifier}" title="[nested] > <em>">mode 0700</span>',
        f'<!-- {noun}: {qualifier} -->mode 0700',
    )
] + [
    ('<span title="temporary directory:\nnotes">mode 0700</span>', True),
    ('<span\ntitle="temporary directory: notes">mode 0700</span>', True),
    ('<span title="temporary directory: notes\n">mode 0700</span>', True),
    ('<span title="temporary directory: notes">temporary directory: notes</span>', False),
    ('<!-- temporary directory: notes -->temporary directory: workaround', False),
    ('temporary directory: <!-- temporary directory: workaround -->notes', False),
    ('temporary directory: <span title="temporary directory: notes">mode 0700</span>', True),
    ('temporary directory: <span title="temporary directory: notes">notes</span>', False),
    ('`<span title="temporary directory: notes">mode 0700</span>`', False),
    (r'\<span title="temporary directory: notes">mode 0700</span>', False),
    ('`<!-- temporary directory: notes -->`', False),
    (r'\<!-- temporary directory: notes -->', False),
    ('<span title="temporary directory: notes>mode 0700', False),
    ('<!-- temporary directory: notes', False),
    ('<span title="temporary directory: notes"><!-- temporary directory: workaround -->mode 0700</span>', True),
    ('<span title="temporary directory: notes">TODO finish</span>', False),
    ('<!-- temporary directory: notes; TODO finish -->mode 0700', False),
    ('<span title="temporary directory: notes">temporary workaround</span>', False),
    ('[<span title="temporary directory: notes">temporary directory</span>](Operations-Runbook) notes', False),
    ('[<span title="temporary directory: notes">mode 0700</span>](Operations-Runbook)', True),
    ('temporary directory: <ops@example.com> notes', True),
    ('temporary directory: &lt;span title="temporary directory: notes"&gt;mode 0700', False),
]


@pytest.mark.parametrize("prose, accepted", DIRECTORY_RAW_SEPARATOR_CASES)
def test_directory_raw_separator_policy_actual_and_cli(
    tmp_path: Path, prose: str, accepted: bool,
) -> None:
    _assert_directory_prose_actual_and_cli(tmp_path, prose, accepted)


@pytest.mark.parametrize("prose, accepted", DIRECTORY_HIDDEN_NOUN_CASES)
def test_directory_hidden_noun_policy_actual_and_cli(
    tmp_path: Path, prose: str, accepted: bool,
) -> None:
    _assert_directory_prose_actual_and_cli(tmp_path, prose, accepted)


def test_directory_hidden_noun_preserves_named_link_guard(tmp_path: Path) -> None:
    _assert_directory_prose_actual_and_cli(
        tmp_path, '<span title="temporary directory: notes">https://example.com</span>',
        True, bare_url_failure_expected=True,
    )


DIRECTORY_NESTED_AUTOLINK_CASES = [
    (f"[{label}](Operations-Runbook) notes", True)
    for autolink in ("<ops@example.com>", "<irc://example.com/[x]>")
    for label in (f"{autolink} temporary directory", f"temporary directory {autolink}")
] + [
    (f"[{label}][target] notes\n\n[target]: Operations-Runbook", True)
    for autolink in ("<ops@example.com>", "<irc://example.com/[x]>")
    for label in (f"{autolink} temporary directory", f"temporary directory {autolink}")
] + [
    ('[<ops@example.com> temporary directory][] notes\n\n[<ops@example.com> temporary directory]: Operations-Runbook', False),
    ('[<ops@example.com> temporary directory] notes\n\n[<ops@example.com> temporary directory]: Operations-Runbook', False),
    ('[temporary directory](Operations-Runbook) notes', False),
    ('[`<ops@example.com>` temporary directory](Operations-Runbook) notes', False),
    (r'[\<ops@example.com> temporary directory](Operations-Runbook) notes', False),
    ('[<!-- <ops@example.com> -->temporary directory](Operations-Runbook) notes', False),
    ('[<span title="<ops@example.com>">temporary directory</span>](Operations-Runbook) notes', False),
    ('[![<ops@example.com>](Operations-Runbook) temporary directory](Operations-Runbook) notes', False),
    ('[![<ops@example.com>][image] temporary directory](Operations-Runbook) notes\n\n[image]: Operations-Runbook', False),
    (r'[\![<ops@example.com>](Operations-Runbook) temporary directory](Operations-Runbook) notes', True),
    ('![<ops@example.com> temporary directory](Operations-Runbook) notes', True),
    ('`[<ops@example.com> temporary directory](Operations-Runbook) notes`', True),
    ('temporary directory: [<ops@example.com>](Operations-Runbook) notes', True),
    ('temporary directory: [notes <ops@example.com>](Operations-Runbook)', False),
    ('temporary directory: [![<ops@example.com>](Operations-Runbook) notes](Operations-Runbook)', True),
    ('[<ops@example.com> temporary directory](Operations-Runbook) mode 0700', True),
]


@pytest.mark.parametrize("prose, accepted", DIRECTORY_NESTED_AUTOLINK_CASES)
def test_directory_nested_autolink_policy_actual_and_cli(
    tmp_path: Path, prose: str, accepted: bool,
) -> None:
    _assert_directory_prose_actual_and_cli(tmp_path, prose, accepted)


DIRECTORY_AUTOLINK_GRAMMAR_CASES = [
    (f"<{local}@example.com>", True)
    for local in ("ops", "Ops", "1", "a.b", "a!b", "a#b", "a$b", "a%b", "a&b",
                  "a'b", "a*b", "a+b", "a/b", "a=b", "a?b", "a^b", "a_b",
                  "a`b", "a{b", "a|b", "a}b", "a~b", "a-b")
] + [
    (f"<ops@{domain}>", accepted)
    for domain, accepted in (("x", True), ("a-b.example", True), ("a" * 63, True),
                             ("a" * 64, False), ("-bad.com", False), ("bad-.com", False),
                             ("bad..com", False), ("bad_com", False), ("", False))
] + [
    (f"<{scheme}:payload>", accepted)
    for scheme, accepted in (("ab", True), ("HTTPS", True), ("a+b.c-d", True),
                             ("a" * 32, True), ("a" * 33, False), ("a", False),
                             ("1a", False), ("a_b", False))
] + [
    (f"<ab:{body}>", accepted)
    for body, accepted in (("", True), ("a%20b", True), ("[a]*_`&x;", True),
                           ("a\\b", True), ("a'b\"c", True), ("a b", False),
                           ("a\t", False), ("a\n", False), ("a\r", False),
                           ("a\x00", False), ("a\x1f", False), ("a\x7f", False),
                           ("a<b", False), ("a>b", False))
] + [("<ops\\+@example.com>", False), ("< ops@example.com>", False),
     ("<ops@example.com >", False), ("ops@example.com", False)]


@pytest.mark.parametrize("token, recognized", DIRECTORY_AUTOLINK_GRAMMAR_CASES)
def test_directory_autolink_complete_grammar(token: str, recognized: bool) -> None:
    audit = _load_audit_module()
    assert (audit.DIRECTORY_AUTOLINK_PATTERN.fullmatch(token) is not None) is recognized
    if recognized:
        assert audit._directory_qualifier_text(token, set()) == token[1:-1]


DIRECTORY_AUTOLINK_CASES = [
    (f"temporary directory: <{label}> notes the ownership exception", True)
    for label in ("ops@example.com", "Ops+audit@Example.COM", "1@x", "a.b@a-b.example",
                  "a&b@example.com", "a*b@example.com", "a_b@example.com", "a`b@example.com",
                  "irc://example.com", "MAILTO:ops@example.com", "ab:",
                  "a+b.c-d:payload", "irc://example.com/[x]*_`", "irc://example.com/a\\b",
                  "irc://example.com/?a=1&b=2", "irc://example.com/&lt;notes&gt;")
] + [
    ('temporary directory: <span title="ops@example.com">notes</span>', False),
    ('temporary directory: <span title="<ops@example.com>">notes</span>', False),
    ('temporary directory: <!-- <ops@example.com> -->notes', False),
    ('temporary directory: <ops@example.com> mode 0700', True),
    ('temporary directory: `notes`', False),
    ('temporary directory: `<ops@example.com>` notes', True),
    (r'temporary directory: \<ops@example.com> notes', True),
    ('temporary directory: < ops@example.com> notes', True),
    ('temporary directory: <ops@example.com notes', True),
    ('temporary directory: [<ops@example.com>](Operations-Runbook) notes', True),
    ('temporary directory: [<irc://example.com/[x]>](Operations-Runbook) notes', True),
    ('[temporary directory](Operations-Runbook) <ops@example.com> notes', True),
    ('temporary directory: **<ops@example.com>** notes', True),
    ('temporary directory: **n<ops@example.com>otes**', True),
    ('temporary directory: ![<ops@example.com>](Operations-Runbook) notes', True),
    ('temporary directory: <em>notes</em>', False),
    ('temporary directory: notes', False),
    ('temporary directory: **workaround**', False),
]


@pytest.mark.parametrize("prose, accepted", DIRECTORY_AUTOLINK_CASES)
def test_directory_autolink_policy_actual_and_cli(
    tmp_path: Path, prose: str, accepted: bool,
) -> None:
    _assert_directory_prose_actual_and_cli(tmp_path, prose, accepted)


@pytest.mark.parametrize("uri", [
    "https://example.com", "https://example.com/[x]*_`", "https://example.com/a\\b",
    "https://example.com/?a=1&b=2", "https://example.com/&lt;notes&gt;",
])
def test_directory_autolink_preserves_named_link_guard(tmp_path: Path, uri: str) -> None:
    _assert_directory_prose_actual_and_cli(
        tmp_path, f"temporary directory: <{uri}> notes the ownership exception", True,
        bare_url_failure_expected=True,
    )


DIRECTORY_NOUN_HTML_CASES = [
    (f'[{tag}temporary directory</span>](Operations-Runbook) {qualifier}', accepted)
    for tag in ('<span title="]">', "<span title='['>", '<span title="[nested]">')
    for qualifier, accepted in (("notes", False), ("**workaround**", False), ("mode 0700", True))
] + [
    ('[temporary directory](Operations-Runbook) notes', False),
    ('[<!-- ] -->temporary directory](Operations-Runbook) notes', False),
    ('[<span title="]">temporary directory</span>][target] notes\n\n[target]: Operations-Runbook', False),
    ('[<span title="]">temporary directory</span>][missing] notes', True),
    ('`[<span title="]">temporary directory</span>](Operations-Runbook) notes`', True),
    (r'\[<span title="]">temporary directory</span>](Operations-Runbook) notes', True),
    ('![<span title="]">temporary directory</span>](Operations-Runbook) notes', True),
    ('[<span title="]">OS [private] temporary directory</span>](Operations-Runbook) notes', False),
    ('[<span title="]">temporary directory</span> [owner](Operations-Runbook)](Operations-Runbook) notes', True),
    ('[<span title="]>temporary directory</span>](Operations-Runbook) notes', True),
]


@pytest.mark.parametrize("prose, accepted", DIRECTORY_NOUN_HTML_CASES)
def test_directory_noun_html_policy_actual_and_cli(
    tmp_path: Path, prose: str, accepted: bool,
) -> None:
    _assert_directory_prose_actual_and_cli(tmp_path, prose, accepted)


DIRECTORY_FENCE_BOUNDARY_CASES = [
    (f"Intro paragraph.\n{opening}\necho permissions\n{closing}\n"
     f"[{label}]: Operations-Runbook\n{noun} {qualifier}", False)
    for opening, closing in (("```", "```"), ("```sh", "```"), ("````sh", "````"))
    for noun, label in (
        ("[temporary directory][target]", "target"),
        ("[temporary directory][]", "temporary directory"),
        ("[temporary directory]", "temporary directory"),
    )
    for qualifier in ("notes", "**workaround**")
] + [
    (newline.join(("Intro paragraph.", "```", "echo permissions", "```",
                   "[target]: Operations-Runbook", "[temporary directory][target] notes")), False)
    for newline in ("\r", "\n", "\r\n")
] + [
    ("Intro paragraph.\n```\n```\n[target]: Operations-Runbook\n[temporary directory][target] notes", False),
    ("Intro paragraph.\n```\none\n```\n```\ntwo\n```\n[target]: Operations-Runbook\n[temporary directory][target] notes", False),
    ("Intro paragraph.\n```\nTODO temporary directory notes\n```\n[target]: Operations-Runbook\n[temporary directory][target] mode 0700", True),
    ("Intro paragraph.\n```\n[target]: Operations-Runbook\n```\n[temporary directory][target] notes", True),
    ("Intro paragraph.\n```\necho permissions\n```\n[temporary directory][missing] notes", True),
    ("Intro paragraph.\n```\necho permissions\n```\n[target]: Operations-Runbook invalid title\n[temporary directory][target] notes", True),
    ("Intro paragraph.\n[target]: Operations-Runbook\n[temporary directory][target] notes", True),
    ("Intro paragraph.\n\n[target]: Operations-Runbook\n[temporary directory][target] notes", False),
    ("temporary\n```\necho permissions\n```\ndirectory notes", False),
    ("temporary directory\n```\necho permissions\n```\nnotes", True),
    ("Intro paragraph.\n```\n[target]: Operations-Runbook\n[temporary directory][target] notes", True),
]


@pytest.mark.parametrize("prose, accepted", DIRECTORY_FENCE_BOUNDARY_CASES)
def test_directory_fence_boundary_policy_actual_and_cli(
    tmp_path: Path, prose: str, accepted: bool,
) -> None:
    _assert_directory_prose_actual_and_cli(tmp_path, prose, accepted)


DIRECTORY_SPLIT_QUALIFIER_CASES = [
    (f"temporary directory: {word[:split]}{marker}{word[split:]}{marker}", False)
    for word in ("notes", "workaround")
    for split in range(1, len(word))
    for marker in ("*", "**", "***", "****", "*****", "******", "`", "``", "~", "~~")
] + [
    (f"temporary directory: n[o]{suffix}tes{definition}", False)
    for suffix, definition in (
        ("(Operations-Runbook)", ""),
        ('(Operations-Runbook "mode 0700")', ""),
        ("[target]", "\n\n[target]: Operations-Runbook"),
        ("[]", "\n\n[o]: Operations-Runbook"),
        ("", "\n\n[o]: Operations-Runbook"),
    )
] + [
    ("temporary directory: **work**around", False),
    ("temporary directory: n**o**t`e`s", False),
    ("temporary directory: n` o `tes", False),
    ("temporary directory: n`` o ``tes", False),
    ("temporary directory: ` work `around", False),
    ("temporary directory: n`  o  `tes", True),
    ("temporary directory: n` o`tes", True),
    ("temporary directory: n`o `tes", True),
    ("temporary directory: n`   `otes", True),
    ("temporary directory: n`\to\t`tes", True),
    ("temporary directory: n***o***tes", False),
    ("temporary directory: n**[o](Operations-Runbook)**tes", True),
    ("temporary directory: n**o[te](Operations-Runbook)s**", False),
    ('temporary directory: n**o[te](Operations-Runbook "**metadata**")s**', False),
    ("temporary directory: n**o[te](https://example.com/**metadata**)s**", False),
    ("temporary directory: n**o[te](Operations-Runbook '**metadata**')s**", False),
    ("temporary directory: n**o[te](Operations-Runbook (operator **metadata**))s**", False),
    ("temporary directory: n**o[te][target]s**\n\n[target]: Operations-Runbook '**metadata**'", False),
    ("temporary directory: n[*o*](Operations-Runbook)tes", False),
    ("temporary directory: __work__around", True),
    ("temporary directory: _work_ around", True),
    ("temporary directory: **work** around", True),
    ("temporary directory: **work**-around", True),
    ("temporary directory: **work**/around", True),
    ("temporary directory: n_o_tes", True),
    ("temporary directory: n**o**tes_directory", True),
    ("temporary directory: n**o**teskeeper", True),
    (r"temporary directory: n\*o\*tes", True),
    (r"temporary directory: n\`o\`tes", True),
    ("temporary directory: n*otes", True),
    ("temporary directory: n**otes*", True),
    ("temporary directory: n`otes", True),
    ("temporary directory: n``o`tes", True),
    ("temporary directory: n[o][missing]tes", True),
    ("temporary directory: n[o](Operations-Runbook invalid title)tes", True),
    (r"temporary directory: n\[o](Operations-Runbook)tes", True),
    ("temporary directory: n![o](Operations-Runbook)tes", True),
    ("temporary directory: n`*o*`tes", True),
    ("temporary directory: n`[o](Operations-Runbook)`tes", True),
    ("temporary directory: n`<em>o</em>`tes", True),
    ("temporary directory: n`&#111;`tes", True),
    ("temporary directory: n<span title='**technical**'>o</span>tes", False),
    ("temporary directory: **mode 0700**", True),
    ("temporary directory: n[o](Operations-Runbook)tes_directory", True),
] + [
    (f"temporary directory: n**o**{newline}tes", True)
    for newline in ("\r", "\n", "\r\n")
]


@pytest.mark.parametrize("prose, accepted", DIRECTORY_SPLIT_QUALIFIER_CASES)
def test_directory_split_qualifier_policy_actual_and_cli(
    tmp_path: Path, prose: str, accepted: bool,
) -> None:
    _assert_directory_prose_actual_and_cli(tmp_path, prose, accepted)


@pytest.mark.parametrize("prose, accepted", DIRECTORY_IMAGE_MARKER_CASES)
def test_directory_image_marker_policy_actual_and_cli(
    tmp_path: Path, prose: str, accepted: bool,
) -> None:
    _assert_directory_prose_actual_and_cli(tmp_path, prose, accepted)


DIRECTORY_TILDE_CONTROL_CASES = [
    (f"temporary directory: {prefix}{left}{fragment}{right}{suffix}", True)
    for prefix, fragment, suffix in (("n", "o", "tes"), ("work", "a", "round"))
    for left, right in (("~~~", "~~~"), ("~~~~", "~~~~"), ("~", "~~"), ("~~", "~"), ("~", ""))
] + [
    (f"temporary directory: {prefix}{fragment}{suffix}", True)
    for prefix, suffix in (("n", "tes"),)
    for fragment in (r"\~o\~", "`~o~`", "``~o~``")
] + [
    (r"temporary directory: work\~a\~round", True),
    ("temporary directory: work`~a~`round", True),
    ("temporary directory: work``~a~``round", True),
    ("temporary directory: n~**o**~tes", True),
    ("temporary directory: work~<em>a</em>~round", True),
    ("temporary directory: n~o**te**s~", False),
    ("temporary directory: work~a<em>roun</em>d~", False),
    ("temporary directory: n~o[te](Operations-Runbook)s~", False),
    ("temporary directory: n[~o~](Operations-Runbook)tes", False),
    ("[temporary directory](Operations-Runbook) work~a~round", False),
    ("temporary directory: n~o[te][target]s~\n\n[target]: Operations-Runbook", False),
    ("temporary directory: n~[o](Operations-Runbook)~tes", True),
    ("temporary directory: n~`o`~tes", True),
    ("temporary directory: n~o`te`s~", False),
    ("temporary directory: n~`~o~`~tes", True),
    ("temporary directory: n~<span title='~metadata~'>o</span>~tes", True),
    ("temporary directory: n~o<span title='~metadata~'>te</span>s~", False),
    ("temporary directory: ~mode 0700~", True),
    ("temporary directory: ~notes_directory~", True),
    ("temporary directory: n~o~teskeeper", True),
    ("temporary directory: work~a~round_directory", True),
] + [
    (f"temporary directory: n~o~{newline}tes", True)
    for newline in ("\r", "\n", "\r\n")
]


@pytest.mark.parametrize("prose, accepted", DIRECTORY_TILDE_CONTROL_CASES)
def test_directory_tilde_controls_actual_and_cli(
    tmp_path: Path, prose: str, accepted: bool,
) -> None:
    _assert_directory_prose_actual_and_cli(tmp_path, prose, accepted)


DIRECTORY_FENCE_INDENT_CASES = [
    (f"Intro.{newline}{indent}```{newline}temporary directory: notes{newline}```", False)
    for newline in ("\n", "\r", "\r\n")
    for indent in ("\v", "\f", "\u0085", "\u2028", "\u2029", "\u00a0", "\u2003", "    ", "\t")
] + [
    (f"Intro.\n{indent}```\ntemporary directory: notes\n{indent}```", True)
    for indent in ("", " ", "  ", "   ")
] + [
    (f"Intro.\n```\nprivate code\n{indent}```\ntemporary directory: notes", False)
    for indent in ("", " ", "  ", "   ")
] + [
    ("Intro.\n```\nprivate code\n\v```\ntemporary directory: notes\n```", True),
    ("Intro.\n    ```\nUnindented temporary directory: notes", False),
]

DIRECTORY_SHORT_COMMENT_CASES = [
    (f"{token}temporary directory: {word}-->", False)
    for token in ("<!-->", "<!--->")
    for word in ("notes", "workaround")
] + [
    (f"temporary directory: {token}{word}-->", False)
    for token in ("<!-->", "<!--->")
    for word in ("notes", "workaround")
] + [
    ("<!--temporary directory: notes-->mode 0700", True),
    ("<!-- hidden\ntemporary directory: notes -->mode 0700", True),
    ("temporary directory: <!-- notes\nworkaround -->mode 0700", False),
    ("temporary directory: <!-- hidden--interior -->notes", False),
    ("temporary directory: <!---->notes", False),
    ("temporary directory: <!-->mode 0700", True),
    ("temporary directory: <!--->mode 0700", True),
    (r"temporary directory: \<!-->notes-->", False),
    ("temporary directory: `<!-->notes-->`", False),
    ("`<!-->temporary directory: notes-->`", False),
    ("temporary directory: <span title='<!-->notes-->'>mode 0700</span>", True),
    ("temporary directory: <span title='<!-->private-->'>notes</span>", False),
    ("temporary directory: n<!-->o<!--->tes", False),
    ("temporary directory: n<!--long\ncomment-->otes", True),
]

DIRECTORY_CHARACTER_REFERENCE_CASES = [
    (f"temporary directory: n{reference}tes", True)
    for reference in ("&#111", "&#x6f", "&#X6F", "&#00000111;", "&#x0000006f;",
                      "&#;", "&#x;", "&MadeUpEntity;", "&notit;", "&amp;#111;")
] + [
    (f"temporary directory: n{reference}tes", False)
    for reference in ("&#111;", "&#x6f;", "&#X6F;", "&#0000111;", "&#x00006f;")
] + [
    ("temporary directory: &#110;otes", False),
    ("temporary directory:&Tab;notes", False),
    ("temporary directory: work&#97round", True),
    ("temporary directory: work&#97;round", False),
    ("temporary directory: &copy;mode 0700", True),
    ("temporary directory: n`&#111;`tes", True),
    (r"temporary directory: n\&#111;tes", True),
    ("temporary directory: n<em>&#111;</em>tes", False),
    ("temporary directory: n<em>&#111</em>tes", True),
    ("temporary directory: n[&#111;](Operations-Runbook)tes", False),
    ("temporary directory: n[&#111](Operations-Runbook)tes", True),
    ("temporary directory: <ops&#111;@example.com> mode 0700", True),
]


@pytest.mark.parametrize("prose, accepted", DIRECTORY_FENCE_INDENT_CASES)
def test_directory_fence_indent_actual_and_cli(tmp_path: Path, prose: str, accepted: bool) -> None:
    _assert_directory_prose_actual_and_cli(tmp_path, prose, accepted)


@pytest.mark.parametrize("prose, accepted", DIRECTORY_SHORT_COMMENT_CASES)
def test_directory_short_comment_actual_and_cli(tmp_path: Path, prose: str, accepted: bool) -> None:
    _assert_directory_prose_actual_and_cli(tmp_path, prose, accepted)


@pytest.mark.parametrize("prose, accepted", DIRECTORY_CHARACTER_REFERENCE_CASES)
def test_directory_character_reference_actual_and_cli(tmp_path: Path, prose: str, accepted: bool) -> None:
    _assert_directory_prose_actual_and_cli(tmp_path, prose, accepted)


@pytest.mark.parametrize("prose", [
    "[temporary directory](foo<bar>) notes", "[temporary directory](foo>bar) notes",
    r"[temporary directory](foo\<bar\>) notes", r"[temporary directory](foo\>bar) notes",
])
def test_directory_bare_angles_preserve_scratch_and_navigation(tmp_path: Path, prose: str) -> None:
    _assert_directory_prose_actual_and_cli(tmp_path, prose, False, link_failure_expected=True)


DIRECTORY_REFERENCE_BLANK_CASES = [
    (
        ending.join(("Intro.", separator, f"[{label}]: Operations-Runbook", f"{use} notes")),
        not defines if use == "[temporary directory][target]" else False,
        {label} if defines else set(),
    )
    for ending in ("\n", "\r", "\r\n")
    for separator, defines in (
        ("\v", False), ("\f", False), ("\u0085", False), ("\u00a0", False),
        ("\u2028", False), ("\u2029", False), ("\u2003", False),
        ("", True), (" ", True), ("\t", True), (" \t ", True),
    )
    for label, use in (
        ("target", "[temporary directory][target]"),
        ("temporary directory", "[temporary directory][]"),
        ("temporary directory", "[temporary directory]"),
    )
]
DIRECTORY_REFERENCE_BLANK_CASES += [
    ("Intro.\n[target]: Operations-Runbook\n[temporary directory][target] notes", True, set()),
    ("\n[target]: Operations-Runbook\n[temporary directory][target] notes", False, {"target"}),
    ("Intro.\n\u00a0\n\n[target]: Operations-Runbook\n[temporary directory][target] notes", False, {"target"}),
    ("Intro.\n\v\n[other]: Operations-Runbook\n[temporary directory][target] notes", True, set()),
    ("Intro.\n\v\n[target]: Operations-Runbook\n`temporary directory` notes", False, set()),
    ("Intro.\n<!-- comment -->\n[target]: Operations-Runbook\n[temporary directory][target] notes", False, {"target"}),
    ("Intro.\n```text\n\u00a0\n```\n[target]: Operations-Runbook\n[temporary directory][target] notes", False, {"target"}),
]


@pytest.mark.parametrize("prose, accepted, references", DIRECTORY_REFERENCE_BLANK_CASES)
def test_directory_reference_blank_separators_actual_and_cli(
    tmp_path: Path, prose: str, accepted: bool, references: set[str],
) -> None:
    audit = _load_audit_module()
    assert audit._directory_reference_labels(audit._prose_without_fenced_code(prose)) == references
    _assert_directory_prose_actual_and_cli(tmp_path, prose, accepted)


def test_directory_reference_document_start_collector() -> None:
    assert _load_audit_module()._directory_reference_labels("[target]: Operations-Runbook") == {"target"}


def _assert_directory_prose_actual_and_cli(
    tmp_path: Path, prose: str, accepted: bool, *, link_failure_expected: bool = False,
    bare_url_failure_expected: bool = False,
) -> None:
    findings = _load_audit_module()._page_prose_failures("Operations-Runbook.md", prose)
    if bare_url_failure_expected:
        assert findings == ["Operations-Runbook.md: contains bare URL; use a named Markdown link"]
        findings = []
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
        newline="",
    )
    result = subprocess.run(
        [sys.executable, str(AUDIT_PATH), "--wiki-dir", str(wiki), "--repo-root",
         str(repo_root), "--changed-page", "Operations-Runbook.md"],
        capture_output=True, text=True, check=False,
    )
    expected_exit = 0 if accepted and not (link_failure_expected or bare_url_failure_expected) else 1
    assert result.returncode == expected_exit, result.stdout + result.stderr
    assert ("contains scratch-note terms" not in result.stdout) is accepted
    if link_failure_expected:
        assert "broken local or repo-relative link" in result.stdout
    if bare_url_failure_expected:
        assert "contains bare URL; use a named Markdown link" in result.stdout


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
