from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
PLATFORM_STACK_DIR = ROOT / "platform-stack"


def _read_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def test_platform_stack_prometheus_scrapes_the_expected_orchestrated_services() -> None:
    prometheus = _read_yaml(PLATFORM_STACK_DIR / "prometheus" / "prometheus.yml")
    actual_jobs = {job["job_name"] for job in prometheus["scrape_configs"]}

    assert actual_jobs == {
        "lotus-gateway",
        "lotus-archive",
        "lotus-advise",
        "lotus-ai",
        "lotus-core-control",
        "lotus-core-ingestion",
        "lotus-core-query",
        "lotus-idea",
        "lotus-manage",
        "lotus-performance",
        "lotus-render",
        "lotus-report",
        "lotus-risk",
        "lotus-workbench",
    }


def test_platform_stack_prometheus_targets_match_platform_stack_service_names() -> None:
    compose = _read_yaml(PLATFORM_STACK_DIR / "docker-compose.yml")
    prometheus = _read_yaml(PLATFORM_STACK_DIR / "prometheus" / "prometheus.yml")

    services = compose["services"]
    assert "host.docker.internal:host-gateway" in services["prometheus"]["extra_hosts"]
    platform_owned_bridge_hosts = {"host.docker.internal"}
    for job in prometheus["scrape_configs"]:
        target = job["static_configs"][0]["targets"][0]
        host = target.split(":", maxsplit=1)[0]
        assert host in services or host in platform_owned_bridge_hosts
