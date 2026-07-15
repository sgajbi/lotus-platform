# Integration API Migration Proof

Use this reference when a refactor renames or removes repository, port, lease, transaction,
session, worker, or runtime APIs used by integration or end-to-end tests.

## Proof Standard

Successful test collection is not behavioral migration proof. Before closure:

1. search every moved integration and end-to-end test for retired symbols;
2. update fixtures and assertions to the active domain contract;
3. execute the focused suite against the real adapter technology; and
4. run the broad repository-native lane required by the change classification.

Add a cheap no-return source or architecture guard when obsolete calls remain syntactically
collectable and could silently return during later refactors.

## Transaction And Concurrency Integrity

Tests that model concurrent claimants or independent units of work must use independent database
sessions or connections. Reusing one active async session does not prove concurrency semantics and
can mask transaction-ownership defects.

Retain immutable entity identity before a rollback. Do not read expired ORM state outside its
owning async context merely to reconstruct the next operation.

## Evidence

Record:

1. the retired-symbol search result;
2. the real-adapter test command and outcome;
3. any no-return guard added; and
4. the broader repository-native validation result.
