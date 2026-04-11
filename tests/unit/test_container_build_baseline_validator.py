from __future__ import annotations

from automation.validate_container_build_baseline import validate_container_build_baseline


def test_container_build_baseline_validator_accepts_platform_templates() -> None:
    assert validate_container_build_baseline() == []
