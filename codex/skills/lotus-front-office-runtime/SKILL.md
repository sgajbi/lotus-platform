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
9. Before accepting live canonical evidence after code, route, BFF, panel, Dockerfile, or seed-data
   changes, rebuild or targeted-refresh the impacted service images. Treat route 404s, missing UI
   fields, or absent seeded entities from stale containers as diagnostic failures, not proof.
10. If a validated panel depends on a newly implemented business entity, seed or generate a real
    implementation-backed entity first and record the generation evidence path. Do not accept an
    empty panel as proof for a feature whose business outcome requires populated data.
11. Treat `lotus-idea` as part of the default canonical platform QA runtime. Do not reintroduce an
    opt-in flag, skip readiness checks, or leave its app-local compose stack running after QA unless
    the user explicitly requested a diagnostic partial run.
12. Keep the canonical private-banking seed separate from demo-pack content. The governed PB seed
    should remain contract-backed and `DEMO_DATA_PACK_ENABLED=false` by default.
13. When a canonical proof depends on source-owned health or supportability context, verify the
   final persisted service read after all seed steps. Monitoring or batch jobs can overwrite a
   deterministic snapshot created earlier in the seed flow; do not accept the immediate write
   response as proof if a later step recalculates the same entity.
14. Treat each application repository's standalone runtime as the owned composition contract.
   Workbench may orchestrate that contract but must not inject an application's missing database,
   migration, or durability behavior. Before accepting a newly database-backed app in canonical
   startup, prove standalone first start, repeated start, API restart, and persisted readback using
   the app-owned Compose path; then run canonical validation against that same path.
15. Before canonical cleanup, run the platform wrapper with `-CleanPlanOnly` and review
    `output/front-office-qa/cleanup-plan-latest.json`. Cleanup ownership requires the exact
    canonical Compose project plus repository working-directory provenance; never use broad
    Lotus/PBWM/performance name prefixes, daemon-wide prune, or another project's resources. A
    concurrent certification project remains independently owned even when it uses the same repo.
    Treat a reused project name with a different working directory, or residual volumes/images with
    no live container proving the expected checkout, as a blocking ownership conflict.

## Canonical Commands

From `lotus-workbench`:

```powershell
npm run live:stack:up
npm run live:validate
npm run live:stack:down
```

When the audit or implementation changed one or more runtime services, prefer the Workbench
start script option or targeted Docker rebuild before validation:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/live/Start-LotusFrontOfficeCanonical.ps1 `
  -BuildImages -RunValidation -ScreenshotDirectory <target-directory>
```

If a full Workbench bring-up is already running, rebuild only the impacted owning service where
possible, then rerun `npm run live:validate` or `scripts/live/Validate-LotusFrontOfficeCanonical.ps1`.

From `lotus-platform`:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp
```

This wrapper includes `lotus-idea` readiness and teardown evidence by default.

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
## Continuous Skill Improvement

At the end of any meaningful use of this skill, decide whether the work exposed a repeatable failure
mode, missing step, weak trigger, validation gap, or context-routing gap. If yes, update the
platform-owned skill source under `lotus-platform/codex/skills/<skill-name>` or its relevant
reference/script in the same delivery slice when the improvement is small and safe. For broader
learning, create a focused follow-up issue or PR instead of relying on chat memory.

Use this decision order:

1. tighten this skill when future agents need different behavior;
2. update `context/LOTUS-SKILL-ROUTING-MAP.md` when routing or overlap changed;
3. update central or repo-local context when source-of-truth changed;
4. add or adjust validators, scaffolds, or gates when deterministic enforcement is better than prose;
5. record an explicit no-change decision in PR evidence, the review ledger, or the task ledger when no durable update is justified.


