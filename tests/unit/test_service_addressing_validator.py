from __future__ import annotations

import json
from pathlib import Path

from automation.validate_service_addressing import validate_service_addressing


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_validate_service_addressing_accepts_canonical_hostnames(tmp_path: Path) -> None:
    platform = tmp_path / "lotus-platform"
    advise = tmp_path / "lotus-advise"
    ai = tmp_path / "lotus-ai"
    manage = tmp_path / "lotus-manage"
    workbench = tmp_path / "lotus-workbench"
    gateway = tmp_path / "lotus-gateway"
    risk = tmp_path / "lotus-risk"
    report = tmp_path / "lotus-report"

    _write_text(
        platform / "Local Development Runbook.md",
        "gateway.dev.lotus\nworkbench.dev.lotus\nmanage.dev.lotus\nperformance.dev.lotus\ncore-query.dev.lotus\ncore-control.dev.lotus\ncore-ingestion.dev.lotus\n",
    )
    _write_text(
        platform / "platform-stack" / "README.md",
        "gateway.dev.lotus\nworkbench.dev.lotus\ncore-query.dev.lotus\ncore-control.dev.lotus\ncore-ingestion.dev.lotus\n",
    )
    _write_text(
        platform / "platform-stack" / "docker-compose.yml",
        "services:\n"
        "  dev-ingress:\n"
        "    volumes:\n"
        "      - ./dev-ingress/Caddyfile:/etc/caddy/Caddyfile:ro\n"
        "  lotus-core-control:\n"
        "    build:\n"
        "      dockerfile: ./src/services/query_control_plane_service/Dockerfile\n"
        "  bff:\n"
        "    environment:\n"
        "      PORTFOLIO_DATA_QUERY_BASE_URL: http://lotus-core-query:8001\n"
        "      PORTFOLIO_DATA_CONTROL_PLANE_BASE_URL: http://lotus-core-control:8002\n",
    )
    _write_text(
        platform / "platform-stack" / "docker-compose.host-ports.yml",
        '${LOTUS_MANAGE_PORT:-8000}:8000\n${LOTUS_CORE_INGESTION_PORT:-8200}:8000\n${LOTUS_CORE_QUERY_PORT:-8201}:8001\n${LOTUS_PERFORMANCE_PORT:-8002}:8000\n${LOTUS_REPORT_PORT:-8300}:8300\n${BFF_PORT:-8100}:8100\n${UI_PORT:-3000}:3000\n${PROMETHEUS_PORT:-9190}:9090\n${GRAFANA_PORT:-3300}:3000\n',
    )
    _write_text(
        platform / "platform-stack" / "dev-ingress" / "Caddyfile",
        "http://workbench.dev.lotus {\n reverse_proxy ui:3000\n}\n"
        "http://gateway.dev.lotus {\n reverse_proxy bff:8100\n}\n"
        "http://manage.dev.lotus {\n reverse_proxy lotus-manage:8000\n}\n"
        "http://performance.dev.lotus {\n reverse_proxy lotus-performance:8000\n}\n"
        "http://report.dev.lotus {\n reverse_proxy lotus-report:8300\n}\n"
        "http://core-query.dev.lotus {\n reverse_proxy lotus-core-query:8001\n}\n"
        "http://core-control.dev.lotus {\n reverse_proxy lotus-core-control:8002\n}\n"
        "http://core-ingestion.dev.lotus {\n reverse_proxy lotus-core-ingestion:8000\n}\n",
    )
    _write_text(
        platform / "platform-stack" / "dev-ingress" / "hosts.example",
        "127.0.0.1 workbench.dev.lotus\n"
        "127.0.0.1 gateway.dev.lotus\n"
        "127.0.0.1 manage.dev.lotus\n"
        "127.0.0.1 performance.dev.lotus\n"
        "127.0.0.1 report.dev.lotus\n"
        "127.0.0.1 core-query.dev.lotus\n"
        "127.0.0.1 core-control.dev.lotus\n"
        "127.0.0.1 core-ingestion.dev.lotus\n",
    )
    _write_text(
        advise / "README.md",
        "http://core-control.dev.lotus\nhttp://core-query.dev.lotus\nhttp://risk.dev.lotus\n",
    )
    _write_text(
        advise / "docker-compose.yml",
        "services:\n"
        "  lotus-advise:\n"
        "    environment:\n"
        "      - LOTUS_CORE_BASE_URL=${LOTUS_CORE_BASE_URL:-http://core-control.dev.lotus}\n"
        "      - LOTUS_CORE_QUERY_BASE_URL=${LOTUS_CORE_QUERY_BASE_URL:-http://core-query.dev.lotus}\n"
        "      - LOTUS_RISK_BASE_URL=${LOTUS_RISK_BASE_URL:-http://risk.dev.lotus}\n"
        "    extra_hosts:\n"
        '      - "core-control.dev.lotus:host-gateway"\n'
        '      - "core-query.dev.lotus:host-gateway"\n'
        '      - "risk.dev.lotus:host-gateway"\n'
        "  postgres:\n"
        "    image: postgres:17.6\n",
    )
    _write_text(
        ai / "README.md",
        "PostgreSQL stays internal to the Compose network on `postgres:5432`\n"
        "Redis stays internal to the Compose network on `redis:6379`\n",
    )
    _write_text(
        ai / "docker-compose.yml",
        "services:\n"
        "  postgres:\n"
        "    image: postgres:16-alpine\n"
        "  redis:\n"
        "    image: redis:7-alpine\n"
        "  lotus-ai:\n"
        '    ports:\n      - "8140:8140"\n',
    )
    _write_text(
        manage / "README.md",
        "does not publish the internal PostgreSQL port by default\n"
        "`postgres:5432` remains internal to the Compose network\n",
    )
    _write_text(
        manage / "docker-compose.yml",
        "services:\n"
        "  lotus-manage:\n"
        '    ports:\n      - "8000:8000"\n'
        "  postgres:\n"
        "    image: postgres:17.6\n",
    )
    _write_text(
        manage / "docker-compose.ci-local.yml",
        "services:\n"
        "  postgres:\n"
        "    image: postgres:17.6\n",
    )
    _write_text(workbench / "README.md", "gateway.dev.lotus\nworkbench.dev.lotus\n")
    _write_text(workbench / "docs" / "demo" / "README.md", "gateway.dev.lotus\nworkbench.dev.lotus\n")
    _write_text(gateway / "README.md", "gateway.dev.lotus\n")
    _write_text(gateway / "docs" / "demo" / "README.md", "gateway.dev.lotus\n")
    _write_text(
        risk / "src" / "app" / "integrations" / "lotus_core_client.py",
        'DEFAULT_LOTUS_CORE_BASE_URL = "http://core-query.dev.lotus"\n',
    )
    _write_text(
        risk / "src" / "app" / "integrations" / "lotus_performance_client.py",
        'DEFAULT_LOTUS_PERFORMANCE_BASE_URL = "http://performance.dev.lotus"\n',
    )
    _write_text(
        report / "src" / "app" / "config.py",
        'DEFAULT_PAS_BASE_URL = "http://core-query.dev.lotus"\n'
        'DEFAULT_PA_BASE_URL = "http://performance.dev.lotus"\n'
        'DEFAULT_RISK_BASE_URL = "http://risk.dev.lotus"\n',
    )
    _write_text(
        report / "README.md",
        "report.dev.lotus\ncore-query.dev.lotus\nperformance.dev.lotus\nrisk.dev.lotus\n",
    )
    _write_text(workbench / "src" / "features" / "workbench" / "api.ts", 'const base = "http://gateway.dev.lotus";\n')
    _write_text(workbench / "src" / "app" / "workbench" / "page.tsx", 'const base = "http://gateway.dev.lotus";\n')
    _write_text(workbench / "src" / "apps" / "portfolio" / "api.ts", 'const base = "http://gateway.dev.lotus";\n')
    _write_text(
        workbench / "src" / "apps" / "performance" / "performance-analytics-page.tsx",
        'const base = "http://gateway.dev.lotus";\n',
    )
    _write_text(
        workbench / "src" / "app" / "api" / "bff" / "[...path]" / "route.ts",
        'const base = "http://gateway.dev.lotus";\n',
    )

    repos_path = tmp_path / "repos.json"
    repos_path.write_text(
        json.dumps(
            [
                {"name": "lotus-platform", "path": str(platform)},
                {"name": "lotus-advise", "path": str(advise)},
                {"name": "lotus-ai", "path": str(ai)},
                {"name": "lotus-manage", "path": str(manage)},
                {"name": "lotus-workbench", "path": str(workbench)},
                {"name": "lotus-gateway", "path": str(gateway)},
                {"name": "lotus-risk", "path": str(risk)},
                {"name": "lotus-report", "path": str(report)},
            ]
        ),
        encoding="utf-8",
    )

    result = validate_service_addressing(repos_path)

    assert result["result"] == "ok"
    assert result["failed_count"] == 0
    assert result["localhost_literal_observations"] == []


def test_validate_service_addressing_flags_port_based_drift(tmp_path: Path) -> None:
    platform = tmp_path / "lotus-platform"
    advise = tmp_path / "lotus-advise"
    ai = tmp_path / "lotus-ai"
    manage = tmp_path / "lotus-manage"
    workbench = tmp_path / "lotus-workbench"
    gateway = tmp_path / "lotus-gateway"
    risk = tmp_path / "lotus-risk"
    report = tmp_path / "lotus-report"

    _write_text(
        platform / "Local Development Runbook.md",
        "http://localhost:3000\nhttp://host.docker.internal:8100\n",
    )
    _write_text(platform / "platform-stack" / "README.md", "http://localhost:8100\n")
    _write_text(platform / "platform-stack" / "docker-compose.yml", "services: {}\n")
    _write_text(platform / "platform-stack" / "docker-compose.host-ports.yml", "services: {}\n")
    _write_text(platform / "platform-stack" / "dev-ingress" / "Caddyfile", "gateway.dev.lotus {\n reverse_proxy bff:8100\n}\n")
    _write_text(platform / "platform-stack" / "dev-ingress" / "hosts.example", "127.0.0.1 workbench.dev.lotus\n")
    _write_text(advise / "README.md", "http://localhost:8000\n")
    _write_text(
        advise / "docker-compose.yml",
        "services:\n"
        "  lotus-advise:\n"
        "    environment:\n"
        "      - LOTUS_CORE_BASE_URL=http://localhost:8202\n"
        "      - LOTUS_RISK_BASE_URL=http://127.0.0.1:8130\n"
        "  postgres:\n"
        "    ports:\n"
        '      - "5432:5432"\n',
    )
    _write_text(ai / "README.md", "docker local ai runtime\n")
    _write_text(
        ai / "docker-compose.yml",
        "services:\n"
        "  postgres:\n"
        '    ports:\n      - "5432:5432"\n'
        "  redis:\n"
        '    ports:\n      - "6379:6379"\n',
    )
    _write_text(manage / "README.md", "manage local runtime\n")
    _write_text(
        manage / "docker-compose.yml",
        "services:\n"
        "  postgres:\n"
        '    ports:\n      - "5432:5432"\n',
    )
    _write_text(
        manage / "docker-compose.ci-local.yml",
        "services:\n"
        "  postgres:\n"
        '    ports:\n      - "5432:5432"\n',
    )
    _write_text(workbench / "README.md", "http://127.0.0.1:3000\n")
    _write_text(workbench / "docs" / "demo" / "README.md", "http://127.0.0.1:3000\n")
    _write_text(gateway / "README.md", "http://127.0.0.1:8100\n")
    _write_text(gateway / "docs" / "demo" / "README.md", "http://127.0.0.1:8100\n")
    _write_text(
        risk / "src" / "app" / "integrations" / "lotus_core_client.py",
        'DEFAULT_LOTUS_CORE_BASE_URL = "http://localhost:8000"\n',
    )
    _write_text(
        risk / "src" / "app" / "integrations" / "lotus_performance_client.py",
        'DEFAULT_LOTUS_PERFORMANCE_BASE_URL = "http://localhost:8002"\n',
    )
    _write_text(
        report / "src" / "app" / "config.py",
        'pas_base_url = "http://localhost:8201"\n'
        'pa_base_url = "http://localhost:8002"\n'
        'risk_base_url = "http://localhost:8130"\n',
    )
    _write_text(report / "README.md", "http://localhost:8300\n")
    _write_text(workbench / "src" / "features" / "workbench" / "api.ts", 'const base = "http://localhost:8100";\n')
    _write_text(workbench / "src" / "app" / "workbench" / "page.tsx", 'const base = "http://localhost:8100";\n')
    _write_text(workbench / "src" / "apps" / "portfolio" / "api.ts", 'const base = "http://localhost:8100";\n')
    _write_text(
        workbench / "src" / "apps" / "performance" / "performance-analytics-page.tsx",
        'const base = "http://localhost:8100";\n',
    )
    _write_text(
        workbench / "src" / "app" / "api" / "bff" / "[...path]" / "route.ts",
        'const base = "http://localhost:8100";\n',
    )

    repos_path = tmp_path / "repos.json"
    repos_path.write_text(
        json.dumps(
            [
                {"name": "lotus-platform", "path": str(platform)},
                {"name": "lotus-advise", "path": str(advise)},
                {"name": "lotus-ai", "path": str(ai)},
                {"name": "lotus-manage", "path": str(manage)},
                {"name": "lotus-workbench", "path": str(workbench)},
                {"name": "lotus-gateway", "path": str(gateway)},
                {"name": "lotus-risk", "path": str(risk)},
                {"name": "lotus-report", "path": str(report)},
            ]
        ),
        encoding="utf-8",
    )

    result = validate_service_addressing(repos_path)

    assert result["result"] == "failed"
    assert result["failed_count"] > 0
    assert any(
        observation["repo"] == "lotus-workbench"
        and (
            "http://localhost:" in observation["matched_literals"]
            or "http://127.0.0.1:" in observation["matched_literals"]
        )
        for observation in result["localhost_literal_observations"]
    )
    failed_ids = {check["check_id"] for check in result["checks"] if not check["passed"]}
    assert "platform_runbook_drops_host_docker_internal" in failed_ids
    assert "platform_stack_owns_local_dev_ingress" in failed_ids
    assert "platform_stack_wires_core_control_plane_service" in failed_ids
    assert "platform_stack_debug_override_preserves_direct_host_ports" in failed_ids
    assert "platform_stack_dev_ingress_hostnames_are_aligned" in failed_ids
    assert "advise_runtime_defaults_use_canonical_upstream_service_identities" in failed_ids
    assert "advise_local_docker_does_not_publish_internal_postgres_port" in failed_ids
    assert "advise_docs_advertise_canonical_service_identities" in failed_ids
    assert "manage_local_docker_does_not_publish_internal_postgres_port" in failed_ids
    assert "manage_docs_describe_internal_postgres_network_only" in failed_ids
    assert "ai_local_docker_does_not_publish_internal_postgres_or_redis_ports" in failed_ids
    assert "ai_docs_describe_internal_infra_network_only" in failed_ids
    assert "risk_runtime_defaults_use_canonical_upstream_service_identities" in failed_ids
    assert "report_runtime_defaults_use_canonical_upstream_service_identities" in failed_ids
    assert "report_docs_advertise_report_service_identity" in failed_ids
    assert "workbench_runtime_no_longer_embeds_localhost_gateway_fallbacks" in failed_ids
