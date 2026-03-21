# Core -> Performance Baseline Scenario

## Purpose

This scenario runs the whole reusable `lotus-core` -> `lotus-performance` validation family in one pass.

It answers the operational question:

"Do the core performance analytics surfaces still tell one consistent story across TWR, benchmark, MWR, returns-series, contribution, and attribution?"

## What It Covers

- TWR + benchmark
- returns-series
- contribution
- attribution
- MWR

## How Stable Mode Works

When run with `-SkipSeed`, the baseline runner reuses:

- the latest stable shared-scenario suffix from the TWR + benchmark artifact
- the latest stable MWR scenario suffix from the MWR artifact

This lets teams rerun the whole baseline quickly even when fresh-seed analytics readiness is still under investigation upstream.

## How To Run

Run the full stable baseline using the latest available scenario artifacts:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-CrossApp-CorePerformance-Baseline.ps1 -SkipSeed
```

Override the scenario suffixes explicitly when needed:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-CrossApp-CorePerformance-Baseline.ps1 -SkipSeed -SharedScenarioSuffix 030053 -MwrScenarioSuffix 023442
```

## Artifacts

The validator writes:

- `output/cross-app/core-performance-baseline-validation.json`
- `output/cross-app/core-performance-baseline-validation.md`

These artifacts are intended for engineers, QA, ops users, and business stakeholders who want one readable snapshot of the current cross-app baseline state.
