# Migration Engineering Quality Standard

This standard governs all lotus-core/lotus-performance/lotus-gateway/lotus-manage migration work.

## 1. Test Pyramid Requirements

Every migration increment must include:

1. Unit tests:
   - Pure-domain logic and adapters.
   - Fast, deterministic, high branch coverage.
2. Integration tests:
   - Router/service/repository boundaries.
   - Contract and persistence behavior.
3. End-to-end tests:
   - Critical user/workflow slices across services.
   - Docker-based environment parity.

No layer may be skipped for material behavior changes.

## 2. Coverage Policy

Target: approximately `99% meaningful` coverage for changed migration scope.

`Meaningful` means:
- assertions validate business behavior and invariants.
- no artificial tests that only execute lines without validating outcomes.
- error paths, boundary conditions, and policy gates are included.

Gate policy:
1. Global repository coverage should keep improving monotonically.
2. Changed-module coverage should target `>=99%` where practical.
3. Any exception requires explicit rationale in PR and RFC notes.

## 3. Documentation Freshness Rule

Documentation is part of Done criteria.

For each migration PR:
1. Update API docs/OpenAPI summaries and examples for changed endpoints.
2. Update RFC/ADR status for architectural or ownership changes.
3. Update central vocabulary (`docs/standards/Domain Vocabulary Glossary.md`) for shared terms.
4. Remove or rewrite stale statements immediately.
5. Run OpenAPI conformance baseline:
   - `powershell -ExecutionPolicy Bypass -File automation/Validate-OpenAPI-Conformance.ps1`

No code-only migration PRs are allowed for contract/architecture changes.

## 4. Async Execution and Automation

Use asynchronous automation for long-running and repeatable tasks:
- lint/type/test/coverage profiles via `automation/Run-Parallel-Tasks.ps1`
- detached background runs via `automation/Start-Background-Run.ps1`
- status monitoring via `automation/Check-Background-Runs.ps1`
- failure summarization via `automation/Summarize-Task-Failures.ps1`
- command-selection guide: `automation/docs/Automation-Guide.md`

Manual execution is reserved for debugging and high-context decisions.

## 5. Review Checklist

Each migration change must demonstrate:

1. clear boundary movement toward target ownership model.
2. vocabulary consistency across lotus-core, lotus-performance, lotus-gateway, and docs.
3. updated tests across pyramid layers.
4. documentation updated in both local repo and PPD when cross-cutting.
5. reproducible automation path for verification.
