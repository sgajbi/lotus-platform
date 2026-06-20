# Durability and Consistency Standard

- Version: 1.0.0
- Status: Active
- Scope: lotus-core, lotus-performance, lotus-manage, lotus-report, lotus-gateway (lotus-gateway)
- Change control: Any change to mandatory rules requires an RFC in `lotus-platform/rfcs` and ADR for exceptions.

## A. Do Now (Pre-Launch Must-Haves)

1. Durability guarantees for core entities
- Core write paths (transactions, positions, cash/ledger events, valuations/snapshots, reference data updates) must use durable persistence.
- No best-effort write semantics for core flows. Persistence failures must fail explicitly and be observable.

2. Consistency classification by workflow
- Every service must document workflow consistency class (`strong` vs `eventual`).
- Strong consistency is mandatory for:
  - transaction ingestion/booking
  - position and cash updates
  - valuation state per as-of
  - cost basis and realized/unrealized P&L
  - portfolio snapshots used for proposals/reporting

3. Idempotency/logical exactly-once for writes
- Critical write APIs must support `Idempotency-Key` (or equivalent deterministic dedupe contract).
- Replay protection must be enforced with unique constraints, natural keys, or canonical request-hash mapping.
- Retries must not create duplicate business effects.

4. Transaction boundaries and atomicity
- Coupled state transitions must be atomic (commit/rollback).
- Partial updates that can diverge portfolio and ledger state are not permitted.
- Multi-step cross-service workflows must define orchestration/compensation behavior.

5. As-of semantics
- Use canonical `as_of_date`/`as_of_ts` semantics at service boundaries.
- Same input + same as-of + same policy/config version must produce deterministic outputs.
- Responses should include reproducibility metadata (source timestamp and policy/engine/config version) where applicable.

6. Concurrency/conflict handling
- Apply optimistic versioning or equivalent conflict controls where concurrent updates are possible.
- Define deterministic ordering and late-arrival handling.
- Define conflict policy: reject, reconcile, or reprocess.

7. Data integrity constraints
- Enforce DB/API/import constraints (FK/unique/check/schema validations) for financial invariants.
- Invariants must be checked at boundaries and domain layer.

8. Tests as release gates
- Unit tests for idempotency/invariants.
- Integration tests for transaction boundaries, rollback, and atomicity.
- E2E for ingest -> positions -> valuation -> analytics -> reporting where applicable.
- Concurrency/replay/late-arrival regressions for critical paths.

9. Governance artifacts
- Each backend repo must maintain `docs/standards/durability-consistency.md`.
- Deviations require ADR with rationale, mitigation, and expiry review date.

## B. Phase Next (Before First Client Go-Live)

1. Cross-service saga reliability hardening and replay tooling.
2. Automated consistency verification and drift-detection jobs.
3. Expanded reconciliation coverage and exception workflow handling.
4. Operational dashboards for idempotency/replay/conflict metrics.

## C. Phase Later (Scale Hardening)

1. Outbox/inbox and advanced eventing guarantees where needed.
2. Formal consistency SLOs with automated conformance checks.
3. Audit-evidence packaging for due diligence and controls testing.

## D. Per-Repo Implementation Plan

- `lotus-core`:
  - enforce durable ingestion and epoch-consistent query boundaries
  - keep idempotent consumer processing and invariant checks
  - publish explicit as-of/version metadata contracts
- `lotus-performance`:
  - preserve deterministic analytics runs for identical inputs/as-of
  - classify eventual vs strong boundaries for lotus-core-sourced inputs
  - enforce import/schema validation for stateless mode payloads
- `lotus-advise`:
  - enforce idempotent workflow writes and durable run/proposal persistence
  - keep conflict/replay behavior deterministic and testable
  - standardize late-arrival/retry semantics
- `lotus-report`:
  - keep deterministic reporting snapshots by as-of inputs
  - enforce request validation and reproducibility metadata
  - maintain explicit read-only consistency boundaries
- `lotus-gateway`:
  - enforce idempotency propagation on write orchestration endpoints
  - preserve deterministic response shaping and reproducibility metadata
  - keep strong consistency boundaries explicit for write-through workflows
- `lotus-platform`:
  - hold canonical policy and run validators/evidence artifacts

## E. Definition of Done + Evidence

Done requires:
- Central standard merged and referenced by backend repos.
- Repo-level implementation merged for Do-Now controls (code + tests + docs evidence).
- Compliance matrix regenerated with repo/workflow/requirement status.
- No unresolved `Missing` statuses for mandatory Do-Now requirements without documented blocker/ADR.

Evidence artifacts:
- `output/durability-consistency-compliance.json`
- `output/durability-consistency-compliance.md`
- per-repo `docs/standards/durability-consistency.md`

## Non-Negotiable Rules

1. No shared DB integration across services; API contracts remain integration boundary.
2. One source of truth per domain concept; no duplicated ownership.
3. No hidden eventual consistency in strong-consistency workflows.
4. Any deviation requires ADR with mitigation and expiry review date.


