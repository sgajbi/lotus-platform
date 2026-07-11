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
- delegated engineering task ledger and review evidence

## Useful commands

```powershell
powershell -ExecutionPolicy Bypass -File automation\Sync-Dev-Ingress-Hosts.ps1
powershell -ExecutionPolicy Bypass -File automation\Validate-Dev-Ingress-Smoke.ps1
powershell -ExecutionPolicy Bypass -File automation\Explain-Dev-Ingress-Status.ps1
powershell -ExecutionPolicy Bypass -File automation\Invoke-Canonical-FrontOffice-QA.ps1 -BringUp
powershell -ExecutionPolicy Bypass -File automation\Invoke-DpmCommandCenterSeed.ps1
python automation\mesh_certification_gate.py --mode blocking --generated-at-utc 2026-04-20T00:00:00Z --require-sibling-repos
python automation\generate_enterprise_mesh_operating_report.py --generated-at-utc 2026-04-20T00:00:00Z --check
powershell -ExecutionPolicy Bypass -File automation\Platform-Pulse.ps1
powershell -ExecutionPolicy Bypass -File automation\Run-Heartbeat.ps1
python automation\validate_agent_engineering_contracts.py
python automation\delegation_task_ledger.py --help
python automation\validate_analytics_ui_entitlement_certification.py
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
7. treat delegated-agent output as evidence for the accountable main agent, not as review, PR
   approval, wiki publication, or merge authority

## Canonical DPM command-center seed

`Invoke-Canonical-FrontOffice-QA.ps1 -BringUp` runs the DPM command-center seed by default before
Workbench validation. The seed refreshes `MANDATE_PB_SG_GLOBAL_BAL_001` from `lotus-core` through
`lotus-manage`, runs one Manage monitoring pass for command-center evidence, then verifies manage lookup, Gateway mandate lookup, Gateway mandate health, and
Gateway command-center summary before browser proof starts. The seed evidence records
`posture_checks` for populated source-ready `ready`, selector-driven `partial`, and empty-date `empty`
command-center states before Workbench screenshots can be promoted.

Use `Invoke-DpmCommandCenterSeed.ps1` directly only when the stack is already running and the goal
is to diagnose or refresh the DPM command-center data path without rerunning the full browser proof.
Use `-SkipDpmCommandCenterSeed` on canonical QA only for diagnostics that intentionally validate an
unseeded or degraded DPM state. Current governed seed proof covers populated ready, partial, and
empty command-center supportability postures. Explicitly degraded and blocked command-center
fixtures remain source-owner follow-up because the platform seed must not fabricate unavailable or
blocked source truth.

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

## Analytics UI entitlement certification

RFC-0108 caller-context entitlement certification is governed by
`context/contracts/analytics-ui-observability-entitlement-certification.json`.

Before promoting full caller-context entitlement certification:

1. prove both `gateway.analytics.audit.analytics_read_allowed` and
   `gateway.analytics.audit.analytics_read_denied` for each certified Workbench read path
2. prove denied reads use `permission_blocked` and `upstream_authorization_denied`
3. prove malformed or missing caller context is rejected
4. prove raw entitlement failures, support references, portfolio/client identifiers, trace or
   correlation identifiers, request/response bodies, and screen content are absent from evidence
5. prove Workbench renders permission-blocked state without restricted details

Run:

```powershell
python automation\validate_analytics_ui_entitlement_certification.py
python -m pytest tests\unit\test_analytics_ui_entitlement_certification.py tests\unit\test_analytics_ui_observability_contract.py -q
```

## Delegated engineering tasks

RFC-0096 delegated work uses governed profiles and evidence envelopes from
`platform-contracts/agent-engineering/delegation-policy-contract.v1.json`.

Use `automation/delegation_task_ledger.py` when delegated work needs durable source truth:

1. `create` records the delegated task under the RFC-0094 engineering task ledger shape.
2. `update-status` records terminal failure, cancellation, timeout, lost, or superseded posture.
3. `record-return` attaches a returned delegation output artifact and validates changed files
   against the declared write scope.
4. `record-review` records explicit main-agent review and is the only helper path that marks
   returned delegated work as accepted.

If the `delegated_task_ledger` heartbeat source is explicitly enabled, heartbeat can surface stale,
failed, lost, missing-evidence, unresolved-review, or overlapping-write-scope delegated tasks from
the ledger artifact. That attention remains advisory.

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

## Service cost attribution

Platform-owned service cost evidence uses a normalized aggregate billing export, deterministic
decimal allocation, explicit residual handling, and exact artifact attestation. Application
resource observations are supporting digests, not billing authority. Local generation remains
uncertified; only the protected mainline workflow can produce evidence eligible for consumer
qualification.

Use [Service Cost Attribution Operations](../docs/operations/service-cost-attribution.md) for the
evidence flow, protected environment, verification steps, and failure handling. The workflow must
never upload raw billing rows, credentials, provider-account identifiers, or business identifiers.

## Key references

- [automation/README.md](../automation/README.md)
- [platform-stack/README.md](../platform-stack/README.md)
- [Local Development Runbook](../docs/operations/Local%20Development%20Runbook.md)
- [Lotus Documentation Layering](../docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md)
- [Lotus Developer Onboarding](../docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md)
- [Troubleshooting](Troubleshooting)
