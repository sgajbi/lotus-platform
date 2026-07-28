from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT
    / "platform-contracts"
    / "evidence-classification"
    / "evidence-class-vocabulary.v1.json"
)
BANK_READINESS_CATALOG_PATH = (
    ROOT
    / "platform-contracts"
    / "bank-readiness"
    / "bank-ready-control-catalog.v1.json"
)
BACKEND_EVIDENCE_REFERENCE_PATH = (
    ROOT
    / "codex"
    / "skills"
    / "lotus-backend-delivery-governance"
    / "references"
    / "evidence-classification.md"
)
ENGINEERING_CONTEXT_PATH = ROOT / "context" / "LOTUS-ENGINEERING-CONTEXT.md"

EXPECTED_CANONICAL_CLASSES = [
    "source_contract",
    "test_execution",
    "ci_execution",
    "runtime_execution",
    "deployment",
    "production_certification",
]
EXPECTED_LEGACY_MAPPING = {
    "source_design_contract": "source_contract",
    "local_test_execution": "test_execution",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_to_aliases(contract: dict[str, Any]) -> dict[str, set[str]]:
    return {
        item["id"]: set(item.get("legacy_aliases", []))
        for item in contract.get("canonical_persisted_vocabulary", [])
    }


def _alias_to_canonical(contract: dict[str, Any]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for canonical in contract.get("canonical_persisted_vocabulary", []):
        canonical_id = canonical.get("id")
        for alias in canonical.get("legacy_aliases", []):
            mapping[alias] = canonical_id
    return mapping


def validate(
    *,
    contract_path: Path = CONTRACT_PATH,
    bank_readiness_catalog_path: Path = BANK_READINESS_CATALOG_PATH,
    backend_evidence_reference_path: Path = BACKEND_EVIDENCE_REFERENCE_PATH,
    engineering_context_path: Path = ENGINEERING_CONTEXT_PATH,
) -> list[str]:
    contract = _load_json(contract_path)
    errors: list[str] = []

    if contract.get("contract_id") != "lotus-evidence-class-vocabulary":
        errors.append("contract_id must be lotus-evidence-class-vocabulary")
    if contract.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")

    canonical_ids = [
        item.get("id") for item in contract.get("canonical_persisted_vocabulary", [])
    ]
    if canonical_ids != EXPECTED_CANONICAL_CLASSES:
        errors.append("canonical_persisted_vocabulary order or values drifted")
    if contract.get("ordering") != EXPECTED_CANONICAL_CLASSES:
        errors.append("ordering must match canonical persisted evidence classes")

    alias_mapping = _alias_to_canonical(contract)
    if alias_mapping != EXPECTED_LEGACY_MAPPING:
        errors.append("legacy evidence-class mapping must remain closed and explicit")

    aliases_by_canonical = _canonical_to_aliases(contract)
    for alias, canonical in EXPECTED_LEGACY_MAPPING.items():
        if alias not in aliases_by_canonical.get(canonical, set()):
            errors.append(f"{alias} must map to {canonical}")

    _validate_legacy_contexts(contract, bank_readiness_catalog_path, errors)
    _validate_skill_reference(backend_evidence_reference_path, errors)
    _validate_engineering_context(engineering_context_path, errors)
    return errors


def _validate_legacy_contexts(
    contract: dict[str, Any],
    bank_readiness_catalog_path: Path,
    errors: list[str],
) -> None:
    allowed_by_context = {
        item.get("context_id"): set(item.get("allowed_legacy_values", []))
        for item in contract.get("legacy_allowed_contexts", [])
    }
    if (
        allowed_by_context.get("bank_readiness_control_catalog")
        != set(EXPECTED_LEGACY_MAPPING)
    ):
        errors.append("bank-readiness legacy context must allow only mapped legacy values")

    catalog = _load_json(bank_readiness_catalog_path)
    supported_catalog_classes = set(catalog.get("evidence_classes", []))
    unmapped_catalog_classes = supported_catalog_classes - (
        set(EXPECTED_CANONICAL_CLASSES) | set(EXPECTED_LEGACY_MAPPING)
    )
    if unmapped_catalog_classes:
        errors.append(
            f"bank-readiness catalog contains unmapped evidence classes "
            f"{sorted(unmapped_catalog_classes)}"
        )


def _validate_skill_reference(reference_path: Path, errors: list[str]) -> None:
    reference = reference_path.read_text(encoding="utf-8")
    required_phrases = [
        "Canonical persisted vocabulary",
        "source_design_contract` maps to `source_contract",
        "local_test_execution` maps to `test_execution",
        "source_contract` evidence cannot clear `runtime_execution",
    ]
    for phrase in required_phrases:
        if phrase not in reference:
            errors.append(f"evidence-classification reference missing {phrase}")
    for evidence_class in EXPECTED_CANONICAL_CLASSES:
        if evidence_class not in reference:
            errors.append(f"evidence-classification reference missing {evidence_class}")


def _validate_engineering_context(context_path: Path, errors: list[str]) -> None:
    context = context_path.read_text(encoding="utf-8")
    required_phrases = [
        "platform-contracts/evidence-classification/evidence-class-vocabulary.v1.json",
        "`source_contract`, `test_execution`, `ci_execution`, `runtime_execution`,",
        "`source_design_contract` and `local_test_execution` are closed legacy mappings",
    ]
    for phrase in required_phrases:
        if phrase not in context:
            errors.append(f"engineering context missing evidence-class phrase {phrase}")


def main() -> int:
    errors = validate()
    for error in errors:
        print(error)
    if errors:
        return 1
    print("Evidence class vocabulary contract validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
