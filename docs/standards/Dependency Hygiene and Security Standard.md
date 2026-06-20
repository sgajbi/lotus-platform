# Dependency Hygiene and Security Standard

## Objective

Maintain zero known critical/high dependency vulnerabilities across all backend repositories.

## Required Controls

1. `make security-audit` in each backend repository.
2. CI must run dependency health/security checks on each PR.
3. Merge is blocked when security audit fails.
4. Dependencies are reviewed and updated continuously.

## Conformance Artifact

Run:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Generate-Dependency-Vulnerability-Rollup.ps1
```

Outputs:

- `output/dependency-vulnerability-rollup.json`
- `output/dependency-vulnerability-rollup.md`

The rollup report is the platform-level evidence for Item 1 completion.
