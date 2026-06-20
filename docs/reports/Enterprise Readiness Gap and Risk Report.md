# Enterprise Readiness Gap and Risk Report

Status source: `output/enterprise-readiness-compliance.md`.

## A. Do Now (Pre-Launch Must-Haves)

This wave implements a platform-consistent baseline for:
- security/IAM hooks and privileged action audit logging
- API governance and contract-first validation evidence
- config + tenant/role feature management baseline
- data-quality and reconciliation policy alignment
- reliability/operations standards linkage
- privacy/compliance redaction and audit requirements

Current Do-Now status is derived from evidence matrix output.

## B. Phase Next (Before First Client Go-Live)

- Fine-grained entitlement enforcement and tenant-isolation hardening.
- SLI/SLO thresholds for critical business workflows.
- Performance profile benchmarks (small/medium/large portfolios).
- Residency/retention/legal-hold implementation details.

## C. Phase Later (Scale/Enterprise Hardening)

- Deployment portability patterns for enterprise environments.
- Bulkhead/circuit-breaker/degradation architecture.
- Tamper-evident audit evidence packaging.
- Extensibility framework hardening for providers/connectors.

## D. Per-Repo Plan

| Repo | Next Focus | Effort |
|---|---|---|
| lotus-gateway | entitlement + data-scope policy enforcement | M |
| lotus-core | ingest quarantine + reconciliation automation hardening | M |
| lotus-performance | entitlement-aware analytics access and SLI enforcement | M |
| lotus-advise | capability-to-workflow enforcement and conflict audit enhancements | M |
| lotus-report | report/export entitlements and workload SLO evidence | M |

## E. Definition of Done + Evidence

Completion criteria for this standard:
- Do-Now requirements are `Implemented` for all backend repos in matrix artifacts.
- Code, tests, docs, and automation evidence all exist (no docs-only closure).
- Cross-repo consistency is validated through PPD automation.

Evidence artifacts:
- `docs/standards/Enterprise Readiness Standard.md`
- `output/enterprise-readiness-compliance.json`
- `output/enterprise-readiness-compliance.md`
- per-repo `docs/standards/enterprise-readiness.md`

