from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "automation" / "validate_dev_ingress_smoke.py"


def test_validate_dev_ingress_smoke_cli_returns_zero_and_writes_service_identities(tmp_path: Path) -> None:
    output_json = tmp_path / "dev-ingress-smoke.json"
    output_markdown = tmp_path / "dev-ingress-smoke.md"

    bootstrap = (
        "import automation.validate_dev_ingress_smoke as validator\n"
        "validator._resolve_host = lambda hostname: (True, '127.0.0.1')\n"
        "validator._probe = lambda url, timeout_seconds: (True, 200, '')\n"
        "raise SystemExit(validator.main())\n"
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            bootstrap,
            "--output-json",
            str(output_json),
            "--output-markdown",
            str(output_markdown),
            "--timeout-seconds",
            "1",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    payload = json.loads(output_json.read_text(encoding="utf-8"))
    markdown = output_markdown.read_text(encoding="utf-8")

    assert payload["result"] == "ok"
    assert payload["failed_count"] == 0
    assert {check["service_identity"] for check in payload["checks"]} == {
        "workbench",
        "gateway",
        "manage",
        "performance",
        "report",
        "core-query",
        "core-ingestion",
    }
    assert {check["failure_posture"] for check in payload["checks"]} == {"healthy"}
    assert "gateway_dev_ingress (gateway)" in markdown


def test_validate_dev_ingress_smoke_cli_returns_one_for_dns_failure(tmp_path: Path) -> None:
    output_json = tmp_path / "dev-ingress-smoke.json"
    output_markdown = tmp_path / "dev-ingress-smoke.md"

    bootstrap = (
        "import automation.validate_dev_ingress_smoke as validator\n"
        "def fake_resolve(hostname):\n"
        "    if hostname == 'gateway.dev.lotus':\n"
        "        return (False, 'host not found')\n"
        "    return (True, '127.0.0.1')\n"
        "validator._resolve_host = fake_resolve\n"
        "validator._probe = lambda url, timeout_seconds: (True, 200, '')\n"
        "raise SystemExit(validator.main())\n"
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            bootstrap,
            "--output-json",
            str(output_json),
            "--output-markdown",
            str(output_markdown),
            "--timeout-seconds",
            "1",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 1
    payload = json.loads(output_json.read_text(encoding="utf-8"))
    markdown = output_markdown.read_text(encoding="utf-8")

    assert payload["result"] == "failed"
    assert any(
        check["check_id"] == "gateway_dev_ingress_dns"
        and check["service_identity"] == "gateway"
        and check["failure_posture"] == "dns_resolution_failed"
        for check in payload["checks"]
    )
    assert "gateway_dev_ingress_dns (gateway)" in markdown
    assert "| Check | Passed | Status | Posture | Message |" in markdown
