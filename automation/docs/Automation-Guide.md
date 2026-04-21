# Automation Guide

Use this guide to decide what to run, when to run it, and where output lands.

Canonical source: `lotus-platform/automation`

## Start Here

1. Need a quick platform health check: run `Platform-Pulse.ps1`.
2. Need continuous monitoring: run `Run-Agent.ps1`.
3. Need asynchronous long-running checks: run `Start-Background-Run.ps1` with a profile.
4. Need PR lifecycle automation: run `Close-PR-Loop.ps1`.
5. Need one repo preflight before push: run `Preflight-PR.ps1`.
6. Need governed populated front-office validation: run `Invoke-Canonical-FrontOffice-QA.ps1`.
7. Need backend service readiness QA validation: run `Invoke-Platform-QA.ps1`.
8. Need a reusable seeded cross-app business scenario: run `Invoke-CrossApp-CorePerformance-TwrBenchmark.ps1`.
9. Need a reusable seeded cross-app MWR scenario: run `Invoke-CrossApp-CorePerformance-Mwr.ps1`.
10. Need a reusable seeded cross-app returns-series scenario: run `Invoke-CrossApp-CorePerformance-ReturnsSeries.ps1`.
11. Need a reusable seeded cross-app contribution scenario: run `Invoke-CrossApp-CorePerformance-Contribution.ps1`.
12. Need a reusable seeded cross-app attribution scenario: run `Invoke-CrossApp-CorePerformance-Attribution.ps1`.
13. Need the whole cross-app baseline in one run: run `Invoke-CrossApp-CorePerformance-Baseline.ps1`.
14. Need to classify the current RFC-0071 local ingress rollout state: run `Explain-Dev-Ingress-Status.ps1`.
15. Need to verify or publish GitHub wiki content from repo source: run `Sync-RepoWikis.ps1`.

## Decision Matrix (When To Use What)

| Goal | Command | Typical Use |
|---|---|---|
| Sync repos + PR snapshot + core conformance + shared infra ownership guard | `automation/Platform-Pulse.ps1 -IncludeConformance` | Before or after broad platform changes |
| Continuous automation heartbeat | `automation/Run-Agent.ps1` | Long-running local monitor loop |
| One iteration of agent logic | `automation/Run-Agent.ps1 -Once` | Quick status refresh in terminal |
| Run heavy checks in background | `automation/Start-Background-Run.ps1 -Profile <name> -MaxParallel <n>` | Offload checks while coding |
| Monitor detached background runs | `automation/Check-Background-Runs.ps1` | Inspect async run state and artifacts |
| Fast daily alignment baseline | `automation/Start-Background-Run.ps1 -Profile platform-alignment -MaxParallel 3` | Day-to-day cross-repo confidence |
| Full governance sweep | `automation/Start-Background-Run.ps1 -Profile autonomous-foundation -MaxParallel 1` | Deeper standards/governance evidence |
| Detect stalled checks | `automation/Detect-Stalled-PR-Checks.ps1 -StaleMinutes 20` | Investigate PR check deadlocks |
| Queue auto-merge + cleanup merged branches | `automation/Close-PR-Loop.ps1` | PR lifecycle automation |
| Check repo wiki publication drift | `automation/Sync-RepoWikis.ps1 -CheckOnly -Repository <repo-name>` | Fail when repo-local `wiki/` source differs from the published GitHub wiki and the branch is not intentionally changing `wiki/` |
| Publish repo wiki after merge | `automation/Sync-RepoWikis.ps1 -Publish -Repository <repo-name>` | Push repo-authored `wiki/` source to the live `*.wiki.git` publication target |
| Audit or publish all repo wikis | `automation/Sync-RepoWikis.ps1 -CheckOnly -AllRepositories` or `-Publish -AllRepositories` | Coordinated platform-wide wiki source/publication sweeps |
| Validate automation config integrity | `automation/Validate-Automation-Config.ps1` | Keep repos/profiles/refs consistent |
| Enforce local-vs-CI scope parity (fail on gap) | `automation/Validate-Local-CI-Parity.ps1` | Prevent PR failures caused by missing local checks |
| Validate code/test impact | `automation/Validate-Change-Test-Impact.ps1` | Ensure source deltas include test updates |
| Canonical front-office readiness validation | `automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp` | Bring up the governed `lotus-workbench` runtime and validate populated UI/product surfaces |
| Canonical front-office screenshot pack | `automation/Invoke-Canonical-FrontOffice-QA.ps1 -ScreenshotDirectory <path>` | Validate canonical endpoints, calculations, and panels before writing demo screenshots, `SHOT-INDEX.md`, and structured screenshot evidence |
| Canonical front-office clean rebuild | `automation/Invoke-Canonical-FrontOffice-QA.ps1 -Clean -BringUp -BuildImages` | Clean stale Lotus containers and volumes, rebuild images through the governed workbench runtime, and validate populated UI/product surfaces |
| Canonical front-office clean core reseed | `automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp -CleanCoreState` | Reset only `lotus-core` Docker state before reseeding the governed front-office portfolio when stale core state blocks validation |
| Canonical front-office full cleanup | `automation/Invoke-Canonical-FrontOffice-QA.ps1 -Clean -RemoveImages` | Remove stale Lotus containers, volumes, and matching local Lotus images without starting the stack |
| Backend/runtime QA readiness validation | `automation/Invoke-Platform-QA.ps1 -BringUp` | Bring up backend services and validate API/log/observability/standards |
| Backend/runtime QA + issue creation | `automation/Invoke-Platform-QA.ps1 -BringUp -CreateIssues` | File backend/runtime defects with evidence in each repo |
| Seeded cross-app TWR + benchmark validation | `automation/Invoke-CrossApp-CorePerformance-TwrBenchmark.ps1 -BringUp` | Validate `lotus-core` and `lotus-performance` together on a realistic benchmark-aware portfolio scenario |
| Seeded cross-app MWR validation | `automation/Invoke-CrossApp-CorePerformance-Mwr.ps1 -BringUp` | Validate `lotus-core` and `lotus-performance` together on a realistic stateful MWR scenario |
| Seeded cross-app returns-series validation | `automation/Invoke-CrossApp-CorePerformance-ReturnsSeries.ps1 -BringUp` | Validate `lotus-core` and `lotus-performance` together on a realistic benchmark-aware returns-series scenario |
| Seeded cross-app contribution validation | `automation/Invoke-CrossApp-CorePerformance-Contribution.ps1 -BringUp` | Validate `lotus-core` and `lotus-performance` together on a realistic stateful contribution scenario |
| Seeded cross-app attribution validation | `automation/Invoke-CrossApp-CorePerformance-Attribution.ps1 -BringUp` | Validate `lotus-core` and `lotus-performance` together on a realistic stateful attribution scenario |
| Reuse an existing stable cross-app scenario | `automation/Invoke-CrossApp-CorePerformance-*.ps1 -SkipSeed -ScenarioSuffix <suffix>` | Revalidate a known seeded scenario while fresh-seed analytics readiness is unstable |
| Reuse the full cross-app baseline | `automation/Invoke-CrossApp-CorePerformance-Baseline.ps1 -SkipSeed` | Revalidate the full core -> performance engine family using the latest stable scenario artifacts |
| Explain local dev ingress rollout state | `automation/Explain-Dev-Ingress-Status.ps1` | Determine whether DNS is missing, staged hosts need to be applied, or services are unhealthy, and emit the exact compose refresh command when service routing is the problem |

Canonical front-office QA writes Docker cleanup scope, clean-core posture, seed wait, and before/after artifact counts to `output/front-office-qa/latest.json` and `output/front-office-qa/latest.md`. Use `-Clean` for stale-container and stale-volume ambiguity, `-CleanCoreState` when only `lotus-core` reseeding state is stale, and add `-RemoveImages` only when image freshness matters more than startup speed. Use `-SeedWaitSeconds <seconds>` for long canonical reseeds and `-ScreenshotDirectory <path>` when a demo pack must be written outside the default Workbench artifact folder.

## Dev Ingress Operator Loop

Use this sequence for RFC-0071 local ingress rollout:

1. Preview or apply the managed hosts block with `automation/Sync-Dev-Ingress-Hosts.ps1`.
2. Run `automation/Validate-Dev-Ingress-Smoke.ps1` to generate live ingress evidence.
3. Run `automation/Explain-Dev-Ingress-Status.ps1` to classify the current state and the exact next step.

The explainer is intended to remove ambiguity after a failed smoke run. It reads the smoke artifact and the staged hosts preview and reduces the platform state to one operator outcome:
- `missing_smoke_result`
- `dns_not_configured`
- `ingress_unreachable`
- `services_unreachable`
- `ready`

The underlying smoke artifact also records a `failure_posture` per failed routed check:
- `dns_resolution_failed`
- `http_error`
- `connection_refused`
- `timeout`
- `transport_error`

For `ingress_unreachable`, the explainer now recommends `docker compose up -d dev-ingress` first, because the evidence indicates the edge itself is likely not serving requests.
For `services_unreachable`, the explainer now emits the exact `docker compose up -d ...` command for the affected platform-stack services instead of pointing operators back to a full-stack restart.
For `http_error` and `timeout` postures inside `services_unreachable`, the explainer now recommends targeted `docker compose logs --tail=200 ...` inspection before the refresh command.

Prerequisites for this loop:

1. `platform-stack/.env` is populated with the correct local repo paths
2. `platform-stack/dev-ingress/hosts.example` has been previewed or applied through `Sync-Dev-Ingress-Hosts.ps1`
3. some ingress path is actually listening on port `80`
   - full `platform-stack` uses `platform-stack/dev-ingress/Caddyfile`
   - mixed standalone bring-up may use `platform-stack/dev-ingress/Caddyfile.direct-host`

Operator rule:

- treat hostname/DNS and ingress as platform setup concerns first
- do not open app defects for `*.dev.lotus` failures until the ingress operator loop has ruled out `dns_not_configured` and `ingress_unreachable`

## GitHub Actions

Platform end-to-end validation can now also run from GitHub Actions through:

- `.github/workflows/platform-end-to-end-validation.yml`

Recommended operating model right now:
- use a `self-hosted` runner that can already reach live `lotus-core` and `lotus-performance` URLs
- start with `scenario_mode=skip_seed`
- provide explicit suffixes when you want deterministic reruns on a known stable scenario
- use `target=baseline` for the whole suite, or one validator target when you want to isolate a single engine lane

Why this starts as `self-hosted`:
- the validators depend on live cross-app services, not mocks
- stable-mode reuse depends on already-seeded scenarios on the runner
- fresh-seed mode is supported too, but it still exercises the upstream analytics-readiness path we are separately tracking

Current practical split inside the explicit lane:
- `validation_profile=core-performance-green-lanes` is the cleaner day-to-day path for the known-green engines: TWR + benchmark, returns-series, contribution, and MWR
- `validation_profile=core-performance-baseline` is the deeper manual entrypoint when you want baseline evidence, including attribution posture

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
- `background-runs.json` with RFC-0094 `engineering_task_id`, `task_kind`, lifecycle status, cleanup state, and evidence references for detached runs
- `task-runs/*`
- `cross-app/core-performance-twr-benchmark-validation.*`
- `cross-app/core-performance-mwr-validation.*`
- `cross-app/core-performance-returns-series-validation.*`
- `cross-app/core-performance-contribution-validation.*`
- `cross-app/core-performance-attribution-validation.*`
- conformance outputs (`*-conformance.*`, `*-compliance.*`, `*-validation.*`)

## Related Docs

- Directory organization: `automation/docs/Directory-Map.md`
- Profiles and execution intent: `automation/docs/Profile-Reference.md`
- Command details and operational examples: `automation/README.md`
