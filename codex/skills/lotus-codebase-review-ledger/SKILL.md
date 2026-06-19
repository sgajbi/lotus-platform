---
name: lotus-codebase-review-ledger
description: Run a systematic, pattern-based codebase review for a Lotus repository and keep a durable ledger of findings, fixes, follow-up work, and sign-off evidence. Use when the user wants to review architecture, stale code, modularity, duplicate logic, database query quality, hardening gaps, or missing tests; when they want a persistent review log showing what has already been examined; or when they want a cleanup/refactor program driven by patterns rather than ad hoc file-by-file edits.
---

# Lotus Codebase Review Ledger

## Overview

Use this skill to turn repository cleanup and hardening into a controlled engineering program.
Do not produce a loose punch list. Create or update a review playbook and ledger, review by
pattern first, record evidence, and only sign off scopes that are actually proven.

Read the repository's existing review artifacts first if they exist. In `lotus-core`, prefer:

- `docs/architecture/CODEBASE-REVIEW-PLAYBOOK.md`
- `docs/architecture/CODEBASE-REVIEW-LEDGER.md`

If they do not exist, create them.

## Workflow

### 1. Establish the review control documents

Create or update:

- a playbook that defines:
  - review units
  - status model
  - evidence requirements
  - sign-off standard
- a ledger that records:
  - review id
  - scope/pattern
  - status
  - findings
  - actions taken
  - follow-up
  - evidence

Keep these documents concise and operational.

### 2. Review by pattern first

Prefer patterns such as:

- duplicate repository or service logic
- async orchestration, stage transitions, and quiescence
- replay/idempotency/fencing correctness
- hot-path DB query shape and locking semantics
- consumer lifecycle and startup/shutdown behavior
- OpenAPI/example consistency
- stale code, dead code, or documentation drift
- clean report-only quality inventories that should become CI regression blockers

Only do file-by-file review when a single file is the real risk unit.

### 3. Classify every important finding

Use concrete classes:

- stale code
- duplication
- modularity problem
- query/performance risk
- race-condition or correctness risk
- observability gap
- test gap
- documentation drift
- CI-enforcement gap

Do not record vague findings like "needs cleanup" without a specific class and consequence.

### 4. Fix in small slices

For each material finding:

1. record it in the ledger
2. fix the issue in the smallest coherent slice
3. add lower-level tests if the issue was previously only visible in E2E or heavy runtime checks
4. update the ledger with evidence

Prefer pushing invariants downward into:

- unit tests
- repository/query-shape tests
- DB-backed integration tests
- repo-native quality gates when the invariant is deterministic and broadly protective

Use full E2E and heavy gates as proof, not as the primary debugging loop.

### 5. Require evidence before sign-off

Do not mark a scope as signed off unless you have:

- code changes if needed
- tests or characterization evidence
- runtime or heavy-gate evidence when relevant
- explicit follow-up items for anything not completed

If a scope is improved but not fully converged, use `Hardened` or `Refactor Needed`, not `Signed Off`.

## Default artifact model

Unless the repository already has a stronger convention, use:

- `docs/architecture/CODEBASE-REVIEW-PLAYBOOK.md`
- `docs/architecture/CODEBASE-REVIEW-LEDGER.md`

If the repo needs a deeper template, read:

- `references/review-entry-template.md`

## Expected outputs

For a normal review batch, produce:

1. updated playbook or confirm it remains valid
2. updated ledger entries with explicit statuses
3. code/test/docs changes for the reviewed scope
4. a short summary of:
   - what was reviewed
   - what was fixed
   - what remains open

## Guardrails

- Do not claim "100% confidence." Use evidence-based language.
- Do not close a review scope just because one E2E run passed.
- Do not let duplicate implementations drift without direct tests on both sides.
- Do not mix unrelated cleanup into one ledger entry.
