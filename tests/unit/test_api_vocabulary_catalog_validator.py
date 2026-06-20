from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = (
    ROOT
    / "platform-contracts"
    / "api-vocabulary"
    / "validate_api_vocabulary_catalog.py"
)


def _load_validator_module():
    spec = importlib.util.spec_from_file_location(
        "validate_api_vocabulary_catalog_test", VALIDATOR_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _payload(application: str, entries: list[dict[str, str]]) -> dict[str, object]:
    return {"application": application, "attributeCatalog": entries}


def _entry(
    semantic_id: str, canonical_term: str, preferred_name: str | None = None
) -> dict[str, str]:
    return {
        "semanticId": semantic_id,
        "canonicalTerm": canonical_term,
        "preferredName": preferred_name or canonical_term,
    }


def test_cross_app_validation_rejects_semantic_id_canonical_term_drift() -> None:
    validator = _load_validator_module()

    errors = validator.validate_cross_app(
        [
            _payload("lotus-core", [_entry("lotus.client_id", "client_id")]),
            _payload("lotus-gateway", [_entry("lotus.client_id", "customer_id")]),
        ]
    )

    assert any(
        "same semanticId has multiple canonical terms: lotus.client_id" in error
        for error in errors
    )


def test_cross_app_validation_rejects_canonical_term_semantic_id_drift() -> None:
    validator = _load_validator_module()

    errors = validator.validate_cross_app(
        [
            _payload("lotus-core", [_entry("lotus.client_id", "client_id")]),
            _payload("lotus-report", [_entry("lotus.customer_id", "client_id")]),
        ]
    )

    assert any(
        "same canonicalTerm maps to multiple semanticIds: client_id" in error
        for error in errors
    )


def test_cross_app_validation_rejects_legacy_and_canonical_conflict() -> None:
    validator = _load_validator_module()

    errors = validator.validate_cross_app(
        [
            _payload("lotus-core", [_entry("lotus.client_id", "client_id")]),
            _payload("lotus-report", [_entry("lotus.cif_id", "cif_id")]),
        ]
    )

    assert any(
        "legacy/canonical conflict across inventories: cif_id" in error
        for error in errors
    )

