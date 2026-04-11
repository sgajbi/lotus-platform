param(
  [Parameter(Mandatory = $true)]
  [string]$ServiceName,
  [string]$Description = "Lotus backend service",
  [string]$DestinationRoot = "C:/Users/Sandeep/projects",
  [string]$GithubOrg = "sgajbi",
  [int]$Port = 8000,
  [switch]$Force,
  [switch]$SkipAutomationRegistration
)

$ErrorActionPreference = "Stop"

if ($ServiceName -notmatch "^lotus-[a-z0-9-]+$") {
  throw "ServiceName must follow lotus-* naming (example: lotus-risk)."
}

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptRoot "..")
$templateRoot = Join-Path $repoRoot "platform-standards/templates"
$target = Join-Path $DestinationRoot $ServiceName

if ((Test-Path $target) -and -not $Force) {
  throw "Target path exists: $target. Use -Force to overwrite files."
}

$dirs = @(
  ".github/workflows",
  "requirements",
  "src/app",
  "src/app/contracts",
  "src/app/middleware",
  "tests/unit",
  "tests/integration",
  "tests/e2e",
  "scripts",
  "docs/standards",
  "docs/rfcs"
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
$makefile = $makefile -replace [regex]::Escape("lint:`n`truff check .`n`truff format --check ."), "lint:`n`truff check .`n`truff format --check .`n`t`$(MAKE) monetary-float-guard"
$makefile = $makefile -replace [regex]::Escape("typecheck:"), "monetary-float-guard:`n`tpython scripts/check_monetary_float_usage.py`n`ntypecheck:"
$makefile = $makefile -replace [regex]::Escape("test-coverage:`n`tCOVERAGE_FILE=.coverage.unit python -m pytest tests/unit --cov=src --cov-report=`n`tCOVERAGE_FILE=.coverage.integration python -m pytest tests/integration --cov=src --cov-report=`n`tCOVERAGE_FILE=.coverage.e2e python -m pytest tests/e2e --cov=src --cov-report=`n`tpython -m coverage combine .coverage.unit .coverage.integration .coverage.e2e`n`tpython -m coverage report --fail-under=99"), "test-coverage:`n`tCOVERAGE_FILE=.coverage.unit python -m pytest tests/unit --cov=src --cov-report=`n`tCOVERAGE_FILE=.coverage.integration python -m pytest tests/integration --cov=src --cov-report=`n`tCOVERAGE_FILE=.coverage.e2e python -m pytest tests/e2e --cov=src --cov-report=`n`tpython scripts/coverage_gate.py"
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
  "mypy" = "1.19.0"
  "pytest" = "9.0.0"
  "pytest-asyncio" = "1.2.0"
  "pytest-cov" = "7.0.0"
  "httpx" = "0.28.0"
  "coverage" = "7.13.0"
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
from fastapi import FastAPI, Response, status
from prometheus_fastapi_instrumentator import Instrumentator
from app.middleware.correlation import CorrelationIdMiddleware

SERVICE_NAME = "$ServiceName"
SERVICE_VERSION = "0.1.0"
ROUNDING_POLICY_VERSION = "v1"

app = FastAPI(title=SERVICE_NAME, version=SERVICE_VERSION)
app.add_middleware(CorrelationIdMiddleware, service_name=SERVICE_NAME)
Instrumentator().instrument(app).expose(app)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/health/live")
async def health_live() -> dict[str, str]:
    return {"status": "live"}


@app.get("/health/ready")
async def health_ready(response: Response) -> dict[str, str]:
    if bool(getattr(app.state, "is_draining", False)):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "draining"}
    return {"status": "ready"}


@app.get("/metadata")
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
        request.state.correlation_id = correlation_id
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000.0
        response.headers["X-Correlation-Id"] = correlation_id
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


def main() -> None:
    spec = app.openapi()
    if "paths" not in spec or not spec["paths"]:
        raise SystemExit("OpenAPI gate failed: no paths defined")
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

$unitTest = @"
from app.main import SERVICE_NAME


def test_service_name_is_lotus_prefixed() -> None:
    assert SERVICE_NAME.startswith("lotus-")
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


def test_correlation_header_propagation() -> None:
    client = TestClient(app)
    response = client.get("/health", headers={"X-Correlation-Id": "corr-123"})
    assert response.status_code == 200
    assert response.headers["X-Correlation-Id"] == "corr-123"
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
  "python -m pip install -e '.[dev]'",
  "python -m ruff check . && python -m ruff format --check .",
  "python -m mypy --config-file mypy.ini",
  "python scripts/openapi_quality_gate.py",
  "python -m pytest tests/unit tests/integration tests/e2e",
  "python scripts/coverage_gate.py",
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
}

try {
  python -m ruff format $target | Out-Null
  Write-Host "Applied ruff formatting to scaffold"
}
catch {
  Write-Host "Skipped scaffold formatting (ruff unavailable): $($_.Exception.Message)"
}

Write-Host "Scaffold created: $target"
Write-Host "Next steps:"
Write-Host "1) git init + set origin"
Write-Host "2) make install && make ci"
Write-Host "3) apply branch protection + auto-merge governance"





