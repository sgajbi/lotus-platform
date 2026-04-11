param(
  [Parameter(Mandatory=$true)][string]$RepoAlias,
  [Parameter(Mandatory=$true)][string]$RepoSlug,
  [ValidateSet("validate","syncissues","fullcycle","monitorpr","revalidate")][string]$Phase = "fullcycle",
  [string]$PlatformPath = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")).Path,
  [switch]$BringUp,
  [switch]$AutoCloseResolved,
  [int]$PrNumber = 0,
  [int]$PollSeconds = 20,
  [int]$TimeoutMinutes = 60
)

$ErrorActionPreference = "Stop"

$qaRunner = Join-Path $PlatformPath "codex/skills/lotus-qa-platform-validator/scripts/run-lotus-qa.ps1"
$issueLoop = Join-Path $PlatformPath "codex/skills/gh-issue-fix-qa-loop/scripts/update-issue-loop.ps1"
if (-not (Test-Path $qaRunner)) { throw "QA runner not found: $qaRunner" }
if (-not (Test-Path $issueLoop)) { throw "Issue loop script not found: $issueLoop" }
if (-not (Test-Path $PlatformPath)) { throw "Platform path not found: $PlatformPath" }

function Get-LatestRunId {
  param([string]$Path)
  $latestFile = Join-Path $Path "output/qa/latest-run.txt"
  if (Test-Path $latestFile) {
    $candidate = (Get-Content -Raw $latestFile).Trim()
    if (-not [string]::IsNullOrWhiteSpace($candidate)) {
      $summary = Join-Path $Path "output/qa/$candidate/qa-summary.json"
      if (Test-Path $summary) {
        return $candidate
      }
    }
  }
  $dirs = Get-ChildItem (Join-Path $Path "output/qa") -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending
  foreach ($dir in $dirs) {
    $summary = Join-Path $dir.FullName "qa-summary.json"
    if (Test-Path $summary) {
      return $dir.Name
    }
  }
  return $null
}

function Run-Validation {
  & powershell -ExecutionPolicy Bypass -File $qaRunner -Repo $RepoAlias @(
    if ($BringUp) { "-BringUp" }
  ) -CreateIssues

  $runId = Get-LatestRunId -Path $PlatformPath
  if ([string]::IsNullOrWhiteSpace($runId)) { throw "No QA run id detected." }

  $summaryPath = Join-Path $PlatformPath "output/qa/$runId/qa-summary.json"
  $issuesPath = Join-Path $PlatformPath "output/qa/$runId/qa-issues.json"
  if (-not (Test-Path $summaryPath)) { throw "Missing summary: $summaryPath" }
  $issuesData = @()
  if (Test-Path $issuesPath) {
    $parsedIssues = Get-Content -Raw $issuesPath | ConvertFrom-Json
    if ($null -ne $parsedIssues) { $issuesData = @($parsedIssues) }
  }

  return [pscustomobject]@{
    run_id = $runId
    summary_path = $summaryPath
    issues_path = $issuesPath
    summary = (Get-Content -Raw $summaryPath | ConvertFrom-Json)
    issues = $issuesData
  }
}

function Sync-Issues {
  param(
    [object]$RunData
  )

  $actualByCheck = @{}
  foreach ($f in $RunData.summary.findings) { $actualByCheck[[string]$f.check_id] = [string]$f.actual }
  $failingChecks = @($actualByCheck.Keys)

  foreach ($r in $RunData.issues) {
    $url = [string]$r.issue_response
    if ($url -match "/issues/(\d+)") {
      $issueNumber = [int]$matches[1]
      $check = [string]$r.check_id
      $summary = if ($actualByCheck.ContainsKey($check)) { $actualByCheck[$check] } else { "QA failed for $check" }
      & powershell -ExecutionPolicy Bypass -File $issueLoop -Repo $RepoSlug -IssueNumber $issueNumber -Status qa_failed -QaRunRef ("output/qa/{0}/qa-summary.md" -f $RunData.run_id) -Summary $summary
    }
  }

  if ($AutoCloseResolved) {
    $open = gh issue list --repo $RepoSlug --state open --limit 200 --json number,title,url | ConvertFrom-Json
    foreach ($issue in $open) {
      $title = [string]$issue.title
      if ($title -match "^\[QA\]\[automation\]\s+$([regex]::Escape($RepoAlias))\s+::\s+(.+)$") {
        $checkId = [string]$matches[1]
        if (-not ($failingChecks -contains $checkId)) {
          & powershell -ExecutionPolicy Bypass -File $issueLoop -Repo $RepoSlug -IssueNumber ([int]$issue.number) -Status qa_passed_closed -QaRunRef ("output/qa/{0}/qa-summary.md" -f $RunData.run_id)
        }
      }
    }
  }
}

function Wait-ForPrMerge {
  param([int]$Number)
  if ($Number -le 0) { throw "PrNumber must be > 0 for monitorpr phase." }
  $start = Get-Date
  while ($true) {
    $pr = gh pr view $Number --repo $RepoSlug --json state,mergedAt,url | ConvertFrom-Json
    if ($pr.state -eq "MERGED" -or -not [string]::IsNullOrWhiteSpace([string]$pr.mergedAt)) {
      Write-Output "PR merged: $($pr.url)"
      return
    }
    if (((Get-Date) - $start).TotalMinutes -ge $TimeoutMinutes) {
      throw "Timed out waiting for PR #$Number to merge."
    }
    Start-Sleep -Seconds $PollSeconds
  }
}

if ($Phase -eq "validate") {
  $r = Run-Validation
  Write-Output "Validation run: $($r.run_id)"
  exit 0
}

if ($Phase -eq "syncissues") {
  $runId = Get-LatestRunId -Path $PlatformPath
  if ([string]::IsNullOrWhiteSpace($runId)) { throw "No run id available for syncissues." }
  $summaryPath = Join-Path $PlatformPath "output/qa/$runId/qa-summary.json"
  $issuesPath = Join-Path $PlatformPath "output/qa/$runId/qa-issues.json"
  $issuesData = @()
  if (Test-Path $issuesPath) {
    $parsedIssues = Get-Content -Raw $issuesPath | ConvertFrom-Json
    if ($null -ne $parsedIssues) { $issuesData = @($parsedIssues) }
  }
  $r = [pscustomobject]@{
    run_id = $runId
    summary = (Get-Content -Raw $summaryPath | ConvertFrom-Json)
    issues = $issuesData
  }
  Sync-Issues -RunData $r
  Write-Output "Issue sync complete for run: $runId"
  exit 0
}

if ($Phase -eq "monitorpr") {
  Wait-ForPrMerge -Number $PrNumber
  $r = Run-Validation
  Sync-Issues -RunData $r
  Write-Output "Post-merge revalidation complete: $($r.run_id)"
  exit 0
}

if ($Phase -eq "revalidate") {
  $r = Run-Validation
  Sync-Issues -RunData $r
  Write-Output "Revalidation complete: $($r.run_id)"
  exit 0
}

if ($Phase -eq "fullcycle") {
  $r = Run-Validation
  Sync-Issues -RunData $r
  Write-Output "Full cycle complete: $($r.run_id)"
  exit 0
}
