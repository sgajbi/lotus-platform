# Core -> Performance Contribution Scenario

## Purpose

This scenario validates a live cross-app workflow between `lotus-core` and `lotus-performance` for stateful contribution.

The business question is:

"If we seed a realistic portfolio in `lotus-core`, can `lotus-performance` source that portfolio statefully, compute contribution, and reconcile the result to both TWR and the contribution ladders it emits?"

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
- the seeded portfolio state is ready for downstream stateful sourcing

## What It Checks In lotus-performance

- stateful `/performance/contribution` accepts the sourced portfolio
- the response preserves `input_mode = stateful`
- the contribution total portfolio return matches stateful TWR for the same portfolio and window
- the reported contribution total reconciles to:
  - the sum of flat position contributions
- each emitted daily total contribution reconciles to the emitted per-position daily series for the same date
- the emitted by-position contribution series include the expected seeded positions and preserve the five business dates

## Why This Matters

This scenario proves that:

- `lotus-performance` is using real `lotus-core` sourced position state
- contribution output is internally consistent across flat and time-series views
- contribution and TWR stay aligned on the same seeded portfolio and period

## Artifacts

The validator writes:

- `output/cross-app/core-performance-contribution-validation.json`
- `output/cross-app/core-performance-contribution-validation.md`

These artifacts are intended for engineers, QA, ops users, and business stakeholders who want a readable record of what was tested and what the outcome was.
