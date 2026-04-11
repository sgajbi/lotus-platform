# RFC-0075 Slice 3 Core Seed Data Evidence

- RFC: `RFC-0075-canonical-front-office-portfolio-seed-and-demo-validation-system.md`
- Slice: 3, core seed economics and deterministic smoke data
- Status: Complete for seed-data scope
- Captured: 2026-04-11
- Captured by: Codex local validation

## Scope

Slice 3 aligns the canonical seed data contract with RFC-0075 before derived-state readiness fixes.

Implemented scope:

1. `PB_SG_GLOBAL_BAL_001` now uses the fixed canonical as-of date `2026-04-10` in `lotus-core` seed defaults.
2. The governed `lotus-workbench` canonical startup script now passes `--end-date 2026-04-10` to the core seed tool.
3. The future projected withdrawal remains after the canonical as-of date, now dated `2026-04-17` with settlement on `2026-04-20`.
4. Market price coverage reaches `2026-04-10` for every non-cash seed instrument.
5. EUR/USD FX, benchmark return, and USD risk-free coverage reach `2026-05-10`.
6. Cash economics are covered by a deterministic test that proves both USD and EUR operating cash remain positive after the transaction lifecycle.
7. Front-office seed runbook evidence now separates seed-data success from the known derived-state freshness work in Slice 4.

## Validation Evidence

Targeted local checks:

```text
python -m pytest tests/unit/tools/test_front_office_portfolio_seed.py tests/unit/scripts/test_docker_endpoint_smoke.py -q
17 passed in 0.50s
```

```text
npx vitest run tests/unit/live-canonical-validation-script.test.ts
3 tests passed
```

Live seed verification against the running stack:

```text
python tools/front_office_portfolio_seed.py --portfolio-id PB_SG_GLOBAL_BAL_001 --start-date 2025-03-31 --end-date 2026-04-10 --benchmark-start-date 2025-01-06 --wait-seconds 300
Front-office seed verified: positions=10, valued_positions=10, transactions=29, cash_accounts=2, allocation_views=4, income_types=3, activity_buckets=4, projected_cashflow_points=31, benchmark_code=BMK_PB_GLOBAL_BALANCED_60_40
```

Database checks after clean reseed:

```text
PORT_SMOKE_% portfolio count: 0
FO_EQ_AAPL_US max market price date: 2026-04-10
EUR/USD max FX rate date: 2026-05-10
PB_SG_GLOBAL_BAL_001 transaction count: 30
```

The transaction count is `30` in the database because the live API count includes the future projected withdrawal, while the seed readiness verifier counts `29` current transactions in the queried readiness view.

## Review Findings

The governed UI validation after reseed correctly failed because downstream performance derived state still resolves the report window to `2025-05-04`:

```text
report_end_date: 2025-05-04
Return path observation table expected at least 4 body rows but found 1.
```

This is not a seed coverage failure. It is the Slice 4 derived-state freshness problem already recorded in the RFC baseline. The seed now provides data through the canonical as-of date; the next slice must make derived analytics reference that current data instead of silently falling back to stale performance state.

## Slice 3 Review

This slice improves the seed quality without hiding the next readiness defect:

1. The canonical seed as-of date now matches the RFC instead of relying on the older `2026-03-28` date.
2. Forward cashflow remains available after the canonical as-of date.
3. Seed economics remain plausible with positive USD and EUR operating cash.
4. Deterministic smoke cleanup remains covered by existing tests.
5. A live DB check confirms no `PORT_SMOKE_%` portfolio rows remain after the clean seed.

Remaining later-slice work:

1. Slice 4 must fix stale `performance_end_date` and report-window resolution.
2. Slice 5 must revisit performance return sanity after derived-state freshness is corrected.
3. Slice 6 must keep the evidence surface classified as degraded until the gateway contract supports it.
