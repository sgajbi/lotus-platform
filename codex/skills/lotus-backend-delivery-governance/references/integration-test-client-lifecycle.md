# Integration Test Client Lifecycle

Use this reference when FastAPI or Starlette integration tests create in-process API clients, or
when a test lane shows cumulative event-loop, socket, thread, or application-lifespan exhaustion.

## Ownership Contract

Every `TestClient` must be entered through a context manager or a fixture/factory that owns the
application lifespan and closes the client after each test, including failed tests. Keep tests that
explicitly exercise startup or shutdown behavior independent so lifecycle assertions remain real.

## Same-Pattern Migration

When an unmanaged client is found:

1. scan the complete affected integration suite for direct and aliased construction;
2. migrate all credible occurrences to the governed owner in the same slice;
3. keep the fixture or factory in a capability-oriented test-support package; and
4. add a blocking source or AST gate when direct construction can reasonably recur.

The gate should reject bypass through import aliases as well as the obvious direct import. Do not
weaken explicit application-lifespan tests merely to satisfy the gate.

## Closure Proof

For cumulative resource failures, such as Windows event-loop socket exhaustion:

1. run the full affected suite at least twice consecutively;
2. run the repository aggregate lane after its normal preceding checks; and
3. inspect the result for resource, unraisable, and event-loop cleanup warnings.

An isolated retry is diagnostic evidence only. It cannot prove that suite-level resource ownership
is fixed.
