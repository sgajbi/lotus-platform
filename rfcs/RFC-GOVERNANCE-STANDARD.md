# RFC Governance Standard

This standard governs new and reopened implementation-bearing Lotus RFCs.

## Required Closure Slices

Every implementation-bearing RFC must include a mandatory second-last slice and a mandatory final
slice.

### Second-Last Slice: Code Review And Governance Tightening

The second-last slice must cover:

1. code review and loose-end tightening,
2. dead-code and duplicate-logic cleanup,
3. API certification-pattern conformance where APIs are touched,
4. OpenAPI, vocabulary, contract, migration, and platform-governance conformance checks where
   applicable,
5. final test-quality review before closure.

This slice is not optional cleanup. It is the point where the implementation is made smaller,
cleaner, and easier to maintain before documentation closure.

### Final Slice: Documentation, Context, Skills, Wiki, And Branch Hygiene

The final slice must cover:

1. documentation updates,
2. agent context updates,
3. wiki updates where user/operator-facing behavior changed,
4. a conscious skills and guidance assessment,
5. branch hygiene and truthful PR/CI evidence.

The skills and guidance assessment must explicitly decide whether to keep, tighten, add, remove, or
make no change to the relevant guidance. A no-change decision is acceptable only when it is recorded
as a conscious decision.

## Legacy RFC Posture

Older RFCs are not rewritten only to satisfy this format. If a historical RFC is reopened for
implementation or material status changes, it must be upgraded to this standard as part of that
work.

The current mesh RFC family, RFC-0084 through RFC-0088, is the reference implementation of this
closure model.
