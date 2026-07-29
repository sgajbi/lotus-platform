param(
  [Parameter(Mandatory = $true)][string]$ProjectPath,
  [string[]]$Services,
  [switch]$Build = $true,
  [switch]$ChangedOnly,
  [string]$BaseRef = "origin/main",
  [string]$MapPath = "automation/service-map.json",
  [string]$DockerCommand = "docker",
  [switch]$IncludeUncommitted = $true,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Get-ChangedFiles {
  param(
    [string]$RepoPath,
    [string]$DiffBaseRef,
    [bool]$AddUncommitted
  )

  $files = New-Object System.Collections.Generic.HashSet[string]

  $diffSpec = "$DiffBaseRef...HEAD"
  $trackedChanges = git -C $RepoPath diff --name-only $diffSpec
  foreach ($file in $trackedChanges) {
    if (-not [string]::IsNullOrWhiteSpace($file)) {
      [void]$files.Add($file.Trim())
    }
  }

  if ($AddUncommitted) {
    $statusLines = git -C $RepoPath status --porcelain
    foreach ($line in $statusLines) {
      if ([string]::IsNullOrWhiteSpace($line) -or $line.Length -lt 4) {
        continue
      }
      $pathPart = $line.Substring(3).Trim()
      if ($pathPart -like "* -> *") {
        $pathPart = ($pathPart -split " -> ")[-1]
      }
      if (-not [string]::IsNullOrWhiteSpace($pathPart)) {
        [void]$files.Add($pathPart)
      }
    }
  }

  return @($files)
}

function Resolve-ServicesFromChangeMap {
  param(
    [string]$RepoPath,
    [string[]]$ChangedFiles,
    [string]$ChangeMapPath
  )

  if (-not (Test-Path $ChangeMapPath)) {
    throw "Change map not found: $ChangeMapPath"
  }

  $repoName = Split-Path -Leaf $RepoPath
  $map = Get-Content $ChangeMapPath | ConvertFrom-Json
  $repoConfig = $map.repos | Where-Object {
    $_.name -eq $repoName -or ($_.pathHint -and $RepoPath.Replace('\', '/').ToLower().EndsWith($_.pathHint.ToLower()))
  } | Select-Object -First 1

  if (-not $repoConfig) {
    throw "No service map entry found for repo '$repoName' in $ChangeMapPath"
  }

  $serviceSet = New-Object System.Collections.Generic.HashSet[string]
  foreach ($file in $ChangedFiles) {
    $normalized = $file.Replace('\', '/')
    foreach ($rule in $repoConfig.rules) {
      $matched = $false
      foreach ($prefix in $rule.pathPrefixes) {
        if ($normalized.StartsWith($prefix)) {
          $matched = $true
          break
        }
      }
      if ($matched) {
        foreach ($svc in $rule.services) {
          [void]$serviceSet.Add($svc)
        }
      }
    }
  }

  if ($serviceSet.Count -eq 0 -and $repoConfig.defaultServices) {
    foreach ($svc in $repoConfig.defaultServices) {
      [void]$serviceSet.Add($svc)
    }
  }

  return @($serviceSet)
}

function Invoke-CheckedNativeCommand {
  param(
    [Parameter(Mandatory = $true)][string]$Command,
    [Parameter(Mandatory = $true)][string[]]$Arguments,
    [Parameter(Mandatory = $true)][string]$FailureMessage
  )

  & $Command @Arguments
  $exitCode = $LASTEXITCODE
  if ($null -eq $exitCode) {
    $exitCode = 0
  }
  if ($exitCode -ne 0) {
    throw "$FailureMessage (exit code $exitCode): $Command $($Arguments -join ' ')"
  }
}

if (-not (Test-Path $ProjectPath)) {
  throw "Project path not found: $ProjectPath"
}

$resolvedServices = @()
if ($Services -and $Services.Count -gt 0) {
  $resolvedServices = $Services
} elseif ($ChangedOnly) {
  $changedFiles = Get-ChangedFiles -RepoPath $ProjectPath -DiffBaseRef $BaseRef -AddUncommitted $IncludeUncommitted
  if (-not $changedFiles -or $changedFiles.Count -eq 0) {
    Write-Host "No changed files found relative to $BaseRef. Nothing to refresh."
    exit 0
  }

  Write-Host "Changed files detected ($($changedFiles.Count)):"
  $changedFiles | Sort-Object | ForEach-Object { Write-Host " - $_" }

  $resolvedServices = Resolve-ServicesFromChangeMap -RepoPath $ProjectPath -ChangedFiles $changedFiles -ChangeMapPath $MapPath
  if (-not $resolvedServices -or $resolvedServices.Count -eq 0) {
    throw "Could not resolve services from changed files. Pass -Services explicitly."
  }
} else {
  throw "Provide -Services or use -ChangedOnly."
}

$resolvedServices = $resolvedServices | Sort-Object -Unique
Write-Host "Refreshing services: $($resolvedServices -join ', ')"

$composeArgs = @("compose", "up", "-d")
if ($Build) {
  $composeArgs += "--build"
}
$composeArgs += $resolvedServices

if ($DryRun) {
  Write-Host "Dry run: $DockerCommand $($composeArgs -join ' ')"
  exit 0
}

Push-Location $ProjectPath
try {
  Invoke-CheckedNativeCommand `
    -Command $DockerCommand `
    -Arguments $composeArgs `
    -FailureMessage "docker compose up failed; service refresh did not complete"
  Invoke-CheckedNativeCommand `
    -Command $DockerCommand `
    -Arguments @("compose", "ps") `
    -FailureMessage "docker compose ps failed after service refresh"
} finally {
  Pop-Location
}

