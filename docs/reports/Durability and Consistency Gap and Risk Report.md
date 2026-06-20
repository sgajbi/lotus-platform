# Durability and Consistency Gap and Risk Report

Status source: `output/durability-consistency-compliance.md`.

## A. Do Now (Pre-Launch Must-Haves)

This report tracks closure state for mandatory durability/consistency controls:
- durability for core entities
- explicit strong/eventual workflow classification
- idempotent write semantics
- atomic transaction boundaries
- canonical as-of semantics
- deterministic concurrency/conflict handling
- financial data-integrity constraints
- release-gate test coverage by level
- governance/change-control references

## B. Phase Next (Before First Client Go-Live)

- Cross-service saga reliability hardening.
- Automated consistency drift-detection jobs.
- Expanded reconciliation coverage and exception workflows.
- Dashboards for idempotency/replay/conflict metrics.

## C. Phase Later (Scale Hardening)

- Outbox/inbox patterns where required.
- Formal consistency SLO and automated conformance checks.
- Audit-evidence packaging and due-diligence bundles.

## D. Per-Repo Plan

| Repo | Priority Next Step | Effort |
|---|---|---|
| lotus-gateway | Harden idempotency propagation + write-workflow consistency evidence | M |
| lotus-core | Extend atomicity + late-arrival regression coverage in ingestion/recompute paths | M |
| lotus-performance | Expand deterministic replay and lotus-core-input validation evidence for stateless mode | M |
| lotus-advise | Harden conflict and replay telemetry evidence for workflow actions | M |
| lotus-report | Expand deterministic report-output replay coverage and provenance metadata evidence | S |

## E. Definition of Done + Evidence

Done criteria:
- All Do-Now requirements show `Implemented` in the compliance matrix, or `Partial` only with explicit blocker and remediation action.
- Evidence links point to code/tests/docs (not plan-only statements).
- Validation script is repeatable and committed in PPD automation.

Required artifacts:
- `docs/standards/Durability and Consistency Standard.md`
- `output/durability-consistency-compliance.json`
- `output/durability-consistency-compliance.md`
- per-repo `docs/standards/durability-consistency.md`


