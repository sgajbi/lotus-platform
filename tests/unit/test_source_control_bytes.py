"""Source files must not carry control bytes a shell escape produced.

A backslash escape written through an interpreting heredoc is expanded before
the file exists: ``\\b`` in a regex becomes a literal 0x08 backspace, ``\\t`` a
tab, ``\\f`` a formfeed. The corruption is invisible by construction — a
terminal does not render 0x08, a diff shows nothing unusual, and re-reading the
source cannot see it. Only the bytes can.

It is not hypothetical. A sibling repository's guard compiled to
``'\\x08([A-Z][a-z]+)-only\\x08'`` and passed on the exact defect it was written
to catch, because no real text contains a backspace. A guard corrupted this way
does not fail loudly; it silently matches nothing.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# Text suffixes plus extensionless files that are text by convention. The set of
# DIRECTORIES is deliberately not enumerated: a fixed list silently stops
# covering anything added outside it, and the root Makefile, pyproject.toml and
# compose files all sat outside the previous one.
TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".json",
    ".yml",
    ".yaml",
    ".ps1",
    ".sh",
    ".txt",
    ".toml",
    ".cfg",
    ".ini",
    ".sql",
    ".env",
    ".ts",
}
# Extensionless or dot-prefixed files that are text by convention. Each of these
# is also a scaffold output, so the `.backend.template` sources that render into
# them are governed through the `startswith` rule in `_is_governed_text`.
TEXT_FILENAMES = {
    "Makefile",
    "Dockerfile",
    ".gitignore",
    ".dockerignore",
    ".editorconfig",
    ".gitattributes",
}

# The scaffold is the reason this classifier exists: a corrupted template is
# copied verbatim into every repository generated afterwards, so a template
# outside the governed set is a defect that reproduces itself.
SCAFFOLD = REPO_ROOT / "automation" / "New-Lotus-Service.ps1"
TEMPLATE_ROOT = REPO_ROOT / "platform-standards" / "templates"
_SCAFFOLD_TEMPLATE = re.compile(r"Join-Path \$templateRoot \"(?P<name>[^\"]+)\"")


def scaffold_template_sources(scaffold: Path = SCAFFOLD) -> list[Path]:
    """Every template `New-Lotus-Service.ps1` copies into a generated repository.

    Derived from the scaffold rather than listed here: a hand-maintained list
    stops covering whatever is added next, which is exactly how
    `.editorconfig.backend.template` and `.gitattributes.backend.template` came
    to be copied into every generated repository while going unscanned.
    """
    text = scaffold.read_text(encoding="utf-8")
    return [
        TEMPLATE_ROOT / match.group("name")
        for match in _SCAFFOLD_TEMPLATE.finditer(text)
    ]


def is_suspicious(byte: int) -> bool:
    """True for control bytes never legitimate in these files.

    Tab (0x09), newline (0x0A) and carriage return (0x0D) are excluded: they are
    ordinary formatting. Everything else below 0x20 indicates an escape that was
    interpreted when it should have been written literally.
    """
    return byte < 0x09 or byte in (0x0B, 0x0C) or 0x0D < byte < 0x20 or byte == 0x7F


def _is_governed_text(path: Path) -> bool:
    if path.suffix.lower() in TEXT_SUFFIXES or path.name in TEXT_FILENAMES:
        return True
    if path.suffix.lower() != ".template":
        return False
    rendered_name = path.name.removesuffix(".template")
    return (
        Path(rendered_name).suffix.lower() in TEXT_SUFFIXES
        or rendered_name in TEXT_FILENAMES
        or any(rendered_name.startswith(f"{name}.") for name in TEXT_FILENAMES)
    )


def _tracked_text_files(repo_root: Path = REPO_ROOT) -> list[Path]:
    """Every tracked file git knows about that is text by suffix or name."""
    result = subprocess.run(
        ["git", "-C", str(repo_root), "ls-files", "-z"],
        capture_output=True,
        check=True,
    )
    paths = []
    for entry in result.stdout.split(b"\0"):
        if not entry:
            continue
        path = repo_root / entry.decode("utf-8")
        if not path.is_file():
            continue
        if _is_governed_text(path):
            paths.append(path)
    return paths


def _find_suspicious_control_bytes(paths: list[Path]) -> list[tuple[Path, int, int]]:
    offenders: list[tuple[Path, int, int]] = []
    for path in paths:
        data = path.read_bytes()
        for offset, byte in enumerate(data):
            if is_suspicious(byte):
                line = data[:offset].count(b"\n") + 1
                offenders.append((path, line, byte))
                break
    return offenders


def test_no_source_file_carries_an_interpreted_escape() -> None:
    offenders = _find_suspicious_control_bytes(_tracked_text_files())

    assert not offenders, (
        "these files carry control bytes, which a shell escape produces when a "
        "literal backslash sequence was meant; a pattern corrupted this way "
        "matches nothing and its guard passes silently: "
        + "; ".join(
            f"{path.relative_to(REPO_ROOT).as_posix()}:{line} byte=0x{byte:02x}"
            for path, line, byte in offenders
        )
    )


def test_the_scan_reads_a_meaningful_number_of_files() -> None:
    """A zero-input scan would pass while checking nothing."""
    files = _tracked_text_files()
    assert len(files) > 100, (
        f"only {len(files)} files scanned; the assertion would be hollow"
    )


def test_the_detector_recognises_each_corruption_it_exists_for() -> None:
    """Prove the check fails on the shapes it forbids, not only that it passes."""
    for escape, byte in (
        ("\\b", 0x08),
        ("\\f", 0x0C),
        ("\\v", 0x0B),
        ("\\a", 0x07),
        ("\\x7f", 0x7F),
    ):
        assert is_suspicious(byte), (
            f"{escape} expands to 0x{byte:02x} and must be rejected"
        )
    for legitimate in (0x09, 0x0A, 0x0D, 0x20, 0x41):
        assert not is_suspicious(legitimate), f"0x{legitimate:02x} is ordinary text"


def test_the_scan_reports_an_injected_interpreted_escape(tmp_path: Path) -> None:
    corrupted = tmp_path / "corrupted.md"
    corrupted.write_bytes(b"first line\nwrong\x08boundary\n")

    assert _find_suspicious_control_bytes([corrupted]) == [(corrupted, 2, 0x08)]


@pytest.mark.parametrize(
    "filename",
    [
        "Makefile.backend.template",
        "Dockerfile.python-service.template",
        ".editorconfig.backend.template",
        ".gitattributes.backend.template",
        ".gitignore.backend.template",
        ".dockerignore.backend.template",
    ],
)
def test_a_corrupted_tracked_template_is_discovered_and_rejected(
    filename: str, tmp_path: Path
) -> None:
    """Discovery and rejection proven together, on a really tracked file.

    Asserting only that the classifier returns True would pass even if
    `git ls-files` never surfaced the path, so the file is committed to a real
    repository and the corruption is found through the same scan CI runs.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
    template = repo / filename
    template.write_bytes(b"root = true\nwrong\x08boundary\n")
    subprocess.run(
        ["git", "-C", str(repo), "add", filename], check=True, capture_output=True
    )

    governed_files = _tracked_text_files(repo)

    assert governed_files == [template], f"{filename} is tracked but never scanned"
    assert _find_suspicious_control_bytes(governed_files) == [(template, 2, 0x08)]


def test_every_template_the_scaffold_copies_is_scanned() -> None:
    """A template outside the governed set corrupts every repository generated next."""
    templates = scaffold_template_sources()

    assert len(templates) >= 10, (
        f"only {len(templates)} templates parsed from {SCAFFOLD.name}; the "
        "assertion would be hollow if the copy syntax changed"
    )
    missing = [
        path.relative_to(REPO_ROOT).as_posix()
        for path in templates
        if not _is_governed_text(path)
    ]
    assert not missing, (
        "the scaffold copies these into every generated repository, but the "
        "control-byte scan does not read them: " + ", ".join(missing)
    )


def test_the_scaffold_templates_named_by_the_parser_really_exist() -> None:
    """A parser that silently matched nothing would make the coverage test hollow."""
    absent = [
        path.relative_to(REPO_ROOT).as_posix()
        for path in scaffold_template_sources()
        if not path.is_file()
    ]
    assert not absent, f"scaffold copies templates that do not exist: {absent}"
