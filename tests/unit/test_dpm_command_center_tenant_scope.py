"""Prove the shipped DPM seed uses one admitted command-center tenant."""

from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import parse_qs, urlsplit

import pytest


ROOT = Path(__file__).resolve().parents[2]
SEED_SCRIPT = ROOT / "automation" / "Invoke-DpmCommandCenterSeed.ps1"
CONTRACT = (
    ROOT / "context" / "contracts" / "canonical-front-office-demo-data-contract.json"
)


def _powershell() -> str:
    executable = shutil.which("pwsh") or shutil.which("powershell")
    assert executable is not None, "PowerShell is required for the shipped DPM seed test"
    return executable


def _gateway_uri(assignment_name: str) -> str:
    probe = r"""
$ErrorActionPreference = 'Stop'
$ast = [Management.Automation.Language.Parser]::ParseFile('__SEED_SCRIPT__', [ref]$null, [ref]$null)
$assignment = $ast.Find({
  param($node)
  $node -is [Management.Automation.Language.AssignmentStatementAst] -and
  $node.Left -is [Management.Automation.Language.VariableExpressionAst] -and
  $node.Left.VariablePath.UserPath -eq '__ASSIGNMENT_NAME__'
}, $true)
if (-not $assignment) { throw 'Gateway URI assignment is missing' }
$gatewayApiBaseUrl = 'http://gateway.dev.lotus'
$resolvedAsOfDate = '2026-04-10'
$dpm = [pscustomobject]@{
  portfolio_manager_id = 'PM_SG_DPM_001'
  book_id = 'BOOK_SG_BALANCED_DPM'
}
. ([scriptblock]::Create($assignment.Extent.Text))
Write-Output $__ASSIGNMENT_NAME__
""".replace("__SEED_SCRIPT__", str(SEED_SCRIPT).replace("'", "''")).replace(
        "__ASSIGNMENT_NAME__", assignment_name
    )
    result = subprocess.run(
        [_powershell(), "-NoProfile", "-Command", probe],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout.strip()


@pytest.mark.parametrize(
    ("assignment_name", "expected_query"),
    [
        (
            "gatewayCommandCenterUri",
            {
                "portfolio_manager_id": ["PM_SG_DPM_001"],
                "book_id": ["BOOK_SG_BALANCED_DPM"],
                "as_of_date": ["2026-04-10"],
            },
        ),
        ("gatewayCommandCenterPartialUri", {"limit": ["1"]}),
        (
            "gatewayCommandCenterEmptyUri",
            {
                "portfolio_manager_id": ["PM_SG_DPM_001"],
                "book_id": ["BOOK_SG_BALANCED_DPM"],
                "as_of_date": ["2099-01-01"],
            },
        ),
    ],
)
def test_gateway_command_center_uri_has_no_second_tenant_selector(
    assignment_name: str, expected_query: dict[str, list[str]]
) -> None:
    uri = urlsplit(_gateway_uri(assignment_name))

    assert uri.path == "/api/v1/dpm/command-center"
    assert parse_qs(uri.query) == expected_query
    assert "tenant_id" not in parse_qs(uri.query)


def test_seed_refuses_storage_tenant_that_differs_from_admitted_caller(
    tmp_path: Path,
) -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    contract["dpm_command_center"]["tenant_id"] = "default"
    mismatched_contract = tmp_path / "mismatched-contract.json"
    mismatched_contract.write_text(json.dumps(contract), encoding="utf-8")
    output_directory = tmp_path / "evidence"

    result = subprocess.run(
        [
            _powershell(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SEED_SCRIPT),
            "-ContractPath",
            str(mismatched_contract),
            "-OutputDirectory",
            str(output_directory),
            "-PreflightOnly",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )

    assert result.returncode != 0
    diagnostic = re.sub(
        r"\s+",
        " ",
        re.sub(r"\x1b\[[0-9;]*m", "", result.stdout + result.stderr),
    )
    diagnostic = re.sub(r"\s+\|\s+", " ", diagnostic)
    assert "does not match admitted Workbench caller tenant" in diagnostic
    assert not output_directory.exists(), "tenant mismatch must fail before seed evidence or I/O"
