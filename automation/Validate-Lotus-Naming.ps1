param(
  [string]$ReposConfigPath = "automation/repos.json",
  [string]$OutputJson = "output/lotus-naming-conformance.json",
  [string]$OutputMarkdown = "output/lotus-naming-conformance.md",
  [switch]$IncludeRfcs
)

$ErrorActionPreference = "Stop"

$legacyTerms = @(
  ("advisor" + "-experience-api"),
  ("dpm" + "-rebalance-engine"),
  ("performance" + "Analytics"),
  ("portfolio" + "-analytics-system"),
  ("reporting" + "-aggregation-service"),
  ("pbwm" + "-platform-docs"),
  ("lotus" + "-reporting")
)

$repos = Get-Content -Raw $ReposConfigPath | ConvertFrom-Json
$rows = @()

foreach ($repo in $repos) {
  $repoName = [string]$repo.name
  $repoPath = [string]$repo.path
  if (-not (Test-Path $repoPath)) { continue }

  $globs = @(
    "--glob=!**/.git/**",
    "--glob=!**/.venv/**",
    "--glob=!**/node_modules/**",
    "--glob=!**/__pycache__/**",
    "--glob=!**/output/**",
    "--glob=!**/docs/RFCs/**",
    "--glob=!**/docs/rfcs/**",
    "--glob=!**/automation/repos.json",
    "--glob=!**/automation/service-map.json",
    "--glob=!**/docs/operations/Lotus Repository Rename Runbook.md",
    "--glob=!**/automation/Validate-Lotus-Naming.ps1"
  )
  if (-not $IncludeRfcs) {
    $globs += "--glob=!**/rfcs/**"
  }

  $count = 0
  $samples = @()
  foreach ($term in $legacyTerms) {
    $args = @("-n", "-S", $term, $repoPath) + $globs
    $hits = & rg @args 2>$null
    if ($LASTEXITCODE -eq 0 -and $hits) {
      $count += ($hits | Measure-Object).Count
      $samples += ($hits | Select-Object -First 2)
    }
  }

  $rows += [pscustomobject]@{
    repo = $repoName
    status = if ($count -eq 0) { "ok" } else { "gap" }
    findings = $count
    sample = (($samples | Select-Object -First 3) -join " || ")
  }
}

$summary = [pscustomobject]@{
  generated_at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
  include_rfcs = [bool]$IncludeRfcs
  rows = $rows
}

$summary | ConvertTo-Json -Depth 6 | Set-Content -Path $OutputJson

$lines = @()
$lines += "# Lotus Naming Conformance"
$lines += ""
$lines += "- Generated: $($summary.generated_at)"
$lines += "- Include RFC files: $([bool]$IncludeRfcs)"
$lines += "- Legacy terms: $($legacyTerms -join ', ')"
$lines += ""
$lines += "| Repo | Status | Findings | Sample |"
$lines += "|---|---|---:|---|"
foreach ($row in $rows) {
  $sample = ($row.sample -replace "\|", "/")
  $lines += "| $($row.repo) | $($row.status) | $($row.findings) | $sample |"
}

Set-Content -Path $OutputMarkdown -Value ($lines -join "`n")
Write-Host "Wrote $OutputJson"
Write-Host "Wrote $OutputMarkdown"



