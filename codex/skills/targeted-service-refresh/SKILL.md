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
