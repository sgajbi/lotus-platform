# RFC-0075 Slice 5 Performance and Risk Calculation Evidence

- RFC: `RFC-0075-canonical-front-office-portfolio-seed-and-demo-validation-system.md`
- Slice: 5
- Status: Complete
- Date: 2026-04-11
- Canonical portfolio: `PB_SG_GLOBAL_BAL_001`
- Canonical benchmark: `BMK_PB_GLOBAL_BALANCED_60_40`

## Summary

Slice 5 tightened canonical validation from UI/API presence checks to calculation-aware evidence.

The live workbench validator now calls the gateway-backed performance details and risk sub-panel endpoints before screenshots are accepted. It records a `calculationChecks` section in `live-validation-summary.json`, covering performance numeric sanity, contribution reconciliation, governed attribution fallback posture, risk metric readiness, concentration coverage, drawdown evidence, rolling-window availability, and historical risk attribution reconciliation.

## Workbench Evidence

Focused workbench validation:

```powershell
npx vitest run tests/unit/live-canonical-validation-script.test.ts
```

Result:

```text
4 tests passed
```

Syntax validation:

```powershell
node --check scripts\live\validate-canonical-workbench-live.mjs
```

Result:

```text
exit code 0
```

Direct live validator:

```powershell
node scripts/live/validate-canonical-workbench-live.mjs --portfolio-id PB_SG_GLOBAL_BAL_001 --benchmark-code BMK_PB_GLOBAL_BALANCED_60_40 --timeout-ms 60000
```

Result:

```text
Live canonical Workbench validation passed for PB_SG_GLOBAL_BAL_001.
```

## Platform Evidence

Canonical platform validation:

```powershell
powershell -ExecutionPolicy Bypass -File automation\Invoke-Canonical-FrontOffice-QA.ps1
```

Result:

```text
Live canonical Workbench validation passed for PB_SG_GLOBAL_BAL_001.
Wrote C:\Users\Sandeep\projects\lotus-platform\output\front-office-qa\canonical-front-office-qa-20260411-184202.json
Wrote C:\Users\Sandeep\projects\lotus-platform\output\front-office-qa\canonical-front-office-qa-20260411-184202.md
```

`calculationChecks` evidence:

```json
[
  {
    "description": "Performance calculation sanity",
    "portfolioReturnPct": 26.70474,
    "benchmarkReturnPct": 5.209859,
    "activeReturnPct": 21.494881,
    "contributionRows": 4,
    "attributionState": "partial",
    "attributionRows": 0
  },
  {
    "description": "Risk calculation sanity",
    "readyMetricCount": 6,
    "observationCount": 101,
    "concentrationHhi": 1339.487772,
    "rollingWindowCount": 4,
    "rollingWindowResultCount": 4,
    "rollingWindowsWithLatestVolatility": 2,
    "attributionContributorCount": 7
  }
]
```

## Validated Performance Criteria

The validator now asserts:

1. net portfolio return, benchmark return, and active return are finite and within governed sanity ranges,
2. active return reconciles to portfolio return minus benchmark return,
3. market value, cash weight, and position count are finite and plausible,
4. return path has at least four observations,
5. contribution detail has at least four rows,
6. contribution total reconciles to net portfolio return,
7. attribution detail is either populated when supported or carries a governed partial fallback.

Current canonical evidence:

```text
portfolio_return_pct=26.70474
benchmark_return_pct=5.209859
active_return_pct=21.494881
contributionRows=4
attributionState=partial
```

Attribution remains a governed partial because the gateway contract currently reports benchmark-relative attribution detail as summary-level fallback for the selected canonical context. This is accepted only because `fallback_available=true`; a supported attribution contract with zero rows would now fail validation.

## Validated Risk Criteria

The validator now asserts:

1. risk summary is ready,
2. at least six risk metrics are ready,
3. portfolio and benchmark observation counts are sufficient,
4. benchmark context is aligned,
5. concentration HHI and issuer coverage are in valid ranges,
6. drawdown includes an underwater series and benchmark-relative evidence,
7. rolling risk emits all configured windows and enough computable windows for the current horizon,
8. historical risk attribution emits contributors and reconciles with negligible residual.

Current canonical evidence:

```text
readyMetricCount=6
observationCount=101
concentrationHhi=1339.487772
rollingWindowCount=4
rollingWindowsWithLatestVolatility=2
attributionContributorCount=7
```

Longer rolling windows are emitted but may be warm-up only because the canonical YTD horizon has 101 observations. The validator therefore requires all four configured windows to be present and at least two windows to have current computed volatility.

## Remaining Work

Slice 6 should focus on gateway and workbench panel validation quality:

1. prove gateway mappings expose the current backend data used by each panel,
2. classify every workbench panel as ready, empty, partial, unavailable, or out of scope,
3. fail on unsupported blank panels,
4. improve failure attribution when a panel is not populated.
