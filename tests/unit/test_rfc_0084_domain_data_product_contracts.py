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
SLICE_3_EVIDENCE_PATH = ROOT / "rfcs" / "RFC-0084-slice-3-analytics-producer-onboarding-evidence.md"
LOTUS_CORE_PRODUCTS_PATH = (
    ROOT / "platform-contracts" / "domain-data-products" / "lotus-core-products.v1.json"
)
LOTUS_PERFORMANCE_PRODUCTS_PATH = (
    ROOT / "platform-contracts" / "domain-data-products" / "lotus-performance-products.v1.json"
)
LOTUS_PERFORMANCE_CONSUMERS_PATH = (
    ROOT / "platform-contracts" / "domain-data-products" / "lotus-performance-consumers.v1.json"
)
LOTUS_RISK_PRODUCTS_PATH = (
    ROOT / "platform-contracts" / "domain-data-products" / "lotus-risk-products.v1.json"
)
LOTUS_RISK_CONSUMERS_PATH = (
    ROOT / "platform-contracts" / "domain-data-products" / "lotus-risk-consumers.v1.json"
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


def _load_repo_text(repository: str, relative_path: str) -> str:
    return (ROOT.parent / repository / relative_path).read_text(encoding="utf-8")


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
    assert "lotus-performance-products.v1.json" in readme
    assert "lotus-risk-products.v1.json" in readme

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


def test_rfc_0084_validator_rejects_unapproved_consumer_dependency(tmp_path: Path) -> None:
    validator = _load_validator_module()

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
                    "request_scope": {"scope_level": "portfolio", "supports_bulk": False},
                    "temporal_scope": {
                        "primary_time_field": "date",
                        "freshness_basis": "valuation_date",
                        "supports_restatement": True,
                    },
                    "required_trust_metadata": ["product_name", "product_version", "as_of_date"],
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
        "lotus-performance", "docs/technical/benchmark-exposure-context-endpoint-certification.md"
    )
    risk_main = _load_repo_text("lotus-risk", "src/app/main.py")
    risk_endpoint_matrix = _load_repo_text("lotus-risk", "docs/domain-apis/endpoint-matrix.md")
    risk_upstream_map = _load_repo_text("lotus-risk", "docs/domain-apis/RFC-0082-upstream-contract-family-map.md")
    risk_repo_context = _load_repo_text("lotus-risk", "REPOSITORY-ENGINEERING-CONTEXT.md")

    performance_declaration = _load_json(LOTUS_PERFORMANCE_PRODUCTS_PATH)
    performance_consumers = _load_json(LOTUS_PERFORMANCE_CONSUMERS_PATH)
    risk_declaration = _load_json(LOTUS_RISK_PRODUCTS_PATH)
    risk_consumers = _load_json(LOTUS_RISK_CONSUMERS_PATH)

    assert validator.validate_contract_directory(declaration_directory) == []
    assert validator.validate_producer_contract(LOTUS_PERFORMANCE_PRODUCTS_PATH, performance_declaration) == []
    assert validator.validate_consumer_contract(LOTUS_PERFORMANCE_CONSUMERS_PATH, performance_consumers) == []
    assert validator.validate_producer_contract(LOTUS_RISK_PRODUCTS_PATH, risk_declaration) == []
    assert validator.validate_consumer_contract(LOTUS_RISK_CONSUMERS_PATH, risk_consumers) == []

    performance_products = {
        product["product_name"]: product for product in performance_declaration["products"]
    }
    risk_products = {product["product_name"]: product for product in risk_declaration["products"]}

    assert set(performance_products) == {"ReturnsSeriesBundle", "BenchmarkExposureContext"}
    assert set(risk_products) == {
        "RiskMetricsReport",
        "DrawdownAnalyticsReport",
        "RollingRiskMetricsReport",
        "HistoricalRiskAttributionReport",
        "ConcentrationRiskReport",
    }

    assert performance_products["ReturnsSeriesBundle"]["approved_consumers"] == ["lotus-risk"]
    assert performance_products["ReturnsSeriesBundle"]["current_routes"] == [
        "/integration/returns/series",
        "/integration/returns/series/results/{calculation_id}",
    ]
    assert "/integration/returns/series" in performance_capabilities
    assert "/integration/returns/series/results/{calculation_id}" in performance_capabilities
    assert "strategic integration contract for downstream analytics" in returns_series_certification
    assert "`lotus-risk`" in returns_series_certification

    assert performance_products["BenchmarkExposureContext"]["approved_consumers"] == ["lotus-risk"]
    assert performance_products["BenchmarkExposureContext"]["current_routes"] == [
        "/integration/benchmarks/exposure-context"
    ]
    assert "/integration/benchmarks/exposure-context" in performance_capabilities
    assert "Current strategic downstream consumer" in benchmark_exposure_certification
    assert "`lotus-risk`" in benchmark_exposure_certification

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
    }
    assert "/integration/portfolios/{portfolio_id}/analytics/portfolio-timeseries" in performance_upstream_map
    assert "/integration/portfolios/{portfolio_id}/analytics/reference" in performance_upstream_map
    assert "/integration/portfolios/{portfolio_id}/benchmark-assignment" in performance_upstream_map
    assert "/integration/benchmarks/{benchmark_id}/market-series" in performance_upstream_map
    assert "/integration/reference/risk-free-series" in performance_upstream_map

    for product_name, route in {
        "RiskMetricsReport": "/analytics/risk/calculate",
        "DrawdownAnalyticsReport": "/analytics/risk/drawdown",
        "RollingRiskMetricsReport": "/analytics/risk/rolling-metrics",
        "HistoricalRiskAttributionReport": "/analytics/risk/historical-attribution",
        "ConcentrationRiskReport": "/analytics/risk/concentration",
    }.items():
        assert risk_products[product_name]["approved_consumers"] == ["lotus-gateway"]
        assert risk_products[product_name]["current_routes"] == [route]
        assert route in risk_main
        assert route in risk_endpoint_matrix

    assert "| `POST /analytics/risk/historical-attribution` | Domain analytics |" in risk_endpoint_matrix
    assert "| `POST /analytics/risk/concentration` | Domain analytics |" in risk_endpoint_matrix
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
    assert "/integration/portfolios/{portfolio_id}/analytics/position-timeseries" in risk_upstream_map
    assert "/integration/reference/risk-free-series" in risk_upstream_map

    assert "lotus-performance-products.v1.json" in readme
    assert "lotus-risk-products.v1.json" in readme
    assert "lotus-performance-consumers.v1.json" in readme
    assert "lotus-risk-consumers.v1.json" in readme
    assert "mandatory review" in slice_3_evidence.lower()
