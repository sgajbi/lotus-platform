# RFC-0077: Workbench Panel Registry and Evidence Contract

- Status: Proposed
- Date: 2026-04-11
- Owners: lotus-platform governance
- Requires Approval From:
  - lotus-platform maintainers
  - lotus-workbench maintainers
  - lotus-gateway maintainers
  - lotus-core maintainers
  - lotus-performance maintainers
  - lotus-risk maintainers
  - lotus-advise maintainers
  - lotus-manage maintainers
  - lotus-report maintainers
  - lotus-ai maintainers
- Related:
  - `RFC-0057-test-pyramid-and-meaningful-coverage-governance.md`
  - `RFC-0067-centralized-api-vocabulary-inventory-and-openapi-documentation-governance.md`
  - `RFC-0070-gold-standard-product-experience-foundation-and-ownership-model.md`
  - `RFC-0075-canonical-front-office-portfolio-seed-and-demo-validation-system.md`
  - `RFC-0076-canonical-front-office-demo-data-contract.md`
  - `RFC-0078-modular-front-office-validation-framework.md`
  - `RFC-0079-gateway-evidence-and-lineage-contract.md`

## Summary

RFC-0075 introduced panel classification in the live Workbench validator. RFC-0076 then governed the
canonical front-office dataset and contract provenance. The next hardening step is to govern the UI
surface itself.

Lotus should maintain a machine-readable Workbench panel registry and evidence contract that defines
every governed panel and sub-panel, the owning service, the gateway contract, the allowed states,
the ready/partial/empty/unavailable acceptance rules, and the evidence required before a panel can
be treated as supported.

This registry should become the single metadata source for front-office panel validation. It should
prevent unsupported blank panels, reduce hardcoded browser-validation drift, and make product-surface
truth explicit for engineers, QA, and coding agents.

## Problem

Workbench panel behavior can drift when panel ownership and validation rules exist only in code,
screenshots, or engineer memory.

Current risks:

1. new panels can be added without explicit backend or gateway ownership,
2. supported panels can become blank without a governed failure posture,
3. partial and unavailable states can be handled inconsistently across screens,
4. screenshot automation can miss newly added panels or sub-panels,
5. validation logic can become duplicated and page-local instead of governed,
6. agents can misclassify whether a panel is supported, intentionally empty, partial, unavailable,
   or outside the current product contract,
7. evidence and methodology links can drift away from the actual UI surface.

In a private-banking product, every panel must have a clear decision purpose, a truthful state
model, and a defensible evidence trail.

## Decision

Lotus will create a platform-owned, machine-readable Workbench panel registry and evidence contract.

The registry will govern:

1. panel identity,
2. route and screen ownership,
3. upstream service ownership,
4. gateway endpoint mapping,
5. canonical dataset dependency,
6. allowed state model,
7. validation rules,
8. screenshot evidence policy,
9. methodology and limitation references,
10. supported-versus-partial acceptance posture.

Workbench validation will consume this registry as the metadata authority for panel validation.
Browser automation will remain explicit where interaction logic is required, but panel ownership and
acceptance rules must no longer live only as scattered hardcoded assumptions.

## Goals

1. Define a canonical registry for governed Workbench panels and sub-panels.
2. Make owner, route, endpoint, and state model explicit for every governed panel.
3. Ensure supported blank panels fail validation.
4. Ensure partial, empty, unavailable, and out-of-scope states are explicit and auditable.
5. Define screenshot and evidence requirements per panel.
6. Link panel supportability to the RFC-0076 canonical front-office contract where applicable.
7. Reduce duplicated panel metadata in validation scripts and runbooks.
8. Improve agent understanding of panel supportability and ownership.

## Non-Goals

1. Implementing every currently unsupported panel.
2. Replacing frontend component tests.
3. Replacing gateway contract tests.
4. Making screenshots the primary validation mechanism.
5. Allowing UI-only placeholder content to satisfy supportability requirements.
6. Moving browser interaction logic into a purely declarative registry when explicit scripted flow is
   still clearer and safer.

## Scope

The initial governed scope is the canonical Workbench front-office surface validated through the
RFC-0075 runtime and the RFC-0076 dataset.

Initial screens:

1. portfolio,
2. performance summary,
3. performance analysis,
4. performance advisor brief,
5. performance risk,
6. performance evidence.

The registry must support future expansion beyond these screens, but implementation should begin with
the already-governed front-office surface.

## Proposed Registry Artifacts

Platform-owned artifacts:

```text
context/contracts/workbench-panel-registry.json
context/contracts/workbench-panel-registry.schema.json
```

The schema should validate structure, uniqueness, required fields, and state-enum correctness.
The registry document should contain the current governed panel inventory.

## Registry Model

Each registry entry should contain, at minimum:

1. `panel_id`
2. `display_name`
3. `screen_id`
4. `route`
5. `panel_kind`
6. `panel_level`
7. `parent_panel_id`
8. `owning_service`
9. `gateway_endpoint`
10. `canonical_data_contract`
11. `required_support_state`
12. `allowed_states`
13. `validation_rules`
14. `screenshot_policy`
15. `evidence_required`
16. `methodology_reference`
17. `known_limitations`
18. `out_of_scope_reason`
19. `owner_follow_up_rfc`

### Example model

```json
{
  "panel_id": "performance.risk.rolling",
  "display_name": "Rolling Risk",
  "screen_id": "performance.risk",
  "route": "/performance?mode=risk",
  "panel_kind": "analytic_panel",
  "panel_level": "panel",
  "parent_panel_id": null,
  "owning_service": "lotus-risk",
  "gateway_endpoint": "/api/v1/workbench/{portfolio_id}/risk/rolling",
  "canonical_data_contract": "canonical-front-office-demo-data-contract",
  "required_support_state": "ready",
  "allowed_states": ["ready", "partial", "unavailable", "error"],
  "validation_rules": {
    "ready": ["window_count_emitted == 4", "computable_windows >= 2"],
    "partial": ["owner_reason_required == true"],
    "unavailable": ["owner_reason_required == true"]
  },
  "screenshot_policy": {
    "capture_required": true,
    "screenshot_name": "performance-risk-live.png"
  },
  "evidence_required": true,
  "methodology_reference": "lotus-risk/docs/methodology/rolling-risk.md",
  "known_limitations": [],
  "out_of_scope_reason": null,
  "owner_follow_up_rfc": null
}
```

## Initial Panel Inventory

The first governed registry should include at least:

1. `portfolio.summary`
2. `portfolio.detailed`
3. `performance.summary`
4. `performance.analysis.contribution`
5. `performance.analysis.attribution`
6. `performance.advisor_brief`
7. `performance.risk.snapshot`
8. `performance.risk.drawdown`
9. `performance.risk.concentration`
10. `performance.risk.rolling`
11. `performance.risk.historical_attribution`
12. `performance.evidence`

Where sub-panels exist, the registry should represent both panel-level and screen-level ownership so
coverage is explicit rather than implied.

## State Model

Allowed states:

1. `ready`
2. `loading`
3. `empty`
4. `partial`
5. `unavailable`
6. `error`
7. `out_of_scope`

Explicitly disallowed for governed supported panels:

1. `supported_blank`

Rules:

1. `ready` means the panel is supported and populated according to its validation rules,
2. `empty` means the panel is supported and the empty state is expected, designed, and validated,
3. `partial` means the panel is partially supported, with explicit owner and reason,
4. `unavailable` means the panel is intentionally not available for the current route, capability,
   or product posture, with explicit owner and reason,
5. `out_of_scope` means the panel is not part of the current governed front-office contract,
6. a blank supported panel without an explicit governed state is a validation failure.

## Ownership and Boundary Rules

1. `lotus-platform` owns the registry schema, validation tooling contract, and cross-repo governance.
2. `lotus-workbench` owns UI rendering and registry-consumer integration for browser validation.
3. `lotus-gateway` owns truthful endpoint composition and supportability exposure.
4. Domain services own whether the necessary data can support a `ready` state.
5. No team may treat a panel as supported if the registry does not define owner, endpoint, and state
   policy.

## Implementation Slices

### Slice 1: Registry Specification and Testable Contract

1. Add `workbench-panel-registry.schema.json`.
2. Add `workbench-panel-registry.json` with the initial governed panel inventory.
3. Link registry entries to RFC-0075 and RFC-0076 where appropriate.
4. Add platform tests validating:
   - unique `panel_id`,
   - required fields,
   - valid state enums,
   - screenshot-policy completeness,
   - explicit treatment of `performance.evidence`.
5. Add implementation checklist and slice evidence.
6. Review the artifact design for over-modeling before moving on.

### Slice 2: Workbench Validator Adoption

1. Update `lotus-workbench` live validation to consume registry metadata.
2. Replace hardcoded panel metadata with registry-driven metadata where that improves clarity.
3. Keep interaction steps explicit where browser navigation still needs imperative logic.
4. Add high-value tests proving the registry drives:
   - panel classification,
   - screenshot naming,
   - unsupported blank failure behavior.
5. Remove any dead duplicated metadata made obsolete by the registry.
6. Review the resulting validator for readability and maintainability before moving on.

### Slice 3: Gateway and Panel Supportability Alignment

1. Ensure registry endpoint references match gateway routes.
2. Ensure registry ownership and support-state expectations align with actual gateway behavior.
3. Record intentionally partial or unavailable panels with explicit owner and rationale.
4. Fail validation when registry supportability and runtime supportability diverge.
5. Add evidence documenting any panel that remains partial and why.
6. Review for simplification opportunities and stale assumptions before moving on.

### Slice 4: Documentation, Agent Context, Skill Alignment, and Branch Hygiene

1. Update runbooks and onboarding only where the registry materially improves routing or clarity.
2. Update central context if the registry should be part of the default front-office validation path.
3. Review skills and decide consciously whether registry-awareness belongs in:
   - `lotus-qa-platform-validator`,
   - `lotus-frontend-delivery-governance`,
   - another skill,
   - or no skill change at all.
4. Add the rule that new governed panels must update the registry before work is considered complete.
5. Remove stale guidance that leaves panel supportability implicit.
6. Complete PR evidence hygiene and branch hygiene before closure.

## Acceptance Criteria

1. A machine-readable panel registry and schema exist.
2. Every governed panel has owner, route, endpoint, state policy, and screenshot policy.
3. Workbench live validation consumes the registry for panel metadata and supportability.
4. Supported blank panels fail validation.
5. partial and unavailable panels include owner and rationale.
6. new governed panel work requires registry updates.
7. The registry is referenced by the final context and runbook guidance only where it materially
   improves future work.

## Risks and Mitigations

1. Risk: the registry becomes stale.
   Mitigation: schema tests and validator checks fail when governed panels or panel IDs drift.

2. Risk: registry design becomes too abstract and unreadable.
   Mitigation: keep browser flow explicit and use the registry only for durable metadata and
   acceptance rules.

3. Risk: partial states become permanent.
   Mitigation: require explicit owner, reason, and follow-up RFC or backlog reference for material
   partial states.

4. Risk: the registry duplicates gateway truth.
   Mitigation: the registry owns supportability metadata and evidence posture, not domain
   calculations or raw data contracts.

## Skills, Context, and Documentation Implications

Potential updates during the final slice:

1. add the registry path to front-office validation guidance if implementation makes it an operator
   concern,
2. update only the skills that materially benefit from registry awareness,
3. avoid duplicating registry content into multiple docs,
4. document any conscious no-change decision for skills or context.

## Approval Request

Approval is requested to establish a governed Workbench panel registry and evidence contract as the
primary mechanism for preventing panel drift and making front-office supportability explicit.
