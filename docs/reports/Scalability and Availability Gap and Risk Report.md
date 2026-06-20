# Scalability and Availability Gap and Risk Report

## A. Do Now (Pre-Launch Must-Haves)

Status source: `output/scalability-availability-compliance.md`.

Completed in this wave:
- Graceful shutdown and drain-safe readiness behavior implemented in lotus-gateway, lotus-performance, and lotus-report.
- Explicit cache policy sections added in lotus-gateway, lotus-core, and lotus-manage scalability standards docs.
- Explicit availability baseline added in lotus-core (SLO, RTO, RPO, backup/restore validation).
- Real load/concurrency tests added for lotus-gateway and lotus-manage health endpoints.
- Scale-signal observability coverage documented with platform-shared evidence links.
- Compliance validator hardened to reduce false positives from generic benchmark/doc matches.

Open gaps from matrix (current):
- None in Do-Now controls (`Implemented` across all backend repos).

## B. Phase Next (Before First Client Go-Live)

- Circuit breakers/bulkheads and graceful-degradation policy.
- Capacity model by portfolio tiers (S/M/L) and workload profiles.
- HA deployment patterns by environment.
- Restore drill execution with measured RTO/RPO evidence.

## C. Phase Later (Scale Hardening)

- Autoscaling policies and predictive capacity planning.
- Multi-region failover strategy where required.
- SLO/error-budget operational program.
- Tenant-aware scaling controls.

## D. Per-Repo Plan

| Repo | Next Action | Effort |
|---|---|---|
| lotus-gateway | Completed Do-Now baseline; next: circuit-breaker/degradation policy and capacity modeling | M |
| lotus-performance | Completed Do-Now baseline; next: HA deployment patterns and DR drill evidence | M |
| lotus-report | Completed Do-Now baseline; next: capacity model and restore drill evidence | M |
| lotus-core | Completed Do-Now baseline; next: bulkhead policy and HA deployment pattern hardening | M |
| lotus-advise | Completed Do-Now baseline; next: async workload capacity model and DR drill execution | M |

## E. Definition of Done + Evidence

Done criteria for this standard:
- Central standard exists and is referenced by backend repos.
- Matrix is regenerated and no `Missing`/`Partial` in Do-Now controls for any backend repo.
- Resilience controls validated by unit/integration tests.

Evidence artifacts:
- `docs/standards/Scalability and Availability Standard.md`
- `output/scalability-availability-compliance.json`
- `output/scalability-availability-compliance.md`
- Repo PRs with code/tests/docs implementing missing controls.

