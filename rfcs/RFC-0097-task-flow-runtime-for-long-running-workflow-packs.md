# RFC-0097: Task-Flow Runtime For Long-Running Workflow Packs

- Status: Draft
- Date: 2026-04-21
- Owners:
  - lotus-ai runtime owners
  - lotus-platform governance
  - affected domain-service owners
- Target repositories:
  - `lotus-ai`
  - `lotus-gateway`
  - `lotus-advise`
  - `lotus-manage`
  - `lotus-report`
  - optionally `lotus-workbench` for product-surface consumption
- Depends on:
  - `lotus-ai` RFC-0031, RFC-0032, RFC-0033 bounded Phase-1 implementation
  - `RFC-0095-heartbeat-driven-monitoring-and-attention-surfacing.md`
  - `RFC-0096-governed-multi-agent-delegation-model.md`

## Summary

Some workflow packs cannot be modeled as one request and one reviewable output. They need bounded,
multi-step task flows with checkpoints, revision chains, human handoff, evidence accumulation, and
clear stop/retry semantics.

This RFC defines a Lotus-native task-flow runtime above existing workflow-pack registry and run-ledger
capabilities. It keeps `lotus-ai` as the bounded AI runtime owner while preserving domain workflow
authority in the appropriate domain services.

## Problem

Phase-1 workflow-pack work established:

1. governed pack registration and activation,
2. durable run ledger,
3. runtime and review-state separation,
4. bounded downstream UX for current pack families.

The next workflow-pack family will likely need multiple steps:

1. collect inputs,
2. generate draft,
3. request missing evidence,
4. revise,
5. route for review,
6. supersede or accept,
7. deliver or hand off to a domain workflow.

Without a task-flow model, every pack will invent its own checkpointing, retry, and handoff rules.

## Goals

1. Define task-flow identity and lifecycle above individual pack runs.
2. Model checkpoints and transitions without becoming a generic business process engine.
3. Preserve run-ledger evidence for every AI-generated or reviewed output.
4. Preserve review-state truth and lineage across revisions.
5. Support bounded handoff to domain workflows.
6. Expose gateway/workbench contracts only after lotus-ai source contracts are stable.
7. Provide meaningful tests for checkpoint, retry, supersession, failure, and degraded states.

## Non-Goals

1. Replacing domain workflow engines.
2. Storing all domain state in `lotus-ai`.
3. Building unconstrained arbitrary DAG orchestration.
4. Allowing workflow packs to bypass registry activation or caller authorization.
5. Hiding intermediate AI outputs from audit.

## Core Concepts

| Concept | Meaning |
| --- | --- |
| Task flow | A bounded multi-step workflow-pack execution envelope |
| Step | A named unit of progress inside the flow |
| Checkpoint | Durable evidence that a step reached a governed boundary |
| Revision chain | Relationship between draft, revised, superseded, and accepted outputs |
| Handoff | Transfer of reviewed output or evidence to a domain workflow owner |
| Blocking condition | A missing input, failed dependency, degraded store, or review action required |

## Required State Model

Task-flow state must stay separate from run and review state.

1. flow lifecycle: `created`, `running`, `waiting_for_input`, `waiting_for_review`, `blocked`,
   `completed`, `failed`, `cancelled`, `expired`, `superseded`
2. step lifecycle: `pending`, `running`, `succeeded`, `failed`, `skipped`, `blocked`
3. run lifecycle: existing RFC-0033 runtime state
4. review state: existing RFC-0033 review-state contract

## Implementation Plan

### Slice 1: Task-Flow Contract

1. Define flow, step, checkpoint, and handoff contracts.
2. Add validator and unit tests.
3. Explicitly map each field to registry and run-ledger truth.

Review gate:

1. ensure runtime state and review state are not collapsed,
2. ensure the model is bounded and not a generic DAG engine,
3. ensure identifiers preserve pack, version, run, checkpoint, and domain refs.

### Slice 2: Lotus-AI Flow Store And Service Layer

1. Add durable storage for flow headers and checkpoints.
2. Add service methods for create, advance, block, retry, cancel, and complete.
3. Add migration and restart-safe behavior if SQL-backed.

Review gate:

1. inspect transaction boundaries,
2. test restart-safe readback,
3. test invalid transitions.

### Slice 3: Runtime Binding For One First-Wave Flow

1. Choose one practical workflow-pack family for first implementation.
2. Bind steps to existing pack-run execution seams.
3. Record evidence refs and revision lineage through the run ledger.

Review gate:

1. avoid broad runtime rewrites,
2. verify every generated output has ledger evidence,
3. verify degraded readiness blocks execution truthfully.

### Slice 4: Gateway Contract

1. Expose bounded flow posture through gateway only after lotus-ai contracts are stable.
2. Preserve source-of-truth language.
3. Add contract and integration tests.

Review gate:

1. ensure gateway is API face, not source of task-flow truth,
2. ensure degraded and unsupported states propagate truthfully,
3. avoid leaking internal storage details.

### Slice 5: Workbench Or Domain Consumer Adoption

1. Add a first consumer only where product behavior is truly backed by gateway/lotus-ai.
2. Render flow, run, and review states distinctly.
3. Add UI/view-model tests for revision and blocked states.

Review gate:

1. verify no AI output is rendered as authoritative workflow truth,
2. verify superseded outputs cannot appear active-ready,
3. run focused UI validation.

### Slice 6: Code Review, API Certification, And Governance Tightening

Second-last mandatory slice.

1. Review service boundaries, contracts, and tests.
2. Remove duplicated transition logic.
3. Confirm API certification, OpenAPI, vocabulary, and migration governance.
4. Confirm heartbeat coverage for stale or blocked flows.

### Slice 7: Documentation, Context, Wiki, Skills, And Branch Hygiene

Final mandatory slice.

1. Update RFC status, docs, runbooks, and onboarding guidance.
2. Update central agent context or repo-local context where operating truth changed.
3. Update wiki source if operator-facing behavior changed.
4. Assess skills/guidance changes.
5. Run focused and repo-native checks, publish wiki after merge if needed, and clean branches.

## Acceptance Criteria

1. A task-flow contract exists with tests.
2. `lotus-ai` durably stores flow and checkpoint posture.
3. One first-wave task flow proves checkpoint, retry, failure, supersession, and review handoff.
4. Gateway and UI adoption exist only where source contracts support them.
5. Heartbeat monitoring can surface stale or blocked flows.
6. Final docs/context/wiki/skills/branch hygiene is complete.

## Initial Priority

Implement third. This should follow heartbeat and delegation because task flows create more
long-running operational state and may benefit from bounded parallel implementation.
