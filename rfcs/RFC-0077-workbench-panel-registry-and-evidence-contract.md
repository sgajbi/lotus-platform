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

## Summary

RFC-0075 introduced panel classification in the live Workbench validator. This RFC proposes turning
that classification into a governed Workbench panel registry and evidence contract.

The registry will define every Workbench panel and sub-panel, its owning service, gateway endpoint,
expected data state, validation rule, screenshot name, allowed degraded states, and evidence
requirements.

## Problem

Workbench panels can drift when each screen is implemented independently:

1. UI panels can be added without backend ownership,
2. panels can become blank without failing validation,
3. screenshot automation can miss new panels,
4. partial states can be treated inconsistently,
5. validation logic can become hardcoded and duplicated,
6. agents can misunderstand whether a panel is supported, intentionally empty, partial, unavailable,
   or out of scope.

This creates product trust risk. Private-banking users need every panel to have a clear decision
purpose and a reliable evidence trail.

## Goals

1. Define a canonical Workbench panel registry.
2. Make panel ownership explicit.
3. Define the required backend/gateway contract for each panel.
4. Define allowed panel states.
5. Define validation rules for ready, empty, partial, unavailable, loading, and error states.
6. Define screenshot names and capture routes.
7. Ensure validation fails when a supported panel is blank.
8. Ensure partial or unavailable states have explicit owner and rationale.
9. Make the registry consumable by automation.
10. Reduce hardcoded panel expectations in browser validation.

## Non-Goals

1. Implementing every unsupported panel.
2. Replacing frontend component tests.
3. Replacing gateway contract tests.
4. Making screenshots the primary validation mechanism.
5. Allowing UI-only fake content to satisfy registry requirements.

## Proposed Registry

The registry should be machine-readable and platform-owned, with repo-local interpretation where
needed.

Proposed location:

```text
context/contracts/workbench-panel-registry.json
```

Proposed panel fields:

1. `panel_id`
2. `display_name`
3. `route`
4. `screen`
5. `owning_service`
6. `gateway_endpoint`
7. `required_seed_contract`
8. `state`
9. `allowed_states`
10. `ready_validation`
11. `empty_validation`
12. `partial_validation`
13. `unavailable_validation`
14. `screenshot_name`
15. `evidence_required`
16. `methodology_reference`
17. `known_limitations`

## Initial Panel Scope

Initial registry coverage should include:

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

## Allowed Panel States

Allowed states:

1. `ready`
2. `loading`
3. `empty`
4. `partial`
5. `unavailable`
6. `error`
7. `out_of_scope`

Disallowed state:

1. `supported_blank`

Any supported blank panel must fail validation.

## Proposed Implementation

### Slice 1: Registry Specification

1. Add the registry schema and first registry document.
2. Link registry entries to RFC-0075 and RFC-0076.
3. Add platform tests to validate registry shape and unique panel IDs.

### Slice 2: Workbench Validator Adoption

1. Update Workbench live validation to consume the registry.
2. Replace hardcoded panel metadata with registry-driven metadata where practical.
3. Keep route interactions explicit when browser behavior requires it.

### Slice 3: Gateway and Backend Contract Alignment

1. Ensure registry endpoint references match gateway routes.
2. Ensure owning services expose enough data for ready panels.
3. Record partial/unavailable panels with owner and acceptance rule.

### Slice 4: Documentation, Agent Context, Skill Alignment, and Branch Hygiene

1. update the Workbench runbook and panel-governance documentation,
2. update agent ramp-up and engineering-context guidance where the registry should be referenced,
3. review relevant skills to decide whether registry awareness belongs in skill routing or linked
   docs,
4. add the rule that new panels must update the registry before implementation is considered
   complete,
5. complete branch hygiene, PR evidence hygiene, and cross-repo reference cleanup before closure.

## Acceptance Criteria

1. Workbench has a governed panel registry.
2. Every registered panel has owner, route, endpoint, state policy, and screenshot policy.
3. Live validation consumes the registry.
4. Supported blank panels fail validation.
5. Partial and unavailable panels include owner and rationale.
6. New panel work has a clear registry-update requirement.

## Risks and Mitigations

1. Risk: the registry becomes stale.
   Mitigation: validation fails when code references panels not present in the registry.

2. Risk: registry-driven validation becomes too abstract.
   Mitigation: keep browser behavior explicit while registry owns metadata and acceptance rules.

3. Risk: partial states become permanent.
   Mitigation: require owner, reason, and follow-up capability RFC for material partial states.

## Approval Request

Approval is requested to create a governed Workbench panel registry and evidence contract as the
primary mechanism for preventing UI panel drift.
