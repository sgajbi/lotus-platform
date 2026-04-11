# RFC-0075 Slice 4 Derived-State Readiness Evidence

- RFC: `RFC-0075-canonical-front-office-portfolio-seed-and-demo-validation-system.md`
- Slice: 4
- Status: Complete
- Date: 2026-04-11
- Canonical portfolio: `PB_SG_GLOBAL_BAL_001`
- Canonical benchmark: `BMK_PB_GLOBAL_BALANCED_60_40`
- Canonical as-of date: `2026-04-10`

## Summary

Slice 4 closed the gap where canonical seed verification could pass while downstream portfolio-level derived state was still stale.

The root cause was in `lotus-core`: portfolio aggregation eligibility still enforced a legacy prior-day portfolio-timeseries dependency even though current aggregation logic no longer carries forward prior portfolio rows. This forced a long one-day-at-a-time backlog for the canonical front-office seed. Position timeseries could be current while portfolio timeseries and analytics reference remained stale, causing workbench panel validation to fail later.

The fix removed the obsolete sequencing dependency and retained the real readiness gate: a business date is eligible only when the latest snapshot-per-security set has matching position-timeseries rows.

## Core Evidence

Focused core validation:

```powershell
python -m pytest tests/unit/tools/test_front_office_portfolio_seed.py tests/unit/services/portfolio_aggregation_service/repositories/test_timeseries_repository.py tests/unit/services/timeseries_generator_service/timeseries-generator-service/repositories/test_unit_timeseries_repo.py tests/unit/services/portfolio_aggregation_service/core/test_aggregation_scheduler.py -q
```

Result:

```text
42 passed in 1.18s
```

Integration validation:

```powershell
python -m pytest tests/integration/services/timeseries_generator_service/test_timeseries_repository_integration.py -q
```

Result:

```text
5 passed in 37.65s
```

Live canonical seed verification:

```powershell
python tools\front_office_portfolio_seed.py --verify-only --portfolio-id PB_SG_GLOBAL_BAL_001 --start-date 2025-03-31 --end-date 2026-04-10 --benchmark-start-date 2025-01-06 --wait-seconds 120 --poll-interval-seconds 5
```

Result:

```text
Front-office seed verified: {
  'portfolio_id': 'PB_SG_GLOBAL_BAL_001',
  'positions': 11,
  'valued_positions': 11,
  'transactions': 29,
  'cash_accounts': 2,
  'allocation_views': 4,
  'income_types': 3,
  'activity_buckets': 4,
  'projected_cashflow_points': 31,
  'benchmark_code': 'BMK_PB_GLOBAL_BALANCED_60_40',
  'analytics_performance_end_date': '2026-04-10',
  'performance_report_end_date': '2026-04-11',
  'return_path_latest_available_date': '2026-04-11'
}
```

Database readiness evidence after the targeted aggregation service restart:

```text
portfolio_aggregation_jobs for PB_SG_GLOBAL_BAL_001:
pending=0
processing=0
complete=382
max_complete=2026-04-17

portfolio_timeseries max(date)=2026-04-17
```

Core analytics reference evidence:

```text
resolved_as_of_date=2026-04-10
performance_end_date=2026-04-10
portfolio_currency=USD
reference_state_policy=current_portfolio_reference_state
```

## Platform Evidence

Canonical platform validation:

```powershell
powershell -ExecutionPolicy Bypass -File automation\Invoke-Canonical-FrontOffice-QA.ps1
```

Result:

```text
Live canonical Workbench validation passed for PB_SG_GLOBAL_BAL_001.
Wrote C:\Users\Sandeep\projects\lotus-platform\output\front-office-qa\canonical-front-office-qa-20260411-182807.json
Wrote C:\Users\Sandeep\projects\lotus-platform\output\front-office-qa\canonical-front-office-qa-20260411-182807.md
```

Generated screenshot inventory:

```text
portfolio-summary-live.png
portfolio-detailed-live.png
performance-summary-live.png
performance-analysis-live.png
performance-advisor-brief-live.png
performance-risk-live.png
performance-evidence-live.png
```

## Implementation Notes

`lotus-core` now treats portfolio aggregation dates independently once the position-timeseries completeness gate is satisfied. This matches the current calculation model and removes a legacy bottleneck rather than hiding it behind a longer wait.

`lotus-core` seed verification now rejects stale derived analytics state by asserting:

1. analytics reference `performance_end_date` is at or after the canonical ready date,
2. gateway performance `report_end_date` is at or after the canonical ready date,
3. return-path `latest_available_date` is at or after the canonical ready date.

This prevents a future seed run from passing when the UI would later fail due stale derived-state windows.

## Remaining Work

Slice 5 should now validate the performance and risk calculation surfaces in detail:

1. contribution and attribution row counts,
2. benchmark-relative return behavior,
3. risk snapshot, drawdown, concentration, rolling risk, and historical attribution row/window counts,
4. numeric sanity ranges for demo-quality outputs.
