param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("core-performance-baseline", "core-performance-green-lanes")]
    [string]$ValidationProfile,

    [ValidateSet("skip_seed", "fresh_seed")]
    [string]$ScenarioMode = "skip_seed",

    [string]$SharedScenarioSuffix,
    [string]$MwrScenarioSuffix,
    [string]$CoreIngestionBaseUrl = "http://127.0.0.1:8200",
    [string]$CoreQueryBaseUrl = "http://127.0.0.1:8202",
    [string]$PerformanceBaseUrl = "http://127.0.0.1:8002",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$artifactRoot = Join-Path $repoRoot "output/cross-app"
$profileManifestPath = Join-Path $PSScriptRoot "platform-validation-profiles.json"
$profileManifest = Get-Content -Raw $profileManifestPath | ConvertFrom-Json -AsHashtable

$selectedProfile = $profileManifest.profiles | Where-Object { $_.name -eq $ValidationProfile } | Select-Object -First 1
if (-not $selectedProfile) {
    throw "Unsupported validation profile '$ValidationProfile'."
}

$validationRuns = @($selectedProfile.targets)

Push-Location $repoRoot
try {
    if (-not $DryRun) {
        python -m pip install --upgrade pip
        python -m pip install requests
    }

    foreach ($validationRun in $validationRuns) {
        $target = $validationRun.name
        $args = @(
            "automation/core_performance_ci_entrypoint.py",
            "--target", $target,
            "--scenario-mode", $ScenarioMode,
            "--core-ingestion-base-url", $CoreIngestionBaseUrl,
            "--core-query-base-url", $CoreQueryBaseUrl,
            "--performance-base-url", $PerformanceBaseUrl
        )

        if ($validationRun.uses_shared_suffix -and $SharedScenarioSuffix) {
            $args += @("--shared-scenario-suffix", $SharedScenarioSuffix)
        }

        if ($validationRun.uses_mwr_suffix -and $MwrScenarioSuffix) {
            $args += @("--mwr-scenario-suffix", $MwrScenarioSuffix)
        }

        if ($DryRun) {
            Write-Host ("DRY RUN [{0}] python {1}" -f $ValidationProfile, ($args -join " "))
            continue
        }

        python @args
        $summaryPath = Join-Path $artifactRoot ("workflow-summary-{0}.md" -f $target)
        python automation/render_cross_app_workflow_summary.py --target $target --artifact-dir $artifactRoot --output-markdown $summaryPath
    }
}
finally {
    Pop-Location
}
