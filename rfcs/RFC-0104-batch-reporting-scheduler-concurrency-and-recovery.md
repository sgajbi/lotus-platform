# RFC-0104: Batch Reporting Scheduler, Concurrency, And Recovery

- Status: In Progress
- Date: 2026-04-23
- Gold-pass hardened: 2026-04-26
- Implementation started: 2026-04-26
- Owners:
  - `lotus-report` owners
  - `lotus-platform` operations
  - upstream domain service owners
- Target repositories:
  - `lotus-report`
  - `lotus-platform`
  - optionally `lotus-gateway` for operator-facing status if a supported product/API need is
    approved
  - optionally `lotus-workbench` only after a gateway-backed supported operator or product surface
    is approved
- Depends on:
  - `RFC-0099-enterprise-reporting-and-document-archive-target-architecture.md`
  - `RFC-0100-reporting-gateway-invocation-and-job-ledger-foundation.md`
  - `RFC-0101-report-data-snapshot-and-lineage-contracts.md`
  - `RFC-0102-render-package-template-registry-and-render-service.md`
  - `RFC-0103-document-archive-retrieval-retention-and-legal-hold.md`
- Follow-on RFC boundaries:
  - `RFC-0105-reporting-observability-operations-and-replay-tooling.md` owns broad replay,
    rerender, regenerate, dashboards, stuck-job operations, and SLA monitoring.
  - `RFC-0106-reporting-security-entitlements-and-region-tenant-segregation.md` owns the final
    entitlement model, region/tenant segregation certification, and download authorization hardening.
  - `RFC-0107-enterprise-reporting-production-certification.md` owns final end-to-end production
    certification after RFC-0104 through RFC-0106 are implemented.

## Summary

This RFC defines durable batch reporting for active portfolios, selected subsets, explicit portfolio
lists, and scheduled monthly, quarterly, semi-annual, and yearly report production cycles.

The implementation must make batch reporting a governed product capability, not a script, cron-only
loop, or in-memory worker. It must support durable orchestration, item-level job creation, bounded
concurrency, retry, pause, cancel, recovery, progress inspection, audit evidence, and clean
handoff into the existing reporting, rendering, and archive services.

## Critical Review Outcome

The original RFC had the right broad topic but was not strong enough to guide implementation. The
main gaps were:

1. no platform automation and scaffolding improvement slice,
2. no explicit implementation proof slice,
3. no clear supported-features governance,
4. insufficient API certification and Swagger quality requirements,
5. insufficient source-of-truth decisions for scheduler ownership and recovery behavior,
6. insufficient separation between this RFC and RFC-0105 replay/operations scope,
7. insufficient closure guidance for docs, wiki, context, skills, and branch hygiene,
8. insufficient evidence standards for concurrency, idempotency, and recovery.

This gold pass tightened the RFC into an implementation guide. Implementation started on
2026-04-26 with the platform scaffolding slice only. Batch runtime behavior remains unimplemented
until later slices explicitly add and prove it.

## Problem

Enterprise reporting needs to produce report packages for many portfolios on controlled cycles.
A production batch may span many report jobs and may run longer than a request/response lifecycle.
Without durable batch control, the platform risks:

1. duplicate report generation,
2. unbounded load on `lotus-core`, `lotus-performance`, `lotus-risk`, `lotus-advise`,
   `lotus-render`, and `lotus-archive`,
3. partial batches with no trustworthy resume path,
4. operator uncertainty about progress, failures, retries, and completion,
5. unsupported manual reruns that bypass audit and idempotency,
6. documentation or supported-features claims that exceed implementation proof.

## Business Outcome

After implementation, operations should be able to start or schedule a governed reporting batch,
understand exactly which portfolios and report packages are in scope, watch progress, recover
from transient failures, and prove which reports were rendered and archived.

The client-facing product outcome is reliable periodic reporting at scale. The engineering outcome
is a reusable long-running batch pattern that improves future Lotus application scaffolding and
governance.

## Target Scope

In scope:

1. `report_batch` and `report_batch_item` durable model,
2. batch creation from explicit portfolio lists, selected subsets, and governed batch manifests,
3. scheduled monthly, quarterly, semi-annual, yearly, and explicit production cycles,
4. idempotent batch creation and item materialization,
5. one durable `report_job` per batch item using the RFC-0100 job ledger,
6. concurrency limits for batch, worker, upstream data collection, render, and archive handoff,
7. lease/heartbeat semantics for in-flight batch items,
8. bounded retry with reasoned failure categories,
9. pause, cancel, resume, and retry-failed-only behavior,
10. recovery scanning for abandoned, expired, or stuck item leases,
11. progress and failure APIs for supported operator use,
12. OpenAPI/Swagger quality and API certification for all new APIs,
13. observability floor required to operate the batch capability safely,
14. supported-features updates only after implementation-backed proof exists,
15. platform scaffolding and automation improvements discovered while implementing the slice.

Out of scope:

1. new client report templates,
2. document retention policy changes,
3. broad replay, rerender, regenerate, and stuck-job command center tooling owned by RFC-0105,
4. final reporting entitlement and region/tenant segregation certification owned by RFC-0106,
5. final end-to-end production certification owned by RFC-0107,
6. Workbench UI unless a supported gateway-backed operator/product surface is explicitly approved,
7. changing upstream domain data ownership,
8. replacing RFC-0100 report job semantics,
9. replacing RFC-0103 archive metadata, object storage, retention, purge, or legal-hold semantics.

## Locked First-Wave Decisions

These decisions are fixed for the RFC-0104 implementation unless a later committed RFC amendment
changes them:

1. `lotus-report` owns the batch control plane.
2. Batch execution creates or references one durable `report_job` per batch item through the
   RFC-0100 job ledger.
3. `lotus-report` remains the report-data assembly and report-job state owner.
4. `lotus-render` remains the deterministic render owner.
5. `lotus-archive` remains the generated-document archive owner.
6. Object storage is not exposed directly through batch APIs.
7. Gateway exposure is optional and must be justified by a supported operator/product need.
8. Workbench exposure is optional and must consume gateway/BFF APIs only.
9. Retry and recovery must be item-level, not whole-batch blind reruns.
10. Batch status is derived from durable item and job state, not volatile worker memory.
11. Unsupported sections must remain absent from supported-features documentation until proven.

## Conditional Decisions

These must be resolved during implementation and recorded in the RFC before closure:

1. whether the first implementation uses the existing `lotus-report` async runtime only or adds a
   phase-one scheduler adapter that can later be replaced by a managed scheduler,
2. whether schedule materialization is synchronous on operator request or handled by a periodic
   scheduler loop,
3. the exact per-upstream concurrency defaults for core, performance, risk, advise, render, and
   archive calls,
4. the first-wave batch-manifest format and whether it is operator-authored or generated from
   portfolio selectors,
5. whether gateway exposes batch status in RFC-0104 or defers all operator visibility to
   `lotus-report`,
6. whether batch evidence should update any RFC-0084/RFC-0091 domain-data-product declaration in
   this RFC or remain local until RFC-0107 production certification.

## Pre-Implementation Execution Decisions

Before implementation begins, the first slice owner must make these decisions explicit in the first
implementation PR description and then preserve them in the RFC before closure:

1. the first-wave scheduler mechanism,
2. the first-wave worker execution model,
3. the first-wave portfolio selector source for each supported selector,
4. the first-wave database tables, indexes, and uniqueness constraints,
5. the first-wave retry limits and retryable failure taxonomy,
6. the first-wave batch size and concurrency defaults,
7. the first-wave operator API surface,
8. whether any platform scaffolding change is implemented or consciously not needed.

If any answer is not known at implementation start, the implementer must keep that behavior out of
supported scope until the decision is made, implemented, tested, and documented.

## Architecture Direction

`lotus-report` owns batch control. A batch materializes item records. Each item creates or references
one report job. Report jobs collect data snapshots, render packages, and archive successful
documents through the existing RFC-0100 through RFC-0103 contracts.

```mermaid
flowchart LR
    TRIGGER[Schedule or operator trigger] --> BATCH[report_batch]
    BATCH --> ITEMS[report_batch_item]
    ITEMS --> JOBS[report_job per portfolio/report]
    JOBS --> DATA[report data snapshot and lineage]
    JOBS --> RENDER[lotus-render]
    JOBS --> ARCHIVE[lotus-archive]
    ITEMS --> RECOVERY[lease heartbeat and recovery scanner]
    BATCH --> PROGRESS[progress and failure summary]
```

### Batch Selectors

Supported selector families:

1. `explicit_portfolio_list`
   The request names the portfolios. The implementation must validate duplicates, unknown
   portfolios, inactive portfolios, tenant/region scope, and maximum batch size.
2. `selected_subset`
   The request names a governed subset definition. The implementation must resolve the subset into
   deterministic item membership before execution.
3. `all_active_portfolios`
   The request targets all eligible active portfolios. This is high-risk and may be implemented only
   after explicit-list and subset behavior is proven.
4. `batch_manifest`
   The request references a manifest with explicit portfolio/report entries and source metadata.
   Manifest validation must happen before any report job is created.

### Selector Source Mapping

Every selector must be backed by a real Lotus source. No selector may be implemented from ad hoc
fixtures or local-only assumptions.

| Selector | Source owner | Source contract requirement | First-wave posture |
| --- | --- | --- | --- |
| `explicit_portfolio_list` | `lotus-report` request payload plus portfolio eligibility source from owning domain service | Request must carry portfolio identifiers, report package, period, as-of date, tenant, and region; eligibility must be checked before item materialization | Required first-wave selector |
| `selected_subset` | Owning portfolio/relationship management source, expected through `lotus-manage` or an approved report-side selector registry | Subset identity must resolve to deterministic portfolio membership with source timestamp and source reference | Required only after source contract is confirmed |
| `all_active_portfolios` | Owning portfolio system of record, expected through `lotus-core` or an approved gateway/service facade | Must return active eligible portfolios with tenant, region, and entitlement-filterable scope | Deferred until explicit-list and subset paths are proven |
| `batch_manifest` | Operator-authored or generated manifest stored with content hash and source metadata | Manifest schema must include portfolio/report entries, period, as-of date, report package, requester, and provenance | Optional first-wave if it reduces operational risk |

If a source contract is missing, the RFC implementation must record a source gap instead of
inventing selector behavior locally.

### Frequencies

Supported frequency vocabulary:

1. `monthly`,
2. `quarterly`,
3. `semi_annual`,
4. `yearly`,
5. `explicit`.

Each frequency must define:

1. reporting period start and end,
2. as-of date selection,
3. report package/template selection,
4. schedule identity and idempotency key,
5. allowed rerun/retry behavior.

### State Model

The implementation must keep batch state, item state, and report job state distinct.

Batch states:

1. `created`,
2. `planned`,
3. `running`,
4. `paused`,
5. `completed`,
6. `completed_with_failures`,
7. `cancelled`,
8. `failed`.

Item states:

1. `pending`,
2. `queued`,
3. `running`,
4. `waiting_on_report_job`,
5. `succeeded`,
6. `failed_retryable`,
7. `failed_terminal`,
8. `cancelled`,
9. `recovery_pending`.

State transitions must be bounded and tested. No implementation may update batch aggregate state
without reconciling item and job state.

### Data Contract Floor

`report_batch` must include at least:

1. stable `batch_id`,
2. tenant and region scope,
3. selector type and selector source reference,
4. reporting period start and end,
5. as-of date,
6. report package or template version,
7. idempotency key and request hash,
8. requester/operator identity,
9. state,
10. aggregate counts by item state,
11. concurrency policy snapshot,
12. created, updated, started, completed, cancelled, and failed timestamps where applicable,
13. correlation id,
14. implementation version or migration/source marker.

`report_batch_item` must include at least:

1. stable `batch_item_id`,
2. parent `batch_id`,
3. portfolio identifier,
4. report job identifier when created,
5. archive document identifier when successfully archived,
6. item state,
7. attempt count,
8. retry eligibility and next retry timestamp,
9. lease owner, lease token, lease acquired timestamp, and lease expiry timestamp,
10. last error category and safe error summary,
11. source lineage references for selector membership,
12. created, updated, started, completed, cancelled, and failed timestamps where applicable.

Any implementation that cannot populate one of these fields must document whether the field is
deferred, derived, or unavailable from upstream.

### Idempotency And Duplicate Prevention

Batch creation must use a deterministic idempotency key derived from:

1. selector type and selector identity,
2. report package or template version,
3. reporting period,
4. as-of date,
5. tenant and region scope,
6. requester/operator identity where relevant.

Item-level idempotency must prevent duplicate report jobs for the same batch item. Archive handoff
must not create duplicate active archived documents for the same successful report output unless
explicit replacement lineage permits it.

### Concurrency, Back-Pressure, And Leases

Concurrency must be enforced at multiple layers:

1. maximum active batches,
2. maximum active items per batch,
3. maximum active report jobs created by batch execution,
4. per-upstream data-collection limits,
5. render concurrency limits,
6. archive handoff concurrency limits.

In-flight items must carry a lease or heartbeat. A recovery scanner must detect expired leases and
move recoverable items to `recovery_pending` or a retryable failure state. Recovery must be
deterministic and must not create duplicate report jobs or archive records.

### Non-Negotiable Invariants

Implementation and tests must preserve these invariants:

1. one batch item represents one portfolio/report package/reporting period/as-of-date tuple,
2. one batch item may create at most one active report job for a given attempt,
3. a terminal successful item must reference either a completed report job or documented completion
   evidence,
4. an archived successful item must reference the archive document id returned by `lotus-archive`,
5. a cancelled item must not dispatch after cancellation is acknowledged,
6. retry-failed-only must not retry terminal or cancelled failures,
7. pause must prevent new dispatch while allowing already-running work to reach a documented
   boundary,
8. recovery must be safe to run more than once,
9. aggregate batch counts must reconcile exactly with item states,
10. supported-features text must never claim selector, schedule, API, or recovery behavior that has
    not passed implementation proof.

### Storage And Migration Direction

Batch state must be persisted in the primary `lotus-report` database using migrations reviewed in
the same slice that introduces the data model. The implementation must define:

1. uniqueness constraints for batch idempotency and item idempotency,
2. indexes needed for status lookup, dispatch scanning, retry scanning, and recovery scanning,
3. retention posture for batch ledgers and operator evidence,
4. migration rollback or forward-only posture,
5. handling for legacy report jobs that predate batch support,
6. test fixtures that represent realistic batch sizes without hiding performance risks.

No implementation may depend on in-memory state for correctness.

## API Direction

New APIs should be added only where they become supported behavior. Candidate first-wave
`lotus-report` APIs:

1. `POST /api/v1/report-batches`
   Create or idempotently return a batch.
2. `GET /api/v1/report-batches/{batch_id}`
   Return batch metadata, aggregate progress, and current state.
3. `GET /api/v1/report-batches/{batch_id}/items`
   Return item status with pagination and filters.
4. `POST /api/v1/report-batches/{batch_id}:pause`
   Pause dispatch of pending items without interrupting already running report jobs unless
   implementation explicitly supports cooperative cancellation.
5. `POST /api/v1/report-batches/{batch_id}:resume`
   Resume pending/recoverable items.
6. `POST /api/v1/report-batches/{batch_id}:cancel`
   Cancel pending and queued items and mark the batch cancellation boundary clearly.
7. `POST /api/v1/report-batches/{batch_id}:retry-failed`
   Retry only retryable failed items after validating retry limits and idempotency.

API names may be adjusted to match repository conventions, but the behavior must remain certified.

## Swagger And API Certification Requirements

Every new or changed API must complete the Lotus API certification pattern before the feature can be
listed as supported.

OpenAPI/Swagger must include:

1. grouped tags for batch reporting,
2. clear what/when/how guidance for each endpoint,
3. request examples for explicit list, subset, and schedule-backed batch creation where supported,
4. response examples for created, running, completed, completed-with-failures, paused, cancelled,
   and validation-failure states where supported,
5. full error examples for invalid selector, duplicate item, unsupported frequency, maximum batch
   size exceeded, unauthorized scope, conflict, retry limit exceeded, and not found,
6. every attribute described with type, meaning, allowed values, and example value,
7. pagination and filtering documented for item listing,
8. correlation/request identifiers documented in responses and error envelopes,
9. supported versus future behavior described truthfully.

Certification evidence must include endpoint-level tests, OpenAPI contract validation, error-path
tests, and live or integration evidence where the endpoint claims operational behavior.

## Platform Governance And Mesh Requirements

1. Batch orchestration must follow RFC-0026 async job/status/result semantics and current
   RFC-0100 report-job semantics.
2. Concurrency and retry policy must avoid overloading upstream data authorities and preserve
   RFC-0050 service ownership.
3. Batch progress and failure summaries must use platform status/failure vocabulary and be
   documented in OpenAPI.
4. If batch production generates reporting evidence products at scale, RFC-0084/RFC-0091 telemetry,
   SLO, access, lifecycle, and evidence posture must be reviewed and updated where applicable.
5. CI evidence must include retry, resume, idempotency, and concurrency tests before support is
   listed.
6. Any repeatable platform or scaffolding gap found during implementation must be fixed in
   `lotus-platform` automation rather than locally copied into `lotus-report`.
7. Generated documentation, wiki, and supported-features text must distinguish implemented support
   from future RFC scope.
8. Every implementation PR must state whether it changes platform scaffolding, service-local code,
   docs/wiki/context, supported-features material, or API contracts.
9. If multiple repositories change in one slice, each repository must have its own evidence block
   with branch, PR, commit, checks, and remaining risk.

## Requirement Traceability Matrix

Implementation closure must update this matrix with concrete evidence paths before RFC status can
move beyond proposed/in progress.

| Requirement | Primary owner | Required evidence before support |
| --- | --- | --- |
| Batch ledger and item ledger | `lotus-report` | Models, migrations, repository/service tests, uniqueness constraints |
| Explicit portfolio list selector | `lotus-report` plus portfolio source owner | Selector validation tests, source eligibility proof, idempotency tests |
| Selected subset selector | `lotus-report` plus subset source owner | Source contract proof, deterministic materialization tests |
| Schedule and frequency materialization | `lotus-report` | Period/as-of-date tests, unsupported frequency tests |
| Dispatch and report job creation | `lotus-report` | Integration tests proving one item creates/reuses one report job |
| Concurrency and back-pressure | `lotus-report` and platform automation where reused | Race/concurrency tests and policy snapshot evidence |
| Retry, pause, resume, cancel, recovery | `lotus-report` | State-transition tests, expired-lease tests, no-duplicate-output tests |
| Render/archive integration | `lotus-report`, `lotus-render`, `lotus-archive` | Cross-service tests or live proof with artifact ids |
| API certification and Swagger | `lotus-report`, optionally `lotus-gateway` | OpenAPI validation, examples, endpoint tests, error-path tests |
| Documentation, wiki, supported features | Owning repository plus `lotus-platform` if platform truth changes | Docs diff, wiki check or no-change decision, supported-features proof |

## Error Handling Requirements

The implementation must provide deterministic error categories for:

1. selector validation failure,
2. unsupported schedule/frequency,
3. maximum batch size exceeded,
4. duplicate idempotency conflict with incompatible request body,
5. upstream portfolio eligibility failure,
6. upstream data collection failure,
7. render failure,
8. archive handoff failure,
9. retry limit exceeded,
10. expired item lease,
11. cancellation conflict,
12. unauthorized tenant/region/portfolio scope,
13. internal invariant violation.

Every error category must have a client-safe message, operator-safe diagnostic metadata, log
correlation, and tests.

## Observability Floor

RFC-0105 owns the broader observability and operations layer, but RFC-0104 cannot ship blind. The
minimum observability floor is:

1. structured logs for batch creation, item materialization, dispatch, retry, pause, resume, cancel,
   recovery, and terminal state,
2. metrics for active batches, active items, completed items, failed items, retry attempts, lease
   expiries, recovery attempts, and duration,
3. health/readiness impact only where the batch worker is required for service readiness,
4. trace/correlation identifiers propagated into report jobs, render requests, and archive handoff,
5. operator evidence artifacts or API responses sufficient to prove batch completion.

## Implementation Slices

Implementation must proceed slice by slice. Do not move to the next slice until the current slice
is implemented, validated, reviewed, and in a solid state.

### Slice 0: Platform Automation And Scaffolding Improvement

Purpose: improve shared platform and app scaffolding so batch reporting does not solve repeatable
governance concerns locally.

Required work:

1. identify gaps in `lotus-platform` automation that should already be handled by platform
   scaffolding,
2. improve platform automation where needed for API certification, Swagger quality, observability,
   health endpoints, structured logging, error handling, test scaffolding, CI defaults,
   documentation scaffolding, governance hooks, and repo baseline checks,
3. identify cross-cutting concerns that future applications should receive by default,
4. strengthen app scaffolding so new applications start with governance from day one,
5. document any deliberate no-change decisions when platform scaffolding is already sufficient,
6. ensure output benefits future Lotus apps, not only RFC-0104.

Acceptance evidence:

1. platform automation change or explicit no-change rationale,
2. tests for any changed automation,
3. docs/context update if platform truth changed,
4. platform feature-lane validation evidence.

### Slice 1: Cleanup And Structure

Purpose: remove stale batch-reporting sprawl and prepare a clean module boundary.

Required work:

1. review existing batch, scheduler, long-running job, report orchestration, and supported-features
   docs,
2. remove stale script-like batch references,
3. create or prepare a `report_batch_orchestrator` module boundary in `lotus-report`,
4. improve repository structure where needed,
5. move long-lived operator guidance to repo-local wiki source when it is operational truth,
6. avoid duplicate documentation across repo docs and wiki,
7. confirm wiki source and publication posture reflect the planned post-RFC state.

Acceptance evidence:

1. no stale or contradictory batch support claims,
2. module boundary visible and reviewed,
3. docs/wiki decision recorded,
4. targeted tests or lint checks pass.

### Slice 2: Batch Ledger, Selectors, And Idempotent Materialization

Purpose: create durable batch and item truth.

Required work:

1. add `report_batch` and `report_batch_item` models and migrations,
2. implement explicit portfolio list and selected subset selectors first,
3. validate tenant, region, portfolio, active/inactive, duplicate, maximum-size, and unsupported
   selector cases,
4. materialize deterministic batch items before dispatch,
5. implement batch and item idempotency keys,
6. prove duplicate submissions do not duplicate items or report jobs.

Acceptance evidence:

1. migration tests,
2. selector validation tests,
3. idempotent creation tests,
4. duplicate-incompatible-request conflict tests,
5. source API/model mapping documented.

### Slice 3: Scheduling And Frequency Materialization

Purpose: make production cycles deterministic.

Required work:

1. add schedule and frequency contracts,
2. implement monthly, quarterly, semi-annual, yearly, and explicit cycle semantics in the order
   validated by tests,
3. define as-of date, period start, period end, template/package version, and idempotency behavior,
4. ensure all active portfolio scope remains gated until safer selector modes are proven,
5. record any scheduler runtime decision before implementation closure.

Acceptance evidence:

1. schedule materialization tests,
2. period/as-of-date edge-case tests,
3. unsupported frequency tests,
4. idempotency tests for scheduled batches.

### Slice 4: Dispatch, Concurrency, Back-Pressure, And Leases

Purpose: run batches safely without overloading the platform.

Required work:

1. implement batch dispatch from durable item state,
2. create or reuse one `report_job` per batch item,
3. enforce maximum active batches and items,
4. enforce per-upstream, render, and archive concurrency where applicable,
5. add lease/heartbeat fields for in-flight items,
6. prevent duplicate dispatch under concurrent workers,
7. expose operator-visible state without relying on worker memory.

Acceptance evidence:

1. concurrency-limit tests,
2. duplicate-worker race tests,
3. lease acquisition and expiry tests,
4. report-job creation idempotency tests,
5. back-pressure tests for at least render/archive and one upstream service.

### Slice 5: Retry, Pause, Resume, Cancel, And Recovery

Purpose: make partial and interrupted batches recoverable.

Required work:

1. add bounded retry policy,
2. add retry-failed-only behavior for retryable item failures,
3. add pause and resume behavior,
4. add cancel behavior with clear running-job boundary,
5. add recovery scanning for expired leases and abandoned items,
6. prove recovery does not duplicate report jobs, render outputs, or archive records.

Acceptance evidence:

1. retry limit tests,
2. retry-failed-only tests,
3. pause/resume/cancel tests,
4. failed, stuck, partial, and resumed batch tests,
5. no-duplicate-output tests.

### Slice 6: APIs, Swagger, And Certification

Purpose: expose only certified supported behavior.

Required work:

1. add supported `lotus-report` batch APIs,
2. certify every endpoint with behavior, error, contract, and example tests,
3. complete Swagger quality for request/response examples, attribute descriptions, tags, and
   what/when/how guidance,
4. add gateway exposure only if a supported operator/product need is approved,
5. ensure unsupported behavior is absent or explicitly rejected.

Acceptance evidence:

1. endpoint tests,
2. OpenAPI validation evidence,
3. error-path tests,
4. certification notes per endpoint,
5. supported-features updates only for proven endpoints.

### Slice 7: Integration With Report, Render, And Archive

Purpose: prove batch execution uses the existing reporting architecture correctly.

Required work:

1. connect batch items to RFC-0100 report jobs,
2. ensure data snapshots and lineage from RFC-0101 remain intact,
3. ensure render package/template behavior from RFC-0102 remains deterministic,
4. ensure successful render outputs hand off to RFC-0103 archive without bypassing retention,
   legal-hold, lifecycle, or access-audit semantics,
5. verify failure propagation from data, render, and archive stages into item and batch state.

Acceptance evidence:

1. integration tests covering successful report-job/render/archive handoff,
2. render failure propagation tests,
3. archive failure propagation tests,
4. lineage and artifact-reference assertions,
5. documented cross-service evidence.

### Slice 8: Documentation, Runbook, And Supportability Floor

Purpose: make the first-wave batch capability operable before final proof.

Required work:

1. update repo docs and runbooks for creating, inspecting, pausing, resuming, cancelling, and
   retrying batches,
2. update supported-features only for implementation-backed behavior,
3. update wiki source when operator-facing truth changed,
4. document observability floor and known RFC-0105 deferrals,
5. document source gaps, placement questions, or conditional decisions resolved during
   implementation.

Acceptance evidence:

1. docs/runbook review,
2. supported-features truth review,
3. wiki source check or explicit no-wiki-change decision,
4. no duplicate or contradictory docs.

### Slice 9: Implementation Proof

Purpose: prove the implementation end to end against this RFC before hardening.

Required proof:

1. live or integration evidence for explicit-list batch creation through archived document output,
2. live or integration evidence for selected-subset batch creation,
3. evidence that duplicate batch submission is idempotent,
4. evidence that concurrency limits are enforced,
5. evidence that failed items are tracked and retryable,
6. evidence that interrupted or expired-lease items recover safely,
7. evidence that pause, resume, and cancel behavior matches documented semantics,
8. evidence that APIs and Swagger match actual behavior,
9. evidence that no unsupported future behavior is listed as supported,
10. evidence captured with repository, branch, PR, commit SHA, command, endpoint, and artifact
    identifiers.

Acceptance evidence:

1. proof artifacts recorded in RFC closure or linked docs,
2. failed or weak proof findings fixed before moving on,
3. implementation gaps either closed or explicitly deferred with owner and follow-up RFC.

### Second-Last Slice: Hardening, Review, And Certification

Purpose: review the full implementation as production code before closure.

Required work:

1. perform a code review of state transitions, idempotency, concurrency, recovery, data access,
   error handling, and observability,
2. tighten loose ends and remove dead code,
3. verify API certification pattern compliance,
4. verify platform governance and enterprise data mesh standards are met,
5. ensure all APIs are properly certified,
6. ensure Swagger is complete and high quality:
   - grouped correctly,
   - clear what/when/how guidance for each endpoint,
   - full request and response examples,
   - every attribute has description, type, and example value,
7. ensure error handling is complete, correct, and properly tested,
8. run repository-native feature and PR-merge validation lanes,
9. monitor GitHub checks and fix failures promptly.

Acceptance evidence:

1. review findings and resolutions recorded,
2. validation evidence recorded,
3. no known unsupported behavior claimed as supported,
4. CI health green or explicitly explained if external and non-actionable.

### Final Slice: Closure

Purpose: complete documentation, operating context, and branch hygiene.

Required work:

1. update documentation,
2. update agent context when platform or repository operating truth changed,
3. update wiki source and publish after merge when wiki truth changed,
4. update supported-features with implementation-backed product material,
5. update skills/guidance if the work reveals better future execution patterns,
6. explicitly record if no skills, guidance, documentation, or agent-context changes are needed,
7. update RFC status and implementation evidence,
8. ensure branch hygiene and cleanup.

Acceptance evidence:

1. supported-features entries identify the exact implemented selector, scheduling, concurrency,
   retry, API, and recovery behavior,
2. docs/wiki/context/skills decisions recorded,
3. final CI checks green,
4. PR merged and branch cleaned up,
5. RFC records a final gold-pass assessment.

## Acceptance Criteria

The implementation is complete only when:

1. batch reporting supports explicit lists and selected subsets with deterministic materialization,
2. schedule/frequency materialization is deterministic and tested,
3. batch size and concurrency are configurable and enforced,
4. failed items are tracked and retryable when failure category permits retry,
5. interrupted or lease-expired items are recoverable,
6. duplicate batch submissions and concurrent dispatch do not duplicate report jobs or archive
   records,
7. pause, resume, cancel, and retry-failed-only behavior are implemented and documented,
8. operators can inspect progress, item status, and failures through certified APIs or documented
   operator evidence,
9. Swagger is high quality and behavior-accurate,
10. error handling is complete and tested,
11. platform automation/scaffolding gaps discovered during implementation are fixed centrally or
    explicitly recorded as no-change,
12. supported-features documentation reflects only implementation-backed behavior,
13. implementation proof shows report-job, render, and archive integration end to end,
14. final hardening and closure slices are complete.

## Risks

| Risk | Mitigation |
| --- | --- |
| Batch overloads upstream services | Per-upstream concurrency, back-pressure, and feature-lane stress tests |
| Batch state is not recoverable | Durable batch/item ledger, leases, recovery scanner, and recovery tests |
| Duplicate documents are generated | Batch/item idempotency, report-job idempotency, and archive lifecycle checks |
| Long-running jobs become opaque | Progress APIs, status events, structured logs, metrics, and proof artifacts |
| Operator commands become unsafe | Pause/resume/cancel semantics, conflict handling, and endpoint certification |
| RFC-0105 scope leaks into RFC-0104 | Keep broad replay/rerender/regenerate and dashboards out of supported features |
| Unsupported gateway or Workbench surface is built prematurely | Require supported need and gateway/BFF-only consumption before adding surfaces |
| Swagger drifts from actual behavior | Endpoint contract tests and OpenAPI validation in the PR gate |
| Platform scaffolding gaps are solved locally only | Slice 0 requires platform-level remediation or explicit no-change rationale |

## Dependencies

Required implementation dependencies:

1. RFC-0100 report request/job ledger must be available in `lotus-report`.
2. RFC-0101 report data snapshot and lineage contracts must be available for batch-created jobs.
3. RFC-0102 render package/template registry and render service must be available for batch jobs.
4. RFC-0103 archive handoff must be available for successful rendered documents.
5. Portfolio eligibility and selector source truth must be available from the owning Lotus domain
   source.
6. Repository-native CI lanes must run for every changed repository.

Optional dependencies:

1. gateway exposure if an operator/product status API is approved,
2. Workbench exposure only through gateway/BFF after a supported surface is approved,
3. managed scheduler integration if the implementation chooses it over the phase-one local
   scheduler adapter.

## Validation

Required validation:

1. `lotus-report` unit, integration, migration, OpenAPI, and coverage gates,
2. batch creation and selector validation tests,
3. schedule materialization tests,
4. long-running batch simulation,
5. retry/resume/failure tests,
6. pause/cancel tests,
7. concurrency/back-pressure tests,
8. duplicate and race-condition tests,
9. render/archive integration tests,
10. platform feature-lane validation for any `lotus-platform` automation changes,
11. GitHub PR checks monitored and fixed forward.

Evidence must preserve repository, branch, PR number, commit SHA, command, endpoint, batch id, job
id, archive document id, and artifact path wherever those identifiers exist.

## Implementation Status And Evidence

Current status: Slices 0, 1, 2, and 3 are implemented and merged. Slice 0 is implemented in
`lotus-platform`; Slices 1, 2, and 3 are implemented in `lotus-report`. Slice 4 internal dispatch,
lease, report-job creation/reuse, and back-pressure primitives are implemented in the active
`lotus-report` RFC-0104 branch. Slice 5 internal bounded retry, pause/resume,
cancellation-boundary, and expired-lease recovery primitives are implemented in `lotus-report`
commit `ab72576`. Slice 6 certified materialization, status, and control APIs are implemented in
`lotus-report` commit `a061d4e`. Slice 7 internal report-job, snapshot, render, and archive
integration is implemented in the active `lotus-report` RFC-0104 branch. No `lotus-report` batch
scheduler loop, worker process, dispatch operator API, gateway exposure, or Workbench batch surface
is implemented yet.

### Slice 0: Platform Automation And Scaffolding Improvement Evidence

Gap found:

1. `automation/New-Lotus-Service.ps1` generated a service-local `scripts/openapi_quality_gate.py`
   that only checked for the presence of OpenAPI paths.
2. Generated health and metadata endpoints lacked the Swagger-quality baseline expected by current
   Lotus API certification work: tags, summaries, descriptions, response descriptions, and success
   examples.
3. Generated `/metrics` schema exposure caused the strengthened gate to fail because the
   instrumentator route is operational telemetry, not a client-facing API contract.

Implemented improvement:

1. Newly scaffolded Lotus FastAPI services now emit documented health, liveness, readiness, and
   metadata endpoints with explicit tags, summaries, descriptions, response descriptions, and JSON
   response examples.
2. The generated OpenAPI quality gate now checks every generated operation for summary,
   description, tags, response definitions, at least one 2xx response, response descriptions, and
   success examples.
3. The generated Prometheus metrics endpoint remains exposed operationally but is excluded from the
   generated OpenAPI schema.
4. `tests/unit/test_repository_hygiene_scaffold_contract.py` protects the scaffold contract so the
   platform baseline cannot silently regress to path-only OpenAPI validation.

Validation evidence:

1. `python -m pytest tests/unit/test_repository_hygiene_scaffold_contract.py -q` passed with
   2 tests.
2. `python -m pytest tests/unit/test_repository_hygiene_scaffold_contract.py
   tests/unit/test_rfc_closure_governance.py -q` passed with 16 tests.
3. `python automation/validate_engineering_context_system.py` passed.
4. `git diff --check` passed for the Slice 0 patch.
5. `powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane
   feature` passed with 336 tests plus engineering context, agent engineering contracts, heartbeat
   contracts, skill alignment, container baseline, platform validation coverage, mesh advisory, and
   AGENTS synchronization checks.
6. `powershell -ExecutionPolicy Bypass -File automation\Sync-RepoWikis.ps1 -CheckOnly -Repository
   lotus-platform` reported expected `RFC-Index.md` drift because this branch intentionally changes
   repo-authored wiki source. Publication must occur after merge.
7. A fresh generated service scaffold ran its generated `scripts\openapi_quality_gate.py` and
   printed `OpenAPI gate passed`.

Review result:

1. The improvement is deliberately centralized in `lotus-platform` instead of copied into
   `lotus-report`, so future service scaffolds inherit the stronger Swagger-quality posture.
2. This slice does not claim any RFC-0104 batch reporting supported feature. It only strengthens
   the platform baseline required before batch runtime implementation begins.
3. The next slice may start only after this platform Slice 0 branch is merged and required local
   and GitHub evidence is green.

### Slice 1: Cleanup And Structure Evidence

Implemented improvement:

1. `lotus-report` now has an explicit `src/app/report_batch_orchestrator/` module boundary for
   RFC-0104-owned batch orchestration contracts.
2. The boundary defines the first-wave selector and frequency vocabulary in one place:
   `explicit_portfolio_list`, `selected_subset`, `all_active_portfolios`, `batch_manifest`,
   `monthly`, `quarterly`, `semi_annual`, `yearly`, and `explicit`.
3. `BATCH_RUNTIME_SUPPORTED = False` makes the current no-runtime posture executable and testable,
   so planned vocabulary cannot be mistaken for an implemented operator capability.
4. `docs/supported-features.md` now separates RFC-0104 planned feature candidates from
   implementation-backed supported features.
5. `lotus-report` README, repository engineering context, RFC traceability, and repo-local wiki
   source now describe the batch-orchestrator boundary and explicitly exclude scheduler, worker,
   retry, pause/resume/cancel, and recovery runtime behavior.
6. `lotus-report` PR and main releasability Docker build jobs now have `timeout-minutes: 10`, which
   prevents a stuck Docker build from occupying the PR merge gate indefinitely.

Validation evidence:

1. `python -m pytest tests/unit/report_batch_orchestrator/test_boundary.py -q` passed with
   2 tests.
2. `make check` passed in `lotus-report`, including Ruff, Ruff format, monetary-float guard,
   mypy, OpenAPI quality gate, and 239 unit tests.
3. `make docker-build` passed locally for `lotus-report`.
4. `docker run --rm --entrypoint actionlint -v "${PWD}:/repo" -w /repo
   ghcr.io/reviewdog/action-actionlint:v1.72.0` passed for the workflow timeout update.
5. `git diff --check` passed for the Slice 1 branch.
6. `sgajbi/lotus-report#67` passed Feature Lane checks and PR Merge Gate checks, including
   workflow lint, lint/typecheck/security, unit tests, integration tests, e2e tests, combined
   coverage, and Docker build.
7. `sgajbi/lotus-report#67` merged at
   `ea2df53c6a0fd29b9dfdaf2647ef4209dfcdb023`.
8. `powershell -ExecutionPolicy Bypass -File ..\lotus-platform\automation\Sync-RepoWikis.ps1
   -Publish -Repository lotus-report` published the `lotus-report` wiki source.
9. `powershell -ExecutionPolicy Bypass -File ..\lotus-platform\automation\Sync-RepoWikis.ps1
   -CheckOnly -Repository lotus-report` reported zero wiki drift after publication.

Review result:

1. Slice 1 intentionally creates only a clean orchestration boundary and planned vocabulary. It
   does not implement batch scheduling, batch materialization, worker dispatch, retry, recovery,
   or APIs.
2. The no-runtime posture is protected by test coverage and supported-features wording, reducing
   the risk of aspirational documentation being presented as shipped capability.
3. The Docker CI timeout is a production-readiness improvement discovered while proving the slice;
   it prevents a non-diagnostic runner stall from blocking future PRs indefinitely.
4. The next slice may start only after this platform evidence update is merged, platform checks are
   green, and the platform wiki is synchronized.

### Slice 2: Batch Ledger, Selectors, And Idempotent Materialization Evidence

Implemented improvement:

1. `lotus-report` now has source-backed batch materialization primitives in
   `src/app/report_batch_orchestrator/models.py`, `selector.py`, `ledger.py`, and
   `postgres_ledger.py`.
2. Explicit portfolio-list and selected-subset selectors are implemented first. They validate
   tenant, region, active/inactive portfolio status, duplicate requested portfolios, duplicate
   source candidates, unsupported selector modes, empty selectors, missing portfolios, and maximum
   batch size.
3. `migrations/007_report_batch_ledger.sql` adds durable `report_batch` and `report_batch_item`
   tables with idempotency uniqueness, batch-item uniqueness, status constraints, and operational
   indexes.
4. Batch creation is idempotent by caller key and canonical request hash. Duplicate compatible
   submissions return the existing batch and items; duplicate incompatible submissions raise a
   deterministic conflict.
5. Batch items are materialized before any dispatch behavior exists. Slice 2 does not create
   `report_job` rows, does not run a scheduler, and does not expose batch APIs.
6. `docs/standards/batch-orchestration-source-map.md` maps batch attributes to `lotus-core`,
   `lotus-report` caller request data, and `lotus-report` derived composition logic, while
   recording source gaps for `all_active_portfolios` and `batch_manifest`.

Validation evidence:

1. `python -m pytest tests/unit/report_batch_orchestrator -q` passed with 19 tests.
2. `make check` passed in `lotus-report`, including Ruff, Ruff format, monetary-float guard,
   mypy, OpenAPI quality gate, and 256 unit tests.
3. `REPORT_JOB_LEDGER_DATABASE_URL=postgresql://lotus_report:lotus_report@localhost:5439/lotus_report
   make migration-smoke` passed and printed `Migration contract check passed (PostgreSQL report job
   and batch ledger schema mode).`
4. `REPORT_JOB_LEDGER_DATABASE_URL=postgresql://lotus_report:lotus_report@localhost:5439/lotus_report
   make test-integration` passed with 63 tests.
5. `make test-e2e` passed with 6 tests.
6. `REPORT_JOB_LEDGER_DATABASE_URL=postgresql://lotus_report:lotus_report@localhost:5439/lotus_report
   make test-coverage` passed the 99% coverage gate.
7. `make security-audit` passed with no known vulnerabilities.
8. `make docker-build` built `lotus-report:ci-test`.
9. `git diff --check` passed for the Slice 2 branch.
10. `sgajbi/lotus-report#68` passed Feature Lane checks and PR Merge Gate checks, including
    workflow lint, lint/typecheck/security, unit tests, integration tests, e2e tests, combined
    coverage, and Docker build.
11. `sgajbi/lotus-report#68` merged at
    `f6587fc8bc1f58ea5cc812553817cc4fe5d7c428`.
12. `powershell -ExecutionPolicy Bypass -File ..\lotus-platform\automation\Sync-RepoWikis.ps1
    -Publish -Repository lotus-report` published the `lotus-report` wiki source.
13. `powershell -ExecutionPolicy Bypass -File ..\lotus-platform\automation\Sync-RepoWikis.ps1
    -CheckOnly -Repository lotus-report` reported zero wiki drift after publication.

Review result:

1. Slice 2 deliberately stops at durable materialization. It does not leak unsupported scheduler,
   worker, API, dispatch, retry, pause/resume/cancel, or recovery behavior into product
   documentation.
2. The implementation is modular: source-backed selection, durable ledger behavior, PostgreSQL
   schema, migration governance, source mapping, and tests are separated.
3. Duplicate prevention is implemented before dispatch, which reduces later Slice 4 complexity when
   batch items begin creating or reusing report jobs.
4. The next slice may start only after this platform evidence update is merged, platform checks are
   green, and the platform wiki is synchronized.

### Slice 3: Scheduling And Frequency Materialization Evidence

Implemented improvement:

1. `lotus-report` now has deterministic schedule-cycle materialization in
   `src/app/report_batch_orchestrator/schedule.py`.
2. `BatchCycleRequest` and `BatchCycle` in `src/app/report_batch_orchestrator/models.py` define the
   internal schedule contract for monthly, quarterly, semi-annual, yearly, and explicit cycles.
3. Standard frequencies derive `period_start`, `period_end`, and `as_of_date` deterministically from
   the business as-of date; explicit cycles require caller-provided period bounds and validate that
   the as-of date falls inside the explicit period.
4. Scheduled idempotency identity includes caller tenant, caller region, selector mode, frequency,
   period start, period end, as-of date, template id, template version, and render package version.
5. The all-active selector remains deliberately gated. Slice 3 does not create report jobs, does
   not run a scheduler loop, and does not expose batch APIs.
6. `docs/standards/batch-orchestration-source-map.md`, `docs/supported-features.md`,
   `docs/standards/rfc-traceability.md`, README, repository context, and repo-authored wiki source
   now record the schedule-cycle primitives without claiming shipped batch runtime support.

Validation evidence:

1. `python -m pytest tests/unit/report_batch_orchestrator -q` passed with 32 tests.
2. `make check` passed in `lotus-report`, including Ruff, Ruff format, monetary-float guard,
   mypy, OpenAPI quality gate, and 269 unit tests.
3. `REPORT_JOB_LEDGER_DATABASE_URL=postgresql://lotus_report:lotus_report@localhost:5439/lotus_report
   make test-coverage` passed with 269 unit tests, 63 integration tests, 6 e2e tests, total 99%
   coverage, and 100% coverage for `src/app/report_batch_orchestrator/schedule.py`.
4. `REPORT_JOB_LEDGER_DATABASE_URL=postgresql://lotus_report:lotus_report@localhost:5439/lotus_report
   make migration-smoke` passed and printed `Migration contract check passed (PostgreSQL report job
   and batch ledger schema mode).`
5. `make security-audit` passed with no known vulnerabilities.
6. `make docker-build` built `lotus-report:ci-test`.
7. `git diff --check` passed for the Slice 3 branch.
8. `sgajbi/lotus-report#69` passed Feature Lane checks and PR Merge Gate checks, including
   workflow lint, lint/typecheck/security, unit tests, integration tests, e2e tests, combined
   coverage, and Docker build.
9. `sgajbi/lotus-report#69` merged at `28c43e8`.
10. `powershell -ExecutionPolicy Bypass -File ..\lotus-platform\automation\Sync-RepoWikis.ps1
    -Publish -Repository lotus-report` published the `lotus-report` wiki source at wiki commit
    `4062d0e`.
11. `powershell -ExecutionPolicy Bypass -File ..\lotus-platform\automation\Sync-RepoWikis.ps1
    -CheckOnly -Repository lotus-report` reported zero wiki drift after publication.

Review result:

1. Slice 3 deliberately stops at deterministic cycle materialization and scheduled idempotency
   identity. It does not leak unsupported scheduler, worker, API, dispatch, retry,
   pause/resume/cancel, or recovery behavior into product documentation.
2. The implementation is modular: schedule contracts, materialization, idempotency-key generation,
   source mapping, and tests are separated from the batch ledger.
3. The tests cover standard frequency semantics, explicit period validation, unsupported frequency
   handling, vocabulary-drift defense, template/render-package sensitivity, idempotent scheduled
   batch creation, and continued all-active selector gating.
4. The next slice may start only after this platform evidence update is merged, platform checks are
   green, and the platform wiki is synchronized.

### Slice 4: Dispatch, Concurrency, Back-Pressure, And Leases Evidence

Implemented improvement:

1. `lotus-report` now has an internal `ReportBatchDispatcher` that leases materialized batch items
   only when active-batch, active-item, upstream, render, and archive pressure permits dispatch.
2. The PostgreSQL and SQLite ledgers persist `report_job_id`, lease owner/token/acquired/expires
   timestamps, heartbeat time, and dispatch time for batch items.
3. Dispatch creates or reuses exactly one RFC-0100 `report_job` per leased batch item and rejects
   stale lease tokens.
4. Expired leases may be safely re-acquired by another worker without creating duplicate report
   jobs, while report-job-linked items remain protected from duplicate dispatch.
5. `docs/supported-features.md`, `docs/standards/rfc-traceability.md`,
   `docs/standards/batch-orchestration-source-map.md`, README, repository context, and repo-local
   wiki source record the internal dispatch posture without claiming an operator-facing batch
   runtime.

Validation evidence:

1. `python -m pytest tests/unit/report_batch_orchestrator -q` passed with 42 tests.
2. `make check` passed in `lotus-report`, including Ruff, Ruff format, monetary-float guard,
   mypy, OpenAPI quality gate, and 279 unit tests.
3. `REPORT_JOB_LEDGER_DATABASE_URL=postgresql://lotus_report:lotus_report@localhost:5439/lotus_report
   make test-coverage` passed with 279 unit tests, 64 integration tests, 6 e2e tests, total 99%
   coverage, and 100% coverage for `src/app/report_batch_orchestrator/dispatch.py`.
4. `REPORT_JOB_LEDGER_DATABASE_URL=postgresql://lotus_report:lotus_report@localhost:5439/lotus_report
   make migration-smoke` passed and printed `Migration contract check passed (PostgreSQL report job
   and batch ledger schema mode).`
5. `python scripts/rfc_0104_slice4_live_evidence.py --database-url
   postgresql://lotus_report:lotus_report@localhost:5439/lotus_report` produced
   `{"batch_status": "running", "dispatched_count": 1, "job_count": 1}`.
6. `powershell -ExecutionPolicy Bypass -File
   C:\Users\Sandeep\projects\lotus-workbench\scripts\live\Start-LotusFrontOfficeCanonical.ps1
   -CleanCoreState -BuildImages -RunValidation` passed against the canonical Docker front-office
   topology with `lotus-report` backed by `lotus-report-postgres`.
7. `make security-audit` passed with no known vulnerabilities.
8. `make docker-build` built `lotus-report:ci-test`.
9. `git diff --check` passed for the Slice 4 branch.
10. `sgajbi/lotus-report#70` passed Feature Lane and PR Merge Gate checks before Slice 5 local
    work started.

Review result:

1. Slice 4 deliberately stops at internal dispatch primitives. It does not ship a scheduler loop,
   worker process, operator-facing batch API, retry, pause/resume/cancel, or recovery capability.
2. The implementation keeps dispatch, ledger persistence, report-job creation, and runtime-load
   input separated so later scheduler and worker slices can reuse the primitive without copying
   control logic.
3. PostgreSQL is treated as the runtime proof target. SQLite remains only a unit-test adapter.

### Slice 5: Retry, Pause, Resume, Cancel, And Recovery Evidence

Implemented improvement:

1. `lotus-report` now has internal durable state for paused, cancelled, completed,
   completed-with-failures, failed, succeeded, failed-retryable, failed-terminal, cancelled, and
   recovery-pending batch/item lifecycle outcomes.
2. The PostgreSQL migration adds retry/control/recovery fields: attempt count, retry eligibility,
   next retry timestamp, last error category/summary, and batch/item lifecycle timestamps.
3. The PostgreSQL and SQLite ledgers implement bounded retry-failed-only reset, pause, resume,
   cancellation boundaries, expired-lease recovery, and aggregate batch status reconciliation.
4. Retry reset is limited to retryable failed items with no attached `report_job_id`; this prevents
   duplicate report-job creation when a failure occurs after job handoff.
5. Cancellation cancels undispatched or unjobbed work only, leaving items with already-created
   report jobs intact for downstream job lifecycle reconciliation.
6. Expired-lease recovery is idempotent and moves abandoned unjobbed leased items into
   `recovery_pending` for safe redispatch.
7. The migration smoke validator and migration contract now check the Slice 5 schema fields,
   expanded status constraints, and retry lookup index.
8. `docs/supported-features.md`, `docs/standards/rfc-traceability.md`,
   `docs/standards/batch-orchestration-source-map.md`, README, repository context, and repo-local
   wiki source distinguish internal control primitives from operator-supported batch runtime
   capability.

Validation evidence:

1. `python -m pytest tests/unit/report_batch_orchestrator -q` passed locally with 52 tests after
   adding Slice 5 control and recovery coverage.
2. `REPORT_JOB_LEDGER_DATABASE_URL=postgresql://lotus_report:lotus_report@localhost:5439/lotus_report
   python -m pytest tests/integration/test_postgres_report_batch_ledger.py -q` passed locally with
   11 PostgreSQL integration tests after adding Slice 5 parity coverage.
3. `make check` passed in `lotus-report`, including Ruff, Ruff format, monetary-float guard,
   mypy, OpenAPI quality gate, and 289 unit tests.
4. `REPORT_JOB_LEDGER_DATABASE_URL=postgresql://lotus_report:lotus_report@localhost:5439/lotus_report
   make migration-smoke` passed and printed `Migration contract check passed (PostgreSQL report job
   and batch ledger schema mode).`
5. `REPORT_JOB_LEDGER_DATABASE_URL=postgresql://lotus_report:lotus_report@localhost:5439/lotus_report
   make test-integration` passed with 71 tests before the final aggregate-state coverage additions.
6. `make test-e2e` passed with 6 tests.
7. `REPORT_JOB_LEDGER_DATABASE_URL=postgresql://lotus_report:lotus_report@localhost:5439/lotus_report
   make test-coverage` passed with 289 unit tests, 73 integration tests, 6 e2e tests, and total
   99% coverage.
8. `make security-audit` passed with no known vulnerabilities.
9. `make docker-build` built `lotus-report:ci-test`.
10. `powershell -ExecutionPolicy Bypass -File ..\lotus-platform\automation\Sync-RepoWikis.ps1
    -CheckOnly -Repository lotus-report` reported expected wiki publication drift for
    repo-authored wiki changes on this branch. Publication remains a post-merge action.
11. `sgajbi/lotus-report#70` passed Feature Lane and PR Merge Gate checks after the Slice 5 push,
    including lint/typecheck/security, unit tests, integration tests, e2e tests, combined coverage,
    and Docker build.

Review result:

1. Slice 5 deliberately implements internal ledger primitives only. It does not ship scheduler,
   worker, API, Swagger, gateway, Workbench, or operator-supported recovery capability.
2. The critical duplicate-output risk is reduced by refusing retry reset for failed items that
   already have a report job.
3. The control model is intentionally item-level and bounded by retry policy rather than
   whole-batch blind reruns.

### Slice 6: APIs, Swagger, And Certification Evidence

Implemented improvement:

1. `lotus-report` now exposes certified internal batch APIs for durable batch materialization,
   status lookup, pause, resume, cancel, retry-failed, and expired-lease recovery:
   - `POST /reports/batches`
   - `GET /reports/batches/{batch_id}`
   - `POST /reports/batches/{batch_id}:pause`
   - `POST /reports/batches/{batch_id}:resume`
   - `POST /reports/batches/{batch_id}:cancel`
   - `POST /reports/batches/{batch_id}:retry-failed`
   - `POST /reports/batches/{batch_id}:recover-expired-leases`
2. `src/app/routers/report_batches.py` isolates the certified batch API boundary from internal
   dispatch and scheduler primitives.
3. `src/app/report_batch_orchestrator/models.py` now carries product-safe response contracts and
   full OpenAPI examples for batch handle, batch status, item status, control, and recovery
   responses.
4. `src/app/routers/caller_context.py` removes duplicate caller-context validation from
   `report_jobs.py` and reuses the same governed header enforcement for batch create, status, and
   control endpoints.
5. `src/app/report_batch_orchestrator/service.py` wires the PostgreSQL batch ledger through the
   same dependency pattern used by report jobs.
6. `docs/supported-features.md` promotes only
   `lotus-report.reporting.batch_materialization_api.v1` and
   `lotus-report.reporting.batch_control_api.v1` to implementation-backed status. Full
   scheduler/worker-backed batch orchestration remains planned under separate feature keys.
7. README, repository context, API surface wiki, operations runbook wiki, RFC index wiki,
   RFC traceability, and the batch source map now distinguish certified APIs from remaining
   scheduler, worker, dispatch-operator, gateway, and Workbench scope.

Validation evidence:

1. `python -m pytest tests/integration/test_report_batch_api.py
   tests/unit/report_batch_orchestrator/test_boundary.py
   tests/integration/test_api.py::test_integration_capabilities -q` passed with 9 focused tests
   before final coverage-hardening additions.
2. `python -m pytest tests/integration/test_report_batch_api.py -q` passed with 10 tests after
   adding caller-context and error-branch coverage.
3. `make check` passed in `lotus-report`, including Ruff, Ruff format, monetary-float guard,
   mypy, OpenAPI quality gate, and 289 unit tests.
4. `REPORT_JOB_LEDGER_DATABASE_URL=postgresql://lotus_report:lotus_report@localhost:5439/lotus_report
   make migration-smoke` passed and printed `Migration contract check passed (PostgreSQL report job
   and batch ledger schema mode).`
5. `REPORT_JOB_LEDGER_DATABASE_URL=postgresql://lotus_report:lotus_report@localhost:5439/lotus_report
   make test-integration` passed with 79 tests before final coverage-hardening additions.
6. `make test-e2e` passed with 6 tests.
7. `REPORT_JOB_LEDGER_DATABASE_URL=postgresql://lotus_report:lotus_report@localhost:5439/lotus_report
   make test-coverage` passed with 289 unit tests, 83 integration tests, 6 e2e tests, and total
   99% coverage. `src/app/routers/report_batches.py` and
   `src/app/report_batch_orchestrator/service.py` both reached 100% coverage.
8. `make security-audit` passed with no known vulnerabilities.
9. `make docker-build` built `lotus-report:ci-test`.
10. `docker compose up -d --build lotus-report` rebuilt the production-shaped local Docker service
    against healthy `lotus-report-postgres`.
11. Live Docker proof on 2026-04-26 returned OpenAPI paths for `/reports/batches`,
    `/reports/batches/{batch_id}`, `:pause`, `:resume`, `:cancel`, `:retry-failed`, and
    `:recover-expired-leases`, then materialized
    `rbch_b5dc820c412f4763bf9ccb4355755447` for `PB_SG_GLOBAL_BAL_001` with
    `status_counts={"materialized":1}`.
12. `REPORT_JOB_LEDGER_DATABASE_URL=postgresql://lotus_report:lotus_report@localhost:5439/lotus_report
    make ci` passed the composed repo-native CI gate: lint, typecheck, OpenAPI quality, PostgreSQL
    migration smoke, integration, e2e, combined coverage, and security audit.
13. `git diff --check` passed.
14. `powershell -ExecutionPolicy Bypass -File ..\lotus-platform\automation\Sync-RepoWikis.ps1
    -CheckOnly -Repository lotus-report` reported expected wiki publication drift for
    repo-authored wiki changes on this branch. Publication remains a post-merge action.

Review result:

1. Slice 6 deliberately exposes materialization/status/control only. It does not ship scheduled
   execution, worker execution, dispatch operator APIs, gateway routes, or Workbench UI.
2. The certified APIs require caller context headers and idempotency where appropriate, publish
   OpenAPI examples, and return product-safe error codes.
3. The implementation keeps API boundary, ledger construction, caller-context validation, internal
   ledger primitives, docs, and tests separated. That reduces coupling before later scheduler and
   worker slices.
4. A stale local Python listener on `127.0.0.1:8300` initially shadowed the Docker service during
   live proof. It was identified by port ownership, stopped, and the Docker-backed proof was rerun
   successfully against the rebuilt container.

### Slice 7: Integration With Report, Render, And Archive Evidence

Implemented improvement:

1. `src/app/report_batch_orchestrator/execution.py` adds an internal batch item execution bridge.
   The bridge uses the existing RFC-0100 report job ledger, RFC-0101 snapshot capture service,
   RFC-0102 render orchestration service, and RFC-0103 archive handoff path rather than creating a
   second batch-specific reporting pipeline.
2. A dispatched batch item is now reconciled from its linked `report_job_id`:
   - `accepted` jobs are captured through the existing snapshot service.
   - `data_ready` PDF jobs are rendered and archived through the existing render service.
   - successful `archived`, `completed`, `completed_with_warnings`, or json-only `data_ready`
     jobs mark the batch item `succeeded`.
   - failed report jobs propagate failure category, retry posture, and safe summary back to the
     batch item.
3. `src/app/report_batch_orchestrator/ledger.py` and `postgres_ledger.py` add
   `mark_item_succeeded`, clearing lease/retry fields, setting item completion, and reconciling
   aggregate batch status in both the SQLite unit adapter and PostgreSQL runtime ledger.
4. `docs/supported-features.md`, `docs/standards/rfc-traceability.md`,
   `docs/standards/batch-orchestration-source-map.md`, `REPOSITORY-ENGINEERING-CONTEXT.md`, and
   `wiki/RFC-Index.md` now document the internal execution bridge while keeping full
   scheduler/runtime, dispatch operator, gateway, and Workbench scope planned.

Validation evidence:

1. `python -m pytest tests/unit/report_batch_orchestrator/test_execution.py
   tests/unit/report_batch_orchestrator/test_dispatch.py -q` passed with 24 focused tests.
2. `make check` passed in `lotus-report`, including Ruff, Ruff format, monetary-float guard,
   mypy, OpenAPI quality gate, and 298 unit tests.
3. `REPORT_JOB_LEDGER_DATABASE_URL=postgresql://lotus_report:lotus_report@localhost:5439/lotus_report
   make migration-smoke` passed against the Docker `lotus-report-postgres` service.
4. `REPORT_JOB_LEDGER_DATABASE_URL=postgresql://lotus_report:lotus_report@localhost:5439/lotus_report
   make test-integration` passed with 84 PostgreSQL-backed integration tests.
5. `REPORT_JOB_LEDGER_DATABASE_URL=postgresql://lotus_report:lotus_report@localhost:5439/lotus_report
   make ci` passed the composed repo-native CI gate: lint, typecheck, OpenAPI quality,
   PostgreSQL migration smoke, integration, e2e, combined coverage at 99%, and security audit.
6. `make docker-build` built `lotus-report:ci-test`.
7. `docker compose up -d --build lotus-report` rebuilt the production-shaped local Docker service
   against healthy `lotus-report-postgres`; `GET /health` returned `{"status":"ok"}` on
   `localhost:8300`.

Review result:

1. Slice 7 deliberately implements an internal execution bridge only. It does not ship scheduled
   execution, a background executor, dispatch operator APIs, gateway routes, or Workbench UI.
2. The design keeps batch execution thin by reusing the existing report-job, snapshot, render, and
   archive orchestration path. That preserves lineage, render package behavior, archive metadata,
   and failure taxonomy without duplicating those rules inside the batch module.
3. Existing retry semantics remain bounded: failed items with linked report jobs are not blindly
   requeued for duplicate job creation. Later retry execution can explicitly retry or recover the
   linked report job without violating idempotency.

### Slice 8: Documentation, Runbook, And Supportability Floor Evidence

Implemented improvement:

1. `lotus-report/README.md` now records the current RFC-0104 posture: certified internal batch
   materialization/status/control APIs, internal item execution through existing report-job,
   snapshot, render, and archive paths, and the remaining unsupported scheduler/runtime/gateway/UI
   scope.
2. `lotus-report/wiki/Operations-Runbook.md` now provides operator-facing truth for the current
   first-wave batch surface: supported create/status/control actions, durable status semantics,
   correlation/trace behavior, PostgreSQL proof expectations, and RFC-0105 observability deferrals.
3. `lotus-report/wiki/API-Surface.md` now has copy-paste examples for all certified batch control
   endpoints: pause, resume, cancel, retry-failed, and recover-expired-leases.
4. `lotus-report/docs/standards/rfc-traceability.md` records Slice 8 evidence. Supported-features
   remains split between implementation-backed first-wave batch features and planned full
   scheduler/orchestration features.

Validation evidence:

1. `python -m pytest tests/unit/report_batch_orchestrator/test_boundary.py -q` passed.
2. `git diff --check` passed.
3. `powershell -ExecutionPolicy Bypass -File ..\lotus-platform\automation\Sync-RepoWikis.ps1
   -CheckOnly -Repository lotus-report` reported expected branch-local wiki publication drift for
   `API-Surface.md`, `Operations-Runbook.md`, `RFC-Index.md`, and pre-existing
   `Validation-and-CI.md`. Wiki publication remains a post-merge action.

Review result:

1. The previous runbook wording was too broad because it said batch reporting was not implemented,
   while certified materialization/status/control APIs are now shipped. Slice 8 corrected that
   contradiction and narrowed unsupported language to the scheduler/runtime/gateway/UI scope.
2. The documentation now gives operators concrete examples for every currently certified batch
   control endpoint without claiming future scheduled execution or Workbench capability.

### Second-Last Slice: Hardening, Review, And Certification Evidence

Implemented improvement:

1. Reviewed the RFC-0104 `lotus-report` batch surface across
   `src/app/report_batch_orchestrator/`, `src/app/routers/report_batches.py`,
   `docs/supported-features.md`, `wiki/API-Surface.md`, and `wiki/Operations-Runbook.md`.
2. Verified no unresolved `TODO`, `FIXME`, `HACK`, or `TBD` markers remain in the implementation
   slice or proof ledger. Remaining unsupported behavior is intentionally documented as future
   scheduler/runtime/gateway/Workbench scope, not hidden implementation debt.
3. Rechecked API certification posture for `POST /reports/batches`, `GET
   /reports/batches/{batch_id}`, and the pause/resume/cancel/retry/recovery controls:
   - endpoints are grouped under `Report Batches`,
   - request and response examples are present,
   - request and response attributes are typed through Pydantic contracts,
   - caller context and idempotency requirements are enforced,
   - errors use product-safe codes without tracebacks.
4. Rechecked state-transition review coverage for idempotency, dispatch leases, expired lease
   recovery, retry boundaries, cancellation boundaries, successful item reconciliation, and failed
   report-job propagation.
5. Replaced the RFC proof-ledger template with concrete evidence rows so closure no longer depends
   on placeholder proof entries.

Validation evidence:

1. `REPORT_JOB_LEDGER_DATABASE_URL=postgresql://lotus_report:lotus_report@localhost:5439/lotus_report
   make test-integration` passed in `lotus-report` with 85 PostgreSQL-backed integration tests,
   including batch execution through snapshot, render, archive, and status reconciliation.
2. `make check` passed in `lotus-report` with Ruff, Ruff format, monetary-float guard, mypy,
   OpenAPI quality, and 298 unit tests.
3. `REPORT_JOB_LEDGER_DATABASE_URL=postgresql://lotus_report:lotus_report@localhost:5439/lotus_report
   make ci` passed in `lotus-report` with lint, format, monetary-float guard, mypy, OpenAPI
   quality, migration contract check, 85 integration tests, 6 e2e tests, 298 unit tests, combined
   coverage at 99%, and security audit.
4. `git diff --check` passed in both `lotus-report` and `lotus-platform`.
5. GitHub PR `sgajbi/lotus-report#70` at commit
   `b312512cb2640018a825ac939d544fe4bf606095` reached `CLEAN`; Feature Lane and PR Merge Gate
   checks passed, including unit, integration, e2e, combined coverage, and Docker build.
6. GitHub PR `sgajbi/lotus-platform#210` at commit
   `f69fca0e1391a86badf8c88aee10d37807447b9c` reached `CLEAN`; Feature Lane, PR Merge Gate, and
   Cross-App Vocabulary Gate passed.

Review result:

1. The implementation is production-grade for the first-wave RFC-0104 scope: durable internal
   materialization/status/control APIs, deterministic schedule identity primitives, dispatch and
   lease primitives, bounded controls, recovery primitives, and an internal item execution bridge
   over the existing report-job, snapshot, render, and archive path.
2. The implementation deliberately does not claim a scheduler loop, background executor, dispatch
   operator API, gateway route, Workbench surface, or RFC-0105 observability dashboard.
3. No code change was required in this hardening slice because the review did not find stale
   implementation markers, unsafe API error handling, or unsupported behavior listed as shipped.

## Implementation Proof Ledger

The proof ledger is maintained in this RFC because RFC-0104 spans API materialization, internal
dispatch, PostgreSQL concurrency primitives, supportability documentation, and the report-job,
snapshot, render, and archive bridge. Evidence must stay implementation-backed and must not claim
the later scheduler loop, background executor, gateway exposure, or Workbench UI before those slices
ship.

| Proof item | Evidence source | Command/API/artifact | Result | Follow-up |
| --- | --- | --- | --- | --- |
| Explicit-list batch creates items and report jobs | `lotus-report/tests/integration/test_report_batch_api.py`; `lotus-report/tests/unit/report_batch_orchestrator/test_dispatch.py` | `make check`; `REPORT_JOB_LEDGER_DATABASE_URL=postgresql://lotus_report:lotus_report@localhost:5439/lotus_report make test-integration` | Passed locally on 2026-04-26. Explicit-list API materialization and dispatch-linked report job creation are implementation-backed. | None for first-wave materialization/control scope. |
| Selected-subset batch materializes deterministic membership | `lotus-report/tests/unit/report_batch_orchestrator/test_batch_ledger.py`; `lotus-report/tests/integration/test_report_batch_api.py` | `make check`; PostgreSQL integration gate | Passed locally on 2026-04-26. Selected candidates are filtered and ordered deterministically. | None. |
| Duplicate submission is idempotent | `lotus-report/tests/unit/report_batch_orchestrator/test_batch_ledger.py`; `lotus-report/tests/integration/test_postgres_report_batch_ledger.py`; `lotus-report/tests/integration/test_report_batch_api.py` | `make check`; PostgreSQL integration gate | Passed locally on 2026-04-26. Same idempotency key and same materialized request return the existing batch; conflicting request is rejected. | None. |
| Concurrency limit is enforced | `lotus-report/tests/unit/report_batch_orchestrator/test_dispatch.py`; `lotus-report/tests/integration/test_postgres_report_batch_ledger.py` | `make check`; PostgreSQL integration gate | Passed locally on 2026-04-26. Active-batch and active-item limits gate dispatch and leases. | Runtime worker loop remains a later slice. |
| Retry-failed-only retries only eligible failures | `lotus-report/tests/unit/report_batch_orchestrator/test_dispatch.py`; `lotus-report/tests/integration/test_postgres_report_batch_ledger.py`; `lotus-report/tests/integration/test_report_batch_api.py` | `make check`; PostgreSQL integration gate | Passed locally on 2026-04-26. Only due retryable items without linked report jobs are requeued. Job-linked failures remain bounded for explicit future retry execution. | Implement job-linked retry execution in a later scheduler/worker slice. |
| Pause/resume/cancel semantics match API docs | `lotus-report/tests/unit/report_batch_orchestrator/test_dispatch.py`; `lotus-report/tests/integration/test_report_batch_api.py`; `lotus-report/wiki/API-Surface.md` | `make check`; PostgreSQL integration gate; API surface examples | Passed locally on 2026-04-26. Controls preserve already created report jobs and cancel only eligible unstarted items. | None for current control API scope. |
| Expired lease recovery is safe and idempotent | `lotus-report/tests/unit/report_batch_orchestrator/test_dispatch.py`; `lotus-report/tests/integration/test_postgres_report_batch_ledger.py`; `lotus-report/tests/integration/test_report_batch_api.py` | `make check`; PostgreSQL integration gate | Passed locally on 2026-04-26. Expired leases move to recovery-pending once and repeated scans are no-ops. | Scheduler/worker monitoring will consume the primitive in a later slice. |
| Successful item renders and archives document | `lotus-report/tests/integration/test_report_batch_execution.py`; `lotus-report/tests/unit/report_batch_orchestrator/test_execution.py` | `REPORT_JOB_LEDGER_DATABASE_URL=postgresql://lotus_report:lotus_report@localhost:5439/lotus_report python -m pytest tests/integration/test_report_batch_execution.py -q`; full PostgreSQL integration gate | Passed locally on 2026-04-26. A dispatched batch item uses RFC-0100 report job creation, RFC-0101 snapshot persistence, RFC-0102 render orchestration, RFC-0103 archive handoff, then reconciles item and batch status. | None for internal execution bridge scope. |
| Swagger examples match runtime behavior | `lotus-report/tests/integration/test_report_batch_api.py`; OpenAPI quality gate | `make check`; `make ci` | Passed locally on 2026-04-26. Batch create/status/control endpoints have grouped OpenAPI examples and product-safe error behavior. | Gateway exposure remains future scope. |
| Supported-features text is implementation-backed | `lotus-report/tests/unit/report_batch_orchestrator/test_boundary.py`; `lotus-report/docs/supported-features.md` | `python -m pytest tests/unit/report_batch_orchestrator/test_boundary.py -q`; `make check` | Passed locally on 2026-04-26. Supported-features text distinguishes shipped first-wave APIs/internal primitives from planned scheduler/orchestration behavior. | Keep updated as future RFC-0104 slices ship. |

## Supported Features

RFC-0104 currently has implementation-backed batch materialization/status/control APIs exposed to
operators and implementation-backed internal support primitives for schedule-cycle identity,
dispatch, leases, bounded controls, recovery, and item execution through existing report-job,
snapshot, render, and archive paths. Full scheduler/worker-backed orchestration remains planned.

Supported-features entries must be added only after implementation and proof. Each entry must name:

1. selector modes supported,
2. frequencies supported,
3. maximum batch/concurrency controls supported,
4. retry, pause, resume, cancel, and recovery behavior supported,
5. APIs supported,
6. operator evidence supported,
7. unsupported/future behavior still excluded.

Future or unsupported behavior must remain clearly excluded. In particular, broad replay,
rerender, regenerate, dashboards, final security certification, and production certification are
not RFC-0104 supported features unless a later RFC amendment explicitly changes scope.

## Documentation, Wiki, And Context Impact

Implementation must review and update:

1. `lotus-report` docs and supported-features material,
2. `lotus-report` repo-local wiki source when operator guidance changes,
3. `lotus-platform` RFC index or context only if platform truth changes,
4. `lotus-platform` automation docs if scaffolding or governance automation changes,
5. agent context and skills/guidance if the work reveals better future execution patterns.

If no wiki, context, or skills change is needed, the final slice must record that as a deliberate
no-change decision.

## Branching And Delivery Expectations

Implementation must:

1. use a feature branch per repository,
2. create remote branches early so GitHub checks can run asynchronously,
3. keep commits small, meaningful, and truthful,
4. monitor CI at regular intervals,
5. fix failures promptly,
6. avoid branch drift and stale unsupported claims,
7. merge only after required local and GitHub evidence is green or consciously explained.

## Gold-Pass Readiness Assessment

This RFC is ready to guide implementation when this section is true:

1. scope and non-scope are explicit,
2. RFC-0104 ownership is separate from RFC-0105, RFC-0106, and RFC-0107,
3. required slices include platform scaffolding, cleanup, implementation proof, hardening, and final
   closure,
4. every slice has concrete acceptance evidence,
5. API certification and Swagger quality expectations are explicit,
6. supported-features governance prevents aspirational claims,
7. closure requires docs, wiki, context, skills/guidance, and branch hygiene decisions,
8. implementation begins only after the RFC is approved for execution and each slice records its
   evidence before the next slice starts.

## Second Gold-Pass Additions

This final pre-implementation pass tightened the remaining ambiguous areas:

1. explicit pre-implementation decisions required before support can be claimed,
2. selector source mapping and source-gap handling,
3. minimum `report_batch` and `report_batch_item` data contract floors,
4. non-negotiable idempotency, cancellation, recovery, and aggregate-count invariants,
5. storage, migration, indexing, and legacy-job posture,
6. requirement traceability from feature claim to evidence,
7. implementation proof ledger template for closure.

These additions are intended to reduce implementation debate and make the first implementation
slice testable, reviewable, and auditable from the start.
