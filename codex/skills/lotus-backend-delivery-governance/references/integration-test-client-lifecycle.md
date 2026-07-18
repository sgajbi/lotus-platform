# Integration Test Resource Lifecycle

Use this reference when FastAPI or Starlette integration tests create in-process API clients, or
when migration, evidence, batch, CLI, or integration-test code constructs database adapters from
connection settings. Apply it when a lane shows cumulative event-loop, socket, thread,
application-lifespan, connection-pool, resource, or unraisable cleanup failures.

## API Client Ownership

Every `TestClient` must be entered through a context manager or a fixture/factory that owns the
application lifespan and closes the client after each test, including failed tests. Keep tests that
explicitly exercise startup or shutdown behavior independent so lifecycle assertions remain real.

## Database Adapter Ownership

Classify every adapter before changing teardown:

1. A directly constructed adapter that creates its own connection provider owns that provider and
   must close it deterministically.
2. An adapter that receives an injected application-scoped provider borrows it and must never close
   it from request, operation, or test teardown.
3. The application composition root owns shared-provider shutdown after all borrowers stop.

Give owners a context manager or equivalent scope that closes on success and failure. Use nested
contexts or an exit stack when scripts create several adapter families. For integration suites with
many direct constructions, use one capability-oriented fixture or owner registry that records only
directly owned adapters and closes them in reverse creation order after every test, including failed
tests. Keep application service getters and provider-injected adapters outside that registry.

Test successful teardown, exceptional teardown, and reverse-order closure when order can affect
dependent resources. Do not use forced garbage collection, warning suppression, blanket allowlists,
or per-call shared-provider shutdown as lifecycle fixes.

## Same-Pattern Migration

When an unmanaged client or adapter is found:

1. scan the complete affected integration suite for direct and aliased construction;
2. migrate all credible occurrences to the governed owner in the same slice;
3. keep the fixture or factory in a capability-oriented test-support package; and
4. add a blocking source or AST gate when direct construction can reasonably recur.

For database adapters, include job, batch, lineage, repository, migration, proof, and CLI families.
Record each remaining construction as owned, borrowed, or intentionally process-scoped.

The gate should reject bypass through import aliases as well as the obvious direct import. Do not
weaken explicit application-lifespan tests merely to satisfy the gate.

## Closure Proof

For cumulative resource failures, such as Windows event-loop socket exhaustion:

1. run the full affected suite at least twice consecutively;
2. run the repository aggregate lane after its normal preceding checks; and
3. inspect the result for resource, unraisable, and event-loop cleanup warnings.

An isolated retry is diagnostic evidence only. It cannot prove that suite-level resource ownership
is fixed.

For database adapter defects, also:

1. run migration and evidence scripts with `ResourceWarning` promoted to an error;
2. run the complete affected integration lane with resource and unraisable cleanup warnings
   promoted to errors where the runner supports those categories;
3. run the ordinary aggregate repository gate; and
4. inspect output for connection, socket, event-loop, pool, resource, and unraisable warnings.

A green exit code with warning records is not closure. Preserve a separate application-shutdown
test when shared-provider lifecycle is part of the runtime contract. This internal lifecycle
pattern does not justify a pool replacement or separately deployed service without runtime evidence.
