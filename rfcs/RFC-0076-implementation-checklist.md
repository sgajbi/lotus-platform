# RFC-0076 Implementation Checklist

- RFC: `RFC-0076-canonical-front-office-demo-data-contract.md`
- Status: In Progress
- Last updated: 2026-04-11

## Approval Gate

- [x] RFC reviewed and tightened before slice implementation.
- [x] Canonical portfolio ID confirmed as `PB_SG_GLOBAL_BAL_001`.
- [x] Canonical benchmark ID confirmed as `BMK_PB_GLOBAL_BALANCED_60_40`.
- [x] Canonical as-of date confirmed as `2026-04-10`.
- [x] Slice 1 scope constrained to contract artifacts, checklist, and platform tests.
- [ ] RFC approved for Slice 2 implementation.

## Slice 1: Contract Document and Machine-Readable Spec

- [x] Add governed contract artifact directory under `context/contracts`.
- [x] Add machine-readable canonical demo data contract.
- [x] Add machine-readable canonical demo invariants contract.
- [x] Record contract version, governed date, and RFC ownership metadata.
- [x] Record canonical portfolio identity and benchmark identity.
- [x] Record required asset, transaction, reference-data, and derived-state coverage.
- [x] Record repository ownership model.
- [x] Add platform tests that validate contract presence and required fields.
- [x] Add slice evidence documenting what was introduced and why.
- [x] Review slice output for simplification opportunities before moving on.

## Slice 2: Core Seed Contract Enforcement

- [ ] Update `lotus-core` seed tooling to read or mirror the governed contract.
- [ ] Enforce required coverage and deterministic economics in code.
- [ ] Add focused tests for economic invariants and stale coverage failure modes.

## Slice 3: Derived-State Readiness Enforcement

- [ ] Enforce governed readiness semantics against the canonical contract.
- [ ] Surface contract-aware stale state diagnostics.
- [ ] Add tests proving readiness drift is caught before UI validation.

## Slice 4: Cross-App Contract Adoption

- [ ] Update validators and downstream summaries to surface contract identity or version.
- [ ] Align gateway and Workbench expectations with the contract.
- [ ] Document any intentionally partial surfaces that remain outside the current contract.

## Slice 5: Documentation, Agent Context, Skill Alignment, and Branch Hygiene

- [ ] Update docs and onboarding only where the contract materially improves routing or clarity.
- [ ] Review relevant skills and record whether explicit contract references are required.
- [ ] Remove stale guidance that encourages ad hoc smoke portfolio usage where inappropriate.
- [ ] Document any conscious `no change required` decisions for skills and context.
- [ ] Complete PR evidence hygiene and branch hygiene before closure.

## Final Acceptance

- [ ] Canonical contract artifacts are versioned, governed, and machine-readable.
- [ ] Downstream implementation slices adopt the contract without duplicating stale assumptions.
- [ ] Meaningful tests exist for contract drift and slice evidence.
- [ ] CI evidence is truthful.
