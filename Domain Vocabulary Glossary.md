# Domain Vocabulary Glossary

This document is the central source of truth for cross-platform domain language.
All repositories must align request/response models, service names, logs, and docs with this glossary.

## Core Entities

- `portfolio_id`: Canonical portfolio identifier (string).
- `security_id`: Canonical instrument/security identifier (string).
- `instrument`: Tradable security metadata record (static + reference attributes).
- `transaction`: Immutable booking event affecting positions/cash.
- `position`: Derived holdings state from processed transactions.
- `valuation_point`: Daily valuation input row (`begin_mv`, flows, fees, `end_mv`).
- `portfolio_timeseries`: Daily portfolio-level derived state.
- `position_timeseries`: Daily position-level derived state.
- `reporting_snapshot`: Report-ready aggregation output for one portfolio and one `as_of_date`.
- `reporting_row`: Atomic reporting metric row (`bucket`, `metric`, `value`).
- `decision_readiness`: Backend-derived readiness state for advisory decisioning (`READY`, `PENDING`, `ATTENTION`).
- `concentration_signal`: Portfolio concentration category derived from HHI (`LOW`, `MEDIUM`, `HIGH`, `UNKNOWN`).
- `stateful_mode`: Execution mode where service fetches dependent inputs from upstream service APIs.
- `stateless_mode`: Execution mode where caller provides required inputs directly in request payload.
- `api_driven_integration`: Cross-service interaction model using only explicit service APIs/contracts.
- `intermediate_precision`: High-precision `Decimal` representation used during internal calculations before output shaping.
- `final_output_precision`: Canonical quantized precision applied at API/report/export boundaries.
- `rounding_policy_version`: Versioned identifier of the active platform rounding and precision standard.
- `financial_correctness`: Mandatory deterministic behavior for monetary and analytics outputs under equivalent input scenarios.

## Service Responsibilities

- `lotus-core` (`lotus-core`):
  - Core data processing and serving.
  - Ledger/reference/market/position/valuation/time-series ownership.
- `lotus-performance` (`lotus-performance`):
  - Advanced analytics ownership.
  - Performance, attribution, risk, and higher-order analytics.
  - Sources core data from lotus-core via APIs; no direct lotus-core database coupling.
  - Supports `stateful_mode` and `stateless_mode` execution patterns.
- `lotus-manage` (`lotus-advise`):
  - Deterministic decisioning/rebalance simulation and policy gates.
  - Sources core data from lotus-core via APIs for stateful flows.
  - Supports `stateless_mode` for isolated simulation and testing.
- `lotus-gateway` (`lotus-gateway`):
  - Orchestration contract for UI.
  - No domain reimplementation.
- `lotus-report` (`lotus-report`):
  - Reporting/aggregation composition layer.
  - Consumes lotus-core core data and lotus-performance analytics to emit report-ready rows.
  - Owns reporting and aggregation API endpoints.

## Contract Terms

- `core-snapshot`:
  - lotus-core data-serving integration contract.
  - Use only for core snapshot sections (non-advanced analytics).
- `pas-input`:
  - lotus-core raw input contract consumed by lotus-performance analytics engines.
  - Replaces ambiguous `pas-snapshot` analytics wording.
- `analytics contract`:
  - Consumer-facing analytics payload owned by lotus-performance.
- `reporting snapshot contract`:
  - Report-ready row set returned by lotus-report for one portfolio/date.
  - lotus-gateway/UI consume this for reporting tables and downstream report generation.

## Canonical Performance Period Vocabulary

The platform-governed business period vocabulary for portfolio and performance analytics is:

- `MTD`
  - Month to date.
  - Window start is the first calendar day of the anchor month.
- `QTD`
  - Quarter to date.
  - Window start is the first calendar day of the anchor quarter.
- `YTD`
  - Year to date.
  - Window start is January 1 of the anchor year.
- `1Y`
  - Trailing one-year window.
  - Window start is one calendar year before the anchor date plus one day.
- `3Y`
  - Trailing three-year window.
  - Window start is three calendar years before the anchor date plus one day.
- `5Y`
  - Trailing five-year window.
  - Window start is five calendar years before the anchor date plus one day.
- `SI`
  - Since inception.
  - Window start is the resolved portfolio or strategy inception date.
- `EXPLICIT`
  - Caller-provided explicit date window.
  - Requires both start and end boundaries where the API contract expects a full explicit range.

Required governance rules:

1. `YTD` and `1Y` are not interchangeable.
2. `QTD` is a calendar-quarter-to-date concept, not a trailing three-month concept.
3. All APIs that emit period-shaped analytics must expose resolved date boundaries when available.
4. Gateway/BFF layers may translate canonical business periods into upstream request shapes, but must not change business meaning.
5. No service may silently redefine a canonical period token locally.

## Naming Rules

1. Use `snake_case` for JSON fields across services; legacy aliases are not allowed.
2. Use `portfolio_id`, never `portfolio_number`, in cross-service contracts.
3. Use `as_of_date` consistently for business-date anchors.
4. Use `consumer_system` for calling system identity.
5. Avoid overloaded terms (`snapshot` for analytics execution mode is prohibited).
6. When term is reporting-specific, prefix with `reporting_` (`reporting_snapshot`, `reporting_row`).
7. Cross-service data access must be `api_driven_integration` (no shared databases).

## Change Control

1. New shared terms require an RFC entry in `lotus-platform/rfcs`.
2. Any contract rename must update:
   - API models
   - OpenAPI docs
   - integration tests
   - this glossary
3. Run vocabulary baseline validation after glossary or contract changes:
   - `powershell -ExecutionPolicy Bypass -File automation/Validate-Domain-Vocabulary.ps1`

