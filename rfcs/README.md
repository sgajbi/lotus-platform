# Cross-Repository Alignment RFCs

This folder contains architecture RFCs to align:

- `lotus-advise` (current `lotus-advise`)
- `lotus-performance` (current `lotus-performance`)
- `lotus-risk` (current `lotus-risk`)
- `lotus-core` (current `lotus-core`)
- `lotus-manage` (current `lotus-manage`)
- `lotus-gateway` (current `lotus-gateway`)
- `lotus-report` (current `lotus-report`)
- `lotus-workbench` (current `lotus-workbench`)
- `lotus-platform` (current `lotus-platform`)
- `lotus-ai` (current `lotus-ai`)

Reference baseline:
- `lotus-advise` is the primary engineering standard for automation, testing, and architecture discipline.
- Advanced patterns from the other repositories are absorbed where they improve platform quality.

## RFC Index

- `RFC-0001-repository-strategy-and-target-operating-model.md`
- `RFC-0002-bounded-contexts-and-service-boundaries.md`
- `RFC-0003-canonical-domain-vocabulary.md`
- `RFC-0004-cross-service-api-contract-standard.md`
- `RFC-0005-engineering-baseline-and-delivery-standards.md`
- `RFC-0006-shared-python-platform-libraries.md`
- `RFC-0007-bff-integration-contract-for-ui-platform.md`
- `RFC-0008-phased-migration-roadmap-and-governance.md`
- `RFC-0009-platform-service-topology-and-deduplication.md`
- `RFC-0010-reporting-and-document-generation-service.md`
- `RFC-0011-platform-control-plane-and-configurability.md`

## Principles

- Standardization over compatibility (no production consumers yet).
- No backward compatibility requirements for naming/structure while pre-live.
- Single responsibility per service.
- No duplicated ownership of domain capabilities.
- UI consumes a unified lotus-gateway contract, not raw service contracts.
- Cloud and on-prem deployment parity is required for productization.

## Central Standards

- `Domain Vocabulary Glossary.md`
- `Migration Engineering Quality Standard.md`

## Execution RFC Set (Implementation Start)

- `RFC-0012-refined-long-term-platform-vision.md`
- `RFC-0013-repository-strategy-separate-vs-consolidated.md`
- `RFC-0014-commercial-naming-and-positioning-strategy.md`
- `RFC-0015-domain-boundaries-and-service-ownership.md`
- `RFC-0016-standardization-principles-and-engineering-baseline.md`
- `RFC-0017-ui-bff-first-delivery-strategy.md`
- `RFC-0018-phased-implementation-roadmap.md`
- `RFC-0019-pragmatic-unification-plan-now-vs-later.md`
- `RFC-0020-sprint-1-lotus-workbench-vertical-slice.md`
- `RFC-0021-authn-authz-foundation-deferred.md`
- `RFC-0022-performance-analytics-engineering-alignment-to-dpm-standard.md`
- `RFC-0023-performance-analytics-quality-hardening-coverage-and-docker-smoke.md`
- `RFC-0024-lotus-workbench-ui-stack-alignment-and-bff-proxy-hardening.md`
- `RFC-0025-lotus-workbench-proposal-workflow-ux-hardening.md`
- `RFC-0026-lotus-workbench-proposal-operations-workspace.md`
- `RFC-0027-dpm-feature-parity-program-for-lotus-workbench.md`
- `RFC-0028-dpm-parity-phase-2-proposal-version-management.md`
- `RFC-0029-suite-architecture-pas-pa-dpm-and-ui-bff-evolution.md`
- `RFC-0030-ui-suite-storyboard-with-mocked-pas-pa-and-live-dpm.md`
- `RFC-0031-ui-enterprise-workflow-language-and-lineage-visibility.md`
- `RFC-0032-advisor-workflow-shell-phase-1-client-and-task-centric-command-center.md`
- `RFC-0033-advisor-workflow-shell-phase-2-role-based-operating-views.md`
- `RFC-0034-pas-ingestion-integration-for-real-portfolio-creation-from-ui.md`
- `RFC-0035-private-banking-intake-console-ux-hardening.md`
- `RFC-0036-intake-entity-list-operations-and-enterprise-ux-structure.md`
- `RFC-0037-intake-governed-selectors-via-pas-lookups.md`
- `RFC-0038-intake-production-ux-hardening-with-enterprise-form-patterns.md`
- `RFC-0039-ui-responsive-scaling-and-overlap-hardening.md`
- `RFC-0040-ui-browser-qa-remediation-and-enterprise-ux-hardening.md`
- `RFC-0041-platform-integration-architecture-bible-governance.md`
- `RFC-0042-capabilities-governed-ux-contract-and-current-state-assessment.md`
- `RFC-0043-pas-core-snapshot-provenance-and-governance-contract.md`
- `RFC-0044-platform-capability-policy-visibility-in-bff-and-ui.md`
- `RFC-0045-pas-policy-diagnostics-orchestration-in-bff-and-ui.md`
- `RFC-0046-platform-reference-dataset-and-route-identity-alignment.md`
- `RFC-0047-automated-demo-data-pack-bootstrap-and-targeted-service-refresh.md`
- `RFC-0047-domain-driven-product-experience-portfolio-advisory-dpm-lifecycles.md`
- `RFC-0048-shared-automation-and-agent-toolkit.md`
- `RFC-0049A-portfolio-360-and-live-proposal-sandbox.md`
- `RFC-0050-core-data-analytics-and-reporting-service-boundaries.md`
- `RFC-0051-cross-platform-vocabulary-normalization.md`
- `RFC-0052-reporting-and-aggregation-service-v1-bootstrap.md`
- `RFC-0053-pa-authoritative-advanced-analytics-cutover.md`
- `RFC-0054-ras-reporting-endpoint-ownership-cutover.md`
- `RFC-0055-api-driven-service-integration-and-dual-mode-execution.md`
- `RFC-0056-ras-summary-review-phase2-orchestration.md`
- `RFC-0057-test-pyramid-and-meaningful-coverage-governance.md`
- `RFC-0058-coverage-policy-command-alignment-after-99-enforcement.md`
- `RFC-0059-backend-foundation-standardization-wave-1.md`
- `RFC-0060-phase-2-shared-standards-and-automated-conformance.md`
- `RFC-0061-openapi-contract-quality-and-conformance-automation.md`
- `RFC-0062-domain-vocabulary-conformance-automation.md`
- `RFC-0063-platform-wide-rounding-and-precision-standard.md`
- `RFC-0064-lotus-platform-rebrand-and-enterprise-productization-baseline.md`
- `RFC-0065-lotus-performance-to-lotus-performance-and-lotus-risk-split.md`
- `RFC-0066-lotus-advise-to-lotus-advise-and-lotus-manage-split.md`
- `RFC-0067-centralized-api-vocabulary-inventory-and-openapi-documentation-governance.md`
- `RFC-0068-centralized-shared-infrastructure-ownership-and-migration.md`
- `RFC-0069-lotus-ai-shared-ai-platform-service.md`
- `RFC-0070-gold-standard-product-experience-foundation-and-ownership-model.md`
- `RFC-0071-centralized-environment-scoped-service-addressing-and-ingress-governance.md`
- `RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`
- `RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md`
- `RFC-0074-repeatable-developer-and-agent-bootstrap-system.md`
- `RFC-0022-platform-target-operating-model-and-service-additions.md`
- `RFC-0023-pas-api-product-and-governance-principles.md`
- `RFC-0024-pas-pa-dpm-integration-and-boundary-model.md`
- `RFC-0025-backend-driven-configurability-entitlements-and-workflow-control.md`
- `RFC-0026-synchronous-vs-asynchronous-integration-patterns.md`
- `RFC-0027-reporting-and-analytics-separation-strategy.md`
- `RFC-0028-ui-bff-integration-model-and-responsibility-rules.md`
- `RFC-0029-phased-integration-roadmap-pas-pa-dpm.md`
- `RFC-0030-adr-governance-and-decision-traceability.md`
- `RFC-0082-lotus-core-domain-authority-and-analytics-serving-boundary-hardening.md`
- `RFC-0083-lotus-core-system-of-record-target-architecture.md`
- `RFC-0084-mesh-governance.md`
- `RFC-0085-gateway-governed-domain-product-publication-and-trust-contracts.md` (implemented and merged for first-wave gateway publication)
- `RFC-0086-repo-native-domain-product-onboarding-and-federated-rollout.md` (implemented)
- `RFC-0087-live-trust-telemetry-and-certification-plane.md` (implemented and merged for first-wave telemetry, certification, gateway, and Workbench consumption)
- `RFC-0088-self-serve-discovery-and-dependency-catalog.md` (implemented and merged for generated discovery plus Workbench UI)
- `RFC-0089-mesh-certification-merge-gate-and-operational-trust-enforcement.md` (implemented for first-wave mesh certification enforcement)
- `RFC-0090-cross-repo-mesh-certification-pr-merge-gate.md` (implemented for GitHub cross-repo mesh certification gate enforcement)
- `RFC-0091-enterprise-data-mesh-maturity-and-production-readiness.md` (implemented; enterprise maturity matrix, self-service onboarding, telemetry collection, mesh SLO enforcement, access governance, evidence packs, broader product rollout, enterprise certification gate, governance tightening, and final docs/context/wiki/skills review complete)
- `RFC-0092-production-mesh-operations-and-escalation-control.md` (implemented; enterprise operating report, drift trend, regression detection, escalation queue, product operating posture, and operator guidance generated by the mesh certification gate)
- `RFC-0093-lotus-context-assembly-and-compaction-hardening-for-agentic-development.md` (implemented on `main`; context assembly, identifier preservation, procedural memory, skill guidance, AGENTS guidance, wiki source, and validation evidence complete)
- `RFC-0094-durable-background-engineering-task-ledger-and-governed-delegation-model.md` (implemented on `main`; task-ledger contract, background-run ledger state, lifecycle vocabulary, skill guidance, AGENTS guidance, wiki source, and validation evidence complete)
- `RFC-0095-heartbeat-driven-monitoring-and-attention-surfacing.md` (implemented; advisory heartbeat contract, runner, source adapters, workflow-pack attention adapter, deduplication, suppression, validator coverage, docs/context/wiki/skills review complete)
- `RFC-0096-governed-multi-agent-delegation-model.md` (implemented; governed delegation policy contract, RFC-0094-compatible delegated task ledger records, return-envelope review discipline, optional RFC-0095 heartbeat attention, AGENTS/context/wiki/skills guidance, and validation evidence complete)
- `RFC-0097-task-flow-runtime-for-long-running-workflow-packs.md` (implemented; first-wave advisor-brief task-flow runtime, gateway posture, Workbench rendering, clean-core live proof, wiki publication, and branch hygiene complete)
- `RFC-0098-per-pack-queue-and-concurrency-policy.md` (implemented for supported scope; `lotus-ai` source-truth queue policy, admission, queue-status, queue-attention, durable queue-event history, terminal timeout/cancellation/degraded posture, retry/replay recovery-decision posture, repeated-failure cluster attention, degraded queue-source attention, persisted admission-lifecycle events, governed queue request-snapshot artifact refs, bounded snapshot-backed retry/replay execution, persisted queued-worker execution through the existing async runtime, final review, docs/context/wiki, and branch hygiene are complete; optional downstream publication remains future work only if a concrete supported need appears)
- `RFC-0099-enterprise-reporting-and-document-archive-target-architecture.md` (proposed; target-state architecture for enterprise reporting, `lotus-render`, future `lotus-archive`, batch reporting, lineage, rendering, archival, observability, security, and ordered follow-up RFC sequence)
- `RFC-0100-reporting-gateway-invocation-and-job-ledger-foundation.md` (proposed; gateway-first report initiation, durable report request/job ledger, idempotency, status vocabulary, and first job APIs)
- `RFC-0101-report-data-snapshot-and-lineage-contracts.md` (proposed; report data snapshots, upstream-call evidence, hash/reference semantics, supportability, and data mesh alignment)
- `RFC-0102-render-package-template-registry-and-render-service.md` (in progress on feature branches; `lotus-render` service, render package contract, template registry, Typst rendering, render diagnostics, first-wave live proof, portfolio-review visual-system uplift, and `lotus-report` render-package integration are branch-proven, with final review, merge, wiki publication, and branch hygiene still pending)
- `RFC-0103-document-archive-retrieval-retention-and-legal-hold.md` (implemented for supported first-wave scope; `lotus-archive` service, metadata, object-storage abstraction, controlled archive APIs, access audit, retention, purge, legal hold, lifecycle relationships, `lotus-report` handoff, and `lotus-gateway` retrieval are complete; Workbench retrieval, batch/replay/operations, full security certification, and production certification remain later RFC scope)
- `RFC-0104-batch-reporting-scheduler-concurrency-and-recovery.md` (implemented for first-wave scope; durable batch materialization/status/control APIs, schedule-cycle identity primitives, dispatch/lease/back-pressure, retry/recovery controls, internal item execution bridge, bounded worker run primitive, internal run-once operator API, bounded internal runtime-pass primitive, daemonized internal worker process, config-backed internal scheduler process with explicit/all-active/inline-manifest selectors, gateway-facing batch materialization/status/control/operator-run APIs, gateway-facing scheduler administration, and Workbench gateway-backed explicit single-portfolio batch operation are implemented; RFC-0105 dashboards/replay, RFC-0106 security certification, and RFC-0107 production certification remain pending)
- `RFC-0105-reporting-observability-operations-and-replay-tooling.md` (implemented for first-wave scope with Slice 0 platform scaffold hardening, Slice 1 `lotus-report` observability structure cleanup, Slice 2 cross-service trace/structured logging proof across `lotus-gateway`, `lotus-report`, `lotus-render`, and `lotus-archive`, Slice 3 first-wave reporting metrics, dashboard, alert, and SLA contracts, Slice 4 first-wave report-job operator diagnostics, Slice 5 archived-report rerender from immutable snapshot, Slice 6 regenerate from upstream data, Slice 7 failed-work replay for failed retry-eligible report jobs and implementation-backed batch items, Slice 8 source-backed stuck-state/SLA attention scanning, and Slice 9 live implementation proof and final closure; traces, metrics, logs, dashboards, operator APIs, rerender, regenerate, replay, stuck-job, SLA monitoring, implementation slices, API certification requirements, supported-features governance, RFC-0104 batch/scheduler-admin observability inputs, and live proof expectations are tightened; future service scaffolds now include correlation-id plus trace-id propagation defaults, `lotus-report` owns runtime observability vocabulary, `GET /reports/jobs/{job_id}/diagnostics` is implementation-backed for one-job operator review, `POST /reports/jobs/{job_id}/rerender` is implementation-backed for archived PDF correction from the same snapshot id/hash, `POST /reports/jobs/{job_id}/regenerate` is implementation-backed for archived PDF upstream refresh with new snapshot/lineage and replacement archive identities, `POST /reports/jobs/{job_id}/replay` is implementation-backed for failed retry-eligible report jobs, `POST /reports/batches/{batch_id}/items/{batch_item_id}/replay` is implementation-backed for failed retry-eligible batch items linked to failed report jobs, `GET /reports/operations/attention` is implementation-backed for bounded report-job and batch-item stuck-state/SLA attention events, and `lotus-report/output/rfc-0105-live-evidence-20260428-165945` proves the first-wave report/render/archive, rerender, regenerate, replay, scheduler-admin, attention, diagnostics, and metrics path live)
- `RFC-0106-reporting-security-entitlements-and-region-tenant-segregation.md` (gold-pass ready; implementation not started; reporting and document entitlement model, role/action matrix, caller context, service-to-service trust, region/tenant/booking-center segregation, audit, sensitive-surface controls, API certification, supported-features governance, and live proof expectations are tightened before implementation)
- `RFC-0107-enterprise-reporting-production-certification.md` (gold-pass ready; implementation not started; final production certification across gateway, report, render, archive, upstream services, Workbench where supported, batch, observability, security, evidence-pack schema, non-functional thresholds, docs, wiki, context, and supported-features is tightened before implementation)
- `RFC-0108-front-office-analytics-ui-observability-and-operational-posture.md` (first-wave implementation complete and reopened ecosystem scope closed for current implementation-backed claims; Slices 10-11 are complete with the ecosystem completion contract, per-app gap matrix, scaffold/CI enforcement contract, generated backend no-sensitive-content and supported-features gates, reusable Workbench/UI observability template, validators, and tests; governed front-office analytics UI observability across Workbench browser rendering, gateway/BFF/API delivery, backend analytics fan-out, user-visible freshness/degraded/empty/error states, attention and audit events, no-sensitive-content controls, supported-features governance, and canonical proof through `PB_SG_GLOBAL_BAL_001`; Slices 0-9 and the first-wave hardening/final closure are implemented; Slice 13 has implementation-backed Gateway proof for selected fan-out metrics, protected diagnostics lookup, central manage/report/archive/AI client fan-out metrics, and direct lotus-core query/control-plane plus ingestion fan-out metrics; Slice 14 has partial Workbench proof for supported Portfolio workspace, client-side Performance, Risk, explicit report-batch operator reads, and Gateway-backed archive metadata/download reads through a code-owned observed-surface registry reconciled to the governed endpoint registry with no-sensitive metric labels, canonical browser proof captured for `PB_SG_GLOBAL_BAL_001`, source support-state proof for `supportability.state` / `supportability.freshness_bucket`, partial RFC-0079 performance evidence-context reconciliation through Gateway and Workbench, render supportability reconciliation through Gateway PR #171 plus Workbench PR #124 for supported report-batch operator reads, advisory supportability reconciliation through Gateway PR #172 plus Workbench PR #125 for supported advisor-brief reads, and archive retrieval reconciliation through Workbench PR #126 plus lotus-archive commit `203ec6d`; Slice 15 implements platform dashboard, alert, runbook, validator, and platform-stack test coverage across every currently implemented RFC-0108 metric family without sensitive dashboard variables or alert labels; Slice 16 implements platform-owned ecosystem proof automation for the current supported Lotus journey across portfolio state, performance analytics, risk analytics, advisory workflow actions, manage/report capability posture, evidence support posture, AI-backed support, protected diagnostics, Gateway OpenAPI diagnostics evidence, dashboards, alerts, screenshots, residual planned-scope preservation, and no-sensitive assertions; Slice 17 implements platform-owned ecosystem hardening certification with a machine-readable contract, validator, and tests that reconcile supported features, per-repository reviews, Slice 16 proof, protected diagnostics OpenAPI evidence, dashboard/alert proof, residual planned scope, and no-open-P0/P1 findings; Slice 18 implements a separate ecosystem final closure contract, validator, and tests that reconcile Slice 17 hardening, Slice 16 proof, ecosystem completion status, residual planned scope, local/GitHub proof, wiki publication, and branch hygiene; performance/risk backend freshness/supportability metrics are implemented through lotus-performance PR #139 and lotus-risk PR #108; Workbench PR #134 implements Advisor Brief review-action mutation observability through bounded /api/metrics/events ingest, /api/metrics export, Gateway log/trace proof, and no-sensitive metric labels; full RFC-0079 risk/evidence scope remains planned residual; this is not an extension of RFC-0105 reporting observability)

## Recommended Next Implementation Order

1. Review and approve `RFC-0099-enterprise-reporting-and-document-archive-target-architecture.md`
   before implementation starts for enterprise reporting, rendering, batch production, or document
   archival.
2. RFC-0100 through RFC-0105 have implementation-backed first-wave reporting, rendering, archival,
   batch, observability, operations, and replay scope. Continue the reporting sequence with
   RFC-0106 security certification and then RFC-0107 production certification.
3. RFC-0108 may proceed separately for analytics UI observability. It must not be treated as
   reporting scope or a casual RFC-0105 extension; it starts from a governed Workbench/gateway/
   backend telemetry contract and proves one canonical analytics path before rollout.
4. None currently open in the RFC-0095 through RFC-0098 workflow-pack runtime sequence.
   Future gateway or Workbench queue-posture work should start only from a concrete supported
   operator or product need.

## RFC Closure Governance

Use [RFC Governance Standard](RFC-GOVERNANCE-STANDARD.md) for new or reopened implementation
RFCs.

Every implementation-bearing RFC must include:

1. a second-last slice for code review, loose-end tightening, API certification-pattern checks, and
   platform-governance conformance,
2. a final slice for documentation, agent context, wiki updates, skills/guidance assessment, and
   branch hygiene.

Legacy RFCs that predate this rule are not rewritten only for formatting. When a legacy RFC is
reopened for implementation, it must be brought up to the current closure standard in the same
change.
