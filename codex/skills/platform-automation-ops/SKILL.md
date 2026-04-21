---
name: platform-automation-ops
description: Run and monitor async, repeatable cross-repo platform automation tasks using lotus-platform automation scripts. Use when the user asks to offload builds/tests/linting/docker refresh/seeding outside chat, run tasks in parallel, track background execution, or check automation status while implementation continues.
---

# Platform Automation Ops

Use `lotus-platform/automation` as the system of record for operational automation.

Execute scripts from the local `lotus-platform` workspace root, not from `automation/`.

Before launching or summarizing detached work, use
`lotus-platform/context/playbooks/AGENT-CONTEXT-AND-TASK-LEDGER.md` and the contract in
`lotus-platform/platform-contracts/agent-engineering/engineering-task-ledger-contract.v1.json`.
Preserve `engineering_task_id`, repository, branch, PR number, commit SHA, check name, RFC id, file
path, endpoint, contract name, portfolio id, and task status exactly when those identifiers are
present.

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
- `output/heartbeat/heartbeat-status.json`
- `output/heartbeat/heartbeat-status.md`
- `output/heartbeat/heartbeat-issues.json`
- `output/heartbeat/heartbeat-state.json`
- `output/task-runs/*.json`
- `output/task-runs/*.md`
- `output/task-runs/*.out.log`
- `output/task-runs/*.err.log`

For `output/background-runs.json`, report the governed lifecycle status without translation:

- `RUNNING`: launched process is still active,
- `SUCCEEDED`: expected result artifact exists and all child task exit codes are zero,
- `FAILED`: result artifact exists but failed or could not be parsed,
- `LOST`: process ended before expected result evidence was written.

Treat `LOST` as an operational finding that needs cleanup or rerun evidence. GitHub Actions remains
the source of truth for GitHub check status; the background-run ledger is local automation evidence.

## Generate Heartbeat Attention Artifacts

Use this for an advisory RFC-0095 attention snapshot across configured local evidence sources:

```powershell
cd <lotus-platform>
powershell -ExecutionPolicy Bypass -File automation\Run-Heartbeat.ps1
```

Use deterministic metadata when preserving proof in an RFC, PR, or handoff:

```powershell
cd <lotus-platform>
powershell -ExecutionPolicy Bypass -File automation\Run-Heartbeat.ps1 -GeneratedAtUtc 2026-04-21T00:00:00Z -Branch <branch>
```

Heartbeat output is derived advisory evidence. It does not replace GitHub, the RFC-0094
background-run ledger, mesh certification, wiki source, context validators, or `lotus-ai`
workflow-pack runtime APIs as source truth. Suppressed items remain visible; blocking findings are
not suppressible.

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
  - heartbeat context/wiki guidance when RFC-0095 operator behavior changes
- Do not summarize detached work from chat memory alone when a task-ledger or GitHub evidence source
  exists.

For profile definitions and expected behavior, read `references/profile-guide.md`.
