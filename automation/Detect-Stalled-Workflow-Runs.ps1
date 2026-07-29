param(
  [string]$Repo = "sgajbi/lotus-platform",
  [string]$Branch = "main",
  [string[]]$WorkflowName = @(),
  [int]$Limit = 50,
  [int]$StaleMinutes = 60,
  [string]$OutputJsonPath = "output/stalled-workflow-runs.json",
  [string]$OutputMarkdownPath = "output/stalled-workflow-runs.md"
)

$ErrorActionPreference = "Stop"

$python = & (Join-Path $PSScriptRoot "Resolve-PlatformAutomationPython.ps1")
$args = @(
  "automation/detect_stalled_workflow_runs.py",
  "--repo", $Repo,
  "--branch", $Branch,
  "--limit", $Limit,
  "--stale-minutes", $StaleMinutes,
  "--output-json", $OutputJsonPath,
  "--output-markdown", $OutputMarkdownPath
)

foreach ($workflow in $WorkflowName) {
  $args += @("--workflow", $workflow)
}

& $python @args
