# Central local coordination only. No implicit holder and no production IAM grant.
$reservationScript = Join-Path $PSScriptRoot 'canonical_runtime_reservation.py'

function Invoke-CanonicalReservation {
  param(
    [Parameter(Mandatory)][string]$Action,
    [Parameter(Mandatory)][string]$ProjectsRoot,
    [string]$WorkbenchRepoPath,
    [string]$Holder,
    [string]$OperationToken,
    [ValidateSet('success', 'failure')][string]$Outcome = 'failure'
  )
  $arguments = @($reservationScript, $Action, '--projects-root', $ProjectsRoot)
  if ($WorkbenchRepoPath) { $arguments += @('--workbench-repo-path', $WorkbenchRepoPath) }
  if (-not [string]::IsNullOrWhiteSpace($Holder)) { $arguments += @('--holder', $Holder) }
  if ($OperationToken) { $arguments += @('--operation-token', $OperationToken) }
  $arguments += @('--outcome', $Outcome)
  $global:LASTEXITCODE = 0
  $json = & python @arguments
  if ($LASTEXITCODE -ne 0) {
    throw "Canonical reservation refused (exit $LASTEXITCODE): $($json -join ' ')"
  }
  return ($json -join "`n") | ConvertFrom-Json
}

function Enter-CanonicalRuntimeOperation {
  param(
    [Parameter(Mandatory)][string]$ProjectsRoot,
    [string]$WorkbenchRepoPath,
    [string]$Holder,
    [ValidateSet('change', 'teardown')][string]$Action = 'change'
  )
  if ([string]::IsNullOrWhiteSpace($Holder)) {
    throw 'Explicit RuntimeHolder is required; acquire a reservation before changing resources.'
  }
  $directory = Join-Path $ProjectsRoot 'lotus-platform/output/canonical-runtime'
  New-Item -ItemType Directory -Force -Path $directory | Out-Null
  $path = Join-Path $directory 'operation.lock'
  $stream = [System.IO.File]::Open($path, 'OpenOrCreate', 'ReadWrite', 'None')
  try {
    $record = Invoke-CanonicalReservation -Action "begin-$Action" -ProjectsRoot $ProjectsRoot -Holder $Holder -WorkbenchRepoPath $WorkbenchRepoPath
    return [pscustomobject]@{
      ProjectsRoot = $ProjectsRoot; WorkbenchRepoPath = $WorkbenchRepoPath; Holder = $Holder; Token = $record.operation.token
      Bindings = @($record.bindings); Lock = $stream
    }
  } catch {
    $stream.Dispose()
    throw
  }
}

function Exit-CanonicalRuntimeOperation {
  param(
    [Parameter(Mandatory)]$Operation,
    [ValidateSet('success', 'failure')][string]$Outcome = 'failure'
  )
  $incomingNativeStatus = $LASTEXITCODE
  try {
    Invoke-CanonicalReservation -Action finish -ProjectsRoot $Operation.ProjectsRoot `
      -Holder $Operation.Holder -OperationToken $Operation.Token -Outcome $Outcome `
      -WorkbenchRepoPath $Operation.WorkbenchRepoPath | Out-Host
  } finally {
    $Operation.Lock.Dispose()
    # The evidence publisher must not turn the caller's failed native command green.
    $global:LASTEXITCODE = $incomingNativeStatus
  }
}

Export-ModuleMember -Function Invoke-CanonicalReservation, Enter-CanonicalRuntimeOperation, Exit-CanonicalRuntimeOperation
