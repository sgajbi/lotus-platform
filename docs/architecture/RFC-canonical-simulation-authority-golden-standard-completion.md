# RFC: Canonical Simulation Authority Gold-Standard Completion

- Status: Proposed
- Date: 2026-04-05
- Owners: lotus-platform architecture
- Requires Approval From: lotus-platform maintainers plus `lotus-core`, `lotus-advise`, and `lotus-risk` maintainers
- Related:
  - [canonical-simulation-authority-and-domain-evaluation-pattern.md](./canonical-simulation-authority-and-domain-evaluation-pattern.md)
  - `lotus-core` RFC 085
  - `lotus-advise` RFC-0014, RFC-0017, RFC-0019

## Summary

The platform has corrected the primary architectural mistake:

1. `lotus-core` is now the declared canonical simulation authority,
2. `lotus-risk` already consumes canonical projected state from `lotus-core`,
3. `lotus-advise` now delegates advisory execution to `lotus-core`.

That is necessary, but not yet sufficient for a gold-standard, banking-grade architecture.

The remaining work is to convert a successful cutover into a hardened platform standard:

1. versioned canonical contracts,
2. structured lineage and replay guarantees,
3. permanent parity governance,
4. strict degraded-mode rules,
5. retirement of duplicate local runtime authority.

This RFC defines that completion program.

## Why This RFC Exists

The existing architecture note defines the right ownership model.

What it does not define is the remaining hardening work required to keep the estate from drifting back into ambiguity.

The main risk is no longer an obvious "two engines, two authorities" situation.

The main risk now is long-term regression:

1. canonical contracts evolving without enough downstream governance,
2. lineage and replay metadata remaining inconsistent across services,
3. parity testing fading after cutover,
4. fallback behavior silently reintroducing local divergence,
5. leftover duplicate local logic remaining in place long enough to become a shadow authority again.

That is the gap this RFC closes.

## Problem Statement

The platform is in an intermediate state:

1. the authority model is now correct,
2. the first runtime cutover is complete,
3. but the architecture is not yet protected by the right long-lived controls.

Without those controls, the estate can still drift on:

1. projected-state semantics,
2. contract interpretation,
3. lineage and replay evidence,
4. degraded-mode behavior,
5. ownership boundaries between canonical execution and domain interpretation.

For a banking-grade platform, that is still incomplete.

## Goals

1. Make `lotus-core` the only production runtime authority for canonical projected portfolio state.
2. Define a governed canonical simulation contract with explicit compatibility rules.
3. Make lineage, replay, and request identity first-class cross-service invariants.
4. Turn parity from migration evidence into an ongoing platform gate.
5. Eliminate silent fallback and latent second-engine behavior in production.
6. Clarify the boundary between domain intent compilation and canonical scenario execution.

## Non-Goals

1. Moving advisory workflow, suitability, or lifecycle ownership into `lotus-core`.
2. Turning `lotus-core` into a generic front-office product API surface.
3. Preserving local domain simulators as long-term production authorities.
4. Expanding domain APIs before the canonical contract is hardened.
5. Introducing compatibility aliases that blur ownership language.

## Current State

### Already achieved

1. `lotus-platform` documents the canonical ownership pattern.
2. `lotus-core` contains advisory-grade canonical execution sufficient for the first `lotus-advise` cutover.
3. `lotus-risk` already follows the intended pattern in simulation mode.
4. `lotus-advise` now delegates simulation execution to `lotus-core`.
5. Parity and coverage work exists for the first cutover.

### Still incomplete

1. The canonical simulation contract is not yet governed as a long-lived platform compatibility surface.
2. Lineage and replay semantics are still not standardized tightly enough across services.
3. Fallback and degraded-mode behavior are not yet governed as a strict platform policy.
4. Duplicate local execution logic still exists in `lotus-advise`.
5. Cross-service parity remains a migration-era control rather than a permanent one.
6. Future consumers still rely too much on convention and too little on explicit contract guarantees.

## Decision

The platform will complete the canonical simulation authority transition with a platform hardening program.

That program establishes these rules:

1. `lotus-core` is the only production runtime authority for canonical projected state.
2. Downstream services must consume a versioned canonical simulation contract.
3. Cross-service lineage and replay evidence must be structured and propagated end to end.
4. Parity verification is a permanent release control, not a one-time migration artifact.
5. Any surviving local reference engine must be explicitly non-authoritative and excluded from normal production execution.

## Architectural Invariants

The platform must preserve these invariants:

1. For equivalent canonical simulation inputs, only `lotus-core` may determine projected-state truth.
2. Domain services may add domain interpretation, but they may not silently alter canonical projected-state semantics.
3. Simulation-driven outputs in `lotus-risk`, `lotus-advise`, and future services must remain attributable to one canonical lineage identity.
4. Degraded mode must be explicit, reviewable, and operationally visible.
5. Contract changes affecting canonical simulation semantics must be reviewed as platform changes, not app-local refactors.
6. Duplicate local logic must never remain an ungoverned production fallback path.

## Required Work

### 1. Canonical Contract Governance

The canonical advisory execution endpoint in `lotus-core` is the right first step, but it is still too implementation-shaped.

The platform needs one governed contract with:

1. semantic versioning,
2. explicit input and output stability guarantees,
3. deterministic default and optional-field semantics,
4. documented error taxonomy,
5. explicit downstream compatibility policy.

This contract must define:

1. canonical simulation request shape,
2. canonical projected-state result shape,
3. canonical lineage metadata,
4. canonical failure semantics,
5. contract evolution rules.

### 2. Lineage and Replay Standard

The platform needs one structured lineage standard across `lotus-core`, `lotus-risk`, and `lotus-advise`.

That standard must require:

1. stable simulation run identifiers,
2. stable request hashes,
3. snapshot lineage identities,
4. simulation contract version evidence,
5. replay metadata sufficient for audit and rerun.

This must not remain a mix of app-specific evidence blobs and narrative fields.

### 3. Permanent Parity Governance

Cutover parity tests were necessary. They are not sufficient.

The platform needs a permanent parity-governance layer that:

1. compares domain-facing advisory results against canonical `lotus-core` execution semantics,
2. verifies that `lotus-risk` simulation mode still consumes compatible canonical state,
3. blocks releases when canonical behavior drifts without explicit approval.

This should include:

1. governed golden inputs,
2. cross-repo parity fixtures,
3. canonical expected-result lineage,
4. CI or release-gate enforcement.

### 4. Runtime Resilience and Degraded-Mode Policy

The architecture now depends more heavily on cross-service runtime authority. That is correct, but it must be explicit.

The platform needs a strict policy for:

1. what happens when `lotus-core` is unavailable,
2. whether any fallback is permitted in production,
3. how degraded mode appears in APIs, readiness, and capabilities,
4. how operators detect and respond to simulation-authority failure.

The gold-standard default is:

1. no silent local fallback in production,
2. explicit failure when canonical authority is unavailable,
3. environment-scoped exceptions only for controlled development or test workflows,
4. observability and capability surfaces that report degraded authority truthfully.

### 5. Duplicate Local Engine Retirement

`lotus-advise` still contains local simulation code.

Some of it was correctly reused into `lotus-core`. The remaining work is to finish the ownership split:

1. logic defining canonical projected-state semantics belongs in `lotus-core`,
2. logic defining advisory-only interpretation belongs in `lotus-advise`,
3. leftover duplicated local execution logic should be:
   - moved,
   - reduced to thin adapters,
   - or retained only as quarantined reference-test code.

The platform should not tolerate a permanent "just in case" second engine.

### 6. Intent Compilation Boundary Hardening

The most important design seam now is the boundary between:

1. domain intent compilation, and
2. canonical scenario execution.

`lotus-advise` should own:

1. advisory proposal vocabulary,
2. orchestration,
3. domain policy interpretation,
4. workflow posture.

`lotus-core` should own:

1. execution of canonical scenario deltas,
2. state projection,
3. valuation and reconciliation semantics,
4. canonical projected-state lineage.

The translation between those layers needs an explicit contract and tests.

### 7. Vocabulary and Documentation Convergence

Across repos, the same architecture must use the same language for:

1. simulation authority,
2. projected state,
3. lineage and replay,
4. degraded mode,
5. contract version,
6. canonical versus domain interpretation.

This is governance work, but it is also correctness work. A banking-grade platform cannot rely on near-synonyms across repos.

## Delivery Slices

### Slice 1: Canonical Contract and Error Model Hardening

Outcome:

1. versioned canonical simulation contract defined,
2. explicit error taxonomy defined,
3. compatibility policy documented,
4. downstream consumers aligned to the governed contract.

Acceptance gate:

1. contract docs and OpenAPI are explicit,
2. no ambiguous or backend-leaking names remain,
3. contract version is surfaced in lineage or metadata,
4. downstream services consume the same canonical terms.

### Slice 2: Lineage and Replay Convergence

Outcome:

1. `lotus-core`, `lotus-advise`, and `lotus-risk` share one structured lineage standard,
2. simulation-driven workflows preserve canonical replay evidence,
3. audit and rerun semantics are no longer app-specific.

Acceptance gate:

1. replay metadata is structured and persisted,
2. request hashes and simulation run ids propagate end to end,
3. docs and support APIs expose the same evidence vocabulary.

### Slice 3: Parity Governance Program

Outcome:

1. cross-service parity fixtures and golden scenarios exist,
2. parity checks are part of CI or governed release gates,
3. semantic drift is caught before merge or release.

Acceptance gate:

1. parity coverage exists for advisory and risk consumer paths,
2. failures are explainable and actionable,
3. parity is not a one-off script or temporary spreadsheet exercise.

### Slice 4: Degraded-Mode and Runtime-Authority Hardening

Outcome:

1. fallback posture is platform-governed,
2. production behavior is explicit and conservative,
3. readiness and capabilities expose authority truthfully.

Acceptance gate:

1. silent local fallback is disallowed in production,
2. degraded mode is visible through APIs and observability,
3. runbooks define operator response clearly.

### Slice 5: Duplicate Engine Retirement and Boundary Simplification

Outcome:

1. duplicated projected-state logic is removed or quarantined,
2. advisory-only interpretation remains in `lotus-advise`,
3. canonical execution semantics remain in `lotus-core`.

Acceptance gate:

1. no latent second runtime authority remains,
2. code ownership is materially clearer,
3. maintenance burden and drift risk are reduced.

### Slice 6: Estate-Wide Documentation and Governance Completion

Outcome:

1. relevant RFCs and architecture docs reflect the same ownership model,
2. service capability surfaces and runbooks use consistent language,
3. support and operational teams can reason about the design without repo-by-repo interpretation.

Acceptance gate:

1. no cross-repo documentation contradiction remains on simulation authority,
2. public and internal docs match runtime behavior,
3. the architecture is reviewable as one platform design.

## Data and Operational Requirements

1. Canonical simulation runs must be reproducible from persisted lineage.
2. Cross-service identifiers must be sufficient for audit review.
3. Error semantics must distinguish:
   - invalid request,
   - unsupported domain transform,
   - upstream dependency failure,
   - canonical simulation failure,
   - degraded-mode prohibition.
4. Observability must reveal when domain services are blocked on canonical authority availability.
5. No service may claim authoritative simulation success if `lotus-core` execution failed.
6. Migration and cutover steps must be reversible only through explicit operator action, not hidden fallback logic.

## Risks

1. Leaving duplicate local execution logic in place too long will recreate architectural ambiguity.
2. Weak contract versioning will turn future `lotus-core` changes into downstream breakage.
3. Loose fallback rules will preserve convenience at the cost of correctness.
4. Shallow parity governance will create false confidence.
5. Over-centralizing domain behavior into `lotus-core` would create a different design failure and weaken domain boundaries.

## Alternatives Considered

### Alternative 1: Stop after the current cutover

Rejected.

Reason:

1. the direction is now correct,
2. but the architecture is still under-governed for long-term banking-grade operation.

### Alternative 2: Keep local advisory execution as a long-term fallback authority

Rejected.

Reason:

1. that preserves the exact drift risk the cutover was meant to remove,
2. local fallback may remain useful only as controlled development or test tooling, not as normal production authority.

### Alternative 3: Move all advisory logic into `lotus-core`

Rejected.

Reason:

1. canonical state projection and domain interpretation are different responsibilities,
2. `lotus-core` should not own advisory workflow, suitability policy, or proposal lifecycle.

## Acceptance Criteria

This RFC is complete when:

1. `lotus-core` is the only production runtime authority for canonical projected state,
2. the canonical simulation contract is versioned and governed,
3. lineage and replay semantics are structured and propagated end to end,
4. parity governance is institutionalized across affected services,
5. production fallback posture is explicit and conservative,
6. duplicate local projected-state authority has been retired or quarantined,
7. cross-repo docs and vocabulary are aligned,
8. the architecture is resilient against future simulation drift.

## Approval Requested

Approve this RFC if the team agrees that:

1. the current cutover is necessary but not sufficient for the final architecture,
2. the remaining work should be governed as a platform program rather than left to repo-local drift,
3. `lotus-core` must now be hardened as a long-lived canonical simulation contract, not merely a successful migration destination,
4. parity, lineage, and degraded-mode policy must become permanent platform controls.
