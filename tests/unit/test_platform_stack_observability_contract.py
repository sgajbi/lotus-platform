from __future__ import annotations

import json
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


def test_platform_stack_prometheus_scrapes_reporting_observability_targets() -> None:
    prometheus = _read_yaml(PLATFORM_STACK_DIR / "prometheus" / "prometheus.yml")

    jobs = {job["job_name"]: job for job in prometheus["scrape_configs"]}
    assert prometheus["rule_files"] == ["/etc/prometheus/rules/*.yml"]
    assert jobs["lotus-report"]["static_configs"][0]["targets"] == ["lotus-report:8300"]
    assert jobs["lotus-render"]["static_configs"][0]["targets"] == ["host.docker.internal:8310"]
    assert jobs["lotus-archive"]["static_configs"][0]["targets"] == ["host.docker.internal:8150"]


def test_platform_stack_prometheus_mounts_reporting_rules() -> None:
    compose = _read_yaml(PLATFORM_STACK_DIR / "docker-compose.yml")
    prometheus = compose["services"]["prometheus"]
    volumes = prometheus["volumes"]

    assert "./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro" in volumes
    assert "./prometheus/rules:/etc/prometheus/rules:ro" in volumes
    assert (
        PLATFORM_STACK_DIR / "prometheus" / "rules" / "reporting-observability.rules.yml"
    ).exists()


def test_platform_stack_reporting_rules_align_with_contract_alerts() -> None:
    contract = json.loads(
        (ROOT / "context" / "contracts" / "reporting-observability-contract.json").read_text(
            encoding="utf-8"
        )
    )
    rules = _read_yaml(
        PLATFORM_STACK_DIR / "prometheus" / "rules" / "reporting-observability.rules.yml"
    )

    expected_alerts = {
        alert["alert_id"]: {
            "metric_name": alert["metric_name"],
            "severity": alert["severity"],
            "owner_repo": alert["owner_repo"],
            "runbook_path": alert["runbook_path"],
        }
        for alert in contract["alerts"]
    }
    metric_names = {metric["metric_name"] for metric in contract["metrics_catalog"]}
    actual_alerts = {}
    for group in rules["groups"]:
        for rule in group["rules"]:
            alert_id = rule["labels"]["alert_id"]
            actual_alerts[alert_id] = {
                "severity": rule["labels"]["severity"],
                "owner_repo": rule["labels"]["owner_repo"],
                "runbook_path": rule["annotations"]["runbook"],
                "expr": rule["expr"],
            }

    assert set(actual_alerts) == set(expected_alerts)
    for alert_id, expected in expected_alerts.items():
        actual = actual_alerts[alert_id]
        assert actual["severity"] == expected["severity"]
        assert actual["owner_repo"] == expected["owner_repo"]
        assert actual["runbook_path"] == expected["runbook_path"]
        assert expected["metric_name"] in metric_names
        assert expected["metric_name"] in actual["expr"]
