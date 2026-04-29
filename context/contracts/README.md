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
   The RFC-0108 inventory of planned analytics UI metric families, forbidden fields, state
   vocabulary, governed telemetry event names, severity levels, attention/audit event types,
   trace attributes, dashboard/alert reference policy, protected diagnostics policy,
   supported-feature keys, evidence requirements, and scaffold requirements.

Rules:

1. update these files through governed RFC implementation, not ad hoc edits,
2. keep field naming explicit and domain-correct,
3. keep contracts machine-readable and stable enough for tests and automation,
4. avoid embedding fake supportability or UI-only expectations that backend services do not own.
