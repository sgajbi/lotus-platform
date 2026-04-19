# RFC-0084 Slice 2 Evidence - `lotus-core` Producer Alignment

## Scope

This evidence note records completion and mandatory review for RFC-0084 Slice 2.

Implemented artifacts:

1. `platform-contracts/domain-data-products/lotus-core-products.v1.json`
2. `platform-contracts/domain-data-products.schema.json`
3. `platform-contracts/domain-data-products/validate_domain_data_product_contracts.py`
4. `tests/unit/test_rfc_0084_domain_data_product_contracts.py`
5. `platform-contracts/domain-data-products/README.md`

## Deliverables Completed

1. Added the first real producer declaration file for `lotus-core`.
2. Mapped all current RFC-0083 source-data products into the RFC-0084 platform contract family.
3. Preserved current `lotus-core` `v1` product versions rather than forcing a broad rename in this
   slice.
4. Extended the platform producer schema to allow:
   - current `vN` product versions,
   - `snapshot_id` trust metadata,
   - optional `serving_plane` and `current_routes` fields for stronger auditability.
5. Added a cross-repo contract test that imports the live `lotus-core` source-data catalog and
   security profiles and verifies the platform declaration matches current implementation truth.

## Validation Run

Targeted validation for Slice 2:

```powershell
python -m pytest tests/unit/test_rfc_0084_domain_data_product_contracts.py -q
python .\platform-contracts\domain-data-products\validate_domain_data_product_contracts.py
```

## Mandatory Slice Review

Review outcome before moving to the next slice:

### Improvements made in this slice

1. Chose alignment-to-current-truth over a broad `v1` to semver rename in `lotus-core`, which keeps
   the slice small and avoids unnecessary blast radius.
2. Added `serving_plane` and `current_routes` to the platform producer declaration so future audits
   and validator work can reason about route bindings without re-parsing unrelated docs.
3. Added a cross-repo test that compares the platform declaration against live `lotus-core`
   implementation data, which materially reduces drift risk.

### Complexity reduction and maintainability review

1. The slice avoids changing `lotus-core` runtime code where platform alignment can be expressed in
   the platform contract family first.
2. The validator and declaration remain small and responsibility-driven rather than growing a large
   exporter tool before the model is stable.
3. The platform schema now reflects real producer truth instead of forcing premature normalization.

### Deferred issues

1. No `lotus-core` consumer declaration files are added in this slice because `lotus-core` is the
   producer focus here.
2. Product-version normalization across repositories is deferred; the platform contract family now
   tolerates both current `vN` and future semver forms.
3. No generated exporter from `lotus-core` exists yet; the current cross-repo test provides drift
   protection without adding another moving part.

### Why the deferrals are acceptable

1. Slice 3 is the correct place to add consumer-facing analytics producer onboarding for
   `lotus-performance` and `lotus-risk`.
2. Version normalization across all producer repos is a larger governance decision than this slice
   needs.
3. A generation tool would add maintenance cost before the declaration model and onboarding pattern
   have stabilized.

### Cleaner-than-found review

1. The platform contract family now has one real producer aligned to live implementation truth.
2. Cross-repo drift risk is lower because the declaration is backed by a live catalog comparison
   test rather than documentation alone.
