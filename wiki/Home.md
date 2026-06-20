# Home

`lotus-platform` is the governed engineering system for the Lotus ecosystem.

Use it for:

- platform automation
- ingress and local environment support
- cross-repository validation
- central context and playbooks
- standards, templates, and governance RFCs
- onboarding and agent-operating guidance

## Start here

- [Overview](Overview)
- [Architecture](Architecture)
- [Platform Surfaces](Platform-Surfaces)
- [Getting Started](Getting-Started)
- [Development Workflow](Development-Workflow)
- [Validation and CI](Validation-and-CI)
- [Enterprise Backend Refactor Quality](Enterprise-Backend-Refactor-Quality)
- [Operations Runbook](Operations-Runbook)
- [Analytics UI Observability](Analytics-UI-Observability)
- [Canonical DPM Demo Story](Canonical-DPM-Demo-Story)
- [Troubleshooting](Troubleshooting)
- [Business Benefits](Business-Benefits)
- [Market Landscape](Market-Landscape)
- [Technical Moat and Differentiation](Technical-Moat-and-Differentiation)

## Important commands

```powershell
powershell -ExecutionPolicy Bypass -File automation\Validate-LotusDeveloperEnvironment.ps1 -Mode Inspect -Profile fast
powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane feature
python automation/validate_engineering_context_system.py
python automation/generate_enterprise_backend_quality_baseline.py --write --check
```

## Platform boundary

- `lotus-platform` owns standards, automation, ingress support, validation, and central governance
- `lotus-workbench` owns the canonical populated front-office runtime
- domain truth stays in the domain-authoritative Lotus services

## Use this repository when

- you need to validate or govern multiple Lotus repositories together
- you need to debug ingress, environment posture, or cross-repo runtime support
- you need standards, templates, or validator truth
- you need onboarding, agent-guidance, or central context updates
- you need a cross-cutting ecosystem document that does not belong to one application repo
- you need the enterprise backend refactor baseline, before/after scorecard, or quality gate
  promotion trail

## Key references

- [Repository Engineering Context](../REPOSITORY-ENGINEERING-CONTEXT.md)
- [Lotus Context System](../context/README.md)
- [Lotus Documentation Layering](../docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md)
- [Lotus Developer Onboarding](../docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md)
- [Lotus Agent Ramp-Up](../docs/onboarding/LOTUS-AGENT-RAMP-UP.md)
- [RFC Index](RFC-Index)
