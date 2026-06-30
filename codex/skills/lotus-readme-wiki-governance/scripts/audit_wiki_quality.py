from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote


LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
BARE_URL_PATTERN = re.compile(r"(?<!\]\()https?://\S+")
SCRATCH_PATTERN = re.compile(
    r"\b(TODO|maybe|rough|temp|temporary|TBD|FIXME)\b", re.IGNORECASE
)

ALLOWED_EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "#")
REQUIRED_PAGES = ("Home.md", "_Sidebar.md")


def _normalize_link_target(raw_target: str) -> str | None:
    target = raw_target.strip().split("#", 1)[0].strip()
    if not target or target.startswith(ALLOWED_EXTERNAL_PREFIXES):
        return None
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    target = unquote(target).replace("\\", "/")
    if not target.endswith("/") and not Path(target).suffix:
        target = f"{target}.md"
    return target.lstrip("./")


def _page_links(text: str) -> set[str]:
    links: set[str] = set()
    for match in LINK_PATTERN.finditer(text):
        target = _normalize_link_target(match.group(1))
        if target:
            links.add(target)
    return links


def _read_pages(wiki_dir: Path) -> dict[str, str]:
    pages: dict[str, str] = {}
    for path in sorted(wiki_dir.glob("*.md")):
        pages[path.name] = path.read_text(encoding="utf-8")
    return pages


def _first_nonblank_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def _target_exists(target: str, *, wiki_dir: Path, repo_root: Path, known_pages: set[str]) -> bool:
    target_name = Path(target).name
    if target_name in known_pages:
        return True
    return (repo_root / target).exists() or (wiki_dir / target).exists()


def audit_wiki(wiki_dir: Path, repo_root: Path) -> list[str]:
    failures: list[str] = []
    if not wiki_dir.exists():
        return [f"wiki directory does not exist: {wiki_dir}"]
    if not wiki_dir.is_dir():
        return [f"wiki path is not a directory: {wiki_dir}"]

    pages = _read_pages(wiki_dir)
    if not pages:
        return [f"wiki directory has no Markdown pages: {wiki_dir}"]

    for required_page in REQUIRED_PAGES:
        if required_page not in pages:
            failures.append(f"missing required wiki page: {required_page}")

    known_pages = set(pages)
    linked_from_navigation: set[str] = set(REQUIRED_PAGES)
    for navigation_page in REQUIRED_PAGES:
        text = pages.get(navigation_page)
        if text:
            linked_from_navigation.update(_page_links(text))

    for page_name, text in pages.items():
        first_line = _first_nonblank_line(text)
        if not first_line.startswith("# "):
            failures.append(f"{page_name}: first nonblank line should be an H1 page title")

        h1_count = sum(1 for line in text.splitlines() if line.startswith("# "))
        if h1_count != 1:
            failures.append(f"{page_name}: expected exactly one H1, found {h1_count}")

        bare_urls = BARE_URL_PATTERN.findall(text)
        if bare_urls:
            failures.append(f"{page_name}: contains bare URL; use a named Markdown link")

        scratch_terms = sorted({match.group(0) for match in SCRATCH_PATTERN.finditer(text)})
        if scratch_terms:
            failures.append(
                f"{page_name}: contains scratch-note terms: {', '.join(scratch_terms)}"
            )

        for target in _page_links(text):
            if not _target_exists(target, wiki_dir=wiki_dir, repo_root=repo_root, known_pages=known_pages):
                failures.append(f"{page_name}: broken local or repo-relative link: {target}")

    for page_name in sorted(known_pages - set(REQUIRED_PAGES)):
        if page_name not in {Path(link).name for link in linked_from_navigation}:
            failures.append(
                f"{page_name}: page is not reachable from Home.md or _Sidebar.md"
            )

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit a repo-local Lotus wiki source for navigation and publication quality."
    )
    parser.add_argument(
        "--wiki-dir",
        type=Path,
        default=Path("wiki"),
        help="Path to the repo-local wiki source directory. Defaults to ./wiki.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root used to validate repo-relative evidence links. Defaults to the wiki parent.",
    )
    args = parser.parse_args()

    wiki_dir = args.wiki_dir.resolve()
    repo_root = args.repo_root.resolve() if args.repo_root else wiki_dir.parent
    failures = audit_wiki(wiki_dir, repo_root)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print(f"OK: wiki quality audit passed for {args.wiki_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
