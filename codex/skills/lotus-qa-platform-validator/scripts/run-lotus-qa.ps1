param(
  [string]$Repo = "lotus-risk",
  [string]$PlatformPath = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")).Path,
  [switch]$BringUp,
  [switch]$CreateIssues,
  [switch]$KeepRunning,
  [switch]$DryRun,
  [switch]$Async
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $PlatformPath)) {
  throw "Platform path not found: $PlatformPath"
}

$qaScript = Join-Path $PlatformPath "automation/Invoke-Platform-QA.ps1"
if (-not (Test-Path $qaScript)) {
  throw "QA script not found: $qaScript"
}

$args = @(
  "-ExecutionPolicy", "Bypass",
  "-File", $qaScript,
  "-Repo", $Repo
)

if ($BringUp) { $args += "-BringUp" }
if ($CreateIssues) { $args += "-CreateIssues" }
if ($KeepRunning) { $args += "-KeepRunning" }
if ($DryRun) { $args += "-DryRun" }

if ($Async) {
  $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
  $runDir = Join-Path $PlatformPath "output/qa/$stamp"
  New-Item -ItemType Directory -Path $runDir -Force | Out-Null
  $outLog = Join-Path $runDir "runner.out.log"
  $errLog = Join-Path $runDir "runner.err.log"
  Start-Process -FilePath "powershell" -ArgumentList $args -WorkingDirectory $PlatformPath -RedirectStandardOutput $outLog -RedirectStandardError $errLog -WindowStyle Hidden
  $stamp | Set-Content -Path (Join-Path $PlatformPath "output/qa/latest-run.txt")
  Write-Output "Started async run: $stamp"
  Write-Output "Logs: $outLog"
  Write-Output "Err : $errLog"
  exit 0
}

Push-Location $PlatformPath
try {
  & powershell @args
  $latest = Get-ChildItem "output/qa" -Directory | Sort-Object Name -Descending | Select-Object -First 1
  if ($latest) {
    $latest.Name | Set-Content -Path "output/qa/latest-run.txt"
    Write-Output "Latest run: $($latest.Name)"
    Write-Output "Summary : output/qa/$($latest.Name)/qa-summary.md"
  }
} finally {
  Pop-Location
}
