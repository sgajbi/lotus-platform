# API Governance Contracts

## Endpoint Example Parity

The endpoint example parity contract governs deterministic comparison between
documented success examples and code-owned runtime serialization.

Exact structural comparison is the default:

1. object key order is irrelevant,
2. array order remains significant,
3. missing fields differ from explicit null,
4. booleans differ from integers,
5. integers differ from non-integral JSON numbers,
6. field names, blocker vocabulary, aliases, and scalar values must agree.

Dynamic values require an explicit absolute RFC 6901 JSON pointer and one
approved normalization strategy. Readiness, supportability, certification,
promotion, blocker, schema, contract-version, and version fields cannot be
normalized. This prevents a broad dynamic-field exception from hiding the
contract drift the gate exists to detect.

Runtime examples must come from a source-safe route invocation, the response
DTO or serializer, or a deterministic no-I/O example factory. A second
documentation literal is not runtime evidence.

Reference Python comparison behavior lives in
`codex/skills/lotus-ci-enforcement-governance/scripts/endpoint_example_parity.py`.
Other languages must pass equivalent contract fixtures and application-owned runtime parity tests.

Adoption and evidence requirements are defined in
`docs/standards/Endpoint Example Parity Standard.md`.
