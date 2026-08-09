---
name: gh-issue-fix-qa-loop
description: GitHub issue-to-resolution execution loop for engineering and QA handoff. Use when the user asks to take open issues, implement fixes, raise and merge PRs, update issue progress, request QA validation, reconcile stale status labels, or continue fix/retest cycles until issues are verified and closed.
---

# GH Issue Fix QA Loop

Run `analyze -> fix -> local proof -> PR -> merge -> exact-main proof -> QA -> close or reopen`.
Use `gh` CLI, repository-native tests, and the colocated automation. For Lotus services, compose
this skill with the relevant delivery and QA-validation skills.

## Preconditions

1. Verify `gh auth status`.
2. Search open and closed issues for the root cause before creating a new issue.
3. Link every actionable defect, ownership move, or deferred migration to one canonical issue.
4. Use the repository's branch policy and approved merge strategy.
5. Load [state-machine](references/state-machine.md) and
   [comment-templates](references/comment-templates.md) before changing issue state.

Do not leave actionable work only in chat, compacted context, or a review note. For urgent
production containment, mitigate first only when delay increases harm, then capture the canonical
issue before calling the slice complete.

## Governed Labels

The default semantic mapping is defined by
[issue-status-label-contract.json](references/issue-status-label-contract.json):

| Semantic state | Default label |
| --- | --- |
| Active implementation | `status/in-progress` |
| Committed and locally validated | `status/fixed-local` |
| Open PR | `status/pr-open` |
| Merged and exact-main validated | `status/merged-main` |
| Externally or operationally blocked | `status/blocked` |

The scripts discover and validate the repository vocabulary before mutation. They never create
labels. A repository may use either the default label or one configured alias for a lifecycle
state; the scripts resolve the effective per-repository label before mutating issues. Use a
compatible `-LabelContractPath` only when the repository uses labels outside the default
primary-or-alias set. Do not create a second slash, colon, or spelling family.

`status/blocked` is required only when a repository needs blocked-state automation. Repositories
without a blocked label can still use active, fixed-local, PR-open, merged-main, QA, and audit
flows. A blocked transition fails closed before removing any prior state label if the repository
does not define a blocked label.

Repository-specific program ledgers may define additional lifecycle labels, such as
`status/tracker` for parent or umbrella execution anchors. Use those only when the repository's
own audit documents and enforces the mapping; do not route them through the generic issue-loop
transition script unless the label contract and scripts support the state end-to-end.

QA is evidence layered over these lifecycle states, not another status-label family. A QA failure
reopens the issue and returns it to `status/in-progress`. A QA pass closes an issue only after
`status/merged-main` exists and retains that terminal label.

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

## Late Review Finding Triage

Green CI is evidence, not immunity from review. Classify each late finding before resolving its
thread:

1. Keep the finding blocking when the PR introduced it, its acceptance criteria require it, or it
   can affect correctness, security or privacy, authorization or tenant isolation, data integrity,
   contracts or schemas, migrations, breaking behavior, release safety, or a required check.
   Fix it in the PR and rerun the affected required validation.
2. Defer only a genuinely independent, pre-existing, non-blocking finding after required CI is
   green. Search for an existing issue first. The canonical follow-up issue must record an owner,
   impact, evidence, the originating PR and review-thread links, acceptance criteria, evaluation
   conditions, and an explicit non-blocking rationale.
3. Reply to the originating review thread with the canonical issue link and rationale, then resolve
   the thread. Summarize the disposition on the PR so merge evidence is self-contained.
4. Prefer focused affected-lane validation when repository governance permits. Do not restart broad
   green CI when no PR code changed, and do not use a follow-up issue to hide a PR-introduced or
   release-critical defect.

If the classification, ownership, or evidence is uncertain, keep the review finding blocking.
Use the late-review template in [comment-templates](references/comment-templates.md) so the decision
survives chat or context compaction.

## Workflow

1. Start implementation:

```powershell
./scripts/update-issue-loop.ps1 -Repo <owner/repo> -IssueNumber <n> -Status dev_in_progress
```

2. After a focused commit and local proof:

```powershell
./scripts/update-issue-loop.ps1 -Repo <owner/repo> -IssueNumber <n> -Status fixed_local `
  -CommitSha <sha> -LocalValidationRef "<commands/results>"
```

3. After opening a linked PR:

```powershell
./scripts/update-issue-loop.ps1 -Repo <owner/repo> -IssueNumber <n> -Status pr_raised -PrNumber <pr>
```

For partial fixes, blocker-proving PRs, or evidence-consumption PRs that do not satisfy the full
issue acceptance criteria, keep the issue linked without GitHub auto-close keywords. The PR body and
issue comment should say `Keep #<issue> open` and name the remaining evidence class. Do not use
`Closes`, `Fixes`, or `Resolves` for that issue until the closure transition is intended and the
issue is ready for QA-backed closure. Negated closing-keyword phrases are still unsafe when they
include an issue reference, because GitHub matches the closing keyword and reference without honoring
the negation; do not write phrases such as `does not close #<issue>` or `not fixing #<issue>` in PR
titles or bodies. If a repository has an execution-ledger gate, run it before opening the PR and
again before merge evidence is posted. If it also exposes a GitHub issue-state audit, run that audit
after lifecycle-label changes, before quoting issue counts, and before posting merged-main evidence
so GitHub open/closed state cannot drift from the durable execution ledger.
If a PR-text gate fails because the PR body or title used auto-close wording for a keep-open issue,
edit the title/body, run the repo-local PR-text gate locally, and then create a fresh PR check
event with a source-controlled push such as an amend/no-op commit. GitHub Actions reruns and PR-body
edits can retain the stale `pull_request` payload, so do not treat a rerun of the old failing event
as proof that the corrected PR text was evaluated.
Run the PR-text gate as a fail-closed precondition before `gh pr create`, `gh pr edit`, or any
branch-head refresh intended to prove corrected PR text. In PowerShell, check `$LASTEXITCODE` or
wrap the gate in a script step that exits immediately; do not put the gate and `gh pr create` in a
loose command group where later commands continue after the gate rejects unsafe keep-open wording.

4. If merged but exact-main checks are still pending:

```powershell
./scripts/update-issue-loop.ps1 -Repo <owner/repo> -IssueNumber <n> `
  -Status merged_pending_main_validation -PrNumber <pr> -MainSha <sha>
```

5. After exact-main validation, wiki decision/publication, and branch cleanup:

```powershell
./scripts/update-issue-loop.ps1 -Repo <owner/repo> -IssueNumber <n> -Status merged_main `
  -PrNumber <pr> -MainSha <sha> -PrimaryValidationRunId <run> `
  -SecurityValidationRunId <run> -WikiEvidence "<publication or no-change decision>" `
  -BranchCleanupEvidence "<local/remote branch check>"
```

6. Close after QA, or reopen on failure:

```powershell
./scripts/update-issue-loop.ps1 -Repo <owner/repo> -IssueNumber <n> `
  -Status qa_passed_closed -QaRunRef "<artifact or run>"

./scripts/update-issue-loop.ps1 -Repo <owner/repo> -IssueNumber <n> `
  -Status qa_failed -QaRunRef "<artifact or run>" -Summary "<expected versus actual>"
```

Pass comma-delimited values such as `-IssueNumber 101,102` only when one transition and one evidence
set truthfully applies to every issue in the batch.

## Audit

Run before PR closure and after batch reconciliation:

```powershell
./scripts/audit-issue-loop.ps1 -Repo <owner/repo>
```

The audit fails on closed issues with active labels, issues carrying multiple canonical lifecycle
labels, and configured legacy aliases still present in the repository or on an issue. An open
`status/merged-main` issue is valid while QA remains pending; the same completion label is retained
after QA closes the issue. The audit reports JSON and does not mutate issues or delete labels.

When a repository has experienced GitHub auto-closing a merged-main issue before QA evidence is
recorded, or before quoting QA-complete issue counts, run the stricter evidence mode:

```powershell
./scripts/audit-issue-loop.ps1 -Repo <owner/repo> -RequireQaClosureEvidence
```

This keeps the default label-hygiene audit compatible, but flags a closed `status/merged-main`
issue when the issue thread lacks a standard `Loop status: qa_passed_closed` comment. The strict
mode is read-only; fix the issue with a lifecycle update or reopen/comment correction rather than
editing labels by hand.

Use `-IssueNumber <n>` or a comma-delimited PowerShell array to target a recent issue after
correcting an auto-close, while legacy repositories phase in broader strict-mode cleanup:

```powershell
./scripts/audit-issue-loop.ps1 -Repo <owner/repo> -IssueNumber 579 -RequireQaClosureEvidence
```

Repository-specific RFC or program ledgers may also provide a stricter issue-state audit that
compares the checked-in ledger to live GitHub issue state. When present, run it with the ledger gate
after reopen, close, block, unblock, or lifecycle-label changes, and before summarizing remaining
issue counts. Treat failures as lifecycle drift: reconcile the GitHub state or ledger first, then
continue implementation. If the repository ledger distinguishes parent or umbrella issues from
active work items, give those tracker issues an explicit lifecycle label such as `status/tracker`
and make the repo audit fail when the label is missing; statusless tracker issues are not durable
execution truth.

If a repository exposes a deterministic issue execution summary, backlog report, or handoff command
that is generated from the checked-in ledger, run it after the live state audit before quoting issue
counts or next-work posture. Prefer that repo-owned summary over chat memory, compacted context,
assignee-only filters, or one-off `gh issue list` output.

Some repositories also provide a machine-readable issue-learning or pattern ledger. When present,
run its repo-native gate before implementing the next related issue and before PR evidence. Treat
failures as same-pattern drift: either update the pattern ledger with the issue's durable defect
family, controls, future-agent rule, and no-claim boundaries, or create/reuse a more specific
GitHub issue before source mutation. Do not let repeated issue lessons live only in chat,
compacted context, or PR prose.

Both entrypoints dot-source `scripts/issue-loop-common.ps1`; treat that shared module as internal
implementation and invoke only the update or audit entrypoint directly.

## Operating Rules

- Do not close without QA evidence. Treat `status/merged-main` as a completion label that may remain
  on an open issue pending QA or on the closed issue after QA passes, not as a closed-only label.
- Do not apply `status/merged-main` without a merged PR, matching merge/main SHA, successful
  primary and security or repository-equivalent runs for that SHA, wiki evidence, and branch
  cleanup evidence.
- Do not merge while required checks fail.
- Keep lifecycle labels mutually exclusive; every transition removes all configured state labels
  and aliases before applying the repository-resolved target state.
- Reopen an issue when GitHub auto-closure precedes lifecycle normalization. Only the
  evidence-backed `qa_passed_closed` transition closes it again. Do not reopen an already closed
  issue that retains the terminal merged-main label when replaying merged-main evidence.
- Use the same issue thread for retries; avoid duplicate QA issues and comments.
- Treat labels as visibility, not proof. Preserve PR, SHA, run, wiki, and cleanup references.
- Use `status/blocked` only with a concrete blocker comment and return to active implementation when
  work resumes.

## Continuous Skill Improvement

At the end of any meaningful use of this skill, decide whether the work exposed a repeatable failure
mode, missing step, weak trigger, validation gap, or context-routing gap. Promote durable
lessons into the platform-owned skill source, references, scripts, or validators. Update routing or
central context only when task selection or platform truth changes. Keep automation colocated with
this skill and record an explicit no-change decision when no broader update is justified.
