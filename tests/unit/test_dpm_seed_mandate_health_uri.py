"""Exercise shipped PowerShell URIs for tenant-scoped Manage mandate reads."""

import shutil
import subprocess
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest


ROOT = Path(__file__).resolve().parents[2]
SEED_SCRIPT = ROOT / "automation" / "Invoke-DpmCommandCenterSeed.ps1"


def _mandate_uri(seed_script: Path, tenant_id: str, assignment_name: str) -> str:
    shell = shutil.which("pwsh") or shutil.which("powershell")
    assert shell, "PowerShell is required to prove the shipped seed URI"
    script = (
        r"""
$ErrorActionPreference = 'Stop'
$ast = [Management.Automation.Language.Parser]::ParseFile('__SEED_SCRIPT__', [ref]$null, [ref]$null)
$assignment = $ast.Find({
  param($node)
  $node -is [Management.Automation.Language.AssignmentStatementAst] -and
  $node.Left -is [Management.Automation.Language.VariableExpressionAst] -and
  $node.Left.VariablePath.UserPath -eq '__ASSIGNMENT_NAME__'
}, $true)
if (-not $assignment) { throw 'Mandate URI assignment is missing' }
$manageApiBaseUrl = 'http://manage.dev.lotus'
$resolvedMandateId = 'MANDATE_001'
$resolvedPortfolioId = 'PORTFOLIO_001'
$resolvedTenantId = '__TENANT_ID__'
. ([scriptblock]::Create($assignment.Extent.Text))
Write-Output $__ASSIGNMENT_NAME__
""".replace("__SEED_SCRIPT__", str(seed_script).replace("'", "''"))
        .replace("__TENANT_ID__", tenant_id.replace("'", "''"))
        .replace("__ASSIGNMENT_NAME__", assignment_name)
    )
    result = subprocess.run(
        [shell, "-NoProfile", "-Command", script],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout.strip()


def _assert_mandate_tenant_query(
    seed_script: Path, tenant_id: str, assignment_name: str, expected_path: str
) -> None:
    uri = urlsplit(_mandate_uri(seed_script, tenant_id, assignment_name))
    assert uri.path == expected_path
    assert parse_qs(uri.query) == {"tenant_id": [tenant_id]}


@pytest.mark.parametrize("tenant_id", ["default", "tenant with/slash & space"])
def test_mandate_health_uri_carries_exact_contract_tenant(tenant_id: str) -> None:
    _assert_mandate_tenant_query(
        SEED_SCRIPT,
        tenant_id,
        "recalculateHealthUri",
        "/api/v1/mandates/MANDATE_001/health/recalculate",
    )


@pytest.mark.parametrize("tenant_id", ["default", "tenant with/slash & space"])
def test_mandate_lookup_uri_carries_exact_contract_tenant(tenant_id: str) -> None:
    _assert_mandate_tenant_query(
        SEED_SCRIPT,
        tenant_id,
        "manageLookupUri",
        "/api/v1/mandates/by-portfolio/PORTFOLIO_001",
    )


def test_regression_rejects_omitted_mandate_tenant_query(tmp_path: Path) -> None:
    mutated_script = tmp_path / SEED_SCRIPT.name
    source = SEED_SCRIPT.read_text(encoding="utf-8")
    assert '"?tenant_id=$([uri]::EscapeDataString($resolvedTenantId))"' in source
    mutated_script.write_text(
        source.replace(
            '"?tenant_id=$([uri]::EscapeDataString($resolvedTenantId))"',
            '""',
            1,
        ),
        encoding="utf-8",
    )
    with pytest.raises(AssertionError):
        _assert_mandate_tenant_query(
            mutated_script,
            "default",
            "recalculateHealthUri",
            "/api/v1/mandates/MANDATE_001/health/recalculate",
        )


def test_regression_rejects_omitted_mandate_lookup_tenant_query(tmp_path: Path) -> None:
    mutated_script = tmp_path / SEED_SCRIPT.name
    source = SEED_SCRIPT.read_text(encoding="utf-8")
    lookup_assignment = (
        "$manageLookupUri = (\n"
        '  "$manageApiBaseUrl/api/v1/mandates/by-portfolio/$resolvedPortfolioId" +\n'
        '  "?tenant_id=$([uri]::EscapeDataString($resolvedTenantId))"\n'
        ")"
    )
    assert lookup_assignment in source
    mutated_script.write_text(
        source.replace(
            lookup_assignment,
            '$manageLookupUri = "$manageApiBaseUrl/api/v1/mandates/by-portfolio/$resolvedPortfolioId"',
            1,
        ),
        encoding="utf-8",
    )
    with pytest.raises(AssertionError):
        _assert_mandate_tenant_query(
            mutated_script,
            "default",
            "manageLookupUri",
            "/api/v1/mandates/by-portfolio/PORTFOLIO_001",
        )
