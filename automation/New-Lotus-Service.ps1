param(
  [Parameter(Mandatory = $true)]
  [string]$ServiceName,
  [string]$Description = "Lotus backend service",
  [string]$DestinationRoot = "C:/Users/Sandeep/projects",
  [string]$GithubOrg = "sgajbi",
  [int]$Port = 8000,
  [string]$BusinessRole = "",
  [string]$Category = "domain-service",
  [string]$ServiceProfile = "",
  [string]$PrimaryRuntime = "python-fastapi",
  [string[]]$UpstreamDependencies = @(),
  [string[]]$DownstreamDependencies = @(),
  [string]$DevHostName = "",
  [string[]]$RequiredLogPatterns = @("correlation", "trace", "service"),
  [switch]$IncludeMeshPlaceholders,
  [switch]$Force,
  [switch]$SkipAutomationRegistration,
  [switch]$InitializeGit,
  [switch]$CreateGithubRepo,
  [ValidateSet("private", "public")]
  [string]$GithubVisibility = "private",
  [switch]$ApplyMainBranchProtection,
  [switch]$EnableGithubDefaults
)

$ErrorActionPreference = "Stop"

if ($ServiceName -notmatch "^lotus-[a-z0-9-]+$") {
  throw "ServiceName must follow lotus-* naming (example: lotus-risk)."
}

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptRoot "..")
$templateRoot = Join-Path $repoRoot "platform-standards/templates"
$target = Join-Path $DestinationRoot $ServiceName

if (-not $BusinessRole) {
  $BusinessRole = $Description
}

$validServiceProfiles = @(
  "domain-service",
  "experience-api",
  "shared-capability-service",
  "client-facing-service"
)

if (-not $ServiceProfile) {
  $ServiceProfile = $Category
}

if ($validServiceProfiles -notcontains $ServiceProfile) {
  throw "ServiceProfile must be one of: $($validServiceProfiles -join ', ')."
}

$Category = $ServiceProfile

function Test-WriteCapableServiceProfile {
  param([string]$Profile)

  return @("domain-service", "client-facing-service") -contains $Profile
}

function Get-ServiceProfileDescription {
  param([string]$Profile)

  switch ($Profile) {
    "domain-service" {
      return "Domain-authoritative backend service. Keep business rules in domain/application modules and expose explicit source-owned APIs."
    }
    "experience-api" {
      return "Experience API or composition service. Keep client contracts stable while avoiding drift into domain-owned business logic."
    }
    "shared-capability-service" {
      return "Shared capability service. Keep provider, document, archive, AI, or platform capability boundaries explicit and consumer-aware."
    }
    "client-facing-service" {
      return "Client-facing backend surface. Treat product-safe errors, permissions, auditability, and demo claims as first-class controls."
    }
    default {
      return "Lotus backend service profile."
    }
  }
}

function Normalize-ScaffoldStringList {
  param([string[]]$Values)

  $normalized = New-Object System.Collections.Generic.List[string]
  foreach ($value in $Values) {
    if ([string]::IsNullOrWhiteSpace($value)) {
      continue
    }
    foreach ($item in ($value -split ",")) {
      $trimmed = $item.Trim()
      if (-not [string]::IsNullOrWhiteSpace($trimmed) -and -not $normalized.Contains($trimmed)) {
        $normalized.Add($trimmed) | Out-Null
      }
    }
  }
  return @($normalized.ToArray())
}

$UpstreamDependencies = Normalize-ScaffoldStringList -Values $UpstreamDependencies
$DownstreamDependencies = Normalize-ScaffoldStringList -Values $DownstreamDependencies
$RequiredLogPatterns = Normalize-ScaffoldStringList -Values $RequiredLogPatterns

function Sync-AgentOperatingContract {
  param(
    [string]$PlatformRoot,
    [string]$TargetRepoRoot
  )

  $source = Join-Path $PlatformRoot "context/AGENTS-OPERATING-CONTRACT.md"
  $targetPath = Join-Path $TargetRepoRoot "AGENTS.md"
  $content = Get-Content -Raw $source
  $normalized = ($content -replace "`r`n", "`n").TrimEnd("`n", "`r")
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($targetPath, $normalized + "`n", $utf8NoBom)
}

function Write-RepositoryEngineeringContext {
  param(
    [string]$TargetRepoRoot,
    [string]$SvcName,
    [string]$SvcDescription,
    [string]$SvcBusinessRole,
    [string]$SvcCategory,
    [string]$SvcRuntime,
    [string[]]$SvcUpstreamDependencies,
    [string[]]$SvcDownstreamDependencies
  )

  $profileDescription = Get-ServiceProfileDescription -Profile $SvcCategory

  $upstreamText = if ($SvcUpstreamDependencies.Count -gt 0) {
    ($SvcUpstreamDependencies | ForEach-Object { "   - $_" }) -join "`n"
  }
  else {
    "   - none yet"
  }

  $downstreamText = if ($SvcDownstreamDependencies.Count -gt 0) {
    ($SvcDownstreamDependencies | ForEach-Object { "   - $_" }) -join "`n"
  }
  else {
    "   - none yet"
  }

  $context = @(
    '# Repository Engineering Context',
    '',
    '## Repository Role',
    '',
    ('`' + $SvcName + '` is a Lotus backend service.'),
    '',
    ('Service profile: `' + $SvcCategory + '`'),
    '',
    $profileDescription,
    '',
    '## Business And Domain Responsibility',
    '',
    ('`' + $SvcName + '` owns: ' + $SvcBusinessRole),
    '',
    '## Current-State Summary',
    '',
    ('`' + $SvcName + '` is scaffolded from platform automation and starts with the governed backend baseline:'),
    'FastAPI service shell, CI workflows, repo-native quality commands, Docker baseline, AGENTS',
    'contract, and repository engineering context.',
    '',
    '## Architecture And Module Map',
    '',
    '1. `src/app/main.py`: application entrypoint, health/readiness, metadata.',
    '2. `src/app/api/`: route modules and API DTO mapping.',
    '3. `src/app/application/`: use-case orchestration and application services.',
    '4. `src/app/domain/`: framework-free domain models, policies, and calculations.',
    '5. `src/app/ports/`: external capability interfaces used by application logic.',
    '6. `src/app/infrastructure/`: concrete adapters and external clients behind ports.',
    '7. `src/app/observability/`: structured logging, route-template request diagnostics, correlation, tracing, and metrics helpers.',
    '8. `src/app/security/`: caller context and product-safe authorization policies.',
    '9. `src/app/resilience/`: retry, backoff, timeout, and circuit-breaker policy primitives.',
    '10. `src/app/contracts/`: API and contract models.',
    '11. `src/app/middleware/`: shared request middleware.',
    '12. `tests/unit`, `tests/integration`, `tests/e2e`: test pyramid baseline.',
    '13. `docs/standards/`: repository standards placeholders to be replaced with service truth.',
    '',
    '## Runtime And Integration Boundaries',
    '',
    ('1. Runtime model: `' + $SvcRuntime + '`'),
    '2. Upstream dependencies:',
    $upstreamText,
    '3. Downstream consumers:',
    $downstreamText,
    '4. Important boundary rule: this scaffold does not establish domain authority beyond the explicit',
    '   service contract added later by RFC or implementation work.',
    '',
    '## Repo-Native Commands',
    '',
    '1. install or bootstrap: `make install`',
    '2. lint: `make lint`',
    '3. typecheck: `make typecheck`',
    '4. unit tests: `make test-unit`',
    '5. integration or browser tests where applicable: `make test-integration`, `make test-e2e`',
    '6. repo-native CI parity: `make check`, `make ci`',
    '7. CI lane contract gate: `make ci-contract-gate`',
    '8. maintainability gate: `make maintainability-gate`',
    '9. documentation contract gate: `make documentation-contract-gate`',
    '10. quality scorecard gate: `make quality-scorecard-gate`',
    '11. source-observability contract gate: `make source-observability-contract-gate`',
    '12. implementation-truth gate: `make implementation-truth-gate`',
    '',
    '## Validation And CI Expectations',
    '',
    ('`' + $SvcName + '` follows the standard Lotus backend lane model. Required baseline checks include lint,'),
    'typecheck, maintainability thresholds, documentation contract enforcement, quality-scorecard truth, source-observability contract enforcement, OpenAPI quality, implementation-truth gate,',
    'unit/integration/e2e tests, coverage gate, security audit, and Docker build validation.',
    '`make ci-contract-gate` is blocking through `make lint` and prevents future scaffold or agent',
    'changes from silently removing architecture, maintainability, OpenAPI, endpoint-certification,',
    'supported-feature, source-observability, implementation-truth, coverage, security, Docker, release-evidence, action-version,',
    'least-privilege workflow controls, workflow-dispatch access, or merged-PR main-releasability',
    'dispatch.',
    '`make maintainability-gate` prevents oversized source, test, and script files/functions from',
    'becoming normal scaffold output or future agentic implementation drift.',
    '`make documentation-contract-gate` keeps README, repository context, standards, runbooks,',
    'quality, evidence, and wiki surfaces present, substantive, and anchored to validation commands.',
    '`make quality-scorecard-gate` keeps the bank-buyable control matrix aligned with implementation truth.',
    '`make source-observability-contract-gate` blocks raw print, direct Python logging, and',
    'low-level log_event bypasses outside the central observability module.',
    '`make implementation-truth-gate` keeps current-state README, operations, demo, quality, and wiki text',
    'from claiming demo readiness, production support, certification, live source ingestion,',
    'Gateway/Workbench support, or client-ready publication before supported-feature evidence exists.',
    'It also blocks stale scaffold-era demo underclaims after implementation evidence exists.',
    'The scaffold also starts with a bank-buyable quality scorecard under `quality/`; update it when',
    'architecture, API, security, observability, test, CI, or documentation posture changes.',
    '',
    '## Standards And RFCs That Govern This Repository',
    '',
    '1. `lotus-platform/rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`',
    '2. `lotus-platform/context/LOTUS-QUICKSTART-CONTEXT.md`',
    '3. `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`',
    '4. `lotus-platform/platform-standards/LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md`',
    '5. service-specific RFCs once implementation begins',
    '',
    '## Known Constraints And Implementation Notes',
    '',
    '1. this is the platform scaffold baseline, not business-logic completeness,',
    '2. standards placeholders in `docs/standards/` must be replaced with service truth as the service',
    '   matures,',
    '3. keep business role, naming, docs, and tests aligned with actual implemented scope.',
    '',
    '## Context Maintenance Rule',
    '',
    'Update this document when:',
    '',
    '1. repository ownership changes,',
    '2. repo-native commands or CI gates change,',
    '3. runtime or integration boundaries change,',
    '4. dominant local implementation patterns change,',
    '5. current-state rollout or product posture materially changes.',
    '',
    '## Cross-Links',
    '',
    '1. `lotus-platform/context/LOTUS-QUICKSTART-CONTEXT.md`',
    '2. `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`',
    '3. `lotus-platform/context/CONTEXT-REFERENCE-MAP.md`'
  ) -join "`n"

  Set-Content -Path (Join-Path $TargetRepoRoot "REPOSITORY-ENGINEERING-CONTEXT.md") -Value $context
}

function Write-WikiBaseline {
  param(
    [string]$TargetRepoRoot,
    [string]$SvcName,
    [string]$SvcDescription,
    [string]$SvcProfile
  )

  $profileDescription = Get-ServiceProfileDescription -Profile $SvcProfile
  $wikiRoot = Join-Path $TargetRepoRoot "wiki"
  New-Item -ItemType Directory -Force -Path $wikiRoot | Out-Null
  $wikiPages = @{
    "_Sidebar.md" = @(
      "* [Home](Home.md)",
      "* [Overview](Overview.md)",
      "* [Architecture](Architecture.md)",
      "* [Getting Started](Getting-Started.md)",
      "* [Development Workflow](Development-Workflow.md)",
      "* [Validation And CI](Validation-And-CI.md)",
      "* [Operations Runbook](Operations-Runbook.md)",
      "* [Security And Governance](Security-And-Governance.md)",
      "* [Integrations](Integrations.md)",
      "* [Roadmap](Roadmap.md)",
      "* [Supported Features](Supported-Features.md)"
    ) -join "`n";
    "Home.md" = @(
      "# $SvcName Wiki",
      "",
      $SvcDescription,
      "",
      "Service profile: ``$SvcProfile``",
      "",
      $profileDescription,
      "",
      "## Start Here",
      "",
      "1. [Overview](Overview.md)",
      "2. [Getting Started](Getting-Started.md)",
      "3. [Development Workflow](Development-Workflow.md)",
      "4. [Validation And CI](Validation-And-CI.md)",
      "5. [Architecture](Architecture.md)",
      "6. [Operations Runbook](Operations-Runbook.md)",
      "7. [Security And Governance](Security-And-Governance.md)",
      "8. [Integrations](Integrations.md)",
      "9. [Roadmap](Roadmap.md)",
      "10. [Supported Features](Supported-Features.md)",
      "",
      "## Current Posture",
      "",
      "- repo scaffolded from Lotus platform automation",
      "- wiki source lives in-repo and must be published through `lotus-platform` automation",
      "- bank-buyable quality scorecard starts under `quality/` and must move with implementation truth",
      "- replace scaffold wording with operator-facing truth as implementation becomes real",
      "- demo claims must stay Planned until code, tests, endpoint certification, and evidence exist"
    ) -join "`n";
    "Overview.md" = @(
      "# Overview",
      "",
      $SvcDescription,
      "",
      "Current support is scaffold-only. Business capabilities remain Planned until implementation, endpoint certification, supported-feature registration, and validation evidence exist.",
      "",
      "Service profile: ``$SvcProfile``",
      "",
      "Use the README for quick commands and the repository engineering context for service ownership, boundaries, and validation posture."
    ) -join "`n";
    "Architecture.md" = @(
      "# Architecture",
      "",
      "The scaffold starts with the standard Lotus backend layering:",
      "",
      "1. `src/app/api` for route and DTO boundaries.",
      "2. `src/app/application` for use-case orchestration.",
      "3. `src/app/domain` for framework-free business rules.",
      "4. `src/app/ports` for inbound and outbound interfaces.",
      "5. `src/app/infrastructure` for adapters.",
      "6. `src/app/observability`, `src/app/security`, and `src/app/resilience` for cross-cutting production controls.",
      "",
      "Replace this scaffold overview with service-specific architecture decisions before promoting any product capability."
    ) -join "`n";
    "Getting-Started.md" = @(
      "# Getting Started",
      "",
      "Use the repo-native commands from the README:",
      "",
      '```powershell',
      "make install",
      "make check",
      "make ci",
      '```',
      "",
      "The scaffold exposes health, liveness, readiness, metrics, and service metadata endpoints only. Do not treat business behavior as supported until a later implementation slice adds code, tests, docs, supported-feature truth, and evidence."
    ) -join "`n";
    "Development-Workflow.md" = @(
      "# Development Workflow",
      "",
      "Follow Lotus delivery governance:",
      "",
      "1. start from current `main`,",
      "2. run stranded-truth reconciliation for RFC/docs/wiki/context/contract changes,",
      "3. keep commits small and meaningful,",
      "4. update tests, docs, supported features, and wiki source with implementation truth,",
      "5. keep durable docs passing `make documentation-contract-gate`,",
      "6. keep the bank-buyable control matrix passing `make quality-scorecard-gate`,",
      "7. keep source observability passing `make source-observability-contract-gate`,",
      "8. keep current-state docs passing `make implementation-truth-gate`,",
      "9. use rebase-only PR completion,",
      "10. delete completed local and remote feature branches after merge."
    ) -join "`n";
    "Validation-And-CI.md" = @(
      "# Validation And CI",
      "",
      "Generated repositories start with the Lotus backend lane model:",
      "",
      "1. Feature Lane for fast branch feedback.",
      "2. PR Merge Gate for merge readiness.",
      "3. Main Releasability Gate for post-merge truth.",
      "4. Merged PR Main Releasability Dispatch so rebase auto-merged PRs still generate release evidence on `main`.",
      "",
      "Repo-native commands:",
      "",
      '```powershell',
      "make check",
      "make ci",
      "make ci-contract-gate",
      "make maintainability-gate",
      "make documentation-contract-gate",
      "make quality-scorecard-gate",
      "make source-observability-contract-gate",
      "make implementation-truth-gate",
      "make openapi-gate",
      "make quality-baseline",
      '```',
      "",
      "Keep CI warnings actionable. Do not downgrade current action versions to hide runner noise."
    ) -join "`n";
    "Operations-Runbook.md" = @(
      "# Operations Runbook",
      "",
      "Current posture: scaffold operations only.",
      "",
      "Operators may use health, liveness, readiness, metrics, OpenAPI, Docker build validation, and service metadata as baseline checks. Service-specific degraded states and escalation paths must be added with implementation-backed behavior.",
      "",
      "Baseline first checks:",
      "",
      "1. run `make check`,",
      "2. verify `/health/ready`,",
      "3. inspect product-safe logs without sensitive payloads."
    ) -join "`n";
    "Security-And-Governance.md" = @(
      "# Security And Governance",
      "",
      "Generated services must follow `lotus-platform/platform-standards/LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md` from day one.",
      "",
      "Required scaffold controls include dependency hygiene, no-sensitive-content guardrails, implementation-truth guardrails, endpoint certification, OpenAPI quality, supported-feature discipline, branch protection, and wiki-source governance."
    ) -join "`n";
    "Integrations.md" = @(
      "# Integrations",
      "",
      "No service-specific upstream or downstream integration is supported by the scaffold.",
      "",
      "Add source-authority, consumer, producer, Gateway, Workbench, report, AI, and platform integration details only when the contracts and validation evidence exist."
    ) -join "`n";
    "Roadmap.md" = @(
      "# Roadmap",
      "",
      "The scaffold roadmap is deliberately narrow:",
      "",
      "1. replace placeholder ownership with repository-specific domain truth,",
      "2. add implementation slices through governed RFCs or issues,",
      "3. promote supported features only after code, tests, OpenAPI, CI, docs, and evidence pass,",
      "4. publish wiki source after merge when wiki truth changes."
    ) -join "`n";
    "Supported-Features.md" = @(
      "# Supported Features",
      "",
      "No business feature is supported by scaffold creation alone.",
      "",
      "Use `supported-features/supported-features.json` as implementation-backed product truth. Keep demo, README, wiki, and commercial claims aligned to that registry.",
      "",
      "Promotion rule:",
      "",
      "1. implement behavior,",
      "2. certify endpoints and evidence,",
      "3. update supported-feature truth."
    ) -join "`n"
  }

  foreach ($pageName in $wikiPages.Keys) {
    Set-Content -Path (Join-Path $wikiRoot $pageName) -Value $wikiPages[$pageName]
  }
}

function Add-TaskProfileTask {
  param(
    [object]$ProfilesRoot,
    [string]$ProfileName,
    [object]$Task
  )

  $profile = $ProfilesRoot.profiles | Where-Object { $_.name -eq $ProfileName } | Select-Object -First 1
  if ($null -eq $profile) {
    return
  }
  if ($profile.tasks | Where-Object { $_.repo -eq $Task.repo -and $_.id -eq $Task.id }) {
    return
  }
  $profile.tasks += $Task
}

function Convert-ServiceNameToRepoPathVariable {
  param([string]$RepoName)

  return (($RepoName.ToUpperInvariant() -replace "[^A-Z0-9]", "_") + "_REPO_PATH")
}

function Register-AgentOperatingContractRepository {
  param(
    [string]$PlatformRoot,
    [string]$RepoName
  )

  $syncScriptPath = Join-Path $PlatformRoot "automation/Sync-AgentOperatingContract.ps1"
  if (-not (Test-Path $syncScriptPath)) {
    return
  }

  $content = Get-Content -Raw $syncScriptPath
  if ($content.Contains("`"$RepoName`"")) {
    return
  }

  $archiveLineWithComma = '    "lotus-archive",'
  $archiveLine = '    "lotus-archive"'
  if ($content.Contains($archiveLineWithComma)) {
    $content = $content.Replace($archiveLineWithComma, "$archiveLineWithComma`n    `"$RepoName`",")
  }
  elseif ($content.Contains($archiveLine)) {
    $content = $content.Replace($archiveLine, "$archiveLine,`n    `"$RepoName`"")
  }
  else {
    return
  }

  Set-Content -Path $syncScriptPath -Value $content
  Write-Host "Updated automation/Sync-AgentOperatingContract.ps1 with $RepoName"
}

function Register-PlatformDevIngress {
  param(
    [string]$PlatformRoot,
    [string]$RepoName,
    [string]$RepoHostName,
    [int]$RepoPort
  )

  $platformStackRoot = Join-Path $PlatformRoot "platform-stack"
  if (-not (Test-Path $platformStackRoot)) {
    return
  }

  $hostname = "$RepoHostName.dev.lotus"
  $hostsPath = Join-Path $platformStackRoot "dev-ingress/hosts.example"
  if (Test-Path $hostsPath) {
    $hostsText = Get-Content -Raw $hostsPath
    $hostLine = "127.0.0.1 $hostname"
    if ($hostsText -notmatch [regex]::Escape($hostLine)) {
      $hostsText = $hostsText.TrimEnd("`r", "`n") + "`n$hostLine`n"
      Set-Content -Path $hostsPath -Value $hostsText
      Write-Host "Updated platform-stack/dev-ingress/hosts.example with $hostname"
    }
  }

  $caddyPath = Join-Path $platformStackRoot "dev-ingress/Caddyfile"
  if (Test-Path $caddyPath) {
    $caddyText = Get-Content -Raw $caddyPath
    if ($caddyText -notmatch [regex]::Escape("http://$hostname")) {
      $route = "http://$hostname {`n  reverse_proxy ${RepoName}:$RepoPort`n}`n"
      $caddyText = $caddyText.TrimEnd("`r", "`n") + "`n`n$route"
      Set-Content -Path $caddyPath -Value $caddyText
      Write-Host "Updated platform-stack/dev-ingress/Caddyfile with $hostname"
    }
  }

  $directHostCaddyPath = Join-Path $platformStackRoot "dev-ingress/Caddyfile.direct-host"
  if (Test-Path $directHostCaddyPath) {
    $directHostCaddyText = Get-Content -Raw $directHostCaddyPath
    if ($directHostCaddyText -notmatch [regex]::Escape("http://$hostname")) {
      $directHostRoute = "http://$hostname {`n`t reverse_proxy host.docker.internal:$RepoPort`n}`n"
      $directHostCaddyText = $directHostCaddyText.TrimEnd("`r", "`n") + "`n`n$directHostRoute"
      Set-Content -Path $directHostCaddyPath -Value $directHostCaddyText
      Write-Host "Updated platform-stack/dev-ingress/Caddyfile.direct-host with $hostname"
    }
  }

  $composePath = Join-Path $platformStackRoot "docker-compose.yml"
  if (Test-Path $composePath) {
    $composeText = Get-Content -Raw $composePath
    if ($composeText -notmatch "(?m)^  ${RepoName}:$") {
      $repoPathVariable = Convert-ServiceNameToRepoPathVariable -RepoName $RepoName
      $repoPathExpression = '${' + $repoPathVariable + '}'
      $serviceBlock = @"
  ${RepoName}:
    build:
      context: $repoPathExpression
      dockerfile: Dockerfile
    environment:
      OTEL_SERVICE_NAME: $RepoName
      OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector:4317
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:$RepoPort/health/ready', timeout=5)"]
      interval: 20s
      timeout: 5s
      retries: 15
      start_period: 20s
    logging: *default-logging

"@
      if ($composeText.Contains("  bff:`r`n")) {
        $composeText = $composeText.Replace("  bff:`r`n", "$serviceBlock  bff:`r`n")
      }
      elseif ($composeText.Contains("  bff:`n")) {
        $composeText = $composeText.Replace("  bff:`n", "$serviceBlock  bff:`n")
      }
      if ($composeText -notmatch [regex]::Escape("      ${RepoName}:`n        condition: service_healthy")) {
        $dependsBlock = "      ${RepoName}:`n        condition: service_healthy`n"
        $composeText = $composeText -replace "      prometheus:\r?\n        condition: service_started", "$dependsBlock      prometheus:`n        condition: service_started"
      }
      Set-Content -Path $composePath -Value $composeText
      Write-Host "Updated platform-stack/docker-compose.yml with $RepoName"
    }
  }

  $envExamplePath = Join-Path $platformStackRoot ".env.example"
  if (Test-Path $envExamplePath) {
    $repoPathVariable = Convert-ServiceNameToRepoPathVariable -RepoName $RepoName
    $envText = Get-Content -Raw $envExamplePath
    if ($envText -notmatch [regex]::Escape($repoPathVariable)) {
      $envLine = "$repoPathVariable=c:/Users/Sandeep/projects/$RepoName"
      $envText = $envText.TrimEnd("`r", "`n") + "`n$envLine`n"
      Set-Content -Path $envExamplePath -Value $envText
      Write-Host "Updated platform-stack/.env.example with $repoPathVariable"
    }
  }
}

function Register-PlatformContextAndAutomation {
  param(
    [string]$PlatformRoot,
    [string]$RepoName,
    [string]$RepoPathNormalized,
    [string]$RepoDescription,
    [string]$RepoBusinessRole,
    [string]$RepoCategory,
    [string]$RepoRuntime,
    [string[]]$RepoUpstreamDependencies,
    [string[]]$RepoDownstreamDependencies,
    [string]$RepoHostName,
    [int]$RepoPort,
    [string[]]$RepoLogPatterns,
    [string]$GithubRepo
  )

  Register-AgentOperatingContractRepository -PlatformRoot $PlatformRoot -RepoName $RepoName

  $manifestPath = Join-Path $PlatformRoot "context/lotus-context-manifest.json"
  if (Test-Path $manifestPath) {
    $manifest = Get-Content -Raw $manifestPath | ConvertFrom-Json
    if (-not ($manifest.applications | Where-Object { $_.repository -eq $RepoName })) {
      $manifest.applications += [pscustomobject]@{
        repository = $RepoName
        category = $RepoCategory
        business_role = $RepoBusinessRole
        primary_runtime = $RepoRuntime
        canonical_commands = [pscustomobject]@{
          quality = "make ci"
        }
        repo_context_path = "REPOSITORY-ENGINEERING-CONTEXT.md"
        status = "implemented"
        upstream_dependencies = @($RepoUpstreamDependencies)
        downstream_dependencies = @($RepoDownstreamDependencies)
        requires_platform_end_to_end_validation = $true
      }
      $manifest | ConvertTo-Json -Depth 12 | Set-Content $manifestPath
      Write-Host "Updated context/lotus-context-manifest.json with $RepoName"
    }
  }

  $qaMatrixPath = Join-Path $PlatformRoot "automation/qa-matrix.json"
  if ((Test-Path $qaMatrixPath) -and $RepoHostName) {
    $qaMatrix = Get-Content -Raw $qaMatrixPath | ConvertFrom-Json
    if (-not ($qaMatrix.repositories | Where-Object { $_.repo -eq $RepoName })) {
      $qaMatrix.repositories += [pscustomobject]@{
        repo = $RepoName
        startup = [pscustomobject]@{
          up_command = "docker compose up -d --build $RepoName"
          down_command = "docker compose down"
          log_command = "docker compose logs --tail=200 $RepoName"
        }
        checks = [pscustomobject]@{
          api = @(
            [pscustomobject]@{ id = "health"; method = "GET"; url = "http://$RepoHostName.dev.lotus/health"; expected_status = 200; must_contain = @("status") },
            [pscustomobject]@{ id = "docs"; method = "GET"; url = "http://$RepoHostName.dev.lotus/docs"; expected_status = 200; must_contain = @("Swagger") }
          )
          monitoring = @(
            [pscustomobject]@{ id = "metrics"; url = "http://$RepoHostName.dev.lotus/metrics"; expected_status = 200; must_contain = @("http") }
          )
          observability = [pscustomobject]@{
            require_response_headers = @("x-correlation-id", "x-trace-id")
            required_log_patterns = @($RepoLogPatterns)
          }
        }
      }
      $qaMatrix | ConvertTo-Json -Depth 12 | Set-Content $qaMatrixPath
      Write-Host "Updated automation/qa-matrix.json with $RepoName"
    }
  }

  if ($RepoHostName) {
    Register-PlatformDevIngress -PlatformRoot $PlatformRoot -RepoName $RepoName -RepoHostName $RepoHostName -RepoPort $RepoPort
  }

  $taskProfilesPath = Join-Path $PlatformRoot "automation/task-profiles.json"
  if (Test-Path $taskProfilesPath) {
    $profiles = Get-Content -Raw $taskProfilesPath | ConvertFrom-Json
    Add-TaskProfileTask -ProfilesRoot $profiles -ProfileName "bootstrap-env" -Task ([pscustomobject]@{
      id = "bootstrap-$RepoName"
      repo = $RepoName
      command = 'make install'
    })
    Add-TaskProfileTask -ProfilesRoot $profiles -ProfileName "fast-feedback" -Task ([pscustomobject]@{
      id = "$RepoName-check"
      repo = $RepoName
      command = 'make check && .venv/Scripts/python.exe -m pytest tests/integration -q'
    })
    Add-TaskProfileTask -ProfilesRoot $profiles -ProfileName "docker-build" -Task ([pscustomobject]@{
      id = "$RepoName-docker-up"
      repo = $RepoName
      command = "docker compose up -d --build $RepoName"
    })
    Add-TaskProfileTask -ProfilesRoot $profiles -ProfileName "ci-parity" -Task ([pscustomobject]@{
      id = "$RepoName-ci-local"
      repo = $RepoName
      command = 'make ci'
    })
    Add-TaskProfileTask -ProfilesRoot $profiles -ProfileName "docker-ci-parity" -Task ([pscustomobject]@{
      id = "$RepoName-docker-build"
      repo = $RepoName
      command = "docker compose build $RepoName"
    })
    Add-TaskProfileTask -ProfilesRoot $profiles -ProfileName "migration-quality" -Task ([pscustomobject]@{
      id = "$RepoName-integration"
      repo = $RepoName
      command = ".venv/Scripts/python.exe -m pytest tests/integration -q"
    })
    $profiles | ConvertTo-Json -Depth 12 | Set-Content $taskProfilesPath
    Write-Host "Updated automation/task-profiles.json with $RepoName"
  }

  $integrationsPath = Join-Path $PlatformRoot "wiki/Integrations.md"
  if (Test-Path $integrationsPath) {
    $integrations = Get-Content -Raw $integrationsPath
    if ($integrations -notmatch [regex]::Escape($RepoName)) {
      $integrations = $integrations -replace "lotus-report`, `lotus-ai", "lotus-report`, `$RepoName`, `lotus-ai"
      Set-Content $integrationsPath $integrations
      Write-Host "Updated wiki/Integrations.md with $RepoName"
    }
  }

  $referenceMapPath = Join-Path $PlatformRoot "context/CONTEXT-REFERENCE-MAP.md"
  if (Test-Path $referenceMapPath) {
    $referenceMap = Get-Content -Raw $referenceMapPath
    if ($referenceMap -notmatch [regex]::Escape("$RepoName/REPOSITORY-ENGINEERING-CONTEXT.md")) {
      $oldReference = '10. `lotus-ai/REPOSITORY-ENGINEERING-CONTEXT.md`'
      $newReference = "10. ``$RepoName/REPOSITORY-ENGINEERING-CONTEXT.md``" + "`n" + '11. `lotus-ai/REPOSITORY-ENGINEERING-CONTEXT.md`'
      $referenceMap = $referenceMap.Replace($oldReference, $newReference)
      Set-Content $referenceMapPath $referenceMap
      Write-Host "Updated context/CONTEXT-REFERENCE-MAP.md with $RepoName"
    }
  }

  $onboardingPath = Join-Path $PlatformRoot "docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md"
  if (Test-Path $onboardingPath) {
    $onboarding = Get-Content -Raw $onboardingPath
    if ($onboarding -notmatch [regex]::Escape("$RepoName\")) {
      $onboarding = $onboarding -replace "  lotus-report\\`r?`n  lotus-ai\\", "  lotus-report\`n  $RepoName\`n  lotus-ai\"
      $onboarding = $onboarding -replace '"lotus-report",\r?\n  "lotus-ai"', """lotus-report"",`n  ""$RepoName"",`n  ""lotus-ai"""
      Set-Content $onboardingPath $onboarding
      Write-Host "Updated docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md with $RepoName"
    }
  }

  $quickstartPath = Join-Path $PlatformRoot "context/LOTUS-QUICKSTART-CONTEXT.md"
  if (Test-Path $quickstartPath) {
    $quickstart = Get-Content -Raw $quickstartPath
    if ($quickstart -notmatch [regex]::Escape("`$RepoName")) {
      $oldQuickstart = '9. `lotus-ai`'
      $newQuickstart = "9. ``$RepoName``" + "`n" + "   $RepoBusinessRole." + "`n" + '10. `lotus-ai`'
      $quickstart = $quickstart.Replace($oldQuickstart, $newQuickstart)
      $quickstart = $quickstart.Replace('10. `lotus-platform`', '11. `lotus-platform`')
      Set-Content $quickstartPath $quickstart
      Write-Host "Updated context/LOTUS-QUICKSTART-CONTEXT.md with $RepoName"
    }
  }

  $engineeringPath = Join-Path $PlatformRoot "context/LOTUS-ENGINEERING-CONTEXT.md"
  if (Test-Path $engineeringPath) {
    $engineering = Get-Content -Raw $engineeringPath
    if ($engineering -notmatch [regex]::Escape("`$RepoName")) {
      $oldEngineering = '7. `lotus-ai`'
      $newEngineering = "7. ``$RepoName``" + "`n" + "   $RepoBusinessRole." + "`n`n" + '8. `lotus-ai`'
      $engineering = $engineering.Replace($oldEngineering, $newEngineering)
      Set-Content $engineeringPath $engineering
      Write-Host "Updated context/LOTUS-ENGINEERING-CONTEXT.md with $RepoName"
    }
  }

  $renderRegistries = Join-Path $PlatformRoot "automation/render_context_registries.py"
  if (Test-Path $renderRegistries) {
    python $renderRegistries | Out-Null
  }

  $validateContext = Join-Path $PlatformRoot "automation/validate_engineering_context_system.py"
  if (Test-Path $validateContext) {
    python $validateContext
  }

  $validateAutomation = Join-Path $PlatformRoot "automation/Validate-Automation-Config.ps1"
  if (Test-Path $validateAutomation) {
    powershell -ExecutionPolicy Bypass -File $validateAutomation | Out-Null
  }
}

function Initialize-GitRepository {
  param(
    [string]$TargetRepoRoot
  )
  git -C $TargetRepoRoot init -b main | Out-Null
}

function Ensure-GitInitialCommit {
  param(
    [string]$TargetRepoRoot,
    [string]$SvcName
  )

  $headExists = $true
  git -C $TargetRepoRoot rev-parse --verify HEAD *> $null
  if ($LASTEXITCODE -ne 0) {
    $headExists = $false
  }
  if ($headExists) {
    return
  }

  git -C $TargetRepoRoot add . | Out-Null
  git -C $TargetRepoRoot commit -m "Scaffold $SvcName service baseline" | Out-Null
}

function Configure-GithubRepository {
  param(
    [string]$TargetRepoRoot,
    [string]$RepoName,
    [string]$RepoDescription,
    [string]$Org,
    [string]$Visibility,
    [switch]$EnableDefaults,
    [switch]$ProtectMain,
    [string[]]$RequiredChecks
  )

  $repoSlug = "$Org/$RepoName"
  gh repo create $repoSlug --source $TargetRepoRoot --remote origin --description $RepoDescription --$Visibility | Out-Null
  git -C $TargetRepoRoot push -u origin main | Out-Null

  if ($EnableDefaults) {
    gh repo edit $repoSlug --enable-issues --enable-wiki --enable-auto-merge --enable-squash-merge=false --enable-merge-commit=false --enable-rebase-merge --delete-branch-on-merge | Out-Null
  }

  if ($ProtectMain) {
    $payload = [ordered]@{
      required_status_checks = [ordered]@{
        strict = $true
        contexts = @($RequiredChecks)
      }
      enforce_admins = $true
      required_pull_request_reviews = [ordered]@{
        dismiss_stale_reviews = $true
        required_approving_review_count = 0
      }
      restrictions = $null
      required_conversation_resolution = $true
      allow_force_pushes = $false
      allow_deletions = $false
      block_creations = $false
      required_linear_history = $true
      lock_branch = $false
      allow_fork_syncing = $false
    } | ConvertTo-Json -Depth 8

    $tempPayload = Join-Path $TargetRepoRoot "branch-protection.json"
    Set-Content -Path $tempPayload -Value $payload -NoNewline
    gh api --method PUT "repos/$repoSlug/branches/main/protection" --input $tempPayload | Out-Null
    Remove-Item $tempPayload -Force
  }
}

if ((Test-Path $target) -and -not $Force) {
  throw "Target path exists: $target. Use -Force to overwrite files."
}

$dirs = @(
  ".github/workflows",
  "requirements",
  "src/app",
  "src/app/api",
  "src/app/application",
  "src/app/contracts",
  "src/app/domain",
  "src/app/infrastructure",
  "src/app/middleware",
  "src/app/observability",
  "src/app/ports",
  "src/app/security",
  "src/app/resilience",
  "docs/operations",
  "docs/demo",
  "tests/unit",
  "tests/integration",
  "tests/e2e",
  "scripts",
  "docs/standards",
  "docs/rfcs",
  "evidence/rfc-implementation",
  "supported-features",
  "quality",
  "wiki"
)

foreach ($dir in $dirs) {
  New-Item -ItemType Directory -Force -Path (Join-Path $target $dir) | Out-Null
}

Copy-Item (Join-Path $templateRoot "Makefile.backend.template") (Join-Path $target "Makefile") -Force
Copy-Item (Join-Path $templateRoot ".editorconfig.backend.template") (Join-Path $target ".editorconfig") -Force
Copy-Item (Join-Path $templateRoot ".gitattributes.backend.template") (Join-Path $target ".gitattributes") -Force
Copy-Item (Join-Path $templateRoot ".gitignore.backend.template") (Join-Path $target ".gitignore") -Force
Copy-Item (Join-Path $templateRoot ".dockerignore.backend.template") (Join-Path $target ".dockerignore") -Force
Copy-Item (Join-Path $templateRoot "requirements.shared-runtime.lock.template.txt") (Join-Path $target "requirements/shared-runtime.lock.txt") -Force
Copy-Item (Join-Path $templateRoot "requirements.ci-tooling.lock.template.txt") (Join-Path $target "requirements/ci-tooling.lock.txt") -Force
Copy-Item (Join-Path $templateRoot "pre-commit.backend.template.yaml") (Join-Path $target ".pre-commit-config.yaml") -Force
Copy-Item (Join-Path $templateRoot "workflows/feature-lane.backend.template.yml") (Join-Path $target ".github/workflows/feature-lane.yml") -Force
Copy-Item (Join-Path $templateRoot "workflows/pr-merge-gate.backend.template.yml") (Join-Path $target ".github/workflows/pr-merge-gate.yml") -Force
Copy-Item (Join-Path $templateRoot "workflows/main-releasability.backend.template.yml") (Join-Path $target ".github/workflows/main-releasability.yml") -Force
Copy-Item (Join-Path $templateRoot "workflows/pr-auto-merge.template.yml") (Join-Path $target ".github/workflows/pr-auto-merge.yml") -Force
Copy-Item (Join-Path $templateRoot "workflows/merged-pr-main-releasability.template.yml") (Join-Path $target ".github/workflows/merged-pr-main-releasability.yml") -Force

$makefilePath = Join-Path $target "Makefile"
$makefile = Get-Content $makefilePath -Raw
$makefile = $makefile -replace [regex]::Escape(".PHONY: install lint typecheck openapi-gate test test-unit test-integration test-e2e test-coverage security-audit check ci docker-build clean"), ".PHONY: install lint ci-contract-gate maintainability-gate documentation-contract-gate quality-scorecard-gate monetary-float-guard no-sensitive-content-guard source-observability-contract-gate implementation-truth-gate supported-features-gate endpoint-certification-gate typecheck architecture-boundary-gate architecture-boundary-report quality-baseline openapi-gate test test-unit test-integration test-e2e test-coverage coverage-gate security-audit check ci docker-build clean"
if ($makefile -notmatch '\$\(MAKE\) ci-contract-gate') {
  $makefile = $makefile -replace [regex]::Escape("lint:`n`t`$(VENV_PYTHON) -m ruff check .`n`t`$(VENV_PYTHON) -m ruff format --check ."), "lint:`n`t`$(VENV_PYTHON) -m ruff check .`n`t`$(VENV_PYTHON) -m ruff format --check .`n`t`$(MAKE) ci-contract-gate"
}
if ($makefile -notmatch "(?m)^ci-contract-gate:") {
  $makefile = $makefile -replace [regex]::Escape("monetary-float-guard:"), "ci-contract-gate:`n`t`$(VENV_PYTHON) scripts/ci_contract_gate.py`n`nmonetary-float-guard:"
}
if ($makefile -notmatch '\$\(MAKE\) maintainability-gate') {
  $makefile = $makefile -replace [regex]::Escape("`t`$(MAKE) ci-contract-gate"), "`t`$(MAKE) ci-contract-gate`n`t`$(MAKE) maintainability-gate"
}
if ($makefile -notmatch "(?m)^maintainability-gate:") {
  $makefile = $makefile -replace [regex]::Escape("monetary-float-guard:"), "maintainability-gate:`n`t`$(VENV_PYTHON) scripts/maintainability_gate.py`n`nmonetary-float-guard:"
}
if ($makefile -notmatch '\$\(MAKE\) documentation-contract-gate') {
  $makefile = $makefile -replace [regex]::Escape("`t`$(MAKE) maintainability-gate"), "`t`$(MAKE) maintainability-gate`n`t`$(MAKE) documentation-contract-gate"
}
if ($makefile -notmatch "(?m)^documentation-contract-gate:") {
  $makefile = $makefile -replace [regex]::Escape("monetary-float-guard:"), "documentation-contract-gate:`n`t`$(VENV_PYTHON) scripts/documentation_contract_gate.py`n`nmonetary-float-guard:"
}
if ($makefile -notmatch '\$\(MAKE\) quality-scorecard-gate') {
  $makefile = $makefile -replace [regex]::Escape("`t`$(MAKE) documentation-contract-gate"), "`t`$(MAKE) documentation-contract-gate`n`t`$(MAKE) quality-scorecard-gate"
}
if ($makefile -notmatch "(?m)^quality-scorecard-gate:") {
  $makefile = $makefile -replace [regex]::Escape("monetary-float-guard:"), "quality-scorecard-gate:`n`t`$(VENV_PYTHON) scripts/quality_scorecard_gate.py`n`nmonetary-float-guard:"
}
if ($makefile -notmatch '\$\(MAKE\) monetary-float-guard') {
  $makefile = $makefile -replace [regex]::Escape("lint:`n`t`$(VENV_PYTHON) -m ruff check .`n`t`$(VENV_PYTHON) -m ruff format --check ."), "lint:`n`t`$(VENV_PYTHON) -m ruff check .`n`t`$(VENV_PYTHON) -m ruff format --check .`n`t`$(MAKE) monetary-float-guard"
}
if ($makefile -notmatch "(?m)^monetary-float-guard:") {
  $makefile = $makefile -replace [regex]::Escape("typecheck:"), "monetary-float-guard:`n`t`$(VENV_PYTHON) scripts/check_monetary_float_usage.py`n`ntypecheck:"
}
if ($makefile -notmatch '\$\(MAKE\) source-observability-contract-gate') {
  $makefile = $makefile -replace [regex]::Escape("`t`$(MAKE) no-sensitive-content-guard"), "`t`$(MAKE) no-sensitive-content-guard`n`t`$(MAKE) source-observability-contract-gate"
}
if ($makefile -notmatch "(?m)^source-observability-contract-gate:") {
  $makefile = $makefile -replace [regex]::Escape("implementation-truth-gate:"), "source-observability-contract-gate:`n`t`$(VENV_PYTHON) scripts/source_observability_contract_gate.py`n`nimplementation-truth-gate:"
}
if ($makefile -notmatch '\$\(MAKE\) implementation-truth-gate') {
  $makefile = $makefile -replace [regex]::Escape("lint:`n`t`$(VENV_PYTHON) -m ruff check .`n`t`$(VENV_PYTHON) -m ruff format --check ."), "lint:`n`t`$(VENV_PYTHON) -m ruff check .`n`t`$(VENV_PYTHON) -m ruff format --check .`n`t`$(MAKE) implementation-truth-gate"
}
if ($makefile -notmatch "(?m)^implementation-truth-gate:") {
  $makefile = $makefile -replace [regex]::Escape("supported-features-gate:"), "implementation-truth-gate:`n`t`$(VENV_PYTHON) scripts/implementation_truth_gate.py`n`nsupported-features-gate:"
}
if ($makefile -notmatch "(?m)^architecture-boundary-report:") {
  $makefile = $makefile -replace [regex]::Escape("openapi-gate:"), "architecture-boundary-gate:`n`t`$(VENV_PYTHON) scripts/architecture_boundary_gate.py --mode blocking`n`narchitecture-boundary-report:`n`t`$(VENV_PYTHON) scripts/architecture_boundary_gate.py --mode report-only`n`nquality-baseline: architecture-boundary-report`n`t`$(VENV_PYTHON) scripts/generate_quality_baseline.py`n`nopenapi-gate:"
}
if ($makefile -notmatch "(?m)^architecture-boundary-gate:") {
  $makefile = $makefile -replace [regex]::Escape("architecture-boundary-report:"), "architecture-boundary-gate:`n`t`$(VENV_PYTHON) scripts/architecture_boundary_gate.py --mode blocking`n`narchitecture-boundary-report:"
}
if ($makefile -notmatch '\$\(MAKE\) coverage-gate') {
  $makefile = $makefile -replace [regex]::Escape("test-coverage:`n`tCOVERAGE_FILE=.coverage.unit `$(VENV_PYTHON) -m pytest tests/unit --cov=src --cov-report=`n`tCOVERAGE_FILE=.coverage.integration `$(VENV_PYTHON) -m pytest tests/integration --cov=src --cov-report=`n`tCOVERAGE_FILE=.coverage.e2e `$(VENV_PYTHON) -m pytest tests/e2e --cov=src --cov-report=`n`t`$(VENV_PYTHON) -m coverage combine .coverage.unit .coverage.integration .coverage.e2e`n`t`$(VENV_PYTHON) -m coverage report --fail-under=99"), "test-coverage:`n`tCOVERAGE_FILE=.coverage.unit `$(VENV_PYTHON) -m pytest tests/unit --cov=src --cov-report=`n`tCOVERAGE_FILE=.coverage.integration `$(VENV_PYTHON) -m pytest tests/integration --cov=src --cov-report=`n`tCOVERAGE_FILE=.coverage.e2e `$(VENV_PYTHON) -m pytest tests/e2e --cov=src --cov-report=`n`t`$(VENV_PYTHON) scripts/coverage_gate.py"
}
$makefile = $makefile -replace [regex]::Escape("check: lint typecheck openapi-gate supported-features-gate endpoint-certification-gate test"), "check: lint typecheck architecture-boundary-gate openapi-gate supported-features-gate endpoint-certification-gate test"
$makefile = $makefile -replace [regex]::Escape("ci: lint typecheck openapi-gate supported-features-gate endpoint-certification-gate test-integration test-e2e test-coverage security-audit"), "ci: lint typecheck architecture-boundary-gate openapi-gate supported-features-gate endpoint-certification-gate test-integration test-e2e test-coverage security-audit"
Set-Content $makefilePath $makefile

$runtimeDependencies = [ordered]@{
  "fastapi" = "0.138.0"
  "starlette" = "1.3.1"
  "uvicorn" = "0.49.0"
  "pydantic" = "2.13.4"
  "pydantic-settings" = "2.14.2"
  "prometheus-fastapi-instrumentator" = "8.0.0"
  "httpx" = "0.28.1"
}

$developmentDependencies = [ordered]@{
  "ruff" = "0.15.18"
  "mypy" = "2.1.0"
  "pytest" = "9.1.1"
  "pytest-asyncio" = "1.4.0"
  "pytest-cov" = "7.1.0"
  "httpx2" = "2.4.0"
  "coverage" = "7.14.2"
  "pip-audit" = "2.10.1"
}

$runtimeDependencyLines = $runtimeDependencies.GetEnumerator() | ForEach-Object { "  `"$($_.Key)==$($_.Value)`"," }
$developmentDependencyLines = $developmentDependencies.GetEnumerator() | ForEach-Object { "  `"$($_.Key)==$($_.Value)`"," }

$pyproject = @"
[build-system]
requires = ["setuptools>=70", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "$ServiceName"
version = "0.1.0"
description = "$Description"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
$(($runtimeDependencyLines -join "`n"))
]

[project.optional-dependencies]
dev = [
$(($developmentDependencyLines -join "`n"))
]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
filterwarnings = [
  "error::starlette.testclient.StarletteDeprecationWarning",
]
"@
Set-Content -Path (Join-Path $target "pyproject.toml") -Value $pyproject

$sharedRuntimeLock = ($runtimeDependencies.GetEnumerator() | ForEach-Object { "$($_.Key)==$($_.Value)" }) -join "`n"
Set-Content -Path (Join-Path $target "requirements/shared-runtime.lock.txt") -Value $sharedRuntimeLock

$ciToolingLock = ($developmentDependencies.GetEnumerator() | ForEach-Object { "$($_.Key)==$($_.Value)" }) -join "`n"
Set-Content -Path (Join-Path $target "requirements/ci-tooling.lock.txt") -Value $ciToolingLock

$mypy = @"
[mypy]
python_version = 3.12
strict = True
mypy_path = src
files = src, tests
"@
Set-Content -Path (Join-Path $target "mypy.ini") -Value $mypy

$dockerfile = @"
FROM python:3.12-slim

ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY scripts ./scripts
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -e ".[dev]"

EXPOSE $Port
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$Port"]
"@
Set-Content -Path (Join-Path $target "Dockerfile") -Value $dockerfile

$mainPy = @"
from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.errors import problem_response
from app.middleware.correlation import CorrelationIdMiddleware
from app.observability import configure_logging, emit_request_diagnostic_event

SERVICE_NAME = "$ServiceName"
SERVICE_VERSION = "0.1.0"
ROUNDING_POLICY_VERSION = "v1"

app = FastAPI(title=SERVICE_NAME, version=SERVICE_VERSION)
app.add_middleware(CorrelationIdMiddleware, service_name=SERVICE_NAME)
Instrumentator().instrument(app).expose(app, include_in_schema=False)
configure_logging()


def _route_template(request: Request) -> str:
    route = request.scope.get("route")
    path = getattr(route, "path", None)
    return path if isinstance(path, str) and path.startswith("/") else "/unknown"


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> Response:
    emit_request_diagnostic_event(
        "request.validation_failed",
        route=_route_template(request),
        method=request.method,
        error_category="validation",
    )
    return problem_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        code="invalid_request",
        title="Invalid request",
        detail="Request validation failed. Correct the request fields and retry.",
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> Response:
    emit_request_diagnostic_event(
        "request.http_error",
        route=_route_template(request),
        method=request.method,
        status_code=exc.status_code,
    )
    return problem_response(
        status_code=exc.status_code,
        code="request_rejected",
        title="Request rejected",
        detail="The service rejected the request. Correct the request or contact support with the correlation id.",
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> Response:
    emit_request_diagnostic_event(
        "request.unhandled_error",
        level="ERROR",
        route=_route_template(request),
        method=request.method,
        error_category=exc.__class__.__name__,
    )
    return problem_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="internal_error",
        title="Internal service error",
        detail="The service could not complete the request. Retry later or contact support with the correlation id.",
    )


@app.get(
    "/health",
    tags=["Health"],
    summary="Get service health",
    description="Returns a lightweight service health response for diagnostics and platform smoke checks.",
    responses={
        200: {
            "description": "Service health response.",
            "content": {
                "application/json": {
                    "example": {"status": "ok", "service": SERVICE_NAME}
                }
            },
        }
    },
)
async def health() -> dict[str, str]:
    return {"status": "ok", "service": SERVICE_NAME}


@app.get(
    "/health/live",
    tags=["Health"],
    summary="Get liveness",
    description="Returns liveness status when the process is running.",
    responses={
        200: {
            "description": "Process is live.",
            "content": {"application/json": {"example": {"status": "live"}}},
        }
    },
)
async def health_live() -> dict[str, str]:
    return {"status": "live"}


@app.get(
    "/health/ready",
    tags=["Health"],
    summary="Get readiness",
    description="Returns readiness status and reports draining state with a 503 response.",
    responses={
        200: {
            "description": "Service is ready to receive traffic.",
            "content": {"application/json": {"example": {"status": "ready"}}},
        },
        503: {
            "description": "Service is intentionally draining and should not receive new traffic.",
            "content": {"application/json": {"example": {"status": "draining"}}},
        },
    },
)
async def health_ready(response: Response) -> dict[str, str]:
    if bool(getattr(app.state, "is_draining", False)):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "draining"}
    return {"status": "ready"}


@app.get(
    "/metadata",
    tags=["Metadata"],
    summary="Get service metadata",
    description="Returns service identity and policy-version metadata for operators and validators.",
    responses={
        200: {
            "description": "Service metadata response.",
            "content": {
                "application/json": {
                    "example": {
                        "service": SERVICE_NAME,
                        "version": SERVICE_VERSION,
                        "roundingPolicyVersion": ROUNDING_POLICY_VERSION,
                    }
                }
            },
        }
    },
)
async def metadata() -> dict[str, str]:
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "roundingPolicyVersion": ROUNDING_POLICY_VERSION,
    }
"@
Set-Content -Path (Join-Path $target "src/app/main.py") -Value $mainPy

Set-Content -Path (Join-Path $target "src/app/__init__.py") -Value ""
Set-Content -Path (Join-Path $target "src/app/api/__init__.py") -Value ""
Set-Content -Path (Join-Path $target "src/app/application/__init__.py") -Value ""
Set-Content -Path (Join-Path $target "src/app/contracts/__init__.py") -Value ""
Set-Content -Path (Join-Path $target "src/app/domain/__init__.py") -Value ""
Set-Content -Path (Join-Path $target "src/app/infrastructure/__init__.py") -Value ""
Set-Content -Path (Join-Path $target "src/app/middleware/__init__.py") -Value ""
Set-Content -Path (Join-Path $target "src/app/observability/__init__.py") -Value ""
Set-Content -Path (Join-Path $target "src/app/ports/__init__.py") -Value ""
Set-Content -Path (Join-Path $target "src/app/resilience/__init__.py") -Value ""
Set-Content -Path (Join-Path $target "src/app/security/__init__.py") -Value ""

$layerReadme = @"
# Layered Architecture Skeleton

This scaffold is intentionally minimal. Add implementation only when a real service responsibility
exists.

Expected dependency flow:

1. ``api`` depends on ``application``.
2. ``application`` depends on ``domain`` and ``ports``.
3. ``domain`` is framework-free and must not import FastAPI, API DTOs, infrastructure, or persistence.
4. ``infrastructure`` implements ``ports``.
5. ``security`` provides caller-context and authorization policy primitives.
6. ``resilience`` provides retry, backoff, timeout, and circuit-breaker policy primitives.
7. ``observability`` provides structured logging, correlation, tracing, and metrics helpers.

Run ``make architecture-boundary-report`` for the report-only architecture boundary check.
"@
Set-Content -Path (Join-Path $target "src/app/README.md") -Value $layerReadme

$domainModel = @"
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceProfile:
    name: str
    description: str


DEFAULT_SERVICE_PROFILE = ServiceProfile(
    name="$ServiceProfile",
    description="$(Get-ServiceProfileDescription -Profile $ServiceProfile)",
)
"@
Set-Content -Path (Join-Path $target "src/app/domain/service_profile.py") -Value $domainModel

$applicationService = @"
from __future__ import annotations

from app.domain.service_profile import DEFAULT_SERVICE_PROFILE, ServiceProfile


def current_service_profile() -> ServiceProfile:
    return DEFAULT_SERVICE_PROFILE
"@
Set-Content -Path (Join-Path $target "src/app/application/service_profile.py") -Value $applicationService

$apiReadme = @"
# API Layer

Keep routes thin. Route modules should validate HTTP input, call application services, and map
application results into response DTOs. Do not put business rules or downstream clients here.
"@
Set-Content -Path (Join-Path $target "src/app/api/README.md") -Value $apiReadme

$portsReadme = @"
# Ports Layer

Define repository, downstream client, clock, audit, idempotency, and event-publisher protocols here
before adding concrete infrastructure adapters.
"@
Set-Content -Path (Join-Path $target "src/app/ports/README.md") -Value $portsReadme

$infrastructureReadme = @"
# Infrastructure Layer

Concrete adapters belong here and should implement interfaces from ``app.ports``. Infrastructure code
may depend on HTTP clients, databases, queues, or files, but domain and application code must not.
"@
Set-Content -Path (Join-Path $target "src/app/infrastructure/README.md") -Value $infrastructureReadme

$securityReadme = @"
# Security Layer

Add caller-context, role/capability policies, and product-safe permission-denied behavior here
before protected business endpoints are promoted.
"@
Set-Content -Path (Join-Path $target "src/app/security/README.md") -Value $securityReadme

$errorsPy = @"
from __future__ import annotations

from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class ProblemDetails(BaseModel):
    code: str = Field(..., description="Stable product-safe error code.", examples=["invalid_request"])
    title: str = Field(..., description="Short product-safe error title.", examples=["Invalid request"])
    detail: str = Field(
        ...,
        description="Product-safe remediation guidance without raw payload or sensitive content.",
        examples=["Correct the request fields and retry."],
    )


def problem_response(status_code: int, code: str, title: str, detail: str) -> JSONResponse:
    problem = ProblemDetails(code=code, title=title, detail=detail)
    return JSONResponse(status_code=status_code, content=problem.model_dump())
"@
Set-Content -Path (Join-Path $target "src/app/errors.py") -Value $errorsPy

$callerContextPy = @"
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from fastapi import status
from fastapi.responses import JSONResponse

from app.errors import problem_response


@dataclass(frozen=True)
class CallerContext:
    subject: str
    roles: frozenset[str] = field(default_factory=frozenset)
    capabilities: frozenset[str] = field(default_factory=frozenset)

    @classmethod
    def from_iterables(
        cls,
        *,
        subject: str,
        roles: Iterable[str] = (),
        capabilities: Iterable[str] = (),
    ) -> "CallerContext":
        return cls(
            subject=subject,
            roles=frozenset(role.strip() for role in roles if role.strip()),
            capabilities=frozenset(capability.strip() for capability in capabilities if capability.strip()),
        )

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def has_capability(self, capability: str) -> bool:
        return capability in self.capabilities


@dataclass(frozen=True)
class CapabilityPolicy:
    required_capability: str
    allowed_roles: frozenset[str] = field(default_factory=frozenset)

    @classmethod
    def for_roles(
        cls,
        *,
        required_capability: str,
        allowed_roles: Iterable[str] = (),
    ) -> "CapabilityPolicy":
        return cls(
            required_capability=required_capability,
            allowed_roles=frozenset(role.strip() for role in allowed_roles if role.strip()),
        )

    def allows(self, caller: CallerContext) -> bool:
        if caller.has_capability(self.required_capability):
            return True
        return any(caller.has_role(role) for role in self.allowed_roles)


class PermissionDeniedError(Exception):
    def __init__(self, required_capability: str) -> None:
        self.required_capability = required_capability
        super().__init__("Permission denied")


def require_capability(caller: CallerContext, policy: CapabilityPolicy) -> None:
    if not policy.allows(caller):
        raise PermissionDeniedError(policy.required_capability)


def permission_denied_response(_: PermissionDeniedError) -> JSONResponse:
    return problem_response(
        status_code=status.HTTP_403_FORBIDDEN,
        code="permission_denied",
        title="Permission denied",
        detail="The caller is not permitted to perform this action.",
    )
"@
Set-Content -Path (Join-Path $target "src/app/security/caller_context.py") -Value $callerContextPy

$downstreamClientPy = @"
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import httpx


class DownstreamClientConfigurationError(ValueError):
    pass


class DownstreamServiceError(Exception):
    def __init__(self, *, code: str, status_code: int | None = None) -> None:
        self.code = code
        self.status_code = status_code
        super().__init__(code)


@dataclass(frozen=True)
class DownstreamClientConfig:
    base_url: str
    timeout_seconds: float = 2.0

    def __post_init__(self) -> None:
        parsed = urlparse(self.base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise DownstreamClientConfigurationError("Downstream base_url must be an absolute HTTP(S) URL.")
        if self.timeout_seconds <= 0:
            raise DownstreamClientConfigurationError("Downstream timeout_seconds must be positive.")


def build_trace_headers(*, correlation_id: str | None, trace_id: str | None) -> dict[str, str]:
    headers: dict[str, str] = {}
    if correlation_id:
        headers["X-Correlation-Id"] = correlation_id
    if trace_id:
        headers["X-Trace-Id"] = trace_id
    return headers


class DownstreamJsonClient:
    def __init__(self, config: DownstreamClientConfig, client: httpx.Client | None = None) -> None:
        self._config = config
        self._client = client or httpx.Client(
            base_url=config.base_url,
            timeout=config.timeout_seconds,
        )

    def get_json(
        self,
        path: str,
        *,
        correlation_id: str | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        try:
            response = self._client.get(
                path,
                headers=build_trace_headers(correlation_id=correlation_id, trace_id=trace_id),
            )
        except httpx.TimeoutException as exc:
            raise DownstreamServiceError(code="upstream_timeout") from exc
        except httpx.HTTPError as exc:
            raise DownstreamServiceError(code="upstream_unavailable") from exc

        if 400 <= response.status_code < 500:
            raise DownstreamServiceError(code="upstream_rejected_request", status_code=response.status_code)
        if response.status_code >= 500:
            raise DownstreamServiceError(code="upstream_unavailable", status_code=response.status_code)

        try:
            payload = response.json()
        except ValueError as exc:
            raise DownstreamServiceError(code="upstream_malformed_response", status_code=response.status_code) from exc

        if not isinstance(payload, dict):
            raise DownstreamServiceError(code="upstream_malformed_response", status_code=response.status_code)
        return payload
"@
Set-Content -Path (Join-Path $target "src/app/infrastructure/downstream_client.py") -Value $downstreamClientPy

if (Test-WriteCapableServiceProfile -Profile $ServiceProfile) {
  $idempotencyPy = @"
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import hashlib
import json
from typing import Any


class IdempotencyDecision(StrEnum):
    ACCEPTED = "accepted"
    REPLAYED = "replayed"
    CONFLICT = "conflict"


@dataclass(frozen=True)
class IdempotencyPolicy:
    namespace: str
    ttl_seconds: int = 86_400


@dataclass(frozen=True)
class IdempotencyRecord:
    key: str
    payload_hash: str


def payload_fingerprint(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def evaluate_idempotency(
    *,
    key: str,
    payload: dict[str, Any],
    existing: IdempotencyRecord | None,
) -> tuple[IdempotencyDecision, IdempotencyRecord]:
    record = IdempotencyRecord(key=key, payload_hash=payload_fingerprint(payload))
    if existing is None:
        return IdempotencyDecision.ACCEPTED, record
    if existing.key == key and existing.payload_hash == record.payload_hash:
        return IdempotencyDecision.REPLAYED, existing
    return IdempotencyDecision.CONFLICT, existing
"@
  Set-Content -Path (Join-Path $target "src/app/domain/idempotency.py") -Value $idempotencyPy

  $auditPy = @"
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from types import MappingProxyType
from typing import Mapping

FORBIDDEN_ATTRIBUTE_KEYS = frozenset(
    {
        "client_id",
        "client_name",
        "portfolio_id",
        "account_id",
        "holding_id",
        "request_body",
        "response_body",
    }
)


@dataclass(frozen=True)
class AuditEvent:
    event_type: str
    actor_subject: str
    outcome: str
    occurred_at_utc: datetime = field(default_factory=lambda: datetime.now(UTC))
    attributes: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        leaked = FORBIDDEN_ATTRIBUTE_KEYS.intersection(self.attributes)
        if leaked:
            raise ValueError(f"Audit event attributes contain sensitive keys: {', '.join(sorted(leaked))}")
        object.__setattr__(self, "attributes", MappingProxyType(dict(self.attributes)))
"@
  Set-Content -Path (Join-Path $target "src/app/domain/audit.py") -Value $auditPy
}

$observabilityPackageInit = @"
from app.observability.logging import configure_logging, emit_request_diagnostic_event

__all__ = ["configure_logging", "emit_request_diagnostic_event"]
"@
Set-Content -Path (Join-Path $target "src/app/observability/__init__.py") -Value $observabilityPackageInit

$observabilityPy = @"
from __future__ import annotations

import json
import logging
from typing import Literal

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
SERVICE_NAME = "$ServiceName"
REQUEST_DIAGNOSTIC_EVENTS = frozenset(
    {
        "request.validation_failed",
        "request.http_error",
        "request.unhandled_error",
    }
)


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")


def log_event(event_name: str, service: str, level: LogLevel = "INFO", **fields: object) -> None:
    payload = {
        "event": event_name,
        "service": service,
        **fields,
    }
    logging.getLogger(service).log(
        getattr(logging, level),
        json.dumps(payload, sort_keys=True, default=str),
    )


def emit_request_diagnostic_event(
    event_name: str,
    *,
    route: str,
    method: str,
    level: LogLevel = "INFO",
    status_code: int | None = None,
    error_category: str | None = None,
) -> None:
    if event_name not in REQUEST_DIAGNOSTIC_EVENTS:
        raise ValueError(f"unsupported request diagnostic event: {event_name}")
    if not route.startswith("/") or "?" in route:
        raise ValueError("route must be a route template without query string")
    if not method.strip():
        raise ValueError("method is required")
    fields: dict[str, object] = {
        "route": route,
        "method": method,
    }
    if status_code is not None:
        fields["status_code"] = status_code
    if error_category is not None:
        fields["error_category"] = error_category
    log_event(event_name, SERVICE_NAME, level, **fields)
"@
Set-Content -Path (Join-Path $target "src/app/observability/logging.py") -Value $observabilityPy

$correlationMiddleware = @"
from __future__ import annotations

from collections.abc import Awaitable, Callable
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, service_name: str) -> None:
        super().__init__(app)
        self._service_name = service_name

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        correlation_id = request.headers.get("X-Correlation-Id") or str(uuid.uuid4())
        trace_id = request.headers.get("X-Trace-Id") or str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        request.state.trace_id = trace_id
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000.0
        response.headers["X-Correlation-Id"] = correlation_id
        response.headers["X-Trace-Id"] = trace_id
        response.headers["X-Service-Name"] = self._service_name
        response.headers["X-Request-Duration-Ms"] = f"{duration_ms:.3f}"
        return response
"@
Set-Content -Path (Join-Path $target "src/app/middleware/correlation.py") -Value $correlationMiddleware

$openapiGate = @"
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.main import app  # noqa: E402


def _operation_name(method: str, path: str) -> str:
    return f"{method.upper()} {path}"


def _has_example(response: dict) -> bool:
    content = response.get("content")
    if not isinstance(content, dict):
        return False
    for media in content.values():
        if not isinstance(media, dict):
            continue
        if "example" in media or "examples" in media:
            return True
    return False


def main() -> None:
    spec = app.openapi()
    if "paths" not in spec or not spec["paths"]:
        raise SystemExit("OpenAPI gate failed: no paths defined")
    errors: list[str] = []
    for path, path_item in spec["paths"].items():
        if not isinstance(path_item, dict):
            errors.append(f"{path}: path item must be an object")
            continue
        for method, operation in path_item.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            name = _operation_name(method, path)
            if not operation.get("summary"):
                errors.append(f"{name}: missing summary")
            if not operation.get("description"):
                errors.append(f"{name}: missing description")
            if not operation.get("tags"):
                errors.append(f"{name}: missing tag")
            responses = operation.get("responses")
            if not isinstance(responses, dict) or not responses:
                errors.append(f"{name}: missing responses")
                continue
            success_responses = [
                response
                for status_code, response in responses.items()
                if str(status_code).startswith("2")
            ]
            if not success_responses:
                errors.append(f"{name}: missing 2xx response")
            for status_code, response in responses.items():
                if not isinstance(response, dict):
                    errors.append(f"{name}: response {status_code} must be an object")
                    continue
                if not response.get("description"):
                    errors.append(f"{name}: response {status_code} missing description")
            if not any(_has_example(response) for response in success_responses):
                errors.append(f"{name}: missing success response example")
    if errors:
        raise SystemExit("OpenAPI gate failed:\n" + "\n".join(sorted(errors)))
    print("OpenAPI gate passed")


if __name__ == "__main__":
    main()
"@
Set-Content -Path (Join-Path $target "scripts/openapi_quality_gate.py") -Value $openapiGate

$architectureBoundaryGate = @"
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = ROOT / "src" / "app"
REPORT_PATH = ROOT / "quality" / "architecture_boundary_report.json"

LAYER_RULES = {
    "domain": {
        "forbidden_prefixes": (
            "fastapi",
            "starlette",
            "requests",
            "httpx",
            "sqlalchemy",
            "app.api",
            "app.infrastructure",
            "app.contracts",
        ),
        "description": "Domain must stay framework-free and independent from API, contract, and infrastructure modules.",
    },
    "application": {
        "forbidden_prefixes": ("fastapi", "starlette", "app.infrastructure", "app.api"),
        "description": "Application services may orchestrate domain and ports but must not depend on HTTP/framework or concrete infrastructure.",
    },
    "api": {
        "forbidden_prefixes": ("app.infrastructure",),
        "description": "API routes should call application services rather than concrete infrastructure.",
    },
}


def _module_name(path: Path) -> str:
    return ".".join(path.relative_to(ROOT / "src").with_suffix("").parts)


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def _layer_for(path: Path) -> str | None:
    relative = path.relative_to(SRC_ROOT)
    return relative.parts[0] if relative.parts else None


def validate_architecture_boundaries() -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    for path in SRC_ROOT.rglob("*.py"):
        layer = _layer_for(path)
        if layer not in LAYER_RULES:
            continue
        imports = _imports(path)
        for imported in sorted(imports):
            for prefix in LAYER_RULES[layer]["forbidden_prefixes"]:
                if imported == prefix or imported.startswith(f"{prefix}."):
                    violations.append(
                        {
                            "path": str(path.relative_to(ROOT)),
                            "module": _module_name(path),
                            "layer": layer,
                            "import": imported,
                            "rule": LAYER_RULES[layer]["description"],
                        }
                    )
    return violations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("report-only", "blocking"),
        default="report-only",
    )
    args = parser.parse_args()
    violations = validate_architecture_boundaries()
    report = {
        "repository": "$ServiceName",
        "mode": args.mode,
        "status": "failed" if violations else "passed",
        "violations": violations,
        "rules": LAYER_RULES,
    }
    if args.mode == "report-only":
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if violations:
        label = "report" if args.mode == "report-only" else "gate"
        print(f"Architecture boundary {label} found {len(violations)} violation(s).")
        if args.mode == "blocking":
            print(json.dumps(violations, indent=2, sort_keys=True))
            return 1
        return 0
    label = "report" if args.mode == "report-only" else "gate"
    print(f"Architecture boundary {label} passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
"@
Set-Content -Path (Join-Path $target "scripts/architecture_boundary_gate.py") -Value $architectureBoundaryGate

$qualityBaseline = @"
from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOTS = (ROOT / "src", ROOT / "tests", ROOT / "scripts")
REPORT_PATH = ROOT / "quality" / "baseline_report.json"
MARKDOWN_PATH = ROOT / "quality" / "baseline_report.md"
ARCHITECTURE_REPORT_PATH = ROOT / "quality" / "architecture_boundary_report.json"


def _python_files() -> list[Path]:
    files: list[Path] = []
    for root in SOURCE_ROOTS:
        if root.exists():
            files.extend(path for path in root.rglob("*.py") if "__pycache__" not in path.parts)
    return sorted(files)


def _function_rows(path: Path) -> list[dict[str, object]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    rows: list[dict[str, object]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end_line = getattr(node, "end_lineno", node.lineno)
            rows.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "name": node.name,
                    "line": node.lineno,
                    "lines": end_line - node.lineno + 1,
                }
            )
    return rows


def build_report() -> dict[str, object]:
    files = _python_files()
    functions = [row for path in files for row in _function_rows(path)]
    architecture_report_exists = ARCHITECTURE_REPORT_PATH.exists()
    architecture_report_status = "missing"
    if architecture_report_exists:
        try:
            architecture_payload = json.loads(ARCHITECTURE_REPORT_PATH.read_text(encoding="utf-8"))
            architecture_report_status = str(architecture_payload.get("status", "unknown"))
        except json.JSONDecodeError:
            architecture_report_status = "malformed"
    largest_files = sorted(
        (
            {
                "path": str(path.relative_to(ROOT)),
                "lines": len(path.read_text(encoding="utf-8").splitlines()),
            }
            for path in files
        ),
        key=lambda item: int(item["lines"]),
        reverse=True,
    )[:10]
    largest_functions = sorted(
        functions,
        key=lambda item: int(item["lines"]),
        reverse=True,
    )[:10]
    return {
        "repository": "$ServiceName",
        "mode": "report-only",
        "service_profile": "$ServiceProfile",
        "python_files": len(files),
        "python_functions": len(functions),
        "largest_files": largest_files,
        "largest_functions": largest_functions,
        "architecture_boundary_report": "quality/architecture_boundary_report.json",
        "architecture_boundary_report_exists": architecture_report_exists,
        "architecture_boundary_report_status": architecture_report_status,
        "notes": [
            "Report-only scaffold baseline. Do not promote noisy metrics before baseline and exception policy are clear.",
            "OpenAPI, endpoint certification, supported-features, and no-sensitive-content gates remain separate deterministic scaffold checks.",
        ],
    }


def main() -> None:
    report = build_report()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Quality Baseline",
        "",
        f"Repository: ``{report['repository']}``",
        "",
        "Mode: ``report-only``",
        "",
        f"Service profile: ``{report['service_profile']}``",
        "",
        f"Python files: ``{report['python_files']}``",
        f"Python functions: ``{report['python_functions']}``",
        "",
        f"Architecture boundary report: ``{report['architecture_boundary_report_status']}``",
        "",
        "## Largest Files",
        "",
    ]
    lines.extend(f"- ``{item['path']}``: {item['lines']} lines" for item in report["largest_files"])
    lines.extend(["", "## Largest Functions", ""])
    lines.extend(
        f"- ``{item['path']}::{item['name']}``: {item['lines']} lines"
        for item in report["largest_functions"]
    )
    MARKDOWN_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if not report["architecture_boundary_report_exists"]:
        print("WARNING: quality/architecture_boundary_report.json is missing; run make architecture-boundary-report.")
    print(f"Wrote {REPORT_PATH} and {MARKDOWN_PATH}")


if __name__ == "__main__":
    main()
"@
Set-Content -Path (Join-Path $target "scripts/generate_quality_baseline.py") -Value $qualityBaseline

$coverageGate = @"
import sys
from pathlib import Path

import coverage


def main() -> int:
    files = [".coverage.unit", ".coverage.integration", ".coverage.e2e"]
    missing = [f for f in files if not Path(f).exists()]
    if missing:
        print(f"Missing coverage files: {missing}")
        return 1
    cov = coverage.Coverage()
    cov.combine(files)
    cov.save()
    total = cov.report()
    if total < 99.0:
        print(f"Coverage gate failed: {total:.2f} < 99.00")
        return 1
    print(f"Coverage gate passed: {total:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
"@
Set-Content -Path (Join-Path $target "scripts/coverage_gate.py") -Value $coverageGate

$maintainabilityGate = @'
from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ScopeLimit:
    name: str
    relative_path: str
    max_file_lines: int
    max_function_lines: int


SCOPE_LIMITS = (
    ScopeLimit("source", "src", max_file_lines=1200, max_function_lines=130),
    ScopeLimit("tests", "tests", max_file_lines=1200, max_function_lines=180),
    ScopeLimit("scripts", "scripts", max_file_lines=500, max_function_lines=120),
)


def _python_files(scope_root: Path) -> list[Path]:
    if not scope_root.exists():
        return []
    return sorted(path for path in scope_root.rglob("*.py") if "__pycache__" not in path.parts)


def _function_rows(path: Path) -> list[tuple[str, int, int]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    rows: list[tuple[str, int, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end_line = getattr(node, "end_lineno", node.lineno)
            rows.append((node.name, node.lineno, end_line - node.lineno + 1))
    return rows


def validate_maintainability(root: Path = ROOT) -> list[str]:
    violations: list[str] = []
    for limit in SCOPE_LIMITS:
        scope_root = root / limit.relative_path
        for path in _python_files(scope_root):
            relative_path = path.relative_to(root).as_posix()
            lines = len(path.read_text(encoding="utf-8").splitlines())
            if lines > limit.max_file_lines:
                violations.append(
                    f"{relative_path} has {lines} lines; {limit.name} files must stay at or below "
                    f"{limit.max_file_lines} lines"
                )
            for function_name, line_number, function_lines in _function_rows(path):
                if function_lines > limit.max_function_lines:
                    violations.append(
                        f"{relative_path}:{line_number} `{function_name}` has {function_lines} "
                        f"lines; {limit.name} functions must stay at or below "
                        f"{limit.max_function_lines} lines"
                    )
    return violations


def main() -> int:
    violations = validate_maintainability()
    if violations:
        print("Maintainability gate failed:")
        print("\n".join(violations))
        return 1
    print("Maintainability gate passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'@
Set-Content -Path (Join-Path $target "scripts/maintainability_gate.py") -Value $maintainabilityGate

$documentationContractGate = @'
from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_SURFACES: tuple[tuple[str, int, tuple[str, ...]], ...] = (
    (
        "AGENTS.md",
        80,
        ("Mandatory Reading Order", "Wiki Publication Rule", "Context Maintenance Rule"),
    ),
    (
        "README.md",
        20,
        ("Quick Start", "make documentation-contract-gate", "make quality-scorecard-gate", "make source-observability-contract-gate", "LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md"),
    ),
    (
        "REPOSITORY-ENGINEERING-CONTEXT.md",
        80,
        ("Repo-Native Commands", "Validation And CI Expectations", "make documentation-contract-gate", "make quality-scorecard-gate", "make source-observability-contract-gate"),
    ),
    ("docs/rfcs/README.md", 1, ("RFC Index",)),
    (
        "docs/standards/enterprise-readiness.md",
        8,
        ("make documentation-contract-gate", "make quality-scorecard-gate", "make source-observability-contract-gate", "LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md"),
    ),
    ("docs/runbooks/service-operations.md", 8, ("Standard Commands", "Health and Readiness")),
    (
        "docs/operations/api-certification.md",
        8,
        ("endpoint-certification-ledger.json", "Source-Degraded And Reconciliation Endpoints"),
    ),
    ("docs/operations/observability.md", 8, ("structured JSON application events",)),
    ("quality/ci_quality_gates.md", 20, ("make documentation-contract-gate", "make quality-scorecard-gate", "make source-observability-contract-gate")),
    ("quality/quality_scorecard.md", 10, ("Bank-Buyable Quality Scorecard", "Documentation and operations", "make quality-scorecard-gate")),
    ("evidence/rfc-implementation/README.md", 5, ("repository", "branch", "commit SHA")),
    ("wiki/Home.md", 10, ("Validation And CI", "Current Posture")),
    ("wiki/Development-Workflow.md", 8, ("make documentation-contract-gate", "make quality-scorecard-gate", "make source-observability-contract-gate")),
    ("wiki/Validation-And-CI.md", 12, ("make documentation-contract-gate", "make quality-scorecard-gate", "make source-observability-contract-gate")),
    ("wiki/Operations-Runbook.md", 5, ("Operations Runbook",)),
    ("wiki/Supported-Features.md", 5, ("No business feature is supported",)),
)

PROHIBITED_PLACEHOLDERS = (
    ("TODO", re.compile(r"\bTODO\b", re.IGNORECASE)),
    ("TBD", re.compile(r"\bTBD\b", re.IGNORECASE)),
    ("lorem ipsum", re.compile(r"\blorem ipsum\b", re.IGNORECASE)),
    ("coming soon", re.compile(r"\bcoming soon\b", re.IGNORECASE)),
)


def _non_empty_lines(content: str) -> list[str]:
    return [line for line in content.splitlines() if line.strip()]


def validate_documentation_contract(
    *,
    root: Path = ROOT,
    surfaces: tuple[tuple[str, int, tuple[str, ...]], ...] = REQUIRED_SURFACES,
) -> list[str]:
    errors: list[str] = []
    for relative_path, min_non_empty_lines, required_fragments in surfaces:
        path = root / relative_path
        if not path.exists():
            errors.append(f"{relative_path}: required documentation surface is missing")
            continue
        content = path.read_text(encoding="utf-8")
        non_empty_count = len(_non_empty_lines(content))
        if non_empty_count < min_non_empty_lines:
            errors.append(
                f"{relative_path}: has {non_empty_count} non-empty lines; "
                f"minimum is {min_non_empty_lines}"
            )
        for fragment in required_fragments:
            if fragment not in content:
                errors.append(f"{relative_path}: missing required fragment `{fragment}`")
        for name, pattern in PROHIBITED_PLACEHOLDERS:
            if pattern.search(content):
                errors.append(f"{relative_path}: contains placeholder text `{name}`")
    return errors


def main() -> int:
    errors = validate_documentation_contract()
    if errors:
        print("\n".join(errors))
        return 1
    print("Documentation contract gate passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'@
Set-Content -Path (Join-Path $target "scripts/documentation_contract_gate.py") -Value $documentationContractGate

$qualityScorecardGate = @'
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCORECARD_PATH = ROOT / "quality" / "quality_scorecard.md"
ENDPOINT_LEDGER_PATH = ROOT / "docs" / "operations" / "endpoint-certification-ledger.json"

ALLOWED_STATUSES = {
    "Implemented",
    "Partially implemented",
    "Planned",
    "Not applicable",
    "Unknown - requires owner review",
}

REQUIRED_CONTROLS = (
    "Architecture",
    "API and contracts",
    "Data and methodology",
    "Security and privacy",
    "Observability and supportability",
    "Resilience and performance",
    "Testing",
    "CI and release evidence",
    "Documentation and operations",
)

REQUIRED_EVIDENCE_ANCHORS: dict[str, tuple[str, ...]] = {
    "Architecture": ("architecture-boundary", "maintainability"),
    "API and contracts": ("OpenAPI", "endpoint certification"),
    "Data and methodology": ("source",),
    "Security and privacy": ("No-sensitive-content", "source-observability"),
    "Observability and supportability": ("health/readiness", "source-observability"),
    "Resilience and performance": ("Docker",),
    "Testing": ("Unit", "integration", "e2e"),
    "CI and release evidence": ("documentation contract", "source-observability", "implementation-truth"),
    "Documentation and operations": ("README", "wiki", "documentation-contract-gate"),
}

STALE_BUSINESS_ENDPOINT_PATTERNS: dict[str, re.Pattern[str]] = {
    "business_endpoints_not_implemented": re.compile(
        r"\bBusiness endpoints not yet implemented\b",
        re.IGNORECASE,
    ),
    "business_behavior_tests_not_implemented": re.compile(
        r"\bBusiness behavior tests not yet implemented\b",
        re.IGNORECASE,
    ),
    "business_supportability_not_implemented": re.compile(
        r"\bBusiness supportability states not yet implemented\b",
        re.IGNORECASE,
    ),
}

BASELINE_ENDPOINT_PATHS = {
    "/health",
    "/health/live",
    "/health/ready",
    "/metadata",
    "/api/v1/source-readiness",
    "/api/v1/reconciliation-status",
}


def _strip_markdown_code(value: str) -> str:
    return value.strip().strip("`").strip()


def _parse_scorecard_rows(content: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in content.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 5 or cells[0] in {"Control Area", "---"} or set(cells[0]) == {"-"}:
            continue
        rows.append(
            {
                "control_area": cells[0],
                "status": _strip_markdown_code(cells[1]),
                "evidence": cells[2],
                "gap": cells[3],
                "next_slice": cells[4],
            }
        )
    return rows


def _has_certified_business_endpoint() -> bool:
    if not ENDPOINT_LEDGER_PATH.exists():
        return False
    payload = json.loads(ENDPOINT_LEDGER_PATH.read_text(encoding="utf-8"))
    endpoints = payload.get("endpoints", [])
    if not isinstance(endpoints, list):
        return False
    for endpoint in endpoints:
        if not isinstance(endpoint, dict):
            continue
        path = str(endpoint.get("path", ""))
        status = endpoint.get("certification_status")
        if path not in BASELINE_ENDPOINT_PATHS and status in {"baseline_certified", "certified"}:
            return True
    return False


def validate_quality_scorecard(path: Path = SCORECARD_PATH) -> list[str]:
    if not path.exists():
        return [f"{path.relative_to(ROOT).as_posix()}: required quality scorecard is missing"]

    content = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if _has_certified_business_endpoint():
        for name, pattern in STALE_BUSINESS_ENDPOINT_PATTERNS.items():
            if pattern.search(content):
                errors.append(
                    f"quality/quality_scorecard.md: stale scaffold-era scorecard claim `{name}`"
                )

    rows = _parse_scorecard_rows(content)
    row_by_control = {row["control_area"]: row for row in rows}

    for control in REQUIRED_CONTROLS:
        row = row_by_control.get(control)
        if row is None:
            errors.append(f"quality/quality_scorecard.md: missing control row `{control}`")
            continue
        if row["status"] not in ALLOWED_STATUSES:
            errors.append(
                f"quality/quality_scorecard.md: `{control}` has unsupported status `{row['status']}`"
            )
        for field_name in ("evidence", "gap", "next_slice"):
            if not row[field_name].strip():
                errors.append(f"quality/quality_scorecard.md: `{control}` has empty `{field_name}` cell")
        evidence_lower = row["evidence"].lower()
        for anchor in REQUIRED_EVIDENCE_ANCHORS[control]:
            if anchor.lower() not in evidence_lower:
                errors.append(f"quality/quality_scorecard.md: `{control}` evidence missing `{anchor}`")

    unexpected_controls = sorted(set(row_by_control) - set(REQUIRED_CONTROLS))
    for control in unexpected_controls:
        errors.append(f"quality/quality_scorecard.md: unexpected control row `{control}`")
    return errors


def main() -> int:
    errors = validate_quality_scorecard()
    if errors:
        print("\n".join(errors))
        return 1
    print("Quality scorecard gate passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'@
Set-Content -Path (Join-Path $target "scripts/quality_scorecard_gate.py") -Value $qualityScorecardGate

$ciContractGate = @'
from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAKEFILE_PATH = ROOT / "Makefile"
WORKFLOWS_DIR = ROOT / ".github" / "workflows"


REQUIRED_TARGETS = (
    "ci-contract-gate",
    "maintainability-gate",
    "documentation-contract-gate",
    "quality-scorecard-gate",
    "monetary-float-guard",
    "no-sensitive-content-guard",
    "source-observability-contract-gate",
    "implementation-truth-gate",
    "supported-features-gate",
    "endpoint-certification-gate",
    "typecheck",
    "architecture-boundary-gate",
    "openapi-gate",
    "test-unit",
    "test-integration",
    "test-e2e",
    "test-coverage",
    "coverage-gate",
    "security-audit",
    "docker-build",
)

REQUIRED_LINT_CALLS = (
    "$(MAKE) ci-contract-gate",
    "$(MAKE) maintainability-gate",
    "$(MAKE) documentation-contract-gate",
    "$(MAKE) quality-scorecard-gate",
    "$(MAKE) monetary-float-guard",
    "$(MAKE) no-sensitive-content-guard",
    "$(MAKE) source-observability-contract-gate",
    "$(MAKE) implementation-truth-gate",
    "$(MAKE) supported-features-gate",
    "$(MAKE) endpoint-certification-gate",
)

REQUIRED_CHECK_DEPS = (
    "lint",
    "typecheck",
    "architecture-boundary-gate",
    "openapi-gate",
    "supported-features-gate",
    "endpoint-certification-gate",
    "test",
)

REQUIRED_CI_DEPS = (
    "lint",
    "typecheck",
    "architecture-boundary-gate",
    "openapi-gate",
    "supported-features-gate",
    "endpoint-certification-gate",
    "test-integration",
    "test-e2e",
    "test-coverage",
    "security-audit",
)

WORKFLOW_EXPECTATIONS: dict[str, tuple[str, ...]] = {
    "feature-lane.yml": (
        "permissions:\n  contents: read",
        "actions/checkout@v7",
        "actions/setup-python@v6",
        "reviewdog/action-actionlint@v1",
        "make lint",
        "make typecheck",
        "make architecture-boundary-gate",
        "make openapi-gate",
        "make security-audit",
        "pytest tests/unit",
    ),
    "pr-merge-gate.yml": (
        "permissions:\n  contents: read",
        "actions/checkout@v7",
        "actions/setup-python@v6",
        "reviewdog/action-actionlint@v1",
        "actions/upload-artifact@v7",
        "actions/download-artifact@v8",
        "docker/setup-buildx-action@v4",
        "suite: unit",
        "suite: integration",
        "suite: e2e",
        "make lint",
        "make typecheck",
        "make architecture-boundary-gate",
        "make openapi-gate",
        "make security-audit",
        "coverage report --fail-under=99",
        "make docker-build",
        "NODE_OPTIONS: --no-deprecation",
    ),
    "main-releasability.yml": (
        "workflow_dispatch:",
        "permissions:\n  contents: read",
        "actions/checkout@v7",
        "actions/setup-python@v6",
        "reviewdog/action-actionlint@v1",
        "actions/upload-artifact@v7",
        "actions/download-artifact@v8",
        "docker/setup-buildx-action@v4",
        "suite: unit",
        "suite: integration",
        "suite: e2e",
        "make lint",
        "make typecheck",
        "make architecture-boundary-gate",
        "make openapi-gate",
        "make security-audit",
        "coverage report --fail-under=99",
        "make docker-build",
        "cyclonedx-py environment",
        "release-evidence.json",
        "main-releasability-release-evidence",
        "NODE_OPTIONS: --no-deprecation",
    ),
    "pr-auto-merge.yml": (
        "pull_request_target:",
        "contents: read",
        "github.event.pull_request.head.repo.fork == false",
        "secrets.LOTUS_AUTOMERGE_TOKEN",
        "LOTUS_AUTOMERGE_TOKEN is required",
        "Skipping auto-merge; use an authorized human or release actor",
        "gh pr merge",
        "--auto --rebase --delete-branch",
    ),
    "merged-pr-main-releasability.yml": (
        "pull_request_target:",
        "types: [closed]",
        "actions: write",
        "contents: read",
        "github.event.pull_request.merged == true",
        "github.event.pull_request.base.ref == 'main'",
        "gh workflow run main-releasability.yml",
        "--ref main",
    ),
}

PROHIBITED_WORKFLOW_PATTERNS: dict[str, tuple[str, ...]] = {
    "feature-lane.yml": (
        "pull_request_target:",
        "contents: write",
        "pull-requests: write",
        "continue-on-error:",
    ),
    "pr-merge-gate.yml": (
        "pull_request_target:",
        "contents: write",
        "pull-requests: write",
        "continue-on-error:",
    ),
    "main-releasability.yml": (
        "pull_request_target:",
        "contents: write",
        "pull-requests: write",
        "continue-on-error:",
    ),
    "pr-auto-merge.yml": ("continue-on-error:",),
    "merged-pr-main-releasability.yml": ("continue-on-error:",),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _target_block(makefile: str, target: str) -> str:
    pattern = re.compile(rf"^{re.escape(target)}:.*?(?=^\S|\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(makefile)
    return match.group(0) if match else ""


def _target_deps(makefile: str, target: str) -> set[str]:
    match = re.search(rf"^{re.escape(target)}:\s*(?P<deps>.*)$", makefile, re.MULTILINE)
    if not match:
        return set()
    return {dependency.strip() for dependency in match.group("deps").split() if dependency.strip()}


def validate_makefile(makefile: str) -> list[str]:
    errors: list[str] = []
    for target in REQUIRED_TARGETS:
        if not re.search(rf"^{re.escape(target)}:", makefile, re.MULTILINE):
            errors.append(f"Makefile missing required target `{target}`")

    lint_block = _target_block(makefile, "lint")
    for call in REQUIRED_LINT_CALLS:
        if call not in lint_block:
            errors.append(f"Makefile lint target must call `{call}`")

    check_deps = _target_deps(makefile, "check")
    for dependency in REQUIRED_CHECK_DEPS:
        if dependency not in check_deps:
            errors.append(f"Makefile check target missing `{dependency}`")

    ci_deps = _target_deps(makefile, "ci")
    for dependency in REQUIRED_CI_DEPS:
        if dependency not in ci_deps:
            errors.append(f"Makefile ci target missing `{dependency}`")

    security_audit = _target_block(makefile, "security-audit")
    if "-m pip_audit" not in security_audit:
        errors.append("Makefile security-audit target must run pip-audit")
    if "requirements/shared-runtime.lock.txt" not in security_audit:
        errors.append("Makefile security-audit target must audit shared runtime lock")
    if "requirements/ci-tooling.lock.txt" not in security_audit:
        errors.append("Makefile security-audit target must audit CI tooling lock")
    return errors


def validate_workflows(workflows_dir: Path) -> list[str]:
    errors: list[str] = []
    for workflow_name, required_fragments in WORKFLOW_EXPECTATIONS.items():
        workflow_path = workflows_dir / workflow_name
        if not workflow_path.exists():
            errors.append(f"Missing workflow `{workflow_name}`")
            continue
        content = _read(workflow_path)
        for fragment in required_fragments:
            if fragment not in content:
                errors.append(f"{workflow_name} missing `{fragment}`")
        for prohibited in PROHIBITED_WORKFLOW_PATTERNS.get(workflow_name, ()):
            if prohibited in content:
                errors.append(f"{workflow_name} must not contain `{prohibited}`")
        errors.extend(_validate_job_timeouts(workflow_name, content))
    return errors


def _validate_job_timeouts(workflow_name: str, workflow: str) -> list[str]:
    errors: list[str] = []
    job_blocks = _job_blocks(workflow)
    if not job_blocks:
        return [f"{workflow_name} must define at least one parseable job"]
    for job_name, job_block in job_blocks.items():
        timeout_match = re.search(r"^    timeout-minutes:\s*(?P<value>\d+)\s*$", job_block, re.M)
        if not timeout_match:
            errors.append(f"{workflow_name} job `{job_name}` missing timeout-minutes")
            continue
        timeout = int(timeout_match.group("value"))
        if timeout < 1 or timeout > 60:
            errors.append(
                f"{workflow_name} job `{job_name}` timeout-minutes must be between 1 and 60"
            )
    return errors


def _job_blocks(workflow: str) -> dict[str, str]:
    lines = workflow.splitlines()
    try:
        jobs_index = next(
            index
            for index, line in enumerate(lines)
            if re.match(r"^\s*jobs\s*:\s*(?:#.*)?$", line)
        )
    except StopIteration:
        return {}

    blocks: dict[str, list[str]] = {}
    current_job: str | None = None
    for line in lines[jobs_index + 1 :]:
        job_match = re.match(r"^  (?P<job>[A-Za-z0-9_-]+):\s*$", line)
        if job_match:
            current_job = job_match.group("job")
            blocks[current_job] = [line]
            continue
        if current_job is not None:
            blocks[current_job].append(line)
    return {job: "\n".join(block_lines) for job, block_lines in blocks.items()}


def validate_ci_contract() -> list[str]:
    if not MAKEFILE_PATH.exists():
        return [f"Missing {MAKEFILE_PATH.relative_to(ROOT).as_posix()}"]
    return [*validate_makefile(_read(MAKEFILE_PATH)), *validate_workflows(WORKFLOWS_DIR)]


def main() -> int:
    errors = validate_ci_contract()
    if errors:
        print("\n".join(errors))
        return 1
    print("CI contract gate passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'@
Set-Content -Path (Join-Path $target "scripts/ci_contract_gate.py") -Value $ciContractGate

$floatGuard = @"
import sys
from pathlib import Path

MONETARY_HINTS = ("amount", "value", "price", "cost", "pnl", "market_value", "fx_rate")
ALLOWLIST = set()


def likely_monetary(line: str) -> bool:
    low = line.lower()
    return any(token in low for token in MONETARY_HINTS)


def main() -> int:
    violations: list[str] = []
    for path in Path("src").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for idx, line in enumerate(text.splitlines(), start=1):
            if "float(" in line and likely_monetary(line) and f"{path}:{idx}" not in ALLOWLIST:
                violations.append(f"{path}:{idx}: monetary float usage detected")
    if violations:
        print("\\n".join(violations))
        return 1
    print("Monetary float guard passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
"@
Set-Content -Path (Join-Path $target "scripts/check_monetary_float_usage.py") -Value $floatGuard

$sensitiveContentGuard = @"
import re
import sys
from pathlib import Path

FORBIDDEN_PATTERNS = {
    "portfolio_id": re.compile(r"\bportfolio[_-]?id\b", re.IGNORECASE),
    "client_id": re.compile(r"\bclient[_-]?id\b", re.IGNORECASE),
    "client_name": re.compile(r"\bclient[_-]?name\b", re.IGNORECASE),
    "account_id": re.compile(r"\baccount[_-]?id\b", re.IGNORECASE),
    "holding_id": re.compile(r"\bholding[_-]?id\b", re.IGNORECASE),
    "transaction_id": re.compile(r"\btransaction[_-]?id\b", re.IGNORECASE),
    "request_body": re.compile(r"\brequest[_-]?body\b", re.IGNORECASE),
    "response_body": re.compile(r"\bresponse[_-]?body\b", re.IGNORECASE),
    "raw_entitlement_failure": re.compile(r"\braw[_-]?entitlement[_-]?failure\b", re.IGNORECASE),
}

SCAN_ROOTS = ("evidence", "logs", "output")
ALLOWLIST = {
    Path("evidence/rfc-implementation/README.md"),
}


def main() -> int:
    violations: list[str] = []
    for root_name in SCAN_ROOTS:
        root = Path(root_name)
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path in ALLOWLIST:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for name, pattern in FORBIDDEN_PATTERNS.items():
                if pattern.search(text):
                    violations.append(f"{path}: forbidden sensitive content marker {name}")
    if violations:
        print("\\n".join(sorted(violations)))
        return 1
    print("No-sensitive-content guard passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
"@
Set-Content -Path (Join-Path $target "scripts/no_sensitive_content_guard.py") -Value $sensitiveContentGuard

$sourceObservabilityContractGate = @'
from __future__ import annotations

import ast
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "src" / "app"

ALLOWED_LOGGING_MODULES = {
    Path("src/app/observability/logging.py"),
}
LOW_LEVEL_OBSERVABILITY_HELPERS = {"log_event"}
PROHIBITED_LOGGING_ATTRIBUTES = {
    "basicConfig",
    "critical",
    "debug",
    "error",
    "exception",
    "getLogger",
    "info",
    "log",
    "warning",
}


def _python_files(source_root: Path) -> list[Path]:
    if not source_root.exists():
        return []
    return sorted(path for path in source_root.rglob("*.py") if "__pycache__" not in path.parts)


def _relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _is_allowed_logging_module(path: Path, root: Path) -> bool:
    return Path(_relative(path, root)) in ALLOWED_LOGGING_MODULES


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return None


def _validate_file(path: Path, root: Path) -> list[str]:
    relative_path = _relative(path, root)
    allowed_logging_module = _is_allowed_logging_module(path, root)
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    errors: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "logging" and not allowed_logging_module:
                    errors.append(
                        f"{relative_path}:{node.lineno}: direct logging imports are only "
                        "allowed in src/app/observability/logging.py"
                    )

        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imported_names = {alias.name for alias in node.names}
            if module == "logging" and not allowed_logging_module:
                errors.append(
                    f"{relative_path}:{node.lineno}: direct logging imports are only "
                    "allowed in src/app/observability/logging.py"
                )
            if (
                module in {"app.observability", "app.observability.logging"}
                and LOW_LEVEL_OBSERVABILITY_HELPERS.intersection(imported_names)
                and not allowed_logging_module
            ):
                errors.append(
                    f"{relative_path}:{node.lineno}: import central observability helpers "
                    "instead of low-level log_event"
                )

        if isinstance(node, ast.Call):
            call_name = _call_name(node.func)
            if call_name == "print":
                errors.append(
                    f"{relative_path}:{node.lineno}: print() is prohibited in application "
                    "source; use bounded structured logging"
                )
            if call_name == "log_event" and not allowed_logging_module:
                errors.append(
                    f"{relative_path}:{node.lineno}: call a central observability helper "
                    "instead of log_event"
                )
            if (
                call_name
                and call_name.startswith("logging.")
                and call_name.removeprefix("logging.") in PROHIBITED_LOGGING_ATTRIBUTES
                and not allowed_logging_module
            ):
                errors.append(
                    f"{relative_path}:{node.lineno}: direct logging calls are only allowed in "
                    "src/app/observability/logging.py"
                )

    return errors


def validate_source_observability_contract(root: Path = ROOT) -> list[str]:
    source_root = root / "src" / "app"
    errors: list[str] = []
    for path in _python_files(source_root):
        errors.extend(_validate_file(path, root))
    return sorted(errors)


def main() -> int:
    errors = validate_source_observability_contract()
    if errors:
        print("Source observability contract gate failed:")
        print("\n".join(errors))
        return 1
    print("Source observability contract gate passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'@
Set-Content -Path (Join-Path $target "scripts/source_observability_contract_gate.py") -Value $sourceObservabilityContractGate

$implementationTruthGate = @'
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUPPORTED_FEATURES_PATH = ROOT / "supported-features" / "supported-features.json"
SCAN_PATHS = (
    ROOT / "README.md",
    ROOT / "REPOSITORY-ENGINEERING-CONTEXT.md",
    ROOT / "docs" / "demo",
    ROOT / "docs" / "operations",
    ROOT / "quality",
    ROOT / "wiki",
)

PROMOTION_PATTERNS: dict[str, re.Pattern[str]] = {
    "demo_ready": re.compile(r"\bdemo[- ]ready\b", re.IGNORECASE),
    "production_ready": re.compile(r"\bproduction[- ]ready\b", re.IGNORECASE),
    "externally_supported": re.compile(r"\bexternally supported\b", re.IGNORECASE),
    "supported_business_feature": re.compile(r"\bsupported business feature\b", re.IGNORECASE),
    "supported_product_capability": re.compile(
        r"\bsupported product (?:capability|claim|workflow)\b",
        re.IGNORECASE,
    ),
    "client_ready_publication": re.compile(r"\bclient[- ]ready publication\b", re.IGNORECASE),
    "certified_data_product": re.compile(r"\bcertified data product\b", re.IGNORECASE),
    "data_mesh_certified": re.compile(r"\bdata[- ]mesh certified\b", re.IGNORECASE),
    "live_source_ingestion": re.compile(r"\blive source ingestion\b", re.IGNORECASE),
    "gateway_workbench_support": re.compile(
        r"\bGateway/Workbench support\b",
        re.IGNORECASE,
    ),
    "platform_certified_true": re.compile(r"\bplatformCertified\s*=\s*true\b"),
    "supported_feature_promoted_true": re.compile(r"\bsupportedFeaturePromoted\s*=\s*true\b"),
}

STALE_SCAFFOLD_PATTERNS: dict[str, re.Pattern[str]] = {
    "scaffold_no_business_workflow": re.compile(
        r"\bNo business workflow is implemented by the scaffold\b",
        re.IGNORECASE,
    ),
    "architecture_report_only": re.compile(
        r"\bReport-only until governance promotes it\b",
        re.IGNORECASE,
    ),
    "keep_architecture_report_only": re.compile(
        r"\bKeep report-only until low-noise policy is proven\b",
        re.IGNORECASE,
    ),
}

QUALIFIED_CONTEXT_PATTERNS = (
    re.compile(r"\bnot\b", re.IGNORECASE),
    re.compile(r"\bno\b", re.IGNORECASE),
    re.compile(r"\bwithout\b", re.IGNORECASE),
    re.compile(r"\bunsupported\b", re.IGNORECASE),
    re.compile(r"\bplanned\b", re.IGNORECASE),
    re.compile(r"\bblocked\b", re.IGNORECASE),
    re.compile(r"\bpending\b", re.IGNORECASE),
    re.compile(r"\bbefore\b", re.IGNORECASE),
    re.compile(r"\buntil\b", re.IGNORECASE),
    re.compile(r"\brequires?\b", re.IGNORECASE),
    re.compile(r"\bdo(?:es)? not\b", re.IGNORECASE),
    re.compile(r"\bmust not\b", re.IGNORECASE),
    re.compile(r"\bcannot\b", re.IGNORECASE),
    re.compile(r"\bmust only\b", re.IGNORECASE),
    re.compile(r"\bonly after\b", re.IGNORECASE),
    re.compile(r"\bremain(?:s)?\b", re.IGNORECASE),
)


def _implemented_features_count(path: Path = SUPPORTED_FEATURES_PATH) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    features = payload.get("features", [])
    if not isinstance(features, list):
        return 0
    return sum(
        1
        for feature in features
        if isinstance(feature, dict) and feature.get("status") == "implemented"
    )


def _scan_files(paths: tuple[Path, ...] = SCAN_PATHS) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if not path.exists():
            continue
        if path.is_file():
            files.append(path)
            continue
        files.extend(
            child
            for child in path.rglob("*")
            if child.is_file() and child.suffix.lower() in {".md", ".json"}
        )
    return files


def _is_qualified(lines: list[str], index: int) -> bool:
    window = " ".join(lines[max(0, index - 2) : index + 3])
    return any(pattern.search(window) for pattern in QUALIFIED_CONTEXT_PATTERNS)


def validate_implementation_truth(
    *,
    implemented_features_count: int | None = None,
    scan_paths: tuple[Path, ...] = SCAN_PATHS,
) -> list[str]:
    if implemented_features_count is None:
        implemented_features_count = _implemented_features_count()
    errors: list[str] = []
    for path in _scan_files(scan_paths):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for index, line in enumerate(lines):
            relative_path = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
            for name, pattern in STALE_SCAFFOLD_PATTERNS.items():
                if pattern.search(line):
                    errors.append(
                        f"{relative_path}:{index + 1}: stale scaffold current-state "
                        f"claim `{name}` no longer matches repository evidence"
                    )
            if implemented_features_count > 0:
                continue
            for name, pattern in PROMOTION_PATTERNS.items():
                if pattern.search(line) and not _is_qualified(lines, index):
                    errors.append(
                        f"{relative_path}:{index + 1}: unqualified current-state "
                        f"promotion claim `{name}` while no supported feature is implemented"
                    )
    return errors


def main() -> int:
    errors = validate_implementation_truth()
    if errors:
        print("\n".join(sorted(errors)))
        return 1
    print("Implementation-truth gate passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'@
Set-Content -Path (Join-Path $target "scripts/implementation_truth_gate.py") -Value $implementationTruthGate

$supportedFeaturesGate = @"
import json
import sys
from pathlib import Path

SUPPORTED_FEATURES_PATH = Path("supported-features/supported-features.json")


def main() -> int:
    if not SUPPORTED_FEATURES_PATH.exists():
        print(f"Missing {SUPPORTED_FEATURES_PATH}")
        return 1
    payload = json.loads(SUPPORTED_FEATURES_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    if payload.get("repository") is None:
        errors.append("supported-features repository is required")
    if payload.get("policy") != "Only implementation-backed behavior may be promoted to supported.":
        errors.append("supported-features policy must preserve implementation-backed promotion")
    features = payload.get("features")
    if not isinstance(features, list):
        errors.append("supported-features features must be a list")
    else:
        for index, feature in enumerate(features):
            if not isinstance(feature, dict):
                errors.append(f"features[{index}] must be an object")
                continue
            status = feature.get("status")
            evidence = feature.get("promotion_evidence")
            if status == "implemented" and not evidence:
                errors.append(f"features[{index}] implemented feature missing promotion_evidence")
            if status not in {"planned", "implemented", "not_applicable"}:
                errors.append(f"features[{index}] invalid status {status!r}")
    if errors:
        print("\\n".join(errors))
        return 1
    print("Supported-features gate passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
"@
Set-Content -Path (Join-Path $target "scripts/supported_features_gate.py") -Value $supportedFeaturesGate

$endpointCertificationGate = @"
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

LEDGER_PATH = Path("docs/operations/endpoint-certification-ledger.json")
APP_MAIN_PATH = Path("src/app/main.py")
REQUIRED_FIELDS = (
    "method",
    "path",
    "certification_status",
    "owner",
    "purpose",
    "when_to_use",
    "when_not_to_use",
    "request_examples",
    "response_examples",
    "error_examples",
    "test_evidence",
    "openapi_evidence",
)
OPERATION_EVENT_TEST_TERMS = ("operation_event", "operation_events")


def _openapi_operations_from_app() -> set[tuple[str, str]]:
    from app.main import app

    operations: set[tuple[str, str]] = set()
    for path, path_item in app.openapi().get("paths", {}).items():
        if not isinstance(path_item, dict):
            continue
        for method in path_item:
            if method.lower() in {"get", "post", "put", "patch", "delete"}:
                operations.add((method.upper(), path))
    return operations


def _openapi_operations_from_source() -> set[tuple[str, str]]:
    operations: set[tuple[str, str]] = set()
    tree = ast.parse(APP_MAIN_PATH.read_text(encoding="utf-8"), filename=str(APP_MAIN_PATH))
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            if not isinstance(decorator.func, ast.Attribute):
                continue
            method = decorator.func.attr.lower()
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue
            if not decorator.args or not isinstance(decorator.args[0], ast.Constant):
                continue
            path = decorator.args[0].value
            if isinstance(path, str):
                operations.add((method.upper(), path))
    return operations


def _openapi_operations() -> set[tuple[str, str]]:
    try:
        return _openapi_operations_from_app()
    except ModuleNotFoundError as exc:
        if APP_MAIN_PATH.exists():
            return _openapi_operations_from_source()
        raise exc


def main() -> int:
    if not LEDGER_PATH.exists():
        print(f"Missing {LEDGER_PATH}")
        return 1

    payload = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []

    if payload.get("policy") != "Every public OpenAPI operation requires certification evidence before promotion.":
        errors.append("endpoint certification policy must preserve evidence-backed promotion")

    entries = payload.get("endpoints")
    if not isinstance(entries, list):
        errors.append("endpoints must be a list")
        entries = []

    openapi_operations = _openapi_operations()
    ledger_operations: set[tuple[str, str]] = set()
    allowed_statuses = {"baseline_certified", "certified", "planned", "not_applicable"}

    for index, endpoint in enumerate(entries):
        if not isinstance(endpoint, dict):
            errors.append(f"endpoints[{index}] must be an object")
            continue

        missing = [field for field in REQUIRED_FIELDS if field not in endpoint]
        if missing:
            errors.append(f"endpoints[{index}] missing fields: {', '.join(missing)}")
            continue

        operation = (str(endpoint["method"]).upper(), str(endpoint["path"]))
        ledger_operations.add(operation)

        if endpoint["certification_status"] not in allowed_statuses:
            errors.append(f"{operation}: invalid certification_status {endpoint['certification_status']!r}")

        for field in ("purpose", "when_to_use", "when_not_to_use", "owner", "openapi_evidence"):
            if not str(endpoint.get(field, "")).strip():
                errors.append(f"{operation}: {field} is required")

        for field in ("request_examples", "response_examples", "error_examples", "test_evidence"):
            value = endpoint.get(field)
            if not isinstance(value, list) or not value:
                errors.append(f"{operation}: {field} must be a non-empty list")
        if endpoint["certification_status"] == "certified":
            test_evidence = endpoint.get("test_evidence", [])
            if not any(
                term in str(reference)
                for reference in test_evidence
                for term in OPERATION_EVENT_TEST_TERMS
            ):
                errors.append(
                    f"{operation}: certified endpoint must reference bounded operation-event test evidence"
                )

    missing_from_ledger = sorted(openapi_operations - ledger_operations)
    stale_in_ledger = sorted(ledger_operations - openapi_operations)

    for method, path in missing_from_ledger:
        errors.append(f"{method} {path}: missing endpoint certification ledger entry")
    for method, path in stale_in_ledger:
        errors.append(f"{method} {path}: stale endpoint certification ledger entry")

    if errors:
        print("\n".join(errors))
        return 1

    print("Endpoint certification gate passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
"@
Set-Content -Path (Join-Path $target "scripts/endpoint_certification_gate.py") -Value $endpointCertificationGate

$profileDescriptionPrefix = (Get-ServiceProfileDescription -Profile $ServiceProfile).Split('.')[0]
$unitTest = @"
from app.application.service_profile import current_service_profile
from app.domain.service_profile import DEFAULT_SERVICE_PROFILE, ServiceProfile
from app.errors import ProblemDetails
from app.main import SERVICE_NAME


def test_service_name_is_lotus_prefixed() -> None:
    assert SERVICE_NAME.startswith("lotus-")


def test_service_profile_is_domain_authoritative() -> None:
    profile = current_service_profile()
    assert profile is DEFAULT_SERVICE_PROFILE
    assert profile.name == "$ServiceProfile"
    assert "$profileDescriptionPrefix" in profile.description
    assert ServiceProfile(name=profile.name, description=profile.description) == profile


def test_problem_details_are_product_safe() -> None:
    problem = ProblemDetails(
        code="invalid_request",
        title="Invalid request",
        detail="Correct the request fields and retry.",
    )
    payload = problem.model_dump()
    assert payload == {
        "code": "invalid_request",
        "title": "Invalid request",
        "detail": "Correct the request fields and retry.",
    }
    assert "portfolio" not in payload["detail"].lower()
    assert "holding" not in payload["detail"].lower()


def test_supported_features_policy_starts_unpromoted() -> None:
    import json
    from pathlib import Path

    payload = json.loads(Path("supported-features/supported-features.json").read_text())
    assert payload["features"] == []
    assert payload["policy"] == "Only implementation-backed behavior may be promoted to supported."


def test_endpoint_certification_ledger_starts_with_scaffold_operations() -> None:
    import json
    from pathlib import Path

    payload = json.loads(Path("docs/operations/endpoint-certification-ledger.json").read_text())
    operations = {(endpoint["method"], endpoint["path"]) for endpoint in payload["endpoints"]}
    assert operations == {
        ("GET", "/health"),
        ("GET", "/health/live"),
        ("GET", "/health/ready"),
        ("GET", "/metadata"),
    }
    assert payload["policy"] == "Every public OpenAPI operation requires certification evidence before promotion."
"@
Set-Content -Path (Join-Path $target "tests/unit/test_service_contract.py") -Value $unitTest

$securityTest = @"
import pytest

from app.security.caller_context import (
    CallerContext,
    CapabilityPolicy,
    PermissionDeniedError,
    permission_denied_response,
    require_capability,
)


def test_capability_policy_allows_capability() -> None:
    caller = CallerContext.from_iterables(
        subject="operator",
        capabilities=("portfolio:read",),
    )
    policy = CapabilityPolicy.for_roles(required_capability="portfolio:read")
    require_capability(caller, policy)


def test_capability_policy_allows_role() -> None:
    caller = CallerContext.from_iterables(subject="operator", roles=("ops-admin",))
    policy = CapabilityPolicy.for_roles(
        required_capability="portfolio:write",
        allowed_roles=("ops-admin",),
    )
    require_capability(caller, policy)


def test_permission_denied_response_is_product_safe() -> None:
    with pytest.raises(PermissionDeniedError) as exc_info:
        require_capability(
            CallerContext.from_iterables(subject="operator"),
            CapabilityPolicy.for_roles(required_capability="portfolio:write"),
        )

    response = permission_denied_response(exc_info.value)
    body = bytes(response.body).decode("utf-8").lower()
    assert response.status_code == 403
    assert "permission_denied" in body
    assert "raw entitlement" not in body
    assert "client" not in body
    assert "portfolio" not in body
    assert "portfolio:write" not in body
"@
Set-Content -Path (Join-Path $target "tests/unit/test_security_caller_context.py") -Value $securityTest

$downstreamClientTest = @"
import httpx
import pytest

from app.infrastructure.downstream_client import (
    DownstreamClientConfig,
    DownstreamClientConfigurationError,
    DownstreamJsonClient,
    DownstreamServiceError,
    build_trace_headers,
)


def _client_for(handler: httpx.MockTransport) -> DownstreamJsonClient:
    return DownstreamJsonClient(
        DownstreamClientConfig(base_url="https://upstream.example", timeout_seconds=0.5),
        client=httpx.Client(base_url="https://upstream.example", transport=handler),
    )


def test_invalid_base_url_is_rejected() -> None:
    with pytest.raises(DownstreamClientConfigurationError):
        DownstreamClientConfig(base_url="not-a-url")


def test_invalid_timeout_is_rejected() -> None:
    with pytest.raises(DownstreamClientConfigurationError):
        DownstreamClientConfig(base_url="https://upstream.example", timeout_seconds=0)


def test_default_client_can_be_constructed_for_valid_config() -> None:
    client = DownstreamJsonClient(DownstreamClientConfig(base_url="https://upstream.example"))
    assert client is not None


def test_empty_trace_headers_are_omitted() -> None:
    assert build_trace_headers(correlation_id=None, trace_id=None) == {}


def test_trace_headers_are_forwarded() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["X-Correlation-Id"] == "corr-123"
        assert request.headers["X-Trace-Id"] == "trace-123"
        return httpx.Response(200, json={"status": "ok"})

    payload = _client_for(httpx.MockTransport(handler)).get_json(
        "/status",
        correlation_id="corr-123",
        trace_id="trace-123",
    )
    assert payload == {"status": "ok"}


def test_timeout_maps_to_safe_upstream_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    with pytest.raises(DownstreamServiceError) as exc_info:
        _client_for(httpx.MockTransport(handler)).get_json("/status")
    assert exc_info.value.code == "upstream_timeout"


def test_generic_http_error_maps_to_safe_upstream_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection failed", request=request)

    with pytest.raises(DownstreamServiceError) as exc_info:
        _client_for(httpx.MockTransport(handler)).get_json("/status")
    assert exc_info.value.code == "upstream_unavailable"


@pytest.mark.parametrize(
    ("status_code", "expected_code"),
    [(400, "upstream_rejected_request"), (404, "upstream_rejected_request"), (500, "upstream_unavailable"), (503, "upstream_unavailable")],
)
def test_http_error_statuses_map_to_safe_errors(status_code: int, expected_code: str) -> None:
    client = _client_for(httpx.MockTransport(lambda request: httpx.Response(status_code, json={"error": "x"})))
    with pytest.raises(DownstreamServiceError) as exc_info:
        client.get_json("/status")
    assert exc_info.value.code == expected_code
    assert exc_info.value.status_code == status_code


def test_malformed_response_maps_to_safe_error() -> None:
    client = _client_for(httpx.MockTransport(lambda request: httpx.Response(200, content=b"not-json")))
    with pytest.raises(DownstreamServiceError) as exc_info:
        client.get_json("/status")
    assert exc_info.value.code == "upstream_malformed_response"


def test_non_object_json_response_maps_to_safe_error() -> None:
    client = _client_for(httpx.MockTransport(lambda request: httpx.Response(200, json=["x"])))
    with pytest.raises(DownstreamServiceError) as exc_info:
        client.get_json("/status")
    assert exc_info.value.code == "upstream_malformed_response"
"@
Set-Content -Path (Join-Path $target "tests/unit/test_downstream_client.py") -Value $downstreamClientTest

$observabilityLoggingTest = @"
import json
import logging

import pytest

from app.observability import configure_logging, emit_request_diagnostic_event
from app.observability.logging import log_event


def test_configure_logging_sets_product_safe_message_format() -> None:
    configure_logging()
    assert logging.getLogger().level in {logging.INFO, logging.WARNING}


def test_log_event_emits_structured_json(caplog) -> None:  # type: ignore[no-untyped-def]
    with caplog.at_level(logging.INFO, logger="$ServiceName"):
        log_event("scaffold.test", service="$ServiceName", status="ok")

    payload = json.loads(caplog.records[-1].message)
    assert payload == {
        "event": "scaffold.test",
        "service": "$ServiceName",
        "status": "ok",
    }


def test_request_diagnostic_event_logs_route_template_only(caplog) -> None:  # type: ignore[no-untyped-def]
    with caplog.at_level(logging.INFO, logger="$ServiceName"):
        emit_request_diagnostic_event(
            "request.http_error",
            route="/health/{probe}",
            method="GET",
            status_code=404,
        )

    payload = json.loads(caplog.records[-1].message)
    assert payload == {
        "event": "request.http_error",
        "method": "GET",
        "route": "/health/{probe}",
        "service": "$ServiceName",
        "status_code": 404,
    }


def test_request_diagnostic_event_rejects_raw_paths() -> None:
    with pytest.raises(ValueError, match="route must be a route template"):
        emit_request_diagnostic_event(
            "request.http_error",
            route="/health/probe?debug=true",
            method="GET",
        )
"@
Set-Content -Path (Join-Path $target "tests/unit/test_observability_logging.py") -Value $observabilityLoggingTest

if (Test-WriteCapableServiceProfile -Profile $ServiceProfile) {
  $idempotencyAuditTest = @"
import pytest

from app.domain.audit import AuditEvent
from app.domain.idempotency import (
    IdempotencyDecision,
    evaluate_idempotency,
)


def test_same_key_same_payload_replays_existing_record() -> None:
    decision, record = evaluate_idempotency(
        key="request-1",
        payload={"action": "approve", "amount": "100.00"},
        existing=None,
    )
    assert decision == IdempotencyDecision.ACCEPTED

    replay_decision, replay_record = evaluate_idempotency(
        key="request-1",
        payload={"amount": "100.00", "action": "approve"},
        existing=record,
    )
    assert replay_decision == IdempotencyDecision.REPLAYED
    assert replay_record == record


def test_same_key_different_payload_conflicts() -> None:
    _, record = evaluate_idempotency(
        key="request-1",
        payload={"action": "approve", "amount": "100.00"},
        existing=None,
    )
    decision, _ = evaluate_idempotency(
        key="request-1",
        payload={"action": "reject", "amount": "100.00"},
        existing=record,
    )
    assert decision == IdempotencyDecision.CONFLICT


def test_audit_event_rejects_sensitive_attributes() -> None:
    with pytest.raises(ValueError):
        AuditEvent(
            event_type="workflow.updated",
            actor_subject="operator",
            outcome="denied",
            attributes={"portfolio_id": "PB_SG_GLOBAL_BAL_001"},
        )


def test_audit_event_allows_bounded_non_sensitive_attributes() -> None:
    event = AuditEvent(
        event_type="workflow.updated",
        actor_subject="operator",
        outcome="accepted",
        attributes={"workflow_state": "planned"},
    )
    assert event.attributes["workflow_state"] == "planned"
"@
  Set-Content -Path (Join-Path $target "tests/unit/test_idempotency_audit.py") -Value $idempotencyAuditTest
}

$integrationTest = @"
from fastapi import HTTPException
from fastapi.testclient import TestClient
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.main import app


@app.get("/__test_validation/{item_id}", include_in_schema=False)
async def _test_validation_route(item_id: int) -> dict[str, int]:
    return {"item_id": item_id}


@app.get("/__test_unhandled_error", include_in_schema=False)
async def _test_unhandled_error_route() -> None:
    raise RuntimeError("raw internal detail")


def test_health_endpoints() -> None:
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    assert client.get("/health/live").status_code == 200
    assert client.get("/health/ready").status_code == 200


def test_correlation_and_trace_header_propagation() -> None:
    client = TestClient(app)
    response = client.get(
        "/health",
        headers={"X-Correlation-Id": "corr-123", "X-Trace-Id": "trace-123"},
    )
    assert response.status_code == 200
    assert response.headers["X-Correlation-Id"] == "corr-123"
    assert response.headers["X-Trace-Id"] == "trace-123"


def test_correlation_and_trace_headers_are_generated() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["X-Correlation-Id"]
    assert response.headers["X-Trace-Id"]


def test_not_found_error_is_product_safe() -> None:
    client = TestClient(app)
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert "portfolio" not in response.text.lower()
    assert "holding" not in response.text.lower()


def test_validation_error_is_product_safe() -> None:
    client = TestClient(app)
    response = client.get("/__test_validation/not-an-int")
    assert response.status_code == 400
    body = response.text.lower()
    assert "invalid_request" in body
    assert "not-an-int" not in body
    assert "portfolio" not in body


def test_unhandled_error_is_product_safe() -> None:
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/__test_unhandled_error")
    assert response.status_code == 500
    body = response.text.lower()
    assert "internal_error" in body
    assert "raw internal detail" not in body


def test_http_exception_is_product_safe() -> None:
    @app.get("/__test_http_exception", include_in_schema=False)
    async def _test_http_exception_route() -> None:
        raise HTTPException(status_code=403, detail="raw entitlement detail")

    client = TestClient(app)
    response = client.get("/__test_http_exception")
    assert response.status_code == 403
    assert "raw entitlement detail" not in response.text.lower()


def test_starlette_http_exception_is_product_safe() -> None:
    @app.get("/__test_starlette_http_exception", include_in_schema=False)
    async def _test_starlette_http_exception_route() -> None:
        raise StarletteHTTPException(status_code=403, detail="raw entitlement detail")

    client = TestClient(app)
    response = client.get("/__test_starlette_http_exception")
    assert response.status_code == 403
    assert "raw entitlement detail" not in response.text.lower()


def test_readiness_reports_draining_state() -> None:
    client = TestClient(app)
    app.state.is_draining = True
    try:
        response = client.get("/health/ready")
        assert response.status_code == 503
        assert response.json()["status"] == "draining"
    finally:
        app.state.is_draining = False
"@
Set-Content -Path (Join-Path $target "tests/integration/test_health.py") -Value $integrationTest

$e2eTest = @"
from fastapi.testclient import TestClient
from app.main import app


def test_e2e_smoke() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_metadata_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/metadata")
    assert response.status_code == 200
    assert response.json()["service"].startswith("lotus-")
"@
Set-Content -Path (Join-Path $target "tests/e2e/test_smoke.py") -Value $e2eTest

Sync-AgentOperatingContract -PlatformRoot $repoRoot -TargetRepoRoot $target
Write-RepositoryEngineeringContext -TargetRepoRoot $target -SvcName $ServiceName -SvcDescription $Description -SvcBusinessRole $BusinessRole -SvcCategory $Category -SvcRuntime $PrimaryRuntime -SvcUpstreamDependencies $UpstreamDependencies -SvcDownstreamDependencies $DownstreamDependencies
Write-WikiBaseline -TargetRepoRoot $target -SvcName $ServiceName -SvcDescription $Description -SvcProfile $ServiceProfile

$standardsDocs = @{
  "docs/standards/enterprise-readiness.md" = "# Enterprise Readiness`n`n- Service: $ServiceName`n- Status: baseline adopted.`n`nEnterprise-quality enforcement is repo-native from day one. ``make lint``, ``make check``, and GitHub lanes protect architecture boundaries, maintainability thresholds, documentation surface contracts, quality-scorecard truth, source-observability contract posture, OpenAPI quality, supported-feature promotion control, endpoint certification, security audit, coverage, workflow timeout posture, no soft-failed critical CI jobs, and implementation-truth claims in README/docs/wiki current-state surfaces.`n`nDay-one enterprise posture is governed by ``lotus-platform/platform-standards/LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md``. ``make documentation-contract-gate`` enforces the minimum durable documentation surface needed for engineers, operators, reviewers, and future agents to apply that contract. ``make quality-scorecard-gate`` enforces the bank-buyable control matrix and blocks stale scaffold-era scorecard underclaims once certified business endpoints exist. ``make source-observability-contract-gate`` blocks raw application logging bypasses so request diagnostics stay route-template based and product-safe.`n`nThe maintainability gate starts with conservative source, test, and script file/function thresholds so new implementation work must split or refactor oversized additions.`n`n``make implementation-truth-gate`` also protects against stale scaffold-era underclaims in current-state demo documentation. As implementation evidence appears, the demo ledger must move from generic scaffold posture to evidence-backed capability rows plus explicit unsupported boundaries.`n`nDo not promote a scaffolded service as bank-buyable until implementation-backed evidence exists.";
  "docs/standards/scalability-availability.md" = "# Scalability and Availability`n`n- Service: $ServiceName`n- Baseline health/readiness, resilience, and metrics adopted.";
  "docs/standards/durability-consistency.md" = "# Durability and Consistency`n`n- Service: $ServiceName`n- Status: Planned.`n- Core write semantics, persistence, and service-specific idempotency policy are not implemented by the scaffold unless a later service slice adds code, tests, and evidence.";
  "docs/standards/rounding-precision.md" = "# Rounding and Precision`n`n- Service: $ServiceName`n- Canonical precision policy must be used for monetary outputs.";
  "docs/standards/data-model-ownership.md" = "# Data Model Ownership`n`n- Service: $ServiceName`n- Owns only its bounded-context schema.";
  "docs/standards/migration-contract.md" = "# Migration Contract`n`n- Service: $ServiceName`n- Versioned migrations + CI smoke gate required.";
}

foreach ($entry in $standardsDocs.GetEnumerator()) {
  Set-Content -Path (Join-Path $target $entry.Key) -Value $entry.Value
}

Set-Content -Path (Join-Path $target "docs/demo/demo-claims.md") -Value @"
# Demo Claims

This file is the starting demo-readiness ledger for ``$ServiceName``.

Do not promote demo claims from ``Planned`` until code, tests, endpoint certification, supported
feature evidence, and validation artifacts exist.

Allowed status vocabulary:

1. ``Implemented``
2. ``Partially implemented``
3. ``Planned``
4. ``Not applicable``
5. ``Unknown - requires owner review``

## Functional Capability Matrix

| Capability | Status | Evidence | Gap | Next step |
| --- | --- | --- | --- | --- |
| Service-specific business workflow | ``Planned`` | Scaffold creation provides only health, readiness, metadata, and governance surfaces. | No service-specific business workflow is implementation-backed yet. | Replace this row with evidence-backed capability rows as endpoints, tests, endpoint certification, supported-feature evidence, and demo proof are added. |
| Health and readiness diagnostics | ``Implemented`` | ``/health``, ``/health/live``, ``/health/ready``, integration tests. | Dependency-aware readiness is service-specific. | Add real dependency checks when integrations exist. |
| Metadata diagnostics | ``Implemented`` | ``/metadata``, e2e smoke test. | Domain metadata is service-specific. | Add service-owned metadata only when implementation needs it. |

## Non-Functional Capability Matrix

| Capability | Status | Evidence | Gap | Next step |
| --- | --- | --- | --- | --- |
| Product-safe errors | ``Implemented`` | ``app.errors.ProblemDetails``, generated tests. | Domain-specific denied/degraded errors are not implemented. | Add endpoint-specific errors with tests. |
| Correlation and trace propagation | ``Implemented`` | ``CorrelationIdMiddleware``, integration tests. | Cross-service propagation depends on real downstream clients. | Certify per integration. |
| Architecture and maintainability enforcement | ``Implemented`` | ``make architecture-boundary-gate`` and ``make maintainability-gate`` are blocking; ``make architecture-boundary-report`` remains available for evidence refresh. | Service-specific business boundaries are still scaffold-level. | Extend boundary rules as real modules, adapters, and ownership boundaries appear. |
| Security authorization model | ``Partially implemented`` | Caller-context and capability-policy placeholders. | No production authentication or service-specific authorization model. | Implement caller extraction and policy decisions for real endpoints. |
| Mesh certification | ``Planned`` | None unless mesh placeholders are explicitly requested. | Not certified. | Add repo-owned mesh declarations, telemetry, SLO/access/evidence policies, and pass certification. |
"@

if ($IncludeMeshPlaceholders) {
  $meshDirs = @(
    "contracts/domain-data-products",
    "contracts/trust-telemetry",
    "contracts/mesh-slo",
    "contracts/mesh-access",
    "contracts/mesh-evidence",
    "docs/operations"
  )
  foreach ($meshDir in $meshDirs) {
    New-Item -ItemType Directory -Force -Path (Join-Path $target $meshDir) | Out-Null
  }

  Set-Content -Path (Join-Path $target "contracts/domain-data-products/README.md") -Value @"
# Domain Data Product Mesh Placeholders

Status: Planned.
Certification status: not certified.

These files are opt-in scaffold placeholders only. Replace them with repo-owned producer and
consumer declarations before requesting mesh certification.
"@
  Set-Content -Path (Join-Path $target "contracts/domain-data-products/producer-consumer-placeholder.json") -Value @"
{
  "repository": "$ServiceName",
  "status": "Planned",
  "certification_status": "not_certified",
  "producer_declarations": [],
  "consumer_declarations": [],
  "policy": "Replace placeholders with repo-owned implementation truth before mesh certification."
}
"@
  Set-Content -Path (Join-Path $target "contracts/trust-telemetry/trust-telemetry-placeholder.json") -Value @"
{
  "repository": "$ServiceName",
  "status": "Planned",
  "certification_status": "not_certified",
  "telemetry_declarations": [],
  "policy": "Replace placeholders with repo-owned trust telemetry before mesh certification."
}
"@
  Set-Content -Path (Join-Path $target "contracts/mesh-slo/slo-policy-placeholder.json") -Value @"
{
  "repository": "$ServiceName",
  "status": "Planned",
  "certification_status": "not_certified",
  "slo_policies": [],
  "policy": "Replace placeholders with service-owned SLOs and validation evidence."
}
"@
  Set-Content -Path (Join-Path $target "contracts/mesh-access/access-policy-placeholder.json") -Value @"
{
  "repository": "$ServiceName",
  "status": "Planned",
  "certification_status": "not_certified",
  "access_policies": [],
  "policy": "Replace placeholders with governed access policy before any mesh claim."
}
"@
  Set-Content -Path (Join-Path $target "contracts/mesh-evidence/evidence-policy-placeholder.json") -Value @"
{
  "repository": "$ServiceName",
  "status": "Planned",
  "certification_status": "not_certified",
  "evidence_policies": [],
  "policy": "Replace placeholders with machine-readable evidence requirements before certification."
}
"@
  Set-Content -Path (Join-Path $target "docs/operations/mesh-placeholder.md") -Value @"
# Mesh Placeholder Posture

Status: Planned.
Certification status: not certified.

Mesh declarations are scaffold placeholders only because ``-IncludeMeshPlaceholders`` was used.
Do not claim producer, consumer, trust telemetry, SLO, access, or evidence-policy readiness until
repo-owned implementation and certification evidence exist.
"@
}

$readme = @(
  "# $ServiceName",
  "",
  "$Description",
  "",
  "Service profile: ``$ServiceProfile``",
  "",
  "$(Get-ServiceProfileDescription -Profile $ServiceProfile)",
  "",
  "## Quick Start",
  "",
  '```powershell',
  "make install",
  "make lint",
  "make ci-contract-gate",
  "make maintainability-gate",
  "make documentation-contract-gate",
  "make quality-scorecard-gate",
  "make source-observability-contract-gate",
  "make implementation-truth-gate",
  "make typecheck",
  "make architecture-boundary-report",
  "make quality-baseline",
  "make openapi-gate",
  "make check",
  "make ci",
  '```',
  "",
  '```powershell',
  ".venv\\Scripts\\python.exe -m pip install -e '.[dev]'",
  ".venv\\Scripts\\python.exe -m ruff check . && .venv\\Scripts\\python.exe -m ruff format --check .",
  ".venv\\Scripts\\python.exe scripts/ci_contract_gate.py",
  ".venv\\Scripts\\python.exe scripts/maintainability_gate.py",
  ".venv\\Scripts\\python.exe scripts/documentation_contract_gate.py",
  ".venv\\Scripts\\python.exe scripts/source_observability_contract_gate.py",
  ".venv\\Scripts\\python.exe scripts/implementation_truth_gate.py",
  ".venv\\Scripts\\python.exe -m mypy --config-file mypy.ini",
  ".venv\\Scripts\\python.exe scripts/openapi_quality_gate.py",
  ".venv\\Scripts\\python.exe -m pytest tests/unit tests/integration tests/e2e",
  ".venv\\Scripts\\python.exe scripts/coverage_gate.py",
  '```',
  "",
  "## Run",
  "",
  '```powershell',
  "uvicorn app.main:app --reload --port $Port",
  '```',
  "",
  "## Docker",
  "",
  '```powershell',
  "docker compose up --build",
  '```',
  "",
  "## Standards",
  "",
  "- CI and governance: .github/workflows/",
  "- Engineering commands: Makefile",
  "- Bank-buyable quality contract: lotus-platform/platform-standards/LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md",
  "- Demo claims ledger: docs/demo/demo-claims.md",
  "- API certification guide: docs/operations/api-certification.md",
  "- Observability guide: docs/operations/observability.md",
  "- RFC implementation evidence guide: evidence/rfc-implementation/README.md",
  "- Platform standards docs: docs/standards/",
  "- Quality scorecard and refactor decisions: quality/",
  "- Blocking CI contract evidence: make ci-contract-gate",
  "- Blocking maintainability evidence: make maintainability-gate",
  "- Blocking documentation contract evidence: make documentation-contract-gate",
  "- Blocking quality scorecard evidence: make quality-scorecard-gate",
  "- Blocking source observability evidence: make source-observability-contract-gate",
  "- Blocking implementation-truth evidence: make implementation-truth-gate",
  "- Layered architecture baseline: src/app/api, src/app/application, src/app/domain, src/app/ports, src/app/infrastructure, src/app/observability, src/app/security, src/app/resilience",
  "- Report-only architecture boundary evidence: make architecture-boundary-report",
  "- Report-only quality baseline evidence: make quality-baseline"
) -join "`n"
Set-Content -Path (Join-Path $target "README.md") -Value $readme

Set-Content -Path (Join-Path $target "docs/rfcs/README.md") -Value "# RFC Index`n"
Set-Content -Path (Join-Path $target "quality/quality_scorecard.md") -Value @"
# Bank-Buyable Quality Scorecard

Repository: $ServiceName
Service profile: $ServiceProfile

Use this scorecard to track movement toward the Lotus Bank-Buyable Engineering Contract.

| Control Area | Current Status | Evidence | Gap | Next Slice |
| --- | --- | --- | --- | --- |
| Architecture | ``Partially implemented`` | Layered package skeleton, blocking architecture-boundary gate, blocking maintainability thresholds, and report-only architecture-boundary evidence refresh. | Service-specific boundaries not yet implemented. | Replace scaffold placeholders with real module map and ownership truth. |
| API and contracts | ``Partially implemented`` | Health, readiness, metadata, OpenAPI gate, endpoint certification ledger. | Business endpoints not yet implemented. | Add certification evidence with each endpoint. |
| Data and methodology | ``Planned`` | No business source data scope is promoted by the scaffold. | Domain methodology is planned until source-owner data behavior exists. | Add source-owner and methodology docs when data behavior exists. |
| Security and privacy | ``Partially implemented`` | No-sensitive-content guard, source-observability contract gate, and product-safe errors. | AuthN/AuthZ posture is service-specific. | Add explicit security model before protected APIs. |
| Observability and supportability | ``Partially implemented`` | Correlation/trace headers, structured logs, route-template request diagnostics, health/readiness, metrics, and source-observability contract enforcement. | Business supportability states not yet implemented. | Add operation metrics and runbook updates with real workflows. |
| Resilience and performance | ``Partially implemented`` | Readiness drain baseline and Docker healthcheck. | Timeout/retry/back-pressure posture is service-specific. | Add resilience policy with downstream clients. |
| Testing | ``Partially implemented`` | Unit, integration, e2e scaffold tests. | Business behavior tests not yet implemented. | Add high-value tests with each feature slice. |
| CI and release evidence | ``Partially implemented`` | Feature, PR merge, main releasability workflows plus blocking maintainability, source-observability, documentation contract, quality-scorecard, implementation-truth, and source-safe local quality gates. | Repo-specific thresholds beyond deterministic size limits, source-observability controls, scorecard truth, and documentation surface contracts need evidence. | Tighten gates after measured baseline. |
| Documentation and operations | ``Partially implemented`` | README, repo context, wiki, runbooks, standards, quality scorecard, and RFC evidence guide are protected by ``make documentation-contract-gate``, ``make quality-scorecard-gate``, and ``make implementation-truth-gate``. | Operator docs are scaffold-level. | Replace placeholders with implementation-backed truth. |
"@
Set-Content -Path (Join-Path $target "quality/architecture_rules.md") -Value @"
# Architecture Rules

Use the Lotus layered backend default:

1. ``src/app/api`` routers/controllers stay thin and depend on ``application``,
2. ``src/app/application`` services orchestrate use cases and depend on ``domain`` and ``ports``,
3. ``src/app/domain`` logic stays framework-free and must not import FastAPI, API DTOs, infrastructure, persistence, or HTTP clients,
4. ``src/app/infrastructure`` sits behind ``ports`` adapters,
5. ``src/app/security`` owns caller-context and product-safe authorization policy primitives,
6. ``src/app/resilience`` owns retry, backoff, timeout, and circuit-breaker policy primitives; concrete downstream clients still belong behind ``ports`` in ``infrastructure``,
7. ``src/app/observability`` owns structured logging, route-template request diagnostics, correlation, tracing, and metrics helpers,
8. generated or scaffold placeholders must be replaced with implementation truth before promotion.

Run ``make architecture-boundary-gate`` for blocking CI enforcement. Run
``make architecture-boundary-report`` when a report artifact is needed for scorecard or review
evidence.
"@
Set-Content -Path (Join-Path $target "quality/ci_quality_gates.md") -Value @"
# CI Quality Gates

The scaffold starts with baseline gates in ``Makefile`` and ``.github/workflows/``.

Promote stricter gates only after the signal is measured, deterministic, low-noise, locally
runnable, and tied to a real bank-buyable control.

Blocking scaffold commands:

1. ``make architecture-boundary-gate``
2. ``make ci-contract-gate``
3. ``make maintainability-gate``
4. ``make documentation-contract-gate``
5. ``make quality-scorecard-gate``
6. ``make source-observability-contract-gate``
7. ``make implementation-truth-gate``

Report-only scaffold commands:

1. ``make architecture-boundary-report``
2. ``make quality-baseline``

``make ci-contract-gate`` is the anti-drift gate for the day-one bank-buyable baseline. It checks
that the Makefile and GitHub workflow lanes still include architecture boundaries, OpenAPI quality,
maintainability, supported-feature promotion control, endpoint certification, coverage, security audit, Docker build,
release evidence, least-privilege workflow permissions, documentation contract enforcement, quality-scorecard truth, source-observability contract enforcement, implementation-truth enforcement, and
approved action-runtime majors.
The gate also protects workflow-dispatch access and the merged-PR Main Releasability dispatch
needed for rebase auto-merged PRs.

``make maintainability-gate`` blocks oversized Python files/functions across ``src``, ``tests``,
and ``scripts``. It is calibrated above the initial scaffold baseline so new implementation work
must split or refactor large additions instead of normalizing hard-to-review modules.

``make documentation-contract-gate`` blocks deletion, thinning, missing anchors, and placeholder
text across the generated README, repository context, standards, runbooks, quality, evidence, and
wiki surfaces. It keeps enterprise operating context intact for future implementation agents.

``make quality-scorecard-gate`` blocks bank-buyable scorecard drift. It verifies the required
control matrix, approved status vocabulary, non-empty evidence and gap cells, implementation-backed
evidence anchors, and stale scaffold-era scorecard underclaims once certified business endpoints
exist.

``make source-observability-contract-gate`` blocks ad hoc application logging in ``src/app``.
Feature code must use central observability helpers rather than raw ``print()``, direct Python
logging, or low-level ``log_event`` calls. Request diagnostics log route templates rather than raw
URL paths.

``make implementation-truth-gate`` blocks unqualified current-state claims of demo readiness,
production readiness, external support, certification, live source ingestion, Gateway/Workbench
support, or client-ready publication while ``supported-features/supported-features.json`` has no
implemented features. It prevents generated README/wiki/operations text from outpacing code,
endpoint certification, data-mesh proof, and supported-feature evidence.
It also blocks stale scaffold-era demo underclaims when they no longer match implementation and CI
evidence.
"@
Set-Content -Path (Join-Path $target "quality/refactor_decisions.md") -Value @"
# Refactor Decisions

Record architecture, API, security, observability, testing, CI, and documentation decisions that
change the repository's bank-buyable posture.

Do not use this file for aspirational claims. Every entry should name code, tests, and validation
evidence or explicitly mark the item as planned.
"@
Set-Content -Path (Join-Path $target "supported-features/supported-features.json") -Value @"
{
  "repository": "$ServiceName",
  "features": [],
  "policy": "Only implementation-backed behavior may be promoted to supported."
}
"@
Set-Content -Path (Join-Path $target "evidence/rfc-implementation/README.md") -Value @"
# RFC Implementation Evidence

Use this directory for machine-readable implementation evidence referenced by RFCs and PRs.

Evidence must name the repository, branch, commit SHA, PR number, RFC slice, validation command,
endpoint or route, state-machine or lifecycle decision where applicable, supported-feature posture,
wiki publication posture, source-contract realization, downstream realization, operational
identifiers, and result. Do not store sensitive client, portfolio, holding, transaction,
entitlement, raw HTTP payload, trace, or correlation details here unless a later
security review explicitly certifies the artifact.
"@
Set-Content -Path (Join-Path $target "evidence/rfc-implementation/evidence-manifest.template.json") -Value @"
{
  "repository": "$ServiceName",
  "rfc_id": "RFC-0000",
  "slice_id": "slice-0",
  "generated_at_utc": "YYYY-MM-DDTHH:MM:SSZ",
  "branch": "feature-branch",
  "commit_sha": "unknown",
  "pull_request": null,
  "status": "draft",
  "summary": "Replace with the evidence package purpose and scope.",
  "slice_closure": {
    "implementation_complete": false,
    "tests_complete": false,
    "documentation_complete": false,
    "review_complete": false,
    "unsupported_claims_removed": false,
    "notes": "Replace with the slice closure decision."
  },
  "api_certification": {
    "openapi_gate": "not_run",
    "certified_endpoints": [],
    "degraded_error_examples_reviewed": false,
    "attribute_examples_reviewed": false
  },
  "state_machine_review": {
    "applies": false,
    "transition_matrix_path": null,
    "allowed_transition_tests": [],
    "rejected_transition_tests": []
  },
  "supported_features_review": {
    "supported_features_path": "supported-features/supported-features.json",
    "promoted_features": [],
    "deferred_features": [],
    "no_aspirational_claims": false
  },
  "wiki_publication": {
    "wiki_source_changed": false,
    "check_only_status": "not_run",
    "publish_required_after_merge": false,
    "published_commit": null
  },
  "validation_commands": [
    {
      "command": "make check",
      "status": "not_run",
      "evidence_ref": "output/path-to-command-summary.json"
    }
  ],
  "artifacts": [
    {
      "artifact_id": "example-artifact",
      "artifact_type": "json",
      "path": "output/example/example-artifact.json",
      "hash": "sha256:replace-after-generation",
      "description": "Replace with the source-backed evidence artifact description."
    }
  ],
  "cross_app_evidence": [],
  "upstream_realization": [],
  "source_contract_realization": [],
  "downstream_realization": [],
  "review_notes": [],
  "sensitive_content_policy": "Do not store client, holding, transaction, entitlement, raw HTTP payload, trace, or raw support details unless a later security review explicitly certifies the artifact."
}
"@
Set-Content -Path (Join-Path $target ".env.example") -Value @"
APP_ENV=local
LOG_LEVEL=INFO
ROUNDING_POLICY_VERSION=v1
"@
Set-Content -Path (Join-Path $target "docker-compose.yml") -Value @"
services:
  $($ServiceName):
    build: .
    ports:
      - \"$($Port):$($Port)\"
    env_file:
      - .env
    healthcheck:
      test: [\"CMD\", \"python\", \"-c\", \"import urllib.request; urllib.request.urlopen('http://localhost:$($Port)/health/ready')\"]
      interval: 15s
      timeout: 3s
      retries: 10
"@
New-Item -ItemType Directory -Force -Path (Join-Path $target "docs/runbooks") | Out-Null
Set-Content -Path (Join-Path $target "docs/runbooks/service-operations.md") -Value @"
# Service Operations Runbook

## Standard Commands

- `make lint`
- `make typecheck`
- `make ci`
- `docker compose up --build`

## Health and Readiness

- Liveness: `/health/live`
- Readiness: `/health/ready`
- General health: `/health`
- Metadata: `/metadata`

## Incident First Checks

1. Check container logs for request failures and stack traces.
2. Verify `/health/ready` and metrics endpoint.
3. Run local parity check (`make ci`) before hotfix PR.
"@
Set-Content -Path (Join-Path $target "docs/operations/observability.md") -Value @"
# Observability Baseline

This repository starts from the Lotus platform observability scaffold.

## Default Signals

- `/health`, `/health/live`, and `/health/ready`
- `/metrics` outside the OpenAPI schema
- correlation and trace response headers
- structured JSON application events
- product-safe error responses

## Sensitive-Content Rule

Logs, metrics, traces, dashboards, and evidence artifacts must not include client names, portfolio
ids, holdings, raw entitlement failures, request bodies, response bodies, trace ids, or correlation
ids as metric labels.
"@
Set-Content -Path (Join-Path $target "docs/operations/api-certification.md") -Value @"
# API Certification Baseline

Every endpoint added after scaffold creation must include:

1. domain-correct tag grouping,
2. clear what/when/how description,
3. complete request and response examples,
4. product-safe error examples,
5. attribute descriptions, types, and examples,
6. focused unit or integration tests for success and failure behavior,
7. OpenAPI gate coverage before merge.

The machine-readable source for endpoint certification tracking is:

- `docs/operations/endpoint-certification-ledger.json`

Run `make endpoint-certification-gate` before promoting any endpoint as supported.
Certified business/operator endpoints must cite bounded operation-event test evidence in the
endpoint ledger so API certification stays coupled to supportability telemetry proof.

## Source-Degraded And Reconciliation Endpoints

Endpoints that reconcile expected-versus-realized state or consume another Lotus app as source
authority must also include:

1. explicit source-owner fields in success and degraded responses,
2. source freshness, lineage, and supportability fields where the source owner exposes them,
3. `READY`, `DEGRADED`, `BLOCKED`, and `NOT_SUPPORTED` examples where those states are applicable,
4. tests for missing, stale, unavailable, partial, malformed, and conflicting upstream evidence,
5. proof that the service does not clone calculations owned by another Lotus app,
6. same-RFC upstream source-contract and downstream consumer realization evidence when contracts
   change,
7. README, wiki, supported-feature, and RFC evidence updates before any product support claim.
"@
Set-Content -Path (Join-Path $target "docs/operations/endpoint-certification-ledger.json") -Value @"
{
  "repository": "$ServiceName",
  "policy": "Every public OpenAPI operation requires certification evidence before promotion.",
  "endpoints": [
    {
      "method": "GET",
      "path": "/health",
      "certification_status": "baseline_certified",
      "owner": "$ServiceName owners",
      "purpose": "Report lightweight service health for diagnostics and platform smoke checks.",
      "when_to_use": "Use for simple service health probes and local diagnostics.",
      "when_not_to_use": "Do not use as a readiness or dependency-quality signal.",
      "request_examples": ["No request body."],
      "response_examples": ["{\"status\":\"ok\",\"service\":\"$ServiceName\"}"],
      "error_examples": ["Unhandled service errors return product-safe Problem Details."],
      "test_evidence": ["tests/integration/test_health.py::test_health_endpoints"],
      "openapi_evidence": "scripts/openapi_quality_gate.py validates summary, description, tag, responses, and examples."
    },
    {
      "method": "GET",
      "path": "/health/live",
      "certification_status": "baseline_certified",
      "owner": "$ServiceName owners",
      "purpose": "Report whether the service process is live.",
      "when_to_use": "Use for liveness probes that should only prove the process is running.",
      "when_not_to_use": "Do not use to decide whether the service is ready for traffic.",
      "request_examples": ["No request body."],
      "response_examples": ["{\"status\":\"live\"}"],
      "error_examples": ["Unhandled service errors return product-safe Problem Details."],
      "test_evidence": ["tests/integration/test_health.py::test_health_endpoints"],
      "openapi_evidence": "scripts/openapi_quality_gate.py validates summary, description, tag, responses, and examples."
    },
    {
      "method": "GET",
      "path": "/health/ready",
      "certification_status": "baseline_certified",
      "owner": "$ServiceName owners",
      "purpose": "Report whether the service is ready to receive traffic.",
      "when_to_use": "Use for readiness probes and deployment routing decisions.",
      "when_not_to_use": "Do not use as a business capability or upstream data-quality signal.",
      "request_examples": ["No request body."],
      "response_examples": ["{\"status\":\"ready\"}", "{\"status\":\"draining\"}"],
      "error_examples": ["503 readiness response returns {\"status\":\"draining\"} during intentional drain."],
      "test_evidence": ["tests/integration/test_health.py::test_health_endpoints", "tests/integration/test_health.py::test_readiness_reports_draining_state"],
      "openapi_evidence": "scripts/openapi_quality_gate.py validates summary, description, tag, responses, and examples."
    },
    {
      "method": "GET",
      "path": "/metadata",
      "certification_status": "baseline_certified",
      "owner": "$ServiceName owners",
      "purpose": "Report service identity and policy-version metadata for operators and validators.",
      "when_to_use": "Use for operator diagnostics, inventory, and validation metadata checks.",
      "when_not_to_use": "Do not use as a business data or supportability endpoint.",
      "request_examples": ["No request body."],
      "response_examples": ["{\"service\":\"$ServiceName\",\"version\":\"0.1.0\",\"roundingPolicyVersion\":\"v1\"}"],
      "error_examples": ["Unhandled service errors return product-safe Problem Details."],
      "test_evidence": ["tests/e2e/test_smoke.py::test_metadata_endpoint"],
      "openapi_evidence": "scripts/openapi_quality_gate.py validates summary, description, tag, responses, and examples."
    }
  ]
}
"@

if (-not $SkipAutomationRegistration) {
  $reposPath = Join-Path $repoRoot "automation/repos.json"
  $serviceMapPath = Join-Path $repoRoot "automation/service-map.json"
  $governancePolicyPath = Join-Path $repoRoot "automation/repository-governance-policy.json"
  $coveragePolicyPath = Join-Path $repoRoot "automation/test-coverage-policy.json"
  $repoPathNormalized = $target.Replace("\", "/")
  $repoName = $ServiceName

  if (Test-Path $reposPath) {
    $repos = Get-Content -Raw $reposPath | ConvertFrom-Json
    if (-not ($repos | Where-Object { $_.name -eq $repoName })) {
      $repos += [pscustomobject]@{
        name = $repoName
        github = "$GithubOrg/$repoName"
        path = $repoPathNormalized
        default_branch = "main"
        preflight_fast_command = "make check"
        preflight_full_command = "make ci"
      }
      $repos | ConvertTo-Json -Depth 8 | Set-Content $reposPath
      Write-Host "Updated automation/repos.json with $repoName"
    }
  }

  if (Test-Path $serviceMapPath) {
    $serviceMap = Get-Content -Raw $serviceMapPath | ConvertFrom-Json
    if (-not ($serviceMap.repos | Where-Object { $_.name -eq $repoName })) {
      $serviceMap.repos += [pscustomobject]@{
        name = $repoName
        pathHint = $repoName
        defaultServices = @($repoName)
        rules = @(
          [pscustomobject]@{
            pathPrefixes = @("src/", "tests/", "pyproject.toml", "Dockerfile")
            services = @($repoName)
          }
        )
      }
      $serviceMap | ConvertTo-Json -Depth 12 | Set-Content $serviceMapPath
      Write-Host "Updated automation/service-map.json with $repoName"
    }
  }
  if (Test-Path $governancePolicyPath) {
    $policy = Get-Content -Raw $governancePolicyPath | ConvertFrom-Json
    if (-not ($policy.repos | Where-Object { $_.name -eq $repoName })) {
      $policy.repos += [pscustomobject]@{
        name = $repoName
        default_branch = "main"
        required_checks = @(
          "PR Merge Gate / Workflow Lint",
          "PR Merge Gate / Lint Typecheck Security",
          "PR Merge Gate / Tests (unit)",
          "PR Merge Gate / Tests (integration)",
          "PR Merge Gate / Tests (e2e)",
          "PR Merge Gate / Coverage Gate (Combined)",
          "PR Merge Gate / Validate Docker Build"
        )
      }
      $policy.repos = @($policy.repos | Sort-Object name)
      $policy | ConvertTo-Json -Depth 8 | Set-Content $governancePolicyPath
      Write-Host "Updated automation/repository-governance-policy.json with $repoName"
    }
  }

  if (Test-Path $coveragePolicyPath) {
    $coverage = Get-Content -Raw $coveragePolicyPath | ConvertFrom-Json
    if (-not ($coverage.services | Where-Object { $_.repo -eq $repoName })) {
      $coverage.services += [pscustomobject]@{
        name = $repoName
        repo = $repoName
        buckets = [pscustomobject]@{
          unit = @("tests/unit")
          integration = @("tests/integration")
          e2e = @("tests/e2e")
        }
        coverage_command = "python -m pytest --cov=src --cov-report=term --cov-fail-under=99"
      }
      $coverage.services = @($coverage.services | Sort-Object name)
      $coverage | ConvertTo-Json -Depth 8 | Set-Content $coveragePolicyPath
      Write-Host "Updated automation/test-coverage-policy.json with $repoName"
    }
  }

  Register-PlatformContextAndAutomation -PlatformRoot $repoRoot -RepoName $repoName -RepoPathNormalized $repoPathNormalized -RepoDescription $Description -RepoBusinessRole $BusinessRole -RepoCategory $Category -RepoRuntime $PrimaryRuntime -RepoUpstreamDependencies $UpstreamDependencies -RepoDownstreamDependencies $DownstreamDependencies -RepoHostName $DevHostName -RepoPort $Port -RepoLogPatterns $RequiredLogPatterns -GithubRepo "$GithubOrg/$repoName"
}

try {
  python -m ruff format $target | Out-Null
  $ruffCachePath = Join-Path $target ".ruff_cache"
  if (Test-Path $ruffCachePath) {
    Remove-Item -Recurse -Force $ruffCachePath
  }
  Write-Host "Applied ruff formatting to scaffold"
}
catch {
  Write-Host "Skipped scaffold formatting (ruff unavailable): $($_.Exception.Message)"
}

Write-Host "Scaffold created: $target"
if ($InitializeGit) {
  Initialize-GitRepository -TargetRepoRoot $target
  Write-Host "Initialized git repository at $target"
}

if ($CreateGithubRepo) {
  if (-not $InitializeGit) {
    throw "-CreateGithubRepo requires -InitializeGit so the remote can be seeded before branch protection is applied."
  }
  Ensure-GitInitialCommit -TargetRepoRoot $target -SvcName $ServiceName
  $requiredChecks = @(
    "PR Merge Gate / Workflow Lint",
    "PR Merge Gate / Lint Typecheck Security",
    "PR Merge Gate / Tests (unit)",
    "PR Merge Gate / Tests (integration)",
    "PR Merge Gate / Tests (e2e)",
    "PR Merge Gate / Coverage Gate (Combined)",
    "PR Merge Gate / Validate Docker Build"
  )
  Configure-GithubRepository -TargetRepoRoot $target -RepoName $ServiceName -RepoDescription $Description -Org $GithubOrg -Visibility $GithubVisibility -EnableDefaults:$EnableGithubDefaults -ProtectMain:$ApplyMainBranchProtection -RequiredChecks $requiredChecks
  Write-Host "Configured GitHub repository $GithubOrg/$ServiceName"
}

Write-Host "Next steps:"
Write-Host "1) make install && make ci"
Write-Host "2) start service-specific RFC slices"
Write-Host "3) raise the feature branch PR once real implementation exists"





