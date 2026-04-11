# RFC-0078 Slice 3 Calculation Sanity Evidence

- RFC: `RFC-0078-modular-front-office-validation-framework.md`
- Slice: `Slice 3: Extract Calculation Sanity Modules`
- Date: 2026-04-11

## Summary

Slice 3 extracts the performance and risk calculation sanity checks from the canonical live
validator into a dedicated business-validation module. These checks remain domain-specific and
continue to control panel classification outcomes, but they no longer live inline with transport,
browser, and artifact orchestration logic.

Artifacts added or updated in this slice:

1. `lotus-workbench/scripts/live/validation/calculation-sanity.mjs`
2. `lotus-workbench/scripts/live/validate-canonical-workbench-live.mjs`
3. `lotus-workbench/tests/unit/live-validation-calculation-sanity.test.ts`
4. `lotus-workbench/tests/unit/live-canonical-validation-script.test.ts`
5. `rfcs/RFC-0078-slice-3-calculation-sanity-evidence.md`

## What Was Improved

This slice removes inline business validation for:

1. performance return reconciliation,
2. contribution-total reconciliation,
3. attribution fallback semantics,
4. risk observation-count and benchmark-alignment checks,
5. concentration, drawdown, rolling-risk, and historical-attribution sanity checks.

The extracted module still writes to the shared summary and panel-classification flow, but the
reconciliation logic is now grouped by business concern instead of buried inside the main script.

## Dead Code and Complexity Review

The accepted module boundary is deliberate:

1. `assertFiniteNumber`, `assertNumberInRange`, `assertArrayHasLength`, and calculation-check
   recording moved with the calculation logic because they are only meaningful in that context,
2. panel-classification registration remains callback-driven so registry governance stays owned by
   the main validator,
3. supportability alignment and browser assertions were not moved in this slice because they are
   different concerns,
4. duplicated inline calculation helpers were removed from the monolithic validator rather than
   mirrored in both places.

## Validation

Targeted workbench tests passed:

1. `npm test -- --runInBand tests/unit/live-canonical-validation-script.test.ts tests/unit/live-validation-contract-modules.test.ts tests/unit/live-validation-probes.test.ts tests/unit/live-validation-calculation-sanity.test.ts`

Those tests prove:

1. reconciled performance payloads are accepted and produce governed panel classifications,
2. attribution fallback drift fails with a high-signal business error,
3. ready risk payloads are accepted and classify all required risk panels,
4. historical risk attribution residual breaches fail explicitly.

## Review Notes

Conscious decisions:

1. the calculation module remains business-specific rather than becoming a generic math helper,
2. no documentation changes were made in this slice because operator workflow remains stable,
3. no skill changes were made in this slice because future-agent routing still uses the same
   governed runtime and RFC path.
