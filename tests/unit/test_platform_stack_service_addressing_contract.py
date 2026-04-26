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


def test_platform_stack_base_compose_does_not_publish_legacy_http_service_ports() -> None:
    compose = _read_yaml(PLATFORM_STACK_DIR / "docker-compose.yml")

    for service_name in (
        "lotus-core-query",
        "lotus-core-control",
        "lotus-core-ingestion",
        "lotus-manage",
        "lotus-performance",
        "lotus-report",
        "bff",
        "ui",
        "prometheus",
        "grafana",
    ):
        assert "ports" not in compose["services"][service_name]


def test_platform_stack_wires_dedicated_core_control_plane_service() -> None:
    compose = _read_yaml(PLATFORM_STACK_DIR / "docker-compose.yml")
    control_plane = compose["services"]["lotus-core-control"]
    gateway = compose["services"]["bff"]

    assert (
        control_plane["build"]["dockerfile"]
        == "./src/services/query_control_plane_service/Dockerfile"
    )
    assert (
        control_plane["environment"]["OTEL_SERVICE_NAME"]
        == "lotus-core-control"
    )
    assert (
        gateway["environment"]["PORTFOLIO_DATA_QUERY_BASE_URL"]
        == "http://lotus-core-query:8001"
    )
    assert (
        gateway["environment"]["PORTFOLIO_DATA_CONTROL_PLANE_BASE_URL"]
        == "http://lotus-core-control:8002"
    )


def test_platform_stack_wires_report_to_dedicated_postgres_and_canonical_upstreams() -> None:
    compose = _read_yaml(PLATFORM_STACK_DIR / "docker-compose.yml")
    report_postgres = compose["services"]["lotus-report-postgres"]
    report = compose["services"]["lotus-report"]

    assert report_postgres["image"] == "postgres:16-alpine"
    assert report_postgres["environment"]["POSTGRES_DB"] == "${LOTUS_REPORT_POSTGRES_DB:-lotus_report}"
    assert "lotus-report-postgres-data:/var/lib/postgresql/data" in report_postgres["volumes"]
    assert report["depends_on"]["lotus-report-postgres"]["condition"] == "service_healthy"
    assert report["environment"]["LOTUS_CORE_QUERY_BASE_URL"] == "http://lotus-core-query:8001"
    assert (
        report["environment"]["LOTUS_PERFORMANCE_BASE_URL"]
        == "http://lotus-performance:8000"
    )
    assert "lotus-report-postgres:5432" in report["environment"][
        "REPORT_JOB_LEDGER_DATABASE_URL"
    ]


def test_platform_stack_debug_override_preserves_optional_direct_host_ports() -> None:
    override = _read_yaml(PLATFORM_STACK_DIR / "docker-compose.host-ports.yml")
    services = override["services"]

    assert "${LOTUS_CORE_QUERY_PORT:-8201}:8001" in services["lotus-core-query"]["ports"]
    assert "${LOTUS_CORE_INGESTION_PORT:-8200}:8000" in services["lotus-core-ingestion"]["ports"]
    assert "${LOTUS_MANAGE_PORT:-8000}:8000" in services["lotus-manage"]["ports"]
    assert "${LOTUS_PERFORMANCE_PORT:-8002}:8000" in services["lotus-performance"]["ports"]
    assert "${LOTUS_REPORT_PORT:-8300}:8300" in services["lotus-report"]["ports"]
    assert "${BFF_PORT:-8100}:8100" in services["bff"]["ports"]
    assert "${UI_PORT:-3000}:3000" in services["ui"]["ports"]
    assert "${PROMETHEUS_PORT:-9190}:9090" in services["prometheus"]["ports"]
    assert "${GRAFANA_PORT:-3300}:3000" in services["grafana"]["ports"]


def test_platform_stack_dev_ingress_routes_expected_hostnames() -> None:
    caddyfile = (PLATFORM_STACK_DIR / "dev-ingress" / "Caddyfile").read_text(encoding="utf-8")

    for hostname in (
        "workbench.dev.lotus",
        "gateway.dev.lotus",
        "manage.dev.lotus",
        "performance.dev.lotus",
        "report.dev.lotus",
        "core-query.dev.lotus",
        "core-control.dev.lotus",
        "core-ingestion.dev.lotus",
        "prometheus.dev.lotus",
        "grafana.dev.lotus",
    ):
        assert hostname in caddyfile

    assert "reverse_proxy lotus-core-control:8002" in caddyfile


def test_platform_stack_hosts_example_lists_required_entries() -> None:
    hosts_example = (PLATFORM_STACK_DIR / "dev-ingress" / "hosts.example").read_text(encoding="utf-8")

    assert "127.0.0.1 workbench.dev.lotus" in hosts_example
    assert "127.0.0.1 gateway.dev.lotus" in hosts_example
    assert "127.0.0.1 core-query.dev.lotus" in hosts_example
    assert "127.0.0.1 core-control.dev.lotus" in hosts_example
    assert "127.0.0.1 core-ingestion.dev.lotus" in hosts_example
