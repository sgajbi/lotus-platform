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
    $generator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $generator.GetBytes($bytes)
    } finally {
        $generator.Dispose()
    }
    return -join ($bytes | ForEach-Object { $_.ToString("x2") })
}

function Assert-NoLegacySecretDefault {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$LegacyValue
    )

    $prefix = "$Name="
    $configuredValue = Get-Content -LiteralPath $envPath |
        Where-Object { $_.StartsWith($prefix, [System.StringComparison]::Ordinal) } |
        Select-Object -Last 1 |
        ForEach-Object { $_.Substring($prefix.Length) }
    if ($configuredValue -ceq $LegacyValue) {
        throw "Refusing the legacy tracked default for $Name. Clear it only when initializing a fresh database, or replace it with an operator-managed secret after following the documented database migration path."
    }
}

function Assert-UriSafeDatabaseComponent {
    param(
        [Parameter(Mandatory = $true)][string]$Name
    )

    $prefix = "$Name="
    $configuredValue = Get-Content -LiteralPath $envPath |
        Where-Object { $_.StartsWith($prefix, [System.StringComparison]::Ordinal) } |
        Select-Object -Last 1 |
        ForEach-Object { $_.Substring($prefix.Length) }
    if (
        -not [string]::IsNullOrWhiteSpace($configuredValue) -and
        $configuredValue -cnotmatch '^[A-Za-z0-9._~-]+$'
    ) {
        throw "$Name contains characters that are unsafe in the platform stack PostgreSQL URI. Use only letters, numbers, dot, underscore, tilde, and hyphen."
    }
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

Assert-NoLegacySecretDefault -Name "LOTUS_CORE_POSTGRES_PASSWORD" -LegacyValue "password"
foreach ($databaseComponentName in @(
    "LOTUS_CORE_POSTGRES_USER",
    "LOTUS_CORE_POSTGRES_PASSWORD",
    "LOTUS_CORE_POSTGRES_DB",
    "LOTUS_MANAGE_POSTGRES_USER",
    "LOTUS_MANAGE_POSTGRES_PASSWORD",
    "LOTUS_MANAGE_POSTGRES_DB",
    "LOTUS_REPORT_POSTGRES_USER",
    "LOTUS_REPORT_POSTGRES_PASSWORD",
    "LOTUS_REPORT_POSTGRES_DB"
)) {
    Assert-UriSafeDatabaseComponent -Name $databaseComponentName
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
