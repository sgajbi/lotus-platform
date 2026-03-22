# Core -> Performance MWR Scenario

## Purpose

This scenario validates a live cross-app workflow between `lotus-core` and `lotus-performance` for stateful Money-Weighted Return.

The business question is:

"If we seed a realistic portfolio in `lotus-core`, can `lotus-performance` source the portfolio statefully and calculate MWR in a way that matches the value implied by the actual sourced portfolio timeseries?"

## What The Scenario Seeds

- one live USD portfolio
- one USD cash instrument
- two live equity instruments
- five business dates
- an initial external deposit
- two equity purchases on the first day
- five days of market prices

## What It Checks In lotus-core

- portfolio analytics timeseries becomes available for the seeded window
- the expected number of observations is present
- the first and last portfolio observations are usable for MWR validation
- cash flows are exposed on the sourced observations

## What It Checks In lotus-performance

- stateful `/performance/mwr` accepts the sourced portfolio window
- the response uses `input_mode = stateful`
- the response window matches the requested stateful window
- the reported MWR matches the value implied by the sourced `lotus-core` portfolio timeseries using the Simple Dietz formula

## Expected Formula

The validator computes the expected value from the sourced `lotus-core` observations using:

`(end_mv - begin_mv - net_cash_flow) / (begin_mv + net_cash_flow / 2) * 100`

This is the current stateful Dietz expectation for the seeded scenario.

## Why This Matters

This scenario proves that:

- `lotus-performance` stateful MWR is using real `lotus-core` data
- the sourced observation contract is sufficient for MWR normalization
- the live result is mathematically consistent with the upstream portfolio timeseries

## Artifacts

The validator writes:

- `output/cross-app/core-performance-mwr-validation.json`
- `output/cross-app/core-performance-mwr-validation.md`

These artifacts are intended for engineers, QA, ops users, and business stakeholders who want a readable record of what was tested and what the outcome was.

## How To Run

Bring up the stacks and run the scenario:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-CrossApp-CorePerformance-Mwr.ps1 -BringUp
```

If you need to validate against an already-seeded stable scenario while fresh-seed analytics readiness is being investigated in `lotus-core`, reuse the scenario suffix directly:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-CrossApp-CorePerformance-Mwr.ps1 -SkipSeed -ScenarioSuffix <existing-mwr-suffix>
```
