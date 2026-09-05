# Source Boundary And Recovery Patterns

Use this reference when a backend slice touches lifecycle events, tenant-aware source adapters,
shared API dependencies, upstream mutation retries, source success admission, dead-letter
recovery, queue redrive, audit lineage, replay, or recovery operator controls.

## Contents

1. Typed lifecycle and audit payloads
2. Tenant-aware downstream source adapters
3. Shared dependency problem-details preservation
4. Ambiguous-loss retry and replay identity
5. Source-response semantic admission
6. Dead-letter inspection and redrive
7. Governed replay-evidence authority
8. Database disaster-recovery certification

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

## Ambiguous-Loss Retry And Replay Identity

When a consumer retries an upstream mutation, classify transport failures by whether the request
may already have reached the producer. Connection-establishment failures (connect errors, connect
and pool timeouts) never delivered the request and may retry. Read/write failures, remote-protocol
errors, and read/write timeouts are ambiguous response losses: the producer may have committed, so
an automatic retry re-executes an operation whose outcome is unknown. Retry an ambiguous loss only
when the producer publishes a replay-identity contract and the consumer sends one identity, minted
once per logical operation and reused verbatim across attempts; a correlation or trace id is
tracing, never replay identity, and a fresh key per attempt defeats the contract. For a mutation
with no replay identity, stop after an ambiguous loss and surface the indeterminate outcome
truthfully. Such a mutation must also not follow redirects: a redirect re-delivers the request,
and a failed redirect target masquerades as a pre-send connection error. Do not indiscriminately
ban read-only retries, and record the residual seam when the consumer's own caller can retry the
whole request without a stable inbound identity. Prove with tests: ambiguous loss then identical
replay body, one producer execution, no second attempt without identity, and pre-send failures
still retrying.

## Source-Response Semantic Admission

A well-shaped upstream success is not yet an answer to the requested operation. Before publishing,
bind the response to the identities the source contract actually exposes: the requested resource
id, per-row identities inside collections (an event or lineage row for another owner must not ride
in on a correct envelope), the echoed submission idempotency key, and internal relationships such
as a handle naming the same resource as its status link (comparing URL segments decoded). Refuse a
mismatch as a declared bounded upstream-contract failure that names only the mismatched field
names, never raw identifiers; map a malformed success to the same declared failure family instead
of letting a validation exception escape as an internal error. Keep one admission owner per source
family with small operation-specific checks; do not invent identifiers the contract does not
expose or rewrite source semantics, and verify every echoed shape against the producer's shipped
code rather than sibling patterns. Test one refusal per operation family plus per-row refusal
under a correct envelope.

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

## Governed Replay-Evidence Authority

When ingestion, retry, dead-letter, or operator-support work retains request evidence, define one
versioned policy per endpoint or domain family. The policy must declare durable representation
(`source_safe_payload`, `fingerprint_only`, `redacted`, or `none`), full- and partial-replay
eligibility, technical expiry, retention authority, and source availability. A payload fingerprint,
idempotency identifier, failed-record key, correlation reference, or diagnostic row proves only the
identity or observation it was designed to prove. None independently authorizes replay, proves that
payload bytes remain available, or permits reconstructing a request from downstream state.

Load replay context through a typed port and evaluate the policy in the domain layer. Re-evaluate
temporal and replay authority at the final action boundary after awaited permission, mode, lease,
or duplicate checks and immediately before dry-run success or publication. Fail closed with stable,
source-safe reasons when evidence is absent, expired, unavailable, restricted, non-replayable, or
partial replay is not explicitly authorized. Never turn a fingerprint-only family into a replayable
one by retaining identifiers in a status response, audit event, or test fake.

Keep API and operator contract truth aligned with the same policy. Positive OpenAPI examples,
retry tests, and dead-letter recovery fixtures must use a family whose source-safe payload is
durably available and whose policy authorizes the demonstrated replay shape. Restricted or
fingerprint-only examples must expose no replayable keys and must not fabricate payload authority.
Prove identical-input fingerprint stability, changed-input mismatch, raw-sensitive-value absence,
full/partial authorization, exact expiry, check-then-wait expiry races, restart/reload behavior, and
OpenAPI example parity. Preserve diagnostic identity separately from execution authority.

## Database Disaster-Recovery Certification

Do not treat migration rollback, repository replay, queue re-drive, synthetic smoke, or a logical
dump as production database disaster-recovery certification. Define a versioned service-owned
recovery contract that names RPO/RTO, protected tables, backup/PITR strategy, retention and
legal-hold boundary, residency, encryption/access controls, ownership, escalation, cadence, and
remaining approval blockers.

Keep provider backup infrastructure outside the service while implementing a read-only
restored-database validator behind a port, a real clean-target restore drill, source-safe
counts/hashes and invariant evidence, and a post-restore resume proof for idempotency, leases,
outbox/downstream non-duplication, and lineage. Measure readiness after validation rather than
accepting a caller-declared ready time; distinguish logical restore evidence from physical
base-backup plus WAL/PITR evidence.

Block readiness and every durable write while posture is draining, restoring, degraded, or
invalid, and require an authorized cutover/rollback runbook. Exercise catalog queries, constraints,
indexes, relationships, state invariants, and resume behavior against the real database. Scheduled
attested evidence may support the claim, but production certification remains blocked until an
approved provider topology and a real PITR/failover exercise exist.
