# Platform-Wide Rounding and Precision Standardization Summary

Generated: 2026-02-25
Standard: `docs/standards/Financial Rounding and Precision Standard.md` (`v1.0.0`)
RFC: `RFC-0063-platform-wide-rounding-and-precision-standard.md`

## Compliance Matrix

| Repo | Standard Referenced | Shared Helper Added | Boundary Wiring Applied | Tests Added/Updated | Status |
|---|---|---|---|---|---|
| lotus-core | yes | yes (`precision_policy.py`) | yes (`summary_service.py`) | yes | compliant |
| lotus-performance | yes | yes (`precision_policy.py`) | yes (`engine/breakdown.py`) | yes | compliant |
| lotus-advise | yes | yes (`precision_policy.py`) | yes (`simulation_shared.py`) | yes | compliant |
| lotus-report | yes | yes (`precision_policy.py`) | yes (`aggregation_service.py`) | yes | compliant |
| lotus-gateway | yes | yes (`precision_policy.py`) | yes (`workbench_service.py`) | yes | compliant |
| lotus-platform | yes | n/a | n/a | yes (`Validate-Rounding-Consistency.ps1`) | compliant |

## Cross-Service Equivalence

- Result: `consistent = true`
- Evidence:
  - `output/rounding-consistency-report.json`
  - `output/rounding-consistency-report.md`

## Deviations and Rationale

- No financial rounding deviations detected in configured vectors.
- Non-financial observability latency fields remain float and are explicitly out of scope.

## Unresolved Gaps

- Full-repo deep scan for all historical float monetary fields is not yet automated as a CI gate.
- Next increment: add static rule to fail monetary float usage in model/request/response contracts unless allowlisted.

## Final Sign-off Checklist

- [x] Central standard exists and is versioned.
- [x] RFC created for change control.
- [x] Shared helper adopted/mapped in all backend repos.
- [x] Unit tests for rounding boundaries added.
- [x] Integration boundary behavior validated in touched services.
- [x] Cross-service consistency artifact generated and passing.
- [x] Per-repo standards docs updated.

