# Core -> Performance TWR And Benchmark Scenario

## Purpose

This scenario validates a live cross-app workflow between `lotus-core` and `lotus-performance`.

It answers a business and operations question:

"If we seed a realistic portfolio and benchmark in `lotus-core`, can `lotus-performance` source the data statefully and produce benchmark-aware TWR outputs that are internally consistent?"

## Scenario Shape

The validator seeds:

- one USD portfolio
- one cash position
- one Apple equity position
- one Microsoft equity position
- five business dates
- one 60/40 benchmark
- one equity index component
- one bond index component
- one live portfolio-to-benchmark assignment

## What It Checks In lotus-core

- portfolio analytics timeseries exists
- position analytics timeseries exists
- benchmark assignment resolves
- composition-window resolves
- index price-series resolves

## What It Checks In lotus-performance

- dedicated stateful benchmark calculation works
- benchmark-inclusive stateful TWR works
- relative performance equals portfolio minus benchmark
- benchmark context is returned for the caller

## Why It Matters

This is a business-meaningful scenario, not just a technical smoke test.

It proves that:

- benchmark ownership in `lotus-core` is usable by downstream analytics
- `lotus-performance` can operate statefully instead of relying on caller-built stateless payloads
- benchmark-aware TWR can be validated against a reproducible seeded portfolio

## Expected Outputs

- `output/cross-app/core-performance-twr-benchmark-validation.json`
- `output/cross-app/core-performance-twr-benchmark-validation.md`

## Current Known Defects

At the time this scenario was added, the validation is expected to surface real defects:

- stateful TWR still fails when `performance_start_date` is omitted
- dedicated benchmark endpoint and benchmark-inclusive TWR do not use the same return unit
- benchmark assignment ingestion still requires `assignment_recorded_at` in practice

These should be tracked as GitHub issues and then treated as regression expectations for this scenario.

## How To Run

Bring up the stacks and run the scenario:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-CrossApp-CorePerformance-TwrBenchmark.ps1 -BringUp
```

If the stacks are already up:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-CrossApp-CorePerformance-TwrBenchmark.ps1
```

If you need to validate against an already-seeded stable scenario while fresh-seed analytics readiness is being investigated in `lotus-core`, reuse the scenario suffix directly:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-CrossApp-CorePerformance-TwrBenchmark.ps1 -SkipSeed -ScenarioSuffix 030053
```
