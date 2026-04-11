param(
  [Parameter(Mandatory=$true)][string]$Repo,
  [Parameter(Mandatory=$true)][int]$IssueNumber,
  [Parameter(Mandatory=$true)][ValidateSet("dev_in_progress","pr_raised","merged_pending_qa","qa_failed","qa_passed_closed")][string]$Status,
  [int]$PrNumber = 0,
  [string]$QaCommand = "",
  [string]$QaRunRef = "",
  [string]$Summary = ""
)

$ErrorActionPreference = "Stop"
if (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
  $PSNativeCommandUseErrorActionPreference = $false
}

function Invoke-Gh {
  param([string[]]$GhArgs)
  $result = & gh @GhArgs 2>&1
  if ($LASTEXITCODE -ne 0) {
    $text = ($result | Out-String).Trim()
    throw "gh command failed: gh $($GhArgs -join ' ') :: $text"
  }
  return $result
}

function Set-IssueLabels {
  param(
    [string[]]$Add = @(),
    [string[]]$Remove = @()
  )

  $currentRaw = Invoke-Gh -GhArgs @("issue","view",$IssueNumber.ToString(),"--repo",$Repo,"--json","labels")
  $current = $currentRaw | ConvertFrom-Json
  $currentNames = @()
  foreach ($l in $current.labels) { $currentNames += [string]$l.name }

  foreach ($label in $Add) {
    if (-not ($currentNames -contains $label)) {
      try {
        $null = Invoke-Gh -GhArgs @("issue","edit",$IssueNumber.ToString(),"--repo",$Repo,"--add-label",$label)
      } catch {
        if ($_.Exception.Message -match "label.+not found") {
          $null = Invoke-Gh -GhArgs @("label","create",$label,"--repo",$Repo,"--color","B60205","--description","Issue loop state")
          $null = Invoke-Gh -GhArgs @("issue","edit",$IssueNumber.ToString(),"--repo",$Repo,"--add-label",$label)
        } else {
          throw
        }
      }
    }
  }

  foreach ($label in $Remove) {
    if ($currentNames -contains $label) {
      $null = Invoke-Gh -GhArgs @("issue","edit",$IssueNumber.ToString(),"--repo",$Repo,"--remove-label",$label)
    }
  }
}

function Add-IssueComment {
  param([string]$Body)
  $null = Invoke-Gh -GhArgs @("issue","comment",$IssueNumber.ToString(),"--repo",$Repo,"--body",$Body)
}

if ($Status -eq "dev_in_progress") {
  Set-IssueLabels -Add @("status:dev-in-progress") -Remove @("status:qa-failed","status:qa-pending","status:qa-passed")
  Add-IssueComment -Body @"
Loop status: dev_in_progress

Development is in progress for this issue.
Next step: open PR with Fixes #$IssueNumber.
"@
} elseif ($Status -eq "pr_raised") {
  $prText = if ($PrNumber -gt 0) { "#$PrNumber" } else { "(not provided)" }
  Set-IssueLabels -Add @("status:pr-open") -Remove @("status:dev-in-progress")
  Add-IssueComment -Body @"
Loop status: pr_raised

PR opened: $prText
Waiting for CI/review, then merge and request QA retest.
"@
} elseif ($Status -eq "merged_pending_qa") {
  $prText = if ($PrNumber -gt 0) { "#$PrNumber" } else { "(not provided)" }
  Set-IssueLabels -Add @("status:qa-pending") -Remove @("status:pr-open","status:qa-failed")
  Add-IssueComment -Body @"
Loop status: merged_pending_qa

PR merged: $prText
QA requested.

QA command:
$QaCommand
"@
} elseif ($Status -eq "qa_failed") {
  Set-IssueLabels -Add @("status:qa-failed") -Remove @("status:qa-pending","status:qa-passed")
  Add-IssueComment -Body @"
Loop status: qa_failed

QA failed. New dev iteration required.

QA run/evidence: $QaRunRef
Failure summary: $Summary

Next step: implement follow-up fix and reopen PR cycle.
"@
} elseif ($Status -eq "qa_passed_closed") {
  Set-IssueLabels -Add @("status:qa-passed") -Remove @("status:qa-pending","status:qa-failed","status:pr-open","status:dev-in-progress")
  Add-IssueComment -Body @"
Loop status: qa_passed_closed

QA passed.
QA run/evidence: $QaRunRef

Closing issue as verified fixed.
"@
  $null = Invoke-Gh -GhArgs @("issue","close",$IssueNumber.ToString(),"--repo",$Repo)
}

Write-Output "Updated issue #$IssueNumber in $Repo with status '$Status'."
