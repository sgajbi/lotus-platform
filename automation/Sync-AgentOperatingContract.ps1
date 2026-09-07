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
# Targets refused on provenance, as distinct from targets deferred because
# another session is mid-slice in them. A deferral is re-runnable and reports
# success; a refusal means the content should not exist anywhere yet.
$refusedTargets = [System.Collections.Generic.List[string]]::new()

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
    param([string]$RepositoryRoot)

    # The caller passes the repository root that has already been resolved. This
    # used to take the target's path and split its parent, which asked Git about
    # a directory that need not exist -- and a failed probe was read as
    # quiescent, so a nested target below a dirty sibling was written anyway.
    if (-not $RepositoryRoot) { return $true }
    $repoRoot = $RepositoryRoot

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

    if ($UseDeployedTarget) {
        $targets.Add((New-TargetSpec -Path (Resolve-DefaultTargetPath) -Kind "deployed" -Label "deployed target")) | Out-Null
    }

    # `-IncludeDeployedTarget` adds a target; it does not choose one. Testing
    # for an empty list meant the switch suppressed the repository default, so
    # `-CheckOnly -IncludeDeployedTarget` could pass while the committed
    # repository-root copy was stale -- the opposite of "as well".
    # Wrapped in @() because an unbound array parameter is \$null, and reading
    # .Count on it is a terminating error under Set-StrictMode.
    $hasSelectedTarget = (@($ExplicitTargetPaths).Count -gt 0) -or (@($repoNamesToUse).Count -gt 0)
    if (-not $hasSelectedTarget) {
        # No target was named, so check this repository's own copy rather than
        # the machine-local deployed file. The deployed path exists only on a
        # workstation with Codex installed, so defaulting to it meant the
        # repository's own CI check skipped its only target and then reported
        # success having compared nothing. A deployed check is a developer
        # environment check and must be asked for by name.
        $platformTargetPath = Resolve-RepoRootTargetPath -RepositoryName "lotus-platform" -ResolvedWorkspaceRoot $ResolvedWorkspaceRoot -ResolvedPlatformRoot $ResolvedPlatformRoot
        $targets.Add((New-TargetSpec -Path $platformTargetPath -Kind "repo-root" -Label "lotus-platform repo-root target")) | Out-Null
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

function Get-NearestExistingAncestor {
    <#
        Git cannot run with -C in a directory that does not exist, so asking a
        target's own parent whether it is in a work tree answers "no" for every
        path whose parent is absent from disk: a sparse checkout, or a directory
        deleted locally. The repository is still there and still ships the file,
        so the question is asked from the nearest ancestor that does exist.
    #>
    param([string]$CandidatePath)

    $current = $CandidatePath
    while ($current -and -not (Test-Path -LiteralPath $current -PathType Container)) {
        $parent = Split-Path -Parent $current
        if (-not $parent -or $parent -eq $current) {
            return $null
        }
        $current = $parent
    }

    return $current
}

function Test-PathIsInsideWorkTree {
    param([string]$CandidatePath)

    if (-not $CandidatePath) {
        return $false
    }

    $probePath = Get-NearestExistingAncestor $CandidatePath
    if (-not $probePath) {
        return $false
    }

    return ((Invoke-GitText -RepoRoot $probePath -Arguments @("rev-parse", "--is-inside-work-tree")) -eq "true")
}

function Get-CommittedBlobId {
    <#
        The object id Git recorded for a path at HEAD. Blob ids are content
        addressed, so the same content has the same id in every repository
        regardless of path, remote, or checkout settings.
    #>
    param(
        [string]$RepoRoot,
        [string]$RelativePath
    )

    return (Invoke-GitText -RepoRoot $RepoRoot -Arguments @("rev-parse", "HEAD:$RelativePath"))
}

function Get-CommittedText {
    <#
        The committed content, with only its line endings normalized.

        Invoke-GitText trims the result, which is right for probing a branch
        name and wrong for comparing a document: leading or trailing whitespace
        is content, and trimming it would report two different files as equal.
    #>
    param(
        [string]$RepoRoot,
        [string]$RelativePath
    )

    $gitCommand = Get-Command git -ErrorAction SilentlyContinue
    if (-not $gitCommand) {
        return $null
    }

    $previousErrorActionPreference = $ErrorActionPreference
    # A native command's output is decoded with the host's console encoding,
    # which is UTF-8 in an interactive terminal and frequently is not when the
    # shell is spawned without one. This file already carries that lesson for
    # Get-Content; reading a blob through Git has the same exposure, and it is
    # worse here because the two sides of the comparison would then be decoded
    # differently and every target would report as drifted.
    $previousOutputEncoding = [Console]::OutputEncoding
    try {
        $ErrorActionPreference = "Continue"
        [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
        $output = & $gitCommand.Source -C $RepoRoot show "HEAD:$RelativePath" 2>$null
        if ($LASTEXITCODE -ne 0) {
            return $null
        }
        return ($output -join "`n")
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
        [Console]::OutputEncoding = $previousOutputEncoding
    }
}

function Test-CommittedContractSynchronized {
    <#
        Compare what the repository will actually ship, not what is on disk.

        A working tree holds whatever an editor, a line-ending conversion, or
        another session last left there. It can hold correct bytes over an
        unsynchronized commit, and stale bytes over a correct one, so reading it
        proves nothing about the repository. The committed blob is the artefact
        that reaches every other clone.

        Returns an empty string when synchronized, and a failure message
        otherwise. Every path that cannot prove synchronization returns a
        failure rather than an empty string.
    #>
    param(
        [object]$Target,
        [string]$SourceBlobId,
        [string]$SourceCommittedText
    )

    $repoRoot = Split-Path -Parent $Target.path
    if (-not $repoRoot) {
        return "Cannot resolve a repository root for $($Target.path), so its committed content cannot be verified."
    }

    if (-not $SourceBlobId) {
        return "The governed contract source is not committed, so synchronization of $($Target.path) cannot be proved. Commit the source first, then re-run this check."
    }

    # `<rev>:<path>` is resolved from the tree root, so a nested target such as
    # `<repo>/config/AGENTS.md` must be looked up as `config/AGENTS.md` and not
    # as `AGENTS.md` from its own directory — which reads a different file, and
    # passes or fails on whatever happens to sit at the root.
    #
    # The path is derived from the target itself rather than from Git's
    # `--show-prefix`. The prefix describes the directory Git was asked from,
    # and when the target's own directory is absent from disk that is an
    # ancestor of it: prefix plus leaf would then name `AGENTS.md` at the root
    # while the target is `config/AGENTS.md`, and the check would quietly verify
    # a different file.
    $probeRoot = Get-NearestExistingAncestor $repoRoot
    if (-not $probeRoot) {
        return "Cannot resolve a repository root for $($Target.path), so its committed content cannot be verified."
    }
    # Git answers for the directory it was asked from, so this prefix belongs to
    # the probe root rather than to the target. The remainder below is the part
    # of the target's path under that root, and both operands are written the
    # way the caller wrote them: a workspace reached through a symbolic link
    # subtracts correctly here, where comparing against Git's physical
    # `--show-toplevel` would reject a perfectly synchronized target.
    $probePrefix = Invoke-GitText -RepoRoot $probeRoot -Arguments @("rev-parse", "--show-prefix")
    if ($null -eq $probePrefix) {
        return "Unable to resolve the repository-relative path for $($Target.path), so its committed content cannot be verified."
    }
    $probeFullPath = [System.IO.Path]::GetFullPath($probeRoot).Replace("\", "/").TrimEnd("/")
    $targetFullPath = [System.IO.Path]::GetFullPath($Target.path).Replace("\", "/")
    if (-not $targetFullPath.StartsWith("$probeFullPath/", [System.StringComparison]::OrdinalIgnoreCase)) {
        return "The target $($Target.path) does not sit under the repository directory $probeRoot, so its committed content cannot be verified."
    }
    $relativePath = ($probePrefix + $targetFullPath.Substring($probeFullPath.Length + 1)).Replace("\", "/")
    $targetBlobId = Get-CommittedBlobId -RepoRoot $probeRoot -RelativePath $relativePath
    if (-not $targetBlobId) {
        return "Target AGENTS file is not committed, so its content cannot be verified: $($Target.path)"
    }

    if ($targetBlobId -eq $SourceBlobId) {
        return ""
    }

    # A blob mismatch is drift. An earlier revision normalized line endings here
    # and returned success with a warning, which declared two repositories
    # synchronized while they shipped different committed bytes -- and the
    # governed rule is a committed blob-SHA comparison precisely so that
    # "identical apart from something" cannot become a pass. The remedy for a
    # line-ending difference is to re-lift the file, not to accept it.

    $hint = Get-RepoRootCheckoutHint -Target $Target
    $message = "Committed AGENTS file is not synchronized with the governed source: $($Target.path) (committed blob $targetBlobId, governed source blob $SourceBlobId)"
    if ($hint) {
        $message = "$message ($hint)"
    }
    return $message
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
# `Resolve-Path` fails outright for a path that is not on disk, which stopped a
# sparse checkout or a local deletion before the committed lookup below could
# run. The full path is derived without requiring materialization, and whether
# the file is actually present is decided where that matters.
$resolvedSource = [System.IO.Path]::GetFullPath($sourcePathToUse)
$sourceExistsOnDisk = Test-Path -LiteralPath $resolvedSource -PathType Leaf
# -Encoding utf8 is required: without it Get-Content decodes with the system
# codepage, so a UTF-8 em dash is read as three cp1252 characters and written
# back double-encoded. The check then never converges, because the file this
# script just wrote does not match the source it wrote it from.
$global:LASTEXITCODE = 0
$sourceProbeRoot = Get-NearestExistingAncestor (Split-Path -Parent $resolvedSource)
$sourceRepoRootOutput = if ($sourceProbeRoot) {
    @(& git -C $sourceProbeRoot rev-parse --show-toplevel 2>$null)
}
else {
    @()
}
$sourceRepoRootExitCode = $LASTEXITCODE
$sourceRepoRoot = $sourceRepoRootOutput | Select-Object -First 1
$sourceIsOnOriginMain = $false
# Declared before the branch below because Set-StrictMode makes reading an
# unassigned variable a terminating error, and the source may be outside a
# repository.
$sourceRelativePath = ""
if ($sourceRepoRootExitCode -eq 0 -and $sourceRepoRoot) {
    # Ask Git for the source directory's repository-relative prefix. This works
    # in Windows PowerShell 5.1 and PowerShell 7 without widening the pathspec.
    $sourceDirectory = $sourceProbeRoot
    $sourcePrefixOutput = @(& git -C $sourceDirectory rev-parse --show-prefix 2>$null)
    $sourcePrefixExitCode = $LASTEXITCODE
    $sourcePrefix = $sourcePrefixOutput | Select-Object -First 1
    if ($sourcePrefixExitCode -eq 0) {
        # The prefix belongs to the directory Git was asked from, which may be
        # an ancestor of the source when the source's own directory is absent.
        $sourceProbeFull = [System.IO.Path]::GetFullPath($sourceProbeRoot).Replace("\", "/").TrimEnd("/")
        $sourceFull = $resolvedSource.Replace("\", "/")
        if ($sourceFull.StartsWith("$sourceProbeFull/", [System.StringComparison]::OrdinalIgnoreCase)) {
            $sourceRelativePath = ($sourcePrefix + $sourceFull.Substring($sourceProbeFull.Length + 1)).Replace("\", "/")
        }
    }
    if ($sourceRelativePath) {
        & git -C $sourceRepoRoot ls-files --error-unmatch -- $sourceRelativePath 2>$null | Out-Null
    }
    if ($sourceRelativePath -and $LASTEXITCODE -eq 0) {
        & git -C $sourceRepoRoot rev-parse --verify origin/main 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            & git -C $sourceRepoRoot diff --quiet origin/main -- $sourceRelativePath
            $sourceIsOnOriginMain = ($LASTEXITCODE -eq 0)
        }
    }
}

$sourceCommittedBlobId = ""
$sourceCommittedText = ""
if ($sourceRepoRoot -and $sourceRelativePath) {
    $sourceCommittedBlobId = Get-CommittedBlobId -RepoRoot $sourceRepoRoot -RelativePath $sourceRelativePath
    $sourceCommittedText = Get-CommittedText -RepoRoot $sourceRepoRoot -RelativePath $sourceRelativePath
}

# A source that exists only at HEAD is still a governed source. Requiring it on
# disk failed a check whose two committed blobs were identical, which describes
# the checkout rather than the repositories.
$sourceContent = if ($sourceExistsOnDisk) {
    Get-Content -Raw -Encoding utf8 $resolvedSource
}
elseif ($sourceCommittedText) {
    $sourceCommittedText
}
else {
    throw "Unable to read the governed contract source at $resolvedSource. It is neither on disk nor committed at HEAD."
}
$normalizedSourceContent = Normalize-ContractContent $sourceContent

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$checkedTargets = 0
$checkFailures = New-Object System.Collections.Generic.List[string]

foreach ($target in $targets) {
    if ($CheckOnly) {
        # Git membership decides how a target is compared, not how it was named.
        # An explicit -TargetPath inside a checkout ships its commit exactly as a
        # repo-root target does, so naming it differently must not change what is
        # inspected.
        # A deployed copy is never answered from a commit. It is the file the
        # agent runtime actually reads, so its bytes on disk are the whole
        # question, and a home directory kept as a dotfiles checkout would
        # otherwise route it through HEAD: passing on a committed copy while the
        # installed file is stale, or failing because it is untracked. Keeping
        # the deployed check separate is the point of it.
        if ($target.kind -ne "deployed" -and (Test-PathIsInsideWorkTree (Split-Path -Parent $target.path))) {
            # The commit is read before the working tree is required to exist. A
            # repository ships what it committed: a file missing from disk but
            # present at HEAD is synchronized, and reporting it as absent would
            # describe the checkout rather than the repository.
            $committedFailure = Test-CommittedContractSynchronized -Target $target -SourceBlobId $sourceCommittedBlobId -SourceCommittedText $sourceCommittedText
            if ($committedFailure) {
                $checkFailures.Add($committedFailure) | Out-Null
                continue
            }

            $checkedTargets += 1
            continue
        }

        if (-not (Test-Path $target.path)) {
            if ($target.kind -eq "deployed" -and $env:GITHUB_ACTIONS -eq "true") {
                Write-Host "Agent operating contract check skipped because deployed AGENTS target is not present on this GitHub runner: $($target.path)"
                continue
            }
            $checkFailures.Add("Target AGENTS file not found: $($target.path)") | Out-Null
            continue
        }

        # An explicit or deployed target is a file on disk that need not be in
        # any repository, so its bytes are all there is to compare on that side.
        # The source side is still compared at HEAD whenever the source is in
        # Git: an uncommitted edit present in both would otherwise agree with
        # itself and report a deployed copy as synchronized with a contract it
        # does not match, and a mixed run could validate two source versions.
        # A source that lives outside any repository has only its bytes, and
        # comparing them is the best available answer. A source that lives
        # *inside* one and has nothing at HEAD is a different case: it is
        # untracked or staged-only, so there is no governed content for another
        # clone to pull, and falling back to the working tree would compare the
        # target against a version that exists on this machine alone.
        if (-not $sourceCommittedText -and $sourceRepoRoot) {
            $checkFailures.Add("Cannot verify $($target.path): the governed source $resolvedSource is inside a repository but has no committed content at HEAD, so there is no governed version to compare against. Commit the source first, then re-run this check.") | Out-Null
            continue
        }

        $comparisonSource = if ($sourceCommittedText) {
            Normalize-ContractContent $sourceCommittedText
        }
        else {
            $normalizedSourceContent
        }
        $targetContent = Get-Content -Raw -Encoding utf8 $target.path
        $normalizedTargetContent = Normalize-ContractContent $targetContent
        if ($normalizedTargetContent -ne $comparisonSource) {
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
    # `Resolve-Path` returns nothing for a directory that does not exist yet, and
    # reading `.Path` on nothing left this variable unset. Under Set-StrictMode
    # the provenance condition below then failed to evaluate, and because both
    # errors are non-terminating the script carried on and wrote the file --
    # reporting success while skipping the guard entirely. Full-path
    # normalization answers for a path whether or not it is on disk.
    # Ownership is a property of the repository, not of the target's immediate
    # directory. Comparing the lexical parent classified this repository's own
    # `config/AGENTS.md`, or its root reached through a link, as a sibling: a
    # normal unmerged contract edit was then refused by the provenance guard and
    # a dirty tree skipped, in the one repository where both are expected.
    $isOwnRepository = $false
    $targetWorktreeRoot = ""
    $targetProbeRoot = Get-NearestExistingAncestor $targetRepoRoot
    if ($targetProbeRoot) {
        $targetWorktreeRoot = Invoke-GitText -RepoRoot $targetProbeRoot -Arguments @("rev-parse", "--show-toplevel")
    }
    if ($targetWorktreeRoot) {
        $platformWorktreeRoot = Invoke-GitText -RepoRoot $ResolvedPlatformRoot -Arguments @("rev-parse", "--show-toplevel")
        if ($platformWorktreeRoot) {
            $isOwnRepository = ($targetWorktreeRoot -eq $platformWorktreeRoot)
        }
    }

    # Deploying a contract that is not on origin/main puts branch-only policy
    # into other repositories. Contract changes reach siblings only after the
    # central source lands on main.
    # Only guard real sibling checkouts. A target that is not a git working tree
    # is a deployment location or a test workspace: there is no other session to
    # disturb and no history for the content to be missing from.
    # Git cannot run with -C in a directory that does not exist, and a nested
    # target below a sibling checkout has no parent directory until this script
    # creates one. Probing the missing directory answered "not a work tree",
    # which skipped the provenance refusal and wrote unmerged contract content
    # into another repository -- the one outcome no flag is allowed to override.
    $targetIsWorkTree = [bool]$targetWorktreeRoot

    # -Force is deliberately absent from this condition. It exists to override
    # the quiescence check below, which protects work the operator can see and
    # may legitimately own. Provenance is different in kind: content that is not
    # on origin/main exists nowhere another repository can pull it from, so
    # deploying it publishes policy that has no source. That has happened once,
    # into eleven repositories. No flag overrides it.
    if (-not $isOwnRepository -and $targetIsWorkTree -and -not $sourceIsOnOriginMain) {
        $unmergedMessage = "Skipped $($target.path): the governed source differs from or cannot be verified against origin/main, so deploying it would put unmerged content into another repository. Land and fetch the contract change first, then sync from that repository. -Force does not override this."
        Write-Warning $unmergedMessage
        $skippedTargets.Add($target.path) | Out-Null
        # A refusal is not a deferral. The caller asked for this target to be
        # written and it was not, so the run must not report success: a script
        # that warns and exits 0 lets an operator record a synchronization that
        # never happened.
        $refusedTargets.Add($target.path) | Out-Null
        continue
    }

    if (-not $Force -and -not $isOwnRepository -and $targetIsWorkTree -and -not (Test-RepositoryIsQuiescent -RepositoryRoot $targetWorktreeRoot)) {
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
    if ($checkedTargets -eq 0) {
        # Reporting success for zero comparisons is how this check passed on
        # every GitHub runner while verifying nothing at all.
        throw "Agent operating contract check verified no targets, so it proved nothing. Name a target, or run it where the requested targets exist."
    }
    Write-Host "Agent operating contract is synchronized for $checkedTargets target(s)."
}

# Native Git probes are deliberately allowed to fail when a source or target is
# outside a repository. Once all governed checks and writes have completed,
# prevent that internal probe status from becoming the script's process status.
$global:LASTEXITCODE = 0

if ($refusedTargets.Count -gt 0) {
    throw "Refused to synchronize $($refusedTargets.Count) target(s) because the governed source is not on origin/main: $($refusedTargets.ToArray() -join ', '). Land the contract change first, then sync from those repositories."
}
