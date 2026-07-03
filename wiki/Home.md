# Home

`lotus-platform` is the governed engineering system for the Lotus ecosystem. It owns shared
automation, ingress support, validation, standards, context, skills, and cross-repository operating
guidance.

Current evidence posture: platform claims must point to an implemented command, validator, contract,
RFC, generated artifact, runbook, or repository-owned proof. Planned or bounded-preview material must
stay visibly labelled as such.

## Reader Paths

| Audience | Start Here | Use This For |
| --- | --- | --- |
| Business, product, and demo | [Overview](Overview), [Canonical DPM Demo Story](Canonical-DPM-Demo-Story), [Client Demo Certification](Client-Demo-Certification) | Understand implementation-backed platform value, demo boundaries, and claim evidence |
| Operations and support | [Operations Runbook](Operations-Runbook), [Troubleshooting](Troubleshooting), [Platform Surfaces](Platform-Surfaces) | Diagnose runtime posture, ingress, QA evidence, and ownership boundaries |
| Engineers and agents | [Getting Started](Getting-Started), [Development Workflow](Development-Workflow), [Validation and CI](Validation-and-CI) | Run local checks, choose the correct lane, and avoid stale stack paths |
| Governance and release reviewers | [Security and Governance](Security-and-Governance), [RFC Index](RFC-Index), [Data Mesh Standard](Data-Mesh-Standard) | Review standards, RFC posture, context contracts, and release controls |
| Commercial readers | [Business Benefits](Business-Benefits), [Market Landscape](Market-Landscape), [Technical Moat and Differentiation](Technical-Moat-and-Differentiation) | Read ecosystem positioning that is separated from implementation claims |

## Evidence And Quality Anchors

| Anchor | Use This For |
| --- | --- |
| [Analytics UI Observability](Analytics-UI-Observability) | Current Workbench/Gateway observability scope, residual boundaries, and live proof posture |
| [Enterprise Backend Refactor Quality](Enterprise-Backend-Refactor-Quality) | `quality/baseline_report.md`, quality scorecard, and `generate_enterprise_backend_quality_baseline.py` evidence |
| [Client Demo Pack Template](Client-Demo-Pack-Template) | Audience-ready claim table, evidence map, boundaries, rehearsal, and follow-up structure |
| [Client Demo Brief Template](Client-Demo-Brief-Template) | One-page client brief structure tied to implementation-backed evidence |

## Current Operating Truth

| Area | Current Truth | Evidence |
| --- | --- | --- |
| Canonical front-office runtime | Governed product-surface proof routes through `lotus-workbench`; `lotus-platform` owns wrappers, ingress, and evidence governance. | [Canonical DPM Demo Story](Canonical-DPM-Demo-Story), [Platform Surfaces](Platform-Surfaces) |
| Canonical QA data | `PB_SG_GLOBAL_BAL_001` is the governed private-banking reference portfolio; the demo pack is not part of canonical PB seed by default. | `context/contracts/canonical-front-office-demo-data-contract.json` |
| `lotus-idea` runtime | `lotus-idea` is included by default in canonical platform QA; readiness and teardown evidence are part of the standard proof. | `automation/Invoke-Canonical-FrontOffice-QA.ps1` |
| Merge posture | Required CI checks and conversation resolution are the controls; human approval reviews are optional in the single-developer baseline. | [Validation and CI](Validation-and-CI), `context/playbooks/PR-LOOP-PLAYBOOK.md` |
| Wiki source | Repo-local `wiki/` is the authored source; the GitHub wiki is a publication target. | [Security and Governance](Security-and-Governance) |

## Common Commands

```powershell
powershell -ExecutionPolicy Bypass -File automation\Validate-LotusDeveloperEnvironment.ps1 -Mode Inspect -Profile fast
powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane feature
powershell -ExecutionPolicy Bypass -File automation\Invoke-Canonical-FrontOffice-QA.ps1 -BringUp
python automation\validate_engineering_context_system.py
```

## Platform Boundary

- `lotus-platform` owns standards, automation, ingress support, validation, and central governance.
- `lotus-workbench` owns the canonical populated front-office runtime.
- Domain truth stays in domain-authoritative Lotus services.
- `platform-stack` supports shared local infrastructure; it is not the canonical populated product
  proof path.

## Key References

- [Repository Engineering Context](../REPOSITORY-ENGINEERING-CONTEXT.md)
- [Lotus Context System](../context/README.md)
- [Lotus Documentation Layering](../docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md)
- [Lotus Developer Onboarding](../docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md)
- [Lotus Agent Ramp-Up](../docs/onboarding/LOTUS-AGENT-RAMP-UP.md)
- [RFC Index](RFC-Index)
