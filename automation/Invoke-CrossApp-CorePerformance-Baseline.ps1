param(
  [switch]$SkipSeed,
  [string]$SharedScenarioSuffix,
  [string]$MwrScenarioSuffix,
  [string]$OutputJson = "output/cross-app/core-performance-baseline-validation.json",
  [string]$OutputMarkdown = "output/cross-app/core-performance-baseline-validation.md"
)

$ErrorActionPreference = "Stop"

$arguments = @(
  "automation/core_performance_baseline_validation.py",
  "--output-json", $OutputJson,
  "--output-markdown", $OutputMarkdown
)

if ($SkipSeed) {
  $arguments += "--skip-seed"
}

if ($SharedScenarioSuffix) {
  $arguments += @("--shared-scenario-suffix", $SharedScenarioSuffix)
}

if ($MwrScenarioSuffix) {
  $arguments += @("--mwr-scenario-suffix", $MwrScenarioSuffix)
}

python @arguments

exit $LASTEXITCODE
