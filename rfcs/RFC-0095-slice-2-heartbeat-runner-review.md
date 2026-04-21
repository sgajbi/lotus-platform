# RFC-0095 Slice 2 Review: Platform Heartbeat Runner

Date: 2026-04-21

Branch: `feature/rfc0095-heartbeat-monitoring`

## Implemented

1. Added `automation/run_heartbeat.py` as the single read-only heartbeat artifact generator.
2. Added `automation/Run-Heartbeat.ps1` as the repo-native PowerShell entrypoint.
3. Added `automation/heartbeat-config.json` with advisory, read-only defaults and no enabled source
   adapters.
4. Added focused runner tests for empty-state output, RFC-0094-compatible task metadata,
   configured-source degradation, unknown source rejection, and UTC timestamp validation.
5. Updated automation docs and the RFC implementation evidence.

## Review Findings

1. Deterministic paths: output filenames are stable and match the heartbeat contract.
2. Source truth: the runner emits derived evidence only and does not mutate GitHub, wiki,
   workflow-pack, mesh, or context sources.
3. Adapter truthfulness: configured source systems without implemented adapters become
   `action_required` findings, not healthy posture.
4. Task-ledger compatibility: emitted metadata uses `VALIDATION_RUN`, stable task identity, terminal
   `SUCCEEDED` status for a completed artifact generation run, and `NOT_REQUIRED` cleanup posture.
5. Portability improvement made during review: task-ledger artifact refs are repo-relative when
   generated inside `lotus-platform`, and evidence refs include the RFC-0094-style `path` field.
6. Contract hardening made during review: caller-supplied generation timestamps must end in `Z` so
   deterministic runs cannot emit artifacts that fail the heartbeat contract.

## Complexity Decisions

1. Did not introduce a new `HEARTBEAT_MONITOR` task kind; `VALIDATION_RUN` is sufficient until
   operational evidence proves otherwise.
2. Did not build first-wave source adapters in this slice. The runner now provides a tested
   adapter seam and truthful degraded posture for configured sources, so Slice 3 can add adapters
   without changing artifact rendering.
3. Did not add persistence for first-seen/last-seen yet. That belongs with Slice 5 deduplication and
   suppression so repeated-run behavior is implemented coherently.

## Validation

Focused proof:

```powershell
python -m pytest tests\unit\test_heartbeat_contracts.py tests\unit\test_heartbeat_runner.py -q
powershell -ExecutionPolicy Bypass -File automation\Run-Heartbeat.ps1 -GeneratedAtUtc 2026-04-21T00:00:00Z -Branch feature/rfc0095-heartbeat-monitoring
python automation\validate_heartbeat_contracts.py
```

Result:

1. `21 passed` for the heartbeat contract, runner, and RFC closure governance tests.
2. The PowerShell wrapper wrote `output/heartbeat/heartbeat-status.json`,
   `output/heartbeat/heartbeat-status.md`, and `output/heartbeat/heartbeat-issues.json`.
3. Contract validation passed.

## Remaining RFC Gaps

1. Slice 3 must implement first-wave source adapters.
2. Slice 4 must consume workflow-pack run/review/supportability posture without redefining
   `lotus-ai` truth.
3. Slice 5 must implement deduplication and suppression persistence.
4. Slice 6 must perform final code/governance/API-certification tightening.
5. Slice 7 must complete docs, context, wiki, skills, PR, CI, merge, and branch hygiene.
