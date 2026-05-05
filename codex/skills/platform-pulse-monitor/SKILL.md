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
