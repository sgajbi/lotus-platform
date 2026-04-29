# RFC Index

## Most operationally important current RFCs

- `RFC-0071`
  centralized environment-scoped service addressing and ingress governance
- `RFC-0072`
  platform-wide multi-lane CI validation and release governance
- `RFC-0073`
  Lotus ecosystem engineering context and agent guidance system
- `RFC-0074`
  repeatable developer and agent bootstrap system
- `RFC-0093`
  context assembly and identifier-preserving compaction for agentic development
- `RFC-0094`
  durable background engineering task ledger and governed delegation model
- `RFC-0095`
  advisory heartbeat-driven monitoring and attention surfacing
- `RFC-0096`
  governed multi-agent delegation profiles, task ledgers, and review discipline

## Important repo-specific references

- [rfcs/README.md](../rfcs/README.md)
- [RFC-0071](../rfcs/RFC-0071-centralized-environment-scoped-service-addressing-and-ingress-governance.md)
- [RFC-0072](../rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md)
- [RFC-0073](../rfcs/RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md)
- [RFC-0074](../rfcs/RFC-0074-repeatable-developer-and-agent-bootstrap-system.md)
- [RFC-0089](../rfcs/RFC-0089-mesh-certification-merge-gate-and-operational-trust-enforcement.md)
  mesh certification merge gate and operational trust enforcement
- [RFC-0090](../rfcs/RFC-0090-cross-repo-mesh-certification-pr-merge-gate.md)
  cross-repo mesh certification PR Merge Gate enforcement
- [RFC-0091](../rfcs/RFC-0091-enterprise-data-mesh-maturity-and-production-readiness.md)
  enterprise data mesh maturity and production readiness
- [RFC-0092](../rfcs/RFC-0092-production-mesh-operations-and-escalation-control.md)
  production mesh operations and escalation control
- [RFC-0093](../rfcs/RFC-0093-lotus-context-assembly-and-compaction-hardening-for-agentic-development.md)
  context assembly, compaction, and durable promotion rules for agentic development
- [RFC-0094](../rfcs/RFC-0094-durable-background-engineering-task-ledger-and-governed-delegation-model.md)
  background engineering task ledger, lifecycle, evidence, and delegation governance
- [RFC-0095](../rfcs/RFC-0095-heartbeat-driven-monitoring-and-attention-surfacing.md)
  heartbeat-driven monitoring and deduplicated attention surfacing
- [RFC-0096](../rfcs/RFC-0096-governed-multi-agent-delegation-model.md)
  governed multi-agent delegation profiles, evidence, and review discipline
- [RFC-0097](../rfcs/RFC-0097-task-flow-runtime-for-long-running-workflow-packs.md)
  task-flow runtime for long-running workflow packs
- [RFC-0098](../rfcs/RFC-0098-per-pack-queue-and-concurrency-policy.md)
  per-pack queue, lane, timeout, and concurrency policy; `lotus-ai` source-truth queue policy, durable queue-event history, terminal timeout/cancellation/degraded posture, retry/replay recovery-decision posture, repeated-failure cluster attention, degraded queue-source attention, persisted admission-lifecycle events, governed queue request-snapshot artifact refs, bounded snapshot-backed retry/replay execution, persisted queued-worker execution through the existing async runtime, final review, docs/context/wiki, and branch hygiene are complete
- [RFC-0099](../rfcs/RFC-0099-enterprise-reporting-and-document-archive-target-architecture.md)
  proposed target-state architecture for enterprise reporting, `lotus-render`, future
  `lotus-archive`, batch reporting, durable lineage, rendering, archival, observability, security,
  and ordered follow-up RFC sequence
- [RFC-0100](../rfcs/RFC-0100-reporting-gateway-invocation-and-job-ledger-foundation.md)
  proposed gateway-first report initiation and durable report job ledger foundation
- [RFC-0101](../rfcs/RFC-0101-report-data-snapshot-and-lineage-contracts.md)
  proposed report data snapshot and upstream lineage contract
- [RFC-0102](../rfcs/RFC-0102-render-package-template-registry-and-render-service.md)
  proposed `lotus-render` render package, template registry, and Typst rendering service
- [RFC-0103](../rfcs/RFC-0103-document-archive-retrieval-retention-and-legal-hold.md)
  implemented first-wave `lotus-archive` document metadata, retrieval, retention, legal hold,
  lifecycle, `lotus-report` handoff, and gateway retrieval support
- [RFC-0104](../rfcs/RFC-0104-batch-reporting-scheduler-concurrency-and-recovery.md)
  implemented for first-wave scope; durable batch materialization/status/control APIs, deterministic
  schedule-cycle identity, dispatch/lease/back-pressure, retry/recovery controls, internal
  execution bridge, bounded worker primitive, certified internal run-once operator API, and bounded
  internal runtime-pass primitive plus daemonized internal worker and scheduler processes,
  explicit/all-active/inline-manifest scheduler selectors, and gateway-facing batch
  materialization/status/control/operator-run APIs plus Workbench gateway-backed explicit
  single-portfolio batch operation and gateway-facing scheduler administration are implemented.
  RFC-0105 dashboards/replay, RFC-0106 security certification, and RFC-0107 production
  certification remain pending
- [RFC-0105](../rfcs/RFC-0105-reporting-observability-operations-and-replay-tooling.md)
  implementation started with Slice 0 platform scaffold hardening, Slice 1 `lotus-report`
  observability structure cleanup, Slice 2 cross-service trace/structured logging proof across
  `lotus-gateway`, `lotus-report`, `lotus-render`, and `lotus-archive`, Slice 3 first-wave
  reporting metrics, dashboard, alert, and SLA contracts, Slice 4 first-wave report-job
  operator diagnostics, Slice 5 archived-report rerender from immutable snapshot, Slice 6
  regenerate from upstream data, and Slice 7 failed-work replay for failed retry-eligible report
  jobs and implementation-backed batch items; reporting
  observability, operator APIs, replay, rerender, regenerate, stuck-job, SLA monitoring, implementation slices, API
  certification requirements, supported-features governance, RFC-0104 batch/scheduler-admin
  observability inputs, live proof expectations, future-service correlation-id plus trace-id
  propagation defaults, `lotus-report` runtime observability vocabulary ownership,
  implementation-backed `GET /reports/jobs/{job_id}/diagnostics`,
  implementation-backed `POST /reports/jobs/{job_id}/rerender` for archived PDF correction from
  the same snapshot id/hash, implementation-backed `POST /reports/jobs/{job_id}/regenerate` for
  archived PDF upstream refresh with new snapshot/lineage and replacement archive identities,
  implementation-backed `POST /reports/jobs/{job_id}/replay`,
  implementation-backed `POST /reports/batches/{batch_id}/items/{batch_item_id}/replay`, and the
  data-protection gate before stuck-state/SLA monitoring are now tracked
- [RFC-0106](../rfcs/RFC-0106-reporting-security-entitlements-and-region-tenant-segregation.md)
  gold-pass ready with implementation not started; reporting security, entitlements, role/action
  matrix, caller context, service-to-service trust, region/tenant/booking-center segregation,
  document access audit, sensitive-surface controls, API certification, supported-features
  governance, and live proof expectations are tightened before implementation
- [RFC-0107](../rfcs/RFC-0107-enterprise-reporting-production-certification.md)
  gold-pass ready with implementation not started; final enterprise reporting production
  certification across gateway, report, render, archive, upstream services, Workbench where
  supported, batch, observability, security, evidence-pack schema, non-functional thresholds,
  docs, wiki, context, and supported-features is tightened before implementation
- [RFC-0108](../rfcs/RFC-0108-front-office-analytics-ui-observability-and-operational-posture.md)
  implementation started with Slice 0 complete; governed front-office analytics UI
  observability across Workbench browser rendering, gateway/BFF/API delivery, backend analytics
  fan-out, user-visible freshness/degraded/empty/error states, attention and audit events,
  no-sensitive-content controls, supported-features governance, and canonical proof through
  `PB_SG_GLOBAL_BAL_001`. Slice 0 adds platform analytics UI observability contract validation plus
  generated-app product-safe error, structured JSON event, supported-features, RFC evidence,
  operations observability, and API certification scaffolding. This is not an extension of RFC-0105
  reporting observability.

## Recommended next implementation order

1. Review and approve RFC-0099 before implementation starts for enterprise reporting, rendering,
   batch production, or document archival.
2. RFC-0100 through RFC-0105 now have implementation-backed first-wave reporting, rendering,
   archival, batch, observability, operations, and replay scope. Continue the reporting sequence
   with RFC-0106 security certification and then RFC-0107 production certification.
3. RFC-0108 may proceed separately for analytics UI observability. It must not be treated as
   reporting scope or a casual RFC-0105 extension; it starts from a governed Workbench/gateway/
   backend telemetry contract and proves one canonical analytics path before rollout.
4. None currently open in the RFC-0095 through RFC-0098 workflow-pack runtime sequence.
   Future gateway or Workbench queue-posture work should start only from a concrete supported
   operator or product need.

## Local meaning

- RFC-0071 governs canonical local hostnames and ingress posture
- RFC-0072 governs lane structure and validation expectations
- RFC-0073 governs the central context system and operating contract
- RFC-0074 governs onboarding, bootstrap, and skill distribution posture
- RFC-0089 governs the first-wave mesh certification gate, operator artifacts, and
  fix-forward workflow for trust telemetry, gateway publication, and Workbench discovery drift
- RFC-0090 governs the GitHub cross-repo workflow that runs RFC-0089 in blocking mode with sibling
  producer, gateway, and Workbench checkouts
- RFC-0091 governs the final enterprise mesh maturity program; Slice 0 adds the generated maturity
  matrix that classifies repository participation and candidate expansion before implementation
  continues; Slice 1 adds the self-service onboarding scaffold and validation command for new
  repo-native product bundles; Slice 2 adds runtime-preferred trust telemetry collection with
  explicit static fixture fallback evidence; Slice 3 adds first-wave mesh SLO policy enforcement
  into certification; Slice 4 adds first-wave access governance policies and certification checks;
  Slice 5 adds certification-history records and audience-filtered evidence-pack manifests; Slice
  6 promotes reporting and management products into the enterprise maturity wave; Slice 7 adds the
  enterprise maturity certification taxonomy, evidence-policy drift checks, lifecycle drift checks,
  and enterprise certification artifacts; Slice 8 centralizes the maturity-wave scope and removes
  duplicate required-product lists from certification automation; Slice 9 completes documentation,
  agent context, wiki, skills-routing, and branch-hygiene readiness updates
- RFC-0092 governs the production mesh operating layer. It adds an enterprise operating report
  generated by the mesh certification gate, with operating state, certification-history trend,
  regression detection, product operating posture, escalation ownership, and operator guidance.
- RFC-0093 governs context assembly, compaction, exact identifier preservation, and durable
  promotion decisions for long-running agentic development work.
- RFC-0094 governs detached engineering task identity, lifecycle states, local automation evidence,
  bounded delegation, and the separation between GitHub check truth and local background-run truth.
- RFC-0095 is implemented for advisory heartbeat attention surfacing.
- RFC-0096 is implemented for bounded multi-agent delegation. It adds governed delegation profiles,
  RFC-0094-compatible delegated task ledger records, main-agent review discipline, and optional
  RFC-0095 heartbeat attention for stale, failed, lost, missing-evidence, unresolved-review, and
  overlapping-write-scope delegated work.
- RFC-0097 is implemented for the first-wave advisor-brief task-flow runtime across `lotus-ai`,
  `lotus-gateway`, and `lotus-workbench`, with clean-core live proof recorded and repo wikis
  published.
- RFC-0098 is implemented for its supported scope: `lotus-ai` queue policy, admission, source API,
  queue-attention posture, durable queue-event history, terminal timeout/cancellation/degraded
  posture, retry/replay recovery-decision posture, repeated-failure cluster attention, degraded
  queue-source attention, persisted admission-lifecycle events, governed queue request-snapshot
  artifact refs, bounded snapshot-backed retry/replay execution, and persisted queued-worker
  execution through the existing async runtime are complete; downstream queue posture remains
  future work unless a concrete gateway/operator or Workbench product need appears.
- RFC-0099 is proposed for enterprise reporting target architecture. It records `lotus-report` as
  the reporting orchestration and report-data owner, future `lotus-render` as deterministic
  rendering owner, future `lotus-archive` as generated-document archive and retrieval owner, and
  `lotus-gateway` as the front-office invocation and retrieval boundary. It is not implementation
  evidence and should not be treated as proof that render or archive services exist.
- RFC-0100 through RFC-0103 are implemented for first-wave reporting, rendering, and archival scope.
  RFC-0103 establishes `lotus-archive` as the generated-document archive owner, with controlled
  metadata and binary retrieval, access audit, retention, purge, legal hold, lifecycle
  relationships, `lotus-report` handoff, and `lotus-gateway` retrieval. Workbench retrieval remains
  deferred until a concrete gateway-backed product surface is approved. RFC-0104 is implemented for
  first-wave scope with durable batch materialization/status/control, deterministic schedule
  identity, dispatch/recovery primitives, an internal execution bridge, bounded worker primitive,
  certified internal run-once operator API, bounded internal runtime-pass primitive, daemonized
  internal worker and scheduler processes with explicit/all-active/inline-manifest scheduler
  selectors, gateway-facing batch materialization/status/control/operator-run APIs, gateway-facing
  scheduler administration, and Workbench gateway-backed explicit single-portfolio batch operation.
  RFC-0105 observability/operations, RFC-0106 security, and RFC-0107 production certification remain
  pending.
