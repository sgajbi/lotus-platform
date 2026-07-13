$ErrorActionPreference = "Stop"
if (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
  $PSNativeCommandUseErrorActionPreference = $false
}

function Invoke-IssueLoopGh {
  param([Parameter(Mandatory=$true)][string[]]$GhArgs)

  $result = & gh @GhArgs 2>&1
  if ($LASTEXITCODE -ne 0) {
    $text = ($result | Out-String).Trim()
    throw "gh command failed: gh $($GhArgs -join ' ') :: $text"
  }
  return $result
}

function Get-IssueLoopContract {
  param([Parameter(Mandatory=$true)][string]$Path)

  if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
    throw "Issue status label contract not found: $Path"
  }
  $contract = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
  if ($contract.schemaVersion -ne "lotus.issue-status-labels.v1") {
    throw "Unsupported issue status label contract schemaVersion: $($contract.schemaVersion)"
  }

  $requiredStates = @("in_progress", "fixed_local", "pr_open", "merged_main", "blocked")
  $primaryLabels = @()
  foreach ($state in $requiredStates) {
    $definition = $contract.states.$state
    if ($null -eq $definition -or [string]::IsNullOrWhiteSpace([string]$definition.label)) {
      throw "Issue status label contract is missing states.$state.label"
    }
    $primaryLabels += [string]$definition.label
  }
  if (($primaryLabels | Select-Object -Unique).Count -ne $primaryLabels.Count) {
    throw "Issue status label contract primary labels must be unique"
  }
  return $contract
}

function Get-IssueLoopStateLabel {
  param(
    [Parameter(Mandatory=$true)]$Contract,
    [Parameter(Mandatory=$true)][string]$State
  )
  return [string]$Contract.states.$State.label
}

function Get-IssueLoopAllStateLabels {
  param([Parameter(Mandatory=$true)]$Contract)

  $labels = @()
  foreach ($property in $Contract.states.PSObject.Properties) {
    $labels += [string]$property.Value.label
    foreach ($alias in @($property.Value.aliases)) {
      if (-not [string]::IsNullOrWhiteSpace([string]$alias)) {
        $labels += [string]$alias
      }
    }
  }
  return @($labels | Select-Object -Unique)
}

function Get-IssueLoopAliasLabels {
  param([Parameter(Mandatory=$true)]$Contract)

  $labels = @()
  foreach ($property in $Contract.states.PSObject.Properties) {
    $labels += @($property.Value.aliases)
  }
  return @($labels | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } | Select-Object -Unique)
}

function Assert-IssueLoopRepositoryVocabulary {
  param(
    [Parameter(Mandatory=$true)][string]$Repo,
    [Parameter(Mandatory=$true)]$Contract
  )

  $raw = Invoke-IssueLoopGh -GhArgs @("label", "list", "--repo", $Repo, "--limit", "1000", "--json", "name")
  $available = @(($raw | ConvertFrom-Json) | ForEach-Object { [string]$_.name })
  $missing = @()
  foreach ($property in $Contract.states.PSObject.Properties) {
    $label = [string]$property.Value.label
    if (-not ($available -contains $label)) {
      $missing += $label
    }
  }
  if ($missing.Count -gt 0) {
    throw "Repository $Repo is missing configured issue status labels: $($missing -join ', '). Configure the repository or provide -LabelContractPath; labels are never created automatically."
  }
  return $available
}

function Get-IssueLoopIssue {
  param(
    [Parameter(Mandatory=$true)][string]$Repo,
    [Parameter(Mandatory=$true)][int]$IssueNumber
  )
  $raw = Invoke-IssueLoopGh -GhArgs @("issue", "view", $IssueNumber.ToString(), "--repo", $Repo, "--json", "number,state,labels,url")
  return $raw | ConvertFrom-Json
}

function Set-IssueLoopState {
  param(
    [Parameter(Mandatory=$true)][string]$Repo,
    [Parameter(Mandatory=$true)][int]$IssueNumber,
    [Parameter(Mandatory=$true)]$Contract,
    [Parameter(Mandatory=$true)][string]$State
  )

  $issue = Get-IssueLoopIssue -Repo $Repo -IssueNumber $IssueNumber
  $currentNames = @($issue.labels | ForEach-Object { [string]$_.name })
  $target = Get-IssueLoopStateLabel -Contract $Contract -State $State
  foreach ($label in (Get-IssueLoopAllStateLabels -Contract $Contract)) {
    if ($label -ne $target -and $currentNames -contains $label) {
      $null = Invoke-IssueLoopGh -GhArgs @("issue", "edit", $IssueNumber.ToString(), "--repo", $Repo, "--remove-label", $label)
    }
  }
  if (-not ($currentNames -contains $target)) {
    $null = Invoke-IssueLoopGh -GhArgs @("issue", "edit", $IssueNumber.ToString(), "--repo", $Repo, "--add-label", $target)
  }
}

function Add-IssueLoopComment {
  param(
    [Parameter(Mandatory=$true)][string]$Repo,
    [Parameter(Mandatory=$true)][int]$IssueNumber,
    [Parameter(Mandatory=$true)][string]$Body
  )
  $null = Invoke-IssueLoopGh -GhArgs @("issue", "comment", $IssueNumber.ToString(), "--repo", $Repo, "--body", $Body)
}

function Assert-IssueLoopPrState {
  param(
    [Parameter(Mandatory=$true)][string]$Repo,
    [Parameter(Mandatory=$true)][int]$PrNumber,
    [Parameter(Mandatory=$true)][ValidateSet("OPEN", "MERGED")][string]$ExpectedState,
    [string]$ExpectedMainSha = ""
  )

  if ($PrNumber -le 0) { throw "PrNumber is required" }
  $raw = Invoke-IssueLoopGh -GhArgs @("pr", "view", $PrNumber.ToString(), "--repo", $Repo, "--json", "state,mergeCommit,url")
  $pr = $raw | ConvertFrom-Json
  if ([string]$pr.state -ne $ExpectedState) {
    throw "PR #$PrNumber must be $ExpectedState; actual state is $($pr.state)"
  }
  if ($ExpectedState -eq "MERGED" -and -not [string]::IsNullOrWhiteSpace($ExpectedMainSha)) {
    if ([string]$pr.mergeCommit.oid -ne $ExpectedMainSha) {
      throw "PR #$PrNumber merge commit $($pr.mergeCommit.oid) does not match MainSha $ExpectedMainSha"
    }
  }
  return $pr
}

function Assert-IssueLoopSuccessfulRun {
  param(
    [Parameter(Mandatory=$true)][string]$Repo,
    [Parameter(Mandatory=$true)][long]$RunId,
    [Parameter(Mandatory=$true)][string]$MainSha,
    [Parameter(Mandatory=$true)][string]$EvidenceName
  )

  if ($RunId -le 0) { throw "$EvidenceName run ID is required" }
  $raw = Invoke-IssueLoopGh -GhArgs @("run", "view", $RunId.ToString(), "--repo", $Repo, "--json", "conclusion,headSha,name,url")
  $run = $raw | ConvertFrom-Json
  if ([string]$run.conclusion -ne "success") {
    throw "$EvidenceName run $RunId must have conclusion success; actual conclusion is $($run.conclusion)"
  }
  if ([string]$run.headSha -ne $MainSha) {
    throw "$EvidenceName run $RunId head SHA $($run.headSha) does not match MainSha $MainSha"
  }
  return $run
}
