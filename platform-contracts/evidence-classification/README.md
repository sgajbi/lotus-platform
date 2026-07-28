# Evidence Classification Contracts

This contract family governs Lotus evidence-class vocabulary used by blocker-clearing proof
artifacts, RFC closure manifests, skills, and context.

The current authority is:

1. `evidence-class-vocabulary.v1.json`
   Defines the canonical persisted evidence classes and the closed mapping from older
   platform/bank-readiness terms to canonical proof-artifact terms.

Validate with:

```powershell
python automation/validate_evidence_class_vocabulary.py
```

Rules:

1. persisted proof artifacts should use canonical values such as `source_contract` and
   `test_execution`;
2. legacy values such as `source_design_contract` and `local_test_execution` are accepted only in
   explicitly listed legacy contexts;
3. aliases are closed and deterministic, not free-form compatibility handling;
4. lower evidence classes must not clear runtime, deployment, production-certification, or broader
   promotion blockers by implication.
