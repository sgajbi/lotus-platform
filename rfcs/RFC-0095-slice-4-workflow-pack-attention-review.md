# RFC-0095 Slice 4 Review: Workflow-Pack Attention Inputs

Date: 2026-04-21

Branch: `feature/rfc0095-heartbeat-monitoring`

## Implemented

1. Added a `lotus_ai` heartbeat adapter for bounded workflow-pack runtime-status evidence.
2. Added config support for `source_config.lotus_ai.runtime_status_path`.
3. Added focused tests for:
   - workflow-pack attention queue backlog,
   - action-required run counts,
   - failed run counts,
   - stale `AWAITING_REVIEW` queue items,
   - terminal `FAILED` runtime items,
   - superseded lineage that is not marked `HISTORICAL`,
   - degraded run-ledger readiness summaries.

## Source Truth Review

1. `lotus-ai` remains the workflow-pack runtime and run-ledger source of truth.
2. The heartbeat adapter consumes a bounded runtime-status artifact/API capture and does not read
   gateway or Workbench as ledger truth.
3. Gateway and Workbench are not used to infer run state, review state, lineage, or supportability.
4. The adapter preserves `run_id`, `workflow_pack_id`, and `workflow_authority_owner` in attention
   output when the source artifact provides them.

## Review Findings

1. Runtime state and review state remain separate in adapter logic.
2. `supportability_status=ACTION_REQUIRED` does not get collapsed into runtime failure.
3. Superseded or revised lineage is only treated as a conflict when source supportability does not
   report `HISTORICAL`.
4. Degraded/unready run-ledger posture is detected from source status summaries rather than from a
   fabricated platform readiness state.
5. The adapter is intentionally not enabled by default; platform does not own live `lotus-ai`
   workflow-pack runtime truth.

## Complexity Decisions

1. Kept the `lotus_ai` adapter in `heartbeat_sources.py` with other artifact adapters. The module is
   now the source-adapter boundary; splitting per source is deferred until Slice 6 only if review
   finds that testability or readability has degraded.
2. Did not introduce a live HTTP client in platform heartbeat. A governed runtime-status artifact or
   API capture is the boundary for this slice, keeping the first implementation deterministic and
   safe for GitHub runners.
3. Did not enable `lotus_ai` in default config because missing sibling runtime evidence would create
   noisy local attention unrelated to the platform repo itself.

## Validation

Focused proof:

```powershell
python -m pytest tests\unit\test_heartbeat_runner.py -q
python -m ruff check automation\heartbeat_sources.py tests\unit\test_heartbeat_runner.py
```

Result:

1. `14 passed` for heartbeat runner and adapter tests.
2. Ruff passed for touched workflow-pack adapter code and tests.

## Remaining RFC Gaps

1. Slice 5 must implement repeated-run deduplication and suppression persistence.
2. Slice 6 must review adapter modularity, API-certification posture, governance coverage, and
   whether heartbeat should remain advisory.
3. Slice 7 must complete docs, context, wiki, skills, PR, CI, merge, and branch hygiene.
