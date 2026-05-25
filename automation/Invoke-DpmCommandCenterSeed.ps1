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
  [switch]$SkipGatewayValidation
)

$ErrorActionPreference = "Stop"

$platformRoot = Split-Path -Parent $PSScriptRoot
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

  $response = $ErrorRecord.Exception.Response
  if (-not $response) {
    return $ErrorRecord.Exception.Message
  }

  try {
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
$resolvedCampaignAsOfDate = Resolve-ContractValue -Candidate ([string]$campaignScenario.as_of_date) -Fallback $resolvedAsOfDate
$resolvedCampaignCandidateSourceProduct = Resolve-ContractValue `
  -Candidate ([string]$campaignScenario.candidate_source_product) `
  -Fallback "DpmPortfolioUniverseCandidate:v1"

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
$refreshUri = "$manageApiBaseUrl/api/v1/mandates/$resolvedMandateId/refresh-from-core"
$monitoringRunUri = "$manageApiBaseUrl/api/v1/dpm/monitoring/run-once"
$actionRegisterSimulationUri = "$manageApiBaseUrl/api/v1/rebalance/simulate"
$campaignDefinitionUri = (
  "$manageApiBaseUrl/api/v1/rebalance/waves/campaign-definitions/$resolvedCampaignId" +
  "/versions/$resolvedCampaignVersion"
)
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

$headers = @{
  "X-Actor-Id" = "platform-seed-automation"
  "X-Tenant-Id" = $resolvedTenantId
  "X-Region" = "APAC"
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
    [string]$ContentHash = ""
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
            -ContentHash "sha256:canonical-dpm-candidate-$($_.portfolio_id)"
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
  }
}

function Upsert-CampaignDefinition {
  $existingDefinition = $null
  try {
    $existingDefinition = Invoke-JsonRequest `
      -Method "Get" `
      -Uri $campaignDefinitionUri `
      -Attempts 1
  } catch {
    $existingDefinition = $null
  }

  if ($existingDefinition) {
    Assert-CampaignDefinitionMatchesSeed `
      -Name "Existing Manage campaign definition" `
      -Definition $existingDefinition
    return $existingDefinition
  }

  $createdDefinition = Invoke-JsonRequest `
    -Method "Put" `
    -Uri $campaignDefinitionUri `
    -Body (New-CampaignDefinitionBody)
  Assert-CampaignDefinitionMatchesSeed `
    -Name "Created Manage campaign definition" `
    -Definition $createdDefinition
  return $createdDefinition
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
  booking_center_code = $resolvedBookingCenterCode
  model_portfolio_id = $resolvedModelPortfolioId
  policy_pack_id = $dpm.policy_pack_id
  reference_currency = $resolvedReferenceCurrency
  command_center_as_of_date = $resolvedAsOfDate
  action_register_as_of_date = $resolvedActionRegisterAsOfDate
  source_products = @($dpm.source_products)
  manage_refresh_uri = $refreshUri
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
  status = "ok"
  steps = @()
  posture_checks = @()
  refresh_response = $null
  monitoring_run_response = $null
  action_register_simulation_response = $null
  campaign_definition_response = $null
  manage_lookup_response = $null
  gateway_mandate_response = $null
  gateway_health_response = $null
  gateway_campaign_definitions_response = $null
  gateway_campaign_discovery_response = $null
  gateway_command_center_response = $null
  gateway_command_center_partial_response = $null
  gateway_command_center_empty_response = $null
  error = $null
}

try {
  Write-Host "[dpm-seed] refreshing $resolvedMandateId from lotus-core through lotus-manage"
  $summary.refresh_response = Invoke-JsonRequest -Method "Post" -Uri $refreshUri -Body $refreshBody
  $summary.steps += "manage-refresh-from-core"

  Write-Host "[dpm-seed] running mandate monitoring for command-center evidence"
  $summary.monitoring_run_response = Invoke-JsonRequest -Method "Post" -Uri $monitoringRunUri -Body ([ordered]@{
    mandate_ids = @($resolvedMandateId)
    as_of_date = $resolvedAsOfDate
    tenant_id = $resolvedTenantId
    portfolio_manager_id = $dpm.portfolio_manager_id
    book_id = $dpm.book_id
    booking_center_code = $resolvedBookingCenterCode
    requested_by = "platform-seed-automation"
  })
  $summary.steps += "manage-monitoring-run-once"

  Write-Host "[dpm-seed] recording stateful action-register simulation evidence"
  $actionRegisterIdempotencyKey = (
    "canonical-dpm-action-register:${resolvedPortfolioId}:${resolvedActionRegisterAsOfDate}:$timestamp"
  )
  $summary.action_register_simulation_response = Invoke-JsonRequest `
    -Method "Post" `
    -Uri $actionRegisterSimulationUri `
    -Headers @{
      "Idempotency-Key" = $actionRegisterIdempotencyKey
      "X-Correlation-Id" = (
        "corr-canonical-dpm-action-register-$resolvedPortfolioId-$resolvedActionRegisterAsOfDate-$timestamp"
      )
      "X-Tenant-Id" = $resolvedTenantId
      "X-Policy-Pack-Id" = $dpm.policy_pack_id
    } `
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

  Write-Host "[dpm-seed] persisting source-backed campaign definition $resolvedCampaignId/$resolvedCampaignVersion"
  $summary.campaign_definition_response = Upsert-CampaignDefinition
  $summary.steps += "manage-campaign-definition-upsert"

  Write-Host "[dpm-seed] verifying manage mandate lookup for $resolvedPortfolioId"
  $summary.manage_lookup_response = Invoke-JsonRequest -Method "Get" -Uri $manageLookupUri
  $summary.steps += "manage-lookup-by-portfolio"

  if (-not $SkipGatewayValidation) {
    Write-Host "[dpm-seed] verifying Gateway command-center mandate lookup"
    $summary.gateway_mandate_response = Invoke-JsonRequest -Method "Get" -Uri $gatewayMandateUri -Headers $headers
    $summary.steps += "gateway-mandate-by-portfolio"

    Write-Host "[dpm-seed] verifying Gateway command-center mandate health"
    $summary.gateway_health_response = Invoke-JsonRequest -Method "Get" -Uri $gatewayHealthUri -Headers $headers
    $summary.steps += "gateway-mandate-health"

    Write-Host "[dpm-seed] verifying Gateway campaign definitions"
    $summary.gateway_campaign_definitions_response = Invoke-JsonRequest `
      -Method "Get" `
      -Uri $gatewayCampaignDefinitionsUri `
      -Headers $headers
    Assert-CampaignPageContainsSeed `
      -Name "Gateway campaign definitions" `
      -Response $summary.gateway_campaign_definitions_response
    $summary.steps += "gateway-campaign-definitions"

    Write-Host "[dpm-seed] verifying Gateway campaign discovery"
    $summary.gateway_campaign_discovery_response = Invoke-JsonRequest `
      -Method "Get" `
      -Uri $gatewayCampaignDiscoveryUri `
      -Headers $headers
    Assert-CampaignPageContainsSeed `
      -Name "Gateway campaign discovery" `
      -Response $summary.gateway_campaign_discovery_response
    $summary.steps += "gateway-campaign-discovery"

    Write-Host "[dpm-seed] verifying Gateway command-center summary"
    $summary.gateway_command_center_response = Invoke-JsonRequest -Method "Get" -Uri $gatewayCommandCenterUri -Headers $headers
    $summary.steps += "gateway-command-center-summary"

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

$summaryObject = [pscustomobject]$summary
$summaryObject | ConvertTo-Json -Depth 20 | Set-Content -Path $evidencePath
$summaryObject | ConvertTo-Json -Depth 20 | Set-Content -Path $latestEvidencePath
Write-Host "Wrote $evidencePath"
Write-Host "Wrote $latestEvidencePath"

if ($summary.status -ne "ok") {
  exit 1
}
