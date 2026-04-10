param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("feature", "pr-merge", "main-releasability")]
    [string]$Lane
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

Push-Location $repoRoot
try {
    $toolingPython = & (Join-Path $PSScriptRoot "Resolve-PlatformAutomationPython.ps1")

    & $toolingPython -m pytest tests/unit -q
    & $toolingPython automation/validate_workflow_security.py
    & $toolingPython automation/validate_container_build_baseline.py
    & $toolingPython automation/validate_platform_validation_coverage.py

    if ($Lane -in @("pr-merge", "main-releasability")) {
        & (Join-Path $repoRoot "automation\Validate-Backend-Standards.ps1")
    }
}
finally {
    Pop-Location
}
