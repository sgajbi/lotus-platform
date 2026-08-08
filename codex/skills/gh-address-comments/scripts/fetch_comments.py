#!/usr/bin/env python3
"""
Fetch all PR conversation comments + reviews + review threads (inline threads)
for the PR associated with the current git branch, by shelling out to:

  gh api graphql

Requires:
  - `gh auth login` already set up
  - current branch has an associated (open) PR

Usage:
  python fetch_comments.py > pr_comments.json
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from typing import Any

QUERY = """\
query(
  $owner: String!,
  $repo: String!,
  $number: Int!,
  $commentsCursor: String,
  $reviewsCursor: String,
  $threadsCursor: String,
  $includeComments: Boolean!,
  $includeReviews: Boolean!,
  $includeThreads: Boolean!
) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      number
      url
      title
      state

      # Top-level "Conversation" comments (issue comments on the PR)
      comments(first: 100, after: $commentsCursor) @include(if: $includeComments) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          body
          createdAt
          updatedAt
          author { login }
        }
      }

      # Review submissions (Approve / Request changes / Comment), with body if present
      reviews(first: 100, after: $reviewsCursor) @include(if: $includeReviews) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          state
          body
          submittedAt
          author { login }
        }
      }

      # Inline review threads (grouped), includes resolved state
      reviewThreads(first: 100, after: $threadsCursor) @include(if: $includeThreads) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          isResolved
          isOutdated
          path
          line
          diffSide
          startLine
          startDiffSide
          originalLine
          originalStartLine
          resolvedBy { login }
          comments(first: 100) {
            nodes {
              id
              body
              createdAt
              updatedAt
              author { login }
            }
          }
        }
      }
    }
  }
}
"""


def _run(cmd: list[str], stdin: str | None = None) -> str:
    p = subprocess.run(
        cmd,
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if p.returncode != 0:
        stderr = p.stderr or ""
        stdout = p.stdout or ""
        diagnostic = stderr if stderr.strip() else stdout
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{diagnostic}")
    return p.stdout or ""


def _run_json(cmd: list[str], stdin: str | None = None) -> dict[str, Any]:
    out = _run(cmd, stdin=stdin)
    try:
        return json.loads(out)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse JSON from command output: {e}\nRaw:\n{out}") from e


def _ensure_gh_authenticated() -> None:
    try:
        _run(["gh", "auth", "status"])
    except RuntimeError:
        print("run `gh auth login` to authenticate the GitHub CLI", file=sys.stderr)
        raise RuntimeError("gh auth status failed; run `gh auth login` to authenticate the GitHub CLI") from None


def gh_pr_view_json(fields: str) -> dict[str, Any]:
    # fields is a comma-separated list like: "number,url"
    return _run_json(["gh", "pr", "view", "--json", fields])


def get_current_pr_ref() -> tuple[str, str, int]:
    """
    Resolve the PR for the current branch (whatever gh considers associated).
    Uses the PR URL/base repository identity so forked-head PRs fetch review
    threads from the repository that owns the pull request number.
    """
    pr = gh_pr_view_json("number,url")
    number = int(pr["number"])
    owner, repo, url_number = parse_pull_request_url(str(pr.get("url") or ""))
    if url_number is not None and url_number != number:
        raise RuntimeError(
            f"PR URL number {url_number} does not match gh PR number {number}: {pr.get('url')}"
        )
    return owner, repo, number


def parse_pull_request_url(url: str) -> tuple[str, str, int | None]:
    match = re.search(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)", url)
    if not match:
        raise RuntimeError(f"Unable to resolve base repository from PR URL: {url}")
    return match.group(1), match.group(2), int(match.group(3))


def gh_api_graphql(
    owner: str,
    repo: str,
    number: int,
    comments_cursor: str | None = None,
    reviews_cursor: str | None = None,
    threads_cursor: str | None = None,
    include_comments: bool = True,
    include_reviews: bool = True,
    include_threads: bool = True,
) -> dict[str, Any]:
    """
    Call `gh api graphql` using -F variables, avoiding JSON blobs with nulls.
    Query is passed via stdin using query=@- to avoid shell newline/quoting issues.
    """
    cmd = [
        "gh",
        "api",
        "graphql",
        "-F",
        "query=@-",
        "-F",
        f"owner={owner}",
        "-F",
        f"repo={repo}",
        "-F",
        f"number={number}",
        "-F",
        f"includeComments={str(include_comments).lower()}",
        "-F",
        f"includeReviews={str(include_reviews).lower()}",
        "-F",
        f"includeThreads={str(include_threads).lower()}",
    ]
    if comments_cursor:
        cmd += ["-F", f"commentsCursor={comments_cursor}"]
    if reviews_cursor:
        cmd += ["-F", f"reviewsCursor={reviews_cursor}"]
    if threads_cursor:
        cmd += ["-F", f"threadsCursor={threads_cursor}"]

    return _run_json(cmd, stdin=QUERY)


def fetch_all(owner: str, repo: str, number: int) -> dict[str, Any]:
    conversation_comments: list[dict[str, Any]] = []
    reviews: list[dict[str, Any]] = []
    review_threads: list[dict[str, Any]] = []

    comments_cursor: str | None = None
    reviews_cursor: str | None = None
    threads_cursor: str | None = None
    comments_done = False
    reviews_done = False
    threads_done = False

    pr_meta: dict[str, Any] | None = None

    while not (comments_done and reviews_done and threads_done):
        payload = gh_api_graphql(
            owner=owner,
            repo=repo,
            number=number,
            comments_cursor=comments_cursor,
            reviews_cursor=reviews_cursor,
            threads_cursor=threads_cursor,
            include_comments=not comments_done,
            include_reviews=not reviews_done,
            include_threads=not threads_done,
        )

        if "errors" in payload and payload["errors"]:
            raise RuntimeError(f"GitHub GraphQL errors:\n{json.dumps(payload['errors'], indent=2)}")

        pr = payload["data"]["repository"]["pullRequest"]
        if pr_meta is None:
            pr_meta = {
                "number": pr["number"],
                "url": pr["url"],
                "title": pr["title"],
                "state": pr["state"],
                "owner": owner,
                "repo": repo,
            }

        c = pr.get("comments") or {"nodes": [], "pageInfo": {"hasNextPage": False}}
        r = pr.get("reviews") or {"nodes": [], "pageInfo": {"hasNextPage": False}}
        t = pr.get("reviewThreads") or {"nodes": [], "pageInfo": {"hasNextPage": False}}

        if not comments_done:
            conversation_comments.extend(c.get("nodes") or [])
        if not reviews_done:
            reviews.extend(r.get("nodes") or [])
        if not threads_done:
            review_threads.extend(t.get("nodes") or [])

        if not comments_done:
            comments_done = not bool(c["pageInfo"]["hasNextPage"])
            comments_cursor = None if comments_done else c["pageInfo"]["endCursor"]
        if not reviews_done:
            reviews_done = not bool(r["pageInfo"]["hasNextPage"])
            reviews_cursor = None if reviews_done else r["pageInfo"]["endCursor"]
        if not threads_done:
            threads_done = not bool(t["pageInfo"]["hasNextPage"])
            threads_cursor = None if threads_done else t["pageInfo"]["endCursor"]

    assert pr_meta is not None
    return {
        "pull_request": pr_meta,
        "conversation_comments": conversation_comments,
        "reviews": reviews,
        "review_threads": review_threads,
    }


def main() -> None:
    _ensure_gh_authenticated()
    owner, repo, number = get_current_pr_ref()
    result = fetch_all(owner, repo, number)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
