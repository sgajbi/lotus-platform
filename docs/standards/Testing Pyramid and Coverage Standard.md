# Testing Pyramid and Coverage Standard

- Scope: lotus-core, lotus-performance, lotus-manage, lotus-report, lotus-gateway (lotus-gateway), and any new backend services.
- Objective: sustain `99%+` meaningful coverage while preserving fast feedback and high signal tests.

## 1. Pyramid Distribution

Target distribution of total tests:

- Unit: `70-85%`
- Integration: `15-25%`
- E2E: `5-10%`

Interpretation:

- Unit tests are the majority and cover domain calculations, policy logic, validations, transformations, and edge cases.
- Integration tests verify adapters and boundaries (HTTP, DB, queues, persistence, dependency wiring).
- E2E tests cover critical cross-service workflows and a small set of high-risk failure paths.

## 2. Coverage Targets

- Meaningful total coverage target per backend app: `>=99%`
- Unit/domain logic coverage target: `95-100%`
- Integration coverage: all key endpoint groups and persistence paths.
- E2E coverage: happy path + high-risk negative path per workflow.

## 3. Meaningful Coverage Rules

Tests must:

- assert business and domain outcomes, not only HTTP status.
- validate failure behavior and error contracts.
- include realistic fixtures and data relationships.
- avoid trivial or duplicate assertions used only to increase line coverage.

Tests must not:

- rely on excessive mocking that bypasses core domain logic.
- count placeholder/smoke tests as primary coverage evidence.
- weaken assertions to satisfy coverage gates.

## 4. Execution Policy

- Run fast unit checks continuously during development.
- Run integration checks on each PR and before merge.
- Run E2E checks on critical path PRs and release gates.
- Keep coverage gates non-decreasing (ratchet up only).

## 5. Automation

Use:

- `automation/Measure-Test-Pyramid.ps1`
- `automation/test-coverage-policy.json`

Outputs:

- `output/test-coverage-summary.md`
- `output/test-coverage-summary.json`

Interpretation note:

- `Collect Errors` in the summary indicates bucket-level pytest collection failures. Counts are still extracted from pytest "collected N items" output, but non-zero `Collect Errors` means the bucket needs remediation before coverage posture can be considered reliable.

## 6. Governance

- Any gate change requires RFC in owning repo or PPD if cross-cutting.
- Architecture-impacting test strategy changes must update:
  - this standard
  - `docs/architecture/Platform Integration Architecture Bible.md`
  - `platform-contracts/cross-cutting-platform-contract.yaml`
