# Shared Automation Toolkit

Canonical cross-cutting automation lives here.

## Start Here

Use these docs first:
- `automation/docs/Automation-Guide.md` (what exists, when to run what)
- `automation/docs/Profile-Reference.md` (profile intent and defaults)
- `automation/docs/Directory-Map.md` (organized script/config map)

Quick baseline commands:

```powershell
# Fast daily alignment baseline
powershell -ExecutionPolicy Bypass -File automation/Start-Background-Run.ps1 -Profile platform-alignment -MaxParallel 3

# Continuous monitor loop
powershell -ExecutionPolicy Bypass -File automation/Run-Agent.ps1
```

## Scripts

- `automation/Sync-Repos.ps1`
- `automation/PR-Monitor.ps1`
- `automation/Close-PR-Loop.ps1`
- `automation/Detect-Stalled-PR-Checks.ps1`
- `automation/Prune-MergedRemoteBranches.ps1`
- `automation/Platform-Pulse.ps1`
- `automation/Run-Heartbeat.ps1`
- `automation/Run-Agent.ps1`
- `automation/Service-Refresh.ps1`
- `automation/Run-Parallel-Tasks.ps1`
- `automation/Start-Background-Run.ps1`
- `automation/Check-Background-Runs.ps1`
- `automation/Summarize-Task-Failures.ps1`
- `automation/Sync-RepoWikis.ps1`
- `automation/Bootstrap-Repo-Env.ps1`
- `automation/Bootstrap-LotusDeveloperEnvironment.ps1`
- `automation/Validate-LotusDeveloperEnvironment.ps1`
- `automation/Validate-Platform-Contract.ps1`
- `automation/Measure-Test-Pyramid.ps1`
- `automation/Validate-Backend-Standards.ps1`
- `automation/Validate-Shared-Infrastructure-Ownership.ps1`
- `automation/Validate-Service-Addressing.ps1`
- `automation/Validate-Dev-Ingress-Smoke.ps1`
- `automation/Explain-Dev-Ingress-Status.ps1`
- `automation/Sync-Dev-Ingress-Hosts.ps1`
- `automation/Generate-Dependency-Vulnerability-Rollup.ps1`
- `automation/Invoke-Platform-QA.ps1`
- `automation/Invoke-Canonical-FrontOffice-QA.ps1`
- `automation/Invoke-CrossApp-CorePerformance-TwrBenchmark.ps1`
- `automation/Invoke-CrossApp-CorePerformance-Baseline.ps1`
- `automation/Invoke-CrossApp-CorePerformance-Contribution.ps1`
- `automation/Invoke-CrossApp-CorePerformance-Attribution.ps1`
- `automation/Validate-OpenAPI-Conformance.ps1`
- `automation/Validate-Domain-Vocabulary.ps1`
- `automation/generate_domain_product_discovery.py`
- `automation/generate_domain_product_certification.py`
- `automation/query_domain_product_discovery.py`
- `automation/generate_enterprise_mesh_maturity_matrix.py`
- `automation/validate_trust_telemetry.py`
- `automation/generate_live_trust_certification.py`
- `automation/Validate-Rounding-Consistency.ps1`
- `automation/Validate-Monetary-Float-Guard.ps1`
- `automation/Validate-Scalability-Availability.ps1`
- `automation/Validate-Durability-Consistency.ps1`
- `automation/Validate-Enterprise-Readiness.ps1`
- `automation/Audit-RFC-Conformance.ps1`
- `automation/Verify-Repo-Metadata.ps1`
- `automation/Validate-Automation-Config.ps1`
- `automation/Validate-Change-Test-Impact.ps1`
- `automation/Preflight-PR.ps1`
- `automation/run_heartbeat.py`
- `automation/heartbeat_sources.py`
- `automation/heartbeat_state.py`
- `automation/validate_heartbeat_contracts.py`
- `automation/heartbeat-config.json`
- `automation/service-map.json`
- `automation/task-profiles.json`
- `automation/repos.json`
- `automation/qa-matrix.json`

## Quick Start

Developer environment readiness:

```powershell
# Read-only inspect; writes output/developer-environment-readiness.json and .md
powershell -ExecutionPolicy Bypass -File automation/Validate-LotusDeveloperEnvironment.ps1 -Mode Inspect -Profile fast

# Sync governed Lotus Codex skills and AGENTS.md, preserving unknown local skills
powershell -ExecutionPolicy Bypass -File automation/Bootstrap-LotusDeveloperEnvironment.ps1 -Profile fast

# Explicit readiness gate; heavy platform runtime checks require the extended or platform profile
powershell -ExecutionPolicy Bypass -File automation/Validate-LotusDeveloperEnvironment.ps1 -Mode Validate -Profile extended
```

One-shot pulse:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Platform-Pulse.ps1
```

Pulse with conformance sweep:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Platform-Pulse.ps1 -IncludeConformance
```

Continuous agent loop:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Run-Agent.ps1
```

`Run-Agent.ps1` now executes five checks per iteration: repo sync, PR monitor, backend standards conformance validation, OpenAPI conformance validation, and domain vocabulary conformance validation.
It also validates RFC-0068 shared infrastructure ownership on every iteration, emits machine-readable status to `output/agent-status.json`, runs metadata validation every iteration, and performs full coverage + dependency rollup every N iterations (`-FullAuditEvery`, default `5`).

## Wiki Publication

Repo-local `wiki/` directories are the authored source of truth for GitHub wiki publication.
The `*.wiki.git` repositories are publication targets only.

Before merging wiki-relevant documentation, RFC, context, runbook, or operator-facing changes:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Sync-RepoWikis.ps1 -CheckOnly -Repository lotus-platform
```

PR checks use `-AllowUnpublishedSourceChanges` so branches that intentionally edit `wiki/` can pass
before publication. That warning is a post-merge publish obligation, not a reason to hand-edit the
GitHub wiki directly.

After merge, publish the source to the live GitHub wiki:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Sync-RepoWikis.ps1 -Publish -Repository lotus-platform
```

For coordinated cross-repo sweeps, add `-AllRepositories`. The platform repo check lane enforces
`-CheckOnly -Repository lotus-platform` so platform wiki drift is visible before PR merge.

## Domain-Product Discovery

Generate governed catalog, dependency graph, and markdown artifacts:

```powershell
python automation/generate_domain_product_discovery.py --generated-at-utc 2026-04-19T00:00:00Z
```

The generator reads `platform-contracts/domain-data-products/domain-product-source-manifest.v1.json`.
Repositories marked `source_mode: repo_native` are loaded from sibling repository
`contracts/domain-data-products/` directories, then validated as one federated declaration set
before generated artifacts are written.

Check that checked-in artifacts are current:

```powershell
python automation/generate_domain_product_discovery.py --check --generated-at-utc 2026-04-19T00:00:00Z
```

Query products approved for a consumer:

```powershell
python automation/query_domain_product_discovery.py list-products --approved-consumer lotus-risk
```

Inspect a product by governed identity:

```powershell
python automation/query_domain_product_discovery.py product --product-id lotus-performance:ReturnsSeriesBundle:v1
```

Inspect consumer dependencies and graph neighborhoods:

```powershell
python automation/query_domain_product_discovery.py consumer lotus-risk
python automation/query_domain_product_discovery.py graph-neighborhood repo:lotus-risk
```

The query CLI reads generated artifacts only. It does not redefine product ownership, trust
metadata, approved consumers, or dependency truth.

## Heartbeat Contracts

RFC-0095 heartbeat artifacts are governed by
`platform-contracts/heartbeat/heartbeat-status.schema.json`.

Validate the contract and first-wave example artifacts with:

```powershell
python automation/validate_heartbeat_contracts.py
```

The platform repo check lane runs this validator. It validates the heartbeat status contract,
examples, runner config, and suppression policy. Heartbeat artifacts are derived evidence; they do
not replace GitHub, local automation ledgers, mesh certification, wiki source, or runtime APIs as
source truth.

Generate the current heartbeat artifacts with:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Run-Heartbeat.ps1
```

For deterministic local or GitHub proof, pass explicit generation metadata:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Run-Heartbeat.ps1 -GeneratedAtUtc 2026-04-21T00:00:00Z -Branch feature/rfc0095-heartbeat-monitoring
```

The runner reads `automation/heartbeat-config.json` and writes:

- `output/heartbeat/heartbeat-status.json`
- `output/heartbeat/heartbeat-status.md`
- `output/heartbeat/heartbeat-issues.json`
- `output/heartbeat/heartbeat-state.json`

The default configuration is read-only and advisory. It enables local artifact-backed checks for:

- RFC-0094 background-run ledger evidence,
- RFC-0093/RFC-0073 agent-context validation evidence,
- enterprise mesh operating-report evidence.

GitHub PR monitor and wiki publication adapters are implemented but not enabled by default because
they require explicit upstream evidence (`output/pr-monitor.json` and `output/wiki-sync-status.json`)
from their owning automation. The `lotus_ai` workflow-pack adapter is also implemented but not
enabled by default until a governed runtime-status artifact or API capture is provided at the
configured path. Missing, malformed, stale, degraded, or failed evidence produces attention items
rather than a false healthy posture.

Repeated runs preserve attention `first_seen_at_utc` and update `last_seen_at_utc` through
`output/heartbeat/heartbeat-state.json`. Suppression policy is explicit and defaults to
`platform-contracts/heartbeat/heartbeat-suppressions.json`; blocking items are never suppressed.

Generate trust certification evidence for the generated catalog and dependency graph:

```powershell
python automation/generate_domain_product_certification.py --generated-at-utc 2026-04-19T00:00:00Z
```

Certification artifacts are written to:

- `generated/domain-product-certification-report.json`
- `generated/domain-product-certification-report.md`

The certification report checks product trust metadata, producer-approved consumers, consumer
dependency reciprocity, validation lanes, failure posture, and dependency-graph consistency.

Generate the RFC-0091 enterprise mesh maturity matrix:

```powershell
python automation/generate_enterprise_mesh_maturity_matrix.py --generated-at-utc 2026-04-20T00:00:00Z
```

The maturity matrix classifies every governed Lotus repository into the first enterprise maturity
wave, candidate expansion, explicit non-participant posture, API face, discovery UX, or platform
governance role. It also defines the candidate products required before Lotus can claim mature
enterprise mesh status.

Check that checked-in maturity artifacts are current:

```powershell
python automation/generate_enterprise_mesh_maturity_matrix.py --check --generated-at-utc 2026-04-20T00:00:00Z
```

Maturity artifacts are written to:

- `generated/enterprise-mesh-maturity-matrix.json`
- `generated/enterprise-mesh-maturity-matrix.md`

Generate an RFC-0091 self-service onboarding bundle for a new or promoted domain product:

```powershell
python automation/generate_domain_product_onboarding.py `
  --repository lotus-report `
  --product-name ClientReportEvidencePack `
  --product-version v1 `
  --authoritative-domain reporting `
  --product-family client_reporting `
  --output-directory output/domain-product-onboarding/lotus-report-client-report-evidence-pack
```

Validate a generated onboarding bundle before copying completed files into an owning repository:

```powershell
python automation/generate_domain_product_onboarding.py `
  --repository lotus-report `
  --product-name ClientReportEvidencePack `
  --product-version v1 `
  --output-directory output/domain-product-onboarding/lotus-report-client-report-evidence-pack `
  --check
```

The onboarding generator writes a producer declaration scaffold, telemetry scaffold, SLO policy,
access policy, evidence-pack policy, README, and onboarding checklist. The generated bundle is a
starting point for the owning repository; it is not platform-owned product truth until the domain
team replaces placeholders, adds repo-native tests, emits runtime telemetry, and passes mesh
certification.

Validate live trust telemetry snapshots:

```powershell
python automation/validate_trust_telemetry.py path\to\telemetry-snapshots
```

The telemetry validator checks RFC-0087 runtime trust snapshots against the generated
domain-product catalog and governed trust vocabulary. It rejects unknown products, ungoverned
freshness/completeness/reconciliation/data-quality states, blocked snapshots without reasons, and
observed trust metadata that the product did not declare.

Generate live trust certification artifacts from validated telemetry snapshots:

```powershell
python automation/generate_live_trust_certification.py path\to\telemetry-snapshots --generated-at-utc 2026-04-19T00:00:00Z
```

The generated live trust certification report classifies each telemetry snapshot as `certified` or
`attention_required` using deterministic freshness, completeness, reconciliation, data-quality,
lineage, and blocking rules.

Collect trust telemetry for RFC-0091 certification:

```powershell
python automation/collect_trust_telemetry.py --generated-at-utc 2026-04-20T00:00:00Z
```

The collector prefers runtime snapshots from sibling repository
`output/trust-telemetry/runtime/` directories. If runtime evidence is missing for a product, it
falls back to the repo-native `contracts/trust-telemetry/` static fixture and records that fallback
in the manifest. The manifest and copied snapshots are written to:

- `output/trust-telemetry/collection/trust-telemetry-collection-manifest.json`
- `output/trust-telemetry/collection/snapshots/`

Use the collected snapshot directory as the input to live trust certification when proving the
runtime-vs-fixture evidence boundary:

```powershell
python automation/generate_live_trust_certification.py output/trust-telemetry/collection/snapshots --generated-at-utc 2026-04-20T00:00:00Z
```

Validate RFC-0091 mesh SLO policies:

```powershell
python automation/validate_mesh_slo_policies.py
```

Evaluate SLO drift against collected telemetry:

```powershell
python automation/validate_mesh_slo_policies.py --telemetry-path output/trust-telemetry/collection/snapshots
```

Mesh SLO policies live under `platform-contracts/mesh-slo/`. They define first-wave thresholds for
freshness, completeness, reconciliation, data quality, lineage, escalation owner, and remediation.
The mesh certification gate consumes those policies and emits certification issues when telemetry
drifts from the policy.

Validate RFC-0091 mesh access policies:

```powershell
python automation/validate_mesh_access_policies.py
```

Mesh access policies live under `platform-contracts/mesh-access/`. They define first-wave tenant
scope, allowed roles, allowed use cases, denial posture, audit owner, and gateway-only consumer
publication. The mesh certification gate validates the policies so missing or malformed access
governance fails certification before gateway or Workbench can present product access.

RFC-0091 maturity-wave scope now includes six required products:

- `lotus-core:PortfolioStateSnapshot:v1`
- `lotus-performance:ReturnsSeriesBundle:v1`
- `lotus-risk:RiskMetricsReport:v1`
- `lotus-advise:AdvisoryProposalLifecycleRecord:v1`
- `lotus-report:ClientReportEvidencePack:v1`
- `lotus-manage:PortfolioActionRegister:v1`

The required product scope is centralized in `automation/mesh_maturity_scope.py`. Reuse that module
for platform automation instead of copying the product list into new scripts.

Generate RFC-0091 certification history and evidence-pack manifests:

```powershell
python automation/generate_mesh_evidence_pack.py --generated-at-utc 2026-04-20T00:00:00Z --audience customer-authorized
```

Evidence policies live under `platform-contracts/mesh-evidence/`. The generator reads the mesh
certification status, SLO policy, access policy, catalog, and live trust evidence, then writes:

- `output/mesh-evidence-packs/<pack-id>/evidence-pack-manifest.json`
- `output/mesh-evidence-packs/<pack-id>/evidence-pack-manifest.md`
- `output/mesh-evidence-packs/<pack-id>/certification-history-record.json`
- `output/mesh-evidence-packs/certification-history/<pack-id>.json`

Use `--audience customer-public`, `--audience customer-authorized`, or `--audience operator` to
control field filtering. Public customer packs include only public customer evidence and exclude
restricted telemetry paths, source artifacts, and consumer entitlement details.

Run the RFC-0089 mesh certification gate:

```powershell
# Platform-only CI smoke; does not require sibling gateway/workbench checkouts.
python automation/mesh_certification_gate.py --mode advisory --generated-at-utc 2026-04-20T00:00:00Z --skip-publication-checks

# Local blocking proof with sibling lotus-core, lotus-performance, lotus-risk, lotus-advise,
# lotus-report, lotus-manage, lotus-gateway, and lotus-workbench checkouts next to lotus-platform.
python automation/mesh_certification_gate.py --mode blocking --generated-at-utc 2026-04-20T00:00:00Z --require-sibling-repos
```

The mesh certification gate composes the catalog, source manifest, RFC-0087 telemetry validator,
live trust certification generator, mesh SLO policy, mesh access policy, evidence-pack policy,
required product lifecycle posture, gateway publication drift check, and Workbench BFF-only
consumption drift check. It writes operator artifacts to `output/mesh-certification/`:

- `mesh-certification-status.json`
- `mesh-certification-status.md`
- `mesh-certification-issues.json`
- `enterprise-mesh-certification-status.json`
- `enterprise-mesh-certification-status.md`
- `enterprise-mesh-certification-issues.json`

The enterprise status includes operator-facing maturity check families for telemetry, SLO, access,
lifecycle, evidence, catalog, gateway, and Workbench drift. The `enterprise-*` files are aliases
for RFC-0091 evidence-pack and workflow consumers; the original `mesh-*` files remain for RFC-0089
compatibility.

For failure handling, use [Mesh Certification Gate Runbook](../docs/operations/mesh-certification-gate-runbook.md).

Generate the RFC-0092 enterprise mesh operating report after a certification run:

```powershell
python automation/generate_enterprise_mesh_operating_report.py --generated-at-utc 2026-04-20T00:00:00Z
```

The mesh certification gate now writes the operating report automatically alongside certification
status artifacts:

- `output/mesh-certification/enterprise-mesh-operating-report.json`
- `output/mesh-certification/enterprise-mesh-operating-report.md`

The operating report consumes the current enterprise mesh certification status and optional
certification-history records from `output/mesh-evidence-packs/certification-history/`. It reports
production readiness, limited-history posture, drift trends, regressions, product operating
posture, and escalation ownership. It is operational evidence, not a product registry or customer
evidence export.

One-shot PR health (with failing check detection):

```powershell
powershell -ExecutionPolicy Bypass -File automation/PR-Monitor.ps1 -IncludeChecks
```

`PR-Monitor.ps1` now treats repositories without check-runs as non-fatal and records empty checks instead of failing the agent loop.

PR monitor with custom search filter:

```powershell
powershell -ExecutionPolicy Bypass -File automation/PR-Monitor.ps1 -PrSearch "state:open label:ready-for-review" -IncludeChecks
```

Close PR loop (monitor checks, queue auto-merge, clean merged branches):

```powershell
powershell -ExecutionPolicy Bypass -File automation/Close-PR-Loop.ps1
```

Prune merged or stale closed remote branches using GitHub as the source of truth:

```powershell
# Dry-run a single repository
powershell -ExecutionPolicy Bypass -File automation/Prune-MergedRemoteBranches.ps1 -Repo sgajbi/lotus-core

# Dry-run all governed Lotus repositories
powershell -ExecutionPolicy Bypass -File automation/Prune-MergedRemoteBranches.ps1 -AllLotusRepos

# Apply after reviewing the dry-run report
powershell -ExecutionPolicy Bypass -File automation/Prune-MergedRemoteBranches.ps1 -AllLotusRepos -Apply
```

This script intentionally queries GitHub branches and PR state directly instead of trusting local `git branch -r`, because some Lotus clones track only `main` locally.

Continuous PR lifecycle watch loop:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Close-PR-Loop.ps1 -Watch -IntervalSeconds 30
```

One iteration only:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Run-Agent.ps1 -Once
```

Targeted lotus-core refresh:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Service-Refresh.ps1 -ProjectPath C:/Users/Sandeep/projects/lotus-core -Services query_service demo_data_loader
```

Changed-files based refresh (recommended):

```powershell
powershell -ExecutionPolicy Bypass -File automation/Service-Refresh.ps1 -ProjectPath C:/Users/Sandeep/projects/lotus-core -ChangedOnly -BaseRef origin/main
```

Dry run:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Service-Refresh.ps1 -ProjectPath C:/Users/Sandeep/projects/lotus-gateway -ChangedOnly -DryRun
```

## Parallel Offload Profiles

Run a profile in this terminal:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Run-Parallel-Tasks.ps1 -Profile fast-feedback -MaxParallel 3
```

Bootstrap local dependencies first:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Run-Parallel-Tasks.ps1 -Profile bootstrap-env -MaxParallel 2
```

Docker-first CI parity (recommended for stability):

```powershell
powershell -ExecutionPolicy Bypass -File automation/Run-Parallel-Tasks.ps1 -Profile docker-ci-parity -MaxParallel 2
```

Start a detached background run:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Start-Background-Run.ps1 -Profile ci-parity -MaxParallel 2
```

Fast alignment background run (recommended for day-to-day platform sync):

```powershell
powershell -ExecutionPolicy Bypass -File automation/Start-Background-Run.ps1 -Profile platform-alignment -MaxParallel 3
```

Check background run status:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Check-Background-Runs.ps1
```

`Start-Background-Run.ps1` assigns a deterministic `runId`, `engineering_task_id`, expected result
artifact paths, and RFC-0094 task-ledger metadata. `Check-Background-Runs.ps1` refreshes
`output/background-runs.json` with governed lifecycle states:

- `RUNNING` while the launched process is still active,
- `SUCCEEDED` only when the expected result artifact exists and all child task exit codes are zero,
- `FAILED` when the result artifact exists but contains failed task results or cannot be parsed,
- `LOST` when the process ended before the expected result artifact was written.

The monitor also preserves evidence references for logs, JSON results, and Markdown summaries so
resumed sessions can inspect durable artifacts instead of relying on chat history.

Record a governed RFC-0096 delegated task:

```powershell
python automation/delegation_task_ledger.py create --record platform-contracts/agent-engineering/examples/delegation-exploration-valid.json --ledger-path output/delegated-tasks.json --owner lotus-platform --requested-at 2026-04-21T00:00:00Z
```

Update delegated task posture:

```powershell
python automation/delegation_task_ledger.py update-status --ledger-path output/delegated-tasks.json --engineering-task-id <engineering_task_id> --status CANCELLED --ended-at 2026-04-21T01:00:00Z --error-summary "Main agent handled the work locally."
```

Delegated task records use the RFC-0094 task-ledger shape plus the RFC-0096 delegation policy
contract. They are ledger evidence for bounded agent work, not a replacement for main-agent review,
GitHub checks, repository files, or test results.

Record a delegated worker return envelope and main-agent review:

```powershell
python automation/delegation_task_ledger.py record-return --ledger-path output/delegated-tasks.json --engineering-task-id <engineering_task_id> --output output/delegation-return.json
python automation/delegation_task_ledger.py record-review --ledger-path output/delegated-tasks.json --engineering-task-id <engineering_task_id> --review-status ACCEPTED --reviewed-by <owner> --review-summary "Diff reviewed and focused checks passed."
```

`record-return` validates returned files against the delegated write scope. `record-review` is the
only helper path that marks returned delegated implementation as accepted; review remains a
main-agent responsibility.

Watch mode (refresh every 20s):

```powershell
powershell -ExecutionPolicy Bypass -File automation/Check-Background-Runs.ps1 -Watch -IntervalSeconds 20
```

Prune completed runs from state while checking:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Check-Background-Runs.ps1 -PruneCompleted
```

Summarize recent failures only:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Summarize-Task-Failures.ps1 -Latest 3
```

Run governed canonical front-office QA readiness automation:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp
```

This delegates to the governed `lotus-workbench` runtime and validation flow, uses the seeded front-office portfolio `PB_SG_GLOBAL_BAL_001`, and writes wrapper evidence to:

- `output/front-office-qa/latest.json`
- `output/front-office-qa/latest.md`

Write a demo screenshot pack to a caller-provided directory while also producing platform evidence:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 `
  -ScreenshotDirectory C:\Users\Sandeep\AppData\Local\Temp\lotus-risk-module-shots
```

The screenshot directory receives `live-validation-summary.json`, `SHOT-INDEX.md`, and stable
Workbench product-surface captures only after canonical endpoint, calculation, and panel validation
passes.
The live summary now also carries the governed canonical contract identity and version from
`RFC-0076`, so downstream evidence consumers can prove which demo-data contract backed the run.

Clean stale Lotus Docker containers and volumes before the governed bring-up:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -Clean -BringUp -BuildImages
```

Reset only `lotus-core` Docker state before reseeding the governed portfolio when stale core state blocks validation:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp -CleanCoreState -SeedWaitSeconds 1200
```

Rebuild local service images as part of the clean-core reseed when a live proof must include unmerged branch changes:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp -CleanCoreState -BuildImages -SeedWaitSeconds 1200
```

Run full explicit Lotus cleanup, including matching local Lotus images, without starting the stack:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -Clean -RemoveImages
```

`-Clean` removes stale Lotus containers and Lotus/PBWM/performance volumes after delegating to the governed `lotus-workbench` teardown. `-CleanCoreState` delegates to the Workbench runtime's targeted `lotus-core` reset before reseeding, which is narrower than full cleanup and useful after load/performance data has left core readiness stale. Add `-BuildImages` when proof depends on local branch changes that have not yet been published into existing Docker images. `-RemoveImages` is opt-in because it makes the next startup slower. The evidence summary records Docker artifact counts, clean-core posture, seed wait, and run status.

For a clean demo rebuild from stale local state:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -Clean -BringUp -BuildImages -KeepRunning
```

Troubleshoot failures by category:

1. hostname failures: run `automation/Sync-Dev-Ingress-Hosts.ps1 -Apply` from an elevated shell,
2. readiness failures: inspect the failing canonical service health endpoint in `latest.json`,
3. seed failures: rerun the `lotus-core` front-office seed verifier for `PB_SG_GLOBAL_BAL_001`,
4. calculation failures: inspect `calculationChecks` in `live-validation-summary.json`,
5. blank or degraded panel failures: inspect `panelClassifications` before taking screenshots,
6. screenshot failures: verify the caller-provided `-ScreenshotDirectory` exists and is writable.

Run backend/runtime QA readiness automation (startup + API/log/metrics/standards checks):

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-Platform-QA.ps1 -BringUp
```

Run the seeded analytics maturity invariant against `lotus-core`:

```powershell
python automation/core_seeded_analytics_maturity_validation.py --ingestion-url http://core-ingestion.dev.lotus --query-control-plane-url http://core-control.dev.lotus
```

Run the reusable lotus-core -> lotus-performance cross-app scenario:

```powershell
python automation/core_performance_cross_app_validation.py --scenario automation/scenarios/core-performance/fund_buy_foreign_stock_explicit_window.json --ingestion-url http://core-ingestion.dev.lotus --query-control-plane-url http://core-control.dev.lotus --performance-url http://performance.dev.lotus
```

This scenario suite seeds real-world funding and funded-trade stories into `lotus-core`, then validates both:
- lotus-core analytics-input economic integrity
- lotus-performance stateful explicit-window TWR and contribution behavior
- cross-surface consistency between TWR, contribution, benchmark, and attribution for a shared explicit-window story

Result artifacts are written to:
- `output/core-performance-cross-app/latest.json`

Run the full cross-app scenario suite:

```powershell
python automation/core_performance_cross_app_suite.py --ingestion-url http://core-ingestion.dev.lotus --query-control-plane-url http://core-control.dev.lotus --performance-url http://performance.dev.lotus
```

Suite artifact:
- `output/core-performance-cross-app/suite-latest.json`

Run these cross-app scenarios serially against the shared local stack. They seed live platform state and should not be run in parallel if you want deterministic economic assertions.
Interpret the suite by `expectation_met_count` and each scenario's `expected_posture`, not only by raw failed-check counts. The current core-performance pack is now fully green and acts as a reusable regression suite for healthy cash-only, liquidation/re-entry, staged-flow, same-currency funded-trade, cross-currency funded-trade, single-position cross-surface consistency, multi-position cross-surface consistency, and internal-rebalance consistency stories.

Run backend/runtime QA and auto-create GitHub issues for each detected defect:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-Platform-QA.ps1 -BringUp -CreateIssues
```

Validate RFC-0068 shared infrastructure ownership boundaries:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Validate-Shared-Infrastructure-Ownership.ps1
```

Validate RFC-0071 centralized service addressing drift:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Validate-Service-Addressing.ps1
```

Validate live canonical `*.dev.lotus` ingress reachability:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Validate-Dev-Ingress-Smoke.ps1
```

The smoke artifact now records a `failure_posture` for each failed check:
- `dns_resolution_failed`
- `http_error`
- `connection_refused`
- `timeout`
- `transport_error`

Explain the current ingress rollout state and the exact next operator step:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Explain-Dev-Ingress-Status.ps1
```

When routed services are the problem, the explainer emits the exact `docker compose up -d ...` command for the affected `platform-stack` services.
When the ingress edge itself is the likely fault, it recommends `docker compose up -d dev-ingress` first.
For `http_error` and `timeout` postures, it now recommends targeted `docker compose logs --tail=200 ...` inspection before the refresh command so the likely failure mode is visible first.

Preview or apply the managed local hosts-file block for dev ingress:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Sync-Dev-Ingress-Hosts.ps1
powershell -ExecutionPolicy Bypass -File automation/Sync-Dev-Ingress-Hosts.ps1 -Apply
```

Operational rule for RFC-0071 local ingress:

1. keep `platform-stack/dev-ingress/hosts.example` as the source of truth for required hostnames
2. use `Sync-Dev-Ingress-Hosts.ps1` to preview or apply that block
3. bring up ingress
4. validate with `Validate-Dev-Ingress-Smoke.ps1`
5. classify with `Explain-Dev-Ingress-Status.ps1`

Do not debug app-level routing before this operator loop is green. A browser failure on
`workbench.dev.lotus` or `gateway.dev.lotus` is often just missing hosts-file mappings or a dead
ingress edge, not an application defect.

Run the reusable cross-app `lotus-core` -> `lotus-performance` TWR + benchmark scenario:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-CrossApp-CorePerformance-TwrBenchmark.ps1 -BringUp
```

Run the full core -> performance baseline across all engines using reused stable scenarios inferred from the latest artifacts:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-CrossApp-CorePerformance-Baseline.ps1 -SkipSeed
```

Run the same cross-app validators from GitHub Actions on a self-hosted runner:

- Workflow: `.github/workflows/platform-end-to-end-validation.yml`
- Recommended day-to-day mode: `validation_profile=core-performance-green-lanes`
- Recommended deeper manual mode while attribution alignment is still under investigation: `validation_profile=core-performance-baseline` with `scenario_mode=skip_seed`
- The runner must already be able to reach live `lotus-core` and `lotus-performance` base URLs, and `skip_seed` mode expects an existing stable scenario on that runner unless explicit suffixes are supplied

Reuse an already-seeded stable scenario instead of ingesting a fresh one:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-CrossApp-CorePerformance-TwrBenchmark.ps1 -SkipSeed -ScenarioSuffix 030053
```

Run the reusable cross-app `lotus-core` -> `lotus-performance` MWR scenario:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-CrossApp-CorePerformance-Mwr.ps1 -BringUp
```

Reuse an already-seeded stable MWR scenario instead of ingesting a fresh one:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-CrossApp-CorePerformance-Mwr.ps1 -SkipSeed -ScenarioSuffix <existing-mwr-suffix>
```

Run the reusable cross-app `lotus-core` -> `lotus-performance` returns-series scenario:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-CrossApp-CorePerformance-ReturnsSeries.ps1 -BringUp
```

Reuse an already-seeded stable returns-series scenario instead of ingesting a fresh one:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-CrossApp-CorePerformance-ReturnsSeries.ps1 -SkipSeed -ScenarioSuffix 030053
```

Run the reusable cross-app `lotus-core` -> `lotus-performance` contribution scenario:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-CrossApp-CorePerformance-Contribution.ps1 -BringUp
```

Reuse an already-seeded stable contribution scenario instead of ingesting a fresh one:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-CrossApp-CorePerformance-Contribution.ps1 -SkipSeed -ScenarioSuffix 030053
```

Run the reusable cross-app `lotus-core` -> `lotus-performance` attribution scenario:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-CrossApp-CorePerformance-Attribution.ps1 -BringUp
```

Reuse an already-seeded stable attribution scenario while fresh-seed analytics readiness is under investigation:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-CrossApp-CorePerformance-Attribution.ps1 -SkipSeed -ScenarioSuffix 030053
```

Validate cross-cutting platform contract compliance:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Validate-Platform-Contract.ps1
```

Validate backend standards conformance across all backend repositories:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Validate-Backend-Standards.ps1
```

Validate OpenAPI contract quality conformance across backend repositories:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Validate-OpenAPI-Conformance.ps1
```

Validate domain vocabulary conformance across backend repositories:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Validate-Domain-Vocabulary.ps1
```

Validate cross-service rounding and precision consistency:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Validate-Rounding-Consistency.ps1
```

Validate monetary-float regression guard across backend repositories:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Validate-Monetary-Float-Guard.ps1
```

Validate scalability and availability compliance matrix across backend repositories:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Validate-Scalability-Availability.ps1
```

Validate durability and consistency compliance matrix across backend repositories:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Validate-Durability-Consistency.ps1
```

Validate enterprise readiness baseline compliance matrix across backend repositories:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Validate-Enterprise-Readiness.ps1
```

Build RFC conformance inventory and centralized alignment backlog across repositories:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Audit-RFC-Conformance.ps1
```

Validate repository metadata (default branches and preflight command presence):

```powershell
powershell -ExecutionPolicy Bypass -File automation/Verify-Repo-Metadata.ps1
```

Validate automation config integrity (repos/profiles/command file refs):

```powershell
powershell -ExecutionPolicy Bypass -File automation/Validate-Automation-Config.ps1
```

Validate change/test impact so source changes include test updates:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Validate-Change-Test-Impact.ps1
```

Validate Lotus naming conformance (legacy-name drift detector):

```powershell
powershell -ExecutionPolicy Bypass -File automation/Validate-Lotus-Naming.ps1
```

Detect queued/in-progress PR checks that appear stalled:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Detect-Stalled-PR-Checks.ps1 -StaleMinutes 20
```

Run strict PR preflight for one repository before pushing:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Preflight-PR.ps1 -Repo lotus-report -Mode full
```

Run fast PR preflight while iterating:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Preflight-PR.ps1 -Repo lotus-report -Mode fast
```

Generate test-pyramid and coverage baseline across backend services:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Measure-Test-Pyramid.ps1 -RunCoverage
```

Generate dependency vulnerability rollup across backend services:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Generate-Dependency-Vulnerability-Rollup.ps1
```

Enforce repository governance policy (branch protection + auto-merge + review requirements):

```powershell
powershell -ExecutionPolicy Bypass -File automation/Enforce-Repository-Governance.ps1 -Apply
```

Validate repository hygiene and dependency authority for a scaffolded or existing backend repo:

```powershell
python automation/validate_repository_hygiene.py --repo-root C:/Users/Sandeep/projects/lotus-manage
```

Render the human-readable ecosystem registries from the governed context manifest:

```powershell
python automation/render_context_registries.py
```

Validate the full RFC-0073 engineering context system contract:

```powershell
python automation/validate_engineering_context_system.py
```

Artifacts:
- `output/engineering-context-system-validation.json`
- `output/engineering-context-system-validation.md`

Validate Lotus skill alignment against the governed context system:

```powershell
python automation/validate_lotus_skill_alignment.py
```

Artifacts:
- `output/lotus-skill-alignment-validation.json`
- `output/lotus-skill-alignment-validation.md`

Validate workflow security and permissions posture across platform workflows and templates:

```powershell
python automation/validate_workflow_security.py
```

Validate GitHub Actions version/runtime posture across platform workflows and templates:

```powershell
python automation/validate_workflow_action_runtime.py
```

Validate container build and image baseline posture across backend scaffold templates:

```powershell
python automation/validate_container_build_baseline.py
```

Validate platform end-to-end coverage profiles against the workflow and entrypoint contract:

```powershell
python automation/validate_platform_validation_coverage.py
```

Bootstrap the isolated platform automation Python runtime:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Resolve-PlatformAutomationPython.ps1
```

Validate current repository governance drift against the platform policy:

```powershell
python automation/validate_repository_governance.py
```

Scaffold a new standards-compliant Lotus backend and auto-register it in automation:

```powershell
powershell -ExecutionPolicy Bypass -File automation/New-Lotus-Service.ps1 -ServiceName lotus-foo -Description "New domain service"
```

Profiles currently defined in `automation/task-profiles.json`:
- `bootstrap-env`
- `fast-feedback`
- `docker-build`
- `ci-parity`
- `docker-ci-parity`
- `pas-data-smoke`
- `migration-quality`
- `coverage-pyramid-baseline`
- `backend-standards-conformance`
- `enforce-repository-governance`
- `openapi-conformance-baseline`
- `domain-vocabulary-conformance`
- `lotus-naming-conformance`
- `repo-metadata-validation`
- `automation-integrity`
- `change-test-impact`
- `durability-consistency-baseline`
- `enterprise-readiness-baseline`
- `rfc-conformance-baseline`
- `pr-lifecycle`
- `platform-alignment`
- `qa-platform-readiness`
- `autonomous-foundation`

New repo included in shared automation:
- `lotus-report`

Note: profiles are Windows-native and do not require `make`.
For `ci-parity`, coverage-scoped pytest steps use `set COVERAGE_FILE=... &&` syntax so they run correctly under `cmd /c` on Windows.
`ci-parity` also skips host-level `pip check` in lotus-manage/lotus-performance to avoid shared-environment false failures; use `docker-ci-parity` for strict isolated parity.
For lotus-core, `bootstrap-env` intentionally installs a minimal local dependency set for query-service unit checks instead of full multi-service editable bootstrap.

## Migration Quality Standard

For migration work, run strict async checks in background:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Start-Background-Run.ps1 -Profile migration-quality -MaxParallel 3
```

Then monitor:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Check-Background-Runs.ps1 -Watch -IntervalSeconds 20
```

## Output Artifacts

- `output/pr-monitor.json`
- `output/pr-monitor.md`
- `output/pr-lifecycle.json`
- `output/pr-lifecycle.md`
- `output/stalled-pr-checks.json`
- `output/stalled-pr-checks.md`
- `output/agent-status.md`
- `output/agent-status.json`
- `output/task-runs/*.json`
- `output/task-runs/*.md`
- `output/task-runs/*.out.log`
- `output/task-runs/*.err.log`
- `output/background-runs.json`
- `output/dev-ingress-smoke.json`
- `output/dev-ingress-smoke.md`
- `output/dev-ingress-status.json`
- `output/dev-ingress-status.md`
- `output/test-coverage-summary.json`
- `output/test-coverage-summary.md`
- `output/dependency-vulnerability-rollup.json`
- `output/dependency-vulnerability-rollup.md`
- `output/backend-standards-conformance.json`
- `output/backend-standards-conformance.md`
- `output/repository-governance-enforcement.json`
- `output/repository-governance-enforcement.md`
- `output/repository-governance-validation.json`
- `output/repository-governance-validation.md`
- `output/repository-hygiene-validation.json`
- `output/repository-hygiene-validation.md`
- `output/workflow-security-validation.json`
- `output/workflow-security-validation.md`
- `output/workflow-action-runtime-validation.json`
- `output/workflow-action-runtime-validation.md`
- `output/openapi-conformance-summary.json`
- `output/openapi-conformance-summary.md`
- `output/domain-vocabulary-conformance.json`
- `output/domain-vocabulary-conformance.md`
- `output/rounding-consistency-report.json`
- `output/rounding-consistency-report.md`
- `output/monetary-float-guard-summary.json`
- `output/monetary-float-guard-summary.md`
- `output/durability-consistency-compliance.json`
- `output/durability-consistency-compliance.md`
- `output/enterprise-readiness-compliance.json`
- `output/enterprise-readiness-compliance.md`
- `output/rfc-conformance-inventory.json`
- `output/rfc-conformance-inventory.md`
- `output/rfc-conformance-backlog.json`
- `output/rfc-conformance-backlog.md`
- `output/backend-governance-enforcement.json`
- `output/backend-governance-enforcement.md`
- `output/repo-metadata-validation.json`
- `output/repo-metadata-validation.md`
- `output/automation-config-validation.json`
- `output/automation-config-validation.md`
- `output/change-test-impact.json`
- `output/change-test-impact.md`
- `output/qa/*/qa-summary.json`
- `output/qa/*/qa-summary.md`
- `output/qa/*/qa-issues.json`
- `output/qa/*/evidence/*.md`
- `output/front-office-qa/latest.json`
- `output/front-office-qa/latest.md`
- `output/lotus-naming-conformance.json`
- `output/lotus-naming-conformance.md`
- `output/preflight/*.json`
- `output/preflight/*.md`

## Governance

This folder is the source of truth for platform-wide automation and agent workflows.
Application repositories should reference or consume this toolkit instead of maintaining divergent copies.

PPD acts as a cross-cutting platform application: standards, contracts, validation scripts, and operating conventions are maintained here and consumed by all service repositories.

## Legacy Workspace Cleanup

After Lotus cutover, remove legacy local folders:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Cleanup-Legacy-Workspace.ps1
powershell -ExecutionPolicy Bypass -File automation/Cleanup-Legacy-Workspace.ps1 -Apply
```



## Automatic Onboarding

Automation scope derives from `automation/repos.json` for all `lotus-*` repos (excluding `lotus-platform` where appropriate).

When scaffolding a new service with `New-Lotus-Service.ps1`, automation registration updates by default:
- `automation/repos.json`
- `automation/service-map.json`
- `automation/repository-governance-policy.json`
- `automation/validate_repository_governance.py`
- `automation/test-coverage-policy.json`

This ensures new services inherit CI/CD, governance, and quality baselines without manual wiring.
