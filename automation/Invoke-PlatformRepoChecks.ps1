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
    python -m pip install pytest requests

    python -m pytest tests/unit -q

    if ($Lane -in @("pr-merge", "main-releasability")) {
        powershell -ExecutionPolicy Bypass -File automation\Validate-Backend-Standards.ps1
    }
}
finally {
    Pop-Location
}
