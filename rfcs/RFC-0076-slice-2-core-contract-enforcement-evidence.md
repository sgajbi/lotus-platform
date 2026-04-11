# RFC-0076 Slice 2 Core Contract Enforcement Evidence

- RFC: `RFC-0076-canonical-front-office-demo-data-contract.md`
- Slice: `Slice 2: Core Seed Contract Enforcement`
- Date: 2026-04-11
- Owning repository: `lotus-core`
- Implementation PR: `https://github.com/sgajbi/lotus-core/pull/303`

## Summary

Slice 2 moves RFC-0076 from contract definition into executable adoption in `lotus-core`.

The canonical front-office seeder no longer relies solely on scattered hard-coded contract values.
It now uses a small contract module that:

1. loads the platform-governed contract artifacts when `lotus-platform` is available in the local
   workspace,
2. falls back to a deterministic mirrored contract when the platform repo is not present,
3. derives seeded defaults and verification thresholds from the governed contract path,
4. keeps `lotus-core` operationally self-contained while still respecting platform ownership.

## Implemented Changes

### New contract module

Added:

1. `tools/front_office_seed_contract.py`

This module:

1. resolves the platform repo via `LOTUS_PLATFORM_REPO` or the sibling workspace path,
2. loads:
   - `context/contracts/canonical-front-office-demo-data-contract.json`
   - `context/contracts/canonical-front-office-demo-data-invariants.json`
3. builds a typed `FrontOfficeSeedContract`,
4. falls back to explicit governed defaults when platform artifacts are unavailable.

### Seeder adoption

Updated:

1. `tools/front_office_portfolio_seed.py`

The seeder now:

1. derives default portfolio, benchmark, seed-start, benchmark-start, and canonical end date from
   the governed contract,
2. derives verification thresholds from the governed contract,
3. enforces allocation-view and projected-cashflow minimums via the contract-backed expectation
   model rather than route-local assumptions.

### Focused tests

Updated:

1. `tests/unit/tools/test_front_office_portfolio_seed.py`

Coverage now proves:

1. the platform-governed contract loads correctly in the normal workspace,
2. the runtime expectation is derived from the contract,
3. the seeder retains a deterministic fallback when platform artifacts are unavailable.

## Verification

Local verification run:

```text
python -m pytest tests/unit/tools/test_front_office_portfolio_seed.py -q
```

Observed result:

```text
20 passed in 0.55s
```

## Review Notes

This slice was reviewed for coupling and maintainability before acceptance.

Conscious decisions:

1. `lotus-core` does not hard-depend on `lotus-platform` at runtime,
2. the governed path is preferred when available in the local workspace,
3. the fallback is explicit and deterministic rather than silently diverging,
4. only thresholds already meaningful to the current seed verification were wired in this slice,
5. deeper cross-app adoption remains in later slices rather than being overstuffed here.

## Acceptance Position

Slice 2 is considered complete because:

1. `lotus-core` now reads or mirrors the governed canonical contract,
2. seed defaults and key verification thresholds are contract-backed,
3. tests prove both governed loading and deterministic fallback behavior,
4. the implementation reduces contract drift risk without introducing an unsafe cross-repo runtime
   dependency.
