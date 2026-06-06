param(
    [Parameter(Mandatory=$false)]
    [string[]]$Repositories = @(
        'lotus-advise',
        'lotus-ai',
        'lotus-archive',
        'lotus-core',
        'lotus-gateway',
        'lotus-performance',
        'lotus-render',
        'lotus-report',
        'lotus-risk'
    ),

    [Parameter(Mandatory=$false)]
    [string]$Source = (Resolve-Path (Join-Path $PSScriptRoot '..\..\lotus-manage\docs\architecture\ENTERPRISE_BACKEND_REFACTORING_INSTRUCTIONS.md')).Path,

    [Parameter(Mandatory=$false)]
    [string]$RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

foreach ($repo in $Repositories) {
    $repoPath = Join-Path $RepositoryRoot $repo
    if (!(Test-Path $repoPath)) {
        throw "Repository not found: $repoPath"
    }
    if ((Resolve-Path $repoPath).Path -eq (Split-Path $Source -Parent)) {
        Write-Output "skipped: $repoPath (source repo)"
        continue
    }

    $destDir = Join-Path $repoPath 'docs\architecture'
    if (!(Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir | Out-Null }
    $dest = Join-Path $destDir 'ENTERPRISE_BACKEND_REFACTORING_INSTRUCTIONS.md'
    Copy-Item -Path $Source -Destination $dest -Force
    Write-Output "synced: $repoPath"
}
