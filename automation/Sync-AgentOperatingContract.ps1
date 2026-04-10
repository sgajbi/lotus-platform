param(
    [string]$SourcePath = (Join-Path $PSScriptRoot "..\context\AGENTS-OPERATING-CONTRACT.md"),
    [string]$TargetPath = "",
    [switch]$CheckOnly
)

function Normalize-ContractContent {
    param([string]$Content)

    return ($Content -replace "`r`n", "`n").TrimEnd("`n", "`r")
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

if (-not $TargetPath) {
    $TargetPath = Resolve-DefaultTargetPath
}

$resolvedSource = (Resolve-Path $SourcePath).ProviderPath
$sourceContent = Get-Content -Raw $resolvedSource
$normalizedSourceContent = Normalize-ContractContent $sourceContent

if ($CheckOnly) {
    if (-not (Test-Path $TargetPath)) {
        if ($env:GITHUB_ACTIONS -eq "true") {
            Write-Host "Agent operating contract check skipped because deployed AGENTS target is not present on this GitHub runner: $TargetPath"
            exit 0
        }
        throw "Target AGENTS file not found: $TargetPath"
    }

    $targetContent = Get-Content -Raw $TargetPath
    $normalizedTargetContent = Normalize-ContractContent $targetContent
    if ($normalizedTargetContent -ne $normalizedSourceContent) {
        throw "Target AGENTS file is not synchronized with the governed source."
    }

    Write-Host "Agent operating contract is synchronized."
    exit 0
}

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($TargetPath, $normalizedSourceContent + "`n", $utf8NoBom)
Write-Host "Synchronized AGENTS operating contract to $TargetPath"
