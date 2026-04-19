# Domain Data Product Contracts

This directory stores the platform-governed contract family introduced by RFC-0084 for cross-domain
data-product governance.

Slice 1 adds the contract family foundations:

1. `../domain-data-products.schema.json`
   Producer declaration schema for authoritative domain-product publishers.
2. `../domain-data-product-consumers.schema.json`
   Consumer declaration schema for repositories that depend on governed domain products.
3. `validate_domain_data_product_contracts.py`
   Lightweight validator for producer and consumer declaration files.

Producer onboarding begins in later RFC-0084 slices:

1. Slice 2 aligns `lotus-core` producer declarations.
2. Slice 3 onboards `lotus-performance` and `lotus-risk` as the first analytics producer wave.

Expected declaration file patterns:

1. `*-products.v1.json`
2. `*-consumers.v1.json`

Validation command:

```powershell
python .\platform-contracts\domain-data-products\validate_domain_data_product_contracts.py
```

Contract-family rules:

1. producer declarations live with the platform contract family rather than under `context/contracts/`,
2. producer declarations are repo-owned in content but platform-owned in schema and validation,
3. consumer declarations must remain explicit and version-aware,
4. this contract family governs ownership, lifecycle, trust metadata, and dependency posture rather
   than runtime/demo-only contracts.
