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
