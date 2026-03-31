from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "automation" / "explain_dev_ingress_status.py"


def test_explain_dev_ingress_status_cli_writes_dns_not_configured_artifacts(tmp_path: Path) -> None:
    smoke_path = tmp_path / "dev-ingress-smoke.json"
    staged_hosts_path = tmp_path / "hosts.merged"
    output_json = tmp_path / "dev-ingress-status.json"
    output_markdown = tmp_path / "dev-ingress-status.md"

    smoke_path.write_text(
        json.dumps(
            {
                "result": "failed",
                "failed_count": 2,
                "checks": [
                    {"check_id": "gateway_dev_ingress_dns", "passed": False},
                    {"check_id": "gateway_dev_ingress", "passed": False},
                ],
            }
        ),
        encoding="utf-8",
    )
    staged_hosts_path.write_text(
        "# >>> lotus-platform dev ingress >>>\n"
        "127.0.0.1 gateway.dev.lotus\n"
        "# <<< lotus-platform dev ingress <<<\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--smoke-json-path",
            str(smoke_path),
            "--staged-hosts-path",
            str(staged_hosts_path),
            "--output-json",
            str(output_json),
            "--output-markdown",
            str(output_markdown),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 1
    payload = json.loads(output_json.read_text(encoding="utf-8"))
    markdown = output_markdown.read_text(encoding="utf-8")

    assert payload["status"] == "dns_not_configured"
    assert payload["evidence"]["staged_hostnames"] == ["gateway.dev.lotus"]
    assert "Apply the staged hosts block" in markdown


def test_explain_dev_ingress_status_cli_returns_zero_when_ready(tmp_path: Path) -> None:
    smoke_path = tmp_path / "dev-ingress-smoke.json"
    output_json = tmp_path / "dev-ingress-status.json"
    output_markdown = tmp_path / "dev-ingress-status.md"

    smoke_path.write_text(
        json.dumps({"result": "ok", "failed_count": 0, "checks": []}),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--smoke-json-path",
            str(smoke_path),
            "--output-json",
            str(output_json),
            "--output-markdown",
            str(output_markdown),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    payload = json.loads(output_json.read_text(encoding="utf-8"))

    assert payload["status"] == "ready"
    assert "canonical local entrypoints" in output_markdown.read_text(encoding="utf-8")
