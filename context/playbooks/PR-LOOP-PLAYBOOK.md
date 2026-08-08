# PR Loop Playbook

Use this playbook for branch preparation, push cadence, GitHub monitoring, merge readiness, and cleanup.

## Working Sequence

1. confirm repo and branch scope
2. reconcile stranded governance truth when the work touches or depends on RFC/docs/wiki/context/contracts
3. run the smallest truthful local validation pack
4. push early once local proof is real enough for GitHub to carry the expensive matrix
5. open or update the PR with truthful evidence
6. monitor required checks asynchronously
7. fix forward from real failure logs
8. merge only when required checks are green
9. prove post-merge mainline releasability for the merge commit when the repo has that lane
10. clean local and remote branch state after merge

## Rebase Commit-Count Rule

Before the first PR and during every long-running delivery program, run:

```powershell
python automation/validate_branch_commit_budget.py --repo-root . --base-ref origin/main --head-ref HEAD
```

GitHub [limits server-side rebase merges to 100 commits](https://docs.github.com/en/repositories/creating-and-managing-repositories/repository-limits#rebase-limits).
For repositories that require linear history and use rebase merge, target 40-60 commits and split
at a capability boundary by 90 commits at the latest so review and CI fix-forward work has
headroom. Each tranche must be independently releasable and pass the repository's normal protected
checks.

The branch-budget validator warns at 40 commits, requires an explicit tranche decision at or above
60 commits, and fails above 90 commits by default. For a branch that intentionally continues beyond
60 commits, record the split decision in PR evidence and pass it to shared preflight through
`-TrancheDecision` or to the Python validator through `--tranche-decision`.

If an existing PR is already over the limit, do not weaken branch protection, switch merge policy,
or silently squash governed history. Split it into validated sub-100-commit tranches and retain
issue closure on the final aggregate outcome.

For a governed refactor that needs multiple tranches, create a
`stacked-refactor-campaign` manifest before tranche 1 and update it after every tranche merge. Use
`platform-contracts/agent-engineering/stacked-refactor-campaign-manifest.schema.json` and validate
with:

```powershell
python automation/validate_stacked_refactor_campaign_manifest.py --manifest <path-to-campaign-manifest.json>
```

The manifest records campaign issues, branch/base/head SHAs, predecessor main SHA, capability
boundary, commit budget, tranche decision, local and remote evidence, issue-closure posture, and
final aggregate closure. Campaign issues stay open until the final tranche is merged to validated
main and branch cleanup evidence is recorded.

For a governed refactor campaign that will span multiple dependent PRs, create or update a
`stacked-refactor-campaign` manifest before tranche 1 and after every merge. Use the contract under
`platform-contracts/agent-engineering/stacked-refactor-campaign-manifest.schema.json` and validate
it with `python automation/validate_stacked_refactor_campaign_manifest.py --manifest <path>`. The
manifest must preserve tranche ids, branch/base/head SHAs, predecessor main SHA, capability
boundary, commit budget posture, local and remote evidence, issue closure decision, and final
aggregate closure evidence. Campaign issues stay open until the final tranche is merged and
validated on exact `main`.

## Stranded Governance Truth Rule

For RFC, documentation, wiki, context, contract, API-governance, migration, CI, or
supported-features work, run this before opening or merging a PR:

```powershell
git fetch origin --prune
git branch -r --no-merged origin/main
```

Inspect unmerged branches that touch durable governance paths:

```powershell
git diff --name-status origin/main..<remote-branch> -- docs/rfcs wiki README.md REPOSITORY-ENGINEERING-CONTEXT.md AGENTS.md contracts platform-contracts context docs/standards .github/workflows
git cherry -v origin/main <remote-branch>
```

Classify each branch as:

1. `must-merge`
2. `cherry-pick`
3. `superseded`
4. `delete`
5. `active`

Do not close an RFC or promote a supported feature while unique durable truth remains stranded on
another unmerged branch. Restore or supersede the truth first, add an index/test guard where
practical, and record the disposition in the PR evidence.

## Local Proof Rule

Before pushing:

1. run targeted unit or contract tests for changed code,
2. run repo-native lint and typecheck where applicable,
3. run the minimum additional proof needed to justify the push.

Do not wait for every expensive check locally when GitHub is the better execution engine for:

1. full PR merge-gate matrices,
2. browser smoke or end-to-end suites,
3. Docker build validation,
4. platform-wide validation.

## GitHub-Backed Heavy Execution Rule

Prefer GitHub for heavy execution when:

1. the check is already defined in the repo’s CI lane,
2. the run is long enough to block implementation progress,
3. the failure logs in GitHub are the real source of truth,
4. the result needs merge-gate evidence anyway.

While GitHub is running:

1. continue non-overlapping implementation work,
2. poll check status asynchronously,
3. fix only the failures that the logs actually show.

If a failed check reads PR metadata from `github.event.pull_request`, such as title/body issue
closure wording, editing the PR text alone may not update an already-created Actions run. Do not
rerun stale event payloads as proof. After correcting the PR title or body, create a fresh PR event
by pushing a safe branch-head refresh with the same intended source tree, then verify the new run's
`headSha` and logs.

Negated auto-close wording is not safe when it still includes an issue reference. GitHub can close
an issue from the closing keyword plus reference even when the sentence says the PR does not close
the issue. For keep-open or partial-scope PRs, write `Keep #<issue> open` and describe remaining
evidence without phrases such as `does not close #<issue>` or `not fixing #<issue>`.

Run PR title/body gates as fail-closed preconditions before mutating GitHub PR state. In
PowerShell, do not place the gate, push, and `gh pr create` in one loose command group. Use an
explicit exit check:

```powershell
python scripts/github_issue_pr_text_gate.py --title-env LOTUS_PR_TITLE --body-env LOTUS_PR_BODY
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
gh pr create --title $env:LOTUS_PR_TITLE --body $env:LOTUS_PR_BODY --base main --head <branch>
```

Apply the same pattern before `gh pr edit` and before pushing a source-refresh commit that is meant
to prove corrected PR text. A rejected local PR-text gate means stop, rewrite the title/body, and
rerun the gate before creating or mutating the PR.

## Recoverable Worktree And Branch Lifecycle Rule

Treat a worktree or branch as a potentially unique delivery artifact until Git and GitHub evidence
proves otherwise. A closed PR, an old directory name, or apparent staleness is never deletion
evidence. Do not use force removal to make an inventory look clean.

Before removing any alternate worktree or feature branch:

1. inventory registered worktrees and their checked-out refs:

   ```powershell
   git worktree list --porcelain
   ```

2. in every candidate worktree, capture `git status --short --branch`; a dirty worktree is a
   preservation task, not a cleanup candidate;
3. inspect the candidate branch for unmerged patch-equivalent commits:

   ```powershell
   git fetch origin --prune
   git cherry -v origin/main <candidate-branch>
   ```

   A `+` entry means the branch still has a patch not represented on `origin/main`; classify it
   before any deletion;
4. for a PR-backed branch, verify GitHub state and merge identity rather than trusting local
   ancestry alone, especially after rebase merge:

   ```powershell
   gh pr view <pr-number> --json state,mergedAt,mergeCommit,headRefName,headRefOid,url
   git ls-remote --heads origin <candidate-branch>
   ```

5. confirm the branch is not checked out by another registered worktree before deleting its local
   ref.

For a dirty worktree, first preserve the payload using a named stash with its object SHA recorded
in the task ledger or issue, or commit it to a clearly named recovery branch. Record the repository,
worktree path, original branch or detached HEAD, preservation SHA, reason, and intended disposition.
Do not use `git worktree remove --force`, `git branch -D`, or a broad filesystem deletion as a
substitute for preservation evidence.

For a closed-but-unmerged PR or branch with unique commits, classify it as `must-merge`,
`cherry-pick`, `superseded`, `delete`, or `active`. Record the classification, owner, and proof in
the issue, PR, or task ledger. Preserve `active` and unclassified branches. Delete only after the
classification proves that no unique implementation or durable governance truth will be lost.

For a clean merged candidate, remove it in this order:

1. fast-forward a primary worktree to `main` and capture the merge SHA;
2. remove the clean alternate worktree with `git worktree remove <path>`;
3. delete the local ref with `git branch -d <branch>` only after it is no longer checked out;
4. delete the corresponding remote branch only after GitHub confirms the intended PR merged;
5. run `git worktree prune`, then repeat `git worktree list --porcelain`, `git branch -vv`, and
   `git ls-remote --heads origin` to prove the intended end state.

This policy deliberately preserves intentional worktrees for open PRs, active investigations, and
declared recovery branches. Hygiene means controlled lifecycle ownership, not deleting every
non-`main` ref.

## Truthful PR Evidence Rule

A PR must state:

1. what changed,
2. which commands actually ran locally,
3. which GitHub checks were expected to carry the heavy path,
4. any required platform validation evidence,
5. any stranded-governance-branch reconciliation for RFC/docs/wiki/context/contract changes,
6. any remaining governed deviation.

Do not claim commands or coverage that were not actually run.

Before merge, remeasure scorecards, diff-stat movement, line-count deltas, coverage changes, or
other quantitative PR claims against the final PR head and current base after the last rebase,
force-push, prerequisite merge, or scope correction. Record the reproducible command, final
base/head refs, and evidence artifact where practical. Earlier branch measurements may be retained
as historical context, but they are not final closure truth.

Keep arbitrary prose parsing report-only unless a structured evidence contract can be made
deterministic and low-noise.

## Merge And Cleanup Rule

Before merge:

1. required GitHub checks must be green,
2. unresolved conversations, explicitly blocking review comments, or governance issues must be closed,
3. the PR description must still match the shipped behavior,
4. governance-bearing work must not leave unclassified unique RFC/docs/wiki/context/contract truth
   on unmerged remote branches,
5. quantitative evidence in the PR description or scorecard must be final-head/current-base
   evidence, not a stale measurement from an earlier branch state.

In the single-developer Lotus operating model, approving human reviews are not required. PRs, protected `main`, required checks, conversation resolution, and audit evidence are the approval control.

Use the repository's configured merge policy as the source of truth. If GitHub rejects merge
commits or the repository requires linear history, use the approved non-squash path such as rebase
merge and stop retrying merge commits for that repository. Do not squash governed Lotus PRs unless
repository policy or the owner explicitly requires it. For RFC-driven, proof-driven, standards,
context, wiki, or CI-workflow work, record the merge method in the PR evidence or slice closure
manifest.

After merge:

1. delete remote feature branch,
2. delete local feature branch,
3. fast-forward local `main`,
4. capture the merge commit SHA with `git rev-parse HEAD`,
5. when the repo has a Main Releasability Gate, prove a successful run exists for that SHA:

   ```powershell
   gh run list --workflow "Main Releasability Gate" --commit <merge-sha> --limit 5
   gh run watch <run-id>
   gh run view <run-id> --json status,conclusion,headSha,headBranch,event,url,jobs
   ```

6. if no run exists for the merge SHA and the workflow supports manual dispatch, wait briefly and
   repeat the exact-SHA lookup before dispatching. Some repositories start a post-merge or
   merged-PR releasability run a few seconds after the PR state changes. Dispatch exactly one
   replacement only when the second exact-SHA lookup still finds no active or completed run:

   ```powershell
   gh workflow run main-releasability.yml --ref main
   gh run list --workflow "Main Releasability Gate" --commit <merge-sha> --limit 5
   gh run watch <run-id>
   gh run view <run-id> --json status,conclusion,headSha,headBranch,event,url,jobs
   ```

7. if duplicate exact-SHA releasability runs are accidentally created, do not cancel immediately.
   First re-list the exact-SHA workflow runs and let GitHub concurrency settle. Preserve the sole
   active run. If concurrency has already cancelled the earlier run, keep the latest active run and
   record the cancelled duplicate as operator error. Cancel only redundant runs after confirming
   that at least one exact-SHA run remains active or has already succeeded for the same repository,
   workflow, event, branch, and `headSha`. Never cancel all exact-SHA runs and then claim
   mainline evidence.
8. verify the repo is clean,
9. for governance-bearing work, confirm any branch that previously held the only copy of restored
   truth is merged, deleted, or explicitly recorded as superseded/active.

A green PR Merge Gate is not release evidence by itself when the repository has a Main
Releasability Gate. Post-merge closure must name the successful run URL for the merge SHA, or
record why the repository/change does not require that evidence.
