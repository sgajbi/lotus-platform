# RFC-0075 Final Acceptance Evidence

- RFC: `RFC-0075-canonical-front-office-portfolio-seed-and-demo-validation-system.md`
- Status: Complete
- Date: 2026-04-11
- Canonical portfolio: `PB_SG_GLOBAL_BAL_001`
- Canonical benchmark: `BMK_PB_GLOBAL_BALANCED_60_40`

## Summary

RFC-0075 is complete across the required implementation slices. The governed path now provides:

1. deterministic canonical front-office seed data,
2. clean Docker/startup automation,
3. derived-state readiness checks,
4. performance and risk calculation validation,
5. explicit panel classification,
6. governed screenshot capture into a caller-provided directory,
7. durable runbook, onboarding, and agent-context guidance.

## Pull Requests

The RFC-0075 work is raised as draft PRs so GitHub can run the full validation gates:

| Repository | PR | Status |
| --- | --- | --- |
| `lotus-platform` | `https://github.com/sgajbi/lotus-platform/pull/129` | Green before final documentation commit |
| `lotus-workbench` | `https://github.com/sgajbi/lotus-workbench/pull/79` | Green |
| `lotus-core` | `https://github.com/sgajbi/lotus-core/pull/302` | Green after CI fix-forward |

## Local Validation Evidence

Core focused validation:

```powershell
python scripts\config_access_guard.py
python -m pytest tests\unit\scripts\test_source_contract_guards.py tests\unit\services\query_control_plane_service\test_control_plane_settings.py -q
```

Result:

```text
Configuration access guard passed.
6 passed
```

Workbench focused validation:

```powershell
npx vitest run tests/unit/live-canonical-validation-script.test.ts
node --check scripts\live\validate-canonical-workbench-live.mjs
```

Result:

```text
6 tests passed
```

Platform focused validation:

```powershell
python automation\validate_engineering_context_system.py
python -m pytest tests\unit\test_rfc_0075_front_office_seed_governance.py tests\unit\test_front_office_runtime_automation_contract.py -q
```

Result:

```text
Engineering context system validation passed.
11 passed
```

## Live Canonical Validation Evidence

Canonical validation with caller-provided screenshot directory:

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

Screenshot pack:

```text
C:\Users\Sandeep\AppData\Local\Temp\lotus-risk-module-shots
```

The pack contains `SHOT-INDEX.md`, `live-validation-summary.json`, and seven validated product
surface screenshots covering portfolio summary, portfolio detailed, performance summary,
performance analysis, advisor brief, risk, and evidence/degraded-state behavior.

## GitHub CI Evidence

`lotus-workbench` PR #79:

```text
Feature Lane / Lint Typecheck Test: pass
Feature Lane / Workflow Lint: pass
PR Merge Gate / CI Local Docker Parity: pass
PR Merge Gate / Lint Typecheck Coverage Build: pass
PR Merge Gate / Playwright Smoke: pass
PR Merge Gate / Validate Docker Build: pass
PR Merge Gate / Workflow Lint: pass
```

`lotus-core` PR #302:

```text
Feature Lane / Lint Typecheck Contracts Security: pass
Feature Lane / Tests (integration-lite): pass
Feature Lane / Tests (unit-db): pass
Feature Lane / Workflow Lint: pass
PR Merge Gate / Coverage Gate (Combined): pass
PR Merge Gate / Docker Smoke Contract: pass
PR Merge Gate / E2E Smoke: pass
PR Merge Gate / Latency Gate: pass
PR Merge Gate / Lint Typecheck Contracts Security: pass
PR Merge Gate / Performance Load Gate (Fast): pass
PR Merge Gate / Tests: pass across unit, unit-db, integration-lite, ops-contract, and transaction contract suites
PR Merge Gate / Validate Docker Build: pass
PR Merge Gate / Workflow Lint: pass
```

`lotus-platform` PR #129:

```text
Cross-App Vocabulary Gate: pass
Feature Lane / Platform Repo Contracts: pass
Feature Lane / Workflow Lint: pass
PR Merge Gate / Platform Repo Contracts: pass
PR Merge Gate / Workflow Lint: pass
```

The final platform documentation commit will rerun platform PR checks; the previous run was green,
and the final change is documentation/governance evidence plus matching tests.

## CI Fix-Forward Evidence

Core initially failed `config_access_guard.py` because
`src/services/query_control_plane_service/app/settings.py` was a typed settings boundary but was not
listed in the guard allowlist. The fix added that settings module to the explicit allowlist and added
a regression test in `tests/unit/scripts/test_source_contract_guards.py`.

This keeps the standard intact: service code still cannot read environment variables directly, but
typed settings modules remain the governed place for environment parsing.

## Remaining Partial Capability

`performance.evidence` remains intentionally `truthfully_degraded` because the current gateway
contract does not expose full evidence and lineage surfaces. This is not a blank or faked panel; the
UI and validation summary preserve the partial/unavailable service ownership posture.
