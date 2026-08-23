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
    assert jobs["lotus-workbench"]["metrics_path"] == "/api/metrics"
    assert jobs["lotus-workbench"]["static_configs"][0]["targets"] == ["lotus-workbench:3000"]


def test_platform_stack_retains_traces_in_tempo() -> None:
    compose = _read_yaml(PLATFORM_STACK_DIR / "docker-compose.yml")
    collector = _read_yaml(PLATFORM_STACK_DIR / "otel-collector" / "config.yaml")
    datasources = _read_yaml(
        PLATFORM_STACK_DIR / "grafana" / "provisioning" / "datasources" / "datasource.yml"
    )

    assert compose["services"]["otel-collector"]["depends_on"]["tempo"]["condition"] == "service_healthy"
    assert collector["receivers"]["otlp"]["protocols"]["grpc"]["endpoint"] == "0.0.0.0:4317"
    assert collector["receivers"]["otlp"]["protocols"]["http"]["endpoint"] == "0.0.0.0:4318"
    assert collector["exporters"]["otlp/tempo"]["endpoint"] == "tempo:4317"
    assert collector["service"]["pipelines"]["traces"]["exporters"] == ["otlp/tempo"]
    tempo = next(item for item in datasources["datasources"] if item["name"] == "Tempo")
    assert tempo["url"] == "http://tempo:3200"


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


def test_platform_stack_reporting_rules_use_bounded_status_values() -> None:
    contract = json.loads(
        (ROOT / "context" / "contracts" / "reporting-observability-contract.json").read_text(
            encoding="utf-8"
        )
    )
    rules = _read_yaml(
        PLATFORM_STACK_DIR / "prometheus" / "rules" / "reporting-observability.rules.yml"
    )

    rule_exprs = {}
    for group in rules["groups"]:
        for rule in group["rules"]:
            rule_exprs[rule["labels"]["alert_id"]] = rule["expr"]

    assert "report-operation-failures" in rule_exprs
    assert 'status="failed"' in rule_exprs["report-operation-failures"]
    report_operation_alert = next(
        alert for alert in contract["alerts"] if alert["alert_id"] == "report-operation-failures"
    )
    assert report_operation_alert["metric_name"] == "lotus_report_operations_total"


def test_platform_stack_analytics_ui_rules_align_with_contract_alerts() -> None:
    contract = json.loads(
        (ROOT / "context" / "contracts" / "analytics-ui-observability-contract.json").read_text(
            encoding="utf-8"
        )
    )
    rules = _read_yaml(
        PLATFORM_STACK_DIR / "prometheus" / "rules" / "analytics-ui-observability.rules.yml"
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
    implemented_metric_names = {
        metric["metric_name"]
        for metric in contract["metric_families"]
        if metric["implemented"]
    }
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
    assert {alert["metric_name"] for alert in expected_alerts.values()} == implemented_metric_names
    for alert_id, expected in expected_alerts.items():
        actual = actual_alerts[alert_id]
        assert actual["severity"] == expected["severity"]
        assert actual["owner_repo"] == expected["owner_repo"]
        assert actual["runbook_path"] == expected["runbook_path"]
        assert expected["metric_name"] in actual["expr"]


def test_platform_stack_analytics_ui_dashboard_covers_implemented_metric_families() -> None:
    contract = json.loads(
        (ROOT / "context" / "contracts" / "analytics-ui-observability-contract.json").read_text(
            encoding="utf-8"
        )
    )
    dashboard = json.loads(
        (
            PLATFORM_STACK_DIR
            / "grafana"
            / "dashboards"
            / "analytics-ui-observability-overview.json"
        ).read_text(encoding="utf-8")
    )

    implemented_metric_names = {
        metric["metric_name"]
        for metric in contract["metric_families"]
        if metric["implemented"]
    }
    dashboard_expr_text = json.dumps(dashboard, sort_keys=True)

    assert dashboard["templating"]["list"] == []
    for metric_name in implemented_metric_names:
        assert metric_name in dashboard_expr_text
    for forbidden in contract["telemetry_contract"]["dashboard_reference_policy"][
        "forbidden_variables"
    ]:
        assert forbidden not in dashboard_expr_text
