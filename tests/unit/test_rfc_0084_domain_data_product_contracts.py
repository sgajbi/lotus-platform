from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRODUCER_SCHEMA_PATH = ROOT / "platform-contracts" / "domain-data-products.schema.json"
CONSUMER_SCHEMA_PATH = ROOT / "platform-contracts" / "domain-data-product-consumers.schema.json"
README_PATH = ROOT / "platform-contracts" / "domain-data-products" / "README.md"
VALIDATOR_PATH = ROOT / "platform-contracts" / "domain-data-products" / "validate_domain_data_product_contracts.py"
EVIDENCE_PATH = ROOT / "rfcs" / "RFC-0084-slice-1-schema-evidence.md"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_validator_module():
    spec = importlib.util.spec_from_file_location("rfc_0084_validator", VALIDATOR_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_rfc_0084_slice_1_contract_family_is_present_and_governed() -> None:
    producer_schema = _load_json(PRODUCER_SCHEMA_PATH)
    consumer_schema = _load_json(CONSUMER_SCHEMA_PATH)
    readme = README_PATH.read_text(encoding="utf-8")
    evidence = EVIDENCE_PATH.read_text(encoding="utf-8")

    assert producer_schema["properties"]["contract_id"]["const"] == "domain-data-products"
    assert producer_schema["properties"]["governed_by_rfc"]["const"] == "RFC-0084"
    assert producer_schema["$defs"]["productFamily"]["enum"][0] == "operational_source_data"
    assert "domain-data-products.schema.json" in readme
    assert "domain-data-product-consumers.schema.json" in readme
    assert "validate_domain_data_product_contracts.py" in readme

    assert consumer_schema["properties"]["contract_id"]["const"] == "domain-data-product-consumers"
    assert consumer_schema["properties"]["governed_by_rfc"]["const"] == "RFC-0084"
    assert "platform-contracts/domain-data-products/" in evidence
    assert "mandatory slice review" in evidence.lower()


def test_rfc_0084_validator_accepts_valid_producer_and_consumer_contracts(tmp_path: Path) -> None:
    validator = _load_validator_module()

    _write_json(
        tmp_path / "lotus-core-products.v1.json",
        {
            "contract_id": "domain-data-products",
            "contract_version": "1.0.0",
            "governed_by_rfc": "RFC-0084",
            "producer_repository": "lotus-core",
            "authoritative_domain": "portfolio_state",
            "products": [
                {
                    "product_name": "PortfolioStateSnapshot",
                    "product_version": "1.0.0",
                    "owner_repository": "lotus-core",
                    "product_family": "operational_source_data",
                    "authoritative_domain": "portfolio_state",
                    "lifecycle_status": "active",
                    "request_scope": {"scope_level": "portfolio", "supports_bulk": False},
                    "temporal_scope": {
                        "primary_time_field": "as_of_date",
                        "freshness_basis": "as_of_date",
                        "supports_restatement": True
                    },
                    "required_trust_metadata": [
                        "product_name",
                        "product_version",
                        "as_of_date",
                        "reconciliation_status",
                        "data_quality_status",
                        "lineage_bundle_id"
                    ],
                    "freshness_policy": {
                        "freshness_class": "daily",
                        "max_allowed_age_description": "Must be current for the governed as-of date."
                    },
                    "completeness_policy": {
                        "default_status": "complete",
                        "partial_allowed": True
                    },
                    "lineage_policy": {
                        "lineage_required": True,
                        "evidence_bundle_required": True
                    },
                    "security_profile_ref": "source_data_read.standard",
                    "approved_consumers": ["lotus-performance", "lotus-risk"],
                    "deprecation_policy": {
                        "state": "not_deprecated",
                        "successor_product": None
                    }
                }
            ]
        }
    )

    _write_json(
        tmp_path / "lotus-performance-consumers.v1.json",
        {
            "contract_id": "domain-data-product-consumers",
            "contract_version": "1.0.0",
            "governed_by_rfc": "RFC-0084",
            "consumer_repository": "lotus-performance",
            "dependencies": [
                {
                    "product_name": "PortfolioStateSnapshot",
                    "producer_repository": "lotus-core",
                    "required_product_version": "1.0.0",
                    "consumption_mode": "api_read",
                    "business_purpose": "Seed governed portfolio state into analytics orchestration.",
                    "validation_lanes": ["feature", "pr-merge"],
                    "failure_posture": "fail_closed"
                }
            ]
        }
    )

    assert validator.validate_contract_directory(tmp_path) == []


def test_rfc_0084_validator_rejects_unknown_and_duplicate_dependencies(tmp_path: Path) -> None:
    validator = _load_validator_module()

    _write_json(
        tmp_path / "lotus-core-products.v1.json",
        {
            "contract_id": "domain-data-products",
            "contract_version": "1.0.0",
            "governed_by_rfc": "RFC-0084",
            "producer_repository": "lotus-core",
            "authoritative_domain": "portfolio_state",
            "products": [
                {
                    "product_name": "PortfolioStateSnapshot",
                    "product_version": "1.0.0",
                    "owner_repository": "lotus-core",
                    "product_family": "operational_source_data",
                    "authoritative_domain": "portfolio_state",
                    "lifecycle_status": "active",
                    "request_scope": {"scope_level": "portfolio", "supports_bulk": False},
                    "temporal_scope": {
                        "primary_time_field": "as_of_date",
                        "freshness_basis": "as_of_date",
                        "supports_restatement": True
                    },
                    "required_trust_metadata": ["product_name"],
                    "freshness_policy": {
                        "freshness_class": "daily",
                        "max_allowed_age_description": "Daily."
                    },
                    "completeness_policy": {
                        "default_status": "complete",
                        "partial_allowed": False
                    },
                    "lineage_policy": {
                        "lineage_required": True,
                        "evidence_bundle_required": True
                    },
                    "security_profile_ref": "source_data_read.standard",
                    "approved_consumers": ["lotus-performance"],
                    "deprecation_policy": {
                        "state": "not_deprecated",
                        "successor_product": None
                    }
                },
                {
                    "product_name": "PortfolioStateSnapshot",
                    "product_version": "1.0.0",
                    "owner_repository": "lotus-core",
                    "product_family": "operational_source_data",
                    "authoritative_domain": "portfolio_state",
                    "lifecycle_status": "active",
                    "request_scope": {"scope_level": "portfolio", "supports_bulk": False},
                    "temporal_scope": {
                        "primary_time_field": "as_of_date",
                        "freshness_basis": "as_of_date",
                        "supports_restatement": True
                    },
                    "required_trust_metadata": ["product_name"],
                    "freshness_policy": {
                        "freshness_class": "daily",
                        "max_allowed_age_description": "Daily."
                    },
                    "completeness_policy": {
                        "default_status": "complete",
                        "partial_allowed": False
                    },
                    "lineage_policy": {
                        "lineage_required": True,
                        "evidence_bundle_required": True
                    },
                    "security_profile_ref": "source_data_read.standard",
                    "approved_consumers": ["lotus-performance"],
                    "deprecation_policy": {
                        "state": "not_deprecated",
                        "successor_product": None
                    }
                }
            ]
        }
    )

    _write_json(
        tmp_path / "lotus-risk-consumers.v1.json",
        {
            "contract_id": "domain-data-product-consumers",
            "contract_version": "1.0.0",
            "governed_by_rfc": "RFC-0084",
            "consumer_repository": "lotus-risk",
            "dependencies": [
                {
                    "product_name": "PortfolioStateSnapshot",
                    "producer_repository": "lotus-core",
                    "required_product_version": "2.0.0",
                    "consumption_mode": "api_read",
                    "business_purpose": "Use upstream state snapshot.",
                    "validation_lanes": ["feature"],
                    "failure_posture": "fail_closed"
                }
            ]
        }
    )

    issues = validator.validate_contract_directory(tmp_path)

    assert any("duplicate product declaration" in issue for issue in issues)
    assert any("references unknown product declaration" in issue for issue in issues)
