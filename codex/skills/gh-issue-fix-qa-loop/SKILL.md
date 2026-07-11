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

## Issue Intake Gate

Before material implementation edits, every actionable defect, architecture gap, ownership move,
or deferred migration must link to a canonical GitHub issue:

1. Search open and closed issues using the failure pattern, root-cause terms, and concrete code,
   API, event, table, or contract symbols.
2. Reuse the issue that owns the root cause. Do not create one issue per commit or duplicate an
   umbrella issue for cleanup already inside its acceptance criteria.
3. If no issue owns the work, create one focused evidence-backed issue with impact, current
   evidence, expected owner, acceptance criteria, evaluation conditions, non-goals, and related
   work before starting material edits.
4. Apply `status/in-progress` when implementation begins, and keep subsequent status changes and
   validation evidence on that issue.
5. Keep speculative observations in the repository review ledger until they are actionable.

For urgent production containment, mitigate first only when waiting would increase harm. Capture
or link the canonical issue before considering the implementation slice complete. Issue creation is
traceability, not progress, and does not replace tests, documentation, or validation evidence.

## Workflow

1. Select issue queue:
```powershell
gh issue list --repo <owner/repo> --state open --limit 50
```

2. Start issue cycle:
- create fix branch
- apply `status/in-progress` to the issue or current issue cluster
- reproduce issue
- implement fix
- run unit/integration tests
- after the fix is committed and focused validation passes, replace `status/in-progress` with `status/fixed-local`

3. Raise PR linked to issue:
```powershell
gh pr create --repo <owner/repo> --fill
```
- ensure PR body includes `Fixes #<issue>`
- replace `status/fixed-local` with `status/pr-open`

4. Merge PR after checks:
```powershell
gh pr merge <number> --repo <owner/repo> --merge --delete-branch
```
Use the repository's approved merge strategy. For Lotus work, do not squash unless the user or repository policy explicitly requests it.
- after merge and main-branch validation, replace `status/pr-open` with `status/merged-main` before closing the issue

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
- Treat labels as visibility, not closure proof. PR bodies still need `Fixes #<issue>` and issue comments still need validation evidence.
- Move status labels as soon as the work state changes, especially during batch fixing. Do not wait for the final response.
- Keep status labels mutually exclusive where possible. Remove stale `status/in-progress`, `status/fixed-local`, `status/pr-open`, `status/merged-main`, or `status/blocked` labels when applying the next state.

## GitHub Issue Status Labels

Ensure these repository labels exist before a batch issue-fix run. Create missing labels with:

```powershell
gh label create status/in-progress --repo <owner/repo> --color fbca04 --description "Actively being worked in the current implementation slice"
gh label create status/fixed-local --repo <owner/repo> --color 0e8a16 --description "Fix committed locally or on the working branch; not merged to main yet"
gh label create status/pr-open --repo <owner/repo> --color 1f6feb --description "Fix is included in an open pull request"
gh label create status/merged-main --repo <owner/repo> --color 5319e7 --description "Fix has merged to main; issue may be closed after validation"
gh label create status/blocked --repo <owner/repo> --color d73a4a --description "Work is blocked by missing input, external dependency, or failed prerequisite"
```

Use the labels this way:

- `status/in-progress`: apply when active work starts on an issue or issue cluster.
- `status/fixed-local`: apply only after the fix is committed to the working branch and focused validation has passed.
- `status/pr-open`: apply when a PR containing the fix is open.
- `status/merged-main`: apply after merge to `main` and post-merge validation evidence exists; then close the issue with PR, commit, and validation references.
- `status/blocked`: apply when the issue cannot progress because of missing input, failed prerequisite, unavailable dependency, or policy decision. Remove it when work resumes.

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


