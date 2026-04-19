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
4. `../domain-vocabulary/domain-data-product-semantics.v1.json`
   Identifier, temporal-semantic, and trust-vocabulary registry used to harden cross-domain product contracts.
5. `../domain-vocabulary/domain-data-product-trust-metadata.v1.json`
   Trust metadata field registry, evidence access classes, and lineage bundle expectations for governed products.

Producer onboarding begins in later RFC-0084 slices:

1. Slice 2 aligns `lotus-core` producer declarations.
2. Slice 3 onboards `lotus-performance` and `lotus-risk` as the first analytics producer wave.

Current aligned producer declarations:

1. `lotus-core-products.v1.json`
   Initial platform-mapped declaration derived from the RFC-0083 source-data product catalog and
   governed security profiles.
2. `lotus-performance-products.v1.json`
   First analytics-output producer declaration for the performance authority wave.
3. `lotus-risk-products.v1.json`
   First analytics-output producer declaration for the risk authority wave.

Current aligned consumer declarations:

1. `lotus-performance-consumers.v1.json`
   Declares the first governed upstream dependencies used by the performance authority wave.
2. `lotus-risk-consumers.v1.json`
   Declares the first governed upstream dependencies used by the risk authority wave.

Expected declaration file patterns:

1. `*-products.v1.json`
2. `*-consumers.v1.json`

Validation command:

```powershell
python .\platform-contracts\domain-data-products\validate_domain_data_product_contracts.py
```

Discovery generation command:

```powershell
python .\automation\generate_domain_product_discovery.py
```

Discovery drift-check command:

```powershell
python .\automation\generate_domain_product_discovery.py --check --generated-at-utc 2026-04-19T00:00:00Z
```

Generated discovery artifacts:

1. `../../generated/domain-product-catalog.json`
   Machine-readable product catalog for ownership, lifecycle, route, approval, and trust metadata
   discovery.
2. `../../generated/domain-product-dependency-graph.json`
   Graph-friendly repository, product, approval, and consumer dependency relationships.
3. `../../generated/domain-product-catalog.md`
   Human-readable catalog summary generated from the governed declarations.

Source manifest:

1. `domain-product-source-manifest.v1.json`
   Governed aggregation-source manifest that records which repositories are included from the
   platform mirror today, which repositories already have repo-native declarations, and which
   repositories are waiting for clean-slate confirmation before federated aggregation is enabled.

Contract-family rules:

1. producer declarations live with the platform contract family rather than under `context/contracts/`,
2. producer declarations are repo-owned in content but platform-owned in schema and validation,
3. consumer declarations must remain explicit, version-aware, and trust-metadata-aware,
4. this contract family governs ownership, lifecycle, trust metadata, and dependency posture rather
   than runtime/demo-only contracts.
5. generated discovery artifacts must be regenerated from this contract family rather than edited
   by hand.
6. the source manifest must make temporary platform-mirror usage explicit while repo-native
   aggregation is being staged.
