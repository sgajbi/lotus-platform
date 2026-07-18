# Bank-Ready Engineering

Lotus bank readiness is governed as an evidence system, not a document or compliance claim.

## Use The Right Layer

| Need | Authority |
| --- | --- |
| Standing non-degradation outcomes | `platform-standards/LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md` |
| Assessment and delivery workflow | `platform-standards/LOTUS_BANK_READY_ENGINEERING_IMPLEMENTATION_PLAYBOOK.md` |
| Stable controls, applicability, evidence classes, and owner mappings | `platform-contracts/bank-readiness/bank-ready-control-catalog.v1.json` |
| Finding and deduplicating actionable gaps | `lotus-app-issue-discovery` with `--include-bank-readiness` |
| App implementation truth | Owning repository code, tests, contracts, context, scorecards, and runbooks |

The catalog is the only detailed control authority. This wiki page, agent context, skills, and app
documentation route to it rather than maintaining parallel `BR-NNN` definitions.

## Evidence Discipline

Source design, local tests, CI enforcement, deployment proof, runtime operation, and independent
verification are different evidence classes. A lower class must not be presented as a higher one.
The catalog's presence proves only that Lotus has a source-level control model; it does not prove an
application, deployment, bank, or organization implements every control.

Assess a coherent subset of applicable controls, group issues by evidenced root cause, and keep
unsupported claims visibly unknown or planned. Close a slice only after merge, exact-main
validation, issue evidence, necessary wiki publication, and safe branch/worktree reconciliation.

## Commands

```powershell
python automation\validate_bank_readiness_control_catalog.py
python codex\skills\lotus-app-issue-discovery\scripts\plan_issue_discovery_campaign.py --repository <owner>/<repo> --include-bank-readiness
```

The generated campaign plan is an applicability and evidence-routing aid. It is not an assessment,
certification, or instruction to create one issue per control.
