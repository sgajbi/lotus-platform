"""Whether a subject is discoverable by following links from the repo context.

The repository context is a router: it states ownership and boundaries and links
to the document that owns each subject. Asserting that it CONTAINS every subject
re-inlines exactly what the routing exists to distribute, and pins one file's
structure so that moving a subject to its authoritative home reads as a
regression. These helpers ask the question a reader actually has instead: can I
get there from here, and in how many steps.

Two hops by default, which is what progressive discovery is meant to cost --
the context names an index, the index names the document.
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
REPO_CONTEXT = ROOT / "REPOSITORY-ENGINEERING-CONTEXT.md"

# Relative markdown links only. An absolute URL leaves the checkout, so it is
# not a route a reader can follow offline.
_LINK = re.compile(r"\]\((\.{1,2}/[^)#]+)")


def _linked_documents(document: Path) -> list[Path]:
    """Markdown documents this one links to, resolved against its own directory."""
    try:
        text = document.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    targets = []
    for raw in _LINK.findall(text):
        candidate = (document.parent / unquote(raw)).resolve()
        if candidate.is_file() and candidate.suffix.lower() == ".md":
            targets.append(candidate)
    return targets


def documents_reachable_from_repo_context(max_hops: int = 2) -> set[Path]:
    """Every document reachable from the repository context within max_hops."""
    seen = {REPO_CONTEXT}
    frontier = [REPO_CONTEXT]
    for _ in range(max_hops):
        next_frontier: list[Path] = []
        for document in frontier:
            for linked in _linked_documents(document):
                if linked not in seen:
                    seen.add(linked)
                    next_frontier.append(linked)
        frontier = next_frontier
    return seen


def subject_is_reachable(subject: str, max_hops: int = 2) -> bool:
    """True when some document reachable from the repository context names it."""
    for document in documents_reachable_from_repo_context(max_hops):
        try:
            if subject in document.read_text(encoding="utf-8"):
                return True
        except (OSError, UnicodeDecodeError):
            continue
    return False
