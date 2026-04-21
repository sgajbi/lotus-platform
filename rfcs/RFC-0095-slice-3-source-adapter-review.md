# RFC-0095 Slice 3 Review: First-Wave Source Adapters

Date: 2026-04-21

Branch: `feature/rfc0095-heartbeat-monitoring`

## Implemented

1. Added first-wave heartbeat adapters in `automation/heartbeat_sources.py` for:
   - `github`
   - `background_run_ledger`
   - `wiki_publication`
   - `agent_context`
   - `mesh_certification`
2. Updated `automation/heartbeat-config.json` so the default heartbeat remains read-only and uses
   only local artifact-backed checks that do not require credentials or sibling checkouts.
3. Added focused tests for failing/stale PR evidence, lost/stale background runs, wiki publication
   drift, context validation errors, and stale/blocked mesh operating posture.
4. Preserved source truth by reading existing evidence artifacts rather than reimplementing
   mutation or source polling inside heartbeat.

## Source Truth Review

1. GitHub adapter reads `output/pr-monitor.json`; GitHub and `PR-Monitor.ps1` remain the source
   truth for PR/check status.
2. Background-run adapter reads `output/background-runs.json`; RFC-0094 local automation remains
   the source truth for detached run lifecycle.
3. Wiki adapter reads an explicit wiki-sync status artifact; `Sync-RepoWikis.ps1` and repo-authored
   `wiki/` remain the source truth for publication posture.
4. Agent-context adapter reads `output/engineering-context-system-validation.json`; the context
   validator remains the source truth for context health.
5. Mesh adapter reads `output/mesh-certification/enterprise-mesh-operating-report.json`; enterprise
   mesh certification remains the source truth for mesh operating posture.

## Review Findings

1. Missing artifacts are never treated as healthy. They produce `source_evidence_missing`
   `action_required` items and source-read errors.
2. Malformed source JSON is handled as `source_evidence_malformed`, preserving evidence path and
   avoiding partial parsing.
3. Stable item identity keeps `attention_item_id` distinct from `deduplication_key`, matching the
   heartbeat contract.
4. Default adapter enablement intentionally excludes GitHub and wiki checks until their upstream
   evidence artifacts are explicitly generated.
5. No source adapter mutates GitHub, wiki, runtime APIs, mesh artifacts, or context files.

## Complexity Decisions

1. Split source adapters into `automation/heartbeat_sources.py` after review showed the runner was
   becoming too broad. `automation/run_heartbeat.py` now stays focused on config loading,
   task-ledger metadata, artifact writing, and Markdown rendering.
2. Did not make heartbeat invoke `PR-Monitor.ps1` or `Sync-RepoWikis.ps1`; heartbeat consumes their
   evidence and reports missing evidence truthfully. This avoids hidden network or publication
   behavior inside the artifact renderer.
3. Did not enable GitHub/wiki adapters by default. That would create noisy local failures when
   upstream evidence has not been generated.

## Validation

Focused proof:

```powershell
python -m pytest tests\unit\test_heartbeat_runner.py -q
python -m ruff check automation\run_heartbeat.py automation\heartbeat_sources.py tests\unit\test_heartbeat_runner.py
powershell -ExecutionPolicy Bypass -File automation\Run-Heartbeat.ps1 -GeneratedAtUtc 2026-04-21T00:00:00Z -Branch feature/rfc0095-heartbeat-monitoring
```

Observed default heartbeat output:

1. `run_status`: `healthy`
2. `source_inventory`:
   - `agent_context:healthy`
   - `background_run_ledger:healthy`
   - `mesh_certification:healthy`
3. Contract validation for the generated artifact returned no errors.

## Remaining RFC Gaps

1. Slice 4 must add workflow-pack attention inputs without redefining `lotus-ai` runtime truth.
2. Slice 5 must implement repeated-run deduplication and suppression persistence.
3. Slice 6 must review adapter modularity, API-certification posture, governance coverage, and
   whether heartbeat should remain advisory.
4. Slice 7 must complete docs, context, wiki, skills, PR, CI, merge, and branch hygiene.
