---
name: platform-pulse-monitor
description: Run cross-repo sync and PR monitoring pulse, including continuous agent loop status reporting. Use when the user asks to synchronize repositories, monitor open PRs, keep an automation heartbeat, or generate platform-wide status artifacts.
---

# Platform Pulse Monitor

Use shared scripts in `lotus-platform/automation`.

## One-Shot Pulse

```powershell
cd <lotus-platform>
powershell -ExecutionPolicy Bypass -File automation\Platform-Pulse.ps1
```

## Continuous Agent

```powershell
powershell -ExecutionPolicy Bypass -File automation\Run-Agent.ps1
```

Single iteration:

```powershell
powershell -ExecutionPolicy Bypass -File automation\Run-Agent.ps1 -Once
```

## PR Lifecycle (Auto-Merge + Branch Cleanup)

Use this to continuously close the PR loop without manual repetition:

```powershell
powershell -ExecutionPolicy Bypass -File automation\Close-PR-Loop.ps1
```

Watch mode:

```powershell
powershell -ExecutionPolicy Bypass -File automation\Close-PR-Loop.ps1 -Watch -IntervalSeconds 30
```

When a PR is green but remains blocked, include a signed-commit protection check before reporting it
as waiting on GitHub:

1. inspect base branch protection with
   `gh api repos/<owner>/<repo>/branches/<base>/protection`,
2. if required signatures are enabled, inspect the PR head verification with
   `gh api repos/<owner>/<repo>/commits/<head-sha> --jq .commit.verification`,
3. for local same-owner branches, verify all branch commits with
   `git log --format='%h %G? %s' <base>..HEAD`,
4. classify unsigned-commit blocks as `fix-signatures`, not `ci-pending` or `github-delay`.

Do not recommend admin bypass or weakening signed-commit protection. Re-sign the branch commits with
a registered signing key and push with `--force-with-lease` when the branch is safe to rewrite.

## Outputs to Review

- `output/pr-monitor.json`
- `output/agent-status.md`
- `output/pr-lifecycle.json`
- `output/pr-lifecycle.md`

## Stranded Governance Branch Pulse

When monitoring RFC programs, documentation closure, or platform-wide branch hygiene, include a
stranded-truth pulse for each active Lotus repository:

```powershell
git fetch origin --prune
git branch -r --no-merged origin/main
```

Flag any unmerged remote branch that changes durable governance paths:

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

The pulse output should make branch intent visible:

1. branch name,
2. repository,
3. unique governance paths changed,
4. likely RFC or product area,
5. recommended disposition: `must-merge`, `cherry-pick`, `superseded`, `delete`, or `active`.

Do not report a branch as safe just because its PR was not open. A remote branch with unique
governance truth can still strand product/documentation state outside `main`.

For behavior details, read `references/operations.md`.
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


