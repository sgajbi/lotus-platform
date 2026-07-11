# Service Cost Attribution

## Purpose

This contract defines platform-owned, source-safe cost-attribution evidence for Lotus services.
Applications may supply bounded resource-observation digests and consume verified attribution;
they must not own cloud billing rates, shared-platform allocation, or provider reconciliation.

## Ownership Boundary

| Responsibility | Owner |
| --- | --- |
| Authoritative billing export and normalization | Platform FinOps operating process |
| Decimal allocation, rounding, residual handling, and reconciliation | `lotus-platform` |
| Service resource observation | Consuming Lotus application |
| Artifact signing and provenance | Protected platform mainline workflow |
| Business-domain accounting, portfolio performance, or client reporting | Not this contract |

No runtime service is introduced. The implementation is an internal contract/application/port/
adapter package. A separately scalable process requires measured workload, isolation, ownership, or
operability evidence.

## Methodology

Version: `lotus-platform.proportional-resource-cost-allocation.v1`.

For each governed category `c`:

```text
weight = service_resource_numerator / shared_resource_denominator
unrounded_allocation[c] = authoritative_category_cost[c] * weight
allocation[c] = round_half_even(unrounded_allocation[c], 2 decimal places)
```

The expected weighted total is rounded once from the authoritative source total. Any cent-level
residual between that total and the sum of category allocations is assigned to
`shared_platform`. Monetary values are canonical two-decimal strings and calculations use
`Decimal`; binary floating point is prohibited.

Negative category values represent authoritative credits, refunds, or corrections and remain
negative through allocation. They must reconcile within the same export version. A later provider
correction or late adjustment produces a new immutable artifact; prior evidence is retained rather
than overwritten.

## Certification

Generation proves only reconciliation. The generated artifact always carries
`costAttributionCertified=false` and `artifact_attestation_missing`. Certification is derived by a
consumer only after verifying the exact artifact digest, repository, signer workflow, main source
ref, and source commit.

Incomplete, stale, partial-period, unbalanced, malformed, unknown-field, duplicate-field, or
unverifiable evidence fails closed. Synthetic/test exports remain non-production evidence even when
they reconcile.

## Data Safety And Retention

The persisted artifact contains aggregate service/category values and supporting artifact digests.
It excludes raw billing rows, credentials, provider account/subscription identifiers, tenants,
clients, portfolios, candidates, requests, and payloads. Retain the normalized source digest,
artifact, attestation, and correction chain according to the platform audit schedule; retain raw
provider exports only in the separately governed billing authority system.
