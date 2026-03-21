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

- an acquisition-day attribution window fails closed with a clear contract-gap message
- a steady-state attribution window accepts the sourced portfolio and benchmark
- the steady-state response preserves `input_mode = stateful`
- steady-state `benchmark_context` resolves the seeded benchmark assignment
- the steady-state top attribution level reconciles to the reported `sum_of_effects`
- steady-state attribution `total_active_return` aligns with benchmark-inclusive TWR for the same portfolio and window

## Why This Matters

This scenario proves that:

- the system now fails honestly on an unsupported acquisition-day contract edge
- stateful attribution is consuming real `lotus-core` portfolio and benchmark data on supported windows
- the benchmark-aware attribution normalization path is internally coherent on supported windows
- attribution and TWR are telling the same active-return story for the same seeded workflow once the unsupported window is excluded

## Artifacts

The validator writes:

- `output/cross-app/core-performance-attribution-validation.json`
- `output/cross-app/core-performance-attribution-validation.md`

These artifacts are intended for engineers, QA, ops users, and business stakeholders who want a readable record of what was tested and what the outcome was.
