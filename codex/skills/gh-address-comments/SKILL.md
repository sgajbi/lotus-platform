---
name: gh-address-comments
description: Use when helping address review or issue comments on the open GitHub PR for the current branch using the GitHub CLI; verify gh authentication, fetch conversation and review-thread context, classify comments, implement approved fixes, and report evidence without relying on local-only helper changes.
---

# PR Comment Handler

Guide to find the open PR for the current branch and address its comments with gh CLI.

Prereq: ensure `gh` is authenticated (for example, run `gh auth login` once), then run
`gh auth status` in the target repo. Required scopes usually include `repo` and `workflow`.

## 1) Inspect comments needing attention
- Run scripts/fetch_comments.py which will print out all the comments and review threads on the PR

## 2) Ask the user for clarification
- Number all the review threads and comments and provide a short summary of what would be required to apply a fix for it
- Ask the user which numbered comments should be addressed

## Continuous Skill Improvement

When review-comment handling exposes a repeated helper failure, missing review-thread field,
platform-specific encoding issue, unsafe state mutation, or weak evidence pattern, update the
platform-owned skill source under `lotus-platform/codex/skills/gh-address-comments` and its tests.
Do not leave fixes only in the local Codex profile. Keep subprocess and JSON decoding explicit
UTF-8 with replacement so Windows console code pages cannot crash review-thread inspection before
the actionable comment evidence is reported.

At the end of any meaningful use of this skill, decide whether the work exposed a repeatable failure
mode, missing step, weak trigger, validation gap, or context-routing gap. If yes, update the
platform-owned skill source or its relevant reference/script in the same delivery slice when the
improvement is small and safe; for broader learning, create a focused follow-up issue or PR instead
of relying on chat memory.

## 3) If user chooses comments
- Apply fixes for the selected comments

Notes:
- If gh hits auth/rate issues mid-run, prompt the user to re-authenticate with `gh auth login`, then retry.
