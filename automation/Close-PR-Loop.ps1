param(
  [string]$ConfigPath = "automation/repos.json",
  [string]$OutputPath = "output/pr-lifecycle.json",
  [string]$SummaryPath = "output/pr-lifecycle.md",
  [string]$PrSearch = "author:@me",
  [string]$MergeMethod = "rebase",
  [int]$MergedSinceDays = 14,
  [int]$IntervalSeconds = 30,
  [switch]$Watch,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$scriptRoot = Split-Path -Parent $PSCommandPath

if (-not [System.IO.Path]::IsPathRooted($ConfigPath)) {
  $ConfigPath = Join-Path $scriptRoot "..\$ConfigPath"
}
if (-not [System.IO.Path]::IsPathRooted($OutputPath)) {
  $OutputPath = Join-Path $scriptRoot "..\$OutputPath"
}
if (-not [System.IO.Path]::IsPathRooted($SummaryPath)) {
  $SummaryPath = Join-Path $scriptRoot "..\$SummaryPath"
}
$ConfigPath = [System.IO.Path]::GetFullPath($ConfigPath)
$OutputPath = [System.IO.Path]::GetFullPath($OutputPath)
$SummaryPath = [System.IO.Path]::GetFullPath($SummaryPath)

# Avoid turning native git stderr into terminating errors; inspect exit codes instead.
if (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
  $PSNativeCommandUseErrorActionPreference = $false
}

if (-not (Test-Path $ConfigPath)) {
  throw "Config file not found: $ConfigPath"
}

$repos = Get-Content $ConfigPath | ConvertFrom-Json
$cutoffUtc = (Get-Date).ToUniversalTime().AddDays(-1 * $MergedSinceDays)

function Parse-Checks {
  param(
    [string]$Repo,
    [int]$Number
  )

  $raw = & gh pr view --repo $Repo $Number --json statusCheckRollup 2>&1
  if ($LASTEXITCODE -ne 0) {
    return [pscustomobject]@{
      hasFailures = $false
      hasPending = $false
      checks = @()
      error = ($raw | Out-String).Trim()
    }
  }

  $obj = ($raw | Out-String) | ConvertFrom-Json
  $checks = @($obj.statusCheckRollup)
  $hasFailures = @($checks | Where-Object { $_.status -eq "COMPLETED" -and $_.conclusion -in @("FAILURE", "ERROR", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED") }).Count -gt 0
  $hasPending = @($checks | Where-Object { $_.status -ne "COMPLETED" }).Count -gt 0
  return [pscustomobject]@{
    hasFailures = $hasFailures
    hasPending = $hasPending
    checks = $checks
    error = $null
  }
}

function Queue-AutoMerge {
  param(
    [string]$Repo,
    [int]$Number,
    [string]$Method,
    [switch]$DryRunMode
  )

  if ($DryRunMode) {
    return [pscustomobject]@{ changed = $false; detail = "dry-run" }
  }

  $args = @("pr", "merge", "--repo", $Repo, "$Number", "--auto")
  switch ($Method) {
    "merge" { $args += "--merge" }
    "squash" { $args += "--squash" }
    default { $args += "--rebase" }
  }
  $out = & gh @args 2>&1
  $text = ($out | Out-String).Trim()
  if ($LASTEXITCODE -ne 0) {
    return [pscustomobject]@{ changed = $false; detail = $text }
  }
  return [pscustomobject]@{ changed = $true; detail = if ([string]::IsNullOrWhiteSpace($text)) { "auto-merge queued" } else { $text } }
}

function Remove-MergedBranch {
  param(
    [string]$RepoName,
    [string]$RepoPath,
    [string]$DefaultBranch,
    [string]$Branch,
    [switch]$DryRunMode
  )

  if ([string]::IsNullOrWhiteSpace($Branch)) {
    return [pscustomobject]@{ local = "skip"; remote = "skip"; detail = "empty branch" }
  }
  if ($Branch -eq $DefaultBranch) {
    return [pscustomobject]@{ local = "skip"; remote = "skip"; detail = "default branch" }
  }

  $localState = "not-found"
  $remoteState = "not-found"
  $detail = @()

  $localBranchOutput = (& git -C $RepoPath branch --list $Branch 2>$null | Out-String).Trim()
  if ($localBranchOutput) {
    $current = (& git -C $RepoPath branch --show-current 2>$null | Out-String).Trim()
    if ($current -eq $Branch) {
      $localState = "skip-current"
      $detail += "local branch currently checked out"
    } elseif ($DryRunMode) {
      $localState = "would-delete"
    } else {
      $previousErrorAction = $ErrorActionPreference
      $ErrorActionPreference = "Continue"
      $localDeleteOutput = (& git -C $RepoPath branch -d $Branch 2>&1 | Out-String).Trim()
      $localDeleteExitCode = $LASTEXITCODE
      $ErrorActionPreference = $previousErrorAction
      if ($localDeleteExitCode -eq 0) {
        $localState = "deleted"
      } else {
        $localState = "delete-failed"
        if ($localDeleteOutput) {
          $detail += "local_delete_error: $localDeleteOutput"
        }
      }
    }
  }

  $previousErrorAction = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  $remoteExists = (& git -C $RepoPath ls-remote --heads origin $Branch 2>&1 | Out-String).Trim()
  $remoteExistsExitCode = $LASTEXITCODE
  $ErrorActionPreference = $previousErrorAction
  if ($remoteExists) {
    if ($DryRunMode) {
      $remoteState = "would-delete"
    } else {
      $previousErrorAction = $ErrorActionPreference
      $ErrorActionPreference = "Continue"
      $deleteOutput = (& git -C $RepoPath push origin --delete $Branch 2>&1 | Out-String).Trim()
      $deleteExitCode = $LASTEXITCODE
      $ErrorActionPreference = $previousErrorAction
      if ($deleteExitCode -eq 0) {
        $remoteState = "deleted"
      } elseif ($deleteOutput -match "remote ref does not exist") {
        $remoteState = "not-found"
      } else {
        $remoteState = "delete-failed"
        if ($deleteOutput) {
          $detail += "remote_delete_error: $deleteOutput"
        }
      }
    }
  }

  return [pscustomobject]@{
    local = $localState
    remote = $remoteState
    detail = ($detail -join "; ")
  }
}

function Invoke-LoopIteration {
  param(
    [object[]]$RepoConfig,
    [string]$Search,
    [string]$Method,
    [datetime]$Cutoff,
    [switch]$DryRunMode
  )

  $results = @()
  foreach ($repo in $RepoConfig) {
    $ghRepo = $repo.github
    $openRaw = & gh @(
      "pr", "list", "--repo", $ghRepo,
      "--state", "open",
      "--search", $Search,
      "--limit", "100",
      "--json", "number,title,headRefName,baseRefName,mergeStateStatus,isDraft,url,updatedAt,autoMergeRequest"
    ) 2>&1

    if ($LASTEXITCODE -ne 0) {
      $results += [pscustomobject]@{
        repo = $ghRepo
        open = @()
        merged_cleanup = @()
        query_error = ($openRaw | Out-String).Trim()
      }
      continue
    }

    $openPrs = @((($openRaw | Out-String) | ConvertFrom-Json))
    $openState = @()
    foreach ($pr in $openPrs) {
      $checks = Parse-Checks -Repo $ghRepo -Number $pr.number
      $action = "none"
      $actionDetail = ""

      if (-not $pr.isDraft -and -not $checks.hasFailures) {
        if ($checks.hasPending) {
          if (-not $pr.autoMergeRequest) {
            $queued = Queue-AutoMerge -Repo $ghRepo -Number $pr.number -Method $Method -DryRunMode:$DryRunMode
            $action = "queue-auto-merge"
            $actionDetail = $queued.detail
          } else {
            $action = "waiting-auto-merge"
            $actionDetail = "checks running"
          }
        } else {
          if (-not $pr.autoMergeRequest -or $pr.mergeStateStatus -eq "CLEAN") {
            $queued = Queue-AutoMerge -Repo $ghRepo -Number $pr.number -Method $Method -DryRunMode:$DryRunMode
            $action = "queue-auto-merge"
            $actionDetail = $queued.detail
          } else {
            $action = "waiting-merge"
            $actionDetail = "ready"
          }
        }
      } elseif ($checks.hasFailures) {
        $action = "blocked-failing-checks"
      } elseif ($pr.isDraft) {
        $action = "skip-draft"
      }

      $openState += [pscustomobject]@{
        number = $pr.number
        title = $pr.title
        url = $pr.url
        merge_state = $pr.mergeStateStatus
        draft = [bool]$pr.isDraft
        has_failing_checks = [bool]$checks.hasFailures
        has_pending_checks = [bool]$checks.hasPending
        action = $action
        action_detail = $actionDetail
      }
    }

    $mergedRaw = & gh @(
      "pr", "list", "--repo", $ghRepo,
      "--state", "merged",
      "--search", $Search,
      "--limit", "100",
      "--json", "number,title,headRefName,mergedAt,url"
    ) 2>&1
    $cleanup = @()
    if ($LASTEXITCODE -eq 0) {
      $mergedPrs = @((($mergedRaw | Out-String) | ConvertFrom-Json))
      foreach ($pr in $mergedPrs) {
        if (-not $pr.mergedAt) { continue }
        $mergedUtc = [datetime]::Parse($pr.mergedAt).ToUniversalTime()
        if ($mergedUtc -lt $Cutoff) { continue }
        $cleanupResult = Remove-MergedBranch `
          -RepoName $repo.name `
          -RepoPath $repo.path `
          -DefaultBranch $repo.default_branch `
          -Branch $pr.headRefName `
          -DryRunMode:$DryRunMode

        $cleanup += [pscustomobject]@{
          number = $pr.number
          title = $pr.title
          url = $pr.url
          branch = $pr.headRefName
          merged_at = $pr.mergedAt
          local = $cleanupResult.local
          remote = $cleanupResult.remote
          detail = $cleanupResult.detail
        }
      }
    }

    $results += [pscustomobject]@{
      repo = $ghRepo
      open = $openState
      merged_cleanup = $cleanup
      query_error = $null
    }
  }

  return $results
}

function Write-Summary {
  param(
    [object[]]$Entries,
    [string]$Path,
    [switch]$DryRunMode
  )

  $lines = @()
  $lines += "# PR Lifecycle Summary"
  $lines += ""
  $lines += "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
  $lines += "Dry Run: $([bool]$DryRunMode)"
  $lines += ""

  foreach ($entry in $Entries) {
    $lines += "## $($entry.repo)"
    if ($entry.query_error) {
      $lines += "- query_error: $($entry.query_error)"
      $lines += ""
      continue
    }

    if (-not $entry.open -or $entry.open.Count -eq 0) {
      $lines += "- open_prs: none"
    } else {
      $lines += "- open_prs:"
      foreach ($pr in $entry.open) {
        $lines += "  - #$($pr.number) $($pr.title) | action=$($pr.action) | state=$($pr.merge_state)"
      }
    }

    if (-not $entry.merged_cleanup -or $entry.merged_cleanup.Count -eq 0) {
      $lines += "- merged_cleanup: none"
    } else {
      $lines += "- merged_cleanup:"
      foreach ($row in $entry.merged_cleanup) {
        $lines += "  - #$($row.number) branch=$($row.branch) | local=$($row.local) | remote=$($row.remote)"
      }
    }
    $lines += ""
  }

  $summaryDir = Split-Path -Parent $Path
  if ($summaryDir -and -not (Test-Path $summaryDir)) {
    New-Item -ItemType Directory -Force $summaryDir | Out-Null
  }
  $lines | Set-Content $Path
}

do {
  $iteration = Invoke-LoopIteration -RepoConfig $repos -Search $PrSearch -Method $MergeMethod -Cutoff $cutoffUtc -DryRunMode:$DryRun

  $outputDir = Split-Path -Parent $OutputPath
  if ($outputDir -and -not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Force $outputDir | Out-Null
  }
  $iteration | ConvertTo-Json -Depth 8 | Set-Content $OutputPath
  Write-Summary -Entries $iteration -Path $SummaryPath -DryRunMode:$DryRun

  Write-Host "Wrote PR lifecycle output: $OutputPath"
  Write-Host "Wrote PR lifecycle summary: $SummaryPath"

  if ($Watch) {
    Start-Sleep -Seconds $IntervalSeconds
  }
} while ($Watch)

