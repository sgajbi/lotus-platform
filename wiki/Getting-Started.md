# Getting Started

## Recommended workspace layout

```text
C:\Users\<user>\projects\
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
cd C:\Users\<user>\projects\lotus-platform
powershell -ExecutionPolicy Bypass -File automation\Validate-LotusDeveloperEnvironment.ps1 -Mode Inspect -Profile fast
```

## Sync governed local Codex guidance

```powershell
cd C:\Users\<user>\projects\lotus-platform
powershell -ExecutionPolicy Bypass -File automation\Bootstrap-LotusDeveloperEnvironment.ps1 -Profile fast
```

## Context reading order

1. [Lotus Quickstart Context](../context/LOTUS-QUICKSTART-CONTEXT.md)
2. [Lotus Engineering Context](../context/LOTUS-ENGINEERING-CONTEXT.md)
3. the target repo `REPOSITORY-ENGINEERING-CONTEXT.md`
4. [Context Reference Map](../context/CONTEXT-REFERENCE-MAP.md)

## Documentation work path

When the task is about README, wiki, or deeper docs rather than code behavior, add this before
editing:

1. [Lotus Documentation Layering](../docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md)
2. the target repo `README.md`
3. the target repo `wiki/` source when present
4. only the deeper `docs/` pages needed to keep the README and wiki truthful

Use this path to avoid turning the README into a second wiki or the wiki into a second `docs/`
tree.

## Important runtime note

For canonical populated front-office validation, use `lotus-workbench`:

```powershell
cd C:\Users\<user>\projects\lotus-workbench
npm run live:stack:up
npm run live:validate
```

Use `lotus-platform` when you need ingress support, platform-owned evidence wrappers, or
cross-repository governance automation.
