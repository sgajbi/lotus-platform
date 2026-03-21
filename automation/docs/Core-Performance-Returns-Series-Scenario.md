# Core -> Performance Returns Series Scenario

## Purpose

This scenario validates a live benchmark-aware returns-series workflow between `lotus-core` and `lotus-performance`.

The business question is:

"If we seed a realistic portfolio and benchmark in `lotus-core`, do the benchmark-aware return series in `lotus-performance` stay consistent with the dedicated benchmark endpoint and benchmark-inclusive TWR?"

## What The Scenario Checks

- stateful `/integration/returns/series`
- stateful `/performance/twr` with `include_benchmark=true`
- stateful `/performance/benchmark`

## Expected Relationships

For the same seeded scenario:

- final cumulative portfolio return from returns-series should equal TWR cumulative portfolio return
- final cumulative benchmark return from returns-series should equal:
  - TWR cumulative benchmark return
  - dedicated benchmark endpoint cumulative return
- final cumulative active return from returns-series should equal TWR cumulative relative performance
- each daily active return should equal `portfolio_return - benchmark_return`

## Why This Matters

This scenario proves that the shared benchmark engine and the downstream returns-series surface stay aligned on live stateful data sourced from `lotus-core`.

## Artifacts

The validator writes:

- `output/cross-app/core-performance-returns-series-validation.json`
- `output/cross-app/core-performance-returns-series-validation.md`

## How To Run

Bring up the stacks and run the scenario:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-CrossApp-CorePerformance-ReturnsSeries.ps1 -BringUp
```

If you need to validate against an already-seeded stable scenario while fresh-seed analytics readiness is being investigated in `lotus-core`, reuse the scenario suffix directly:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-CrossApp-CorePerformance-ReturnsSeries.ps1 -SkipSeed -ScenarioSuffix 030053
```
