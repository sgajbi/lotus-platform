# API Governance Rules

`lotus-platform` does not own a business-domain API. API governance work in this repository applies
to generated service scaffolds, OpenAPI validators, vocabulary contracts, gateway-facing governance
artifacts, and cross-repository certification evidence.

Rules for this refactor:

1. platform OpenAPI checks should remain reusable by service repositories,
2. API vocabulary and no-alias truth should live in platform contracts and generated inventories,
3. scaffolds must create Swagger/OpenAPI documentation that is useful by default,
4. platform docs must not claim implementation-backed APIs owned by another repository.
