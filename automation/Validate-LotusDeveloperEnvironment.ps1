param(
    [ValidateSet("Inspect", "Sync", "Validate")]
    [string]$Mode = "Inspect",
    [ValidateSet("fast", "extended", "platform")]
    [string]$Profile = "fast",
    [string]$WorkspaceRoot = "",
    [string]$OutputDirectory = "output",
    [string]$SkillTargetPath = "",
    [string]$AgentsTargetPath = "",
    [switch]$NoExitOnBlocked
)

$ErrorActionPreference = "Stop"

function Resolve-PlatformRoot {
    return (Resolve-Path (Join-Path $PSScriptRoot "..")).ProviderPath
}

function Resolve-WorkspaceRoot {
    param([string]$RequestedWorkspaceRoot)

    if ($RequestedWorkspaceRoot) {
        return (Resolve-Path $RequestedWorkspaceRoot).ProviderPath
    }

    return (Split-Path -Parent (Resolve-PlatformRoot))
}

function Resolve-CodexHome {
    if ($env:CODEX_HOME) {
        return $env:CODEX_HOME
    }
    if ($env:USERPROFILE) {
        return (Join-Path $env:USERPROFILE ".codex")
    }
    if ($env:HOME) {
        return (Join-Path $env:HOME ".codex")
    }
    return $null
}

function Resolve-DefaultSkillTargetPath {
    $codexHome = Resolve-CodexHome
    if (-not $codexHome) {
        return $null
    }
    return (Join-Path $codexHome "skills")
}

function Resolve-DefaultAgentsTargetPath {
    $codexHome = Resolve-CodexHome
    if (-not $codexHome) {
        return $null
    }
    return (Join-Path $codexHome "AGENTS.md")
}

function Normalize-Text {
    param([string]$Value)
    if ($null -eq $Value) {
        return ""
    }
    return ($Value -replace "`r`n", "`n").TrimEnd("`n", "`r")
}

function Redact-Value {
    param([AllowNull()][string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) {
        return ""
    }
    return "[redacted]"
}

function Add-Check {
    param(
        [System.Collections.Generic.List[object]]$Checks,
        [string]$Name,
        [string]$Status,
        [string]$Message,
        [hashtable]$Evidence = @{}
    )

    $Checks.Add([ordered]@{
        name = $Name
        status = $Status
        message = $Message
        evidence = $Evidence
    }) | Out-Null
}

function Test-CommandAvailable {
    param(
        [System.Collections.Generic.List[object]]$Checks,
        [string]$CommandName,
        [string]$DisplayName,
        [string]$RequiredForProfile = "fast"
    )

    $command = Get-Command $CommandName -ErrorAction SilentlyContinue
    if ($command) {
        Add-Check $Checks $DisplayName "ready" "$CommandName is available." @{
            command = $CommandName
            source = $command.Source
        }
        return $true
    }

    $status = if ($Profile -eq "fast" -and $RequiredForProfile -ne "fast") { "skipped" } else { "blocked" }
    Add-Check $Checks $DisplayName $status "$CommandName is not available on PATH." @{
        command = $CommandName
    }
    return $false
}

function Invoke-CommandQuietly {
    param([string[]]$Command)

    $output = & $Command[0] @($Command | Select-Object -Skip 1) 2>&1
    return [ordered]@{
        exit_code = $LASTEXITCODE
        output = (($output | Out-String) -replace "`r`n", "`n").Trim()
    }
}

function Get-DirectoryFingerprint {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        return $null
    }

    $root = (Resolve-Path $Path).ProviderPath.TrimEnd("\", "/")
    $files = Get-ChildItem -LiteralPath $Path -Recurse -File | Sort-Object FullName
    $parts = foreach ($file in $files) {
        $fullName = $file.FullName
        $relative = $fullName.Substring($root.Length).TrimStart("\", "/") -replace "\\", "/"
        $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
        "$relative=$hash"
    }
    return ($parts -join "`n")
}

function Copy-DirectoryContents {
    param(
        [string]$SourcePath,
        [string]$TargetPath,
        [string]$SafeTargetRoot
    )

    $rootFull = [System.IO.Path]::GetFullPath($SafeTargetRoot).TrimEnd("\", "/")
    $targetFull = [System.IO.Path]::GetFullPath($TargetPath).TrimEnd("\", "/")
    $sourceFull = [System.IO.Path]::GetFullPath($SourcePath).TrimEnd("\", "/")
    $comparison = if ($env:OS -eq "Windows_NT") { [System.StringComparison]::OrdinalIgnoreCase } else { [System.StringComparison]::Ordinal }
    $targetIsUnderRoot = $targetFull.StartsWith($rootFull + [System.IO.Path]::DirectorySeparatorChar, $comparison)
    if (-not $targetIsUnderRoot) {
        throw "Refusing to synchronize skill outside the requested Codex skills target root."
    }
    if ($targetFull.Equals($sourceFull, $comparison)) {
        throw "Refusing to synchronize a skill onto its governed source directory."
    }

    if (Test-Path $TargetPath) {
        Remove-Item -LiteralPath $TargetPath -Recurse -Force
    }
    New-Item -ItemType Directory -Path $TargetPath -Force | Out-Null
    Get-ChildItem -LiteralPath $SourcePath -Force | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $TargetPath -Recurse -Force
    }
}

function Test-AgentsSync {
    param(
        [System.Collections.Generic.List[object]]$Checks,
        [string]$SourcePath,
        [string]$TargetPath,
        [string]$Mode
    )

    if (-not $TargetPath) {
        Add-Check $Checks "agents-sync" "warning" "Unable to resolve Codex AGENTS target path." @{}
        return
    }
    if (-not (Test-Path $SourcePath)) {
        Add-Check $Checks "agents-sync" "blocked" "Governed AGENTS source is missing." @{ source = $SourcePath }
        return
    }

    $source = Normalize-Text (Get-Content -Raw $SourcePath)
    $targetExists = Test-Path $TargetPath
    $target = if ($targetExists) { Normalize-Text (Get-Content -Raw $TargetPath) } else { "" }

    if ($targetExists -and $source -eq $target) {
        Add-Check $Checks "agents-sync" "ready" "Local AGENTS.md is synchronized." @{
            target = $TargetPath
        }
        return
    }

    if ($Mode -eq "Sync") {
        $targetParent = Split-Path -Parent $TargetPath
        if ($targetParent) {
            New-Item -ItemType Directory -Path $targetParent -Force | Out-Null
        }
        $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($TargetPath, $source + "`n", $utf8NoBom)
        Add-Check $Checks "agents-sync" "synced" "Local AGENTS.md was synchronized from the governed source." @{
            target = $TargetPath
        }
        return
    }

    $status = if ($targetExists) { "warning" } else { "blocked" }
    $message = if ($targetExists) { "Local AGENTS.md differs from the governed source." } else { "Local AGENTS.md is missing." }
    Add-Check $Checks "agents-sync" $status $message @{
        target = $TargetPath
    }
}

function Test-SkillSync {
    param(
        [System.Collections.Generic.List[object]]$Checks,
        [string]$PlatformRoot,
        [string]$TargetRoot,
        [string]$Mode
    )

    $manifestPath = Join-Path $PlatformRoot "codex\skills\lotus-skill-manifest.json"
    if (-not (Test-Path $manifestPath)) {
        Add-Check $Checks "skill-sync" "blocked" "Lotus skill manifest is missing." @{ manifest = $manifestPath }
        return
    }
    if (-not $TargetRoot) {
        Add-Check $Checks "skill-sync" "warning" "Unable to resolve Codex skills target path." @{}
        return
    }
    if ($Mode -eq "Sync") {
        New-Item -ItemType Directory -Path $TargetRoot -Force | Out-Null
    }

    $manifest = Get-Content -Raw $manifestPath | ConvertFrom-Json
    $skillResults = New-Object System.Collections.Generic.List[object]
    foreach ($skill in $manifest.skills) {
        $source = Join-Path $PlatformRoot $skill.path
        $target = Join-Path $TargetRoot $skill.name
        if (-not (Test-Path $source)) {
            $skillResults.Add([ordered]@{ name = $skill.name; status = "source-unavailable" }) | Out-Null
            continue
        }
        if (-not (Test-Path $target)) {
            if ($Mode -eq "Sync") {
                Copy-DirectoryContents $source $target $TargetRoot
                $skillResults.Add([ordered]@{ name = $skill.name; status = "synced" }) | Out-Null
            }
            else {
                $skillResults.Add([ordered]@{ name = $skill.name; status = "missing" }) | Out-Null
            }
            continue
        }

        $sourceFingerprint = Get-DirectoryFingerprint $source
        $targetFingerprint = Get-DirectoryFingerprint $target
        if ($sourceFingerprint -eq $targetFingerprint) {
            $skillResults.Add([ordered]@{ name = $skill.name; status = "ready" }) | Out-Null
        }
        elseif ($Mode -eq "Sync") {
            Copy-DirectoryContents $source $target $TargetRoot
            $skillResults.Add([ordered]@{ name = $skill.name; status = "synced" }) | Out-Null
        }
        else {
            $skillResults.Add([ordered]@{ name = $skill.name; status = "stale-or-locally-modified" }) | Out-Null
        }
    }

    $knownNames = @($manifest.skills | ForEach-Object { $_.name })
    $unknownLocal = @()
    if (Test-Path $TargetRoot) {
        $unknownLocal = @(Get-ChildItem -LiteralPath $TargetRoot -Directory | Where-Object { $knownNames -notcontains $_.Name } | ForEach-Object { $_.Name })
    }

    $blockingStates = @("source-unavailable")
    $warningStates = @("missing", "stale-or-locally-modified")
    $statuses = @($skillResults | ForEach-Object { $_.status })
    $status = if (@($statuses | Where-Object { $blockingStates -contains $_ }).Count -gt 0) {
        "blocked"
    }
    elseif (@($statuses | Where-Object { $warningStates -contains $_ }).Count -gt 0) {
        "warning"
    }
    elseif (@($statuses | Where-Object { $_ -eq "synced" }).Count -gt 0) {
        "synced"
    }
    else {
        "ready"
    }

    Add-Check $Checks "skill-sync" $status "Lotus skill inventory evaluated; unknown local skills are preserved." @{
        target = $TargetRoot
        governed_skill_count = @($manifest.skills).Count
        unknown_local_skills = $unknownLocal
        governed_skills = $skillResults
    }
}

function Test-RepositoryPresence {
    param(
        [System.Collections.Generic.List[object]]$Checks,
        [string]$PlatformRoot,
        [string]$WorkspaceRoot
    )

    $reposConfigPath = Join-Path $PlatformRoot "automation\repos.json"
    if (-not (Test-Path $reposConfigPath)) {
        Add-Check $Checks "repository-presence" "blocked" "Repository registry is missing." @{ path = $reposConfigPath }
        return
    }

    $repos = Get-Content -Raw $reposConfigPath | ConvertFrom-Json
    $repoStatuses = foreach ($repo in $repos) {
        $repoPath = if ($repo.name -eq "lotus-platform") { $PlatformRoot } else { Join-Path $WorkspaceRoot $repo.name }
        [ordered]@{
            name = $repo.name
            status = if (Test-Path $repoPath) { "ready" } else { "missing" }
            path = $repoPath
        }
    }
    $missing = @($repoStatuses | Where-Object { $_.status -eq "missing" })
    $status = if ($missing.Count -gt 0 -and $Profile -eq "fast") { "warning" } elseif ($missing.Count -gt 0) { "blocked" } else { "ready" }
    Add-Check $Checks "repository-presence" $status "Lotus repository workspace presence evaluated." @{
        workspace_root = $WorkspaceRoot
        repositories = @($repoStatuses)
    }
}

function Test-ContextDocs {
    param(
        [System.Collections.Generic.List[object]]$Checks,
        [string]$PlatformRoot
    )

    $requiredDocs = @(
        "context\LOTUS-QUICKSTART-CONTEXT.md",
        "context\LOTUS-ENGINEERING-CONTEXT.md",
        "context\CONTEXT-REFERENCE-MAP.md",
        "context\AGENTS-OPERATING-CONTRACT.md",
        "docs\onboarding\LOTUS-DEVELOPER-ONBOARDING.md",
        "docs\onboarding\LOTUS-AGENT-RAMP-UP.md",
        "codex\skills\README.md",
        "codex\skills\lotus-skill-manifest.json"
    )
    $docStatuses = foreach ($doc in $requiredDocs) {
        $path = Join-Path $PlatformRoot $doc
        [ordered]@{
            path = $doc
            status = if (Test-Path $path) { "ready" } else { "missing" }
        }
    }
    $missing = @($docStatuses | Where-Object { $_.status -eq "missing" })
    Add-Check $Checks "context-docs" $(if ($missing.Count -gt 0) { "blocked" } else { "ready" }) "Governed context and onboarding documents evaluated." @{
        documents = @($docStatuses)
    }
}

function Test-IngressPosture {
    param([System.Collections.Generic.List[object]]$Checks)

    $hostsPath = if ($IsWindows -or $env:OS -eq "Windows_NT") {
        Join-Path $env:SystemRoot "System32\drivers\etc\hosts"
    }
    else {
        "/etc/hosts"
    }

    if (-not (Test-Path $hostsPath)) {
        Add-Check $Checks "ingress-posture" "warning" "Hosts file was not readable; run ingress sync validation explicitly." @{ hosts_file = $hostsPath }
        return
    }

    $hosts = Get-Content -Raw $hostsPath
    $requiredHosts = @("workbench.dev.lotus", "gateway.dev.lotus")
    $missingHosts = @($requiredHosts | Where-Object { $hosts -notmatch [regex]::Escape($_) })
    $status = if ($missingHosts.Count -gt 0) { "warning" } else { "ready" }
    Add-Check $Checks "ingress-posture" $status "Canonical dev ingress host posture evaluated; no stack startup was attempted." @{
        hosts_file = $hostsPath
        missing_hosts = $missingHosts
    }
}

function Test-DsnPosture {
    param(
        [System.Collections.Generic.List[object]]$Checks,
        [string]$PlatformRoot
    )

    $candidateEnvFiles = @(
        "platform-stack\.env",
        ".env"
    )
    $envFiles = foreach ($relativePath in $candidateEnvFiles) {
        $path = Join-Path $PlatformRoot $relativePath
        [ordered]@{
            path = $relativePath
            status = if (Test-Path $path) { "present" } else { "missing" }
        }
    }
    $dsnEnvNames = @("DATABASE_URL", "POSTGRES_DSN", "LOTUS_CORE_DSN", "LOTUS_MANAGE_DSN")
    $processDsnStatus = foreach ($name in $dsnEnvNames) {
        $value = [Environment]::GetEnvironmentVariable($name)
        [ordered]@{
            name = $name
            status = if ([string]::IsNullOrWhiteSpace($value)) { "unset" } else { "set" }
            value = Redact-Value $value
        }
    }
    $hasAnyFile = @($envFiles | Where-Object { $_.status -eq "present" }).Count -gt 0
    $hasAnyProcessDsn = @($processDsnStatus | Where-Object { $_.status -eq "set" }).Count -gt 0
    $status = if ($hasAnyFile -or $hasAnyProcessDsn) { "ready" } else { "warning" }
    Add-Check $Checks "dsn-posture" $status "DSN posture evaluated with secret values redacted." @{
        env_files = @($envFiles)
        process_variables = @($processDsnStatus)
    }
}

function Test-GitHubAuth {
    param([System.Collections.Generic.List[object]]$Checks)

    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        Add-Check $Checks "github-auth" "blocked" "GitHub CLI is not available." @{ command = "gh" }
        return
    }

    $result = Invoke-CommandQuietly @("gh", "auth", "status")
    $status = if ($result.exit_code -eq 0) { "ready" } else { "blocked" }
    Add-Check $Checks "github-auth" $status "GitHub CLI authentication evaluated." @{
        command = "gh auth status"
        exit_code = $result.exit_code
    }
}

function Test-DockerPosture {
    param([System.Collections.Generic.List[object]]$Checks)

    if ($Profile -eq "fast") {
        Add-Check $Checks "docker-posture" "skipped" "Docker daemon checks are skipped in the fast profile." @{
            profile = $Profile
        }
        return
    }
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Add-Check $Checks "docker-posture" "blocked" "Docker CLI is not available." @{ command = "docker" }
        return
    }
    $version = Invoke-CommandQuietly @("docker", "--version")
    $compose = Invoke-CommandQuietly @("docker", "compose", "version")
    $info = Invoke-CommandQuietly @("docker", "info")
    $status = if ($version.exit_code -eq 0 -and $compose.exit_code -eq 0 -and $info.exit_code -eq 0) { "ready" } else { "blocked" }
    Add-Check $Checks "docker-posture" $status "Docker CLI, compose, and daemon posture evaluated." @{
        docker_version_exit_code = $version.exit_code
        compose_exit_code = $compose.exit_code
        docker_info_exit_code = $info.exit_code
    }
}

function Write-ReadinessReports {
    param(
        [object]$Report,
        [string]$OutputDirectory
    )

    New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
    $jsonPath = Join-Path $OutputDirectory "developer-environment-readiness.json"
    $markdownPath = Join-Path $OutputDirectory "developer-environment-readiness.md"

    $Report | ConvertTo-Json -Depth 20 | Set-Content -Path $jsonPath -Encoding utf8

    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add("# Lotus Developer Environment Readiness") | Out-Null
    $lines.Add("") | Out-Null
    $lines.Add("- Mode: ``$($Report.mode)``") | Out-Null
    $lines.Add("- Profile: ``$($Report.profile)``") | Out-Null
    $lines.Add("- Overall status: ``$($Report.overall_status)``") | Out-Null
    $lines.Add("- Generated at: ``$($Report.generated_at)``") | Out-Null
    $lines.Add("") | Out-Null
    $lines.Add("| Check | Status | Message |") | Out-Null
    $lines.Add("| --- | --- | --- |") | Out-Null
    foreach ($check in $Report.checks) {
        $message = ($check.message -replace "\|", "\|")
        $lines.Add("| $($check.name) | $($check.status) | $message |") | Out-Null
    }
    $lines.Add("") | Out-Null
    $lines.Add("Secret-bearing values are redacted. Heavy stack startup and E2E validation are not run implicitly by this readiness script.") | Out-Null
    $lines | Set-Content -Path $markdownPath -Encoding utf8

    return [ordered]@{
        json = $jsonPath
        markdown = $markdownPath
    }
}

$platformRoot = Resolve-PlatformRoot
$resolvedWorkspaceRoot = Resolve-WorkspaceRoot $WorkspaceRoot
if (-not $SkillTargetPath) {
    $SkillTargetPath = Resolve-DefaultSkillTargetPath
}
if (-not $AgentsTargetPath) {
    $AgentsTargetPath = Resolve-DefaultAgentsTargetPath
}

$checks = New-Object System.Collections.Generic.List[object]

Test-CommandAvailable $checks "git" "git-cli" "fast" | Out-Null
Test-CommandAvailable $checks "python" "python-runtime" "fast" | Out-Null
Test-CommandAvailable $checks "node" "node-runtime" "fast" | Out-Null
Test-CommandAvailable $checks "npm" "npm-cli" "fast" | Out-Null
Test-GitHubAuth $checks
Test-DockerPosture $checks
Test-RepositoryPresence $checks $platformRoot $resolvedWorkspaceRoot
Test-ContextDocs $checks $platformRoot
Test-SkillSync $checks $platformRoot $SkillTargetPath $Mode
Test-AgentsSync $checks (Join-Path $platformRoot "context\AGENTS-OPERATING-CONTRACT.md") $AgentsTargetPath $Mode
Test-IngressPosture $checks
Test-DsnPosture $checks $platformRoot

$blockedCount = @($checks | Where-Object { $_.status -eq "blocked" }).Count
$warningCount = @($checks | Where-Object { $_.status -eq "warning" }).Count
$overallStatus = if ($blockedCount -gt 0) { "blocked" } elseif ($warningCount -gt 0) { "warning" } else { "ready" }
$checkArray = @($checks | ForEach-Object { $_ })

$report = [ordered]@{
    schema_version = "1.0"
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    mode = $Mode
    profile = $Profile
    platform_root = $platformRoot
    workspace_root = $resolvedWorkspaceRoot
    overall_status = $overallStatus
    blocked_count = $blockedCount
    warning_count = $warningCount
    checks = $checkArray
}

$reports = Write-ReadinessReports $report $OutputDirectory
Write-Host "Wrote Lotus developer environment readiness report:"
Write-Host "  JSON: $($reports.json)"
Write-Host "  Markdown: $($reports.markdown)"
Write-Host "Overall status: $overallStatus"

if ($Mode -eq "Validate" -and $overallStatus -eq "blocked" -and -not $NoExitOnBlocked) {
    exit 1
}
exit 0
