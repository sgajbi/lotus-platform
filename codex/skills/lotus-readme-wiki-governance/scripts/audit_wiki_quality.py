from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


LINK_START_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(")
REFERENCE_DEFINITION_PATTERN = re.compile(
    r"^[ \t]{0,3}\[(?!\^)[^\]]+\]:[ \t]*(.+?)\s*$", re.MULTILINE
)
BARE_URL_PATTERN = re.compile(r"(?<!\]\()https?://\S+")
SCRATCH_PATTERN = re.compile(
    r"\b(TODO|maybe|rough|temp|temporary|TBD|FIXME)\b", re.IGNORECASE
)

ALLOWED_EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "#")
REQUIRED_PAGES = ("Home.md", "_Sidebar.md")
LONG_PAGE_LINE_THRESHOLD = 80
FIRST_SCREEN_LINE_LIMIT = 60
INTRO_NONBLANK_LINE_LIMIT = 8
INTRO_CHARACTER_LIMIT = 900
COMMAND_BLOCK_LINE_LIMIT = 25
COMMAND_BLOCK_COMMAND_LIMIT = 15
GITHUB_ORIGIN_PATTERN = re.compile(
    r"^(?:https://github\.com/|git@github\.com:)(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$",
    re.IGNORECASE,
)

CURRENT_SCOPE_PATTERN = re.compile(
    r"\b(current[- ]state|current scope|current posture|current summary|"
    r"current support|support posture|implementation[- ]backed|implemented|"
    r"current maturity|evidence posture)\b",
    re.IGNORECASE,
)
FIRST_SCREEN_STRUCTURE_HEADING_PATTERN = re.compile(
    r"^##\s+("
    r"Audience Paths|Reader Map|How To Read This Page|Quick Decision Map|"
    r"Decision Matrix|First Response Matrix|Current Support Summary|"
    r"Demo Decision Matrix|Integration Reader Map|RFC Reader Map|"
    r"Evidence Standard|Operator Evidence Map|Governance Map|Route Families|"
    r"Start Here|Capability Map|Support Summary|Quality Signal Map"
    r")\s*$",
    re.IGNORECASE,
)
COMMAND_LINE_PATTERN = re.compile(
    r"^(make|npm|pnpm|yarn|python|pytest|powershell|pwsh|gh|git|docker|"
    r"docker-compose|curl|uvicorn|pip|\.\\|\.\/)\b",
    re.IGNORECASE,
)


def _markdown_link_destination(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<"):
        closing_angle = target.find(">")
        if closing_angle != -1:
            return target[1:closing_angle].strip()
    return target.split(maxsplit=1)[0] if target else ""


def _markdown_link_targets(text: str) -> list[str]:
    targets = [match.group(1) for match in REFERENCE_DEFINITION_PATTERN.finditer(text)]
    for match in LINK_START_PATTERN.finditer(text):
        start = match.end()
        depth = 0
        escaped = False
        in_angle_destination = text[start : start + 1] == "<"
        for index in range(start, len(text)):
            character = text[index]
            if escaped:
                escaped = False
                continue
            if character == "\\":
                escaped = True
                continue
            if in_angle_destination:
                if character == ">":
                    in_angle_destination = False
                continue
            if character == "(":
                depth += 1
            elif character == ")":
                if depth == 0:
                    targets.append(text[start:index])
                    break
                depth -= 1
    return targets


def _normalize_link_target(raw_target: str) -> str | None:
    target = _markdown_link_destination(raw_target).split("#", 1)[0].strip()
    if not target or target.startswith(ALLOWED_EXTERNAL_PREFIXES):
        return None
    target = unquote(target).replace("\\", "/")
    if not target.endswith("/") and not Path(target).suffix:
        target = f"{target}.md"
    return target.lstrip("./")


def _page_links(text: str) -> set[str]:
    links: set[str] = set()
    for raw_target in _markdown_link_targets(text):
        target = _normalize_link_target(raw_target)
        if target:
            links.add(target)
    return links


def _publication_unsafe_parent_links(text: str) -> set[str]:
    links: set[str] = set()
    for raw_target in _markdown_link_targets(text):
        target = _markdown_link_destination(raw_target).split("#", 1)[0].strip()
        if target.startswith(ALLOWED_EXTERNAL_PREFIXES):
            continue
        target = unquote(target).replace("\\", "/")
        if ".." in Path(target).parts:
            links.add(target)
    return links


def _publication_unsafe_repository_links(
    text: str, *, wiki_dir: Path, repo_root: Path
) -> set[str]:
    links: set[str] = set()
    resolved_wiki = wiki_dir.resolve()
    resolved_repo = repo_root.resolve()
    for raw_target in _markdown_link_targets(text):
        target = _markdown_link_destination(raw_target).split("#", 1)[0].strip()
        if not target or target.startswith(ALLOWED_EXTERNAL_PREFIXES):
            continue
        decoded_target = unquote(target).replace("\\", "/")
        target_path = Path(decoded_target)
        if target_path.is_absolute() or ".." in target_path.parts:
            continue
        wiki_target = (resolved_wiki / target_path).resolve()
        repo_target = (resolved_repo / target_path).resolve()
        if (
            repo_target.exists()
            and repo_target.is_relative_to(resolved_repo)
            and not repo_target.is_relative_to(resolved_wiki)
            and not wiki_target.exists()
        ):
            links.add(decoded_target)
    return links


def _github_repository_identity(repo_root: Path) -> tuple[str, str] | None:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "remote", "get-url", "origin"],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        return None
    match = GITHUB_ORIGIN_PATTERN.fullmatch(result.stdout.strip())
    if not match:
        return None
    return match.group("owner").lower(), match.group("repo").lower()


def _repository_github_link_failures(
    page_name: str, text: str, *, repo_root: Path
) -> list[str]:
    failures: list[str] = []
    repository_identity = _github_repository_identity(repo_root)
    for raw_target in _markdown_link_targets(text):
        target = _markdown_link_destination(raw_target)
        parsed = urlparse(target)
        if parsed.netloc.lower() != "github.com":
            continue

        parts = parsed.path.strip("/").split("/", 4)
        if len(parts) != 5:
            continue
        expected_repository = (
            repository_identity[1] if repository_identity else repo_root.name.lower()
        )
        if parts[1].lower() != expected_repository:
            continue
        link_identity = parts[0].lower(), parts[1].lower()
        if repository_identity is None:
            failures.append(
                f"{page_name}: cannot verify repository GitHub link without a GitHub origin: {target}"
            )
            continue
        if link_identity != repository_identity:
            expected_slug = "/".join(repository_identity)
            failures.append(
                f"{page_name}: repository GitHub link must target {expected_slug}: {target}"
            )
            continue
        mode = parts[2]
        if mode not in {"blob", "tree"}:
            failures.append(
                f"{page_name}: repository GitHub file link must use blob or tree: {target}"
            )
            continue
        if unquote(parts[3]) != "main":
            failures.append(
                f"{page_name}: repository GitHub link must target main: {target}"
            )
            continue

        relative_path = unquote(parts[4]).replace("\\", "/")
        relative_parts = Path(relative_path).parts
        if (
            Path(relative_path).is_absolute()
            or not relative_parts
            or any(part in {".", ".."} for part in relative_parts)
        ):
            failures.append(
                f"{page_name}: repository GitHub link escapes repository root: {target}"
            )
            continue
        local_path = (repo_root / relative_path).resolve()
        if not local_path.is_relative_to(repo_root.resolve()):
            failures.append(
                f"{page_name}: repository GitHub link escapes repository root: {target}"
            )
            continue
        expected_type_exists = (
            local_path.is_file() if mode == "blob" else local_path.is_dir()
        )
        if not expected_type_exists:
            failures.append(
                f"{page_name}: broken repository GitHub {mode} link: {relative_path}"
            )
    return failures


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


def _prose_without_fenced_code(text: str) -> str:
    prose_lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            prose_lines.append(line)
    return "\n".join(prose_lines)


def _has_markdown_table(lines: list[str]) -> bool:
    for index, line in enumerate(lines[:-1]):
        if "|" not in line:
            continue
        next_line = lines[index + 1].strip()
        if "|" in next_line and re.fullmatch(r"\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?", next_line):
            return True
    return False


def _has_first_screen_structure(lines: list[str]) -> bool:
    return _has_markdown_table(lines) or any(
        FIRST_SCREEN_STRUCTURE_HEADING_PATTERN.match(line.strip()) for line in lines
    )


def _intro_block_after_h1(lines: list[str]) -> list[str]:
    intro: list[str] = []
    seen_h1 = False
    for line in lines:
        stripped = line.strip()
        if not seen_h1:
            if stripped.startswith("# "):
                seen_h1 = True
            continue
        if stripped.startswith("## "):
            break
        if stripped:
            intro.append(stripped)
    return intro


def _first_screen_failures(page_name: str, text: str) -> list[str]:
    lines = text.splitlines()
    if len(lines) < LONG_PAGE_LINE_THRESHOLD:
        return []

    first_screen = lines[:FIRST_SCREEN_LINE_LIMIT]
    failures: list[str] = []
    if not CURRENT_SCOPE_PATTERN.search("\n".join(first_screen)):
        failures.append(
            f"{page_name}: long wiki page must state current scope or evidence posture near the top"
        )
    if not _has_first_screen_structure(first_screen):
        failures.append(
            f"{page_name}: long wiki page needs an early reader map, decision/evidence table, or equivalent first-screen structure"
        )

    intro = _intro_block_after_h1(lines)
    intro_text = " ".join(intro)
    if len(intro) > INTRO_NONBLANK_LINE_LIMIT or len(intro_text) > INTRO_CHARACTER_LIMIT:
        failures.append(
            f"{page_name}: opening section is too dense before the first H2; add current-state framing and reader structure"
        )
    return failures


def _command_dump_failures(page_name: str, text: str) -> list[str]:
    failures: list[str] = []
    in_fence = False
    block_lines: list[str] = []
    for line in [*text.splitlines(), "```"]:
        if line.strip().startswith("```"):
            if in_fence:
                nonblank = [block_line.strip() for block_line in block_lines if block_line.strip()]
                command_like_count = sum(
                    1 for block_line in nonblank if COMMAND_LINE_PATTERN.match(block_line)
                )
                if (
                    len(nonblank) > COMMAND_BLOCK_LINE_LIMIT
                    and command_like_count > COMMAND_BLOCK_COMMAND_LIMIT
                ):
                    failures.append(
                        f"{page_name}: command dump is too large; group commands by purpose and link to the authoritative Makefile or runbook"
                    )
                block_lines = []
                in_fence = False
            else:
                in_fence = True
            continue
        if in_fence:
            block_lines.append(line)
    return failures


def _target_exists(target: str, *, wiki_dir: Path, repo_root: Path, known_pages: set[str]) -> bool:
    target_name = Path(target).name
    if target_name in known_pages:
        return True
    return (repo_root / target).exists() or (wiki_dir / target).exists()


def _normalize_page_scope(raw_pages: list[str] | None) -> set[str]:
    if not raw_pages:
        return set()
    normalized: set[str] = set()
    for raw_page in raw_pages:
        page_name = Path(raw_page.replace("\\", "/")).name
        if not page_name.endswith(".md"):
            page_name = f"{page_name}.md"
        normalized.add(page_name)
    return normalized


def _wiki_directory_failures(wiki_dir: Path) -> list[str]:
    if not wiki_dir.exists():
        return [f"wiki directory does not exist: {wiki_dir}"]
    if not wiki_dir.is_dir():
        return [f"wiki path is not a directory: {wiki_dir}"]
    return []


def _required_page_failures(pages: dict[str, str]) -> list[str]:
    return [
        f"missing required wiki page: {required_page}"
        for required_page in REQUIRED_PAGES
        if required_page not in pages
    ]


def _navigation_links(pages: dict[str, str]) -> set[str]:
    linked_from_navigation: set[str] = set(REQUIRED_PAGES)
    for navigation_page in REQUIRED_PAGES:
        text = pages.get(navigation_page)
        if text:
            linked_from_navigation.update(_page_links(text))
    return linked_from_navigation


def _page_heading_failures(page_name: str, text: str) -> list[str]:
    failures: list[str] = []
    first_line = _first_nonblank_line(text)
    if not first_line.startswith("# "):
        failures.append(f"{page_name}: first nonblank line should be an H1 page title")

    h1_count = sum(1 for line in text.splitlines() if line.startswith("# "))
    if h1_count != 1:
        failures.append(f"{page_name}: expected exactly one H1, found {h1_count}")
    return failures


def _page_prose_failures(page_name: str, text: str) -> list[str]:
    failures: list[str] = []
    prose = _prose_without_fenced_code(text)
    if BARE_URL_PATTERN.findall(prose):
        failures.append(f"{page_name}: contains bare URL; use a named Markdown link")

    scratch_terms = sorted(
        {match.group(0) for match in SCRATCH_PATTERN.finditer(prose)}
    )
    if scratch_terms:
        failures.append(
            f"{page_name}: contains scratch-note terms: {', '.join(scratch_terms)}"
        )
    return failures


def _page_link_failures(
    page_name: str,
    text: str,
    *,
    wiki_dir: Path,
    repo_root: Path,
    known_pages: set[str],
) -> list[str]:
    failures: list[str] = []
    for target in sorted(_publication_unsafe_parent_links(text)):
        failures.append(
            f"{page_name}: publication-unsafe parent-relative link: {target}"
        )
    for target in sorted(
        _publication_unsafe_repository_links(
            text, wiki_dir=wiki_dir, repo_root=repo_root
        )
    ):
        failures.append(
            f"{page_name}: repository-relative link must use a main-anchored GitHub blob/tree URL: {target}"
        )
    failures.extend(
        _repository_github_link_failures(page_name, text, repo_root=repo_root)
    )
    for target in _page_links(text):
        if not _target_exists(
            target,
            wiki_dir=wiki_dir,
            repo_root=repo_root,
            known_pages=known_pages,
        ):
            failures.append(f"{page_name}: broken local or repo-relative link: {target}")
    return failures


def _page_quality_failures(
    page_name: str,
    text: str,
    *,
    wiki_dir: Path,
    repo_root: Path,
    known_pages: set[str],
    professional_scope: set[str],
) -> list[str]:
    failures = _page_heading_failures(page_name, text)
    failures.extend(_page_prose_failures(page_name, text))
    if page_name in professional_scope:
        failures.extend(_first_screen_failures(page_name, text))
        failures.extend(_command_dump_failures(page_name, text))
    failures.extend(
        _page_link_failures(
            page_name,
            text,
            wiki_dir=wiki_dir,
            repo_root=repo_root,
            known_pages=known_pages,
        )
    )
    return failures


def _navigation_reachability_failures(
    known_pages: set[str],
    linked_from_navigation: set[str],
) -> list[str]:
    reachable_pages = {Path(link).name for link in linked_from_navigation}
    return [
        f"{page_name}: page is not reachable from Home.md or _Sidebar.md"
        for page_name in sorted(known_pages - set(REQUIRED_PAGES))
        if page_name not in reachable_pages
    ]


def audit_wiki(
    wiki_dir: Path,
    repo_root: Path,
    *,
    professional_pages: set[str] | None = None,
) -> list[str]:
    directory_failures = _wiki_directory_failures(wiki_dir)
    if directory_failures:
        return directory_failures

    pages = _read_pages(wiki_dir)
    if not pages:
        return [f"wiki directory has no Markdown pages: {wiki_dir}"]

    known_pages = set(pages)
    professional_scope = professional_pages or set()
    failures = _required_page_failures(pages)
    linked_from_navigation = _navigation_links(pages)

    for page_name, text in pages.items():
        failures.extend(
            _page_quality_failures(
                page_name,
                text,
                wiki_dir=wiki_dir,
                repo_root=repo_root,
                known_pages=known_pages,
                professional_scope=professional_scope,
            )
        )
    failures.extend(_navigation_reachability_failures(known_pages, linked_from_navigation))

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
    parser.add_argument(
        "--changed-page",
        action="append",
        default=[],
        help=(
            "Wiki page to check with stricter first-screen and command-dump controls. "
            "Pass once per changed page. Existing navigation and link checks remain repo-wide."
        ),
    )
    parser.add_argument(
        "--all-professional-pages",
        action="store_true",
        help=(
            "Apply stricter first-screen and command-dump controls to every wiki page. "
            "Use this for full polish campaigns after legacy pages have been remediated."
        ),
    )
    args = parser.parse_args()

    wiki_dir = args.wiki_dir.resolve()
    repo_root = args.repo_root.resolve() if args.repo_root else wiki_dir.parent
    pages = _read_pages(wiki_dir) if wiki_dir.exists() and wiki_dir.is_dir() else {}
    professional_pages = (
        set(pages)
        if args.all_professional_pages
        else _normalize_page_scope(args.changed_page)
    )
    failures = audit_wiki(wiki_dir, repo_root, professional_pages=professional_pages)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print(f"OK: wiki quality audit passed for {args.wiki_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
