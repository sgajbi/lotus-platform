from __future__ import annotations

import argparse
import json
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_JSON = ROOT / "output" / "dev-ingress-smoke.json"
DEFAULT_OUTPUT_MD = ROOT / "output" / "dev-ingress-smoke.md"


@dataclass(frozen=True)
class EndpointCheck:
    check_id: str
    service_identity: str
    url: str
    expected_status: int = 200


def _result(
    check_id: str,
    service_identity: str,
    passed: bool,
    message: str,
    evidence: list[str],
    failure_posture: str,
    status: int | None = None,
) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "service_identity": service_identity,
        "passed": passed,
        "message": message,
        "evidence": evidence,
        "failure_posture": failure_posture,
        "status": status,
    }


def _infer_failure_posture(status: int | None, error: str) -> str:
    if status is not None:
        return "http_error"

    lowered = error.lower()
    if "timed out" in lowered or "timeout" in lowered:
        return "timeout"
    if "connection refused" in lowered or "actively refused" in lowered:
        return "connection_refused"
    return "transport_error"


def _probe(url: str, timeout_seconds: int) -> tuple[bool, int | None, str]:
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            return True, int(response.status), ""
    except urllib.error.HTTPError as exc:
        return False, int(exc.code), str(exc)
    except Exception as exc:  # pragma: no cover - exercised indirectly in tests
        return False, None, str(exc)


def _resolve_host(hostname: str) -> tuple[bool, str]:
    try:
        address = socket.gethostbyname(hostname)
        return True, address
    except OSError as exc:
        return False, str(exc)


def build_dev_ingress_checks() -> list[EndpointCheck]:
    return [
        EndpointCheck("workbench_dev_ingress", "workbench", "http://workbench.dev.lotus/"),
        EndpointCheck("gateway_dev_ingress", "gateway", "http://gateway.dev.lotus/health/ready"),
        EndpointCheck("manage_dev_ingress", "manage", "http://manage.dev.lotus/health/ready"),
        EndpointCheck("performance_dev_ingress", "performance", "http://performance.dev.lotus/health/ready"),
        EndpointCheck("report_dev_ingress", "report", "http://report.dev.lotus/health/ready"),
        EndpointCheck("core_query_dev_ingress", "core-query", "http://core-query.dev.lotus/health/ready"),
        EndpointCheck("core_control_dev_ingress", "core-control", "http://core-control.dev.lotus/health/ready"),
        EndpointCheck("core_ingestion_dev_ingress", "core-ingestion", "http://core-ingestion.dev.lotus/health/ready"),
    ]


def validate_dev_ingress_smoke(timeout_seconds: int = 10) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    for endpoint in build_dev_ingress_checks():
        hostname = endpoint.url.split("/")[2]
        host_resolved, resolution = _resolve_host(hostname)
        if not host_resolved:
            checks.append(
                _result(
                    f"{endpoint.check_id}_dns",
                    endpoint.service_identity,
                    False,
                    f"Hostname {hostname} does not resolve locally.",
                    [resolution],
                    "dns_resolution_failed",
                )
            )
            checks.append(
                _result(
                    endpoint.check_id,
                    endpoint.service_identity,
                    False,
                    f"Canonical dev ingress endpoint {endpoint.url} is not reachable because hostname resolution failed.",
                    [resolution],
                    "dns_resolution_failed",
                )
            )
            continue

        checks.append(
            _result(
                f"{endpoint.check_id}_dns",
                endpoint.service_identity,
                True,
                f"Hostname {hostname} resolves locally.",
                [resolution],
                "healthy",
            )
        )

        ok, status, error = _probe(endpoint.url, timeout_seconds)
        checks.append(
            _result(
                endpoint.check_id,
                endpoint.service_identity,
                ok and status == endpoint.expected_status,
                (
                    f"Canonical dev ingress endpoint {endpoint.url} returned {status}."
                    if ok
                    else f"Canonical dev ingress endpoint {endpoint.url} did not return the expected status."
                ),
                [error or endpoint.url],
                "healthy" if ok and status == endpoint.expected_status else _infer_failure_posture(status, error),
                status=status,
            )
        )

    failures = [check for check in checks if not check["passed"]]
    return {
        "generated_at": datetime.now().astimezone().isoformat(),
        "result": "ok" if not failures else "failed",
        "checks": checks,
        "failed_count": len(failures),
    }


def _write_markdown(output_path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Dev Ingress Smoke Validation",
        "",
        f"- Generated: {payload['generated_at']}",
        f"- Result: {payload['result']}",
        f"- Failed checks: {payload['failed_count']}",
        "",
        "| Check | Passed | Status | Posture | Message |",
        "|---|---|---|---|---|",
    ]
    for check in payload["checks"]:
        passed = "true" if check["passed"] else "false"
        status = "" if check["status"] is None else str(check["status"])
        lines.append(f"| {check['check_id']} ({check['service_identity']}) | {passed} | {status} | {check['failure_posture']} | {check['message']} |")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-markdown", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--timeout-seconds", type=int, default=10)
    args = parser.parse_args()

    payload = validate_dev_ingress_smoke(timeout_seconds=args.timeout_seconds)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_markdown(args.output_markdown, payload)

    print(f"Wrote {args.output_json}")
    print(f"Wrote {args.output_markdown}")
    return 0 if payload["result"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
