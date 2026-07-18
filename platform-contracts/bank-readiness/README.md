# Bank-Readiness Control Contracts

This contract family turns the Lotus Bank-Ready Engineering Implementation Playbook into a
versioned, machine-readable control system.

The human standard explains intent and operating practice:

1. `platform-standards/LOTUS_BANK_READY_ENGINEERING_IMPLEMENTATION_PLAYBOOK.md`
2. `platform-standards/LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md`

The catalog is the automation authority:

1. `bank-ready-control-catalog.v1.json`
2. `automation/validate_bank_readiness_control_catalog.py`

## What The Catalog Governs

Each stable control identifies:

1. applicable repository profiles and applicability conditions;
2. local-development, CI, and production expectations;
3. required evidence types and minimum evidence class;
4. issue-discovery lenses;
5. default enforcement posture and accountable owner roles.

The catalog also governs the closed status vocabulary, maturity levels, completion layers,
repository profiles, evidence classes, and external engineering-reference registry.

## Evidence Boundary

Catalog presence is `source_design_contract` evidence only. It does not prove that an application,
deployment, or organization implements a control. An application assessment must cite the actual
evidence class supplied. Runtime, deployment, independently reviewed, regulatory, or bank-acceptance
claims cannot be inferred from source or CI evidence.

## Validation

```powershell
python automation\validate_bank_readiness_control_catalog.py
```

The validator is worktree-clean and runs in the platform repository checks. App-local assessment
generation and rollout are separate bounded slices; they must not copy or fork the catalog.
