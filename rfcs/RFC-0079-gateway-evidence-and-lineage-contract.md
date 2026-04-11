# RFC-0079: Gateway Evidence and Lineage Contract

- Status: Proposed
- Date: 2026-04-11
- Owners: lotus-platform governance
- Requires Approval From:
  - lotus-gateway maintainers
  - lotus-performance maintainers
  - lotus-risk maintainers
  - lotus-core maintainers
  - lotus-workbench maintainers
- Related:
  - `RFC-0063-performance-analytics-input-contracts-and-stateful-computation.md`
  - `RFC-0067-centralized-api-vocabulary-inventory-and-openapi-documentation-governance.md`
  - `RFC-0070-gold-standard-product-experience-foundation-and-ownership-model.md`
  - `RFC-0075-canonical-front-office-portfolio-seed-and-demo-validation-system.md`
  - `RFC-0077-workbench-panel-registry-and-evidence-contract.md`
  - `RFC-0078-modular-front-office-validation-framework.md`

## Summary

The current Workbench `performance.evidence` experience is truthful but degraded because the
gateway contract does not yet expose enough execution, lineage, coverage, and methodology evidence
to support a first-class evidence panel.

This RFC proposes a governed gateway evidence and lineage contract so Lotus product surfaces can
show calculation supportability with banking-grade clarity rather than generic "unavailable"
messages.

## Problem

Today, a user can see summary analytics while still lacking a coherent explanation of:

1. where the result came from,
2. which services participated,
3. whether the inputs were fresh,
4. which methodology and calculation basis applied,
5. which dimensions or segments are supported,
6. whether fallbacks or limitations were used.

This is a trust gap. In a private-banking and portfolio-analytics platform, evidence and lineage are
not optional embellishments. They are part of the product contract.

## Goals

1. Define a gateway evidence and lineage contract for performance and risk analytics.
2. Make execution supportability explicit to UI consumers.
3. Expose freshness, source, methodology, coverage, and limitations in a structured way.
4. Ensure evidence states can be validated and rendered consistently across product surfaces.
5. Support truthful `ready`, `partial`, and `unavailable` panel states.
6. Align the contract with Lotus domain language and OpenAPI governance.

## Non-Goals

1. Replacing backend observability tooling.
2. Exposing internal implementation details that should remain service-private.
3. Adding unsupported analytics just to populate the evidence UI.
4. Creating a generic lineage platform unrelated to product needs.

## Proposed Contract

### Candidate Endpoints

The exact path names should be finalized in gateway design review, but the contract should expose
evidence per product surface, for example:

```text
GET /api/v1/workbench/{portfolio_id}/performance/evidence
GET /api/v1/workbench/{portfolio_id}/risk/evidence
GET /api/v1/workbench/{portfolio_id}/analytics/evidence
```

The final design may choose route-specific or consolidated endpoints. The important point is that
the evidence contract must be explicit, typed, and documented.

### Required Evidence Fields

Minimum fields should include:

1. `portfolio_id`
2. `as_of_date`
3. `period`
4. `basis`
5. `benchmark_code`
6. `calculation_scope`
7. `execution_status`
8. `source_services`
9. `input_freshness`
10. `methodology_references`
11. `calculation_versions`
12. `coverage`
13. `fallbacks`
14. `limitations`
15. `generated_at`

### Example Shape

```json
{
  "portfolio_id": "PB_SG_GLOBAL_BAL_001",
  "as_of_date": "2026-04-10",
  "period": "YTD",
  "basis": "NET",
  "benchmark_code": "BMK_PB_GLOBAL_BALANCED_60_40",
  "calculation_scope": "performance_analysis",
  "execution_status": "partial",
  "source_services": [
    {
      "service": "lotus-performance",
      "status": "ready",
      "as_of_date": "2026-04-10",
      "freshness_status": "fresh"
    }
  ],
  "input_freshness": {
    "positions": "fresh",
    "prices": "fresh",
    "benchmark": "fresh"
  },
  "methodology_references": [
    {
      "metric_family": "attribution",
      "document_id": "performance-attribution-methodology-v1"
    }
  ],
  "calculation_versions": {
    "gateway_contract": "v1",
    "analytics_engine": "2026.04"
  },
  "coverage": {
    "supported_dimensions": ["asset_class"],
    "unsupported_dimensions": ["issuer"]
  },
  "fallbacks": [],
  "limitations": [
    "Lineage artifact retrieval is not yet available for issuer-level attribution."
  ],
  "generated_at": "2026-04-11T02:30:00Z"
}
```

## Design Principles

1. Business-facing clarity over internal jargon.
2. Truthful disclosure of partial support.
3. Stable field naming with OpenAPI documentation.
4. No UI-only fake evidence.
5. No leaking of unsafe internal details.
6. Methodology references must connect to governed documentation.

## Product Surface Expectations

Once this contract exists, Workbench evidence panels should be able to answer:

1. Is the displayed result fully supported, partially supported, or unavailable?
2. Which services contributed?
3. Were the inputs fresh?
4. Which benchmark and basis were applied?
5. Which dimensions are actually supported?
6. Were any fallbacks used?
7. Which methodology should the user review?

## API Governance Requirements

This RFC must align with RFC-0067 expectations:

1. OpenAPI documentation is mandatory,
2. vocabulary must be consistent across services,
3. no opaque aliases or ambiguous names,
4. examples must be truthful and domain-correct,
5. partial-state semantics must be standardized.

## Testing Requirements

Required testing should include:

1. gateway contract tests,
2. service integration tests for evidence mapping,
3. Workbench rendering tests for `ready`, `partial`, and `unavailable` states,
4. live validation checks proving evidence contract support,
5. regression tests ensuring unsupported dimensions are explicitly disclosed.

## Documentation Requirements

The following must be updated:

1. gateway OpenAPI specs,
2. methodology references used by evidence payloads,
3. Workbench product-surface docs,
4. agent guidance and panel registry references.

## Proposed Implementation Slices

### Slice 1: Evidence Vocabulary and OpenAPI Proposal

1. finalize field names and state vocabulary,
2. define response schemas,
3. document examples and semantics.

### Slice 2: Performance Evidence Support

1. expose performance evidence through gateway,
2. include source-services, freshness, and methodology references,
3. add gateway and service tests.

### Slice 3: Risk Evidence Support

1. expose risk evidence for supported risk panels,
2. disclose partial and unsupported areas explicitly,
3. align wording with Workbench panel expectations.

### Slice 4: Workbench Evidence Panel Upgrade

1. replace current degraded placeholder handling with contract-backed rendering,
2. support meaningful empty/partial/ready states,
3. add browser and component tests.

### Slice 5: Documentation, Agent Context, Skill Alignment, and Branch Hygiene

1. integrate evidence checks into the live validation framework,
2. align with the panel registry,
3. update docs, operational runbooks, and any context references that should explicitly point to
   evidence-backed product support,
4. review whether skills and guidance should reference the evidence contract directly or via linked
   runbooks,
5. complete branch hygiene, PR evidence hygiene, and cross-repo reference cleanup before closure.

## Acceptance Criteria

1. Gateway exposes a documented evidence contract for supported analytics surfaces.
2. Workbench evidence panels are backed by real contract data.
3. Partial and unsupported states are explicit and truthful.
4. Methodology and freshness references are available in a structured way.
5. Tests prove both API correctness and UI rendering behavior.

## Risks and Mitigations

### Risk: Contract exposes too much internal detail

Mitigation:

1. expose only product-relevant evidence,
2. review payloads for security and operational sensitivity,
3. keep deep observability in internal tooling.

### Risk: Over-promising unsupported capabilities

Mitigation:

1. use explicit coverage and limitation fields,
2. fail validation when UI claims unsupported evidence,
3. require owner sign-off for each supported evidence scope.

## Approval Request

Approve this RFC if Lotus should treat evidence and lineage as a first-class product contract rather
than a secondary implementation detail.
