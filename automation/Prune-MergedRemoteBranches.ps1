param(
    [string] $Repo,
    [switch] $AllLotusRepos,
    [switch] $Apply,
    [int] $ClosedBranchRetentionDays = 30
)

$ErrorActionPreference = "Stop"

if (-not $Repo -and -not $AllLotusRepos) {
    throw "Specify -Repo owner/name or -AllLotusRepos."
}

if ($Repo -and $AllLotusRepos) {
    throw "Specify only one of -Repo or -AllLotusRepos."
}

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$platformRoot = Split-Path -Parent $scriptRoot
$python = & (Join-Path $scriptRoot "Resolve-PlatformAutomationPython.ps1")

$arguments = @(
    (Join-Path $scriptRoot "prune_merged_remote_branches.py"),
    "--closed-branch-retention-days",
    $ClosedBranchRetentionDays
)

if ($AllLotusRepos) {
    $arguments += "--all-lotus-repos"
} else {
    $arguments += @("--repo", $Repo)
}

if ($Apply) {
    $arguments += "--apply"
}

Push-Location $platformRoot
try {
    & $python @arguments
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}
finally {
    Pop-Location
}
