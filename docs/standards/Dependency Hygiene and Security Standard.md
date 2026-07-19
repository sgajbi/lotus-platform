# Dependency Hygiene and Security Standard

## Objective

Maintain zero known critical/high dependency vulnerabilities across all backend repositories.

## Required Controls

1. `make security-audit` in each backend repository.
2. CI must run dependency health/security checks on each PR.
3. Merge is blocked when security audit fails.
4. Dependencies are reviewed and updated continuously.

## Governed Technology Posture

Application libraries, quality-tool dependencies, runtime base images, and deployable container
images are part of Lotus bank-readiness posture. The default technology choice is mature, widely
deployed, well-documented, actively maintained, and supported by broad developer training, scanner
coverage, and operational tooling.

By default, Lotus repositories exclude beta, alpha, preview, experimental, incubating, unsupported,
or novelty-driven major upgrades from runtime and release-image posture. A dependency or base-image
exception must be explicit, issue-backed, time-bounded, owner-assigned, and must record the affected
package or image layer, version or digest, vulnerability posture, exploitability or exposure,
compensating controls, rollback path, expiry or revisit date, and planned fix path.

Critical or high vulnerability findings must be remediated or governed through an approved
time-bounded exception before a PR, release, README, wiki, RFC, or supported-feature claim can call
the result production-ready, bank-buyable, or fully supported. Permanent suppressions, unscoped
scanner logs, missing SBOMs, missing image scans, mutable dependency resolution, and unsupported
base-image families are not acceptable conformance evidence.

Container-image release posture is additionally governed by:

1. `platform-standards/Container-Build-and-Image-Engineering-Standard.md`
2. `platform-standards/Release-Evidence-and-SBOM-Foundation-Standard.md`

## Conformance Artifact

Run:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Generate-Dependency-Vulnerability-Rollup.ps1
```

Outputs:

- `output/dependency-vulnerability-rollup.json`
- `output/dependency-vulnerability-rollup.md`

The rollup report is the platform-level evidence for Item 1 completion.
