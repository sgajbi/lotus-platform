# Operations Runbook

## Start Here

Current scope and evidence posture: this page routes platform operators to implemented automation,
source contracts, and first-response paths. It does not certify an application runtime, production
environment, or bank operation.

| If you need to | Start with |
| --- | --- |
| Classify ingress or local routing | `Validate-Dev-Ingress-Smoke.ps1` and `Explain-Dev-Ingress-Status.ps1` |
| Prove the canonical front-office flow | `Invoke-Canonical-FrontOffice-QA.ps1` after reading the cleanup plan |
| Validate BFF principal-session contract posture | `validate_bff_principal_session_contracts.py` and the BFF principal-session runbook |
| Inspect mesh posture | `mesh_certification_gate.py` and the operating report |
| Inspect CI or background work | `Platform-Pulse.ps1`, heartbeat evidence, and GitHub truth |
| Change documentation | Lotus documentation layering and repo-local authored source |

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
powershell -ExecutionPolicy Bypass -File automation\Invoke-Canonical-FrontOffice-QA.ps1 -CleanPlanOnly
python automation\canonical_orphan_retirement.py --help
powershell -ExecutionPolicy Bypass -File automation\Invoke-DpmCommandCenterSeed.ps1
python automation\mesh_certification_gate.py --mode blocking --generated-at-utc 2026-04-20T00:00:00Z --require-sibling-repos
python automation\generate_enterprise_mesh_operating_report.py --generated-at-utc 2026-04-20T00:00:00Z --check
powershell -ExecutionPolicy Bypass -File automation\Platform-Pulse.ps1
powershell -ExecutionPolicy Bypass -File automation\Run-Heartbeat.ps1
python automation\validate_agent_engineering_contracts.py
python automation\validate_bff_principal_session_contracts.py
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
8. review `output/front-office-qa/cleanup-plan-latest.json` before canonical cleanup; require exact
   Compose-project and working-directory provenance, and never remove Docker resources by broad
   Lotus/PBWM/performance name prefix. Concurrent certification projects are separate owners; a
   reused project name from another or nested working directory, or residual project volumes/images without
   live working-directory provenance, must block cleanup before mutation. The cleanup inventory
   explicitly recognizes `lotus-core`, `lotus-core-app-local`, and
   `lotus-core-canonical-ui` as Core project identities only when their working-directory label is
   the canonical `lotus-core` checkout; a noncanonical checkout alias is a blocking conflict. It
   classifies active foreign owners, missing labelled checkouts, and unproven resource-only owners
   separately. Only a fresh, digest-bound `missing_labelled_checkout` container may be passed to
   `canonical_orphan_retirement.py`; dry-run first, restate every exact target field, review the
   receipt, and use explicit confirmation for execution. The command removes only that full
   container ID and refuses projects, volumes, images, networks, active/registered paths, stale
   plans, and changed identities. Its execution receipt is persisted before mutation and finalized
   with a newly generated view of remaining ownership conflicts.
9. use `Service-Refresh.ps1 -DryRun` before refreshing a service in a shared stack. The governed
   service map must preserve non-secret coexistence environment and published ports; Manage must
   retain host port 8001 and its canonical Core source/workflow settings while Advise remains on
   host port 8000. A refresh is incomplete until running, health, and port verification passes.

## Canonical DPM command-center seed

`Invoke-Canonical-FrontOffice-QA.ps1 -BringUp` runs the DPM command-center seed by default before
Workbench validation. The seed refreshes `MANDATE_PB_SG_GLOBAL_BAL_001` from `lotus-core` through
`lotus-manage`, runs one Manage monitoring pass for command-center evidence, then verifies manage lookup, Gateway mandate lookup, Gateway mandate health, and
Gateway command-center summary before browser proof starts. The seed evidence records
`posture_checks` for populated source-ready `ready`, selector-driven `partial`, and empty-date `empty`
command-center states before Workbench screenshots can be promoted.

The governed contract separates the general command-centre query tenant from the Workbench caller
tenant. Campaign upsert, legacy supersession, Gateway campaign verification, and PM Operating
Quality proof use `dpm_command_center.workbench_caller_tenant_id` (`tenant-sg`); the campaign
scenario repeats the same value to prevent drift. Other command-centre seed operations retain
`dpm_command_center.tenant_id` (`default`). Do not replace this caller boundary with a
query-parameter tenant override.

Before recalculating mandate health, the seed reads the portfolio's cash percentage from the
Gateway Workbench overview at the exact requested date. The read excludes optional Performance and
rebalance enrichment, then validates portfolio/date identity, source warnings and partial failures,
and normalizes the percentage to a ratio. Missing, mismatched, degraded, malformed, or out-of-range
cash evidence fails before persistence; there is no fixed cash-weight fallback. The evidence JSON
records the source URI and both source and normalized values for review.

Use `Invoke-DpmCommandCenterSeed.ps1` directly only when the stack is already running and the goal
is to diagnose or refresh the DPM command-center data path without rerunning the full browser proof.
The seed must pass the Manage write-authorization preflight with
`X-Actor-Id=platform-seed-automation`,
`X-Role=platform-automation`,
`X-Service-Identity=lotus-platform.canonical-dpm-command-center-seed`, and
`X-Capabilities=manage.write` before it performs state-changing refresh, monitoring,
health-recalculate, action-register, or campaign-definition writes. Use
`Invoke-DpmCommandCenterSeed.ps1 -PreflightOnly` to diagnose the exact caller contract without
refreshing or persisting DPM evidence. A 403 is a seed-authority defect and must not be resolved by
disabling Manage authorization. After that preflight passes, `DPM_CORE_CONTEXT_INCOMPLETE` in the
full seed is a Core source-readiness dependency rather than another auth issue; preserve the
response body in `output/front-office-qa/dpm-command-center-seed-latest.json` and link the owning
Core issue, currently `sgajbi/lotus-core#840` for the canonical missing eligibility, tax-lot, and
market-data families.
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

## Background task cancellation

Cancel only by the durable `engineering_task_id` recorded at launch:

```powershell
powershell -ExecutionPolicy Bypass -File automation\Cancel-Background-Run.ps1 `
  -EngineeringTaskId <engineering_task_id> `
  -Reason "Superseded by corrected exact-head evidence" `
  -Actor <operator>
```

The command verifies the recorded PID and process-start identity before terminating that process
tree. Docker cleanup is permitted only for exact Compose projects declared at launch and verified
through live Compose labels; ambiguous, vanished, or reused ownership fails closed. Treat
`CANCELLED` and `cleanup_state` as independent evidence, and retain the generated cancellation
receipt. Never reconstruct cancellation with broad process matching or daemon-wide Docker cleanup.
Launch, monitoring reconciliation, and cancellation share one exclusive ledger lock; contention
defers or rejects the writer without overwriting newer task evidence, and a failed launch append
rolls back its exact newly started process tree.

See [Platform automation](../automation/README.md) for cleanup-plan shape, receipt fields, and
failure classifications.

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

## Authenticated BFF principal session

Platform-owned BFF principal-session evidence defines the source-safe session-to-principal contract
that Workbench, Gateway, and downstream services must consume once a bank-approved IdP/session
authority exists. Current posture is contract/fixture only: local/dev fixtures are non-certifying,
browser-supplied authority headers remain forbidden, and production token-claims certification stays
blocked until external identity, key-discovery, revocation/logout, consumer proof, and exact-main
evidence exist.

Use [Authenticated BFF Principal Session Operations](../docs/operations/bff-principal-session.md)
for contract rules, failure handling, and validation commands.

## Key references

- [automation/README.md](../automation/README.md)
- [platform-stack/README.md](../platform-stack/README.md)
- [Local Development Runbook](../docs/operations/Local%20Development%20Runbook.md)
- [Lotus Documentation Layering](../docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md)
- [Lotus Developer Onboarding](../docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md)
- [Troubleshooting](Troubleshooting)
