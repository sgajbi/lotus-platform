from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPOS_PATH = ROOT / "automation" / "repos.json"
DEFAULT_OUTPUT_JSON = ROOT / "output" / "shared-infra-ownership.json"
DEFAULT_OUTPUT_MD = ROOT / "output" / "shared-infra-ownership.md"


@dataclass(frozen=True)
class RepoConfig:
    name: str
    path: Path


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


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


def _validate_platform_stack(platform_root: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    compose_path = platform_root / "platform-stack" / "docker-compose.yml"
    prometheus_path = platform_root / "platform-stack" / "prometheus" / "prometheus.yml"
    datasource_path = (
        platform_root / "platform-stack" / "grafana" / "provisioning" / "datasources" / "datasource.yml"
    )
    dashboards_path = (
        platform_root / "platform-stack" / "grafana" / "provisioning" / "dashboards" / "dashboard.yml"
    )
    otel_config_path = platform_root / "platform-stack" / "otel-collector" / "config.yaml"
    readme_path = platform_root / "platform-stack" / "README.md"

    compose = _load_yaml(compose_path)
    readme = _load_text(readme_path)
    services = compose["services"]
    grafana_volumes = services["grafana"]["volumes"]

    results.append(
        _result(
            "platform_stack_prometheus_owned_in_platform",
            prometheus_path.exists(),
            "Canonical shared Prometheus config exists in lotus-platform/platform-stack.",
            [str(prometheus_path)],
        )
    )
    results.append(
        _result(
            "platform_stack_grafana_datasource_owned_in_platform",
            datasource_path.exists(),
            "Canonical shared Grafana datasource provisioning exists in lotus-platform/platform-stack.",
            [str(datasource_path)],
        )
    )
    results.append(
        _result(
            "platform_stack_grafana_dashboard_provisioning_owned_in_platform",
            dashboards_path.exists(),
            "Canonical shared Grafana dashboard provisioning exists in lotus-platform/platform-stack.",
            [str(dashboards_path)],
        )
    )
    results.append(
        _result(
            "platform_stack_otel_config_owned_in_platform",
            otel_config_path.exists(),
            "Canonical shared OpenTelemetry collector configuration exists in lotus-platform/platform-stack.",
            [str(otel_config_path)],
        )
    )
    results.append(
        _result(
            "platform_stack_mounts_core_dashboards_as_app_owned_content",
            (
                "./grafana/provisioning:/etc/grafana/provisioning:ro" in grafana_volumes
                and "./grafana/dashboards:/var/lib/grafana/dashboards/platform:ro" in grafana_volumes
                and "${LOTUS_CORE_REPO_PATH}/grafana/dashboards:/var/lib/grafana/dashboards/lotus-core:ro"
                in grafana_volumes
            ),
            "Platform Grafana owns provisioning and the platform dashboard baseline while mounting lotus-core dashboard content as app-owned input.",
            [str(compose_path)],
        )
    )
    results.append(
        _result(
            "platform_stack_readme_preserves_app_owned_bootstrap_boundary",
            "Application repositories may still provide app-owned images and bootstrap jobs consumed by this stack." in readme
            and "Using an app-owned migration runner or topic bootstrap job inside this compose file does not make that app the owner of shared infrastructure." in readme,
            "platform-stack README keeps the ownership boundary explicit for app-owned migration runners and topic bootstrap jobs.",
            [str(readme_path)],
        )
    )

    return results


def _validate_lotus_core(core_root: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    compose_path = core_root / "docker-compose.yml"
    prometheus_path = core_root / "prometheus" / "prometheus.yml"
    readme_path = core_root / "README.md"
    grafana_guide_path = core_root / "docs" / "operations" / "Grafana-Dashboard-Guide.md"
    app_local_stack_guide_path = core_root / "docs" / "operations" / "App-Local-Stack-Guide.md"
    grafana_datasource_path = core_root / "grafana" / "provisioning" / "datasources" / "datasource.yml"
    grafana_dashboard_provider_path = (
        core_root / "grafana" / "provisioning" / "dashboards" / "dashboard.yml"
    )

    compose = _load_yaml(compose_path)
    readme = _load_text(readme_path)
    prometheus = _load_text(prometheus_path)
    grafana_guide = _load_text(grafana_guide_path)
    app_local_stack_guide = _load_text(app_local_stack_guide_path)
    grafana_datasource = _load_text(grafana_datasource_path)
    grafana_dashboard_provider = _load_text(grafana_dashboard_provider_path)

    contract = compose.get("x-lotus-stack-contract", {})
    results.append(
        _result(
            "lotus_core_compose_declares_app_local_contract",
            (
                compose.get("name") == "lotus-core-app-local"
                and contract.get("stack_classification") == "app-local"
                and contract.get("canonical_shared_infra") is False
                and contract.get("canonical_shared_infra_owner")
                == "lotus-platform/platform-stack"
            ),
            "lotus-core compose is explicitly classified as app-local rather than canonical shared infrastructure.",
            [str(compose_path)],
        )
    )
    results.append(
        _result(
            "lotus_core_readme_points_shared_infra_to_platform",
            "Canonical shared infrastructure ownership now lives in `lotus-platform`" in readme
            and "lotus-platform\\platform-stack" in readme,
            "lotus-core README points shared infrastructure ownership to lotus-platform/platform-stack.",
            [str(readme_path)],
        )
    )
    results.append(
        _result(
            "lotus_core_prometheus_marked_app_local_overlay",
            "Canonical shared Prometheus ownership lives in:" in prometheus
            and "lotus-platform/platform-stack/prometheus/prometheus.yml" in prometheus,
            "lotus-core Prometheus config is explicitly marked as app-local overlay.",
            [str(prometheus_path)],
        )
    )
    results.append(
        _result(
            "lotus_core_grafana_guide_points_to_platform_stack",
            "Canonical shared observability baseline:" in grafana_guide
            and "`lotus-platform/platform-stack`" in grafana_guide,
            "lotus-core Grafana guide points to platform-stack as the canonical shared observability baseline.",
            [str(grafana_guide_path)],
        )
    )
    results.append(
        _result(
            "lotus_core_app_local_stack_guide_preserves_kafka_and_telemetry_boundary",
            "canonical shared Kafka broker lifecycle" in app_local_stack_guide
            and "canonical shared telemetry collector baseline" in app_local_stack_guide,
            "lotus-core app-local stack guide keeps Kafka and telemetry ownership explicit.",
            [str(app_local_stack_guide_path)],
        )
    )
    results.append(
        _result(
            "lotus_core_grafana_datasource_marked_app_local_overlay",
            "app-local" in grafana_datasource.lower() and "platform-stack" in grafana_datasource,
            "lotus-core Grafana datasource provisioning is explicitly marked as app-local overlay.",
            [str(grafana_datasource_path)],
        )
    )
    results.append(
        _result(
            "lotus_core_grafana_dashboard_provider_marked_app_local_overlay",
            "app-local" in grafana_dashboard_provider.lower() and "platform-stack" in grafana_dashboard_provider,
            "lotus-core Grafana dashboard provisioning is explicitly marked as app-local overlay.",
            [str(grafana_dashboard_provider_path)],
        )
    )
    results.append(
        _result(
            "lotus_core_has_app_local_stack_guide",
            app_local_stack_guide_path.exists(),
            "lotus-core documents the app-local stack separately from the shared platform stack.",
            [str(app_local_stack_guide_path)],
        )
    )

    return results


def validate_shared_infra_ownership(repos_path: Path) -> dict[str, Any]:
    repo_configs = _load_repo_configs(repos_path)
    platform_root = repo_configs["lotus-platform"].path
    core_root = repo_configs["lotus-core"].path

    checks = [
        *_validate_platform_stack(platform_root),
        *_validate_lotus_core(core_root),
    ]

    failures = [check for check in checks if not check["passed"]]
    return {
        "generated_at": __import__("datetime").datetime.now().astimezone().isoformat(),
        "result": "ok" if not failures else "failed",
        "checks": checks,
        "failed_count": len(failures),
    }


def _write_markdown(output_path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Shared Infrastructure Ownership Validation",
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
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repos-path", type=Path, default=DEFAULT_REPOS_PATH)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-markdown", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()

    payload = validate_shared_infra_ownership(args.repos_path)

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_markdown(args.output_markdown, payload)

    print(f"Wrote {args.output_json}")
    print(f"Wrote {args.output_markdown}")
    return 0 if payload["result"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
