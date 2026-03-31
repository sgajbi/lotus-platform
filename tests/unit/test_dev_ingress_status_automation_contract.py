from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_ingress_status_explainer_is_documented_in_operator_guides() -> None:
    expected_snippet = "automation/Explain-Dev-Ingress-Status.ps1"

    automation_readme = (ROOT / "automation" / "README.md").read_text(encoding="utf-8")
    automation_guide = (ROOT / "automation" / "docs" / "Automation-Guide.md").read_text(encoding="utf-8")
    local_runbook = (ROOT / "Local Development Runbook.md").read_text(encoding="utf-8")
    platform_stack_readme = (ROOT / "platform-stack" / "README.md").read_text(encoding="utf-8")

    assert expected_snippet in automation_readme
    assert expected_snippet in automation_guide
    assert expected_snippet in local_runbook
    assert expected_snippet in platform_stack_readme

    expected_refresh_guidance = "docker compose up -d"
    assert expected_refresh_guidance in automation_guide
    assert expected_refresh_guidance in automation_readme
    assert expected_refresh_guidance in local_runbook
    assert expected_refresh_guidance in platform_stack_readme

    assert "ingress_unreachable" in automation_guide
    assert "docker compose up -d dev-ingress" in automation_guide
    assert "docker compose up -d dev-ingress" in automation_readme
    assert "docker compose up -d dev-ingress" in local_runbook
    assert "docker compose up -d dev-ingress" in platform_stack_readme


def test_ingress_status_explainer_wrapper_calls_python_entrypoint() -> None:
    wrapper = (ROOT / "automation" / "Explain-Dev-Ingress-Status.ps1").read_text(encoding="utf-8")

    assert "python automation/explain_dev_ingress_status.py" in wrapper
    assert "exit $LASTEXITCODE" in wrapper
