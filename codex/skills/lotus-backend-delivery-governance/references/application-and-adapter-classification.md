# Application And Adapter Classification

Use this reference when backend code has concrete external dependencies or when a module named
`processor`, `service`, `manager`, or `workflow` is being moved into a layered package structure.

## Contents

1. [Classify Before Moving](#classify-before-moving)
2. [External Capability Coupling](#external-capability-coupling)
3. [Provider Contract Fixtures](#provider-contract-fixtures)
4. [Required Proof](#required-proof)

## Classify Before Moving

Classify code by actual dependencies and transaction ownership, not its filename or class name.
Code is not application-ready when it:

1. constructs database sessions or concrete repositories,
2. constructs idempotency, outbox, audit, queue, storage, HTTP, or transport clients,
3. reads framework metrics, clocks, UUID generators, or runtime configuration directly,
4. commits or rolls back a concrete unit of work,
5. coordinates a legacy workflow through private methods or framework DTOs.

Choose one truthful outcome:

1. extract a framework-neutral use case with typed commands/results and narrow ports,
2. keep or fold transitional behavior into a clearly named infrastructure compatibility adapter
   behind the existing application use case,
3. retain the current location temporarily and record the exact dependency extraction plan.

Do not move or rename code merely to make the tree appear layered.

## External Capability Coupling

When an issue exposes direct database, Kafka/EventHub, HTTP, object-storage, clock, UUID, audit,
idempotency, outbox, or unit-of-work coupling, fix the repeated pattern rather than only the named
call site. Define the narrow port and concrete adapter, preserve runtime behavior, test business and
failure semantics through fake ports, and add a deterministic guard when statically checkable.

## Provider Contract Fixtures

For external-provider or peer-service adapters, add or refresh versioned consumer-contract fixtures
instead of relying only on fake happy paths. Cover:

1. valid response,
2. malformed JSON or non-object payload,
3. missing required fields,
4. identity or as-of mismatch,
5. partial data,
6. authentication failure,
7. timeout and bounded retry/non-retry posture,
8. duplicate/idempotency behavior,
9. provider error mapping,
10. raw-payload and secret non-leakage.

Wire deterministic fixtures into the repo-native fast gate and document their source and command.

## Required Proof

1. Scan sibling processors/services and adjacent call sites for the same dependency pattern.
2. Prove domain/application behavior with focused tests.
3. Prove concrete adapter, transaction, replay, and rollback behavior with the real technology when
   those claims are in scope.
4. Preserve public API, event, persistence, metric, retry, and downstream contracts unless a change
   is intentional and governed.
5. Guard retired paths or forbidden imports when deterministic.
6. Update repository context and supersede stale architecture guidance so future agents do not
   recreate the mixed boundary.
