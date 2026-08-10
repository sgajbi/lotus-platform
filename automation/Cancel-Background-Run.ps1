[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][string]$EngineeringTaskId,
  [Parameter(Mandatory = $true)][string]$Reason,
  [string]$Actor = "",
  [string]$StatePath = "output/background-runs.json",
  [string]$ReceiptDir = "output/task-runs"
)

$ErrorActionPreference = "Stop"

$resolvedActor = if (-not [string]::IsNullOrWhiteSpace($Actor)) {
  $Actor
} elseif ($env:USERNAME) {
  $env:USERNAME
} elseif ($env:USER) {
  $env:USER
} else {
  "unknown"
}

$implementation = "automation/background_task_cancellation.py"
if (-not (Test-Path $implementation)) {
  throw "Background-task cancellation implementation not found: $implementation"
}

& python $implementation cancel `
  --engineering-task-id $EngineeringTaskId `
  --reason $Reason `
  --actor $resolvedActor `
  --state-path $StatePath `
  --receipt-dir $ReceiptDir
exit $LASTEXITCODE
