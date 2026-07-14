# Source Boundary And Recovery Patterns

Use this reference when a backend slice touches lifecycle events, tenant-aware source adapters,
shared API dependencies, dead-letter recovery, queue redrive, audit lineage, replay, or recovery
operator controls.

## Contents

1. Typed lifecycle and audit payloads
2. Tenant-aware downstream source adapters
3. Shared dependency problem-details preservation
4. Dead-letter inspection and redrive

## Typed Lifecycle And Audit Payloads

When a backend slice touches lifecycle events, audit logs, replay lineage, recovery, outbox records,
status history, or operator event history, do not encode identifiers or machine state only in
human-readable messages. Define a versioned, support-safe typed payload contract; add schema/read
compatibility for existing rows; ensure replay, regenerate, dedupe, and lineage logic consume typed
fields rather than parsing text; and test accepted, failed, render/archive, retry/replay,
batch-item, and legacy-read cases that match the touched event family.

## Tenant-Aware Downstream Source Adapters

When a source adapter calls a tenant-aware downstream service, carry one resolved tenant from
trusted caller context through the request DTO mapper, application command, port, and adapter.
Reject missing, multiple, or inconsistent tenant context before runtime construction or network
I/O; reject unknown request fields so a body cannot silently pose as scope input, and never use a
hard-coded production tenant fallback. Propagate tenant only where the downstream route publishes a
tenant-aware contract; do not invent query/header fields on non-tenant-aware routes. Retain the
resolved tenant in local access scope, deterministic aggregate identity, persistence/idempotency
identity, and audit lineage wherever those artifacts can otherwise collide across tenants. Apply
the same contract to scheduled or batch workers through explicit governed configuration. Keep raw
tenant identifiers out of logs and metric labels; use a bounded scope-provenance posture when
operations need explanatory evidence. Test tenant A/B outbound payload, candidate identity,
persistence and ingestion isolation plus no-tenant, ambiguous-tenant, untrusted-header, body
override, and non-tenant-aware downstream paths. Add a cross-layer deterministic gate when the
contract is statically enforceable.

## Shared Dependency Problem-Details Preservation

When a shared dependency can reject a request before route code runs, preserve its approved
product-safe error code, title, status, media type, and remediation detail through the global
exception handler. Use a typed boundary exception for governed failures and retain a generic safe
fallback for unrelated framework errors. Test representative routes, correlation headers,
observability category, and absence of raw header/token/scope values; add a deterministic gate when
direct generic exceptions can be detected statically.

## Dead-Letter Inspection And Redrive

Do not treat a dead-letter status or queue as a complete recovery control. Provide a bounded,
operator-authorized, source-safe inspection projection and an explicit re-drive use case through
API/command DTO, application service, domain policy, repository port, and durable adapter. Bind
re-drive to trusted caller provenance, dedicated capability, idempotency key, bounded reason and
change reference, event-family/schema eligibility, a new fenced lease, and append-only audit
evidence that preserves the original retry count, failure reason, and timestamps. Fence concurrent
requests, prove replay/conflict after repository or process restart, cap poison-event recovery,
return rejected attempts to quarantine without automatic infinite retry, and keep payloads,
aggregate/client/portfolio ids, and raw idempotency material out of responses and telemetry.
Resolve opaque support references with an exact durable, indexed selector across the states needed
for truthful conflict reporting; never make older records unreachable through a fixed-size
recent-row scan or lock unrelated rows while searching. Execute the selector, transition,
migration/index, restart, and replay path against the real repository technology; migration
dry-runs and fake adapters are not sufficient database proof. Improve this as an internal bounded
module first; add a separately deployed recovery service only when workload, failure-isolation,
ownership, or operability evidence justifies it.
