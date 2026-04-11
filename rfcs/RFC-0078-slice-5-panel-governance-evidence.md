# RFC-0078 Slice 5 Panel Governance Evidence

- RFC: `RFC-0078-modular-front-office-validation-framework.md`
- Slice: `Slice 5: Registry-Driven Panel Classification`
- Date: 2026-04-11

## Summary

Slice 5 extracts panel classification and supportability alignment into a dedicated governance
module. This makes the RFC-0077 panel registry rules explicit in one place and removes the last
substantial registry-enforcement block from the monolithic live validator.

Artifacts added or updated in this slice:

1. `lotus-workbench/scripts/live/validation/panel-governance.mjs`
2. `lotus-workbench/scripts/live/validate-canonical-workbench-live.mjs`
3. `lotus-workbench/tests/unit/live-validation-panel-governance.test.ts`
4. `lotus-workbench/tests/unit/live-canonical-validation-script.test.ts`
5. `rfcs/RFC-0078-slice-5-panel-governance-evidence.md`

## What Was Improved

This slice centralizes:

1. panel classification recording,
2. unsupported blank panel detection,
3. owner/state drift detection,
4. supportability evidence recording from the governed registry.

The validator now consumes a panel-governance module instead of re-implementing registry alignment
inline.

## Dead Code and Complexity Review

The accepted boundary is:

1. registry enforcement moved into a dedicated module because it is conceptually separate from
   backend probing, calculation sanity, and browser orchestration,
2. the module still writes to the shared summary because panel classifications and supportability
   checks are top-level validator outputs,
3. inline registry-enforcement helpers were removed from the monolithic validator,
4. no generic policy abstraction was introduced beyond the governed panel registry itself.

This keeps the logic explicit and readable while removing page-local policy drift.

## Validation

Targeted workbench tests passed:

1. `npm test -- --runInBand tests/unit/live-canonical-validation-script.test.ts tests/unit/live-validation-contract-modules.test.ts tests/unit/live-validation-probes.test.ts tests/unit/live-validation-calculation-sanity.test.ts tests/unit/live-validation-browser-workflows.test.ts tests/unit/live-validation-panel-governance.test.ts`

Those tests prove:

1. governed panel classifications are recorded and reflected into supportability checks,
2. unsupported blank panels fail explicitly,
3. owner drift against the registry fails explicitly,
4. the live validator still imports the panel-governance module instead of owning that logic
   directly.

## Review Notes

Conscious decisions:

1. no operator documentation changes were made in this slice because the runtime entrypoints and
   artifacts remain stable,
2. no skill changes were made in this slice because the governed runtime path is unchanged,
3. registry policy remains expressed by the existing RFC-0077 contract rather than a second policy
   document.
