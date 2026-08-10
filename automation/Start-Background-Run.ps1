[CmdletBinding(DefaultParameterSetName = "Profile")]
param(
  [Parameter(Mandatory = $true, ParameterSetName = "Profile")][string]$Profile,
  [Parameter(ParameterSetName = "Profile")][int]$MaxParallel = 3,

  [Parameter(Mandatory = $true, ParameterSetName = "RepositoryTarget")][string]$Repository,
  [Parameter(Mandatory = $true, ParameterSetName = "RepositoryTarget")]
  [ValidateSet("make", "npm", "python", "powershell")][string]$TargetType,
  [Parameter(Mandatory = $true, ParameterSetName = "RepositoryTarget")][string]$Target,
  [Parameter(ParameterSetName = "RepositoryTarget")][string[]]$TargetArgument = @(),
  [Parameter(ParameterSetName = "RepositoryTarget")][string]$TargetArgumentsJson = "",
  [Parameter(ParameterSetName = "RepositoryTarget")][string[]]$RequiredArtifact = @(),
  [Parameter(ParameterSetName = "RepositoryTarget")][string]$ExpectedHead = "",
  [Parameter(ParameterSetName = "RepositoryTarget")][switch]$RequireClean,
  [Parameter(ParameterSetName = "RepositoryTarget")][string]$ReposConfigPath = "automation/repos.json",
  [Parameter(ParameterSetName = "RepositoryTarget")][string]$OutputDir = "output/task-runs",
  [Parameter(ParameterSetName = "RepositoryTarget")][string]$RunId = "",
  [Parameter(ParameterSetName = "RepositoryTarget")][string]$Owner = "",

  [string]$ComposeCleanupPlanPath = "",
  [switch]$NoExternalCleanupRequired,
  [string]$StatePath = "output/background-runs.json"
)

$ErrorActionPreference = "Stop"

if (-not [string]::IsNullOrWhiteSpace($ComposeCleanupPlanPath) -and $NoExternalCleanupRequired) {
  throw "Use either -ComposeCleanupPlanPath or -NoExternalCleanupRequired, not both"
}

function Resolve-CleanupContract {
  param(
    [string]$PlanPath,
    [switch]$NoCleanupRequired,
    [string]$AllowedRepositoryRoot = ""
  )

  if ($NoCleanupRequired) {
    return [pscustomobject]@{
      ownership_state = "NONE"
      compose_projects = @()
      source_plan = $null
    }
  }
  if ([string]::IsNullOrWhiteSpace($PlanPath)) {
    return [pscustomobject]@{
      ownership_state = "UNKNOWN"
      compose_projects = @()
      source_plan = $null
    }
  }

  $validatorArguments = @(
    "automation/background_task_cancellation.py",
    "validate-compose-plan",
    "--plan-path", $PlanPath
  )
  if (-not [string]::IsNullOrWhiteSpace($AllowedRepositoryRoot)) {
    $validatorArguments += @("--allowed-repository-root", $AllowedRepositoryRoot)
  }
  $normalizedJson = & python @validatorArguments
  if ($LASTEXITCODE -ne 0) {
    throw "Compose cleanup plan validation failed: $PlanPath"
  }
  $normalized = $normalizedJson | ConvertFrom-Json
  return [pscustomobject]@{
    ownership_state = "COMPOSE"
    compose_projects = @($normalized.projects)
    source_plan = (Resolve-Path $PlanPath).Path
  }
}

if ($PSCmdlet.ParameterSetName -eq "RepositoryTarget") {
  $launcherPath = "automation/repository_background_task.py"
  if (-not (Test-Path $launcherPath)) {
    throw "Repository background-task launcher not found: $launcherPath"
  }

  $resolvedTargetArguments = @($TargetArgument)
  if (-not [string]::IsNullOrWhiteSpace($TargetArgumentsJson)) {
    if ($resolvedTargetArguments.Count -gt 0) {
      throw "Use either -TargetArgument or -TargetArgumentsJson, not both"
    }
    try {
      $parsedArguments = ConvertFrom-Json $TargetArgumentsJson
    } catch {
      throw "TargetArgumentsJson must be a valid JSON array of strings"
    }
    if (-not ($parsedArguments -is [System.Array])) {
      throw "TargetArgumentsJson must be a JSON array"
    }
    $resolvedTargetArguments = @($parsedArguments)
    if ($resolvedTargetArguments | Where-Object { $_ -isnot [string] }) {
      throw "TargetArgumentsJson must contain only strings"
    }
  }

  $arguments = @(
    $launcherPath,
    "launch",
    "--repository", $Repository,
    "--target-type", $TargetType,
    "--target", $Target,
    "--repos-config", $ReposConfigPath,
    "--state-path", $StatePath,
    "--output-dir", $OutputDir
  )
  foreach ($argument in $resolvedTargetArguments) {
    $arguments += "--target-argument=$argument"
  }
  foreach ($artifact in $RequiredArtifact) {
    $arguments += "--required-artifact=$artifact"
  }
  if (-not [string]::IsNullOrWhiteSpace($ExpectedHead)) {
    $arguments += @("--expected-head", $ExpectedHead)
  }
  if ($RequireClean) {
    $arguments += "--require-clean"
  }
  if (-not [string]::IsNullOrWhiteSpace($RunId)) {
    $arguments += @("--run-id", $RunId)
  }
  if (-not [string]::IsNullOrWhiteSpace($Owner)) {
    $arguments += @("--owner", $Owner)
  }
  if (-not [string]::IsNullOrWhiteSpace($ComposeCleanupPlanPath)) {
    $arguments += @("--compose-cleanup-plan", $ComposeCleanupPlanPath)
  }
  if ($NoExternalCleanupRequired) {
    $arguments += "--no-external-cleanup-required"
  }

  & python @arguments
  exit $LASTEXITCODE
}

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
$ownerName = if ($env:USERNAME) { $env:USERNAME } elseif ($env:USER) { $env:USER } else { "unknown" }
$requestedAt = (Get-Date).ToUniversalTime().ToString("o")
$cleanupContract = Resolve-CleanupContract `
  -PlanPath $ComposeCleanupPlanPath `
  -NoCleanupRequired:$NoExternalCleanupRequired

$arguments = @(
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

$process = Start-Process -FilePath "powershell" -ArgumentList $arguments -PassThru -WindowStyle Hidden -RedirectStandardOutput $outLogPath -RedirectStandardError $errLogPath
$processStartedAt = $process.StartTime.ToUniversalTime().ToString("o")
$entry = [pscustomobject]@{
  engineering_task_id = $engineeringTaskId
  task_kind = "LOCAL_BACKGROUND_RUN"
  repository = "lotus-platform"
  branch = $branch
  owner = $ownerName
  requested_at = $requestedAt
  origin = "automation/Start-Background-Run.ps1"
  correlation_ref = $correlationRef
  summary = "Background run for task profile '$Profile'"
  pid = $process.Id
  profile = $Profile
  display_name = "profile/$Profile"
  mode = "profile"
  maxParallel = $MaxParallel
  runId = $timestamp
  started_at = $requestedAt
  startedAt = $requestedAt
  status = "RUNNING"
  runtime = [pscustomobject]@{
    kind = "powershell"
    runner = $scriptPath
    pid = $process.Id
    process_started_at = $processStartedAt
  }
  scope = [pscustomobject]@{
    profile = $Profile
    maxParallel = $MaxParallel
    cleanup_contract = $cleanupContract
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

try {
  $entryJson = ConvertTo-Json -InputObject $entry -Depth 8 -Compress
  $entryPath = "$StatePath.$PID.entry.tmp"
  $utf8WithoutBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText([System.IO.Path]::GetFullPath($entryPath), $entryJson, $utf8WithoutBom)
  & python automation/repository_background_task.py append-ledger-entry --state-path $StatePath --entry-path $entryPath
  if ($LASTEXITCODE -ne 0) {
    throw "Background task ledger append failed for $engineeringTaskId"
  }
} catch {
  if (Get-Process -Id $process.Id -ErrorAction SilentlyContinue) {
    & taskkill.exe /PID $process.Id /T /F 2>$null | Out-Null
    Wait-Process -Id $process.Id -Timeout 10 -ErrorAction SilentlyContinue
  }
  if (Get-Process -Id $process.Id -ErrorAction SilentlyContinue) {
    throw "Background task ledger append failed and process $($process.Id) survived rollback"
  }
  throw
} finally {
  if ($entryPath -and (Test-Path -LiteralPath $entryPath)) {
    Remove-Item -LiteralPath $entryPath -Force
  }
}

Write-Host ("Started background run. PID={0}, Profile={1}" -f $process.Id, $Profile)
Write-Host "Monitor status with: powershell -ExecutionPolicy Bypass -File automation/Check-Background-Runs.ps1"
