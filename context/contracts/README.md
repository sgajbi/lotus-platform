# Context Contracts

This directory stores machine-readable, platform-governed contracts that are intended to be
consumed by Lotus automation, validation, and product-surface governance.

These files are not product-runtime source-of-truth implementations by themselves. They define the
cross-repository contract that implementation work must satisfy.

Current contracts:

1. `canonical-front-office-demo-data-contract.json`
   The governed identity, ownership, date policy, and coverage contract for the canonical
   front-office portfolio and benchmark.
2. `canonical-front-office-demo-data-invariants.json`
   The governed minimum thresholds and supportability invariants for the canonical dataset.

Rules:

1. update these files through governed RFC implementation, not ad hoc edits,
2. keep field naming explicit and domain-correct,
3. keep contracts machine-readable and stable enough for tests and automation,
4. avoid embedding fake supportability or UI-only expectations that backend services do not own.
