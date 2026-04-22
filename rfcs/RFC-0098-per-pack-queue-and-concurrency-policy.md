# RFC-0098: Per-Pack Queue And Concurrency Policy

- Status: Implemented
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

The supported-features list is implementation-backed and must not include aspirational posture.

Implemented in the first `lotus-ai` source-truth wave merged through
`sgajbi/lotus-ai#46`:

1. finite queue lane vocabulary and validation,
2. queue policy descriptors for all current executable Phase-1 workflow-pack versions:
   `advisor_brief.pack@v1`, `workspace_rationale.pack@v1`, and
   `twr_inspection_support_brief.pack@v1`,
3. registry catalog/detail queue-policy publication for executable pack versions, while
   discovery-only versions remain without executable queue posture,
4. queue-admission preflight after registry/caller/readiness checks and before audit, run-ledger,
   and task-flow side effects,
5. per-pack and per-lane active-admission capacity enforcement for explicit
   `/platform/workflow-packs/execute` and implicit pack-backed `/ai/tasks/execute`,
6. explicit `queue_lane` selection for `/platform/workflow-packs/execute`, with unsupported lanes
   rejected before side effects,
7. bounded `lotus-ai` queue policy and queue status source APIs:
   `/platform/workflow-packs/queue-policies`,
   `/platform/workflow-packs/queue-policies/{pack_id}/{version}`,
   `/platform/workflow-packs/queue-status`, and
   `/platform/workflow-packs/queue-status/{queue_item_id}`,
8. queue status payloads that expose active-admission posture, per-lane saturation posture, and
   queue admission timestamps without raw worker or lock internals,
9. runtime-status `queue_attention` for source-backed lane saturation and stale active admissions,
10. degraded readiness behavior for queue policy/status routes when the registry source store is
    not ready.

Implemented in the durable queue-event source-truth wave merged through
`sgajbi/lotus-ai#47`:

1. durable admission-event history for queue admission requested, granted, rejected, and released
   posture,
2. memory and SQLAlchemy queue-event stores, with migration
   `0032_add_workflow_pack_queue_event_tables`,
3. readiness-aware metadata, runtime-status, startup-policy, and degraded-source behavior for the
   configured queue-event store,
4. bounded source APIs under `/platform/workflow-packs/queue-events` and
   `/platform/workflow-packs/queue-events/{queue_item_id}`,
5. execution and task-execution lineage preservation for caller app, correlation id, tenant id, and
   workflow surface in queue events,
6. repo-local docs, wiki source, and context updates, with `lotus-ai` wiki publication completed at
   wiki commit `dc37eee`.

Implemented in the terminal queue-event posture wave merged through
`sgajbi/lotus-ai#48`:

1. durable timeout and cancellation queue-event vocabulary,
2. timeout posture recorded when an active queue admission is released after its policy execution
   timeout,
3. bounded internal queue-admission cancellation that requires actor, reason, and evidence before
   it records cancellation posture and releases capacity,
4. runtime-status queue attention for durable timeout and cancellation queue events,
5. docs, wiki source, and repo-local context updates, with `lotus-ai` wiki publication completed at
   wiki commit `3e6378a`.

Implemented in the retry/replay recovery-decision posture wave merged through
`sgajbi/lotus-ai#49`:

1. durable retry and replay queue-event vocabulary:
   `RETRY_RECORDED`, `RETRY_BLOCKED`, `REPLAY_RECORDED`, and `REPLAY_BLOCKED`,
2. bounded retry and replay decision APIs under
   `/platform/workflow-packs/queue-events/{queue_item_id}/retry-decisions` and
   `/platform/workflow-packs/queue-events/{queue_item_id}/replay-decisions`,
3. recovery decision evidence fields on queue-event descriptors:
   `source_queue_item_id`, `recovery_action_type`, `recovery_attempt_number`, `requested_by`, and
   `evidence_ref`,
4. retry amplification blocking when failure codes are non-retryable, max-attempt policy would be
   exceeded, or completed handoff posture is incorrectly retried,
5. replay amplification blocking after one governed replay decision exists for the queue item,
6. runtime-status `queue_attention` for blocked retry and blocked replay posture,
7. API contract, OpenAPI, unit, and integration tests proving recovery metadata is preserved and
   that decision responses do not claim workflow re-execution,
8. repo-local docs, wiki source, and context updates describing recovery decisions as evidence
   posture rather than execution posture, with `lotus-ai` wiki publication completed at wiki commit
   `d2feff3`.

Implemented in the repeated queue-failure cluster attention wave merged through
`sgajbi/lotus-ai#50`:

1. cluster attention types for repeated timeout, repeated cancellation, and repeated blocked
   recovery posture,
2. explicit `event_count` on queue attention items so event-derived cluster counts do not overload
   active-admission counts,
3. runtime-status `queue_attention` clusters derived from durable queue events while preserving
   queue source truth in the event catalog/detail surfaces,
4. unit and OpenAPI tests proving repeated failure clusters are reported as bounded derived
   attention,
5. repo-local docs, wiki source, and context updates describing cluster attention as operator
   posture, with `lotus-ai` wiki publication completed at wiki commit `582fc97`.

Implemented in the degraded queue-source attention wave through `sgajbi/lotus-ai#51`:

1. explicit `degraded_source_count` on workflow-pack queue attention summaries,
2. runtime-status `queue_attention` posture for configured queue source dependencies that prevent
   queue attention computation,
3. OpenAPI and runtime-status tests proving degraded queue-source posture is part of the public
   contract rather than only free-text status,
4. repo-local docs, wiki source, and context updates describing degraded source posture as operator
   triage evidence, with `lotus-ai` wiki publication completed at wiki commit `647dc06`.

Implemented in the persisted admission-lifecycle wave through `sgajbi/lotus-ai#52`:

1. durable `ADMISSION_QUEUED` and `ADMISSION_ADMITTED` queue-event vocabulary,
2. queue-event history that records admission request, queued posture, admitted posture, running
   handoff, and terminal release or timeout posture,
3. OpenAPI, unit, and integration tests proving the lifecycle vocabulary and queue-event detail
   order are part of the served contract,
4. repo-local docs, wiki source, and context updates describing persisted admission lifecycle
   evidence without claiming distributed queued execution, with `lotus-ai` wiki publication
   completed at wiki commit `7db54f9`.

Implemented in the queue request-snapshot artifact wave through `sgajbi/lotus-ai#53`:

1. governed `artifact_refs` on workflow-pack queue-event descriptors,
2. retained `queue_request_snapshot` artifacts for explicit `/platform/workflow-packs/execute` and
   implicit pack-backed `/ai/tasks/execute` admissions,
3. request-snapshot artifact refs propagated across admission lifecycle, terminal release or
   timeout posture, and bounded retry/replay decision evidence,
4. API, OpenAPI, and integration tests proving queue events do not embed raw task payloads while
   the referenced artifact contains the bounded recovery input snapshot,
5. repo-local docs, wiki source, and context updates describing request snapshots as recovery
   evidence for future retry/replay execution without claiming that retry/replay execution exists.

Implemented in the bounded queue recovery execution wave through `sgajbi/lotus-ai#54`:

1. explicit retry and replay execution routes:
   `/platform/workflow-packs/queue-events/{queue_item_id}/retry-executions` and
   `/platform/workflow-packs/queue-events/{queue_item_id}/replay-executions`,
2. retained request snapshots now preserve explicit workflow-pack `environment` and
   `caller_identity_class` so recovery execution can reconstruct the governed execution request,
3. retry/replay execution preflights the retained request snapshot before recording an execution
   decision, so queue items without executable snapshots fail truthfully without creating a
   misleading recovery event,
4. recovery execution reuses the normal workflow-pack execution seam, including eligibility,
   queue admission, run ledger, and task-flow recording,
5. API, OpenAPI, and integration tests proving retry and replay execution produce new
   workflow-pack runs from retained request snapshots while decision-only routes remain evidence
   posture.

Implemented in the persisted queued-worker execution wave through `sgajbi/lotus-ai#55`:

1. explicit durable async execution submission route:
   `/platform/workflow-packs/execute-async`,
2. workflow-pack async jobs persisted through the existing async runtime job, attempt, lease, and
   delivery-queue contracts with job type `workflow_pack_execution`,
3. retained `queue_request_snapshot` artifacts used as the executable worker input instead of
   embedding raw task payloads in queue events or generic async job payloads,
4. generic `/platform/async/jobs/submit` submissions rejected for `workflow_pack_execution` so
   callers cannot bypass workflow-pack eligibility, queue policy, readiness, and snapshot evidence,
5. active duplicate submission blocking by caller app, correlation id, pack id, and version,
6. queued capacity enforcement for persisted workflow-pack async jobs using retained snapshot
   metadata for pack and lane identity,
7. dedicated worker dispatch that records `ADMISSION_ADMITTED`, `ADMISSION_GRANTED`, and
   `ADMISSION_RELEASED` queue events, then reuses the normal workflow-pack execution seam so
   run-ledger and task-flow state remain separate source-truth records,
8. terminal `ADMISSION_DEGRADED` queue-event posture and runtime-status queue attention when a
   persisted worker execution fails before completed handoff, including corrupt or missing snapshot
   evidence,
9. memory and SQL-backed async runtime proof that a queued workflow-pack execution can survive
   async runtime store restart and still complete through the dedicated worker path,
10. API, OpenAPI, runtime-status, worker-dispatch, and integration tests proving the submission,
    worker, restart, duplicate, generic-bypass rejection, and degraded-snapshot paths.

Explicitly deferred because no supported downstream product or operator contract needs it yet:

1. gateway publication of queue posture,
2. Workbench rendering of queue posture.

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
5. `GET /platform/workflow-packs/queue-events`
6. `GET /platform/workflow-packs/queue-events/{queue_item_id}`
7. `POST /platform/workflow-packs/queue-events/{queue_item_id}/retry-decisions`
8. `POST /platform/workflow-packs/queue-events/{queue_item_id}/replay-decisions`

Mutating queue APIs should not be added unless the implementation proves they are needed. The
current bounded retry/replay decision APIs record recovery evidence only and must not be treated as
replacement workflow execution.

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

For the first `lotus-ai` source-truth wave:

1. Queue policy is explicit for every executable pack version in scope.
2. Queue admission cannot bypass registry activation, caller policy, rollout, run-ledger readiness,
   or task-flow readiness where applicable.
3. Queue state, run state, task-flow state, and review state remain separate in contracts and tests.
4. Capacity, explicit lane selection, rejection, stale active admission, saturation, missing policy,
   unsupported lane, and degraded readiness are tested.
5. Operator posture explains queue delay or rejection truthfully without leaking internal mechanics.
6. Heartbeat detects source-backed saturated, stale active-admission, timeout, cancellation, blocked
   retry, blocked replay, repeated failure cluster, and degraded queue-source posture.
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

Resolved for the first `lotus-ai` source-truth wave:

1. first executable pack families in scope are the three current Phase-1 executable versions:
   `advisor_brief.pack@v1`, `workspace_rationale.pack@v1`, and
   `twr_inspection_support_brief.pack@v1`,
2. queue policy is a separate declared policy catalog attached to registry catalog/detail posture,
   not a separate SQL table in this wave,
3. queue state is current in-process active-admission posture plus durable queue-event history for
   admission request, queued posture, admitted posture, running handoff, release, timeout,
   cancellation, retained request-snapshot artifact refs, recovery-decision evidence, bounded
   snapshot-backed retry/replay execution, degraded source posture, and persisted queued-worker
   execution through the existing async runtime,
4. source API shape now includes read-only policy/status/event routes plus bounded retry/replay
   decision routes under `/platform/workflow-packs/queue-events/{queue_item_id}`,
5. gateway publication is deferred until an operator or product surface has a concrete supported
   need,
6. Workbench rendering is deferred because no banker-facing queue posture is supported yet,
7. saturation and stale thresholds are policy fields per executable pack version,
8. retryable and non-retryable failure vocabulary is declared in policy descriptors, bounded
   recovery-decision evidence is recordable, and snapshot-backed retry/replay execution is
   implemented,
9. a dedicated queue-policy skill is not needed yet; the implementation is still narrow enough to
   be governed by backend delivery, API certification, pre-merge, and RFC review skills.

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

## Post-Merge Implementation Review

Reviewed again on 2026-04-21 after the first `lotus-ai` source-truth wave was merged and published.

Implementation evidence:

1. `sgajbi/lotus-ai#46` merged the first-wave source contracts, policy catalog, registry posture,
   queue-admission checks, read-only source APIs, runtime-status queue attention, docs, wiki source,
   and repo-local context updates.
2. `sgajbi/lotus-platform#179` merged the RFC and index posture update for this first wave.
3. `lotus-ai` GitHub CI passed Feature Lane lint/typecheck/unit, PR Merge Gate lint/typecheck,
   unit, integration, e2e, runtime-mode smoke, combined coverage, and Docker build validation.
4. `lotus-platform` GitHub CI passed Cross-App Vocabulary Gate, Feature Lane workflow/contracts, and
   PR Merge Gate workflow/contracts.
5. Repo-authored wiki source was published after merge for `lotus-ai` and `lotus-platform`, and
   `Sync-RepoWikis.ps1 -CheckOnly` reported no publication drift for those changed repos.

Review findings:

1. The first `lotus-ai` source-truth wave satisfies the first-wave acceptance criteria: executable
   Phase-1 pack versions have explicit bounded queue policies; queue admission happens after
   registry/caller/readiness checks and before audit, run-ledger, or task-flow side effects; queue
   posture remains separate from run, review, and task-flow state; and source APIs expose bounded
   operator posture without worker internals.
2. No additional `lotus-ai` hotfix slice is required before closing this first wave.
3. At this review point, the full RFC remained incomplete because persisted queued-worker
   execution lifecycle had not yet been implemented and any downstream gateway or Workbench queue
   posture was intentionally deferred.

Additional slices needed for full RFC completion:

1. optional `lotus-gateway` publication only when an operator or product contract needs bounded
   queue posture,
2. optional `lotus-workbench` rendering only after gateway has a supported queue-posture contract,
3. a final full-RFC closure slice after the durable queue wave and any required downstream adoption
   are proven.

Skills, guidance, documentation, and context decision:

1. Existing backend delivery, API certification, pre-merge, RFC review, async-task, and platform
   automation guidance is sufficient for the first wave.
2. A dedicated queue-policy skill is still not justified; create one only after durable queue-event
   history introduces repeatable operational commands, investigation patterns, and validation
   artifacts that are broader than ordinary backend delivery governance.
3. No `AGENTS.md` change is needed for this review because the operating model did not change.

## Persisted Queued-Worker Execution Review

Reviewed on 2026-04-22 after the `lotus-ai` persisted queued-worker execution slice was implemented
and locally proven.

Implementation evidence:

1. `sgajbi/lotus-ai#55` implements durable workflow-pack async execution submission and dedicated
   worker dispatch using the existing async runtime rather than introducing a second scheduler.
2. The public source route is `/platform/workflow-packs/execute-async`; generic
   `/platform/async/jobs/submit` is deliberately blocked for `workflow_pack_execution` so callers
   cannot bypass queue policy, workflow-pack eligibility, readiness, and request-snapshot evidence.
3. Worker execution records queue events on the original queue item and reuses the normal
   workflow-pack execution seam for run ledger and task-flow state, preserving source-truth
   separation.
4. Missing or corrupt retained request snapshots fail terminally with async-job failure evidence and
   `ADMISSION_DEGRADED` queue posture instead of leaving a claimed worker item stranded.
5. Local proof included focused API/worker integration tests, OpenAPI contract tests, runtime-status
   attention tests, async catalog/readiness tests, async worker dispatch tests, async submission
   tests, queue-policy API tests, targeted mypy, ruff, and `git diff --check`.

Review findings:

1. The slice materially closes the prior persisted queued-worker execution gap in `lotus-ai`.
2. The implementation intentionally uses the existing async runtime job, attempt, lease, and
   delivery-queue model. That is simpler and safer than creating a workflow-pack-specific worker
   platform.
3. Gateway and Workbench queue-posture adoption remains deferred. No supported operator or banker
   product flow currently requires exposing queue posture outside `lotus-ai`, and downstream UI must
   not invent it.
4. The next slice should be the mandatory full implementation review, API certification, and
   platform governance tightening pass before final RFC closure.

## Final Hardening And Governance Review

Reviewed on 2026-04-22 after `sgajbi/lotus-ai#55` and `sgajbi/lotus-platform#189` merged.

Review scope:

1. `lotus-ai` source APIs and contracts:
   `/platform/workflow-packs/queue-policies`,
   `/platform/workflow-packs/queue-status`,
   `/platform/workflow-packs/queue-events`,
   `/platform/workflow-packs/queue-events/{queue_item_id}/retry-decisions`,
   `/platform/workflow-packs/queue-events/{queue_item_id}/replay-decisions`,
   `/platform/workflow-packs/queue-events/{queue_item_id}/retry-executions`,
   `/platform/workflow-packs/queue-events/{queue_item_id}/replay-executions`,
   `/platform/workflow-packs/execute`, and `/platform/workflow-packs/execute-async`,
2. queue state, run state, task-flow state, review state, async runtime state, and retained
   request-snapshot artifact boundaries,
3. OpenAPI operation ids, response schemas, error behavior, and runtime-status queue attention,
4. wiki, runbook, repo-local context, platform RFC index, and central context reference posture,
5. downstream gateway and Workbench adoption posture.

Hardening result:

1. A direct endpoint-certification pass found one meaningful gap: persisted async queue-capacity
   enforcement existed but was not directly proven at the endpoint. `sgajbi/lotus-ai#55` was
   tightened before merge with a capacity-saturation test that proves the second queued execution
   fails with HTTP 429 before admission.
2. The same review tightened failure coverage for missing queue events, corrupt or missing
   snapshots, missing policy after claim, unsupported claimed jobs, execution conflicts,
   unexpected worker errors, non-snapshot artifacts, invalid internal transitions, and missing
   queue-event identity.
3. Combined GitHub coverage, lint/typecheck/security, unit, integration, e2e, runtime-mode smoke,
   and Docker build gates passed on `sgajbi/lotus-ai#55`.
4. Platform RFC/index/context governance checks passed on `sgajbi/lotus-platform#189`.
5. No extra gateway or Workbench slice is required for RFC-0098 closure because source queue
   posture is inspectable in `lotus-ai`, no supported downstream contract currently consumes it,
   and adding UI or gateway posture without a real product/operator need would create speculative
   surface area.

API certification posture:

1. Implemented queue endpoints use explicit operation ids and response models, and the OpenAPI
   quality gate passed.
2. Queue source endpoints expose bounded source-truth posture and do not expose worker internals,
   locks, raw queue implementation details, or raw task payloads.
3. The async execution endpoint explicitly rejects generic async submission bypass, validates
   workflow-pack eligibility and binding, checks run-ledger and task-flow readiness, preserves
   request-snapshot evidence, enforces active duplicate/capacity posture, and returns degraded or
   failed posture truthfully.

Platform governance posture:

1. Source behavior, supported features, RFC status, repo-local docs, authored wiki source, and
   central context references are aligned.
2. `lotus-ai` wiki was published after `sgajbi/lotus-ai#55` at wiki commit `57ea635`.
3. `lotus-platform` wiki was published after `sgajbi/lotus-platform#189` at wiki commit `61ff089`.
4. `Sync-RepoWikis.ps1 -CheckOnly -Repository lotus-ai` and
   `Sync-RepoWikis.ps1 -CheckOnly -Repository lotus-platform` reported no drift after publication.
5. Feature branches for the merged work were cleaned locally and remotely where applicable.

## Final Closure Decisions

RFC-0098 is implemented for its supported scope: source-truth per-pack queue policy, queue
admission, durable queue-event history, terminal timeout/cancellation/degraded posture,
retry/replay decisions, snapshot-backed retry/replay execution, queue attention, and persisted
queued-worker execution through the existing async runtime.

Conscious closure decisions:

1. Gateway publication: no implementation in this RFC. Deferred until a concrete operator or product
   contract needs bounded queue posture outside `lotus-ai`.
2. Workbench rendering: no implementation in this RFC. Deferred until gateway exposes a supported
   queue-posture contract and a banker-facing workflow needs it.
3. `AGENTS.md`: no change. Existing operating contract already covers wiki publication,
   async execution, multi-agent discipline, and final-slice governance.
4. Central context: updated through `CONTEXT-REFERENCE-MAP.md`; no broader architecture-context
   rewrite is needed because repository ownership and platform operating rules did not change.
5. Repo-local context: updated in `lotus-ai` because its supported workflow-pack runtime posture
   changed.
6. Wiki: updated and published for `lotus-ai` and `lotus-platform`.
7. Supported features: updated in this RFC and in the RFC index. Unsupported downstream surfaces
   remain excluded from supported posture.
8. Skills and guidance: no new queue-specific skill is needed. The repeatable path remains covered
   by backend delivery governance, endpoint certification, PR pre-merge governance, async
   automation, and RFC review guidance.
9. Branch hygiene: merged PR branches were cleaned; local working trees were returned to `main`.

## Current Priority

No active RFC-0098 implementation slice remains. Future gateway or Workbench queue-posture work
should be opened only when a concrete supported operator or product need appears, and should cite
this RFC as source-truth context rather than reopening the completed `lotus-ai` source scope.
