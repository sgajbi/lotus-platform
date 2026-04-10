param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("feature", "pr-merge", "main-releasability")]
    [string]$Lane
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

Push-Location $repoRoot
try {
    python -m pip install --upgrade pip
    python -m pip install pytest requests PyYAML

    python -m pytest tests/unit -q
    python automation/validate_workflow_security.py
    python automation/validate_container_build_baseline.py
    python automation/validate_platform_validation_coverage.py

    if ($Lane -in @("pr-merge", "main-releasability")) {
        & (Join-Path $repoRoot "automation\Validate-Backend-Standards.ps1")
    }
}
finally {
    Pop-Location
}
