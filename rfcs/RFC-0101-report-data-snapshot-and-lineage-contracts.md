# RFC-0101: Report Data Snapshot And Lineage Contracts

- Status: Proposed
- Date: 2026-04-23
- Owners:
  - `lotus-report` owners
  - upstream domain service owners
  - lotus-platform data mesh governance
- Target repositories:
  - `lotus-report`
  - `lotus-core`
  - `lotus-performance`
  - `lotus-risk`
  - `lotus-advise`
  - `lotus-manage`
  - `lotus-platform`
- Depends on:
  - `RFC-0099-enterprise-reporting-and-document-archive-target-architecture.md`
  - `RFC-0100-reporting-gateway-invocation-and-job-ledger-foundation.md`
  - `RFC-0084-mesh-governance.md`
  - `RFC-0091-enterprise-data-mesh-maturity-and-production-readiness.md`

## Summary

This RFC defines the report data snapshot and lineage contracts required for reproducible,
supportable, and auditable reporting. It makes the machine-readable report payload, upstream call
evidence, hashes, source references, and supportability status durable enough to support rerender,
regenerate, correction, and operational diagnosis.

## Problem

Generated reports cannot be certified from final PDFs alone. A banking-grade report must preserve
the data snapshot or immutable references used to render the document, along with upstream service,
request, response, completeness, supportability, and trace evidence.

Without explicit snapshot and lineage contracts:

1. rerender cannot prove numbers stayed unchanged,
2. regenerate cannot explain changed numbers,
3. support teams cannot distinguish data issues from render issues,
4. audit cannot verify source inputs,
5. downstream archive metadata cannot carry meaningful lineage references.

## Target Scope

In scope:

1. `report_input_snapshot` contract,
2. `report_upstream_call` contract,
3. source response hash and reference semantics,
4. report data contract versioning,
5. snapshot retention and storage choice for first wave,
6. supportability and completeness fields,
7. portfolio review first-wave adoption,
8. data mesh declaration updates where applicable.

Out of scope:

1. rendering templates,
2. archive binary storage,
3. batch scheduling,
4. user-facing document download,
5. changing upstream domain ownership.

## Architecture Direction

`lotus-report` owns the report snapshot ledger, but upstream services remain authoritative for their
domain data. Snapshot lineage must record enough evidence to answer:

1. which upstream service was called,
2. which endpoint and contract version were used,
3. which request payload hash was submitted,
4. which response hash or immutable evidence reference was captured,
5. which trace/correlation identifiers connect the call,
6. whether the data was complete, partial, unavailable, or not supported.

## Contract Direction

Minimum `report_input_snapshot` fields:

1. `snapshot_id`,
2. `report_job_id`,
3. `report_type`,
4. `report_data_contract_version`,
5. `portfolio_scope`,
6. `as_of_date`,
7. `created_at`,
8. `snapshot_hash`,
9. `snapshot_storage_ref`,
10. `supportability_status`,
11. `lineage_ref_ids`.

Minimum `report_upstream_call` fields:

1. `upstream_call_id`,
2. `snapshot_id`,
3. `service_name`,
4. `endpoint`,
5. `method`,
6. `request_hash`,
7. `response_hash`,
8. `response_ref`,
9. `status_code`,
10. `latency_ms`,
11. `correlation_id`,
12. `trace_id`,
13. `supportability_status`,
14. `failure_category`.

## Implementation Slices

### Slice 0: Cleanup And Structure

1. Review current `lotus-report` lineage, evidence, coverage, and report data docs.
2. Remove duplicate lineage descriptions or convert them to links.
3. Create clear module boundaries for snapshot and upstream-call evidence.
4. Update wiki source only for durable operator lineage truth.

### Slice 1: Snapshot Contract And Storage

1. Add snapshot models and migration.
2. Define snapshot hash and storage reference behavior.
3. Add unit and migration tests for snapshot immutability and lookup.

### Slice 2: Upstream Call Evidence

1. Capture upstream call evidence for portfolio review.
2. Record request/response hash or explicit redacted/unavailable posture.
3. Add tests for success, partial, failed, timeout, and unsupported upstream responses.

### Slice 3: Report Data Contract Versioning

1. Add report data contract version to snapshot and report job records.
2. Add compatibility checks for rerender eligibility.
3. Document rules for incompatible snapshot versions.

### Slice 4: Data Mesh Alignment

1. Update report evidence product declarations if snapshot lineage becomes a governed product.
2. Validate producer/consumer declarations.
3. Ensure data mesh certification does not treat placeholder lineage as certified evidence.

### Second-Last Slice: Hardening, Review, And Certification

1. Review all snapshot and lineage paths.
2. Verify API certification and platform/data mesh governance.
3. Verify sensitive payload handling and redaction.
4. Tighten naming and failure semantics.

### Final Slice: Closure

1. Update docs, wiki, supported-features, context, and agent guidance.
2. Record whether lineage work should update skills or methodology guidance.
3. Publish wiki after merge if changed.

## Acceptance Criteria

1. Report data snapshots are durable and immutable after capture.
2. Upstream call lineage is queryable by report job and snapshot.
3. Snapshot hashes make rerender/reproduce workflows auditable.
4. Partial/unavailable upstream data is explicitly represented.
5. Sensitive payloads are not leaked in logs or public evidence.
6. Portfolio review uses the snapshot contract for first-wave proof.

## Risks

| Risk | Mitigation |
| --- | --- |
| Snapshot stores too much sensitive data | Use redaction, object references, access controls, and classification |
| Hashes are inconsistent | Define canonical JSON serialization and test golden vectors |
| Lineage becomes optional | Make snapshot creation part of report job lifecycle |
| Upstream services lack source refs | Capture request/response hashes first, then improve upstream refs in later RFCs |

## Validation

Required validation:

1. `lotus-report` lint, typecheck, unit, integration, migration, OpenAPI, and coverage gates.
2. Data mesh validation if declarations change.
3. Security review of snapshot storage and logging.

## Supported Features

No supported feature is added until report snapshots and upstream lineage are implemented, validated,
and reflected in `lotus-report` supported-features material.

