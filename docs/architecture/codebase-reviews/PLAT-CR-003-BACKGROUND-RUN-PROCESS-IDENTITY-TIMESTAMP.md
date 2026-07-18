# PLAT-CR-003 Background-Run Process Identity Timestamp

## Objective

Prevent a live repository-native background task from being classified `LOST` when PowerShell
deserializes its ISO process-start timestamp into a typed `DateTime`.

## Finding

Exact core task `eng-task-20260718-105538-lotus-core-make-profile-derived-state-fan-in` launched
runner PID `45280` and child `make` PID `32604`. The first reconciliation marked it `LOST`, although
both processes remained live. `ConvertFrom-Json` had materialized `runtime.process_started_at` as a
`DateTime`; the checker passed that object to `DateTimeOffset.Parse`, which culture-formatted it as
`07/18/2026 10:55:38`. The Singapore parser rejected `18` as a month and the catch path returned no
owned process.

## Change

- Accept `DateTimeOffset` values through `UtcDateTime` directly.
- Accept `DateTime` values through `ToUniversalTime()` directly.
- Parse only string inputs, using invariant culture and `RoundtripKind`.
- Preserve the existing five-second process-start identity tolerance and stale-PID rejection.

## Tests

The focused regression launches a hidden live sleeper, writes its start identity through the real
JSON ledger boundary, runs `Check-Background-Runs.ps1`, and requires `RUNNING` with no terminal time
or error. The adjacent wrong-start-time test continues to require `LOST`.

## Exact Runtime Proof

After the fix, repository-native task
`eng-task-20260718-111112-lotus-core-make-profile-derived-state-fan-in` launched hidden runner PID
`39596` and target PID `49928` against clean `lotus-core` source
`31ac198a43d0263940ee3c349caffd88ee521155`. Immediate reconciliation retained `RUNNING` instead of
misclassifying the live process as `LOST`. Terminal reconciliation then recorded `SUCCEEDED`, exit
code `0`, no error summary, and the required fresh artifact
`output/task-runs/20260718T031229Z-bank-day-load.json`.

This proves the JSON-deserialized timestamp path at both live and terminal boundaries using the
same typed repository-native launcher that exposed the defect.

## Compatibility And Documentation Decision

No ledger schema, task ID, launcher CLI, target execution, artifact contract, or GitHub workflow
changes. The fix corrects monitor interpretation only. Automation README, repository context,
central engineering context, the task-ledger playbook, and this review ledger are updated. No wiki
source changes because this remains internal automation behavior.
