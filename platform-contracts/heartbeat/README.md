# Heartbeat Contracts

This directory contains RFC-0095 heartbeat monitoring contracts.

The first-wave heartbeat contract is `heartbeat-status.schema.json`. It governs the derived
operator artifacts written to:

1. `output/heartbeat/heartbeat-status.json`
2. `output/heartbeat/heartbeat-status.md`
3. optional `output/heartbeat/heartbeat-issues.json`
4. derived repeated-run state in `output/heartbeat/heartbeat-state.json`

Heartbeat artifacts are derived evidence. They summarize source posture and preserve exact source
identifiers, but they do not replace GitHub Actions, PR state, local automation ledgers, mesh
certification artifacts, wiki source, or `lotus-ai` runtime APIs as source truth.

RFC-0096 delegated-task posture is represented through the `delegated_task_ledger` source system
when a caller explicitly enables it and provides a governed delegated-task ledger artifact. The
heartbeat reads task-ledger truth only; it does not infer hidden agent state or replace main-agent
review.

Suppression policy lives in `heartbeat-suppressions.json`. Suppressions are explicit metadata for
temporary non-blocking attention items; they do not remove evidence from heartbeat output and cannot
hide blocking findings.

Validate examples and future artifacts with:

```powershell
python automation/validate_heartbeat_contracts.py
```

The validator also certifies `automation/heartbeat-config.json` and
`heartbeat-suppressions.json`, so runner mode, mutation policy, governed source names, thresholds,
and suppression expiry shape stay under the platform repo check lane.
