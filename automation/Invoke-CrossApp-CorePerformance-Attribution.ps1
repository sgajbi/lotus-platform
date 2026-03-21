param(
  [string]$CoreRepoPath = "C:/Users/Sandeep/projects/lotus-core",
  [string]$PerformanceRepoPath = "C:/Users/Sandeep/projects/lotus-performance",
  [switch]$BringUp,
  [string]$OutputJson = "output/cross-app/core-performance-attribution-validation.json",
  [string]$OutputMarkdown = "output/cross-app/core-performance-attribution-validation.md"
)

$ErrorActionPreference = "Stop"

if ($BringUp) {
  Push-Location $CoreRepoPath
  try {
    docker compose up -d
  }
  finally {
    Pop-Location
  }

  Push-Location $PerformanceRepoPath
  try {
    docker compose up -d performance-lineage-db performance-analytics
  }
  finally {
    Pop-Location
  }
}

python automation/core_performance_attribution_validation.py `
  --output-json $OutputJson `
  --output-markdown $OutputMarkdown

exit $LASTEXITCODE
