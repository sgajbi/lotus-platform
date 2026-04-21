# RFC-0095 Slice 5 Review: Operator Output, Deduplication, And Suppression

Date: 2026-04-21

Branch: `feature/rfc0095-heartbeat-monitoring`

## Implemented

1. Added `automation/heartbeat_state.py` for repeated-run attention state and suppression
   application.
2. Added default governed suppression policy at
   `platform-contracts/heartbeat/heartbeat-suppressions.json`.
3. Added config keys:
   - `state_path`
   - `suppression_file_path`
4. Updated Markdown output to show explicit suppression posture per attention item.
5. Added tests for first-seen preservation, active non-blocking suppression, and blocking
   suppression rejection.

## Review Findings

1. Deduplication uses the existing stable `deduplication_key`; no random identity is introduced.
2. `first_seen_at_utc` is preserved from prior state while `last_seen_at_utc` reflects the current
   heartbeat run.
3. Suppressed items remain in `attention_items`; suppression is metadata, not deletion.
4. Suppression decisions are emitted in `suppression_decisions` with owner, reason, expiry, and
   deduplication key.
5. Blocking items ignore matching suppression rules, preserving the Slice 1 contract invariant.
6. The state file is derived output under `output/heartbeat/`; suppression policy is governed input
   under `platform-contracts/heartbeat/`.

## Complexity Decisions

1. Kept repeated-run state in a small separate module rather than expanding source adapters or the
   runner.
2. Did not add a database or durable service for heartbeat state. A deterministic JSON file is
   enough for first-wave local/GitHub evidence and can be replaced later without changing source
   adapter contracts.
3. Did not filter suppressed items out of summaries. Operators should see that evidence exists and
   why it is temporarily suppressed.

## Validation

Focused proof:

```powershell
python -m pytest tests\unit\test_heartbeat_runner.py -q
python -m ruff check automation\run_heartbeat.py automation\heartbeat_sources.py automation\heartbeat_state.py tests\unit\test_heartbeat_runner.py
powershell -ExecutionPolicy Bypass -File automation\Run-Heartbeat.ps1 -GeneratedAtUtc 2026-04-21T00:00:00Z -Branch feature/rfc0095-heartbeat-monitoring
```

Result:

1. `17 passed` for heartbeat runner, source adapter, and state tests.
2. Ruff passed.
3. The PowerShell wrapper wrote valid heartbeat status, report, issues, and state artifacts.

## Remaining RFC Gaps

1. Slice 6 must complete code review, API-certification, and governance tightening.
2. Slice 7 must complete docs, context, wiki, skills, PR, CI, merge, and branch hygiene.
