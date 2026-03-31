from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPOS_PATH = ROOT / "automation" / "repos.json"
DEFAULT_OUTPUT_JSON = ROOT / "output" / "service-addressing.json"
DEFAULT_OUTPUT_MD = ROOT / "output" / "service-addressing.md"


@dataclass(frozen=True)
class RepoConfig:
    name: str
    path: Path


LOCALHOST_LITERALS = (
    "http://localhost:",
    "https://localhost:",
    "http://127.0.0.1:",
    "https://127.0.0.1:",
    "host.docker.internal",
)


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_repo_configs(path: Path) -> dict[str, RepoConfig]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload if isinstance(payload, list) else payload.get("repositories", [])
    return {
        entry["name"]: RepoConfig(name=entry["name"], path=Path(entry["path"]))
        for entry in entries
    }


def _result(check_id: str, passed: bool, message: str, evidence: list[str]) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "passed": passed,
        "message": message,
        "evidence": evidence,
    }


def _contains_all(text: str, required: list[str]) -> bool:
    return all(item in text for item in required)


def _contains_none(text: str, forbidden: list[str]) -> bool:
    return all(item not in text for item in forbidden)


def _extract_caddy_hostnames(text: str) -> set[str]:
    hostnames: set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("{") or line.startswith("}"):
            continue
        if line.endswith("{"):
            hostname = line[:-1].strip()
            hostname = hostname.removeprefix("http://").removeprefix("https://")
            if "." in hostname:
                hostnames.add(hostname)
    return hostnames


def _extract_hosts_file_hostnames(text: str) -> set[str]:
    hostnames: set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.replace("\ufeff", "").strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            hostnames.add(parts[1])
    return hostnames


def _find_localhost_literal_observations(repo_configs: dict[str, RepoConfig]) -> list[dict[str, Any]]:
    observations: list[dict[str, Any]] = []

    candidate_paths_by_repo: dict[str, list[Path]] = {
        repo_name: [
            config.path / "README.md",
            config.path / "docs" / "demo" / "README.md",
            config.path / "Local Development Runbook.md",
        ]
        for repo_name, config in repo_configs.items()
    }

    for repo_name, candidate_paths in candidate_paths_by_repo.items():
        for path in candidate_paths:
            if not path.exists():
                continue
            text = _load_text(path)
            matched_literals = [literal for literal in LOCALHOST_LITERALS if literal in text]
            if matched_literals:
                observations.append(
                    {
                        "repo": repo_name,
                        "path": str(path),
                        "matched_literals": matched_literals,
                    }
                )
    return observations


def validate_service_addressing(repos_path: Path) -> dict[str, Any]:
    repo_configs = _load_repo_configs(repos_path)
    platform_root = repo_configs["lotus-platform"].path
    workbench_root = repo_configs["lotus-workbench"].path
    gateway_root = repo_configs["lotus-gateway"].path

    platform_runbook = platform_root / "Local Development Runbook.md"
    platform_stack_readme = platform_root / "platform-stack" / "README.md"
    dev_ingress_caddyfile = platform_root / "platform-stack" / "dev-ingress" / "Caddyfile"
    dev_ingress_hosts = platform_root / "platform-stack" / "dev-ingress" / "hosts.example"
    platform_compose = platform_root / "platform-stack" / "docker-compose.yml"
    host_ports_compose = platform_root / "platform-stack" / "docker-compose.host-ports.yml"
    workbench_readme = workbench_root / "README.md"
    workbench_demo = workbench_root / "docs" / "demo" / "README.md"
    gateway_readme = gateway_root / "README.md"
    gateway_demo = gateway_root / "docs" / "demo" / "README.md"
    workbench_api = workbench_root / "src" / "features" / "workbench" / "api.ts"
    workbench_entry = workbench_root / "src" / "app" / "workbench" / "page.tsx"
    workbench_portfolio_api = workbench_root / "src" / "apps" / "portfolio" / "api.ts"
    workbench_performance_page = (
        workbench_root / "src" / "apps" / "performance" / "performance-analytics-page.tsx"
    )
    workbench_bff_route = workbench_root / "src" / "app" / "api" / "bff" / "[...path]" / "route.ts"

    runbook_text = _load_text(platform_runbook)
    platform_stack_text = _load_text(platform_stack_readme)
    dev_ingress_caddyfile_text = _load_text(dev_ingress_caddyfile)
    dev_ingress_hosts_text = _load_text(dev_ingress_hosts)
    dev_ingress_caddy_hostnames = _extract_caddy_hostnames(dev_ingress_caddyfile_text)
    dev_ingress_hosts_hostnames = _extract_hosts_file_hostnames(dev_ingress_hosts_text)
    platform_compose_text = _load_text(platform_compose)
    host_ports_compose_text = _load_text(host_ports_compose)
    workbench_readme_text = _load_text(workbench_readme)
    workbench_demo_text = _load_text(workbench_demo)
    gateway_readme_text = _load_text(gateway_readme)
    gateway_demo_text = _load_text(gateway_demo)

    checks = [
        _result(
            "platform_runbook_defines_canonical_dev_hostnames",
            _contains_all(
                runbook_text,
                [
                    "gateway.dev.lotus",
                    "workbench.dev.lotus",
                    "manage.dev.lotus",
                    "performance.dev.lotus",
                    "core-query.dev.lotus",
                    "core-ingestion.dev.lotus",
                ],
            ),
            "Local Development Runbook defines canonical environment-scoped service identities for the Phase A local stack.",
            [str(platform_runbook)],
        ),
        _result(
            "platform_runbook_drops_host_docker_internal",
            _contains_none(runbook_text, ["host.docker.internal"]),
            "Local Development Runbook no longer uses host.docker.internal as the canonical service identity model.",
            [str(platform_runbook)],
        ),
        _result(
            "platform_stack_readme_advertises_canonical_hostnames",
            _contains_all(
                platform_stack_text,
                ["gateway.dev.lotus", "workbench.dev.lotus", "core-query.dev.lotus", "core-ingestion.dev.lotus"],
            ),
            "platform-stack README advertises canonical service hostnames instead of raw ports as the primary operator contract.",
            [str(platform_stack_readme)],
        ),
        _result(
            "platform_stack_owns_local_dev_ingress",
            _contains_all(platform_compose_text, ["dev-ingress:", "./dev-ingress/Caddyfile:/etc/caddy/Caddyfile:ro"]),
            "platform-stack owns a central local ingress service for environment-scoped dev hostnames.",
            [str(platform_compose)],
        ),
        _result(
            "platform_stack_base_compose_is_ingress_first",
            _contains_none(
                platform_compose_text,
                [
                    '${LOTUS_MANAGE_PORT:-8000}:8000',
                    '${LOTUS_CORE_INGESTION_PORT:-8200}:8000',
                    '${LOTUS_CORE_QUERY_PORT:-8201}:8001',
                    '${LOTUS_PERFORMANCE_PORT:-8002}:8000',
                    '${LOTUS_REPORT_PORT:-8300}:8300',
                    '${BFF_PORT:-8100}:8100',
                    '${UI_PORT:-3000}:3000',
                    '${PROMETHEUS_PORT:-9190}:9090',
                    '${GRAFANA_PORT:-3300}:3000',
                ],
            ),
            "Base platform-stack compose is ingress-first and does not publish legacy direct host ports by default.",
            [str(platform_compose)],
        ),
        _result(
            "platform_stack_debug_override_preserves_direct_host_ports",
            _contains_all(
                host_ports_compose_text,
                [
                    '${LOTUS_MANAGE_PORT:-8000}:8000',
                    '${LOTUS_CORE_INGESTION_PORT:-8200}:8000',
                    '${LOTUS_CORE_QUERY_PORT:-8201}:8001',
                    '${LOTUS_PERFORMANCE_PORT:-8002}:8000',
                    '${LOTUS_REPORT_PORT:-8300}:8300',
                    '${BFF_PORT:-8100}:8100',
                    '${UI_PORT:-3000}:3000',
                    '${PROMETHEUS_PORT:-9190}:9090',
                    '${GRAFANA_PORT:-3300}:3000',
                ],
            ),
            "platform-stack keeps a separate debug-only override for legacy direct host-port publishing.",
            [str(host_ports_compose)],
        ),
        _result(
            "platform_stack_dev_ingress_routes_canonical_hostnames",
            _contains_all(
                dev_ingress_caddyfile_text,
                [
                    "workbench.dev.lotus",
                    "gateway.dev.lotus",
                    "manage.dev.lotus",
                    "performance.dev.lotus",
                    "report.dev.lotus",
                    "core-query.dev.lotus",
                    "core-ingestion.dev.lotus",
                ],
            ),
            "platform-stack ingress routes the canonical local dev hostnames to the correct services.",
            [str(dev_ingress_caddyfile)],
        ),
        _result(
            "platform_stack_dev_ingress_hosts_example_exists",
            _contains_all(dev_ingress_hosts_text, ["workbench.dev.lotus", "gateway.dev.lotus", "core-query.dev.lotus", "core-ingestion.dev.lotus"]),
            "platform-stack publishes the required local hosts-file mappings for the dev ingress.",
            [str(dev_ingress_hosts)],
        ),
        _result(
            "platform_stack_dev_ingress_hostnames_are_aligned",
            dev_ingress_caddy_hostnames == dev_ingress_hosts_hostnames,
            "platform-stack ingress router hostnames and hosts.example entries stay exactly aligned.",
            [
                str(dev_ingress_caddyfile),
                str(dev_ingress_hosts),
                f"caddy={sorted(dev_ingress_caddy_hostnames)}",
                f"hosts={sorted(dev_ingress_hosts_hostnames)}",
            ],
        ),
        _result(
            "workbench_docs_advertise_gateway_service_identity",
            _contains_all(
                workbench_readme_text + "\n" + workbench_demo_text,
                ["gateway.dev.lotus", "workbench.dev.lotus"],
            ),
            "lotus-workbench docs point operators to environment-scoped service URLs for UI and gateway.",
            [str(workbench_readme), str(workbench_demo)],
        ),
        _result(
            "gateway_docs_advertise_gateway_service_identity",
            _contains_all(gateway_readme_text + "\n" + gateway_demo_text, ["gateway.dev.lotus"]),
            "lotus-gateway docs point operators to the gateway service identity rather than raw localhost port mappings.",
            [str(gateway_readme), str(gateway_demo)],
        ),
        _result(
            "workbench_runtime_no_longer_embeds_localhost_gateway_fallbacks",
            all(
                "http://localhost:8100"
                not in _load_text(path)
                for path in [
                    workbench_api,
                    workbench_entry,
                    workbench_portfolio_api,
                    workbench_performance_page,
                    workbench_bff_route,
                ]
            ),
            "lotus-workbench runtime entry points no longer embed localhost gateway fallbacks and instead centralize service addressing.",
            [
                str(workbench_api),
                str(workbench_entry),
                str(workbench_portfolio_api),
                str(workbench_performance_page),
                str(workbench_bff_route),
            ],
        ),
    ]

    failures = [check for check in checks if not check["passed"]]
    observations = _find_localhost_literal_observations(repo_configs)
    return {
        "generated_at": datetime.now().astimezone().isoformat(),
        "result": "ok" if not failures else "failed",
        "checks": checks,
        "failed_count": len(failures),
        "localhost_literal_observations": observations,
    }


def _write_markdown(output_path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Service Addressing Validation",
        "",
        f"- Generated: {payload['generated_at']}",
        f"- Result: {payload['result']}",
        f"- Failed checks: {payload['failed_count']}",
        "",
        "| Check | Passed | Message |",
        "|---|---|---|",
    ]
    for check in payload["checks"]:
        passed = "true" if check["passed"] else "false"
        lines.append(f"| {check['check_id']} | {passed} | {check['message']} |")
    observations = payload.get("localhost_literal_observations", [])
    if observations:
        lines.extend(["", "## Localhost Literal Observations", ""])
        for observation in observations:
            lines.append(
                f"- {observation['repo']}: {observation['path']} -> {', '.join(observation['matched_literals'])}"
            )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repos-path", type=Path, default=DEFAULT_REPOS_PATH)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-markdown", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()

    payload = validate_service_addressing(args.repos_path)

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_markdown(args.output_markdown, payload)

    print(f"Wrote {args.output_json}")
    print(f"Wrote {args.output_markdown}")
    return 0 if payload["result"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
