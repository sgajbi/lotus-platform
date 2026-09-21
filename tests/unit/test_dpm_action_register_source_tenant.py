"""Exercise the production DPM seed's source-tenant guard without starting services."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[2]
PROBE = r"""
$ErrorActionPreference = 'Stop'
$tokens = $null
$errors = $null
$scriptPath = Join-Path (Get-Location) 'automation/Invoke-DpmCommandCenterSeed.ps1'
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
  $scriptPath, [ref]$tokens, [ref]$errors
)
if ($errors.Count -ne 0) { throw 'DPM seed does not parse' }
$definition = $ast.Find({
  param($node)
  $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and
    $node.Name -eq 'Resolve-ActionRegisterSourceTenant'
}, $true)
if (-not $definition) { throw 'DPM source-tenant guard is missing' }
. ([scriptblock]::Create($definition.Extent.Text))
$portfolio = $env:LOTUS_TEST_PORTFOLIO_JSON | ConvertFrom-Json
try {
  $tenant = Resolve-ActionRegisterSourceTenant `
    -Portfolio $portfolio -PortfolioId $env:LOTUS_TEST_PORTFOLIO_ID
  Write-Output $tenant
  exit 0
} catch {
  Write-Output $_.Exception.Message
  exit 2
}
"""


@pytest.mark.parametrize(
    (
        "source_tenant",
        "contract_portfolio",
        "requested_portfolio",
        "expected_code",
        "expected_text",
    ),
    [
        ("tenant-sg", "PB_SG_GLOBAL_BAL_001", "PB_SG_GLOBAL_BAL_001", 0, "tenant-sg"),
        (
            "tenant-other",
            "PB_SG_GLOBAL_BAL_001",
            "PB_SG_GLOBAL_BAL_001",
            0,
            "tenant-other",
        ),
        (
            None,
            "PB_SG_GLOBAL_BAL_001",
            "PB_SG_GLOBAL_BAL_001",
            2,
            "portfolio.source_tenant_id",
        ),
        (
            "  ",
            "PB_SG_GLOBAL_BAL_001",
            "PB_SG_GLOBAL_BAL_001",
            2,
            "portfolio.source_tenant_id",
        ),
        (
            " tenant-sg ",
            "PB_SG_GLOBAL_BAL_001",
            "PB_SG_GLOBAL_BAL_001",
            2,
            "portfolio.source_tenant_id",
        ),
        (
            7,
            "PB_SG_GLOBAL_BAL_001",
            "PB_SG_GLOBAL_BAL_001",
            2,
            "portfolio.source_tenant_id",
        ),
        (
            True,
            "PB_SG_GLOBAL_BAL_001",
            "PB_SG_GLOBAL_BAL_001",
            2,
            "portfolio.source_tenant_id",
        ),
        ("tenant-sg", "PB_SG_GLOBAL_BAL_001", "PB_SG_OTHER", 2, "governed portfolio"),
        (
            "tenant-sg",
            "PB_SG_GLOBAL_BAL_001",
            "pb_sg_global_bal_001",
            2,
            "governed portfolio",
        ),
        ("tenant-sg", 7, "7", 2, "governed portfolio"),
        ("tenant-sg", None, "", 2, "governed portfolio"),
    ],
)
def test_action_register_tenant_guard_executes_from_seed(
    source_tenant: str | int | bool | None,
    contract_portfolio: str | int | None,
    requested_portfolio: str,
    expected_code: int,
    expected_text: str,
) -> None:
    portfolio: dict[str, str | int | bool] = {}
    if contract_portfolio is not None:
        portfolio["portfolio_id"] = contract_portfolio
    if source_tenant is not None:
        portfolio["source_tenant_id"] = source_tenant
    env = {
        **os.environ,
        "LOTUS_TEST_PORTFOLIO_JSON": json.dumps(portfolio),
        "LOTUS_TEST_PORTFOLIO_ID": requested_portfolio,
    }
    powershell = shutil.which("pwsh") or shutil.which("powershell")
    assert powershell is not None, (
        "PowerShell is required for the DPM seed contract test"
    )
    result = subprocess.run(
        [powershell, "-NoProfile", "-Command", PROBE],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )

    assert result.returncode == expected_code, result.stderr or result.stdout
    assert expected_text in result.stdout
