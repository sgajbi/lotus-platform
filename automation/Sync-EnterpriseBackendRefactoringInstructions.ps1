param(
    [Parameter(Mandatory=$false)]
    [string[]]$Repositories = @(),

    [Parameter(Mandatory=$false)]
    [string]$Source = '',

    [Parameter(Mandatory=$false)]
    [string]$RepositoryRoot = '',

    [switch]$CheckOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($Source)) {
    $Source = (Resolve-Path (Join-Path $PSScriptRoot '..\context\playbooks\ENTERPRISE-BACKEND-REFACTORING-INSTRUCTIONS.md')).Path
}
if ([string]::IsNullOrWhiteSpace($RepositoryRoot)) {
    $RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
}

$sourceContent = Get-Content -Raw $Source
$sourceNormalized = ($sourceContent -replace "`r`n", "`n").TrimEnd("`n", "`r")
$drift = @()

$repositoryNames = $Repositories
if ($repositoryNames.Count -eq 0) {
    $repoRegistry = Join-Path $PSScriptRoot 'repos.json'
    if (Test-Path $repoRegistry) {
        $repositoryNames = @(
            Get-Content -Raw $repoRegistry |
                ConvertFrom-Json |
                Where-Object {
                    $_.name -like 'lotus-*' -and
                    $_.name -ne 'lotus-platform' -and
                    $_.name -ne 'lotus-workbench'
                } |
                Select-Object -ExpandProperty name
        )
    } else {
        $repositoryNames = @(
            Get-ChildItem -Path $RepositoryRoot -Directory -Filter 'lotus-*' |
                Where-Object { $_.Name -ne 'lotus-platform' -and $_.Name -ne 'lotus-workbench' } |
                Select-Object -ExpandProperty Name
        )
    }
}

if ($repositoryNames.Count -eq 0) {
    throw "No Lotus backend repositories were resolved for enterprise backend refactoring instruction sync."
}

foreach ($repo in $repositoryNames) {
    $repoPath = Join-Path $RepositoryRoot $repo
    if (!(Test-Path $repoPath)) {
        throw "Repository not found: $repoPath"
    }

    $destDir = Join-Path $repoPath 'docs\architecture'
    $dest = Join-Path $destDir 'ENTERPRISE_BACKEND_REFACTORING_INSTRUCTIONS.md'

    if ($CheckOnly) {
        if (!(Test-Path $dest)) {
            $drift += "missing: $dest"
            Write-Output "missing: $repoPath"
            continue
        }
        $destContent = Get-Content -Raw $dest
        $destNormalized = ($destContent -replace "`r`n", "`n").TrimEnd("`n", "`r")
        if ($destNormalized -ne $sourceNormalized) {
            $drift += "drift: $dest"
            Write-Output "drift: $repoPath"
            continue
        }
        Write-Output "ok: $repoPath"
        continue
    }

    if (!(Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir | Out-Null }
    Copy-Item -Path $Source -Destination $dest -Force
    Write-Output "synced: $repoPath"
}

if ($CheckOnly -and $drift.Count -gt 0) {
    throw "Enterprise backend refactoring instruction drift detected in $($drift.Count) repository/repositories."
}
