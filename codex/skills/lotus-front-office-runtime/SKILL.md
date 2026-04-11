---
name: lotus-front-office-runtime
description: "Use when a Lotus task is about the governed front-office runtime, canonical Workbench demo bring-up, populated Workbench panels, demo screenshots, `PB_SG_GLOBAL_BAL_001`, `lotus-risk-module-shots`, or proving UI support with machine-readable evidence. Route these tasks to the governed Workbench runtime and canonical validation flow rather than generic platform QA or stale stack paths."
---

# Lotus Front-Office Runtime

Use this skill when the task is about governed front-office runtime proof, not generic backend QA.

The governed source of truth is:

1. `lotus-workbench/docs/operations/canonical-front-office-local-runtime.md`
2. `lotus-platform/automation/Invoke-Canonical-FrontOffice-QA.ps1`
3. `lotus-platform/context/contracts/canonical-front-office-demo-data-contract.json`
4. `lotus-platform/context/contracts/workbench-panel-registry.json`

## Route Here First

Use this skill when the request includes concepts such as:

1. `PB_SG_GLOBAL_BAL_001`
2. populated Workbench panels
3. canonical UI proof
4. demo screenshots
5. `lotus-risk-module-shots`
6. "all panels loaded"
7. "bring up all UI-related stack"
8. screenshot evidence for the front-office runtime

Do not route those tasks through generic platform QA by default.

## Operating Rules

1. Use the governed Workbench-owned runtime path, not stale ad hoc platform-stack assumptions.
2. Validate before claiming success.
3. Treat screenshots as evidence only when paired with machine-readable validation output.
4. Use the canonical seeded portfolio `PB_SG_GLOBAL_BAL_001`.
5. Use the canonical benchmark `BMK_PB_GLOBAL_BALANCED_60_40`.
6. Surface `ready`, `partial`, `empty`, `unavailable`, and `error` truthfully.
7. Do not use timestamped smoke portfolios when the canonical dataset is required.
8. Prefer targeted local checks and let GitHub run heavyweight CI asynchronously when appropriate.

## Canonical Commands

From `lotus-workbench`:

```powershell
npm run live:stack:up
npm run live:validate
npm run live:stack:down
```

From `lotus-platform`:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp
```

To write a screenshot pack to a caller-provided directory:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 `
  -ScreenshotDirectory <target-directory>
```

## Required Evidence

Require all of:

1. screenshot artifacts,
2. `live-validation-summary.json`,
3. `SHOT-INDEX.md`,
4. truthful panel classifications and calculation checks.

Do not accept screenshot-only proof.

## Boundary Rule

Use `lotus-qa-platform-validator` for backend or infrastructure QA that does not require populated
front-office product surfaces.

Use `lotus-pr-premerge-gate` once the work moves into PR verification and merge hygiene.
