param(
    [ValidateSet("core-performance-green-lanes")]
    [string]$ValidationProfile = "core-performance-green-lanes",

    [ValidateSet("fresh_seed", "skip_seed")]
    [string]$ScenarioMode = "fresh_seed",

    [string]$CoreIngestionBaseUrl = "http://127.0.0.1:8200",
    [string]$CoreQueryBaseUrl = "http://127.0.0.1:8202",
    [string]$PerformanceBaseUrl = "http://127.0.0.1:8002",
    [string]$ArtifactDirectory = "output/cross-app",
    [string]$OutputDirectory = "output/demo-readiness/platform",
    [switch]$SkipValidationRun
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

function Resolve-InputPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }
    return (Join-Path $repoRoot $Path)
}

$artifactRoot = Resolve-InputPath -Path $ArtifactDirectory
$outputRoot = Resolve-InputPath -Path $OutputDirectory
$validationExitCode = 0

Push-Location $repoRoot
try {
    $toolingPython = & (Join-Path $PSScriptRoot "Resolve-PlatformAutomationPython.ps1")

    if (-not $SkipValidationRun) {
        try {
            & (Join-Path $PSScriptRoot "Invoke-PlatformValidationLane.ps1") `
                -ValidationProfile $ValidationProfile `
                -ScenarioMode $ScenarioMode `
                -CoreIngestionBaseUrl $CoreIngestionBaseUrl `
                -CoreQueryBaseUrl $CoreQueryBaseUrl `
                -PerformanceBaseUrl $PerformanceBaseUrl
            $validationExitCode = $LASTEXITCODE
        }
        catch {
            $validationExitCode = if ($LASTEXITCODE) { $LASTEXITCODE } else { 1 }
            Write-Warning ("Platform validation lane failed before certification review: {0}" -f $_.Exception.Message)
        }
    }

    $expectedSeedMode = if ($ScenarioMode -eq "fresh_seed") { "fresh_seeded" } else { "reused_existing" }
    & $toolingPython automation/certify_platform_demo_readiness.py `
        --profile $ValidationProfile `
        --artifact-dir $artifactRoot `
        --output-dir $outputRoot `
        --validation-exit-code $validationExitCode `
        --expected-scenario-seed-mode $expectedSeedMode
}
finally {
    Pop-Location
}
