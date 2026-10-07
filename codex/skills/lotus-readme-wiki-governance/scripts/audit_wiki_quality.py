from __future__ import annotations

import argparse
import re
import subprocess
import sys
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from string import punctuation
from urllib.parse import unquote, urlparse


LINK_START_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(")
REFERENCE_DEFINITION_PATTERN = re.compile(
    r"^[ \t]{0,3}\[(?!\^)([^\]]+)\]:[ \t]*(.+?)\s*$", re.MULTILINE
)
REFERENCE_USE_PATTERN = re.compile(r"(?<!!)\[([^\]]+)\]\[([^\]]*)\]")
SHORTCUT_REFERENCE_PATTERN = re.compile(r"(?<!!)\[([^\]]+)\](?![\[\(])")
BARE_URL_PATTERN = re.compile(r"(?<!\]\()https?://\S+")
SCRATCH_PATTERN = re.compile(
    r"\b(TODO|maybe|rough|temp|temporary|TBD|FIXME)\b", re.IGNORECASE
)
DATABASE_TEMPORARY_PATTERN = re.compile(
    r"temporary[ \t]+(?:relations?|tables?)\b"
    r"(?![ \t]+(?:workaround|notes)\b)", re.IGNORECASE
)
DIRECTORY_TEMPORARY_PATTERN = re.compile(
    r"temporary[ \t]+director(?:y|ies)\b",
    re.IGNORECASE,
)
DIRECTORY_SCRATCH_QUALIFIER_PATTERN = re.compile(
    r"(?:[^\w\r\n]|_)*(?:workaround|notes)(?=\b|_+(?!\w))", re.IGNORECASE
)
INLINE_CODE_SPAN_PATTERN = re.compile(r"(?<!`)(`+)(?!`)(.*?)(?<!`)\1(?!`)")
DIRECTORY_REFERENCE_LABEL_PATTERN = re.compile(r"\[((?:\\[^\r\n]|[^\[\]\\\r\n]){0,999})\]")
DIRECTORY_REFERENCE_DEFINITION_PATTERN = re.compile(
    r"^[ \t]{0,3}\[((?:\\[^\r\n]|[^\[\]\\\r\n]){1,999})\]:[ \t]*(.+)$"
)
HTML_LINE_BREAK_TAGS = frozenset({
    # WHATWG default flow/list/text-bearing table layout plus br. This local
    # lexical set excludes CSS, sanitization, visibility and HTML5 tree repair.
    "address", "article", "aside", "blockquote", "body", "br", "caption",
    "center", "dd", "details", "dialog", "dir", "div", "dl", "dt", "fieldset",
    "figcaption", "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5",
    "h6", "header", "hgroup", "hr", "html", "legend", "li", "listing", "main",
    "menu", "nav", "ol", "p", "plaintext", "pre", "search", "section", "summary",
    "table", "tbody", "td", "tfoot", "th", "thead", "tr", "ul", "xmp",
})


class _DirectoryQualifierParser(HTMLParser):
    """Extract local qualifier text; this is not a general Markdown renderer."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in HTML_LINE_BREAK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        self.handle_starttag(tag, [])

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _directory_qualifier_text(raw_line: str) -> str:
    # Code-span contents and backslash-escaped angles are literal Markdown text.
    protected = INLINE_CODE_SPAN_PATTERN.sub(
        lambda match: match[1] + escape(match[2], quote=False) + match[1], raw_line
    )
    protected = re.sub(
        r"(\\+)<",
        lambda match: match[1][:-1] + "&lt;" if len(match[1]) % 2 else match[0],
        protected,
    )
    parser = _DirectoryQualifierParser()
    parser.feed(protected)
    parser.close()
    return "".join(parser.parts)


def _directory_link_title_end(line: str, start: int) -> int | None:
    if start >= len(line) or line[start] not in "\"'(":
        return None
    closing = ")" if line[start] == "(" else line[start]
    index = start + 1
    while index < len(line):
        if line[index] == "\\" and index + 1 < len(line) and line[index + 1] in punctuation:
            index += 2
            continue
        if line[index] == closing:
            return index + 1
        if closing == ")" and line[index] == "(":
            return None
        index += 1
    return None


def _directory_inline_link_end(line: str, start: int) -> int | None:
    """Read complete same-line destination/title metadata, without rendering it."""
    index = start + 1
    while index < len(line) and line[index] in " \t":
        index += 1
    if index == len(line):
        return None
    if line[index] == ")":
        return index + 1
    title_end = _directory_link_title_end(line, index)
    if title_end is not None:
        tail = title_end
        while tail < len(line) and line[tail] in " \t":
            tail += 1
        if tail < len(line) and line[tail] == ")":
            return tail + 1
    angle = line[index] == "<"
    if angle:
        index += 1
    depth = 0
    while index < len(line):
        character = line[index]
        if character == "\\" and index + 1 < len(line) and line[index + 1] in punctuation:
            index += 2
            continue
        if angle:
            if character == "<":
                return None
            if character == ">":
                index += 1
                break
        elif character in " \t":
            break
        elif ord(character) < 32 or ord(character) == 127:
            return None
        elif character == "(":
            depth += 1
        elif character == ")":
            if depth == 0:
                return index + 1
            depth -= 1
        index += 1
    else:
        return None
    if depth:
        return None
    separated = index < len(line) and line[index] in " \t"
    while index < len(line) and line[index] in " \t":
        index += 1
    if index < len(line) and line[index] == ")":
        return index + 1
    if not separated:
        return None
    title_end = _directory_link_title_end(line, index)
    if title_end is None:
        return None
    while title_end < len(line) and line[title_end] in " \t":
        title_end += 1
    return title_end + 1 if title_end < len(line) and line[title_end] == ")" else None


def _directory_reference_labels(prose: str) -> set[str]:
    labels: set[str] = set()
    definition_block = True
    for line in prose.splitlines():
        if not line.strip():
            definition_block = True
            continue
        definition = DIRECTORY_REFERENCE_DEFINITION_PATTERN.fullmatch(line) if definition_block else None
        if definition is None:
            definition_block = False
            continue
        target = f"({definition[2]})"
        label = " ".join(definition[1].casefold().split())
        if label and _directory_inline_link_end(target, 0) == len(target):
            labels.add(label)
        else:
            definition_block = False
    return labels


def _directory_link_metadata_end(
    line: str, closing: int, label: str, references: set[str],
) -> int | None:
    suffix = closing + 1
    if line[suffix:suffix + 1] == "(":
        inline_end = _directory_inline_link_end(line, suffix)
        if inline_end is not None:
            return inline_end
    if line[suffix:suffix + 1] == "[":
        reference = DIRECTORY_REFERENCE_LABEL_PATTERN.match(line, suffix)
        if reference is None:
            return None
        label = reference[1] or label
        suffix = reference.end()
    normalized = " ".join(label.casefold().split())
    return suffix if normalized in references else None


def _directory_label_is_image(line: str, opening: int) -> bool:
    if opening == 0 or line[opening - 1] != "!":
        return False
    index = opening - 2
    while index >= 0 and line[index] == "\\":
        index -= 1
    return (opening - 2 - index) % 2 == 0


def _directory_noun_link_tail(
    line: str, noun_start: int, noun_end: int, references: set[str],
) -> str:
    """Elide only recognized metadata around this noun; preserve visible label text."""
    code_spans = {match.start(): match.end() for match in INLINE_CODE_SPAN_PATTERN.finditer(line)}
    stack: list[int] = []
    pairs: list[tuple[int, int]] = []
    index = 0
    while index < len(line):
        if index in code_spans:
            if index <= noun_start < code_spans[index]:
                return line[noun_end:]
            index = code_spans[index]
            continue
        if line[index] == "\\" and index + 1 < len(line) and line[index + 1] in punctuation:
            index += 2
            continue
        if line[index] == "[":
            stack.append(index)
        elif line[index] == "]" and stack:
            pairs.append((stack.pop(), index))
        index += 1
    for opening, closing in pairs:
        if not opening < noun_start < noun_end <= closing or _directory_label_is_image(line, opening):
            continue
        label = line[opening + 1:closing]
        metadata_end = _directory_link_metadata_end(line, closing, label, references)
        if metadata_end is None:
            continue
        nested_link = any(
            opening < nested_open < nested_close < closing
            and not _directory_label_is_image(line, nested_open)
            and _directory_link_metadata_end(
                line, nested_close, line[nested_open + 1:nested_close], references
            ) is not None
            for nested_open, nested_close in pairs
        )
        if not nested_link:
            return line[noun_end:closing] + line[metadata_end:]
    return line[noun_end:]


def _directory_term_is_technical(prose: str, start: int, references: set[str]) -> bool:
    noun = DIRECTORY_TEMPORARY_PATTERN.match(prose, start)
    if noun is None:
        return False
    line_start = max(prose.rfind("\n", 0, start), prose.rfind("\r", 0, start)) + 1
    line = prose[line_start:].partition("\n")[0].partition("\r")[0]
    raw_line = _directory_noun_link_tail(line, start - line_start, noun.end() - line_start, references)
    return DIRECTORY_SCRATCH_QUALIFIER_PATTERN.match(_directory_qualifier_text(raw_line)) is None

# Evidence routes are syntax-checked citations, not checkout file paths.
GITHUB_EVIDENCE_ROUTE_PATTERN = re.compile(
    r"(?:actions/runs/[1-9][0-9]*(?:/job/[1-9][0-9]*)?"
    r"|actions/workflows/[A-Za-z0-9_-][A-Za-z0-9_.-]*\.ya?ml"
    r"|issues/[1-9][0-9]*"
    r"|pull/[1-9][0-9]*(?:/(?:files|commits|checks))?"
    r"|commit/[0-9a-fA-F]{7,40}"
    r"|releases(?:/latest|/tag/[A-Za-z0-9_-][A-Za-z0-9_.-]*)?"
    r"|compare/[A-Za-z0-9_-][A-Za-z0-9_./~-]*\.\.\.[A-Za-z0-9_-][A-Za-z0-9_./~-]*)"
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


def _has_balanced_destination_parentheses(destination: str) -> bool:
    depth = 0
    escaped = False
    for character in destination:
        if escaped:
            escaped = False
            continue
        if character == "\\":
            escaped = True
        elif character == "(":
            depth += 1
        elif character == ")":
            if depth == 0:
                return False
            depth -= 1
    return depth == 0


def _valid_reference_definition(raw_target: str) -> bool:
    target = raw_target.strip()
    if not target:
        return False
    if target.startswith("<"):
        closing_angle = target.find(">")
        if closing_angle == -1:
            return False
        remainder = target[closing_angle + 1 :].strip()
    else:
        parts = target.split(maxsplit=1)
        if not _has_balanced_destination_parentheses(parts[0]):
            return False
        remainder = parts[1].strip() if len(parts) == 2 else ""
    if not remainder:
        return True
    return (
        len(remainder) >= 2
        and (remainder[0], remainder[-1]) in {("\"", "\""), ("'", "'"), ("(", ")")}
    )


def _markdown_link_targets(text: str) -> list[str]:
    definitions: dict[str, str] = {}
    for match in REFERENCE_DEFINITION_PATTERN.finditer(text):
        if not _valid_reference_definition(match.group(2)):
            continue
        label = " ".join(match.group(1).lower().split())
        definitions.setdefault(label, match.group(2))
    used_references = {
        " ".join((match.group(2) or match.group(1)).lower().split())
        for match in REFERENCE_USE_PATTERN.finditer(text)
    }
    prose_without_definitions = REFERENCE_DEFINITION_PATTERN.sub(
        lambda match: "" if _valid_reference_definition(match.group(2)) else match.group(0),
        text,
    )
    used_references.update(
        " ".join(match.group(1).lower().split())
        for match in SHORTCUT_REFERENCE_PATTERN.finditer(prose_without_definitions)
    )
    targets = [
        definitions[label] for label in used_references if label in definitions
    ]
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


def _publication_unsafe_root_links(text: str) -> set[str]:
    links: set[str] = set()
    for raw_target in _markdown_link_targets(text):
        target = _markdown_link_destination(raw_target).split("#", 1)[0].strip()
        if target.startswith(ALLOWED_EXTERNAL_PREFIXES):
            continue
        decoded_target = unquote(target).replace("\\", "/")
        if decoded_target.startswith("/"):
            links.add(decoded_target)
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
        normalized_target = _normalize_link_target(raw_target)
        if normalized_target and (resolved_wiki / normalized_target).is_file():
            continue
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

        parts = parsed.path.strip("/").split("/", 2)
        if len(parts) < 2:
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
        route = unquote(parts[2]) if len(parts) == 3 else ""
        if GITHUB_EVIDENCE_ROUTE_PATTERN.fullmatch(route) and all(
            part not in {".", ".."} for part in route.split("/")
        ):
            continue
        file_parts = route.split("/", 2)
        mode = file_parts[0]
        if mode not in {"blob", "tree"}:
            failures.append(
                f"{page_name}: repository GitHub file link must use blob or tree: {target}"
            )
            continue
        if len(file_parts) != 3 or not file_parts[2]:
            failures.append(f"{page_name}: malformed repository GitHub file link: {target}")
            continue
        if file_parts[1] != "main":
            failures.append(
                f"{page_name}: repository GitHub link must target main: {target}"
            )
            continue

        relative_path = file_parts[2].replace("\\", "/")
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
    directory_references = _directory_reference_labels(prose)
    if BARE_URL_PATTERN.findall(prose):
        failures.append(f"{page_name}: contains bare URL; use a named Markdown link")

    scratch_terms = sorted(
        {
            match.group(0) for match in SCRATCH_PATTERN.finditer(prose)
            if not (
                match.group(0).lower() == "temporary"
                and (
                    DATABASE_TEMPORARY_PATTERN.match(prose, match.start())
                    or _directory_term_is_technical(prose, match.start(), directory_references)
                )
            )
        }
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
    for target in sorted(_publication_unsafe_root_links(text)):
        failures.append(
            f"{page_name}: publication-unsafe root-relative link: {target}"
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
