# Central local coordination only. No implicit holder and no production IAM grant.
$reservationScript = Join-Path $PSScriptRoot 'canonical_runtime_reservation.py'
# Only Enter registers the exact exclusive stream returned for its admitted token.
# This process-local reference cannot be reconstructed from a persisted token/path.
$operationFences = @{}

function Invoke-CanonicalReservation {
  param(
    [Parameter(Mandatory)][string]$Action,
    [Parameter(Mandatory)][string]$ProjectsRoot,
    [string]$WorkbenchRepoPath,
    [string]$Holder,
    [ValidateSet('full', 'core-manage')][string]$RuntimeMode = 'full',
    [string]$OperationToken,
    [ValidateSet('success', 'failure')][string]$Outcome = 'failure'
  )
  $arguments = @($reservationScript, $Action, '--projects-root', $ProjectsRoot)
  $arguments += @('--runtime-mode', $RuntimeMode)
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
    [ValidateSet('full', 'core-manage')][string]$RuntimeMode = 'full',
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
    $record = Invoke-CanonicalReservation -Action "begin-$Action" -ProjectsRoot $ProjectsRoot -Holder $Holder -WorkbenchRepoPath $WorkbenchRepoPath -RuntimeMode $RuntimeMode
    $operationFences[$record.operation.token] = $stream
    return [pscustomobject]@{
      ProjectsRoot = $ProjectsRoot; WorkbenchRepoPath = $WorkbenchRepoPath; Holder = $Holder; Token = $record.operation.token
      Bindings = @($record.bindings); Lock = $stream; RuntimeMode = $RuntimeMode; Scope = $record.scope
    }
  } catch {
    $stream.Dispose()
    throw
  }
}

function Assert-CanonicalRuntimeOperationFence {
  param([Parameter(Mandatory)][string]$ProjectsRoot, [Parameter(Mandatory)][string]$OperationToken, [System.IO.FileStream]$Fence)
  $expected = [IO.Path]::GetFullPath((Join-Path $ProjectsRoot 'lotus-platform/output/canonical-runtime/operation.lock'))
  $comparison = if ([Environment]::OSVersion.Platform -eq 'Win32NT') { [StringComparison]::OrdinalIgnoreCase } else { [StringComparison]::Ordinal }
  if (-not $operationFences.ContainsKey($OperationToken) -or
      -not [object]::ReferenceEquals($operationFences[$OperationToken], $Fence) -or
      -not $Fence -or -not $Fence.CanRead -or -not $Fence.CanWrite -or $Fence.SafeFileHandle.IsClosed -or
      $Fence.SafeFileHandle.IsInvalid -or -not [string]::Equals($Fence.Name, $expected, $comparison)) {
    throw 'Nested execution requires the live canonical parent operation fence registered to its originating token; a persisted token is not admission.'
  }
}

function Exit-CanonicalRuntimeOperation {
  param(
    [Parameter(Mandatory)]$Operation,
    [ValidateSet('success', 'failure')][string]$Outcome = 'failure'
  )
  $incomingNativeStatus = $LASTEXITCODE
  $mode = if ($Operation.RuntimeMode) { $Operation.RuntimeMode } else { 'full' }
  try {
    Invoke-CanonicalReservation -Action finish -ProjectsRoot $Operation.ProjectsRoot `
      -Holder $Operation.Holder -OperationToken $Operation.Token -Outcome $Outcome `
      -WorkbenchRepoPath $Operation.WorkbenchRepoPath -RuntimeMode $mode | Out-Host
  } finally {
    if ($operationFences.ContainsKey($Operation.Token) -and
        [object]::ReferenceEquals($operationFences[$Operation.Token], $Operation.Lock)) {
      $operationFences.Remove($Operation.Token)
    }
    $Operation.Lock.Dispose()
    # The evidence publisher must not turn the caller's failed native command green.
    $global:LASTEXITCODE = $incomingNativeStatus
  }
}

Export-ModuleMember -Function Invoke-CanonicalReservation, Enter-CanonicalRuntimeOperation, Assert-CanonicalRuntimeOperationFence, Exit-CanonicalRuntimeOperation
