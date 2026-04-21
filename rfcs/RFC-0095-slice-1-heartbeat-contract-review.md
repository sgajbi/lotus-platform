# RFC-0095 Slice 1 Review: Heartbeat Contract And Attention Schema

- Date: 2026-04-21
- Branch: `feature/rfc0095-heartbeat-monitoring`
- Slice: Heartbeat contract and attention schema
- Status: Complete

## Implemented

1. Added `platform-contracts/heartbeat/heartbeat-status.schema.json`.
2. Added first-wave examples for healthy, warning, action-required, blocking, suppressed, and
   degraded-source heartbeat artifacts.
3. Added `automation/validate_heartbeat_contracts.py`.
4. Added `tests/unit/test_heartbeat_contracts.py`.
5. Wired the heartbeat validator into `automation/Invoke-PlatformRepoChecks.ps1`.
6. Updated automation documentation and directory map.

## Review Findings

1. The schema does not duplicate RFC-0094 task-ledger identity fields. It references heartbeat
   posture, source inventory, source read errors, attention items, evidence refs, and suppression
   decisions.
2. `HEARTBEAT_MONITOR` was not added to the RFC-0094 task kind vocabulary in this slice. The first
   implementation remains compatible with `VALIDATION_RUN`; adding a new task kind stays an open
   implementation decision until runner behavior proves it is necessary.
3. Missing source evidence is explicitly non-healthy. The validator rejects missing or errored
   source evidence when it does not produce an attention item.
4. Blocking attention items cannot be suppressed.
5. Summary counts are validator-protected so operator output cannot drift from item severity.
6. Example artifacts preserve exact source refs such as PR identity, wiki check command, mesh
   artifact path, and local background-run ledger path.

## Simplification Decisions

1. No JSON Schema dependency was added. A small repo-native Python validator is enough for the
   current contract and keeps the platform check lane lightweight.
2. The heartbeat contract lives in a dedicated `platform-contracts/heartbeat/` directory instead of
   being folded into RFC-0094 task-ledger contracts. Heartbeat artifacts are derived evidence, not
   task-ledger source truth.
3. The first slice does not create a runner or source adapters. Those belong to later slices after
   the artifact contract is stable.

## Validation

1. `python -m pytest tests\unit\test_heartbeat_contracts.py -q`
2. `python automation\validate_heartbeat_contracts.py`
3. `git diff --check`
