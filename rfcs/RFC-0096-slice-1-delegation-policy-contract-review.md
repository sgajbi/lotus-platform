# RFC-0096 Slice 1 Review: Delegation Policy Contract

Date: 2026-04-21

Branch: `feature/rfc0096-delegation-implementation`

## Slice Outcome

Implemented the first RFC-0096 contract slice:

1. added `platform-contracts/agent-engineering/delegation-policy-contract.v1.json`,
2. added governed valid and invalid delegation examples,
3. extended `automation/validate_agent_engineering_contracts.py` so the platform agent-engineering
   validator certifies the task-ledger contract, delegation policy contract, and delegation
   examples together,
4. added focused tests for profile vocabulary, no-write profile behavior, implementation write-scope
   requirements, broad-scope rejection, return-envelope requirements, and invalid example coverage.

## Review Findings

1. The RFC-0094 task-ledger contract already owns task identity, lifecycle, cleanup, and evidence
   posture. Extending it directly with every delegation prompt/return-envelope rule would make the
   ledger contract too broad.
2. A companion policy contract is cleaner: it depends on the RFC-0094 contract while owning
   delegation profiles, disallowed profiles, required prompt fields, required return fields,
   forbidden actions, and heartbeat attention identifiers.
3. The first validator draft caught broad read scopes, but broad write scopes on an already-invalid
   profile were not reported. The validator now rejects broad write scopes regardless of whether
   the profile is governed.
4. The contract remains artifact-certified, not OpenAPI-certified. No HTTP endpoint was introduced.

## Complexity And Maintainability Review

1. Kept validation inside the existing agent-engineering validator instead of adding a parallel
   script. This keeps platform feature-lane coverage simple and avoids another check entrypoint.
2. Kept examples small and representative: one no-write exploration, one bounded implementation,
   and one deliberately broad invalid delegation.
3. Did not add AGENTS/context/skill guidance in this slice. The durable behavior changes become
   meaningful after the operating guidance and ledger integration slices.

## Proof

Commands run:

```powershell
python -m pytest tests\unit\test_agent_engineering_contracts.py -q
python -m ruff check automation\validate_agent_engineering_contracts.py tests\unit\test_agent_engineering_contracts.py
python automation\validate_agent_engineering_contracts.py
git diff --check
```

Results:

1. `9 passed` for agent-engineering contract tests.
2. Ruff passed.
3. Agent engineering contract validator passed.
4. `git diff --check` passed.

## Remaining RFC-0096 Work

1. Slice 2 must update AGENTS/context/skill routing guidance with the governed delegation model.
2. Slice 3 must integrate delegated task status with RFC-0094 task-ledger records.
3. Slice 5 must wire stale or lost delegated task posture into RFC-0095 heartbeat evidence.
4. Slice 6 must perform code review, API-certification, and governance tightening.
5. Slice 7 must complete docs/context/wiki/skills and branch hygiene decisions.
