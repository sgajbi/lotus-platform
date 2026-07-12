# Application And Adapter Classification

Use this reference when backend code has concrete external dependencies or when a module named
`processor`, `service`, `manager`, or `workflow` is being moved into a layered package structure.

## Contents

1. [Classify Before Moving](#classify-before-moving)
2. [Capability-Oriented Layout And Naming](#capability-oriented-layout-and-naming)
3. [External Capability Coupling](#external-capability-coupling)
4. [Provider Contract Fixtures](#provider-contract-fixtures)
5. [Proof Validators During Refactors](#proof-validators-during-refactors)
6. [Required Proof](#required-proof)

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

## Capability-Oriented Layout And Naming

Organize cohesive feature families inside the existing runtime layers before adding deployables.
For example, a lifecycle capability may use `domain/data_lifecycle/authority.py` and
`domain/data_lifecycle/schedule.py` while its application, port, and adapter modules remain in
their owning layers. Preserve the dependency direction; a feature package is not permission to
collapse API, application, domain, port, and infrastructure code into one directory.

Use enduring capability or invariant names for executable artifacts. Do not name source modules,
scripts, workflows, contracts, migrations, or tests after an RFC number, slice number, issue, PR,
or temporary project phase. RFC identifiers belong in RFC documents, RFC closure manifests, and
explicit tracking artifacts whose purpose is that RFC. Rename an executable gate introduced by an
RFC for what it enforces, such as `foundation_structure_gate.py`, not `slice2_structure_gate.py`.

When introducing a bounded package:

1. define its public package surface and avoid private cross-package imports;
2. migrate imports atomically and prohibit obsolete flat paths rather than retaining indefinite
   compatibility aliases;
3. mirror the capability grouping in focused tests when test discovery supports it;
4. keep reusable logic out of crowded CLI directories; scripts should be thin entrypoints;
5. avoid tests that infer repository root from a fragile fixed parent depth after relocation;
6. add a deterministic placement/naming guard only after the canonical layout is proven;
7. verify wheel/container inclusion and the real runtime import path when packaging is affected.

Do not impose arbitrary directory-size limits or create one-off subfolder conventions. Inventory
large flat directories, select one cohesive pilot, prove the pattern, then migrate other families
incrementally. Folder size alone never justifies a new service or process.

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

## Proof Validators During Refactors

Source-backed proof checks must follow stable interfaces and governed behavior, not comments,
incidental prose, or implementation literals that disappear during a valid refactor. When shared
security, transport, policy, or adapter logic is extracted:

1. identify every proof generator and contract gate that inspects the moved source;
2. bind checks to stable exported symbols, calls, schemas, or runtime behavior;
3. retain adversarial tests for missing producer evidence, tampering, overclaiming, and consumer
   controls;
4. run the live sibling-repository proof when a local checkout is available;
5. preserve consumer-only fail-closed behavior when the producer checkout is unavailable.

Do not weaken a proof gate merely to survive a rename. Replace brittle evidence with stronger
interface or behavioral evidence and record which certification blockers remain.

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
