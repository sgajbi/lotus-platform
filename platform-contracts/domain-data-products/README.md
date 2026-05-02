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

Onboarding scaffold command:

```powershell
python .\automation\generate_domain_product_onboarding.py --repository lotus-core --product-name ExampleSourceProduct --product-version v1 --authoritative-domain portfolio_management --product-family source_data
```

Generated onboarding bundles include:

1. repo-native producer declaration scaffold,
2. trust telemetry scaffold,
3. SLO, access, and evidence policy scaffolds,
4. source-data product API profile scaffold covering ingestion, serving API, certification, and downstream consumption posture,
5. API certification checklist for OpenAPI, output-family, error, security, non-functional, and live-evidence proof,
6. ingestion pipeline checklist for source acquisition, idempotency, lineage, reconciliation, backfill, runtime telemetry, and canonical seed-data readiness.

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
   Governed aggregation-source manifest that records which repositories are included from
   repo-native declarations and which, if any, still require temporary platform mirrors.

Contract-family rules:

1. producer declarations live in the owning repository once repo-native rollout is complete,
2. producer declarations are repo-owned in content but platform-owned in schema and validation,
3. consumer declarations must remain explicit, version-aware, and trust-metadata-aware,
4. this contract family governs ownership, lifecycle, trust metadata, and dependency posture rather
   than runtime/demo-only contracts.
5. generated discovery artifacts must be regenerated from this contract family rather than edited
   by hand.
6. the source manifest must make temporary platform-mirror usage explicit; included repo-native
   sources are validated together before catalog, graph, and certification artifacts are generated.
