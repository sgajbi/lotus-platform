param(
  [Parameter(Mandatory = $true)]
  [string]$ServiceName,
  [string]$Description = "Lotus backend service",
  [string]$DestinationRoot = "C:/Users/Sandeep/projects",
  [string]$GithubOrg = "sgajbi",
  [int]$Port = 8000,
  [string]$BusinessRole = "",
  [string]$Category = "domain-service",
  [string]$PrimaryRuntime = "python-fastapi",
  [string[]]$UpstreamDependencies = @(),
  [string[]]$DownstreamDependencies = @(),
  [string]$DevHostName = "",
  [string[]]$RequiredLogPatterns = @("correlation", "trace", "service"),
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
    '2. `src/app/contracts/`: API and contract models.',
    '3. `src/app/middleware/`: shared request middleware.',
    '4. `tests/unit`, `tests/integration`, `tests/e2e`: test pyramid baseline.',
    '5. `docs/standards/`: repository standards placeholders to be replaced with service truth.',
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
    '',
    '## Validation And CI Expectations',
    '',
    ('`' + $SvcName + '` follows the standard Lotus backend lane model. Required baseline checks include lint,'),
    'typecheck, OpenAPI quality, unit/integration/e2e tests, coverage gate, security audit, and Docker',
    'build validation.',
    '',
    '## Standards And RFCs That Govern This Repository',
    '',
    '1. `lotus-platform/rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`',
    '2. `lotus-platform/context/LOTUS-QUICKSTART-CONTEXT.md`',
    '3. `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`',
    '4. service-specific RFCs once implementation begins',
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
    [string]$SvcDescription
  )

  $wikiRoot = Join-Path $TargetRepoRoot "wiki"
  New-Item -ItemType Directory -Force -Path $wikiRoot | Out-Null
  $wikiHome = @(
    "# $SvcName Wiki",
    "",
    $SvcDescription,
    "",
    "## Current posture",
    "",
    "- repo scaffolded from Lotus platform automation",
    "- wiki source lives in-repo and must be published through `lotus-platform` automation",
    "- replace this page with operator-facing truth as implementation becomes real"
  ) -join "`n"
  Set-Content -Path (Join-Path $wikiRoot "Home.md") -Value $wikiHome
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
    [string[]]$RepoLogPatterns,
    [string]$GithubRepo
  )

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
    gh repo edit $repoSlug --enable-issues --enable-wiki --enable-auto-merge --enable-squash-merge --enable-rebase-merge --delete-branch-on-merge | Out-Null
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
      required_linear_history = $false
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
  "src/app/contracts",
  "src/app/middleware",
  "docs/operations",
  "tests/unit",
  "tests/integration",
  "tests/e2e",
  "scripts",
  "docs/standards",
  "docs/rfcs",
  "evidence/rfc-implementation",
  "supported-features",
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

$makefilePath = Join-Path $target "Makefile"
$makefile = Get-Content $makefilePath -Raw
$makefile = $makefile -replace [regex]::Escape(".PHONY: install lint typecheck openapi-gate test test-unit test-integration test-e2e test-coverage security-audit check ci docker-build clean"), ".PHONY: install lint monetary-float-guard typecheck openapi-gate test test-unit test-integration test-e2e test-coverage coverage-gate security-audit check ci docker-build clean"
$makefile = $makefile -replace [regex]::Escape("lint:`n`t`$(VENV_PYTHON) -m ruff check .`n`t`$(VENV_PYTHON) -m ruff format --check ."), "lint:`n`t`$(VENV_PYTHON) -m ruff check .`n`t`$(VENV_PYTHON) -m ruff format --check .`n`t`$(MAKE) monetary-float-guard"
$makefile = $makefile -replace [regex]::Escape("typecheck:"), "monetary-float-guard:`n`t`$(VENV_PYTHON) scripts/check_monetary_float_usage.py`n`ntypecheck:"
$makefile = $makefile -replace [regex]::Escape("test-coverage:`n`tCOVERAGE_FILE=.coverage.unit `$(VENV_PYTHON) -m pytest tests/unit --cov=src --cov-report=`n`tCOVERAGE_FILE=.coverage.integration `$(VENV_PYTHON) -m pytest tests/integration --cov=src --cov-report=`n`tCOVERAGE_FILE=.coverage.e2e `$(VENV_PYTHON) -m pytest tests/e2e --cov=src --cov-report=`n`t`$(VENV_PYTHON) -m coverage combine .coverage.unit .coverage.integration .coverage.e2e`n`t`$(VENV_PYTHON) -m coverage report --fail-under=99"), "test-coverage:`n`tCOVERAGE_FILE=.coverage.unit `$(VENV_PYTHON) -m pytest tests/unit --cov=src --cov-report=`n`tCOVERAGE_FILE=.coverage.integration `$(VENV_PYTHON) -m pytest tests/integration --cov=src --cov-report=`n`tCOVERAGE_FILE=.coverage.e2e `$(VENV_PYTHON) -m pytest tests/e2e --cov=src --cov-report=`n`t`$(VENV_PYTHON) scripts/coverage_gate.py"
$makefile = $makefile -replace [regex]::Escape("ci: lint typecheck openapi-gate test-integration test-e2e test-coverage security-audit"), "ci: lint typecheck openapi-gate test-integration test-e2e test-coverage security-audit"
Set-Content $makefilePath $makefile

$runtimeDependencies = [ordered]@{
  "fastapi" = "0.133.0"
  "uvicorn" = "0.41.0"
  "pydantic" = "2.12.0"
  "pydantic-settings" = "2.13.0"
  "prometheus-fastapi-instrumentator" = "7.1.0"
}

$developmentDependencies = [ordered]@{
  "ruff" = "0.15.0"
  "mypy" = "1.19.1"
  "pytest" = "9.0.3"
  "pytest-asyncio" = "1.3.0"
  "pytest-cov" = "7.1.0"
  "httpx" = "0.28.0"
  "coverage" = "7.13.5"
  "pip-audit" = "2.10.0"
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
from app.errors import problem_response
from app.middleware.correlation import CorrelationIdMiddleware
from app.observability import configure_logging, log_event

SERVICE_NAME = "$ServiceName"
SERVICE_VERSION = "0.1.0"
ROUNDING_POLICY_VERSION = "v1"

app = FastAPI(title=SERVICE_NAME, version=SERVICE_VERSION)
app.add_middleware(CorrelationIdMiddleware, service_name=SERVICE_NAME)
Instrumentator().instrument(app).expose(app, include_in_schema=False)
configure_logging()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> Response:
    log_event(
        "request.validation_failed",
        service=SERVICE_NAME,
        path=str(request.url.path),
        method=request.method,
        error_category="validation",
    )
    return problem_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        code="invalid_request",
        title="Invalid request",
        detail="Request validation failed. Correct the request fields and retry.",
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> Response:
    log_event(
        "request.unhandled_error",
        service=SERVICE_NAME,
        level="ERROR",
        path=str(request.url.path),
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
Set-Content -Path (Join-Path $target "src/app/contracts/__init__.py") -Value ""
Set-Content -Path (Join-Path $target "src/app/middleware/__init__.py") -Value ""

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

$observabilityPy = @"
from __future__ import annotations

import json
import logging
from typing import Literal

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


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
"@
Set-Content -Path (Join-Path $target "src/app/observability.py") -Value $observabilityPy

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

$unitTest = @"
from app.errors import ProblemDetails
from app.main import SERVICE_NAME


def test_service_name_is_lotus_prefixed() -> None:
    assert SERVICE_NAME.startswith("lotus-")


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
"@
Set-Content -Path (Join-Path $target "tests/unit/test_service_contract.py") -Value $unitTest

$integrationTest = @"
from fastapi.testclient import TestClient
from app.main import app


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
Write-WikiBaseline -TargetRepoRoot $target -SvcName $ServiceName -SvcDescription $Description

$standardsDocs = @{
  "docs/standards/enterprise-readiness.md" = "# Enterprise Readiness`n`n- Service: $ServiceName`n- Status: baseline adopted.";
  "docs/standards/scalability-availability.md" = "# Scalability and Availability`n`n- Service: $ServiceName`n- Baseline health/readiness, resilience, and metrics adopted.";
  "docs/standards/durability-consistency.md" = "# Durability and Consistency`n`n- Service: $ServiceName`n- Core write semantics and idempotency policy baseline adopted.";
  "docs/standards/rounding-precision.md" = "# Rounding and Precision`n`n- Service: $ServiceName`n- Canonical precision policy must be used for monetary outputs.";
  "docs/standards/data-model-ownership.md" = "# Data Model Ownership`n`n- Service: $ServiceName`n- Owns only its bounded-context schema.";
  "docs/standards/migration-contract.md" = "# Migration Contract`n`n- Service: $ServiceName`n- Versioned migrations + CI smoke gate required.";
}

foreach ($entry in $standardsDocs.GetEnumerator()) {
  Set-Content -Path (Join-Path $target $entry.Key) -Value $entry.Value
}

$readme = @(
  "# $ServiceName",
  "",
  "$Description",
  "",
  "## Quick Start",
  "",
  '```powershell',
  "make install",
  "make lint",
  "make typecheck",
  "make openapi-gate",
  "make check",
  "make ci",
  '```',
  "",
  '```powershell',
  ".venv\\Scripts\\python.exe -m pip install -e '.[dev]'",
  ".venv\\Scripts\\python.exe -m ruff check . && .venv\\Scripts\\python.exe -m ruff format --check .",
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
  "- Platform standards docs: docs/standards/"
) -join "`n"
Set-Content -Path (Join-Path $target "README.md") -Value $readme

Set-Content -Path (Join-Path $target "docs/rfcs/README.md") -Value "# RFC Index`n"
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

Evidence must name the repository, branch, commit SHA, PR number, command, endpoint or route,
operational identifiers, and result. Do not store sensitive client, portfolio, holding,
transaction, entitlement, request-body, response-body, trace, or correlation details here unless a
later security review explicitly certifies the artifact.
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

  Register-PlatformContextAndAutomation -PlatformRoot $repoRoot -RepoName $repoName -RepoPathNormalized $repoPathNormalized -RepoDescription $Description -RepoBusinessRole $BusinessRole -RepoCategory $Category -RepoRuntime $PrimaryRuntime -RepoUpstreamDependencies $UpstreamDependencies -RepoDownstreamDependencies $DownstreamDependencies -RepoHostName $DevHostName -RepoLogPatterns $RequiredLogPatterns -GithubRepo "$GithubOrg/$repoName"
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





