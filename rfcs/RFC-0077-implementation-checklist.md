# RFC-0077 Implementation Checklist

- RFC: `RFC-0077-workbench-panel-registry-and-evidence-contract.md`
- Status: In Progress
- Last updated: 2026-04-11

## Approval Gate

- [x] RFC reviewed and tightened before slice implementation.
- [x] Slice 1 scope constrained to registry artifacts, checklist, evidence, and platform tests.
- [ ] RFC approved for Slice 2 implementation.

## Slice 1: Registry Specification and Testable Contract

- [x] Add `context/contracts/workbench-panel-registry.schema.json`.
- [x] Add `context/contracts/workbench-panel-registry.json`.
- [x] Link registry metadata to RFC-0075 and RFC-0076 where appropriate.
- [x] Define the initial governed panel inventory.
- [x] Define the allowed state model and disallow implicit supported blank posture.
- [x] Record explicit treatment of `performance.evidence`.
- [x] Update contract-directory documentation.
- [x] Add platform tests validating schema and registry expectations.
- [x] Add slice evidence documenting the artifact design and review outcome.
- [x] Review slice output for over-modeling before moving on.

## Slice 2: Workbench Validator Adoption

- [ ] Update Workbench live validation to consume registry metadata.
- [ ] Replace duplicated hardcoded panel metadata where the registry improves clarity.
- [ ] Keep browser interaction steps explicit where imperative logic is still safer.
- [ ] Add high-value tests for panel classification, screenshot naming, and unsupported blank failure behavior.
- [ ] Remove dead duplicated metadata made obsolete by the registry.
- [ ] Review validator readability and maintainability before moving on.

## Slice 3: Gateway and Panel Supportability Alignment

- [ ] Align registry endpoint references with actual gateway routes.
- [ ] Align registry support-state expectations with actual runtime behavior.
- [ ] Record intentionally partial or unavailable panels with explicit owner and rationale.
- [ ] Fail validation when registry supportability and runtime supportability diverge.
- [ ] Add slice evidence for remaining partial or unavailable panels.
- [ ] Review for simplification opportunities and stale assumptions before moving on.

## Slice 4: Documentation, Agent Context, Skill Alignment, and Branch Hygiene

- [ ] Update docs and onboarding only where the registry materially improves routing or clarity.
- [ ] Review relevant skills and record whether registry-awareness is required.
- [ ] Remove stale guidance that leaves panel supportability implicit.
- [ ] Document conscious no-change decisions for skills and context.
- [ ] Complete PR evidence hygiene and branch hygiene before closure.

## Final Acceptance

- [ ] Registry schema and registry document are versioned, governed, and machine-readable.
- [ ] Initial governed panel inventory is explicit and test-backed.
- [ ] Workbench validation consumes the registry without duplicated stale metadata.
- [ ] Meaningful tests exist for registry drift and slice evidence.
- [ ] CI evidence is truthful.
