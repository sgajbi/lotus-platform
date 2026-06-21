# Lotus Domain Product Catalog

This file is generated from governed domain-data-product declarations.

- Generated at UTC: `2026-04-19T00:00:00Z`
- Source declaration directory: `federated:domain-product-source-manifest`
- Product count: `70`
- Dependency count: `46`

## Products

| Product | Producer | Version | Family | Lifecycle | Approved Consumers | Routes |
| --- | --- | --- | --- | --- | --- | --- |
| `AdvisorCockpitOperatingSnapshot` | `lotus-advise` | `v1` | `workflow_and_decision_state` | `active` | lotus-gateway, lotus-workbench | /advisory/cockpit/snapshot, /advisory/cockpit/supportability |
| `AdvisoryActionItemRegister` | `lotus-advise` | `v1` | `workflow_and_decision_state` | `active` | lotus-gateway, lotus-workbench | /advisory/cockpit/actions, /advisory/cockpit/actions/{action_item_id}, /advisory/cockpit/actions/{action_item_id}/acknowledgements |
| `AdvisoryCopilotInteractionRecord` | `lotus-advise` | `v1` | `workflow_and_decision_state` | `active` | lotus-gateway, lotus-workbench | /advisory/copilot/evidence-packets/from-proposal-version, /advisory/copilot/actions, /advisory/copilot/actions/{run_id}, /advisory/copilot/actions/{run_id}/reviews, /advisory/copilot/supportability, /advisory/proposals/{proposal_id}/versions/{version_id}/copilot-runs |
| `AdvisoryPolicyEvaluationRecord` | `lotus-advise` | `v1` | `workflow_and_decision_state` | `active` | lotus-gateway, lotus-report, lotus-render, lotus-archive, lotus-workbench, lotus-ai | /advisory/proposals/{proposal_id}/versions/{proposal_version_id}/policy-evaluations, /advisory/policy-evaluations/review-queue, /advisory/policy-evaluations/{evaluation_id}, /advisory/policy-evaluations/{evaluation_id}/replay, /advisory/policy-evaluations/{evaluation_id}/events, /advisory/policy-evaluations/{evaluation_id}/lineage, /advisory/policy-evaluations/{evaluation_id}/sign-off-package, /advisory/policy-evaluations/{evaluation_id}/workflow, /advisory/policy-evaluations/{evaluation_id}/sign-off-decisions, /advisory/policy-evaluations/{evaluation_id}/report-packages, /advisory/policy-evaluations/{evaluation_id}/ai-evidence |
| `AdvisoryProposalLifecycleRecord` | `lotus-advise` | `v1` | `workflow_and_decision_state` | `active` | lotus-gateway | /advisory/proposals/{proposal_id}, /advisory/proposals/{proposal_id}/versions/{version_no}, /advisory/proposals/{proposal_id}/timeline, /advisory/proposals/{proposal_id}/approvals |
| `AdvisoryProposalMemoEvidencePack` | `lotus-advise` | `v1` | `reporting_and_evidence` | `active` | lotus-gateway, lotus-report, lotus-render, lotus-archive, lotus-workbench | /advisory/proposals/{proposal_id}/versions/{version_no}/memos, /advisory/proposals/{proposal_id}/versions/{version_no}/memos/{memo_id}, /advisory/proposals/{proposal_id}/versions/{version_no}/memos/{memo_id}/projection, /advisory/proposals/{proposal_id}/versions/{version_no}/memos/{memo_id}/review, /advisory/proposals/{proposal_id}/versions/{version_no}/memos/{memo_id}/report-package-events, /advisory/proposals/{proposal_id}/versions/{version_no}/memos/{memo_id}/report-packages, /advisory/proposals/{proposal_id}/versions/{version_no}/memos/{memo_id}/ai-commentary, /advisory/proposals/{proposal_id}/memos/lineage, /advisory/proposals/{proposal_id}/versions/{version_no}/memos/{memo_id}/replay-evidence |
| `ProposalNarrativeEvidence` | `lotus-advise` | `v1` | `workflow_and_decision_state` | `active` | lotus-gateway, lotus-report, lotus-render, lotus-archive | /advisory/proposals/artifact, /advisory/proposals/{proposal_id}/versions/{version_no}/narrative, /advisory/proposals/{proposal_id}/versions/{version_no}/narrative/regenerate, /advisory/proposals/{proposal_id}/versions/{version_no}/narrative/review, /advisory/proposals/{proposal_id}/versions/{version_no}/replay-evidence, /advisory/proposals/{proposal_id}/report-requests, /advisory/proposals/{proposal_id}/delivery-summary |
| `TacticalHouseViewAffectedCohort` | `lotus-advise` | `v1` | `cohort_membership` | `active` | lotus-manage | /advisory/tactical-house-view/cohorts/evaluate |
| `BenchmarkAssignment` | `lotus-core` | `v1` | `analytics_input` | `active` | lotus-performance, lotus-risk, lotus-report, lotus-manage | /integration/portfolios/{portfolio_id}/benchmark-assignment |
| `BenchmarkConstituentWindow` | `lotus-core` | `v1` | `analytics_input` | `active` | lotus-performance, lotus-risk | /integration/benchmarks/{benchmark_id}/composition-window |
| `CioModelChangeAffectedCohort` | `lotus-core` | `v1` | `dpm_source_data` | `active` | lotus-manage | /integration/model-portfolios/{model_portfolio_id}/affected-mandates |
| `ClientIncomeNeedsSchedule` | `lotus-core` | `v1` | `dpm_source_data` | `active` | lotus-manage | /integration/portfolios/{portfolio_id}/client-income-needs-schedule |
| `ClientRestrictionProfile` | `lotus-core` | `v1` | `dpm_source_data` | `active` | lotus-manage | /integration/portfolios/{portfolio_id}/client-restriction-profile |
| `ClientTaxProfile` | `lotus-core` | `v1` | `dpm_source_data` | `active` | lotus-manage | /integration/portfolios/{portfolio_id}/client-tax-profile |
| `ClientTaxRuleSet` | `lotus-core` | `v1` | `dpm_source_data` | `active` | lotus-manage | /integration/portfolios/{portfolio_id}/client-tax-rule-set |
| `DataQualityCoverageReport` | `lotus-core` | `v1` | `supportability_and_control_plane` | `active` | lotus-performance, lotus-risk, lotus-gateway, lotus-manage | /integration/benchmarks/{benchmark_id}/coverage, /integration/reference/risk-free-series/coverage |
| `DiscretionaryMandateBinding` | `lotus-core` | `v1` | `dpm_source_data` | `active` | lotus-manage | /integration/portfolios/{portfolio_id}/mandate-binding |
| `DpmModelPortfolioTarget` | `lotus-core` | `v1` | `dpm_source_data` | `active` | lotus-manage | /integration/model-portfolios/{model_portfolio_id}/targets |
| `DpmPortfolioUniverseCandidate` | `lotus-core` | `v1` | `dpm_source_data` | `active` | lotus-manage | /integration/dpm/portfolio-universe/candidates |
| `DpmSourceReadiness` | `lotus-core` | `v1` | `dpm_source_data` | `active` | lotus-manage, lotus-gateway | /integration/portfolios/{portfolio_id}/dpm-source-readiness |
| `ExternalCurrencyExposure` | `lotus-core` | `v1` | `dpm_source_data` | `active` | lotus-manage | /integration/portfolios/{portfolio_id}/external-currency-exposure |
| `ExternalEligibleHedgeInstrument` | `lotus-core` | `v1` | `dpm_source_data` | `active` | lotus-manage | /integration/portfolios/{portfolio_id}/external-eligible-hedge-instruments |
| `ExternalFXForwardCurve` | `lotus-core` | `v1` | `dpm_source_data` | `active` | lotus-manage | /integration/market-data/external-fx-forward-curve |
| `ExternalHedgeExecutionReadiness` | `lotus-core` | `v1` | `dpm_source_data` | `active` | lotus-manage | /integration/portfolios/{portfolio_id}/external-hedge-execution-readiness |
| `ExternalHedgePolicy` | `lotus-core` | `v1` | `dpm_source_data` | `active` | lotus-manage | /integration/portfolios/{portfolio_id}/external-hedge-policy |
| `ExternalOrderExecutionAcknowledgement` | `lotus-core` | `v1` | `dpm_source_data` | `active` | lotus-manage | /integration/portfolios/{portfolio_id}/external-order-execution-acknowledgement |
| `HoldingsAsOf` | `lotus-core` | `v1` | `operational_source_data` | `active` | lotus-gateway, lotus-risk, lotus-report, lotus-manage, lotus-advise | /portfolios/{portfolio_id}/positions, /portfolios/{portfolio_id}/cash-balances |
| `IndexSeriesWindow` | `lotus-core` | `v1` | `analytics_input` | `active` | lotus-performance, lotus-risk | /integration/indices/{index_id}/price-series, /integration/indices/{index_id}/return-series |
| `IngestionEvidenceBundle` | `lotus-core` | `v1` | `supportability_and_control_plane` | `active` | lotus-gateway, lotus-manage, lotus-report | /lineage/portfolios/{portfolio_id}/keys, /support/portfolios/{portfolio_id}/reprocessing-keys, /support/portfolios/{portfolio_id}/reprocessing-jobs |
| `InstrumentEligibilityProfile` | `lotus-core` | `v1` | `dpm_source_data` | `active` | lotus-manage | /integration/instruments/eligibility-bulk |
| `InstrumentReferenceBundle` | `lotus-core` | `v1` | `analytics_input` | `active` | lotus-performance, lotus-risk, lotus-gateway, lotus-advise | /integration/instruments/enrichment-bulk, /integration/reference/classification-taxonomy |
| `LiquidityReserveRequirement` | `lotus-core` | `v1` | `dpm_source_data` | `active` | lotus-manage | /integration/portfolios/{portfolio_id}/liquidity-reserve-requirement |
| `MarketDataCoverageWindow` | `lotus-core` | `v1` | `dpm_source_data` | `active` | lotus-manage | /integration/market-data/coverage |
| `MarketDataWindow` | `lotus-core` | `v1` | `analytics_input` | `active` | lotus-performance, lotus-risk | /integration/benchmarks/{benchmark_id}/market-series |
| `PlannedWithdrawalSchedule` | `lotus-core` | `v1` | `dpm_source_data` | `active` | lotus-manage | /integration/portfolios/{portfolio_id}/planned-withdrawal-schedule |
| `PortfolioAnalyticsReference` | `lotus-core` | `v1` | `analytics_input` | `active` | lotus-performance, lotus-risk | /integration/portfolios/{portfolio_id}/analytics/reference |
| `PortfolioCashMovementSummary` | `lotus-core` | `v1` | `operational_source_data` | `active` | lotus-gateway, lotus-report, lotus-manage | /portfolios/{portfolio_id}/cash-movement-summary |
| `PortfolioCashflowProjection` | `lotus-core` | `v1` | `operational_source_data` | `active` | lotus-gateway, lotus-report, lotus-manage | /portfolios/{portfolio_id}/cashflow-projection |
| `PortfolioLiquidityLadder` | `lotus-core` | `v1` | `operational_source_data` | `active` | lotus-gateway, lotus-report, lotus-manage, lotus-advise | /portfolios/{portfolio_id}/liquidity-ladder |
| `PortfolioManagerBookMembership` | `lotus-core` | `v1` | `dpm_source_data` | `active` | lotus-manage | /integration/portfolio-manager-books/{portfolio_manager_id}/memberships |
| `PortfolioRealizedTaxSummary` | `lotus-core` | `v1` | `operational_source_data` | `active` | lotus-gateway, lotus-report, lotus-manage | /portfolios/{portfolio_id}/realized-tax-summary |
| `PortfolioStateSnapshot` | `lotus-core` | `v1` | `simulation_and_projected_state` | `active` | lotus-gateway, lotus-advise, lotus-manage, lotus-risk | /integration/portfolios/{portfolio_id}/core-snapshot |
| `PortfolioTaxLotWindow` | `lotus-core` | `v1` | `dpm_source_data` | `active` | lotus-manage | /integration/portfolios/{portfolio_id}/tax-lots |
| `PortfolioTimeseriesInput` | `lotus-core` | `v1` | `analytics_input` | `active` | lotus-performance, lotus-risk | /integration/portfolios/{portfolio_id}/analytics/portfolio-timeseries |
| `PositionTimeseriesInput` | `lotus-core` | `v1` | `analytics_input` | `active` | lotus-performance, lotus-risk | /integration/portfolios/{portfolio_id}/analytics/position-timeseries |
| `ReconciliationEvidenceBundle` | `lotus-core` | `v1` | `supportability_and_control_plane` | `active` | lotus-performance, lotus-risk, lotus-gateway, lotus-manage | /support/portfolios/{portfolio_id}/reconciliation-runs, /support/portfolios/{portfolio_id}/reconciliation-runs/{run_id}/findings |
| `RiskFreeSeriesWindow` | `lotus-core` | `v1` | `analytics_input` | `active` | lotus-performance, lotus-risk | /integration/reference/risk-free-series |
| `SustainabilityPreferenceProfile` | `lotus-core` | `v1` | `dpm_source_data` | `active` | lotus-manage | /integration/portfolios/{portfolio_id}/sustainability-preference-profile |
| `TransactionCostCurve` | `lotus-core` | `v1` | `dpm_source_data` | `active` | lotus-manage | /integration/portfolios/{portfolio_id}/transaction-cost-curve |
| `TransactionLedgerWindow` | `lotus-core` | `v1` | `operational_source_data` | `active` | lotus-gateway, lotus-report, lotus-manage, lotus-risk | /portfolios/{portfolio_id}/transactions |
| `BulkReviewCampaignMembership` | `lotus-manage` | `v1` | `portfolio_management_workflow` | `active` | lotus-gateway | /api/v1/rebalance/waves/campaign-definitions, /api/v1/rebalance/waves/campaign-definitions/{campaign_id}/versions/{campaign_version}, /api/v1/rebalance/waves/campaign-definitions/{campaign_id}/versions/{campaign_version}/launch-package, /api/v1/rebalance/waves/campaign-definitions/{campaign_id}/versions/{campaign_version}/launch, /api/v1/rebalance/waves/campaign-definitions/{campaign_id}/versions/{campaign_version}/approval-decisions, /api/v1/rebalance/waves/campaign-definitions/{campaign_id}/versions/{campaign_version}/assignment-actions, /api/v1/rebalance/waves/campaign-definitions/{campaign_id}/versions/{campaign_version}/assignment-tasks, /api/v1/rebalance/waves/campaign-definitions/{campaign_id}/versions/{campaign_version}/assignment-tasks/{task_ref}/transitions, /api/v1/rebalance/waves/campaign-definitions/{campaign_id}/versions/{campaign_version}/maker-checker-controls, /api/v1/rebalance/waves/campaign-definitions/{campaign_id}/versions/{campaign_version}/workflow-overview, /api/v1/rebalance/waves/campaign-definitions/{campaign_id}/versions/{campaign_version}/preview-readiness, /api/v1/rebalance/waves/campaign-operating-queue, /api/v1/rebalance/waves/campaign-approval-inbox, /api/v1/rebalance/waves/campaign-workflow-board, /api/v1/rebalance/waves/campaign-assignment-plan, /api/v1/rebalance/waves/campaign-workflow-automation, /api/v1/rebalance/waves/preview, /api/v1/rebalance/waves |
| `PmOperatingQualityScoreRun` | `lotus-manage` | `v1` | `portfolio_management_workflow` | `active` | lotus-gateway | /api/v1/rebalance/pm-operating-quality/score-runs/preview, /api/v1/rebalance/pm-operating-quality/policies, /api/v1/rebalance/pm-operating-quality/policies/{policy_id}/versions/{policy_version}, /api/v1/rebalance/pm-operating-quality/score-runs, /api/v1/rebalance/pm-operating-quality/score-runs/{score_run_id}, /api/v1/rebalance/pm-operating-quality/fairness-analyses/preview, /api/v1/rebalance/pm-operating-quality/fairness-analyses, /api/v1/rebalance/pm-operating-quality/fairness-analyses/{fairness_analysis_id}, /api/v1/rebalance/pm-operating-quality/review-actions/preview, /api/v1/rebalance/pm-operating-quality/review-actions, /api/v1/rebalance/pm-operating-quality/review-actions/{review_action_id}, /api/v1/rebalance/pm-operating-quality/summary-invocations/preview, /api/v1/rebalance/pm-operating-quality/summary-invocations, /api/v1/rebalance/pm-operating-quality/summary-invocations/{summary_invocation_id}, /api/v1/rebalance/portfolio-memory/search, /api/v1/rebalance/portfolio-memory/{portfolio_id} |
| `PortfolioActionRegister` | `lotus-manage` | `v1` | `portfolio_management_workflow` | `active` | lotus-gateway | /api/v1/rebalance/supportability/summary, /api/v1/rebalance/runs/{rebalance_run_id}/artifact, /api/v1/rebalance/runs/{rebalance_run_id}/workflow, /api/v1/rebalance/workflow/decisions |
| `AttributionAnalytics` | `lotus-performance` | `v1` | `analytics_output` | `active` | lotus-gateway | /performance/attribution, /performance/attribution/results/{calculation_id} |
| `BenchmarkExposureContext` | `lotus-performance` | `v1` | `analytics_output` | `active` | lotus-risk | /integration/benchmarks/exposure-context |
| `CompositePerformanceAnalytics` | `lotus-performance` | `v1` | `analytics_output` | `active` | lotus-gateway | /performance/composites/twr |
| `ContributionAnalytics` | `lotus-performance` | `v1` | `analytics_output` | `active` | lotus-gateway | /performance/contribution, /performance/contribution/results/{calculation_id} |
| `MandatePerformanceHealthContext` | `lotus-performance` | `v1` | `analytics_output` | `active` | lotus-gateway, lotus-manage | /performance/mandate-health-context |
| `MoneyWeightedReturnAnalytics` | `lotus-performance` | `v1` | `analytics_output` | `active` | lotus-gateway | /performance/mwr |
| `ReturnsSeriesBundle` | `lotus-performance` | `v1` | `analytics_output` | `active` | lotus-risk | /integration/returns/series, /integration/returns/series/results/{calculation_id} |
| `TimeWeightedReturnAnalytics` | `lotus-performance` | `v1` | `analytics_output` | `active` | lotus-gateway | /performance/twr, /performance/twr/results/{calculation_id} |
| `ClientReportEvidencePack` | `lotus-report` | `v1` | `client_reporting_evidence` | `active` | lotus-gateway | /reports/client-evidence-packs/{portfolio_id}, /reports/portfolios/{portfolio_id}/review |
| `ConcentrationRiskReport` | `lotus-risk` | `v1` | `analytics_output` | `active` | lotus-gateway | /analytics/risk/concentration |
| `DrawdownAnalyticsReport` | `lotus-risk` | `v1` | `analytics_output` | `active` | lotus-gateway | /analytics/risk/drawdown |
| `HistoricalRiskAttributionReport` | `lotus-risk` | `v1` | `analytics_output` | `active` | lotus-gateway | /analytics/risk/historical-attribution |
| `MandateRiskHealthContext` | `lotus-risk` | `v1` | `analytics_output` | `active` | lotus-gateway, lotus-manage | /analytics/risk/mandate-health-context |
| `RegimeScenarioPackEvaluation` | `lotus-risk` | `v1` | `analytics_output` | `active` | lotus-gateway, lotus-manage | /analytics/risk/regime-scenario-pack/evaluate |
| `RiskEventAffectedCohort` | `lotus-risk` | `v1` | `cohort_membership` | `active` | lotus-manage | /analytics/risk/risk-event-cohorts/evaluate |
| `RiskMetricsReport` | `lotus-risk` | `v1` | `analytics_output` | `active` | lotus-gateway | /analytics/risk/calculate |
| `RollingRiskMetricsReport` | `lotus-risk` | `v1` | `analytics_output` | `active` | lotus-gateway | /analytics/risk/rolling-metrics |

## Dependencies

| Consumer | Upstream Product | Producer | Version | Mode | Failure Posture |
| --- | --- | --- | --- | --- | --- |
| `lotus-advise` | `HoldingsAsOf` | `lotus-core` | `v1` | `api_read` | `fail_closed` |
| `lotus-advise` | `InstrumentReferenceBundle` | `lotus-core` | `v1` | `api_read` | `degrade_to_partial` |
| `lotus-manage` | `TacticalHouseViewAffectedCohort` | `lotus-advise` | `v1` | `api_read` | `fail_closed` |
| `lotus-manage` | `BenchmarkAssignment` | `lotus-core` | `v1` | `stateful_core_sourcing` | `degrade_or_pending_review` |
| `lotus-manage` | `CioModelChangeAffectedCohort` | `lotus-core` | `v1` | `stateful_core_sourcing` | `fail_closed` |
| `lotus-manage` | `ClientIncomeNeedsSchedule` | `lotus-core` | `v1` | `stateful_core_sourcing` | `degrade` |
| `lotus-manage` | `ClientRestrictionProfile` | `lotus-core` | `v1` | `stateful_core_sourcing` | `degrade_or_block` |
| `lotus-manage` | `DiscretionaryMandateBinding` | `lotus-core` | `v1` | `stateful_core_sourcing` | `fail_closed` |
| `lotus-manage` | `DpmModelPortfolioTarget` | `lotus-core` | `v1` | `stateful_core_sourcing` | `fail_closed` |
| `lotus-manage` | `DpmPortfolioUniverseCandidate` | `lotus-core` | `v1` | `stateful_core_sourcing` | `fail_closed` |
| `lotus-manage` | `DpmSourceReadiness` | `lotus-core` | `v1` | `stateful_core_sourcing` | `fail_closed` |
| `lotus-manage` | `ExternalCurrencyExposure` | `lotus-core` | `v1` | `stateful_core_sourcing` | `fail_closed` |
| `lotus-manage` | `ExternalEligibleHedgeInstrument` | `lotus-core` | `v1` | `stateful_core_sourcing` | `fail_closed` |
| `lotus-manage` | `ExternalFXForwardCurve` | `lotus-core` | `v1` | `stateful_core_sourcing` | `fail_closed` |
| `lotus-manage` | `ExternalHedgeExecutionReadiness` | `lotus-core` | `v1` | `stateful_core_sourcing` | `fail_closed` |
| `lotus-manage` | `ExternalHedgePolicy` | `lotus-core` | `v1` | `stateful_core_sourcing` | `fail_closed` |
| `lotus-manage` | `ExternalOrderExecutionAcknowledgement` | `lotus-core` | `v1` | `stateful_core_sourcing` | `fail_closed` |
| `lotus-manage` | `InstrumentEligibilityProfile` | `lotus-core` | `v1` | `stateful_core_sourcing` | `fail_closed` |
| `lotus-manage` | `LiquidityReserveRequirement` | `lotus-core` | `v1` | `stateful_core_sourcing` | `degrade_or_pending_review` |
| `lotus-manage` | `MarketDataCoverageWindow` | `lotus-core` | `v1` | `stateful_core_sourcing` | `degrade_or_block` |
| `lotus-manage` | `PlannedWithdrawalSchedule` | `lotus-core` | `v1` | `stateful_core_sourcing` | `degrade_or_pending_review` |
| `lotus-manage` | `PortfolioCashflowProjection` | `lotus-core` | `v1` | `stateful_core_sourcing` | `degrade_or_pending_review` |
| `lotus-manage` | `PortfolioManagerBookMembership` | `lotus-core` | `v1` | `api_read` | `fail_closed` |
| `lotus-manage` | `PortfolioStateSnapshot` | `lotus-core` | `v1` | `caller_supplied_contract_payload` | `fail_closed` |
| `lotus-manage` | `PortfolioTaxLotWindow` | `lotus-core` | `v1` | `stateful_core_sourcing` | `degrade_or_block` |
| `lotus-manage` | `SustainabilityPreferenceProfile` | `lotus-core` | `v1` | `stateful_core_sourcing` | `degrade_or_pending_review` |
| `lotus-manage` | `TransactionCostCurve` | `lotus-core` | `v1` | `stateful_core_sourcing` | `degrade` |
| `lotus-manage` | `MandatePerformanceHealthContext` | `lotus-performance` | `v1` | `caller_supplied_contract_payload` | `degrade_or_pending_review` |
| `lotus-manage` | `MandateRiskHealthContext` | `lotus-risk` | `v1` | `caller_supplied_contract_payload` | `degrade_or_pending_review` |
| `lotus-manage` | `RegimeScenarioPackEvaluation` | `lotus-risk` | `v1` | `api_read` | `degrade_or_pending_review` |
| `lotus-manage` | `RiskEventAffectedCohort` | `lotus-risk` | `v1` | `api_read` | `fail_closed` |
| `lotus-performance` | `BenchmarkAssignment` | `lotus-core` | `v1` | `api_read` | `fail_closed` |
| `lotus-performance` | `InstrumentReferenceBundle` | `lotus-core` | `v1` | `paged_api_read` | `fail_closed` |
| `lotus-performance` | `MarketDataWindow` | `lotus-core` | `v1` | `paged_api_read` | `fail_closed` |
| `lotus-performance` | `PortfolioAnalyticsReference` | `lotus-core` | `v1` | `api_read` | `fail_closed` |
| `lotus-performance` | `PortfolioTimeseriesInput` | `lotus-core` | `v1` | `api_read` | `fail_closed` |
| `lotus-performance` | `PositionTimeseriesInput` | `lotus-core` | `v1` | `paged_api_read` | `fail_closed` |
| `lotus-performance` | `RiskFreeSeriesWindow` | `lotus-core` | `v1` | `api_read` | `degrade_to_partial` |
| `lotus-report` | `HoldingsAsOf` | `lotus-core` | `v1` | `api_read` | `fail_closed` |
| `lotus-report` | `TransactionLedgerWindow` | `lotus-core` | `v1` | `api_read` | `fail_closed` |
| `lotus-risk` | `InstrumentReferenceBundle` | `lotus-core` | `v1` | `paged_api_read` | `fail_closed` |
| `lotus-risk` | `PortfolioStateSnapshot` | `lotus-core` | `v1` | `api_read` | `fail_closed` |
| `lotus-risk` | `PositionTimeseriesInput` | `lotus-core` | `v1` | `api_read` | `fail_closed` |
| `lotus-risk` | `RiskFreeSeriesWindow` | `lotus-core` | `v1` | `api_read` | `degrade_to_partial` |
| `lotus-risk` | `BenchmarkExposureContext` | `lotus-performance` | `v1` | `paged_api_read` | `degrade_to_partial` |
| `lotus-risk` | `ReturnsSeriesBundle` | `lotus-performance` | `v1` | `api_read` | `fail_closed` |
