# RFC-0041 Platform Integration Architecture Bible Governance

- Status: Accepted
- Date: 2026-02-23
- Owners: Platform Architecture
- Scope: lotus-core, lotus-performance, lotus-manage, lotus-gateway, cross-service platform governance
- Depends On:
  - `RFC-0015-domain-boundaries-and-service-ownership.md`
  - `RFC-0016-standardization-principles-and-engineering-baseline.md`
  - `RFC-0024-pas-pa-dpm-integration-and-boundary-model.md`
  - `RFC-0025-backend-driven-configurability-entitlements-and-workflow-control.md`
  - `RFC-0026-synchronous-vs-asynchronous-integration-patterns.md`
  - `RFC-0028-ui-bff-integration-model-and-responsibility-rules.md`
  - `RFC-0030-adr-governance-and-decision-traceability.md`

## 1. Summary

Adopt `docs/architecture/Platform Integration Architecture Bible.md` as the central guiding principle for platform-wide architecture and integration decisions.

## 2. Decision

1. Cross-cutting architecture and multi-service alignment documents are maintained in `lotus-platform`.
2. Service implementation RFCs remain in their respective service repositories.
3. Any cross-service divergence requires central RFC/ADR updates and explicit disposition (`intentional`, `temporary`, `refactor-required`).

## 3. Rationale

1. Keeps platform governance decoupled from any single service codebase.
2. Improves ownership clarity between platform-level and service-level decisions.
3. Reduces ambiguity during lotus-core/lotus-performance/lotus-manage/lotus-gateway parallel evolution.

## 4. Expected Outcomes

1. One authoritative source for platform architecture standards.
2. Cleaner service repositories focused on implementation details.
3. Better traceability for multi-service integration decisions.
4. Documentation and implementation stay synchronized through same-cycle update discipline.

