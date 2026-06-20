# Enterprise Readiness Standard

- Version: 1.0.0
- Status: Active
- Scope: lotus-core, lotus-performance, lotus-manage, lotus-report, lotus-gateway/lotus-gateway, and shared cross-cutting standards in PPD
- Change control: Changes to mandatory controls require RFC in `lotus-platform/rfcs`; temporary deviations require ADR with expiry review date.

## A. Do Now (Pre-Launch Must-Haves)

1. Security and IAM baseline
- Standard authn/authz integration hooks are mandatory at service boundaries.
- Service identity and secret handling must follow central platform standards.
- Privileged and critical actions must produce structured audit events with actor/tenant/role/correlation context.

2. API governance baseline
- APIs must publish contract-first OpenAPI with explicit version metadata.
- Versioning/deprecation and backward-compatibility rules must be documented and enforced through tests.
- Contract validation is a CI gate.

3. Configuration and feature management baseline
- Config must be schema-driven with safe defaults and rollback discipline.
- Feature flags must support tenant and role scoping.
- Invalid config should fail closed for security-sensitive paths.

4. Data quality and reconciliation baseline
- Ingest and API boundaries require validation checks.
- Bad input handling requires explicit reject/quarantine semantics (service-owned handling path).
- Data-quality signal visibility is required through logs/metrics/tests.

5. Reliability and operations baseline
- Inter-service communication requires explicit timeout + bounded retry behavior.
- Expensive endpoints require rate-limit strategy or guardrails.
- Service runbooks and incident playbooks are mandatory.
- Migration and rollback/change-control rules are mandatory for release.

6. Privacy and compliance foundations
- Data classification for sensitive fields must exist.
- Sensitive fields require masking/redaction in logs and audit payloads.
- Encryption in transit and at rest must be part of service policy.
- Critical paths must emit audit trail fields (`who`, `what`, `when`, `why/context`).

## B. Phase Next (Before First Client Go-Live)

1. Fine-grained entitlements: user -> role -> capability -> data-scope enforcement.
2. Tenant-isolation model and tenant-level config/feature controls.
3. SLO/SLI thresholds per critical workflow with alert baselines.
4. Performance tiers and benchmark profiles (S/M/L portfolios).
5. Residency, retention, and legal-hold implementation where required.

## C. Phase Later (Scale/Enterprise Hardening)

1. Deployment portability patterns (on-prem/private/public cloud).
2. Advanced reliability controls (bulkheads, circuit breakers, graceful degradation).
3. Stronger tamper-evidence and evidence packaging for due diligence.
4. Extensibility framework for adapters/connectors/event-driven optionality.

## D. Per-Repo Implementation Plan

- `lotus-gateway`
  - Enforce write-path audit middleware and redaction.
  - Maintain resilient upstream calls and contract validation.
  - Keep tenant/role feature flag controls for lotus-gateway orchestration.

- `lotus-core`
  - Apply enterprise controls in query-service API surface.
  - Keep schema validation and data-quality checks in core data paths.
  - Maintain migration, runbook, and durability links for operational evidence.

- `lotus-performance`
  - Apply enterprise controls on advanced analytics API surface.
  - Keep contract governance and deterministic config/feature controls.
  - Preserve resilience + observability evidence for critical analytics workflows.

- `lotus-advise`
  - Apply enterprise audit and feature controls in advisory/discretionary APIs.
  - Keep policy and workflow validation evidence for decision-critical actions.
  - Enforce run-supportability and migration governance evidence.

- `lotus-report`
  - Apply enterprise controls to reporting and aggregation API surface.
  - Keep data-quality checks and upstream failure handling explicit.
  - Preserve operational guardrails for report-generation flows.

- `lotus-platform`
  - Own canonical checklist, validator automation, and machine-readable compliance artifacts.

## E. Definition of Done + Evidence

Done requires all of the following:
- Do-Now controls implemented consistently across backend repositories.
- CI gates cover contract/security/config/data-quality checks.
- Per-repo standards docs + tests + code evidence are present.
- Compliance matrix generated with repo/requirement status and blockers.

Required evidence artifacts:
- `output/enterprise-readiness-compliance.json`
- `output/enterprise-readiness-compliance.md`
- per-repo `docs/standards/enterprise-readiness.md`

## Non-Negotiable Rules

1. No repo-specific ad hoc standards that conflict with platform baseline.
2. All deviations require ADR with rationale and expiry/review date.
3. Every requirement must map to testable evidence (code/tests/config/docs/runbooks).

