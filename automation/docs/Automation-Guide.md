# Automation Guide

Use this guide to decide what to run, when to run it, and where output lands.

Canonical source: `lotus-platform/automation`

## Start Here

1. Need a quick platform health check: run `Platform-Pulse.ps1`.
2. Need continuous monitoring: run `Run-Agent.ps1`.
3. Need asynchronous long-running checks: run `Start-Background-Run.ps1` with a profile.
4. Need PR lifecycle automation: run `Close-PR-Loop.ps1`.
5. Need one repo preflight before push: run `Preflight-PR.ps1`.
6. Need production-readiness QA validation: run `Invoke-Platform-QA.ps1`.
7. Need a reusable seeded cross-app business scenario: run `Invoke-CrossApp-CorePerformance-TwrBenchmark.ps1`.

## Decision Matrix (When To Use What)

| Goal | Command | Typical Use |
|---|---|---|
| Sync repos + PR snapshot + core conformance | `automation/Platform-Pulse.ps1 -IncludeConformance` | Before or after broad platform changes |
| Continuous automation heartbeat | `automation/Run-Agent.ps1` | Long-running local monitor loop |
| One iteration of agent logic | `automation/Run-Agent.ps1 -Once` | Quick status refresh in terminal |
| Run heavy checks in background | `automation/Start-Background-Run.ps1 -Profile <name> -MaxParallel <n>` | Offload checks while coding |
| Monitor detached background runs | `automation/Check-Background-Runs.ps1` | Inspect async run state and artifacts |
| Fast daily alignment baseline | `automation/Start-Background-Run.ps1 -Profile platform-alignment -MaxParallel 3` | Day-to-day cross-repo confidence |
| Full governance sweep | `automation/Start-Background-Run.ps1 -Profile autonomous-foundation -MaxParallel 1` | Deeper standards/governance evidence |
| Detect stalled checks | `automation/Detect-Stalled-PR-Checks.ps1 -StaleMinutes 20` | Investigate PR check deadlocks |
| Queue auto-merge + cleanup merged branches | `automation/Close-PR-Loop.ps1` | PR lifecycle automation |
| Validate automation config integrity | `automation/Validate-Automation-Config.ps1` | Keep repos/profiles/refs consistent |
| Enforce local-vs-CI scope parity (fail on gap) | `automation/Validate-Local-CI-Parity.ps1` | Prevent PR failures caused by missing local checks |
| Validate code/test impact | `automation/Validate-Change-Test-Impact.ps1` | Ensure source deltas include test updates |
| Platform QA readiness validation | `automation/Invoke-Platform-QA.ps1 -BringUp` | Bring up services and validate API/log/observability/standards |
| Platform QA + issue creation | `automation/Invoke-Platform-QA.ps1 -BringUp -CreateIssues` | File defects with evidence in each repo |
| Seeded cross-app TWR + benchmark validation | `automation/Invoke-CrossApp-CorePerformance-TwrBenchmark.ps1 -BringUp` | Validate `lotus-core` and `lotus-performance` together on a realistic benchmark-aware portfolio scenario |

## Core Validation Scripts

- Backend standards: `automation/Validate-Backend-Standards.ps1`
- OpenAPI conformance: `automation/Validate-OpenAPI-Conformance.ps1`
- Domain vocabulary: `automation/Validate-Domain-Vocabulary.ps1`
- Enterprise readiness: `automation/Validate-Enterprise-Readiness.ps1`
- Metadata validation: `automation/Verify-Repo-Metadata.ps1`
- Local-CI parity gate: `automation/Validate-Local-CI-Parity.ps1`
- Change/test impact validation: `automation/Validate-Change-Test-Impact.ps1`
- Rounding consistency: `automation/Validate-Rounding-Consistency.ps1`
- Monetary float guard: `automation/Validate-Monetary-Float-Guard.ps1`

## Profiles

See full catalog and intent in `automation/docs/Profile-Reference.md`.

Most common:
- `platform-alignment`
- `fast-feedback`
- `ci-parity`
- `docker-ci-parity`
- `qa-platform-readiness`
- `autonomous-foundation`

## Output Artifacts

Primary outputs are written to `lotus-platform/output/`:
- `pr-monitor.*`
- `agent-status.*`
- `pr-lifecycle.*`
- `background-runs.json`
- `task-runs/*`
- `cross-app/core-performance-twr-benchmark-validation.*`
- conformance outputs (`*-conformance.*`, `*-compliance.*`, `*-validation.*`)

## Related Docs

- Directory organization: `automation/docs/Directory-Map.md`
- Profiles and execution intent: `automation/docs/Profile-Reference.md`
- Command details and operational examples: `automation/README.md`
