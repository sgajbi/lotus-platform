from __future__ import annotations

from pathlib import Path

import automation.explain_dev_ingress_status as status_tool
import automation.validate_dev_ingress_smoke as smoke_tool


ROOT = Path(__file__).resolve().parents[2]


def test_dev_ingress_tools_use_governed_output_locations() -> None:
    assert smoke_tool.DEFAULT_OUTPUT_JSON == ROOT / "output" / "dev-ingress-smoke.json"
    assert smoke_tool.DEFAULT_OUTPUT_MD == ROOT / "output" / "dev-ingress-smoke.md"

    assert status_tool.DEFAULT_SMOKE_PATH == ROOT / "output" / "dev-ingress-smoke.json"
    assert status_tool.DEFAULT_STAGED_HOSTS_PATH == ROOT / "output" / "hosts-preview" / "hosts.merged"
    assert status_tool.DEFAULT_OUTPUT_JSON == ROOT / "output" / "dev-ingress-status.json"
    assert status_tool.DEFAULT_OUTPUT_MD == ROOT / "output" / "dev-ingress-status.md"


def test_dev_ingress_powershell_wrappers_use_same_default_output_paths() -> None:
    smoke_wrapper = (ROOT / "automation" / "Validate-Dev-Ingress-Smoke.ps1").read_text(encoding="utf-8")
    status_wrapper = (ROOT / "automation" / "Explain-Dev-Ingress-Status.ps1").read_text(encoding="utf-8")

    assert 'output/dev-ingress-smoke.json' in smoke_wrapper
    assert 'output/dev-ingress-smoke.md' in smoke_wrapper

    assert 'output/dev-ingress-smoke.json' in status_wrapper
    assert 'output/hosts-preview/hosts.merged' in status_wrapper
    assert 'output/dev-ingress-status.json' in status_wrapper
    assert 'output/dev-ingress-status.md' in status_wrapper
