---
name: lotus-rfc-review-loop
description: Standardize and govern RFC documentation in Lotus repositories through an iterative review loop. Use when a user asks to audit many RFCs without sacrificing quality, classify each RFC against current implementation reality, normalize RFC structure, produce/update an RFC index with status tracking, identify archive candidates, and define prioritized next actions.
---

# Lotus RFC Review Loop

Run a disciplined, repeatable RFC quality loop in small batches to preserve depth and correctness.

## Non-Negotiable Quality Rules

1. **Preserve requirement fidelity**: Never collapse an RFC into a short status summary that drops original asks.
2. **Always capture three views** in each reviewed RFC:
   - What was originally requested.
   - What is implemented now (with code/test evidence).
   - Why the implementation/design choices make sense (or no longer make sense) now.
3. **Traceability is mandatory**: Every major requirement must map to concrete implementation evidence or a clear gap.
4. **Delta discipline**:
   - Propose deltas only after verifying they are not already implemented.
   - Evaluate whether each delta is still relevant given current app state and lotus-platform standards.
   - Mark as `done`/`deferred` when appropriate; avoid duplicate future work.
5. **Cross-app clarity**: If capability ownership moved out of repo, archive with full migration rationale and destination ownership.

## Loop Workflow

1. Set review scope and batch size.
2. Build or refresh RFC inventory/index.
3. Review RFCs one by one in the batch with evidence.
4. Classify each RFC.
5. Standardize RFC document structure/content.
6. Record next actions and priority.
7. Commit loop outputs and prepare next batch.

## Step 1: Set Scope and Batch Size

- Work on one repository at a time.
- Use a batch of `3-7` RFCs per loop.
- Prefer ordering by risk and recency:
  - Runtime-critical RFCs first.
  - Cross-app contract RFCs second.
  - Historical/legacy RFCs last.

## Step 2: Build/Refresh RFC Inventory

- Run:
  - `python <skill-dir>/scripts/rfc_inventory.py --rfc-dir <repo>/docs/RFCs --output <repo>/docs/RFCs/RFC-INDEX.md`
- Use generated index as the source of truth for progress.
- If index already exists, keep existing reviewed rows and only update delta rows.

## Step 3: Review RFCs One by One (Evidence Required)

For each RFC in the current batch:
- Read RFC fully.
- Gather implementation evidence from:
  - `src/`
  - `tests/`
  - OpenAPI/contracts
  - runbooks/operations docs
- Capture concrete evidence links/paths in index.

Do not classify from wording alone without code/test evidence.

Also extract and preserve from the original RFC:
- Original problem statement.
- Original goals/requirements.
- Original acceptance criteria (or equivalent success conditions).

## Step 4: Classify Each RFC

Use these implementation classes:
- `Fully implemented and aligned`
- `Partially implemented (requires enhancement)`
- `Outdated (requires revision)`
- `No longer relevant to this repository`

Use RFC lifecycle statuses:
- `Draft`
- `Approved`
- `Implemented`
- `Partially Implemented`
- `Deprecated`
- `Archived`

## Step 5: Standardize RFC Structure

- Normalize each reviewed RFC using `references/rfc-standard-template.md`.
- Preserve historical context and original requirement intent.
- Do not omit implementation details if they explain architecture, flows, or trade-offs.
- Add explicit:
  - original requested requirements (preserved)
  - requirement-to-implementation traceability table
  - design reasoning and trade-offs
  - deviations/evolution since original RFC
  - current reality
  - gap assessment
  - next actions
  - ownership

## Step 6: Handle Archive Candidates

If RFC scope belongs outside current repository:
- Mark `Archived` in `RFC-INDEX.md`.
- Add destination/owner note in `Next Actions`.
- Keep historical context so the file remains a migration/reference pointer.
- Include why ownership moved and what parts (if any) remain relevant in current repo.

## Step 7: Output of Each Loop

Each loop must leave:
- Updated `docs/RFCs/RFC-INDEX.md`.
- Updated `docs/RFCs/RFC-DELTA-BACKLOG.md` with validated deltas only.
- Standardized RFC docs for the reviewed batch.
- Explicit prioritized action list (P0/P1/P2) tied to RFC IDs.

## Delta Validation Protocol (Required)

For each proposed delta:
1. Verify in `src/`, `tests/`, migrations, contracts, and docs whether it already exists.
2. Record one of:
   - `open` (not implemented, still relevant)
   - `done` (already implemented)
   - `deferred` (implemented alternatives or no longer high-value now)
3. Add evidence paths and concise rationale.
4. Ensure alignment with lotus-platform standards before keeping delta open.

## Resources

- Script: `scripts/rfc_inventory.py`
  - Generates a normalized RFC review index scaffold.
- Reference: `references/rfc-standard-template.md`
  - Canonical section and metadata structure.
