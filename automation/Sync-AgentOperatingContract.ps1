[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$SourcePath = "",
    [string[]]$TargetPath = @(),
    [string]$WorkspaceRoot = "",
    [string[]]$Repository = @(),
    [switch]$AllRepoRoots,
    [switch]$IncludeDeployedTarget,
    [switch]$CheckOnly,
    [switch]$Force
)

Set-StrictMode -Version Latest

$skippedTargets = [System.Collections.Generic.List[string]]::new()

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
    "lotus-archive",
    "lotus-idea"
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


function Test-RepositoryIsQuiescent {
    <#
        A deploy into a repository someone else is mid-slice in is locally
        reasonable and remotely destructive: it appears in their working tree as
        a change they did not make, and if the governing source is not merged yet
        it is a change that should not exist anywhere. Skip such a target and say
        so, rather than writing and leaving them to discover it.
    #>
    param([string]$TargetPath)

    $repoRoot = Split-Path -Parent $TargetPath
    if (-not $repoRoot) { return $true }

    $insideWorkTree = & git -C $repoRoot rev-parse --is-inside-work-tree 2>$null
    if ($LASTEXITCODE -ne 0 -or $insideWorkTree -ne "true") {
        # Not a checkout (the deployed CODEX_HOME target); nothing to disturb.
        return $true
    }

    $dirty = & git -C $repoRoot status --porcelain 2>$null
    if ($LASTEXITCODE -ne 0) { return $true }
    return [string]::IsNullOrWhiteSpace(($dirty | Out-String).Trim())
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

function Invoke-GitText {
    param(
        [string]$RepoRoot,
        [string[]]$Arguments
    )

    $gitCommand = Get-Command git -ErrorAction SilentlyContinue
    if (-not $gitCommand) {
        return $null
    }

    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        $output = & $gitCommand.Source -C $RepoRoot @Arguments 2>$null
        if ($LASTEXITCODE -ne 0) {
            return $null
        }
        return (($output -join "`n").Trim())
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
}

function Get-RepoRootCheckoutHint {
    param([object]$Target)

    if ($Target.kind -ne "repo-root") {
        return ""
    }

    $repoRoot = Split-Path -Parent $Target.path
    if (-not (Test-Path (Join-Path $repoRoot ".git"))) {
        return ""
    }

    $insideWorkTree = Invoke-GitText -RepoRoot $repoRoot -Arguments @("rev-parse", "--is-inside-work-tree")
    if ($insideWorkTree -ne "true") {
        return ""
    }

    $branch = Invoke-GitText -RepoRoot $repoRoot -Arguments @("rev-parse", "--abbrev-ref", "HEAD")
    $originMain = Invoke-GitText -RepoRoot $repoRoot -Arguments @("rev-parse", "--verify", "origin/main")
    if (-not $originMain) {
        return ""
    }

    $aheadBehind = Invoke-GitText -RepoRoot $repoRoot -Arguments @("rev-list", "--left-right", "--count", "HEAD...origin/main")
    if (-not $aheadBehind) {
        return ""
    }

    $parts = @($aheadBehind -split "\s+")
    if ($parts.Count -lt 2) {
        return ""
    }

    $ahead = [int]$parts[0]
    $behind = [int]$parts[1]
    $branchLabel = if ($branch) { $branch } else { "current checkout" }

    if ($behind -gt 0 -and $ahead -gt 0) {
        return "checkout hint: $branchLabel has diverged from origin/main ($ahead ahead, $behind behind)"
    }

    if ($behind -gt 0) {
        return "checkout hint: $branchLabel is behind origin/main by $behind commit(s)"
    }

    if ($ahead -gt 0) {
        return "checkout hint: $branchLabel is ahead of origin/main by $ahead commit(s)"
    }

    return ""
}

$resolvedPlatformRoot = Resolve-PlatformRoot
$resolvedWorkspaceRoot = Resolve-WorkspaceRootPath -RequestedWorkspaceRoot $WorkspaceRoot
$targets = Resolve-RequestedTargets -ExplicitTargetPaths $TargetPath -RepositoryNames $Repository -UseAllRepoRoots:$AllRepoRoots -UseDeployedTarget:$IncludeDeployedTarget -ResolvedWorkspaceRoot $resolvedWorkspaceRoot -ResolvedPlatformRoot $resolvedPlatformRoot
$sourcePathToUse = if ($SourcePath) {
    $SourcePath
}
else {
    Join-Path $PSScriptRoot "..\context\AGENTS-OPERATING-CONTRACT.md"
}
$resolvedSource = (Resolve-Path $sourcePathToUse).ProviderPath
# -Encoding utf8 is required: without it Get-Content decodes with the system
# codepage, so a UTF-8 em dash is read as three cp1252 characters and written
# back double-encoded. The check then never converges, because the file this
# script just wrote does not match the source it wrote it from.
$sourceRepoRoot = (& git -C (Split-Path -Parent $resolvedSource) rev-parse --show-toplevel 2>$null | Select-Object -First 1)
$sourceIsOnOriginMain = $false
if ($LASTEXITCODE -eq 0 -and $sourceRepoRoot) {
    $sourceRelativePath = [System.IO.Path]::GetRelativePath($sourceRepoRoot, $resolvedSource).Replace("\", "/")
    & git -C $sourceRepoRoot rev-parse --verify origin/main 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        & git -C $sourceRepoRoot diff --quiet origin/main -- $sourceRelativePath
        $sourceIsOnOriginMain = ($LASTEXITCODE -eq 0)
    }
}

$sourceContent = Get-Content -Raw -Encoding utf8 $resolvedSource
$normalizedSourceContent = Normalize-ContractContent $sourceContent

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$checkedTargets = 0
$checkFailures = New-Object System.Collections.Generic.List[string]

foreach ($target in $targets) {
    if ($CheckOnly) {
        if (-not (Test-Path $target.path)) {
            if ($target.kind -eq "deployed" -and $env:GITHUB_ACTIONS -eq "true") {
                Write-Host "Agent operating contract check skipped because deployed AGENTS target is not present on this GitHub runner: $($target.path)"
                continue
            }
            $checkFailures.Add("Target AGENTS file not found: $($target.path)") | Out-Null
            continue
        }

        $targetContent = Get-Content -Raw -Encoding utf8 $target.path
        $normalizedTargetContent = Normalize-ContractContent $targetContent
        if ($normalizedTargetContent -ne $normalizedSourceContent) {
            $hint = Get-RepoRootCheckoutHint -Target $target
            $message = "Target AGENTS file is not synchronized with the governed source: $($target.path)"
            if ($hint) {
                $message = "$message ($hint)"
            }
            $checkFailures.Add($message) | Out-Null
            continue
        }

        $checkedTargets += 1
        continue
    }

    # The repository this script lives in is the operator's own: they are editing
    # the contract here, so a dirty tree is expected and not someone else's work.
    $targetRepoRoot = Split-Path -Parent $target.path
    $isOwnRepository = $targetRepoRoot -and ((Resolve-Path -LiteralPath $targetRepoRoot -ErrorAction SilentlyContinue).Path -eq (Resolve-Path -LiteralPath $ResolvedPlatformRoot -ErrorAction SilentlyContinue).Path)

    # Deploying a contract that is not on origin/main puts branch-only policy
    # into other repositories. Contract changes reach siblings only after the
    # central source lands on main.
    # Only guard real sibling checkouts. A target that is not a git working tree
    # is a deployment location or a test workspace: there is no other session to
    # disturb and no history for the content to be missing from.
    $targetIsWorkTree = $false
    if ($targetRepoRoot) {
        $probe = & git -C $targetRepoRoot rev-parse --is-inside-work-tree 2>$null
        $targetIsWorkTree = ($LASTEXITCODE -eq 0) -and ($probe -eq "true")
    }

    if (-not $Force -and -not $isOwnRepository -and $targetIsWorkTree -and -not $sourceIsOnOriginMain) {
        $unmergedMessage = "Skipped $($target.path): the governed source differs from or cannot be verified against origin/main, so deploying it would put unmerged content into another repository. Land and fetch the contract change first, then sync from that repository."
        Write-Warning $unmergedMessage
        $skippedTargets.Add($target.path) | Out-Null
        continue
    }

    if (-not $Force -and -not $isOwnRepository -and $targetIsWorkTree -and -not (Test-RepositoryIsQuiescent -TargetPath $target.path)) {
        $skipMessage = "Skipped $($target.path): that repository has uncommitted changes, so another session is working in it. Re-run the sync there once it is clean, or pass -Force if the change is yours."
        Write-Warning $skipMessage
        $skippedTargets.Add($target.path) | Out-Null
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
    if ($checkFailures.Count -gt 0) {
        $failureList = ($checkFailures.ToArray() -join "`n")
        throw "Agent operating contract check failed for $($checkFailures.Count) target(s):`n$failureList"
    }
    Write-Host "Agent operating contract is synchronized for $checkedTargets target(s)."
}
