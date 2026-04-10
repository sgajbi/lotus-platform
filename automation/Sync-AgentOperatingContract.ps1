param(
    [string]$SourcePath = (Join-Path $PSScriptRoot "..\context\AGENTS-OPERATING-CONTRACT.md"),
    [string]$TargetPath = "C:\Users\Sandeep\.codex\AGENTS.md",
    [switch]$CheckOnly
)

function Normalize-ContractContent {
    param([string]$Content)

    return ($Content -replace "`r`n", "`n").TrimEnd("`n", "`r")
}

$resolvedSource = (Resolve-Path $SourcePath).ProviderPath
$sourceContent = Get-Content -Raw $resolvedSource
$normalizedSourceContent = Normalize-ContractContent $sourceContent

if ($CheckOnly) {
    if (-not (Test-Path $TargetPath)) {
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
