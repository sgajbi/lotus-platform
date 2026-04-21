# Directory Map

This map organizes the automation directory by responsibility without changing script paths.

## Canonical Root

- `automation/`: executable scripts + config JSON used by platform automation.

## Script Groups

### Orchestration

- `Platform-Pulse.ps1`
- `Run-Agent.ps1`
- `Run-Parallel-Tasks.ps1`
- `Start-Background-Run.ps1`
- `Check-Background-Runs.ps1`
- `Summarize-Task-Failures.ps1`

### Repo and PR Operations

- `Sync-Repos.ps1`
- `PR-Monitor.ps1`
- `Close-PR-Loop.ps1`
- `Detect-Stalled-PR-Checks.ps1`
- `Preflight-PR.ps1`
- `Sync-RepoWikis.ps1`
- `Invoke-Platform-QA.ps1`
- `Invoke-Canonical-FrontOffice-QA.ps1`

### Cross-App Validation

- `Invoke-CrossApp-CorePerformance-TwrBenchmark.ps1`
- `Invoke-CrossApp-CorePerformance-Mwr.ps1`
- `Invoke-CrossApp-CorePerformance-ReturnsSeries.ps1`
- `Invoke-CrossApp-CorePerformance-Contribution.ps1`
- `Invoke-CrossApp-CorePerformance-Attribution.ps1`
- `core_performance_twr_benchmark_validation.py`
- `core_performance_mwr_validation.py`
- `core_performance_returns_series_validation.py`
- `core_performance_contribution_validation.py`
- `core_performance_attribution_validation.py`

### Service Runtime Operations

- `Service-Refresh.ps1`
- `Bootstrap-Repo-Env.ps1`
- `Bootstrap-LotusDeveloperEnvironment.ps1`
- `Validate-LotusDeveloperEnvironment.ps1`
- `Sync-Dev-Ingress-Hosts.ps1`
- `Validate-Dev-Ingress-Smoke.ps1`
- `Explain-Dev-Ingress-Status.ps1`

### Standards and Conformance

- `Validate-Platform-Contract.ps1`
- `Validate-Backend-Standards.ps1`
- `Validate-OpenAPI-Conformance.ps1`
- `Validate-Domain-Vocabulary.ps1`
- `Validate-Lotus-Naming.ps1`
- `Validate-Rounding-Consistency.ps1`
- `Validate-Rounding-Governance.ps1`
- `Validate-Monetary-Float-Guard.ps1`
- `Validate-Scalability-Availability.ps1`
- `Validate-Durability-Consistency.ps1`
- `Validate-Enterprise-Readiness.ps1`
- `Verify-Repo-Metadata.ps1`
- `Validate-Automation-Config.ps1`
- `Validate-Change-Test-Impact.ps1`

### Evidence and Analytics

- `Measure-Test-Pyramid.ps1`
- `Generate-Dependency-Vulnerability-Rollup.ps1`
- `Generate-Local-CI-Parity-Evidence.ps1`
- `Audit-RFC-Conformance.ps1`

### Governance and Scaffolding

- `Enforce-Repository-Governance.ps1`
- `validate_repository_governance.py`
- `validate_repository_hygiene.py`
- `render_context_registries.py`
- `validate_engineering_context_system.py`
- `validate_heartbeat_contracts.py`
- `validate_lotus_skill_alignment.py`
- `validate_workflow_security.py`
- `validate_workflow_action_runtime.py`
- `validate_container_build_baseline.py`
- `validate_platform_validation_coverage.py`
- `Resolve-PlatformAutomationPython.ps1`
- `New-Lotus-Service.ps1`
- `Cleanup-Legacy-Workspace.ps1`

## Config Files

- `repos.json`: repo registry and preflight commands
- `task-profiles.json`: profile-to-task mapping
- `qa-matrix.json`: runtime QA startup/API/log/monitoring checks per service
- `service-map.json`: service refresh mapping
- `repository-governance-policy.json`
- `platform-validation-profiles.json`
- `test-coverage-policy.json`

## Documentation Set

- `automation/README.md`: command-level reference and quick start
- `automation/docs/Automation-Guide.md`: what to run and when
- `automation/docs/Profile-Reference.md`: profile intent
- `automation/docs/Directory-Map.md`: this map
- `automation/docs/Core-Performance-TWR-Benchmark-Scenario.md`: business-readable scenario guide for the reusable `lotus-core` -> `lotus-performance` validation
- `automation/docs/Core-Performance-MWR-Scenario.md`: business-readable scenario guide for the reusable `lotus-core` -> `lotus-performance` stateful MWR validation
- `automation/docs/Core-Performance-Returns-Series-Scenario.md`: business-readable scenario guide for the reusable `lotus-core` -> `lotus-performance` benchmark-aware returns-series validation
- `automation/docs/Core-Performance-Contribution-Scenario.md`: business-readable scenario guide for the reusable `lotus-core` -> `lotus-performance` stateful contribution validation
- `automation/docs/Core-Performance-Attribution-Scenario.md`: business-readable scenario guide for the reusable `lotus-core` -> `lotus-performance` stateful attribution validation
