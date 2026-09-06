# Getting Started

Current support starts with environment inspection and platform validation. Product startup follows
the owning repository's runbook.

## Start Here

| Goal | First action |
| --- | --- |
| Inspect prerequisites | Run the environment inspection below. |
| Validate `lotus-platform` | Run the platform repository checks below. |
| Start populated front-office products | Follow the Workbench-owned runtime guide linked below. |

## Recommended workspace layout

```text
<workspace-root>/
  lotus-platform\
  lotus-core\
  lotus-performance\
  lotus-risk\
  lotus-advise\
  lotus-manage\
  lotus-report\
  lotus-ai\
  lotus-gateway\
  lotus-workbench\
```

## First checks

```powershell
git --version
gh auth status
python --version
node --version
npm --version
$PSVersionTable.PSVersion
```

## Platform readiness inspection

```powershell
$env:LOTUS_WORKSPACE_ROOT = "<workspace-root>"
Set-Location "$env:LOTUS_WORKSPACE_ROOT/lotus-platform"
powershell -ExecutionPolicy Bypass -File automation\Validate-LotusDeveloperEnvironment.ps1 -Mode Inspect -Profile fast
```

## Sync governed local Codex guidance

```powershell
Set-Location "$env:LOTUS_WORKSPACE_ROOT/lotus-platform"
powershell -ExecutionPolicy Bypass -File automation\Bootstrap-LotusDeveloperEnvironment.ps1 -Profile fast
```

## Context reading order

1. the target repository's `AGENTS.md`
2. [Lotus Quickstart Context](https://github.com/sgajbi/lotus-platform/blob/main/context/LOTUS-QUICKSTART-CONTEXT.md)
3. the target repository's `REPOSITORY-ENGINEERING-CONTEXT.md`
4. [Lotus Skill Routing Map](https://github.com/sgajbi/lotus-platform/blob/main/context/LOTUS-SKILL-ROUTING-MAP.md)

Load the engineering context, reference map, procedural memory, and specialist documentation only
when the task route calls for them.

## Documentation work path

When the task is about README, wiki, or deeper docs rather than code behavior, add this before
editing:

1. [Lotus Documentation Layering](https://github.com/sgajbi/lotus-platform/blob/main/docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md)
2. the target repo `README.md`
3. the target repo `wiki/` source when present
4. only the deeper `docs/` pages needed to keep the README and wiki truthful

Use this path to avoid turning the README into a second wiki or the wiki into a second `docs/`
tree.

## New backend services

Use the platform scaffold when creating a new Lotus backend repository:

```powershell
Set-Location "$env:LOTUS_WORKSPACE_ROOT/lotus-platform"
powershell -ExecutionPolicy Bypass -File automation\New-Lotus-Service.ps1 `
  -ServiceName lotus-example `
  -Description "Example Lotus backend service" `
  -ServiceProfile domain-service `
  -DestinationRoot $env:LOTUS_WORKSPACE_ROOT
```

See [New Backend Service Scaffold](New-Backend-Service-Scaffold) for the wiki summary and
[Lotus Backend Service Scaffold Guide](https://github.com/sgajbi/lotus-platform/blob/main/docs/onboarding/LOTUS-BACKEND-SERVICE-SCAFFOLD-GUIDE.md)
for the detailed generated-feature and usage guide.

## Important runtime note

For canonical populated front-office validation, use `lotus-workbench`:

```powershell
Set-Location "$env:LOTUS_WORKSPACE_ROOT/lotus-workbench"
npm run live:stack:up
npm run live:validate
```

Use `lotus-platform` when you need ingress support, platform-owned evidence wrappers, or
cross-repository governance automation.
