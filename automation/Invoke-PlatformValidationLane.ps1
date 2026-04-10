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

$validationRuns = switch ($ValidationProfile) {
    "core-performance-baseline" {
        @(
            @{
                Target = "baseline"
                UsesSharedSuffix = $true
                UsesMwrSuffix = $true
            }
        )
    }
    "core-performance-green-lanes" {
        @(
            @{
                Target = "twr_benchmark"
                UsesSharedSuffix = $true
                UsesMwrSuffix = $false
            },
            @{
                Target = "returns_series"
                UsesSharedSuffix = $true
                UsesMwrSuffix = $false
            },
            @{
                Target = "contribution"
                UsesSharedSuffix = $true
                UsesMwrSuffix = $false
            },
            @{
                Target = "mwr"
                UsesSharedSuffix = $false
                UsesMwrSuffix = $true
            }
        )
    }
}

Push-Location $repoRoot
try {
    if (-not $DryRun) {
        python -m pip install --upgrade pip
        python -m pip install requests
    }

    foreach ($validationRun in $validationRuns) {
        $target = $validationRun.Target
        $args = @(
            "automation/core_performance_ci_entrypoint.py",
            "--target", $target,
            "--scenario-mode", $ScenarioMode,
            "--core-ingestion-base-url", $CoreIngestionBaseUrl,
            "--core-query-base-url", $CoreQueryBaseUrl,
            "--performance-base-url", $PerformanceBaseUrl
        )

        if ($validationRun.UsesSharedSuffix -and $SharedScenarioSuffix) {
            $args += @("--shared-scenario-suffix", $SharedScenarioSuffix)
        }

        if ($validationRun.UsesMwrSuffix -and $MwrScenarioSuffix) {
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
