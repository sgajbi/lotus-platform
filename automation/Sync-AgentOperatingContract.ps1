param(
    [string]$SourcePath = (Join-Path $PSScriptRoot "..\context\AGENTS-OPERATING-CONTRACT.md"),
    [string[]]$TargetPath = @(),
    [string]$WorkspaceRoot = "",
    [string[]]$Repository = @(),
    [switch]$AllRepoRoots,
    [switch]$IncludeDeployedTarget,
    [switch]$CheckOnly
)

Set-StrictMode -Version Latest

$InScopeRepositories = @(
    "lotus-platform",
    "lotus-workbench",
    "lotus-gateway",
    "lotus-core",
    "lotus-performance",
    "lotus-risk",
    "lotus-advise",
    "lotus-manage",
    "lotus-report",
    "lotus-ai",
    "lotus-render",
    "lotus-archive"
)

function Normalize-ContractContent {
    param([string]$Content)

    return ($Content -replace "`r`n", "`n").TrimEnd("`n", "`r")
}

function Resolve-PlatformRoot {
    return (Resolve-Path (Join-Path $PSScriptRoot "..")).ProviderPath
}

function Resolve-DefaultTargetPath {
    if ($env:CODEX_HOME) {
        return (Join-Path $env:CODEX_HOME "AGENTS.md")
    }

    if ($env:USERPROFILE) {
        return (Join-Path $env:USERPROFILE ".codex\AGENTS.md")
    }

    if ($env:HOME) {
        return (Join-Path $env:HOME ".codex/AGENTS.md")
    }

    throw "Unable to resolve default AGENTS target path from CODEX_HOME, USERPROFILE, or HOME."
}

function Resolve-WorkspaceRootPath {
    param([string]$RequestedWorkspaceRoot)

    if ($RequestedWorkspaceRoot) {
        return (Resolve-Path $RequestedWorkspaceRoot).ProviderPath
    }

    return (Split-Path -Parent (Resolve-PlatformRoot))
}

function New-TargetSpec {
    param(
        [string]$Path,
        [string]$Kind,
        [string]$Label
    )

    return [ordered]@{
        path = [System.IO.Path]::GetFullPath($Path)
        kind = $Kind
        label = $Label
    }
}

function Resolve-RepoRootTargetPath {
    param(
        [string]$RepositoryName,
        [string]$ResolvedWorkspaceRoot,
        [string]$ResolvedPlatformRoot
    )

    if ($RepositoryName -notin $InScopeRepositories) {
        throw "Unsupported Lotus repository for AGENTS synchronization: $RepositoryName"
    }

    $repoRoot = if ($RepositoryName -eq "lotus-platform") {
        $ResolvedPlatformRoot
    }
    else {
        Join-Path $ResolvedWorkspaceRoot $RepositoryName
    }

    return (Join-Path $repoRoot "AGENTS.md")
}

function Resolve-RequestedTargets {
    param(
        [string[]]$ExplicitTargetPaths,
        [string[]]$RepositoryNames,
        [switch]$UseAllRepoRoots,
        [switch]$UseDeployedTarget,
        [string]$ResolvedWorkspaceRoot,
        [string]$ResolvedPlatformRoot
    )

    $targets = New-Object System.Collections.Generic.List[object]

    foreach ($path in $ExplicitTargetPaths) {
        $targets.Add((New-TargetSpec -Path $path -Kind "explicit" -Label "explicit target")) | Out-Null
    }

    $repoNamesToUse = if ($UseAllRepoRoots) {
        $InScopeRepositories
    }
    else {
        $RepositoryNames
    }

    foreach ($repoName in $repoNamesToUse) {
        $repoTargetPath = Resolve-RepoRootTargetPath -RepositoryName $repoName -ResolvedWorkspaceRoot $ResolvedWorkspaceRoot -ResolvedPlatformRoot $ResolvedPlatformRoot
        $targets.Add((New-TargetSpec -Path $repoTargetPath -Kind "repo-root" -Label "$repoName repo-root target")) | Out-Null
    }

    if ($UseDeployedTarget -or $targets.Count -eq 0) {
        $targets.Add((New-TargetSpec -Path (Resolve-DefaultTargetPath) -Kind "deployed" -Label "default deployed target")) | Out-Null
    }

    $seen = @{}
    $dedupedTargets = New-Object System.Collections.Generic.List[object]
    foreach ($target in $targets) {
        if ($seen.ContainsKey($target.path)) {
            continue
        }
        $seen[$target.path] = $true
        $dedupedTargets.Add($target) | Out-Null
    }

    return @($dedupedTargets.ToArray())
}

$resolvedPlatformRoot = Resolve-PlatformRoot
$resolvedWorkspaceRoot = Resolve-WorkspaceRootPath -RequestedWorkspaceRoot $WorkspaceRoot
$targets = Resolve-RequestedTargets -ExplicitTargetPaths $TargetPath -RepositoryNames $Repository -UseAllRepoRoots:$AllRepoRoots -UseDeployedTarget:$IncludeDeployedTarget -ResolvedWorkspaceRoot $resolvedWorkspaceRoot -ResolvedPlatformRoot $resolvedPlatformRoot
$resolvedSource = (Resolve-Path $SourcePath).ProviderPath
$sourceContent = Get-Content -Raw $resolvedSource
$normalizedSourceContent = Normalize-ContractContent $sourceContent

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$checkedTargets = 0

foreach ($target in $targets) {
    if ($CheckOnly) {
        if (-not (Test-Path $target.path)) {
            if ($target.kind -eq "deployed" -and $env:GITHUB_ACTIONS -eq "true") {
                Write-Host "Agent operating contract check skipped because deployed AGENTS target is not present on this GitHub runner: $($target.path)"
                continue
            }
            throw "Target AGENTS file not found: $($target.path)"
        }

        $targetContent = Get-Content -Raw $target.path
        $normalizedTargetContent = Normalize-ContractContent $targetContent
        if ($normalizedTargetContent -ne $normalizedSourceContent) {
            throw "Target AGENTS file is not synchronized with the governed source: $($target.path)"
        }

        $checkedTargets += 1
        continue
    }

    $targetParent = Split-Path -Parent $target.path
    if ($targetParent) {
        New-Item -ItemType Directory -Path $targetParent -Force | Out-Null
    }
    [System.IO.File]::WriteAllText($target.path, $normalizedSourceContent + "`n", $utf8NoBom)
    Write-Host "Synchronized AGENTS operating contract to $($target.path)"
}

if ($CheckOnly) {
    Write-Host "Agent operating contract is synchronized for $checkedTargets target(s)."
}
