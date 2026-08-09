param(
  [Parameter(Mandatory=$true)][string]$Repo,
  [string]$LabelContractPath = "",
  [string[]]$IssueNumber = @(),
  [switch]$RequireQaClosureEvidence
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "issue-loop-common.ps1")
if ([string]::IsNullOrWhiteSpace($LabelContractPath)) {
  $LabelContractPath = Join-Path $PSScriptRoot "..\references\issue-status-label-contract.json"
}

$contract = Get-IssueLoopContract -Path $LabelContractPath
$repositoryLabels = Assert-IssueLoopRepositoryVocabulary -Repo $Repo -Contract $contract
$activeLabels = @($contract.activeIssueStates | ForEach-Object { Get-IssueLoopStateLabel -Contract $contract -State $_ })
$lifecycleLabels = @($contract.states.PSObject.Properties | ForEach-Object { [string]$_.Value.label })
$mergedMainLabel = Get-IssueLoopStateLabel -Contract $contract -State "merged_main"
$aliases = @(Get-IssueLoopAliasLabels -Contract $contract)
$violations = @()

foreach ($alias in $aliases) {
  if ($repositoryLabels -contains $alias) {
    $violations += [pscustomobject]@{
      kind = "repository_alias_label_present"
      issueNumber = $null
      state = $null
      label = $alias
    }
  }
}

if ($IssueNumber.Count -gt 0) {
  $requestedIssueNumbers = @($IssueNumber | ForEach-Object { [int]$_ })
  $issues = @()
  foreach ($requestedIssueNumber in $requestedIssueNumbers) {
    try {
      $requestedRaw = Invoke-IssueLoopGh -GhArgs @(
        "issue",
        "view",
        ([string]$requestedIssueNumber),
        "--repo",
        $Repo,
        "--json",
        "number,state,labels,url"
      )
      $issues += ($requestedRaw | ConvertFrom-Json)
    } catch {
      $violations += [pscustomobject]@{
        kind = "requested_issue_not_found"
        issueNumber = $requestedIssueNumber
        state = $null
        label = $null
      }
    }
  }
} else {
  $raw = Invoke-IssueLoopGh -GhArgs @("issue", "list", "--repo", $Repo, "--state", "all", "--limit", "1000", "--json", "number,state,labels,url")
  $parsedIssues = $raw | ConvertFrom-Json
  $issues = @($parsedIssues | ForEach-Object { $_ })
}
foreach ($issue in $issues) {
  $names = @($issue.labels | ForEach-Object { [string]$_.name })
  $presentLifecycleLabels = @($names | Where-Object { $lifecycleLabels -contains $_ })
  if ($presentLifecycleLabels.Count -gt 1) {
    $violations += [pscustomobject]@{
      kind = "issue_has_multiple_lifecycle_labels"
      issueNumber = [int]$issue.number
      state = [string]$issue.state
      label = ($presentLifecycleLabels -join ",")
    }
  }
  foreach ($label in $names) {
    if ($aliases -contains $label) {
      $violations += [pscustomobject]@{
        kind = "issue_alias_label_present"
        issueNumber = [int]$issue.number
        state = [string]$issue.state
        label = $label
      }
    }
    if ([string]$issue.state -eq "CLOSED" -and $activeLabels -contains $label) {
      $violations += [pscustomobject]@{
        kind = "closed_issue_has_active_label"
        issueNumber = [int]$issue.number
        state = [string]$issue.state
        label = $label
      }
    }
  }
  if ($RequireQaClosureEvidence -and [string]$issue.state -eq "CLOSED" -and $names -contains $mergedMainLabel) {
    $detailRaw = Invoke-IssueLoopGh -GhArgs @(
      "issue",
      "view",
      ([string]$issue.number),
      "--repo",
      $Repo,
      "--json",
      "number,comments,url"
    )
    $detail = $detailRaw | ConvertFrom-Json
    $latestLoopStatus = $null
    foreach ($comment in @($detail.comments)) {
      $matches = [regex]::Matches(
        ([string]$comment.body),
        "(?im)^\s*Loop status:\s*([a-z0-9_-]+)\s*$"
      )
      foreach ($match in $matches) {
        $latestLoopStatus = [string]$match.Groups[1].Value
      }
    }
    if ($latestLoopStatus -ne "qa_passed_closed") {
      $violations += [pscustomobject]@{
        kind = "closed_merged_main_issue_missing_qa_passed_evidence"
        issueNumber = [int]$issue.number
        state = [string]$issue.state
        label = $mergedMainLabel
      }
    }
  }
}

$result = [pscustomobject]@{
  schemaVersion = "lotus.issue-status-audit.v1"
  repository = $Repo
  requireQaClosureEvidence = [bool]$RequireQaClosureEvidence
  requestedIssueNumbers = @($IssueNumber | ForEach-Object { [int]$_ })
  issueCount = $issues.Count
  violationCount = $violations.Count
  violations = $violations
}
$result | ConvertTo-Json -Depth 8
if ($violations.Count -gt 0) {
  exit 1
}
