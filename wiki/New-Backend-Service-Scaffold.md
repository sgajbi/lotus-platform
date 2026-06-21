# New Backend Service Scaffold

`automation/New-Lotus-Service.ps1` is the platform-owned generator for new Lotus backend
repositories.

Use it when a new backend service should start from the governed Lotus baseline: service profile,
layered package skeleton, repo-native Makefile, explicit CI lanes, starter health/readiness/API
behavior, product-safe errors, structured logs, quality scorecard, endpoint certification,
supported-feature governance, and report-only architecture/quality evidence.

Detailed guide:

- [Lotus Backend Service Scaffold Guide](../docs/onboarding/LOTUS-BACKEND-SERVICE-SCAFFOLD-GUIDE.md)

Common command:

```powershell
cd C:\Users\<user>\projects\lotus-platform
powershell -ExecutionPolicy Bypass -File automation/New-Lotus-Service.ps1 `
  -ServiceName lotus-example `
  -Description "Example Lotus backend service" `
  -ServiceProfile domain-service `
  -DestinationRoot C:\Users\<user>\projects
```

Do not treat a generated repository as bank-buyable by default. The scaffold is a governed starting
point; the owning team must add real domain behavior, tests, endpoint certification,
supported-feature evidence, security posture, observability, runbooks, and wiki truth before
promoting capabilities.

