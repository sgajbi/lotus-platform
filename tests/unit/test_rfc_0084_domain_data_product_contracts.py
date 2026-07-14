from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
LOTUS_CORE_PREVIEW_ENV = "LOTUS_RFC0084_LIVE_CORE_PREVIEW"
PRODUCER_SCHEMA_PATH = ROOT / "platform-contracts" / "domain-data-products.schema.json"
CONSUMER_SCHEMA_PATH = (
    ROOT / "platform-contracts" / "domain-data-product-consumers.schema.json"
)
README_PATH = ROOT / "platform-contracts" / "domain-data-products" / "README.md"
VALIDATOR_PATH = (
    ROOT
    / "platform-contracts"
    / "domain-data-products"
    / "validate_domain_data_product_contracts.py"
)
EVIDENCE_PATH = ROOT / "rfcs" / "RFC-0084-slice-1-schema-evidence.md"
SLICE_3_EVIDENCE_PATH = (
    ROOT / "rfcs" / "RFC-0084-slice-3-analytics-producer-onboarding-evidence.md"
)
SEMANTICS_REGISTRY_PATH = (
    ROOT
    / "platform-contracts"
    / "domain-vocabulary"
    / "domain-data-product-semantics.v1.json"
)
TRUST_METADATA_REGISTRY_PATH = (
    ROOT
    / "platform-contracts"
    / "domain-vocabulary"
    / "domain-data-product-trust-metadata.v1.json"
)
LOTUS_CORE_PRODUCTS_PATH = (
    ROOT / "platform-contracts" / "domain-data-products" / "lotus-core-products.v1.json"
)
LOTUS_PERFORMANCE_PRODUCTS_PATH = (
    ROOT
    / "platform-contracts"
    / "domain-data-products"
    / "lotus-performance-products.v1.json"
)
LOTUS_PERFORMANCE_CONSUMERS_PATH = (
    ROOT
    / "platform-contracts"
    / "domain-data-products"
    / "lotus-performance-consumers.v1.json"
)
LOTUS_RISK_PRODUCTS_PATH = (
    ROOT / "platform-contracts" / "domain-data-products" / "lotus-risk-products.v1.json"
)
LOTUS_RISK_CONSUMERS_PATH = (
    ROOT
    / "platform-contracts"
    / "domain-data-products"
    / "lotus-risk-consumers.v1.json"
)
DOMAIN_PRODUCT_CATALOG_PATH = ROOT / "generated" / "domain-product-catalog.json"


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


def _consumer_contract_with_migration_posture(migration_posture: dict) -> dict:
    return {
        "contract_id": "domain-data-product-consumers",
        "contract_version": "1.0.0",
        "governed_by_rfc": "RFC-0084",
        "consumer_repository": "lotus-risk",
        "dependencies": [
            {
                "product_name": "ReturnsSeriesBundle",
                "producer_repository": "lotus-performance",
                "required_product_version": "v1",
                "required_trust_metadata": ["generated_at"],
                "migration_posture": migration_posture,
                "consumption_mode": "api_read",
                "business_purpose": "Use upstream return series in risk analytics.",
                "validation_lanes": ["feature"],
                "failure_posture": "fail_closed",
            }
        ],
    }


def _load_repo_text(repository: str, relative_path: str) -> str:
    return (ROOT.parent / repository / relative_path).read_text(encoding="utf-8")


def test_rfc_0084_producer_contract_rejects_malformed_identity_and_products(
    tmp_path: Path,
) -> None:
    validator = _load_validator_module()
    path = tmp_path / "invalid-products.json"
    payload = {
        "contract_id": "wrong",
        "governed_by_rfc": "RFC-0000",
        "producer_repository": "core",
        "contract_version": "latest",
        "products": [],
    }

    issues = validator.validate_producer_contract(path, payload)

    assert f"{path}: contract_id must be 'domain-data-products'" in issues
    assert f"{path}: governed_by_rfc must be 'RFC-0084'" in issues
    assert f"{path}: producer_repository must match lotus repo naming" in issues
    assert f"{path}: contract_version must be semantic versioning" in issues
    assert f"{path}: products must be a non-empty array" in issues


def _write_semantics_registry(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _write_json(
        path,
        {
            "contract_id": "domain-data-product-semantics",
            "contract_version": "1.0.0",
            "governed_by_rfc": "RFC-0084",
            "domain": "domain_data_product_semantics",
            "description": "Test semantics registry.",
            "identifiers": [
                {
                    "key": "portfolio_id",
                    "semantic_id": "lotus.portfolio_id",
                    "stability": "stable",
                    "lifecycle": "active",
                    "description": "Portfolio identifier.",
                },
                {
                    "key": "calculation_id",
                    "semantic_id": "lotus.calculation_id",
                    "stability": "ephemeral",
                    "lifecycle": "active",
                    "description": "Calculation identifier.",
                },
            ],
            "temporal_semantics": [
                {
                    "key": "as_of_date",
                    "semantic_id": "lotus.as_of_date",
                    "category": "business_effective_date",
                    "description": "As-of date.",
                },
                {
                    "key": "valuation_date",
                    "semantic_id": "lotus.valuation_date",
                    "category": "observation_date",
                    "description": "Valuation date.",
                },
            ],
            "trust_vocabularies": {
                "freshness_classes": [{"key": "daily", "meaning": "Daily."}],
                "completeness_statuses": [{"key": "complete", "meaning": "Complete."}],
                "reconciliation_statuses": [
                    {"key": "reconciled", "meaning": "Reconciled."}
                ],
                "data_quality_statuses": [
                    {"key": "quality_passed", "meaning": "Passed."}
                ],
            },
        },
    )


def _write_trust_metadata_registry(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _write_json(
        path,
        {
            "contract_id": "domain-data-product-trust-metadata",
            "contract_version": "1.0.0",
            "governed_by_rfc": "RFC-0084",
            "domain": "domain_data_product_trust",
            "description": "Test trust metadata registry.",
            "evidence_access_classes": [
                {"key": "customer_consumable", "description": "Customer-facing."},
                {"key": "operator_only", "description": "Operator-only."},
            ],
            "trust_metadata_fields": [
                {
                    "key": "product_name",
                    "semantic_id": "lotus.product_name",
                    "evidence_access_class": "customer_consumable",
                    "description": "Product name.",
                },
                {
                    "key": "product_version",
                    "semantic_id": "lotus.product_version",
                    "evidence_access_class": "customer_consumable",
                    "description": "Product version.",
                },
                {
                    "key": "as_of_date",
                    "semantic_id": "lotus.as_of_date",
                    "evidence_access_class": "customer_consumable",
                    "description": "As-of date.",
                },
                {
                    "key": "generated_at",
                    "semantic_id": "lotus.generated_at",
                    "evidence_access_class": "customer_consumable",
                    "description": "Generated at.",
                },
                {
                    "key": "reconciliation_status",
                    "semantic_id": "lotus.reconciliation_status",
                    "evidence_access_class": "customer_consumable",
                    "description": "Reconciliation status.",
                },
                {
                    "key": "data_quality_status",
                    "semantic_id": "lotus.data_quality_status",
                    "evidence_access_class": "customer_consumable",
                    "description": "Data-quality status.",
                },
                {
                    "key": "lineage_bundle_id",
                    "semantic_id": "lotus.lineage_bundle_id",
                    "evidence_access_class": "operator_only",
                    "description": "Lineage bundle id.",
                },
                {
                    "key": "correlation_id",
                    "semantic_id": "lotus.correlation_id",
                    "evidence_access_class": "customer_consumable",
                    "description": "Correlation id.",
                },
                {
                    "key": "latest_evidence_timestamp",
                    "semantic_id": "lotus.latest_evidence_timestamp",
                    "evidence_access_class": "operator_only",
                    "description": "Latest evidence timestamp.",
                },
                {
                    "key": "request_fingerprint",
                    "semantic_id": "lotus.request_fingerprint",
                    "evidence_access_class": "customer_consumable",
                    "description": "Request fingerprint.",
                },
            ],
            "lineage_bundle_classes": [
                {
                    "key": "customer_lineage_summary",
                    "evidence_access_class": "customer_consumable",
                    "required_fields": [
                        "generated_at",
                        "correlation_id",
                        "request_fingerprint",
                    ],
                    "description": "Customer lineage summary.",
                },
                {
                    "key": "operator_reconciliation_evidence",
                    "evidence_access_class": "operator_only",
                    "required_fields": [
                        "generated_at",
                        "correlation_id",
                        "reconciliation_status",
                        "latest_evidence_timestamp",
                    ],
                    "description": "Operator reconciliation evidence.",
                },
                {
                    "key": "operator_quality_evidence",
                    "evidence_access_class": "operator_only",
                    "required_fields": [
                        "generated_at",
                        "correlation_id",
                        "data_quality_status",
                        "latest_evidence_timestamp",
                    ],
                    "description": "Operator quality evidence.",
                },
                {
                    "key": "operator_ingestion_evidence",
                    "evidence_access_class": "operator_only",
                    "required_fields": [
                        "generated_at",
                        "correlation_id",
                        "latest_evidence_timestamp",
                    ],
                    "description": "Operator ingestion evidence.",
                },
            ],
        },
    )


def _load_lotus_core_modules():
    import sys

    lotus_core_root = ROOT.parent / "lotus-core"
    if not lotus_core_root.exists():
        pytest.skip(
            "lotus-core sibling checkout is missing; live source preview is "
            f"diagnostic-only and requires {LOTUS_CORE_PREVIEW_ENV}=1"
        )
    sys.path.insert(0, str(lotus_core_root))
    sys.path.insert(0, str(lotus_core_root / "src" / "libs" / "portfolio-common"))
    from portfolio_common.source_data_products import (  # type: ignore
        ANALYTICS_INPUT,
        CONTROL_PLANE_AND_POLICY,
        OPERATIONAL_READ,
        QUERY_CONTROL_PLANE_SERVICE,
        QUERY_SERVICE,
        SNAPSHOT_AND_SIMULATION,
        DPM_PLANNED_SOURCE_DATA_PRODUCT_CATALOG,
        SOURCE_DATA_PRODUCT_CATALOG,
    )
    from portfolio_common.source_data_security import (  # type: ignore
        DPM_PLANNED_SOURCE_DATA_SECURITY_PROFILES,
        SOURCE_DATA_SECURITY_PROFILES,
    )

    return {
        "ANALYTICS_INPUT": ANALYTICS_INPUT,
        "CONTROL_PLANE_AND_POLICY": CONTROL_PLANE_AND_POLICY,
        "OPERATIONAL_READ": OPERATIONAL_READ,
        "QUERY_CONTROL_PLANE_SERVICE": QUERY_CONTROL_PLANE_SERVICE,
        "QUERY_SERVICE": QUERY_SERVICE,
        "SNAPSHOT_AND_SIMULATION": SNAPSHOT_AND_SIMULATION,
        "DPM_PLANNED_SOURCE_DATA_PRODUCT_CATALOG": DPM_PLANNED_SOURCE_DATA_PRODUCT_CATALOG,
        "SOURCE_DATA_PRODUCT_CATALOG": SOURCE_DATA_PRODUCT_CATALOG,
        "SOURCE_DATA_SECURITY_PROFILES": SOURCE_DATA_SECURITY_PROFILES,
        "DPM_PLANNED_SOURCE_DATA_SECURITY_PROFILES": DPM_PLANNED_SOURCE_DATA_SECURITY_PROFILES,
    }


def _live_lotus_core_preview_enabled() -> bool:
    return os.getenv(LOTUS_CORE_PREVIEW_ENV, "").lower() in {"1", "true", "yes"}


def _skip_unless_live_lotus_core_preview_enabled() -> None:
    if _live_lotus_core_preview_enabled():
        return
    pytest.skip(
        "Default RFC-0084 gates use checked-in platform declaration/catalog truth. "
        f"Set {LOTUS_CORE_PREVIEW_ENV}=1 for diagnostic sibling lotus-core preview."
    )


def _assert_lotus_core_declaration_matches_source_catalog(
    declaration: dict,
    core_modules: dict,
) -> None:
    family_map = {
        core_modules["OPERATIONAL_READ"]: "operational_source_data",
        core_modules["SNAPSHOT_AND_SIMULATION"]: "simulation_and_projected_state",
        core_modules["ANALYTICS_INPUT"]: "analytics_input",
        core_modules["CONTROL_PLANE_AND_POLICY"]: "supportability_and_control_plane",
    }

    catalog = (
        *core_modules["SOURCE_DATA_PRODUCT_CATALOG"],
        *core_modules["DPM_PLANNED_SOURCE_DATA_PRODUCT_CATALOG"],
    )
    security_profiles = {
        profile.product_name: profile
        for profile in (
            *core_modules["SOURCE_DATA_SECURITY_PROFILES"],
            *core_modules["DPM_PLANNED_SOURCE_DATA_SECURITY_PROFILES"],
        )
    }
    by_name = {product["product_name"]: product for product in declaration["products"]}

    assert declaration["producer_repository"] == "lotus-core"
    assert len(declaration["products"]) == len(catalog)

    for source_product in catalog:
        declared = by_name[source_product.product_name]
        profile = security_profiles[source_product.product_name]

        assert declared["product_version"] == source_product.product_version
        assert declared["owner_repository"] == source_product.owner
        expected_family = (
            "dpm_source_data"
            if source_product.product_name
            in {
                "DpmModelPortfolioTarget",
                "DiscretionaryMandateBinding",
                "InstrumentEligibilityProfile",
                "PortfolioTaxLotWindow",
                "TransactionCostCurve",
                "MarketDataCoverageWindow",
                "DpmSourceReadiness",
                "PortfolioManagerBookMembership",
                "CioModelChangeAffectedCohort",
                "DpmPortfolioUniverseCandidate",
                "ClientRestrictionProfile",
                "SustainabilityPreferenceProfile",
                "ClientTaxProfile",
                "ClientTaxRuleSet",
                "ClientIncomeNeedsSchedule",
                "LiquidityReserveRequirement",
                "PlannedWithdrawalSchedule",
                "ExternalCurrencyExposure",
                "ExternalHedgePolicy",
                "ExternalFXForwardCurve",
                "ExternalEligibleHedgeInstrument",
                "ExternalHedgeExecutionReadiness",
                "ExternalOrderExecutionAcknowledgement",
            }
            else family_map[source_product.route_family]
        )
        assert declared["product_family"] == expected_family
        assert declared["approved_consumers"] == list(source_product.consumers)
        assert declared["required_trust_metadata"] == list(
            source_product.required_metadata_fields
        )
        assert declared["serving_plane"] == source_product.serving_plane
        assert declared["current_routes"] == list(source_product.current_routes)
        assert declared["security_profile_ref"] == (
            f"{profile.access_classification}:{profile.sensitivity_classification}:"
            f"{profile.retention_requirement}:{profile.audit_requirement}"
        )


def test_rfc_0084_semantics_registry_rejects_malformed_registry_entries(
    tmp_path: Path,
) -> None:
    validator = _load_validator_module()
    path = tmp_path / "bad-semantics-registry.json"
    payload = {
        "contract_id": "domain-data-product-semantics",
        "contract_version": "1.0.0",
        "governed_by_rfc": "RFC-0084",
        "domain": "domain_data_product_semantics",
        "description": "Test semantics registry.",
        "identifiers": [
            {
                "key": "PortfolioId",
                "semantic_id": "lotus.portfolio_id",
                "stability": "stable",
                "lifecycle": "active",
                "description": "Portfolio identifier.",
            },
            {
                "key": "portfolio_id",
                "semantic_id": "lotus.portfolio_id",
                "stability": "stable",
                "lifecycle": "active",
                "description": "Portfolio identifier.",
            },
            {
                "key": "portfolio_id",
                "semantic_id": "",
                "stability": "stable",
                "lifecycle": "active",
                "description": "Duplicate portfolio identifier.",
            },
        ],
        "temporal_semantics": ["not-an-object"],
        "trust_vocabularies": {
            "freshness_classes": [{"key": "daily", "meaning": "Daily."}],
            "completeness_statuses": [{"key": "complete", "meaning": "Complete."}],
            "reconciliation_statuses": [{"key": "reconciled", "meaning": "Reconciled."}],
            "data_quality_statuses": [{"key": "quality_passed", "meaning": "Passed."}],
        },
    }

    issues = validator.validate_semantics_registry(path, payload)

    assert any("identifiers[0].key must be snake_case" in issue for issue in issues)
    assert any("identifiers contains duplicate key portfolio_id" in issue for issue in issues)
    assert any(
        "identifiers[2].semantic_id must be a non-empty string" in issue
        for issue in issues
    )
    assert any("temporal_semantics[0] must be an object" in issue for issue in issues)


def test_rfc_0084_slice_1_contract_family_is_present_and_governed() -> None:
    producer_schema = _load_json(PRODUCER_SCHEMA_PATH)
    consumer_schema = _load_json(CONSUMER_SCHEMA_PATH)
    readme = README_PATH.read_text(encoding="utf-8")
    evidence = EVIDENCE_PATH.read_text(encoding="utf-8")

    assert (
        producer_schema["properties"]["contract_id"]["const"] == "domain-data-products"
    )
    assert producer_schema["properties"]["governed_by_rfc"]["const"] == "RFC-0084"
    assert (
        producer_schema["$defs"]["productFamily"]["enum"][0]
        == "operational_source_data"
    )
    assert "domain-data-products.schema.json" in readme
    assert "domain-data-product-consumers.schema.json" in readme
    assert "validate_domain_data_product_contracts.py" in readme
    assert "lotus-performance-products.v1.json" in readme
    assert "lotus-risk-products.v1.json" in readme
    assert "domain-data-product-semantics.v1.json" in readme
    assert "domain-data-product-trust-metadata.v1.json" in readme

    assert (
        consumer_schema["properties"]["contract_id"]["const"]
        == "domain-data-product-consumers"
    )
    assert consumer_schema["properties"]["governed_by_rfc"]["const"] == "RFC-0084"
    assert "platform-contracts/domain-data-products/" in evidence
    assert "mandatory slice review" in evidence.lower()


def test_rfc_0084_validator_accepts_valid_producer_and_consumer_contracts(
    tmp_path: Path,
) -> None:
    validator = _load_validator_module()
    _write_semantics_registry(
        tmp_path.parent / "domain-vocabulary" / "domain-data-product-semantics.v1.json"
    )
    _write_trust_metadata_registry(
        tmp_path.parent
        / "domain-vocabulary"
        / "domain-data-product-trust-metadata.v1.json"
    )

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
                    "request_scope": {
                        "scope_level": "portfolio",
                        "supports_bulk": False,
                    },
                    "temporal_scope": {
                        "primary_time_field": "as_of_date",
                        "freshness_basis": "as_of_date",
                        "supports_restatement": True,
                    },
                    "temporal_semantics_ref": "as_of_date",
                    "identifier_refs": ["portfolio_id"],
                    "required_trust_metadata": [
                        "product_name",
                        "product_version",
                        "as_of_date",
                        "reconciliation_status",
                        "data_quality_status",
                        "lineage_bundle_id",
                    ],
                    "freshness_policy": {
                        "freshness_class": "daily",
                        "max_allowed_age_description": "Must be current for the governed as-of date.",
                    },
                    "completeness_policy": {
                        "default_status": "complete",
                        "partial_allowed": True,
                    },
                    "lineage_policy": {
                        "lineage_required": True,
                        "evidence_bundle_required": True,
                        "evidence_access_class_ref": "operator_only",
                        "lineage_bundle_class_ref": "operator_reconciliation_evidence",
                    },
                    "security_profile_ref": "source_data_read.standard",
                    "approved_consumers": ["lotus-performance", "lotus-risk"],
                    "deprecation_policy": {
                        "state": "not_deprecated",
                        "successor_product": None,
                    },
                }
            ],
        },
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
                    "required_trust_metadata": ["product_name"],
                    "migration_posture": {"status": "current"},
                    "consumption_mode": "api_read",
                    "business_purpose": "Seed governed portfolio state into analytics orchestration.",
                    "validation_lanes": ["feature", "pr-merge"],
                    "failure_posture": "fail_closed",
                }
            ],
        },
    )

    assert validator.validate_contract_directory(tmp_path) == []


def test_rfc_0084_validator_rejects_unknown_and_duplicate_dependencies(
    tmp_path: Path,
) -> None:
    validator = _load_validator_module()
    _write_semantics_registry(
        tmp_path.parent / "domain-vocabulary" / "domain-data-product-semantics.v1.json"
    )
    _write_trust_metadata_registry(
        tmp_path.parent
        / "domain-vocabulary"
        / "domain-data-product-trust-metadata.v1.json"
    )

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
                    "request_scope": {
                        "scope_level": "portfolio",
                        "supports_bulk": False,
                    },
                    "temporal_scope": {
                        "primary_time_field": "as_of_date",
                        "freshness_basis": "as_of_date",
                        "supports_restatement": True,
                    },
                    "temporal_semantics_ref": "as_of_date",
                    "identifier_refs": ["portfolio_id"],
                    "required_trust_metadata": ["product_name"],
                    "freshness_policy": {
                        "freshness_class": "daily",
                        "max_allowed_age_description": "Daily.",
                    },
                    "completeness_policy": {
                        "default_status": "complete",
                        "partial_allowed": False,
                    },
                    "lineage_policy": {
                        "lineage_required": True,
                        "evidence_bundle_required": True,
                        "evidence_access_class_ref": "operator_only",
                        "lineage_bundle_class_ref": "operator_reconciliation_evidence",
                    },
                    "security_profile_ref": "source_data_read.standard",
                    "approved_consumers": ["lotus-performance"],
                    "deprecation_policy": {
                        "state": "not_deprecated",
                        "successor_product": None,
                    },
                },
                {
                    "product_name": "PortfolioStateSnapshot",
                    "product_version": "1.0.0",
                    "owner_repository": "lotus-core",
                    "product_family": "operational_source_data",
                    "authoritative_domain": "portfolio_state",
                    "lifecycle_status": "active",
                    "request_scope": {
                        "scope_level": "portfolio",
                        "supports_bulk": False,
                    },
                    "temporal_scope": {
                        "primary_time_field": "as_of_date",
                        "freshness_basis": "as_of_date",
                        "supports_restatement": True,
                    },
                    "temporal_semantics_ref": "as_of_date",
                    "identifier_refs": ["portfolio_id"],
                    "required_trust_metadata": ["product_name"],
                    "freshness_policy": {
                        "freshness_class": "daily",
                        "max_allowed_age_description": "Daily.",
                    },
                    "completeness_policy": {
                        "default_status": "complete",
                        "partial_allowed": False,
                    },
                    "lineage_policy": {
                        "lineage_required": True,
                        "evidence_bundle_required": True,
                        "evidence_access_class_ref": "operator_only",
                        "lineage_bundle_class_ref": "operator_reconciliation_evidence",
                    },
                    "security_profile_ref": "source_data_read.standard",
                    "approved_consumers": ["lotus-performance"],
                    "deprecation_policy": {
                        "state": "not_deprecated",
                        "successor_product": None,
                    },
                },
            ],
        },
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
                    "required_trust_metadata": ["product_name"],
                    "migration_posture": {"status": "current"},
                    "consumption_mode": "api_read",
                    "business_purpose": "Use upstream state snapshot.",
                    "validation_lanes": ["feature"],
                    "failure_posture": "fail_closed",
                }
            ],
        },
    )

    issues = validator.validate_contract_directory(tmp_path)

    assert any("duplicate product declaration" in issue for issue in issues)
    assert any("references unknown product declaration" in issue for issue in issues)


def test_rfc_0084_validator_rejects_unapproved_consumer_dependency(
    tmp_path: Path,
) -> None:
    validator = _load_validator_module()
    _write_semantics_registry(
        tmp_path.parent / "domain-vocabulary" / "domain-data-product-semantics.v1.json"
    )
    _write_trust_metadata_registry(
        tmp_path.parent
        / "domain-vocabulary"
        / "domain-data-product-trust-metadata.v1.json"
    )

    _write_json(
        tmp_path / "lotus-performance-products.v1.json",
        {
            "contract_id": "domain-data-products",
            "contract_version": "1.0.0",
            "governed_by_rfc": "RFC-0084",
            "producer_repository": "lotus-performance",
            "authoritative_domain": "performance_analytics",
            "products": [
                {
                    "product_name": "ReturnsSeriesBundle",
                    "product_version": "v1",
                    "owner_repository": "lotus-performance",
                    "product_family": "analytics_output",
                    "authoritative_domain": "performance_analytics",
                    "lifecycle_status": "active",
                    "request_scope": {
                        "scope_level": "portfolio",
                        "supports_bulk": False,
                    },
                    "temporal_scope": {
                        "primary_time_field": "date",
                        "freshness_basis": "valuation_date",
                        "supports_restatement": True,
                    },
                    "temporal_semantics_ref": "valuation_date",
                    "identifier_refs": ["portfolio_id", "calculation_id"],
                    "required_trust_metadata": [
                        "product_name",
                        "product_version",
                        "as_of_date",
                    ],
                    "freshness_policy": {
                        "freshness_class": "daily",
                        "max_allowed_age_description": "Daily.",
                    },
                    "completeness_policy": {
                        "default_status": "complete",
                        "partial_allowed": True,
                    },
                    "lineage_policy": {
                        "lineage_required": True,
                        "evidence_bundle_required": False,
                        "evidence_access_class_ref": "customer_consumable",
                    },
                    "security_profile_ref": "system_access:client_confidential:retain_for_client_record:audit_system_access",
                    "approved_consumers": ["lotus-risk"],
                    "deprecation_policy": {
                        "state": "not_deprecated",
                        "successor_product": None,
                    },
                }
            ],
        },
    )

    _write_json(
        tmp_path / "lotus-gateway-consumers.v1.json",
        {
            "contract_id": "domain-data-product-consumers",
            "contract_version": "1.0.0",
            "governed_by_rfc": "RFC-0084",
            "consumer_repository": "lotus-gateway",
            "dependencies": [
                {
                    "product_name": "ReturnsSeriesBundle",
                    "producer_repository": "lotus-performance",
                    "required_product_version": "v1",
                    "required_trust_metadata": ["generated_at"],
                    "migration_posture": {"status": "current"},
                    "consumption_mode": "gateway_composition",
                    "business_purpose": "Use upstream performance return-series output directly.",
                    "validation_lanes": ["feature"],
                    "failure_posture": "fail_closed",
                }
            ],
        },
    )

    issues = validator.validate_contract_directory(tmp_path)

    assert any("consumer is not approved" in issue for issue in issues)


def test_rfc_0084_validator_rejects_version_drift_without_approved_transition(
    tmp_path: Path,
) -> None:
    validator = _load_validator_module()
    _write_semantics_registry(
        tmp_path.parent / "domain-vocabulary" / "domain-data-product-semantics.v1.json"
    )
    _write_trust_metadata_registry(
        tmp_path.parent
        / "domain-vocabulary"
        / "domain-data-product-trust-metadata.v1.json"
    )

    _write_json(
        tmp_path / "lotus-performance-products.v1.json",
        {
            "contract_id": "domain-data-products",
            "contract_version": "1.0.0",
            "governed_by_rfc": "RFC-0084",
            "producer_repository": "lotus-performance",
            "authoritative_domain": "performance_analytics",
            "products": [
                {
                    "product_name": "ReturnsSeriesBundle",
                    "product_version": "v1",
                    "owner_repository": "lotus-performance",
                    "product_family": "analytics_output",
                    "authoritative_domain": "performance_analytics",
                    "lifecycle_status": "active",
                    "request_scope": {
                        "scope_level": "portfolio",
                        "supports_bulk": False,
                    },
                    "temporal_scope": {
                        "primary_time_field": "date",
                        "freshness_basis": "valuation_date",
                        "supports_restatement": True,
                    },
                    "temporal_semantics_ref": "valuation_date",
                    "identifier_refs": ["portfolio_id", "calculation_id"],
                    "required_trust_metadata": ["generated_at", "correlation_id"],
                    "freshness_policy": {
                        "freshness_class": "daily",
                        "max_allowed_age_description": "Daily.",
                    },
                    "completeness_policy": {
                        "default_status": "complete",
                        "partial_allowed": True,
                    },
                    "lineage_policy": {
                        "lineage_required": True,
                        "evidence_bundle_required": False,
                        "evidence_access_class_ref": "customer_consumable",
                    },
                    "security_profile_ref": "system_access:client_confidential:retain_for_client_record:audit_system_access",
                    "approved_consumers": ["lotus-risk"],
                    "deprecation_policy": {
                        "state": "not_deprecated",
                        "successor_product": None,
                    },
                },
                {
                    "product_name": "ReturnsSeriesBundle",
                    "product_version": "v2",
                    "owner_repository": "lotus-performance",
                    "product_family": "analytics_output",
                    "authoritative_domain": "performance_analytics",
                    "lifecycle_status": "active",
                    "request_scope": {
                        "scope_level": "portfolio",
                        "supports_bulk": False,
                    },
                    "temporal_scope": {
                        "primary_time_field": "date",
                        "freshness_basis": "valuation_date",
                        "supports_restatement": True,
                    },
                    "temporal_semantics_ref": "valuation_date",
                    "identifier_refs": ["portfolio_id", "calculation_id"],
                    "required_trust_metadata": ["generated_at", "correlation_id"],
                    "freshness_policy": {
                        "freshness_class": "daily",
                        "max_allowed_age_description": "Daily.",
                    },
                    "completeness_policy": {
                        "default_status": "complete",
                        "partial_allowed": True,
                    },
                    "lineage_policy": {
                        "lineage_required": True,
                        "evidence_bundle_required": False,
                        "evidence_access_class_ref": "customer_consumable",
                    },
                    "security_profile_ref": "system_access:client_confidential:retain_for_client_record:audit_system_access",
                    "approved_consumers": ["lotus-risk"],
                    "deprecation_policy": {
                        "state": "not_deprecated",
                        "successor_product": None,
                    },
                },
            ],
        },
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
                    "product_name": "ReturnsSeriesBundle",
                    "producer_repository": "lotus-performance",
                    "required_product_version": "v1",
                    "required_trust_metadata": ["generated_at"],
                    "migration_posture": {"status": "current"},
                    "consumption_mode": "api_read",
                    "business_purpose": "Use upstream return series while drifting from the latest version.",
                    "validation_lanes": ["feature"],
                    "failure_posture": "fail_closed",
                }
            ],
        },
    )

    issues = validator.validate_contract_directory(tmp_path)

    assert any(
        "version drift requires approved_transition" in issue for issue in issues
    )


def test_rfc_0084_validator_rejects_current_dependency_with_target_version() -> None:
    validator = _load_validator_module()
    path = Path("lotus-risk-consumers.v1.json")

    issues = validator.validate_consumer_contract(
        path,
        _consumer_contract_with_migration_posture(
            {"status": "current", "target_product_version": "v2"}
        ),
    )

    assert (
        f"{path}: dependencies[0].migration_posture.target_product_version "
        "must be null or omitted when status is current"
    ) in issues


def test_rfc_0084_validator_rejects_incomplete_approved_transition() -> None:
    validator = _load_validator_module()
    path = Path("lotus-risk-consumers.v1.json")

    issues = validator.validate_consumer_contract(
        path,
        _consumer_contract_with_migration_posture(
            {
                "status": "approved_transition",
                "target_product_version": "latest",
                "justification": "",
            }
        ),
    )

    assert (
        f"{path}: dependencies[0].migration_posture.target_product_version "
        "must use vN or semantic versioning when status is approved_transition"
    ) in issues
    assert (
        f"{path}: dependencies[0].migration_posture.justification must be a non-empty "
        "string when status is approved_transition"
    ) in issues
    assert (
        f"{path}: dependencies[0].migration_posture.sunset_condition must be a non-empty "
        "string when status is approved_transition"
    ) in issues


def test_rfc_0084_validator_allows_approved_transition_for_version_drift(
    tmp_path: Path,
) -> None:
    validator = _load_validator_module()
    _write_semantics_registry(
        tmp_path.parent / "domain-vocabulary" / "domain-data-product-semantics.v1.json"
    )
    _write_trust_metadata_registry(
        tmp_path.parent
        / "domain-vocabulary"
        / "domain-data-product-trust-metadata.v1.json"
    )

    _write_json(
        tmp_path / "lotus-performance-products.v1.json",
        {
            "contract_id": "domain-data-products",
            "contract_version": "1.0.0",
            "governed_by_rfc": "RFC-0084",
            "producer_repository": "lotus-performance",
            "authoritative_domain": "performance_analytics",
            "products": [
                {
                    "product_name": "ReturnsSeriesBundle",
                    "product_version": "v1",
                    "owner_repository": "lotus-performance",
                    "product_family": "analytics_output",
                    "authoritative_domain": "performance_analytics",
                    "lifecycle_status": "active",
                    "request_scope": {
                        "scope_level": "portfolio",
                        "supports_bulk": False,
                    },
                    "temporal_scope": {
                        "primary_time_field": "date",
                        "freshness_basis": "valuation_date",
                        "supports_restatement": True,
                    },
                    "temporal_semantics_ref": "valuation_date",
                    "identifier_refs": ["portfolio_id", "calculation_id"],
                    "required_trust_metadata": ["generated_at", "correlation_id"],
                    "freshness_policy": {
                        "freshness_class": "daily",
                        "max_allowed_age_description": "Daily.",
                    },
                    "completeness_policy": {
                        "default_status": "complete",
                        "partial_allowed": True,
                    },
                    "lineage_policy": {
                        "lineage_required": True,
                        "evidence_bundle_required": False,
                        "evidence_access_class_ref": "customer_consumable",
                    },
                    "security_profile_ref": "system_access:client_confidential:retain_for_client_record:audit_system_access",
                    "approved_consumers": ["lotus-risk"],
                    "deprecation_policy": {
                        "state": "not_deprecated",
                        "successor_product": None,
                    },
                },
                {
                    "product_name": "ReturnsSeriesBundle",
                    "product_version": "v2",
                    "owner_repository": "lotus-performance",
                    "product_family": "analytics_output",
                    "authoritative_domain": "performance_analytics",
                    "lifecycle_status": "active",
                    "request_scope": {
                        "scope_level": "portfolio",
                        "supports_bulk": False,
                    },
                    "temporal_scope": {
                        "primary_time_field": "date",
                        "freshness_basis": "valuation_date",
                        "supports_restatement": True,
                    },
                    "temporal_semantics_ref": "valuation_date",
                    "identifier_refs": ["portfolio_id", "calculation_id"],
                    "required_trust_metadata": ["generated_at", "correlation_id"],
                    "freshness_policy": {
                        "freshness_class": "daily",
                        "max_allowed_age_description": "Daily.",
                    },
                    "completeness_policy": {
                        "default_status": "complete",
                        "partial_allowed": True,
                    },
                    "lineage_policy": {
                        "lineage_required": True,
                        "evidence_bundle_required": False,
                        "evidence_access_class_ref": "customer_consumable",
                    },
                    "security_profile_ref": "system_access:client_confidential:retain_for_client_record:audit_system_access",
                    "approved_consumers": ["lotus-risk"],
                    "deprecation_policy": {
                        "state": "not_deprecated",
                        "successor_product": None,
                    },
                },
            ],
        },
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
                    "product_name": "ReturnsSeriesBundle",
                    "producer_repository": "lotus-performance",
                    "required_product_version": "v1",
                    "required_trust_metadata": ["generated_at"],
                    "migration_posture": {
                        "status": "approved_transition",
                        "target_product_version": "v2",
                        "justification": "Risk is migrating to the latest producer contract incrementally.",
                        "sunset_condition": "Remove the old version after downstream characterization and rollout close.",
                    },
                    "consumption_mode": "api_read",
                    "business_purpose": "Use upstream return series during an approved migration window.",
                    "validation_lanes": ["feature"],
                    "failure_posture": "fail_closed",
                }
            ],
        },
    )

    assert validator.validate_contract_directory(tmp_path) == []


def test_rfc_0084_validator_rejects_missing_upstream_trust_metadata_for_consumer_dependency(
    tmp_path: Path,
) -> None:
    validator = _load_validator_module()
    _write_semantics_registry(
        tmp_path.parent / "domain-vocabulary" / "domain-data-product-semantics.v1.json"
    )
    _write_trust_metadata_registry(
        tmp_path.parent
        / "domain-vocabulary"
        / "domain-data-product-trust-metadata.v1.json"
    )

    _write_json(
        tmp_path / "lotus-performance-products.v1.json",
        {
            "contract_id": "domain-data-products",
            "contract_version": "1.0.0",
            "governed_by_rfc": "RFC-0084",
            "producer_repository": "lotus-performance",
            "authoritative_domain": "performance_analytics",
            "products": [
                {
                    "product_name": "ReturnsSeriesBundle",
                    "product_version": "v1",
                    "owner_repository": "lotus-performance",
                    "product_family": "analytics_output",
                    "authoritative_domain": "performance_analytics",
                    "lifecycle_status": "active",
                    "request_scope": {
                        "scope_level": "portfolio",
                        "supports_bulk": False,
                    },
                    "temporal_scope": {
                        "primary_time_field": "date",
                        "freshness_basis": "valuation_date",
                        "supports_restatement": True,
                    },
                    "temporal_semantics_ref": "valuation_date",
                    "identifier_refs": ["portfolio_id", "calculation_id"],
                    "required_trust_metadata": ["generated_at"],
                    "freshness_policy": {
                        "freshness_class": "daily",
                        "max_allowed_age_description": "Daily.",
                    },
                    "completeness_policy": {
                        "default_status": "complete",
                        "partial_allowed": True,
                    },
                    "lineage_policy": {
                        "lineage_required": True,
                        "evidence_bundle_required": False,
                        "evidence_access_class_ref": "customer_consumable",
                    },
                    "security_profile_ref": "system_access:client_confidential:retain_for_client_record:audit_system_access",
                    "approved_consumers": ["lotus-risk"],
                    "deprecation_policy": {
                        "state": "not_deprecated",
                        "successor_product": None,
                    },
                }
            ],
        },
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
                    "product_name": "ReturnsSeriesBundle",
                    "producer_repository": "lotus-performance",
                    "required_product_version": "v1",
                    "required_trust_metadata": ["generated_at", "correlation_id"],
                    "migration_posture": {"status": "current"},
                    "consumption_mode": "api_read",
                    "business_purpose": "Use upstream return series and require trace metadata.",
                    "validation_lanes": ["feature"],
                    "failure_posture": "fail_closed",
                }
            ],
        },
    )

    issues = validator.validate_contract_directory(tmp_path)

    assert any("missing required trust metadata" in issue for issue in issues)


def test_rfc_0084_validator_rejects_unknown_consumer_trust_metadata_reference(
    tmp_path: Path,
) -> None:
    validator = _load_validator_module()
    _write_semantics_registry(
        tmp_path.parent / "domain-vocabulary" / "domain-data-product-semantics.v1.json"
    )
    _write_trust_metadata_registry(
        tmp_path.parent
        / "domain-vocabulary"
        / "domain-data-product-trust-metadata.v1.json"
    )

    _write_json(
        tmp_path / "lotus-performance-products.v1.json",
        {
            "contract_id": "domain-data-products",
            "contract_version": "1.0.0",
            "governed_by_rfc": "RFC-0084",
            "producer_repository": "lotus-performance",
            "authoritative_domain": "performance_analytics",
            "products": [
                {
                    "product_name": "ReturnsSeriesBundle",
                    "product_version": "v1",
                    "owner_repository": "lotus-performance",
                    "product_family": "analytics_output",
                    "authoritative_domain": "performance_analytics",
                    "lifecycle_status": "active",
                    "request_scope": {
                        "scope_level": "portfolio",
                        "supports_bulk": False,
                    },
                    "temporal_scope": {
                        "primary_time_field": "date",
                        "freshness_basis": "valuation_date",
                        "supports_restatement": True,
                    },
                    "temporal_semantics_ref": "valuation_date",
                    "identifier_refs": ["portfolio_id", "calculation_id"],
                    "required_trust_metadata": ["generated_at", "correlation_id"],
                    "freshness_policy": {
                        "freshness_class": "daily",
                        "max_allowed_age_description": "Daily.",
                    },
                    "completeness_policy": {
                        "default_status": "complete",
                        "partial_allowed": True,
                    },
                    "lineage_policy": {
                        "lineage_required": True,
                        "evidence_bundle_required": False,
                        "evidence_access_class_ref": "customer_consumable",
                    },
                    "security_profile_ref": "system_access:client_confidential:retain_for_client_record:audit_system_access",
                    "approved_consumers": ["lotus-risk"],
                    "deprecation_policy": {
                        "state": "not_deprecated",
                        "successor_product": None,
                    },
                }
            ],
        },
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
                    "product_name": "ReturnsSeriesBundle",
                    "producer_repository": "lotus-performance",
                    "required_product_version": "v1",
                    "required_trust_metadata": ["generated_at", "unknown_trust_field"],
                    "migration_posture": {"status": "current"},
                    "consumption_mode": "api_read",
                    "business_purpose": "Use upstream return series and request an unknown trust field.",
                    "validation_lanes": ["feature"],
                    "failure_posture": "fail_closed",
                }
            ],
        },
    )

    issues = validator.validate_contract_directory(tmp_path)

    assert any(
        "required_trust_metadata contains unknown fields" in issue for issue in issues
    )


def test_rfc_0084_validator_ignores_retired_versions_when_evaluating_version_drift(
    tmp_path: Path,
) -> None:
    validator = _load_validator_module()
    _write_semantics_registry(
        tmp_path.parent / "domain-vocabulary" / "domain-data-product-semantics.v1.json"
    )
    _write_trust_metadata_registry(
        tmp_path.parent
        / "domain-vocabulary"
        / "domain-data-product-trust-metadata.v1.json"
    )

    _write_json(
        tmp_path / "lotus-performance-products.v1.json",
        {
            "contract_id": "domain-data-products",
            "contract_version": "1.0.0",
            "governed_by_rfc": "RFC-0084",
            "producer_repository": "lotus-performance",
            "authoritative_domain": "performance_analytics",
            "products": [
                {
                    "product_name": "ReturnsSeriesBundle",
                    "product_version": "v1",
                    "owner_repository": "lotus-performance",
                    "product_family": "analytics_output",
                    "authoritative_domain": "performance_analytics",
                    "lifecycle_status": "active",
                    "request_scope": {
                        "scope_level": "portfolio",
                        "supports_bulk": False,
                    },
                    "temporal_scope": {
                        "primary_time_field": "date",
                        "freshness_basis": "valuation_date",
                        "supports_restatement": True,
                    },
                    "temporal_semantics_ref": "valuation_date",
                    "identifier_refs": ["portfolio_id", "calculation_id"],
                    "required_trust_metadata": ["generated_at", "correlation_id"],
                    "freshness_policy": {
                        "freshness_class": "daily",
                        "max_allowed_age_description": "Daily.",
                    },
                    "completeness_policy": {
                        "default_status": "complete",
                        "partial_allowed": True,
                    },
                    "lineage_policy": {
                        "lineage_required": True,
                        "evidence_bundle_required": False,
                        "evidence_access_class_ref": "customer_consumable",
                    },
                    "security_profile_ref": "system_access:client_confidential:retain_for_client_record:audit_system_access",
                    "approved_consumers": ["lotus-risk"],
                    "deprecation_policy": {
                        "state": "not_deprecated",
                        "successor_product": None,
                    },
                },
                {
                    "product_name": "ReturnsSeriesBundle",
                    "product_version": "v2",
                    "owner_repository": "lotus-performance",
                    "product_family": "analytics_output",
                    "authoritative_domain": "performance_analytics",
                    "lifecycle_status": "retired",
                    "request_scope": {
                        "scope_level": "portfolio",
                        "supports_bulk": False,
                    },
                    "temporal_scope": {
                        "primary_time_field": "date",
                        "freshness_basis": "valuation_date",
                        "supports_restatement": True,
                    },
                    "temporal_semantics_ref": "valuation_date",
                    "identifier_refs": ["portfolio_id", "calculation_id"],
                    "required_trust_metadata": ["generated_at", "correlation_id"],
                    "freshness_policy": {
                        "freshness_class": "daily",
                        "max_allowed_age_description": "Daily.",
                    },
                    "completeness_policy": {
                        "default_status": "complete",
                        "partial_allowed": True,
                    },
                    "lineage_policy": {
                        "lineage_required": True,
                        "evidence_bundle_required": False,
                        "evidence_access_class_ref": "customer_consumable",
                    },
                    "security_profile_ref": "system_access:client_confidential:retain_for_client_record:audit_system_access",
                    "approved_consumers": ["lotus-risk"],
                    "deprecation_policy": {
                        "state": "retired",
                        "successor_product": "ReturnsSeriesBundle",
                    },
                },
            ],
        },
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
                    "product_name": "ReturnsSeriesBundle",
                    "producer_repository": "lotus-performance",
                    "required_product_version": "v1",
                    "required_trust_metadata": ["generated_at"],
                    "migration_posture": {"status": "current"},
                    "consumption_mode": "api_read",
                    "business_purpose": "Use the active upstream version while a retired declaration remains in history.",
                    "validation_lanes": ["feature"],
                    "failure_posture": "fail_closed",
                }
            ],
        },
    )

    assert validator.validate_contract_directory(tmp_path) == []


def test_rfc_0084_validator_rejects_unknown_identifier_reference(
    tmp_path: Path,
) -> None:
    validator = _load_validator_module()
    _write_semantics_registry(
        tmp_path.parent / "domain-vocabulary" / "domain-data-product-semantics.v1.json"
    )
    _write_trust_metadata_registry(
        tmp_path.parent
        / "domain-vocabulary"
        / "domain-data-product-trust-metadata.v1.json"
    )

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
                    "product_version": "v1",
                    "owner_repository": "lotus-core",
                    "product_family": "operational_source_data",
                    "authoritative_domain": "portfolio_state",
                    "lifecycle_status": "active",
                    "request_scope": {
                        "scope_level": "portfolio",
                        "supports_bulk": False,
                    },
                    "temporal_scope": {
                        "primary_time_field": "as_of_date",
                        "freshness_basis": "as_of_date",
                        "supports_restatement": True,
                    },
                    "temporal_semantics_ref": "as_of_date",
                    "identifier_refs": ["portfolio_id", "unknown_identifier"],
                    "required_trust_metadata": ["product_name"],
                    "freshness_policy": {
                        "freshness_class": "daily",
                        "max_allowed_age_description": "Daily.",
                    },
                    "completeness_policy": {
                        "default_status": "complete",
                        "partial_allowed": False,
                    },
                    "lineage_policy": {
                        "lineage_required": True,
                        "evidence_bundle_required": True,
                        "evidence_access_class_ref": "operator_only",
                        "lineage_bundle_class_ref": "operator_reconciliation_evidence",
                    },
                    "security_profile_ref": "source_data_read.standard",
                    "approved_consumers": ["lotus-performance"],
                    "deprecation_policy": {
                        "state": "not_deprecated",
                        "successor_product": None,
                    },
                }
            ],
        },
    )

    issues = validator.validate_contract_directory(tmp_path)

    assert any("unknown identifiers" in issue for issue in issues)


def test_rfc_0084_validator_rejects_unknown_trust_metadata_reference(
    tmp_path: Path,
) -> None:
    validator = _load_validator_module()
    _write_semantics_registry(
        tmp_path.parent / "domain-vocabulary" / "domain-data-product-semantics.v1.json"
    )
    _write_trust_metadata_registry(
        tmp_path.parent
        / "domain-vocabulary"
        / "domain-data-product-trust-metadata.v1.json"
    )

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
                    "product_version": "v1",
                    "owner_repository": "lotus-core",
                    "product_family": "operational_source_data",
                    "authoritative_domain": "portfolio_state",
                    "lifecycle_status": "active",
                    "request_scope": {
                        "scope_level": "portfolio",
                        "supports_bulk": False,
                    },
                    "temporal_scope": {
                        "primary_time_field": "as_of_date",
                        "freshness_basis": "as_of_date",
                        "supports_restatement": True,
                    },
                    "temporal_semantics_ref": "as_of_date",
                    "identifier_refs": ["portfolio_id"],
                    "required_trust_metadata": ["product_name", "unknown_trust_field"],
                    "freshness_policy": {
                        "freshness_class": "daily",
                        "max_allowed_age_description": "Daily.",
                    },
                    "completeness_policy": {
                        "default_status": "complete",
                        "partial_allowed": False,
                    },
                    "lineage_policy": {
                        "lineage_required": True,
                        "evidence_bundle_required": False,
                        "evidence_access_class_ref": "customer_consumable",
                    },
                    "security_profile_ref": "source_data_read.standard",
                    "approved_consumers": ["lotus-performance"],
                    "deprecation_policy": {
                        "state": "not_deprecated",
                        "successor_product": None,
                    },
                }
            ],
        },
    )

    issues = validator.validate_contract_directory(tmp_path)

    assert any("unknown fields" in issue for issue in issues)


def test_rfc_0084_validator_requires_semantics_registry_for_producer_validation(
    tmp_path: Path,
) -> None:
    validator = _load_validator_module()
    products_dir = tmp_path / "domain-data-products"
    products_dir.mkdir()

    _write_json(
        products_dir / "lotus-core-products.v1.json",
        {
            "contract_id": "domain-data-products",
            "contract_version": "1.0.0",
            "governed_by_rfc": "RFC-0084",
            "producer_repository": "lotus-core",
            "authoritative_domain": "portfolio_state",
            "products": [
                {
                    "product_name": "PortfolioStateSnapshot",
                    "product_version": "v1",
                    "owner_repository": "lotus-core",
                    "product_family": "operational_source_data",
                    "authoritative_domain": "portfolio_state",
                    "lifecycle_status": "active",
                    "request_scope": {
                        "scope_level": "portfolio",
                        "supports_bulk": False,
                    },
                    "temporal_scope": {
                        "primary_time_field": "as_of_date",
                        "freshness_basis": "as_of_date",
                        "supports_restatement": True,
                    },
                    "temporal_semantics_ref": "as_of_date",
                    "identifier_refs": ["portfolio_id"],
                    "required_trust_metadata": ["product_name"],
                    "freshness_policy": {
                        "freshness_class": "daily",
                        "max_allowed_age_description": "Daily.",
                    },
                    "completeness_policy": {
                        "default_status": "complete",
                        "partial_allowed": False,
                    },
                    "lineage_policy": {
                        "lineage_required": True,
                        "evidence_bundle_required": True,
                        "evidence_access_class_ref": "operator_only",
                        "lineage_bundle_class_ref": "operator_reconciliation_evidence",
                    },
                    "security_profile_ref": "source_data_read.standard",
                    "approved_consumers": ["lotus-performance"],
                    "deprecation_policy": {
                        "state": "not_deprecated",
                        "successor_product": None,
                    },
                }
            ],
        },
    )

    issues = validator.validate_contract_directory(products_dir)

    assert any("semantics registry is required" in issue for issue in issues)


def test_rfc_0084_lotus_core_declaration_aligns_to_checked_in_catalog() -> None:
    validator = _load_validator_module()
    declaration = _load_json(LOTUS_CORE_PRODUCTS_PATH)
    catalog = _load_json(DOMAIN_PRODUCT_CATALOG_PATH)

    assert (
        validator.validate_producer_contract(LOTUS_CORE_PRODUCTS_PATH, declaration)
        == []
    )

    generated_core_products = {
        product["product_name"]: product
        for product in catalog["products"]
        if product["producer_repository"] == "lotus-core"
    }
    assert declaration["producer_repository"] == "lotus-core"
    assert len(declaration["products"]) == len(generated_core_products)

    for declared in declaration["products"]:
        generated = generated_core_products[declared["product_name"]]
        assert generated["product_id"] == (
            f"lotus-core:{declared['product_name']}:{declared['product_version']}"
        )
        assert generated["producer_repository"] == "lotus-core"
        assert generated["product_name"] == declared["product_name"]
        assert generated["product_version"] == declared["product_version"]


def test_rfc_0084_lotus_core_live_source_preview_is_opt_in(monkeypatch) -> None:
    monkeypatch.delenv(LOTUS_CORE_PREVIEW_ENV, raising=False)
    assert not _live_lotus_core_preview_enabled()

    monkeypatch.setenv(LOTUS_CORE_PREVIEW_ENV, "1")
    assert _live_lotus_core_preview_enabled()


def test_rfc_0084_lotus_core_declaration_aligns_to_live_source_data_catalog_preview() -> None:
    _skip_unless_live_lotus_core_preview_enabled()
    validator = _load_validator_module()
    core_modules = _load_lotus_core_modules()
    declaration = _load_json(LOTUS_CORE_PRODUCTS_PATH)

    assert (
        validator.validate_producer_contract(LOTUS_CORE_PRODUCTS_PATH, declaration)
        == []
    )
    _assert_lotus_core_declaration_matches_source_catalog(declaration, core_modules)
    by_name = {product["product_name"]: product for product in declaration["products"]}

    assert (
        by_name["MarketDataWindow"]["temporal_scope"]["primary_time_field"]
        == "valuation_date"
    )
    assert by_name["PortfolioStateSnapshot"]["identifier_refs"] == [
        "portfolio_id",
        "snapshot_id",
        "tenant_id",
    ]
    assert by_name["RiskFreeSeriesWindow"]["identifier_refs"] == [
        "risk_free_curve_id",
        "tenant_id",
    ]
    assert by_name["MarketDataWindow"]["request_scope"]["scope_level"] == "benchmark"
    assert by_name["MarketDataWindow"]["temporal_semantics_ref"] == "valuation_date"
    assert by_name["RiskFreeSeriesWindow"]["request_scope"]["scope_level"] == "global"
    assert by_name["BenchmarkDefinition"]["identifier_refs"] == [
        "benchmark_id",
        "tenant_id",
    ]
    assert by_name["BenchmarkDefinition"]["temporal_semantics_ref"] == "as_of_date"
    assert by_name["IndexDefinition"]["identifier_refs"] == ["index_id", "tenant_id"]
    assert by_name["IndexDefinition"]["temporal_semantics_ref"] == "as_of_date"
    assert by_name["BenchmarkReturnSeriesWindow"]["identifier_refs"] == [
        "benchmark_id",
        "tenant_id",
    ]
    assert (
        by_name["BenchmarkReturnSeriesWindow"]["temporal_semantics_ref"]
        == "valuation_date"
    )
    assert (
        by_name["IngestionEvidenceBundle"]["temporal_scope"]["primary_time_field"]
        == "ingested_at"
    )
    assert by_name["IngestionEvidenceBundle"]["temporal_semantics_ref"] == "ingested_at"
    assert (
        by_name["ReconciliationEvidenceBundle"]["lineage_policy"][
            "evidence_bundle_required"
        ]
        is True
    )
    assert (
        by_name["ReconciliationEvidenceBundle"]["lineage_policy"][
            "evidence_access_class_ref"
        ]
        == "operator_only"
    )
    assert (
        by_name["ReconciliationEvidenceBundle"]["lineage_policy"][
            "lineage_bundle_class_ref"
        ]
        == "operator_reconciliation_evidence"
    )
    assert (
        by_name["DataQualityCoverageReport"]["lineage_policy"][
            "evidence_access_class_ref"
        ]
        == "operator_only"
    )
    assert (
        by_name["DataQualityCoverageReport"]["lineage_policy"][
            "lineage_bundle_class_ref"
        ]
        == "operator_quality_evidence"
    )
    assert (
        by_name["IngestionEvidenceBundle"]["lineage_policy"][
            "evidence_access_class_ref"
        ]
        == "operator_only"
    )
    assert (
        by_name["IngestionEvidenceBundle"]["lineage_policy"]["lineage_bundle_class_ref"]
        == "operator_ingestion_evidence"
    )


def test_rfc_0084_identifier_and_trust_semantics_registry_aligns_to_current_declarations() -> (
    None
):
    validator = _load_validator_module()
    semantics_registry = _load_json(SEMANTICS_REGISTRY_PATH)
    trust_metadata_registry = _load_json(TRUST_METADATA_REGISTRY_PATH)
    core_declaration = _load_json(LOTUS_CORE_PRODUCTS_PATH)
    performance_declaration = _load_json(LOTUS_PERFORMANCE_PRODUCTS_PATH)
    risk_declaration = _load_json(LOTUS_RISK_PRODUCTS_PATH)

    assert (
        validator.validate_semantics_registry(
            SEMANTICS_REGISTRY_PATH, semantics_registry
        )
        == []
    )
    assert (
        validator.validate_trust_metadata_registry(
            TRUST_METADATA_REGISTRY_PATH, trust_metadata_registry
        )
        == []
    )

    identifier_keys = {entry["key"] for entry in semantics_registry["identifiers"]}
    temporal_keys = {entry["key"] for entry in semantics_registry["temporal_semantics"]}
    freshness_classes = {
        entry["key"]
        for entry in semantics_registry["trust_vocabularies"]["freshness_classes"]
    }
    completeness_statuses = {
        entry["key"]
        for entry in semantics_registry["trust_vocabularies"]["completeness_statuses"]
    }
    trust_metadata_keys = {
        entry["key"] for entry in trust_metadata_registry["trust_metadata_fields"]
    }
    evidence_access_classes = {
        entry["key"] for entry in trust_metadata_registry["evidence_access_classes"]
    }
    lineage_bundle_class_keys = {
        entry["key"] for entry in trust_metadata_registry["lineage_bundle_classes"]
    }

    assert {
        "portfolio_id",
        "benchmark_id",
        "position_id",
        "instrument_id",
        "issuer_id",
        "index_id",
        "risk_free_curve_id",
        "calculation_id",
        "tenant_id",
        "correlation_id",
        "snapshot_id",
    }.issubset(identifier_keys)
    assert {
        "as_of_date",
        "valuation_date",
        "generated_at",
        "observed_at",
        "ingested_at",
    } <= temporal_keys
    assert {"daily", "batch", "event_driven"} <= freshness_classes
    assert {
        "complete",
        "partial",
        "stale",
        "unreconciled",
        "break_open",
        "blocked",
        "unknown",
    } <= completeness_statuses
    assert {"customer_consumable", "operator_only"} <= evidence_access_classes
    assert {
        "operator_reconciliation_evidence",
        "operator_quality_evidence",
        "operator_ingestion_evidence",
    } <= lineage_bundle_class_keys

    for declaration in (core_declaration, performance_declaration, risk_declaration):
        for product in declaration["products"]:
            assert set(product["identifier_refs"]) <= identifier_keys
            assert product["temporal_semantics_ref"] in temporal_keys
            assert product["freshness_policy"]["freshness_class"] in freshness_classes
            assert (
                product["completeness_policy"]["default_status"]
                in completeness_statuses
            )
            assert set(product["required_trust_metadata"]) <= trust_metadata_keys
            assert (
                product["lineage_policy"]["evidence_access_class_ref"]
                in evidence_access_classes
            )
            if product["lineage_policy"]["evidence_bundle_required"]:
                assert (
                    product["lineage_policy"]["lineage_bundle_class_ref"]
                    in lineage_bundle_class_keys
                )


def test_rfc_0084_first_analytics_wave_declarations_align_to_live_repo_truth() -> None:
    validator = _load_validator_module()
    declaration_directory = ROOT / "platform-contracts" / "domain-data-products"
    readme = README_PATH.read_text(encoding="utf-8")
    slice_3_evidence = SLICE_3_EVIDENCE_PATH.read_text(encoding="utf-8")

    performance_upstream_map = _load_repo_text(
        "lotus-performance", "docs/technical/RFC-0082-upstream-contract-family-map.md"
    )
    performance_capabilities = _load_repo_text(
        "lotus-performance", "app/api/endpoints/integration_capabilities.py"
    )
    returns_series_certification = _load_repo_text(
        "lotus-performance", "docs/technical/returns-series-endpoint-certification.md"
    )
    benchmark_exposure_certification = _load_repo_text(
        "lotus-performance",
        "docs/technical/benchmark-exposure-context-endpoint-certification.md",
    )
    risk_app_factory = _load_repo_text("lotus-risk", "src/app/app_factory.py")
    risk_router_modules = "\n".join(
        _load_repo_text("lotus-risk", relative_path)
        for relative_path in (
            "src/app/routers/concentration.py",
            "src/app/routers/drawdown.py",
            "src/app/routers/historical_attribution.py",
            "src/app/routers/risk_calculation.py",
            "src/app/routers/rolling.py",
            "src/app/routers/source_products.py",
        )
    )
    risk_endpoint_matrix = _load_repo_text(
        "lotus-risk", "docs/domain-apis/endpoint-matrix.md"
    )
    risk_upstream_map = _load_repo_text(
        "lotus-risk", "docs/domain-apis/RFC-0082-upstream-contract-family-map.md"
    )
    risk_repo_context = _load_repo_text(
        "lotus-risk", "REPOSITORY-ENGINEERING-CONTEXT.md"
    )

    performance_declaration = _load_json(LOTUS_PERFORMANCE_PRODUCTS_PATH)
    performance_consumers = _load_json(LOTUS_PERFORMANCE_CONSUMERS_PATH)
    risk_declaration = _load_json(LOTUS_RISK_PRODUCTS_PATH)
    risk_consumers = _load_json(LOTUS_RISK_CONSUMERS_PATH)

    assert validator.validate_contract_directory(declaration_directory) == []
    assert (
        validator.validate_producer_contract(
            LOTUS_PERFORMANCE_PRODUCTS_PATH, performance_declaration
        )
        == []
    )
    assert (
        validator.validate_consumer_contract(
            LOTUS_PERFORMANCE_CONSUMERS_PATH, performance_consumers
        )
        == []
    )
    assert (
        validator.validate_producer_contract(LOTUS_RISK_PRODUCTS_PATH, risk_declaration)
        == []
    )
    assert (
        validator.validate_consumer_contract(LOTUS_RISK_CONSUMERS_PATH, risk_consumers)
        == []
    )

    performance_products = {
        product["product_name"]: product
        for product in performance_declaration["products"]
    }
    risk_products = {
        product["product_name"]: product for product in risk_declaration["products"]
    }

    assert set(performance_products) == {
        "TimeWeightedReturnAnalytics",
        "MoneyWeightedReturnAnalytics",
        "ContributionAnalytics",
        "AttributionAnalytics",
        "MandatePerformanceHealthContext",
        "ReturnsSeriesBundle",
        "BenchmarkExposureContext",
        "CompositePerformanceAnalytics",
    }
    assert set(risk_products) == {
        "RiskMetricsReport",
        "DrawdownAnalyticsReport",
        "RollingRiskMetricsReport",
        "HistoricalRiskAttributionReport",
        "ConcentrationRiskReport",
        "MandateRiskHealthContext",
        "RegimeScenarioPackEvaluation",
        "RiskEventAffectedCohort",
    }

    assert performance_products["ReturnsSeriesBundle"]["approved_consumers"] == [
        "lotus-risk",
        "lotus-idea",
    ]
    assert performance_products["ReturnsSeriesBundle"]["current_routes"] == [
        "/integration/returns/series",
        "/integration/returns/series/results/{calculation_id}",
    ]
    assert "/integration/returns/series" in performance_capabilities
    assert (
        "/integration/returns/series/results/{calculation_id}"
        in performance_capabilities
    )
    assert (
        "strategic integration contract for downstream analytics"
        in returns_series_certification
    )
    assert "`lotus-risk`" in returns_series_certification

    assert performance_products["BenchmarkExposureContext"]["approved_consumers"] == [
        "lotus-risk",
        "lotus-idea",
    ]
    assert performance_products["BenchmarkExposureContext"]["current_routes"] == [
        "/integration/benchmarks/exposure-context"
    ]
    assert "/integration/benchmarks/exposure-context" in performance_capabilities
    assert "Current strategic downstream consumer" in benchmark_exposure_certification
    assert "`lotus-risk`" in benchmark_exposure_certification

    assert performance_products["MandatePerformanceHealthContext"][
        "approved_consumers"
    ] == [
        "lotus-gateway",
        "lotus-manage",
        "lotus-idea",
    ]
    assert performance_products["MandatePerformanceHealthContext"][
        "current_routes"
    ] == ["/performance/mandate-health-context"]
    assert "/performance/mandate-health-context" in performance_capabilities
    assert (
        "performance.integration.mandate_performance_health_context"
        in performance_capabilities
    )

    performance_dependency_names = {
        (dependency["product_name"], dependency["producer_repository"])
        for dependency in performance_consumers["dependencies"]
    }
    assert performance_dependency_names == {
        ("PortfolioTimeseriesInput", "lotus-core"),
        ("PortfolioAnalyticsReference", "lotus-core"),
        ("BenchmarkAssignment", "lotus-core"),
        ("MarketDataWindow", "lotus-core"),
        ("InstrumentReferenceBundle", "lotus-core"),
        ("RiskFreeSeriesWindow", "lotus-core"),
        ("PositionTimeseriesInput", "lotus-core"),
    }
    assert (
        "/integration/portfolios/{portfolio_id}/analytics/portfolio-timeseries"
        in performance_upstream_map
    )
    assert (
        "/integration/portfolios/{portfolio_id}/analytics/reference"
        in performance_upstream_map
    )
    assert (
        "/integration/portfolios/{portfolio_id}/benchmark-assignment"
        in performance_upstream_map
    )
    assert (
        "/integration/benchmarks/{benchmark_id}/market-series"
        in performance_upstream_map
    )
    assert "/integration/reference/risk-free-series" in performance_upstream_map
    assert all(
        dependency["migration_posture"]["status"] == "current"
        for dependency in performance_consumers["dependencies"]
    )
    assert all(
        dependency["required_trust_metadata"]
        for dependency in performance_consumers["dependencies"]
    )

    for product_name, route in {
        "RiskMetricsReport": "/analytics/risk/calculate",
        "DrawdownAnalyticsReport": "/analytics/risk/drawdown",
        "RollingRiskMetricsReport": "/analytics/risk/rolling-metrics",
        "HistoricalRiskAttributionReport": "/analytics/risk/historical-attribution",
        "ConcentrationRiskReport": "/analytics/risk/concentration",
    }.items():
        expected_consumers = (
            ["lotus-gateway", "lotus-idea"]
            if product_name in {"RiskMetricsReport", "ConcentrationRiskReport"}
            else ["lotus-gateway"]
        )
        assert risk_products[product_name]["approved_consumers"] == expected_consumers
        assert risk_products[product_name]["current_routes"] == [route]
        assert route in risk_router_modules
        assert route in risk_endpoint_matrix

    assert risk_products["MandateRiskHealthContext"]["approved_consumers"] == [
        "lotus-gateway",
        "lotus-manage",
        "lotus-idea",
    ]
    assert risk_products["MandateRiskHealthContext"]["current_routes"] == [
        "/analytics/risk/mandate-health-context"
    ]
    assert "risk_app.include_router(risk_calculation_router)" in risk_app_factory
    assert "risk_app.include_router(drawdown_router)" in risk_app_factory
    assert "risk_app.include_router(rolling_router)" in risk_app_factory
    assert "risk_app.include_router(concentration_router)" in risk_app_factory
    assert "risk_app.include_router(historical_attribution_router)" in risk_app_factory
    assert "risk_app.include_router(source_products_router)" in risk_app_factory
    assert "/analytics/risk/mandate-health-context" in risk_router_modules
    assert (
        "| `POST /analytics/risk/mandate-health-context` | Domain analytics |"
        in risk_endpoint_matrix
    )
    assert (
        "| `POST /analytics/risk/historical-attribution` | Domain analytics |"
        in risk_endpoint_matrix
    )
    assert (
        "| `POST /analytics/risk/concentration` | Domain analytics |"
        in risk_endpoint_matrix
    )
    assert "primarily consumed through `lotus-gateway`" in risk_repo_context

    risk_dependency_names = {
        (dependency["product_name"], dependency["producer_repository"])
        for dependency in risk_consumers["dependencies"]
    }
    assert risk_dependency_names == {
        ("ReturnsSeriesBundle", "lotus-performance"),
        ("BenchmarkExposureContext", "lotus-performance"),
        ("PortfolioStateSnapshot", "lotus-core"),
        ("PositionTimeseriesInput", "lotus-core"),
        ("InstrumentReferenceBundle", "lotus-core"),
        ("RiskFreeSeriesWindow", "lotus-core"),
    }
    assert "/integration/returns/series" in risk_upstream_map
    assert "/integration/benchmarks/exposure-context" in risk_upstream_map
    assert "/integration/portfolios/{portfolio_id}/core-snapshot" in risk_upstream_map
    assert (
        "/integration/portfolios/{portfolio_id}/analytics/position-timeseries"
        in risk_upstream_map
    )
    assert "/integration/reference/risk-free-series" in risk_upstream_map
    assert all(
        dependency["migration_posture"]["status"] == "current"
        for dependency in risk_consumers["dependencies"]
    )
    assert all(
        dependency["required_trust_metadata"]
        for dependency in risk_consumers["dependencies"]
    )
    returns_dependency = next(
        dependency
        for dependency in risk_consumers["dependencies"]
        if dependency["product_name"] == "ReturnsSeriesBundle"
    )
    assert {"generated_at", "as_of_date", "correlation_id"} <= set(
        returns_dependency["required_trust_metadata"]
    )

    assert "lotus-performance-products.v1.json" in readme
    assert "lotus-risk-products.v1.json" in readme
    assert "lotus-performance-consumers.v1.json" in readme
    assert "lotus-risk-consumers.v1.json" in readme
    assert "mandatory review" in slice_3_evidence.lower()


def test_rfc_0084_selected_producer_trust_metadata_aligns_to_live_repo_truth() -> None:
    semantics_registry = _load_json(SEMANTICS_REGISTRY_PATH)
    risk_declaration = _load_json(LOTUS_RISK_PRODUCTS_PATH)
    core_declaration = _load_json(LOTUS_CORE_PRODUCTS_PATH)

    reconciliation_target_model = _load_repo_text(
        "lotus-core",
        "docs/architecture/RFC-0083-reconciliation-data-quality-target-model.md",
    )
    risk_surface_alignment = _load_repo_text(
        "lotus-risk", "docs/domain-apis/risk-product-surface-alignment.md"
    )
    concentration_live_characterization = _load_repo_text(
        "lotus-risk", "tests/integration/test_concentration_live_characterization.py"
    )
    rolling_live_characterization = _load_repo_text(
        "lotus-risk", "tests/integration/test_rolling_live_characterization.py"
    )

    completeness_keys = {
        entry["key"]
        for entry in semantics_registry["trust_vocabularies"]["completeness_statuses"]
    }
    assert {
        "complete",
        "partial",
        "stale",
        "unreconciled",
        "break_open",
        "blocked",
        "unknown",
    } <= completeness_keys
    for status in (
        "`COMPLETE`",
        "`PARTIAL`",
        "`STALE`",
        "`UNRECONCILED`",
        "`BREAK_OPEN`",
        "`BLOCKED`",
        "`UNKNOWN`",
    ):
        assert status in reconciliation_target_model

    risk_products = {
        product["product_name"]: product for product in risk_declaration["products"]
    }
    core_products = {
        product["product_name"]: product for product in core_declaration["products"]
    }

    for field in (
        "lineage_version",
        "request_fingerprint",
        "source_services",
        "upstream_request_fingerprints",
        "coverage_status",
    ):
        assert field in risk_surface_alignment

    for field in (
        "lineage_version",
        "request_fingerprint",
        "source_services",
        "upstream_request_fingerprints",
    ):
        assert field in concentration_live_characterization
        assert (
            field in risk_products["ConcentrationRiskReport"]["required_trust_metadata"]
        )

    for field in ("coverage_ratio", "coverage_status"):
        assert field in concentration_live_characterization
        assert (
            field in risk_products["ConcentrationRiskReport"]["required_trust_metadata"]
        )

    for field in ("benchmark_context", "risk_free_context"):
        assert field in rolling_live_characterization
        assert (
            field
            in risk_products["RollingRiskMetricsReport"]["required_trust_metadata"]
        )
        assert field in risk_products["RiskMetricsReport"]["required_trust_metadata"]

    assert (
        core_products["ReconciliationEvidenceBundle"]["lineage_policy"][
            "evidence_access_class_ref"
        ]
        == "operator_only"
    )
    assert (
        core_products["DataQualityCoverageReport"]["lineage_policy"][
            "evidence_access_class_ref"
        ]
        == "operator_only"
    )
    assert (
        core_products["IngestionEvidenceBundle"]["lineage_policy"][
            "evidence_access_class_ref"
        ]
        == "operator_only"
    )
