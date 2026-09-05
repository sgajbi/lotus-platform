# Troubleshooting

Current support posture is evidence-first: identify the failing layer, run its narrow diagnostic,
then use the owning runbook before changing shared infrastructure.

## First Response Matrix

| Symptom | First response |
| --- | --- |
| Canonical hostname fails | Check host synchronization and ingress status. |
| Service is unhealthy | Validate ingress, then inspect the owning service. |
| Product surface is empty or stale | Use the Workbench-owned canonical runtime validation. |
| Documentation validation fails | Classify the documentation layer, then run its contract tests. |

## Common failure patterns

### Canonical hostname does not resolve

Likely issue:

- hosts-file block is missing or stale

Use:

```powershell
powershell -ExecutionPolicy Bypass -File automation\Sync-Dev-Ingress-Hosts.ps1
powershell -ExecutionPolicy Bypass -File automation\Sync-Dev-Ingress-Hosts.ps1 -Apply
```

### Canonical hostname resolves but service is unhealthy

Likely issue:

- ingress edge is up but routed service is unhealthy
- target service is not running
- target service is returning timeout or HTTP errors

Use:

```powershell
powershell -ExecutionPolicy Bypass -File automation\Validate-Dev-Ingress-Smoke.ps1
powershell -ExecutionPolicy Bypass -File automation\Explain-Dev-Ingress-Status.ps1
```

### Product screenshots exist but are not demo-ready

Likely issue:

- screenshots were captured before canonical validation completed

Rule:

- use `lotus-workbench` canonical runtime for populated front-office proof
- treat pre-validation captures as diagnostic artifacts only

### Platform docs changed and you are unsure what to run

Classify the change first:

- use [Lotus Documentation Layering](https://github.com/sgajbi/lotus-platform/blob/main/docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md) to
  decide whether the change belongs in `README.md`, repo-local `wiki/`, deep `docs/`, or platform
  `context/`
- use [Task Routing Guide](https://github.com/sgajbi/lotus-platform/blob/main/context/TASK-ROUTING-GUIDE.md) when the task is really documentation
  workflow rather than generic platform debugging

Use this high-signal pack first:

```powershell
python -m pytest tests/unit/test_engineering_context_system_contract.py tests/unit/test_dev_ingress_status_automation_contract.py tests/unit/test_front_office_runtime_automation_contract.py -q
python automation/validate_engineering_context_system.py
```

### A cross-cutting document exists in the wrong repo

Likely issue:

- historical material survived a repo split or ecosystem redesign

Use:

- [Legacy Core Wiki Migration Ledger](Legacy-Core-Wiki-Migration-Ledger)
- [Platform Surfaces](Platform-Surfaces)

## Escalation rule

If the issue is truly product-surface runtime proof, switch to the governed `lotus-workbench`
runtime flow before continuing platform-level debugging.

## Related pages

- [Getting Started](Getting-Started)
- [Operations Runbook](Operations-Runbook)
- [Platform Surfaces](Platform-Surfaces)
- [Lotus Documentation Layering](https://github.com/sgajbi/lotus-platform/blob/main/docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md)
