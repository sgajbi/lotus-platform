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

For behavior details, read `references/operations.md`.
