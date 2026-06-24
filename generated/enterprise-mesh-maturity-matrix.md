# Enterprise Mesh Maturity Matrix

This file is generated from governed domain-product catalog evidence and RFC-0091 maturity-wave rules.

- Generated at: `2026-06-24T00:00:00Z`
- Source catalog: `generated/domain-product-catalog.json`
- Repository count: `11`
- Product count: `80`
- Certified first-wave products: `8`
- Candidate products: `0`
- Ambiguous repositories: `0`

## Repository Maturity

| Repository | Classification | Mesh role | Produced | Consumed | Next step |
| --- | --- | --- | ---: | ---: | --- |
| `lotus-platform` | `not_mesh_participant` | `platform_governance` | `0` | `0` | Owns contracts, validators, generated evidence, CI, and certification enforcement rather than product truth. |
| `lotus-core` | `certified_first_wave` | `producer` | `43` | `0` | Maintain repo-native declaration, trust telemetry, SLO, access, lifecycle, evidence-pack, and certification-gate posture. |
| `lotus-performance` | `certified_first_wave` | `producer` | `8` | `7` | Maintain repo-native declaration, trust telemetry, SLO, access, lifecycle, evidence-pack, and certification-gate posture. |
| `lotus-risk` | `certified_first_wave` | `producer` | `8` | `6` | Maintain repo-native declaration, trust telemetry, SLO, access, lifecycle, evidence-pack, and certification-gate posture. |
| `lotus-advise` | `certified_first_wave` | `producer` | `8` | `2` | Maintain repo-native declaration, trust telemetry, SLO, access, lifecycle, evidence-pack, and certification-gate posture. |
| `lotus-report` | `certified_first_wave` | `producer` | `1` | `2` | Maintain repo-native declaration, trust telemetry, SLO, access, lifecycle, evidence-pack, and certification-gate posture. |
| `lotus-manage` | `certified_first_wave` | `producer` | `3` | `29` | Maintain repo-native declaration, trust telemetry, SLO, access, lifecycle, evidence-pack, and certification-gate posture. |
| `lotus-gateway` | `not_mesh_participant` | `api_face` | `0` | `0` | Publishes catalog, trust, access, and evidence APIs without becoming a product authority. |
| `lotus-workbench` | `not_mesh_participant` | `discovery_and_operator_ux` | `0` | `0` | Consumes gateway/BFF APIs for discovery and evidence UX; it must not read platform files directly. |
| `lotus-idea` | `deferred` | `producer` | `9` | `16` | Decide whether these non-first-wave products enter a later maturity wave. |
| `lotus-ai` | `not_mesh_participant` | `explicit_posture_decision` | `0` | `0` | Not included until it owns a stable governed product or a catalog-consuming capability. |

## Product Maturity

| Product | Producer | Classification | Wave | Lifecycle | Next step |
| --- | --- | --- | --- | --- | --- |
| `lotus-advise:AdvisorCockpitOperatingSnapshot:v1` | `lotus-advise` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-advise:AdvisoryActionItemRegister:v1` | `lotus-advise` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-advise:AdvisoryCopilotInteractionRecord:v1` | `lotus-advise` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-advise:AdvisoryPolicyEvaluationRecord:v1` | `lotus-advise` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-advise:AdvisoryProposalLifecycleRecord:v1` | `lotus-advise` | `certified_first_wave` | `enterprise_wave_1` | `active` | Maintain RFC-0091 runtime, SLO, access, lifecycle, evidence-pack, and certification-gate controls. |
| `lotus-advise:AdvisoryProposalMemoEvidencePack:v1` | `lotus-advise` | `certified_first_wave` | `enterprise_wave_1` | `active` | Maintain RFC-0091 runtime, SLO, access, lifecycle, evidence-pack, and certification-gate controls. |
| `lotus-advise:ProposalNarrativeEvidence:v1` | `lotus-advise` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-advise:TacticalHouseViewAffectedCohort:v1` | `lotus-advise` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:BenchmarkAssignment:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:BenchmarkConstituentWindow:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:CioModelChangeAffectedCohort:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:ClientIncomeNeedsSchedule:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:ClientRestrictionProfile:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:ClientTaxProfile:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:ClientTaxRuleSet:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:DataQualityCoverageReport:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:DiscretionaryMandateBinding:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:DpmModelPortfolioTarget:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:DpmPortfolioUniverseCandidate:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:DpmSourceReadiness:v1` | `lotus-core` | `certified_first_wave` | `enterprise_wave_1` | `active` | Maintain RFC-0091 runtime, SLO, access, lifecycle, evidence-pack, and certification-gate controls. |
| `lotus-core:ExternalCurrencyExposure:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:ExternalEligibleHedgeInstrument:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:ExternalFXForwardCurve:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:ExternalHedgeExecutionReadiness:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:ExternalHedgePolicy:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:ExternalOrderExecutionAcknowledgement:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:HoldingsAsOf:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:IndexSeriesWindow:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:IngestionEvidenceBundle:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:InstrumentEligibilityProfile:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:InstrumentReferenceBundle:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:LiquidityReserveRequirement:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:MarketDataCoverageWindow:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:MarketDataWindow:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:PerformanceComponentEconomics:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:PlannedWithdrawalSchedule:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:PortfolioAnalyticsReference:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:PortfolioCashMovementSummary:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:PortfolioCashflowProjection:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:PortfolioLiquidityLadder:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:PortfolioManagerBookMembership:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:PortfolioRealizedTaxSummary:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:PortfolioStateSnapshot:v1` | `lotus-core` | `certified_first_wave` | `enterprise_wave_1` | `active` | Maintain RFC-0091 runtime, SLO, access, lifecycle, evidence-pack, and certification-gate controls. |
| `lotus-core:PortfolioTaxLotWindow:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:PortfolioTimeseriesInput:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:PositionTimeseriesInput:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:ReconciliationEvidenceBundle:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:RiskFreeSeriesWindow:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:SustainabilityPreferenceProfile:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:TransactionCostCurve:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-core:TransactionLedgerWindow:v1` | `lotus-core` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-idea:AdvisorOpportunityQueue:v1` | `lotus-idea` | `deferred` | `future_wave` | `proposed` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-idea:IdeaCandidate:v1` | `lotus-idea` | `deferred` | `future_wave` | `proposed` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-idea:IdeaConversionIntent:v1` | `lotus-idea` | `deferred` | `future_wave` | `proposed` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-idea:IdeaConversionOutcome:v1` | `lotus-idea` | `deferred` | `future_wave` | `proposed` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-idea:IdeaEvidencePacket:v1` | `lotus-idea` | `deferred` | `future_wave` | `proposed` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-idea:IdeaFeedbackEvent:v1` | `lotus-idea` | `deferred` | `future_wave` | `proposed` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-idea:IdeaReviewDecision:v1` | `lotus-idea` | `deferred` | `future_wave` | `proposed` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-idea:IdeaTrustTelemetry:v1` | `lotus-idea` | `deferred` | `future_wave` | `proposed` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-idea:OpportunitySignalCandidate:v1` | `lotus-idea` | `deferred` | `future_wave` | `proposed` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-manage:BulkReviewCampaignMembership:v1` | `lotus-manage` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-manage:PmOperatingQualityScoreRun:v1` | `lotus-manage` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-manage:PortfolioActionRegister:v1` | `lotus-manage` | `certified_first_wave` | `enterprise_wave_1` | `active` | Maintain RFC-0091 runtime, SLO, access, lifecycle, evidence-pack, and certification-gate controls. |
| `lotus-performance:AttributionAnalytics:v1` | `lotus-performance` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-performance:BenchmarkExposureContext:v1` | `lotus-performance` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-performance:CompositePerformanceAnalytics:v1` | `lotus-performance` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-performance:ContributionAnalytics:v1` | `lotus-performance` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-performance:MandatePerformanceHealthContext:v1` | `lotus-performance` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-performance:MoneyWeightedReturnAnalytics:v1` | `lotus-performance` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-performance:ReturnsSeriesBundle:v1` | `lotus-performance` | `certified_first_wave` | `enterprise_wave_1` | `active` | Maintain RFC-0091 runtime, SLO, access, lifecycle, evidence-pack, and certification-gate controls. |
| `lotus-performance:TimeWeightedReturnAnalytics:v1` | `lotus-performance` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-report:ClientReportEvidencePack:v1` | `lotus-report` | `certified_first_wave` | `enterprise_wave_1` | `active` | Maintain RFC-0091 runtime, SLO, access, lifecycle, evidence-pack, and certification-gate controls. |
| `lotus-risk:ConcentrationRiskReport:v1` | `lotus-risk` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-risk:DrawdownAnalyticsReport:v1` | `lotus-risk` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-risk:HistoricalRiskAttributionReport:v1` | `lotus-risk` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-risk:MandateRiskHealthContext:v1` | `lotus-risk` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-risk:RegimeScenarioPackEvaluation:v1` | `lotus-risk` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-risk:RiskEventAffectedCohort:v1` | `lotus-risk` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
| `lotus-risk:RiskMetricsReport:v1` | `lotus-risk` | `certified_first_wave` | `enterprise_wave_1` | `active` | Maintain RFC-0091 runtime, SLO, access, lifecycle, evidence-pack, and certification-gate controls. |
| `lotus-risk:RollingRiskMetricsReport:v1` | `lotus-risk` | `deferred` | `future_wave` | `active` | Keep outside blocking maturity gate until explicitly promoted. |
