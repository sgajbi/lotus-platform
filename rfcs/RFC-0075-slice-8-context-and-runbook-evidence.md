# RFC-0075 Slice 8 Context and Runbook Evidence

- RFC: `RFC-0075-canonical-front-office-portfolio-seed-and-demo-validation-system.md`
- Slice: 8
- Status: Complete
- Date: 2026-04-11
- Canonical portfolio: `PB_SG_GLOBAL_BAL_001`
- Canonical benchmark: `BMK_PB_GLOBAL_BALANCED_60_40`

## Summary

Slice 8 updated durable platform guidance so future agents and developers use the governed
front-office runtime and screenshot path instead of recreating ad hoc stack or screenshot flows.

The updated guidance points to:

1. `lotus-workbench/docs/operations/canonical-front-office-local-runtime.md`,
2. `npm run live:stack:up`,
3. `npm run live:validate`,
4. `npm run live:stack:down`,
5. `automation/Invoke-Canonical-FrontOffice-QA.ps1 -ScreenshotDirectory <path>`.

The context now also makes the readiness rule explicit: demo-ready screenshots are valid only after
canonical endpoint, calculation, and panel validation passes. Pre-validation captures must be kept
separate with a `diagnostic-` prefix.

## Updated Artifacts

Platform context and onboarding:

```text
context/LOTUS-ENGINEERING-CONTEXT.md
context/AGENTS-OPERATING-CONTRACT.md
docs/onboarding/LOTUS-AGENT-RAMP-UP.md
docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md
```

Automation runbooks and validators:

```text
automation/README.md
automation/docs/Automation-Guide.md
automation/validate_engineering_context_system.py
```

Deployed agent contract:

```text
<codex-home>/AGENTS.md
```

## Validation Evidence

Context system validation:

```powershell
python automation\validate_engineering_context_system.py
```

Result:

```text
Engineering context system validation passed.
```

Focused RFC and automation governance tests:

```powershell
python -m pytest tests\unit\test_rfc_0075_front_office_seed_governance.py tests\unit\test_front_office_runtime_automation_contract.py -q
```

Result:

```text
10 passed
```

## Operational Guidance Added

Clean demo rebuild:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -Clean -BringUp -BuildImages -KeepRunning
```

Screenshot pack:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 `
  -ScreenshotDirectory <temp-dir>/lotus-risk-module-shots
```

Troubleshooting categories now direct operators to:

1. managed hosts sync for hostname failures,
2. service readiness endpoints for runtime failures,
3. the canonical seed verifier for seed failures,
4. `calculationChecks` for calculation failures,
5. `panelClassifications` for blank or degraded panel failures,
6. `-ScreenshotDirectory` writeability checks for screenshot failures.

## Remaining Work

Final acceptance should focus on:

1. confirming all RFC-0075 PR checks are green,
2. deciding whether to merge once user review posture is satisfied,
3. completing branch hygiene after merge,
4. recording any CI fix-forward evidence discovered after GitHub completes the heavier gates.
