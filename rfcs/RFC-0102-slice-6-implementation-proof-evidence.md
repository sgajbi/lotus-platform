# RFC-0102 Slice 6 Implementation Proof Evidence

- RFC: `RFC-0102-render-package-template-registry-and-render-service.md`
- Date: `2026-04-23`
- Repositories:
  - `lotus-render`
  - `lotus-report`
- Clean evidence directory:
  - `<workspace-root>/lotus-report/output/rfc-0102-live-evidence-20260423-155229`

## What Was Run

In `lotus-report`:

```powershell
python -m ruff check scripts/rfc_0102_proof_app.py scripts/rfc_0102_live_evidence.py
python scripts/rfc_0102_live_evidence.py
```

The proof runner started live `lotus-render` and proof-only live `lotus-report` processes, executed
positive and negative scenarios over HTTP, captured request and response artifacts, and wrote a
clean evidence pack.

## Clean Proof Coverage

The evidence directory contains:

1. direct `lotus-render` render request and response,
2. direct render status and artifact-metadata responses,
3. repeat-render proof in a fresh runtime and store envelope,
4. template-registry validation evidence,
5. package-validation failure evidence,
6. render-engine failure evidence,
7. exact `lotus-report` -> `lotus-render` render package and render response capture,
8. positive report-job status, events, snapshot, and lineage evidence,
9. negative report-job failure evidence,
10. runtime process logs,
11. `AUDIT-SUMMARY.md` and `README.md`.

## Critical Findings

1. The first-wave live proof is clean and sufficient for the current supported scope.
2. `lotus-render` behaves correctly for supported, invalid-package, and engine-unavailable paths.
3. `lotus-report` truthfully captures snapshot and lineage, assembles a governed render package,
   submits it to `lotus-render`, and persists render outcome metadata on the report job.
4. Archive retrieval, retention, replay, rerender, regenerate, and document distribution are not
   implied by the APIs or the evidence pack.

## Determinism Finding

The proof corrected one important assumption:

1. raw PDF bytes did not remain identical across renders or against the committed golden artifact,
2. the bounded determinism fingerprint remained stable,
3. the byte drift is explained by reminted PDF document ids and creation timestamps.

Therefore the supported RFC-0102 determinism claim is:

- bounded runtime-envelope determinism via `bounded_determinism_fingerprint`,
- not byte-for-byte stable PDF output.

## Acceptance Posture

Slice 6 is satisfied for the current implementation because:

1. one clean evidence pack exists,
2. positive and negative render behavior is proven,
3. hash, status, and artifact-metadata responses agree per concrete artifact,
4. the prior determinism overstatement was corrected and explained explicitly.
