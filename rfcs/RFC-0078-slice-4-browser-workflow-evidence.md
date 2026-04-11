# RFC-0078 Slice 4 Browser Workflow Evidence

- RFC: `RFC-0078-modular-front-office-validation-framework.md`
- Slice: `Slice 4: Extract Browser Workflow and Screenshot Capture`
- Date: 2026-04-11

## Summary

Slice 4 extracts the Playwright workflow and governed screenshot capture behavior from the canonical
live validator. The validator still orchestrates backend readiness and registry supportability, but
browser navigation, panel-level assertions, route transitions, and screenshot capture now live in a
dedicated browser workflow module.

Artifacts added or updated in this slice:

1. `lotus-workbench/scripts/live/validation/browser-workflows.mjs`
2. `lotus-workbench/scripts/live/validate-canonical-workbench-live.mjs`
3. `lotus-workbench/tests/unit/live-validation-browser-workflows.test.ts`
4. `lotus-workbench/tests/unit/live-canonical-validation-script.test.ts`
5. `rfcs/RFC-0078-slice-4-browser-workflow-evidence.md`

## What Was Improved

This slice removes inline browser workflow duplication for:

1. portfolio summary and detailed route validation,
2. performance summary, analysis, advisor brief, risk, and evidence route validation,
3. screenshot path construction and screenshot evidence recording,
4. governed route resolution from the RFC-0077 panel registry.

The browser workflow module keeps the route-level behavior reusable without weakening the existing
proof model.

## Dead Code and Complexity Review

The accepted extraction boundary is:

1. screenshot path and metadata handling moved with the browser workflow because those semantics are
   tightly coupled to route validation,
2. supportability alignment and gateway readiness remain in the main validator because they are not
   browser concerns,
3. the browser helpers still mutate the shared summary directly because screenshot evidence and UI
   checks are first-class validator outputs,
4. inline screenshot and route-resolution helpers were removed from the monolithic validator.

This keeps slice 4 focused on UI orchestration instead of introducing a second evidence ownership
layer.

## Validation

Targeted workbench tests passed:

1. `npm test -- --runInBand tests/unit/live-canonical-validation-script.test.ts tests/unit/live-validation-contract-modules.test.ts tests/unit/live-validation-probes.test.ts tests/unit/live-validation-calculation-sanity.test.ts tests/unit/live-validation-browser-workflows.test.ts`

Those tests prove:

1. governed route templates still resolve correctly,
2. screenshot evidence still records registry-owned names, routes, absolute paths, and as-of dates,
3. the live validator still imports the browser workflow from a dedicated module,
4. screenshot behavior remains truthful for degraded evidence surfaces.

## Review Notes

Conscious decisions:

1. no operator documentation changes were made in this slice because `npm run live:validate` and
   the surrounding PowerShell workflow did not change,
2. no skill changes were made in this slice because future-agent routing still points to the same
   governed runtime and evidence path,
3. browser assertions remain panel-specific rather than abstracted into a generic scene model
   because the product surfaces are intentionally business-shaped.
