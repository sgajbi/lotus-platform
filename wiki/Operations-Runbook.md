# Operations Runbook

## Core operational surfaces

- ingress host synchronization
- ingress readiness smoke and diagnosis
- platform repo checks
- platform QA entrypoints
- canonical front-office QA wrapper
- mesh certification gate
- enterprise mesh operating report
- PR and background-run monitoring
- advisory heartbeat attention report

## Useful commands

```powershell
powershell -ExecutionPolicy Bypass -File automation\Sync-Dev-Ingress-Hosts.ps1
powershell -ExecutionPolicy Bypass -File automation\Validate-Dev-Ingress-Smoke.ps1
powershell -ExecutionPolicy Bypass -File automation\Explain-Dev-Ingress-Status.ps1
powershell -ExecutionPolicy Bypass -File automation\Invoke-Canonical-FrontOffice-QA.ps1 -BringUp
python automation\mesh_certification_gate.py --mode blocking --generated-at-utc 2026-04-20T00:00:00Z --require-sibling-repos
python automation\generate_enterprise_mesh_operating_report.py --generated-at-utc 2026-04-20T00:00:00Z --check
powershell -ExecutionPolicy Bypass -File automation\Platform-Pulse.ps1
powershell -ExecutionPolicy Bypass -File automation\Run-Heartbeat.ps1
```

## Operational rules

1. use `platform-stack/dev-ingress/hosts.example` as the hostname source of truth
2. do not debug app routing before ingress posture is classified
3. do not treat `platform-stack` as the canonical front-office product proof flow
4. capture demo-ready product evidence only after canonical validation passes
5. do not claim seasoned production mesh posture from a single clean certification run; use the
   RFC-0092 operating report state and history count
6. treat heartbeat output as advisory derived evidence, not as replacement truth for GitHub,
   background-run ledgers, mesh certification, wiki source, context validators, or `lotus-ai`
   workflow-pack runtime APIs

## First-response sequence

1. classify whether the issue is ingress, platform automation, documentation governance, or
   front-office runtime proof
2. if ingress-related, run `Validate-Dev-Ingress-Smoke.ps1` and `Explain-Dev-Ingress-Status.ps1`
3. if documentation-related, first classify whether the change belongs in `README.md`, repo-local
   `wiki/`, deep `docs/`, or platform `context/` using [Lotus Documentation
   Layering](../docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md), then run the targeted
   doc-contract pack
4. if product-surface proof is required, switch to the governed `lotus-workbench` runtime flow
5. if mesh posture is questioned, run the blocking mesh certification gate and inspect
   `enterprise-mesh-operating-report.md`
6. only after the category is clear should you start deeper repo-level debugging
7. if multiple operational surfaces may be stale or degraded, run `Run-Heartbeat.ps1` and inspect
   `output/heartbeat/heartbeat-status.md` for deduplicated attention items before jumping between
   tools manually

## Mesh operations

For mesh issues, start with:

1. `output/mesh-certification/enterprise-mesh-certification-status.md`
2. `output/mesh-certification/enterprise-mesh-operating-report.md`
3. [Mesh Certification Gate Runbook](../docs/operations/mesh-certification-gate-runbook.md)

Operating states:

- `production_ready`: clean current certification and enough history for seasoned posture
- `production_ready_limited_history`: clean current certification but shallow history
- `attention_required`: warnings need review before customer evidence export or product promotion
- `blocked`: errors or failed certification; owning repositories must fix forward

## Key references

- [automation/README.md](../automation/README.md)
- [platform-stack/README.md](../platform-stack/README.md)
- [Local Development Runbook](../Local%20Development%20Runbook.md)
- [Lotus Documentation Layering](../docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md)
- [Lotus Developer Onboarding](../docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md)
- [Troubleshooting](Troubleshooting)
