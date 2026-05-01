from __future__ import annotations

import automation.validate_dev_ingress_smoke as validator
from automation.validate_dev_ingress_smoke import (
    build_dev_ingress_checks,
    validate_dev_ingress_smoke,
)


def _expected_service_identities() -> set[str]:
    return {check.service_identity for check in build_dev_ingress_checks()}


def test_validate_dev_ingress_smoke_accepts_resolved_reachable_endpoints(monkeypatch) -> None:
    monkeypatch.setattr(validator, "_resolve_host", lambda hostname: (True, "127.0.0.1"))
    monkeypatch.setattr(validator, "_probe", lambda url, timeout_seconds: (True, 200, ""))

    result = validate_dev_ingress_smoke(timeout_seconds=1)

    assert result["result"] == "ok"
    assert result["failed_count"] == 0
    assert len(result["checks"]) == len(build_dev_ingress_checks()) * 2
    assert {check["failure_posture"] for check in result["checks"]} == {"healthy"}
    assert {check["service_identity"] for check in result["checks"]} == (
        _expected_service_identities()
    )


def test_validate_dev_ingress_smoke_flags_dns_and_http_failures(monkeypatch) -> None:
    def fake_resolve(hostname: str):
        if hostname == "workbench.dev.lotus":
            return False, "host not found"
        return True, "127.0.0.1"

    def fake_probe(url: str, timeout_seconds: int):
        if "gateway.dev.lotus" in url:
            return False, 502, "bad gateway"
        return True, 200, ""

    monkeypatch.setattr(validator, "_resolve_host", fake_resolve)
    monkeypatch.setattr(validator, "_probe", fake_probe)

    result = validate_dev_ingress_smoke(timeout_seconds=1)

    assert result["result"] == "failed"
    failed_ids = {check["check_id"] for check in result["checks"] if not check["passed"]}
    assert "workbench_dev_ingress_dns" in failed_ids
    assert "workbench_dev_ingress" in failed_ids
    assert "gateway_dev_ingress" in failed_ids
    postures = {
        check["check_id"]: check["failure_posture"]
        for check in result["checks"]
        if not check["passed"]
    }
    assert postures["workbench_dev_ingress_dns"] == "dns_resolution_failed"
    assert postures["workbench_dev_ingress"] == "dns_resolution_failed"
    assert postures["gateway_dev_ingress"] == "http_error"
    failing_services = {
        check["service_identity"]
        for check in result["checks"]
        if not check["passed"]
    }
    assert failing_services == {"workbench", "gateway"}
