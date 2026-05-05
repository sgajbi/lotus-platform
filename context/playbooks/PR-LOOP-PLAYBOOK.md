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
9. clean local and remote branch state after merge

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

## Truthful PR Evidence Rule

A PR must state:

1. what changed,
2. which commands actually ran locally,
3. which GitHub checks were expected to carry the heavy path,
4. any required platform validation evidence,
5. any stranded-governance-branch reconciliation for RFC/docs/wiki/context/contract changes,
6. any remaining governed deviation.

Do not claim commands or coverage that were not actually run.

## Merge And Cleanup Rule

Before merge:

1. required GitHub checks must be green,
2. unresolved conversations, explicitly blocking review comments, or governance issues must be closed,
3. the PR description must still match the shipped behavior,
4. governance-bearing work must not leave unclassified unique RFC/docs/wiki/context/contract truth
   on unmerged remote branches.

In the single-developer Lotus operating model, approving human reviews are not required. PRs, protected `main`, required checks, conversation resolution, and audit evidence are the approval control.

After merge:

1. delete remote feature branch,
2. delete local feature branch,
3. fast-forward local `main`,
4. verify the repo is clean,
5. for governance-bearing work, confirm any branch that previously held the only copy of restored
   truth is merged, deleted, or explicitly recorded as superseded/active.
