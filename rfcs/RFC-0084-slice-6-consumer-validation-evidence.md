# RFC-0084 Slice 6 Evidence - Platform Consumer Validation

## Scope

This evidence note records completion and mandatory review for RFC-0084 Slice 6.

Implemented artifacts:

1. `platform-contracts/domain-data-product-consumers.schema.json`
2. `platform-contracts/domain-data-products/validate_domain_data_product_contracts.py`
3. `platform-contracts/domain-data-products/lotus-performance-consumers.v1.json`
4. `platform-contracts/domain-data-products/lotus-risk-consumers.v1.json`
5. `platform-contracts/domain-data-products/README.md`
6. `tests/unit/test_rfc_0084_domain_data_product_contracts.py`

## Deliverables Completed

1. Expanded consumer declarations so every dependency now records:
   - required trust metadata,
   - migration posture,
   - the existing consumption mode, validation lanes, and failure posture.
2. Hardened the validator so it fails when:
   - consumers depend on undeclared products,
   - consumers drift behind the latest declared producer version without approved transition posture,
   - consumers require trust metadata that upstream producers do not publish.
3. Aligned the current `lotus-performance` and `lotus-risk` consumer declarations to the new
   contract shape using trust metadata that current upstream products already publish.
4. Added fixture coverage for current-state dependencies, version-drift failures, approved
   transition posture, and missing-upstream-trust-metadata failures.
5. Extended live-repo alignment tests so the current first-wave consumer declarations prove nonempty
   trust metadata requirements and explicit current migration posture.

## Validation Run

Targeted validation for Slice 6:

```powershell
python -m pytest tests/unit/test_rfc_0084_domain_data_product_contracts.py -q
python .\platform-contracts\domain-data-products\validate_domain_data_product_contracts.py
python -m pytest tests/unit/test_engineering_context_system_contract.py -q
python -m pytest tests/unit/test_ci_governance_documentation_contract.py -q
git diff --check
```

## Mandatory Slice Review

Review outcome before moving to the next slice:

### Improvements made in this slice

1. Upgraded consumer declarations from passive dependency lists into executable compatibility
   contracts.
2. Added explicit migration posture instead of treating version drift as tribal knowledge or a
   future clean-up item.
3. Required consumers to state which upstream trust metadata they actually rely on, which gives the
   platform a concrete way to catch explainability regressions.
4. Kept the current producer and consumer declarations aligned without forcing paper-only upstream
   metadata fields.

### Complexity reduction and maintainability review

1. Extended the existing consumer schema and validator instead of creating a parallel migration
   waiver system.
2. Used the platform declarations as the single comparison surface for version drift and trust
   metadata compatibility.
3. Kept migration posture narrow with only `current` and `approved_transition` states so the model
   remains easy to reason about in CI.

### Deferred issues

1. Consumer declarations still do not express field-level shape expectations beyond trust metadata.
2. Migration posture does not yet carry explicit owner approval references or change-ticket links.
3. The validator does not yet consume repo-native CI artifacts or upstream PR evidence directly.

### Why the deferrals are acceptable

1. Slice 6 is meant to enforce compatibility posture, not to replace endpoint certification or
   repo-native evidence workflows.
2. Approval-evidence linkage belongs naturally in later governance tightening work once the base
   contract shape is stable.
3. The current validator already catches the highest-value failure modes for undeclared dependencies,
   silent version drift, and missing trust metadata.

### Cleaner-than-found review

1. The consumer contract family now carries explicit migration and explainability posture rather
   than relying on prose or implied repo convention.
2. `lotus-performance` and `lotus-risk` consumer declarations are now more informative while still
   staying tightly scoped to real upstream dependencies.
3. CI can now detect a meaningful new class of cross-repo regressions before runtime integration
   fails.
