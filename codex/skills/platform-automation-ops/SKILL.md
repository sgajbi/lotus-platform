---
name: platform-automation-ops
description: Run and monitor async, repeatable cross-repo platform automation tasks using lotus-platform automation scripts. Use when the user asks to offload builds/tests/linting/docker refresh/seeding outside chat, run tasks in parallel, track background execution, or check automation status while implementation continues.
---

# Platform Automation Ops

Use `lotus-platform/automation` as the system of record for operational automation.

Execute scripts from the local `lotus-platform` workspace root, not from `automation/`.

## Execute Background Profiles

1. Run detached tasks:
```powershell
cd <lotus-platform>
powershell -ExecutionPolicy Bypass -File automation\Start-Background-Run.ps1 -Profile fast-feedback -MaxParallel 3
```
2. Check status on demand:
```powershell
cd <lotus-platform>
powershell -ExecutionPolicy Bypass -File automation\Check-Background-Runs.ps1
```
3. Watch status:
```powershell
cd <lotus-platform>
powershell -ExecutionPolicy Bypass -File automation\Check-Background-Runs.ps1 -Watch -IntervalSeconds 20
```

## Run Foreground Parallel Profiles

Use this for immediate feedback in current terminal:

```powershell
cd <lotus-platform>
powershell -ExecutionPolicy Bypass -File automation\Run-Parallel-Tasks.ps1 -Profile fast-feedback -MaxParallel 3
```

## Refresh Only Impacted Services

Use changed-files mapping for selective restart:

```powershell
powershell -ExecutionPolicy Bypass -File automation\Service-Refresh.ps1 -ProjectPath <lotus-app-repo> -ChangedOnly -BaseRef origin/main
```

Use explicit services when needed:

```powershell
powershell -ExecutionPolicy Bypass -File automation\Service-Refresh.ps1 -ProjectPath <lotus-app-repo> -Services <service-name>
```

## Report Artifacts

Read and summarize:
- `output/background-runs.json`
- `output/task-runs/*.json`
- `output/task-runs/*.md`
- `output/task-runs/*.out.log`
- `output/task-runs/*.err.log`

## Close PR Loop

Use this when asked to monitor PRs, queue merges, and clean branches without manual repetition:

```powershell
cd <lotus-platform>
powershell -ExecutionPolicy Bypass -File automation\Close-PR-Loop.ps1
```

Continuous mode:

```powershell
cd <lotus-platform>
powershell -ExecutionPolicy Bypass -File automation\Close-PR-Loop.ps1 -Watch -IntervalSeconds 30
```

## Safety and Operating Rules

- Keep stack stable; do not restart entire platform unless explicitly requested.
- Prefer `-ChangedOnly` or specific services for refresh.
- Check logs first when failures occur.
- Keep documentation updates in `lotus-platform` synchronized with script behavior.
- When automation script behavior changes, update:
  - `automation/README.md`
  - `Local Development Runbook.md`
  - this skill reference file if command flow changed

For profile definitions and expected behavior, read `references/profile-guide.md`.
