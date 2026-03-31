from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SMOKE_PATH = ROOT / "output" / "dev-ingress-smoke.json"
DEFAULT_STAGED_HOSTS_PATH = ROOT / "output" / "hosts-preview" / "hosts.merged"
DEFAULT_OUTPUT_JSON = ROOT / "output" / "dev-ingress-status.json"
DEFAULT_OUTPUT_MD = ROOT / "output" / "dev-ingress-status.md"
BLOCK_START = "# >>> lotus-platform dev ingress >>>"
BLOCK_END = "# <<< lotus-platform dev ingress <<<"
COMPOSE_SERVICE_BY_IDENTITY = {
    "workbench": "ui",
    "gateway": "bff",
    "manage": "lotus-manage",
    "performance": "lotus-performance",
    "report": "lotus-report",
    "core-query": "lotus-core-query",
    "core-ingestion": "lotus-core-ingestion",
}


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _load_text(path: Path) -> str | None:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def _extract_staged_hostnames(text: str | None) -> list[str]:
    if not text:
        return []

    relevant_text = text
    if BLOCK_START in text and BLOCK_END in text:
        start_index = text.index(BLOCK_START) + len(BLOCK_START)
        end_index = text.index(BLOCK_END, start_index)
        relevant_text = text[start_index:end_index]

    hostnames: list[str] = []
    for raw_line in relevant_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            hostnames.extend(parts[1:])
    return hostnames


def explain_dev_ingress_status(
    smoke_payload: dict[str, Any] | None,
    staged_hosts_text: str | None,
) -> dict[str, Any]:
    staged_hostnames = _extract_staged_hostnames(staged_hosts_text)
    staged_hosts_present = bool(staged_hostnames)

    if smoke_payload is None:
        return {
            "generated_at": datetime.now().astimezone().isoformat(),
            "status": "missing_smoke_result",
            "summary": "No dev ingress smoke result is available yet.",
            "next_steps": [
                "Run `powershell -ExecutionPolicy Bypass -File automation/Validate-Dev-Ingress-Smoke.ps1`.",
            ],
            "evidence": {
                "staged_hosts_present": staged_hosts_present,
                "staged_hostnames": staged_hostnames,
            },
        }

    failed_checks = [check for check in smoke_payload.get("checks", []) if not check.get("passed")]
    failed_dns_checks = [check for check in failed_checks if str(check.get("check_id", "")).endswith("_dns")]
    failed_http_checks = [check for check in failed_checks if not str(check.get("check_id", "")).endswith("_dns")]

    if smoke_payload.get("result") == "ok":
        return {
            "generated_at": datetime.now().astimezone().isoformat(),
            "status": "ready",
            "summary": "Canonical dev ingress is healthy.",
            "next_steps": [
                "Use `*.dev.lotus` endpoints as the canonical local entrypoints.",
            ],
            "evidence": {
                "failed_count": 0,
                "staged_hosts_present": staged_hosts_present,
                "staged_hostnames": staged_hostnames,
            },
        }

    if failed_dns_checks:
        next_steps = []
        if staged_hosts_present:
            next_steps.append(
                "Apply the staged hosts block from `output/hosts-preview/hosts.merged` from an elevated shell."
            )
        else:
            next_steps.append(
                "Run `powershell -ExecutionPolicy Bypass -File automation/Sync-Dev-Ingress-Hosts.ps1 -Apply` from an elevated shell."
            )
        next_steps.append(
            "Re-run `powershell -ExecutionPolicy Bypass -File automation/Validate-Dev-Ingress-Smoke.ps1` after the hosts file is updated."
        )
        return {
            "generated_at": datetime.now().astimezone().isoformat(),
            "status": "dns_not_configured",
            "summary": "Canonical dev ingress hostnames are not resolving locally.",
            "next_steps": next_steps,
            "evidence": {
                "failed_dns_check_ids": [check["check_id"] for check in failed_dns_checks],
                "staged_hosts_present": staged_hosts_present,
                "staged_hostnames": staged_hostnames,
            },
        }

    if failed_http_checks:
        affected_services = sorted(
            {
                str(check.get("service_identity") or str(check["check_id"]).removesuffix("_dns").removesuffix("_dev_ingress").replace("_", "-"))
                for check in failed_http_checks
            }
        )
        affected_compose_services = [
            COMPOSE_SERVICE_BY_IDENTITY[service]
            for service in affected_services
            if service in COMPOSE_SERVICE_BY_IDENTITY
        ]
        next_steps = []
        if affected_compose_services:
            next_steps.append(
                "Run `docker compose up -d "
                + " ".join(affected_compose_services)
                + "` from `lotus-platform/platform-stack`."
            )
        else:
            next_steps.append(
                f"Bring up or refresh the affected services through the ingress-first compose flow: {', '.join(affected_services)}."
            )
        next_steps.append(
            "Re-run `powershell -ExecutionPolicy Bypass -File automation/Validate-Dev-Ingress-Smoke.ps1` after the stack is up."
        )
        return {
            "generated_at": datetime.now().astimezone().isoformat(),
            "status": "services_unreachable",
            "summary": "Canonical dev ingress hostnames resolve, but one or more routed services are not healthy.",
            "next_steps": next_steps,
            "evidence": {
                "failed_http_check_ids": [check["check_id"] for check in failed_http_checks],
                "affected_services": affected_services,
                "affected_compose_services": affected_compose_services,
                "failing_http_statuses": [check.get("status") for check in failed_http_checks if check.get("status") is not None],
                "staged_hosts_present": staged_hosts_present,
            },
        }

    return {
        "generated_at": datetime.now().astimezone().isoformat(),
        "status": "unknown_failure",
        "summary": "Dev ingress validation failed, but the failure could not be classified cleanly.",
        "next_steps": [
            "Inspect `output/dev-ingress-smoke.json` and rerun the smoke validator.",
        ],
        "evidence": {
            "failed_count": smoke_payload.get("failed_count"),
            "staged_hosts_present": staged_hosts_present,
            "staged_hostnames": staged_hostnames,
        },
    }


def _write_markdown(output_path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Dev Ingress Status",
        "",
        f"- Generated: {payload['generated_at']}",
        f"- Status: {payload['status']}",
        f"- Summary: {payload['summary']}",
        "",
        "## Next Steps",
        "",
    ]
    for step in payload["next_steps"]:
        lines.append(f"- {step}")

    evidence = payload.get("evidence", {})
    if evidence:
        lines.extend(["", "## Evidence", ""])
        for key, value in evidence.items():
            lines.append(f"- {key}: {value}")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-json-path", type=Path, default=DEFAULT_SMOKE_PATH)
    parser.add_argument("--staged-hosts-path", type=Path, default=DEFAULT_STAGED_HOSTS_PATH)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-markdown", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()

    payload = explain_dev_ingress_status(
        smoke_payload=_load_json(args.smoke_json_path),
        staged_hosts_text=_load_text(args.staged_hosts_path),
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_markdown(args.output_markdown, payload)

    print(f"Wrote {args.output_json}")
    print(f"Wrote {args.output_markdown}")
    return 0 if payload["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
