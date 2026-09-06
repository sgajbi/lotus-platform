# RFC-0075 Slice 6 Panel Classification Evidence

- RFC: `RFC-0075-canonical-front-office-portfolio-seed-and-demo-validation-system.md`
- Slice: 6
- Status: Complete
- Date: 2026-04-11
- Canonical portfolio: `PB_SG_GLOBAL_BAL_001`
- Canonical benchmark: `BMK_PB_GLOBAL_BALANCED_60_40`

## Summary

Slice 6 made Workbench panel readiness explicit in the canonical live validation summary.

The validator now records `panelClassifications` so operators and future agents can see which product surfaces are ready, partial, or unavailable, and which owning service is responsible. It also fails if a supported panel is recorded as blank without a governed empty, partial, unavailable, or out-of-scope posture.

## Workbench Evidence

Focused workbench validation:

```powershell
npx vitest run tests/unit/live-canonical-validation-script.test.ts
```

Result:

```text
5 tests passed
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
Wrote <workspace-root>/lotus-platform/output/front-office-qa/canonical-front-office-qa-20260411-184944.json
Wrote <workspace-root>/lotus-platform/output/front-office-qa/canonical-front-office-qa-20260411-184944.md
```

## Panel Classification Evidence

Current `panelClassifications` evidence:

```json
[
  { "panel": "performance.summary", "state": "ready", "owner": "lotus-gateway", "returnPathRows": 4 },
  { "panel": "performance.analysis.contribution", "state": "ready", "owner": "lotus-gateway", "contributionRows": 4 },
  { "panel": "performance.analysis.attribution", "state": "partial", "owner": "lotus-gateway", "attributionRows": 0, "fallbackAvailable": true },
  { "panel": "performance.evidence", "state": "unavailable", "owner": "lotus-gateway" },
  { "panel": "risk.snapshot", "state": "ready", "owner": "lotus-risk", "readyMetricCount": 6 },
  { "panel": "risk.concentration", "state": "ready", "owner": "lotus-risk", "issuerCoverageRatio": 1 },
  { "panel": "risk.drawdown", "state": "ready", "owner": "lotus-risk", "underwaterSeriesRows": 101 },
  { "panel": "risk.rolling", "state": "ready", "owner": "lotus-risk", "windowCount": 4, "computableWindows": 2 },
  { "panel": "risk.historical_attribution", "state": "ready", "owner": "lotus-risk", "contributorRows": 7 },
  { "panel": "portfolio.summary", "state": "ready", "owner": "lotus-gateway", "portfolioId": "PB_SG_GLOBAL_BAL_001" },
  { "panel": "portfolio.detailed", "state": "ready", "owner": "lotus-gateway", "portfolioId": "PB_SG_GLOBAL_BAL_001" },
  { "panel": "performance.advisor_brief", "state": "ready", "owner": "lotus-gateway", "sourceMetricMinimum": 3 }
]
```

## Governed Partial and Unavailable States

Current accepted non-ready panels:

1. `performance.analysis.attribution`
   - State: `partial`
   - Owner: `lotus-gateway`
   - Reason: benchmark-relative attribution detail is currently exposed as a summary-level fallback for the selected canonical context.
   - Acceptance rule: allowed only when `fallbackAvailable=true`; a supported zero-row attribution contract fails validation.

2. `performance.evidence`
   - State: `unavailable`
   - Owner: `lotus-gateway`
   - Reason: evidence and lineage surfaces are not exposed by the current gateway contract.
   - Acceptance rule: UI must render a truthful unavailable/degraded state, not a blank panel.

## Remaining Work

Slice 7 should focus on final screenshot automation:

1. copy validated screenshots to the caller-provided output directory,
2. preserve stable screenshot names,
3. ensure machine-readable summary references the external screenshot output paths,
4. keep diagnostic captures separate from demo-ready captures.
