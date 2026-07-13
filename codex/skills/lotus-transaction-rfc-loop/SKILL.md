---
name: lotus-transaction-rfc-loop
description: End-to-end workflow for lotus-core transaction RFC delivery (analysis, implementation RFC, slice-by-slice execution, governance gates, PR loop, and branch hygiene). Use when implementing or planning transaction specs such as BUY/SELL/DIVIDEND from docs/rfc-transaction-specs, or when the user asks to run incremental slices with strict RFC-0067 OpenAPI and vocabulary governance.
---

# Lotus Transaction RFC Loop

## Overview

Use this skill to execute lotus-core transaction-type work in a controlled lifecycle: analyze spec, write implementation RFC, execute approved slices, enforce governance gates, and complete PR merge + branch cleanup after each slice.

## Workflow

### 1) Baseline and guardrails

1. Confirm repo is clean and on `main` before starting a new slice.
2. Confirm repo-focus lock before actions:
   - `git rev-parse --show-toplevel`
   - `git remote -v`
   - ensure path/remote matches `lotus-core` when executing this skill
2. Read the target transaction RFC and shared specs:
   - `docs/rfc-transaction-specs/transactions/<TYPE>/RFC-<TYPE>-01.md`
   - `docs/rfc-transaction-specs/shared/*`
3. Read governance requirements:
   - `../lotus-platform/rfcs/RFC-0067-centralized-api-vocabulary-inventory-and-openapi-documentation-governance.md`

### 2) Planning phase (no code)

1. Build gap assessment against current code.
2. Create/update implementation plan RFC under `docs/RFCs/` with:
   - incremental slices
   - tests and evidence per slice
   - risk and open decision points
   - slice tracking table
3. Wait for explicit approval before code changes.

### 3) Slice execution phase

For each approved slice:

1. Create branch: `feat/<rfc-or-slice-name>`.
2. Implement only slice scope.
3. Add meaningful tests first-class (unit + integration as needed).
4. Keep OpenAPI complete (summary/description/tags/responses, field descriptions/examples/types).
5. Enforce canonical snake_case names only; no aliases.
6. Regenerate `lotus-core` vocabulary inventory if contracts changed.
7. If vocabulary changed, sync to `lotus-platform` and run cross-app validator.

### 4) Required validation gates

Run relevant gates before PR:

1. `python -m ruff check ...`
2. `make typecheck`
3. targeted pytest suite for changed slice
4. `python scripts/migration_contract_check.py --mode alembic-sql` (if migration touched)
5. `python scripts/openapi_quality_gate.py` (if API touched)
6. `python scripts/api_vocabulary_inventory.py --output docs/standards/api-vocabulary/lotus-core-api-vocabulary.v1.json` (if API touched)
7. `python scripts/api_vocabulary_inventory.py --validate-only` (if API touched)
8. `python platform-contracts/api-vocabulary/validate_api_vocabulary_catalog.py` in `lotus-platform` (if synced)

### Transaction economics integrity checklist

For transaction types that combine product economics, cash settlement, cost basis, position
movement, or realized P&L:

1. Model each economic role explicitly; do not classify corporate-action proceeds, return of
   capital, redemption proceeds, or transfer consideration as income merely because cash is
   received.
2. Keep the product/economic leg distinct from the actual cash-account settlement leg. Link them
   through canonical event, group, and cash-transaction identifiers.
3. Require source-owned basis allocation when realized P&L or basis transfer depends on it. Fail
   closed when the RFC does not authorize a deterministic fallback.
4. Reconcile local and base basis plus capital, FX, and total P&L components. Do not invent an FX
   split for cross-currency economics without an approved policy and sufficient source evidence.
5. Prove product-level synthetic flows balance at the governed scope and ensure the linked cash
   settlement is not counted again as the same position or portfolio economic flow.
6. Verify that position reducers apply quantity and basis exactly once across source, target,
   product-marker, and cash-instrument legs.
7. Define whether every supplied amount is gross, net of tax/deductions, net of fees, or final
   settlement cash. Optional explicit amounts must not bypass components applied by the derived
   path; prove economically equivalent explicit and derived source shapes produce the same result.
8. Model unsigned economic magnitude separately from ledger direction. Test the direction-by-fee
   matrix, including zero fees and fees equal to or greater than proceeds; never use absolute-value
   signing to hide an invalid negative intermediate amount.
9. Scan sibling transaction types and serializers for the same pattern, including stale calculated
   metadata, generic strategy reuse, generic income classification, omitted reconciliation
   components, and inconsistent component-fee precedence.
10. Add pure domain-policy tests, independently reviewed golden vectors that do not import the
   production calculator, and a database-backed combined workflow test covering persistence,
   linkage, idempotency/replay, reconciliation evidence, and atomic rollback.
11. State unsupported sibling behavior explicitly. Do not broaden cash consideration semantics to
   cash-in-lieu, fractional handling, or another corporate-action family without its own RFC proof.

### 5) PR loop

1. Open PR with explicit slice summary and validation evidence.
2. Enable auto-merge when policy allows.
3. Monitor checks until merged.
4. If checks fail, fix-forward and rerun gates.

### 6) Mandatory branch hygiene after each merged slice

1. Delete local and remote feature branches.
2. Return to `main`.
3. Fast-forward pull from `origin/main`.
4. Confirm clean tree.
5. Validate no leftover remote feature branches using server truth:
   - `git ls-remote --heads origin`
6. Validate no open PRs remain for completed slice:
   - `gh pr list --state open --limit 100`

## Decision rules

1. Prefer incremental additive schema changes over broad rewrites.
2. Never remove unrelated legacy behavior without explicit approval.
3. If domain semantics are ambiguous, stop and record decision options in the RFC before implementation.
4. Keep implementation and docs in same change cycle to avoid drift.
5. Treat transaction classification, basis, cashflow level, P&L decomposition, and position effect
   as one reconciled contract even when separate internal modules own their calculations.

## Evidence format

For each slice, capture:

1. what changed
2. which RFC requirements are now covered
3. tests run and pass/fail outcome
4. residual gaps
5. next slice scope
## Continuous Skill Improvement

At the end of any meaningful use of this skill, decide whether the work exposed a repeatable failure
mode, missing step, weak trigger, validation gap, or context-routing gap. If yes, update the
platform-owned skill source under `lotus-platform/codex/skills/<skill-name>` or its relevant
reference/script in the same delivery slice when the improvement is small and safe. For broader
learning, create a focused follow-up issue or PR instead of relying on chat memory.

Use this decision order:

1. tighten this skill when future agents need different behavior;
2. update `context/LOTUS-SKILL-ROUTING-MAP.md` when routing or overlap changed;
3. update central or repo-local context when source-of-truth changed;
4. add or adjust validators, scaffolds, or gates when deterministic enforcement is better than prose;
5. record an explicit no-change decision in PR evidence, the review ledger, or the task ledger when no durable update is justified.


