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

## Key references

- [automation/README.md](../automation/README.md)
- [platform-stack/README.md](../platform-stack/README.md)
- [Local Development Runbook](../Local%20Development%20Runbook.md)
- [Lotus Developer Onboarding](../docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md)
