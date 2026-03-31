from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
PLATFORM_STACK_DIR = ROOT / "platform-stack"


def _read_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def test_platform_stack_includes_central_dev_ingress_service() -> None:
    compose = _read_yaml(PLATFORM_STACK_DIR / "docker-compose.yml")
    ingress = compose["services"]["dev-ingress"]

    assert ingress["image"] == "caddy:2.8.4"
    assert "./dev-ingress/Caddyfile:/etc/caddy/Caddyfile:ro" in ingress["volumes"]
    assert "${DEV_INGRESS_HTTP_PORT:-80}:80" in ingress["ports"]


def test_platform_stack_dev_ingress_routes_expected_hostnames() -> None:
    caddyfile = (PLATFORM_STACK_DIR / "dev-ingress" / "Caddyfile").read_text(encoding="utf-8")

    for hostname in (
        "workbench.dev.lotus",
        "gateway.dev.lotus",
        "manage.dev.lotus",
        "performance.dev.lotus",
        "report.dev.lotus",
        "core-query.dev.lotus",
        "core-ingestion.dev.lotus",
        "prometheus.dev.lotus",
        "grafana.dev.lotus",
    ):
        assert hostname in caddyfile


def test_platform_stack_hosts_example_lists_required_entries() -> None:
    hosts_example = (PLATFORM_STACK_DIR / "dev-ingress" / "hosts.example").read_text(encoding="utf-8")

    assert "127.0.0.1 workbench.dev.lotus" in hosts_example
    assert "127.0.0.1 gateway.dev.lotus" in hosts_example
    assert "127.0.0.1 core-query.dev.lotus" in hosts_example
    assert "127.0.0.1 core-ingestion.dev.lotus" in hosts_example
