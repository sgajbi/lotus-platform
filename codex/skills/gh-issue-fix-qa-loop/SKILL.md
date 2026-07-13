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
labels. A repository with a different established vocabulary must pass its own compatible
`-LabelContractPath`; do not create a second slash, colon, or spelling family.

QA is evidence layered over these lifecycle states, not another status-label family. A QA failure
reopens the issue and returns it to `status/in-progress`. A QA pass closes an issue only after
`status/merged-main` exists and retains that terminal label.

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

The audit fails on closed issues with active labels, open issues with terminal labels, and
configured legacy aliases still present in the repository or on an issue. It reports JSON and does
not mutate issues or delete labels.

Both entrypoints dot-source `scripts/issue-loop-common.ps1`; treat that shared module as internal
implementation and invoke only the update or audit entrypoint directly.

## Operating Rules

- Do not close without QA evidence.
- Do not apply `status/merged-main` without a merged PR, matching merge/main SHA, successful
  primary and security or repository-equivalent runs for that SHA, wiki evidence, and branch
  cleanup evidence.
- Do not merge while required checks fail.
- Keep lifecycle labels mutually exclusive; every transition removes all configured state labels
  and aliases before applying the target state.
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
