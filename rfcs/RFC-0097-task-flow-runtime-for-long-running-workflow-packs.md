# RFC-0097: Task-Flow Runtime For Long-Running Workflow Packs

- Status: Implemented
- Date: 2026-04-21
- Owners:
  - `lotus-ai` runtime owners
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
  - `lotus-ai` RFC-0031 governed workflow packs
  - `lotus-ai` RFC-0032 workflow-pack registry and activation posture
  - `lotus-ai` RFC-0033 durable AI run ledger and review-state contracts
  - `RFC-0095-heartbeat-driven-monitoring-and-attention-surfacing.md`
  - `RFC-0096-governed-multi-agent-delegation-model.md`

## Summary

Some workflow packs cannot truthfully be modeled as one request followed by one reviewable output.
They need bounded multi-step task flows with checkpoints, revision chains, human handoff, evidence
accumulation, and clear stop, retry, and degraded-state semantics.

This RFC defines a Lotus-native task-flow runtime above the existing workflow-pack registry and
run-ledger capabilities. `lotus-ai` owns AI runtime orchestration and task-flow source truth.
Domain services keep domain workflow authority. `lotus-gateway` exposes only stable task-flow
contracts, and `lotus-workbench` consumes gateway-backed posture only after source contracts and
gateway APIs are proven.

## Problem

Phase-1 workflow-pack work established:

1. governed pack registration and activation,
2. durable run ledger,
3. runtime and review-state separation,
4. caller authorization and rollout posture,
5. downstream UX for bounded first-wave pack families.

The next workflow-pack family is likely to require multiple steps:

1. collect inputs,
2. generate a draft,
3. request missing evidence,
4. revise through a replacement run,
5. route for human review,
6. supersede, reject, or accept,
7. deliver reviewed output or evidence to a domain workflow.

Without a governed task-flow model, every pack will invent its own checkpointing, retry,
replacement-lineage, and handoff rules. That creates inconsistent audit posture and increases the
risk that intermediate AI output is mistaken for authoritative domain truth.

## Current Reality

| Surface | Current state | RFC-0097 implication |
| --- | --- | --- |
| `lotus-ai` workflow-pack registry | RFC-0031/RFC-0032 registry, activation, caller authorization, rollout posture, and runtime readiness have been materially implemented | Task-flow creation must require an active, authorized pack and must not bypass registry posture |
| `lotus-ai` run ledger and review contracts | RFC-0033 run ledger, review state, replacement lineage, supportability, and degraded readiness behavior are materially implemented | Task flows must reference run-ledger records rather than redefining run or review state |
| `lotus-ai` task-flow runtime | First-wave implementation is merged on `main`: task-flow contracts, bounded transitions, memory/SQL stores, readiness, read-only inspection APIs, Phase-1 execution binding, review synchronization, handoff-readiness posture, and runtime-status heartbeat attention | Remaining work is future domain handoff execution, not RFC-0097 first-wave closure |
| `lotus-gateway` | Gateway is the API face for product surfaces, not product or AI source truth. First-wave advisor-brief task-flow posture publication is merged on `main` | Gateway preserves task-flow state, replacement lineage, and handoff posture from `lotus-ai` without becoming source truth |
| `lotus-workbench` | Workbench consumes gateway/BFF contracts and must not read platform or `lotus-ai` files directly. First-wave advisor-brief task-flow rendering and live validation are merged on `main` | UI renders flow, run, review, lineage, and handoff-readiness posture from gateway only |
| RFC-0095 heartbeat | Advisory attention surfacing exists for local artifacts and selected runtime posture | `lotus-ai` runtime status now emits task-flow heartbeat attention for waiting, blocked, stale, and action-required flows |
| RFC-0096 delegation | Bounded delegated engineering work is now governed | Multi-repo implementation can use delegation, but source code still needs main-agent review and PR checks |

## Goals

1. Define task-flow identity and lifecycle above individual pack runs.
2. Model checkpoints and transitions without becoming a generic business process engine.
3. Preserve run-ledger evidence for every AI-generated or reviewed output.
4. Preserve review-state truth and replacement lineage across revisions.
5. Support bounded handoff to domain workflows without moving domain authority into `lotus-ai`.
6. Expose gateway and Workbench contracts only after `lotus-ai` source contracts are stable.
7. Provide meaningful tests for checkpoint, retry, supersession, failure, timeout, cancellation,
   unsupported, and degraded states.
8. Define API certification, OpenAPI, vocabulary, migration, and heartbeat expectations before
   implementation begins.

## Non-Goals

1. Replacing domain workflow engines.
2. Storing all domain workflow state in `lotus-ai`.
3. Building unconstrained arbitrary DAG orchestration.
4. Allowing workflow packs to bypass registry activation, rollout posture, or caller authorization.
5. Hiding intermediate AI outputs from audit.
6. Creating product UI without a gateway-backed contract.
7. Making heartbeat or delegated-agent evidence source truth for task-flow state.

## Design Principles

1. **Source truth stays layered.** Task-flow truth starts in `lotus-ai`; gateway and Workbench
   mirror or render it without reinterpreting it.
2. **Flow state, run state, and review state remain separate.** A flow may wait for review while a
   run is complete and a review state remains pending.
3. **Checkpoint evidence is durable.** Every step boundary records source refs, run refs, review
   refs, actor, timestamp, and decision context when applicable.
4. **Replacement lineage is explicit.** Revisions and supersessions preserve previous run ids and
   replacement run ids rather than rewriting historical summaries.
5. **Bounded transitions only.** The first implementation should use a finite state machine and
   named step definitions, not arbitrary user-defined DAGs.
6. **Domain handoff is explicit.** Domain services receive reviewed evidence or instructions; they
   remain authoritative for business workflow state.
7. **Degraded is not green.** Unmigrated stores, missing ledger readiness, unsupported consumers,
   stale checkpoints, and failed dependencies must surface truthfully.

## Core Concepts

| Concept | Meaning |
| --- | --- |
| Task flow | Bounded multi-step workflow-pack execution envelope |
| Step | Named unit of progress inside the flow |
| Checkpoint | Durable evidence that a step reached a governed boundary |
| Revision chain | Relationship between draft, revised, superseded, rejected, and accepted outputs |
| Handoff | Transfer of reviewed output or evidence to a domain workflow owner |
| Blocking condition | Missing input, failed dependency, degraded store, timeout, or review action required |
| Transition | Governed state change with actor, reason, timestamp, and evidence |

## Required State Model

Task-flow state must stay separate from run and review state.

Flow lifecycle:

1. `created`
2. `running`
3. `waiting_for_input`
4. `waiting_for_review`
5. `blocked`
6. `completed`
7. `failed`
8. `cancelled`
9. `expired`
10. `superseded`

Step lifecycle:

1. `pending`
2. `running`
3. `succeeded`
4. `failed`
5. `skipped`
6. `blocked`

Run lifecycle: existing RFC-0033 runtime state.

Review state: existing RFC-0033 review-state contract.

## Minimum Contract Fields

The first machine-readable task-flow contract should include:

1. `task_flow_id`
2. `workflow_pack_id`
3. `workflow_pack_version`
4. `tenant_id`
5. `caller`
6. `desk_id` or rollout context when applicable
7. `flow_status`
8. `current_step_id`
9. `step_statuses`
10. `checkpoint_refs`
11. `run_refs`
12. `review_refs`
13. `replacement_lineage`
14. `blocking_conditions`
15. `handoff_refs`
16. `supportability_status`
17. `created_at`, `updated_at`, `expires_at`
18. `authorization_evidence_ref`
19. `readiness_evidence_ref`

Checkpoint records should preserve:

1. checkpoint id,
2. step id,
3. actor,
4. timestamp,
5. transition,
6. evidence refs,
7. run id or review id when applicable,
8. domain handoff ref when applicable,
9. reason or decision summary,
10. degraded or unsupported posture when applicable.

## Transition Rules

1. `created` may move to `running`, `cancelled`, or `expired`.
2. `running` may move to `waiting_for_input`, `waiting_for_review`, `blocked`, `completed`,
   `failed`, `cancelled`, `expired`, or `superseded`.
3. `waiting_for_input` may move back to `running`, or to `cancelled`, `expired`, or `blocked`.
4. `waiting_for_review` may move back to `running` through a revision, or to `completed`,
   `rejected` through review-state evidence if represented by existing review contracts, `blocked`,
   `cancelled`, `expired`, or `superseded`.
5. Terminal states must not be advanced except through an explicit supersession or a new task flow.
6. Every transition must carry actor, timestamp, reason, and evidence refs.

Implementation note: if existing RFC-0033 review contracts do not expose `rejected` as a flow
status, rejection should remain review-state truth and the flow should map to `completed`,
`blocked`, or `superseded` only when that mapping is explicit and tested.

## Cross-Repo Boundary Rules

1. `lotus-ai` owns task-flow contracts, state transitions, checkpoints, run-ledger refs, review refs,
   replacement lineage, supportability, and readiness behavior.
2. `lotus-gateway` owns external API shape and downstream composition only after `lotus-ai`
   contracts are stable.
3. `lotus-workbench` consumes gateway/BFF APIs only. It must not read `lotus-ai` or platform
   artifacts directly.
4. `lotus-advise`, `lotus-manage`, and `lotus-report` own domain handoff effects and domain
   workflow state.
5. `lotus-platform` owns RFC governance, shared context, cross-repo validation expectations, and
   optional heartbeat policy patterns.

## API Certification Pattern

Any served task-flow endpoint must follow the Lotus endpoint certification pattern before being
treated as source truth or product truth.

Certification must cover:

1. endpoint behavior for every lifecycle state,
2. returned identifier fidelity for flow id, step id, pack id, run id, review id, replacement run id,
   tenant id, caller, and domain handoff ref,
3. OpenAPI schema and example accuracy,
4. API vocabulary and no-alias rules,
5. unsupported caller and unauthorized caller behavior,
6. degraded readiness and unmigrated-store behavior,
7. pagination or catalog semantics if multiple flows are listed,
8. gateway propagation semantics,
9. Workbench view-model behavior when adopted.

Platform RFC text alone is not API certification evidence.

## Heartbeat And Operational Attention

Heartbeat coverage should be added only after there is durable task-flow source evidence.

First-wave heartbeat attention should surface:

1. stale active flows,
2. flows blocked on missing input,
3. flows waiting for review beyond threshold,
4. failed or degraded checkpoint writes,
5. unsupported downstream consumer attempts,
6. domain handoff failures,
7. replacement-lineage inconsistencies.

Heartbeat must remain advisory unless a later governance change makes task-flow attention
gate-affecting.

## Implementation Plan

### Slice 0: Pre-Implementation Alignment

1. Confirm current `lotus-ai`, `lotus-gateway`, and `lotus-workbench` branches and active PRs.
2. Verify RFC-0031/RFC-0032/RFC-0033 source contracts and downstream adoption reality.
3. Identify the first-wave task-flow candidate and explicitly reject unsuitable candidates.
4. Decide whether platform owns a shared task-flow contract template or whether `lotus-ai` owns the
   first contract entirely.

Review gate:

1. confirm no active branch or merged work already implements the chosen slice,
2. confirm source truth remains in `lotus-ai`,
3. record why the chosen first-wave flow is narrow enough.

### Slice 1: Task-Flow Contract

1. Define flow, step, checkpoint, transition, blocking-condition, revision-lineage, and handoff
   contracts in the owning repository.
2. Add validator and unit tests.
3. Explicitly map every run and review reference to RFC-0033 run-ledger/review truth.
4. Add valid and invalid examples.

Review gate:

1. ensure runtime state and review state are not collapsed,
2. ensure the model is bounded and not a generic DAG engine,
3. ensure identifiers preserve pack, version, run, review, checkpoint, and domain refs,
4. prove unsupported or degraded contract examples are not green.

### Slice 2: Lotus-AI Flow Store And Service Layer

1. Add durable storage for flow headers, step state, checkpoints, transition history, blocking
   conditions, and handoff refs.
2. Add service methods for create, advance, block, retry, cancel, expire, supersede, and complete.
3. Add migration and restart-safe behavior if SQL-backed.
4. Add readiness-aware degradation if the store or run ledger is not ready.

Review gate:

1. inspect transaction boundaries,
2. test restart-safe readback,
3. test invalid transitions,
4. verify terminal states cannot advance silently,
5. verify degraded stores block execution truthfully.

### Slice 3: Runtime Binding For One First-Wave Flow

1. Choose one practical workflow-pack family for first implementation.
2. Bind steps to existing pack-run execution seams.
3. Record evidence refs and revision lineage through the run ledger.
4. Preserve review action requirements for revise and supersede.
5. Block execution when pack activation, authorization, rollout, or run-ledger readiness fails.

Review gate:

1. avoid broad runtime rewrites,
2. verify every generated output has run-ledger evidence,
3. verify degraded readiness blocks execution truthfully,
4. verify replacement lineage is visible in flow detail and run detail,
5. verify summary text is not rewritten by review actions unless the source service returns it.

### Slice 4: Gateway Contract

1. Expose bounded flow posture through gateway only after `lotus-ai` contracts are stable.
2. Preserve source-of-truth language.
3. Add contract and integration tests for create, detail, checkpoint, review, revision, and degraded
   posture.
4. Propagate unsupported, unauthorized, readiness-blocked, and conflicting-lineage errors without
   normalizing them into generic failures.

Review gate:

1. ensure gateway is API face, not source of task-flow truth,
2. ensure degraded and unsupported states propagate truthfully,
3. avoid leaking internal storage details,
4. confirm OpenAPI examples match the real payloads.

### Slice 5: Workbench Or Domain Consumer Adoption

1. Add a first consumer only where product behavior is truly backed by gateway and `lotus-ai`.
2. Render flow, run, and review states distinctly.
3. Add UI/view-model tests for revision, superseded, blocked, unsupported, and degraded states.
4. If no UI adoption is justified, add a domain-service handoff consumer instead and record why.

Review gate:

1. verify no AI output is rendered as authoritative workflow truth,
2. verify superseded outputs cannot appear active-ready,
3. verify unsupported/degraded responses produce truthful user-facing posture,
4. run focused UI or domain-service validation.

### Slice 6: Heartbeat And Operational Attention

1. Add heartbeat attention for stale or blocked task flows only after source evidence exists.
2. Preserve flow id, pack id, run id, review id, step id, tenant/caller, and owner in attention
   items.
3. Keep heartbeat advisory unless a later governance change makes it gate-affecting.
4. Add tests for stale active flows, waiting-for-review threshold, blocked input, failed handoff,
   and degraded source evidence.

Review gate:

1. ensure heartbeat reads source truth without redefining it,
2. ensure terminal completed/cancelled/superseded flows do not alert when closure evidence is
   complete,
3. ensure deduplication keys preserve the exact flow and step identifiers.

### Slice 7: Code Review, API Certification, And Governance Tightening

Second-last mandatory slice.

1. Review service boundaries, contracts, validators, docs, and tests for duplicated transition
   logic.
2. Remove dead code and stale task-flow assumptions encountered in touched paths.
3. Confirm API certification, OpenAPI, vocabulary, no-alias, migration, and security governance.
4. Confirm heartbeat coverage for stale or blocked flows.
5. Confirm downstream consumers cannot bypass gateway or source contracts.
6. Record any out-of-scope follow-up instead of silently expanding the RFC.

Review gate:

1. run focused tests across touched repositories,
2. run API certification checks for served endpoints,
3. prove invalid transitions and degraded stores fail truthfully,
4. verify code review found no unreviewed generated or delegated changes.

### Slice 8: Documentation, Context, Wiki, Skills, And Branch Hygiene

Final mandatory slice.

1. Update RFC status and implementation evidence only after behavior is proven.
2. Update docs, runbooks, OpenAPI docs, and operator guidance where task-flow truth changed.
3. Update central agent context or repo-local context where operating truth changed.
4. Update wiki source if operator-facing behavior changed and publish after merge.
5. Assess whether existing skills or guidance should be updated for task-flow implementation and
   validation.
6. Record an explicit no-change decision for AGENTS, context, wiki, and skills if no updates are
   needed.
7. Run focused and repo-native checks, push PRs, monitor CI, merge only when green, and clean local
   and remote branches.

Required final-slice decisions:

1. `AGENTS.md`: update, no change, or defer with rationale.
2. `context/`: update, no change, or defer with rationale.
3. `wiki/`: update and publish, or record no-wiki-change rationale.
4. skills/guidance: update existing skills, add a new skill, remove stale guidance, or record
   no-change rationale.
5. branch hygiene: record local clean state, remote branch cleanup, generated artifact posture, and
   open follow-ups.

## Test Plan

Minimum implementation proof:

1. contract tests for flow, step, checkpoint, transition, blocking-condition, and handoff shapes,
2. invalid-transition tests for every disallowed lifecycle edge,
3. restart-safe persistence tests for SQL-backed storage,
4. readiness/degraded tests for unmigrated or unavailable stores,
5. run-ledger linkage tests for run refs, review refs, replacement run ids, and superseded history,
6. authorization and rollout tests proving registry posture is enforced,
7. gateway contract and OpenAPI tests when endpoints are introduced,
8. Workbench or domain-consumer tests only after gateway/source contracts exist,
9. heartbeat tests for stale or blocked flows after source evidence exists,
10. cross-repo end-to-end proof for the selected first-wave flow before marking implemented.

## Acceptance Criteria

1. A task-flow contract exists with validator and tests.
2. `lotus-ai` durably stores flow headers, step state, checkpoints, transitions, and handoff refs.
3. One first-wave task flow proves checkpoint, retry, failure, cancellation, expiration,
   supersession, replacement lineage, and review handoff.
4. Gateway and UI or domain adoption exist only where source contracts support them.
5. Heartbeat monitoring can surface stale or blocked flows without redefining source truth.
6. API certification, OpenAPI, vocabulary, no-alias, migration, and security posture are explicit.
7. Final docs/context/wiki/skills/branch hygiene is complete.
8. Implementation evidence proves behavior across the owning repositories before status changes to
   Implemented.

## Implementation Evidence

As of 2026-04-21, RFC-0097 is implemented for the first-wave advisor-brief workflow-pack path across
the merged `main` branches for `lotus-ai`, `lotus-gateway`, `lotus-workbench`, and `lotus-platform`.

1. `lotus-ai`: merged through PR #44 and PR #45
   - task-flow descriptor, checkpoint, blocking-condition, replacement-lineage, handoff, and
     source-evidence contracts,
   - bounded transition validation,
   - memory and SQL-backed task-flow/checkpoint stores with readiness-aware degradation,
   - read-only task-flow catalog, detail, and checkpoint APIs,
   - Phase-1 workflow-pack execution records task-flow/checkpoint state,
   - review actions synchronize task-flow review state and replacement lineage,
   - accepted flows record `READY_FOR_HANDOFF` posture for the workflow authority owner,
   - `/platform/runtime-status` emits bounded heartbeat-style task-flow attention.
2. `lotus-gateway`: merged through PR #143
   - advisor-brief responses preserve gateway-shaped task-flow posture from `lotus-ai`,
   - replacement lineage and handoff refs are forwarded without inferring state locally,
   - tests cover client forwarding, service parsing, router serialization, OpenAPI schema, and typecheck.
3. `lotus-workbench`: merged through PR #104, PR #105, PR #106, and PR #107
   - gateway `workflow_pack_task_flow` payloads are typed,
   - advisor-brief view model renders task-flow supportability, provenance, lineage, and handoff
     posture,
   - fallback previews remain excluded from RFC-0097 proof.

Local and CI proof recorded in repository slice-review files:

1. `lotus-ai`: 106 focused RFC-0097 tests passed after heartbeat and handoff-readiness slices.
2. `lotus-gateway`: 95 focused advisor-brief/gateway contract tests passed after task-flow and
   handoff-posture preservation; `make typecheck` passed.
3. `lotus-workbench`: 44 focused advisor-brief tests passed, `npm run typecheck`, `npm run lint`,
   and `npm run build` passed.

Live proof:

1. `qa-platform-readiness-clean-core-build` passed on 2026-04-21 after rebuilding local service
   images, resetting `lotus-core` state, seeding only the governed canonical front-office portfolio,
   and running deterministic provider-disabled `lotus-ai` posture through `.env.example`.
2. Evidence:
   - `output/task-runs/20260421-192146-qa-platform-readiness-clean-core-build.md`
   - `output/front-office-qa/canonical-front-office-qa-20260421-192148.md`
   - `lotus-workbench/output/playwright/live-canonical/live-validation-summary.json`
3. The proof validated `PB_SG_GLOBAL_BAL_001`, gateway readiness, Workbench canonical panels,
   initial advisor-brief workflow-pack posture, `ACCEPT`, `SUPERSEDE`, and `REVISE` task-flow
   posture through `lotus-ai` -> `lotus-gateway` -> `lotus-workbench`.
4. Repo wikis for `lotus-platform`, `lotus-ai`, `lotus-gateway`, and `lotus-workbench` were
   published after merge.

## Implementation Boundaries

The implementation must not:

1. create a generic DAG or arbitrary workflow engine,
2. move domain workflow authority into `lotus-ai`,
3. expose gateway or Workbench behavior before `lotus-ai` contracts exist,
4. collapse flow, run, and review states into one ambiguous status,
5. treat heartbeat attention as source truth,
6. treat delegated implementation output as review,
7. declare implemented based only on contracts without a proven first-wave flow.

## Open Implementation Decisions

Resolved for first-wave implementation closure:

1. first-wave task-flow candidate,
2. exact repository that owns the first task-flow contract file,
3. whether `lotus-platform` needs a shared task-flow contract template,
4. SQL persistence shape and migration strategy in `lotus-ai`,
5. gateway endpoint shape and pagination semantics,
6. Workbench versus domain-service first consumer,
7. heartbeat stale thresholds,
8. task-flow-specific skill assessment: no new skill is needed yet because the reusable operating
   pattern is captured in the RFC, repo contexts, slice-review docs, wiki pages, and canonical QA
   automation. A dedicated skill should be reconsidered only after a second task-flow family needs
   repeatable implementation guidance beyond advisor brief.

## Pre-Implementation Gold-Standard Review

Reviewed on 2026-04-21 before implementation begins.

Tightening applied:

1. added current-reality mapping to RFC-0031/RFC-0032/RFC-0033, gateway, Workbench, RFC-0095, and
   RFC-0096,
2. clarified source-truth boundaries across `lotus-ai`, gateway, Workbench, domain services, and
   platform,
3. added design principles for state separation, evidence, replacement lineage, bounded
   transitions, domain handoff, and degraded posture,
4. expanded required contract fields and checkpoint fields,
5. added transition rules and terminal-state constraints,
6. added API certification pattern requirements,
7. added heartbeat attention requirements and advisory posture,
8. split implementation into eight slices with explicit review gates,
9. added final-slice decisions for AGENTS, context, wiki, skills, and branch hygiene,
10. expanded test plan, acceptance criteria, boundaries, and open decisions.

Documentation, context, wiki, and skills decision for this pre-implementation pass:

1. RFC document: updated because the previous draft was too implicit for cross-repo implementation.
2. Repo RFC index and wiki index: no status change required; RFC-0097 remains draft and already
   appears as the next implementation item.
3. Central agent context: no behavior change yet, so no context update is required before
   implementation.
4. Skills: no change yet. A task-flow-specific skill should be considered only after implementation
   proves repeatable commands and review patterns.
5. Wiki: no publication required for this pre-implementation tightening because operator-facing
   behavior did not change.

## Initial Priority

Implement next. RFC-0095 heartbeat and RFC-0096 delegation are now implemented, so task-flow runtime
is the next governed workflow-pack runtime capability before RFC-0098 queue and concurrency policy.
