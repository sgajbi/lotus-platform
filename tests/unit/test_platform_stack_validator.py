from __future__ import annotations

from pathlib import Path
import shutil

import yaml

from automation.validate_platform_stack import validate_stack


ROOT = Path(__file__).resolve().parents[2]
SOURCE_STACK = ROOT / "platform-stack"


def _copy_stack(tmp_path: Path) -> Path:
    stack = tmp_path / "platform-stack"
    shutil.copytree(SOURCE_STACK, stack, ignore=shutil.ignore_patterns(".env"))
    return stack


def _read_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _write_yaml(path: Path, value: dict) -> None:
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")


def _mutate_compose(stack: Path, mutation) -> None:
    path = stack / "docker-compose.yml"
    compose = _read_yaml(path)
    mutation(compose)
    _write_yaml(path, compose)


def test_repository_platform_stack_satisfies_the_contract() -> None:
    assert validate_stack() == []


def test_validator_rejects_a_secret_default(tmp_path: Path) -> None:
    stack = _copy_stack(tmp_path)
    _mutate_compose(
        stack,
        lambda compose: compose["services"]["grafana"]["environment"].update(
            {"GF_SECURITY_ADMIN_PASSWORD": "${GRAFANA_ADMIN_PASSWORD:-admin}"}
        ),
    )

    assert any("required environment interpolation" in issue for issue in validate_stack(stack))


def test_validator_rejects_literal_dsn_credentials(tmp_path: Path) -> None:
    stack = _copy_stack(tmp_path)
    _mutate_compose(
        stack,
        lambda compose: compose["services"]["lotus-manage"]["environment"].update(
            {"DPM_SUPPORTABILITY_POSTGRES_DSN": "postgresql://operator:guess-me@db/app"}
        ),
    )

    assert any("literal DSN credentials" in issue for issue in validate_stack(stack))


def test_validator_rejects_anonymous_grafana_and_public_port_binding(tmp_path: Path) -> None:
    stack = _copy_stack(tmp_path)

    def mutate(compose: dict) -> None:
        compose["services"]["grafana"]["environment"]["GF_AUTH_ANONYMOUS_ENABLED"] = "true"
        compose["services"]["dev-ingress"]["ports"] = ["${DEV_INGRESS_HTTP_PORT:-80}:80"]

    _mutate_compose(stack, mutate)
    issues = validate_stack(stack)

    assert "Grafana anonymous authentication must be disabled" in issues
    assert any("dev-ingress port must bind to 127.0.0.1" in issue for issue in issues)


def test_validator_rejects_telemetry_identity_and_retention_drift(tmp_path: Path) -> None:
    stack = _copy_stack(tmp_path)
    _mutate_compose(
        stack,
        lambda compose: compose["services"]["lotus-manage"]["environment"].update(
            {"OTEL_SERVICE_NAME": "lotus-advise"}
        ),
    )
    collector_path = stack / "otel-collector" / "config.yaml"
    collector = _read_yaml(collector_path)
    collector["receivers"]["otlp"]["protocols"]["http"]["endpoint"] = "localhost:4318"
    collector["service"]["pipelines"]["traces"]["exporters"] = ["debug"]
    _write_yaml(collector_path, collector)

    issues = validate_stack(stack)

    assert any("lotus-manage.OTEL_SERVICE_NAME" in issue for issue in issues)
    assert "OTel HTTP receiver must listen on the container network at 0.0.0.0:4318" in issues
    assert "OTel traces pipeline must retain traces through otlp/tempo" in issues


def test_validator_rejects_missing_scrape_health_and_resource_controls(tmp_path: Path) -> None:
    stack = _copy_stack(tmp_path)
    prometheus_path = stack / "prometheus" / "prometheus.yml"
    prometheus = _read_yaml(prometheus_path)
    prometheus["scrape_configs"] = [
        item for item in prometheus["scrape_configs"] if item["job_name"] != "lotus-ai"
    ]
    _write_yaml(prometheus_path, prometheus)

    def mutate(compose: dict) -> None:
        compose["services"]["prometheus"].pop("healthcheck")
        compose["services"]["prometheus"].pop("cpus")
        compose["services"]["prometheus"].pop("extra_hosts")

    _mutate_compose(stack, mutate)
    issues = validate_stack(stack)

    assert any("Prometheus job inventory drift" in issue for issue in issues)
    assert "prometheus must define a healthcheck" in issues
    assert "prometheus must define CPU and memory limits" in issues
    assert "Prometheus must map host.docker.internal through host-gateway" in issues


def test_validator_rejects_workstation_paths_and_secret_template_values(tmp_path: Path) -> None:
    stack = _copy_stack(tmp_path)
    env_path = stack / ".env.example"
    env_path.write_text(
        env_path.read_text(encoding="utf-8")
        + "\nLOTUS_WORKSPACE_ROOT=C:/Users/example/projects\nLOTUS_TOKEN=tracked-value\n",
        encoding="utf-8",
    )

    issues = validate_stack(stack)

    assert ".env.example must not contain workstation-specific paths" in issues
    assert ".env.example must not contain secret values" in issues


def test_validator_rejects_missing_bootstrap_and_tls_profile(tmp_path: Path) -> None:
    stack = _copy_stack(tmp_path)
    (stack / "bootstrap.sh").unlink()
    (stack / "docker-compose.tls.yml").unlink()

    issues = validate_stack(stack)

    assert "platform stack is missing bootstrap.sh" in issues
    assert "platform stack must provide the Caddy local-CA TLS profile" in issues


def test_validator_rejects_late_umask_and_legacy_manage_volume(tmp_path: Path) -> None:
    stack = _copy_stack(tmp_path)
    bootstrap_path = stack / "bootstrap.sh"
    bootstrap_path.write_text(
        bootstrap_path.read_text(encoding="utf-8")
        .replace("umask 077\n", "")
        .replace("if ! value=$(new_secret); then", "if value=$(new_secret); then"),
        encoding="utf-8",
    )

    def reuse_legacy_manage_volume(compose: dict) -> None:
        compose["services"]["lotus-manage-postgres"]["volumes"] = [
            "lotus-manage-postgres-data:/var/lib/postgresql/data"
        ]
        compose["volumes"].pop("lotus-manage-postgres-identity-v2-data")
        compose["volumes"]["lotus-manage-postgres-data"] = None

    _mutate_compose(stack, reuse_legacy_manage_volume)

    issues = validate_stack(stack)

    assert "POSIX bootstrap must set umask 077 before creating .env" in issues
    assert "POSIX bootstrap must fail closed when secret generation fails" in issues
    assert "Manage PostgreSQL must use the identity-v2 data volume" in issues
    assert "Compose must declare the Manage identity-v2 data volume" in issues
    assert "Compose must not attach the legacy Manage PostgreSQL data volume" in issues


def test_platform_repo_lanes_enforce_stack_validation() -> None:
    repo_checks = (ROOT / "automation" / "Invoke-PlatformRepoChecks.ps1").read_text(
        encoding="utf-8"
    )

    assert "Invoke-CheckedCommand $toolingPython automation/validate_platform_stack.py" in repo_checks
