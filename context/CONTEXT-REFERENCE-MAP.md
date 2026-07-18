# Context Reference Map

Use this file to route quickly to the right Lotus context source without loading unnecessary material.

Start with:

1. [Lotus Quickstart Context](./LOTUS-QUICKSTART-CONTEXT.md)
2. [Lotus Engineering Context](./LOTUS-ENGINEERING-CONTEXT.md)
3. [Task Routing Guide](./TASK-ROUTING-GUIDE.md)
4. [lotus-context-manifest.json](./lotus-context-manifest.json)

## Central Memory Layer

1. [Lotus Quickstart Context](./LOTUS-QUICKSTART-CONTEXT.md)
   Fast orientation for a new session.
2. [Lotus Engineering Context](./LOTUS-ENGINEERING-CONTEXT.md)
   Canonical ecosystem truth and engineering posture.
3. [Platform Engineering Ledger](./platform-engineering-ledger.md)
   Curated record of patterns, fixes, and recurring quality lessons.
4. [Recent Architectural Decisions Digest](./recent-architectural-decisions-digest.md)
   High-signal summary of recent decisions affecting implementation reality.

## Structured Context And Registries

1. [lotus-context-manifest.json](./lotus-context-manifest.json)
   Machine-readable ecosystem inventory and doc routing layer.
2. [Ecosystem Registries](./ECOSYSTEM-REGISTRIES.md)
   Human-readable registry view derived from the manifest.

The manifest currently carries:

1. application registry,
2. domain authority map,
3. standards registry,
4. active RFC registry,
5. canonical reading order,
6. context document path map.

The registry companion currently exposes:

1. application registry,
2. domain authority map,
3. standards registry,
4. active RFC registry.

Important machine-readable platform contract families now include:

1. `../platform-contracts/api-vocabulary/`
2. `../platform-contracts/domain-vocabulary/`
3. `../platform-contracts/domain-data-products/`
4. `../generated/domain-product-catalog.json`
5. `../generated/domain-product-dependency-graph.json`
6. `../platform-contracts/lifecycle-authority/`

For bank lifecycle-authority interoperability, use:

1. [Lifecycle Authority Interoperability](../platform-contracts/lifecycle-authority/README.md)
2. [Signed Decision Schema](../platform-contracts/lifecycle-authority/lifecycle-authority-decision.schema.json)
3. [Key Discovery Schema](../platform-contracts/lifecycle-authority/lifecycle-authority-key-discovery.schema.json)
4. [Producer Certification Posture](../platform-contracts/lifecycle-authority/producer-certification.v1.json)

These artifacts govern interfaces and certification only. Bank legal, records, and privacy
functions retain substantive decision authority.

For governed analytics period naming, use:

1. [Domain Vocabulary Contracts](../platform-contracts/domain-vocabulary/README.md)
2. [Canonical Performance Periods](../platform-contracts/domain-vocabulary/canonical-performance-periods.v1.json)

For RFC-0084 work, the highest-signal machine-readable files are:

Start with [Lotus Data Mesh Standard](../docs/standards/Lotus%20Data%20Mesh%20Standard.md) when
you need the human operating model: what data mesh means in Lotus, which apps own which role, what
certification requires, and which anti-patterns are blocked.

1. [Domain Data Product Contracts](../platform-contracts/domain-data-products/README.md)
2. [Domain Data Product Semantics Registry](../platform-contracts/domain-vocabulary/domain-data-product-semantics.v1.json)
3. [Domain Data Product Trust Metadata Registry](../platform-contracts/domain-vocabulary/domain-data-product-trust-metadata.v1.json)
4. [Generated Domain Product Catalog](../generated/domain-product-catalog.json)
5. [Generated Domain Product Dependency Graph](../generated/domain-product-dependency-graph.json)
6. [Domain Product Source Manifest](../platform-contracts/domain-data-products/domain-product-source-manifest.v1.json)
7. [Generated Domain Product Certification Report](../generated/domain-product-certification-report.json)
8. `../automation/query_domain_product_discovery.py`
   Read-only self-serve query CLI for generated catalog, consumer dependency, and graph-neighborhood
   discovery.
9. `../automation/generate_domain_product_certification.py`
   Generates trust-certification evidence over the catalog and dependency graph without redefining
   product ownership or dependency truth.
10. `../automation/generate_domain_product_discovery.py`
    Reads the governed source manifest, validates included repo-native declarations from sibling
    repositories as one federated source set, and regenerates the catalog and dependency graph.
11. [Trust Telemetry Contracts](../platform-contracts/trust-telemetry/README.md)
    Runtime telemetry schema and validation entrypoint for RFC-0087 live trust evidence.
12. `../automation/validate_trust_telemetry.py`
    Validates product trust telemetry snapshots against the generated product catalog and governed
    trust vocabulary before certification logic consumes them.
13. `../automation/generate_live_trust_certification.py`
    Generates deterministic RFC-0087 live trust certification artifacts from validated telemetry
    snapshots.
14. `../automation/mesh_certification_gate.py`
    Runs the RFC-0089 mesh certification gate. It composes source-manifest/catalog checks,
    first-wave telemetry validation, live trust certification, gateway publication drift checks,
    and Workbench gateway/BFF-only consumption checks.
15. [Mesh Certification Gate Runbook](../docs/operations/mesh-certification-gate-runbook.md)
    Operator commands and fix-forward guidance for advisory, local blocking, and GitHub cross-repo
    mesh certification runs.
16. `../.github/workflows/mesh-certification-gate.yml`
    RFC-0090 GitHub workflow that checks out first-wave sibling repositories and runs the
    RFC-0089 gate in blocking mode with artifact upload and read-only permissions.
17. `../output/mesh-certification/`
    Generated RFC-0089 operator artifacts:
    `mesh-certification-status.json`, `mesh-certification-status.md`, and
    `mesh-certification-issues.json`.
18. `../../lotus-core/contracts/trust-telemetry/`
    First-wave producer telemetry snapshot for `PortfolioStateSnapshot`.
19. `../../lotus-performance/contracts/trust-telemetry/`
    First-wave producer telemetry snapshot for `ReturnsSeriesBundle`.
20. `../../lotus-risk/contracts/trust-telemetry/`
    First-wave producer telemetry snapshot for `RiskMetricsReport`.
21. `../../lotus-advise/contracts/trust-telemetry/`
    First-wave producer telemetry snapshot for `AdvisoryProposalLifecycleRecord`.
22. `../tests/unit/test_domain_product_rollout_closure.py`
    Protects RFC-0086 closure posture: first-wave repo-native source ownership, active catalog source
    paths, `lotus-ai` exclusion rationale, and transitional platform mirror retention.
23. `../tests/unit/test_mesh_certification_gate.py`
    Protects RFC-0089 certified, stale, missing, advisory, artifact rendering, gateway drift, and
    Workbench drift behavior.
24. `../tests/unit/test_mesh_certification_workflow.py`
    Protects RFC-0090 workflow triggers, branch override inputs, checkout layout, artifact upload,
    read-only posture, and no duplicated certification logic in workflow YAML.
25. `../../lotus-gateway/src/app/routers/domain_product_catalog.py`,
    `../../lotus-gateway/src/app/routers/domain_product_detail.py`,
    `../../lotus-gateway/src/app/routers/domain_product_graph.py`, and
    `../../lotus-gateway/src/app/routers/domain_product_trust.py`
    Gateway API face modules for domain-product catalog, detail, dependency graph, and live trust
    certification.
26. `../../lotus-gateway/src/app/services/domain_product_catalog_service.py`
    Gateway service that reads platform-generated discovery and trust artifacts without becoming the
    product authority.
27. `../../lotus-workbench/src/app/data-products/page.tsx`
    Workbench self-serve discovery route that must consume gateway/BFF APIs only.
28. `../../lotus-workbench/src/features/domain-products/`
    Workbench client/API module for catalog, graph, trust, and degraded discovery states.
29. `../automation/generate_enterprise_mesh_maturity_matrix.py`
    Generates and checks the RFC-0091 Slice 0 maturity matrix for repository participation,
    first-wave products, candidate products, support roles, and explicit non-participants.
30. [Enterprise Mesh Maturity Matrix](../generated/enterprise-mesh-maturity-matrix.json)
    Machine-readable RFC-0091 Slice 0 matrix. Generated evidence, not source truth.
31. [Enterprise Mesh Maturity Matrix Markdown](../generated/enterprise-mesh-maturity-matrix.md)
    Human-readable RFC-0091 Slice 0 matrix for implementation planning and operator review.
32. `../automation/generate_domain_product_onboarding.py`
    Generates and validates RFC-0091 self-service onboarding bundles for repo-native product
    declarations, trust telemetry, SLO, access, evidence, source-data API profile, API
    certification checklist, ingestion pipeline checklist, README, and onboarding checklist files.
    The generated bundle is an onboarding aid for owning repositories, not platform product truth.
33. `../automation/collect_trust_telemetry.py`
    Collects RFC-0087 trust telemetry snapshots for RFC-0091 certification. Runtime snapshots from
    sibling repository `output/trust-telemetry/runtime/` directories are preferred; static fixtures
    from `contracts/trust-telemetry/` are explicit fallback evidence in the generated manifest.
34. [Mesh SLO Policies](../platform-contracts/mesh-slo/README.md)
    RFC-0091 first-wave SLO policies for freshness, completeness, reconciliation, data quality,
    lineage, escalation owner, and remediation.
35. `../automation/validate_mesh_slo_policies.py`
    Validates mesh SLO policy identity against the generated catalog and evaluates trust telemetry
    drift for mesh certification.
36. [Mesh Access Policies](../platform-contracts/mesh-access/README.md)
    RFC-0091 first-wave access policies for tenant scope, roles, use cases, denial posture, audit
    owner, and gateway-only publication.
37. `../automation/validate_mesh_access_policies.py`
    Validates mesh access policy identity against the generated catalog and evaluates usable versus
    restricted caller-context posture.
38. [Mesh Evidence Policies](../platform-contracts/mesh-evidence/README.md)
    RFC-0091 first-wave evidence-pack policies and field access classes for public customer,
    restricted customer, operator-only, and internal-only evidence.
39. `../automation/generate_mesh_evidence_pack.py`
    Generates certification-history records and audience-filtered evidence-pack manifests from
    derived mesh certification, catalog, SLO, access, and live trust artifacts.
40. `../../lotus-report/contracts/domain-data-products/lotus-report-products.v1.json`
    RFC-0091 promoted producer declaration for `ClientReportEvidencePack`.
41. `../../lotus-manage/contracts/domain-data-products/lotus-manage-products.v1.json`
    RFC-0091 promoted producer declaration for `PortfolioActionRegister`.
42. [Mesh Certification Gate Runbook](../docs/operations/mesh-certification-gate-runbook.md)
    RFC-0091 operator taxonomy for telemetry, SLO, access, lifecycle, evidence, catalog, gateway,
    and Workbench certification failures.
43. `../output/mesh-certification/enterprise-mesh-certification-status.json`
    RFC-0091 generated enterprise maturity status artifact. Generated evidence, not source truth.
44. `../automation/mesh_maturity_scope.py`
    Shared RFC-0091 maturity-wave product scope used by telemetry collection, SLO, access,
    evidence, maturity matrix, and certification-gate automation.
45. `../automation/generate_enterprise_mesh_operating_report.py`
    Generates the RFC-0092 production mesh operating report from current enterprise certification
    status and certification-history records.
46. `../output/mesh-certification/enterprise-mesh-operating-report.json`
    RFC-0092 generated operator evidence for production-ready versus limited-history posture,
    drift trend, regression detection, product operating posture, and escalation ownership.
47. [Enterprise Mesh Completion Handoff](../docs/operations/enterprise-mesh-completion-handoff.md)
    Durable completion handoff for RFC-0084 through RFC-0092, including product wave, PR evidence,
    wiki publication commits, proof commands, and future-work boundary.
48. [Enterprise Mesh Closure Ledger](../generated/enterprise-mesh-closure-ledger.json)
    Machine-readable closure ledger for completed mesh RFCs, repo roles, product IDs, source PRs,
    published wiki commits, validation commands, and future-work boundary.
49. [Enterprise Mesh Status Wiki Source](../wiki/Enterprise-Mesh-Status.md)
    Authored wiki landing page for human-readable mesh status and restart guidance.

For client demo certification work, use:

1. [Lotus Client Demo Certification Standard](../docs/standards/Lotus%20Client%20Demo%20Certification%20Standard.md)
   Human standard for claim states, evidence requirements, demo packs, and client-safe boundaries.
2. [Lotus Client Demo Operating Process](../docs/demo/client-demo-operating-process.md)
   Client-facing operating process for intake, claim classification, certification, demo packs,
   rehearsal, delivery, and follow-up.
3. [Lotus Client Demo Brief Template](../docs/demo/client-demo-brief-template.md)
   Reusable one-page client brief template that explains what Lotus is doing, why it is
   trustworthy, current boundaries, and follow-up ownership.
4. [Lotus Client Demo Pack Template](../docs/demo/client-demo-pack-template.md)
   Complete demo-pack skeleton for client brief, business story, demo sequence, claim table,
   boundary register, evidence map, rehearsal plan, and follow-up register.
5. [Canonical DPM Demo Story](../docs/demo/canonical-dpm-demo-story.md)
   Audience-ready deep demo narrative for the governed front-office DPM story.
6. [Canonical DPM Demo Story Wiki Source](../wiki/Canonical-DPM-Demo-Story.md)
   Published-source summary for business, operations, engineering, sales, pre-sales, and client demo
   preparation.
7. [Client Demo Certification Wiki Source](../wiki/Client-Demo-Certification.md)
   Human-readable certification process summary.
8. [Client Demo Operating Process Wiki Source](../wiki/Client-Demo-Operating-Process.md)
   Human-readable client-demo workflow summary for business, sales, pre-sales, operations,
   marketing, and engineering readers.
9. [Client Demo Brief Template Wiki Source](../wiki/Client-Demo-Brief-Template.md)
   Human-readable template for client-facing one-page demo briefs.
10. [Client Demo Pack Template Wiki Source](../wiki/Client-Demo-Pack-Template.md)
    Human-readable complete demo-pack structure for claim, evidence, boundary, rehearsal, and
    follow-up governance.
11. `../automation/Invoke-PlatformDemoReadinessCertification.ps1`
   Platform report-only demo-readiness certification wrapper.
12. `../automation/Invoke-Canonical-FrontOffice-QA.ps1`
   Canonical Workbench runtime, API, panel, transcript, and screenshot evidence wrapper.

## Task Routing

1. [Task Routing Guide](./TASK-ROUTING-GUIDE.md)
   Primary task-first routing for frontend, backend, cross-app validation, and governance work.
2. [Lotus Quickstart Context](./LOTUS-QUICKSTART-CONTEXT.md)
   Fast orientation and high-signal working posture.
3. [Lotus Engineering Context](./LOTUS-ENGINEERING-CONTEXT.md)
   Canonical architecture and delivery rules that explain why the task-routing paths exist.

## Procedural Memory

1. [Procedural Memory Index](./PROCEDURAL-MEMORY-INDEX.md)
   Navigation layer for governed operating playbooks.
2. [Change Playbooks](./playbooks/CHANGE-PLAYBOOKS.md)
   Task-type delivery sequences.
3. [PR Loop Playbook](./playbooks/PR-LOOP-PLAYBOOK.md)
   Push, GitHub monitoring, stranded governance truth reconciliation, merge, and cleanup guidance.
4. [Validation Playbook](./playbooks/VALIDATION-PLAYBOOK.md)
   Validation depth and evidence selection.
5. [Fix-Forward Patterns](./playbooks/FIX-FORWARD-PATTERNS.md)
   Repeatable response patterns for CI and runtime failures.
6. [TWR Investigation Playbook](./playbooks/TWR-INVESTIGATION-PLAYBOOK.md)
   Investigation sequence for time-weighted return defects, implausible economics, and upstream reconciliation issues.
7. [Agent Context And Task Ledger Playbook](./playbooks/AGENT-CONTEXT-AND-TASK-LEDGER.md)
   RFC-0093/RFC-0094 sequence for scoped context assembly, exact identifier preservation,
   detached task ledger evidence, RFC-0096 delegation guardrails, and durable promotion decisions.
8. [Agentic Coding Quality Evaluation Loop](./playbooks/AGENTIC-CODING-QUALITY-EVALUATION-LOOP.md)
   How to turn repeated agent-authored code, test, documentation, and CI failures into
   deterministic gates, scorecards, evaluator cases, skills, and context improvements.
9. [Enterprise Backend Refactoring Instructions](./playbooks/ENTERPRISE-BACKEND-REFACTORING-INSTRUCTIONS.md)
   Detailed backend and business-application RFC slice guidance, including source-ownership,
   exact blocker semantics, API/error-model polish, test-pyramid posture, and design-before-runtime
   modularity.
10. [Delegation Policy Contract](../platform-contracts/agent-engineering/delegation-policy-contract.v1.json)
   RFC-0096 governed profiles, input envelopes, output envelopes, write-scope rules, and heartbeat
   attention identifiers for bounded multi-agent work.

## Platform Standards

Key standards to use frequently:

1. [Continuous Integration, Validation, and Release Governance Standard](../docs/standards/Continuous%20Integration%2C%20Validation%2C%20and%20Release%20Governance%20Standard.md)
2. [Testing Pyramid and Coverage Standard](../docs/standards/Testing%20Pyramid%20and%20Coverage%20Standard.md)
3. [Dependency Hygiene and Security Standard](../docs/standards/Dependency%20Hygiene%20and%20Security%20Standard.md)
4. [Enterprise Readiness Standard](../docs/standards/Enterprise%20Readiness%20Standard.md)
5. [Scalability and Availability Standard](../docs/standards/Scalability%20and%20Availability%20Standard.md)
6. [Lotus Data Mesh Standard](../docs/standards/Lotus%20Data%20Mesh%20Standard.md)
7. [Lotus Client Demo Certification Standard](../docs/standards/Lotus%20Client%20Demo%20Certification%20Standard.md)
8. [Platform Observability Standards](../docs/standards/Platform%20Observability%20Standards.md)
9. [Domain Vocabulary Glossary](../docs/standards/Domain%20Vocabulary%20Glossary.md)
10. [Platform Integration Architecture Bible](../docs/architecture/Platform%20Integration%20Architecture%20Bible.md)
11. [Lotus Bank-Buyable Engineering Contract](../platform-standards/LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md)
12. [Lotus Bank-Ready Engineering Implementation Playbook](../platform-standards/LOTUS_BANK_READY_ENGINEERING_IMPLEMENTATION_PLAYBOOK.md)
13. [Bank-Readiness Control Catalog](../platform-contracts/bank-readiness/README.md)
14. [Domain Data Product Contracts](../platform-contracts/domain-data-products/README.md)

Use the bank-buyable contract as the concise non-degradation standard, the implementation playbook
for assessment workflow and evidence boundaries, and the catalog for control definitions and
applicability. Use the enterprise backend refactoring instructions for larger measurement-backed
refactors. Do not load or copy all catalog controls when a bounded slice is sufficient.

## Active Governance RFCs

The most operationally important current RFCs are:

1. [RFC-0071](../rfcs/RFC-0071-centralized-environment-scoped-service-addressing-and-ingress-governance.md)
2. [RFC-0072](../rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md)
3. [RFC-0073](../rfcs/RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md)
4. [RFC-0074](../rfcs/RFC-0074-repeatable-developer-and-agent-bootstrap-system.md)
5. [RFC-0093](../rfcs/RFC-0093-lotus-context-assembly-and-compaction-hardening-for-agentic-development.md)
6. [RFC-0094](../rfcs/RFC-0094-durable-background-engineering-task-ledger-and-governed-delegation-model.md)
7. [RFC-0095](../rfcs/RFC-0095-heartbeat-driven-monitoring-and-attention-surfacing.md)
   advisory heartbeat-driven monitoring and attention surfacing
8. [RFC-0096](../rfcs/RFC-0096-governed-multi-agent-delegation-model.md)
   governed multi-agent delegation model

The next draft implementation sequence for workflow-pack runtime governance is:

1. [RFC-0097](../rfcs/RFC-0097-task-flow-runtime-for-long-running-workflow-packs.md)
   task-flow runtime for long-running workflow packs
2. [RFC-0098](../rfcs/RFC-0098-per-pack-queue-and-concurrency-policy.md)
   per-pack queue and concurrency policy; implemented for the supported `lotus-ai` source-truth
   scope including queue policy, queue events, recovery execution, persisted queued-worker
   execution, final review, docs/context/wiki posture, and branch hygiene; downstream
   gateway/Workbench publication remains future work only if a supported product or operator need
   exists

The current reporting and analytics observability governance references are:

1. [RFC-0105](../rfcs/RFC-0105-reporting-observability-operations-and-replay-tooling.md)
   implemented first-wave reporting observability, operations, rerender, regenerate, replay,
   stuck-state/SLA attention, diagnostics, metrics, and live proof for asynchronous report evidence
   production.
2. [RFC-0108](../rfcs/RFC-0108-front-office-analytics-ui-observability-and-operational-posture.md)
   implemented for first-wave scope and reopened ecosystem scope closed for current
   implementation-backed claims; governs interactive front-office analytics UI
   observability from browser to gateway to backend, including Workbench panel hydration, API
   fan-out, calculation freshness, empty/degraded/stale/error states, frontend/backend
   correlation, no-sensitive-content controls, attention and audit events, and canonical
   `PB_SG_GLOBAL_BAL_001` proof. Slices 0-9 now cover platform contract/scaffold hardening,
   Workbench/Gateway vocabulary, telemetry contract governance, correlation propagation,
   Gateway fan-out structured logs, Workbench metric/dashboard/alert contracts, Workbench attention
   events, Gateway selected analytics read audit logs, governed canonical Workbench proof, a
   rollout-readiness contract that separates certified route/panel scope from residual planned
   gateway/backend/entitlement work, and a hardening review contract covering telemetry fields,
   panel states, API/Swagger applicability, dashboard/alert certification, enterprise governance,
   residual planned scope, and no-open-P0/P1 findings. Final closure adds a governed closure
   contract, validator, docs/context/wiki source updates, residual planned-scope preservation,
   branch/wiki hygiene requirements, and a deliberate no-change skills/guidance review outcome.
   Slices 10 and 11 are complete with a governed ecosystem-completion contract, per-app gap matrix,
   scaffold/CI enforcement contract, validators, first-wave protected evidence, branch policy,
   generated backend no-sensitive-content, implementation-truth, and supported-features gates,
   reusable Workbench/UI observability template, and platform repo check wiring. Slice 12 is partially implemented in
   `lotus-risk` and `lotus-manage` for risk calculation and management action-register
   supportability posture with bounded metrics. Later PRs completed performance/risk backend
   freshness supportability and Gateway/Workbench source-supportability reconciliation for current
   supported reads; Slice 12 remains partially implemented only because full Workbench
   all-supported-surface and full RFC-0079 risk/evidence promotion stay planned.
   Slice 13 has implementation-backed Gateway proof for selected fan-out metrics, protected
   diagnostics lookup, central manage/report/archive/AI client fan-out metrics, and direct
   lotus-core query/control-plane plus ingestion fan-out metrics. Slice 14 is partially implemented
   for supported Workbench reads including Gateway-backed archive metadata/download retrieval, Slice
   15 implements ecosystem dashboard/alert/runbook coverage for
   current metric families, Slice 16 implements platform-owned ecosystem proof automation, and
   Slice 17 implements ecosystem hardening certification with a machine-readable contract and
   validator. Slice 18 implements ecosystem final closure with a separate machine-readable
   contract, validator, and tests that reconcile Slice 17 hardening, Slice 16 proof, ecosystem
   completion status, residual planned scope, local/GitHub proof requirements, wiki publication,
   branch hygiene, and skills guidance. Performance/risk backend freshness is now
   implementation-backed through lotus-performance PR #139 and lotus-risk PR #108, with
   lotus-performance PR #140 hardening capability publication across completed performance
   supportability surfaces and lotus-performance PR #141 hardening explicit performance
   `metric_labels`, shared bounded Prometheus label tuples, and no-sensitive metric-label proof;
   full Workbench supported-surface promotion remains planned until separately implemented and
   proved. Workbench PR #133 closes the current certified read-path
   entitlement proof gap for performance Summary, Risk Review, and Advisor Brief; future certified
   read paths must add equivalent Gateway allow/deny audit, caller-context, BFF forwarding,
   permission-blocked UI, tests, live evidence, and wiki proof before promotion. Workbench PR #134
   adds implementation-backed Advisor Brief review-action mutation observability through the
   bounded `performance-advisor-brief-review-action` surface, `/api/metrics/events` browser metric
   ingest, `/api/metrics` export, bounded mutation errors, Gateway log/trace proof, and no-sensitive
   metric label assertions. Workbench PR #136 hardens the mutation hydration boundary: the same
   review-action mutation emits API request and panel-state metrics but must not increment
   `lotus_workbench_panel_hydration_duration_seconds`; live proof recorded
   `hydrationReviewActionLineCount=0` and `leakedForbidden=[]`. Gateway PR #179 hardens the
   downstream ownership boundary so proposal simulation/create/list/detail/version/workflow/
   approval/lineage uses `lotus-advise` `/advisory/proposals*`, while Gateway `lotus-manage`
   consumption is limited to versioned strategic run, supportability summary, and capability
   endpoints. Workbench PR #137 hardens the canonical live evidence boundary so Workbench no
   longer treats stale direct manage `/integration/capabilities` as proof, validates strategic
   manage supportability through `/api/v1/rebalance/supportability/summary`, preserves
   gateway-first capability proof, and fixes screenshot evidence defects in the performance and
   risk panels before publishing wiki truth. lotus-ai PR #57 hardens AI surface
   supportability proof with bounded `supportability_reason`, explicit `metric_labels`,
   sensitive-diagnostic rejection tests, Prometheus metric-label tests, `make check`, `make ci`,
   Docker build, and published wiki source. lotus-core PR #329 hardens portfolio readiness
   supportability proof with explicit `metric_labels`, bounded Prometheus labels, no-sensitive
   metric-label tests, full local and GitHub runtime gates, and published wiki source. lotus-risk
   PR #109 hardens risk supportability proof with explicit `metric_labels`, bounded Prometheus
   labels, no-sensitive metric-label tests, full local and GitHub runtime gates, and published wiki
   source. lotus-advise PR #109 hardens advisory supportability proof with explicit
   `supportability.metric_labels`, bounded Prometheus labels, no-sensitive metric-label tests,
   full local and GitHub runtime gates, and published wiki source. Workbench
   archive retrieval is supported only through the BFF/Gateway boundary.
   It is not an extension of RFC-0105.

Use [rfcs/README.md](../rfcs/README.md) for the full RFC inventory.

## RFC Governance

1. [RFC Governance Standard](../rfcs/RFC-GOVERNANCE-STANDARD.md)
   Required closure model for new and reopened implementation-bearing RFCs.
2. New or reopened implementation RFCs must include the second-last code-review/governance slice and
   the final docs/context/wiki/skills/branch-hygiene slice described in the standard.

## Task Routing Guidance

### For frontend and product-surface work

Read:

1. the quickstart context,
2. the engineering context,
3. the [Task Routing Guide](./TASK-ROUTING-GUIDE.md),
4. the `lotus-workbench` repository context,
5. RFC-0070 and RFC-0072 where delivery or UI-platform governance matters,
6. the platform validation references when end-to-end proof is required.

### For backend API or domain-service work

Read:

1. the engineering context,
2. the [Task Routing Guide](./TASK-ROUTING-GUIDE.md),
3. the owning repo context,
4. RFC-0067 and related vocabulary or contract standards,
5. RFC-0072 for CI and validation expectations.

### For cross-app runtime and validation work

Read:

1. the engineering context,
2. the [Task Routing Guide](./TASK-ROUTING-GUIDE.md),
3. RFC-0071,
4. RFC-0072,
5. the local development and ingress runbooks,
6. the manifest and [Ecosystem Registries](./ECOSYSTEM-REGISTRIES.md) to identify participating services and canonical paths.

### For platform standards and governance work

Read:

1. the engineering context,
2. the [Task Routing Guide](./TASK-ROUTING-GUIDE.md),
3. RFC-0072,
4. RFC-0073,
5. the relevant standard documents under `platform-standards/`,
6. the platform engineering ledger and recent architectural decisions digest.

### For README, wiki, and documentation-system work

Read:

1. the engineering context,
2. the target repo context,
3. [Lotus Documentation Layering](../docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md),
4. [Task Routing Guide](./TASK-ROUTING-GUIDE.md),
5. [Lotus Skill Routing Map](./LOTUS-SKILL-ROUTING-MAP.md) when a documentation skill boundary matters,
6. only the target repo `README.md`, `wiki/`, and deeper `docs/` pages needed to keep the docs truthful.

## Runbooks And Operations

1. [Lotus Developer Onboarding](../docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md)
2. [Lotus Agent Ramp-Up](../docs/onboarding/LOTUS-AGENT-RAMP-UP.md)
3. [Local Development Runbook](../docs/operations/Local%20Development%20Runbook.md)
4. `docs/` and `automation/README.md` in `lotus-platform`
5. platform validation and ingress automation under `automation/`

## Enterprise Backend Refactor Quality

For `lotus-platform` enterprise backend refactor work, use:

1. [Enterprise Backend Refactoring Instructions](./playbooks/ENTERPRISE-BACKEND-REFACTORING-INSTRUCTIONS.md)
2. `../automation/generate_enterprise_backend_quality_baseline.py`
3. `../quality/baseline_report.md`
4. `../quality/quality_scorecard.md`
5. `../quality/refactor_health_report.md`
6. `../quality/architecture_rules.md`
7. `../quality/ci_quality_gates.md`

The quality baseline is initially report-only. Promote individual signals only after they are
measured, deterministic, low-noise, locally runnable, and represented in repo checks, scorecards,
docs, wiki source, repo context, central context, and relevant skill guidance.

## Repository-Local Context Documents

These are now the implementation-truth entrypoints for each repo:

1. [lotus-platform/REPOSITORY-ENGINEERING-CONTEXT.md](../REPOSITORY-ENGINEERING-CONTEXT.md)
2. `lotus-workbench/REPOSITORY-ENGINEERING-CONTEXT.md`
3. `lotus-gateway/REPOSITORY-ENGINEERING-CONTEXT.md`
4. `lotus-core/REPOSITORY-ENGINEERING-CONTEXT.md`
5. `lotus-performance/REPOSITORY-ENGINEERING-CONTEXT.md`
6. `lotus-risk/REPOSITORY-ENGINEERING-CONTEXT.md`
7. `lotus-advise/REPOSITORY-ENGINEERING-CONTEXT.md`
8. `lotus-manage/REPOSITORY-ENGINEERING-CONTEXT.md`
9. `lotus-report/REPOSITORY-ENGINEERING-CONTEXT.md`
10. `lotus-idea/REPOSITORY-ENGINEERING-CONTEXT.md`
11. `lotus-render/REPOSITORY-ENGINEERING-CONTEXT.md`
12. `lotus-ai/REPOSITORY-ENGINEERING-CONTEXT.md`

Use [Repository Engineering Context Contract](./Repository-Engineering-Context-Contract.md) and [the template](./templates/REPOSITORY-ENGINEERING-CONTEXT.template.md) when updating or extending the repo-local context set.

