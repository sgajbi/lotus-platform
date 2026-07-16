# Stateful Database Migration Proof

Use this reference when a migration changes durable worker status, claim or lease identity,
recovery eligibility, idempotency uniqueness, outbox/replay state, or a partial index over mutable
workflow states. Schema validity alone is not upgrade proof.

## Pre-Upgrade State Matrix

Before editing the migration, inventory every persisted state the previous release can leave behind:

| Required field | Evidence |
| --- | --- |
| Legacy status/state | Every status value and transitional marker present before upgrade. |
| New nullable/default fields | Values legacy rows receive when the column is added. |
| New claim path | Whether the new runtime can claim the legacy row. |
| New recovery path | Whether timeout, restart, or stale recovery can select it. |
| Conflict posture | Partial-unique, foreign-key, check, and idempotency conflicts after transition. |
| Upgrade decision | Preserve, transform, requeue, quarantine, terminalize, or reject deployment. |

Do not assume an existing in-flight row will acquire a new lease, owner, version, or timestamp.
Do not leave a row in a state that the new runtime neither claims nor recovers.

## Migration Ordering

1. Add fields in a form that can represent legacy rows.
2. Atomically transform or quarantine every incompatible legacy state before the old runtime is
   removed or the new runtime becomes authoritative.
3. Resolve duplicate or conflicting pending/in-flight identities before creating partial unique
   indexes or constraints.
4. Preserve the earliest affected scope, latest authoritative lineage, bounded attempt history,
   and supportable failure reason when coalescing work.
5. Create indexes and constraints only after the data transition satisfies them.
6. Make the cutover order explicit when old and new binaries can overlap. If overlap is unsafe,
   require a bounded drain/pause and prove it operationally.

Never relabel completed business work as unprocessed merely to satisfy a new worker protocol.
Requeue only work whose completion is not durably proven; otherwise preserve or terminalize it with
support evidence.

## Required Executable Tests

Seed representative pre-upgrade rows and execute the real migration technology. Prove:

1. every legacy terminal, pending, in-flight, retryable, failed, and special marker state reaches
   an intentional post-upgrade state;
2. null lease/owner identity cannot strand an in-flight row;
3. stale recovery and ordinary claiming can make progress after restart;
4. existing pending plus in-flight rows for the same partial-unique identity migrate without a
   constraint failure or lost earliest scope;
5. duplicate migration execution is prevented by the migration framework and the data transition
   is deterministic from the supported prior schema;
6. downgrade is executable when supported, or the forward-fix/restore boundary is explicit when a
   data transition cannot be truthfully reversed;
7. repository behavior against the migrated database matches the application state machine, not
   only the generated SQL text.

Use generated-SQL assertions as a guard, not as the sole proof. Include a real database test for
changes whose correctness depends on locking, partial indexes, null semantics, or concurrent rows.

## Closure Evidence

Record the prior schema/version, seeded legacy state matrix, migration command, post-upgrade row
states, restart/recovery result, constraint/index evidence, rollback or forward-fix posture, and any
required deployment drain. Do not claim compatibility from an empty-database migration smoke run.
