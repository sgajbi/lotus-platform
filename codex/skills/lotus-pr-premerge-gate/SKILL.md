---
name: lotus-pr-premerge-gate
description: "Enforce Lotus pre-merge verification using the platform multi-lane CI model. Use when preparing to open, update, or merge a PR in any Lotus repo and the goal is zero avoidable CI failures: run repository-native local gates, map the change to Feature Lane and PR Merge Gate expectations, verify required GitHub checks are green, confirm evidence is truthful, then complete merge, mainline releasability proof, and branch hygiene."
---

# Lotus PR Premerge Gate

## Overview

Use this skill to prevent merge churn by enforcing a fixed sequence: local verification, CI verification, merge decision, and post-merge cleanup.

Apply it in line with:

1. `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`
2. `lotus-platform/context/PROCEDURAL-MEMORY-INDEX.md`
3. the target repo `REPOSITORY-ENGINEERING-CONTEXT.md`
4. `lotus-platform/rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`
5. `lotus-platform/docs/standards/Continuous Integration, Validation, and Release Governance Standard.md`

Use `lotus-platform/context/playbooks/PR-LOOP-PLAYBOOK.md` as the operating sequence and `lotus-platform/context/playbooks/FIX-FORWARD-PATTERNS.md` when a required check fails.

Use `lotus-ci-enforcement-governance` before this skill when the work changes CI gate design,
promotes report-only inventories to blocking checks, or updates agent-facing quality enforcement.

## Workspace Scope

The governed source for this skill is `lotus-platform/codex/skills/lotus-pr-premerge-gate`.

Apply it consistently in all Lotus repos unless a repo explicitly defines a stricter policy.

## Workflow

### 0) Repo-focus lock (required)

Before any PR, merge, or cleanup action:

1. Confirm intended repo path explicitly.
2. Confirm repo identity:
   - `git rev-parse --show-toplevel`
   - `git remote -v`
3. If repo does not match active user intent, stop and switch to the correct repo first.

### 1) Pre-flight baseline

1. Confirm branch status and divergence:
   - `git status --short --branch`
   - `git fetch origin --prune`
2. Confirm scope of change:
   - `git diff --name-only origin/main...HEAD`
3. Confirm commit count before the branch becomes expensive to split:
   - `python automation/validate_branch_commit_budget.py --repo-root . --base-ref origin/main --head-ref HEAD`
4. Target 40-60 small, meaningful commits for a substantial governed program and split at a
   capability boundary by 90 commits at the latest when the repository uses rebase merge. GitHub
   [limits server-side rebase merges to 100 commits](https://docs.github.com/en/repositories/creating-and-managing-repositories/repository-limits#rebase-limits).
   The 90-commit threshold preserves room for review and CI fix-forward commits. The canonical
   validator warns at 40 commits, requires a recorded tranche decision at or above 60 commits, and
   fails above 90 commits unless a repository sets a stricter limit.
5. For dependent multi-PR refactor campaigns, create or update the
   `stacked-refactor-campaign` manifest before tranche 1 and after every merge, then validate it
   with `python automation/validate_stacked_refactor_campaign_manifest.py --manifest <path>`.
6. If an existing rebase-only PR exceeds 100 commits, stop retrying the merge. Do not weaken branch
   protection or silently squash the audit trail. Split it into independently releasable,
   sub-100-commit tranches, validate each intermediate state, and keep issue closure on the final
   aggregate outcome.
7. If scope is broad, split into smaller PRs before proceeding.

### 1.0.1) Stranded truth check for governance-bearing PRs

Run this check for any PR that touches or depends on RFCs, README, wiki source, repository context,
AGENTS.md, contracts, API vocabulary, OpenAPI snapshots, migrations, CI workflows, standards, or
supported-features material:

```powershell
git fetch origin --prune
git branch -r --no-merged origin/main
```

For each unmerged remote branch that touches durable governance paths, classify it before merge:

1. `must-merge`
2. `cherry-pick`
3. `superseded`
4. `delete`
5. `active`

Durable governance paths include:

1. `docs/rfcs/`
2. `wiki/`
3. `README.md`
4. `REPOSITORY-ENGINEERING-CONTEXT.md`
5. `AGENTS.md`
6. `contracts/`
7. `platform-contracts/`
8. `context/`
9. `docs/standards/`
10. `.github/workflows/`
11. migrations, OpenAPI snapshots, API vocabulary inventories, and supported-features files

Use:

```powershell
git diff --name-status origin/main..<remote-branch> -- docs/rfcs wiki README.md REPOSITORY-ENGINEERING-CONTEXT.md AGENTS.md contracts platform-contracts context docs/standards .github/workflows
git diff --diff-filter=A --name-status origin/main..<remote-branch> -- docs/rfcs wiki README.md REPOSITORY-ENGINEERING-CONTEXT.md AGENTS.md contracts platform-contracts context docs/standards .github/workflows
git cherry -v origin/main <remote-branch>
```

Rule: do not merge or close an RFC/documentation-governance PR while unique durable truth remains
stranded on another unmerged branch unless that branch is explicitly recorded as `active` with owner,
purpose, expected merge path, and risk.

### 1.1) Branch policy (single-developer optimized)

1. Always branch from `main`.
2. Use one branch per RFC or implementation slice.
3. Never commit directly to `main`, even in single-developer mode.
4. Prefer small, auditable commits and frequent push cadence.
5. Use durable, capability-oriented branch names that are safe to persist in CI evidence,
   release manifests, provenance attestations, and issue comments. Avoid secret-shaped substrings
   such as `token`, `secret`, `password`, `credential`, `private-key`, `apikey`, or `bearer` in
   branch names even when the change is about authentication; prefer names such as
   `auth-env`, `attestation-auth`, `release-provenance`, or `runtime-identity`.
6. Before the first commit or PR push, inspect branch protection for the target base branch:
   - `gh api repos/<owner>/<repo>/branches/<base>/protection`
   - if required signatures are enabled, configure commit signing and verify `git log --format='%h %G? %s' <base>..HEAD` shows `G` for every branch commit before pushing merge intent.
7. For Lotus repositories with required linear history and signed commits, use signed commits from
   the start. Do not rely on a later green CI run to make an unsigned branch mergeable.

### 2) Mandatory local gate pack

Run gates in this order and fail fast:

1. Static quality:
   - repo-native lint command
   - repo-native typecheck command
2. Fast tests:
   - Targeted unit tests for changed modules.
3. Contract/API gates (when API/schema touched):
   - OpenAPI quality gate.
   - API vocabulary generation/validation per RFC-0067.
4. Integration slice:
   - Changed service integration tests.
5. Runtime confidence:
   - Docker smoke and latency gate (if service/runtime behavior changed).

Rule:

1. use repository-native commands such as `make check`, `make lint`, `npm run typecheck`, or equivalent;
2. do not invent ad hoc one-off commands if the repo already defines canonical local gates.

Rule: do not push merge intent if any local gate is red.

### 2.1) Tiered CI strategy (required)

1. Fast PR tier (blocking):
   - Feature Lane + PR Merge Gate checks relevant to the repository profile.
2. Heavy tier (scheduled/manual/main):
   - Main Releasability Gate and Platform End-to-End Validation checks.
3. Do not run heavy-tier checks as blocking on every PR unless explicitly required for high-risk changes.

Map the repo to one of these profiles before deciding what "required" means:

1. UI Product
2. Experience API
3. Domain API
4. Platform Governance / Automation
5. Shared Capability Service

### 3) PR check policy

1. Push only after local gates are green.
2. Open/update PR with explicit evidence section listing commands and pass results.
3. PR is mandatory in single-developer mode.
4. Human review approval is optional in the single-developer baseline; required GitHub checks, conversation resolution, and truthful evidence are the approval control.
5. Prefer asynchronous monitoring for long checks:
   - `gh pr checks <PR_NUMBER> --watch=false`
6. If only heavy GitHub lanes remain pending and local proof is already green:
   - enable auto-merge when appropriate,
   - continue useful work,
   - poll periodically instead of idling.
7. If any required check fails:
   - Diagnose from logs.
   - Fix-forward in same branch.
   - Re-run affected local gates before pushing again.
   - If the failed check consumes PR metadata from `github.event.pull_request` (for example a
     title/body issue-reference guard), do not rely on editing the PR text plus rerunning the old
     workflow run. Existing GitHub Actions reruns can retain the stale pull-request event payload.
     After correcting the PR title/body, create a fresh PR event by pushing the same source tree
     through a safe branch-head refresh, then verify the new run's `headSha` and check logs.
8. If strict branch protection blocks an otherwise-green PR, rebase or merge the current base
   branch into the PR branch and rerun checks instead of bypassing branch protection.
9. If `mergeStateStatus=BLOCKED` or `mergeable_state=blocked` while required checks are green,
   inspect branch protection and commit verification before retrying merge:
   - `gh api repos/<owner>/<repo>/branches/<base>/protection`
   - `gh api repos/<owner>/<repo>/commits/<head-sha> --jq .commit.verification`
   - `git log --format='%h %G? %s' <base>..HEAD`
   If required signatures are enabled and any branch commit is unsigned, configure a registered
   signing key, re-sign the branch commits, push with `--force-with-lease`, and rerun required
   checks. Do not use admin bypass or weaken branch protection to merge unsigned commits.

Rule: never enable merge (or auto-merge) while any required check is failing or pending with known
instability. Pending heavy lanes with a stable history are acceptable for async monitoring once
auto-merge is enabled.

### 3.0.1) Late review finding triage

Before merge, apply the canonical risk-based triage in
[`gh-issue-fix-qa-loop`](../gh-issue-fix-qa-loop/SKILL.md#late-review-finding-triage).
Record whether each finding remains blocking or qualifies for a linked, independent follow-up. A
green check set does not override the blocker classification, and a properly linked and resolved
non-blocking thread does not require a code-changing CI rerun.

Definition of green:

1. local repository-native gates are green,
2. required PR checks are green in GitHub,
3. no known flaky required check is being ignored,
4. PR evidence matches what actually ran,
5. PR evidence names any measured quality movement or explicitly states why the slice preserves
   duplicate-code, complexity, architecture-boundary, security, API-contract, accessibility, and
   supportability posture,
6. before/after scorecards, diff-stat claims, line-count claims, and other quantitative PR claims
   were remeasured against the final PR head and current base after the last rebase, force-push, or
   scope correction, with the reproducible command or evidence artifact named where practical.

Definition of done:

1. implementation and durable closure truth are merged to `main`,
2. required local and GitHub validation has passed,
3. local repository state is synced clean from `main`,
4. repo-local wiki source has been checked when documentation truth changed,
5. published wiki has been updated after merge when wiki truth changed.

### 3.1) Active CI wait queue

Treat a pending required check as monitored delivery time, not as permission to idle or broaden the
active implementation. Preserve the exact repository, branch, PR number, run id, check name, and
head SHA, then poll often enough to keep the user informed within the operating contract.

Between polls, prefer bounded non-overlapping work that can stop immediately when CI or review state
changes:

1. reconcile unresolved review threads and inspect sibling code for the same proven failure pattern;
2. audit repo-local wiki, README, runbook, supported-feature, or review-ledger truth;
3. perform next-slice issue discovery and prepare evidence-backed acceptance criteria;
4. capture repeatable review lessons in skills, context, validators, or fix-forward guidance;
5. perform read-only branch, worktree, stash, stranded-truth, and dangling-process hygiene checks.

Put every real finding into an issue, ledger, or separately scoped issue-backed branch and PR. Do not
leave it only in chat memory or mix it into the active PR because CI happens to be running.

Do not use wait time to:

1. mutate overlapping files in the active branch or another agent's write scope;
2. commit directly to `main`, bypass a gate, or assume a pending check will pass;
3. broaden repository authority, start destructive cleanup without exact-target proof, or launch a
   second long-running runtime that can interfere with the active validation;
4. create unrelated cosmetic churn with no issue, evidence, or durable closure path;
5. leave `gh ... --watch` or equivalent watcher processes dangling after the check or head changes.

Return to the active delivery as soon as CI or review state changes. Re-read the exact head SHA and
required-check set before taking merge action; work completed during the wait does not substitute for
green evidence on the active PR.

### 4) Merge decision gate

Allow merge only when all conditions are true:

1. Required GitHub checks are green.
2. No unresolved conversations, explicitly blocking review comments, or requested changes remain
   after canonical late-review triage.
3. Local repo state is clean and branch contains only intended commits.
4. PR description accurately reflects shipped behavior.
5. If the base branch requires signed commits, every branch commit is verified by GitHub as signed
   before merge is attempted.
6. Quantitative scorecard and diff-stat evidence is final-head evidence, not an earlier branch
   measurement carried forward after a rebase, force-push, prerequisite merge, or scope correction.

If one condition is false, block merge.

In single-developer mode, do not block merge only because no human approval review exists. The governed branch-protection baseline uses required approving review count `0`.

If the change affects canonical UI behavior, cross-app integration, or platform runtime assumptions, also confirm whether Platform End-to-End Validation evidence is required before merge.

### 5) Post-merge hygiene

After merge completes:

1. Inventory every registered worktree before deleting anything:
   - `git worktree list --porcelain`
   - `git status --short --branch` from each candidate worktree
2. Treat a dirty worktree as a preservation task. Before cleanup, create a named stash and record
   its object SHA, or commit the content to a recovery branch; record the repository, worktree
   path, detached HEAD or branch, preservation SHA, reason, and disposition in the issue, PR, or
   task ledger. Never use `git worktree remove --force` to discard it.
3. Verify every candidate branch has no unmerged patch-equivalent commits and that any PR was
   actually merged:
   - `git fetch origin --prune`
   - `git cherry -v origin/main <candidate-branch>`
   - `gh pr view <pr-number> --json state,mergedAt,mergeCommit,headRefName,headRefOid,url`
   A `+` entry, a closed-but-unmerged PR, or an unknown PR state requires an explicit
   `must-merge`, `cherry-pick`, `superseded`, `delete`, or `active` classification; preserve it
   until that evidence is recorded.
4. Confirm the local branch is not checked out by another worktree. Only then remove a clean,
   merged alternate worktree with `git worktree remove <path>` and delete its local branch with
   `git branch -d <branch>`; do not use `-D` as normal cleanup.
5. Delete the remote branch only after GitHub confirms the intended PR merge.
6. Switch a primary worktree to main and sync:
   - `git checkout main`
   - `git pull --ff-only origin main`
7. Capture the merge commit SHA from local `main`:
   - `git rev-parse HEAD`
8. Confirm clean and aligned state:
   - `git status --short --branch`
   - `git branch -vv`
9. Confirm authoritative remote branch state (server truth):
   - `git ls-remote --heads origin`
10. Confirm GitHub PR state:
   - `gh pr list --state open --limit 100`
11. Prove mainline releasability for the exact merge commit when the repository has a Main
    Releasability Gate:
   - `gh run list --workflow "Main Releasability Gate" --commit <merge-sha> --limit 5`
   - `gh run view <run-id> --json status,conclusion,headSha,headBranch,event,url,jobs`
12. If no Main Releasability Gate run exists for the merge SHA and the workflow has
    `workflow_dispatch`, wait briefly and re-run the exact-SHA lookup before dispatching. Some
    repositories start a post-merge or merged-PR releasability dispatch a few seconds after the PR
    state flips. Dispatch exactly one replacement only when the second exact-SHA lookup still finds
    no active or completed run:
   - `gh workflow run main-releasability.yml --ref main`
   - `gh run list --workflow "Main Releasability Gate" --commit <merge-sha> --limit 5`
   - `gh run view <run-id> --json status,conclusion,headSha,headBranch,event,url,jobs`
   If duplicate exact-SHA releasability runs are accidentally created, preserve one active run and
   cancel only redundant runs after confirming repository, workflow, event, branch, and `headSha`.
13. Treat a missing, failed, or wrong-SHA main releasability run as an open release-evidence gap;
   fix forward or record the explicit non-applicability reason before claiming closure.
14. Re-run the stranded truth check for governance-bearing work and delete or record any branch that
   is now superseded.
15. Run `git worktree prune` only after the explicit removal/disposition checks, then repeat
    `git worktree list --porcelain` to verify no stale registrations remain.

Target end-state: local = remote = main.

### 5.1) Branch cleanup policy

1. Delete a merged remote feature branch only after GitHub merge evidence and `git ls-remote`
   verification; never delete a closed-but-unmerged branch without explicit disposition evidence.
2. Delete the corresponding local branch only after a worktree inventory proves it is not checked
   out and `git cherry -v origin/main <branch>` shows no unique patches.
3. Preserve dirty worktree changes as a recorded stash SHA or recovery branch before removal.
4. Ensure no stale worktree registrations or unclassified working files remain.

## Evidence template (use in PR body)

1. `Static:` ruff, mypy
2. `Unit:` targeted module tests
3. `Integration:` affected suites
4. `Runtime:` docker smoke, latency, fast performance gate (if applicable)
5. `Governance:` OpenAPI + RFC-0067 vocabulary checks (if applicable)
6. `Tiering:` confirm whether heavy checks are PR-blocking or scheduled/manual for this change
7. `Stranded truth:` unmerged governance-bearing branches classified, with any restored or
   superseded durable truth named explicitly
8. `Post-merge mainline proof:` Main Releasability Gate run URL and conclusion for the merge SHA,
   or an explicit reason this repository/change does not require mainline releasability evidence
9. `Non-degradation:` measured quality movement, or a precise preservation statement for
   duplicate-code, complexity, architecture boundaries, security, API contracts, accessibility, and
   supportability as applicable
10. `Final-head quantitative evidence:` before/after scorecards, diff-stat, line-count, or other
    numeric PR claims remeasured against the final PR head and current base after the last rebase,
    force-push, prerequisite merge, or scope correction; include base/head refs, the reproducible
    command, and evidence artifact where practical

## Additional Lotus Rules

1. Never merge a repo-local green branch if platform-level required evidence is still red for the affected surface.
2. If a required check is flaky, treat it as a governance defect; do not silently work around it.
3. If branch protection is weaker than the platform standard, call that out explicitly in the final response.
4. Keep merge strategy aligned to repo policy; do not squash unless the user or repo policy requires it.
5. For governed front-office runtime or screenshot-proof changes, require machine-readable evidence
   in addition to screenshots.
6. For CI-enforcement PRs, verify the PR body names the new repo-native command, lane placement,
   focused gate tests, scorecard movement, and any skill/context sync evidence.

## Non-negotiables

1. Never merge on red checks.
2. Never skip local verification for speed.
3. Never leave branch hygiene incomplete after merge.
4. If a gate is flaky, stabilize the gate or make readiness explicit before merge.
5. In single-developer mode, PR and CI checks replace human approval; they are mandatory.
6. Branch cleanup must be verified with both local refs (`git branch -r`) and remote server truth (`git ls-remote --heads origin`).
7. For RFC/docs/wiki/context/contract PRs, merged code or docs without reconciled mainline closure
   truth is not complete.
8. A green PR Merge Gate is not release evidence by itself when a repository has a Main
   Releasability Gate; post-merge proof must point to the merge SHA.
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


