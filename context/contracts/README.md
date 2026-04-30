# Context Contracts

This directory stores machine-readable, platform-governed contracts that are intended to be
consumed by Lotus automation, validation, and product-surface governance.

These files are not product-runtime source-of-truth implementations by themselves. They define the
cross-repository contract that implementation work must satisfy.

Current contracts:

1. `canonical-front-office-demo-data-contract.json`
   The governed identity, ownership, date policy, and coverage contract for the canonical
   front-office portfolio and benchmark.
2. `canonical-front-office-demo-data-invariants.json`
   The governed minimum thresholds and supportability invariants for the canonical dataset.
3. `workbench-panel-registry.schema.json`
   The governed schema for the RFC-0077 machine-readable Workbench panel registry.
4. `workbench-panel-registry.json`
   The governed initial panel inventory, state policy, ownership mapping, and evidence posture for
   the canonical Workbench front-office surface.
5. `reporting-observability-contract.schema.json`
   The governed schema for the RFC-0105 reporting metrics, dashboard, and alert contract.
6. `reporting-observability-contract.json`
   The first-wave machine-readable inventory of implemented reporting metrics plus dashboard and
   alert references that are allowed to claim them.
7. `analytics-ui-observability-contract.schema.json`
   The governed schema for the RFC-0108 front-office analytics UI observability contract.
8. `analytics-ui-observability-contract.json`
   The RFC-0108 inventory of implemented first-wave Workbench analytics UI metric and attention
   event families, implemented Gateway analytics fan-out, read-audit, protected-diagnostics
   events, expanded central Gateway client fan-out metrics, direct lotus-core Gateway fan-out
   metrics, planned later backend metric families, forbidden fields,
   state vocabulary, governed telemetry event names, severity levels, attention/audit event types,
   trace attributes, dashboard/alert reference policy, protected diagnostics policy,
   supported-feature keys, evidence requirements, and scaffold requirements.
9. `analytics-ui-observability-rollout-readiness.schema.json`
   The governed schema for RFC-0108 analytics UI rollout readiness after canonical proof.
10. `analytics-ui-observability-rollout-readiness.json`
   The RFC-0108 Slice 9 expansion contract that records certified Workbench route and panel scope,
   the reusable rollout checklist, validator proof cases, and residual planned scope before broader
   analytics UI observability claims are promoted.
11. `analytics-ui-observability-hardening-review.schema.json`
    The governed schema for the RFC-0108 second-last hardening, API/Swagger certification, and
    governance review.
12. `analytics-ui-observability-hardening-review.json`
    The RFC-0108 second-last review contract that records telemetry-field review, panel-state
    review, API/Swagger applicability, dashboard/alert certification, enterprise-governance
    posture, findings, residual scope, local proof commands, and required GitHub checks.
13. `analytics-ui-observability-final-closure.schema.json`
    The governed schema for the RFC-0108 final closure contract.
14. `analytics-ui-observability-final-closure.json`
    The RFC-0108 final closure contract that records implemented-scope closure, merged PR
    evidence, local proof commands, required GitHub checks, wiki publication requirements,
    skills/guidance review, residual planned scope, and branch hygiene requirements.
15. `analytics-ui-observability-ecosystem-completion.schema.json`
    The governed schema for the RFC-0108 Slice 10 ecosystem-completion contract.
16. `analytics-ui-observability-ecosystem-completion.json`
    The RFC-0108 Slice 10 contract that records every participating Lotus repository, the
    ecosystem completion slices, first-wave protected evidence, per-app observability gap matrix,
    required GitHub checks, and branch policy that blocks runtime work before contract expansion
    is merged.
17. `analytics-ui-observability-scaffold-ci-enforcement.schema.json`
    The governed schema for RFC-0108 Slice 11 platform scaffold and CI enforcement.
18. `analytics-ui-observability-scaffold-ci-enforcement.json`
    The RFC-0108 Slice 11 contract that proves generated backend service defaults, reusable
    Workbench observability surface defaults, platform CI wiring, generated workflow templates, and
    reusable validators that keep observability, OpenAPI, supported-features, docs/wiki, evidence,
    and no-sensitive-content checks platform-owned.
19. `analytics-ui-observability-ecosystem-proof.schema.json`
    The governed schema for RFC-0108 Slice 16 ecosystem implementation proof.
20. `analytics-ui-observability-ecosystem-proof.json`
    The RFC-0108 Slice 16 contract that records the supported end-to-end Lotus user journeys,
    canonical runtime identity, protected diagnostics proof, Gateway OpenAPI proof, dashboard and
    alert reconciliation, residual planned scope, and local proof commands.

Rules:

1. update these files through governed RFC implementation, not ad hoc edits,
2. keep field naming explicit and domain-correct,
3. keep contracts machine-readable and stable enough for tests and automation,
4. avoid embedding fake supportability or UI-only expectations that backend services do not own.
