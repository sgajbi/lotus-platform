param(
  [string]$ProjectsRoot,
  [string]$WorkbenchRepoPath,
  [string]$PortfolioId = "PB_SG_GLOBAL_BAL_001",
  [string]$BenchmarkCode = "BMK_PB_GLOBAL_BALANCED_60_40",
  [string]$OutputDirectory = "output/front-office-qa",
  [switch]$BringUp,
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
$liveSummaryPath = Join-Path $WorkbenchRepoPath "output\playwright\live-canonical\live-validation-summary.json"

foreach ($requiredPath in @($startScript, $validateScript, $stopScript)) {
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
  & $ScriptPath @Arguments
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
$latestJsonPath = Join-Path $resolvedOutputDirectory "latest.json"
$latestMarkdownPath = Join-Path $resolvedOutputDirectory "latest.md"

$summary = [ordered]@{
  generated_at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
  platform_root = $platformRoot
  projects_root = $ProjectsRoot
  workbench_repo_path = $WorkbenchRepoPath
  bring_up = [bool]$BringUp
  keep_running = [bool]$KeepRunning
  portfolio_id = $PortfolioId
  benchmark_code = $BenchmarkCode
  governed_runbook = (Join-Path $WorkbenchRepoPath "docs\operations\canonical-front-office-local-runtime.md")
  governed_live_summary = $liveSummaryPath
  status = "ok"
  steps = @()
  screenshots = @()
  error = $null
}

$commonArguments = @{
  ProjectsRoot = $ProjectsRoot
  PortfolioId = $PortfolioId
  BenchmarkCode = $BenchmarkCode
}

try {
  if ($BringUp) {
    Invoke-CanonicalRuntimeStep -StepName "bring-up" -ScriptPath $startScript -Arguments $commonArguments
    $summary.steps += "bring-up"
  } else {
    Invoke-CanonicalRuntimeStep -StepName "validate" -ScriptPath $validateScript -Arguments $commonArguments
    $summary.steps += "validate"
  }

  if (Test-Path $liveSummaryPath) {
    $liveSummary = Get-Content -Raw $liveSummaryPath | ConvertFrom-Json
    $summary.screenshots = @($liveSummary.screenshots)
    $summary.live_validation_summary = $liveSummary
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
$markdown += "- Keep running: $($summary.keep_running)"
$markdown += "- Portfolio: $PortfolioId"
$markdown += "- Benchmark: $BenchmarkCode"
$markdown += "- Workbench repo: $WorkbenchRepoPath"
$markdown += "- Governed runbook: $($summary.governed_runbook)"
$markdown += "- Live summary: $liveSummaryPath"
$markdown += ""
$markdown += "## Steps"
$markdown += ""
foreach ($step in @($summary.steps)) {
  $markdown += "- $step"
}
if ($summary.screenshots.Count -gt 0) {
  $markdown += ""
  $markdown += "## Screenshots"
  $markdown += ""
  foreach ($screenshot in @($summary.screenshots)) {
    $markdown += "- $screenshot"
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

if ($summary.status -ne "ok") {
  exit 1
}
