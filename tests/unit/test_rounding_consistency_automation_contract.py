"""Protect package-context isolation in cross-repository rounding validation."""

from pathlib import Path


SCRIPT = Path("automation/Validate-Rounding-Consistency.ps1")


def test_rounding_validator_loads_each_policy_in_an_isolated_package_context() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert '"src/services/query_service", "app.precision_policy"' in source
    assert '"src", "core.precision_policy"' in source
    assert "subprocess.run(" in source
    assert "importlib.import_module(module_name)" in source
    assert "spec_from_file_location" not in source
    assert "unable to load {module_name} in package context" in source
