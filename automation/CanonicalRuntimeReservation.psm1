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
    [ValidateSet('success', 'failure')][string]$Outcome = 'failure',
    [string]$RefreshPlan,
    [string]$RefreshPlanDigest,
    [string]$PreparedImages
  )
  $arguments = @($reservationScript, $Action, '--projects-root', $ProjectsRoot)
  $arguments += @('--runtime-mode', $RuntimeMode)
  if ($WorkbenchRepoPath) { $arguments += @('--workbench-repo-path', $WorkbenchRepoPath) }
  if (-not [string]::IsNullOrWhiteSpace($Holder)) { $arguments += @('--holder', $Holder) }
  if ($OperationToken) { $arguments += @('--operation-token', $OperationToken) }
  if ($RefreshPlan) { $arguments += @('--refresh-plan', $RefreshPlan) }
  if ($RefreshPlanDigest) { $arguments += @('--refresh-plan-digest', $RefreshPlanDigest) }
  if ($PreparedImages) { $arguments += @('--prepared-images', $PreparedImages) }
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
    [ValidateSet('change', 'teardown', 'refresh')][string]$Action = 'change',
    [switch]$Preview,
    [string]$RefreshPlan,
    [string]$RefreshPlanDigest
  )
  if ([string]::IsNullOrWhiteSpace($Holder)) {
    throw 'Explicit RuntimeHolder is required; acquire a reservation before changing resources.'
  }
  $directory = Join-Path $ProjectsRoot 'lotus-platform/output/canonical-runtime'
  New-Item -ItemType Directory -Force -Path $directory | Out-Null
  $path = Join-Path $directory 'operation.lock'
  $stream = [System.IO.File]::Open($path, 'OpenOrCreate', 'ReadWrite', 'None')
  try {
    if ($Preview -and $Action -ne 'refresh') { throw 'Only refresh supports read-only preview.' }
    $admissionAction = if ($Preview) { 'preview-refresh' } else { "begin-$Action" }
    $record = Invoke-CanonicalReservation -Action $admissionAction -ProjectsRoot $ProjectsRoot -Holder $Holder -WorkbenchRepoPath $WorkbenchRepoPath -RuntimeMode $RuntimeMode -RefreshPlan $RefreshPlan -RefreshPlanDigest $RefreshPlanDigest
    $operationFences[$record.operation.token] = $stream
    return [pscustomobject]@{
      ProjectsRoot = $ProjectsRoot; WorkbenchRepoPath = $WorkbenchRepoPath; Holder = $Holder; Token = $record.operation.token
      Preview = [bool]$Preview
      Bindings = @($record.bindings); Lock = $stream; RuntimeMode = $RuntimeMode; Scope = $record.scope; Action = $Action
      RefreshPlan = if ($Action -eq 'refresh') { $record.operation.refresh.plan } else { $null }
      OriginalResources = if ($Action -eq 'refresh') { @($record.operation.refresh.originalResources) } else { @() }
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
    if ($Operation.Preview) { return }
    if ($Operation.Action -eq 'refresh') {
      Assert-CanonicalRuntimeOperationFence -ProjectsRoot $Operation.ProjectsRoot -OperationToken $Operation.Token -Fence $Operation.Lock
    }
    $finishAction = if ($Operation.Action -eq 'refresh') { 'finish-refresh' } else { 'finish' }
    Invoke-CanonicalReservation -Action $finishAction -ProjectsRoot $Operation.ProjectsRoot `
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

function Enter-CanonicalRuntimeRefresh {
  param(
    [Parameter(Mandatory)][string]$ProjectsRoot,
    [Parameter(Mandatory)][string]$Holder,
    [Parameter(Mandatory)][string]$RefreshPlan,
    [Parameter(Mandatory)][string]$RefreshPlanDigest,
    [switch]$Preview,
    [string]$WorkbenchRepoPath,
    [ValidateSet('full', 'core-manage')][string]$RuntimeMode = 'full'
  )
  Enter-CanonicalRuntimeOperation @PSBoundParameters -Action refresh
}

function Assert-CanonicalRuntimeRefresh {
  param([Parameter(Mandatory)]$Operation, [string]$PreparedImages)
  Assert-CanonicalRuntimeOperationFence -ProjectsRoot $Operation.ProjectsRoot -OperationToken $Operation.Token -Fence $Operation.Lock
  if ($Operation.Action -ne 'refresh') { throw 'A refresh operation is required.' }
  $action = if ($PreparedImages) { 'prepare-refresh' } else { 'preflight-refresh' }
  Invoke-CanonicalReservation -Action $action -ProjectsRoot $Operation.ProjectsRoot -Holder $Operation.Holder `
    -OperationToken $Operation.Token -WorkbenchRepoPath $Operation.WorkbenchRepoPath `
    -RuntimeMode $Operation.RuntimeMode -PreparedImages $PreparedImages
}

Export-ModuleMember -Function Invoke-CanonicalReservation, Enter-CanonicalRuntimeOperation, Assert-CanonicalRuntimeOperationFence, Exit-CanonicalRuntimeOperation, Enter-CanonicalRuntimeRefresh, Assert-CanonicalRuntimeRefresh
