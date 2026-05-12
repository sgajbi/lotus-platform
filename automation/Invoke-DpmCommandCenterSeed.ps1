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
$manageLookupUri = "$manageApiBaseUrl/api/v1/mandates/by-portfolio/$resolvedPortfolioId"
$gatewayMandateUri = "$gatewayApiBaseUrl/api/v1/dpm/command-center/mandates/by-portfolio/$resolvedPortfolioId"
$gatewayHealthUri = "$gatewayApiBaseUrl/api/v1/dpm/command-center/mandates/$resolvedMandateId/health"
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
  source_products = @($dpm.source_products)
  manage_refresh_uri = $refreshUri
  manage_monitoring_run_uri = $monitoringRunUri
  manage_lookup_uri = $manageLookupUri
  gateway_mandate_uri = $gatewayMandateUri
  gateway_health_uri = $gatewayHealthUri
  gateway_command_center_uri = $gatewayCommandCenterUri
  gateway_command_center_partial_uri = $gatewayCommandCenterPartialUri
  gateway_command_center_empty_uri = $gatewayCommandCenterEmptyUri
  status = "ok"
  steps = @()
  posture_checks = @()
  refresh_response = $null
  monitoring_run_response = $null
  manage_lookup_response = $null
  gateway_mandate_response = $null
  gateway_health_response = $null
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
