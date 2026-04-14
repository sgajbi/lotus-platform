# RFC-0083: Lotus Core System-of-Record Target Architecture

- Status: Draft
- Date: 2026-04-15
- Owners:
  - lotus-platform architecture
  - lotus-core maintainers
- Requires Approval From:
  - lotus-platform maintainers
  - lotus-core maintainers
  - lotus-performance maintainers
  - lotus-risk maintainers
  - lotus-gateway maintainers
  - lotus-advise maintainers
  - lotus-manage maintainers
  - lotus-report maintainers
- Related:
  - `RFC-0041-platform-integration-architecture-bible-governance.md`
  - `RFC-0050-core-data-analytics-and-reporting-service-boundaries.md`
  - `RFC-0067-centralized-api-vocabulary-inventory-and-openapi-documentation-governance.md`
  - `RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`
  - `RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md`
  - `RFC-0082-lotus-core-domain-authority-and-analytics-serving-boundary-hardening.md`
  - `C:/Users/Sandeep/projects/lotus-core/docs/architecture/RFC-0082-contract-family-inventory.md`

## Summary

RFC-0082 defines the boundary rule for `lotus-core`: core owns source truth and governed input
contracts, but it does not own downstream performance, risk, gateway composition, advisory workflow,
or management workflow conclusions.

RFC-0083 defines the target architecture for making `lotus-core` the banking-grade system of record
that Lotus needs before first production release.

This RFC is the master blueprint. It intentionally separates:

1. target state,
2. domain model,
3. temporal model,
4. command/read model,
5. source-data products,
6. ingestion and lineage,
7. reconciliation and data quality,
8. endpoint consolidation,
9. implementation slices.

It does not require a greenfield `lotus-core-v2`, a parallel repository, or a gRPC migration.

The target is to harden the current `lotus-core` into a clear, explainable, auditable system of
record through controlled implementation slices.

## Problem

`lotus-core` is already the intended authority for portfolio, booking, account, holding, transaction,
market-data, benchmark, and foundational reference data.

However, "source of truth" is not yet expressed as one complete target architecture.

The current risks are:

1. core ownership is clear in intent but still uneven in API shape, documentation, and module language,
2. temporal concepts are not yet governed as one platform-wide model,
3. portfolio state reconstruction, lineage, and restatement behavior need a stronger explicit design,
4. ingestion, validation, replay, data quality, and reconciliation need to feel like first-class product
   capabilities rather than supporting implementation details,
5. endpoint families can grow around consumer convenience instead of stable source-data products,
6. downstream services can depend on ambiguous source shapes if target source-data contracts are not
   defined,
7. pre-live cleanup opportunities can be lost if the target state remains implicit.

RFC-0083 exists so the team can answer:

> What does "correct `lotus-core`" mean?

The answer must be stable enough to guide future implementation RFCs and small enough to execute in
safe slices.

## Decision

Lotus adopts the following target architecture for `lotus-core`.

`lotus-core` is the system-of-record and source-data product service for:

1. portfolio identity and lifecycle,
2. account and custody structures,
3. holdings and position state,
4. transaction and booking ledger truth,
5. cash ledger truth,
6. instrument master and reference classifications,
7. market data needed for core valuation inputs,
8. FX data needed for core valuation inputs,
9. benchmark, index, and risk-free source primitives,
10. ingestion, validation, replay, and source lineage,
11. reconciliation, breaks, and data-quality evidence,
12. deterministic portfolio-state snapshots and analytics input products.

`lotus-core` is not the authority for:

1. performance return, contribution, attribution, or review conclusions,
2. risk concentration, drawdown, stress, VaR, or risk interpretation conclusions,
3. gateway product composition,
4. advisory workflow, suitability decisioning, proposal alternatives, or consent workflow,
5. discretionary portfolio-management execution workflow,
6. report generation and document packaging,
7. AI-generated explanation or summarization.

## Target State In One Page

In the target state:

1. every mutation of core truth is a command with idempotency, validation, lineage, and audit evidence,
2. every important read is a governed read model or source-data product with clear temporal semantics,
3. every source-data product carries provenance, completeness, freshness, and policy/supportability
   context,
4. portfolio state can be deterministically reconstructed for an as-of context,
5. corrections and restatements are explicit and auditable,
6. ingestion is replayable and produces validation evidence,
7. reconciliation status is visible and usable by downstream consumers,
8. data-quality status is part of the API contract, not hidden in logs,
9. endpoint count is controlled by stable product contracts rather than ad hoc convenience routes,
10. downstream analytics services receive ingredients, not core-owned analytics conclusions.

## Architectural Principles

### 1. System of record means explainable state

`lotus-core` must be able to explain how a current or historical portfolio state was produced:

1. source records,
2. ingestion batches,
3. validation results,
4. transaction bookings,
5. corrections,
6. prices and FX references,
7. reconciliation status,
8. snapshot identity,
9. policy context.

### 2. Command and read responsibilities are separate

Command behavior changes truth.

Read behavior exposes truth.

The target architecture uses a CQRS-lite shape:

1. command/write modules own validation and mutation,
2. read modules own projections and source-data products,
3. support/control-plane modules expose diagnostics and policy context,
4. analytics services consume read products instead of command internals.

This is not a mandate for full event sourcing.

### 3. Time is a first-class domain concept

Core must treat time as domain data, not incidental request metadata.

The target model distinguishes:

1. `trade_date`: date the trade occurred,
2. `settlement_date`: date cash/security settlement is expected or completed,
3. `booking_date`: date the transaction was booked into core,
4. `effective_date`: date a correction or state change should affect business state,
5. `valuation_date`: date prices, FX, and valuation state apply,
6. `as_of_date`: date a consumer asks the read model to represent,
7. `ingested_at`: timestamp the source record entered Lotus,
8. `observed_at`: timestamp the source system or feed says the data was observed,
9. `corrected_at`: timestamp a correction was recorded,
10. `restatement_version`: version identifier for corrected historical truth.

### 4. Source-data products are durable contracts

Analytics input contracts are not helper endpoints.

They are source-data products with:

1. stable names,
2. versioned semantics,
3. deterministic request scope,
4. clear completeness and freshness signals,
5. page/export identity where large,
6. supportability and lineage evidence.

### 5. Ingestion and reconciliation are product capabilities

In banking-grade systems, data arrival and data trust are part of the product.

`lotus-core` must make ingestion, validation, replay, reconciliation, and data quality visible enough
for downstream services and operators to make safe decisions.

### 6. The current repositories remain the target

This RFC does not authorize `lotus-core-v2`.

The target state is achieved by improving the current repository through controlled slices.

## Bounded Domains Inside `lotus-core`

The target `lotus-core` architecture is organized around domain modules. Exact package names may
evolve, but responsibilities should not blur.

| Domain module | Owns | Does not own |
| --- | --- | --- |
| Portfolio Registry | portfolio identity, lifecycle, ownership metadata, mandate references | performance or risk interpretations |
| Account and Custody | accounts, custody structures, account-to-portfolio relationships | gateway presentation or report layout |
| Transaction Booking | transaction normalization, booking, correction, cancellation, idempotency | downstream execution workflow |
| Position State | position reconstruction, holdings as-of, lot linkage where applicable | performance contribution or attribution |
| Cash Ledger | cash balances, cash movements, settlement-linked cash state | manage execution workflow |
| Instrument Master | instruments, identifiers, classifications, eligibility source attributes | advisory suitability conclusions |
| Market Data | prices, FX, market-data source lineage, valuation inputs | performance return calculations |
| Benchmark and Reference Series | benchmark assignments, benchmark constituents, index series, risk-free primitives | benchmark-relative performance conclusions |
| Ingestion and Validation | source batches, file/feed metadata, validation reports, partial rejection, replay | downstream product workflow |
| Reconciliation and Data Quality | reconciliation status, breaks, tolerances, data-quality flags, freshness | risk methodology |
| Source-Data Products | analytics inputs, snapshots, exports, read products | analytics interpretation |
| Control Plane and Supportability | capabilities, policy context, readiness, diagnostics, operator views | primary domain mutations |

## Command Model

Commands are the write side of `lotus-core`.

Target command families:

1. create or update portfolio identity,
2. create or update account/custody relationship,
3. ingest transaction batch,
4. book transaction,
5. correct or cancel transaction,
6. ingest market-data batch,
7. ingest instrument/reference-data batch,
8. assign or update benchmark,
9. run reconciliation,
10. record reconciliation break resolution,
11. replay ingestion or event records,
12. apply data-quality override where governed.

Command requirements:

1. idempotency key or deterministic source identity where repeat submission is possible,
2. request correlation id,
3. tenant or policy context where applicable,
4. validation result,
5. audit actor or source-system identity,
6. source lineage,
7. clear success, partial success, rejection, or conflict behavior,
8. no hidden downstream analytics side effects.

## Read Model

Reads expose core truth.

Target read families:

1. operational reads,
2. snapshot and simulation reads,
3. analytics input products,
4. source-data exports,
5. supportability and control-plane reads,
6. reconciliation and data-quality reads.

Read requirements:

1. explicit temporal scope,
2. explicit currency behavior where values are currency-bearing,
3. explicit source-service identity,
4. contract version,
5. request id or snapshot id,
6. completeness/freshness diagnostics where downstream safety depends on them,
7. deterministic pagination or export lifecycle for large retrieval,
8. no downstream analytics conclusions.

## Temporal Model

The target temporal model is mandatory for new core source-data products and should be backfilled into
existing contracts as they are touched.

### Required temporal vocabulary

| Term | Meaning | Required where |
| --- | --- | --- |
| `as_of_date` | business date represented by a read product | snapshots, holdings, analytics inputs |
| `valuation_date` | date used for price/FX valuation | valuation-bearing read products |
| `trade_date` | transaction trade date | transaction and position reconstruction |
| `settlement_date` | settlement date for trade/cash movement | cash, settlement, manage inputs |
| `booking_date` | date recorded in core ledger | booking and audit |
| `effective_date` | business-effective correction or state date | corrections and restatements |
| `ingested_at` | ingestion timestamp into Lotus | ingestion lineage |
| `observed_at` | source-observed timestamp | market/reference feeds |
| `corrected_at` | correction recording timestamp | corrections |
| `restatement_version` | corrected historical version id | restated snapshots and exports |

### Temporal rules

1. Do not use one generic `date` field when the domain meaning is specific.
2. Do not mix trade-date and settlement-date semantics in one field.
3. Do not let analytics consumers infer whether data is current or restated.
4. Historical corrections must create explicit lineage rather than silent overwrite semantics where
   downstream results may change.
5. Snapshot identity must encode or reference the temporal scope that produced it.

## Portfolio State Reconstruction

Target portfolio state is not just stored rows.

It is a deterministic reconstruction from:

1. portfolio identity,
2. account relationships,
3. transaction bookings,
4. cash ledger movements,
5. position state,
6. instrument attributes,
7. prices and FX,
8. corrections and restatement version,
9. reconciliation and data-quality status.

Target reconstruction outputs:

1. holdings as-of,
2. cash balances as-of,
3. positions with quantity, value, cost basis where governed, and source lineage,
4. transaction window,
5. valuation input references,
6. data-quality state,
7. reconciliation state,
8. snapshot identity.

Rules:

1. reconstruction must be deterministic for the same source scope,
2. downstream services must be able to identify whether a result used restated data,
3. corrections must preserve enough lineage for audit and recalculation,
4. position state must not embed performance attribution or risk interpretation.

## Canonical Source-Data Products

The target architecture defines the following source-data products.

These products may be implemented incrementally, but new consumer-facing contracts should align to this
catalog rather than creating ad hoc endpoint shapes.

| Product | Primary consumers | Purpose |
| --- | --- | --- |
| `PortfolioStateSnapshot` | gateway, advise, manage, support, simulation consumers | governed as-of portfolio state bundle |
| `HoldingsAsOf` | gateway, advise, manage, report | holdings and cash state for product/support use |
| `TransactionLedgerWindow` | performance, risk, report, support | deterministic transaction history window |
| `PositionTimeseriesInput` | performance, risk | canonical position timeseries inputs |
| `PortfolioTimeseriesInput` | performance, risk | canonical portfolio-level timeseries inputs |
| `MarketDataWindow` | performance, risk, manage, advise | prices and FX source inputs |
| `InstrumentReferenceBundle` | gateway, advise, risk, performance | instrument metadata and enrichment source attributes |
| `BenchmarkAssignment` | performance, gateway, risk | governed benchmark relationship for a portfolio |
| `BenchmarkConstituentWindow` | performance, risk | benchmark constituent inputs |
| `IndexSeriesWindow` | performance, risk | index time-series source inputs |
| `RiskFreeSeriesWindow` | performance, risk | risk-free source primitive |
| `ReconciliationEvidenceBundle` | support, gateway, report, operators | reconciliation status and break evidence |
| `DataQualityCoverageReport` | performance, risk, gateway, support | completeness, freshness, and quality diagnostics |
| `IngestionEvidenceBundle` | support, operations, audit | source batch, validation, replay, and rejection evidence |

## API Target Topology

The target API topology should be easy to explain.

### Public downstream read plane

Owns:

1. operational portfolio reads,
2. holdings and transaction reads,
3. lookups and source reference reads.

Primary consumers:

1. `lotus-gateway`,
2. `lotus-advise`,
3. `lotus-manage`,
4. `lotus-report`,
5. support tooling.

### Analytics input plane

Owns:

1. portfolio timeseries,
2. position timeseries,
3. benchmark and reference inputs,
4. risk-free inputs,
5. export and paging contracts.

Primary consumers:

1. `lotus-performance`,
2. `lotus-risk`.

### Snapshot and simulation plane

Owns:

1. core snapshots,
2. simulation source bundles,
3. projected state inputs where core-owned.

Primary consumers:

1. `lotus-advise`,
2. `lotus-manage`,
3. `lotus-gateway`,
4. support tooling.

### Write and ingestion plane

Owns:

1. source ingestion,
2. transaction booking,
3. corrections,
4. replay,
5. validation reports.

Primary consumers:

1. upstream adapters,
2. operations,
3. governed internal tooling.

### Control plane and supportability plane

Owns:

1. capabilities,
2. effective policy,
3. readiness,
4. data-quality coverage,
5. reconciliation evidence,
6. operator diagnostics.

Primary consumers:

1. gateway,
2. support tooling,
3. CI/QA validators,
4. platform operations.

## Ingestion And Source Lineage

Target ingestion behavior:

1. every source batch has a durable batch identity,
2. every record can be traced to a source file, feed, manual action, or integration event,
3. validation reports distinguish accepted, rejected, quarantined, and partially accepted records,
4. ingestion is idempotent by source identity or idempotency key,
5. replay is explicit and auditable,
6. dead-letter and repair flows are visible to operators,
7. source-system identity is preserved through downstream read products.

Target ingestion evidence:

1. `source_system`,
2. `source_batch_id`,
3. `source_record_id`,
4. `ingestion_run_id`,
5. `validation_report_id`,
6. `replay_run_id` where applicable,
7. accepted/rejected record counts,
8. rejection reasons,
9. operator or automation identity.

## Reconciliation And Data Quality

Target reconciliation behavior:

1. reconciliation is a core product capability,
2. cash, position, transaction, and market-data reconciliation status is queryable,
3. breaks carry age, severity, owner, tolerance, and resolution state,
4. downstream consumers can detect whether data is reconciled, stale, partial, or blocked,
5. data-quality state is included in source-data products when safety depends on it.

Target statuses:

1. `COMPLETE`,
2. `PARTIAL`,
3. `STALE`,
4. `UNRECONCILED`,
5. `BREAK_OPEN`,
6. `BLOCKED`,
7. `UNKNOWN`.

Status naming may be refined by implementation RFCs, but the target contract must preserve these
business distinctions.

## Market, Instrument, Benchmark, And Reference Data

The target architecture treats reference data as source truth, not metadata decoration.

Core-owned reference primitives:

1. instrument identity,
2. security identifiers,
3. classifications,
4. currency,
5. issuer and sector/region attributes where sourced,
6. eligibility/source attributes where core owns the evidence,
7. prices,
8. FX rates,
9. benchmark assignment,
10. benchmark constituent data,
11. index series,
12. risk-free series.

Rules:

1. source attributes may feed suitability, risk, and performance, but those downstream conclusions are
   not core-owned,
2. benchmark source data belongs in core when it is foundational input,
3. benchmark-relative analytics belong in `lotus-performance` and `lotus-risk`,
4. stale or partial reference data must be visible in supportability and source-data products.

## Eventing

Events are useful for propagation and audit, but they are not a replacement for governed read
contracts.

Target event families:

1. portfolio created or updated,
2. account relationship changed,
3. transaction batch ingested,
4. transaction booked,
5. transaction corrected or cancelled,
6. portfolio state restated,
7. market-data batch ingested,
8. benchmark assignment changed,
9. reconciliation completed,
10. data-quality status changed,
11. source-data export completed,
12. replay completed.

Event rules:

1. events must be idempotent for consumers,
2. events must include correlation and source identity,
3. event schema must be versioned,
4. events should notify consumers that source truth changed; consumers should still use governed read
   contracts for state retrieval,
5. eventing does not justify duplicating core-owned state into downstream services without a clear
   projection contract.

## OpenAPI, Vocabulary, And Contract Governance

RFC-0083 relies on RFC-0067 and RFC-0082.

Target API governance:

1. every downstream-facing route has an RFC-0082 family,
2. every route description states the core-owned semantic responsibility,
3. request and response schemas use platform vocabulary,
4. temporal fields use the canonical temporal vocabulary,
5. source-data products expose provenance and completeness consistently,
6. new aliases are rejected unless documented as intentional,
7. deprecations are explicit while the estate is pre-live.

## Endpoint Consolidation Policy

Because Lotus is pre-live, core should prefer correction over compatibility.

Endpoint consolidation rules:

1. remove duplicate endpoint shapes when one governed source-data product can serve the need,
2. replace gateway-friendly convenience shapes with source-data products plus gateway composition,
3. avoid creating special-purpose endpoints for one consumer unless the business domain requires it,
4. use export jobs for large retrieval rather than proliferating bulk variants,
5. keep compatibility aliases only when a short-lived migration slice needs them.

## Relationship To RFC-0082

RFC-0082 answers:

> What may `lotus-core` own, and what must stay downstream?

RFC-0083 answers:

> What should `lotus-core` look like internally and contractually so it can be a banking-grade system
> of record?

RFC-0082 is the boundary guardrail.

RFC-0083 is the target architecture blueprint.

Implementation slices must comply with both.

## Implementation Program

RFC-0083 should be implemented through small, reviewable slices.

### Slice 0: Baseline inventory and acceptance model

Deliverables:

1. align RFC-0083 with current RFC-0082 route inventory,
2. identify current modules and routes that map cleanly to target domains,
3. identify stale, duplicate, or ambiguous route families,
4. define acceptance evidence for each later slice.

Minimum validation:

1. docs proof,
2. route inventory proof,
3. no runtime behavior change.

### Slice 1: Temporal vocabulary and schema policy

Deliverables:

1. canonical temporal vocabulary in core docs and OpenAPI guidance,
2. route/schema inventory for ambiguous date fields,
3. test or validator for new ambiguous temporal fields where practical.

Minimum validation:

1. OpenAPI/vocabulary proof if schema metadata changes,
2. targeted contract tests where route docs or schemas change.

### Slice 2: Command/read route classification

Deliverables:

1. command/write route classification,
2. read/source-data product classification,
3. support/control-plane classification,
4. tests that fail when downstream-facing routes lack a family.

Minimum validation:

1. `lotus-core` targeted route/OpenAPI tests,
2. RFC-0067 vocabulary checks where affected.

### Slice 3: Portfolio state reconstruction target model

Deliverables:

1. reconstruction model document,
2. lineage requirements for holdings, cash, and transaction-derived state,
3. deterministic snapshot identity rules,
4. gaps against current implementation.

Minimum validation:

1. focused unit tests for reconstruction semantics where code changes,
2. contract tests for snapshot identity and lineage where API changes.

### Slice 4: Ingestion and source-lineage hardening

Deliverables:

1. source batch identity model,
2. validation report contract,
3. partial rejection and replay contract,
4. DLQ/repair supportability posture.

Minimum validation:

1. ingestion unit/integration tests,
2. replay/DLQ tests where runtime changes,
3. migration smoke if persistence changes.

### Slice 5: Reconciliation and data-quality model

Deliverables:

1. reconciliation status vocabulary,
2. break model,
3. data-quality coverage contract,
4. source-data product supportability fields.

Minimum validation:

1. reconciliation unit/integration tests,
2. contract tests for supportability payloads,
3. downstream consumer tests if response semantics change.

### Slice 6: Source-data product catalog implementation

Deliverables:

1. implement or normalize priority source-data products,
2. align current analytics inputs to the catalog,
3. document paging/export behavior,
4. retire duplicate convenience shapes where safe.

Minimum validation:

1. `lotus-performance` and `lotus-risk` consumer contract tests,
2. `lotus-core` OpenAPI/vocabulary checks,
3. performance characterization for large retrieval paths.

### Slice 7: Market and reference data hardening

Deliverables:

1. instrument master target alignment,
2. price and FX source-lineage alignment,
3. benchmark/index/risk-free source-product alignment,
4. freshness/completeness diagnostics.

Minimum validation:

1. market/reference data unit tests,
2. downstream analytics input tests,
3. data-quality coverage tests.

### Slice 8: Endpoint consolidation and deprecation cleanup

Deliverables:

1. remove or deprecate duplicate route families,
2. replace convenience routes with source-data products where appropriate,
3. update gateway/performance/risk/advise/manage consumers,
4. update all repo-local contexts that reference removed or changed routes.

Minimum validation:

1. affected repo PR Merge Gate when runtime contracts change,
2. platform end-to-end proof when gateway/workbench behavior changes.

### Slice 9: Eventing and supportability hardening

Deliverables:

1. event family definitions,
2. event schema governance,
3. operator diagnostics,
4. supportability evidence bundles.

Minimum validation:

1. event contract tests where events exist,
2. supportability API tests,
3. platform validation where operations workflows change.

### Slice 10: Production-readiness closure

Deliverables:

1. final route inventory,
2. final source-data product catalog,
3. final deprecation list,
4. downstream consumer conformance proof,
5. platform context and onboarding updates.

Minimum validation:

1. `lotus-core` PR Merge Gate,
2. affected consumer PR Merge Gates,
3. platform end-to-end validation where canonical product flows depend on the changes.

## Validation And Evidence Model

RFC-0083 implementation uses the RFC-0072 lane model.

| Change type | Minimum lane | Escalation trigger |
| --- | --- | --- |
| target architecture docs only | Feature Lane docs proof | none unless repository truth changes |
| route metadata or OpenAPI descriptions | Feature Lane plus OpenAPI/vocabulary proof | PR Merge Gate when schemas or behavior change |
| command/read classification tests | Feature Lane targeted tests | PR Merge Gate if route behavior changes |
| persistence, ingestion, reconciliation, or migration changes | PR Merge Gate | Main releasability when production posture changes |
| downstream consumer contract changes | affected repo Feature Lane | affected repo PR Merge Gate when runtime coupling changes |
| gateway/workbench-facing behavior changes | affected backend and gateway gates | platform end-to-end validation |

## Acceptance Criteria

RFC-0083 is implemented when all of the following are true.

1. `lotus-core` has an approved system-of-record target architecture.
2. Current core modules and route families are mapped to target bounded domains.
3. Core command/write behavior is distinguishable from read/source-data behavior.
4. Canonical temporal vocabulary is enforced in new or touched contracts.
5. Portfolio state reconstruction has deterministic lineage and snapshot identity rules.
6. Ingestion contracts expose source lineage, validation, replay, and rejection evidence.
7. Reconciliation and data-quality status are queryable and usable by downstream services.
8. Priority source-data products exist or current equivalents are formally mapped.
9. Duplicate or ambiguous endpoint families are removed, deprecated, or explicitly governed.
10. Downstream consumers use source-data products and do not depend on core-owned analytics
    conclusions.
11. Platform context and repo-local contexts reflect the target architecture.
12. No gRPC or parallel `lotus-core-v2` path is introduced without separate evidence and approval.

## Non-Goals

This RFC does not:

1. implement all target architecture slices immediately,
2. authorize a new `lotus-core-v2`,
3. move performance or risk analytics into core,
4. move advisory or management workflow into core,
5. mandate event sourcing,
6. mandate gRPC,
7. require preserving weak pre-live compatibility routes indefinitely.

## Open Questions

1. Which current `lotus-core` persistence tables already map cleanly to the target bounded domains?
2. Which temporal fields are currently ambiguous and should be fixed first?
3. Which source-data product should be implemented first after route classification?
4. Which current reporting, cashflow, projection, or enrichment routes should be retired rather than
   formalized?
5. Should platform CI eventually validate source-data product catalog completeness across consumers?

## Recommended Next Actions

1. Approve RFC-0083 as the master `lotus-core` target architecture blueprint.
2. Create a repo-local `lotus-core` target-state gap analysis against this RFC.
3. Implement Slice 0 and Slice 1 before touching runtime behavior.
4. Keep RFC-0082 and RFC-0083 linked in all future `lotus-core` boundary and source-data work.
