from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
PLATFORM_STACK_DIR = ROOT / "platform-stack"


def _read_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def test_platform_stack_grafana_owns_provisioning_and_mounts_core_dashboards() -> None:
    compose = _read_yaml(PLATFORM_STACK_DIR / "docker-compose.yml")
    grafana = compose["services"]["grafana"]
    volumes = grafana["volumes"]

    assert "./grafana/provisioning:/etc/grafana/provisioning:ro" in volumes
    assert "./grafana/dashboards:/var/lib/grafana/dashboards/platform:ro" in volumes
    assert (
        "${LOTUS_CORE_REPO_PATH}/grafana/dashboards:/var/lib/grafana/dashboards/lotus-core:ro"
        in volumes
    )


def test_platform_stack_dashboard_providers_separate_platform_and_core_ownership() -> None:
    provisioning = _read_yaml(
        PLATFORM_STACK_DIR / "grafana" / "provisioning" / "dashboards" / "dashboard.yml"
    )

    providers = {provider["name"]: provider for provider in provisioning["providers"]}
    assert providers["platform-shared-dashboards"]["options"]["path"] == (
        "/var/lib/grafana/dashboards/platform"
    )
    assert providers["lotus-core-dashboards"]["options"]["path"] == (
        "/var/lib/grafana/dashboards/lotus-core"
    )


def test_platform_stack_otel_collector_is_platform_owned() -> None:
    compose = _read_yaml(PLATFORM_STACK_DIR / "docker-compose.yml")
    otel = compose["services"]["otel-collector"]
    volumes = otel["volumes"]

    assert "./otel-collector/config.yaml:/etc/otelcol/config.yaml:ro" in volumes
    assert (PLATFORM_STACK_DIR / "otel-collector" / "config.yaml").exists()
