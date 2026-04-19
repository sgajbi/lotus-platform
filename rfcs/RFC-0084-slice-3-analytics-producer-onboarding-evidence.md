# RFC-0084 Slice 3 Evidence - First Analytics Producer Onboarding

## Scope

This evidence note records completion and mandatory review for RFC-0084 Slice 3.

Implemented artifacts:

1. `platform-contracts/domain-data-products/lotus-performance-products.v1.json`
2. `platform-contracts/domain-data-products/lotus-performance-consumers.v1.json`
3. `platform-contracts/domain-data-products/lotus-risk-products.v1.json`
4. `platform-contracts/domain-data-products/lotus-risk-consumers.v1.json`
5. `platform-contracts/domain-data-products/README.md`
6. `tests/unit/test_rfc_0084_domain_data_product_contracts.py`

## Deliverables Completed

1. Registered the first governed `lotus-performance` analytics-output products.
2. Registered the first governed `lotus-risk` analytics-output products.
3. Declared the first cross-domain consumer dependencies for `lotus-performance` and `lotus-risk`.
4. Kept the first analytics wave focused on products that are already authoritative, already documented,
   and already used across repository boundaries today.
5. Added live cross-repo tests that compare the platform declarations to current implementation and
   certification evidence in `lotus-performance` and `lotus-risk`.

## Validation Run

Targeted validation for Slice 3:

```powershell
python -m pytest tests/unit/test_rfc_0084_domain_data_product_contracts.py -q
python .\platform-contracts\domain-data-products\validate_domain_data_product_contracts.py
```

## Mandatory Slice Review

Review outcome before moving to the next slice:

### Improvements made in this slice

1. Chose a small first-wave product set instead of registering every analytics endpoint in both
   repositories. The registered products are already authoritative and already cross-domain.
2. Declared consumer dependencies explicitly enough for validator-backed cross-repo approval checks.
3. Backed the declarations with live repo-code and certification-doc checks rather than relying on
   RFC text alone.

### Complexity reduction and maintainability review

1. Did not invent a new exporter or registry generator before the product model is stable across the
   first analytics wave.
2. Avoided forcing gateway into the producer wave; it remains a governed consumer and composer.
3. Kept declarations in the platform contract family so the onboarding pattern stays centralized and
   discoverable.

### Deferred issues

1. The first-wave producer set is intentionally narrow and does not register every performance or
   risk endpoint.
2. Analytics-output trust metadata is still constrained by the current platform trust-field enum and
   does not yet model every lineage field exposed by `lotus-performance` and `lotus-risk`.
3. Optional watchlist or supportability-only upstream routes remain outside the first registered
   dependency set unless they are already covered by governed products.

### Why the deferrals are acceptable

1. Slice 3 is meant to prove the onboarding pattern, not exhaust the whole estate.
2. Slice 5 is the correct place to expand the platform-wide trust metadata vocabulary.
3. Slice 4 and Slice 6 will further harden identifier semantics and consumer validation once the
   first-wave registry is established.

### Cleaner-than-found review

1. The platform registry now covers both source-data authority and the first analytics producer wave.
2. Cross-domain dependency posture for `lotus-performance` and `lotus-risk` is now machine-readable.
3. The platform contract tests now verify live repo truth for all first-wave producers rather than
   only schema shape.
