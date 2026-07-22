# Enterprise Refactor Quality Scorecard

Generated: `2026-07-22T18:32:59Z`

This scorecard tracks before/after movement for the enterprise backend refactor. Update it after
meaningful slices with measured evidence, not narrative-only claims.

| Area | Before | Target After | Evidence |
| --- | --- | --- | --- |
| Code health | Current max complexity 24 and largest function 884 lines | Reduce current hotspots without behavior drift | Largest files, highest-complexity functions, and completed extraction history are recorded in the baseline and health report. |
| Architecture | Report-only | Boundary rules enforced where practical | Architecture rules documented. |
| OpenAPI quality | Parseable examples could drift from runtime response truth | Generated services bind certified examples to deterministic response producers | A versioned parity contract, fail-closed comparator, scaffold gate, and mutation tests cover stale fields, blockers, aliases, types, and governed normalization. |
| Tests | 816 unit tests collected | Focused coverage added per slice | Collection result recorded. |
| Security | Keyword review sample measured | Scanner-backed findings clean or governed | No new dependency added yet. |
| Observability | Not yet assessed | Operational diagnostics measured and improved | Future slices should add concrete checks. |
| Documentation | Quality docs created | Scorecard updated per slice | Docs are implementation-backed. |
| Bank readiness controls | Overlapping prose guidance without stable machine-readable control identity | One versioned control catalog with evidence-aware discovery and validation | The standing contract is concise; the implementation playbook, catalog validator, and control-aware issue plan keep definitions centralized. |
