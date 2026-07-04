---
name: gh-issue-fix-qa-loop
description: GitHub issue-to-resolution execution loop for engineering and QA handoff. Use when the user asks to take open issues, implement fixes, raise and merge PRs, update issue progress, request QA validation, and continue fix/retest cycles until issues are verified and closed.
---

# GH Issue Fix QA Loop

Run a strict loop for each issue: `analyze -> fix -> PR -> merge -> QA retest -> close or reopen`.

Use this skill with `gh` CLI and repository-local tests. For Lotus services, call the platform QA validator after merge.

## Preconditions

- Verify GitHub auth:
```powershell
gh auth status
```
- Ensure clean branch strategy per issue:
  - `fix/issue-<number>-<slug>`
- Ensure QA command is known:
  - Lotus services: `run-lotus-qa.ps1 -Repo <service> -BringUp -CreateIssues`

## Workflow

1. Select issue queue:
```powershell
gh issue list --repo <owner/repo> --state open --limit 50
```

2. Start issue cycle:
- create fix branch
- reproduce issue
- implement fix
- run unit/integration tests

3. Raise PR linked to issue:
```powershell
gh pr create --repo <owner/repo> --fill
```
- ensure PR body includes `Fixes #<issue>`

4. Merge PR after checks:
```powershell
gh pr merge <number> --repo <owner/repo> --merge --delete-branch
```
Use the repository's approved merge strategy. For Lotus work, do not squash unless the user or repository policy explicitly requests it.

5. Update issue and request QA:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\update-issue-loop.ps1 -Repo <owner/repo> -IssueNumber <n> -Status merged_pending_qa -PrNumber <pr> -QaCommand "<qa command>"
```

6. Run QA and decide:
- If QA passes:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\update-issue-loop.ps1 -Repo <owner/repo> -IssueNumber <n> -Status qa_passed_closed -QaRunRef "<artifact-or-run-id>"
```
- If QA fails:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\update-issue-loop.ps1 -Repo <owner/repo> -IssueNumber <n> -Status qa_failed -QaRunRef "<artifact-or-run-id>" -Summary "<failure summary>"
```
- Then restart cycle from step 2 on a new fix branch.

7. Continue until issue is closed with QA evidence.

## Operating Rules

- Do not close issues without QA evidence.
- Do not merge PRs with failing required checks.
- Always post expected vs actual in QA-failed updates.
- Avoid duplicate QA issues/comments by using the same issue thread for iterations.
- Keep loop state visible via labels and structured comments.

Use [state-machine](references/state-machine.md) and [comment-templates](references/comment-templates.md) when updating issue status.
## Continuous Skill Improvement

At the end of any meaningful use of this skill, decide whether the work exposed a repeatable failure
mode, missing step, weak trigger, validation gap, or context-routing gap. If yes, update the
platform-owned skill source under `lotus-platform/codex/skills/<skill-name>` or its relevant
reference/script in the same delivery slice when the improvement is small and safe. For broader
learning, create a focused follow-up issue or PR instead of relying on chat memory.

Use this decision order:

1. tighten this skill when future agents need different behavior;
2. update `context/LOTUS-SKILL-ROUTING-MAP.md` when routing or overlap changed;
3. update central or repo-local context when source-of-truth changed;
4. add or adjust validators, scaffolds, or gates when deterministic enforcement is better than prose;
5. record an explicit no-change decision in PR evidence, the review ledger, or the task ledger when no durable update is justified.


