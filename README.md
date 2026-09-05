# lotus-platform

> The shared engineering foundation for Lotus.

Lotus is a suite of independently owned applications for private-banking portfolio management,
analytics, advice, operations, and reporting. `lotus-platform` helps teams develop, integrate,
validate, and operate those applications through shared contracts, standards, tooling, runtime
support, and cross-repository assurance.

This repository owns the engineering foundation around the applications, not their business
capabilities. Domain behavior and implementation truth stay with the owning repositories. Start
with the [Lotus ecosystem overview](wiki/Home.md) for the wider system.

## Reader Paths

| Goal | Start here | Outcome |
| --- | --- | --- |
| Understand the ecosystem | [Ecosystem overview](wiki/Home.md) | See the platform, applications, ownership, and evidence paths |
| Onboard a developer | [Developer onboarding](docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md) | Prepare a workspace and choose the right validation flow |
| Contribute to platform tooling | [Repository engineering context](REPOSITORY-ENGINEERING-CONTEXT.md) | Follow local boundaries, commands, and delivery gates |
| Operate shared infrastructure | [Operations runbook](wiki/Operations-Runbook.md) | Inspect ingress, shared services, QA wrappers, and recovery paths |
| Review standards and evidence | [Documentation index](docs/README.md) | Navigate standards, contracts, RFCs, quality evidence, and decisions |

## Role And Operational Posture

`lotus-platform` owns shared automation, cross-repository validation, platform contracts and
standards, central engineering context, governed agent skills, and shared ingress and
infrastructure support. It does not own domain APIs, application behavior, or the canonical
populated front-office runtime.

The context system, CI lanes, validators, onboarding guidance, and platform standards are active
engineering controls. Shared infrastructure lives under `platform-stack`; integrated populated
product startup belongs to `lotus-workbench`. Platform automation wraps that runtime when
cross-application QA or durable evidence is required.

Current contract assertions:

- Human approval reviews are optional; green required checks and resolved review conversations are
  mandatory.
- `lotus-idea` is included by default in canonical platform QA.
- The canonical private-banking seed data excludes the demo pack by default.

See [Platform Surfaces](wiki/Platform-Surfaces.md) for the detailed ownership map and
[quality/baseline_report.md](quality/baseline_report.md) for the current enterprise backend quality
baseline.

## Repository Map

| Responsibility | Primary paths | Authoritative guide |
| --- | --- | --- |
| Automation and assurance | `automation/`, `tests/unit/` | [Automation guide](automation/README.md) |
| Contracts and standards | `platform-contracts/`, `platform-standards/` | [Platform standards](platform-standards/README.md) |
| Context and onboarding | `context/`, `docs/onboarding/` | [Context system](context/README.md) |
| Shared runtime support | `platform-stack/` | [Platform stack](platform-stack/README.md) |
| Agent workflow source | `codex/skills/` | [Lotus skills](codex/skills/README.md) |
| Decisions and evidence | `rfcs/`, `quality/`, `docs/`, `wiki/` | [Documentation index](docs/README.md) |

## Getting Started

Run commands from the repository root in PowerShell. Normal platform work requires Git, an
authenticated GitHub CLI, PowerShell, and Python; Node.js, npm, and Docker are required only by
the selected workflow. The [developer onboarding guide](docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md)
contains the complete prerequisite matrix.

### 1. Inspect the environment

```powershell
powershell -ExecutionPolicy Bypass -File automation\Validate-LotusDeveloperEnvironment.ps1 -Mode Inspect -Profile fast
```

Expected result: a non-mutating readiness report that identifies available tools, repository
state, and any task-specific gaps.

### 2. Validate this repository

```powershell
powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane feature
```

Expected result: platform feature-lane contract checks pass locally. Workflow lint runs in a
separate GitHub job. Use the lane summary below when preparing or verifying a merge.

### 3. Start populated products only when needed

Use the Workbench-owned
[Canonical Front-Office Local Runtime](https://github.com/sgajbi/lotus-workbench/blob/main/docs/operations/canonical-front-office-local-runtime.md)
for `npm run live:stack:up`, `npm run live:validate`, and `npm run live:stack:down`.

When platform-owned cross-application assurance or a governed evidence pack is required, invoke
the QA wrapper from this repository:

```powershell
powershell -ExecutionPolicy Bypass -File automation\Invoke-Canonical-FrontOffice-QA.ps1 -BringUp
```

The wrapper validates and records the integrated flow; it does not transfer runtime ownership from
Workbench. Review the [operations runbook](wiki/Operations-Runbook.md) before using cleanup or
evidence options.

## Validation Summary

| Intent | Command |
| --- | --- |
| Feature feedback | `powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane feature` |
| Pull-request parity | `powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane pr-merge` |
| Exact-main release proof | `powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane main-releasability` |
| Context drift | `python automation/validate_engineering_context_system.py` |

GitHub enforces the remote feature, pull-request merge, and main releasability gates. See
[Validation and CI](wiki/Validation-and-CI.md) for lane definitions, evidence, and specialist
commands.

## Documentation

- [Documentation index](docs/README.md): technical guides, standards, reports, and evidence
- [Central context system](context/README.md): cross-repository truth, routing, and playbooks
- [Platform standards](platform-standards/README.md): reusable engineering controls and templates
- [Automation guide](automation/README.md): command catalog and operator behavior
- [RFC inventory](rfcs/README.md): governed decisions and delivery status
- [Documentation layering](docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md): source placement rules
- [Troubleshooting](wiki/Troubleshooting.md): operator diagnosis and recovery navigation

Repository-authored pages under [wiki/](wiki/) are the canonical wiki source. A separate GitHub
wiki repository is publication transport only.
