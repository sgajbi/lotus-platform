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
LOTUS_CORE_PRODUCTS_PATH = (
    ROOT / "platform-contracts" / "domain-data-products" / "lotus-core-products.v1.json"
)


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


def _load_lotus_core_modules():
    import sys

    lotus_core_root = ROOT.parent / "lotus-core"
    sys.path.insert(0, str(lotus_core_root))
    sys.path.insert(0, str(lotus_core_root / "src" / "libs" / "portfolio-common"))
    from portfolio_common.source_data_products import (  # type: ignore
        ANALYTICS_INPUT,
        CONTROL_PLANE_AND_POLICY,
        OPERATIONAL_READ,
        QUERY_CONTROL_PLANE_SERVICE,
        QUERY_SERVICE,
        SNAPSHOT_AND_SIMULATION,
        SOURCE_DATA_PRODUCT_CATALOG,
    )
    from portfolio_common.source_data_security import get_source_data_security_profile  # type: ignore

    return {
        "ANALYTICS_INPUT": ANALYTICS_INPUT,
        "CONTROL_PLANE_AND_POLICY": CONTROL_PLANE_AND_POLICY,
        "OPERATIONAL_READ": OPERATIONAL_READ,
        "QUERY_CONTROL_PLANE_SERVICE": QUERY_CONTROL_PLANE_SERVICE,
        "QUERY_SERVICE": QUERY_SERVICE,
        "SNAPSHOT_AND_SIMULATION": SNAPSHOT_AND_SIMULATION,
        "SOURCE_DATA_PRODUCT_CATALOG": SOURCE_DATA_PRODUCT_CATALOG,
        "get_source_data_security_profile": get_source_data_security_profile,
    }


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


def test_rfc_0084_lotus_core_declaration_aligns_to_live_source_data_catalog() -> None:
    validator = _load_validator_module()
    core_modules = _load_lotus_core_modules()
    declaration = _load_json(LOTUS_CORE_PRODUCTS_PATH)

    assert validator.validate_producer_contract(LOTUS_CORE_PRODUCTS_PATH, declaration) == []

    family_map = {
        core_modules["OPERATIONAL_READ"]: "operational_source_data",
        core_modules["SNAPSHOT_AND_SIMULATION"]: "simulation_and_projected_state",
        core_modules["ANALYTICS_INPUT"]: "analytics_input",
        core_modules["CONTROL_PLANE_AND_POLICY"]: "supportability_and_control_plane",
    }

    catalog = core_modules["SOURCE_DATA_PRODUCT_CATALOG"]
    by_name = {product["product_name"]: product for product in declaration["products"]}

    assert declaration["producer_repository"] == "lotus-core"
    assert len(declaration["products"]) == len(catalog)

    for source_product in catalog:
        declared = by_name[source_product.product_name]
        profile = core_modules["get_source_data_security_profile"](source_product.product_name)

        assert declared["product_version"] == source_product.product_version
        assert declared["owner_repository"] == source_product.owner
        assert declared["product_family"] == family_map[source_product.route_family]
        assert declared["approved_consumers"] == list(source_product.consumers)
        assert declared["required_trust_metadata"] == list(source_product.required_metadata_fields)
        assert declared["serving_plane"] == source_product.serving_plane
        assert declared["current_routes"] == list(source_product.current_routes)
        assert declared["security_profile_ref"] == (
            f"{profile.access_classification}:{profile.sensitivity_classification}:"
            f"{profile.retention_requirement}:{profile.audit_requirement}"
        )

    assert by_name["MarketDataWindow"]["temporal_scope"]["primary_time_field"] == "valuation_date"
    assert by_name["MarketDataWindow"]["request_scope"]["scope_level"] == "benchmark"
    assert by_name["RiskFreeSeriesWindow"]["request_scope"]["scope_level"] == "global"
    assert by_name["IngestionEvidenceBundle"]["temporal_scope"]["primary_time_field"] == "ingested_at"
    assert by_name["ReconciliationEvidenceBundle"]["lineage_policy"]["evidence_bundle_required"] is True
