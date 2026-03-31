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
                    {"check_id": "gateway_dev_ingress_dns", "service_identity": "gateway", "passed": False},
                    {"check_id": "gateway_dev_ingress", "service_identity": "gateway", "passed": False},
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


def test_explain_dev_ingress_status_cli_writes_affected_services_for_http_failures(tmp_path: Path) -> None:
    smoke_path = tmp_path / "dev-ingress-smoke.json"
    output_json = tmp_path / "dev-ingress-status.json"
    output_markdown = tmp_path / "dev-ingress-status.md"

    smoke_path.write_text(
        json.dumps(
            {
                "result": "failed",
                "failed_count": 2,
                "checks": [
                    {"check_id": "gateway_dev_ingress_dns", "service_identity": "gateway", "passed": True, "failure_posture": "healthy"},
                    {"check_id": "gateway_dev_ingress", "service_identity": "gateway", "passed": False, "status": 502, "failure_posture": "http_error"},
                    {"check_id": "core_query_dev_ingress_dns", "service_identity": "core-query", "passed": True, "failure_posture": "healthy"},
                    {"check_id": "core_query_dev_ingress", "service_identity": "core-query", "passed": False, "status": 503, "failure_posture": "http_error"},
                ],
            }
        ),
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

    assert completed.returncode == 1
    payload = json.loads(output_json.read_text(encoding="utf-8"))
    markdown = output_markdown.read_text(encoding="utf-8")

    assert payload["status"] == "services_unreachable"
    assert payload["evidence"]["affected_services"] == ["core-query", "gateway"]
    assert payload["evidence"]["affected_compose_services"] == ["lotus-core-query", "bff"]
    assert payload["evidence"]["failing_http_postures"] == ["http_error", "http_error"]
    assert "docker compose logs --tail=200 lotus-core-query bff" in markdown
    assert "docker compose up -d lotus-core-query bff" in markdown


def test_explain_dev_ingress_status_cli_identifies_ingress_edge_failure(tmp_path: Path) -> None:
    smoke_path = tmp_path / "dev-ingress-smoke.json"
    output_json = tmp_path / "dev-ingress-status.json"
    output_markdown = tmp_path / "dev-ingress-status.md"

    smoke_path.write_text(
        json.dumps(
            {
                "result": "failed",
                "failed_count": 4,
                "checks": [
                    {"check_id": "gateway_dev_ingress_dns", "service_identity": "gateway", "passed": True, "failure_posture": "healthy"},
                    {"check_id": "gateway_dev_ingress", "service_identity": "gateway", "passed": False, "status": None, "evidence": ["connection refused"], "failure_posture": "connection_refused"},
                    {"check_id": "workbench_dev_ingress_dns", "service_identity": "workbench", "passed": True, "failure_posture": "healthy"},
                    {"check_id": "workbench_dev_ingress", "service_identity": "workbench", "passed": False, "status": None, "evidence": ["connection refused"], "failure_posture": "connection_refused"},
                ],
            }
        ),
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

    assert completed.returncode == 1
    payload = json.loads(output_json.read_text(encoding="utf-8"))
    markdown = output_markdown.read_text(encoding="utf-8")

    assert payload["status"] == "ingress_unreachable"
    assert payload["evidence"]["failing_http_postures"] == ["connection_refused", "connection_refused"]
    assert payload["evidence"]["likely_ingress_failure"] is True
    assert "docker compose up -d dev-ingress" in markdown


def test_explain_dev_ingress_status_cli_uses_logs_first_for_timeout_failures(tmp_path: Path) -> None:
    smoke_path = tmp_path / "dev-ingress-smoke.json"
    output_json = tmp_path / "dev-ingress-status.json"
    output_markdown = tmp_path / "dev-ingress-status.md"

    smoke_path.write_text(
        json.dumps(
            {
                "result": "failed",
                "failed_count": 2,
                "checks": [
                    {"check_id": "performance_dev_ingress_dns", "service_identity": "performance", "passed": True, "failure_posture": "healthy"},
                    {"check_id": "performance_dev_ingress", "service_identity": "performance", "passed": False, "status": None, "failure_posture": "timeout"},
                    {"check_id": "report_dev_ingress_dns", "service_identity": "report", "passed": True, "failure_posture": "healthy"},
                    {"check_id": "report_dev_ingress", "service_identity": "report", "passed": False, "status": None, "failure_posture": "timeout"},
                ],
            }
        ),
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

    assert completed.returncode == 1
    payload = json.loads(output_json.read_text(encoding="utf-8"))
    markdown = output_markdown.read_text(encoding="utf-8")

    assert payload["status"] == "services_unreachable"
    assert payload["evidence"]["failing_http_postures"] == ["timeout", "timeout"]
    assert "docker compose logs --tail=200 lotus-performance lotus-report" in markdown
    assert "docker compose up -d lotus-performance lotus-report" in markdown
