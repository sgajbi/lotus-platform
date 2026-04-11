# Platform Engineering Ledger

This ledger records cross-repository engineering lessons, recurring quality patterns, and important ecosystem fixes that future sessions should treat as already-learned knowledge.

## How To Use This Ledger

Add entries when a change reveals:

1. a repeatable quality failure,
2. a recurring architectural cleanup theme,
3. a cross-repo delivery pattern that should influence future work,
4. a governance or validation lesson that should not remain trapped in chat history.

Keep entries concise and operational.

## Current Ledger Entries

### 2026-04-11 | Canonical local runtime must be treated as a governed operator flow

The local Lotus bring-up path only became repeatable once:

1. direct ingress, managed host mappings, and canonical service addresses were treated as one governed system,
2. startup and teardown were scripted rather than improvised,
3. seeded data validation was included as part of the runtime contract,
4. UI validation checked real screens and sub-screens rather than only health endpoints.

Implication:

Future runtime or demo work should use canonical automation and validation instead of hand-built service startup sequences.

### 2026-04-11 | CI should use GitHub for heavy execution, not repeated expensive local reruns

RFC-0072 rollout work demonstrated that productivity improves when:

1. local checks are targeted and truthful,
2. GitHub Actions carries the expensive full matrix,
3. PRs are raised early,
4. failures are fixed forward from GitHub logs asynchronously.

Implication:

Future work should prefer targeted local proof plus GitHub-backed heavy execution rather than blocking on repeated full local reruns.

### 2026-04-11 | Platform standards become durable only when backed by scaffold and validators

Standards such as CI lane structure, workflow permissions, action baselines, repository hygiene, and container build rules were only durable once they were backed by:

1. scaffold templates,
2. validators,
3. documentation contract tests,
4. platform-owned repo checks.

Implication:

When a pattern matters ecosystem-wide, do not stop at prose. Promote it into executable truth where practical.
