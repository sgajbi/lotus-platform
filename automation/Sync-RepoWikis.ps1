param(
    [switch]$CheckOnly,
    [switch]$Publish,
    [switch]$AllowUnpublishedSourceChanges,
    [switch]$AllRepositories,
    [string]$Repository = "lotus-platform",
    [string]$WorkspaceRoot = (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)),
    [string]$PublishRoot = (Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) "_wiki_publish"),
    [string]$RemoteOwner = "sgajbi"
)

$ErrorActionPreference = "Stop"

if (($CheckOnly -and $Publish) -or (-not $CheckOnly -and -not $Publish)) {
    throw "Specify exactly one of -CheckOnly or -Publish."
}

$platformRoot = Split-Path -Parent $PSScriptRoot
$reposConfigPath = Join-Path $PSScriptRoot "repos.json"

function Get-RepositoryNames {
    if ($AllRepositories) {
        $repos = Get-Content -LiteralPath $reposConfigPath -Raw | ConvertFrom-Json
        return @($repos | ForEach-Object { $_.name })
    }
    return @($Repository)
}

function Get-NormalizedContentHash {
    param([Parameter(Mandatory = $true)][string]$Path)

    $text = [System.IO.File]::ReadAllText($Path)
    $normalized = $text -replace "`r`n", "`n"
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($normalized)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        return [BitConverter]::ToString($sha.ComputeHash($bytes)).Replace("-", "")
    }
    finally {
        $sha.Dispose()
    }
}

function Get-RelativePath {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$Path
    )

    $rootFull = [System.IO.Path]::GetFullPath($Root).TrimEnd([System.IO.Path]::DirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
    $pathFull = [System.IO.Path]::GetFullPath($Path)
    return $pathFull.Substring($rootFull.Length).Replace("\", "/")
}

function Get-WikiFileMap {
    param([Parameter(Mandatory = $true)][string]$Root)

    $map = @{}
    if (-not (Test-Path -LiteralPath $Root)) {
        return $map
    }

    Get-ChildItem -LiteralPath $Root -File -Recurse |
        Where-Object { $_.FullName -notmatch "\\.git(\\|$)" } |
        ForEach-Object {
            $map[(Get-RelativePath -Root $Root -Path $_.FullName)] = Get-NormalizedContentHash -Path $_.FullName
        }
    return $map
}

function Compare-WikiDirectories {
    param(
        [Parameter(Mandatory = $true)][string]$SourceRoot,
        [Parameter(Mandatory = $true)][string]$PublishedRoot
    )

    $sourceMap = Get-WikiFileMap -Root $SourceRoot
    $publishedMap = Get-WikiFileMap -Root $PublishedRoot
    $allPaths = @($sourceMap.Keys + $publishedMap.Keys | Sort-Object -Unique)
    $diffs = @()
    foreach ($path in $allPaths) {
        if ($sourceMap[$path] -ne $publishedMap[$path]) {
            $diffs += $path
        }
    }
    return $diffs
}

function Test-WikiSourceChanged {
    param([Parameter(Mandatory = $true)][string]$RepositoryRoot)

    Push-Location $RepositoryRoot
    try {
        $changed = @()
        try {
            $changed = @(& git diff --name-only origin/main...HEAD -- wiki 2>$null)
        }
        catch {
            $changed = @()
        }
        if ($changed.Count -eq 0) {
            try {
                $null = & git rev-parse --verify origin/main 2>$null
                if ($LASTEXITCODE -ne 0) {
                    & git fetch --depth=1 origin main:refs/remotes/origin/main 2>$null
                }
                $changed = @(& git diff --name-only origin/main HEAD -- wiki 2>$null)
            }
            catch {
                $changed = @()
            }
        }
        if ($changed.Count -eq 0) {
            $changed = @(& git status --short -- wiki 2>$null)
        }
        if ($changed.Count -eq 0) {
            try {
                $changed = @(& git diff --name-only HEAD^ HEAD -- wiki 2>$null)
            }
            catch {
                $changed = @()
            }
        }
        return $changed.Count -gt 0
    }
    finally {
        Pop-Location
    }
}

function Clear-PublishedWikiContent {
    param([Parameter(Mandatory = $true)][string]$PublishedRoot)

    $resolvedPublishRoot = (Resolve-Path -LiteralPath $PublishedRoot).Path
    $resolvedBase = (Resolve-Path -LiteralPath $PublishRoot).Path
    if (-not $resolvedPublishRoot.StartsWith($resolvedBase, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to clean unexpected wiki publish path: $resolvedPublishRoot"
    }

    Get-ChildItem -LiteralPath $PublishedRoot -Force |
        Where-Object { $_.Name -ne ".git" } |
        Remove-Item -Recurse -Force
}

function Ensure-WikiClone {
    param(
        [Parameter(Mandatory = $true)][string]$RepositoryName,
        [Parameter(Mandatory = $true)][string]$PublishedRoot
    )

    if (Test-Path -LiteralPath $RemoteOwner) {
        $remote = Join-Path $RemoteOwner "$RepositoryName.wiki.git"
    }
    else {
        $remote = "https://github.com/$RemoteOwner/$RepositoryName.wiki.git"
    }
    if (-not (Test-Path -LiteralPath $PublishedRoot)) {
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $PublishedRoot) | Out-Null
        & git clone $remote $PublishedRoot
    }
    Push-Location $PublishedRoot
    try {
        & git fetch origin --prune
        $branch = & git branch --show-current
        if (-not $branch) {
            $branch = "master"
            & git switch $branch
        }
        & git pull --ff-only origin $branch
        return $branch
    }
    finally {
        Pop-Location
    }
}

$results = @()
foreach ($repositoryName in Get-RepositoryNames) {
    $repositoryRoot = Join-Path $WorkspaceRoot $repositoryName
    $sourceRoot = Join-Path $repositoryRoot "wiki"
    $publishedRoot = Join-Path $PublishRoot "$repositoryName-wiki"
    if (-not (Test-Path -LiteralPath $sourceRoot)) {
        throw "${repositoryName}: missing repo-authored wiki source at $sourceRoot"
    }

    $branch = Ensure-WikiClone -RepositoryName $repositoryName -PublishedRoot $publishedRoot

    if ($Publish) {
        Push-Location $publishedRoot
        try {
            Clear-PublishedWikiContent -PublishedRoot $publishedRoot
            Copy-Item -Path (Join-Path $sourceRoot "*") -Destination $publishedRoot -Recurse -Force
            $status = @(& git status --short)
            if ($status.Count -gt 0) {
                & git add -A
                & git commit -m "docs: publish wiki from repo source"
                & git push origin $branch
            }
        }
        finally {
            Pop-Location
        }
    }

    $diffs = @(Compare-WikiDirectories -SourceRoot $sourceRoot -PublishedRoot $publishedRoot)
    $results += [pscustomobject]@{
        Repository = $repositoryName
        Source = $sourceRoot
        Published = $publishedRoot
        DiffCount = $diffs.Count
        Diffs = ($diffs -join ", ")
    }

    if ($CheckOnly -and $diffs.Count -gt 0 -and $AllowUnpublishedSourceChanges -and (Test-WikiSourceChanged -RepositoryRoot $repositoryRoot)) {
        Write-Warning "${repositoryName}: repo-authored wiki source differs from published wiki because this branch changes wiki/. Publish after merge with Sync-RepoWikis.ps1 -Publish -Repository $repositoryName."
    }
    elseif ($CheckOnly -and $diffs.Count -gt 0) {
        throw "${repositoryName}: published GitHub wiki is not synchronized with repo-authored wiki source. Drift: $($diffs -join ', ')"
    }
}

$results | Format-Table -AutoSize
