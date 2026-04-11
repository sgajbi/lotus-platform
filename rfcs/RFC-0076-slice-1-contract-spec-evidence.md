# RFC-0076 Slice 1 Contract Spec Evidence

- RFC: `RFC-0076-canonical-front-office-demo-data-contract.md`
- Slice: `Slice 1: Contract Document and Machine-Readable Spec`
- Date: 2026-04-11

## Summary

Slice 1 establishes the governed contract surface for the canonical front-office dataset before any
cross-repository implementation changes are made. The goal of this slice is to lock the contract
shape, ownership model, and minimum invariants into durable artifacts that can be consumed by later
validation and implementation work.

Artifacts added in this slice:

1. `context/contracts/README.md`
2. `context/contracts/canonical-front-office-demo-data-contract.json`
3. `context/contracts/canonical-front-office-demo-data-invariants.json`
4. `rfcs/RFC-0076-implementation-checklist.md`

## Governed Contract Decisions Captured

This slice records the following governed decisions in machine-readable form:

1. canonical portfolio ID: `PB_SG_GLOBAL_BAL_001`,
2. canonical benchmark code: `BMK_PB_GLOBAL_BALANCED_60_40`,
3. canonical as-of date: `2026-04-10`,
4. warm-up start date: `2025-01-06`,
5. seed start date: `2025-03-31`,
6. projected-horizon end date: `2026-05-10`,
7. required asset coverage includes cash, equity, fixed income, fund, private credit, and
   multi-currency exposure,
8. required transaction coverage includes funding, buy, sell, income, fee, withdrawal,
   FX-sensitive cash movement, and projected cashflow,
9. required derived state includes positions, valuations, timeseries, performance, and risk
   readiness outputs,
10. repository ownership is explicitly allocated across platform, core, performance, risk, gateway,
    and workbench.

## Why This Slice Matters

Without a machine-readable contract, later slices would drift back into implementation-by-memory.
This slice ensures that future work has to satisfy a governed contract rather than reconstructing
the intended dataset shape from prose alone.

## Review Notes

The slice was reviewed for unnecessary complexity before acceptance.

Conscious decisions:

1. the contract is split into two JSON files rather than one overly large mixed document,
2. thresholds are represented as governed minimums where exact values may evolve in later slices,
3. no context or skill docs were changed in this slice because the contract is not yet adopted by
   runtime and onboarding flows,
4. no additional manifest wiring was added yet because that belongs to later cross-app adoption or
   final-slice work once the contract path stabilizes.

## Validation

Slice 1 is accepted when platform tests prove:

1. the contract artifacts exist,
2. the portfolio, benchmark, and governed date are stable,
3. required ownership and readiness fields are present,
4. the checklist records slice completion and later-slice boundaries correctly.
