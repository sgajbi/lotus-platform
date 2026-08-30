# Lotus Domain Vocabulary Contracts

This directory stores platform-owned domain vocabularies that must be reused by Lotus services instead of rediscovering local enum names.

## Performance Periods

`canonical-performance-periods.v1.json` is the governed period vocabulary for performance, risk, reporting, and front-office analytics.

Use it when defining or changing:

1. request period fields such as `period`, `periods`, `window.period`, or `period.type`,
2. response maps keyed by period,
3. Swagger/OpenAPI examples for analytics periods,
4. adapters that translate between service-specific legacy names.

New APIs should expose `canonical_code` values. Existing service contracts may continue to accept values listed in `accepted_aliases`, but they should normalize those values internally and document compatibility explicitly. Do not introduce a new period token unless it is added here first with semantics, required fields, and an owner-reviewed migration stance.

Validation:

```powershell
python -m pytest tests/unit/test_canonical_performance_period_vocabulary.py -q
```

## Domain Data Product Trust Metadata

`domain-data-product-trust-metadata.v1.json` is the governed field registry for product
declarations and trust telemetry snapshots.

When a source-owning service exposes receipt or evidence envelopes for downstream proof, use the
standard temporal identity fields instead of local aliases:

1. `producer_generated_at` for the producer-generated receipt timestamp,
2. `evidence_as_of_date` for the source-owned business as-of date represented by the evidence,
3. `temporal_identity_status` for closed fail-safe posture such as available, missing, mixed, or
   not applicable.

Consumers must not substitute request dates, caller clocks, or self-asserted tenant context for
missing producer temporal identity.

## Transaction Identity

`transaction_id` is the stable, source-owned identifier for an individual booked or projected
transaction record. Domain-product declarations must include it when a route or payload selects an
exact transaction. It complements `portfolio_id`; neither identifier alone implies tenant ownership.

## Advisory Proposal Identity

The domain-data-product semantics registry includes `proposal_id`, `proposal_version_id`,
`version_no`, `version_id`, `memo_id`, `evaluation_id`, and `action_item_id` as stable identifiers
for advisory proposal lifecycle, evidence, policy, memo, and cockpit products. Producer
declarations should list these identifiers whenever their governed routes expose the corresponding
identity; consumers should use the source-owned identifiers rather than inferring them from opaque
payloads.
