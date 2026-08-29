param(
  [string]$ContractPath,
  [string]$ManageBaseUrl = "http://manage.dev.lotus",
  [string]$GatewayBaseUrl = "http://gateway.dev.lotus",
  [string]$OutputDirectory = "output/front-office-qa",
  [string]$PortfolioId = "",
  [string]$MandateId = "",
  [string]$AsOfDate = "",
  [string]$TenantId = "",
  [string]$BookingCenterCode = "",
  [string]$ModelPortfolioId = "",
  [string]$ReferenceCurrency = "",
  [switch]$PreflightOnly,
  [switch]$SkipGatewayValidation
)

$ErrorActionPreference = "Stop"

$platformRoot = Split-Path -Parent $PSScriptRoot
$canonicalCashEvidenceScript = Join-Path $PSScriptRoot "resolve_canonical_cash_evidence.py"
if (-not (Test-Path $canonicalCashEvidenceScript)) {
  throw "Canonical cash-evidence resolver not found: $canonicalCashEvidenceScript"
}
if ([string]::IsNullOrWhiteSpace($ContractPath)) {
  $ContractPath = Join-Path $platformRoot "context\contracts\canonical-front-office-demo-data-contract.json"
}
if (-not (Test-Path $ContractPath)) {
  throw "Canonical front-office data contract not found: $ContractPath"
}

$contract = Get-Content -Raw $ContractPath | ConvertFrom-Json
$dpm = $contract.dpm_command_center
if (-not $dpm) {
  throw "Canonical front-office data contract does not define dpm_command_center."
}

function Resolve-ContractValue {
  param(
    [string]$Candidate,
    [object]$Fallback
  )

  if (-not [string]::IsNullOrWhiteSpace($Candidate)) {
    return $Candidate
  }
  return [string]$Fallback
}

function Invoke-JsonRequest {
  param(
    [string]$Method,
    [string]$Uri,
    [object]$Body = $null,
    [hashtable]$Headers = @{},
    [int]$Attempts = 8,
    [int]$DelaySeconds = 5
  )

  $lastError = $null
  for ($attempt = 1; $attempt -le $Attempts; $attempt++) {
    try {
      $arguments = @{
        Method = $Method
        Uri = $Uri
        Headers = $Headers
        TimeoutSec = 90
      }
      if ($null -ne $Body) {
        $arguments.ContentType = "application/json"
        $arguments.Body = ($Body | ConvertTo-Json -Depth 8)
      }

      return Invoke-RestMethod @arguments
    } catch {
      $lastError = Get-HttpErrorDetail -ErrorRecord $_
      if ($attempt -lt $Attempts) {
        Write-Warning "$Method $Uri failed: $lastError; retrying ($attempt/$Attempts)."
        Start-Sleep -Seconds $DelaySeconds
      }
    }
  }

  throw "$Method $Uri failed after $Attempts attempts: $lastError"
}

function Get-CommandCenterPosture {
  param([object]$Response)

  $supportability = $Response.supportability
  if (-not $supportability -and $Response.data) {
    $supportability = $Response.data.supportability
  }
  if (-not $supportability) {
    return "missing"
  }

  $state = [string]$supportability.state
  if (-not [string]::IsNullOrWhiteSpace($state)) {
    return $state.Trim().ToLowerInvariant()
  }

  $completeness = [string]$supportability.data_completeness_state
  if ($completeness -eq "COMPLETE") {
    return "ready"
  }
  if ($completeness -eq "PARTIAL") {
    return "partial"
  }
  if ($completeness -eq "EMPTY") {
    return "empty"
  }
  return "missing"
}

function Add-CommandCenterPostureCheck {
  param(
    [System.Collections.ArrayList]$Checks,
    [string]$Name,
    [string]$ExpectedState,
    [string]$Uri,
    [object]$Response
  )

  $observedState = Get-CommandCenterPosture -Response $Response
  $supportability = if ($Response.supportability) { $Response.supportability } else { $Response.data.supportability }
  $reasons = @()
  if ($supportability.partial_readiness_reasons) {
    $reasons = @($supportability.partial_readiness_reasons)
  }
  [void]$Checks.Add([ordered]@{
    name = $Name
    uri = $Uri
    expected_state = $ExpectedState
    observed_state = $observedState
    passed = ($observedState -eq $ExpectedState)
    reason = $supportability.reason
    partial_readiness_reasons = $reasons
  })
}

function Get-HttpErrorDetail {
  param([object]$ErrorRecord)

  $errorDetails = $ErrorRecord.ErrorDetails
  if ($errorDetails -and -not [string]::IsNullOrWhiteSpace($errorDetails.Message)) {
    return "$($ErrorRecord.Exception.Message) Body: $($errorDetails.Message)"
  }

  $response = $ErrorRecord.Exception.Response
  if (-not $response) {
    return $ErrorRecord.Exception.Message
  }

  try {
    if ($response.Content -and ($response.Content.PSObject.Methods.Name -contains "ReadAsStringAsync")) {
      $body = $response.Content.ReadAsStringAsync().GetAwaiter().GetResult()
      if (-not [string]::IsNullOrWhiteSpace($body)) {
        return "$($ErrorRecord.Exception.Message) Body: $body"
      }
    }
  } catch {
    return $ErrorRecord.Exception.Message
  }

  try {
    if (-not ($response.PSObject.Methods.Name -contains "GetResponseStream")) {
      return $ErrorRecord.Exception.Message
    }
    $stream = $response.GetResponseStream()
    if ($stream) {
      $reader = [System.IO.StreamReader]::new($stream)
      $body = $reader.ReadToEnd()
      if (-not [string]::IsNullOrWhiteSpace($body)) {
        return "$($ErrorRecord.Exception.Message) Body: $body"
      }
    }
  } catch {
    return $ErrorRecord.Exception.Message
  }

  return $ErrorRecord.Exception.Message
}

function Get-HttpStatusCode {
  param([object]$ErrorRecord)

  $response = $ErrorRecord.Exception.Response
  if (-not $response -or -not $response.StatusCode) {
    return $null
  }
  return [int]$response.StatusCode
}

function Invoke-ManageWriteAuthorizationPreflight {
  param(
    [string]$Uri,
    [hashtable]$Headers
  )

  $probeBody = [ordered]@{
    as_of_date = "not-a-date"
  }
  $arguments = @{
    Method = "Post"
    Uri = $Uri
    Headers = $Headers
    ContentType = "application/json"
    Body = ($probeBody | ConvertTo-Json -Depth 8)
    TimeoutSec = 30
  }

  try {
    [void](Invoke-RestMethod @arguments)
  } catch {
    $statusCode = Get-HttpStatusCode -ErrorRecord $_
    $detail = Get-HttpErrorDetail -ErrorRecord $_
    if ($statusCode -eq 422) {
      return [ordered]@{
        status_code = $statusCode
        passed = $true
        expected_post_auth_status = 422
        posture = "authorized_validation_rejected_side_effect_free_probe"
      }
    }
    if ($statusCode -eq 403) {
      throw "Manage write-authorization preflight denied for $Uri. Expected post-auth 422 validation rejection; observed 403. Detail: $detail"
    }
    throw "Manage write-authorization preflight failed for $Uri. Expected post-auth 422 validation rejection; observed $statusCode. Detail: $detail"
  }

  $unexpectedSuccessMessage = (
    "Manage write-authorization preflight failed for $Uri. " +
    "Expected post-auth 422 validation rejection; observed unexpected 2xx success. " +
    "The side-effect-free sentinel payload may have reached the write operation."
  )
  throw $unexpectedSuccessMessage
}

$resolvedPortfolioId = Resolve-ContractValue -Candidate $PortfolioId -Fallback $dpm.portfolio_id
$resolvedMandateId = Resolve-ContractValue -Candidate $MandateId -Fallback $dpm.mandate_id
$resolvedAsOfDate = Resolve-ContractValue -Candidate $AsOfDate -Fallback $dpm.command_center_as_of_date
$resolvedTenantId = Resolve-ContractValue -Candidate $TenantId -Fallback $dpm.tenant_id
$resolvedBookingCenterCode = Resolve-ContractValue -Candidate $BookingCenterCode -Fallback $dpm.booking_center_code
$resolvedModelPortfolioId = Resolve-ContractValue -Candidate $ModelPortfolioId -Fallback $dpm.model_portfolio_id
$resolvedReferenceCurrency = Resolve-ContractValue -Candidate $ReferenceCurrency -Fallback $dpm.reference_currency
$resolvedActionRegisterAsOfDate = [string]$contract.date_policy.canonical_as_of_date
if ([string]::IsNullOrWhiteSpace($resolvedActionRegisterAsOfDate)) {
  $resolvedActionRegisterAsOfDate = $resolvedAsOfDate
}
$campaignScenario = $dpm.campaign_definition_scenario
if (-not $campaignScenario) {
  throw "Canonical front-office data contract does not define dpm_command_center.campaign_definition_scenario."
}
$resolvedCampaignId = [string]$campaignScenario.campaign_id
$resolvedCampaignVersion = [string]$campaignScenario.campaign_version
$resolvedCampaignTenantId = [string]$campaignScenario.tenant_id
if ([string]::IsNullOrWhiteSpace($resolvedCampaignTenantId)) {
  throw "Canonical front-office data contract does not define dpm_command_center.campaign_definition_scenario.tenant_id."
}
$resolvedCampaignAsOfDate = Resolve-ContractValue -Candidate ([string]$campaignScenario.as_of_date) -Fallback $resolvedAsOfDate
$resolvedCampaignCandidateSourceProduct = Resolve-ContractValue `
  -Candidate ([string]$campaignScenario.candidate_source_product) `
  -Fallback "DpmPortfolioUniverseCandidate:v1"
$campaignCandidateSelectionBasis = $campaignScenario.candidate_selection_basis
if (-not $campaignCandidateSelectionBasis) {
  throw "Canonical front-office data contract does not define dpm_command_center.campaign_definition_scenario.candidate_selection_basis."
}

$resolvedOutputDirectory = if ([System.IO.Path]::IsPathRooted($OutputDirectory)) {
  $OutputDirectory
} else {
  Join-Path $platformRoot $OutputDirectory
}
New-Item -ItemType Directory -Path $resolvedOutputDirectory -Force | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$evidencePath = Join-Path $resolvedOutputDirectory "dpm-command-center-seed-$timestamp.json"
$latestEvidencePath = Join-Path $resolvedOutputDirectory "dpm-command-center-seed-latest.json"

$manageApiBaseUrl = $ManageBaseUrl.TrimEnd("/")
$gatewayApiBaseUrl = $GatewayBaseUrl.TrimEnd("/")
$outcomeReviewRebalanceRunId = "rr_canonical_$($resolvedPortfolioId)_$($resolvedAsOfDate -replace '-', '')"
$outcomeReviewWaveId = "dwv_canonical_$($resolvedPortfolioId)_$($resolvedAsOfDate -replace '-', '')"
$outcomeReviewWaveItemId = "dwi_canonical_$($resolvedPortfolioId)_$($resolvedAsOfDate -replace '-', '')"
$refreshUri = "$manageApiBaseUrl/api/v1/mandates/$resolvedMandateId/refresh-from-core"
$recalculateHealthUri = "$manageApiBaseUrl/api/v1/mandates/$resolvedMandateId/health/recalculate"
$monitoringRunUri = "$manageApiBaseUrl/api/v1/dpm/monitoring/run-once"
$actionRegisterSimulationUri = "$manageApiBaseUrl/api/v1/rebalance/simulate"
$campaignDefinitionUri = (
  "$manageApiBaseUrl/api/v1/rebalance/waves/campaign-definitions/$resolvedCampaignId" +
  "/versions/$resolvedCampaignVersion"
)
$campaignDefinitionBaseUri = "$manageApiBaseUrl/api/v1/rebalance/waves/campaign-definitions/$resolvedCampaignId"
$manageLookupUri = "$manageApiBaseUrl/api/v1/mandates/by-portfolio/$resolvedPortfolioId"
$gatewayMandateUri = "$gatewayApiBaseUrl/api/v1/dpm/command-center/mandates/by-portfolio/$resolvedPortfolioId"
$gatewayHealthUri = "$gatewayApiBaseUrl/api/v1/dpm/command-center/mandates/$resolvedMandateId/health"
$gatewayCampaignDefinitionsUri = (
  "$gatewayApiBaseUrl/api/v1/dpm/command-center/waves/campaign-definitions" +
  "?campaign_status=ACTIVE"
)
$gatewayCampaignDiscoveryUri = (
  "$gatewayApiBaseUrl/api/v1/dpm/command-center/waves/campaign-discovery" +
  "?campaign_status=ACTIVE&active_on=$resolvedCampaignAsOfDate&include_expired=false"
)
$gatewayCommandCenterUri = (
  "$gatewayApiBaseUrl/api/v1/dpm/command-center" +
  "?portfolio_manager_id=$($dpm.portfolio_manager_id)" +
  "&tenant_id=$resolvedTenantId" +
  "&book_id=$($dpm.book_id)" +
  "&as_of_date=$resolvedAsOfDate"
)
$gatewayCommandCenterPartialUri = (
  "$gatewayApiBaseUrl/api/v1/dpm/command-center" +
  "?tenant_id=$resolvedTenantId" +
  "&limit=1"
)
$gatewayCommandCenterEmptyUri = (
  "$gatewayApiBaseUrl/api/v1/dpm/command-center" +
  "?portfolio_manager_id=$($dpm.portfolio_manager_id)" +
  "&tenant_id=$resolvedTenantId" +
  "&book_id=$($dpm.book_id)" +
  "&as_of_date=2099-01-01"
)
$gatewayOutcomeReviewsUri = (
  "$gatewayApiBaseUrl/api/v1/dpm/command-center/outcome-reviews" +
  "?portfolio_id=$resolvedPortfolioId&limit=50"
)

$manageSeedActorId = "platform-seed-automation"
$manageSeedRole = "platform-automation"
$manageSeedServiceIdentity = "lotus-platform.canonical-dpm-command-center-seed"
$manageSeedCapability = "manage.write"

function New-ManageRequestHeaders {
  param(
    [string]$CorrelationId,
    [string]$TenantId = $resolvedTenantId,
    [hashtable]$ExtraHeaders = @{}
  )

  $requestHeaders = @{
    "X-Actor-Id" = $manageSeedActorId
    "X-Tenant-Id" = $TenantId
    "X-Region" = "APAC"
    "X-Role" = $manageSeedRole
    "X-Correlation-Id" = $CorrelationId
    "X-Service-Identity" = $manageSeedServiceIdentity
    "X-Capabilities" = $manageSeedCapability
  }
  foreach ($key in $ExtraHeaders.Keys) {
    $requestHeaders[$key] = $ExtraHeaders[$key]
  }
  return $requestHeaders
}

$headers = New-ManageRequestHeaders -CorrelationId "corr-canonical-dpm-seed-$resolvedPortfolioId-$timestamp"
$campaignHeaders = New-ManageRequestHeaders `
  -CorrelationId "corr-canonical-dpm-campaign-$resolvedCampaignId-$timestamp" `
  -TenantId $resolvedCampaignTenantId
$manageAuthoritySummary = [ordered]@{
  actor_id = $manageSeedActorId
  tenant_id = $resolvedTenantId
  campaign_tenant_id = $resolvedCampaignTenantId
  role = $manageSeedRole
  service_identity = $manageSeedServiceIdentity
  capabilities = @($manageSeedCapability)
  required_headers = @(
    "X-Actor-Id",
    "X-Tenant-Id",
    "X-Role",
    "X-Correlation-Id",
    "X-Service-Identity",
    "X-Capabilities"
  )
}

$refreshBody = [ordered]@{
  portfolio_id = $resolvedPortfolioId
  as_of_date = $resolvedAsOfDate
  tenant_id = $resolvedTenantId
  booking_center_code = $resolvedBookingCenterCode
  model_portfolio_id = $resolvedModelPortfolioId
  reference_currency = $resolvedReferenceCurrency
  include_market_data_coverage = $true
}

function Split-SourceProduct {
  param([string]$SourceProduct)

  $parts = $SourceProduct -split ":", 2
  return [ordered]@{
    source_type = $parts[0]
    source_version = if ($parts.Count -gt 1) { $parts[1] } else { $null }
  }
}

function New-SourceRef {
  param(
    [string]$SourceSystem,
    [string]$SourceType,
    [string]$SourceId,
    [string]$SourceVersion = "",
    [string]$SupportabilityState = "READY",
    [string]$ContentHash = "",
    [object]$SelectionBasis = $null
  )

  $sourceRef = [ordered]@{
    source_system = $SourceSystem
    source_type = $SourceType
    source_id = $SourceId
    supportability_state = $SupportabilityState
  }
  if (-not [string]::IsNullOrWhiteSpace($SourceVersion)) {
    $sourceRef.source_version = $SourceVersion
  }
  if (-not [string]::IsNullOrWhiteSpace($ContentHash)) {
    $sourceRef.content_hash = $ContentHash
  }
  if ($null -ne $SelectionBasis) {
    $sourceRef.selection_basis = $SelectionBasis
  }
  return $sourceRef
}

function New-CampaignDefinitionBody {
  $sourceProduct = Split-SourceProduct -SourceProduct $resolvedCampaignCandidateSourceProduct
  $candidateSourceType = [string]$sourceProduct.source_type
  $candidateSourceVersion = [string]$sourceProduct.source_version
  $candidatePortfolios = @($dpm.multi_portfolio_wave_scenario.portfolios)
  $candidates = @(
    $candidatePortfolios | ForEach-Object {
      [ordered]@{
        portfolio_id = [string]$_.portfolio_id
        mandate_id = [string]$_.mandate_id
        portfolio_manager_id = [string]$_.portfolio_manager_id
        portfolio_type = [string]$_.portfolio_type
        source_refs = @(
          New-SourceRef `
            -SourceSystem "lotus-core" `
            -SourceType $candidateSourceType `
            -SourceId "$($_.portfolio_id):$resolvedCampaignAsOfDate" `
            -SourceVersion $candidateSourceVersion `
            -SupportabilityState "READY" `
            -ContentHash "sha256:canonical-dpm-candidate-$($_.portfolio_id)" `
            -SelectionBasis $campaignCandidateSelectionBasis
        )
      }
    }
  )
  $governance = [ordered]@{
    approval_ref = [string]$campaignScenario.governance.approval_ref
    approved_by = [string]$campaignScenario.governance.approved_by
    approved_at = [string]$campaignScenario.governance.approved_at
    expires_on = [string]$campaignScenario.governance.expires_on
    entitled_actor_ids = @($campaignScenario.governance.entitled_actor_ids)
    access_purpose = [string]$campaignScenario.governance.access_purpose
    source_refs = @(
      New-SourceRef `
        -SourceSystem "lotus-platform" `
        -SourceType "CanonicalDpmCampaignApproval" `
        -SourceId ([string]$campaignScenario.governance.approval_ref) `
        -SourceVersion $contract.contract_version `
        -SupportabilityState "READY"
    )
  }
  return [ordered]@{
    display_name = [string]$campaignScenario.display_name
    status = "ACTIVE"
    as_of_date = $resolvedCampaignAsOfDate
    rationale = [string]$campaignScenario.rationale
    eligible_portfolio_types = @($campaignScenario.eligible_portfolio_types)
    candidates = $candidates
    governance = $governance
    source_refs = @(
      New-SourceRef `
        -SourceSystem "lotus-platform" `
        -SourceType "CanonicalFrontOfficeDemoDataContract" `
        -SourceId $contract.contract_id `
        -SourceVersion $contract.contract_version `
        -SupportabilityState "READY"
    )
    created_by = [string]$campaignScenario.created_by
    correlation_id = "corr-canonical-dpm-campaign-$resolvedCampaignId-$timestamp"
  }
}

function New-OutcomeSourceRef {
  param(
    [string]$SourceSystem,
    [string]$SourceType,
    [string]$SourceId,
    [string]$SourceVersion,
    [string]$ContentHash
  )

  return [ordered]@{
    source_system = $SourceSystem
    source_type = $SourceType
    source_id = $SourceId
    source_version = $SourceVersion
    content_hash = $ContentHash
  }
}

function New-OutcomeMetric {
  param(
    [string]$Value,
    [string]$SourceSystem,
    [string]$SourceType,
    [string]$SourceId,
    [string]$ReasonCode
  )

  $contentHash = "sha256:canonical-outcome-$SourceSystem-$SourceId"
  return [ordered]@{
    value = $Value
    unit = "ratio"
    source_refs = @(
      New-OutcomeSourceRef `
        -SourceSystem $SourceSystem `
        -SourceType $SourceType `
        -SourceId $SourceId `
        -SourceVersion $contract.contract_version `
        -ContentHash $contentHash
    )
    source_freshness = [ordered]@{
      observed_at = "$resolvedAsOfDate`T01:10:00Z"
      as_of_date = $resolvedAsOfDate
      freshness_state = "CURRENT"
    }
    supportability = [ordered]@{
      state = "READY"
      reason_codes = @($ReasonCode)
      required_source = $true
    }
  }
}

function New-CanonicalOutcomeReviewGatewayBody {
  $expectedMetric = New-OutcomeMetric `
    -Value "0.0350" `
    -SourceSystem "lotus-manage" `
    -SourceType "DpmExpectedOutcomeSnapshot:v1" `
    -SourceId "$resolvedPortfolioId`:expected:$resolvedAsOfDate" `
    -ReasonCode "EXPECTED_READY"
  $realizedMetric = New-OutcomeMetric `
    -Value "0.0340" `
    -SourceSystem "lotus-performance" `
    -SourceType "DpmRealizedOutcomeSnapshot:v1" `
    -SourceId "$resolvedPortfolioId`:realized:$resolvedAsOfDate" `
    -ReasonCode "REALIZED_READY"
  $expectedSourceRef = New-OutcomeSourceRef `
    -SourceSystem "lotus-platform" `
    -SourceType "CanonicalDpmOutcomeExpectedEvidence" `
    -SourceId "$resolvedPortfolioId`:expected:$resolvedAsOfDate" `
    -SourceVersion $contract.contract_version `
    -ContentHash "sha256:canonical-outcome-expected-$resolvedPortfolioId-$resolvedAsOfDate"
  $realizedSourceRef = New-OutcomeSourceRef `
    -SourceSystem "lotus-performance" `
    -SourceType "CanonicalDpmOutcomeRealizedEvidence" `
    -SourceId "$resolvedPortfolioId`:realized:$resolvedAsOfDate" `
    -SourceVersion $contract.contract_version `
    -ContentHash "sha256:canonical-outcome-realized-$resolvedPortfolioId-$resolvedAsOfDate"

  return [ordered]@{
    body = [ordered]@{
      expected_snapshot = [ordered]@{
        portfolio_id = $resolvedPortfolioId
        mandate_id = $resolvedMandateId
        rebalance_run_id = $outcomeReviewRebalanceRunId
        alternative_set_id = "cas_canonical_$($resolvedPortfolioId)_$($resolvedAsOfDate -replace '-', '')"
        selected_alternative_id = "alt_min_turnover"
        proof_pack_id = "dpp_canonical_$($resolvedPortfolioId)_$($resolvedAsOfDate -replace '-', '')"
        wave_id = $outcomeReviewWaveId
        wave_item_id = $outcomeReviewWaveItemId
        operations_handoff_ref_id = "dwh_canonical_$($resolvedPortfolioId)_$($resolvedAsOfDate -replace '-', '')"
        expected_values = [ordered]@{
          DRIFT_REDUCTION = $expectedMetric
        }
        supportability = [ordered]@{
          state = "READY"
          reason_codes = @("EXPECTED_READY")
          required_source = $true
        }
        source_lineage = @($expectedSourceRef)
        source_hashes = [ordered]@{
          expected = "sha256:canonical-outcome-expected-$resolvedPortfolioId-$resolvedAsOfDate"
        }
        section_hashes = [ordered]@{
          selected_alternative = "sha256:canonical-outcome-selected-alternative-$resolvedPortfolioId-$resolvedAsOfDate"
        }
      }
      realized_snapshot = [ordered]@{
        portfolio_id = $resolvedPortfolioId
        review_window = [ordered]@{
          start_at = "$resolvedAsOfDate`T00:00:00Z"
          end_at = "$resolvedAsOfDate`T23:59:59Z"
          as_of_date = $resolvedAsOfDate
          timezone = "Asia/Singapore"
        }
        realized_values = [ordered]@{
          DRIFT_REDUCTION = $realizedMetric
        }
        supportability = [ordered]@{
          state = "READY"
          reason_codes = @("REALIZED_READY")
          required_source = $true
        }
        source_lineage = @($realizedSourceRef)
        source_hashes = [ordered]@{
          realized = "sha256:canonical-outcome-realized-$resolvedPortfolioId-$resolvedAsOfDate"
        }
        quality_summary = [ordered]@{
          COMPLETE = 1
        }
      }
      dimension_configs = @(
        [ordered]@{
          dimension = "DRIFT_REDUCTION"
          tolerance = [ordered]@{
            soft = "0.0025"
            hard = "0.0100"
          }
          materiality = "0.0050"
          direction = "LOWER_IS_BETTER"
        }
      )
      actor_id = "platform-seed-automation"
    }
  }
}

function New-CanonicalMandateHealthBody {
  param([object]$Mandate)

  if (-not $summary.cash_evidence -or [string]::IsNullOrWhiteSpace([string]$summary.cash_evidence.normalized_cash_weight)) {
    throw "Canonical cash evidence must be resolved before mandate health recalculation."
  }

  return [ordered]@{
    twin = $Mandate
    cash_weight = [string]$summary.cash_evidence.normalized_cash_weight
    source_readiness_state = "READY"
    risk_health_context = [ordered]@{
      source_system = "lotus-risk"
      source_product_name = "MandateRiskHealthContext"
      source_product_version = "v1"
      health_state = "attention"
      threshold_breached = $true
      request_fingerprint = "sha256:canonical-mandate-risk-health-$resolvedPortfolioId-$resolvedAsOfDate"
      source_metric = [ordered]@{
        tracking_error = "0.0710"
        threshold = "0.0650"
      }
      methodology_posture = [ordered]@{
        owner = "lotus-risk"
        local_calculation = $false
      }
      reason_codes = @("CANONICAL_RISK_DRIFT_ATTENTION")
    }
    performance_health_context = [ordered]@{
      source_system = "lotus-performance"
      source_product_name = "MandatePerformanceHealthContext"
      source_product_version = "v1"
      health_state = "ready"
      threshold_breached = $false
      request_fingerprint = "sha256:canonical-mandate-performance-health-$resolvedPortfolioId-$resolvedAsOfDate"
      source_metric = [ordered]@{
        active_return = "-0.0060"
        threshold = "-0.0200"
      }
      methodology_posture = [ordered]@{
        owner = "lotus-performance"
        local_calculation = $false
      }
      benchmark_context = [ordered]@{
        benchmark_id = $contract.benchmark.benchmark_code
      }
      reason_codes = @("CANONICAL_PERFORMANCE_HEALTH_READY")
    }
  }
}

function Assert-CampaignDefinitionMatchesSeed {
  param(
    [string]$Name,
    [object]$Definition
  )

  if (-not $Definition) {
    throw "$Name returned an empty campaign definition for $resolvedCampaignId/$resolvedCampaignVersion."
  }
  if ([string]$Definition.campaign_id -ne $resolvedCampaignId -or
      [string]$Definition.campaign_version -ne $resolvedCampaignVersion) {
    throw "$Name returned $($Definition.campaign_id)/$($Definition.campaign_version), expected $resolvedCampaignId/$resolvedCampaignVersion."
  }
  if ([string]$Definition.status -ne "ACTIVE") {
    throw "$Name returned status $($Definition.status), expected ACTIVE."
  }
  if ([string]$Definition.as_of_date -ne $resolvedCampaignAsOfDate) {
    throw "$Name returned as_of_date $($Definition.as_of_date), expected $resolvedCampaignAsOfDate."
  }

  $sourceProduct = Split-SourceProduct -SourceProduct $resolvedCampaignCandidateSourceProduct
  $expectedSourceType = [string]$sourceProduct.source_type
  $expectedSourceVersion = [string]$sourceProduct.source_version
  $expectedPortfolioIds = @($dpm.multi_portfolio_wave_scenario.portfolios | ForEach-Object { [string]$_.portfolio_id })
  $observedCandidates = @($Definition.candidates)
  foreach ($portfolioId in $expectedPortfolioIds) {
    $candidate = @($observedCandidates | Where-Object { [string]$_.portfolio_id -eq $portfolioId })
    if ($candidate.Count -ne 1) {
      throw "$Name did not include exactly one candidate for $portfolioId."
    }
    $sourceRef = @(
      @($candidate[0].source_refs) | Where-Object {
        [string]$_.source_system -eq "lotus-core" -and
          [string]$_.source_type -eq $expectedSourceType -and
          [string]$_.source_version -eq $expectedSourceVersion -and
          [string]$_.source_id -eq "$portfolioId`:$resolvedCampaignAsOfDate" -and
          [string]$_.supportability_state -eq "READY"
      }
    )
    if ($sourceRef.Count -lt 1) {
      throw "$Name candidate $portfolioId did not include READY lotus-core $resolvedCampaignCandidateSourceProduct source lineage."
    }
    $selectionBasis = $sourceRef[0].selection_basis
    if (-not $selectionBasis) {
      throw "$Name candidate $portfolioId did not include source-owned selection_basis evidence."
    }
    if ([string]$selectionBasis.basis_type -ne [string]$campaignCandidateSelectionBasis.basis_type) {
      throw "$Name candidate $portfolioId returned selection_basis.basis_type $($selectionBasis.basis_type), expected $($campaignCandidateSelectionBasis.basis_type)."
    }
    if ([string]$selectionBasis.source_table -ne [string]$campaignCandidateSelectionBasis.source_table) {
      throw "$Name candidate $portfolioId returned selection_basis.source_table $($selectionBasis.source_table), expected $($campaignCandidateSelectionBasis.source_table)."
    }
    $expectedPredicates = @($campaignCandidateSelectionBasis.included_when | ForEach-Object { [string]$_ })
    $observedPredicates = @($selectionBasis.included_when | ForEach-Object { [string]$_ })
    foreach ($predicate in $expectedPredicates) {
      if ($observedPredicates -notcontains $predicate) {
        throw "$Name candidate $portfolioId selection_basis did not include predicate $predicate."
      }
    }
  }
}

function Assert-MandateHealthMatchesSeed {
  param(
    [string]$Name,
    [object]$Response
  )

  $health = if ($Response.data) { $Response.data } else { $Response }
  if (-not $health) {
    throw "$Name returned an empty mandate-health snapshot."
  }
  if ([string]$health.mandate_id -ne $resolvedMandateId) {
    throw "$Name returned mandate_id $($health.mandate_id), expected $resolvedMandateId."
  }
  if ([string]$health.portfolio_id -ne $resolvedPortfolioId) {
    throw "$Name returned portfolio_id $($health.portfolio_id), expected $resolvedPortfolioId."
  }
  if ([string]$health.as_of_date -ne $resolvedAsOfDate) {
    throw "$Name returned as_of_date $($health.as_of_date), expected $resolvedAsOfDate."
  }
  if ([string]::IsNullOrWhiteSpace([string]$health.health_snapshot_id)) {
    throw "$Name did not return a source-owned health_snapshot_id."
  }
}

function Upsert-CampaignDefinition {
  $existingDefinition = $null
  try {
    $existingDefinition = Invoke-JsonRequest `
      -Method "Get" `
      -Uri $campaignDefinitionUri `
      -Headers $campaignHeaders `
      -Attempts 1
  } catch {
    $existingDefinition = $null
  }

  if ($existingDefinition) {
    try {
      Assert-CampaignDefinitionMatchesSeed `
        -Name "Existing Manage campaign definition" `
        -Definition $existingDefinition
      return $existingDefinition
    } catch {
      Write-Warning "Existing canonical Manage campaign definition is stale against the governed seed contract: $($_.Exception.Message). Refreshing the seed-owned definition."
    }
  }

  $createdDefinition = Invoke-JsonRequest `
    -Method "Put" `
    -Uri $campaignDefinitionUri `
    -Headers (New-ManageRequestHeaders `
      -CorrelationId "corr-canonical-dpm-campaign-upsert-$resolvedCampaignId-$resolvedCampaignVersion-$timestamp" `
      -TenantId $resolvedCampaignTenantId) `
    -Body (New-CampaignDefinitionBody)
  Assert-CampaignDefinitionMatchesSeed `
    -Name "Created Manage campaign definition" `
    -Definition $createdDefinition
  return $createdDefinition
}

function Supersede-LegacyCampaignDefinitions {
  $legacyVersions = @(
    $campaignScenario.supersedes_campaign_versions |
      ForEach-Object { [string]$_ } |
      Where-Object { -not [string]::IsNullOrWhiteSpace($_) -and $_ -ne $resolvedCampaignVersion }
  )
  foreach ($legacyVersion in $legacyVersions) {
    $legacyDefinition = $null
    $legacyUri = "$campaignDefinitionBaseUri/versions/$legacyVersion"
    try {
      $legacyDefinition = Invoke-JsonRequest `
        -Method "Get" `
        -Uri $legacyUri `
        -Headers $campaignHeaders `
        -Attempts 1
    } catch {
      $legacyDefinition = $null
    }
    if (-not $legacyDefinition -or [string]$legacyDefinition.status -ne "ACTIVE") {
      continue
    }
    Write-Warning "Superseding stale canonical Manage campaign definition $resolvedCampaignId/$legacyVersion with $resolvedCampaignVersion."
    [void](Invoke-JsonRequest `
      -Method "Post" `
      -Uri "$legacyUri/supersede" `
      -Headers (New-ManageRequestHeaders `
        -CorrelationId "corr-canonical-dpm-campaign-supersede-$resolvedCampaignId-$legacyVersion-$timestamp" `
        -TenantId $resolvedCampaignTenantId) `
      -Body ([ordered]@{
        superseded_by_campaign_version = $resolvedCampaignVersion
        superseded_by = "platform-seed-automation"
        supersession_reason = "Canonical seed contract now carries source-owned candidate selection-basis evidence."
        correlation_id = "corr-canonical-dpm-campaign-supersede-$resolvedCampaignId-$legacyVersion-$timestamp"
      }))
  }
}

function Assert-CampaignPageContainsSeed {
  param(
    [string]$Name,
    [object]$Response
  )

  $items = @($Response.data.items)
  $matched = @(
    $items | Where-Object {
      [string]$_.campaign_id -eq $resolvedCampaignId -and
        [string]$_.campaign_version -eq $resolvedCampaignVersion
    }
  )
  if ($matched.Count -lt 1) {
    throw "$Name did not include canonical campaign definition $resolvedCampaignId/$resolvedCampaignVersion."
  }
}

function Assert-OutcomeReviewPageContainsSeed {
  param([object]$Response)

  $items = @($Response.data.items)
  $matched = @(
    $items | Where-Object {
      $expectedSnapshot = $_.expected_snapshot
      $observedRunId = [string]$_.rebalance_run_id
      if ([string]::IsNullOrWhiteSpace($observedRunId) -and $expectedSnapshot) {
        $observedRunId = [string]$expectedSnapshot.rebalance_run_id
      }
      $observedWaveId = [string]$_.wave_id
      if ([string]::IsNullOrWhiteSpace($observedWaveId) -and $expectedSnapshot) {
        $observedWaveId = [string]$expectedSnapshot.wave_id
      }

      [string]$_.portfolio_id -eq $resolvedPortfolioId -and
        [string]$_.mandate_id -eq $resolvedMandateId -and
        [string]$_.state -eq "READY" -and
        $observedRunId -eq $outcomeReviewRebalanceRunId -and
        $observedWaveId -eq $outcomeReviewWaveId
    }
  )
  if ($matched.Count -lt 1) {
    throw (
      "Gateway outcome-review list did not include canonical READY review for " +
      "$resolvedPortfolioId/$resolvedMandateId with rebalance_run_id $outcomeReviewRebalanceRunId " +
      "and wave_id $outcomeReviewWaveId."
    )
  }

  return $matched[0]
}

$summary = [ordered]@{
  generated_at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
  contract_id = $contract.contract_id
  contract_version = $contract.contract_version
  governed_by_rfc = $contract.governed_by_rfc
  portfolio_id = $resolvedPortfolioId
  mandate_id = $resolvedMandateId
  portfolio_manager_id = $dpm.portfolio_manager_id
  book_id = $dpm.book_id
  tenant_id = $resolvedTenantId
  campaign_tenant_id = $resolvedCampaignTenantId
  booking_center_code = $resolvedBookingCenterCode
  model_portfolio_id = $resolvedModelPortfolioId
  policy_pack_id = $dpm.policy_pack_id
  reference_currency = $resolvedReferenceCurrency
  command_center_as_of_date = $resolvedAsOfDate
  action_register_as_of_date = $resolvedActionRegisterAsOfDate
  source_products = @($dpm.source_products)
  campaign_candidate_selection_basis = $campaignCandidateSelectionBasis
  manage_refresh_uri = $refreshUri
  manage_recalculate_health_uri = $recalculateHealthUri
  manage_monitoring_run_uri = $monitoringRunUri
  manage_action_register_simulation_uri = $actionRegisterSimulationUri
  manage_campaign_definition_uri = $campaignDefinitionUri
  manage_lookup_uri = $manageLookupUri
  gateway_mandate_uri = $gatewayMandateUri
  gateway_health_uri = $gatewayHealthUri
  gateway_campaign_definitions_uri = $gatewayCampaignDefinitionsUri
  gateway_campaign_discovery_uri = $gatewayCampaignDiscoveryUri
  gateway_command_center_uri = $gatewayCommandCenterUri
  gateway_command_center_partial_uri = $gatewayCommandCenterPartialUri
  gateway_command_center_empty_uri = $gatewayCommandCenterEmptyUri
  gateway_outcome_reviews_uri = $gatewayOutcomeReviewsUri
  status = "ok"
  steps = @()
  posture_checks = @()
  manage_write_authority = $manageAuthoritySummary
  manage_authorization_preflight_response = $null
  preflight_only = [bool]$PreflightOnly
  refresh_response = $null
  cash_evidence = $null
  recalculated_health_response = $null
  monitoring_run_response = $null
  action_register_simulation_response = $null
  action_register_workflow_response = $null
  action_register_workflow_action_response = $null
  campaign_definition_response = $null
  manage_lookup_response = $null
  gateway_mandate_response = $null
  gateway_health_response = $null
  gateway_campaign_definitions_response = $null
  gateway_campaign_discovery_response = $null
  gateway_command_center_response = $null
  gateway_command_center_partial_response = $null
  gateway_command_center_empty_response = $null
  gateway_outcome_review_create_response = $null
  gateway_outcome_reviews_response = $null
  error = $null
}

function Complete-SeedSummary {
  $summaryObject = [pscustomobject]$summary
  $summaryObject | ConvertTo-Json -Depth 20 | Set-Content -Path $evidencePath
  $summaryObject | ConvertTo-Json -Depth 20 | Set-Content -Path $latestEvidencePath
  Write-Host "Wrote $evidencePath"
  Write-Host "Wrote $latestEvidencePath"

  if ($summary.status -ne "ok") {
    exit 1
  }
  exit 0
}

if ($PreflightOnly) {
  try {
    Write-Host "[dpm-seed] preflighting Manage write authorization for canonical refresh route"
    $summary.manage_authorization_preflight_response = Invoke-ManageWriteAuthorizationPreflight `
      -Uri $refreshUri `
      -Headers (New-ManageRequestHeaders -CorrelationId "corr-canonical-dpm-refresh-auth-preflight-$resolvedPortfolioId-$timestamp")
    $summary.steps += "manage-refresh-authorization-preflight"
  } catch {
    $summary.status = "failed"
    $summary.error = $_.Exception.Message
  }
  Complete-SeedSummary
}

try {
  Write-Host "[dpm-seed] preflighting Manage write authorization for canonical refresh route"
  $summary.manage_authorization_preflight_response = Invoke-ManageWriteAuthorizationPreflight `
    -Uri $refreshUri `
    -Headers (New-ManageRequestHeaders -CorrelationId "corr-canonical-dpm-refresh-auth-preflight-$resolvedPortfolioId-$timestamp")
  $summary.steps += "manage-refresh-authorization-preflight"

  Write-Host "[dpm-seed] resolving date-aligned canonical cash evidence before persistent writes"
  $cashEvidenceJson = & python $canonicalCashEvidenceScript `
    --gateway-base-url $gatewayApiBaseUrl `
    --portfolio-id $resolvedPortfolioId `
    --as-of-date $resolvedAsOfDate
  if ($LASTEXITCODE -ne 0) {
    throw "Canonical cash-evidence resolution failed with exit code $LASTEXITCODE before any persistent seed write."
  }
  try {
    $summary.cash_evidence = $cashEvidenceJson | ConvertFrom-Json
  } catch {
    throw "Canonical cash-evidence resolver returned invalid JSON before any persistent seed write: $($_.Exception.Message)"
  }
  $summary.steps += "gateway-date-aligned-cash-evidence-preflight"

  Write-Host "[dpm-seed] refreshing $resolvedMandateId from lotus-core through lotus-manage"
  $summary.refresh_response = Invoke-JsonRequest `
    -Method "Post" `
    -Uri $refreshUri `
    -Headers (New-ManageRequestHeaders -CorrelationId "corr-canonical-dpm-refresh-$resolvedPortfolioId-$timestamp") `
    -Body $refreshBody
  $summary.steps += "manage-refresh-from-core"

  Write-Host "[dpm-seed] running mandate monitoring for command-center evidence"
  $summary.monitoring_run_response = Invoke-JsonRequest `
    -Method "Post" `
    -Uri $monitoringRunUri `
    -Headers (New-ManageRequestHeaders -CorrelationId "corr-canonical-dpm-monitoring-$resolvedPortfolioId-$timestamp") `
    -Body ([ordered]@{
    mandate_ids = @($resolvedMandateId)
    as_of_date = $resolvedAsOfDate
    tenant_id = $resolvedTenantId
    portfolio_manager_id = $dpm.portfolio_manager_id
    book_id = $dpm.book_id
    booking_center_code = $resolvedBookingCenterCode
    requested_by = "platform-seed-automation"
  })
  $summary.steps += "manage-monitoring-run-once"

  Write-Host "[dpm-seed] preserving source-owned risk/performance mandate health contexts"
  $summary.recalculated_health_response = Invoke-JsonRequest `
    -Method "Post" `
    -Uri $recalculateHealthUri `
    -Headers (New-ManageRequestHeaders -CorrelationId "corr-canonical-dpm-health-recalculate-$resolvedPortfolioId-$timestamp") `
    -Body (New-CanonicalMandateHealthBody -Mandate $summary.refresh_response.mandate)
  Assert-MandateHealthMatchesSeed `
    -Name "Manage mandate-health recalculation" `
    -Response $summary.recalculated_health_response
  $summary.steps += "manage-mandate-health-source-contexts"
  $summary.steps += "manage-mandate-health-date-match"

  Write-Host "[dpm-seed] recording stateful action-register simulation evidence"
  $actionRegisterIdempotencyKey = (
    "canonical-dpm-action-register:${resolvedPortfolioId}:${resolvedActionRegisterAsOfDate}:$timestamp"
  )
  $summary.action_register_simulation_response = Invoke-JsonRequest `
    -Method "Post" `
    -Uri $actionRegisterSimulationUri `
    -Headers (New-ManageRequestHeaders `
      -CorrelationId "corr-canonical-dpm-action-register-$resolvedPortfolioId-$resolvedActionRegisterAsOfDate-$timestamp" `
      -ExtraHeaders @{
      "Idempotency-Key" = $actionRegisterIdempotencyKey
      "X-Policy-Pack-Id" = $dpm.policy_pack_id
    }) `
    -Body ([ordered]@{
      input_mode = "stateful"
      stateful_input = [ordered]@{
        portfolio_id = $resolvedPortfolioId
        as_of = $resolvedActionRegisterAsOfDate
        mandate_id = $resolvedMandateId
        model_portfolio_id = $resolvedModelPortfolioId
        tenant_id = $resolvedTenantId
        booking_center_code = $resolvedBookingCenterCode
        policy_pack_id = $dpm.policy_pack_id
      }
    })
  $summary.steps += "manage-action-register-stateful-simulation"

  $actionRegisterRunId = [string]$summary.action_register_simulation_response.rebalance_run_id
  if ([string]::IsNullOrWhiteSpace($actionRegisterRunId)) {
    throw "Manage action-register simulation returned no rebalance_run_id for workflow evidence."
  }
  Write-Host "[dpm-seed] reading review workflow posture for action-register evidence"
  $summary.action_register_workflow_response = Invoke-JsonRequest `
    -Method "Get" `
    -Uri "$manageApiBaseUrl/api/v1/rebalance/runs/$actionRegisterRunId/workflow" `
    -Headers (New-ManageRequestHeaders -CorrelationId "corr-canonical-dpm-action-register-workflow-$resolvedPortfolioId-$timestamp")
  $summary.steps += "manage-action-register-workflow-posture"

  $workflowRequiresReview = [bool]$summary.action_register_workflow_response.requires_review
  if ($workflowRequiresReview) {
    Write-Host "[dpm-seed] recording review workflow decision for action-register evidence"
    $summary.action_register_workflow_action_response = Invoke-JsonRequest `
      -Method "Post" `
      -Uri "$manageApiBaseUrl/api/v1/rebalance/runs/$actionRegisterRunId/workflow/actions" `
      -Headers (New-ManageRequestHeaders -CorrelationId "corr-canonical-dpm-action-register-review-$resolvedPortfolioId-$timestamp") `
      -Body ([ordered]@{
        action = "APPROVE"
        reason_code = "REVIEW_APPROVED"
        comment = "Canonical DPM action-register evidence reviewed for front-office validation."
        actor_id = "platform-seed-automation"
      })
    $summary.steps += "manage-action-register-workflow-decision"
  } else {
    $summary.action_register_workflow_action_response = [ordered]@{
      skipped = $true
      reason_code = "DPM_WORKFLOW_NOT_REQUIRED_FOR_RUN_STATUS"
      run_id = $actionRegisterRunId
      run_status = [string]$summary.action_register_workflow_response.run_status
      workflow_status = [string]$summary.action_register_workflow_response.workflow_status
      requires_review = $false
      evidence_note = (
        "Manage reported this action-register simulation run does not require workflow review; " +
        "the canonical seed preserves that posture and does not fabricate an approval decision."
      )
    }
    $summary.steps += "manage-action-register-workflow-not-required"
  }

  Write-Host "[dpm-seed] persisting source-backed campaign definition $resolvedCampaignId/$resolvedCampaignVersion"
  $summary.campaign_definition_response = Upsert-CampaignDefinition
  $summary.steps += "manage-campaign-definition-upsert"
  Supersede-LegacyCampaignDefinitions
  $summary.steps += "manage-campaign-definition-supersede-legacy"

  Write-Host "[dpm-seed] verifying manage mandate lookup for $resolvedPortfolioId"
  $summary.manage_lookup_response = Invoke-JsonRequest -Method "Get" -Uri $manageLookupUri -Headers $headers
  $summary.steps += "manage-lookup-by-portfolio"

  if (-not $SkipGatewayValidation) {
    Write-Host "[dpm-seed] verifying Gateway command-center mandate lookup"
    $summary.gateway_mandate_response = Invoke-JsonRequest -Method "Get" -Uri $gatewayMandateUri -Headers $headers
    $summary.steps += "gateway-mandate-by-portfolio"

    Write-Host "[dpm-seed] verifying Gateway command-center mandate health"
    $summary.gateway_health_response = Invoke-JsonRequest -Method "Get" -Uri $gatewayHealthUri -Headers $headers
    Assert-MandateHealthMatchesSeed `
      -Name "Gateway command-center mandate health" `
      -Response $summary.gateway_health_response
    $summary.steps += "gateway-mandate-health"
    $summary.steps += "gateway-mandate-health-date-match"

    Write-Host "[dpm-seed] verifying Gateway campaign definitions"
    $summary.gateway_campaign_definitions_response = Invoke-JsonRequest `
      -Method "Get" `
      -Uri $gatewayCampaignDefinitionsUri `
      -Headers $campaignHeaders
    Assert-CampaignPageContainsSeed `
      -Name "Gateway campaign definitions" `
      -Response $summary.gateway_campaign_definitions_response
    $summary.steps += "gateway-campaign-definitions"

    Write-Host "[dpm-seed] verifying Gateway campaign discovery"
    $summary.gateway_campaign_discovery_response = Invoke-JsonRequest `
      -Method "Get" `
      -Uri $gatewayCampaignDiscoveryUri `
      -Headers $campaignHeaders
    Assert-CampaignPageContainsSeed `
      -Name "Gateway campaign discovery" `
      -Response $summary.gateway_campaign_discovery_response
    $summary.steps += "gateway-campaign-discovery"

    Write-Host "[dpm-seed] verifying Gateway command-center summary"
    $summary.gateway_command_center_response = Invoke-JsonRequest -Method "Get" -Uri $gatewayCommandCenterUri -Headers $headers
    $summary.steps += "gateway-command-center-summary"

    Write-Host "[dpm-seed] creating canonical Gateway outcome-review evidence"
    $outcomeReviewIdempotencyKey = "canonical-dpm-outcome-review:${resolvedPortfolioId}:${resolvedAsOfDate}"
    $summary.gateway_outcome_review_create_response = Invoke-JsonRequest `
      -Method "Post" `
      -Uri "$gatewayApiBaseUrl/api/v1/dpm/command-center/outcome-reviews" `
      -Headers (New-ManageRequestHeaders `
        -CorrelationId "corr-canonical-dpm-outcome-review-$resolvedPortfolioId-$($resolvedAsOfDate -replace '-', '')" `
        -ExtraHeaders @{
          "Idempotency-Key" = $outcomeReviewIdempotencyKey
        }) `
      -Body (New-CanonicalOutcomeReviewGatewayBody)
    $summary.steps += "gateway-outcome-review-create"

    Write-Host "[dpm-seed] verifying Gateway outcome-review list"
    $summary.gateway_outcome_reviews_response = Invoke-JsonRequest `
      -Method "Get" `
      -Uri $gatewayOutcomeReviewsUri `
      -Headers $headers
    $summary.gateway_outcome_review_verified_item = Assert-OutcomeReviewPageContainsSeed `
      -Response $summary.gateway_outcome_reviews_response
    $summary.steps += "gateway-outcome-review-list"

    $postureChecks = [System.Collections.ArrayList]::new()
    Add-CommandCenterPostureCheck `
      -Checks $postureChecks `
      -Name "ready-populated-command-center" `
      -ExpectedState "ready" `
      -Uri $gatewayCommandCenterUri `
      -Response $summary.gateway_command_center_response

    Write-Host "[dpm-seed] verifying Gateway command-center partial posture"
    $summary.gateway_command_center_partial_response = Invoke-JsonRequest -Method "Get" -Uri $gatewayCommandCenterPartialUri -Headers $headers
    $summary.steps += "gateway-command-center-partial-posture"
    Add-CommandCenterPostureCheck `
      -Checks $postureChecks `
      -Name "partial-selector-command-center" `
      -ExpectedState "partial" `
      -Uri $gatewayCommandCenterPartialUri `
      -Response $summary.gateway_command_center_partial_response

    Write-Host "[dpm-seed] verifying Gateway command-center empty posture"
    $summary.gateway_command_center_empty_response = Invoke-JsonRequest -Method "Get" -Uri $gatewayCommandCenterEmptyUri -Headers $headers
    $summary.steps += "gateway-command-center-empty-posture"
    Add-CommandCenterPostureCheck `
      -Checks $postureChecks `
      -Name "empty-filter-command-center" `
      -ExpectedState "empty" `
      -Uri $gatewayCommandCenterEmptyUri `
      -Response $summary.gateway_command_center_empty_response
    $summary.posture_checks = @($postureChecks)

    $failedPostures = @($summary.posture_checks | Where-Object { -not $_.passed })
    if ($failedPostures.Count -gt 0) {
      $details = ($failedPostures | ForEach-Object { "$($_.name): expected $($_.expected_state), observed $($_.observed_state)" }) -join "; "
      throw "DPM command-center posture validation failed: $details"
    }
  }
} catch {
  $summary.status = "failed"
  $summary.error = $_.Exception.Message
}

Complete-SeedSummary
