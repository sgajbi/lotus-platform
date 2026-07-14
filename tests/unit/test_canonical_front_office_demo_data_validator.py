from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "automation" / "validate_canonical_front_office_demo_data_contract.py"
CONTRACT_PATH = ROOT / "context" / "contracts" / "canonical-front-office-demo-data-contract.json"
INVARIANTS_PATH = (
    ROOT / "context" / "contracts" / "canonical-front-office-demo-data-invariants.json"
)
SEED_SCRIPT_PATH = ROOT / "automation" / "Invoke-DpmCommandCenterSeed.ps1"


def _validator():
    spec = importlib.util.spec_from_file_location(
        "validate_canonical_front_office_demo_data_contract", VALIDATOR_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _invariants() -> dict:
    return json.loads(INVARIANTS_PATH.read_text(encoding="utf-8"))


def _seed_script() -> str:
    return SEED_SCRIPT_PATH.read_text(encoding="utf-8")


def test_canonical_front_office_demo_data_contract_passes_focused_validation() -> None:
    assert _validator().validate_default_paths() == []


def test_validator_rejects_drift_from_canonical_dpm_seed_identity() -> None:
    contract = _contract()
    contract["dpm_command_center"]["portfolio_manager_id"] = "PM_LOCAL_SMOKE"

    errors = _validator().validate_contract(contract, _invariants(), _seed_script())

    assert "dpm_command_center.portfolio_manager_id must be PM_SG_DPM_001" in errors


def test_validator_rejects_missing_required_source_product_lineage() -> None:
    contract = _contract()
    contract["dpm_command_center"]["source_products"] = [
        "DiscretionaryMandateBinding:v1",
    ]

    errors = _validator().validate_contract(contract, _invariants(), _seed_script())

    assert any("ModelPortfolioTargets:v1" in error for error in errors)
    assert any("DpmMarketDataCoverage:v1" in error for error in errors)


def test_validator_rejects_seed_script_hardcoded_mandate_identity() -> None:
    errors = _validator().validate_contract(
        _contract(),
        _invariants(),
        f"{_seed_script()}\nMANDATE_PB_SG_GLOBAL_BAL_001\n",
    )

    assert "Invoke-DpmCommandCenterSeed.ps1 must read mandate identity from contract" in errors


def test_validator_rejects_missing_ready_partial_empty_posture_evidence() -> None:
    seed_script = _seed_script().replace("gateway-command-center-empty-posture", "")

    errors = _validator().validate_contract(_contract(), _invariants(), seed_script)

    assert (
        "Invoke-DpmCommandCenterSeed.ps1 is missing step "
        "gateway-command-center-empty-posture"
    ) in errors
