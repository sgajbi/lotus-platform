param(
  [int]$IntervalSeconds = 120,
  [string]$ConfigPath = "automation/repos.json",
  [string]$OutputPath = "output/agent-status.md",
  [string]$JsonOutputPath = "output/agent-status.json",
  [int]$FullAuditEvery = 5,
  [switch]$Once
)

$ErrorActionPreference = "Stop"

function Write-Status {
  param([string]$Path, [string[]]$Lines)
  $dir = Split-Path -Parent $Path
  if ($dir -and -not (Test-Path $dir)) {
    New-Item -ItemType Directory -Force $dir | Out-Null
  }
  $Lines | Set-Content $Path
}

function Invoke-Step {
  param(
    [string]$Name,
    [scriptblock]$Action
  )

  $start = Get-Date
  $ok = $true
  $output = ""
  $exitCode = 0
  try {
    $global:LASTEXITCODE = 0
    $output = & $Action 2>&1 | Out-String
    $exitCode = if ($null -eq $LASTEXITCODE) { 0 } else { [int]$LASTEXITCODE }
    if ($exitCode -ne 0) {
      $ok = $false
    }
  } catch {
    $ok = $false
    $exitCode = 1
    $output = $_.ToString()
  }
  $end = Get-Date

  return [pscustomobject]@{
    name = $Name
    ok = $ok
    started_at = $start.ToString("s")
    finished_at = $end.ToString("s")
    duration_sec = [Math]::Round(($end - $start).TotalSeconds, 2)
    exit_code = $exitCode
    output = $output.TrimEnd()
  }
}

$iteration = 0
while ($true) {
  $iteration += 1
  $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
  $runFullAudit = ($iteration % $FullAuditEvery -eq 0)

  $steps = @()
  $steps += Invoke-Step -Name "sync" -Action { powershell -ExecutionPolicy Bypass -File "automation/Sync-Repos.ps1" -ConfigPath $ConfigPath }
  $steps += Invoke-Step -Name "pr-monitor" -Action { powershell -ExecutionPolicy Bypass -File "automation/PR-Monitor.ps1" -ConfigPath $ConfigPath -OutputPath "output/pr-monitor.json" -IncludeChecks }
  $steps += Invoke-Step -Name "stalled-pr-checks" -Action { powershell -ExecutionPolicy Bypass -File "automation/Detect-Stalled-PR-Checks.ps1" -ConfigPath $ConfigPath -StaleMinutes 20 }
  $steps += Invoke-Step -Name "background-runs" -Action { powershell -ExecutionPolicy Bypass -File "automation/Check-Background-Runs.ps1" }
  $steps += Invoke-Step -Name "backend-standards" -Action { powershell -ExecutionPolicy Bypass -File "automation/Validate-Backend-Standards.ps1" }
  $steps += Invoke-Step -Name "openapi-conformance" -Action { powershell -ExecutionPolicy Bypass -File "automation/Validate-OpenAPI-Conformance.ps1" }
  $steps += Invoke-Step -Name "domain-vocabulary" -Action { powershell -ExecutionPolicy Bypass -File "automation/Validate-Domain-Vocabulary.ps1" }
  $steps += Invoke-Step -Name "shared-infra-ownership" -Action { powershell -ExecutionPolicy Bypass -File "automation/Validate-Shared-Infrastructure-Ownership.ps1" }
  $steps += Invoke-Step -Name "repo-metadata" -Action { powershell -ExecutionPolicy Bypass -File "automation/Verify-Repo-Metadata.ps1" }

  if ($runFullAudit) {
    $steps += Invoke-Step -Name "test-pyramid-full" -Action { powershell -ExecutionPolicy Bypass -File "automation/Measure-Test-Pyramid.ps1" -RunCoverage }
    $steps += Invoke-Step -Name "dependency-rollup" -Action { powershell -ExecutionPolicy Bypass -File "automation/Generate-Dependency-Vulnerability-Rollup.ps1" }
  } else {
    $steps += Invoke-Step -Name "test-pyramid" -Action { powershell -ExecutionPolicy Bypass -File "automation/Measure-Test-Pyramid.ps1" }
  }

  $steps += Invoke-Step -Name "summarize-failures" -Action { powershell -ExecutionPolicy Bypass -File "automation/Summarize-Task-Failures.ps1" -Latest 3 }

  $failedSteps = @($steps | Where-Object { -not $_.ok })
  $statusObj = [pscustomobject]@{
    updated_at = (Get-Date).ToString("s")
    iteration = $iteration
    run_full_audit = $runFullAudit
    failed_step_count = $failedSteps.Count
    steps = $steps
  }

  $jsonDir = Split-Path -Parent $JsonOutputPath
  if ($jsonDir -and -not (Test-Path $jsonDir)) {
    New-Item -ItemType Directory -Force $jsonDir | Out-Null
  }
  $statusObj | ConvertTo-Json -Depth 8 | Set-Content $JsonOutputPath

  $lines = @()
  $lines += "# Platform Agent Status"
  $lines += ""
  $lines += "Updated: $timestamp"
  $lines += "Iteration: $iteration"
  $lines += "Full audit run: $runFullAudit"
  $lines += "Failed steps: $($failedSteps.Count)"
  $lines += ""

  foreach ($step in $steps) {
    $lines += "## $($step.name)"
    $lines += "status: $(if ($step.ok) { 'ok' } else { 'failed' }) | duration: $($step.duration_sec)s | exit_code: $($step.exit_code)"
    $lines += '```text'
    $lines += $step.output
    $lines += '```'
    $lines += ""
  }

  Write-Status -Path $OutputPath -Lines $lines
  Write-Host "[$timestamp] agent iteration complete (failed_steps=$($failedSteps.Count)). Next run in $IntervalSeconds sec."

  if ($Once) {
    break
  }

  Start-Sleep -Seconds $IntervalSeconds
}

