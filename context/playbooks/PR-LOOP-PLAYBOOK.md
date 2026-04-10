# PR Loop Playbook

Use this playbook for branch preparation, push cadence, GitHub monitoring, merge readiness, and cleanup.

## Working Sequence

1. confirm repo and branch scope
2. run the smallest truthful local validation pack
3. push early once local proof is real enough for GitHub to carry the expensive matrix
4. open or update the PR with truthful evidence
5. monitor required checks asynchronously
6. fix forward from real failure logs
7. merge only when required checks are green
8. clean local and remote branch state after merge

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
5. any remaining governed deviation.

Do not claim commands or coverage that were not actually run.

## Merge And Cleanup Rule

Before merge:

1. required GitHub checks must be green,
2. unresolved critical review or governance issues must be closed,
3. the PR description must still match the shipped behavior.

After merge:

1. delete remote feature branch,
2. delete local feature branch,
3. fast-forward local `main`,
4. verify the repo is clean.
