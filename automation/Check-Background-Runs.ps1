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

function Expand-BackgroundRunEntries {
  param([object[]]$Entries)

  $expanded = @()
  foreach ($entry in $Entries) {
    $propertyNames = @($entry.PSObject.Properties.Name)
    $hasTaskIdentity = $propertyNames -contains "engineering_task_id" -or
      $propertyNames -contains "engineeringTaskId" -or
      $propertyNames -contains "pid" -or
      $propertyNames -contains "runId" -or
      $propertyNames -contains "expectedResultPath"

    $wrappedValue = Get-PropertyValue -Object $entry -Name "value"
    if (-not $hasTaskIdentity -and $wrappedValue) {
      $expanded += @($wrappedValue)
      continue
    }

    $expanded += $entry
  }

  return @($expanded)
}

function Get-TaskStatusFromResult {
  param(
    [string]$ExpectedResultPath,
    [object]$Process,
    [string]$CurrentStatus
  )

  if ($CurrentStatus -in @("CANCELLED", "SUPERSEDED", "TIMED_OUT")) {
    return $CurrentStatus
  }

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

function Get-OwnedProcess {
  param(
    [object]$Entry,
    [object]$Runtime
  )

  $pidValue = Get-PropertyValue -Object $Entry -Name "pid"
  if ($null -eq $pidValue) {
    return $null
  }

  $process = Get-Process -Id $pidValue -ErrorAction SilentlyContinue
  if (-not $process) {
    return $null
  }

  $expectedStartedAt = Get-PropertyValue -Object $Runtime -Name "process_started_at"
  if (-not $expectedStartedAt) {
    return $process
  }

  try {
    $expected = if ($expectedStartedAt -is [DateTimeOffset]) {
      $expectedStartedAt.UtcDateTime
    } elseif ($expectedStartedAt -is [DateTime]) {
      $expectedStartedAt.ToUniversalTime()
    } else {
      [DateTimeOffset]::Parse(
        [string]$expectedStartedAt,
        [System.Globalization.CultureInfo]::InvariantCulture,
        [System.Globalization.DateTimeStyles]::RoundtripKind
      ).UtcDateTime
    }
    $actual = $process.StartTime.ToUniversalTime()
    if ([Math]::Abs(($actual - $expected).TotalSeconds) -gt 5) {
      return $null
    }
  } catch {
    return $null
  }
  return $process
}

function Write-BackgroundRunLedgerAtomically {
  param(
    [string]$RunStatePath,
    [string]$Content
  )

  $resolvedStatePath = [System.IO.Path]::GetFullPath($RunStatePath)
  $temporaryPath = "$resolvedStatePath.$PID.tmp"
  $backupPath = "$resolvedStatePath.$PID.bak"
  $utf8WithoutBom = New-Object System.Text.UTF8Encoding($false)
  try {
    [System.IO.File]::WriteAllText($temporaryPath, "$Content`n", $utf8WithoutBom)
    [System.IO.File]::Replace($temporaryPath, $resolvedStatePath, $backupPath)
  } finally {
    if (Test-Path -LiteralPath $temporaryPath) {
      Remove-Item -LiteralPath $temporaryPath -Force
    }
    if (Test-Path -LiteralPath $backupPath) {
      Remove-Item -LiteralPath $backupPath -Force
    }
  }
}

function Update-BackgroundRunLedger {
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
  $entries = Expand-BackgroundRunEntries -Entries $entries

  $updated = @()
  foreach ($entry in $entries) {
    $profile = Get-PropertyValue -Object $entry -Name "profile"
    $displayName = Get-PropertyValue -Object $entry -Name "display_name" -Default $(
      if ($profile) { "profile/$profile" } else { "task/$($entry.runId)" }
    )
    $mode = Get-PropertyValue -Object $entry -Name "mode" -Default "profile"
    $runtime = Get-PropertyValue -Object $entry -Name "runtime" -Default ([pscustomobject]@{
      kind = "powershell"
      runner = "automation/Run-Parallel-Tasks.ps1"
      pid = $entry.pid
    })
    $proc = Get-OwnedProcess -Entry $entry -Runtime $runtime
    $expectedResultPath = $entry.expectedResultPath
    $latestResult = if ($expectedResultPath -and (Test-Path $expectedResultPath)) {
      $expectedResultPath
    } elseif ($profile) {
      Get-LatestResult -Profile $profile
    } else {
      $null
    }
    $currentStatus = Get-PropertyValue -Object $entry -Name "status"
    $status = Get-TaskStatusFromResult `
      -ExpectedResultPath $expectedResultPath `
      -Process $proc `
      -CurrentStatus $currentStatus
    $terminalExitCode = Get-PropertyValue -Object $entry -Name "terminal_exit_code"
    $processTree = Get-PropertyValue -Object $entry -Name "process_tree"
    $resultErrorSummary = $null
    if ($expectedResultPath -and (Test-Path $expectedResultPath)) {
      try {
        $terminalResults = @(Get-Content $expectedResultPath -Raw | ConvertFrom-Json)
        $failedTerminalResults = @($terminalResults | Where-Object { $_.exitCode -ne 0 })
        $terminalExitCode = if ($failedTerminalResults.Count -gt 0) {
          [int]($failedTerminalResults[0].exitCode)
        } else {
          0
        }
        $resultErrorSummary = @(
          $terminalResults |
            ForEach-Object { Get-PropertyValue -Object $_ -Name "error_summary" } |
            Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
        ) -join "; "
        if ($terminalResults.Count -eq 1) {
          $terminalProcessTree = $terminalResults[0].process_tree
          if ($terminalProcessTree) {
            $processTree = $terminalProcessTree
          }
        }
      } catch {
        $terminalExitCode = $null
      }
    }
    $legacyCorrelationRef = Get-PropertyValue -Object $entry -Name "correlationRef"
    $correlationRef = Get-PropertyValue -Object $entry -Name "correlation_ref" -Default $legacyCorrelationRef
    if (-not $correlationRef) {
      $correlationRef = if ($profile) {
        "$($entry.runId)-$profile"
      } else {
        "$($entry.runId)-$displayName"
      }
    }
    $legacyEngineeringTaskId = Get-PropertyValue -Object $entry -Name "engineeringTaskId"
    $engineeringTaskId = Get-PropertyValue -Object $entry -Name "engineering_task_id" -Default $legacyEngineeringTaskId
    if (-not $engineeringTaskId) {
      $engineeringTaskId = "eng-task-$correlationRef"
    }
    $requestedAt = Get-PropertyValue -Object $entry -Name "requested_at" -Default (Get-PropertyValue -Object $entry -Name "requestedAt" -Default $entry.startedAt)
    $scope = Get-PropertyValue -Object $entry -Name "scope" -Default ([pscustomobject]@{
      profile = $profile
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
    if ($resultErrorSummary) {
      $errorSummary = $resultErrorSummary
    }
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
      profile = $profile
      display_name = $displayName
      mode = $mode
      maxParallel = $entry.maxParallel
      runId = $entry.runId
      started_at = Get-PropertyValue -Object $entry -Name "started_at" -Default $entry.startedAt
      startedAt = $entry.startedAt
      status = $status
      runtime = $runtime
      process_tree = $processTree
      terminal_exit_code = $terminalExitCode
      scope = $scope
      artifacts = $artifacts
      evidence_refs = $evidenceRefs
      cleanup_state = $cleanupState
      cancellation = Get-PropertyValue -Object $entry -Name "cancellation"
      ended_at = $endedAt
      error_summary = $errorSummary
      outLogPath = $entry.outLogPath
      errLogPath = $entry.errLogPath
      jobSpecPath = Get-PropertyValue -Object $entry -Name "jobSpecPath"
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
    ConvertTo-Json -InputObject @($persisted) -Depth 8
  }
  Write-BackgroundRunLedgerAtomically -RunStatePath $RunStatePath -Content $persistedJson
  $updated | Sort-Object startedAt -Descending | Format-Table pid, display_name, status, startedAt, latestResult -AutoSize
}

function Print-Status {
  param(
    [string]$RunStatePath,
    [switch]$Prune
  )

  $resolvedStatePath = [System.IO.Path]::GetFullPath($RunStatePath)
  $lockPath = "$resolvedStatePath.lock"
  $lockStream = $null
  try {
    try {
      $lockStream = [System.IO.File]::Open(
        $lockPath,
        [System.IO.FileMode]::CreateNew,
        [System.IO.FileAccess]::Write,
        [System.IO.FileShare]::None
      )
      $owner = [System.Text.Encoding]::UTF8.GetBytes("pid=$PID`n")
      $lockStream.Write($owner, 0, $owner.Length)
      $lockStream.Flush()
    } catch [System.IO.IOException] {
      Write-Warning "Background-run ledger is locked; reconciliation deferred: $lockPath"
      return
    }

    Update-BackgroundRunLedger -RunStatePath $resolvedStatePath -Prune:$Prune
  } finally {
    if ($lockStream) {
      $lockStream.Dispose()
      Remove-Item -LiteralPath $lockPath -Force -ErrorAction SilentlyContinue
    }
  }
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

