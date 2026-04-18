# lotus-platform

Shared platform, governance, automation, and runtime support repository for the Lotus ecosystem.

Repository-local engineering context:
[REPOSITORY-ENGINEERING-CONTEXT.md](REPOSITORY-ENGINEERING-CONTEXT.md)

Central context system:
[context/README.md](context/README.md)

Developer onboarding:
[docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md](docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md)

## Purpose And Scope

`lotus-platform` is the platform-governance repository for Lotus.

It owns:

- shared automation
- ingress and environment-level runtime support
- cross-repository validation
- standards, templates, and validators
- onboarding and agent-operating guidance
- ecosystem-wide governance RFCs and durable context

It does not own:

- business-domain APIs
- portfolio, performance, risk, advisory, management, reporting, or AI domain truth
- the canonical front-office product runtime itself, which is governed through `lotus-workbench`

## Ownership And Boundaries

`lotus-platform` is the central engineering system around Lotus, not the product surface and not a
domain service.

Boundary rules that matter:

1. platform-wide truth belongs here
2. repository-local implementation truth stays in the owning repository
3. `platform-stack` owns shared ingress and infrastructure support, not the canonical populated
   front-office product runtime
4. standards-only changes are incomplete unless validator, scaffold, automation, or runbook impact
   is considered

## Current Operational Posture

1. RFC-0072 CI lane and validation governance is active.
2. RFC-0073 central context and agent-guidance governance is active.
3. RFC-0074 developer and agent bootstrap governance is active.
4. The context system, onboarding guides, skills, and platform validators are already part of the
   living engineering contract.
5. Canonical populated product proof routes through `lotus-workbench`, while `lotus-platform`
   supports ingress, shared automation, evidence wrappers, and governance around that flow.

## Architecture At A Glance

Primary platform surfaces:

- `automation/`
  PowerShell and Python automation for repo checks, ingress, QA, CI alignment, PR loops, and
  cross-app validation
- `context/`
  central Lotus context system, registries, playbooks, and governed operating contract
- `platform-standards/`
  templates and standards for backend repositories and workflow baselines
- `platform-stack/`
  shared local ingress and infrastructure orchestration
- `codex/skills/`
  platform-owned Lotus skill source
- `rfcs/`
  ecosystem and platform governance RFCs
- `docs/onboarding/`
  governed onboarding and ramp-up guides

## Repository Layout

- `automation/`
  operational commands, validators, background-run tooling, QA entrypoints, and automation docs
- `context/`
  quickstart, engineering context, routing guides, registries, contracts, and playbooks
- `platform-standards/`
  reusable standards and scaffold templates
- `platform-stack/`
  shared local stack, ingress, and observability support assets
- `codex/skills/`
  Lotus-owned skills and manifest
- `rfcs/`
  governance and implementation RFC inventory
- `tests/unit/`
  documentation, validator, standards, and automation contract tests
- `wiki/`
  canonical authored source for GitHub wiki publication

## Quick Start

Developer readiness inspection:

```powershell
powershell -ExecutionPolicy Bypass -File automation\Validate-LotusDeveloperEnvironment.ps1 -Mode Inspect -Profile fast
```

Platform repo checks:

```powershell
powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane feature
```

Canonical ingress host sync preview:

```powershell
powershell -ExecutionPolicy Bypass -File automation\Sync-Dev-Ingress-Hosts.ps1
```

Canonical front-office QA wrapper:

```powershell
powershell -ExecutionPolicy Bypass -File automation\Invoke-Canonical-FrontOffice-QA.ps1 -BringUp
```

Important runtime note:

- use `lotus-workbench` for canonical populated front-office validation
- use `lotus-platform` for ingress, governance, validation wrappers, and ecosystem-wide automation
- use [`wiki/Platform-Surfaces.md`](wiki/Platform-Surfaces.md) when you need to decide which
  platform-owned area is responsible for a task

## Common Commands

- `powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane feature`
  feature-lane repo checks
- `powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane pr-merge`
  PR merge gate parity
- `powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane main-releasability`
  main releasability parity
- `powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformValidationLane.ps1 -ValidationProfile core-performance-green-lanes`
  platform validation lane
- `python -m pytest tests/unit -q`
  targeted unit contract tests
- `python -m pytest tests/unit/test_engineering_context_system_contract.py tests/unit/test_dev_ingress_status_automation_contract.py tests/unit/test_front_office_runtime_automation_contract.py -q`
  high-signal targeted documentation and operator contract pack
- `python automation/validate_engineering_context_system.py`
  context-system drift validation
- `powershell -ExecutionPolicy Bypass -File automation\Validate-Service-Addressing.ps1`
  RFC-0071 addressing drift validation
- `powershell -ExecutionPolicy Bypass -File automation\Validate-Shared-Infrastructure-Ownership.ps1`
  RFC-0068 shared-infrastructure boundary validation

## Validation And CI Lanes

`lotus-platform` uses:

1. `Remote Feature Lane`
2. `Pull Request Merge Gate`
3. `Main Releasability Gate`
4. `Platform End-to-End Validation`

For documentation and context slices:

- use targeted doc-contract tests locally
- keep automation and context validators green
- let GitHub carry the heavier full matrix

## Platform Contract Notes

Important current platform truths:

1. the central context system under `context/` is a governed delivery artifact, not auxiliary prose
2. platform-owned skills under `codex/skills/` are the durable Lotus source of truth for skill
   distribution
3. `platform-stack` is the shared ingress and infrastructure baseline, not the canonical populated
   front-office product proof flow
4. repo-local truth should live in repository-local engineering context docs rather than being
   duplicated here
5. documentation changes in this repo are partially governed by unit-level documentation contract
   tests and should be treated as contract work, not just prose edits

## Documentation Map

- central context system:
  [context/README.md](context/README.md)
- task routing guide:
  [context/TASK-ROUTING-GUIDE.md](context/TASK-ROUTING-GUIDE.md)
- skill routing map:
  [context/LOTUS-SKILL-ROUTING-MAP.md](context/LOTUS-SKILL-ROUTING-MAP.md)
- developer onboarding:
  [docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md](docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md)
- agent ramp-up:
  [docs/onboarding/LOTUS-AGENT-RAMP-UP.md](docs/onboarding/LOTUS-AGENT-RAMP-UP.md)
- automation guide:
  [automation/README.md](automation/README.md)
- platform stack:
  [platform-stack/README.md](platform-stack/README.md)
- platform standards:
  [platform-standards/README.md](platform-standards/README.md)
- RFC inventory:
  [rfcs/README.md](rfcs/README.md)
- documentation layering:
  [docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md](docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md)
- platform narrative and commercial framing:
  [wiki/Investor-Pitch.md](wiki/Investor-Pitch.md)
- platform market framing:
  [wiki/Market-Landscape.md](wiki/Market-Landscape.md)
- platform responsibility map:
  [wiki/Platform-Surfaces.md](wiki/Platform-Surfaces.md)
- troubleshooting:
  [wiki/Troubleshooting.md](wiki/Troubleshooting.md)
- wiki home:
  [wiki/Home.md](wiki/Home.md)

## Wiki Source

Repository-authored wiki pages live under [wiki/](wiki). If the GitHub wiki is published later,
keep `wiki/` as the canonical source and treat any separate `*.wiki.git` clone as publication
plumbing only.
