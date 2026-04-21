param(
  [Parameter(Mandatory = $true)][string]$Profile,
  [int]$MaxParallel = 3,
  [string]$StatePath = "output/background-runs.json"
)

$ErrorActionPreference = "Stop"

$scriptPath = "automation/Run-Parallel-Tasks.ps1"
if (-not (Test-Path $scriptPath)) {
  throw "Runner script not found: $scriptPath"
}

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$correlationRef = "$timestamp-$Profile"
$engineeringTaskId = "eng-task-$correlationRef"
$branch = (git branch --show-current 2>$null)
if ([string]::IsNullOrWhiteSpace($branch)) {
  $branch = "unknown"
}
$owner = if ($env:USERNAME) { $env:USERNAME } elseif ($env:USER) { $env:USER } else { "unknown" }
$requestedAt = (Get-Date).ToString("s")

$args = @(
  "-NoProfile",
  "-ExecutionPolicy", "Bypass",
  "-File", $scriptPath,
  "-Profile", $Profile,
  "-MaxParallel", "$MaxParallel",
  "-RunId", $timestamp
)

$stateDir = Split-Path -Parent $StatePath
if ($stateDir -and -not (Test-Path $stateDir)) {
  New-Item -ItemType Directory -Force $stateDir | Out-Null
}

$outLogPath = "output/task-runs/bg-$timestamp-$Profile.out.log"
$errLogPath = "output/task-runs/bg-$timestamp-$Profile.err.log"
$expectedJsonPath = "output/task-runs/$timestamp-$Profile.json"
$expectedMdPath = "output/task-runs/$timestamp-$Profile.md"
$logDir = Split-Path -Parent $outLogPath
if ($logDir -and -not (Test-Path $logDir)) {
  New-Item -ItemType Directory -Force $logDir | Out-Null
}

$process = Start-Process -FilePath "powershell" -ArgumentList $args -PassThru -WindowStyle Hidden -RedirectStandardOutput $outLogPath -RedirectStandardError $errLogPath

$state = @()
if (Test-Path $StatePath) {
  $raw = Get-Content $StatePath -Raw
  if (-not [string]::IsNullOrWhiteSpace($raw)) {
    $parsed = $raw | ConvertFrom-Json
    if ($parsed -is [System.Array]) {
      $state = @($parsed)
    } else {
      $state = @($parsed)
    }
  }
}

$entry = [pscustomobject]@{
  engineering_task_id = $engineeringTaskId
  task_kind = "LOCAL_BACKGROUND_RUN"
  repository = "lotus-platform"
  branch = $branch
  owner = $owner
  requested_at = $requestedAt
  origin = "automation/Start-Background-Run.ps1"
  correlation_ref = $correlationRef
  summary = "Background run for task profile '$Profile'"
  pid = $process.Id
  profile = $Profile
  maxParallel = $MaxParallel
  runId = $timestamp
  started_at = $requestedAt
  startedAt = $requestedAt
  status = "RUNNING"
  runtime = [pscustomobject]@{
    kind = "powershell"
    runner = $scriptPath
    pid = $process.Id
  }
  scope = [pscustomobject]@{
    profile = $Profile
    maxParallel = $MaxParallel
  }
  artifacts = @($outLogPath, $errLogPath, $expectedJsonPath, $expectedMdPath)
  evidence_refs = @(
    [pscustomobject]@{ type = "LOG_FILE"; path = $outLogPath },
    [pscustomobject]@{ type = "LOG_FILE"; path = $errLogPath },
    [pscustomobject]@{ type = "LOCAL_JSON_ARTIFACT"; path = $expectedJsonPath },
    [pscustomobject]@{ type = "LOCAL_MARKDOWN_ARTIFACT"; path = $expectedMdPath }
  )
  cleanup_state = "PENDING"
  outLogPath = $outLogPath
  errLogPath = $errLogPath
  expectedResultPath = $expectedJsonPath
  expectedSummaryPath = $expectedMdPath
}

$state = @($state | Where-Object { $_.pid -ne $process.Id })
$state += $entry
ConvertTo-Json -InputObject @($state) -Depth 5 | Set-Content $StatePath

Write-Host ("Started background run. PID={0}, Profile={1}" -f $process.Id, $Profile)
Write-Host "Monitor status with: powershell -ExecutionPolicy Bypass -File automation/Check-Background-Runs.ps1"

