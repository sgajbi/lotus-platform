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
6. **Mainline truth only**: RFC closure, tightening, implementation planning, and supported-feature
   promotion must be based on `main`, not on an active side branch or local memory. Durable RFC,
   wiki, context, supported-features, source-map, ledger, and proof-index truth stranded on an
   unmerged branch is not complete.
7. **No stranded RFC truth**: Before starting or closing RFC work, reconcile every unmerged remote
   branch that touches governance artifacts. Unique truth must be merged, cherry-picked, explicitly
   superseded with rationale, or deleted.
8. **Business outcome clarity**: Business application RFCs must explain the business outcome in
   private-banking or platform-operating language, not only technical deliverables.
9. **Domain vocabulary discipline**: Use industry-standard, domain-driven terminology. For banking
   apps, prefer precise language such as mandate, investment policy, strategic asset allocation,
   tactical tilt, house view, risk budget, tracking error, source readiness, proof pack, decision
   timeline, and outcome review over generic software labels.
10. **Enterprise posture must improve**: New features must strengthen API quality, data-mesh posture,
   observability, logging, auditability, supportability, tests, documentation, or operational
   resilience. If a feature adds unavoidable complexity, require compensating controls.
11. **One slice at a time**: RFC implementation should close one meaningful slice on `main` before
   opening the next. Do not spread work across many partial slices unless a shared foundation is
   explicitly required, and even then record which blockers remain uncleared.
12. **Bounded proof semantics**: Proof artifacts clear exact blocker codes only. A proof for source
    product typing, live route reachability, report materialization, data-mesh onboarding, Workbench
    discovery, or AI workflow registration must not be promoted into unsupported readiness claims.
13. **Design modularity before runtime modularity**: RFCs should require clean internal domain,
    application, port, adapter, and proof-module boundaries before proposing additional deployable
    microservices. Runtime splits require independent scaling, deployment, ownership, data, failure,
    or security justification.

## Loop Workflow

1. Set review scope and batch size.
2. Run stranded RFC truth reconciliation.
3. Build or refresh RFC inventory/index.
4. Review RFCs one by one in the batch with evidence.
5. Classify each RFC.
6. Standardize RFC document structure/content.
7. Record next actions and priority.
8. Commit loop outputs and prepare next batch.

## Stranded RFC Truth Reconciliation (Required)

Run this before RFC tightening, RFC implementation start, post-merge audit, final closure, or any
supported-feature promotion:

```powershell
git fetch origin --prune
git branch -r --no-merged origin/main
```

For each unmerged remote branch, classify it in the RFC output or task ledger:

1. `must-merge`: contains unique RFC/docs/wiki/context/contract/proof truth that must reach `main`.
2. `cherry-pick`: contains some useful truth, but the branch as a whole is obsolete.
3. `superseded`: all useful truth is already present on `main`; record the evidence.
4. `delete`: branch is merged, obsolete, or contains no durable truth.
5. `active`: branch is intentionally still in flight; record owner, RFC/slice, and expected closure.

High-risk paths that require inspection when present in an unmerged branch:

1. `docs/rfcs/`
2. `wiki/`
3. `README.md`
4. `REPOSITORY-ENGINEERING-CONTEXT.md`
5. `AGENTS.md`
6. `contracts/`
7. `platform-contracts/`
8. `context/`
9. `docs/standards/`
10. `.github/workflows/`
11. migrations, OpenAPI snapshots, API vocabulary inventories, and supported-features files

Use these commands to identify unique truth:

```powershell
git diff --name-status origin/main..<remote-branch> -- docs/rfcs wiki README.md REPOSITORY-ENGINEERING-CONTEXT.md AGENTS.md contracts platform-contracts context docs/standards .github/workflows
git diff --diff-filter=A --name-status origin/main..<remote-branch> -- docs/rfcs wiki README.md REPOSITORY-ENGINEERING-CONTEXT.md AGENTS.md contracts platform-contracts context docs/standards .github/workflows
git cherry -v origin/main <remote-branch>
```

Do not interpret large `D` rows against an older branch as deleted mainline truth without checking
direction and ancestry. Verify whether the branch predates newer mainline work. A file is lost only
when it is absent from `main` and exists as unique useful truth on an unmerged branch.

Record the reconciliation result in the RFC, source-map, closure slice, or task ledger. If useful
truth is restored, add or update a regression test or index reference so it cannot disappear
silently again.

## Step 1: Set Scope and Batch Size

- Work on one repository at a time.
- Use a batch of `3-7` RFCs per loop.
- Prefer ordering by risk and recency:
  - Runtime-critical RFCs first.
  - Cross-app contract RFCs second.
  - Historical/legacy RFCs last.

## Step 1.5: Confirm Mainline Baseline

- Start from a clean, current `main`.
- If the work continues on a feature branch, verify the branch was created from current `main` or
  explicitly rebased/merged after stranded-truth reconciliation.
- Do not use old side branches as execution guides until their durable truth has been reconciled
  onto `main` or intentionally superseded.

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
- For new or reopened implementation-bearing RFCs, also add explicit:
  - business outcomes
  - domain vocabulary and architecture direction
  - supported-features ledger with implementation-backed promotion rules
  - source-authority and dependency map
  - compatibility posture, including whether strategic redesign can delete stale APIs
  - platform automation/scaffolding improvement slice when applicable
  - cleanup and structure slice
  - implementation proof slice with live evidence expectations
  - second-last hardening and review slice
  - final documentation/context/wiki/supported-features/branch-hygiene closure slice
  - enterprise data-mesh, observability, structured logging, audit, API certification, and CI baseline
  - documentation-as-product expectations for README, wiki, demos, sales, operations, and developers

## Gold-Standard Implementation RFC Authoring

Use this section when the user asks to prepare, tighten, or create an implementation RFC before
coding begins.

### Critical Review Before Implementation

Before writing implementation code:

1. read the current RFC and classify ambiguity in scope, sequencing, APIs, source ownership,
   dependencies, evidence, tests, acceptance criteria, and closure,
2. verify current repo truth from code, tests, contracts, OpenAPI, README, wiki, and repo context,
3. identify duplicated, dead, legacy, or misleading scope,
4. record whether backward compatibility is required; do not preserve old endpoints by default
   without proven downstream dependency,
5. strengthen the RFC until a strong implementer can execute with minimal clarification.

### Required Slices For New/Reopened Implementation RFCs

Every new or reopened implementation-bearing RFC must include these slices explicitly:

1. **Platform automation and scaffolding improvement slice**
   - Identify repeatable gaps that belong in `lotus-platform`, not one app.
   - Cover API certification, Swagger quality, observability, health/readiness, structured logging,
     error handling, test scaffolding, CI defaults, documentation scaffolding, governance hooks,
     data-mesh onboarding, and live-evidence patterns where applicable.
   - If no platform change is needed, record a deliberate no-change decision.
2. **Cleanup and structure slice**
   - Remove dead code, duplicate docs, stale endpoints, old aliases, misleading target-state
     claims, and repo/document sprawl.
   - Improve module boundaries and documentation layering before adding more scope.
   - Harden domain ownership, API naming, error models, and design modularity before adding broad
     feature behavior.
3. **Implementation proof slice**
   - Prove endpoints and workflows end to end with live or canonical evidence.
   - Capture full request/response artifacts under non-git-tracked `output/`.
   - Critically review every returned figure, reason code, lineage ref, readiness state, and
     degraded state.
   - State exact blocker codes cleared, exact blockers preserved, and the non-proof boundary that
     prevents overclaiming.
4. **Second-last hardening and review slice**
   - Perform proper code review and tighten bugs, duplication, tests, error handling, API
     certification, OpenAPI examples, data-mesh posture, logs, metrics, health, readiness, and
     platform governance before closure.
5. **Final closure slice**
   - Update README, wiki source, RFC status, supported-features, agent context, skills/guidance
     decisions, evidence summary, branch hygiene, and PR/CI posture.

### Supported-Features Ledger

Every implementation RFC must include a supported-features ledger:

1. list each feature or endpoint delivered by the RFC,
2. state whether it is proposed, gated, supported, deprecated, or removed,
3. define the exact promotion rule from target-state wording to implementation-backed product
   material,
4. include the evidence required for README/wiki/supported-features updates,
5. separate business-demo claims from unimplemented target-state design.

### Enterprise Baseline

Every implementation RFC must state how it will satisfy:

1. API certification and OpenAPI field-level quality,
2. data-mesh producer/consumer declarations, trust telemetry, SLO/access/evidence posture where
   applicable,
3. structured logs, bounded metrics, trace/correlation propagation, supportability, health,
   liveness, readiness, and safe operator diagnostics,
4. source-authority lineage and degraded-source behavior,
5. test-pyramid coverage with meaningful unit, contract, integration, e2e, and live proof where
   appropriate,
6. GitHub Feature Lane, PR Merge Gate, and fix-forward monitoring expectations.
7. repository merge policy, including the default non-squash linear merge path when merge commits
   are disabled.

### Slice Execution Ledger

For each active RFC slice, maintain a short execution ledger in the RFC, RFC index, source map, or
task ledger:

1. slice name and branch,
2. current mainline baseline,
3. blockers targeted in this slice,
4. blockers intentionally preserved,
5. code, API, contract, documentation, and test evidence paths,
6. local commands and GitHub checks,
7. merge method and branch cleanup status,
8. post-merge validation and wiki publication status,
9. branch/code-loss audit evidence such as PR merge state, `git log origin/main..<branch>`,
   `git diff origin/main..<branch>`, or cherry-pick evidence before branch deletion,
10. next slice chosen from updated `main`.

Use the ledger as the slice closure manifest. It should be compact enough for a PR reviewer to read
but exact enough that a future agent can prove which code, docs, wiki, contracts, and proof truth
landed on `main` and which blockers intentionally remain.

### Documentation-As-Product

For product or business application RFCs:

1. documentation must be useful to business, engineering, sales, marketing, operations, and demo
   preparation,
2. wiki pages should explain current feature behavior, integrations, operational posture, diagrams,
   and target-state roadmap without duplicating deep RFC mechanics,
3. README should remain concise and command-accurate,
4. RFCs should carry architecture, sequencing, acceptance criteria, risks, dependencies, evidence,
   and delivery standards,
5. avoid brittle market-size claims or competitor assertions unless freshly verified; prefer
   durable market patterns and source-backed methodology.

### Research and Vocabulary

When domain expertise matters:

1. use current official sources, industry methodology, and durable textbooks or professional bodies,
2. cite or reference sources where the RFC relies on market or methodology claims,
3. translate research into implementation requirements, not marketing prose,
4. normalize vocabulary before implementation begins,
5. avoid copying vendor wording; write in Lotus domain language.

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
