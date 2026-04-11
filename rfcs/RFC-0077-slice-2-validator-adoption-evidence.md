# RFC-0077 Slice 2 Evidence: Workbench Validator Adoption

- RFC: `RFC-0077-workbench-panel-registry-and-evidence-contract.md`
- Date: `2026-04-11`
- Scope:
  - `lotus-workbench`
  - `lotus-platform`

## What changed

Slice 2 moves the governed panel registry from documentation into runtime validation behavior.

Updated artifacts:

1. `lotus-workbench/scripts/live/validate-canonical-workbench-live.mjs`
2. `lotus-workbench/tests/unit/live-canonical-validation-script.test.ts`
3. `lotus-workbench/docs/operations/canonical-front-office-local-runtime.md`
4. `lotus-platform/rfcs/RFC-0077-implementation-checklist.md`
5. `lotus-platform/rfcs/RFC-0077-slice-2-validator-adoption-evidence.md`

## What improved

### Registry-backed panel classification

The live validator now loads `workbench-panel-registry.json` and validates:

1. the panel identifier exists in the governed registry,
2. the emitted panel state is allowed by that registry entry,
3. screenshot ownership resolves from registry metadata rather than duplicated inline strings.

This removes a meaningful class of drift where browser validation could silently invent or rename
panel identifiers without updating the contract.

### Dead metadata removed

The validator no longer relies on:

1. legacy risk panel identifiers such as `risk.snapshot`,
2. route-level screenshot metadata duplicated inline for governed panels,
3. the unused `assertRegionHasButtons` helper.

The remaining imperative browser navigation stays explicit because that logic is interaction flow,
not durable contract metadata.

### Risk route alignment

The validator now classifies the governed risk surface as:

1. `performance.risk.snapshot`
2. `performance.risk.drawdown`
3. `performance.risk.concentration`
4. `performance.risk.rolling`
5. `performance.risk.historical_attribution`

That aligns the runtime evidence with the registry introduced in Slice 1.

## Why this slice is in the right shape

This slice keeps a clean boundary:

1. the registry owns durable panel metadata,
2. the validator owns browser flow and runtime assertions,
3. the runbook owns operator guidance.

It does not overreach into a generic execution engine yet. That modularization belongs to the
future validation-framework RFC, not this slice.

## Verification

```text
npm test -- --runInBand tests/unit/live-canonical-validation-script.test.ts
8 passed
```

## Review outcome

Slice 2 is complete and materially better than the prior state. The validator is more governed,
has less duplicated panel metadata, and now records risk evidence using the canonical RFC-0077
panel vocabulary. The next slice should align registry support-state expectations with actual
gateway/runtime behavior, especially for intentionally partial surfaces.
