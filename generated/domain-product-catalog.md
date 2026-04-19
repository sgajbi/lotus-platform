# Lotus Domain Product Catalog

This file is generated from governed domain-data-product declarations.

- Generated at UTC: `2026-04-19T00:00:00Z`
- Source declaration directory: `platform-contracts/domain-data-products`
- Product count: `22`
- Dependency count: `12`

## Products

| Product | Producer | Version | Family | Lifecycle | Approved Consumers | Routes |
| --- | --- | --- | --- | --- | --- | --- |
| `BenchmarkAssignment` | `lotus-core` | `v1` | `analytics_input` | `active` | lotus-performance, lotus-risk, lotus-report | /integration/portfolios/{portfolio_id}/benchmark-assignment |
| `BenchmarkConstituentWindow` | `lotus-core` | `v1` | `analytics_input` | `active` | lotus-performance, lotus-risk | /integration/benchmarks/{benchmark_id}/composition-window |
| `DataQualityCoverageReport` | `lotus-core` | `v1` | `supportability_and_control_plane` | `active` | lotus-performance, lotus-risk, lotus-gateway, lotus-manage | /integration/benchmarks/{benchmark_id}/coverage, /integration/reference/risk-free-series/coverage |
| `HoldingsAsOf` | `lotus-core` | `v1` | `operational_source_data` | `active` | lotus-gateway, lotus-risk, lotus-report, lotus-manage, lotus-advise | /portfolios/{portfolio_id}/positions, /portfolios/{portfolio_id}/cash-balances |
| `IndexSeriesWindow` | `lotus-core` | `v1` | `analytics_input` | `active` | lotus-performance, lotus-risk | /integration/indices/{index_id}/price-series, /integration/indices/{index_id}/return-series |
| `IngestionEvidenceBundle` | `lotus-core` | `v1` | `supportability_and_control_plane` | `active` | lotus-gateway, lotus-manage, lotus-report | /lineage/portfolios/{portfolio_id}/keys, /support/portfolios/{portfolio_id}/reprocessing-keys, /support/portfolios/{portfolio_id}/reprocessing-jobs |
| `InstrumentReferenceBundle` | `lotus-core` | `v1` | `analytics_input` | `active` | lotus-performance, lotus-risk, lotus-gateway, lotus-advise | /integration/instruments/enrichment-bulk, /integration/reference/classification-taxonomy |
| `MarketDataWindow` | `lotus-core` | `v1` | `analytics_input` | `active` | lotus-performance, lotus-risk | /integration/benchmarks/{benchmark_id}/market-series |
| `PortfolioAnalyticsReference` | `lotus-core` | `v1` | `analytics_input` | `active` | lotus-performance, lotus-risk | /integration/portfolios/{portfolio_id}/analytics/reference |
| `PortfolioStateSnapshot` | `lotus-core` | `v1` | `simulation_and_projected_state` | `active` | lotus-gateway, lotus-advise, lotus-manage, lotus-risk | /integration/portfolios/{portfolio_id}/core-snapshot |
| `PortfolioTimeseriesInput` | `lotus-core` | `v1` | `analytics_input` | `active` | lotus-performance, lotus-risk | /integration/portfolios/{portfolio_id}/analytics/portfolio-timeseries |
| `PositionTimeseriesInput` | `lotus-core` | `v1` | `analytics_input` | `active` | lotus-performance, lotus-risk | /integration/portfolios/{portfolio_id}/analytics/position-timeseries |
| `ReconciliationEvidenceBundle` | `lotus-core` | `v1` | `supportability_and_control_plane` | `active` | lotus-performance, lotus-risk, lotus-gateway, lotus-manage | /support/portfolios/{portfolio_id}/reconciliation-runs, /support/portfolios/{portfolio_id}/reconciliation-runs/{run_id}/findings |
| `RiskFreeSeriesWindow` | `lotus-core` | `v1` | `analytics_input` | `active` | lotus-performance, lotus-risk | /integration/reference/risk-free-series |
| `TransactionLedgerWindow` | `lotus-core` | `v1` | `operational_source_data` | `active` | lotus-gateway, lotus-report, lotus-manage, lotus-risk | /portfolios/{portfolio_id}/transactions |
| `BenchmarkExposureContext` | `lotus-performance` | `v1` | `analytics_output` | `active` | lotus-risk | /integration/benchmarks/exposure-context |
| `ReturnsSeriesBundle` | `lotus-performance` | `v1` | `analytics_output` | `active` | lotus-risk | /integration/returns/series, /integration/returns/series/results/{calculation_id} |
| `ConcentrationRiskReport` | `lotus-risk` | `v1` | `analytics_output` | `active` | lotus-gateway | /analytics/risk/concentration |
| `DrawdownAnalyticsReport` | `lotus-risk` | `v1` | `analytics_output` | `active` | lotus-gateway | /analytics/risk/drawdown |
| `HistoricalRiskAttributionReport` | `lotus-risk` | `v1` | `analytics_output` | `active` | lotus-gateway | /analytics/risk/historical-attribution |
| `RiskMetricsReport` | `lotus-risk` | `v1` | `analytics_output` | `active` | lotus-gateway | /analytics/risk/calculate |
| `RollingRiskMetricsReport` | `lotus-risk` | `v1` | `analytics_output` | `active` | lotus-gateway | /analytics/risk/rolling-metrics |

## Dependencies

| Consumer | Upstream Product | Producer | Version | Mode | Failure Posture |
| --- | --- | --- | --- | --- | --- |
| `lotus-performance` | `BenchmarkAssignment` | `lotus-core` | `v1` | `api_read` | `fail_closed` |
| `lotus-performance` | `InstrumentReferenceBundle` | `lotus-core` | `v1` | `paged_api_read` | `fail_closed` |
| `lotus-performance` | `MarketDataWindow` | `lotus-core` | `v1` | `paged_api_read` | `fail_closed` |
| `lotus-performance` | `PortfolioAnalyticsReference` | `lotus-core` | `v1` | `api_read` | `fail_closed` |
| `lotus-performance` | `PortfolioTimeseriesInput` | `lotus-core` | `v1` | `api_read` | `fail_closed` |
| `lotus-performance` | `RiskFreeSeriesWindow` | `lotus-core` | `v1` | `api_read` | `degrade_to_partial` |
| `lotus-risk` | `InstrumentReferenceBundle` | `lotus-core` | `v1` | `paged_api_read` | `fail_closed` |
| `lotus-risk` | `PortfolioStateSnapshot` | `lotus-core` | `v1` | `api_read` | `fail_closed` |
| `lotus-risk` | `PositionTimeseriesInput` | `lotus-core` | `v1` | `api_read` | `fail_closed` |
| `lotus-risk` | `RiskFreeSeriesWindow` | `lotus-core` | `v1` | `api_read` | `degrade_to_partial` |
| `lotus-risk` | `BenchmarkExposureContext` | `lotus-performance` | `v1` | `paged_api_read` | `degrade_to_partial` |
| `lotus-risk` | `ReturnsSeriesBundle` | `lotus-performance` | `v1` | `api_read` | `fail_closed` |
