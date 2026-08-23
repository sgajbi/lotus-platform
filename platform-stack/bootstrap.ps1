[CmdletBinding()]
param(
    [string]$WorkspaceRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$stackRoot = $PSScriptRoot
$envPath = Join-Path $stackRoot ".env"
$templatePath = Join-Path $stackRoot ".env.example"
$resolvedWorkspaceRoot = if ([string]::IsNullOrWhiteSpace($WorkspaceRoot)) {
    [System.IO.Path]::GetFullPath((Join-Path $stackRoot "..\.."))
} else {
    [System.IO.Path]::GetFullPath($WorkspaceRoot)
}
$resolvedWorkspaceRoot = $resolvedWorkspaceRoot.Replace("\", "/").TrimEnd("/")

if (-not (Test-Path -LiteralPath $envPath)) {
    Copy-Item -LiteralPath $templatePath -Destination $envPath
}

function New-RandomSecret {
    $bytes = [byte[]]::new(32)
    [System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
    return [Convert]::ToHexString($bytes).ToLowerInvariant()
}

function Set-EnvironmentValueIfEmpty {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Value
    )

    $lines = [System.Collections.Generic.List[string]](Get-Content -LiteralPath $envPath)
    $prefix = "$Name="
    $found = $false
    for ($index = 0; $index -lt $lines.Count; $index += 1) {
        if (-not $lines[$index].StartsWith($prefix, [System.StringComparison]::Ordinal)) {
            continue
        }
        $found = $true
        if ([string]::IsNullOrWhiteSpace($lines[$index].Substring($prefix.Length))) {
            $lines[$index] = "$prefix$Value"
            Write-Host "Generated $Name"
        }
        break
    }
    if (-not $found) {
        $lines.Add("$prefix$Value")
        Write-Host "Generated $Name"
    }
    [System.IO.File]::WriteAllLines($envPath, $lines, [System.Text.UTF8Encoding]::new($false))
}

Set-EnvironmentValueIfEmpty -Name "LOTUS_WORKSPACE_ROOT" -Value $resolvedWorkspaceRoot
$repositoryPaths = [ordered]@{
    LOTUS_MANAGE_REPO_PATH = "lotus-manage"
    LOTUS_CORE_REPO_PATH = "lotus-core"
    LOTUS_PERFORMANCE_REPO_PATH = "lotus-performance"
    LOTUS_REPORT_REPO_PATH = "lotus-report"
    LOTUS_IDEA_REPO_PATH = "lotus-idea"
    LOTUS_GATEWAY_REPO_PATH = "lotus-gateway"
    LOTUS_WORKBENCH_REPO_PATH = "lotus-workbench"
}
foreach ($entry in $repositoryPaths.GetEnumerator()) {
    Set-EnvironmentValueIfEmpty -Name $entry.Key -Value "$resolvedWorkspaceRoot/$($entry.Value)"
}
foreach ($secretName in @(
    "LOTUS_CORE_POSTGRES_PASSWORD",
    "LOTUS_MANAGE_POSTGRES_PASSWORD",
    "LOTUS_REPORT_POSTGRES_PASSWORD",
    "GRAFANA_ADMIN_PASSWORD"
)) {
    Set-EnvironmentValueIfEmpty -Name $secretName -Value (New-RandomSecret)
}

Write-Host "Platform stack environment is ready at $envPath"
