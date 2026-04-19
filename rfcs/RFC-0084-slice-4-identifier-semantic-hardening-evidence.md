# RFC-0084 Slice 4 Evidence - Identifier And Semantic Hardening

## Scope

This evidence note records completion and mandatory review for RFC-0084 Slice 4.

Implemented artifacts:

1. `platform-contracts/domain-vocabulary/domain-data-product-semantics.v1.json`
2. `platform-contracts/domain-data-products.schema.json`
3. `platform-contracts/domain-data-products/validate_domain_data_product_contracts.py`
4. `platform-contracts/domain-data-products/lotus-core-products.v1.json`
5. `platform-contracts/domain-data-products/lotus-performance-products.v1.json`
6. `platform-contracts/domain-data-products/lotus-risk-products.v1.json`
7. `platform-contracts/domain-data-products/README.md`
8. `README.md`
9. `REPOSITORY-ENGINEERING-CONTEXT.md`
10. `context/LOTUS-ENGINEERING-CONTEXT.md`
11. `tests/unit/test_rfc_0084_domain_data_product_contracts.py`

## Deliverables Completed

1. Added a governed registry for cross-domain identifier keys, temporal semantics, and trust
   vocabularies used by RFC-0084 product declarations.
2. Hardened the producer schema so every declared product must reference registered identifier and
   temporal semantics.
3. Extended the validator so it:
   - validates the semantics registry shape,
   - requires the registry when producer declarations are present,
   - rejects unknown identifier references,
   - rejects unknown temporal semantic references,
   - rejects freshness and completeness values that are not registered.
4. Aligned all currently onboarded producer declarations to the new semantic registry.
5. Added positive and negative tests so the registry is enforced rather than treated as
   documentation-only metadata.
6. Updated platform documentation and context so the semantic registry is discoverable as platform
   truth.

## Validation Run

Targeted validation for Slice 4:

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

1. Converted identifier and temporal semantics from prose-only assumptions into a governed
   machine-readable registry.
2. Tightened validation so the registry is a required dependency for producer declarations rather
   than an optional best-effort lookup.
3. Normalized the producer declaration JSON formatting after the structural update so the contract
   family remains readable and maintainable.
4. Expanded tests to cover both aligned live declarations and targeted validator failure modes.

### Complexity reduction and maintainability review

1. Kept semantic governance in one registry file instead of scattering identifier enums across each
   producer declaration.
2. Reused the existing validator path and declaration model instead of introducing another generator
   or compilation layer before the contract family is mature.
3. Limited the scope to identifiers, temporal semantics, and trust-vocabulary references that are
   already in live use across `lotus-core`, `lotus-performance`, and `lotus-risk`.

### Deferred issues

1. The trust vocabulary registry currently governs freshness and completeness references, but the
   producer schema does not yet require every optional trust field to reference a governed registry.
2. Consumer declarations do not yet carry their own semantic compatibility assertions.
3. Semantic registry entries are still hand-maintained rather than exported from a broader platform
   vocabulary source.

### Why the deferrals are acceptable

1. Slice 5 is explicitly reserved for trust and supportability contract expansion.
2. Consumer semantic compatibility becomes more valuable after trust metadata and supportability
   expectations are fully modeled.
3. Export automation would add maintenance cost before the vocabulary surface stabilizes.

### Cleaner-than-found review

1. The RFC-0084 contract family now has one discoverable semantic registry instead of implicit
   per-file conventions.
2. Drift risk is lower because producer declarations are validator-backed against registered keys.
3. Platform context now points future work to the registry directly rather than relying on RFC text
   alone.
