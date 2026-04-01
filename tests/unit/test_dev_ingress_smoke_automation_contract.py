from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_task_profiles_wire_dev_ingress_smoke_into_governance_profiles() -> None:
    profiles_doc = json.loads((ROOT / "automation" / "task-profiles.json").read_text(encoding="utf-8"))
    profiles = {profile["name"]: profile for profile in profiles_doc["profiles"]}

    expected_command = (
        "powershell -ExecutionPolicy Bypass -File automation/Validate-Dev-Ingress-Smoke.ps1"
    )

    for profile_name in ("platform-alignment", "autonomous-foundation"):
        task_commands = {task["command"] for task in profiles[profile_name]["tasks"]}
        assert expected_command in task_commands


def test_agent_and_pulse_include_dev_ingress_smoke_validation() -> None:
    run_agent = (ROOT / "automation" / "Run-Agent.ps1").read_text(encoding="utf-8")
    platform_pulse = (ROOT / "automation" / "Platform-Pulse.ps1").read_text(encoding="utf-8")

    expected_snippet = 'automation/Validate-Dev-Ingress-Smoke.ps1'

    assert expected_snippet in run_agent
    assert expected_snippet in platform_pulse
