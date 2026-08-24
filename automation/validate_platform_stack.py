"""Validate the canonical local platform stack's security and operability contract."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STACK_ROOT = ROOT / "platform-stack"

ONE_SHOT_SERVICES = frozenset(
    {"lotus-core-kafka-topic-creator", "lotus-core-migration-runner"}
)
EXPECTED_OTEL_SERVICE_NAMES = {
    "lotus-core-query": "lotus-core-query",
    "lotus-core-control": "lotus-core-control",
    "lotus-core-ingestion": "lotus-core-ingestion",
    "lotus-manage": "lotus-manage",
    "lotus-performance": "lotus-performance",
    "lotus-report": "lotus-report",
    "lotus-idea": "lotus-idea",
    "lotus-gateway": "lotus-gateway",
}
EXPECTED_PROMETHEUS_JOBS = frozenset(
    {
        "lotus-ai",
        "lotus-advise",
        "lotus-archive",
        "lotus-core-control",
        "lotus-core-ingestion",
        "lotus-core-query",
        "lotus-gateway",
        "lotus-idea",
        "lotus-manage",
        "lotus-performance",
        "lotus-render",
        "lotus-report",
        "lotus-risk",
        "lotus-workbench",
    }
)
EXPECTED_LEGACY_VOLUME_ADOPTIONS = {
    "lotus-core-postgres-data": "pbwm-platform_lotus-core-postgres-data",
    "lotus-report-postgres-data": "pbwm-platform_lotus-report-postgres-data",
    "grafana-data": "pbwm-platform_grafana-data",
}
_REQUIRED_INTERPOLATION = re.compile(r"^\$\{[A-Z][A-Z0-9_]*:\?[^}]+\}$")
_LOOPBACK_PORT = re.compile(r"^127\.0\.0\.1:\$\{[A-Z][A-Z0-9_]*(?::-\d+)?\}:\d+$")
_LITERAL_DSN_CREDENTIAL = re.compile(r"://[^${:/\s]+:[^${@/\s]+@")
_INTERPOLATED_POSTGRESQL_CREDENTIALS = re.compile(
    r"^postgresql://"
    r"\$\{[A-Z][A-Z0-9_]*(?::[-?][^}]*)?\}:"
    r"\$\{[A-Z][A-Z0-9_]*:\?[^}]+\}@"
)


def _read_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    return value if isinstance(value, dict) else {}


def _as_map(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _environment_map(service: dict[str, Any]) -> dict[str, Any]:
    return _as_map(service.get("environment"))


def _has_resource_limit(service: dict[str, Any]) -> bool:
    if service.get("cpus") and service.get("mem_limit"):
        return True
    deploy = _as_map(service.get("deploy"))
    resources = _as_map(deploy.get("resources"))
    limits = _as_map(resources.get("limits"))
    return bool(limits.get("cpus") and limits.get("memory"))


def _validate_secret_values(services: dict[str, Any], issues: list[str]) -> None:
    for service_name, service in services.items():
        for key, value in _environment_map(service).items():
            if any(marker in key.upper() for marker in ("PASSWORD", "SECRET", "TOKEN")):
                if not isinstance(value, str) or not _REQUIRED_INTERPOLATION.fullmatch(
                    value
                ):
                    issues.append(
                        f"{service_name}.{key} must use required environment interpolation"
                    )
            if isinstance(value, str) and "://" in value:
                contains_literal_credentials = bool(
                    _LITERAL_DSN_CREDENTIAL.search(value)
                )
                if value.startswith("postgresql://"):
                    contains_literal_credentials = not bool(
                        _INTERPOLATED_POSTGRESQL_CREDENTIALS.match(value)
                    )
                if contains_literal_credentials:
                    issues.append(
                        f"{service_name}.{key} contains literal DSN credentials"
                    )


def _validate_port_bindings(compose: dict[str, Any], issues: list[str]) -> None:
    for service_name, raw_service in _as_map(compose.get("services")).items():
        service = _as_map(raw_service)
        for port in _as_list(service.get("ports")):
            if not isinstance(port, str) or not _LOOPBACK_PORT.fullmatch(port):
                issues.append(f"{service_name} port must bind to 127.0.0.1: {port!r}")


def _validate_service_controls(services: dict[str, Any], issues: list[str]) -> None:
    for service_name, raw_service in services.items():
        service = _as_map(raw_service)
        if service_name in ONE_SHOT_SERVICES:
            continue
        if not isinstance(service.get("healthcheck"), dict):
            issues.append(f"{service_name} must define a healthcheck")
        if not _has_resource_limit(service):
            issues.append(f"{service_name} must define CPU and memory limits")

    ingress = _as_map(services.get("dev-ingress"))
    ingress_dependencies = _as_map(ingress.get("depends_on"))
    for dependency in ("prometheus", "grafana"):
        condition = _as_map(ingress_dependencies.get(dependency)).get("condition")
        if condition != "service_healthy":
            issues.append(f"dev-ingress must wait for healthy {dependency}")


def _validate_observability(
    stack_root: Path, services: dict[str, Any], issues: list[str]
) -> None:
    for service_name, expected in EXPECTED_OTEL_SERVICE_NAMES.items():
        actual = _environment_map(_as_map(services.get(service_name))).get(
            "OTEL_SERVICE_NAME"
        )
        if actual != expected:
            issues.append(
                f"{service_name}.OTEL_SERVICE_NAME must be {expected!r}, found {actual!r}"
            )

    collector = _read_yaml(stack_root / "otel-collector" / "config.yaml")
    receivers = _as_map(collector.get("receivers"))
    otlp_receiver = _as_map(receivers.get("otlp"))
    receiver_protocols = _as_map(otlp_receiver.get("protocols"))
    if _as_map(receiver_protocols.get("grpc")).get("endpoint") != "0.0.0.0:4317":
        issues.append(
            "OTel gRPC receiver must listen on the container network at 0.0.0.0:4317"
        )
    if _as_map(receiver_protocols.get("http")).get("endpoint") != "0.0.0.0:4318":
        issues.append(
            "OTel HTTP receiver must listen on the container network at 0.0.0.0:4318"
        )
    exporters = _as_map(collector.get("exporters"))
    tempo_exporter = _as_map(exporters.get("otlp/tempo"))
    if tempo_exporter.get("endpoint") != "tempo:4317":
        issues.append("OTel collector must export traces to tempo:4317")
    collector_service = _as_map(collector.get("service"))
    pipelines = _as_map(collector_service.get("pipelines"))
    traces_pipeline = _as_map(pipelines.get("traces"))
    trace_exporters = _as_list(traces_pipeline.get("exporters"))
    if "otlp/tempo" not in trace_exporters:
        issues.append("OTel traces pipeline must retain traces through otlp/tempo")

    datasource_config = _read_yaml(
        stack_root / "grafana" / "provisioning" / "datasources" / "datasource.yml"
    )
    datasources = _as_list(datasource_config.get("datasources"))
    tempo_sources = [
        _as_map(item) for item in datasources if _as_map(item).get("type") == "tempo"
    ]
    if len(tempo_sources) != 1 or tempo_sources[0].get("url") != "http://tempo:3200":
        issues.append(
            "Grafana must provision exactly one Tempo datasource at http://tempo:3200"
        )

    prometheus = _read_yaml(stack_root / "prometheus" / "prometheus.yml")
    jobs = {
        _as_map(item).get("job_name")
        for item in _as_list(prometheus.get("scrape_configs"))
    }
    composed_otel_services = {
        service_name
        for service_name, service in services.items()
        if _environment_map(_as_map(service)).get("OTEL_SERVICE_NAME")
    }
    expected_jobs = EXPECTED_PROMETHEUS_JOBS | composed_otel_services
    if jobs != expected_jobs:
        missing = sorted(expected_jobs - jobs)
        extra = sorted(jobs - expected_jobs)
        issues.append(
            f"Prometheus job inventory drift: missing={missing} extra={extra}"
        )
    prometheus_service = _as_map(services.get("prometheus"))
    prometheus_extra_hosts = _as_list(prometheus_service.get("extra_hosts"))
    if "host.docker.internal:host-gateway" not in prometheus_extra_hosts:
        issues.append("Prometheus must map host.docker.internal through host-gateway")
    ingress_service = _as_map(services.get("dev-ingress"))
    ingress_extra_hosts = _as_list(ingress_service.get("extra_hosts"))
    if "host.docker.internal:host-gateway" not in ingress_extra_hosts:
        issues.append("Dev ingress must map host.docker.internal through host-gateway")


def _validate_security(
    stack_root: Path, services: dict[str, Any], issues: list[str]
) -> None:
    _validate_secret_values(services, issues)
    grafana_environment = _environment_map(_as_map(services.get("grafana")))
    if grafana_environment.get("GF_AUTH_ANONYMOUS_ENABLED") != "false":
        issues.append("Grafana anonymous authentication must be disabled")

    env_example = (stack_root / ".env.example").read_text(encoding="utf-8")
    if re.search(
        r"(?im)^[A-Z0-9_]*(?:PASSWORD|SECRET|TOKEN)[A-Z0-9_]*=.+$", env_example
    ):
        issues.append(".env.example must not contain secret values")
    if re.search(r"(?i)[a-z]:/users/|/home/[^/]+/", env_example):
        issues.append(".env.example must not contain workstation-specific paths")
    for bootstrap_name in ("bootstrap.ps1", "bootstrap.sh"):
        if not (stack_root / bootstrap_name).is_file():
            issues.append(f"platform stack is missing {bootstrap_name}")

    posix_bootstrap_path = stack_root / "bootstrap.sh"
    if posix_bootstrap_path.is_file():
        posix_bootstrap = posix_bootstrap_path.read_text(encoding="utf-8")
        restrictive_umask = posix_bootstrap.find("umask 077")
        first_environment_write = posix_bootstrap.find(
            'cp "$template_path" "$env_path"'
        )
        if (
            restrictive_umask < 0
            or first_environment_write < 0
            or restrictive_umask > first_environment_write
        ):
            issues.append("POSIX bootstrap must set umask 077 before creating .env")
        if (
            "set_secret_if_empty" not in posix_bootstrap
            or "if ! value=$(new_secret); then" not in posix_bootstrap
            or 'if [ -z "$value" ]; then' not in posix_bootstrap
        ):
            issues.append(
                "POSIX bootstrap must fail closed when secret generation fails"
            )

    manage_postgres = _as_map(services.get("lotus-manage-postgres"))
    manage_postgres_volumes = _as_list(manage_postgres.get("volumes"))
    expected_manage_volume = (
        "lotus-manage-postgres-identity-v2-data:/var/lib/postgresql/data"
    )
    if expected_manage_volume not in manage_postgres_volumes:
        issues.append("Manage PostgreSQL must use the identity-v2 data volume")

    tls_profile_path = stack_root / "docker-compose.tls.yml"
    tls_caddyfile_path = stack_root / "dev-ingress" / "Caddyfile.tls"
    if not tls_profile_path.is_file() or not tls_caddyfile_path.is_file():
        issues.append("platform stack must provide the Caddy local-CA TLS profile")
    else:
        tls_profile = _read_yaml(tls_profile_path)
        tls_services = _as_map(tls_profile.get("services"))
        tls_ingress = _as_map(tls_services.get("dev-ingress"))
        tls_ports = _as_list(tls_ingress.get("ports"))
        tls_caddyfile = tls_caddyfile_path.read_text(encoding="utf-8")
        if "127.0.0.1:${DEV_INGRESS_HTTPS_PORT:-443}:443" not in tls_ports:
            issues.append("TLS profile HTTPS port must bind to 127.0.0.1")
        if "local_certs" not in tls_caddyfile:
            issues.append("TLS profile must use Caddy's local CA")


def _validate_legacy_volume_adoption(stack_root: Path, issues: list[str]) -> None:
    profile_path = stack_root / "docker-compose.legacy-volumes.yml"
    if not profile_path.is_file():
        issues.append("platform stack must provide the legacy-volume adoption profile")
        return

    profile = _read_yaml(profile_path)
    adopted_volumes = _as_map(profile.get("volumes"))
    for logical_name, legacy_name in EXPECTED_LEGACY_VOLUME_ADOPTIONS.items():
        adoption = _as_map(adopted_volumes.get(logical_name))
        if adoption.get("external") is not True or adoption.get("name") != legacy_name:
            issues.append(
                f"legacy-volume profile must adopt {logical_name} from {legacy_name}"
            )
    if "lotus-manage-postgres-identity-v2-data" in adopted_volumes:
        issues.append("legacy-volume profile must not attach legacy Manage state")


def validate_stack(stack_root: Path = DEFAULT_STACK_ROOT) -> list[str]:
    issues: list[str] = []
    compose = _read_yaml(stack_root / "docker-compose.yml")
    services = _as_map(compose.get("services"))
    if not services:
        return ["docker-compose.yml must define services"]

    if compose.get("name") != "lotus-platform":
        issues.append("Compose project name must be lotus-platform")
    declared_volumes = _as_map(compose.get("volumes"))
    if "lotus-manage-postgres-identity-v2-data" not in declared_volumes:
        issues.append("Compose must declare the Manage identity-v2 data volume")
    if "lotus-manage-postgres-data" in declared_volumes:
        issues.append(
            "Compose must not attach the legacy Manage PostgreSQL data volume"
        )
    if "bff" in services or "ui" in services:
        issues.append(
            "Legacy bff/ui service names are forbidden; use lotus-gateway/lotus-workbench"
        )

    _validate_security(stack_root, services, issues)
    _validate_port_bindings(compose, issues)
    _validate_port_bindings(
        _read_yaml(stack_root / "docker-compose.host-ports.yml"), issues
    )
    _validate_service_controls(services, issues)
    _validate_observability(stack_root, services, issues)
    _validate_legacy_volume_adoption(stack_root, issues)
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stack-root", type=Path, default=DEFAULT_STACK_ROOT)
    args = parser.parse_args()
    issues = validate_stack(args.stack_root.resolve())
    if issues:
        print("platform stack validation failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("platform stack validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
