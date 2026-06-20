# Scalability and Availability Standard

- Version: 1.0.0
- Status: Active
- Scope: lotus-core, lotus-performance, lotus-manage, lotus-report, lotus-gateway (lotus-gateway), lotus-workbench integration surface
- Change control: Any change to mandatory rules requires an RFC in `lotus-platform/rfcs`.

## A. Do Now (Pre-Launch Must-Haves)

1. Stateless service baseline
- No business-critical in-memory state tied to a single process.
- State must be externalized to DB/cache/object store/queue.

2. Resilient service communication
- Every inter-service call must define explicit timeout.
- Retries must be bounded with exponential backoff.
- No silent or infinite retries.
- Services must expose `health`, `health/live`, and `health/ready`.

3. API performance hygiene
- Collection endpoints require pagination/filtering/sorting guardrails.
- Responses must enforce max limits for payload size.
- Critical endpoint latency targets must be documented per repo.

4. Workload isolation
- Heavy analytics/batch workloads must be async and isolated from sync request paths.

5. Database scalability fundamentals
- Critical queries must have index/query-plan review evidence.
- Growth assumptions and retention/archival policy must exist.

6. Caching policy baseline
- Cache usage must be explicit, owned, and documented with TTL/invalidation policy.

7. Observability for scaling
- Required metrics: latency, throughput, error rate, CPU/memory, DB performance, queue depth.

8. Availability baseline
- Internal SLO targets, plus RTO/RPO assumptions, must be defined.
- Backup/restore runbook and minimal restore validation required.

9. Load and concurrency validation
- Critical workflows require load/concurrency tests and regression guard in CI where feasible.

## B. Phase Next (Before First Client Go-Live)

1. Circuit breaker/bulkhead patterns with graceful degradation policy.
2. Capacity models by portfolio tier (S/M/L) and workload profile.
3. HA deployment patterns for SaaS and single-tenant.
4. Disaster-recovery drill schedule with restore verification evidence.

## C. Phase Later (Scale Hardening)

1. Advanced autoscaling and predictive capacity planning.
2. Multi-region failover strategy where required.
3. Formal SLO/error-budget program.
4. Tenant-aware scaling and noisy-neighbor controls.

## D. Per-Repo Plan

- `lotus-gateway`: resilient upstream clients (lotus-core/lotus-performance/lotus-manage/lotus-report), pagination guardrails, concurrency tests, SLO notes.
- `lotus-performance`: lotus-core input resilience, async-heavy workloads isolated, load tests for analytics APIs.
- `lotus-report`: lotus-core/lotus-performance resilient ingestion, aggregation path performance budgets, report-path concurrency tests.
- `lotus-core`: enforce stateless query APIs, index and retention documentation, queue depth observability.
- `lotus-advise`: async batch isolation, bounded retries for dependencies, policy-based degradation behavior.
- `lotus-platform`: central policy, compliance matrix, validation automation and evidence artifacts.

## E. Definition of Done + Evidence

Done requires all of the following:
- Central standard merged in PPD and referenced by backend repos.
- Repo-level implementation merged for all Do Now controls marked Partial/Missing.
- Compliance matrix generated with status per requirement and evidence links.
- CI/test artifacts prove resilience, concurrency, and observability baselines.

Required evidence artifacts:
- `output/scalability-availability-compliance.json`
- `output/scalability-availability-compliance.md`
- per-repo `docs/standards/scalability-availability.md`

## Non-Negotiable Rules

1. No single-instance assumptions in business-critical flows.
2. No silent or infinite retries.
3. Scaling/availability claims must map to metrics/tests.
4. Deviations require ADR with remediation timeline.


