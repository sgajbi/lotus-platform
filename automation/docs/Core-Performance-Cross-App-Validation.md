# Core-Performance Cross-App Validation

## Purpose

This validation lane seeds a domain-realistic portfolio story into `lotus-core` and then verifies
that `lotus-performance` can consume the resulting stateful analytics inputs correctly.

It exists to catch defects that unit tests inside one repository will miss, especially when:
- transaction intent is translated incorrectly into analytics inputs
- stateful query-control-plane payloads drift from downstream consumer assumptions
- explicit reporting windows behave differently in the live integrated path than they do in isolated tests

## Scenario Files

Scenario files live under:

- `automation/scenarios/core-performance/`

Current scenarios:

- `cash_only_funding_explicit_window.json`
- `cash_liquidation_reentry_explicit_window.json`
- `cash_staged_flows_explicit_window.json`
- `fund_buy_domestic_stock_consistency_explicit_window.json`
- `fund_buy_domestic_stock_explicit_window.json`
- `fund_buy_foreign_stock_explicit_window.json`
- `fund_buy_multi_position_consistency_explicit_window.json`
- `fund_rebalance_multi_position_consistency_explicit_window.json`

Together these scenarios model:
- a healthy pure-cash funding control
- a full cash liquidation followed by recapitalization
- staged external deposits and withdrawals in a cash-only book
- a same-currency funded stock purchase from cash
- a same-currency funded stock purchase from cash with benchmark and attribution consistency checks
- a cross-currency funded stock purchase from cash
- a multi-position funded allocation with cross-surface consistency checks
- an internal rebalance that shifts capital between live sleeves without creating external-flow drift
- explicit-window stateful TWR and contribution queries into `lotus-performance`
- a shared economic story where TWR, contribution, benchmark, and attribution reconcile at different detail levels

## Runner

Run:

```powershell
python automation/core_performance_cross_app_validation.py --scenario automation/scenarios/core-performance/fund_buy_foreign_stock_explicit_window.json --ingestion-url http://127.0.0.1:8200 --query-control-plane-url http://127.0.0.1:8202 --performance-url http://127.0.0.1:8002
```

The runner:
1. seeds the scenario into `lotus-core`
2. waits for analytics maturity
3. validates lotus-core portfolio/position analytics invariants
4. calls `lotus-performance` stateful APIs
5. writes a reusable artifact to `output/core-performance-cross-app/latest.json`

For the consistency scenario, "same story" means:
- TWR reports the top-line portfolio return
- contribution totals reconcile to that portfolio return
- benchmark reports the comparison return over the same explicit window
- attribution reconciles the active return between portfolio and benchmark

Run the whole scenario suite:

```powershell
python automation/core_performance_cross_app_suite.py
```

Suite artifact:

- `output/core-performance-cross-app/suite-latest.json`

The suite is expectation-aware, not just raw pass/fail aware:
- healthy control scenarios are expected to finish with no failed checks
- known upstream defect scenarios can still have raw failed core checks while being treated as `known_issue_observed`
- review `results[*].expected_posture` and top-level `expectation_met_count` before treating a suite run as a regression

The suite now retries each scenario once on transient execution failures such as delayed analytics maturity. This keeps the lane resilient to local-stack timing noise without masking real economic defects.
The suite also uses a longer default analytics maturity timeout than the single-scenario runner because serial seeded scenarios put more sustained pressure on the local core stack.

## What Good Looks Like

For this scenario, the integrated system should show:
- portfolio-level external funding on the funding date
- no external flow on the stock position for the buy leg
- the cash position carrying the full external funding amount, not a trade-settlement netted value
- summed position-level external flow matching portfolio-level external flow for the date
- `lotus-performance` TWR and contribution explicit-window requests returning `200`
- explicit-window daily slices beginning on the requested report start date

Current posture:
- `cash_only_funding_explicit_window` is the healthy control story and passes end to end
- `cash_liquidation_reentry_explicit_window` now passes end to end and serves as the cash liquidation/re-entry control story
- `cash_staged_flows_explicit_window` now passes end to end and serves as the staged external-flow control story
- `fund_buy_domestic_stock_explicit_window` now passes end to end and serves as the same-currency funded-trade control story
- `fund_buy_domestic_stock_consistency_explicit_window` now passes end to end and serves as the cross-surface consistency story for TWR, contribution, benchmark, and attribution
- `fund_buy_foreign_stock_explicit_window` now passes end to end and serves as the cross-currency funded-trade control story
- `fund_buy_multi_position_consistency_explicit_window` now passes end to end and serves as the richer multi-position same-story control for TWR, contribution, benchmark, and attribution
- `fund_rebalance_multi_position_consistency_explicit_window` now passes end to end and serves as the internal-rebalance same-story control for TWR, contribution, benchmark, and attribution

Run scenarios serially. They seed shared local services and parallel runs can distort economic assertions even when each scenario uses unique identifiers.

## Current Known Gap

If the artifact shows that:
- portfolio-level external flow is inflated above the seeded cash movement
- the stock position carries external flow on the buy date
- the cash position external flow is netted down by the trade settlement
- summed position external flow does not match portfolio external flow

then the issue is upstream in `lotus-core` analytics-input generation, not in `lotus-performance`
period resolution.

If the artifact shows that:
- staged cash-only deposits or withdrawals are doubled or otherwise inflated in portfolio-timeseries and position-timeseries
- downstream explicit-window TWR/contribution become non-zero in a zero-return cash story

then the issue is upstream in `lotus-core` external-flow analytics generation and provenance, not in the cross-app runner itself.

That staged cash-only story has now been fixed across the live integrated path. The scenario remains
in the suite as a reusable regression guard for:
- dated portfolio external-flow preservation
- dated position external-flow preservation
- position-flow reconciliation inside `lotus-performance` contribution diagnostics

The cash liquidation/re-entry story remains in the suite as a reusable regression guard for:
- full withdrawal of a cash-only book down to zero
- clean recapitalization on the next business day
- dated portfolio and position external-flow continuity through the liquidation boundary
- zero-return explicit-window TWR and contribution staying economically clean across the re-entry

The funded-trade stories have also been fixed across the live integrated path. They now remain in
the suite as reusable regression guards for:
- funded buy legs staying internal at the position level
- cash-leg external flow preserving the original funding amount
- summed position external flow reconciling to portfolio external flow on the trade date
- stateful explicit-window TWR and contribution remaining stable for both same-currency and FX-funded books

The new consistency story remains in the suite as a reusable regression guard for:
- explicit-window stateful TWR with benchmark in a funded trade
- contribution totals tying to the same portfolio return
- direct benchmark return matching the benchmark leg used in TWR
- attribution total active return matching TWR relative performance for the same explicit day

The new multi-position consistency story remains in the suite as a reusable regression guard for:
- funded multi-position books preserving external-flow neutrality at the position sum level
- contribution totals reconciling to TWR across more than one live equity sleeve
- benchmark comparison staying aligned to the same explicit reporting day
- attribution explaining the same active return through grouped sector effects rather than a single-position shortcut

The rebalance consistency story remains in the suite as a reusable regression guard for:
- internal reallocations preserving zero external-flow leakage on the rebalance date
- post-rebalance TWR reflecting the new sleeve weights rather than the pre-trade allocation
- contribution totals and position-level decomposition following the same post-rebalance economic path
- benchmark and attribution explaining the same active return after allocation changes, not only after initial funding
