param(
    [switch]$CheckOnly,
    [switch]$Publish,
    [switch]$AllowUnpublishedSourceChanges,
    [switch]$AllowPublishedContentLoss,
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

function Invoke-GitCommand {
    param(
        [Parameter(Position = 0, ValueFromRemainingArguments = $true)]
        [string[]]$Arguments
    )

    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        $output = @(& git @Arguments 2>&1)
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    foreach ($line in $output) {
        Write-Host $line
    }
    if ($exitCode -ne 0) {
        throw "git command failed with exit code ${exitCode}: git $($Arguments -join ' ')"
    }
}

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

    $map = [System.Collections.Generic.Dictionary[string, string]]::new([System.StringComparer]::Ordinal)
    if (-not (Test-Path -LiteralPath $Root)) {
        return $map
    }

    if (Test-Path -LiteralPath (Join-Path $Root ".git")) {
        $trackedPaths = @(& git -C $Root ls-files)
        if ($LASTEXITCODE -ne 0) {
            throw "git command failed with exit code ${LASTEXITCODE}: git -C $Root ls-files"
        }
        foreach ($path in $trackedPaths) {
            $fullPath = Join-Path $Root $path
            if (Test-Path -LiteralPath $fullPath -PathType Leaf) {
                $map[$path] = Get-NormalizedContentHash -Path $fullPath
            }
            else {
                $map[$path] = "__MISSING_TRACKED_WIKI_FILE__"
            }
        }
        return $map
    }

    Get-ChildItem -LiteralPath $Root -File -Recurse |
        Where-Object { $_.FullName -notmatch "\\.git(\\|$)" } |
        ForEach-Object {
            $map[(Get-RelativePath -Root $Root -Path $_.FullName)] = Get-NormalizedContentHash -Path $_.FullName
        }
    return $map
}

function Get-WikiMapValue {
    param(
        [Parameter(Mandatory = $true)]$Map,
        [Parameter(Mandatory = $true)][string]$Path
    )

    if ($Map.ContainsKey($Path)) {
        return $Map[$Path]
    }
    return $null
}

function Compare-WikiDirectories {
    param(
        [Parameter(Mandatory = $true)][string]$SourceRoot,
        [Parameter(Mandatory = $true)][string]$PublishedRoot,
        [string]$RepositoryRoot = ""
    )

    $sourceMap = Get-WikiFileMap -Root $SourceRoot
    $publishedMap = Get-WikiFileMap -Root $PublishedRoot
    $allPaths = [System.Collections.Generic.SortedSet[string]]::new([System.StringComparer]::Ordinal)
    foreach ($path in $sourceMap.Keys) {
        $null = $allPaths.Add($path)
    }
    foreach ($path in $publishedMap.Keys) {
        $null = $allPaths.Add($path)
    }
    $diffs = @()
    foreach ($path in $allPaths) {
        $sourceHash = Get-WikiMapValue -Map $sourceMap -Path $path
        $publishedHash = Get-WikiMapValue -Map $publishedMap -Path $path
        if ($sourceHash -eq $publishedHash) {
            continue
        }

        # Three outcomes, not two. `SourceOnly` is an unrun publish and is safe
        # to resolve by publishing. `PublishedOnly` is content that exists
        # nowhere else, and publishing destroys it. `ModifiedBoth` is the common
        # case and is neither -- reading it as one-sided is how a two-way
        # classifier gets the right answer for the wrong reason.
        if ($null -eq $publishedHash) {
            $direction = "SourceOnly"
        }
        elseif ($null -eq $sourceHash) {
            # A published path whose content is still authored somewhere in
            # source is a rename, not a loss, and publishing replaces it
            # correctly. Classifying it as PublishedOnly would refuse a
            # legitimate publish and teach the operator to pass
            # -AllowPublishedContentLoss as a matter of course, which is the
            # erosion the refusal exists to avoid.
            #
            # Two forms, and the first alone was not enough. A case-only change
            # of spelling keeps the path recognisable. An ordinary move --
            # Old.md to New.md with the content unchanged -- does not, and
            # review of this change found that it produced a PublishedOnly and
            # a SourceOnly entry and refused the routine post-merge publish.
            #
            # The counterpart must be a source path that does NOT exist on the
            # published wiki. Matching the content against any source path was
            # the first attempt and review found it deletes a distinct page: if
            # two published pages happen to share content and source keeps only
            # one of them, the other matches the retained page's hash, is called
            # a rename, and is destroyed with no override. Requiring the match
            # to be a source-only path means the counterpart is a page that
            # genuinely arrived under a new name.
            #
            # Deliberately NOT covered: a rename whose content was also edited
            # in the move has no matching hash and is still refused as
            # PublishedOnly. Content identity is not necessary for a rename, only
            # sufficient, and the operator resolves that case with the explicit
            # override. Refusing a real rename costs one flag; deleting a real
            # page costs the page.
            $renamedByCase = @($sourceMap.Keys | Where-Object { $_ -ieq $path }).Count -gt 0
            $retainedInSource = $false
            if (-not $renamedByCase -and $null -ne $publishedHash) {
                # A rename is a PAIRING, so the counterparts must be countable
                # one-to-one. Taking the first source-only match was the second
                # attempt and review found the fan-in it allows: two published
                # pages holding the same bytes both match the single source-only
                # page that replaced one of them, both are called renames, and
                # publishing replaces two distinct pages with one -- no override
                # asked for.
                #
                # Comparing counts refuses exactly that case while still
                # accepting the ordinary one-for-one move, and it needs no
                # arbitrary choice about WHICH published page the survivor is.
                # Ambiguity is resolved by refusing, because the cost of being
                # wrong is a deleted page against one explicit flag.
                $publishedOnlyWithHash = 0
                foreach ($publishedPath in $publishedMap.Keys) {
                    if ((Get-WikiMapValue -Map $publishedMap -Path $publishedPath) -ne $publishedHash) {
                        continue
                    }
                    if ($null -eq (Get-WikiMapValue -Map $sourceMap -Path $publishedPath)) {
                        $publishedOnlyWithHash++
                    }
                }
                $sourceOnlyWithHash = 0
                foreach ($sourcePath in $sourceMap.Keys) {
                    if ((Get-WikiMapValue -Map $sourceMap -Path $sourcePath) -ne $publishedHash) {
                        continue
                    }
                    if ($null -eq (Get-WikiMapValue -Map $publishedMap -Path $sourcePath)) {
                        $sourceOnlyWithHash++
                    }
                }
                $retainedInSource = ($sourceOnlyWithHash -ge $publishedOnlyWithHash) -and ($sourceOnlyWithHash -gt 0)
            }
            $deletedInSource = $false
            if (-not $renamedByCase -and -not $retainedInSource) {
                $deletedInSource = Test-WikiPageDeletedInSource -RepositoryRoot $RepositoryRoot -RelativePath $path -PublishedHash $publishedHash
            }
            $direction = if ($renamedByCase) { "RenamedCase" }
                elseif ($retainedInSource) { "RenamedPath" }
                elseif ($deletedInSource) { "SourceDeleted" }
                else { "PublishedOnly" }
        }
        else {
            $direction = "ModifiedBoth"
        }

        $diffs += [pscustomobject]@{
            Path = $path
            Direction = $direction
            SourceHash = $sourceHash
            PublishedHash = $publishedHash
        }
    }
    return $diffs
}

function Format-WikiDiffs {
    param($Diffs)

    return (($Diffs | ForEach-Object { "$($_.Path) [$($_.Direction)]" }) -join ", ")
}

function Test-WikiPageDeletedInSource {
    <#
        .SYNOPSIS
        Whether this page was authored in wiki/ and has since been removed.

        .DESCRIPTION
        A page the repository once authored and deliberately deleted is not an
        unrelated hand edit, but it reaches the comparison looking identical to
        one: absent from source, present on the published wiki.

        Making PublishedOnly unconditionally blocking -- correct for hand edits
        -- therefore refused intentional removals as well, in both the pre-merge
        gate and the post-merge publish, and the only way through was a
        destructive-sounding override on a decision that had already been
        reviewed and merged. That is the flag-passing habit these refusals exist
        to avoid.

        History separates them, and it separates them the same way before and
        after the merge: a page with commits under wiki/ and no file today was
        removed on purpose. A page hand-created on the live wiki has no such
        history and stays blocking.
    #>
    param(
        [Parameter(Mandatory = $true)][string]$RepositoryRoot,
        [Parameter(Mandatory = $true)][string]$RelativePath,
        [Parameter(Mandatory = $true)][string]$PublishedHash
    )

    if ([string]::IsNullOrWhiteSpace($RepositoryRoot) -or -not (Test-Path (Join-Path $RepositoryRoot ".git"))) {
        # Not a repository: history cannot answer, so fail closed and keep the
        # page blocking rather than assume the deletion was authored.
        return $false
    }

    Push-Location $RepositoryRoot
    try {
        # A shallow checkout cannot answer this. `git log` exits successfully
        # and returns nothing, because the page existed only in a commit that
        # was never fetched -- so an authored deletion is indistinguishable from
        # a page that was never in source, and the caller would silently take
        # the wrong branch. Say so instead of guessing: a wrong silent answer
        # here either blocks every deliberate removal or destroys a live page.
        $shallow = (& git rev-parse --is-shallow-repository 2>$null)
        if ($LASTEXITCODE -eq 0 -and $shallow -eq "true") {
            throw "Cannot classify wiki/$RelativePath : the repository at $RepositoryRoot is a shallow checkout, so a deletion recorded in an unfetched commit is indistinguishable from a page that was never authored. Check out with fetch-depth: 0 before running the wiki parity check."
        }

        # Having existed is not enough. A page whose path was authored and later
        # removed, but whose PUBLISHED copy was afterwards hand-edited or
        # recreated, still has history under wiki/ -- and treating that as an
        # authored removal deletes live content nobody authored, with no
        # override, which is the failure this whole change exists to prevent.
        #
        # So the live bytes must match the last version source actually
        # authored. Anything else is live-only content wearing a deleted path,
        # and stays blocking.
        $commits = @()
        try {
            $commits = @(& git log --format=%H -- "wiki/$RelativePath" 2>$null)
        }
        catch {
            $commits = @()
        }
        if ($LASTEXITCODE -ne 0 -or $commits.Count -eq 0) {
            return $false
        }

        $temporaryFile = [System.IO.Path]::GetTempFileName()
        try {
            foreach ($commit in $commits) {
                $blob = & git show "${commit}:wiki/$RelativePath" 2>$null
                if ($LASTEXITCODE -ne 0) {
                    # This commit is the removal itself, or predates the file.
                    continue
                }
                # Hashed through the same normalisation the maps use, so the
                # comparison is against like: writing the blob out and hashing
                # the file avoids a second hashing path drifting from the first.
                Set-Content -LiteralPath $temporaryFile -Value $blob -NoNewline -Encoding utf8
                $authoredHash = Get-NormalizedContentHash -Path $temporaryFile
                return $authoredHash -eq $PublishedHash
            }
        }
        finally {
            Remove-Item -LiteralPath $temporaryFile -Force -ErrorAction SilentlyContinue
        }
        return $false
    }
    finally {
        Pop-Location
    }
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
        Invoke-GitCommand clone $remote $PublishedRoot
    }
    Push-Location $PublishedRoot
    try {
        Invoke-GitCommand fetch origin --prune
        $branch = (& git branch --show-current)
        if ($LASTEXITCODE -ne 0) {
            throw "git command failed with exit code ${LASTEXITCODE}: git branch --show-current"
        }
        if (-not $branch) {
            $branch = "master"
            Invoke-GitCommand switch $branch
        }
        Invoke-GitCommand config user.email "lotus-wiki-sync@users.noreply.github.com"
        Invoke-GitCommand config user.name "Lotus Wiki Sync"

        # The published tree must be what the WIKI holds, not what this reusable
        # clone happens to contain. `pull --ff-only` does not give that: it
        # succeeds when the local branch is merely ahead, so a leftover local
        # commit or an uncommitted deletion -- both reachable after an
        # interrupted publish -- stays in the working tree. The deleted page is
        # then absent from the comparison, no PublishedOnly refusal fires, and
        # the unconditional push below sends the deletion to the live wiki with
        # no override ever requested. Found in review.
        #
        # Resetting to origin/$branch discards local state deliberately. That is
        # safe and correct here: the clone is a derived workspace whose content
        # is regenerated from repo-authored wiki/ on every publish, and anything
        # committed only locally was never on the wiki, so nothing published is
        # lost. It also enforces the rule that the publication target must not
        # carry hand-authored truth absent from source.
        Invoke-GitCommand reset --hard "origin/$branch"
        Invoke-GitCommand clean -fd
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

    # Compared before publishing, not after. The publish overwrites the
    # published tree with source, so a comparison taken afterwards reports no
    # drift by construction and can never see what the publish destroyed.
    $diffs = @(Compare-WikiDirectories -SourceRoot $sourceRoot -PublishedRoot $publishedRoot -RepositoryRoot $repositoryRoot)

    if ($Publish) {
        $publishedOnly = @($diffs | Where-Object { $_.Direction -eq "PublishedOnly" })
        if ($publishedOnly.Count -gt 0) {
            $detail = (($publishedOnly | ForEach-Object { "$($_.Path) (published hash $($_.PublishedHash))" }) -join ", ")
            if (-not $AllowPublishedContentLoss) {
                throw "${repositoryName}: refusing to publish. $($publishedOnly.Count) file(s) exist only on the published wiki and would be destroyed: $detail. Repo-authored wiki/ is the source of truth, so this is content that was hand-edited on the wiki or predates the source. Recover it into wiki/ first, or re-run with -AllowPublishedContentLoss to discard it deliberately."
            }
            Write-Warning "${repositoryName}: -AllowPublishedContentLoss was supplied; destroying $($publishedOnly.Count) published-only file(s): $detail"
        }

        Push-Location $publishedRoot
        try {
            Clear-PublishedWikiContent -PublishedRoot $publishedRoot
            Invoke-GitCommand rm -r --quiet --ignore-unmatch .
            Copy-Item -Path (Join-Path $sourceRoot "*") -Destination $publishedRoot -Recurse -Force
            Invoke-GitCommand add --all
            $status = @(& git status --short)
            if ($status.Count -gt 0) {
                Invoke-GitCommand commit --message "docs: publish wiki from repo source"
            }
            Invoke-GitCommand push origin $branch
        }
        finally {
            Pop-Location
        }
    }

    if ($Publish) {
        # Re-read after publishing so the reported state is what the wiki now
        # holds rather than what it held before the copy.
        $diffs = @(Compare-WikiDirectories -SourceRoot $sourceRoot -PublishedRoot $publishedRoot -RepositoryRoot $repositoryRoot)
    }
    $results += [pscustomobject]@{
        Repository = $repositoryName
        Source = $sourceRoot
        Published = $publishedRoot
        DiffCount = $diffs.Count
        Diffs = (Format-WikiDiffs -Diffs $diffs)
    }

    # The allowance is for drift THIS BRANCH created, and it must stay that
    # narrow. It used to consume every category, so an unrelated page that
    # exists only on the live wiki passed the pre-merge gate whenever a branch
    # touched wiki/ at all -- and the post-merge publish then refused, leaving
    # the merged wiki change unpublished with no way forward that does not
    # discard someone's page. Found in review of this change.
    #
    # PublishedOnly is never something a branch created, so it is never covered.
    $blockingDiffs = @($diffs | Where-Object { $_.Direction -eq "PublishedOnly" })
    if ($CheckOnly -and $diffs.Count -gt 0 -and $blockingDiffs.Count -eq 0 -and $AllowUnpublishedSourceChanges -and (Test-WikiSourceChanged -RepositoryRoot $repositoryRoot)) {
        Write-Warning "${repositoryName}: repo-authored wiki source differs from published wiki because this branch changes wiki/. Publish after merge with Sync-RepoWikis.ps1 -Publish -Repository $repositoryName."
    }
    elseif ($CheckOnly -and $diffs.Count -gt 0) {
        $publishedOnlyCount = @($diffs | Where-Object { $_.Direction -eq "PublishedOnly" }).Count
        $remedy = if ($publishedOnlyCount -gt 0) {
            "$publishedOnlyCount file(s) exist only on the published wiki; publishing would destroy them. Recover them into wiki/ first."
        }
        else {
            "Publish after merge with Sync-RepoWikis.ps1 -Publish -Repository $repositoryName."
        }
        throw "${repositoryName}: published GitHub wiki is not synchronized with repo-authored wiki source. Drift: $(Format-WikiDiffs -Diffs $diffs). $remedy"
    }
}

$results | Select-Object Repository, DiffCount, Source, Published, Diffs | Format-Table -AutoSize
