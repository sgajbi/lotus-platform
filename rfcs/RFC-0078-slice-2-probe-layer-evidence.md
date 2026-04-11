# RFC-0078 Slice 2 Probe Layer Evidence

- RFC: `RFC-0078-modular-front-office-validation-framework.md`
- Slice: `Slice 2: Extract API Probing and Gateway Assertions`
- Date: 2026-04-11

## Summary

Slice 2 extracts the network probe layer from the canonical live validator. The validator still owns
the ordering of portfolio, performance, risk, manage, report, and gateway checks, but DNS and HTTP
probe behavior is now centralized behind a dedicated module that can be tested in isolation.

Artifacts added or updated in this slice:

1. `lotus-workbench/scripts/live/validation/probes.mjs`
2. `lotus-workbench/scripts/live/validate-canonical-workbench-live.mjs`
3. `lotus-workbench/tests/unit/live-validation-probes.test.ts`
4. `rfcs/RFC-0078-slice-2-probe-layer-evidence.md`

## What Was Improved

This slice removes duplicated monolithic implementations for:

1. required versus optional DNS checks,
2. JSON fetch timeout and parse handling,
3. text fetch timeout handling,
4. API summary evidence recording.

The extracted probe module keeps operator-facing failure messages stable while making the network
probe layer independently testable.

## Dead Code and Complexity Review

The slice was reviewed for shallow extraction and dead-code drift.

Accepted outcome:

1. `checkDns`, `fetchJson`, and `fetchText` no longer exist in the monolithic validator,
2. summary mutation remains explicit because the validator still owns evidence aggregation,
3. gateway payload assertions remain in the validator because they are business checks, not generic
   transport behavior,
4. no wrapper indirection was added around the probe helpers.

This keeps the transport boundary separate from business validation without prematurely fragmenting
the higher-level workflow.

## Validation

Targeted workbench tests passed:

1. `npm test -- --runInBand tests/unit/live-canonical-validation-script.test.ts tests/unit/live-validation-contract-modules.test.ts tests/unit/live-validation-probes.test.ts`

Those tests prove:

1. optional DNS failures are recorded without aborting validation,
2. required DNS failures keep the operator-facing remediation message,
3. JSON and text probes still record summary evidence,
4. malformed JSON responses fail with a high-signal error instead of a vague parse failure.

## Review Notes

Conscious decisions:

1. gateway payload shape assertions were intentionally left in the validator because they are still
   coupled to portfolio, performance, and risk business semantics,
2. no documentation changes were made in this slice because operator commands and runbook flow are
   unchanged,
3. no skill changes were made in this slice because future-agent routing still points to the same
   governed runtime path.
