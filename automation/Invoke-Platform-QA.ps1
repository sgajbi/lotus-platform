param(
  [string]$Repo = "all",
  [string]$ReposPath = "automation/repos.json",
  [string]$QaMatrixPath = "automation/qa-matrix.json",
  [string]$OutputDir = "output/qa",
  [switch]$BringUp,
  [switch]$KeepRunning,
  [switch]$CreateIssues,
  [switch]$DryRun,
  [switch]$SkipStandardsValidators,
  [int]$HttpTimeoutSeconds = 20
)

$ErrorActionPreference = "Stop"
if (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
  $PSNativeCommandUseErrorActionPreference = $false
}

function Invoke-CommandCapture {
  param(
    [string]$RepoPath,
    [string]$Command
  )

  if ([string]::IsNullOrWhiteSpace($Command)) {
    return [pscustomobject]@{ exitCode = 0; output = "" }
  }

  if ($DryRun) {
    return [pscustomobject]@{ exitCode = 0; output = "[dry-run] $Command" }
  }

  $tmpOut = [System.IO.Path]::GetTempFileName()
  $tmpErr = [System.IO.Path]::GetTempFileName()
  try {
    $proc = Start-Process -FilePath "cmd.exe" `
      -ArgumentList "/c", $Command `
      -WorkingDirectory $RepoPath `
      -NoNewWindow `
      -Wait `
      -PassThru `
      -RedirectStandardOutput $tmpOut `
      -RedirectStandardError $tmpErr

    $stdout = if (Test-Path $tmpOut) { Get-Content -Raw $tmpOut } else { "" }
    $stderr = if (Test-Path $tmpErr) { Get-Content -Raw $tmpErr } else { "" }
    $combined = (($stdout + "`n" + $stderr).Trim())
    return [pscustomobject]@{ exitCode = [int]$proc.ExitCode; output = $combined }
  } finally {
    Remove-Item $tmpOut,$tmpErr -ErrorAction SilentlyContinue
  }
}

function Invoke-HttpCheck {
  param(
    [string]$Method,
    [string]$Url,
    [hashtable]$Headers,
    [string]$Body,
    [int]$TimeoutSec
  )

  if ($DryRun) {
    return [pscustomobject]@{
      status = 200
      body = "[dry-run] $Method $Url"
      headers = @{}
      error = $null
    }
  }

  try {
    $params = @{
      Uri = $Url
      Method = $Method
      Headers = $Headers
      TimeoutSec = $TimeoutSec
      UseBasicParsing = $true
    }
    if (-not [string]::IsNullOrWhiteSpace($Body)) {
      $params["Body"] = $Body
      $params["ContentType"] = "application/json"
    }

    $response = Invoke-WebRequest @params
    $respHeaders = @{}
    foreach ($k in $response.Headers.Keys) {
      $respHeaders[($k.ToString().ToLowerInvariant())] = [string]$response.Headers[$k]
    }

    return [pscustomobject]@{
      status = [int]$response.StatusCode
      body = [string]$response.Content
      headers = $respHeaders
      error = $null
    }
  } catch {
    $status = 0
    $body = $_.Exception.Message
    $respHeaders = @{}
    if ($_.Exception.Response) {
      try {
        $status = [int]$_.Exception.Response.StatusCode.value__
      } catch {
      }
    }
    return [pscustomobject]@{
      status = $status
      body = $body
      headers = $respHeaders
      error = $_.ToString()
    }
  }
}

function New-Recommendation {
  param([string]$Type)

  switch ($Type) {
    "startup" { return "Add a docker-compose smoke test that validates container health and startup dependencies." }
    "api" { return "Add contract tests for endpoint status/body schema and required headers under tests/integration." }
    "docs" { return "Add an OpenAPI docs availability check in CI and include docs endpoint references in README." }
    "metrics" { return "Add monitoring tests to assert /metrics exposure and key metric names." }
    "logs" { return "Add log-structure tests asserting correlation/tracing keys and structured log payloads." }
    "standards" { return "Add a CI task invoking the corresponding lotus-platform validator and fail on non-ok status." }
    "lineage" { return "Add integration tests and documentation checks for lineage/traceability endpoints and metadata." }
    "error" { return "Add tests asserting problem-details and structured error payloads for invalid requests and exceptions." }
    "custom" { return "Promote this custom validation into a stable QA gate and keep its evidence payload versioned." }
    default { return "Add automated regression coverage for this check in unit/integration CI gates." }
  }
}

function New-TestGap {
  param([string]$Type)

  switch ($Type) {
    "startup" { return "Current test suite validates code behavior but does not validate runtime startup behavior in compose." }
    "api" { return "Existing tests likely do not assert this endpoint behavior in a running environment." }
    "docs" { return "Existing tests do not verify live docs endpoint reachability." }
    "metrics" { return "Current tests do not enforce observability endpoint and metric surface contracts." }
    "logs" { return "Logging assertions are missing or do not validate runtime correlation/tracing fields." }
    "standards" { return "Validator result is not enforced as a merge-blocking gate for this repository state." }
    "lineage" { return "Lineage/traceability checks are not currently exercised in automated regression tests." }
    "error" { return "Error-handling behavior is not fully validated against platform problem-details conventions." }
    "custom" { return "This scenario is not yet enforced by the default platform QA matrix or CI quality gates." }
    default { return "Coverage for this behavior is missing in current automated tests." }
  }
}

function Add-Finding {
  param(
    [System.Collections.Generic.List[object]]$Findings,
    [string]$Repo,
    [string]$CheckId,
    [string]$Type,
    [string]$Expected,
    [string]$Actual,
    [string]$Evidence,
    [string[]]$Steps
  )

  $Findings.Add([pscustomobject]@{
    repo = $Repo
    check_id = $CheckId
    type = $Type
    expected = $Expected
    actual = $Actual
    evidence = $Evidence
    reproducible_steps = $Steps
    why_not_caught = New-TestGap -Type $Type
    recommended_coverage = New-Recommendation -Type $Type
  })
}

function Get-AvailableGitHubLabels {
  param([string]$GitHubRepo)

  if ($DryRun) {
    return @("qa","platform-conformance")
  }

  try {
    $raw = & gh label list --repo $GitHubRepo --limit 200 --json name 2>$null
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($raw)) {
      return @()
    }
    $parsed = $raw | ConvertFrom-Json
    $names = @()
    foreach ($row in $parsed) { $names += [string]$row.name }
    return $names
  } catch {
    return @()
  }
}

function New-GitHubIssue {
  param(
    [string]$GitHubRepo,
    [string]$Title,
    [string]$BodyFile,
    [string[]]$RequestedLabels
  )

  $available = Get-AvailableGitHubLabels -GitHubRepo $GitHubRepo
  $labelsToUse = @()
  foreach ($label in $RequestedLabels) {
    if ($available -contains $label) { $labelsToUse += $label }
  }

  $args = @("issue","create","--repo",$GitHubRepo,"--title",$Title,"--body-file",$BodyFile)
  foreach ($label in $labelsToUse) {
    $args += @("--label",$label)
  }

  $result = & gh @args 2>&1
  return [pscustomobject]@{
    success = ($LASTEXITCODE -eq 0)
    labels = $labelsToUse
    response = (($result | Out-String).Trim())
  }
}

function Get-IssueByExactTitle {
  param(
    [string]$GitHubRepo,
    [string]$Title
  )

  if ($DryRun) {
    return $null
  }

  try {
    $json = & gh issue list --repo $GitHubRepo --state all --limit 200 --json title,url,number,state 2>$null
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($json)) {
      return $null
    }
    $rows = $json | ConvertFrom-Json
    foreach ($row in $rows) {
      if ([string]$row.title -eq $Title) {
        return $row
      }
    }
    return $null
  } catch {
    return $null
  }
}

function Wait-ForServiceReady {
  param(
    [string]$Url,
    [int]$ExpectedStatus = 200,
    [int]$TimeoutSeconds = 60
  )

  if ($DryRun -or [string]::IsNullOrWhiteSpace($Url)) {
    return $true
  }

  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  while ((Get-Date) -lt $deadline) {
    $probe = Invoke-HttpCheck -Method "GET" -Url $Url -Headers @{} -Body "" -TimeoutSec 5
    if ([int]$probe.status -eq [int]$ExpectedStatus) {
      return $true
    }
    Start-Sleep -Seconds 2
  }
  return $false
}

function Get-StandardsSnapshot {
  param([string]$PlatformRepoPath)

  $snapshot = [ordered]@{
    backend = @{}
    openapi = @{}
    durability = @{}
    enterprise = @{}
    platformContract = @{}
    rounding = @{}
  }

  if ($SkipStandardsValidators -or $DryRun) {
    return $snapshot
  }

  Push-Location $PlatformRepoPath
  try {
    & powershell -ExecutionPolicy Bypass -File "automation/Validate-Backend-Standards.ps1" | Out-Null
    & powershell -ExecutionPolicy Bypass -File "automation/Validate-OpenAPI-Conformance.ps1" | Out-Null
    & powershell -ExecutionPolicy Bypass -File "automation/Validate-Durability-Consistency.ps1" | Out-Null
    & powershell -ExecutionPolicy Bypass -File "automation/Validate-Enterprise-Readiness.ps1" | Out-Null
    & powershell -ExecutionPolicy Bypass -File "automation/Validate-Rounding-Consistency.ps1" | Out-Null
    & powershell -ExecutionPolicy Bypass -File "automation/Validate-Platform-Contract.ps1" | Out-Null

    $backendJson = Get-Content -Raw "output/backend-standards-conformance.json" | ConvertFrom-Json
    foreach ($row in $backendJson.results) { $snapshot.backend[$row.repo] = $row }

    $openapiJson = Get-Content -Raw "output/openapi-conformance-summary.json" | ConvertFrom-Json
    foreach ($row in $openapiJson.results) { $snapshot.openapi[$row.repo] = $row }

    $durabilityJson = Get-Content -Raw "output/durability-consistency-compliance.json" | ConvertFrom-Json
    foreach ($row in $durabilityJson.rows) {
      if (-not $snapshot.durability.Contains($row.repo)) { $snapshot.durability[$row.repo] = @() }
      $snapshot.durability[$row.repo] += $row
    }

    $enterpriseJson = Get-Content -Raw "output/enterprise-readiness-compliance.json" | ConvertFrom-Json
    foreach ($row in $enterpriseJson.rows) {
      if (-not $snapshot.enterprise.Contains($row.repo)) { $snapshot.enterprise[$row.repo] = @() }
      $snapshot.enterprise[$row.repo] += $row
    }

    $roundingJson = Get-Content -Raw "output/rounding-consistency-report.json" | ConvertFrom-Json
    $snapshot.rounding["_root"] = $roundingJson

    $contractLines = Get-Content "output/platform-contract-validation.md"
    foreach ($line in $contractLines) {
      if ($line -match "^\|\s*(lotus-[^|]+)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|") {
        $repoName = $Matches[1].Trim()
        $snapshot.platformContract[$repoName] = [pscustomobject]@{
          health = $Matches[2].Trim()
          metrics = $Matches[3].Trim()
          correlation = $Matches[4].Trim()
          tracing = $Matches[5].Trim()
        }
      }
    }
  } finally {
    Pop-Location
  }

  return $snapshot
}

if (-not (Test-Path $ReposPath)) { throw "Repos config not found: $ReposPath" }
if (-not (Test-Path $QaMatrixPath)) { throw "QA matrix not found: $QaMatrixPath" }

$reposConfig = Get-Content -Raw $ReposPath | ConvertFrom-Json
$qaConfig = Get-Content -Raw $QaMatrixPath | ConvertFrom-Json
$repoMap = @{}
foreach ($r in $reposConfig) { $repoMap[$r.name] = $r }

$selected = if ($Repo -eq "all") {
  @($qaConfig.repositories)
} else {
  $targets = $Repo.Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ }
  @($qaConfig.repositories | Where-Object { $targets -contains $_.repo })
}

if ($selected.Count -eq 0) {
  throw "No QA targets selected."
}

if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null }
$runId = Get-Date -Format "yyyyMMdd-HHmmss"
$runDir = Join-Path $OutputDir $runId
$evidenceDir = Join-Path $runDir "evidence"
New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null

$platformRepoPath = "C:/Users/Sandeep/projects/lotus-platform"
$standards = Get-StandardsSnapshot -PlatformRepoPath $platformRepoPath
$findings = New-Object 'System.Collections.Generic.List[object]'
$issueRecords = New-Object 'System.Collections.Generic.List[object]'
$repoResults = New-Object 'System.Collections.Generic.List[object]'

foreach ($entry in $selected) {
  $repoName = [string]$entry.repo
  if (-not $repoMap.ContainsKey($repoName)) {
    Add-Finding -Findings $findings -Repo $repoName -CheckId "repo-registration" -Type "standards" -Expected "Repo registered in automation/repos.json" -Actual "Missing repo entry" -Evidence "Repo not found in repos config." -Steps @("Add $repoName into automation/repos.json and rerun QA.")
    continue
  }

  $repoInfo = $repoMap[$repoName]
  $repoPath = [string]$repoInfo.path
  $githubRepo = [string]$repoInfo.github

  $startupOutput = ""
  $logOutput = ""
  $headersChecked = @{}

  if ($BringUp) {
    $startResult = Invoke-CommandCapture -RepoPath $repoPath -Command ([string]$entry.startup.up_command)
    $startupOutput = $startResult.output
    if ($startResult.exitCode -ne 0) {
      Add-Finding -Findings $findings -Repo $repoName -CheckId "startup" -Type "startup" -Expected "Startup command exits 0" -Actual "Startup command failed with exit code $($startResult.exitCode)" -Evidence $startupOutput -Steps @("cd $repoPath", ([string]$entry.startup.up_command))
    } elseif ($entry.checks.api -and $entry.checks.api.Count -gt 0) {
      $readyUrl = [string]$entry.checks.api[0].url
      $readyStatus = [int]$entry.checks.api[0].expected_status
      $ready = Wait-ForServiceReady -Url $readyUrl -ExpectedStatus $readyStatus -TimeoutSeconds 60
      if (-not $ready) {
        Add-Finding -Findings $findings -Repo $repoName -CheckId "startup-readiness" -Type "startup" -Expected "Service ready at $readyUrl with HTTP $readyStatus within timeout" -Actual "Service did not become ready within timeout" -Evidence $startupOutput -Steps @("cd $repoPath", ([string]$entry.startup.up_command), "Probe readiness URL: $readyUrl")
      }
    }
  }

  foreach ($check in $entry.checks.api) {
    $correlationId = [guid]::NewGuid().ToString()
    $traceparent = "00-" + (([guid]::NewGuid().ToString("N") + [guid]::NewGuid().ToString("N")).Substring(0,32)) + "-" + ([guid]::NewGuid().ToString("N").Substring(0,16)) + "-01"
    $headers = @{
      "x-correlation-id" = $correlationId
      "traceparent" = $traceparent
      "x-actor-id" = "qa-automation"
      "x-tenant-id" = "qa"
      "x-role" = "qa"
      "x-service-identity" = "platform-qa"
      "accept" = "application/json"
    }
    $result = Invoke-HttpCheck -Method ([string]$check.method) -Url ([string]$check.url) -Headers $headers -Body ([string]$check.body) -TimeoutSec $HttpTimeoutSeconds

    $headersChecked[[string]$check.id] = $result.headers

    if ([int]$result.status -ne [int]$check.expected_status) {
      Add-Finding -Findings $findings -Repo $repoName -CheckId ([string]$check.id) -Type "api" -Expected "HTTP $($check.expected_status) from $($check.url)" -Actual "HTTP $($result.status) from $($check.url)" -Evidence $result.body -Steps @("Bring up service", "Invoke endpoint: $($check.method) $($check.url)")
      continue
    }

    if ($check.must_contain) {
      foreach ($needle in $check.must_contain) {
        if (($result.body -as [string]) -notmatch [regex]::Escape([string]$needle)) {
          Add-Finding -Findings $findings -Repo $repoName -CheckId ([string]$check.id) -Type "api" -Expected "Response contains '$needle'" -Actual "Response missing '$needle'" -Evidence $result.body -Steps @("Invoke endpoint: $($check.method) $($check.url)")
        }
      }
    }

    if ($entry.checks.observability.require_response_headers) {
      foreach ($requiredHeader in $entry.checks.observability.require_response_headers) {
        $h = [string]$requiredHeader
        if (-not $result.headers.ContainsKey($h.ToLowerInvariant())) {
          Add-Finding -Findings $findings -Repo $repoName -CheckId ([string]$check.id + "-header-" + $h) -Type "logs" -Expected "Response header '$h' present" -Actual "Header '$h' missing" -Evidence ($result.body | Select-Object -First 1) -Steps @("Invoke endpoint: $($check.method) $($check.url)", "Inspect response headers")
        }
      }
    }
  }

  foreach ($mcheck in $entry.checks.monitoring) {
    $result = Invoke-HttpCheck -Method "GET" -Url ([string]$mcheck.url) -Headers @{} -Body "" -TimeoutSec $HttpTimeoutSeconds
    if ([int]$result.status -ne [int]$mcheck.expected_status) {
      Add-Finding -Findings $findings -Repo $repoName -CheckId ([string]$mcheck.id) -Type "metrics" -Expected "HTTP $($mcheck.expected_status) from $($mcheck.url)" -Actual "HTTP $($result.status)" -Evidence $result.body -Steps @("Bring up service", "GET $($mcheck.url)")
      continue
    }

    if ($mcheck.must_contain) {
      foreach ($needle in $mcheck.must_contain) {
        if (($result.body -as [string]) -notmatch [regex]::Escape([string]$needle)) {
          Add-Finding -Findings $findings -Repo $repoName -CheckId ([string]$mcheck.id) -Type "metrics" -Expected "Metrics body contains '$needle'" -Actual "Metrics body missing '$needle'" -Evidence $result.body -Steps @("GET $($mcheck.url)")
        }
      }
    }
  }

  if ($entry.checks.custom_checks) {
    foreach ($customCheck in $entry.checks.custom_checks) {
      if ([string]$customCheck.type -ne "command") {
        Add-Finding -Findings $findings -Repo $repoName -CheckId ([string]$customCheck.id) -Type "custom" -Expected "Supported custom check type" -Actual "Unsupported type '$([string]$customCheck.type)'" -Evidence ($customCheck | ConvertTo-Json -Depth 5) -Steps @("Review automation/qa-matrix.json for the custom check definition.")
        continue
      }

      $customResult = Invoke-CommandCapture -RepoPath $platformRepoPath -Command ([string]$customCheck.command)
      $expectedExitCode = if ($null -ne $customCheck.expected_exit_code) {
        [int]$customCheck.expected_exit_code
      } else {
        0
      }

      if ([int]$customResult.exitCode -ne $expectedExitCode) {
        Add-Finding -Findings $findings -Repo $repoName -CheckId ([string]$customCheck.id) -Type "custom" -Expected "Exit code $expectedExitCode from custom check" -Actual "Exit code $($customResult.exitCode)" -Evidence $customResult.output -Steps @("cd $platformRepoPath", ([string]$customCheck.command))
      }
    }
  }

  if ($entry.startup.log_command) {
    $logResult = Invoke-CommandCapture -RepoPath $repoPath -Command ([string]$entry.startup.log_command)
    $logOutput = $logResult.output
    foreach ($pattern in $entry.checks.observability.required_log_patterns) {
      if (($logOutput -as [string]) -notmatch [string]$pattern) {
        Add-Finding -Findings $findings -Repo $repoName -CheckId ("logs-pattern-" + [string]$pattern) -Type "logs" -Expected "Log output matches pattern '$pattern'" -Actual "Pattern '$pattern' not found in logs" -Evidence $logOutput -Steps @("cd $repoPath", ([string]$entry.startup.log_command))
      }
    }
  }

  $errorScanTargets = @()
  foreach ($candidate in @((Join-Path $repoPath "src"), (Join-Path $repoPath "app"))) {
    if (Test-Path $candidate) { $errorScanTargets += $candidate }
  }
  $errorHandlingHits = if ($errorScanTargets.Count -gt 0) {
    & rg -n -i "application/problem\+json|problem details|exception_handler|HTTPException|payload_too_large" $errorScanTargets 2>$null
  } else {
    $null
  }
  if (-not $errorHandlingHits) {
    Add-Finding -Findings $findings -Repo $repoName -CheckId "error-handling" -Type "error" -Expected "Repository has explicit problem/error handling patterns" -Actual "No platform-style error handling evidence found" -Evidence "No matches for expected error-handling patterns." -Steps @('rg -n -i "application/problem\+json|exception_handler|HTTPException" <repo>/src <repo>/app')
  }

  $lineageDoc = Join-Path $repoPath "docs/standards/data-model-ownership.md"
  $lineageScanTargets = @()
  foreach ($candidate in @((Join-Path $repoPath "docs"), (Join-Path $repoPath "src"), (Join-Path $repoPath "app"))) {
    if (Test-Path $candidate) { $lineageScanTargets += $candidate }
  }
  $lineageHits = if ($lineageScanTargets.Count -gt 0) {
    & rg -n -i "lineage|traceability|source system|audit trail|correlation" $lineageScanTargets 2>$null
  } else {
    $null
  }
  if (-not (Test-Path $lineageDoc) -or -not $lineageHits) {
    Add-Finding -Findings $findings -Repo $repoName -CheckId "lineage-traceability" -Type "lineage" -Expected "Data lineage and traceability evidence in docs/code" -Actual "Missing lineage evidence in docs/code checks" -Evidence "data-model-ownership exists=$([bool](Test-Path $lineageDoc)); matches=$([bool]$lineageHits)" -Steps @("Check docs/standards/data-model-ownership.md", "Add lineage/traceability references and endpoint/test coverage")
  }

  if ($standards.backend.Contains($repoName)) {
    $row = $standards.backend[$repoName]
    if ($row.status -ne "ok") {
      Add-Finding -Findings $findings -Repo $repoName -CheckId "standards-backend" -Type "standards" -Expected "Backend standards status = ok" -Actual "Backend standards status = $($row.status); missing=$($row.missing -join ', ')" -Evidence ($row | ConvertTo-Json -Depth 5) -Steps @("Run powershell -ExecutionPolicy Bypass -File automation/Validate-Backend-Standards.ps1")
    }
  }

  if ($standards.openapi.Contains($repoName)) {
    $row = $standards.openapi[$repoName]
    if ($row.status -ne "ok") {
      Add-Finding -Findings $findings -Repo $repoName -CheckId "standards-openapi" -Type "standards" -Expected "OpenAPI conformance status = ok" -Actual "OpenAPI status = $($row.status); missing=$($row.missing -join ', ')" -Evidence ($row | ConvertTo-Json -Depth 5) -Steps @("Run powershell -ExecutionPolicy Bypass -File automation/Validate-OpenAPI-Conformance.ps1")
    }
  }

  if ($standards.durability.Contains($repoName)) {
    $gaps = @($standards.durability[$repoName] | Where-Object { $_.status -ne "Implemented" })
    if ($gaps.Count -gt 0) {
      Add-Finding -Findings $findings -Repo $repoName -CheckId "standards-durability" -Type "standards" -Expected "All durability requirements implemented" -Actual "$($gaps.Count) durability requirements not implemented" -Evidence ($gaps | ConvertTo-Json -Depth 5) -Steps @("Run powershell -ExecutionPolicy Bypass -File automation/Validate-Durability-Consistency.ps1")
    }
  }

  if ($standards.enterprise.Contains($repoName)) {
    $gaps = @($standards.enterprise[$repoName] | Where-Object { $_.status -ne "Implemented" })
    if ($gaps.Count -gt 0) {
      Add-Finding -Findings $findings -Repo $repoName -CheckId "standards-enterprise" -Type "standards" -Expected "All enterprise readiness requirements implemented" -Actual "$($gaps.Count) enterprise requirements not implemented" -Evidence ($gaps | ConvertTo-Json -Depth 5) -Steps @("Run powershell -ExecutionPolicy Bypass -File automation/Validate-Enterprise-Readiness.ps1")
    }
  }

  if ($standards.platformContract.Contains($repoName)) {
    $row = $standards.platformContract[$repoName]
    $bad = @()
    if ($row.health -ne "ok") { $bad += "health" }
    if ($row.metrics -ne "ok") { $bad += "metrics" }
    if ($row.correlation -ne "ok") { $bad += "correlation" }
    if ($row.tracing -ne "ok") { $bad += "tracing" }
    if ($bad.Count -gt 0) {
      Add-Finding -Findings $findings -Repo $repoName -CheckId "standards-platform-contract" -Type "standards" -Expected "Platform contract health/metrics/correlation/tracing are all ok" -Actual "Platform contract gaps: $($bad -join ', ')" -Evidence ($row | ConvertTo-Json -Depth 3) -Steps @("Run powershell -ExecutionPolicy Bypass -File automation/Validate-Platform-Contract.ps1")
    }
  }

  $repoFindings = @($findings | Where-Object { $_.repo -eq $repoName })
  $repoResults.Add([pscustomobject]@{
    repo = $repoName
    github = $githubRepo
    findings = $repoFindings.Count
    startup_attempted = [bool]$BringUp
  })

  if ($CreateIssues -and -not $DryRun -and $repoFindings.Count -gt 0) {
    $repoEvidenceDir = Join-Path $evidenceDir $repoName
    New-Item -ItemType Directory -Path $repoEvidenceDir -Force | Out-Null

    $index = 0
    foreach ($finding in $repoFindings) {
      $index += 1
      $evidencePath = Join-Path $repoEvidenceDir ("finding-{0:000}-{1}.md" -f $index, $finding.check_id.Replace("/","-").Replace(" ","-"))
      $body = @()
      $body += "# QA Defect Evidence"
      $body += ""
      $body += "- Repo: $repoName"
      $body += "- Check: $($finding.check_id)"
      $body += "- Type: $($finding.type)"
      $body += "- Run ID: $runId"
      $body += ""
      $body += "## Repro Steps"
      foreach ($step in $finding.reproducible_steps) { $body += "1. $step" }
      $body += ""
      $body += "## Expected"
      $body += $finding.expected
      $body += ""
      $body += "## Actual"
      $body += $finding.actual
      $body += ""
      $body += "## Evidence"
      $body += '```text'
      $body += ([string]$finding.evidence)
      $body += '```'
      $body += ""
      $body += "## Screenshots"
      $body += "- N/A for API-only automation checks."
      $body | Set-Content -Path $evidencePath

      $issueTitle = "[QA][automation] $repoName :: $($finding.check_id)"
      $issueText = @()
      $issueText += "Automated platform-level QA detected a standards/readiness defect."
      $issueText += ""
      $issueText += "Expected: $($finding.expected)"
      $issueText += ""
      $issueText += "Actual: $($finding.actual)"
      $issueText += ""
      $issueText += "Reproducible steps:"
      foreach ($step in $finding.reproducible_steps) { $issueText += "- $step" }
      $issueText += ""
      $issueText += "Why existing tests did not catch this: $($finding.why_not_caught)"
      $issueText += ""
      $issueText += "Recommended coverage to prevent regression: $($finding.recommended_coverage)"
      $issueText += ""
      $issueText += "Evidence file: $evidencePath"
      $issueText += "Run ID: $runId"

      $tmpBody = Join-Path $repoEvidenceDir ("issue-{0:000}.md" -f $index)
      $issueText | Set-Content -Path $tmpBody

      $existing = Get-IssueByExactTitle -GitHubRepo $githubRepo -Title $issueTitle
      if ($null -ne $existing) {
        $action = "existing"
        if ([string]$existing.state -eq "CLOSED") {
          $null = & gh issue reopen ([string]$existing.number) --repo $githubRepo 2>$null
          $action = if ($LASTEXITCODE -eq 0) { "reopened" } else { "existing-closed" }
        }
        $issueRecords.Add([pscustomobject]@{
          repo = $repoName
          check_id = $finding.check_id
          issue_action = $action
          issue_success = $true
          labels_used = ""
          issue_response = [string]$existing.url
        })
      } else {
        $issueResult = New-GitHubIssue -GitHubRepo $githubRepo -Title $issueTitle -BodyFile $tmpBody -RequestedLabels @("qa","platform-conformance")
        $issueRecords.Add([pscustomobject]@{
          repo = $repoName
          check_id = $finding.check_id
          issue_action = "created"
          issue_success = [bool]$issueResult.success
          labels_used = ($issueResult.labels -join ",")
          issue_response = [string]$issueResult.response
        })
      }
    }
  }

  if ($BringUp -and -not $KeepRunning) {
    $null = Invoke-CommandCapture -RepoPath $repoPath -Command ([string]$entry.startup.down_command)
  }
}

$targetRepos = @()
foreach ($s in $selected) { $targetRepos += [string]$s.repo }

$summaryMap = [ordered]@{}
$summaryMap["generated_at"] = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
$summaryMap["run_id"] = $runId
$summaryMap["bring_up"] = [bool]$BringUp
$summaryMap["create_issues"] = [bool]$CreateIssues
$summaryMap["dry_run"] = [bool]$DryRun
$summaryMap["targets"] = $targetRepos
$summaryMap["repo_results"] = $repoResults.ToArray()
$summaryMap["finding_count"] = [int]$findings.Count
$summaryMap["findings"] = $findings.ToArray()
$summaryMap["issues"] = $issueRecords.ToArray()
$summary = [pscustomobject]$summaryMap

$jsonPath = Join-Path $runDir "qa-summary.json"
$mdPath = Join-Path $runDir "qa-summary.md"
$issuePath = Join-Path $runDir "qa-issues.json"

$summary | ConvertTo-Json -Depth 8 | Set-Content -Path $jsonPath
$issuesPayload = @($summary.issues)
if ($issuesPayload.Count -eq 0) {
  "[]" | Set-Content -Path $issuePath
} else {
  $issuesPayload | ConvertTo-Json -Depth 6 | Set-Content -Path $issuePath
}

$md = @()
$md += "# Platform QA Summary"
$md += ""
$md += "- Generated: $($summary.generated_at)"
$md += "- Run ID: $($summary.run_id)"
$md += "- Targets: $($summary.targets -join ', ')"
$md += "- Bring up services: $($summary.bring_up)"
$md += "- Create GitHub issues: $($summary.create_issues)"
$md += "- Total findings: $($summary.finding_count)"
$md += ""
$md += "| Repo | Findings |"
$md += "|---|---:|"
foreach ($row in $summary.repo_results) {
  $md += "| $($row.repo) | $($row.findings) |"
}
$md += ""
$md += "## Findings"
$md += ""
foreach ($f in $summary.findings) {
  $md += "### $($f.repo) :: $($f.check_id)"
  $md += "- Type: $($f.type)"
  $md += "- Expected: $($f.expected)"
  $md += "- Actual: $($f.actual)"
  $md += "- Why not caught: $($f.why_not_caught)"
  $md += "- Recommended coverage: $($f.recommended_coverage)"
  $md += ""
}

$md | Set-Content -Path $mdPath

Write-Host "Wrote $jsonPath"
Write-Host "Wrote $mdPath"
Write-Host "Wrote $issuePath"

if ((-not $DryRun) -and $summary.finding_count -gt 0) {
  exit 2
}
