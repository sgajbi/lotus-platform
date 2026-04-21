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

## Validation

Run:

```powershell
python automation/validate_agent_engineering_contracts.py
```

The validator certifies the contract files and governed delegation examples under
`platform-contracts/agent-engineering/examples/`.

## Operating Rules

Delegated work is evidence for the accountable main agent. It is not review, PR approval, wiki
publication, or merge authority. Returned implementation or documentation work must stay within the
declared write scope, include evidence refs, and receive explicit main-agent review before it can
support RFC or PR closure.
