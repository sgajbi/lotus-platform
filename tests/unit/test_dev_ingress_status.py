from __future__ import annotations

from automation.explain_dev_ingress_status import explain_dev_ingress_status


def test_explain_dev_ingress_status_marks_runtime_ready_when_smoke_passes() -> None:
    payload = explain_dev_ingress_status(
        smoke_payload={"result": "ok", "checks": [], "failed_count": 0},
        staged_hosts_text="# >>> lotus-platform dev ingress >>>\n127.0.0.1 gateway.dev.lotus\n# <<< lotus-platform dev ingress <<<\n",
    )

    assert payload["status"] == "ready"
    assert "canonical local entrypoints" in payload["next_steps"][0]


def test_explain_dev_ingress_status_points_to_staged_hosts_when_dns_is_missing() -> None:
    payload = explain_dev_ingress_status(
        smoke_payload={
            "result": "failed",
            "failed_count": 2,
            "checks": [
                {"check_id": "gateway_dev_ingress_dns", "service_identity": "gateway", "passed": False},
                {"check_id": "gateway_dev_ingress", "service_identity": "gateway", "passed": False},
            ],
        },
        staged_hosts_text=(
            "127.0.0.1 localhost\n"
            "# >>> lotus-platform dev ingress >>>\n"
            "127.0.0.1 gateway.dev.lotus\n"
            "# <<< lotus-platform dev ingress <<<\n"
        ),
    )

    assert payload["status"] == "dns_not_configured"
    assert "output/hosts-preview/hosts.merged" in payload["next_steps"][0]
    assert payload["evidence"]["staged_hosts_present"] is True
    assert payload["evidence"]["staged_hostnames"] == ["gateway.dev.lotus"]


def test_explain_dev_ingress_status_points_to_services_when_dns_is_healthy_but_http_fails() -> None:
    payload = explain_dev_ingress_status(
        smoke_payload={
                "result": "failed",
                "failed_count": 2,
                "checks": [
                    {"check_id": "gateway_dev_ingress_dns", "service_identity": "gateway", "passed": True},
                    {"check_id": "gateway_dev_ingress", "service_identity": "gateway", "passed": False, "status": 502},
                    {"check_id": "core_query_dev_ingress_dns", "service_identity": "core-query", "passed": True},
                    {"check_id": "core_query_dev_ingress", "service_identity": "core-query", "passed": False, "status": 503},
                ],
            },
            staged_hosts_text=None,
    )

    assert payload["status"] == "services_unreachable"
    assert "core-query, gateway" in payload["next_steps"][0]
    assert payload["evidence"]["affected_services"] == ["core-query", "gateway"]
    assert payload["evidence"]["failing_http_statuses"] == [502, 503]


def test_explain_dev_ingress_status_requests_smoke_run_when_artifact_is_missing() -> None:
    payload = explain_dev_ingress_status(smoke_payload=None, staged_hosts_text=None)

    assert payload["status"] == "missing_smoke_result"
    assert "Validate-Dev-Ingress-Smoke.ps1" in payload["next_steps"][0]
