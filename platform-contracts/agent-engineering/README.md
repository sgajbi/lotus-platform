# Agent Engineering Contracts

This contract family governs source-truth artifacts for long-running and delegated Lotus
engineering work.

## Contracts

1. `engineering-task-ledger-contract.v1.json`
   Defines RFC-0094 engineering task identity, lifecycle states, cleanup posture, evidence refs,
   and task kinds for local automation, background checks, and delegated subtasks.
2. `delegation-policy-contract.v1.json`
   Defines RFC-0096 delegation profiles, input-envelope fields, output-envelope fields,
   write-scope rules, disallowed broad profiles, main-agent review statuses, and heartbeat
   attention identifiers.
3. `stacked-refactor-campaign-manifest.schema.json`
   Defines the versioned manifest for long-running refactor campaigns that need multiple
   independently releasable tranches, predecessor main-SHA proof, branch commit budgets, issue
   closure posture, local and remote evidence, and final aggregate closure.

## Validation

Run:

```powershell
python automation/validate_agent_engineering_contracts.py
python automation/validate_stacked_refactor_campaign_manifest.py
```

The validator certifies the contract files and governed delegation examples under
`platform-contracts/agent-engineering/examples/`, including the stacked-refactor campaign example.

## Operating Rules

Delegated work is evidence for the accountable main agent. It is not review, PR approval, wiki
publication, or merge authority. Returned implementation or documentation work must stay within the
declared write scope, include evidence refs, and receive explicit main-agent review before it can
support RFC or PR closure.

Stacked refactor campaign manifests are required for governed refactor work that cannot fit in one
reviewable PR without exceeding rebase-safe commit budgets. Campaign issues stay open until the
final tranche is merged, exact-main validation is recorded, and branch cleanup evidence is present.
