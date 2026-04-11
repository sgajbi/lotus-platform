from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "automation" / "validate_engineering_context_system.py"


def _load_validator_module():
    spec = importlib.util.spec_from_file_location("validate_engineering_context_system", VALIDATOR_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_engineering_context_validator_passes_for_governed_context_set() -> None:
    validator = _load_validator_module()

    errors = validator.validate_engineering_context_system()

    assert errors == []


def test_engineering_context_validator_builds_success_markdown() -> None:
    validator = _load_validator_module()

    markdown = validator.build_markdown([])

    assert "Engineering Context System Validation" in markdown
    assert "Status: `ok`" in markdown
    assert "synchronized and valid" in markdown
