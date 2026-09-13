# Canonical Runtime Reservation Control

This control governs a bounded canonical front-office window. It does not grant
authority over a running Docker resource merely because an operator has been
nominated as the window holder.

## Reservation record

Before a holder starts, stops, rebuilds, seeds, or cleans anything, record on
the coordinating issue:

- holder and teardown owner;
- bounded purpose, UTC start and expiry;
- the exact canonical Compose projects and host ports requested;
- the pinned repository revisions and image identities when they are known;
- the acquisition, preflight, and final release/teardown receipts.

`C6-X05` currently uses this record on Platform #849. The approved holder is
not a substitute for an ownership handover from an existing project.

## Acquire and preflight

Run the read-only Workbench-owned port control from `lotus-workbench` before
any runtime mutation:

```powershell
npm run live:stack:preflight
```

It checks the complete canonical port plan and Docker Compose working-directory
labels. A successful result is the acquisition precondition; a failed result is
a refusal, not a partial acquisition. In particular, an incidental unit or
integration-test container is neither a canonical resource nor an object the
holder may remove. A canonical-named project from another checkout is foreign
until its owner records an exact handover or teardown receipt.

For cleanup planning, use the Platform wrapper's read-only mode first:

```powershell
Set-Location "$env:LOTUS_WORKSPACE_ROOT/lotus-platform"
powershell -NoProfile -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -CleanPlanOnly
```

```bash
cd "$LOTUS_WORKSPACE_ROOT/lotus-platform"
pwsh -NoProfile -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -CleanPlanOnly
```

Review `output/front-office-qa/cleanup-plan-latest.json`. Do not replace this
with a Docker name-prefix match, daemon-wide prune, or manually stopping an
unlabelled resource.

## Release

Only the recorded holder releases resources acquired for that same window.
Run the Workbench teardown and the Platform wrapper's strict cleanup-plan
review, then attach the final owned-resource and validation evidence to the
reservation. A failed or interrupted release remains an open operational
receipt; it is never represented as a successful Cycle 6 runtime acceptance.

Level A consumer receipts and Level B canonical acceptance remain distinct.
CI, source provenance, and a passing preflight do not certify either one.
