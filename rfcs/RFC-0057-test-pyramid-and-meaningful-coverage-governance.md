# RFC-0057: Test Pyramid and Meaningful Coverage Governance

## Status

Proposed

## Date

2026-02-24

## Authors

Platform Engineering

## Problem Statement

Backend services currently use inconsistent test distributions and non-uniform coverage expectations. This creates uneven confidence, slower defect detection, and weak comparability across lotus-core, lotus-performance, lotus-manage, lotus-report, and lotus-gateway.

## Decision

Adopt a cross-platform standard that enforces:

- Meaningful coverage target per backend service: `>=99%`.
- Test pyramid distribution targets:
  - Unit: `70-85%`
  - Integration: `15-25%`
  - E2E: `5-10%`
- Domain logic unit coverage target: `>=95%`.
- Quality rules that prohibit coverage gaming and require domain outcome assertions and high-risk negative paths.

The standard is codified in:

- `docs/standards/Testing Pyramid and Coverage Standard.md`
- `platform-contracts/cross-cutting-platform-contract.yaml`
- `automation/test-coverage-policy.json`
- `automation/Measure-Test-Pyramid.ps1`

## Architectural Impact

- Introduces a platform-level testing contract owned by PPD.
- Enables objective, repeatable validation across repositories.
- Creates consistent reporting artifacts for governance and PR readiness.

## Risks and Trade-offs

- Short-term delivery speed may decrease while services close coverage and pyramid gaps.
- Some repositories may require test refactoring to rebalance over-weighted unit or integration suites.
- Coverage targets must remain meaningful; trivial tests do not satisfy policy intent.

## High-Level Implementation Approach

1. Establish policy and automation in PPD (this RFC phase).
2. Generate baseline reports for all backend services.
3. Open per-repo hardening RFCs/PRs to close measured gaps.
4. Add non-decreasing CI gates per service until target state is reached.

## Rollout and Validation

- Run:
  - `powershell -ExecutionPolicy Bypass -File automation/Measure-Test-Pyramid.ps1 -RunCoverage`
- Review:
  - `output/test-coverage-summary.md`
  - `output/test-coverage-summary.json`
- Track remediation by service in follow-on RFCs and PRs.

