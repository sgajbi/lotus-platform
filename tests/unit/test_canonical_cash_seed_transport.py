"""Execute the shipped PowerShell cash boundary and Python CLI over real loopback HTTP."""

import json
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def cash_source():
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            tenant = self.headers.get("X-Tenant-Id")
            requests.append((tenant, self.path, dict(self.headers)))
            status = 403 if tenant == "tenant-denied" else 200
            payload = {
                "portfolio": {"portfolio_id": "PB"},
                "as_of_date": "2026-04-10", "effective_as_of_date": "2026-04-10",
                "as_of_state": "confirmed", "warnings": [], "partial_failures": [],
                "overview": {"cash_weight_pct": 12.5 if tenant == "tenant-a" else 25},
            }
            if tenant == "tenant-degraded":
                payload["warnings"] = ["PRIVATE SOURCE DETAIL"]
            if tenant in {"tenant-zero", "tenant-hundred"}:
                payload["overview"]["cash_weight_pct"] = 0 if tenant == "tenant-zero" else 100
            if tenant == "tenant-precision":
                payload["overview"]["cash_weight_pct"] = "EXACT_PERCENT"
            if tenant == "tenant-negative-zero":
                payload["overview"]["cash_weight_pct"] = -0.0
            self.send_response(status)
            self.end_headers()
            body = json.dumps(payload).replace('"EXACT_PERCENT"', '12.3456789012345678901234567890123456789')
            self.wfile.write(body.encode())

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def invoke_cash_boundary(url, tenant, *, validate_only=False):
    shell = shutil.which("pwsh") or shutil.which("powershell")
    assert shell, "PowerShell is required for the shipped cash adapter proof"
    # Parse the real function, not a test copy. The complete seed/fence boundary is
    # separately executed by test_canonical_runtime_reservation.py.
    seed = (ROOT / "automation/Invoke-DpmCommandCenterSeed.ps1").as_posix()
    resolver = (ROOT / "automation/resolve_canonical_cash_evidence.py").as_posix()
    script = f"""$ErrorActionPreference='Stop'
$ast=[Management.Automation.Language.Parser]::ParseFile('{seed}',[ref]$null,[ref]$null)
$fn=$ast.Find({{param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -eq 'Invoke-CanonicalCashEvidence'}},$true)
. ([scriptblock]::Create($fn.Extent.Text))
$canonicalCashEvidenceScript='{resolver}'
$gatewayApiBaseUrl='{url}'
$resolvedPortfolioId='PB'
$resolvedAsOfDate='2026-04-10'
$resolvedWorkbenchCallerTenantId='{tenant}'
$resolvedTenantId='default'
try {{
  Invoke-CanonicalCashEvidence {'-ValidateCallerOnly' if validate_only else ''} | ConvertTo-Json -Compress
}} catch {{ Write-Output $_.Exception.Message; exit 1 }}
"""
    return subprocess.run([shell, "-NoProfile", "-Command", script],
                          capture_output=True, text=True, timeout=30)


def test_shipped_boundary_isolates_concurrent_caller_scopes(cash_source):
    url, requests = cash_source
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda tenant: invoke_cash_boundary(url, tenant),
                                ["tenant-a", "tenant-b"]))
    for result, ratio in zip(results, ["0.125", "0.25"], strict=True):
        assert result.returncode == 0, result.stdout + result.stderr
        assert json.loads(result.stdout)["normalized_cash_weight"] == ratio
    assert sorted(item[0] for item in requests) == ["tenant-a", "tenant-b"]
    for _, path, headers in requests:
        assert "as_of_date=2026-04-10" in path
        assert "include_performance_snapshot=false" in path
        assert "X-Capabilities" not in headers


@pytest.mark.parametrize(("tenant", "reason", "request_count"), [
    ("", "CALLER_TENANT_INVALID", 0),
    ("tenant-a,tenant-b", "CALLER_TENANT_INVALID", 0),
    ("tenant-denied", "SOURCE_HTTP_403", 1),
    ("tenant-degraded", "SOURCE_DEGRADED", 1),
])
def test_shipped_boundary_retains_only_bounded_refusal(cash_source, tenant, reason, request_count):
    url, requests = cash_source
    result = invoke_cash_boundary(url, tenant)
    assert result.returncode == 1
    assert f"CANONICAL_CASH_{reason}" in result.stdout
    assert "before any persistent seed write" in result.stdout
    assert "PRIVATE SOURCE DETAIL" not in result.stdout + result.stderr
    assert len(requests) == request_count


def test_cheap_caller_validation_does_not_claim_live_admission(cash_source):
    url, requests = cash_source
    result = invoke_cash_boundary(url, "tenant-a", validate_only=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout) == {"state": "caller_scope_validated", "network_performed": False}
    assert requests == []


@pytest.mark.parametrize(("tenant", "ratio"), [
    ("tenant-zero", "0"),
    ("tenant-hundred", "1"),
    ("tenant-negative-zero", "-0"),
    ("tenant-precision", "0.123456789012345678901234567890123456789"),
])
def test_shipped_boundary_preserves_exact_decimal_identity(cash_source, tenant, ratio):
    url, requests = cash_source
    result = invoke_cash_boundary(url, tenant)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["normalized_cash_weight"] == ratio
    assert len(requests) == 1
