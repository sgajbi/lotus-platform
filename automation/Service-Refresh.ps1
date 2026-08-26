param(
  [Parameter(Mandatory = $true)][string]$ProjectPath,
  [string[]]$Services,
  [switch]$Build = $true,
  [switch]$ChangedOnly,
  [string]$BaseRef = "origin/main",
  [string]$MapPath = "automation/service-map.json",
  [string]$DockerCommand = "docker",
  [switch]$IncludeUncommitted = $true,
  [ValidateRange(0, 600)][int]$HealthTimeoutSeconds = 60,
  [ValidateRange(1, 30)][int]$HealthPollIntervalSeconds = 2,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

trap {
  $message = if ($_.Exception -and -not [string]::IsNullOrWhiteSpace($_.Exception.Message)) {
    $_.Exception.Message
  } else {
    [string]$_
  }
  [Console]::Error.WriteLine($message)
  exit 1
}

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

function Resolve-RepositoryConfig {
  param(
    [string]$RepoPath,
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

  return $repoConfig
}

function Resolve-ServicesFromChangeMap {
  param(
    [object]$RepositoryConfig,
    [string[]]$ChangedFiles
  )

  $serviceSet = New-Object System.Collections.Generic.HashSet[string]
  foreach ($file in $ChangedFiles) {
    $normalized = $file.Replace('\', '/')
    foreach ($rule in $RepositoryConfig.rules) {
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

  if ($serviceSet.Count -eq 0 -and $RepositoryConfig.defaultServices) {
    foreach ($svc in $RepositoryConfig.defaultServices) {
      [void]$serviceSet.Add($svc)
    }
  }

  return @($serviceSet)
}

function Resolve-GovernedComposeEnvironment {
  param([object]$RepositoryConfig)

  $resolved = [ordered]@{}
  if (-not $RepositoryConfig.composeEnvironment) {
    return $resolved
  }

  foreach ($property in $RepositoryConfig.composeEnvironment.PSObject.Properties) {
    $name = [string]$property.Name
    $value = $property.Value
    if ($name -notmatch '^[A-Z][A-Z0-9_]*$') {
      throw "Unsafe Compose environment name '$name' in service map."
    }
    if ($name -notmatch '^(LOTUS|DPM)_[A-Z0-9_]+$') {
      throw "Compose environment '$name' is outside the governed LOTUS_/DPM_ namespaces and cannot be governed by service refresh."
    }
    if ($value -isnot [string] -or [string]::IsNullOrWhiteSpace([string]$value)) {
      throw "Compose environment '$name' must have a non-empty string value."
    }
    $resolved[$name] = [string]$value
  }

  return $resolved
}

function Get-ServiceVerification {
  param(
    [object]$RepositoryConfig,
    [string]$Service
  )

  if (-not $RepositoryConfig.serviceVerification) {
    return $null
  }
  return $RepositoryConfig.serviceVerification.PSObject.Properties |
    Where-Object { $_.Name -eq $Service } |
    Select-Object -ExpandProperty Value -First 1
}

function Get-ComposeServiceStates {
  param(
    [Parameter(Mandatory = $true)][string]$Command,
    [Parameter(Mandatory = $true)][string[]]$ServiceNames
  )

  $arguments = @('compose', 'ps', '--format', 'json') + $ServiceNames
  $output = @(& $Command @arguments 2>&1)
  $exitCode = $LASTEXITCODE
  if ($null -eq $exitCode) {
    $exitCode = 0
  }
  if ($exitCode -ne 0) {
    throw "docker compose ps failed after service refresh (exit code $exitCode): $Command $($arguments -join ' ')"
  }

  $states = @()
  foreach ($line in $output) {
    $json = [string]$line
    if ([string]::IsNullOrWhiteSpace($json)) {
      continue
    }
    try {
      $states += @($json | ConvertFrom-Json)
    } catch {
      throw "docker compose ps returned invalid JSON service state: $json"
    }
  }
  return @($states)
}

function Get-ServiceReadinessFailures {
  param(
    [object[]]$States,
    [string[]]$ServiceNames,
    [object]$RepositoryConfig
  )

  $failures = New-Object System.Collections.Generic.List[string]
  foreach ($service in $ServiceNames) {
    $state = $States | Where-Object { $_.Service -eq $service } | Select-Object -First 1
    if (-not $state) {
      $failures.Add("$service is absent from docker compose ps")
      continue
    }
    if ([string]$state.State -ne 'running') {
      $failures.Add("$service state is '$($state.State)' instead of 'running'")
      continue
    }

    $verification = Get-ServiceVerification -RepositoryConfig $RepositoryConfig -Service $service
    $requiresHealthy = [bool]($verification -and $verification.requireHealthy)
    $reportedHealth = [string]$state.Health
    if (($requiresHealthy -or -not [string]::IsNullOrWhiteSpace($reportedHealth)) -and $reportedHealth -ne 'healthy') {
      $failures.Add("$service health is '$reportedHealth' instead of 'healthy'")
    }

    $expectedPorts = if ($verification -and $verification.publishedPorts) {
      @($verification.publishedPorts)
    } else {
      @()
    }
    foreach ($expectedPort in $expectedPorts) {
      $portFound = @($state.Publishers) | Where-Object {
        [int]$_.TargetPort -eq [int]$expectedPort.target -and
        [int]$_.PublishedPort -eq [int]$expectedPort.published
      } | Select-Object -First 1
      if (-not $portFound) {
        $failures.Add("$service does not publish required port $($expectedPort.published):$($expectedPort.target)")
      }
    }
  }
  return @($failures)
}

function Wait-ComposeServiceReadiness {
  param(
    [Parameter(Mandatory = $true)][string]$Command,
    [Parameter(Mandatory = $true)][string[]]$ServiceNames,
    [Parameter(Mandatory = $true)][object]$RepositoryConfig,
    [int]$TimeoutSeconds,
    [int]$PollIntervalSeconds
  )

  $deadline = [DateTimeOffset]::UtcNow.AddSeconds($TimeoutSeconds)
  do {
    $states = Get-ComposeServiceStates -Command $Command -ServiceNames $ServiceNames
    $failures = @(Get-ServiceReadinessFailures -States $states -ServiceNames $ServiceNames -RepositoryConfig $RepositoryConfig)
    if ($failures.Count -eq 0) {
      Write-Host "Verified service readiness: $($ServiceNames -join ', ')"
      return
    }
    if ([DateTimeOffset]::UtcNow -ge $deadline) {
      throw "Service refresh readiness verification failed: $($failures -join '; ')"
    }
    Start-Sleep -Seconds $PollIntervalSeconds
  } while ($true)
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

$platformRoot = Split-Path -Parent $PSScriptRoot
if (-not [System.IO.Path]::IsPathRooted($MapPath)) {
  $MapPath = Join-Path $platformRoot $MapPath
}
$repositoryConfig = Resolve-RepositoryConfig -RepoPath $ProjectPath -ChangeMapPath $MapPath
$composeEnvironment = Resolve-GovernedComposeEnvironment -RepositoryConfig $repositoryConfig

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

  $resolvedServices = Resolve-ServicesFromChangeMap -RepositoryConfig $repositoryConfig -ChangedFiles $changedFiles
  if (-not $resolvedServices -or $resolvedServices.Count -eq 0) {
    throw "Could not resolve services from changed files. Pass -Services explicitly."
  }
} else {
  throw "Provide -Services or use -ChangedOnly."
}

$resolvedServices = $resolvedServices | Sort-Object -Unique
Write-Host "Refreshing services: $($resolvedServices -join ', ')"
if ($composeEnvironment.Count -gt 0) {
  Write-Host "Governed Compose environment:"
  foreach ($name in @($composeEnvironment.Keys | Sort-Object)) {
    Write-Host " - $name=$($composeEnvironment[$name])"
  }
}

$composeArgs = @("compose", "up", "-d")
if ($Build) {
  $composeArgs += "--build"
}
$composeArgs += $resolvedServices

if ($DryRun) {
  Write-Host "Dry run: $DockerCommand $($composeArgs -join ' ')"
  foreach ($service in $resolvedServices) {
    $verification = Get-ServiceVerification -RepositoryConfig $repositoryConfig -Service $service
    $expectedPorts = if ($verification -and $verification.publishedPorts) {
      @($verification.publishedPorts)
    } else {
      @()
    }
    foreach ($expectedPort in $expectedPorts) {
      Write-Host "Expected published port: $service $($expectedPort.published):$($expectedPort.target)"
    }
  }
  exit 0
}

$originalEnvironment = [ordered]@{}
foreach ($name in $composeEnvironment.Keys) {
  $originalEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
  [Environment]::SetEnvironmentVariable($name, $composeEnvironment[$name], 'Process')
}

Push-Location $ProjectPath
try {
  Invoke-CheckedNativeCommand `
    -Command $DockerCommand `
    -Arguments $composeArgs `
    -FailureMessage "docker compose up failed; service refresh did not complete"
  Wait-ComposeServiceReadiness `
    -Command $DockerCommand `
    -ServiceNames $resolvedServices `
    -RepositoryConfig $repositoryConfig `
    -TimeoutSeconds $HealthTimeoutSeconds `
    -PollIntervalSeconds $HealthPollIntervalSeconds
} finally {
  Pop-Location
  foreach ($name in $composeEnvironment.Keys) {
    [Environment]::SetEnvironmentVariable($name, $originalEnvironment[$name], 'Process')
  }
}

