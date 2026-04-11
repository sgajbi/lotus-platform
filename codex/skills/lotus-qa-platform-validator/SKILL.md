---
name: lotus-qa-platform-validator
description: Intelligent Lotus platform QA validator for service bring-up, API probing, observability checks, standards conformance, and defect issue filing with evidence. Use when the user asks to validate an app against lotus-platform standards, run QA automation for a specific Lotus repo, execute QA in background/agent-loop style, or create actionable defects with reproducible proof.
---

# Lotus QA Platform Validator

Use `lotus-platform/automation/Invoke-Platform-QA.ps1` as the source of truth for platform-level readiness validation.

Before substantial QA or validation work, read:

1. `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`
2. `lotus-platform/context/PROCEDURAL-MEMORY-INDEX.md`
3. the target repo `REPOSITORY-ENGINEERING-CONTEXT.md`

Use:

1. `lotus-platform/context/playbooks/VALIDATION-PLAYBOOK.md` to choose validation depth,
2. `lotus-platform/context/playbooks/FIX-FORWARD-PATTERNS.md` when a run exposes a real failure pattern.

## Workflow

1. Resolve platform repo path:
```powershell
$platform = "<lotus-platform>"
if (-not (Test-Path $platform)) { throw "lotus-platform repo not found at $platform" }
```

2. Run QA for a target repo:
```powershell
powershell -ExecutionPolicy Bypass -File automation\Invoke-Platform-QA.ps1 -Repo lotus-risk -BringUp -CreateIssues
```

3. Use dry-run for pipeline verification:
```powershell
powershell -ExecutionPolicy Bypass -File automation\Invoke-Platform-QA.ps1 -Repo lotus-risk -DryRun -CreateIssues
```

4. Read run artifacts:
- `output/qa/<run-id>/qa-summary.md`
- `output/qa/<run-id>/qa-summary.json`
- `output/qa/<run-id>/qa-issues.json`

5. Report:
- findings by severity and check id
- created issue URLs
- evidence file paths
- next gating actions (tests/standards fixes)

## Agent Loop / Async Mode

Use async monitoring when asked to keep runs going while implementation continues:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run-lotus-qa.ps1 -Repo lotus-risk -CreateIssues -Async
```

Monitor:

```powershell
Get-Content output\qa\latest-run.txt
Get-Content (Get-Content output\qa\latest-run.txt | ForEach-Object { "output/qa/$_/qa-summary.md" })
```

## Standards Coverage

Validate beyond functional checks:
- API docs and endpoint reachability
- logging shape and correlation/tracing keys
- metrics and health exposure
- durability/consistency rules
- rounding and precision controls
- data lineage and traceability
- platform contract checks from lotus-platform validators

## Defect Quality Bar

For every defect, ensure issue content includes:
- reproducible steps
- expected vs actual behavior
- concrete evidence (API response/log extracts/run artifact path)
- why existing tests missed it
- recommended regression coverage additions

Use [QA-Checklist](references/qa-checklist.md) and [Issue-Quality](references/issue-quality.md) before marking a service production-ready.

When command flags or artifact paths change, update this skill and keep it aligned with `lotus-platform/automation`.
