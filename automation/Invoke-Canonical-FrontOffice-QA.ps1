param(
  [string]$ProjectsRoot,
  [string]$WorkbenchRepoPath,
  [string]$RuntimeHolder = $env:LOTUS_CANONICAL_RUNTIME_HOLDER,
  [string]$PortfolioId = "PB_SG_GLOBAL_BAL_001",
  [string]$BenchmarkCode = "BMK_PB_GLOBAL_BALANCED_60_40",
  [ValidateSet('full', 'client-demo')][string]$ValidationProfile = 'full',
  [string]$ReportStartDate = "",
  [string]$OutputDirectory = "output/front-office-qa",
  [string]$ScreenshotDirectory = "",
  [string]$LotusAiEnvFile = "",
  [int]$SeedWaitSeconds = 900,
  [switch]$BringUp,
  [switch]$Clean,
  [switch]$CleanPlanOnly,
  [switch]$CleanCoreState,
  [switch]$BuildImages,
  [switch]$RequireMainlineSources,
  [switch]$RemoveImages,
  [switch]$SkipDpmCommandCenterSeed,
  [switch]$KeepRunning
)

$ErrorActionPreference = "Stop"
Import-Module (Join-Path $PSScriptRoot 'CanonicalRuntimeReservation.psm1') -Force

$platformRoot = Split-Path -Parent $PSScriptRoot
function Resolve-CanonicalReportStartDate {
  param(
    [string]$RequestedDate,
    [pscustomobject]$DatePolicy
  )

  $culture = [System.Globalization.CultureInfo]::InvariantCulture
  $style = [System.Globalization.DateTimeStyles]::None
  $seedStart = [datetime]::ParseExact($DatePolicy.seed_start_date, 'yyyy-MM-dd', $culture, $style)
  $asOf = [datetime]::ParseExact($DatePolicy.canonical_as_of_date, 'yyyy-MM-dd', $culture, $style)
  $selected = if ($RequestedDate -eq '') { $DatePolicy.seed_start_date } else { $RequestedDate }
  if ($selected -cnotmatch '^[0-9]{4}-[0-9]{2}-[0-9]{2}$') {
    throw 'Report start date must be an ISO calendar date (YYYY-MM-DD).'
  }
  try {
    $start = [datetime]::ParseExact($selected, 'yyyy-MM-dd', $culture, $style)
  } catch {
    throw "Report start date is not a valid calendar date: $selected"
  }
  if ($start -lt $seedStart -or $start -gt $asOf) {
    throw "Report start date must be within the governed seeded window $($DatePolicy.seed_start_date) through $($DatePolicy.canonical_as_of_date)."
  }
  return $start.ToString('yyyy-MM-dd', $culture)
}

$demoDataContractPath = Join-Path $platformRoot 'context/contracts/canonical-front-office-demo-data-contract.json'
$demoDataContract = Get-Content -LiteralPath $demoDataContractPath -Raw | ConvertFrom-Json
$canonicalAsOfDate = $demoDataContract.date_policy.canonical_as_of_date
$resolvedReportStartDate = Resolve-CanonicalReportStartDate `
  -RequestedDate $ReportStartDate -DatePolicy $demoDataContract.date_policy
if ([string]::IsNullOrWhiteSpace($ProjectsRoot)) {
  $ProjectsRoot = Split-Path -Parent $platformRoot
}
if ([string]::IsNullOrWhiteSpace($WorkbenchRepoPath)) {
  $WorkbenchRepoPath = Join-Path $ProjectsRoot "lotus-workbench"
}
if ($CleanPlanOnly -and ($Clean -or $BringUp -or $CleanCoreState -or $BuildImages -or $RemoveImages -or $KeepRunning)) {
  throw "-CleanPlanOnly is read-only and cannot be combined with cleanup, startup, build, or keep-running switches."
}
if ($RequireMainlineSources -and -not $BringUp) {
  throw "-RequireMainlineSources requires -BringUp so Workbench can run mainline-source preflight before startup and validation."
}

function Resolve-CanonicalQaDpmSeedEnabled {
  param(
    [bool]$IsBringUp,
    [bool]$SkipRequested
  )

  return $IsBringUp -and -not $SkipRequested
}

function New-CanonicalQaBringUpArguments {
  param(
    [hashtable]$CommonArguments,
    [string]$AiEnvFile,
    [bool]$ShouldBuildImages,
    [bool]$ShouldRequireMainlineSources,
    [bool]$ShouldCleanCoreState,
    [int]$WaitSeconds
  )

  $arguments = $CommonArguments.Clone()
  if (-not [string]::IsNullOrWhiteSpace($AiEnvFile)) {
    $arguments.LotusAiEnvFile = $AiEnvFile
  }
  if ($ShouldBuildImages) {
    $arguments.BuildImages = $true
  }
  if ($ShouldRequireMainlineSources) {
    $arguments.RequireMainlineSources = $true
  }
  if ($ShouldCleanCoreState) {
    $arguments.CleanCoreState = $true
  }
  $arguments.SeedWaitSeconds = $WaitSeconds
  $arguments.RunValidation = $true
  return $arguments
}
if (-not $BringUp -and -not $Clean -and -not $CleanPlanOnly -and $ValidationProfile -eq 'full') {
  throw "Full validation must be run with -BringUp so Workbench can create the ephemeral Idea capacity capability. Use -ValidationProfile client-demo only for read-only validation of an already-running stack."
}
if ($BringUp -and $ValidationProfile -eq 'client-demo') {
  throw "-ValidationProfile client-demo cannot be combined with -BringUp. Governed startup always runs the strict full profile; client-demo is read-only validation of an already-running stack."
}
if ($BringUp -and $SkipDpmCommandCenterSeed) {
  throw "-SkipDpmCommandCenterSeed cannot be combined with -BringUp because governed Workbench startup always seeds DPM evidence."
}
$dpmCommandCenterSeedEnabled = Resolve-CanonicalQaDpmSeedEnabled `
  -IsBringUp ([bool]$BringUp) `
  -SkipRequested ([bool]$SkipDpmCommandCenterSeed)
if ($RequireMainlineSources -and -not $BuildImages) {
  $BuildImages = $true
}
$lotusIdeaRepoPath = Join-Path $ProjectsRoot "lotus-idea"
if (-not (Test-Path $WorkbenchRepoPath)) {
  throw "Workbench repository path not found: $WorkbenchRepoPath"
}

$startScript = Join-Path $WorkbenchRepoPath "scripts\live\Start-LotusFrontOfficeCanonical.ps1"
$validateScript = Join-Path $WorkbenchRepoPath "scripts\live\Validate-LotusFrontOfficeCanonical.ps1"
$stopScript = Join-Path $WorkbenchRepoPath "scripts\live\Stop-LotusFrontOfficeCanonical.ps1"
$dpmSeedScript = Join-Path $PSScriptRoot "Invoke-DpmCommandCenterSeed.ps1"
$dockerOwnershipScript = Join-Path $PSScriptRoot "canonical_docker_ownership.py"
$defaultScreenshotDirectory = Join-Path $WorkbenchRepoPath "output\playwright\live-canonical"
if ([string]::IsNullOrWhiteSpace($ScreenshotDirectory)) {
  $resolvedScreenshotDirectory = $defaultScreenshotDirectory
} elseif ([System.IO.Path]::IsPathRooted($ScreenshotDirectory)) {
  $resolvedScreenshotDirectory = $ScreenshotDirectory
} else {
  $resolvedScreenshotDirectory = Join-Path $platformRoot $ScreenshotDirectory
}
$liveSummaryPath = Join-Path $resolvedScreenshotDirectory "live-validation-summary.json"

foreach ($requiredPath in @($startScript, $validateScript, $stopScript, $dpmSeedScript, $dockerOwnershipScript)) {
  if (-not (Test-Path $requiredPath)) {
    throw "Required canonical front-office runtime artifact not found: $requiredPath"
  }
}

function Invoke-CanonicalRuntimeStep {
  param(
    [string]$StepName,
    [string]$ScriptPath,
    [hashtable]$Arguments
  )

  Write-Host "[$StepName] $ScriptPath"
  $preflightAction = if ($ScriptPath -eq $stopScript -and -not $Arguments['KeepReservation']) {
    'preflight-teardown'
  } else { 'preflight' }
  Invoke-CanonicalReservation -Action $preflightAction -ProjectsRoot $ProjectsRoot -Holder $RuntimeHolder -WorkbenchRepoPath $WorkbenchRepoPath | Out-Host
  if ($ScriptPath -eq $startScript -or $ScriptPath -eq $stopScript -or $ScriptPath -eq $validateScript -or $ScriptPath -eq $dpmSeedScript) {
    $Arguments['RuntimeHolder'] = $RuntimeHolder
    $Arguments['WorkbenchRepoPath'] = $WorkbenchRepoPath
    $Arguments['ProjectsRoot'] = $ProjectsRoot
  }
  $global:LASTEXITCODE = 0
  & $ScriptPath @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "$StepName failed with exit code $LASTEXITCODE."
  }
}

function Get-CanonicalDockerCleanupPlan {
  param([string[]]$IncludeProjects = @())

  $arguments = @(
    $dockerOwnershipScript,
    "--projects-root", $ProjectsRoot,
    "--workbench-repo-path", $WorkbenchRepoPath
  )
  foreach ($project in $IncludeProjects) {
    if (-not [string]::IsNullOrWhiteSpace($project)) {
      $arguments += @("--include-project", $project)
    }
  }

  $global:LASTEXITCODE = 0
  $json = & python @arguments
  if ($LASTEXITCODE -ne 0) {
    throw "Canonical Docker ownership inventory failed with exit code $LASTEXITCODE."
  }
  return ($json -join "`n") | ConvertFrom-Json
}

function Invoke-MainlineSourceProvenancePreflight {
  param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectsRoot,

    [Parameter(Mandatory = $true)]
    [string]$WorkbenchRepoPath,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath
  )

  $scriptPath = Join-Path $WorkbenchRepoPath "scripts\live\validation\mainline-source-provenance.mjs"
  if (-not (Test-Path $scriptPath)) {
    throw "Canonical mainline source provenance script not found: $scriptPath"
  }

  $global:LASTEXITCODE = 0
  & node $scriptPath --projects-root $ProjectsRoot --output $OutputPath
  if ($LASTEXITCODE -ne 0) {
    throw "Canonical mainline source provenance preflight failed before cleanup, Docker build, seed, or validation was started."
  }

  return [ordered]@{
    script_path = $scriptPath
    output_path = $OutputPath
  }
}

function Test-HttpEndpoint {
  param(
    [string]$Name,
    [string]$Url
  )

  try {
    $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 15
    [ordered]@{
      name = $Name
      url = $Url
      status_code = $response.StatusCode
      ready = ($response.StatusCode -ge 200 -and $response.StatusCode -lt 300)
      error = $null
    }
  } catch {
    [ordered]@{
      name = $Name
      url = $Url
      status_code = $null
      ready = $false
      error = $_.Exception.Message
    }
  }
}

function Wait-HttpEndpoint {
  param(
    [string]$Name,
    [string]$Url,
    [int]$Attempts = 12,
    [int]$DelaySeconds = 5
  )

  $latest = $null
  for ($attempt = 1; $attempt -le $Attempts; $attempt++) {
    $latest = Test-HttpEndpoint -Name $Name -Url $Url
    $latest["attempt"] = $attempt
    $latest["max_attempts"] = $Attempts
    if ($latest.ready) {
      return $latest
    }
    if ($attempt -lt $Attempts) {
      Start-Sleep -Seconds $DelaySeconds
    }
  }
  return $latest
}

function Invoke-LotusIdeaValidation {
  param([string]$RepoPath)

  $checks = @(
    Wait-HttpEndpoint -Name "lotus-idea-direct-readiness" -Url "http://127.0.0.1:8330/health/ready"
    Wait-HttpEndpoint -Name "lotus-idea-ingress-readiness" -Url "http://idea.dev.lotus/health/ready"
  )
  $allReady = -not ($checks | Where-Object { -not $_.ready })

  [ordered]@{
    repo_path = $RepoPath
    compose_file = (Join-Path $RepoPath "docker-compose.yml")
    direct_host = "http://127.0.0.1:8330"
    canonical_host = "http://idea.dev.lotus"
    checks = $checks
    ready = $allReady
  }
}

function Assert-NoOwnedDockerArtifacts {
  param(
    [pscustomobject]$Artifacts,
    [switch]$IncludeImages
  )

  $remaining = @()
  $requiredEmptyKeys = @("containers", "volumes")
  if ($IncludeImages) {
    $requiredEmptyKeys += "images"
  }

  foreach ($key in $requiredEmptyKeys) {
    foreach ($value in @($Artifacts.$key)) {
      $remaining += "$key`: $($value.name) [$($value.ownership_provenance)]"
    }
  }
  if ($remaining.Count -gt 0) {
    throw ("Canonical clean left run-owned Docker artifacts: {0}" -f ($remaining -join "; "))
  }
}

$resolvedOutputDirectory = if ([System.IO.Path]::IsPathRooted($OutputDirectory)) {
  $OutputDirectory
} else {
  Join-Path $platformRoot $OutputDirectory
}
New-Item -ItemType Directory -Path $resolvedOutputDirectory -Force | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$summaryJsonPath = Join-Path $resolvedOutputDirectory "canonical-front-office-qa-$timestamp.json"
$summaryMarkdownPath = Join-Path $resolvedOutputDirectory "canonical-front-office-qa-$timestamp.md"
$runtimeTranscriptPath = Join-Path $resolvedOutputDirectory "canonical-front-office-qa-$timestamp.log"
$cleanupPlanPath = Join-Path $resolvedOutputDirectory "canonical-front-office-cleanup-plan-$timestamp.json"
$mainlineSourcePreflightPath = Join-Path $resolvedOutputDirectory "mainline-source-provenance-preflight-$timestamp.json"
$latestCleanupPlanPath = Join-Path $resolvedOutputDirectory "cleanup-plan-latest.json"
$latestMainlineSourcePreflightPath = Join-Path $resolvedOutputDirectory "mainline-source-provenance-preflight-latest.json"
$latestJsonPath = Join-Path $resolvedOutputDirectory "latest.json"
$latestMarkdownPath = Join-Path $resolvedOutputDirectory "latest.md"
$latestTranscriptPath = Join-Path $resolvedOutputDirectory "latest.log"
$runStartedAt = Get-Date
$transcriptStarted = $false
$dockerBefore = Get-CanonicalDockerCleanupPlan
$profileExclusions = @()
if ($ValidationProfile -eq 'client-demo') {
  $profileExclusions = @([ordered]@{
    proofScope = 'idea.presentation_backed_downstream_capacity_probe'
    reasonCode = 'NON_CERTIFYING_CAPACITY_PROBE_EXCLUDED'
    owningIssue = 'sgajbi/lotus-idea#1345'
    claimBoundary = 'No Idea downstream-capacity acceptance or full-profile certification'
  })
}

function Assert-CanonicalQaLiveProfile {
  param(
    [pscustomobject]$LiveSummary,
    [string]$ValidationProfile,
    [object[]]$ExpectedExclusions
  )

  if ($LiveSummary.validationProfile -ne $ValidationProfile) {
    throw "Canonical Workbench validation profile differs from requested Platform profile: expected $ValidationProfile, observed $($LiveSummary.validationProfile)."
  }
  $actualExclusions = @($LiveSummary.excludedProofs)
  if ($actualExclusions.Count -ne $ExpectedExclusions.Count) {
    throw "Canonical Workbench validation exclusions differ from requested Platform profile."
  }
  for ($index = 0; $index -lt $ExpectedExclusions.Count; $index++) {
    foreach ($field in @('proofScope', 'reasonCode', 'owningIssue', 'claimBoundary')) {
      if ($actualExclusions[$index].$field -ne $ExpectedExclusions[$index].$field) {
        throw "Canonical Workbench validation excluded an unexpected proof or weakened its claim boundary."
      }
    }
  }
}

function Assert-CanonicalQaLiveWindow {
  param(
    [pscustomobject]$LiveSummary,
    [string]$PortfolioId,
    [string]$StartDate,
    [string]$EndDate
  )

  if ($LiveSummary.portfolioId -ne $PortfolioId) {
    throw "Canonical Workbench validation resolved a different portfolio: $($LiveSummary.portfolioId)."
  }
  $requiredChecks = @(
    @{ description = 'Performance summary evidence readiness'; path = "/api/v1/workbench/$PortfolioId/performance/summary"; status = 'ready' }
    @{ description = 'Risk summary'; path = "/api/v1/workbench/$PortfolioId/risk/summary"; status = '200' }
    @{ description = 'Advisor brief'; path = "/api/v1/workbench/$PortfolioId/performance/advisor-brief"; status = '200' }
  )
  foreach ($required in $requiredChecks) {
    $observed = @($LiveSummary.apiChecks | Where-Object {
      $_.description -eq $required.description -and [string]$_.status -eq $required.status
    })
    if ($observed.Count -ne 1) {
      throw "Canonical Workbench live evidence lacks a unique successful $($required.description) check."
    }
    try {
      $url = [uri]$observed[0].url
    } catch {
      throw "Canonical Workbench live evidence has an invalid $($required.description) URL."
    }
    if (-not $url.IsAbsoluteUri -or $url.AbsolutePath -cne $required.path) {
      throw "Canonical Workbench live evidence uses an unexpected $($required.description) route."
    }
    $pairs = @($url.Query.TrimStart('?').Split('&') | Where-Object { $_ -ne '' })
    foreach ($field in @(
      @{ key = 'report_start_date'; value = $StartDate }
      @{ key = 'report_end_date'; value = $EndDate }
    )) {
      $matching = @($pairs | Where-Object { $_ -cmatch "^$($field.key)=" })
      if ($matching.Count -ne 1 -or $matching[0] -cne "$($field.key)=$($field.value)") {
        throw "Canonical Workbench $($required.description) did not execute the selected $($field.key)."
      }
    }
  }
  foreach ($description in @('Performance calculation sanity', 'Risk calculation sanity')) {
    if (@($LiveSummary.calculationChecks | Where-Object { $_.description -eq $description }).Count -ne 1) {
      throw "Canonical Workbench live evidence lacks $description for the selected report window."
    }
  }
}

$summary = [ordered]@{
  generated_at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
  platform_root = $platformRoot
  projects_root = $ProjectsRoot
  workbench_repo_path = $WorkbenchRepoPath
  bring_up = [bool]$BringUp
  clean = [bool]$Clean
  clean_plan_only = [bool]$CleanPlanOnly
  clean_core_state = [bool]$CleanCoreState
  build_images = [bool]$BuildImages
  require_mainline_sources = [bool]$RequireMainlineSources
  remove_images = [bool]$RemoveImages
  include_lotus_idea = $true
  canonical_core_demo_pack_enabled = $false
  dpm_command_center_seed_enabled = $dpmCommandCenterSeedEnabled
  keep_running = [bool]$KeepRunning
  lotus_ai_env_file = $LotusAiEnvFile
  seed_wait_seconds = $SeedWaitSeconds
  portfolio_id = $PortfolioId
  benchmark_code = $BenchmarkCode
  validation_profile = $ValidationProfile
  report_start_date = $resolvedReportStartDate
  report_end_date = $canonicalAsOfDate
  excluded_proofs = $profileExclusions
  governed_runbook = (Join-Path $WorkbenchRepoPath "docs\operations\canonical-front-office-local-runtime.md")
  governed_live_summary = $liveSummaryPath
  screenshot_directory = $resolvedScreenshotDirectory
  runtime_transcript = $runtimeTranscriptPath
  lotus_idea = $null
  dpm_command_center_seed_summary = $null
  mainline_source_preflight = $null
  docker_ownership_policy = $dockerBefore.selection_policy
  docker_cleanup_plan_path = if ($Clean -or $CleanPlanOnly) { $cleanupPlanPath } else { $null }
  docker_before = $dockerBefore
  docker_after_clean = $null
  docker_after = $null
  status = "ok"
  steps = @()
  screenshots = @()
  error = $null
}

$commonArguments = @{
  ProjectsRoot = $ProjectsRoot
  PortfolioId = $PortfolioId
  BenchmarkCode = $BenchmarkCode
  StartDate = $resolvedReportStartDate
  AsOfDate = $canonicalAsOfDate
  ValidationProfile = $ValidationProfile
  ScreenshotDirectory = $resolvedScreenshotDirectory
  CanonicalEvidenceDirectory = $resolvedOutputDirectory
}
$validationArguments = @{
  PortfolioId = $PortfolioId
  BenchmarkCode = $BenchmarkCode
  ValidationProfile = $ValidationProfile
  StartDate = $resolvedReportStartDate
  AsOfDate = $canonicalAsOfDate
  ScreenshotDirectory = $resolvedScreenshotDirectory
}

try {
  Start-Transcript -Path $runtimeTranscriptPath -Force | Out-Null
  $transcriptStarted = $true

  $certifiedSourcePreflightPassed = $false
  if ($RequireMainlineSources) {
    $mainlineSourcePreflightScript = Join-Path $WorkbenchRepoPath "scripts\live\validation\mainline-source-provenance.mjs"
    $summary.mainline_source_preflight = [ordered]@{
      script_path = $mainlineSourcePreflightScript
      output_path = $mainlineSourcePreflightPath
    }
    $summary.mainline_source_preflight = Invoke-MainlineSourceProvenancePreflight `
      -ProjectsRoot $ProjectsRoot `
      -WorkbenchRepoPath $WorkbenchRepoPath `
      -OutputPath $mainlineSourcePreflightPath
    Copy-Item -Path $mainlineSourcePreflightPath -Destination $latestMainlineSourcePreflightPath -Force
    $summary.steps += "mainline-source-preflight"
    $certifiedSourcePreflightPassed = $true
  }

  if ($Clean -or $CleanPlanOnly) {
    $summary.docker_before | ConvertTo-Json -Depth 10 | Set-Content -Path $cleanupPlanPath
    $summary.docker_before | ConvertTo-Json -Depth 10 | Set-Content -Path $latestCleanupPlanPath
    Write-Host "[clean-plan] ownership policy: $($summary.docker_ownership_policy)"
    Write-Host "[clean-plan] compose projects: $(@($summary.docker_before.compose_projects) -join ', ')"
    foreach ($resourceType in @("containers", "volumes", "images")) {
      foreach ($resource in @($summary.docker_before.$resourceType)) {
        Write-Host "[clean-plan] $resourceType $($resource.name) [$($resource.ownership_provenance)]"
      }
    }
    $summary.steps += "clean-plan"
  }

  if ($CleanPlanOnly) {
    $summary.steps += "clean-plan-only"
  } elseif ($Clean) {
    if (@($summary.docker_before.ownership_conflicts).Count -gt 0) {
      $conflicts = @($summary.docker_before.ownership_conflicts | ForEach-Object {
        "$($_.name) project=$($_.compose_project) working_dir=$($_.compose_working_dir) repository_checkout=$($_.repository_checkout)"
      })
      throw ("Canonical clean blocked by Compose ownership conflicts: {0}" -f ($conflicts -join "; "))
    }
    $cleanArguments = @{
      ProjectsRoot = $ProjectsRoot
      RemoveVolumes = $true
    }
    if ($BringUp) { $cleanArguments.KeepReservation = $true }
    if ($RemoveImages) {
      $cleanArguments.RemoveImages = $true
    }
    Invoke-CanonicalRuntimeStep -StepName "clean" -ScriptPath $stopScript -Arguments $cleanArguments
    $summary.steps += "clean"
    $summary.docker_after_clean = Get-CanonicalDockerCleanupPlan `
      -IncludeProjects @($summary.docker_before.compose_projects)
    Assert-NoOwnedDockerArtifacts `
      -Artifacts $summary.docker_after_clean `
      -IncludeImages:$RemoveImages
  }

  if ($BringUp) {
    $bringUpArguments = New-CanonicalQaBringUpArguments `
      -CommonArguments $commonArguments `
      -AiEnvFile $LotusAiEnvFile `
      -ShouldBuildImages ([bool]$BuildImages) `
      -ShouldRequireMainlineSources ([bool]$RequireMainlineSources) `
      -ShouldCleanCoreState ([bool]$CleanCoreState) `
      -WaitSeconds $SeedWaitSeconds
    Invoke-CanonicalRuntimeStep -StepName "bring-up" -ScriptPath $startScript -Arguments $bringUpArguments
    $summary.steps += "bring-up"
    $summary.steps += "dpm-command-center-seed"
    $summary.steps += "validate"
  }

  if (-not $CleanPlanOnly -and ($BringUp -or (-not $Clean))) {
    if (-not (Test-Path $lotusIdeaRepoPath)) {
      throw "lotus-idea repository path not found: $lotusIdeaRepoPath"
    }
    if ($BringUp) {
      Write-Host "[lotus-idea] preserving governed runtime started and seeded by canonical Workbench startup"
    }

    $summary.lotus_idea = Invoke-LotusIdeaValidation -RepoPath $lotusIdeaRepoPath
    $summary.steps += "lotus-idea-validate"
    if (-not $summary.lotus_idea.ready) {
      throw "lotus-idea readiness validation failed. See lotus_idea checks in the QA summary."
    }
  }

  if (-not $CleanPlanOnly -and ($BringUp -or (-not $Clean))) {
    if (-not $BringUp -and $dpmCommandCenterSeedEnabled) {
      $dpmSeedArguments = @{
        OutputDirectory = $resolvedOutputDirectory
        PortfolioId = $PortfolioId
      }
      Invoke-CanonicalRuntimeStep -StepName "dpm-command-center-seed" -ScriptPath $dpmSeedScript -Arguments $dpmSeedArguments
      $summary.steps += "dpm-command-center-seed"
    }
    if ($dpmCommandCenterSeedEnabled) {
      $dpmSeedSummaryPath = Join-Path $resolvedOutputDirectory "dpm-command-center-seed-latest.json"
      if (-not (Test-Path $dpmSeedSummaryPath)) {
        throw "DPM command-center seed did not produce evidence: $dpmSeedSummaryPath"
      }
      $summary.dpm_command_center_seed_summary = Get-Content -Raw $dpmSeedSummaryPath | ConvertFrom-Json
    }
    if (-not $BringUp) {
      Invoke-CanonicalRuntimeStep -StepName "validate" -ScriptPath $validateScript -Arguments $validationArguments
      $summary.steps += "validate"
    }
  }

  if ($summary.steps -contains "bring-up" -or $summary.steps -contains "validate") {
    if (-not (Test-Path $liveSummaryPath)) {
      throw "Canonical Workbench validation did not produce a live summary: $liveSummaryPath"
    }
    $liveSummaryFile = Get-Item $liveSummaryPath
    if ($liveSummaryFile.LastWriteTime -lt $runStartedAt) {
      throw "Canonical Workbench validation summary is stale: $liveSummaryPath was last written at $($liveSummaryFile.LastWriteTime.ToString('yyyy-MM-ddTHH:mm:ssK'))."
    }
    $liveSummary = Get-Content -Raw $liveSummaryPath | ConvertFrom-Json
    Assert-CanonicalQaLiveProfile -LiveSummary $liveSummary -ValidationProfile $ValidationProfile -ExpectedExclusions $profileExclusions
    Assert-CanonicalQaLiveWindow -LiveSummary $liveSummary -PortfolioId $PortfolioId `
      -StartDate $resolvedReportStartDate -EndDate $canonicalAsOfDate
    $summary.screenshots = @($liveSummary.screenshots)
    $summary.live_validation_summary = $liveSummary
    $summary.canonical_contract = $liveSummary.canonicalContract
  }
} catch {
  $summary.status = "failed"
  $summary.error = $_.Exception.Message
} finally {
  if ($BringUp -and -not $KeepRunning -and (-not $RequireMainlineSources -or $certifiedSourcePreflightPassed)) {
    try {
      Invoke-CanonicalRuntimeStep -StepName "teardown" -ScriptPath $stopScript -Arguments @{ ProjectsRoot = $ProjectsRoot }
      $summary.steps += "lotus-idea-teardown"
      $summary.steps += "teardown"
    } catch {
      $summary.status = "failed"
      if (-not $summary.error) {
        $summary.error = $_.Exception.Message
      }
    }
  }
  $summary.docker_after = Get-CanonicalDockerCleanupPlan `
    -IncludeProjects @($summary.docker_before.compose_projects)
}

$summaryObject = [pscustomobject]$summary
$summaryObject | ConvertTo-Json -Depth 10 | Set-Content -Path $summaryJsonPath
$summaryObject | ConvertTo-Json -Depth 10 | Set-Content -Path $latestJsonPath

$markdown = @()
$markdown += "# Canonical Front-Office QA Summary"
$markdown += ""
$markdown += "- Generated: $($summary.generated_at)"
$markdown += "- Status: $($summary.status)"
$markdown += "- Bring up: $($summary.bring_up)"
$markdown += "- Clean: $($summary.clean)"
$markdown += "- Clean plan only: $($summary.clean_plan_only)"
$markdown += "- Clean core state: $($summary.clean_core_state)"
$markdown += "- Build images: $($summary.build_images)"
$markdown += "- Require mainline sources: $($summary.require_mainline_sources)"
$markdown += "- Validation profile: $($summary.validation_profile)"
$markdown += "- Report window: $($summary.report_start_date) through $($summary.report_end_date)"
foreach ($proof in @($summary.excluded_proofs)) {
  $markdown += "- Excluded proof: $($proof.proofScope) [$($proof.reasonCode); $($proof.owningIssue)] - $($proof.claimBoundary)"
}
$markdown += "- Remove images: $($summary.remove_images)"
$markdown += "- Include lotus-idea: $($summary.include_lotus_idea)"
$markdown += "- Canonical core demo pack enabled: $($summary.canonical_core_demo_pack_enabled)"
$markdown += "- DPM command-center seed enabled: $($summary.dpm_command_center_seed_enabled)"
$markdown += "- Keep running: $($summary.keep_running)"
$markdown += "- Lotus AI env file: $($summary.lotus_ai_env_file)"
$markdown += "- Seed wait seconds: $($summary.seed_wait_seconds)"
$markdown += "- Portfolio: $PortfolioId"
$markdown += "- Benchmark: $BenchmarkCode"
$markdown += "- Canonical contract: $($summary.canonical_contract.contractId) $($summary.canonical_contract.contractVersion)"
$markdown += "- Governed by: $($summary.canonical_contract.governedByRfc)"
$markdown += "- Workbench repo: $WorkbenchRepoPath"
$markdown += "- Governed runbook: $($summary.governed_runbook)"
$markdown += "- Live summary: $liveSummaryPath"
$markdown += "- Screenshot directory: $resolvedScreenshotDirectory"
$markdown += "- Runtime transcript: $runtimeTranscriptPath"
if ($summary.dpm_command_center_seed_summary) {
  $markdown += "- DPM command-center seed status: $($summary.dpm_command_center_seed_summary.status)"
  $markdown += "- DPM command-center seed mandate: $($summary.dpm_command_center_seed_summary.mandate_id)"
}
if ($summary.lotus_idea) {
  $markdown += "- lotus-idea ready: $($summary.lotus_idea.ready)"
  $markdown += "- lotus-idea direct host: $($summary.lotus_idea.direct_host)"
  $markdown += "- lotus-idea canonical host: $($summary.lotus_idea.canonical_host)"
}
$markdown += ""
$markdown += "## Steps"
$markdown += ""
foreach ($step in @($summary.steps)) {
  $markdown += "- $step"
}
$markdown += ""
$markdown += "## Docker Evidence"
$markdown += ""
$markdown += "- Ownership policy: $($summary.docker_ownership_policy)"
$markdown += "- Cleanup plan: $($summary.docker_cleanup_plan_path)"
$markdown += "- Mainline source preflight: $($summary.mainline_source_preflight.output_path)"
$markdown += "- Compose projects: $(@($summary.docker_before.compose_projects) -join ', ')"
$markdown += "- Ownership conflicts: $(@($summary.docker_before.ownership_conflicts).Count)"
$markdown += "- Containers before: $(@($summary.docker_before.containers).Count)"
$markdown += "- Volumes before: $(@($summary.docker_before.volumes).Count)"
$markdown += "- Images before: $(@($summary.docker_before.images).Count)"
if ($summary.docker_after_clean) {
  $markdown += "- Containers after clean: $(@($summary.docker_after_clean.containers).Count)"
  $markdown += "- Volumes after clean: $(@($summary.docker_after_clean.volumes).Count)"
  $markdown += "- Images after clean: $(@($summary.docker_after_clean.images).Count)"
}
if ($summary.docker_after) {
  $markdown += "- Containers after run: $(@($summary.docker_after.containers).Count)"
  $markdown += "- Volumes after run: $(@($summary.docker_after.volumes).Count)"
  $markdown += "- Images after run: $(@($summary.docker_after.images).Count)"
}
if ($summary.screenshots.Count -gt 0) {
  $markdown += ""
  $markdown += "## Screenshots"
  $markdown += ""
  foreach ($screenshot in @($summary.screenshots)) {
    if ($screenshot.path) {
      $markdown += "- $($screenshot.name) - $($screenshot.panel) - $($screenshot.path)"
    } else {
      $markdown += "- $screenshot"
    }
  }
}
if ($summary.lotus_idea) {
  $markdown += ""
  $markdown += "## lotus-idea"
  $markdown += ""
  foreach ($check in @($summary.lotus_idea.checks)) {
    $status = if ($check.ready) { "ready" } else { "failed" }
    $markdown += "- $($check.name): $status $($check.url)"
    if ($check.error) {
      $markdown += "  Error: $($check.error)"
    }
  }
}
if ($summary.error) {
  $markdown += ""
  $markdown += "## Error"
  $markdown += ""
  $markdown += "- $($summary.error)"
}
$markdown | Set-Content -Path $summaryMarkdownPath
$markdown | Set-Content -Path $latestMarkdownPath

Write-Host "Wrote $summaryJsonPath"
Write-Host "Wrote $summaryMarkdownPath"

if ($transcriptStarted) {
  Stop-Transcript | Out-Null
  Copy-Item -Path $runtimeTranscriptPath -Destination $latestTranscriptPath -Force
}

if ($summary.status -ne "ok") {
  exit 1
}
