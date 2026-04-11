# RFC-0075 Slice 7 Demo Screenshot Evidence

- RFC: `RFC-0075-canonical-front-office-portfolio-seed-and-demo-validation-system.md`
- Slice: 7
- Status: Complete
- Date: 2026-04-11
- Canonical portfolio: `PB_SG_GLOBAL_BAL_001`
- Canonical benchmark: `BMK_PB_GLOBAL_BALANCED_60_40`
- Screenshot directory: `C:\Users\Sandeep\AppData\Local\Temp\lotus-risk-module-shots`

## Summary

Slice 7 made demo screenshot capture a governed validation artifact instead of an ad hoc browser task.

The Workbench validator now accepts a caller-provided `-ScreenshotDirectory`, writes screenshots and
`live-validation-summary.json` into that directory, and records structured screenshot evidence for
each capture: stable file name, absolute path, route, panel identifier, portfolio ID, benchmark ID,
as-of date, and readiness state. It also writes `SHOT-INDEX.md` for demo review.

## Validation Evidence

Focused Workbench checks:

```powershell
npx vitest run tests/unit/live-canonical-validation-script.test.ts
node --check scripts\live\validate-canonical-workbench-live.mjs
```

Result:

```text
6 tests passed
```

Focused platform wrapper checks:

```powershell
python -m pytest tests\unit\test_front_office_runtime_automation_contract.py -q
```

Result:

```text
2 passed
```

Canonical platform validation with explicit screenshot directory:

```powershell
powershell -ExecutionPolicy Bypass -File automation\Invoke-Canonical-FrontOffice-QA.ps1 `
  -ScreenshotDirectory C:\Users\Sandeep\AppData\Local\Temp\lotus-risk-module-shots
```

Result:

```text
Live canonical Workbench validation passed for PB_SG_GLOBAL_BAL_001.
Wrote C:\Users\Sandeep\projects\lotus-platform\output\front-office-qa\canonical-front-office-qa-20260411-190254.json
Wrote C:\Users\Sandeep\projects\lotus-platform\output\front-office-qa\canonical-front-office-qa-20260411-190254.md
```

## Captured Product Surfaces

The screenshot directory contains:

```text
portfolio-summary-live.png
portfolio-detailed-live.png
performance-summary-live.png
performance-analysis-live.png
performance-advisor-brief-live.png
performance-risk-live.png
performance-evidence-live.png
live-validation-summary.json
SHOT-INDEX.md
```

`SHOT-INDEX.md` records:

```text
portfolio-summary-live.png - portfolio.summary - /portfolio?portfolioId=PB_SG_GLOBAL_BAL_001 - demo_ready
portfolio-detailed-live.png - portfolio.detailed - /portfolio?portfolioId=PB_SG_GLOBAL_BAL_001&tab=detailed - demo_ready
performance-summary-live.png - performance.summary - /performance?portfolioId=PB_SG_GLOBAL_BAL_001 - demo_ready
performance-analysis-live.png - performance.analysis - /performance?portfolioId=PB_SG_GLOBAL_BAL_001&mode=analysis - demo_ready
performance-advisor-brief-live.png - performance.advisor_brief - /performance?portfolioId=PB_SG_GLOBAL_BAL_001&mode=advisor - demo_ready
performance-risk-live.png - performance.risk - /performance?portfolioId=PB_SG_GLOBAL_BAL_001&mode=risk - demo_ready
performance-evidence-live.png - performance.evidence - /performance?portfolioId=PB_SG_GLOBAL_BAL_001&mode=evidence - truthfully_degraded
```

The `performance.evidence` capture remains intentionally marked `truthfully_degraded` because the
current gateway contract does not expose full evidence and lineage surfaces. The panel is not treated
as demo-ready data; it is included to show the supported degraded-state behavior.

## Remaining Work

Slice 8 should focus on final documentation and agent-context hardening:

1. update platform runbooks and onboarding documents,
2. update agent context with the governed demo path,
3. remove stale script references,
4. decide whether additional service health or observability screenshots belong in future demo packs.
