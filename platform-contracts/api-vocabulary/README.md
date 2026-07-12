# Lotus API Vocabulary Inventory

This directory stores per-application API vocabulary contracts used to enforce shared naming and documentation quality across Lotus services.

Governance model:

1. App-specific inventories are the implementation source of truth.
2. Platform-level cross-app validation enforces semantic consistency across inventories.

## Document Once Rule

For each application inventory:

- Every semantic attribute is documented exactly once in `attributeCatalog`.
- Endpoint request/response fields must reference that attribute using `attributeRef`/`semanticId`.
- Endpoint-local field entries are usage mappings, not duplicate documentation records.

## lotus-core Inventory

- File: `lotus-core-api-vocabulary.v1.json`
- Source: `lotus-core` OpenAPI contracts (`query_service` and `ingestion_service`)
- Generator: `lotus-core/scripts/quality/api_vocabulary_inventory.py`

## lotus-risk Inventory

- File: `lotus-risk-api-vocabulary.v1.json`
- Source: `lotus-risk` OpenAPI contracts
- Generator: `lotus-risk/scripts/api_vocabulary_inventory.py`

## lotus-performance Inventory

- File: `lotus-performance-api-vocabulary.v1.json`
- Source: `lotus-performance` OpenAPI contracts
- Generator: `lotus-performance/scripts/api_vocabulary_inventory.py`

## lotus-manage Inventory

- File: `lotus-manage-api-vocabulary.v1.json`
- Source: `lotus-manage` OpenAPI contracts
- Generator: `lotus-manage/scripts/api_vocabulary_inventory.py`

## Regeneration

```powershell
python ..\lotus-core\scripts\api_vocabulary_inventory.py `
  --output .\platform-contracts\api-vocabulary\lotus-core-api-vocabulary.v1.json
```

```powershell
python ..\lotus-risk\scripts\api_vocabulary_inventory.py `
  --output .\docs\standards\api-vocabulary\lotus-risk-api-vocabulary.v1.json
Copy-Item `
  ..\lotus-risk\docs\standards\api-vocabulary\lotus-risk-api-vocabulary.v1.json `
  .\platform-contracts\api-vocabulary\lotus-risk-api-vocabulary.v1.json `
  -Force
```

```powershell
python ..\lotus-performance\scripts\api_vocabulary_inventory.py `
  --output .\docs\standards\api-vocabulary\lotus-performance-api-vocabulary.v1.json
Copy-Item `
  ..\lotus-performance\docs\standards\api-vocabulary\lotus-performance-api-vocabulary.v1.json `
  .\platform-contracts\api-vocabulary\lotus-performance-api-vocabulary.v1.json `
  -Force
```

```powershell
python ..\lotus-manage\scripts\api_vocabulary_inventory.py `
  --output .\docs\standards\api-vocabulary\lotus-manage-api-vocabulary.v1.json
Copy-Item `
  ..\lotus-manage\docs\standards\api-vocabulary\lotus-manage-api-vocabulary.v1.json `
  .\platform-contracts\api-vocabulary\lotus-manage-api-vocabulary.v1.json `
  -Force
```

## Cross-App Validation Gate

Run platform-level conformance checks:

```powershell
python .\platform-contracts\api-vocabulary\validate_api_vocabulary_catalog.py
```

The gate fails when:

1. A per-app inventory duplicates `semanticId`.
2. `canonicalTerm != preferredName`.
3. Non-snake-case canonical terms appear.
4. The same `semanticId` maps to different canonical terms across apps.
5. The same canonical term maps to multiple semantic IDs across apps.
6. Legacy/canonical conflicts appear (for example `cif_id` and `client_id` both present).
