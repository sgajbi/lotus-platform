# RFC-0063: Platform-Wide Rounding and Precision Standard

Status: Proposed  
Author: Platform Engineering  
Date: 2026-02-25

## Problem Statement

Numeric handling differs across services (mix of `Decimal`, `float`, and ad hoc `round(...)`), creating cross-service inconsistencies for equivalent financial scenarios.

## Decision

Adopt a mandatory cross-platform precision standard defined in:

- `docs/standards/Financial Rounding and Precision Standard.md`

Key decisions:

1. Monetary and financial calculations use `Decimal` end-to-end.
2. Intermediate calculations do not round.
3. Final output rounding uses fixed semantic scales and `ROUND_HALF_EVEN`.
4. Shared helper behavior is implemented in each backend service with equivalent contract.
5. Cross-service golden tests are required for equivalence validation.

## Scope

- In scope: lotus-core, lotus-performance, lotus-manage, lotus-report, lotus-gateway, platform governance docs.
- Out of scope: UI rendering precision behavior (consumes lotus-gateway payload as-is).

## Architectural Impact

1. Removes ambiguity in financial correctness guarantees.
2. Improves deterministic replay and reconciliation.
3. Enables shared regression vectors for cross-service consistency.

## Risks and Trade-offs

1. Minor response-value deltas where previous endpoints rounded differently.
2. Migration effort to replace float-based boundary formatting.
3. Requires strict test updates where old precision assumptions existed.

Mitigation:

- Boundary-only behavior changes.
- Golden regression vectors and compatibility notes in release docs.

## Rollout

1. Merge central standard and glossary updates.
2. Patch each backend service with shared precision helper + boundary wiring.
3. Add per-service unit/integration tests and cross-service golden checks.
4. Validate with platform automation and conformance report.

