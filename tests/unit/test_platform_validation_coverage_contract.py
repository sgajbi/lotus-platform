from __future__ import annotations

from automation.validate_platform_validation_coverage import validate_platform_validation_coverage


def test_platform_validation_coverage_contract_accepts_manifest_workflow_and_entrypoint() -> None:
    assert validate_platform_validation_coverage() == []
