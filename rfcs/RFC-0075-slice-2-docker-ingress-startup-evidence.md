# RFC-0075 Slice 2 Docker, Ingress, and Startup Evidence

- RFC: `RFC-0075-canonical-front-office-portfolio-seed-and-demo-validation-system.md`
- Slice: 2, canonical Docker and ingress cleanup path
- Status: Complete
- Captured: 2026-04-11
- Captured by: Codex local validation

## Scope

Slice 2 standardizes the governed local runtime path before seed economics changes begin.

Implemented scope:

1. `Invoke-Canonical-FrontOffice-QA.ps1 -Clean` now delegates to the governed `lotus-workbench` teardown and removes remaining stale Lotus containers and Lotus/PBWM/performance volumes.
2. `Invoke-Canonical-FrontOffice-QA.ps1 -Clean -RemoveImages` additionally removes matching local Lotus images.
3. The platform wrapper records Docker artifact counts before cleanup, after cleanup, and after validation.
4. Cleanup-only mode no longer runs validation or imports stale screenshot evidence.
5. Workbench live validation now propagates browser validation failures to callers.
6. Workbench live validation now runs from the workbench repository root so screenshot and summary evidence land in the governed workbench output directory regardless of caller working directory.
7. Platform validation now fails if a workbench live summary is missing or stale.

## Validation Evidence

Targeted local checks:

```text
python -m pytest tests/unit/test_front_office_runtime_automation_contract.py tests/unit/test_rfc_0075_front_office_seed_governance.py -q
4 passed in 0.28s
```

```text
npx vitest run tests/unit/live-canonical-validation-script.test.ts
1 test passed
```

```text
PowerShell parse validation:
Platform wrapper parse ok
Workbench validation script parse ok
```

Cleanup-only evidence:

```text
powershell -ExecutionPolicy Bypass -File automation\Invoke-Canonical-FrontOffice-QA.ps1 -Clean -RemoveImages
Status: ok
Steps: clean
Containers after clean: 0
Volumes after clean: 0
Images after clean: 0
```

Clean rebuild and startup evidence:

```text
powershell -ExecutionPolicy Bypass -File automation\Invoke-Canonical-FrontOffice-QA.ps1 -Clean -BringUp -BuildImages -KeepRunning
Status: ok
Steps: clean, bring-up
Containers before: 0
Volumes before: 0
Images before: 0
Containers after clean: 0
Volumes after clean: 0
Images after clean: 0
Containers after run: 35
Volumes after run: 4
Images after run: 25
```

Fresh validation evidence against the running stack:

```text
powershell -ExecutionPolicy Bypass -File automation\Invoke-Canonical-FrontOffice-QA.ps1
Status: ok
Steps: validate
Containers before: 35
Volumes before: 4
Images before: 25
Containers after run: 35
Volumes after run: 4
Images after run: 25
```

Fresh workbench live summary:

```text
generatedAt: 2026-04-11T09:59:13.987Z
portfolioId: PB_SG_GLOBAL_BAL_001
benchmarkCode: BMK_PB_GLOBAL_BALANCED_60_40
```

Canonical DNS checks passed for:

```text
workbench.dev.lotus
gateway.dev.lotus
core-query.dev.lotus
core-control.dev.lotus
core-ingestion.dev.lotus
performance.dev.lotus
risk.dev.lotus
advise.dev.lotus
manage.dev.lotus
report.dev.lotus
ai.dev.lotus
```

Canonical API and UI checks passed for:

```text
Foundation workspace
Performance summary
Risk summary
Advisor brief
lotus-manage integration capabilities
lotus-report integration capabilities
Gateway platform capabilities
Gateway workbench overview
Workbench portfolio route
Workbench performance route
Top holdings chart: 10 items
Return path observation table: 7 rows
Attribution detail table: 6 rows
Contribution detail table: 4 rows
Advisor brief source metrics: 5 buttons
Historical risk attribution table: 7 rows
Evidence support status: degraded
```

## Slice 2 Review

The cleanup and validation path now rejects stale runtime evidence instead of accepting old screenshots or old summaries.

One real defect was found during review: `Validate-LotusFrontOfficeCanonical.ps1` allowed Node browser-validation failures to appear as a successful PowerShell script run. That was fixed in `lotus-workbench` with a focused contract test.

Another evidence defect was found during review: the Node validator wrote artifacts relative to the caller working directory. That was fixed by running the validator from the workbench repository root.

Remaining later-slice work:

1. The canonical seed still uses the existing seed window in `lotus-core`; Slice 3 will rebuild the economics and date coverage.
2. Evidence support remains degraded by current contract posture; Slice 6 will classify or implement the supported contract.
3. The current stack is intentionally left running after the `-KeepRunning` bring-up for follow-on seed and panel work.
