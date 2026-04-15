# TWR Investigation Playbook

Use this playbook when reported time-weighted return numbers do not make economic sense, disagree with a benchmark story, or appear inconsistent across Lotus services.

This is not only a `lotus-performance` playbook. Proper TWR triage is cross-boundary work:

1. `lotus-performance` may be linking correctly while upstream economics are wrong,
2. `lotus-core` may be serving inconsistent valuation or cash-flow state,
3. `lotus-gateway` or product surfaces may be rendering the right number with the wrong narrative,
4. documentation may be stale even when code is correct.

The objective is to identify which layer is wrong, explain why, and produce evidence that can be handed to the owning agent or repository without ambiguity.

## When To Use This Playbook

Use it when:

1. a TWR number is too large or too small for the stated mandate,
2. a balanced portfolio behaves like a leveraged or distressed book without explanation,
3. relative return looks wrong,
4. benchmark-aware output and benchmark-only output disagree,
5. daily, monthly, and cumulative paths do not reconcile,
6. the endpoint contract is unclear or documentation appears stale,
7. production triage needs a support-grade explanation rather than a code-level guess.

## Investigation Principle

Never start by assuming the TWR engine is wrong.

Work from the outside in:

1. confirm the live API behavior,
2. reconstruct the number from its direct inputs,
3. test whether those inputs are economically credible,
4. reconcile portfolio-level and position-level state,
5. isolate the owning service and data contract,
6. only then decide whether the defect is in performance math, upstream source data, snapshot serving, or documentation.

## Standard Investigation Sequence

### 1. Capture the exact live request and response

Record:

1. endpoint and hostname,
2. portfolio id,
3. benchmark id if present,
4. `report_end_date`,
5. requested periods and frequencies,
6. `input_mode`,
7. async `calculation_id` if returned,
8. final completed response.

At this stage, answer:

1. does the endpoint respond,
2. does it fail synchronously or asynchronously,
3. is the contract shape internally coherent,
4. which fields are materially relevant to the complaint.

For TWR, the headline fields are usually:

1. `results_by_period.<period>.portfolio.summary.period_return.base`,
2. `results_by_period.<period>.benchmark.summary.period_return.base`,
3. `results_by_period.<period>.relative_performance.summary.period_return.base`,
4. `benchmark_context`,
5. daily and monthly breakdown rows.

### 2. Check the arithmetic before checking the economics

For benchmark-aware TWR:

1. verify `relative = portfolio - benchmark` for period return,
2. verify the same arithmetic for cumulative return,
3. compare the benchmark block inside TWR to the dedicated benchmark endpoint over the same window,
4. confirm daily and monthly rows geometrically link into the reported period return.

If these checks fail, the issue is likely in `lotus-performance`.

If these checks pass, move upstream.

### 3. Pull the upstream source series used by stateful TWR

For Lotus stateful TWR, inspect:

1. portfolio analytics reference,
2. portfolio analytics timeseries,
3. benchmark assignment,
4. benchmark return series or benchmark composition window when calculated mode is in play.

Typical questions:

1. is the portfolio open date what the engine expects,
2. are there actual observations in the requested window,
3. does the returned window match the requested window,
4. are observations marked current, stale, or restated,
5. is the row count consistent with business-date expectations,
6. are cash flows present and classified correctly.

### 4. Compute raw daily returns directly from source observations

Do not rely only on the TWR endpoint output.

For each portfolio timeseries row, calculate:

1. beginning market value,
2. beginning-of-day cash flow,
3. end-of-day cash flow,
4. ending market value,
5. fees,
6. implied daily return using the service contract.

Then rank the largest and smallest days.

This step answers:

1. are the suspicious returns already present in the source data,
2. are the largest moves associated with real cash flows,
3. are there weekend rows, duplicate rows, or implausible valuation jumps,
4. is the problem isolated to one or two dates or pervasive across the whole path.

### 5. Apply domain sense, not only formula checks

Use the mandate and benchmark context.

For a private-banking global balanced mandate:

1. ordinary daily returns should usually be modest,
2. large returns should require a clear valuation event, cash event, or corporate action,
3. a no-cash-flow double-digit daily move is usually a red flag,
4. a monthly result dominated by one unexplained day is not supportable,
5. benchmark divergence should still tell a believable story.

A mathematically correct TWR can still be operationally wrong if the economic path is not credible.

### 6. Reconcile portfolio-level and position-level state

If the source data looks wrong, compare:

1. `portfolio_timeseries`,
2. `position_timeseries`,
3. raw transactions,
4. cash positions,
5. aggregation jobs or reprocessing jobs,
6. served API snapshots.

Core reconciliation checks:

1. portfolio market value should reconcile to authoritative position totals,
2. cash-flow totals should reconcile to actual transactions,
3. fees should not duplicate external withdrawals or deposits,
4. one business date should not expose mixed epochs as though it were one coherent snapshot,
5. stale or superseded rows should not remain query-visible in a way that distorts totals.

### 7. Check epoch and snapshot coherence

This is a common hidden failure mode.

On the same portfolio and date:

1. identify the epoch used by `portfolio_timeseries`,
2. identify the epochs present in `position_timeseries`,
3. determine whether the latest available row per security yields a coherent single snapshot,
4. check whether the API is exposing a mixed-epoch portfolio state.

If positions are split across multiple epochs while the portfolio aggregate is served as one epoch, the analytics inputs are not trustworthy.

### 8. Check cash-flow and fee classification

TWR is very sensitive to cash classification.

Validate whether:

1. deposits appear once, not twice,
2. withdrawals are not also stamped as fees,
3. advisory fees are not doubled,
4. bond interest, dividends, and cash legs are reflected once and in the correct direction,
5. linked transaction groups produce one economic effect, not repeated effects across derived state.

### 9. Check contract and documentation truthfulness

Even when code is correct, support failures multiply if docs are stale.

Check:

1. request examples,
2. response field paths,
3. async accepted/result flow,
4. benchmark semantics,
5. cumulative semantics,
6. hostname and ingress guidance,
7. methodology docs versus live output shape.

Documentation defects do not create bad TWR directly, but they cause repeated mis-triage and wrong operational expectations.

## Decision Tree

### The issue is in `lotus-performance` when:

1. manual linking from the exact source rows disagrees with the API result,
2. benchmark block math is inconsistent with benchmark-only output,
3. relative return arithmetic is wrong,
4. cumulative and period semantics are implemented incorrectly,
5. endpoint response shape differs from its own contract in a materially misleading way.

### The issue is in `lotus-core` when:

1. raw source rows already produce implausible returns,
2. portfolio timeseries does not reconcile to positions,
3. cash flows are duplicated or misclassified,
4. served snapshots mix epochs,
5. derived state does not match seeded transactions or holdings reality.

### The issue is in documentation when:

1. live output is coherent,
2. code behavior is supportable,
3. but docs point operators or callers to the wrong request shape, response fields, or upstream route.

## Production Triage Checklist

When a production TWR issue is reported, answer these questions in order:

1. What exactly was requested?
2. What exact number looks wrong?
3. Is the number mathematically self-consistent?
4. Does the upstream source series explain it?
5. Does the source series make economic sense for the mandate?
6. Do transactions support the implied cash-flow story?
7. Do portfolio and position aggregates reconcile?
8. Are there epoch or restatement anomalies?
9. Is the endpoint contract or methodology doc misleading the operator?
10. Which repository owns the defect?

## Evidence Package To Hand Off

A good handoff to the owning agent should include:

1. the exact request payload,
2. the exact response snippet that is problematic,
3. the manually reconstructed result,
4. the specific dates with abnormal moves,
5. source API evidence for those dates,
6. database evidence when available,
7. the reconciliation gap in plain numbers,
8. the business explanation of why the result is not credible,
9. a concrete ask for fix plus test coverage.

## Example Failure Patterns

### Pattern 1: TWR math is correct but economics are wrong

Symptoms:

1. manual link equals API result,
2. daily source rows contain unexplained double-digit returns,
3. portfolio mandate makes those moves implausible.

Likely owner: upstream source service or data generation.

### Pattern 2: Portfolio and positions disagree

Symptoms:

1. portfolio-level timeseries shows one value,
2. position totals show another,
3. discrepancy persists even after choosing latest rows per security.

Likely owner: aggregation pipeline, snapshot promotion, or query serving logic.

### Pattern 3: Cash-flow duplication

Symptoms:

1. one deposit becomes two times the expected amount in derived state,
2. one withdrawal appears as both cash flow and fee,
3. fees are doubled relative to raw transaction intent.

Likely owner: cash-flow classification or derived-state generation logic.

### Pattern 4: Mixed-epoch state

Symptoms:

1. same portfolio/date exposes rows from several epochs,
2. cash or one security is on a later epoch than the rest,
3. portfolio aggregate appears fully refreshed while positions are not.

Likely owner: timeseries generation, epoch promotion, or serving filter logic.

## Output Standard For Future Agents

When closing a TWR investigation, always report:

1. endpoint status,
2. arithmetic status,
3. economic credibility status,
4. reconciliation status,
5. documentation status,
6. owning repository,
7. exact next action.

Use verdict language like:

1. `API works, math ties, economics fail upstream`,
2. `API contract is correct, methodology doc is stale`,
3. `source data absent, cannot validate TWR`,
4. `portfolio aggregate and position state are not coherent`,
5. `benchmark path is supportable, portfolio path is not`.

## Why This Playbook Exists

TWR complaints often look like analytics defects when they are really source-economics defects, and they often look like source defects when they are actually contract misunderstandings.

This playbook exists to stop shallow triage:

1. do not stop at HTTP 200,
2. do not stop at one formula check,
3. do not stop at one suspicious chart,
4. trace the number to its economic source and its serving boundary,
5. then assign the issue to the right owner with evidence strong enough to act on.
