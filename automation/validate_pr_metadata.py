"""Conservative candidate policy and separate, current GitHub closure evidence.

No candidate-text inference is presented as GitHub's closing-reference truth.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
KEYWORD = re.compile(r"\b(?:close[sd]?|fix(?:es|ed)?|resolve[sd]?)\b", re.I)
REFERENCE = re.compile(
    r"https://github\.com/([\w.-]+/[\w.-]+)/issues/([1-9]\d*)\b"
    r"|(?<![\w/])(?:([\w.-]+/[\w.-]+))?#([1-9]\d*)\b"
)
DECLARATION = re.compile(r"^Intended closures: (.+)$", re.M)
QUERY = """query($owner:String!,$name:String!,$number:Int!,$cursor:String) {
  repository(owner:$owner,name:$name) { pullRequest(number:$number) {
    number title body headRefOid baseRefName state updatedAt url
    closingIssuesReferences(first:100,after:$cursor) {
      totalCount nodes { number repository { nameWithOwner } }
      pageInfo { hasNextPage endCursor }
    }
  } }
}"""


class MetadataError(ValueError):
    """Required policy or authoritative evidence is absent or contradictory."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise MetadataError(message)


def supported_repositories() -> set[str]:
    profiles = json.loads(
        (ROOT / "automation/repos.json").read_text(encoding="utf-8-sig")
    )
    return {profile["github"].lower() for profile in profiles}


def repository(value: str) -> str:
    require(
        isinstance(value, str) and value.lower() in supported_repositories(),
        "Unsupported repository profile",
    )
    return value.lower()


def reference(value: str, repo: str) -> str:
    match = REFERENCE.fullmatch(value)
    require(match is not None, "Malformed issue reference")
    assert match is not None
    target = repository(match[1] or match[3] or repo)
    return f"{target}#{match[2] or match[4]}"


def intended_set(body: str, repo: str) -> set[str]:
    declarations = DECLARATION.findall(body.replace("\r\n", "\n"))
    require(
        len(declarations) == 1, "Require exactly one Intended closures: declaration"
    )
    value = declarations[0]
    if value == "none":
        return set()
    items = value.split(", ")
    result = {reference(item, repo) for item in items}
    require(len(result) == len(items), "Duplicate intended closure")
    return result


def validate_candidate(title: str, body: str, repo: str) -> set[str]:
    repository(repo)
    require(
        isinstance(title, str)
        and bool(title.strip())
        and not any(c in title for c in "\r\n"),
        "Require a nonempty single-line title",
    )
    require(isinstance(body, str) and bool(body.strip()), "Require a nonempty body")
    intended = intended_set(body, repo)
    require(
        REFERENCE.search(title + "\n" + body) is not None, "Require an issue reference"
    )
    for match in REFERENCE.finditer(title + "\n" + body):
        reference(match[0], repo)
    # Deliberately accept only standalone, affirmative closure lines. This
    # avoids pretending that arbitrary prose, negation, code fences or quotes
    # can be interpreted with GitHub's semantics offline.
    declared: set[str] = set()
    in_fence = False
    for line in (title + "\n" + body).splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
        if KEYWORD.search(line) and (
            REFERENCE.search(line) or "#" in line or "github.com/" in line.lower()
        ):
            closing = re.fullmatch(r"(?:Closes|Fixes|Resolves) (\S+)", line)
            require(
                not in_fence and closing is not None and line != title,
                "Ambiguous closing wording; use neutral Related issue/Remaining acceptance text",
            )
            assert closing is not None
            declared.add(reference(closing[1], repo))
    require(
        declared == intended, "Closing lines differ from explicit intended closure set"
    )
    return intended


def github_page(repo: str, number: int, cursor: str | None) -> dict:
    owner, name = repo.split("/")
    args = [
        "gh",
        "api",
        "graphql",
        "-f",
        f"query={QUERY}",
        "-f",
        f"owner={owner}",
        "-f",
        f"name={name}",
        "-F",
        f"number={number}",
    ]
    if cursor is not None:
        args += ["-f", f"cursor={cursor}"]
    result = subprocess.run(
        args, capture_output=True, text=True, encoding="utf-8", timeout=60
    )
    require(
        result.returncode == 0, "GitHub GraphQL request failed (details suppressed)"
    )
    try:
        payload = json.loads(result.stdout)
        require(isinstance(payload, dict), "Malformed GraphQL envelope")
        require(not payload.get("errors"), "GraphQL returned errors")
        pr = payload["data"]["repository"]["pullRequest"]
        require(isinstance(pr, dict), "Missing pull request evidence")
        return pr
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise MetadataError("Malformed GraphQL evidence") from exc


def identity(pr: dict) -> tuple:
    require(isinstance(pr, dict), "Malformed PR evidence")
    fields = (
        "number",
        "title",
        "body",
        "headRefOid",
        "baseRefName",
        "state",
        "updatedAt",
        "url",
    )
    require(
        all(field in pr for field in fields), "Incomplete current metadata identity"
    )
    require(type(pr["number"]) is int and pr["number"] > 0, "Invalid PR number")
    require(
        all(isinstance(pr[field], str) and pr[field] for field in fields[1:]),
        "Invalid metadata identity",
    )
    require(
        re.fullmatch(r"[0-9a-f]{40}", pr["headRefOid"]) is not None, "Invalid head SHA"
    )
    return tuple(pr[field] for field in fields)


def collect_current(
    repo: str, number: int, expected_head: str, fetch=github_page
) -> tuple[dict, set[str]]:
    repository(repo)
    require(
        re.fullmatch(r"[0-9a-f]{40}", expected_head) is not None,
        "Require exact expected head SHA",
    )
    cursor = None
    seen_cursors: set[str] = set()
    actual: set[str] = set()
    first = None
    total = None
    while True:
        pr = fetch(repo, number, cursor)
        current_identity = identity(pr)
        if first is None:
            first = pr
        require(
            current_identity == identity(first), "PR metadata changed during pagination"
        )
        require(
            pr["number"] == number and pr["headRefOid"] == expected_head,
            "Current PR identity differs from requested number/head",
        )
        require(
            pr["url"] == f"https://github.com/{repo}/pull/{number}",
            "Wrong PR repository",
        )
        require(
            pr["state"] == "OPEN" and pr["baseRefName"] == "main",
            "Require an open main-targeting PR",
        )
        connection = pr.get("closingIssuesReferences")
        require(isinstance(connection, dict), "Missing closing-reference capability")
        count = connection.get("totalCount")
        require(type(count) is int and count >= 0, "Missing closing-reference count")
        if total is None:
            total = count
        require(total == count, "Closing-reference count changed")
        nodes, page = connection.get("nodes"), connection.get("pageInfo")
        require(
            isinstance(nodes, list) and isinstance(page, dict),
            "Incomplete closing-reference page",
        )
        require(
            type(page.get("hasNextPage")) is bool and "endCursor" in page,
            "Incomplete pagination evidence",
        )
        for node in nodes:
            try:
                target, issue = node["repository"]["nameWithOwner"], node["number"]
                require(
                    type(issue) is int and issue > 0, "Invalid closing issue number"
                )
                item = reference(f"{target}#{issue}", repo)
            except (KeyError, TypeError) as exc:
                raise MetadataError("Malformed closing-reference node") from exc
            require(item not in actual, "Duplicate closing-reference evidence")
            actual.add(item)
        require(len(actual) <= total, "Closing-reference count exceeded")
        if not page["hasNextPage"]:
            require(len(actual) == total, "Truncated closing-reference evidence")
            break
        next_cursor = page["endCursor"]
        require(
            isinstance(next_cursor, str)
            and bool(next_cursor)
            and next_cursor not in seen_cursors
            and bool(nodes),
            "Pagination made no progress",
        )
        seen_cursors.add(next_cursor)
        cursor = next_cursor
    # A fresh read prevents pagination from certifying an earlier body/head.
    final = fetch(repo, number, None)
    require(identity(final) == identity(first), "PR changed after collection")
    require(
        final.get("closingIssuesReferences") == first.get("closingIssuesReferences"),
        "Closing references changed after collection",
    )
    return first, actual


def validate_live(
    repo: str, number: int, expected_head: str, fetch=github_page
) -> dict:
    pr, actual = collect_current(repo, number, expected_head, fetch)
    intended = validate_candidate(pr["title"], pr["body"], repo)
    require(
        actual == intended,
        "Actual GraphQL closing references differ from intended closures",
    )
    return {
        "mode": "live",
        "repository": repo,
        "pr": number,
        "head": expected_head,
        "updated_at": pr["updatedAt"],
        "body_sha256": hashlib.sha256(pr["body"].encode()).hexdigest(),
        "closing_references": sorted(actual),
        "complete": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    modes = parser.add_subparsers(dest="mode", required=True)
    candidate = modes.add_parser("candidate")
    candidate.add_argument("--title-env", required=True)
    candidate.add_argument("--body-file", type=Path, required=True)
    live = modes.add_parser("live")
    live.add_argument("--pr", type=int, required=True)
    live.add_argument("--expected-head", required=True)
    args = parser.parse_args()
    try:
        repo = repository(args.repo)
        if args.mode == "candidate":
            intended = validate_candidate(
                os.environ.get(args.title_env, ""),
                args.body_file.read_text(encoding="utf-8-sig"),
                repo,
            )
            evidence = {
                "mode": "candidate",
                "intended_closures": sorted(intended),
                "github_evidence": False,
            }
        else:
            evidence = validate_live(repo, args.pr, args.expected_head)
        print(json.dumps(evidence, sort_keys=True))
        return 0
    except MetadataError as exc:
        print(f"PR metadata rejected: {exc}")
        return 1
    except (OSError, ValueError, subprocess.SubprocessError):
        # No raw subprocess output, PR body or environment values are printed.
        print(
            "PR metadata rejected: required policy or complete current GitHub evidence failed"
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
