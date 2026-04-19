# RFC-0084 Slice 1 Evidence - Platform Registry Schemas

## Scope

This evidence note records completion and mandatory review for RFC-0084 Slice 1 in
`lotus-platform`.

Implemented artifacts:

1. `platform-contracts/domain-data-products.schema.json`
2. `platform-contracts/domain-data-product-consumers.schema.json`
3. `platform-contracts/domain-data-products/README.md`
4. `platform-contracts/domain-data-products/validate_domain_data_product_contracts.py`
5. `tests/unit/test_rfc_0084_domain_data_product_contracts.py`

Documentation/context updates:

1. `REPOSITORY-ENGINEERING-CONTEXT.md`
2. `context/CONTEXT-REFERENCE-MAP.md`
3. `context/LOTUS-ENGINEERING-CONTEXT.md`
4. `README.md`

## Deliverables Completed

1. Added the platform-owned producer declaration schema for governed domain data products.
2. Added the platform-owned consumer declaration schema for governed domain product dependencies.
3. Added a lightweight validator script so the contract family is executable rather than prose-only.
4. Added meaningful unit tests that validate contract-family governance metadata, a valid producer
   plus consumer flow, and duplicate-product and unknown-dependency failure behavior.
5. Kept onboarding of real producer repositories out of Slice 1 so Slice 2 and Slice 3 remain
   cleanly scoped.

## Validation Run

Targeted validation for Slice 1:

```powershell
python -m pytest tests/unit/test_rfc_0084_domain_data_product_contracts.py -q
python .\platform-contracts\domain-data-products\validate_domain_data_product_contracts.py
```

## Mandatory Slice Review

Review outcome before moving to the next slice:

### Improvements made in this slice

1. Chose `platform-contracts/` rather than `context/contracts/` to keep the new family aligned with
   platform-wide machine-readable governance artifacts.
2. Added a focused validator script instead of embedding contract logic only in tests.
3. Kept the file set small and named by responsibility rather than introducing a large monolithic
   governance module.
4. Added tests that exercise realistic producer and consumer declarations rather than superficial
   existence checks only.

### Complexity reduction and maintainability review

1. Slice 1 intentionally avoids onboarding real producer declarations before the schemas and
   validator exist.
2. The validator keeps cross-reference logic in one place instead of duplicating it in multiple
   tests.
3. The contract family README documents expected file patterns and command usage so future slices do
   not have to rediscover the conventions.

### Deferred issues

1. No actual producer declaration files are added in Slice 1; that is deferred intentionally to
   Slice 2 and Slice 3.
2. No workflow file is added yet for automated execution of the validator because the first goal is
   to stabilize the contract family and tests.

### Why the deferrals are acceptable

1. Adding real producer declarations before the schemas and validator are stable would blur slice
   boundaries and make review noisier.
2. Local targeted validation is enough proof for Slice 1; CI workflow wiring can follow when the
   first real declaration files exist.

### Cleaner-than-found review

1. The repository now has a concrete, testable starting point for RFC-0084 implementation.
2. Platform contract ownership is more explicit in docs and context than before the slice began.
