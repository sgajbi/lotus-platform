---
name: targeted-service-refresh
description: Perform minimal-impact Docker rebuild and restart of only changed services. Use when the user asks to keep the full platform running, refresh only impacted services, avoid full stack restarts, or run changed-files-based service refresh.
---

# Targeted Service Refresh

Refresh only impacted services through `automation/Service-Refresh.ps1`.

## Changed-Files Driven Refresh

```powershell
cd <lotus-platform>
powershell -ExecutionPolicy Bypass -File automation\Service-Refresh.ps1 -ProjectPath <lotus-app-repo> -ChangedOnly -BaseRef origin/main
```

Dry run:

```powershell
powershell -ExecutionPolicy Bypass -File automation\Service-Refresh.ps1 -ProjectPath <lotus-app-repo> -ChangedOnly -DryRun
```

## Explicit Services

```powershell
powershell -ExecutionPolicy Bypass -File automation\Service-Refresh.ps1 -ProjectPath <lotus-app-repo> -Services <service-name>
```

## Rules

- Prefer `-ChangedOnly` first.
- Do not restart full stack unless explicitly requested.
- Check container logs first when service startup fails.

For service mapping details, read `references/mapping.md`.
## Continuous Skill Improvement

At the end of any meaningful use of this skill, decide whether the work exposed a repeatable failure
mode, missing step, weak trigger, validation gap, or context-routing gap. If yes, update the
platform-owned skill source under `lotus-platform/codex/skills/<skill-name>` or its relevant
reference/script in the same delivery slice when the improvement is small and safe. For broader
learning, create a focused follow-up issue or PR instead of relying on chat memory.

Use this decision order:

1. tighten this skill when future agents need different behavior;
2. update `context/LOTUS-SKILL-ROUTING-MAP.md` when routing or overlap changed;
3. update central or repo-local context when source-of-truth changed;
4. add or adjust validators, scaffolds, or gates when deterministic enforcement is better than prose;
5. record an explicit no-change decision in PR evidence, the review ledger, or the task ledger when no durable update is justified.


