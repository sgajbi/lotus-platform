param(
  [string]$ProjectsRoot,
  [string]$WorkbenchRepoPath,
  [string]$PortfolioId = "PB_SG_GLOBAL_BAL_001",
  [string]$BenchmarkCode = "BMK_PB_GLOBAL_BALANCED_60_40",
  [string]$OutputDirectory = "output/front-office-qa",
  [string]$ScreenshotDirectory = "",
  [string]$LotusAiEnvFile = "",
  [int]$SeedWaitSeconds = 900,
  [switch]$BringUp,
  [switch]$Clean,
  [switch]$CleanCoreState,
  [switch]$BuildImages,
  [switch]$RemoveImages,
  [switch]$SkipDpmCommandCenterSeed,
  [switch]$KeepRunning
)

$ErrorActionPreference = "Stop"

$platformRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ProjectsRoot)) {
  $ProjectsRoot = Split-Path -Parent $platformRoot
}
if ([string]::IsNullOrWhiteSpace($WorkbenchRepoPath)) {
  $WorkbenchRepoPath = Join-Path $ProjectsRoot "lotus-workbench"
}
if (-not (Test-Path $WorkbenchRepoPath)) {
  throw "Workbench repository path not found: $WorkbenchRepoPath"
}

$startScript = Join-Path $WorkbenchRepoPath "scripts\live\Start-LotusFrontOfficeCanonical.ps1"
$validateScript = Join-Path $WorkbenchRepoPath "scripts\live\Validate-LotusFrontOfficeCanonical.ps1"
$stopScript = Join-Path $WorkbenchRepoPath "scripts\live\Stop-LotusFrontOfficeCanonical.ps1"
$dpmSeedScript = Join-Path $PSScriptRoot "Invoke-DpmCommandCenterSeed.ps1"
$defaultScreenshotDirectory = Join-Path $WorkbenchRepoPath "output\playwright\live-canonical"
if ([string]::IsNullOrWhiteSpace($ScreenshotDirectory)) {
  $resolvedScreenshotDirectory = $defaultScreenshotDirectory
} elseif ([System.IO.Path]::IsPathRooted($ScreenshotDirectory)) {
  $resolvedScreenshotDirectory = $ScreenshotDirectory
} else {
  $resolvedScreenshotDirectory = Join-Path $platformRoot $ScreenshotDirectory
}
$liveSummaryPath = Join-Path $resolvedScreenshotDirectory "live-validation-summary.json"

foreach ($requiredPath in @($startScript, $validateScript, $stopScript, $dpmSeedScript)) {
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
  $global:LASTEXITCODE = 0
  & $ScriptPath @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "$StepName failed with exit code $LASTEXITCODE."
  }
}

function Get-LotusDockerArtifacts {
  $containers = @(
    docker ps -a --format "{{.Names}}" |
      Where-Object { $_ -match "^(lotus|pbwm|performance)" -or $_ -eq "lotus-direct-dev-ingress" }
  )
  $volumes = @(
    docker volume ls -q |
      Where-Object { $_ -match "^(lotus|pbwm|performance)" }
  )
  $images = @(
    docker images --format "{{.Repository}}:{{.Tag}}" |
      Where-Object { $_ -match "^(lotus|pbwm|performance)" }
  )

  [ordered]@{
    containers = $containers
    volumes = $volumes
    images = $images
  }
}

function Remove-LotusDockerArtifacts {
  param(
    [hashtable]$Artifacts,
    [switch]$IncludeImages
  )

  foreach ($container in @($Artifacts["containers"])) {
    if (-not [string]::IsNullOrWhiteSpace($container)) {
      Write-Host "[clean] removing container $container"
      docker rm -f $container | Out-Null
    }
  }

  foreach ($volume in @($Artifacts["volumes"])) {
    if (-not [string]::IsNullOrWhiteSpace($volume)) {
      Write-Host "[clean] removing volume $volume"
      docker volume rm $volume | Out-Null
    }
  }

  if ($IncludeImages) {
    foreach ($image in @($Artifacts["images"])) {
      if (-not [string]::IsNullOrWhiteSpace($image)) {
        Write-Host "[clean] removing image $image"
        docker image rm -f $image | Out-Null
      }
    }
  }
}

function Assert-NoLotusDockerArtifacts {
  param(
    [hashtable]$Artifacts,
    [switch]$IncludeImages
  )

  $remaining = @()
  $requiredEmptyKeys = @("containers", "volumes")
  if ($IncludeImages) {
    $requiredEmptyKeys += "images"
  }

  foreach ($key in $requiredEmptyKeys) {
    foreach ($value in @($Artifacts[$key])) {
      $remaining += "$key`: $value"
    }
  }
  if ($remaining.Count -gt 0) {
    throw ("Full clean left stale Lotus Docker artifacts: {0}" -f ($remaining -join "; "))
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
$latestJsonPath = Join-Path $resolvedOutputDirectory "latest.json"
$latestMarkdownPath = Join-Path $resolvedOutputDirectory "latest.md"
$latestTranscriptPath = Join-Path $resolvedOutputDirectory "latest.log"
$runStartedAt = Get-Date
$transcriptStarted = $false

$summary = [ordered]@{
  generated_at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
  platform_root = $platformRoot
  projects_root = $ProjectsRoot
  workbench_repo_path = $WorkbenchRepoPath
  bring_up = [bool]$BringUp
  clean = [bool]$Clean
  clean_core_state = [bool]$CleanCoreState
  build_images = [bool]$BuildImages
  remove_images = [bool]$RemoveImages
  dpm_command_center_seed_enabled = -not [bool]$SkipDpmCommandCenterSeed
  keep_running = [bool]$KeepRunning
  lotus_ai_env_file = $LotusAiEnvFile
  seed_wait_seconds = $SeedWaitSeconds
  portfolio_id = $PortfolioId
  benchmark_code = $BenchmarkCode
  governed_runbook = (Join-Path $WorkbenchRepoPath "docs\operations\canonical-front-office-local-runtime.md")
  governed_live_summary = $liveSummaryPath
  screenshot_directory = $resolvedScreenshotDirectory
  runtime_transcript = $runtimeTranscriptPath
  dpm_command_center_seed_summary = $null
  docker_before = Get-LotusDockerArtifacts
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
  ScreenshotDirectory = $resolvedScreenshotDirectory
}
$validationArguments = @{
  PortfolioId = $PortfolioId
  BenchmarkCode = $BenchmarkCode
  ScreenshotDirectory = $resolvedScreenshotDirectory
}

try {
  Start-Transcript -Path $runtimeTranscriptPath -Force | Out-Null
  $transcriptStarted = $true

  if ($Clean) {
    $cleanArguments = @{
      ProjectsRoot = $ProjectsRoot
      RemoveVolumes = $true
    }
    if ($RemoveImages) {
      $cleanArguments.RemoveImages = $true
    }
    Invoke-CanonicalRuntimeStep -StepName "clean" -ScriptPath $stopScript -Arguments $cleanArguments
    $summary.steps += "clean"
    Remove-LotusDockerArtifacts -Artifacts (Get-LotusDockerArtifacts) -IncludeImages:$RemoveImages
    $summary.docker_after_clean = Get-LotusDockerArtifacts
    Assert-NoLotusDockerArtifacts -Artifacts $summary.docker_after_clean -IncludeImages:$RemoveImages
  }

  if ($BringUp) {
    $bringUpArguments = $commonArguments.Clone()
    if (-not [string]::IsNullOrWhiteSpace($LotusAiEnvFile)) {
      $bringUpArguments.LotusAiEnvFile = $LotusAiEnvFile
    }
    if ($BuildImages) {
      $bringUpArguments.BuildImages = $true
    }
    if ($CleanCoreState) {
      $bringUpArguments.CleanCoreState = $true
    }
    $bringUpArguments.SeedWaitSeconds = $SeedWaitSeconds
    $bringUpArguments.Remove("ScreenshotDirectory")
    Invoke-CanonicalRuntimeStep -StepName "bring-up" -ScriptPath $startScript -Arguments $bringUpArguments
    $summary.steps += "bring-up"
  }

  if ($BringUp -or (-not $Clean)) {
    if (-not $SkipDpmCommandCenterSeed) {
      $dpmSeedArguments = @{
        OutputDirectory = $resolvedOutputDirectory
        PortfolioId = $PortfolioId
      }
      Invoke-CanonicalRuntimeStep -StepName "dpm-command-center-seed" -ScriptPath $dpmSeedScript -Arguments $dpmSeedArguments
      $summary.steps += "dpm-command-center-seed"

      $dpmSeedSummaryPath = Join-Path $resolvedOutputDirectory "dpm-command-center-seed-latest.json"
      if (-not (Test-Path $dpmSeedSummaryPath)) {
        throw "DPM command-center seed did not produce evidence: $dpmSeedSummaryPath"
      }
      $summary.dpm_command_center_seed_summary = Get-Content -Raw $dpmSeedSummaryPath | ConvertFrom-Json
    }

    Invoke-CanonicalRuntimeStep -StepName "validate" -ScriptPath $validateScript -Arguments $validationArguments
    $summary.steps += "validate"
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
    $summary.screenshots = @($liveSummary.screenshots)
    $summary.live_validation_summary = $liveSummary
    $summary.canonical_contract = $liveSummary.canonicalContract
  }
} catch {
  $summary.status = "failed"
  $summary.error = $_.Exception.Message
} finally {
  if ($BringUp -and -not $KeepRunning) {
    try {
      Invoke-CanonicalRuntimeStep -StepName "teardown" -ScriptPath $stopScript -Arguments @{ ProjectsRoot = $ProjectsRoot }
      $summary.steps += "teardown"
    } catch {
      $summary.status = "failed"
      if (-not $summary.error) {
        $summary.error = $_.Exception.Message
      }
    }
  }
  $summary.docker_after = Get-LotusDockerArtifacts
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
$markdown += "- Clean core state: $($summary.clean_core_state)"
$markdown += "- Build images: $($summary.build_images)"
$markdown += "- Remove images: $($summary.remove_images)"
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
$markdown += ""
$markdown += "## Steps"
$markdown += ""
foreach ($step in @($summary.steps)) {
  $markdown += "- $step"
}
$markdown += ""
$markdown += "## Docker Evidence"
$markdown += ""
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
