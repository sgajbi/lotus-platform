# RFC-0098: Per-Pack Queue And Concurrency Policy

- Status: Draft
- Date: 2026-04-21
- Owners:
  - lotus-ai runtime owners
  - lotus-platform governance
- Target repositories:
  - `lotus-ai`
  - optionally `lotus-gateway` for operator-facing queue posture
- Depends on:
  - `lotus-ai` RFC-0031, RFC-0032, RFC-0033 bounded Phase-1 implementation
  - `RFC-0095-heartbeat-driven-monitoring-and-attention-surfacing.md`
  - `RFC-0097-task-flow-runtime-for-long-running-workflow-packs.md`

## Summary

AI workflow-pack execution needs explicit queue and concurrency policy before expensive or long-running
packs expand beyond the current bounded Phase-1 flows. This RFC defines per-pack and per-lane
concurrency, timeout, fairness, and degradation policy.

This RFC may be implemented as part of RFC-0097 if the first task-flow runtime slice remains small.
It should split into standalone implementation only when queue policy proves large enough to require
separate contracts, tests, and operator surfaces.

## Problem

As workflow packs expand, expensive AI work can starve banker-facing experiences or operational
support tasks. Without explicit queue policy:

1. one pack can consume all runtime capacity,
2. batch work can block latency-sensitive review paths,
3. retries can amplify failures,
4. timeout semantics can drift per pack,
5. operators cannot explain why a pack is delayed or rejected.

## Goals

1. Define lane types for workflow-pack execution.
2. Define per-pack concurrency limits.
3. Define timeout, retry, and cancellation policy.
4. Preserve caller authorization and activation checks before queue admission.
5. Surface queue posture to operators without exposing internal implementation detail.
6. Ensure heartbeat monitoring can detect stuck or saturated queues.

## Non-Goals

1. Building a distributed queue platform from scratch if repo-native or standard primitives are enough.
2. Guaranteeing real-time execution.
3. Allowing queue admission to bypass pack registry, caller policy, or supportability readiness.
4. Exposing internal queue mechanics directly to Workbench users.

## Lane Model

Initial lanes:

1. `latency_sensitive` for banker-facing interactive work,
2. `review_support` for review-state transitions and revision requests,
3. `batch` for larger asynchronous runs,
4. `nightly` for scheduled lower-priority work,
5. `operator` for supportability and repair tasks.

## Required Policy Fields

Each pack version should have explicit policy:

1. allowed lanes,
2. default lane,
3. max concurrent runs,
4. max queued runs,
5. timeout,
6. retry policy,
7. cancellation policy,
8. stale-run handling,
9. degradation behavior when ledger or registry store is not ready.

## Implementation Plan

### Slice 1: Queue Policy Contract

1. Add queue policy schema for pack versions.
2. Validate lane names, limits, timeouts, and retry posture.
3. Add tests for invalid and valid policies.

Review gate:

1. confirm the policy is small enough to remain standalone,
2. confirm registry and runtime responsibilities are separated,
3. confirm no unlimited defaults exist.

### Slice 2: Registry Integration

1. Attach queue policy to workflow-pack registry records.
2. Keep activation and caller policy ahead of queue admission.
3. Add registry contract tests.

Review gate:

1. verify stale or missing policy fails safely,
2. verify deprecated/retired packs cannot enqueue,
3. verify policy changes are version-aware.

### Slice 3: Runtime Queue Admission

1. Add queue admission checks in `lotus-ai`.
2. Enforce per-pack concurrency and lane limits.
3. Emit truthful queued, rejected, timeout, and cancelled posture.

Review gate:

1. test fairness and capacity boundaries,
2. test timeout and cancellation,
3. test readiness-degraded stores block or degrade truthfully.

### Slice 4: Operator Posture And Heartbeat

1. Expose bounded queue posture to operators.
2. Feed saturation, stuck queue, and repeated timeout conditions into RFC-0095 heartbeat.
3. Add supportability docs.

Review gate:

1. ensure operator posture does not expose internal queue implementation details,
2. ensure heartbeat deduplicates repeated queue warnings,
3. ensure missing evidence is not treated as healthy.

### Slice 5: Gateway Or Workbench Adoption If Needed

1. Add gateway surface only if operator or product UX needs it.
2. Add Workbench UI only if there is a supported user-facing flow.
3. Keep internal queue mechanics out of banker-facing UI unless required.

Review gate:

1. verify gateway is not source of queue truth,
2. verify UI copy is truthful and non-technical,
3. avoid speculative UX.

### Slice 6: Code Review, API Certification, And Governance Tightening

Second-last mandatory slice.

1. Review policy, runtime, and operator code for duplicated capacity logic.
2. Confirm contract/API certification posture.
3. Confirm tests cover saturation, timeout, cancellation, rejection, and degraded readiness.

### Slice 7: Documentation, Context, Wiki, Skills, And Branch Hygiene

Final mandatory slice.

1. Update docs and runbooks.
2. Update agent context if queue posture becomes a platform-wide operating rule.
3. Update wiki source if operator-facing behavior changed.
4. Assess skills/guidance changes.
5. Run wiki checks, publish after merge if needed, and clean branches.

## Acceptance Criteria

1. Queue policy is explicit for each executable pack version.
2. Runtime queue admission cannot bypass registry activation or caller policy.
3. Capacity, timeout, cancellation, and degraded readiness are tested.
4. Operator posture explains queue delay or rejection truthfully.
5. Heartbeat detects stuck or saturated queues.
6. Final docs/context/wiki/skills/branch hygiene is complete.

## Initial Priority

Implement fourth, and initially treat it as a companion to RFC-0097. Split into a dedicated
implementation track only if the first task-flow runtime proves queue policy is large enough to
justify independent delivery.
