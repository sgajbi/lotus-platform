# RFC-0095 Slice 6 Review: Code, Certification, And Governance Tightening

Date: 2026-04-21

Branch: `feature/rfc0095-heartbeat-monitoring`

## Review Scope

Reviewed:

1. `automation/run_heartbeat.py`
2. `automation/heartbeat_sources.py`
3. `automation/heartbeat_state.py`
4. `automation/validate_heartbeat_contracts.py`
5. `automation/heartbeat-config.json`
6. `platform-contracts/heartbeat/`
7. heartbeat tests and RFC slice evidence

## Findings And Fixes

1. Finding: heartbeat status schema and examples were certified, but runner config and suppression
   policy were not.
   Fix: `automation/validate_heartbeat_contracts.py` now validates
   `automation/heartbeat-config.json` and
   `platform-contracts/heartbeat/heartbeat-suppressions.json`.
2. Finding: invalid enabled source names or source-config keys could drift outside the governed
   source vocabulary.
   Fix: config validation rejects unknown source systems.
3. Finding: suppression expiry shape needed direct governance coverage.
   Fix: suppression validation requires owner, reason, deduplication key, and UTC `Z` expiry.

## Certification Decision

Heartbeat currently introduces machine-readable local artifacts, not a served API endpoint.

Decision:

1. API/OpenAPI certification is not applicable inside `lotus-platform` for this slice.
2. Artifact certification is applicable and now covered by the heartbeat validator and platform
   feature lane.
3. If heartbeat output is later exposed through `lotus-gateway`, that endpoint must use the Lotus
   endpoint certification pattern before any UI or operator surface treats it as a supported API.

## Governance Decision

Heartbeat output remains advisory-only.

Rationale:

1. The validator should be gate-covered because schema/config/policy drift is deterministic.
2. Generated heartbeat status should not become PR-blocking yet because source evidence freshness
   depends on upstream automation cadence and would be noisy before multiple operating runs prove
   signal quality.
3. Slice 7 should document the advisory posture in context/skills guidance rather than turning the
   heartbeat into a merge gate prematurely.

## Complexity Review

Current module boundaries:

1. `run_heartbeat.py`: CLI, config orchestration, task-ledger metadata, artifact writing, Markdown.
2. `heartbeat_sources.py`: source adapters and source evidence normalization.
3. `heartbeat_state.py`: repeated-run state and suppression application.

Decision:

This is clean enough for the RFC-0095 first wave. Splitting every source adapter into separate files
would add import churn without improving tests or ownership yet. Revisit if a second wave adds live
HTTP clients or product-facing notifications.

## Validation

Focused proof:

```powershell
python -m pytest tests\unit\test_heartbeat_contracts.py tests\unit\test_heartbeat_runner.py -q
python -m ruff check automation\run_heartbeat.py automation\heartbeat_sources.py automation\heartbeat_state.py automation\validate_heartbeat_contracts.py tests\unit\test_heartbeat_contracts.py tests\unit\test_heartbeat_runner.py
python automation\validate_heartbeat_contracts.py
```

Expected platform proof before commit:

```powershell
powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane feature
```

## Remaining RFC Gaps

1. Slice 7 must complete docs, context, wiki, skills, PR, CI, merge, and branch hygiene.
2. Slice 7 must consciously decide whether future agent skill guidance should add heartbeat
   operation to `platform-automation-ops`, `platform-pulse-monitor`, both, or neither.
