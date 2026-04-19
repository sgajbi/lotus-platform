# RFC-0084 Slice 5 Evidence - Trust And Supportability Contract Expansion

## Scope

This evidence note records completion and mandatory review for RFC-0084 Slice 5.

Implemented artifacts:

1. `platform-contracts/domain-vocabulary/domain-data-product-trust-metadata.v1.json`
2. `platform-contracts/domain-vocabulary/domain-data-product-semantics.v1.json`
3. `platform-contracts/domain-data-products.schema.json`
4. `platform-contracts/domain-data-products/validate_domain_data_product_contracts.py`
5. `platform-contracts/domain-data-products/lotus-core-products.v1.json`
6. `platform-contracts/domain-data-products/lotus-performance-products.v1.json`
7. `platform-contracts/domain-data-products/lotus-risk-products.v1.json`
8. `platform-contracts/domain-data-products/README.md`
9. `README.md`
10. `REPOSITORY-ENGINEERING-CONTEXT.md`
11. `context/LOTUS-ENGINEERING-CONTEXT.md`
12. `tests/unit/test_rfc_0084_domain_data_product_contracts.py`

## Deliverables Completed

1. Added a platform-owned trust metadata contract covering trust metadata fields, evidence access
   classes, and lineage bundle classes.
2. Expanded shared trust vocabularies to cover stale, unreconciled, break-open, blocked, and
   unknown semantics for completeness and reconciliation posture.
3. Hardened the producer schema and validator so producer declarations now reference:
   - registered trust metadata fields,
   - registered evidence access classes,
   - registered lineage bundle classes when evidence bundles are required.
4. Classified current first-wave producer evidence posture so operator support bundles are explicit
   and customer-consumable trust metadata remains distinct.
5. Aligned selected `lotus-risk` products to live trust metadata already required by the current
   risk product-surface contract and characterization tests.
6. Added validator and live-truth tests that prove the trust metadata contract is enforced rather
   than advisory.

## Validation Run

Targeted validation for Slice 5:

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

1. Replaced the schema's hardcoded trust metadata enum with a governed registry so the platform can
   evolve trust metadata intentionally without scattering duplicate lists across code and docs.
2. Added explicit evidence access classes to `lineage_policy`, which cleanly separates
   operator-only bundles from metadata that may flow into customer-facing downstream surfaces.
3. Used live `lotus-core` and `lotus-risk` truth to drive the first alignment pass instead of
   inventing new supportability fields that current repos do not publish.
4. Added negative tests for unknown trust metadata references so drift is caught by the validator.

### Complexity reduction and maintainability review

1. Kept trust metadata governance in one machine-readable registry instead of adding more nested
   per-product special cases.
2. Extended the existing validator path rather than creating a separate trust-lint tool.
3. Limited producer declaration expansion to metadata fields already evidenced by current
   `lotus-risk` contracts and `lotus-core` supportability products.

### Deferred issues

1. The trust metadata contract does not yet govern every optional supportability field that may
   appear in future performance inspection or operator-only payloads.
2. The validator does not yet require product declarations to publish the full field set implied by
   each lineage bundle class.
3. Consumer declarations still do not express trust metadata compatibility requirements directly.

### Why the deferrals are acceptable

1. Slice 6 is the correct place to harden consumer validation and mandatory trust-metadata posture.
2. Lineage bundle completeness checks are valuable, but they should follow only after the producer
   field set stabilizes further across repos.
3. The current slice already moves trust metadata governance from prose into validator-backed
   platform contracts.

### Cleaner-than-found review

1. The RFC-0084 contract family now has a dedicated trust metadata registry instead of mixing field
   governance into schema enums and ad hoc product notes.
2. Operator-only supportability products in `lotus-core` are now explicitly classified in the
   platform declarations.
3. Downstream-critical risk metadata is now visible in the platform contract family rather than only
   in risk-local docs and tests.
