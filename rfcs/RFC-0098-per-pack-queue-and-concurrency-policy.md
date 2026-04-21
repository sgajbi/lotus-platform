# RFC-0098: Per-Pack Queue And Concurrency Policy

- Status: Partially Implemented
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

Explicitly deferred because source behavior does not yet exist:

1. persisted queued-item lifecycle beyond active in-process admission and durable admission-event
   history,
2. timeout, cancellation, retry-cluster, replay, and repeated-cancellation heartbeat attention,
3. gateway publication of queue posture,
4. Workbench rendering of queue posture.

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

For the first `lotus-ai` source-truth wave:

1. Queue policy is explicit for every executable pack version in scope.
2. Queue admission cannot bypass registry activation, caller policy, rollout, run-ledger readiness,
   or task-flow readiness where applicable.
3. Queue state, run state, task-flow state, and review state remain separate in contracts and tests.
4. Capacity, explicit lane selection, rejection, stale active admission, saturation, missing policy,
   unsupported lane, and degraded readiness are tested.
5. Operator posture explains queue delay or rejection truthfully without leaking internal mechanics.
6. Heartbeat detects source-backed saturated and stale active-admission posture; repeated-timeout,
   repeated-cancellation, retry-blocked, and durable degraded queue-source attention remain deferred
   until queue-event history exists.
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
3. queue state is current in-process active-admission posture; durable queue-event history is
   deferred,
4. source API shape is the four read-only `lotus-ai` routes under
   `/platform/workflow-packs/queue-policies` and `/platform/workflow-packs/queue-status`,
5. gateway publication is deferred until an operator or product surface has a concrete supported
   need,
6. Workbench rendering is deferred because no banker-facing queue posture is supported yet,
7. saturation and stale thresholds are policy fields per executable pack version,
8. retryable and non-retryable failure vocabulary is declared in policy descriptors, but runtime
   retry execution and retry-cluster attention require durable queue-event history,
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
3. The full RFC remains partially implemented, not complete, because durable queue-event history,
   persisted queued-item lifecycle, runtime timeout/cancellation/retry execution, repeated
   timeout/cancellation/retry-cluster heartbeat attention, and any downstream gateway or Workbench
   queue posture are intentionally deferred.

Additional slices needed for full RFC completion:

1. persisted queued-item lifecycle beyond active admission in `lotus-ai`,
2. timeout, cancellation, retry, replay, and terminal queue-state execution semantics backed by
   durable evidence,
3. RFC-0095 heartbeat expansion for repeated timeout, cancellation, retry-blocked, and durable
   degraded queue-source attention,
4. optional `lotus-gateway` publication only when an operator or product contract needs bounded
   queue posture,
5. optional `lotus-workbench` rendering only after gateway has a supported queue-posture contract,
6. a final full-RFC closure slice after the durable queue wave and any required downstream adoption
   are proven.

Skills, guidance, documentation, and context decision:

1. Existing backend delivery, API certification, pre-merge, RFC review, async-task, and platform
   automation guidance is sufficient for the first wave.
2. A dedicated queue-policy skill is still not justified; create one only after durable queue-event
   history introduces repeatable operational commands, investigation patterns, and validation
   artifacts that are broader than ordinary backend delivery governance.
3. No `AGENTS.md` change is needed for this review because the operating model did not change.

## Current Priority

Keep RFC-0098 open as partially implemented. Durable queue-event history is now merged and the
`lotus-ai` wiki source has been published. The next high-value implementation slice is terminal
timeout, cancellation, retry, replay, and retry-cluster attention semantics backed by durable queue
evidence. Gateway or Workbench adoption should remain deferred until a supported operator or product
surface needs it.
