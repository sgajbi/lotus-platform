from __future__ import annotations

import json
from pathlib import Path

import yaml

from automation.validate_shared_infra_ownership import validate_shared_infra_ownership


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_validate_shared_infra_ownership_accepts_expected_boundary(tmp_path: Path) -> None:
    platform = tmp_path / "lotus-platform"
    core = tmp_path / "lotus-core"

    _write_yaml(
        platform / "platform-stack" / "docker-compose.yml",
        {
            "services": {
                "grafana": {
                    "volumes": [
                        "./grafana/provisioning:/etc/grafana/provisioning:ro",
                        "./grafana/dashboards:/var/lib/grafana/dashboards/platform:ro",
                        "${LOTUS_CORE_REPO_PATH}/grafana/dashboards:/var/lib/grafana/dashboards/lotus-core:ro",
                    ]
                }
            }
        },
    )
    _write_text(platform / "platform-stack" / "prometheus" / "prometheus.yml", "shared")
    _write_text(
        platform / "platform-stack" / "grafana" / "provisioning" / "datasources" / "datasource.yml",
        "datasource",
    )
    _write_text(
        platform / "platform-stack" / "grafana" / "provisioning" / "dashboards" / "dashboard.yml",
        "dashboard",
    )
    _write_text(platform / "platform-stack" / "otel-collector" / "config.yaml", "receivers: {}\n")
    _write_text(
        platform / "platform-stack" / "README.md",
        "Application repositories may still provide app-owned images and bootstrap jobs consumed by this stack.\n"
        "Using an app-owned migration runner or topic bootstrap job inside this compose file does not make that app the owner of shared infrastructure.\n",
    )

    _write_yaml(
        core / "docker-compose.yml",
        {
            "name": "lotus-core-app-local",
            "x-lotus-stack-contract": {
                "stack_classification": "app-local",
                "canonical_shared_infra": False,
                "canonical_owner": "lotus-core",
                "canonical_shared_infra_owner": "lotus-platform/platform-stack",
            },
        },
    )
    _write_text(
        core / "README.md",
        "Canonical shared infrastructure ownership now lives in `lotus-platform`\n"
        "C:\\Users\\Sandeep\\projects\\lotus-platform\\platform-stack\n",
    )
    _write_text(
        core / "prometheus" / "prometheus.yml",
        "Canonical shared Prometheus ownership lives in:\n"
        "lotus-platform/platform-stack/prometheus/prometheus.yml\n",
    )
    _write_text(
        core / "docs" / "operations" / "Grafana-Dashboard-Guide.md",
        "Canonical shared observability baseline:\n`lotus-platform/platform-stack`\n",
    )
    _write_text(
        core / "docs" / "operations" / "App-Local-Stack-Guide.md",
        "canonical shared Kafka broker lifecycle\ncanonical shared telemetry collector baseline\n",
    )
    _write_text(
        core / "grafana" / "provisioning" / "datasources" / "datasource.yml",
        "# app-local overlay\n# canonical shared provisioning lives in lotus-platform/platform-stack\n",
    )
    _write_text(
        core / "grafana" / "provisioning" / "dashboards" / "dashboard.yml",
        "# app-local overlay\n# canonical shared provisioning lives in lotus-platform/platform-stack\n",
    )

    repos_path = tmp_path / "repos.json"
    repos_path.write_text(
        json.dumps(
            [
                {"name": "lotus-platform", "path": str(platform)},
                {"name": "lotus-core", "path": str(core)},
            ]
        ),
        encoding="utf-8",
    )

    result = validate_shared_infra_ownership(repos_path)

    assert result["result"] == "ok"
    assert result["failed_count"] == 0


def test_validate_shared_infra_ownership_flags_drift(tmp_path: Path) -> None:
    platform = tmp_path / "lotus-platform"
    core = tmp_path / "lotus-core"

    _write_yaml(
        platform / "platform-stack" / "docker-compose.yml",
        {"services": {"grafana": {"volumes": []}}},
    )
    _write_text(platform / "platform-stack" / "prometheus" / "prometheus.yml", "shared")
    _write_text(platform / "platform-stack" / "README.md", "platform docs\n")
    _write_yaml(
        core / "docker-compose.yml",
        {"name": "lotus-core"},
    )
    _write_text(core / "README.md", "lotus-core owns kafka\n")
    _write_text(core / "prometheus" / "prometheus.yml", "local only\n")
    _write_text(core / "docs" / "operations" / "Grafana-Dashboard-Guide.md", "local grafana\n")
    _write_text(core / "docs" / "operations" / "App-Local-Stack-Guide.md", "guide\n")
    _write_text(core / "grafana" / "provisioning" / "datasources" / "datasource.yml", "local datasource\n")
    _write_text(core / "grafana" / "provisioning" / "dashboards" / "dashboard.yml", "local dashboards\n")

    repos_path = tmp_path / "repos.json"
    repos_path.write_text(
        json.dumps(
            [
                {"name": "lotus-platform", "path": str(platform)},
                {"name": "lotus-core", "path": str(core)},
            ]
        ),
        encoding="utf-8",
    )

    result = validate_shared_infra_ownership(repos_path)

    assert result["result"] == "failed"
    assert result["failed_count"] > 0
    failed_ids = {check["check_id"] for check in result["checks"] if not check["passed"]}
    assert "platform_stack_grafana_datasource_owned_in_platform" in failed_ids
    assert "lotus_core_compose_declares_app_local_contract" in failed_ids
    assert "platform_stack_otel_config_owned_in_platform" in failed_ids
