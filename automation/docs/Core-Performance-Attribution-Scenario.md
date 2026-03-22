# Core -> Performance Attribution Scenario

## Purpose

This scenario validates a live cross-app workflow between `lotus-core` and `lotus-performance` for stateful attribution.

The business question is:

"If we seed a realistic portfolio plus benchmark assignment in `lotus-core`, can `lotus-performance` source the portfolio and benchmark statefully, run attribution, and keep the active-return story aligned with benchmark-inclusive TWR?"

## What The Scenario Seeds

- one live USD portfolio
- one USD cash instrument
- two live equity instruments
- five business dates
- an initial external deposit
- two equity purchases on the first day
- five days of security market prices
- one live benchmark definition
- one live benchmark assignment
- two benchmark indexes with live index price series

## What It Checks In lotus-performance

- an acquisition-day attribution window uses the current upstream-supported contract semantics instead of a stale fail-closed fence
- a steady-state attribution window accepts the sourced portfolio and benchmark
- the steady-state response preserves `input_mode = stateful`
- steady-state `benchmark_context` resolves the seeded benchmark assignment
- the steady-state top attribution level reconciles to the reported `sum_of_effects`
- steady-state attribution `total_active_return` aligns with benchmark-inclusive TWR for the same portfolio and window
- the steady-state output records the first-level attribution groups and flags any duplicate normalized group keys, so we can spot classification-shape regressions quickly
- if `lotus-core` portfolio-timeseries and summed position-timeseries disagree for the same dates, `lotus-performance` now fails closed with an explicit source-alignment message instead of returning misleading attribution numbers

## Why This Matters

This scenario proves that:

- acquisition-day attribution is no longer blocked by stale local fences once upstream cash-flow semantics are present
- stateful attribution is consuming real `lotus-core` portfolio and benchmark data on supported windows
- the benchmark-aware attribution normalization path is internally coherent on supported windows
- attribution and TWR will either tell the same active-return story or fail clearly when the upstream source contracts disagree

## Scenario Structure

This validator intentionally covers two linked sub-scenarios:

1. Acquisition-day boundary
- window starts on the day positions are opened
- expected current behavior: request is accepted if upstream source semantics are present
- this confirms the old local acquisition-day fence is gone

2. Supported steady-state window
- window starts on the next business day after positions are opened
- expected current behavior: stateful attribution succeeds and reconciles, or fails closed with an explicit source-alignment message if `lotus-core` portfolio and position series disagree
- this is our baseline proof that the supported path is healthy and that source inconsistencies are surfaced honestly when present

## Artifacts

The validator writes:

- `output/cross-app/core-performance-attribution-validation.json`
- `output/cross-app/core-performance-attribution-validation.md`

These artifacts are intended for engineers, QA, ops users, and business stakeholders who want a readable record of what was tested and what the outcome was.

## How To Run

Bring up the stacks and run the scenario:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-CrossApp-CorePerformance-Attribution.ps1 -BringUp
```

If you need to validate against an already-seeded stable scenario while fresh-seed analytics readiness is being investigated in `lotus-core`, reuse the scenario suffix directly:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-CrossApp-CorePerformance-Attribution.ps1 -SkipSeed -ScenarioSuffix 030053
```
