param(
  [Parameter(Mandatory=$true)][string]$Repo,
  [Parameter(Mandatory=$true)][int[]]$IssueNumber,
  [Parameter(Mandatory=$true)]
  [ValidateSet("dev_in_progress", "fixed_local", "pr_raised", "merged_pending_main_validation", "merged_main", "blocked", "qa_failed", "qa_passed_closed")]
  [string]$Status,
  [int]$PrNumber = 0,
  [string]$CommitSha = "",
  [string]$LocalValidationRef = "",
  [string]$MainSha = "",
  [long]$PrimaryValidationRunId = 0,
  [long]$SecurityValidationRunId = 0,
  [string]$WikiEvidence = "",
  [string]$BranchCleanupEvidence = "",
  [string]$QaRunRef = "",
  [string]$Summary = "",
  [string]$LabelContractPath = ""
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "issue-loop-common.ps1")
if ([string]::IsNullOrWhiteSpace($LabelContractPath)) {
  $LabelContractPath = Join-Path $PSScriptRoot "..\references\issue-status-label-contract.json"
}

function Assert-RequiredText {
  param([string]$Value, [string]$Name)
  if ([string]::IsNullOrWhiteSpace($Value)) { throw "$Name is required for status '$Status'" }
}

function Update-IssueLoopIssue {
  param([int]$Number, $Contract)

  if ($Status -eq "dev_in_progress") {
    Set-IssueLoopState -Repo $Repo -IssueNumber $Number -Contract $Contract -State "in_progress"
    Add-IssueLoopComment -Repo $Repo -IssueNumber $Number -Body @"
Loop status: dev_in_progress

Development is in progress for this issue.
Next: commit a focused fix with local validation evidence.
"@
    return
  }

  if ($Status -eq "fixed_local") {
    Assert-RequiredText -Value $CommitSha -Name "CommitSha"
    Assert-RequiredText -Value $LocalValidationRef -Name "LocalValidationRef"
    Set-IssueLoopState -Repo $Repo -IssueNumber $Number -Contract $Contract -State "fixed_local"
    Add-IssueLoopComment -Repo $Repo -IssueNumber $Number -Body @"
Loop status: fixed_local

Commit: $CommitSha
Local validation: $LocalValidationRef
Next: open a PR linked to this issue.
"@
    return
  }

  if ($Status -eq "pr_raised") {
    $pr = Assert-IssueLoopPrState -Repo $Repo -PrNumber $PrNumber -ExpectedState "OPEN"
    Set-IssueLoopState -Repo $Repo -IssueNumber $Number -Contract $Contract -State "pr_open"
    Add-IssueLoopComment -Repo $Repo -IssueNumber $Number -Body @"
Loop status: pr_raised

PR opened: #$PrNumber ($($pr.url))
Next: merge only after required PR checks pass.
"@
    return
  }

  if ($Status -eq "merged_pending_main_validation") {
    Assert-RequiredText -Value $MainSha -Name "MainSha"
    $pr = Assert-IssueLoopPrState -Repo $Repo -PrNumber $PrNumber -ExpectedState "MERGED" -ExpectedMainSha $MainSha
    Set-IssueLoopState -Repo $Repo -IssueNumber $Number -Contract $Contract -State "in_progress"
    Add-IssueLoopComment -Repo $Repo -IssueNumber $Number -Body @"
Loop status: merged_pending_main_validation

PR merged: #$PrNumber ($($pr.url))
Main SHA: $MainSha
Result: merge is complete, but exact-main validation is not yet proven. The issue remains open and active.
"@
    return
  }

  if ($Status -eq "merged_main") {
    Assert-RequiredText -Value $MainSha -Name "MainSha"
    Assert-RequiredText -Value $WikiEvidence -Name "WikiEvidence"
    Assert-RequiredText -Value $BranchCleanupEvidence -Name "BranchCleanupEvidence"
    $pr = Assert-IssueLoopPrState -Repo $Repo -PrNumber $PrNumber -ExpectedState "MERGED" -ExpectedMainSha $MainSha
    $primaryRun = Assert-IssueLoopSuccessfulRun -Repo $Repo -RunId $PrimaryValidationRunId -MainSha $MainSha -EvidenceName "Primary mainline validation"
    $securityRun = Assert-IssueLoopSuccessfulRun -Repo $Repo -RunId $SecurityValidationRunId -MainSha $MainSha -EvidenceName "Security or repository-equivalent validation"
    Set-IssueLoopState -Repo $Repo -IssueNumber $Number -Contract $Contract -State "merged_main"
    Add-IssueLoopComment -Repo $Repo -IssueNumber $Number -Body @"
Loop status: merged_main

PR merged: #$PrNumber ($($pr.url))
Exact main SHA: $MainSha
Primary mainline validation: $($primaryRun.name) $($primaryRun.url)
Security/repository-equivalent validation: $($securityRun.name) $($securityRun.url)
Wiki decision/publication: $WikiEvidence
Branch cleanup: $BranchCleanupEvidence
Next: QA verification may close the issue while retaining the merged-main label.
"@
    return
  }

  if ($Status -eq "blocked") {
    Assert-RequiredText -Value $Summary -Name "Summary"
    Set-IssueLoopState -Repo $Repo -IssueNumber $Number -Contract $Contract -State "blocked"
    Add-IssueLoopComment -Repo $Repo -IssueNumber $Number -Body @"
Loop status: blocked

Blocker: $Summary
Next: remove the blocker, then transition back to dev_in_progress.
"@
    return
  }

  if ($Status -eq "qa_failed") {
    Assert-RequiredText -Value $QaRunRef -Name "QaRunRef"
    Assert-RequiredText -Value $Summary -Name "Summary"
    $issue = Get-IssueLoopIssue -Repo $Repo -IssueNumber $Number
    if ([string]$issue.state -eq "CLOSED") {
      $null = Invoke-IssueLoopGh -GhArgs @("issue", "reopen", $Number.ToString(), "--repo", $Repo)
    }
    Set-IssueLoopState -Repo $Repo -IssueNumber $Number -Contract $Contract -State "in_progress"
    Add-IssueLoopComment -Repo $Repo -IssueNumber $Number -Body @"
Loop status: qa_failed

QA run/evidence: $QaRunRef
Failure: $Summary
Result: issue is open and returned to active implementation.
"@
    return
  }

  Assert-RequiredText -Value $QaRunRef -Name "QaRunRef"
  $issue = Get-IssueLoopIssue -Repo $Repo -IssueNumber $Number
  $currentNames = @($issue.labels | ForEach-Object { [string]$_.name })
  $mergedMainLabel = Get-IssueLoopStateLabel -Contract $Contract -State "merged_main"
  if (-not ($currentNames -contains $mergedMainLabel)) {
    throw "Issue #$Number must have $mergedMainLabel before qa_passed_closed"
  }
  Set-IssueLoopState -Repo $Repo -IssueNumber $Number -Contract $Contract -State "merged_main"
  Add-IssueLoopComment -Repo $Repo -IssueNumber $Number -Body @"
Loop status: qa_passed_closed

QA run/evidence: $QaRunRef
Result: verified fixed on main. Closing the issue with merged-main retained.
"@
  $null = Invoke-IssueLoopGh -GhArgs @("issue", "close", $Number.ToString(), "--repo", $Repo)
}

$contract = Get-IssueLoopContract -Path $LabelContractPath
$null = Assert-IssueLoopRepositoryVocabulary -Repo $Repo -Contract $contract
foreach ($number in $IssueNumber) {
  Update-IssueLoopIssue -Number $number -Contract $contract
}

Write-Output "Updated issue(s) $($IssueNumber -join ', ') in $Repo with status '$Status'."
