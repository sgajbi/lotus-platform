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
- `automation/Platform-Pulse.ps1`
- `automation/Run-Agent.ps1`
- `automation/Service-Refresh.ps1`
- `automation/Run-Parallel-Tasks.ps1`
- `automation/Start-Background-Run.ps1`
- `automation/Check-Background-Runs.ps1`
- `automation/Summarize-Task-Failures.ps1`
- `automation/Bootstrap-Repo-Env.ps1`
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
- `automation/Invoke-CrossApp-CorePerformance-TwrBenchmark.ps1`
- `automation/Invoke-CrossApp-CorePerformance-Baseline.ps1`
- `automation/Invoke-CrossApp-CorePerformance-Contribution.ps1`
- `automation/Invoke-CrossApp-CorePerformance-Attribution.ps1`
- `automation/Validate-OpenAPI-Conformance.ps1`
- `automation/Validate-Domain-Vocabulary.ps1`
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
- `automation/service-map.json`
- `automation/task-profiles.json`
- `automation/repos.json`
- `automation/qa-matrix.json`

## Quick Start

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

`Start-Background-Run.ps1` now assigns a deterministic `runId` and expected result artifact paths, and `Check-Background-Runs.ps1` marks runs as completed based on artifact existence to avoid stale `running` status from PID reuse.

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

Run platform-level QA readiness automation (startup + API/log/metrics/standards checks):

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

Run QA and auto-create GitHub issues for each detected defect:

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
