param(
    [string]$ConfigPath = "automation/heartbeat-config.json",
    [string]$OutputDirectory = "",
    [string]$GeneratedAtUtc = "",
    [string]$Branch = ""
)

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptRoot
$python = & (Join-Path $scriptRoot "Resolve-PlatformAutomationPython.ps1")

$arguments = @(
    "automation/run_heartbeat.py",
    "--config",
    $ConfigPath
)

if ($OutputDirectory.Trim().Length -gt 0) {
    $arguments += @("--output-dir", $OutputDirectory)
}
if ($GeneratedAtUtc.Trim().Length -gt 0) {
    $arguments += @("--generated-at-utc", $GeneratedAtUtc)
}
if ($Branch.Trim().Length -gt 0) {
    $arguments += @("--branch", $Branch)
}

Push-Location $repoRoot
try {
    & $python @arguments
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}
finally {
    Pop-Location
}
