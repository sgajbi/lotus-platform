param(
  [string]$StatePath = "output/background-runs.json",
  [switch]$Watch,
  [int]$IntervalSeconds = 20,
  [switch]$PruneCompleted
)

$ErrorActionPreference = "Stop"

function Get-LatestResult {
  param([string]$Profile)
  $pattern = "*-$Profile.json"
  $file = Get-ChildItem -Path "output/task-runs" -Filter $pattern -File -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
  if (-not $file) {
    return $null
  }
  return $file.FullName
}

function Get-PropertyValue {
  param(
    [object]$Object,
    [string]$Name,
    [object]$Default = $null
  )

  if ($null -ne $Object -and $Object.PSObject.Properties.Name -contains $Name) {
    return $Object.$Name
  }
  return $Default
}

function Get-TaskStatusFromResult {
  param(
    [string]$ExpectedResultPath,
    [object]$Process
  )

  if ($ExpectedResultPath -and (Test-Path $ExpectedResultPath)) {
    try {
      $results = Get-Content $ExpectedResultPath -Raw | ConvertFrom-Json
      if (-not ($results -is [System.Array])) {
        $results = @($results)
      }
      $failed = @($results | Where-Object { $_.exitCode -ne 0 })
      if ($failed.Count -gt 0) {
        return "FAILED"
      }
      return "SUCCEEDED"
    } catch {
      return "FAILED"
    }
  }

  if ($Process) {
    return "RUNNING"
  }

  return "LOST"
}

function Print-Status {
  param(
    [string]$RunStatePath,
    [switch]$Prune
  )

  if (-not (Test-Path $RunStatePath)) {
    Write-Host "No background run state found at $RunStatePath"
    return
  }

  $raw = Get-Content $RunStatePath -Raw
  if ([string]::IsNullOrWhiteSpace($raw)) {
    Write-Host "Background run state is empty."
    return
  }

  $entries = $raw | ConvertFrom-Json
  if (-not ($entries -is [System.Array])) {
    $entries = @($entries)
  }

  $updated = @()
  foreach ($entry in $entries) {
    $proc = Get-Process -Id $entry.pid -ErrorAction SilentlyContinue
    $expectedResultPath = $entry.expectedResultPath
    $latestResult = if ($expectedResultPath -and (Test-Path $expectedResultPath)) {
      $expectedResultPath
    } else {
      Get-LatestResult -Profile $entry.profile
    }
    $status = Get-TaskStatusFromResult -ExpectedResultPath $expectedResultPath -Process $proc
    $legacyCorrelationRef = Get-PropertyValue -Object $entry -Name "correlationRef"
    $correlationRef = Get-PropertyValue -Object $entry -Name "correlation_ref" -Default $legacyCorrelationRef
    if (-not $correlationRef) {
      $correlationRef = "$($entry.runId)-$($entry.profile)"
    }
    $legacyEngineeringTaskId = Get-PropertyValue -Object $entry -Name "engineeringTaskId"
    $engineeringTaskId = Get-PropertyValue -Object $entry -Name "engineering_task_id" -Default $legacyEngineeringTaskId
    if (-not $engineeringTaskId) {
      $engineeringTaskId = "eng-task-$correlationRef"
    }
    $requestedAt = Get-PropertyValue -Object $entry -Name "requested_at" -Default (Get-PropertyValue -Object $entry -Name "requestedAt" -Default $entry.startedAt)
    $runtime = Get-PropertyValue -Object $entry -Name "runtime" -Default ([pscustomobject]@{
      kind = "powershell"
      runner = "automation/Run-Parallel-Tasks.ps1"
      pid = $entry.pid
    })
    $scope = Get-PropertyValue -Object $entry -Name "scope" -Default ([pscustomobject]@{
      profile = $entry.profile
      maxParallel = $entry.maxParallel
    })
    $artifacts = Get-PropertyValue -Object $entry -Name "artifacts" -Default @(
      $entry.outLogPath,
      $entry.errLogPath,
      $entry.expectedResultPath,
      $entry.expectedSummaryPath
    )
    $evidenceRefs = Get-PropertyValue -Object $entry -Name "evidence_refs" -Default (Get-PropertyValue -Object $entry -Name "evidenceRefs" -Default @(
      [pscustomobject]@{ type = "LOG_FILE"; path = $entry.outLogPath },
      [pscustomobject]@{ type = "LOG_FILE"; path = $entry.errLogPath },
      [pscustomobject]@{ type = "LOCAL_JSON_ARTIFACT"; path = $entry.expectedResultPath },
      [pscustomobject]@{ type = "LOCAL_MARKDOWN_ARTIFACT"; path = $entry.expectedSummaryPath }
    ))
    $cleanupState = Get-PropertyValue -Object $entry -Name "cleanup_state" -Default (Get-PropertyValue -Object $entry -Name "cleanupState" -Default "PENDING")
    if ($status -eq "SUCCEEDED") {
      $cleanupState = "DONE"
    }
    $endedAt = Get-PropertyValue -Object $entry -Name "ended_at" -Default (Get-PropertyValue -Object $entry -Name "endedAt")
    if ($status -notin @("QUEUED", "RUNNING") -and -not $endedAt) {
      $endedAt = (Get-Date).ToString("s")
    }
    $errorSummary = Get-PropertyValue -Object $entry -Name "error_summary" -Default (Get-PropertyValue -Object $entry -Name "errorSummary")
    if ($status -in @("FAILED", "TIMED_OUT", "LOST", "CANCELLED") -and -not $errorSummary) {
      $errorSummary = if ($status -eq "LOST") {
        "Process ended before the expected result artifact was written."
      } else {
        "Expected result artifact indicates failure or could not be parsed."
      }
    }

    $updated += [pscustomobject]@{
      engineering_task_id = $engineeringTaskId
      task_kind = Get-PropertyValue -Object $entry -Name "task_kind" -Default (Get-PropertyValue -Object $entry -Name "taskKind" -Default "LOCAL_BACKGROUND_RUN")
      repository = Get-PropertyValue -Object $entry -Name "repository" -Default "lotus-platform"
      branch = Get-PropertyValue -Object $entry -Name "branch" -Default "unknown"
      owner = Get-PropertyValue -Object $entry -Name "owner" -Default "unknown"
      requested_at = $requestedAt
      origin = Get-PropertyValue -Object $entry -Name "origin" -Default "automation/Start-Background-Run.ps1"
      correlation_ref = $correlationRef
      summary = Get-PropertyValue -Object $entry -Name "summary" -Default "Background run for task profile '$($entry.profile)'"
      pid = $entry.pid
      profile = $entry.profile
      maxParallel = $entry.maxParallel
      runId = $entry.runId
      started_at = Get-PropertyValue -Object $entry -Name "started_at" -Default $entry.startedAt
      startedAt = $entry.startedAt
      status = $status
      runtime = $runtime
      scope = $scope
      artifacts = $artifacts
      evidence_refs = $evidenceRefs
      cleanup_state = $cleanupState
      ended_at = $endedAt
      error_summary = $errorSummary
      outLogPath = $entry.outLogPath
      errLogPath = $entry.errLogPath
      expectedResultPath = $entry.expectedResultPath
      expectedSummaryPath = $entry.expectedSummaryPath
      latestResult = $latestResult
    }
  }

  $persisted = if ($Prune) {
    @($updated | Where-Object { $_.status -eq "RUNNING" })
  } else {
    $updated
  }

  $persistedJson = if (@($persisted).Count -eq 0) {
    "[]"
  } else {
    ConvertTo-Json -InputObject @($persisted) -Depth 5
  }
  $persistedJson | Set-Content $RunStatePath
  $updated | Sort-Object startedAt -Descending | Format-Table pid, profile, status, startedAt, latestResult -AutoSize
}

if ($Watch) {
  while ($true) {
    Clear-Host
    Print-Status -RunStatePath $StatePath -Prune:$PruneCompleted
    Start-Sleep -Seconds $IntervalSeconds
  }
} else {
  Print-Status -RunStatePath $StatePath -Prune:$PruneCompleted
}

