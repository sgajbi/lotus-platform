# RFC-0002 Review Hardening

Use this reference when backend review, issue execution, or RFC-0002-adjacent work touches trusted
local/dev headers, receipt/replay idempotency, or source-owned temporal evidence.

## Guardrails

1. Source-owned temporal evidence
   - Do not substitute a consumer-owned request date, local snapshot date, persistence time, or
     calculation clock for a source-owned business/effective date.
   - Omit the source date and keep the posture fail-closed/non-certifying until the producer
     preserves that evidence.
   - When optional source refs lack source-owned temporal fields, test that downstream proof remains
     `missing_source_evidence` or the repository's equivalent blocker state.

2. Receipt/replay idempotency
   - Scope idempotency state to the trusted caller/resource context that defines ownership, such as
     tenant, legal entity, subject, service identity, capability, portfolio, book, or aggregate
     identity.
   - Validate trimmed blank idempotency keys before hashing.
   - Prove same-key cross-scope requests cannot replay or conflict with another caller's receipt.

3. Trusted local/dev caller context
   - If a local/dev route uses trusted headers instead of a production IdP, the OpenAPI/API
     vocabulary must still mark every required trusted-context header as required.
   - Preserve an explicit no-auth/production-IdP blocker issue instead of implying production
     authorization is complete.
