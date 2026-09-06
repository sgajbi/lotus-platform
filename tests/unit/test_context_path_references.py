"""Context documents must not name paths that do not exist.

The corpus asserts state: it names files, skills and contracts a session is
expected to open. A reference that has quietly stopped resolving is the same
class as a policy table naming another repository — confident documentation
that stopped being true, which nothing fails on and no gate catches.

Generic per-service paths are exempt by construction. A playbook telling every
service repository to keep `docs/api-governance.md` is describing a convention,
not claiming a file exists here, and flagging those would drown the real
findings. What is checked is a reference that names a repository or resolves
from this repository's root — a claim about something specific.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = REPO_ROOT.parent
CONTEXT = REPO_ROOT / "context"
REGISTERED_REPOSITORIES = {
    entry["name"]
    for entry in json.loads((REPO_ROOT / "automation" / "repos.json").read_text(encoding="utf-8"))
}

# Backtick-quoted paths ending in a source or document suffix.
_REFERENCE = re.compile(r"`([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:md|py|ps1|json|yml|yaml))`")

# A reference is "anchored" — a claim about a specific file — when it names a
# repository, or a directory that exists only in this repository.
_ANCHORS = ("lotus-", "context/", "codex/", "automation/", "platform-", "rfcs/", "wiki/")


def _is_anchored(reference: str) -> bool:
    return reference.startswith(_ANCHORS)


def _resolves(reference: str) -> bool:
    if reference.startswith("lotus-"):
        repository = reference.split("/", 1)[0]
        if repository in REGISTERED_REPOSITORIES and not (WORKSPACE / repository).exists():
            return True
    return any(
        candidate.exists()
        for candidate in (WORKSPACE / reference, REPO_ROOT / reference, CONTEXT / reference)
    )


def _anchored_references() -> list[tuple[Path, str]]:
    found: list[tuple[Path, str]] = []
    for document in sorted(CONTEXT.rglob("*.md")):
        text = document.read_text(encoding="utf-8", errors="replace")
        for match in _REFERENCE.finditer(text):
            reference = match.group(1)
            if "/" in reference and _is_anchored(reference):
                found.append((document, reference))
    return found


def test_every_anchored_context_reference_resolves() -> None:
    unresolved = [
        f"{document.relative_to(REPO_ROOT).as_posix()} -> {reference}"
        for document, reference in _anchored_references()
        if not _resolves(reference)
    ]
    assert not unresolved, (
        "these context documents name paths that do not exist; a reader "
        "following them finds nothing: " + "; ".join(sorted(set(unresolved)))
    )


def test_the_scan_reads_the_corpus() -> None:
    """A zero-input scan would pass while checking nothing."""
    documents = list(CONTEXT.rglob("*.md"))
    assert len(documents) > 5, f"only {len(documents)} context documents found"
    assert _anchored_references(), "no anchored references parsed; the assertion would be hollow"


def test_the_anchor_rule_separates_claims_from_conventions() -> None:
    """Both halves: a specific claim is checked, a per-service convention is not."""
    for claim in (
        "lotus-gateway/tests/unit/test_x.py",
        "context/LOTUS-ENGINEERING-CONTEXT.md",
        "automation/validate_x.py",
    ):
        assert _is_anchored(claim), f"{claim} names something specific and must be checked"
    for convention in ("docs/api-governance.md", "src/app/observability.py", "scripts/gate.py"):
        assert not _is_anchored(convention), (
            f"{convention} is a per-service convention, not a claim about this repository"
        )


def test_external_reference_is_optional_when_sibling_repository_is_absent(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setitem(globals(), "WORKSPACE", tmp_path)

    assert _resolves("lotus-workbench/docs/operations/runtime.md")
    assert not _resolves("lotus-wokrbench/docs/operations/runtime.md")
