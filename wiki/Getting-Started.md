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

## Important runtime note

For canonical populated front-office validation, use `lotus-workbench`:

```powershell
cd C:\Users\<user>\projects\lotus-workbench
npm run live:stack:up
npm run live:validate
```

Use `lotus-platform` when you need ingress support, platform-owned evidence wrappers, or
cross-repository governance automation.
