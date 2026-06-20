# Data Model and Migration Contract Standard

This standard covers item 10 (data model standards) and item 11 (migration framework standardization) for backend services.

## Data Model Standard

1. Each service must publish `docs/standards/data-model-ownership.md`.
2. Ownership boundaries must be explicit and aligned to platform architecture:
   - lotus-core owns core portfolio ledger and valuation data model.
   - lotus-performance owns advanced analytics contract model.
   - lotus-manage owns advisory/discretionary proposal and policy execution model.
   - lotus-report owns reporting and aggregation contract model.
   - lotus-gateway/lotus-gateway owns response-shaping contracts only (no core business persistence).
3. No shared database across services.
4. Canonical terminology must match `docs/standards/Domain Vocabulary Glossary.md`.

## Migration Contract Standard

1. Each service must expose `make migration-smoke` and `make migration-apply`.
2. Each service must publish `docs/standards/migration-contract.md`.
3. `make migration-smoke` must run in CI and be deterministic.
4. Migration strategy is service-native, but contract-unified:
   - versioned migration inventory,
   - deterministic smoke execution,
   - forward-fix policy,
   - immutable applied migrations,
   - documented apply and rollback strategy.

## Service-Specific Modes

- lotus-core: Alembic-backed migration smoke (`alembic heads`, `alembic upgrade head --sql`).
- lotus-manage: forward-only SQL pack contract checks and migration-focused unit smoke.
- lotus-gateway/lotus-performance/lotus-report: no-schema mode with explicit migration contract docs and CI smoke guard.

## Conformance Automation

`automation/Validate-Backend-Standards.ps1` verifies:

- required migration Make targets,
- migration contract doc presence,
- data model ownership doc presence,
- CI migration-smoke gate presence.
