# Lotus Developer Onboarding

Use this guide after cloning or pulling the Lotus repositories on a developer machine.

This guide is the human developer entrypoint for RFC-0074. It explains how to prepare the local workspace, how to validate prerequisites, and where to go next for stack bring-up or demo readiness.

It does not replace:

1. [RFC-0071](../../rfcs/RFC-0071-centralized-environment-scoped-service-addressing-and-ingress-governance.md) for canonical ingress governance,
2. [RFC-0072](../../rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md) for CI and validation lanes,
3. [RFC-0073](../../rfcs/RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md) for the governed context system,
4. [RFC-0074](../../rfcs/RFC-0074-repeatable-developer-and-agent-bootstrap-system.md) for the onboarding bootstrap target state,
5. [Local Development Runbook](../operations/Local%20Development%20Runbook.md) for shared ingress and platform-stack operations,
6. [Canonical Front-Office Local Runtime](../../../lotus-workbench/docs/operations/canonical-front-office-local-runtime.md) for populated product-surface bring-up, seeded front-office data, and UI panel validation.

## Purpose

Lotus onboarding must be repeatable, fast, and safe.

The goal is to get a developer to one of three clear states:

1. `ready` for normal repository development,
2. `ready for full-stack validation`,
3. `blocked` with a specific next action.

Onboarding should not silently start Docker stacks, mutate repositories, overwrite local Codex files, or run long E2E suites. Those actions belong to explicit later validation or bootstrap modes.

## Expected Workspace Layout

Use one parent folder for the Lotus repositories.

Recommended Windows layout:

```text
C:\Users\<user>\projects\
  lotus-platform\
  lotus-core\
  lotus-performance\
  lotus-risk\
  lotus-advise\
  lotus-manage\
  lotus-report\
  lotus-render\
  lotus-archive\
  lotus-ai\
  lotus-gateway\
  lotus-workbench\
```

The current local examples often use:

```text
C:\Users\Sandeep\projects\
```

Do not treat that path as the only supported layout. Platform automation and documentation should be path-aware and should accept a different workspace root.

## First Pull Sequence

Start with `lotus-platform` because it owns the central context, onboarding, standards, runbooks, ingress guidance, and platform automation.

```powershell
cd C:\Users\<user>\projects\lotus-platform
git checkout main
git pull --ff-only
```

Then update the repositories needed for the task. For full ecosystem work, update all Lotus repositories:

```powershell
$repos = @(
  "lotus-core",
  "lotus-performance",
  "lotus-risk",
  "lotus-advise",
  "lotus-manage",
  "lotus-report",
  "lotus-render",
  "lotus-archive",
  "lotus-ai",
  "lotus-gateway",
  "lotus-workbench"
)

foreach ($repo in $repos) {
  Push-Location "C:\Users\<user>\projects\$repo"
  git checkout main
  git pull --ff-only
  Pop-Location
}
```

If a repository has local changes, do not force-reset. Inspect the changes and decide whether they are active work, stale generated files, or local-only configuration.

## Prerequisite Classification

### Required For Normal Development

These block normal Lotus development if missing.

| Prerequisite | Check | Expected Posture |
| --- | --- | --- |
| Git | `git --version` | available on `PATH` |
| GitHub CLI | `gh auth status` | authenticated for `github.com` |
| PowerShell | `$PSVersionTable.PSVersion` | available for platform automation |
| Python | `python --version` | compatible with repo tooling |
| Node.js | `node --version` | available for frontend work |
| npm | `npm --version` | available for frontend work |
| Platform repository | `Test-Path .\context\LOTUS-QUICKSTART-CONTEXT.md` | `lotus-platform` pulled locally |
| Repository context | `Test-Path .\REPOSITORY-ENGINEERING-CONTEXT.md` in target repo | local implementation context present |

Minimum check:

```powershell
git --version
gh auth status
python --version
node --version
npm --version
$PSVersionTable.PSVersion
```

### Required For Full-Stack Validation

These may not block documentation or narrow code work, but they block local stack bring-up, demo readiness, and platform end-to-end validation.

| Prerequisite | Check | Expected Posture |
| --- | --- | --- |
| Docker CLI | `docker --version` | installed |
| Docker daemon | `docker info` | running |
| Docker Compose | `docker compose version` | installed |
| Canonical ingress hosts | `automation/Sync-Dev-Ingress-Hosts.ps1` | hosts block present or staged |
| Ingress smoke | `automation/Validate-Dev-Ingress-Smoke.ps1` | `ready` after stack start |
| Shared platform-stack `.env` | `platform-stack\.env` | configured from `.env.example` when shared infra flow is required |
| DSN and environment posture | repo-local `.env` or platform stack `.env` | variables present, secrets not printed |
| Seeded data | governed front-office seed scripts and runbooks | available when demo or panel validation is required |

Use the [Canonical Front-Office Local Runtime](../../../lotus-workbench/docs/operations/canonical-front-office-local-runtime.md) when the task requires populated Workbench, Gateway, Manage, Risk, Performance, Advisor Brief, or Evidence product surfaces.

Use the [Local Development Runbook](../operations/Local%20Development%20Runbook.md) for shared ingress and platform-stack operations rather than as the primary front-office demo bring-up path.

## Canonical Front-Office Runtime

For front-office product validation, demo preparation, screenshot capture, and populated panel checks, the governed path is in `lotus-workbench`.

Use:

```powershell
cd C:\Users\<user>\projects\lotus-workbench
npm run live:stack:up
npm run live:validate
```

The governed reference seed is:

1. portfolio `PB_SG_GLOBAL_BAL_001`
2. benchmark `BMK_PB_GLOBAL_BALANCED_60_40`

Use `npm run live:stack:down` for teardown.

Do not improvise a separate product-surface bring-up from `lotus-platform/platform-stack` when this governed runtime already covers seeded data, canonical endpoints, and populated UI validation.

When a demo screenshot pack and platform-owned validation summary are required, run from `lotus-platform`:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 `
  -ScreenshotDirectory C:\Users\Sandeep\AppData\Local\Temp\lotus-risk-module-shots
```

The screenshot pack is valid only after canonical endpoint, calculation, and panel validation passes.
Pre-validation screenshots must be labelled as diagnostic artifacts and kept separate from demo-ready
evidence.

### Optional Or Task-Specific

These should be reported when relevant but should not block normal onboarding.

| Prerequisite | Required When |
| --- | --- |
| Playwright browser dependencies | UI/browser validation |
| performance profiling tools | latency or load validation |
| local database clients | manual database inspection |
| editor extensions | developer convenience only |
| screenshot tooling | demo capture or UI evidence collection |

## Canonical Context Entry Points

After pulling `lotus-platform`, read context in the smallest useful order.

For normal development:

1. [Lotus Quickstart Context](../../context/LOTUS-QUICKSTART-CONTEXT.md)
2. [Context Reference Map](../../context/CONTEXT-REFERENCE-MAP.md)
3. the target repository's `REPOSITORY-ENGINEERING-CONTEXT.md`
4. the relevant RFC, standard, playbook, or skill for the task

Use the full [Lotus Engineering Context](../../context/LOTUS-ENGINEERING-CONTEXT.md) when the task affects architecture, standards, cross-repo ownership, or governance.

When the task is specifically about README, wiki, or documentation structure, also load:

1. [Lotus Documentation Layering](../documentation/LOTUS-DOCUMENTATION-LAYERING.md)
2. the target repository `README.md`
3. the target repository `wiki/` source when present
4. only the deeper `docs/` pages needed to keep the front-door docs truthful

## Codex Agent Context And Skills

The governed operating contract source is:

1. [AGENTS Operating Contract](../../context/AGENTS-OPERATING-CONTRACT.md)

The deployed local copy normally lives at:

```text
C:\Users\<user>\.codex\AGENTS.md
```

The platform-owned Lotus skill source is:

1. [Lotus Codex Skills](../../codex/skills/README.md)
2. [Lotus Skill Manifest](../../codex/skills/lotus-skill-manifest.json)

For repository README and wiki standardization work, use the governed
`lotus-readme-wiki-governance` skill and keep the repo-local `wiki/` directory as the authored
source when a GitHub wiki exists.

Treat the local Codex profile as a consumer of platform guidance, not the source of truth.

To check global `AGENTS.md` drift from the governed source:

```powershell
cd C:\Users\<user>\projects\lotus-platform
powershell -ExecutionPolicy Bypass -File automation\Sync-AgentOperatingContract.ps1 -CheckOnly
```

To synchronize only `AGENTS.md` after reviewing the change:

```powershell
cd C:\Users\<user>\projects\lotus-platform
powershell -ExecutionPolicy Bypass -File automation\Sync-AgentOperatingContract.ps1
```

To inspect developer-environment readiness without mutating local files:

```powershell
cd C:\Users\<user>\projects\lotus-platform
powershell -ExecutionPolicy Bypass -File automation\Validate-LotusDeveloperEnvironment.ps1 -Mode Inspect -Profile fast
```

To bootstrap governed Lotus Codex skills and `AGENTS.md` into the local Codex profile:

```powershell
cd C:\Users\<user>\projects\lotus-platform
powershell -ExecutionPolicy Bypass -File automation\Bootstrap-LotusDeveloperEnvironment.ps1 -Profile fast
```

The bootstrap script synchronizes only governed Lotus artifacts from `lotus-platform`; unknown local Codex skills are preserved. It writes redacted readiness evidence to:

1. `output/developer-environment-readiness.json`
2. `output/developer-environment-readiness.md`

Do not overwrite local Codex guidance blindly. If a local file has intentional machine-specific content, preserve it or move durable guidance into the governed platform source first.

## GitHub And CI Posture

Lotus uses GitHub as the heavy validation engine.

Use RFC-0072 validation lanes this way:

1. run targeted local checks for the files or behavior you changed,
2. push to a feature branch for Remote Feature Lane validation,
3. open a PR for Pull Request Merge Gate validation,
4. let GitHub run long or expensive checks,
5. monitor asynchronously and fix-forward when a check fails,
6. do not repeatedly run full CI locally unless the failure requires local reproduction.

Useful commands:

```powershell
gh pr checks <pr-number> --watch=false
gh run list --limit 10
gh run view <run-id> --log-failed
```

For PR loop details, use:

1. [PR Loop Playbook](../../context/playbooks/PR-LOOP-PLAYBOOK.md)
2. [Validation Playbook](../../context/playbooks/VALIDATION-PLAYBOOK.md)
3. [Fix-Forward Patterns](../../context/playbooks/FIX-FORWARD-PATTERNS.md)

## Ingress And Canonical Endpoints

Use canonical `*.dev.lotus` endpoints for local platform work.

Canonical local endpoints include:

| Service | Canonical URL |
| --- | --- |
| Workbench | `http://workbench.dev.lotus` |
| Gateway | `http://gateway.dev.lotus` |
| AI | `http://ai.dev.lotus` |
| Manage | `http://manage.dev.lotus` |
| Performance | `http://performance.dev.lotus` |
| Report | `http://report.dev.lotus` |
| Core query | `http://core-query.dev.lotus` |
| Core control-plane | `http://core-control.dev.lotus` |
| Core ingestion | `http://core-ingestion.dev.lotus` |

Host mapping source of truth:

1. `platform-stack/dev-ingress/hosts.example`

Preview host mapping:

```powershell
cd C:\Users\<user>\projects\lotus-platform
powershell -ExecutionPolicy Bypass -File automation\Sync-Dev-Ingress-Hosts.ps1
```

Apply host mapping from an elevated shell:

```powershell
cd C:\Users\<user>\projects\lotus-platform
powershell -ExecutionPolicy Bypass -File automation\Sync-Dev-Ingress-Hosts.ps1 -Apply
```

Verify ingress after the stack is expected to be running:

```powershell
cd C:\Users\<user>\projects\lotus-platform
powershell -ExecutionPolicy Bypass -File automation\Validate-Dev-Ingress-Smoke.ps1
powershell -ExecutionPolicy Bypass -File automation\Explain-Dev-Ingress-Status.ps1
```

Use [RFC-0071](../../rfcs/RFC-0071-centralized-environment-scoped-service-addressing-and-ingress-governance.md), the [Local Development Runbook](../operations/Local%20Development%20Runbook.md), and the [Canonical Front-Office Local Runtime](../../../lotus-workbench/docs/operations/canonical-front-office-local-runtime.md) when ingress status is not `ready` or when a front-office surface must be validated end-to-end.

## DSN And Environment Posture

Onboarding may validate that DSN and environment variables exist, but it must not print secrets.

Rules:

1. never paste DSN passwords, tokens, or secrets into docs, PRs, or chat,
2. prefer `.env.example` files for required variable names,
3. treat actual `.env` files as local-only configuration unless a repo explicitly documents another policy,
4. report DSN posture as present, missing, or malformed without revealing values,
5. use repo-local setup docs for service-specific environment variables.

If connectivity must be tested, use a repo-native or platform-owned command that redacts output.

## Validation Depth

Choose the smallest validation depth that proves the change.

| Change Type | Local Validation | GitHub Validation |
| --- | --- | --- |
| documentation-only | context validator and targeted doc tests | Feature Lane and PR Merge Gate |
| backend code | changed unit tests, lint/typecheck for touched scope | PR Merge Gate, relevant Docker/E2E checks |
| frontend UI | lint/typecheck/unit tests, targeted browser proof when needed | PR Merge Gate and platform UI validation if cross-app |
| ingress/runtime | ingress validation scripts, targeted Docker status checks | Platform validation lane if release/demo critical |
| cross-repo integration | contract tests and targeted smoke | PR gates for touched repos plus platform E2E where relevant |

Do not run full local CI reflexively. Use local checks to prove the fix, then let GitHub run the expensive matrix.

## Fresh Machine Readiness Checklist

Use this checklist after a new clone or pull.

1. `lotus-platform` is present and on the intended branch.
2. Required repositories for the task are present.
3. `gh auth status` is authenticated.
4. Git, PowerShell, Python, Node, npm, Docker, and Docker Compose are installed as required by the task.
5. `context/LOTUS-QUICKSTART-CONTEXT.md` exists.
6. The target repo has `REPOSITORY-ENGINEERING-CONTEXT.md`.
7. Global `AGENTS.md` drift has been checked if Codex will be used.
8. Canonical ingress hosts are configured when full-stack validation is required.
9. DSN and `.env` posture is present when runtime validation is required.
10. The validation depth for the first task is selected before running expensive checks.

## Current RFC-0074 Boundary

RFC-0074 is implemented and governed. platform-owned bootstrap automation exists.

Current automation supports:

1. inspect mode for read-only readiness checks,
2. sync mode for governed Lotus skill and `AGENTS.md` synchronization,
3. validate mode for explicit readiness gating,
4. fast, extended, and platform validation profiles,
5. redacted JSON and Markdown readiness reports,
6. onboarding drift controls through context validation,
7. repository-local cross-links back to the central onboarding and ramp-up guides.
