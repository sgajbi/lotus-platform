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

- [x] Update Workbench live validation to consume registry metadata.
- [x] Replace duplicated hardcoded panel metadata where the registry improves clarity.
- [x] Keep browser interaction steps explicit where imperative logic is still safer.
- [x] Add high-value tests for panel classification, screenshot naming, and unsupported blank failure behavior.
- [x] Remove dead duplicated metadata made obsolete by the registry.
- [x] Review validator readability and maintainability before moving on.

## Slice 3: Gateway and Panel Supportability Alignment

- [x] Align registry endpoint references with actual gateway routes.
- [x] Align registry support-state expectations with actual runtime behavior.
- [x] Record intentionally partial or unavailable panels with explicit owner and rationale.
- [x] Fail validation when registry supportability and runtime supportability diverge.
- [x] Add slice evidence for remaining partial or unavailable panels.
- [x] Review for simplification opportunities and stale assumptions before moving on.

## Slice 4: Documentation, Agent Context, Skill Alignment, and Branch Hygiene

- [x] Update docs and onboarding only where the registry materially improves routing or clarity.
- [x] Review relevant skills and record whether registry-awareness is required.
- [x] Remove stale guidance that leaves panel supportability implicit.
- [x] Document conscious no-change decisions for skills and context.
- [x] Complete PR evidence hygiene and branch hygiene before closure.

## Final Acceptance

- [x] Registry schema and registry document are versioned, governed, and machine-readable.
- [x] Initial governed panel inventory is explicit and test-backed.
- [x] Workbench validation consumes the registry without duplicated stale metadata.
- [x] Meaningful tests exist for registry drift and slice evidence.
- [x] CI evidence is truthful.
