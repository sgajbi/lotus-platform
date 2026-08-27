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
- `automation/Detect-Stalled-Workflow-Runs.ps1`
- `automation/Prune-MergedRemoteBranches.ps1`
- `automation/Platform-Pulse.ps1`
- `automation/Run-Heartbeat.ps1`
- `automation/Run-Agent.ps1`
- `automation/Service-Refresh.ps1`
- `automation/Run-Parallel-Tasks.ps1`
- `automation/Start-Background-Run.ps1`
- `automation/Cancel-Background-Run.ps1`
- `automation/repository_background_task.py`
- `automation/background_task_cancellation.py`
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
- `automation/validate_bank_readiness_control_catalog.py`
- `automation/validate_deployment_promotion_manifest.py`
- `automation/heartbeat-config.json`
- `automation/service-map.json`
- `automation/task-profiles.json`
- `automation/repos.json`
- `automation/qa-matrix.json`

## RFC Issue Coverage Audit

Use the issue-discovery skill-owned auditor when an RFC proof, blueprint, or blocker contract lists
owner-repo GitHub issues and you need a durable completeness snapshot before claiming RFC backlog,
slice, or closure readiness.

Read-only audit against live GitHub:

```powershell
python codex\skills\lotus-app-issue-discovery\scripts\audit_rfc_issue_coverage.py `
  --contract ..\lotus-idea\contracts\implementation-proof\rfc0002-blueprint-scope-coverage.v1.json
```

Strict mode for CI or pre-closure checks:

```powershell
python codex\skills\lotus-app-issue-discovery\scripts\audit_rfc_issue_coverage.py `
  --contract <path-to-rfc-issue-reference-contract.json> `
  --strict
```

The command writes `output/rfc-issue-coverage-audit.json` and
`output/rfc-issue-coverage-audit.md`. It verifies each referenced issue exists, has the RFC label,
has each required `rfc/<RFC>/slice-*` label implied by the contract entry, and reports issue state,
status labels, priority labels, blocked/closed posture, duplicate/superseded posture, and exact
reviewable `gh issue edit` commands for missing labels. It does not mutate GitHub by default.

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

Canonical front-office QA writes timestamped JSON, Markdown, and runtime transcript artifacts under
`output/front-office-qa/`, with `latest.json`, `latest.md`, and `latest.log` maintained for the
most recent run. Treat the runtime transcript as part of the evidence bundle: it preserves seed
readiness progression, retry warnings, and teardown output that may not appear in the structured
live validation summary.

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

## Bank-Readiness Control Catalog

Validate the versioned control catalog before relying on it for repository assessment or issue
discovery:

```powershell
python automation/validate_bank_readiness_control_catalog.py
```

The catalog is the machine-readable authority for stable control identifiers, evidence classes,
repository applicability, and enforcement posture. The implementation playbook explains how to use
those controls without duplicating their definitions.

Validate the governed evidence-class vocabulary and closed legacy mapping before comparing
blocker-clearing proof artifacts with platform or bank-readiness evidence:

```powershell
python automation/validate_evidence_class_vocabulary.py
```

The canonical persisted proof vocabulary is defined in
`platform-contracts/evidence-classification/evidence-class-vocabulary.v1.json`. The older
`source_design_contract` and `local_test_execution` terms remain valid only through the explicit
legacy mapping for stable bank-readiness and historical evidence contexts.

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
in the manifest. Default collection includes required maturity producers plus platform-tracked
certification-candidate producers such as `lotus-idea`; candidate snapshots are collected for
evidence and operator visibility without making them required maturity products. JSON artifacts in
those directories that are not RFC-0087 telemetry snapshots are recorded as info-level
`ignored_non_snapshot_json` entries rather than blocking the collection. The manifest and copied
snapshots are written to:

- `output/trust-telemetry/collection/trust-telemetry-collection-manifest.json`
- `output/trust-telemetry/collection/snapshots/`

Use the collected snapshot directory as the input to live trust certification when proving the
runtime-vs-fixture evidence boundary:

```powershell
python automation/generate_live_trust_certification.py output/trust-telemetry/collection/snapshots --generated-at-utc 2026-04-20T00:00:00Z
```

Validate bounded RFC-0002 platform consumption of `lotus-idea` proof classes:

```powershell
python automation/validate_lotus_idea_rfc0002_platform_proof_consumption.py
```

This validator recognizes `lotus-idea.outbox-broker-runtime-execution.v1` and
`lotus-idea.outbox-consumer-runtime-execution.v1` as bounded runtime-execution evidence, and it
reconciles platform-owned cost-attribution plus deployment-promotion readiness as bounded
operational proof. It also reconciles Idea mesh candidate catalog, policy, and telemetry coverage
as bounded mesh-readiness proof. Broker proof may clear only the external broker runtime dependency marker.
Downstream-consumer proof may clear only the Advise/Manage/Report consumer runtime dependency
marker. Cost-attribution proof may clear only the contract-consumable marker. Deployment-promotion
readiness may clear only the pending-manifest-consumable marker. Mesh readiness may clear only the
candidate catalog/policy-consumable marker. The validator deliberately fails if any proof clears
platform mesh event publication, Gateway/Workbench live journey, protected FinOps execution,
attested cost verification, live deployed-digest observation, protected migration execution,
data-product certification, supported-feature promotion, required-product promotion, or
production-certification blockers.

### Authenticated BFF principal-session contract

```powershell
python automation/validate_bff_principal_session_contracts.py
python -m pytest tests/unit/test_bff_principal_session_contracts.py -q
```

This validator protects `platform-contracts/bff-principal-session/`: the source-safe
session-to-principal schema, non-certifying fixture posture, least-privilege Gateway header
projection, hostile browser authority-header rejection, and certification controls that must remain
false until a bank-approved IdP/session authority and consumer proof exist. It is a contract and
fixture gate, not a production authentication implementation.

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

# Branch-current advisory proof for active repo-native declaration or telemetry changes. This
# writes derived catalog artifacts under the output directory and does not mutate checked-in
# generated files.
python automation/mesh_certification_gate.py --mode advisory --generated-at-utc 2026-04-20T00:00:00Z --catalog-source current-repo-native --skip-publication-checks

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

The dry run reports repository-governed, non-secret Compose environment and expected published
ports. `lotus-manage` refreshes always preserve the canonical shared-stack posture: host port 8001,
stateful Core sourcing/workflow settings, and Core endpoints on 8202/8201. After recreation the
script polls Compose JSON and fails unless every selected service is running, configured health is
healthy, and required published ports match. Governed environment is process-scoped and restored
after the command; credential-bearing or process-critical environment names are rejected.

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

Launch one repository-native target without editing the central profile catalog:

```powershell
$repositoryRoot = "C:\path\to\lotus-core"
$head = git -C $repositoryRoot rev-parse HEAD
powershell -ExecutionPolicy Bypass -File automation/Start-Background-Run.ps1 `
  -Repository lotus-core -TargetType make -Target profile-derived-state-daily `
  -ExpectedHead $head -RequireClean `
  -RequiredArtifact "output/task-runs/*-bank-day-load.json" `
  -ComposeCleanupPlanPath <compose-cleanup-plan.json>
```

Repository mode accepts only typed `make`, `npm`, `python`, or `powershell` targets. The repository
must resolve exactly once from `automation/repos.json`; Make/NPM target names are character-
validated; script paths must resolve inside that repository; and arguments are serialized as an
argv array rather than evaluated through `cmd`. Use `-TargetArgument @("value1", "value2")` from
PowerShell or `-TargetArgumentsJson '["value1","value2"]'` from a native caller. Optional
`-ExpectedHead`, `-RequireClean`, and `-RequiredArtifact` fences are checked at launch and again by
the detached runner. A launch must also declare cleanup posture when later cancellation needs a
clean receipt: use `-NoExternalCleanupRequired` for process-only work, or
`-ComposeCleanupPlanPath` for Docker-backed work. Omitting both preserves compatibility but records
cleanup ownership as `UNKNOWN`, so cancellation cannot claim `cleanup_state=DONE`.
Profile and repository launches append through the same exclusive ledger lock used by reconciliation
and cancellation; a contending launch fails without replacing newer task or cancellation evidence.
If repository-runner identity inspection fails after detach, launch rolls back that exact process
tree before returning an error, so no untracked runner is left behind.

The Compose cleanup plan is explicit launch evidence, not a discovery hint:

```json
{
  "schema_version": "lotus.background-task-compose-cleanup-plan.v1",
  "projects": [
    {
      "project_name": "exact-compose-project",
      "working_directory": "C:\\path\\to\\exact-repository-root",
      "compose_files": ["docker-compose.yml"]
    }
  ]
}
```

Cancel one exact task by its durable identifier:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Cancel-Background-Run.ps1 `
  -EngineeringTaskId <engineering_task_id> `
  -Reason "Superseded by corrected exact-head certification" `
  -Actor <operator>
```

Cancellation requires the task id to resolve exactly once and verifies the recorded root PID plus
process-start timestamp before terminating its owned process tree. A vanished, reused, or
unreconciled PID remains `LOST`; it is not relabeled `CANCELLED`. Successful termination records
`CANCELLED`. `cleanup_state` becomes `DONE` only when the launch declared no external cleanup or
every launch-declared Compose project is clean; otherwise it becomes `BLOCKED`.

Compose mutation requires exact project, working-directory, and config-file label agreement on a
live project container. Residual volumes or networks without live container provenance fail
closed. Cleanup uses only exact `docker compose ... down --remove-orphans --volumes`; it never
uses daemon-wide prune, name-prefix cleanup, image removal, or an unrelated project. The atomic
receipt under `output/task-runs/*-<engineering_task_id>.cancellation.json` records reason, actor,
timestamps, targets, outcomes, and before/after counts and is referenced from the ledger.

Fast alignment background run (recommended for day-to-day platform sync):

```powershell
powershell -ExecutionPolicy Bypass -File automation/Start-Background-Run.ps1 -Profile platform-alignment -MaxParallel 3
```

Check background run status:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Check-Background-Runs.ps1
```

`Start-Background-Run.ps1` assigns a deterministic `runId`, `engineering_task_id`, expected result
artifact paths, and RFC-0094 task-ledger metadata for both modes. Repository mode also writes an
exact job specification and terminal result JSON under `output/task-runs/`.
`Check-Background-Runs.ps1` refreshes
`output/background-runs.json` with governed lifecycle states:

- `RUNNING` while the launched process is still active,
- `SUCCEEDED` only when the expected result artifact exists and all child task exit codes are zero,
- `FAILED` when the result artifact exists but contains failed task results or cannot be parsed,
- `LOST` when the process ended before the expected result artifact was written,
- `CANCELLED` when governed cancellation terminated the verified task process; the independent
  `cleanup_state` records whether cleanup passed or remains blocked.

The monitor also preserves evidence references for logs, JSON results, and Markdown summaries so
resumed sessions can inspect durable artifacts instead of relying on chat history.
It validates the recorded process start time as well as PID, so an unrelated process that reuses a
stale PID cannot keep a lost task falsely `RUNNING`. Reconciliation also persists the terminal exit
code and runner/target process identities from the exact result artifact.
The checker normalizes JSON-deserialized `DateTime`, `DateTimeOffset`, and round-trip timestamp
strings without culture-dependent string conversion. A live task must not become `LOST` because a
day/month rendering differs from the host locale.
It also flattens older wrapped ledger entries before reconciliation, so historical
`output/background-runs.json` shape drift cannot prevent the current background-run monitor from
reporting active task status.
It preserves terminal cancellation state and its receipt reference instead of reclassifying a
cancelled process with no normal result artifact as `LOST`.

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

For RFC closure, supported-feature promotion, or other mainline certification proof, require exact
mainline source provenance before cleanup, Docker startup, seeding, validation, screenshots, and
Lotus Idea readiness evidence. This mode forces image builds so proof is not certified against
stale local images:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp -RequireMainlineSources
```

This delegates to the governed `lotus-workbench` runtime and validation flow, uses the seeded front-office portfolio `PB_SG_GLOBAL_BAL_001`, and writes wrapper evidence to:

- `output/front-office-qa/latest.json`
- `output/front-office-qa/latest.md`
- `output/front-office-qa/dpm-command-center-seed-latest.json`

By default the wrapper also runs the DPM command-center seed after stack bring-up and before
Workbench validation. That seed refreshes the canonical mandate from `lotus-core` through
`lotus-manage`, runs one Manage monitoring pass for command-center evidence, persists or reuses
the date-aligned portfolio cash weight from Gateway's implementation-backed Workbench overview
before recalculating mandate health. The resolver disables optional Performance and rebalance
enrichment for this source-evidence read while continuing to reject source warnings, partial
failures, identity/date mismatches, and invalid values (the evidence records source URI,
requested/resolved date, percentage, and normalized ratio), persists or reuses
the canonical source-backed DPM campaign definition for
`lotus-core:DpmPortfolioUniverseCandidate:v1`, including source-owned selection-basis evidence
from the governed contract, creates and verifies the canonical Manage-owned outcome review through
Gateway, then verifies the manage lookup, Gateway campaign definition/discovery paths, and Gateway
command-center read paths so
`DPM_MANDATE_NOT_FOUND` is treated as a seed failure rather than a valid populated-panel state.
Before any state-changing Manage seed call, `Invoke-DpmCommandCenterSeed.ps1` now runs a
side-effect-free authorization preflight against the exact refresh route. The seed actor uses
`X-Actor-Id=platform-seed-automation`,
`X-Role=platform-automation`,
`X-Service-Identity=lotus-platform.canonical-dpm-command-center-seed`, and
`X-Capabilities=manage.write`; a 403 remains a seed-authority failure, not a reason to disable
Manage authorization. Use `-PreflightOnly` to diagnose the caller contract without refreshing or
persisting DPM evidence. After preflight passes, a full-seed `DPM_CORE_CONTEXT_INCOMPLETE` response
is a source-readiness dependency, not an authorization failure; preserve the response body in
`dpm-command-center-seed-latest.json` and link the owning Core issue, currently
`sgajbi/lotus-core#840` for the canonical `PB_SG_GLOBAL_BAL_001` missing eligibility, tax-lot, and
market-data families.
The seed evidence records explicit `posture_checks` for the populated source-ready `ready` command
center, selector-driven `partial` state, and empty-date `empty` state. Explicitly degraded and
blocked command-center fixtures remain source-owner follow-up rather than demo-ready seed claims.
Wrapper summaries record `require_mainline_sources` and `mainline_source_preflight` so proof
consumers can distinguish development evidence from RFC/mainline certification evidence.
Use `-SkipDpmCommandCenterSeed` only for diagnostic runs that intentionally prove the unseeded
empty/error posture.

Validate the governed DPM command-center seed contract without bringing up the runtime:

```powershell
python automation/validate_canonical_front_office_demo_data_contract.py
```

This focused check verifies that the canonical mandate, PM book, source-product lineage,
date-aligned cash evidence, ready/partial/empty posture expectations, Manage authority preflight,
and seed-script evidence hooks remain aligned before
the heavier Workbench runtime proof runs. The CLI is the fail-closed cross-repository path and
requires a resolvable `lotus-core` checkout (or explicit `--core-repo`) for executable seed proof.
Platform unit callers may use `validate_default_paths()` for hermetic Platform-owned contract
validation and must pass `core_repo` when they intend to certify producer evidence.

Use `-LotusAiEnvFile .env.example` when the proof should exercise deterministic
provider-disabled Advisor Brief execution. Use the repo-local `lotus-ai/.env` only when its live
provider dependency, such as the `local-llm` Ollama compose profile and model, is intentionally
running.

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

Preview the exact run-owned Docker cleanup scope without mutating the daemon:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -CleanPlanOnly
```

The plan is written to `output/front-office-qa/cleanup-plan-latest.json`. Every selected resource
includes Compose-project and working-directory provenance. A Lotus-shaped name is never sufficient
ownership evidence. The inventory explicitly maps `lotus-core`, repository-declared
`lotus-core-app-local`, and isolated `lotus-core-canonical-ui` to the canonical `lotus-core`
checkout boundary. If another, temporary, or nested checkout reuses one of those project names, the
plan records an ownership conflict and `-Clean` fails before mutation. The plan distinguishes
`active_foreign_owner`, `missing_labelled_checkout`, and `unproven_resource_only_owner`; all three
remain blocking. Residual project-labeled volumes or images without a live container proving the
expected checkout also fail closed.

When a fresh plan proves that one exact conflict is a `missing_labelled_checkout`, first run the
separate retirement command without `--execute`. Bind the plan digest and restate every identity
field from that conflict rather than copying this example literally:

```powershell
$plan = Resolve-Path output\front-office-qa\cleanup-plan-latest.json
$digest = (Get-FileHash -Algorithm SHA256 $plan).Hash.ToLowerInvariant()
python automation\canonical_orphan_retirement.py `
  --plan $plan --expected-plan-sha256 $digest `
  --container-id <full-container-id> --container-name <exact-container-name> `
  --compose-project <exact-project> --labelled-working-dir <missing-checkout> `
  --expected-working-dir <canonical-repository-root> `
  --projects-root C:\Users\Sandeep\projects `
  --workbench-repo-path C:\Users\Sandeep\projects\lotus-workbench `
  --output output\front-office-qa\orphan-retirement-dry-run.json
```

Review the receipt. To execute, generate a new cleanup plan and digest within the default five-minute
freshness window, repeat the exact command with a new receipt path, and add
`--execute --confirmation RETIRE_EXACT_ORPHAN`. The command re-inspects the full container ID,
name, Compose project, labelled working directory, filesystem absence, and every registered Git
worktree immediately before removing only that container. It never removes a Compose project,
volume, image, network, similarly named resource, active checkout, registered missing worktree, or
resource-only conflict. A failed post-mutation verification is recorded as
`indeterminate_after_mutation`, never as success. Execution writes a validated pre-mutation receipt
before removal and replaces it with a final receipt containing a newly generated view of all
remaining ownership conflicts.

Clean only the canonical Compose projects owned by the declared repository roots before governed
bring-up:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -Clean -BringUp -BuildImages
```

Reset only `lotus-core` Docker state before reseeding the governed portfolio when stale core state blocks validation:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp -CleanCoreState -LotusAiEnvFile .env.example -SeedWaitSeconds 1200
```

Rebuild local service images as part of the clean-core reseed when a live proof must include unmerged branch changes:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp -CleanCoreState -BuildImages -LotusAiEnvFile .env.example -SeedWaitSeconds 1200
```

Remove local images owned by those same canonical Compose projects, without starting the stack:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -Clean -RemoveImages
```

`-Clean` delegates deletion to the governed `lotus-workbench` teardown, which executes repository-
scoped Compose shutdowns. The platform wrapper does not enumerate or remove resources by broad
`lotus`, `pbwm`, or `performance` name prefixes. It builds and publishes an ownership plan first,
then fails if the planned Compose projects retain containers or volumes after teardown. This keeps
concurrent Core certification and unrelated Lotus Compose projects outside the cleanup boundary.
`-CleanCoreState` delegates to the Workbench runtime's targeted `lotus-core` reset before reseeding,
which is narrower than a canonical-runtime clean and useful after load/performance data has left core
readiness stale. Add `-BuildImages` when proof depends on local branch changes not yet present in
existing Docker images. `-LotusAiEnvFile` pins provider posture. `-RemoveImages` remains opt-in
because it makes the next startup slower.

For a clean demo rebuild from stale local state:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -Clean -BringUp -BuildImages -KeepRunning
```

The clean demo rebuild is also the all-Lotus-app local rebuild: it keeps the governed front-office
validation contract and adds `lotus-idea` runtime evidence by default.

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -Clean -BringUp -BuildImages -KeepRunning
```

The governed Workbench runtime starts and seeds `lotus-idea` from its app-local Docker compose by
default. The platform wrapper preserves that seeded runtime and records both direct
`127.0.0.1:8330` readiness and `idea.dev.lotus` ingress readiness under `lotus_idea` in the
wrapper summary. This keeps `lotus-idea` visible for all-app validation without wiping the advisor
queue, treating it as a Workbench populated-panel surface, or changing the RFC-0076/RFC-0077
front-office screenshot evidence contract.

If Windows blocks hosts-file updates, run the reusable elevated helper:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Apply-DevIngressHosts-Elevated.ps1
```

Troubleshoot failures by category:

1. hostname failures: run `automation/Apply-DevIngressHosts-Elevated.ps1`, or run `automation/Sync-Dev-Ingress-Hosts.ps1 -Apply` from an elevated shell,
2. readiness failures: inspect the failing canonical service health endpoint in `latest.json`,
3. seed failures: rerun the `lotus-core` front-office seed verifier for `PB_SG_GLOBAL_BAL_001`,
4. calculation failures: inspect `calculationChecks` in `live-validation-summary.json`,
5. blank or degraded panel failures: inspect `panelClassifications` before taking screenshots,
6. screenshot failures: verify the caller-provided `-ScreenshotDirectory` exists and is writable.

Run backend/runtime QA readiness automation (startup + API/log/metrics/standards checks):

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-Platform-QA.ps1 -BringUp
```

The `lotus-core` custom platform QA gate uses the governed canonical front-office verifier for
`PB_SG_GLOBAL_BAL_001`. Run it directly when troubleshooting the demo-readiness lane:

```powershell
python ..\lotus-core\tools\front_office_portfolio_seed.py --verify-only --portfolio-id PB_SG_GLOBAL_BAL_001 --start-date 2025-03-31 --end-date 2026-04-10 --benchmark-start-date 2025-01-06 --ingestion-base-url http://core-ingestion.dev.lotus --query-base-url http://core-query.dev.lotus --query-control-plane-base-url http://core-control.dev.lotus --gateway-base-url http://gateway.dev.lotus --wait-seconds 300 --poll-interval-seconds 3
```

Run the generated seeded analytics maturity invariant against `lotus-core` as a clean-state
hardening check:

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

Run the platform demo-readiness certification wrapper:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-PlatformDemoReadinessCertification.ps1 -ScenarioMode fresh_seed
```

The command invokes `Invoke-PlatformValidationLane.ps1` for `core-performance-green-lanes`, which
seeds deterministic synthetic scenarios in `fresh_seed` mode, calls the real `lotus-core` and
`lotus-performance` APIs, asserts cross-app domain figures, then writes
`output/demo-readiness/platform/platform-demo-readiness-certification.json`. The feature lane uploads
this evidence as report-only with `continue-on-error`; promote it to a blocking gate only after the
CI governance intake proves the signal is deterministic, low-noise, and policy-backed.

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

Validate rebase-safe branch size before PR merge intent:

```powershell
python automation/validate_branch_commit_budget.py --repo-root C:/Users/Sandeep/projects/lotus-report --base-ref origin/main --head-ref HEAD
```

`Preflight-PR.ps1` runs the same branch-budget validator unless `-NoGitChecks` is supplied. The
default budget warns at 40 commits, requires a recorded tranche decision at 60 commits, and blocks
above 90 commits so long-running refactors split before GitHub's rebase-merge limit.

Generate test-pyramid and coverage baseline across backend services:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Measure-Test-Pyramid.ps1 -RunCoverage
```

Generate dependency vulnerability rollup across backend services:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Generate-Dependency-Vulnerability-Rollup.ps1
```

Plan repository governance policy reconciliation after proving that every required check is
emitted by current workflow source:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Enforce-Repository-Governance.ps1 -Repository lotus-workbench
```

Use the same bounded repository selector with `-Apply` only after reviewing the plan. Omit
`-Repository` for an intentional ecosystem-wide reconciliation. The enforcer refuses to plan or
apply a policy containing a required context that current default-branch workflows do not emit.

```powershell
powershell -ExecutionPolicy Bypass -File automation/Enforce-Repository-Governance.ps1 -Repository lotus-workbench -Apply
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

Validate auto-merge and exact-main releasability convergence across registered Lotus repositories:

```powershell
python automation/validate_auto_merge_releasability.py
```

The validator checks local sibling repositories when they are present, records temporary rollout
exceptions from `platform-contracts/ci-governance/auto-merge-releasability-exceptions.v1.json`,
and fails on undeclared or expired drift in `pr-auto-merge.yml`,
`merged-pr-main-releasability.yml`, or `main-releasability.yml`. The merged-PR dispatcher must create
and dispatch through an immutable `main-releasability-<merge-sha>` ref, pass `expected_sha` from
`github.event.pull_request.merge_commit_sha`, and Main Releasability must use revision-aware
concurrency and assert that the checked-out commit matches that expected SHA when provided. Manual
operator dispatch remains valid without `expected_sha`.

Validate exact-commit GitHub verification before accepting mainline provenance:

```powershell
python automation/validate_mainline_commit_provenance.py
```

The validator checks GitHub commit verification for the current repository and commit when
available, falls back to local `git verify-commit` for unpushed local work, and fails on unsigned
or otherwise unverified commits unless
`platform-contracts/ci-governance/mainline-commit-provenance-exceptions.v1.json` contains an exact,
unexpired, issue-backed exception.
For protected linear-history repositories that use GitHub rebase merge without required signed
commits, GitHub may rewrite the merged `main` commit as unsigned. In that case the validator records
`unsigned_allowed_by_branch_policy` only when GitHub branch protection reports required signatures
disabled. If the workflow token cannot read the branch-protection endpoint, the mainline workflow
must declare `LOTUS_BRANCH_SIGNATURES_REQUIRED`; live GitHub branch-protection truth takes
precedence whenever it is available. Enabling required signatures turns the same unsigned condition
into a failure.
The shared platform repo check entrypoint runs this validator as a blocking gate only for the
`main-releasability` lane. GitHub Actions steps that run that lane must expose
`GH_TOKEN: ${{ github.token }}` so provenance validation uses GitHub verification instead of a
local-git fallback.

When updating `quality/baseline_report.json`, run
`automation/Resolve-PlatformAutomationPython.ps1` first and invoke the baseline generator with that
resolved interpreter. The test-count metric is interpreter-environment sensitive and must match the
same platform automation runtime used by `Invoke-PlatformRepoChecks.ps1`.

Validate GitHub Actions version/runtime posture across platform workflows and templates:

```powershell
python automation/validate_workflow_action_runtime.py
```

Validate container build and image baseline posture across backend scaffold templates:

```powershell
python automation/validate_container_build_baseline.py
```

Validate digest-based deployment promotion manifests:

```powershell
python automation/validate_deployment_promotion_manifest.py
python automation/validate_deployment_promotion_manifest.py --manifest platform-contracts/deployment-promotion/examples/lotus-archive-deployment-promotion.valid.json
python automation/validate_deployment_promotion_manifest.py --manifest platform-contracts/deployment-promotion/examples/lotus-idea-deployment-promotion.pending.json
```

`deployment_evidence_status: deployment_pending` is reserved for release-bound manifests that have
current service release evidence but no approved deployed-digest observation yet. It is useful
durable blocker evidence, not same-digest deployment proof or production certification.

Validate a supported-claim register before promoting demo, RFP, security-pack, or screenshot claims:

```powershell
python automation/validate_supported_claim_register.py --path platform-contracts/supported-claims/examples/rfc0028-advisory-bank-demo-supported-claims.valid.json
```

Validate platform end-to-end coverage profiles against the workflow and entrypoint contract:

```powershell
python automation/validate_platform_validation_coverage.py
```

Generate and validate the automation discoverability inventory used for cleanup reviews:

```powershell
python automation/generate_automation_inventory.py --write --check
```

Artifacts:
- `quality/automation_inventory.json`
- `quality/automation_inventory.md`

Generate the cross-repository rounding governance compliance matrix:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Validate-Rounding-Governance.ps1
```

Artifacts:
- `output/rounding-governance-compliance.json`
- `output/rounding-governance-compliance.md`

Bootstrap the isolated platform automation Python runtime:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Resolve-PlatformAutomationPython.ps1
```

Validate current workflow-source and live repository-governance drift against the platform policy:

```powershell
python automation/validate_repository_governance.py
```

Use a repeatable repository selector for bounded proof, or `--source-only` as the non-mutating
preflight before governance reconciliation:

```powershell
python automation/validate_repository_governance.py --repository lotus-workbench
python automation/validate_repository_governance.py --source-only --repository lotus-workbench --repository lotus-idea
```

Required-check names must match the exact job names emitted by current default-branch workflow
source. Matrix job names are expanded using their axes, includes, and exclusions. A context emitted
outside repository workflow source must be declared in that repository's
`external_required_checks` mapping with a non-empty provider description; this exception is for a
real external check provider, not a differently named local job.

Scaffold a new standards-compliant Lotus backend and auto-register it in automation:

```powershell
powershell -ExecutionPolicy Bypass -File automation/New-Lotus-Service.ps1 -ServiceName lotus-foo -Description "New domain service" -ServiceProfile domain-service
```

Detailed scaffold usage and generated-feature documentation:
`docs/onboarding/LOTUS-BACKEND-SERVICE-SCAFFOLD-GUIDE.md`.

Check whether app-local enterprise backend refactoring instruction copies match the canonical
platform playbook:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Sync-EnterpriseBackendRefactoringInstructions.ps1 -CheckOnly
```

Synchronize those app-local copies from the platform source when a coordinated rollout needs local
copies:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Sync-EnterpriseBackendRefactoringInstructions.ps1
```

The canonical source is
`context/playbooks/ENTERPRISE-BACKEND-REFACTORING-INSTRUCTIONS.md`; app-local
`docs/architecture/ENTERPRISE_BACKEND_REFACTORING_INSTRUCTIONS.md` files are deployed copies. By
default the sync scope is resolved from `automation/repos.json` so newly registered backend apps are
covered without editing this script; pass `-Repositories` only for a deliberate bounded rollout.

For a fuller governed bootstrap that also initializes git, creates the GitHub repository, makes it
public, and applies baseline main-branch protection:

```powershell
powershell -ExecutionPolicy Bypass -File automation/New-Lotus-Service.ps1 `
  -ServiceName lotus-foo `
  -Description "New domain service" `
  -BusinessRole "New domain service" `
  -ServiceProfile domain-service `
  -DevHostName foo `
  -InitializeGit `
  -CreateGithubRepo `
  -GithubVisibility public `
  -EnableGithubDefaults `
  -ApplyMainBranchProtection
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
- `qa-platform-readiness-clean-core`
- `qa-platform-readiness-clean-core-build`
- `autonomous-foundation`

New repo included in shared automation:
- `lotus-report`

Note: scaffolded backend services now default to repo-native `make` commands backed by a repo-local
`.venv`, so bootstrap and CI-parity profiles do not need to mutate the shared user Python
environment just to validate a new service.
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
- `output/stalled-workflow-runs.json`
- `output/stalled-workflow-runs.md`
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
- `automation/test-coverage-policy.json`
- `automation/qa-matrix.json` when `-DevHostName` is provided
- `automation/task-profiles.json`
- `context/lotus-context-manifest.json`
- `context/ECOSYSTEM-REGISTRIES.md`
- `context/LOTUS-QUICKSTART-CONTEXT.md`
- `context/LOTUS-ENGINEERING-CONTEXT.md`
- `context/CONTEXT-REFERENCE-MAP.md`
- `docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md`
- `wiki/Integrations.md`

The scaffold now also creates repo-local `AGENTS.md`, `REPOSITORY-ENGINEERING-CONTEXT.md`, and
the standard repo-local wiki skeleton by default. Optional Git/GitHub provisioning can initialize the repository, create
the remote, configure baseline repository settings, and apply protected-`main` governance in the
same workflow.

Scaffolded backend repositories now also default to:
- repo-local virtualenv bootstrap through `make install`
- repo-native `make` commands in automation task profiles instead of raw host-environment Python commands
- service-profile-aware README, repository context, wiki source, and quality documentation
- layered `src/app/api`, `src/app/application`, `src/app/domain`, `src/app/ports`,
  `src/app/infrastructure`, `src/app/observability`, and `src/app/security` package skeleton
- baseline health, readiness, metrics, correlation-id and trace-id propagation, OpenAPI quality, coverage gate, and wiki-source posture from day one
- product-safe problem-details errors, structured JSON application events, supported-features placeholders, RFC implementation evidence scaffolding, operations observability documentation, and API certification documentation from day one
- worktree-clean blocking architecture-boundary gate plus report-only `make architecture-boundary-report`
  and `make quality-baseline` commands. Report artifacts stay behind explicit report commands so
  local preflight and CI gates do not dirty generated repositories.
- `evidence/rfc-implementation/evidence-manifest.template.json`, so RFC implementation slices can
  publish comparable machine-readable evidence across repositories without inventing local manifest
  shapes; the template now includes slice closure, API certification, state-machine review,
  supported-feature review, wiki-publication, and downstream-realization sections for
  stateful/API-heavy RFC programs

RFC-0108 Slice 0 added the analytics UI observability scaffold baseline. Validate that baseline with:

```powershell
python automation/validate_analytics_ui_observability_contract.py
python -m pytest tests/unit/test_repository_hygiene_scaffold_contract.py tests/unit/test_analytics_ui_observability_contract.py
```
