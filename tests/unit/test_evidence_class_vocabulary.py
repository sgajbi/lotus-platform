from __future__ import annotations

import copy
import json
from pathlib import Path

from automation.validate_evidence_class_vocabulary import validate


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = (
    ROOT
    / "platform-contracts"
    / "evidence-classification"
    / "evidence-class-vocabulary.v1.json"
)


def _load_contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_evidence_class_vocabulary_accepts_governed_current_state() -> None:
    assert validate() == []


def test_evidence_class_vocabulary_defines_canonical_persisted_values() -> None:
    contract = _load_contract()

    assert contract["ordering"] == [
        "source_contract",
        "test_execution",
        "ci_execution",
        "runtime_execution",
        "deployment",
        "production_certification",
    ]
    assert contract["persisted_artifact_policy"] == {
        "new_artifacts_must_use_canonical_ids": True,
        "legacy_aliases_are_closed": True,
        "arbitrary_aliases_allowed": False,
        "alias_normalization_must_be_explicit": True,
    }


def test_evidence_class_vocabulary_maps_legacy_terms_without_open_aliasing() -> None:
    contract = _load_contract()
    mapping = {
        alias: canonical["id"]
        for canonical in contract["canonical_persisted_vocabulary"]
        for alias in canonical["legacy_aliases"]
    }

    assert mapping == {
        "source_design_contract": "source_contract",
        "local_test_execution": "test_execution",
    }


def test_evidence_class_vocabulary_rejects_new_unmapped_alias(
    tmp_path: Path,
) -> None:
    contract = copy.deepcopy(_load_contract())
    contract["canonical_persisted_vocabulary"][0]["legacy_aliases"].append(
        "static_contract"
    )
    contract_path = tmp_path / "evidence-class-vocabulary.v1.json"
    contract_path.write_text(json.dumps(contract), encoding="utf-8")

    errors = validate(contract_path=contract_path)

    assert any("legacy evidence-class mapping must remain closed" in error for error in errors)


def test_evidence_class_vocabulary_rejects_context_without_mapping(
    tmp_path: Path,
) -> None:
    context_path = tmp_path / "LOTUS-ENGINEERING-CONTEXT.md"
    context_path.write_text("missing governed mapping", encoding="utf-8")

    errors = validate(engineering_context_path=context_path)

    assert any("engineering context missing evidence-class phrase" in error for error in errors)
