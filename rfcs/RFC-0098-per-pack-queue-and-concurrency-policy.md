# RFC-0098: Per-Pack Queue And Concurrency Policy

- Status: Draft
- Date: 2026-04-21
- Owners:
  - `lotus-ai` runtime owners
  - lotus-platform governance
  - affected gateway/operator-surface owners if posture is published outside `lotus-ai`
- Target repositories:
  - `lotus-ai`
  - `lotus-platform`
  - optionally `lotus-gateway` for operator-facing queue posture
  - optionally `lotus-workbench` only if a supported user-facing posture is required
- Depends on:
  - `lotus-ai` RFC-0031 governed workflow packs
  - `lotus-ai` RFC-0032 workflow-pack registry and activation posture
  - `lotus-ai` RFC-0033 durable AI run ledger and review-state contracts
  - `RFC-0095-heartbeat-driven-monitoring-and-attention-surfacing.md`
  - `RFC-0097-task-flow-runtime-for-long-running-workflow-packs.md`

## Summary

RFC-0097 created the first-wave task-flow runtime for workflow packs. RFC-0098 adds the next
runtime control: explicit per-pack queue, lane, timeout, retry, cancellation, and concurrency policy.

The goal is not to build a generic distributed queue platform. The goal is to prevent expensive or
long-running workflow-pack executions from starving banker-facing paths, silently bypassing
activation or caller policy, or creating operator-opaque delay and retry behavior.

`lotus-ai` remains the source of queue policy and queue-admission truth. `lotus-gateway` may expose a
bounded operator-facing posture after source contracts are implemented. `lotus-workbench` should only
render queue posture when the gateway contract supports a real product need.

## Problem

As workflow packs expand, expensive AI work can starve interactive banker workflows and support
tasks. Without explicit queue policy:

1. one pack can consume all runtime capacity,
2. batch or nightly work can block latency-sensitive advisor flows,
3. retries can amplify upstream failures,
4. timeout and cancellation semantics can drift per pack,
5. review and replacement runs can compete with initial generation work,
6. readiness-degraded stores can create ambiguous queued or partially executed state,
7. operators cannot explain why a pack is queued, delayed, rejected, cancelled, timed out, or
   degraded.

## Current Reality

| Surface | Current state | RFC-0098 implication |
| --- | --- | --- |
| `lotus-ai` workflow-pack registry | RFC-0032 records pack activation, caller posture, rollout, and explicit execution binding | Queue policy must be attached to active executable pack versions without bypassing registry truth |
| `lotus-ai` run ledger | RFC-0033 records run lifecycle, review state, supportability, and lineage | Queue state must not replace run lifecycle; admitted work must still produce durable run evidence where execution begins |
| RFC-0097 task flows | First-wave advisor-brief task-flow posture is implemented and proven | Queue admission must preserve task-flow/run/review separation and must not create task-flow records before admission semantics are truthful |
| RFC-0095 heartbeat | Advisory heartbeat can surface derived attention from source evidence | Queue saturation, stuck lanes, timeout clusters, and degraded queue sources should emit advisory attention after source evidence exists |
| `lotus-gateway` | Gateway is the API face, not runtime source truth | Gateway may publish bounded queue posture only after `lotus-ai` owns it |
| `lotus-workbench` | Workbench consumes gateway/BFF contracts only | UI adoption is optional and must not invent queue state or internal mechanics |

## Goals

1. Define lane types for workflow-pack execution.
2. Define per-pack and per-lane concurrency limits.
3. Define bounded queue capacity, timeout, retry, cancellation, stale-queue, and rejection policy.
4. Preserve registry activation, rollout, caller authorization, run-ledger readiness, and task-flow
   readiness checks before queue admission.
5. Keep queue state separate from run lifecycle, task-flow lifecycle, and review state.
6. Surface queue posture to operators without exposing internal queue implementation details.
7. Ensure heartbeat monitoring can detect stuck, saturated, repeated-timeout, and degraded queue
   states.
8. Provide meaningful tests for capacity, fairness, timeout, cancellation, rejection, retry,
   degraded readiness, and downstream posture.

## Supported Features

No RFC-0098 product features are implemented yet.

The supported-features list must remain explicit throughout implementation. A feature can move from
future work into supported posture only after source code, tests, docs, and proof exist. Initial
candidate supported features are:

1. queue policy descriptors attached to executable workflow-pack versions,
2. finite queue lane vocabulary and validation,
3. queue-admission preflight that runs after registry/caller/readiness checks and before execution,
4. per-pack and per-lane capacity enforcement,
5. explicit queued, rejected, cancelled, timed-out, and degraded posture,
6. bounded operator queue summary in `lotus-ai`,
7. RFC-0095 heartbeat attention for queue saturation and stuck queues,
8. optional gateway publication of source queue posture,
9. optional Workbench rendering of gateway-backed queue posture.

Unsupported unless explicitly implemented by this RFC:

1. a generic arbitrary queueing platform,
2. real-time execution guarantees,
3. queue admission before registry, caller, run-ledger, and task-flow readiness checks,
4. gateway or Workbench source truth for queue state,
5. exposing worker internals, database locks, or raw queue implementation details to bankers,
6. cross-pack global optimization beyond bounded first-wave fairness rules.

## Non-Goals

1. Building a distributed queue platform from scratch if repo-native or standard primitives are
   enough.
2. Guaranteeing real-time execution.
3. Allowing queue admission to bypass pack registry, caller policy, rollout, supportability, run
   store readiness, or task-flow store readiness.
4. Exposing internal queue mechanics directly to Workbench users.
5. Replacing RFC-0033 run lifecycle, RFC-0097 task-flow lifecycle, or review-state contracts.
6. Moving domain workflow authority into `lotus-ai`.

## Design Principles

1. **Admission is a governed boundary.** A workflow-pack request must pass activation, caller,
   rollout, and readiness gates before queue admission can occur.
2. **Queue state is not run state.** Queue posture explains scheduling and capacity. Run records
   explain execution lifecycle. Task flows explain multi-step workflow posture.
3. **No unlimited defaults.** Every executable pack version must have an explicit bounded policy or
   fail safely.
4. **Latency-sensitive work is protected.** Banker-facing interactive work must have a lane and
   capacity posture that cannot be starved by batch or nightly work.
5. **Retries are bounded and explainable.** Retry amplification must be prevented with explicit
   max-attempt, backoff, timeout, and terminal-posture rules.
6. **Degraded is not queued-green.** If registry, run-ledger, task-flow, or queue source truth is not
   ready, the response must be explicit degraded or rejected posture, not a silent queue.
7. **Operator posture is bounded.** Operators should see counts, reasons, lane posture, affected pack
   versions, and evidence refs without raw implementation details.
8. **Heartbeat remains advisory.** Queue attention helps operators, but source queue and runtime
   contracts remain authoritative.

## Queue Lane Model

Initial governed lanes:

| Lane | Purpose | First-wave examples |
| --- | --- | --- |
| `latency_sensitive` | Interactive banker-facing execution where delay harms user workflow | advisor brief generation |
| `review_support` | Review-state supporting work, replacement runs, revision chains, and supersession support | revise/supersede follow-up generation |
| `batch` | Larger asynchronous work with user-visible or operator-visible completion posture | portfolio-level AI inspections |
| `nightly` | Scheduled lower-priority work | scheduled support brief generation |
| `operator` | Supportability, repair, or operator-triggered work | replay, diagnosis, controlled retry |

Lane names are contract vocabulary. New lane names require schema, tests, docs, and heartbeat review.

## Required Policy Fields

Each executable pack version must have explicit queue policy:

1. `policy_id`
2. `workflow_pack_id`
3. `workflow_pack_version`
4. `allowed_lanes`
5. `default_lane`
6. `max_concurrent_runs_per_pack`
7. `max_concurrent_runs_per_lane`
8. `max_queued_runs_per_pack`
9. `max_queued_runs_per_lane`
10. `admission_timeout_seconds`
11. `execution_timeout_seconds`
12. `retry_policy`
    - `max_attempts`
    - `backoff_strategy`
    - `retryable_failure_codes`
    - `non_retryable_failure_codes`
13. `cancellation_policy`
    - who may cancel
    - terminal state emitted
    - evidence required
14. `stale_queue_threshold_seconds`
15. `saturation_attention_threshold`
16. `degraded_readiness_behavior`
17. `operator_visibility`
18. `evidence_requirements`

## Queue State Model

Queue state must be finite and separate from run and task-flow state:

1. `not_admitted`
2. `queued`
3. `admitted`
4. `running`
5. `rejected`
6. `cancelled`
7. `timed_out`
8. `degraded`
9. `completed_handoff`

Rules:

1. `not_admitted` can become `queued`, `rejected`, or `degraded`.
2. `queued` can become `admitted`, `cancelled`, `timed_out`, or `degraded`.
3. `admitted` can become `running`, `cancelled`, `timed_out`, or `degraded`.
4. `running` is execution posture and must be reflected through the run ledger once execution
   starts.
5. terminal queue states must not silently re-enter `queued`; retry must create explicit retry
   evidence.
6. `completed_handoff` only means the queue boundary handed work to execution; it does not mean the
   workflow-pack run or task flow completed.

## Admission Ordering

Queue admission must happen in this order:

1. validate request shape,
2. load workflow-pack registration,
3. verify activation state and version,
4. verify caller authorization and rollout posture,
5. verify registry store readiness,
6. verify run-ledger store readiness,
7. verify task-flow store readiness when the pack is task-flow-backed,
8. load queue policy for the exact pack version,
9. validate requested lane against allowed lanes,
10. evaluate capacity and concurrency,
11. emit queue admission result,
12. create execution/run/task-flow state only after the queue policy allows admission.

This ordering prevents a rejected or degraded queue request from creating misleading run or task-flow
state.

## Operator And API Surface Direction

`lotus-ai` should own the first queue posture surface. Candidate source APIs:

1. `GET /platform/workflow-packs/queue-policies`
2. `GET /platform/workflow-packs/queue-policies/{pack_id}/{version}`
3. `GET /platform/workflow-packs/queue-status`
4. `GET /platform/workflow-packs/queue-status/{queue_item_id}`

Mutating queue APIs should not be added unless the implementation proves they are needed. Initial
mutation should prefer existing workflow-pack execution and review-action seams.

Gateway publication is optional. If added, it must:

1. preserve `lotus-ai` source posture,
2. avoid becoming queue authority,
3. expose only bounded operator/product fields,
4. propagate degraded or unsupported source posture truthfully.

Workbench adoption is optional. If added, it must:

1. consume gateway/BFF contracts only,
2. avoid internal queue mechanics,
3. use user-facing copy for delayed, queued, degraded, rejected, cancelled, and timed-out posture,
4. hide queue details where they are not useful to bankers.

## Heartbeat Direction

RFC-0095 heartbeat should consume queue source truth only after `lotus-ai` queue posture exists.

Attention candidates:

1. lane saturated above threshold,
2. pack queue full,
3. queue item stale beyond threshold,
4. repeated timeouts for one pack version,
5. repeated cancellations by the same actor or lane,
6. degraded queue store or degraded upstream readiness,
7. retry amplification blocked by policy.

Heartbeat output must preserve pack id, version, lane, queue item id, correlation id, tenant/caller
where available, threshold evidence, and source evidence refs.

## Risks And Mitigations

| Risk | Mitigation |
| --- | --- |
| Queue state is confused with run state | Keep queue state in separate contracts and tests; require run-ledger linkage only after execution starts |
| Queue policy becomes a generic scheduler | Keep finite lanes and per-pack policy only; defer global optimization |
| Gateway or Workbench invents queue posture | Add downstream tests only after source contracts exist; fail closed on missing source posture |
| Retry amplification worsens upstream failures | Require bounded retry policy, backoff, and non-retryable failure codes |
| Defaults allow unlimited execution | Require explicit policy and tests for missing-policy rejection |
| Queue store degradation creates ambiguous execution | Preflight readiness before admission and block execution when source truth cannot be written |
| Documentation sprawl duplicates policy | Keep implementation evidence in repo docs and long-lived operator usage in wiki source |

## Implementation Plan

### Slice 0: Pre-Implementation Review And Scope Lock

1. Confirm the first executable pack families in scope.
2. Confirm whether RFC-0098 starts with `advisor_brief.pack` only or all current executable pack
   versions.
3. Confirm whether queue policy belongs directly in registry records or in a separate policy table
   referenced by registry detail.
4. Identify whether any current runtime behavior already implies queue/concurrency limits.
5. Record why any gateway or Workbench adoption is needed or consciously deferred.

Review gate:

1. confirm no existing branch already implements the same queue policy,
2. confirm `lotus-ai` remains queue source truth,
3. confirm the slice is narrow enough for meaningful proof,
4. confirm RFC-0098 remains separate from RFC-0097 and does not reopen task-flow implementation.

### Slice 1: Queue Policy Contract

1. Add queue policy contract types for pack versions.
2. Define finite lane vocabulary, capacity fields, timeout fields, retry policy, cancellation policy,
   stale threshold, degraded behavior, and operator visibility.
3. Add schema examples for latency-sensitive, review-support, batch, degraded, and invalid policy
   posture.
4. Add tests for valid policies, invalid lanes, unlimited defaults, impossible capacities, invalid
   timeout ordering, retry amplification, and missing evidence requirements.

Review gate:

1. confirm the policy is bounded and not a generic scheduler,
2. confirm no unlimited defaults exist,
3. confirm policy naming matches Lotus domain vocabulary,
4. simplify duplicated validation helpers before moving on.

### Slice 2: Registry Integration

1. Attach queue policy to executable workflow-pack registry records.
2. Keep activation, caller policy, rollout, and readiness checks ahead of queue admission.
3. Add registry catalog/detail fields only where implementation-backed.
4. Add tests for missing policy, stale policy, deprecated/retired pack posture, version-specific
   policy selection, and policy change history.

Review gate:

1. verify stale or missing policy fails safely,
2. verify deprecated/retired packs cannot enqueue,
3. verify policy changes are version-aware,
4. avoid duplicating registry-state logic inside queue-policy code.

### Slice 3: Runtime Queue Admission

1. Add queue admission checks in `lotus-ai`.
2. Enforce per-pack and per-lane concurrency and queue-capacity limits.
3. Emit explicit queued, admitted, rejected, cancelled, timed-out, degraded, and handoff posture.
4. Ensure execution/run/task-flow records are created only after admission allows handoff.
5. Add tests for fairness, capacity boundaries, timeout, cancellation, retry posture, degraded
   registry/run-ledger/task-flow readiness, and race-prone admission behavior.

Review gate:

1. inspect transaction and locking boundaries,
2. prove invalid or degraded admission creates no misleading execution state,
3. prove terminal queue states do not silently requeue,
4. reduce duplicated capacity logic before moving on.

### Slice 4: Operator Queue Posture And Source APIs

1. Expose bounded queue policy and queue status posture in `lotus-ai` only after source contracts are
   implemented.
2. Include counts, lane posture, saturation posture, timeout posture, degraded posture, and evidence
   refs.
3. Add OpenAPI and contract tests for catalog/detail/status surfaces.
4. Add operator-profile or runtime-status integration only where it reduces operator ambiguity.

Review gate:

1. ensure operator posture does not expose raw implementation details,
2. ensure OpenAPI examples match real payloads,
3. ensure API certification pattern requirements are documented and tested,
4. ensure missing evidence is not reported as healthy.

### Slice 5: Heartbeat Attention Integration

1. Feed saturation, stuck queue, repeated timeout, repeated cancellation, retry-blocked, and degraded
   source posture into RFC-0095 heartbeat.
2. Preserve identifiers exactly in attention items.
3. Add suppression/deduplication posture where repeated queue issues would otherwise spam operators.
4. Add tests for healthy, warning, action-required, blocking, suppressed, and source-missing queue
   attention.

Review gate:

1. ensure heartbeat reads source queue posture without redefining it,
2. ensure deduplication keys preserve queue item, pack, version, lane, and tenant/caller where
   available,
3. ensure terminal healthy posture clears stale attention truthfully.

### Slice 6: Gateway Or Workbench Adoption If Needed

1. Add gateway surface only if operator or product UX needs it.
2. Add Workbench UI only if there is a supported user-facing flow.
3. Keep internal queue mechanics out of banker-facing UI unless required.
4. Add downstream tests for delayed, rejected, timed-out, cancelled, degraded, and unsupported
   posture only after gateway/source contracts exist.

Review gate:

1. verify gateway is not queue source truth,
2. verify Workbench consumes gateway/BFF APIs only,
3. verify UI copy is truthful and non-technical,
4. avoid speculative UX and document any no-adoption decision.

### Slice 7: Cleanup, Structure, And Documentation Shape

Dedicated cleanup and structure slice.

1. Remove dead code and stale queue/concurrency assumptions found in touched paths.
2. Improve repository structure where queue policy introduces real local complexity.
3. Improve document structure and reduce sprawl by keeping implementation evidence in repo docs and
   long-lived operator guidance in wiki source.
4. Move the right long-lived material to `wiki/`.
5. Avoid duplicate documentation across repo docs and wiki pages.
6. Ensure changed repo wikis are published and usable after merge.
7. Update the supported-features list when features are proven; keep aspirational items out of
   supported posture.

Review gate:

1. compare repo docs and wiki pages for stale duplicated claims,
2. verify no generated evidence artifacts are accidentally committed,
3. verify wiki source and published wiki are synchronized for changed repos,
4. record any deferred cleanup as future work rather than broadening this RFC silently.

### Slice 8: Code Review, API Certification, And Governance Tightening

Second-last mandatory slice.

1. Perform a full implementation review across policy, registry, runtime, operator, heartbeat, and
   downstream surfaces.
2. Tighten loose ends, remove duplication, and simplify capacity/admission logic where possible.
3. Check API certification pattern compliance for every served endpoint.
4. Verify OpenAPI, vocabulary, no-alias, migration, security, CI, wiki, and platform governance
   requirements are met.
5. Confirm tests cover saturation, timeout, cancellation, rejection, retry, degraded readiness,
   missing policy, stale policy, and downstream posture.
6. Record out-of-scope follow-up instead of silently expanding the RFC.

Review gate:

1. run focused tests across touched repositories,
2. run platform repo checks and relevant API certification checks,
3. prove invalid policies and degraded stores fail truthfully,
4. verify code review found no unreviewed generated or delegated changes,
5. confirm supported-features wording matches implementation evidence.

### Slice 9: Documentation, Context, Wiki, Supported Features, Skills, And Branch Hygiene

Final mandatory slice.

1. Update RFC status and implementation evidence only after behavior is proven.
2. Update docs, runbooks, OpenAPI docs, and operator guidance where queue truth changed.
3. Update central agent context or repo-local context where operating truth changed.
4. Update wiki source if operator-facing behavior changed and publish after merge.
5. Update the supported-features list so it reflects implementation-backed product material only.
6. Review skills, guidance, documentation, and context for future agent effectiveness and ramp-up.
7. Add, remove, tighten, or explicitly decline skill/guidance/context changes with rationale.
8. Run focused and repo-native checks, push PRs, monitor CI, merge only when green, and clean local
   and remote branches.

Required final-slice decisions:

1. `AGENTS.md`: update, no change, or defer with rationale.
2. `context/`: update, no change, or defer with rationale.
3. `wiki/`: update and publish, or record no-wiki-change rationale.
4. supported features: update the list or explicitly record why no support posture changed.
5. skills/guidance: update existing skills, add a new skill, remove stale guidance, or record
   no-change rationale.
6. branch hygiene: record local clean state, remote branch cleanup, generated artifact posture, and
   open follow-ups.

## Test Plan

Minimum implementation proof:

1. policy contract tests for lane vocabulary, capacity, timeout, retry, cancellation, degraded
   behavior, and evidence requirements,
2. invalid-policy tests for missing limits, impossible capacities, invalid timeout ordering,
   unsupported lanes, and unbounded retries,
3. registry integration tests proving activation, caller, rollout, and version posture remain ahead
   of queue admission,
4. runtime admission tests for capacity, fairness, stale queue, timeout, cancellation, retry,
   rejection, and degraded readiness,
5. persistence/restart tests if queue state is durable,
6. OpenAPI and endpoint certification tests for any served queue endpoints,
7. heartbeat tests for saturated, stuck, timeout-cluster, cancellation-cluster, retry-blocked, and
   degraded queue posture,
8. gateway/Workbench tests only if downstream adoption is implemented,
9. platform governance tests for RFC structure, supported-features posture, wiki sync, and branch
   hygiene evidence.

## Acceptance Criteria

1. Queue policy is explicit for every executable pack version in scope.
2. Queue admission cannot bypass registry activation, caller policy, rollout, run-ledger readiness,
   or task-flow readiness where applicable.
3. Queue state, run state, task-flow state, and review state remain separate in contracts and tests.
4. Capacity, fairness, timeout, cancellation, retry, rejection, and degraded readiness are tested.
5. Operator posture explains queue delay or rejection truthfully without leaking internal mechanics.
6. Heartbeat detects stuck, saturated, repeated-timeout, repeated-cancellation, retry-blocked, and
   degraded queue posture.
7. API certification, OpenAPI examples, vocabulary, no-alias, migration, security, and CI governance
   are satisfied for every implemented served surface.
8. Supported-features wording is implementation-backed and excludes aspirational features.
9. Cleanup/structure, second-last hardening/review, and final closure slices are completed.
10. Final docs/context/wiki/skills/branch hygiene is complete and repo wikis are published when
    changed.

## Implementation Boundaries

The implementation must not:

1. create a generic distributed queue system unless a future RFC expands scope,
2. create queue state without source evidence,
3. create run or task-flow records for requests rejected before admission,
4. let gateway or Workbench infer queue truth,
5. expose internal worker details in public contracts,
6. hide degraded readiness behind queued posture,
7. declare implemented without live or integration proof for the first executable pack family in
   scope.

## Open Implementation Decisions

Resolve before implementation closure:

1. first executable pack families in scope,
2. whether queue policy is embedded in registry records or stored in a separate policy store,
3. whether queue state is in-memory only for the first slice or migration-backed from the start,
4. exact source API shape for queue policy and queue status,
5. whether gateway publication is needed for first-wave operator posture,
6. whether Workbench needs user-facing queue posture or should defer,
7. saturation and stale thresholds per lane,
8. retryable and non-retryable failure vocabulary,
9. whether a dedicated queue-policy skill is useful after implementation evidence exists.

## Pre-Implementation Gold-Standard Review

Reviewed on 2026-04-21 before implementation begins.

Tightening applied:

1. clarified source-truth boundaries across `lotus-ai`, gateway, Workbench, heartbeat, and task
   flows,
2. added current-reality mapping to RFC-0032, RFC-0033, RFC-0095, and RFC-0097,
3. added explicit supported-features and unsupported-features posture,
4. added queue lane vocabulary, required policy fields, finite queue states, and admission ordering,
5. added operator/API direction and heartbeat attention direction,
6. added risks and mitigations,
7. added mandatory cleanup/structure, second-last hardening/review, and final closure slices,
8. added final-slice decisions for AGENTS, context, wiki, supported features, skills, and branch
   hygiene,
9. expanded test plan, acceptance criteria, implementation boundaries, and open decisions.

Documentation, context, wiki, and skills decision for this pre-implementation pass:

1. RFC document: updated because the prior draft was too small to guide implementation safely.
2. Repo RFC index and wiki index: no status change required; RFC-0098 already appears as the next
   implementation item after RFC-0097 closure.
3. Central agent context: no behavior change yet, so no context update is required before
   implementation.
4. Skills: no change yet. A queue-policy-specific skill should be considered only after
   implementation proves repeatable commands, review patterns, and validation artifacts.
5. Wiki: no publication required for this pre-implementation tightening because operator-facing
   behavior has not changed yet.

## Initial Priority

Implement next. RFC-0097 is implemented, so explicit per-pack queue and concurrency policy is the
next governed workflow-pack runtime control before broader long-running pack families expand.
