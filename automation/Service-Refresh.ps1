param(
  [Parameter(Mandatory = $true)][string]$ProjectPath,
  [string[]]$Services,
  [switch]$Build = $true,
  [switch]$ChangedOnly,
  [string]$BaseRef = "origin/main",
  [string]$MapPath = "automation/service-map.json",
  [string]$DockerCommand = "docker",
  [string]$ProjectsRoot,
  [string]$WorkbenchRepoPath,
  [string]$RuntimeHolder,
  [ValidateSet('full', 'core-manage')][string]$RuntimeMode = 'full',
  [string]$RefreshPlan,
  [string]$RefreshPlanDigest,
  [string[]]$ComposeFiles,
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
    if ($name -notmatch '^(LOTUS|DPM)_[A-Z0-9_]+$') {
      throw "Compose environment '$name' is outside the governed LOTUS_/DPM_ namespaces and cannot be governed by service refresh."
    }
    if ($name -match '(SECRET|TOKEN|PASSWORD|PASS|CREDENTIAL|PRIVATE_KEY|API_KEY)') {
      throw "Credential-bearing Compose environment '$name' cannot be governed by service refresh."
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
    [Parameter(Mandatory = $true)][string[]]$ServiceNames,
    [string[]]$ComposePrefix = @('compose')
  )

  $arguments = $ComposePrefix + @('ps', '--format', 'json') + $ServiceNames
  $stdoutPath = [IO.Path]::GetTempFileName()
  $stderrPath = [IO.Path]::GetTempFileName()
  try {
    & $Command @arguments 1> $stdoutPath 2> $stderrPath
    $exitCode = $LASTEXITCODE
    $output = @(Get-Content -LiteralPath $stdoutPath)
    $diagnostics = Get-Content -LiteralPath $stderrPath -Raw
    if ($null -eq $diagnostics) {
      $diagnostics = ""
    } else {
      $diagnostics = ([string]$diagnostics).Trim()
    }
  } finally {
    Remove-Item -LiteralPath $stdoutPath, $stderrPath -Force -ErrorAction SilentlyContinue
  }
  if ($null -eq $exitCode) {
    $exitCode = 0
  }
  if ($exitCode -ne 0) {
    $diagnosticSuffix = if ([string]::IsNullOrWhiteSpace($diagnostics)) { "" } else { "; stderr: $diagnostics" }
    throw "docker compose ps failed after service refresh (exit code $exitCode): $Command $($arguments -join ' ')$diagnosticSuffix"
  }
  if (-not [string]::IsNullOrWhiteSpace($diagnostics)) {
    [Console]::Error.WriteLine($diagnostics)
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
    [int]$PollIntervalSeconds,
    [string[]]$ComposePrefix = @('compose')
  )

  $deadline = [DateTimeOffset]::UtcNow.AddSeconds($TimeoutSeconds)
  do {
    $states = Get-ComposeServiceStates -Command $Command -ServiceNames $ServiceNames -ComposePrefix $ComposePrefix
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

function Assert-ReviewedRepositoryPath {
  param([string]$Path, [string]$RepoPath, [switch]$AllowRoot)
  $root = [IO.Path]::GetFullPath($RepoPath).TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
  $fullPath = [IO.Path]::GetFullPath($Path)
  $comparison = if ([Environment]::OSVersion.Platform -eq 'Win32NT') { [StringComparison]::OrdinalIgnoreCase } else { [StringComparison]::Ordinal }
  if (-not ($AllowRoot -and $fullPath.Equals($root, $comparison)) -and
      -not $fullPath.StartsWith($root + [IO.Path]::DirectorySeparatorChar, $comparison)) {
    throw 'Reserved input is outside its reviewed repository.'
  }
  $item = Get-Item -LiteralPath $fullPath -Force
  while ($item) {
    if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reserved input cannot redirect through a reparse point or ancestor.' }
    if ($item.FullName.Equals($root, $comparison)) { break }
    $item = if ($item -is [IO.DirectoryInfo]) { $item.Parent } else { $item.Directory }
  }
}

function Assert-ReservedComposeInputs {
  param([string]$Command, [string[]]$Prefix, $Operation, [object[]]$PlannedServices, [string]$RepoPath)
  # Evaluated Compose may include secrets; inspect in memory and suppress its error payload.
  $diagnostics = [IO.Path]::GetTempFileName()
  try {
    $configText = & $Command @Prefix config --format json 2> $diagnostics
    if ($LASTEXITCODE -ne 0) { throw 'Reserved Compose configuration inspection failed.' }
    $config = ($configText -join "`n") | ConvertFrom-Json
  } finally { Remove-Item -LiteralPath $diagnostics -Force -ErrorAction SilentlyContinue }
  if ($config.name -ne $PlannedServices[0].project) { throw 'Compose project differs from reviewed project.' }
  foreach ($planned in $PlannedServices) {
    $service = $config.services.($planned.service)
    if (-not $service -or -not $service.build -or $service.build.additional_contexts -or $service.build.dockerfile_inline) {
      throw 'Reserved build requires a local owned context and Dockerfile without additional contexts.'
    }
    $context = [IO.Path]::GetFullPath([string]$service.build.context)
    $dockerfile = if ($service.build.dockerfile) { [string]$service.build.dockerfile } else { 'Dockerfile' }
    if (-not [IO.Path]::IsPathRooted($dockerfile)) { $dockerfile = Join-Path $context $dockerfile }
    foreach ($path in @($context, [IO.Path]::GetFullPath($dockerfile))) {
      Assert-ReviewedRepositoryPath -Path $path -RepoPath $RepoPath -AllowRoot
    }
    $actualPorts = @($service.ports | ForEach-Object {
      if ([string]$_.published -notmatch '^[0-9]+$') { throw 'Reserved refresh requires bounded published ports.' }
      [int]$_.published
    } | Sort-Object -Unique)
    $resourceIds = @($Operation.OriginalResources | Where-Object { $_.project -eq $planned.project -and $_.service -eq $planned.service } | ForEach-Object { $_.id })
    $originalPorts = @($Operation.Bindings | Where-Object { $_.id -in $resourceIds } | ForEach-Object { $_.ports } | Sort-Object -Unique)
    if (($actualPorts -join ',') -ne ($originalPorts -join ',')) { throw 'Reserved Compose service publications differ from original bindings.' }
  }
  return $configText -join "`n"
}

function Resolve-ReviewedComposeFile {
  param([string]$File, [string]$RepoPath)
  $root = [IO.Path]::GetFullPath($RepoPath).TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
  $path = (Resolve-Path -LiteralPath $File).Path
  Assert-ReviewedRepositoryPath -Path $path -RepoPath $RepoPath
  $relative = $path.Substring($root.Length + 1).Replace('\', '/')
  & git -C $root ls-files --error-unmatch -- $relative *> $null
  if ($LASTEXITCODE -ne 0) { throw 'Reserved Compose files must be tracked reviewed inputs.' }
  & git -C $root diff --quiet HEAD -- $relative
  if ($LASTEXITCODE -ne 0) { throw 'Reserved Compose files must match the reviewed commit.' }
  return $path
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
$ProjectPath = (Resolve-Path -LiteralPath $ProjectPath).Path
if (-not $ProjectsRoot) { $ProjectsRoot = Split-Path -Parent $ProjectPath }
$bookPath = Join-Path $ProjectsRoot 'lotus-platform/output/canonical-runtime/reservations.v1.json'
$reservedRefresh = (Test-Path -LiteralPath $bookPath) -or $RefreshPlan -or $RuntimeHolder -or $RefreshPlanDigest
if ($reservedRefresh) {
  if (-not $RuntimeHolder -or -not $RefreshPlan -or -not $RefreshPlanDigest) {
    throw 'Canonical reservation requires RuntimeHolder, RefreshPlan and reviewed RefreshPlanDigest before service mutation.'
  }
  $RefreshPlan = (Resolve-Path -LiteralPath $RefreshPlan).Path
  $reviewedPlan = Get-Content -LiteralPath $RefreshPlan -Raw | ConvertFrom-Json
  $plannedServices = @($reviewedPlan.services)
  $repoName = [string]$repositoryConfig.name
  if ($plannedServices.Count -ne @($resolvedServices).Count -or
      @($plannedServices | Where-Object { $_.repository -ne $repoName -or $_.service -notin $resolvedServices }).Count -gt 0 -or
      @($plannedServices.project | Sort-Object -Unique).Count -ne 1) {
    throw 'This refresh must match exactly one reviewed repository/project and its complete service allowlist.'
  }
  if (-not $Build) { throw 'Reserved service refresh requires a fenced build before image replacement.' }
}
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

if ($DryRun -and -not $reservedRefresh) {
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
$operation = $null
$refreshOutcome = 'failure'
$temporaryFiles = @()
$snapshotRoot = $null
$composePrefix = @('compose')
try {
  if ($reservedRefresh) {
    Import-Module (Join-Path $PSScriptRoot 'CanonicalRuntimeReservation.psm1') -Force
    $operation = Enter-CanonicalRuntimeRefresh -ProjectsRoot $ProjectsRoot -Holder $RuntimeHolder `
      -WorkbenchRepoPath $WorkbenchRepoPath -RuntimeMode $RuntimeMode -RefreshPlan $RefreshPlan -RefreshPlanDigest $RefreshPlanDigest -Preview:$DryRun
    $reviewedPlan = $operation.RefreshPlan
    $plannedServices = @($reviewedPlan.services)
    if (@($plannedServices.service | Sort-Object -Unique).Count -ne @($resolvedServices).Count -or
        @($plannedServices | Where-Object { $_.repository -ne $repoName -or $_.service -notin $resolvedServices }).Count -gt 0 -or
        @($plannedServices.project | Sort-Object -Unique).Count -ne 1) {
      throw 'Admitted plan differs from the selected repository/project/services.'
    }
    # Compose receives only the reviewed project and explicit files. Unique image tags prevent
    # a build from moving the image tag of an untouched service in this project.
    $project = [string]$plannedServices[0].project
    $admittedCheckout = [IO.Path]::GetFullPath([string]$reviewedPlan.targetScope.projects.($project)).TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    $selectedCheckout = [IO.Path]::GetFullPath($ProjectPath).TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    $pathComparison = if ([Environment]::OSVersion.Platform -eq 'Win32NT') { [StringComparison]::OrdinalIgnoreCase } else { [StringComparison]::Ordinal }
    if (-not $selectedCheckout.Equals($admittedCheckout, $pathComparison)) {
      throw 'ProjectPath differs from the checkout admitted for the reviewed Compose project.'
    }
    $composePrefix += @('-p', $project)
    if (-not $ComposeFiles) {
      if ($env:COMPOSE_FILE) {
        $separator = if ($env:COMPOSE_PATH_SEPARATOR) { $env:COMPOSE_PATH_SEPARATOR } else { [IO.Path]::PathSeparator }
        $ComposeFiles = $env:COMPOSE_FILE -split [regex]::Escape([string]$separator)
      } else {
        $baseFile = @('compose.yaml', 'compose.yml', 'docker-compose.yml', 'docker-compose.yaml') |
          Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
        if (-not $baseFile) { throw 'No Compose file found; pass ComposeFiles explicitly.' }
        $ComposeFiles = @($baseFile)
        $overrideNames = if ($baseFile.StartsWith('docker-compose')) { @('docker-compose.override.yml', 'docker-compose.override.yaml') } else { @('compose.override.yaml', 'compose.override.yml') }
        $defaultOverride = $overrideNames | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
        if ($defaultOverride) { $ComposeFiles += $defaultOverride }
      }
    }
    foreach ($file in $ComposeFiles) { $composePrefix += @('-f', (Resolve-ReviewedComposeFile -File $file -RepoPath $ProjectPath)) }
    if (-not $DryRun) { Assert-CanonicalRuntimeRefresh -Operation $operation | Out-Null }
    $configText = Assert-ReservedComposeInputs -Command $DockerCommand -Prefix $composePrefix -Operation $operation -PlannedServices $plannedServices -RepoPath $ProjectPath
    $snapshotRoot = Join-Path ([IO.Path]::GetTempPath()) ('lotus-refresh-' + [guid]::NewGuid().ToString('N'))
    [void][IO.Directory]::CreateDirectory($snapshotRoot)
    $configPath = Join-Path $snapshotRoot 'evaluated.json'
    $emptyEnvironment = Join-Path $snapshotRoot 'empty.env'
    [IO.File]::WriteAllText($configPath, $configText)
    [IO.File]::WriteAllText($emptyEnvironment, '')
    & python (Join-Path $PSScriptRoot 'canonical_refresh_inputs.py') freeze --config $configPath --repo $ProjectPath `
      --revision $reviewedPlan.targetScope.sources.($repoName) --digest $reviewedPlan.composeConfigDigest `
      --output $snapshotRoot --services $resolvedServices 2> $null
    if ($LASTEXITCODE -ne 0) { throw 'Reviewed Compose digest or committed build snapshot validation failed.' }
    $composePrefix = @('compose', '--project-directory', $ProjectPath, '--env-file', $emptyEnvironment, '-p', $project, '-f', (Join-Path $snapshotRoot 'compose.json'))
    $overridePath = [IO.Path]::GetTempFileName()
    $referencesPath = [IO.Path]::GetTempFileName()
    $temporaryFiles += @($overridePath, $referencesPath)
    $overrideServices = [ordered]@{}
    $references = @()
    foreach ($service in $plannedServices) {
      if ($service.service -notmatch '^[a-zA-Z0-9][a-zA-Z0-9_.-]*$') { throw 'Invalid reviewed Compose service name.' }
      $tag = "lotus-reserved-refresh:$($operation.Token)-$($service.service)".ToLowerInvariant()
      $labels = [ordered]@{
        'org.opencontainers.image.revision' = $reviewedPlan.targetScope.sources.($service.repository)
        'org.opencontainers.image.source' = $service.repository
        'com.lotus.repository.checkout' = $reviewedPlan.targetScope.projects.($service.project)
      }
      $overrideServices[$service.service] = @{ image = $tag; build = @{ labels = $labels } }
      $references += @{ project = $project; service = $service.service; reference = $tag }
    }
    [IO.File]::WriteAllText($overridePath, (@{ services = $overrideServices } | ConvertTo-Json -Depth 12))
    [IO.File]::WriteAllText($referencesPath, (ConvertTo-Json -InputObject @($references) -Depth 5))
    $composePrefix += @('-f', $overridePath)
    if ($DryRun) {
      Write-Host "Dry run validated reviewed plan $RefreshPlanDigest; reservation unchanged."
      Write-Host "Dry run: $DockerCommand $($composePrefix -join ' ') build $($resolvedServices -join ' ')"
      Write-Host 'After build: verify source labels and pin each selected image to its observed immutable ID.'
      Write-Host "Dry run: $DockerCommand $($composePrefix -join ' ') up -d --no-deps --no-build --pull never $($resolvedServices -join ' ')"
      return
    }
    Invoke-CheckedNativeCommand -Command $DockerCommand -Arguments ($composePrefix + @('build') + $resolvedServices) `
      -FailureMessage 'Reserved build failed before service replacement'
    $prepared = Assert-CanonicalRuntimeRefresh -Operation $operation -PreparedImages $referencesPath
    foreach ($image in $prepared.operation.refresh.preparedImages) {
      $overrideServices[$image.service].image = $image.imageId
    }
    [IO.File]::WriteAllText($overridePath, (@{ services = $overrideServices } | ConvertTo-Json -Depth 12))
    Assert-CanonicalRuntimeRefresh -Operation $operation | Out-Null
    $composeArgs = $composePrefix + @('up', '-d', '--no-deps', '--no-build', '--pull', 'never') + $resolvedServices
  }
  Invoke-CheckedNativeCommand `
    -Command $DockerCommand `
    -Arguments $composeArgs `
    -FailureMessage "docker compose up failed; service refresh did not complete"
  Wait-ComposeServiceReadiness `
    -Command $DockerCommand `
    -ServiceNames $resolvedServices `
    -RepositoryConfig $repositoryConfig `
    -TimeoutSeconds $HealthTimeoutSeconds `
    -PollIntervalSeconds $HealthPollIntervalSeconds `
    -ComposePrefix $composePrefix
  $refreshOutcome = 'success'
} finally {
  try {
    if ($operation) { Exit-CanonicalRuntimeOperation -Operation $operation -Outcome $refreshOutcome }
  } finally {
    foreach ($file in $temporaryFiles) { Remove-Item -LiteralPath $file -Force -ErrorAction SilentlyContinue }
    if ($snapshotRoot) {
      $resolvedSnapshot = [IO.Path]::GetFullPath($snapshotRoot)
      $tempPrefix = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar + 'lotus-refresh-'
      if (-not $resolvedSnapshot.StartsWith($tempPrefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'Unexpected refresh snapshot cleanup path.' }
      Remove-Item -LiteralPath $resolvedSnapshot -Recurse -Force -ErrorAction SilentlyContinue
    }
    Pop-Location
    foreach ($name in $composeEnvironment.Keys) {
      [Environment]::SetEnvironmentVariable($name, $originalEnvironment[$name], 'Process')
    }
  }
}

