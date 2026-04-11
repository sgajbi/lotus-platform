# RFC-0078 Slice 1 Contract Layer Evidence

- RFC: `RFC-0078-modular-front-office-validation-framework.md`
- Slice: `Slice 1: Extract Core Validation Types and Result Models`
- Date: 2026-04-11

## Summary

Slice 1 extracts the low-churn bootstrap layer from the canonical live validator without changing
operator entrypoints or browser validation behavior. The goal is to remove duplicated bootstrap
logic first so later slices can isolate probe, calculation, browser, and panel-classification
behavior without continuing to grow a monolithic script.

Artifacts added or updated in this slice:

1. `lotus-workbench/scripts/live/validation/args.mjs`
2. `lotus-workbench/scripts/live/validation/contract-metadata.mjs`
3. `lotus-workbench/scripts/live/validation/evidence-summary-writer.mjs`
4. `lotus-workbench/scripts/live/validate-canonical-workbench-live.mjs`
5. `lotus-workbench/tests/unit/live-validation-contract-modules.test.ts`
6. `lotus-workbench/tests/unit/live-canonical-validation-script.test.ts`
7. `rfcs/RFC-0078-implementation-checklist.md`

## What Was Improved

This slice removes duplicate local implementations for:

1. CLI argument parsing,
2. governed canonical contract loading,
3. governed panel registry loading,
4. output directory and artifact path construction,
5. summary and screenshot index writing.

The monolithic validator now consumes those shared modules rather than owning them directly. This
reduces drift risk for later slices and makes the RFC-0076 and RFC-0077 contract surfaces reusable
from a stable module boundary.

## Dead Code and Complexity Review

The slice was reviewed specifically for "extraction that only relocates complexity". The accepted
outcome is:

1. duplicated bootstrap helpers were removed from the monolithic validator,
2. operator command surfaces were intentionally left unchanged,
3. no probe, calculation, or browser logic was moved prematurely,
4. no new wrapper layer was introduced around the validator entrypoint.

This is the minimal extraction that materially improves maintainability without creating a partial
abstraction that future slices would need to unwind.

## Validation

Targeted workbench tests passed:

1. `npm test -- --runInBand tests/unit/live-canonical-validation-script.test.ts tests/unit/live-validation-contract-modules.test.ts`

Those tests prove:

1. the live validator now imports the extracted modules,
2. governed contract and panel registry metadata remain available,
3. summary artifacts and screenshot index output remain stable,
4. CLI defaults and URL normalization remain deterministic.

## Review Notes

Conscious decisions:

1. contract metadata and evidence writing were separated into distinct modules because they evolve
   for different reasons,
2. no documentation changes were made in this slice because the operator workflow did not change,
3. no skill changes were made in this slice because future-agent routing is unaffected until later
   slices change validator composition materially.
