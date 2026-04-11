# RFC-0076 Slice 3 Derived-State Readiness Evidence

- RFC: `RFC-0076-canonical-front-office-demo-data-contract.md`
- Slice: `Slice 3: Derived-State Readiness Enforcement`
- Date: 2026-04-11
- Owning repository: `lotus-core`
- Implementation PR: `https://github.com/sgajbi/lotus-core/pull/303`

## Summary

Slice 3 hardens the front-office seeder so derived-state failures do not collapse into a generic
timeout with no operational signal.

The verification flow now emits contract-aware readiness diagnostics when the canonical portfolio is
not analytically ready. This makes it much easier to distinguish:

1. stale or lagging snapshot state,
2. unvalued positions,
3. missing historical FX dependencies,
4. reporting readiness blockers,
5. aggregation backlog conditions.

## Implemented Changes

Updated:

1. `tools/front_office_portfolio_seed.py`
2. `tests/unit/tools/test_front_office_portfolio_seed.py`

The seed verifier now:

1. captures the last observed verification state before timeout,
2. queries source-owned support surfaces:
   - `/support/portfolios/{portfolio_id}/readiness`
   - `/support/portfolios/{portfolio_id}/overview`
   - `/support/portfolios/{portfolio_id}/aggregation-jobs`
3. extracts operator-relevant readiness fields rather than dumping entire payloads,
4. includes readiness, blocking-reason, and aggregation backlog diagnostics in the timeout message.

## Why This Improves the System

This slice improves the current implementation in three important ways:

1. it reduces guesswork during canonical seed bring-up,
2. it uses source-owned readiness semantics instead of inventing new local heuristics,
3. it keeps the implementation modular by adding focused extraction helpers instead of embedding
   large ad hoc error formatting blocks in the verification loop.

## Verification

Local verification run:

```text
python -m pytest tests/unit/tools/test_front_office_portfolio_seed.py -q
```

Observed result:

```text
23 passed in 0.70s
```

The test pack now covers:

1. readiness summary extraction,
2. support overview extraction,
3. support endpoint querying for readiness diagnostics,
4. existing canonical seed economics and fallback behavior.

## Review Notes

This slice was reviewed for overreach before acceptance.

Conscious decisions:

1. readiness diagnostics are queried only on failure rather than on every successful loop,
2. the implementation reuses existing source-owned support endpoints instead of adding a new
   one-off troubleshooting endpoint,
3. helper functions extract only high-signal fields, which keeps timeout output readable,
4. no additional documentation changes were required in `lotus-core` for this slice because the
   runtime contract did not change, only the quality of diagnostics improved.

## Acceptance Position

Slice 3 is considered complete because:

1. derived-state readiness failures now surface actionable diagnostics,
2. the seeder points operators toward source-owned readiness reasons and aggregation backlog state,
3. tests prove the diagnostics helpers and query path,
4. the implementation improves maintainability without creating new contract drift.
