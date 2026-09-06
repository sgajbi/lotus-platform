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


def test_application_agent_contract_sync_warns_for_external_repo_drift() -> None:
    validator = _load_validator_module()
    errors: list[str] = []
    warnings: list[str] = []

    validator._validate_application_agent_contract_sync(
        errors=errors,
        warnings=warnings,
        applications=[
            {
                "repository": "lotus-core",
                "repo_context_path": "REPOSITORY-ENGINEERING-CONTEXT.md",
            }
        ],
        normalized_agents_contract="new contract",
    )

    assert errors == []
    assert any("lotus-core: repo-root AGENTS.md is not synchronized" in warning for warning in warnings)


def test_application_context_sync_warns_when_registered_context_is_missing(
    tmp_path: Path, monkeypatch
) -> None:
    validator = _load_validator_module()
    monkeypatch.setattr(validator, "WORKSPACE_ROOT", tmp_path)
    (tmp_path / "lotus-core").mkdir()
    errors: list[str] = []
    warnings: list[str] = []

    validator._validate_application_agent_contract_sync(
        errors=errors,
        warnings=warnings,
        applications=[{"repository": "lotus-core"}],
        normalized_agents_contract="contract",
    )

    assert errors == []
    assert warnings == ["lotus-core: missing REPOSITORY-ENGINEERING-CONTEXT.md"]


def test_agents_operating_contract_validator_reports_missing_required_guidance() -> None:
    validator = _load_validator_module()
    errors: list[str] = []

    validator._validate_agents_operating_contract(
        errors=errors,
        agents_contract="Progressive Context Discovery\nMandatory Operating Rules",
    )

    assert "AGENTS-OPERATING-CONTRACT.md: missing section `Context Maintenance Rule`" in errors
    assert (
        "AGENTS-OPERATING-CONTRACT.md: missing procedural memory index cross-link"
        in errors
    )
    assert (
        "AGENTS-OPERATING-CONTRACT.md: missing agent context and task ledger playbook cross-link"
        in errors
    )
    assert (
        "AGENTS-OPERATING-CONTRACT.md: missing background-run evidence guidance"
        in errors
    )
    assert (
        "AGENTS-OPERATING-CONTRACT.md: missing repo-root synchronization guidance"
        in errors
    )
    assert (
        "AGENTS-OPERATING-CONTRACT.md: missing front-office runtime routing `PB_SG_GLOBAL_BAL_001`"
        in errors
    )

