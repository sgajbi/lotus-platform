# RFC-0096 Slice 6 Review: Code, Certification, And Governance Tightening

Date: 2026-04-21

Branch: `feature/rfc0096-delegation-implementation`

## Scope Reviewed

1. `platform-contracts/agent-engineering/delegation-policy-contract.v1.json`
2. `platform-contracts/agent-engineering/engineering-task-ledger-contract.v1.json`
3. `automation/validate_agent_engineering_contracts.py`
4. `automation/delegation_task_ledger.py`
5. `automation/heartbeat_sources.py`
6. heartbeat contract/config changes
7. focused tests and slice review evidence
8. AGENTS/context/skill guidance changed so far

## Findings And Fixes

1. Finding: delegated ledger timestamp fields accepted caller-provided strings without parseable UTC
   validation.
   Fix: `automation/delegation_task_ledger.py` now requires parseable RFC-3339 UTC strings ending
   in `Z` for `requested_at`, `ended_at`, and `reviewed_at`.
2. Finding: the delegated-task CLI dispatch was harder to read after adding return and review
   commands.
   Fix: the command dispatch was flattened into direct `if`/`elif` handling.
3. Finding: API certification posture needed an explicit decision.
   Fix: recorded below. RFC-0096 introduces machine-readable artifacts and automation, not a served
   HTTP API.

## API Certification And Governance Decision

RFC-0096 currently introduces artifact contracts and automation entrypoints:

1. delegation policy contract,
2. delegated task ledger records,
3. delegated return-envelope artifacts,
4. heartbeat attention derived from delegated task ledger artifacts.

OpenAPI certification is not applicable because no HTTP endpoint was introduced. Artifact
certification is applicable and is covered by:

1. `automation/validate_agent_engineering_contracts.py`,
2. `automation/validate_heartbeat_contracts.py`,
3. focused contract and ledger tests,
4. platform feature-lane validators.

If delegation posture is later exposed through `lotus-gateway` or another served API, that endpoint
must go through the Lotus endpoint certification pattern before being treated as product or operator
API truth.

## Gate-Affecting Decision

Delegation evidence remains advisory in this RFC. The contracts and validators are gate-covered,
but generated delegated task ledgers and generated heartbeat status should not become PR-blocking
yet. The first implementation needs signal history before generated stale-task posture can safely
block merges without creating noisy false positives.

## Complexity And Maintainability Review

1. The policy contract owns profile/envelope rules; the task-ledger contract owns task identity and
   lifecycle. This split is clean and avoids an overloaded monolith contract.
2. The delegated-task ledger helper is focused on local JSON ledger state. It does not launch
   agents, mutate GitHub, publish wiki, or merge PRs.
3. Heartbeat integration is read-only and artifact-backed. It does not inspect hidden model state.
4. Tests cover meaningful behavior: broad profile rejection, no-write scope enforcement,
   implementation write-scope enforcement, terminal failure context, replacement lineage, return
   envelope recording, main-agent review, timestamp parsing, and heartbeat attention conditions.

## Proof

Commands run:

```powershell
python -m pytest tests\unit\test_delegation_task_ledger.py tests\unit\test_agent_engineering_contracts.py tests\unit\test_heartbeat_contracts.py tests\unit\test_heartbeat_runner.py -q
python -m ruff check automation\delegation_task_ledger.py automation\heartbeat_sources.py automation\validate_agent_engineering_contracts.py automation\validate_heartbeat_contracts.py tests\unit\test_delegation_task_ledger.py tests\unit\test_agent_engineering_contracts.py tests\unit\test_heartbeat_contracts.py tests\unit\test_heartbeat_runner.py
python automation\validate_agent_engineering_contracts.py
python automation\validate_heartbeat_contracts.py
```

Results:

1. `55 passed` for focused delegated-task and heartbeat tests.
2. Ruff passed.
3. Agent engineering contract validator passed.
4. Heartbeat contract validator passed.

## Remaining RFC-0096 Work

1. Slice 7 must update final RFC status/evidence.
2. Slice 7 must complete docs/context/wiki/skills/branch hygiene decisions.
3. Slice 7 must run repo-level proof and GitHub PR checks before merge.
