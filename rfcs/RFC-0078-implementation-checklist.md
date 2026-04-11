# RFC-0078 Implementation Checklist

- RFC: `RFC-0078-modular-front-office-validation-framework.md`
- Status: In Progress
- Last updated: 2026-04-11

## Approval Gate

- [x] RFC reviewed and tightened before slice implementation.
- [x] Slice 1 scope constrained to shared contract/config/evidence module extraction.
- [x] Operator-facing commands remain stable during slice execution.
- [ ] RFC approved for Slice 2 implementation.

## Slice 1: Extract Core Validation Types and Result Models

- [x] Extract shared validation config parsing into a dedicated module.
- [x] Extract governed contract and panel registry metadata loading into a dedicated module.
- [x] Extract validation summary and screenshot index writers into a dedicated module.
- [x] Remove duplicated bootstrap helpers from `validate-canonical-workbench-live.mjs`.
- [x] Keep operator entrypoints and browser validation semantics unchanged.
- [x] Add meaningful module-level tests for shared validation helpers.
- [x] Record slice evidence documenting dead code removal and retained boundaries.
- [x] Review slice output for simplification opportunities before moving on.

## Slice 2: Extract API Probing and Gateway Assertions

- [x] Move HTTP and DNS probing into dedicated validation modules.
- [x] Preserve source-owned error messages and timeout behavior.
- [x] Add focused tests for probe result handling and gateway failure classification.
- [x] Remove obsolete fetch-helper duplication from the monolithic validator.
- [x] Review slice output for simplification opportunities before moving on.

## Slice 3: Extract Calculation Sanity Modules

- [ ] Split performance and risk calculation sanity checks into dedicated modules.
- [ ] Keep reconciliation and range assertions explicit and readable.
- [ ] Add focused tests for meaningful failure modes, not just happy paths.
- [ ] Remove dead code or overlapping helpers revealed by the extraction.

## Slice 4: Extract Browser Workflow and Screenshot Capture

- [ ] Isolate Playwright navigation and screenshot capture into reusable modules.
- [ ] Keep screenshot naming governed by the RFC-0077 panel registry.
- [ ] Preserve truthful ready/partial/unavailable evidence semantics.
- [ ] Remove page-local duplication once the shared browser workflow is stable.

## Slice 5: Registry-Driven Panel Classification

- [ ] Move panel classification and supportability alignment into dedicated modules.
- [ ] Keep registry ownership, required states, and follow-up RFC checks enforced.
- [ ] Add focused tests for unsupported blank panels and owner/state drift.
- [ ] Remove stale classification logic from the monolithic validator.

## Slice 6: Documentation, Agent Context, Skill Alignment, and Branch Hygiene

- [ ] Update docs only where the modular framework materially changes implementation routing.
- [ ] Review relevant skills and record whether guidance should be added, tightened, or left unchanged.
- [ ] Remove stale guidance that points future agents toward the monolithic validator shape.
- [ ] Complete PR evidence hygiene and branch hygiene before closure.

## Final Acceptance

- [ ] The live validator is decomposed into clear modules with stable operator commands.
- [ ] Shared validation behavior is test-backed and does not depend on hidden monolithic state.
- [ ] Dead code introduced by extraction work is removed, not relocated.
- [ ] CI evidence is truthful.
