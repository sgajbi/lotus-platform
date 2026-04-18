# Operations Runbook

## Core operational surfaces

- ingress host synchronization
- ingress readiness smoke and diagnosis
- platform repo checks
- platform QA entrypoints
- canonical front-office QA wrapper
- PR and background-run monitoring

## Useful commands

```powershell
powershell -ExecutionPolicy Bypass -File automation\Sync-Dev-Ingress-Hosts.ps1
powershell -ExecutionPolicy Bypass -File automation\Validate-Dev-Ingress-Smoke.ps1
powershell -ExecutionPolicy Bypass -File automation\Explain-Dev-Ingress-Status.ps1
powershell -ExecutionPolicy Bypass -File automation\Invoke-Canonical-FrontOffice-QA.ps1 -BringUp
powershell -ExecutionPolicy Bypass -File automation\Platform-Pulse.ps1
```

## Operational rules

1. use `platform-stack/dev-ingress/hosts.example` as the hostname source of truth
2. do not debug app routing before ingress posture is classified
3. do not treat `platform-stack` as the canonical front-office product proof flow
4. capture demo-ready product evidence only after canonical validation passes

## First-response sequence

1. classify whether the issue is ingress, platform automation, documentation governance, or
   front-office runtime proof
2. if ingress-related, run `Validate-Dev-Ingress-Smoke.ps1` and `Explain-Dev-Ingress-Status.ps1`
3. if documentation-related, first classify whether the change belongs in `README.md`, repo-local
   `wiki/`, deep `docs/`, or platform `context/` using [Lotus Documentation
   Layering](../docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md), then run the targeted
   doc-contract pack
4. if product-surface proof is required, switch to the governed `lotus-workbench` runtime flow
5. only after the category is clear should you start deeper repo-level debugging

## Key references

- [automation/README.md](../automation/README.md)
- [platform-stack/README.md](../platform-stack/README.md)
- [Local Development Runbook](../Local%20Development%20Runbook.md)
- [Lotus Documentation Layering](../docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md)
- [Lotus Developer Onboarding](../docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md)
- [Troubleshooting](Troubleshooting)
