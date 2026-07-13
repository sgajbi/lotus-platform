# Endpoint Example Parity Standard

- Version: 1.0.0
- Status: Active
- Scope: Lotus readiness, supportability, version, certification, and certified business or
  operator endpoints
- Machine-readable contract:
  `platform-contracts/api-governance/endpoint-example-parity-contract.v1.json`

## Purpose

Documented response examples are operational contract evidence. Valid JSON syntax alone does not
prove that an example still matches the code-owned response model, aliases, blocker vocabulary, or
runtime serialization.

This standard requires certified examples to be compared with deterministic runtime evidence so
stale documentation fails before merge.

## Required Comparison

Exact structural comparison is the default.

| Concern | Required behavior |
| --- | --- |
| Object fields | Field order is irrelevant; missing and additional fields fail. |
| Arrays | Length, order, item type, and item value must match. |
| Nullability | A missing field differs from an explicit `null`. |
| Scalar types | Boolean differs from integer; integer differs from JSON number. |
| Aliases and vocabulary | Serialized field names, statuses, blockers, and version values match exactly. |
| Diagnostics | Failures identify code and JSON Pointer without echoing response values. |

Readiness, supportability, certification, supported-feature promotion, schema, contract-version,
and version fields must never use broad exclusions or value masking.

## Runtime Evidence Sources

Every governed example must use one of these sources:

1. an actual source-safe route invocation,
2. a code-owned response DTO or serializer,
3. a deterministic no-I/O example factory.

A copied documentation literal, untyped duplicate fixture, live production call, or sibling
feature branch is not runtime evidence. Route invocation is limited to operations whose execution
is safe and deterministic. Mutating, entitled, or dependency-backed endpoints should use a
code-owned serializer or no-I/O factory.

## Dynamic Values

Dynamic values require an explicit absolute RFC 6901 JSON Pointer and one approved strategy:

| Strategy | Intended value |
| --- | --- |
| `rfc3339` | Timezone-aware timestamp |
| `uuid` | Canonical UUID string |
| `non_empty_string` | Bounded generated string whose exact value is not contractual |
| `environment_string` | Bounded environment-specific identifier |

Normalizers apply only to the declared field. They must not suppress object shape, aliases,
blockers, readiness, supportability, certification, promotion, schema, contract, or version truth.

## Repository Adoption

Python services should use the platform comparator directly or carry the generated scaffold copy.
Other runtimes must implement equivalent exact semantics and bind authored examples to actual
route or serializer behavior in repository-native tests.

The generated backend scaffold:

1. copies `scripts/endpoint_example_parity.py`,
2. requires `response_example_parity.cases` for `baseline_certified` and `certified` ledger entries,
3. requires every documented success example index to have evidence,
4. supports source-safe static `GET` invocation and deterministic callable evidence,
5. fails malformed normalization, missing/stale fields, type drift, alias drift, and value drift.

## Validation

Minimum proof for an adoption:

1. matching documented and runtime examples pass,
2. a missing runtime field fails,
3. a stale documented field fails,
4. blocker, alias, value, and scalar-type drift fail,
5. malformed or forbidden normalization fails closed,
6. an approved dynamic normalization passes without hiding adjacent drift,
7. failure output remains source-safe.

Endpoint parity is one API-governance control. It does not replace OpenAPI validation,
authorization tests, runtime dependency proof, supportability telemetry, supported-feature
promotion evidence, or live canonical validation.
