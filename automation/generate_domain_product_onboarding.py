from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = ROOT / "output" / "domain-product-onboarding"
PRODUCT_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9]+$")
REPOSITORY_PATTERN = re.compile(r"^lotus-[a-z0-9-]+$")
PRODUCT_VERSION_PATTERN = re.compile(r"^(v[0-9]+|[0-9]+\.[0-9]+\.[0-9]+)$")


def _product_id(repository: str, product_name: str, product_version: str) -> str:
    return f"{repository}:{product_name}:{product_version}"


def _kebab(value: str) -> str:
    tokens = re.findall(r"[A-Z]?[a-z0-9]+|[A-Z]+(?=[A-Z]|$)", value)
    return "-".join(token.lower() for token in tokens if token)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _product_payload(
    *,
    repository: str,
    product_name: str,
    product_version: str,
    authoritative_domain: str,
    product_family: str,
) -> dict[str, Any]:
    return {
        "contract_id": "domain-data-products",
        "contract_version": "1.0.0",
        "governed_by_rfc": "RFC-0084",
        "producer_repository": repository,
        "authoritative_domain": authoritative_domain,
        "products": [
            {
                "product_name": product_name,
                "product_version": product_version,
                "owner_repository": repository,
                "product_family": product_family,
                "authoritative_domain": authoritative_domain,
                "lifecycle_status": "preview",
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
                "identifier_refs": ["portfolio_id", "tenant_id", "correlation_id"],
                "required_trust_metadata": [
                    "product_name",
                    "product_version",
                    "tenant_id",
                    "generated_at",
                    "as_of_date",
                    "reconciliation_status",
                    "data_quality_status",
                    "correlation_id",
                ],
                "serving_plane": "replace_with_service_or_query_plane",
                "current_routes": ["replace_with_gateway_or_domain_route"],
                "freshness_policy": {
                    "freshness_class": "daily",
                    "max_allowed_age_description": "Replace with product-specific freshness policy.",
                },
                "completeness_policy": {
                    "default_status": "complete",
                    "partial_allowed": False,
                },
                "lineage_policy": {
                    "lineage_required": True,
                    "evidence_bundle_required": True,
                    "evidence_access_class_ref": "customer_consumable",
                },
                "security_profile_ref": "business_consumer_access:client_confidential:retain_for_client_record:audit_read_and_export",
                "approved_consumers": ["lotus-gateway"],
                "deprecation_policy": {
                    "state": "not_deprecated",
                    "successor_product": None,
                },
            }
        ],
    }


def _telemetry_payload(
    *,
    repository: str,
    product_name: str,
    product_version: str,
) -> dict[str, Any]:
    product_id = _product_id(repository, product_name, product_version)
    return {
        "contract_id": "lotus-domain-product-trust-telemetry-snapshot",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0087", "RFC-0091"],
        "emitted_at_utc": "replace_with_runtime_utc_timestamp",
        "product_id": product_id,
        "producer_repository": repository,
        "product_name": product_name,
        "product_version": product_version,
        "source_repository": repository,
        "runtime_source": {
            "emission_mode": "deterministic_local_or_service_runtime",
            "service_version": "replace_with_service_version",
            "environment": "local",
        },
        "freshness": {
            "freshness_class": "daily",
            "freshness_state": "current",
            "evaluated_at_utc": "replace_with_runtime_utc_timestamp",
            "observed_at_utc": "replace_with_runtime_utc_timestamp",
            "age_seconds": 0,
            "max_allowed_age_seconds": 86400,
        },
        "completeness_status": "complete",
        "reconciliation_status": "reconciled",
        "data_quality_status": "quality_passed",
        "lineage": {
            "lineage_materialized": True,
            "lineage_bundle_id": f"lineage:{repository}:{_kebab(product_name)}:replace",
            "evidence_access_class": "customer_consumable",
            "evidence_uris": [
                f"{repository}://evidence/{_kebab(product_name)}/replace"
            ],
        },
        "blocking": {"blocked": False},
        "observed_trust_metadata": {
            "product_name": product_name,
            "product_version": product_version,
            "tenant_id": "replace_with_tenant_id",
            "generated_at": "replace_with_runtime_utc_timestamp",
            "as_of_date": "replace_with_as_of_date",
            "reconciliation_status": "reconciled",
            "data_quality_status": "quality_passed",
            "correlation_id": f"replace_with_correlation_id:{product_id}",
        },
        "evidence": {
            "correlation_id": f"replace_with_correlation_id:{product_id}",
            "validation_lanes": ["feature", "pr-merge"],
            "source_event_id": f"source-event:{repository}:{_kebab(product_name)}:replace",
            "source_artifact_uri": f"{repository}://contracts/trust-telemetry/{_kebab(product_name)}.telemetry.v1.json",
        },
    }


def _slo_payload(
    *,
    repository: str,
    product_name: str,
    product_version: str,
) -> dict[str, Any]:
    return {
        "contract_id": "lotus-mesh-slo-policy",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0091"],
        "product_id": _product_id(repository, product_name, product_version),
        "producer_repository": repository,
        "freshness": {
            "max_allowed_age_seconds": 86400,
            "violation_severity": "blocking",
        },
        "completeness": {
            "required_status": "complete",
            "violation_severity": "blocking",
        },
        "reconciliation": {
            "required_status": "reconciled",
            "violation_severity": "blocking",
        },
        "data_quality": {
            "required_status": "quality_passed",
            "violation_severity": "blocking",
        },
        "lineage": {
            "lineage_materialized_required": True,
            "violation_severity": "blocking",
        },
        "certification": {
            "max_certification_age_seconds": 86400,
            "violation_severity": "blocking",
        },
        "escalation": {
            "owner_repository": repository,
            "owner_role": "replace_with_domain_owner",
            "remediation": "Refresh runtime evidence or block publication until trust posture is restored.",
        },
    }


def _access_payload(
    *,
    repository: str,
    product_name: str,
    product_version: str,
) -> dict[str, Any]:
    return {
        "contract_id": "lotus-mesh-access-policy",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0091"],
        "product_id": _product_id(repository, product_name, product_version),
        "producer_repository": repository,
        "default_posture": "restricted",
        "allowed_consumers": [
            {
                "consumer_repository": "lotus-gateway",
                "tenant_scope": ["replace_with_tenant_or_all"],
                "roles": ["operator", "advisor"],
                "use_cases": ["discovery", "evidence_review"],
            }
        ],
        "denial_posture": {
            "customer_visible_state": "requestable",
            "operator_visible_state": "restricted_with_reason",
            "reason": "Access policy requires explicit tenant, role, consumer, and use-case approval.",
        },
    }


def _evidence_payload(
    *,
    repository: str,
    product_name: str,
    product_version: str,
) -> dict[str, Any]:
    return {
        "contract_id": "lotus-mesh-evidence-pack-policy",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0091"],
        "product_id": _product_id(repository, product_name, product_version),
        "producer_repository": repository,
        "field_access_classes": {
            "product_identity": "public_customer",
            "runtime_telemetry": "restricted_customer",
            "lineage_evidence": "restricted_customer",
            "operator_remediation": "operator_only",
            "internal_debug": "internal_only",
        },
        "required_manifest_sections": [
            "product_identity",
            "source_declaration",
            "runtime_telemetry",
            "slo_posture",
            "access_posture",
            "dependency_graph",
            "certification_state",
            "validation_lanes",
        ],
    }


def _source_api_profile_payload(
    *,
    repository: str,
    product_name: str,
    product_version: str,
    authoritative_domain: str,
    product_family: str,
) -> dict[str, Any]:
    product_id = _product_id(repository, product_name, product_version)
    return {
        "contract_id": "lotus-source-data-product-api-profile",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0084", "RFC-0087", "RFC-0091"],
        "product_id": product_id,
        "producer_repository": repository,
        "authoritative_domain": authoritative_domain,
        "product_family": product_family,
        "source_ingestion": {
            "required": True,
            "mode": "replace_with_batch_stream_or_hybrid",
            "source_systems": ["replace_with_authoritative_upstream_system"],
            "idempotency_key_fields": [
                "tenant_id",
                "portfolio_id",
                "as_of_date",
                "source_batch_id",
            ],
            "lineage_fields": [
                "source_system",
                "source_record_id",
                "source_batch_id",
                "ingested_at",
                "correlation_id",
            ],
            "reconciliation_required": True,
            "backfill_required": True,
        },
        "serving_api": {
            "required": True,
            "route_family": "replace_with_rfc_0082_route_family",
            "routes": [
                {
                    "method": "GET",
                    "path": "replace_with_product_route",
                    "purpose": "Read the governed source-data product from the authoritative producer.",
                    "request_examples_required": True,
                    "response_examples_required": True,
                    "every_attribute_documented": True,
                    "error_examples_required": True,
                }
            ],
        },
        "certification": {
            "api_certification_required": True,
            "openapi_quality_required": True,
            "source_data_product_contract_guard_required": True,
            "domain_product_validation_required": True,
            "trust_telemetry_required": True,
            "mesh_certification_required": True,
            "live_canonical_evidence_required": True,
        },
        "downstream_consumption": {
            "approved_consumers": ["lotus-gateway"],
            "direct_service_consumers": [],
            "consumer_contract_required": True,
            "duplicate_endpoint_review_required": True,
        },
    }


def _analytics_product_profile_payload(
    *,
    repository: str,
    product_name: str,
    product_version: str,
    authoritative_domain: str,
    product_family: str,
) -> dict[str, Any]:
    product_id = _product_id(repository, product_name, product_version)
    return {
        "contract_id": "lotus-analytics-data-product-profile",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0084", "RFC-0087", "RFC-0091"],
        "product_id": product_id,
        "producer_repository": repository,
        "authoritative_domain": authoritative_domain,
        "product_family": product_family,
        "analytics_methodology": {
            "methodology_document_required": True,
            "formula_dictionary_required": True,
            "deterministic_worked_examples_required": True,
            "edge_case_and_failure_behavior_required": True,
            "unsupported_state_catalog_required": True,
        },
        "computation_contract": {
            "source_authority_map_required": True,
            "raw_vs_final_result_evidence_required": True,
            "reconciliation_evidence_required": True,
            "materiality_threshold_policy_required": True,
            "status_contract_required": True,
            "reason_codes_required": True,
            "source_alignment_controls_required": True,
            "support_safe_daily_evidence_required": True,
            "lineage_required": True,
            "restatement_policy_required": True,
        },
        "serving_api": {
            "required": True,
            "routes": [
                {
                    "method": "POST",
                    "path": "replace_with_analytics_route",
                    "purpose": "Calculate or retrieve the governed analytics product from the authoritative producer.",
                    "what_when_how_guidance_required": True,
                    "request_examples_required": True,
                    "response_examples_required": True,
                    "every_attribute_documented": True,
                    "error_examples_required": True,
                }
            ],
        },
        "downstream_realization": {
            "gateway_contract_required": True,
            "workbench_product_surface_required": True,
            "consumer_search_required_before_api_change": True,
            "same_rfc_consumer_updates_required": True,
        },
        "proof_requirements": {
            "unit_tests_required": True,
            "integration_tests_required": True,
            "contract_openapi_tests_required": True,
            "e2e_or_live_canonical_proof_required": True,
            "observability_and_safe_diagnostics_required": True,
            "data_mesh_certification_required": True,
        },
    }


def _readme(
    *,
    repository: str,
    product_name: str,
    product_version: str,
    authoritative_domain: str,
    product_family: str,
) -> str:
    product_id = _product_id(repository, product_name, product_version)
    return "\n".join(
        [
            f"# Domain Product Onboarding Bundle - {product_id}",
            "",
            "This bundle is a scaffold for repo-native Lotus data-product onboarding.",
            "It is not product authority until the owning repository replaces placeholders,",
            "adds repo-native tests, emits runtime telemetry, and passes platform certification.",
            "",
            "## Product Identity",
            "",
            f"- Repository: `{repository}`",
            f"- Product: `{product_name}`",
            f"- Version: `{product_version}`",
            f"- Product ID: `{product_id}`",
            f"- Authoritative domain: `{authoritative_domain}`",
            f"- Product family: `{product_family}`",
            "",
            "## Ownership Rules",
            "",
            "- Keep source truth in the producer repository.",
            "- Keep generated catalog, graph, trust, and evidence artifacts derived.",
            "- Publish through `lotus-gateway`; do not make gateway the product registry.",
            "- Expose customer/operator discovery through Workbench only after gateway support exists.",
            "- Treat placeholders as blockers before production certification.",
            "",
        ]
    )


def _checklist(
    *,
    repository: str,
    product_name: str,
    product_version: str,
    written_paths: list[Path],
    output_directory: Path,
) -> str:
    product_id = _product_id(repository, product_name, product_version)
    lines = [
        f"# Domain Product Onboarding Checklist - {product_id}",
        "",
        "This checklist is generated by `automation/generate_domain_product_onboarding.py`.",
        "",
        "## Generated Files",
        "",
    ]
    for path in written_paths:
        lines.append(f"- `{_relative(path, output_directory)}`")

    lines.extend(
        [
            "",
            "## Required Implementation Slices",
            "",
            "- Producer declaration: replace scaffold placeholders and validate domain-product contracts.",
            "- Runtime telemetry: emit or generate deterministic local telemetry from repo-native commands.",
            "- SLO policy: tune blocking and advisory thresholds with owner escalation.",
            "- Access policy: define tenant, role, consumer, and use-case entitlement.",
            "- Evidence policy: classify public, restricted, operator-only, and internal-only fields.",
            "- Lifecycle policy: define active, preview, deprecated, replaced, blocked, or retired posture.",
            "- Gateway publication: expose the product only through governed gateway APIs.",
            "- Workbench discovery: consume gateway/BFF only and render degraded states truthfully.",
            "- Tests: add repo-native unit/contract tests and platform cross-repo certification proof.",
            "- Documentation: update repo context, operator docs, and customer/operator evidence notes.",
            "- Source API profile: define ingestion, serving API, certification, and downstream consumption before implementation.",
            "- Analytics product profile: define methodology, raw/final evidence, status, materiality thresholds, reason codes, source alignment, downstream realization, and live proof before promoting analytics outputs.",
            "",
            "## Validation Commands",
            "",
            "```powershell",
            (
                "python automation/generate_domain_product_onboarding.py "
                f"--repository {repository} --product-name {product_name} "
                f"--product-version {product_version} --output-directory <bundle> --check"
            ),
            "python automation/generate_enterprise_mesh_maturity_matrix.py --check --generated-at-utc 2026-04-20T00:00:00Z",
            "python automation/mesh_certification_gate.py --mode blocking --generated-at-utc 2026-04-20T00:00:00Z --require-sibling-repos",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def _api_certification_checklist(
    *,
    repository: str,
    product_name: str,
    product_version: str,
) -> str:
    product_id = _product_id(repository, product_name, product_version)
    return "\n".join(
        [
            f"# API Certification Checklist - {product_id}",
            "",
            "Use this checklist before promoting a source-data product API.",
            "",
            "## Contract Quality",
            "",
            "- Endpoint purpose, when-to-use, and when-not-to-use guidance is explicit.",
            "- OpenAPI documentation is complete, grouped correctly, and implementation-backed.",
            "- Every request and response attribute has a description, type, and example.",
            "- Success, validation-error, authorization-error, stale-data, and upstream-unavailable examples exist.",
            "- Route family and product identity match the platform source-data product catalog.",
            "",
            "## Functional Proof",
            "",
            "- Tests cover every request option, default, filter, and pagination/export decision.",
            "- Tests assert every output family, not only headline totals.",
            "- Reconciliation, freshness, completeness, lineage, and data-quality fields are tested.",
            "- Duplicate or deprecated endpoints are recorded with downstream migration issues.",
            "",
            "## Non-Functional Proof",
            "",
            "- Latency, timeout, retry, paging, and bulk-read behavior are bounded.",
            "- Structured logs, metrics, and traces use safe bounded labels only.",
            "- Authorization, entitlement, retention, audit, and evidence-access posture are tested.",
            "- Live canonical validation captures evidence from the authoritative runtime.",
            "",
        ]
    )


def _ingestion_pipeline_checklist(
    *,
    repository: str,
    product_name: str,
    product_version: str,
) -> str:
    product_id = _product_id(repository, product_name, product_version)
    return "\n".join(
        [
            f"# Ingestion Pipeline Checklist - {product_id}",
            "",
            "Use this checklist before claiming source-data product readiness.",
            "",
            "## Source Acquisition",
            "",
            "- Authoritative source systems, files, topics, or APIs are named.",
            "- Tenant, portfolio, account, instrument, and as-of identifiers are mapped.",
            "- Idempotency keys prevent duplicate loads across replay and backfill.",
            "- Source batch, record, correction, and restatement lineage are persisted.",
            "",
            "## Validation And Reconciliation",
            "",
            "- Schema validation rejects malformed records with governed problem details.",
            "- Business validation covers missing identifiers, stale dates, invalid weights, and unsupported instruments.",
            "- Reconciliation compares source counts, accepted counts, rejected counts, and materialized counts.",
            "- Data-quality status and completeness status are derived from persisted facts.",
            "",
            "## Operations",
            "",
            "- Backfill, replay, partial reload, and operator diagnosis flows are documented.",
            "- Runtime telemetry feeds trust certification without hand-edited artifacts.",
            "- Failure modes are observable with safe labels and actionable remediation.",
            "- Canonical demo seed data includes enough realistic rows for live validation.",
            "",
        ]
    )


def _analytics_product_certification_checklist(
    *,
    repository: str,
    product_name: str,
    product_version: str,
) -> str:
    product_id = _product_id(repository, product_name, product_version)
    return "\n".join(
        [
            f"# Analytics Data Product Certification Checklist - {product_id}",
            "",
            "Use this checklist before promoting an analytics output as a governed Lotus data product.",
            "",
            "## Methodology Proof",
            "",
            "- Methodology documentation states variables, formulas, units, deterministic steps, validation behavior, and failure behavior.",
            "- Worked examples reconcile from source inputs through raw results, final results, residuals, materiality thresholds, statuses, and reason codes.",
            "- Unsupported, degraded, partial, stale, and invalid-domain states are explicit.",
            "",
            "## Computation Evidence",
            "",
            "- Source authority and upstream snapshot references are named.",
            "- Raw result, final result, reconciliation residual, materiality classification, and status evidence are available without recomputing internals.",
            "- Benchmark-relative, model-relative, or source-comparative analytics define source-alignment controls before promotion.",
            "- Support-safe daily or observation-level evidence is available when operations need to explain period-level output.",
            "- Restatement and lineage behavior are documented and tested.",
            "",
            "## API And Product Realization",
            "",
            "- OpenAPI explains what the endpoint does, when to use it, and how to interpret the response.",
            "- Gateway preserves source-owned totals, evidence, status, and degraded states.",
            "- Workbench renders source-owned status and does not invent analytics quality locally.",
            "- All downstream consumers are searched and updated in the same RFC when contracts change.",
            "",
            "## Enterprise Readiness",
            "",
            "- Unit, integration, contract/OpenAPI, e2e or live canonical proof, docs, and mesh certification pass.",
            "- Logs, metrics, traces, and support artifacts use bounded safe labels and do not expose sensitive payloads.",
            "- Supported-feature and wiki claims are promoted only after implementation proof exists.",
            "",
        ]
    )


def scaffold_domain_product_onboarding(
    *,
    repository: str,
    product_name: str,
    product_version: str,
    authoritative_domain: str,
    product_family: str,
    output_directory: Path,
) -> list[Path]:
    _validate_identity_inputs(
        repository=repository,
        product_name=product_name,
        product_version=product_version,
    )
    product_slug = _kebab(product_name)
    written_paths = [
        output_directory
        / "contracts"
        / "domain-data-products"
        / f"{repository}-products.v1.json",
        output_directory
        / "contracts"
        / "trust-telemetry"
        / f"{product_slug}.telemetry.v1.json",
        output_directory
        / "platform-contracts"
        / "mesh-slo"
        / f"{repository}-{product_slug}.slo.v1.json",
        output_directory
        / "platform-contracts"
        / "mesh-access"
        / f"{repository}-{product_slug}.access.v1.json",
        output_directory
        / "platform-contracts"
        / "mesh-evidence"
        / f"{repository}-{product_slug}.evidence-pack-policy.v1.json",
        output_directory
        / "contracts"
        / "source-data-products"
        / f"{product_slug}.api-profile.v1.json",
        output_directory
        / "contracts"
        / "analytics-products"
        / f"{product_slug}.analytics-profile.v1.json",
    ]
    payloads = [
        _product_payload(
            repository=repository,
            product_name=product_name,
            product_version=product_version,
            authoritative_domain=authoritative_domain,
            product_family=product_family,
        ),
        _telemetry_payload(
            repository=repository,
            product_name=product_name,
            product_version=product_version,
        ),
        _slo_payload(
            repository=repository,
            product_name=product_name,
            product_version=product_version,
        ),
        _access_payload(
            repository=repository,
            product_name=product_name,
            product_version=product_version,
        ),
        _evidence_payload(
            repository=repository,
            product_name=product_name,
            product_version=product_version,
        ),
        _source_api_profile_payload(
            repository=repository,
            product_name=product_name,
            product_version=product_version,
            authoritative_domain=authoritative_domain,
            product_family=product_family,
        ),
        _analytics_product_profile_payload(
            repository=repository,
            product_name=product_name,
            product_version=product_version,
            authoritative_domain=authoritative_domain,
            product_family=product_family,
        ),
    ]
    for path, payload in zip(written_paths, payloads, strict=True):
        _write_json(path, payload)

    readme_path = output_directory / "README.md"
    readme_path.write_text(
        _readme(
            repository=repository,
            product_name=product_name,
            product_version=product_version,
            authoritative_domain=authoritative_domain,
            product_family=product_family,
        ),
        encoding="utf-8",
    )

    checklist_path = output_directory / "PRODUCT-ONBOARDING-CHECKLIST.md"
    checklist_path.parent.mkdir(parents=True, exist_ok=True)
    checklist_path.write_text(
        _checklist(
            repository=repository,
            product_name=product_name,
            product_version=product_version,
            written_paths=[*written_paths, readme_path, checklist_path],
            output_directory=output_directory,
        ),
        encoding="utf-8",
    )
    api_certification_path = (
        output_directory / "docs" / "API-CERTIFICATION-CHECKLIST.md"
    )
    api_certification_path.parent.mkdir(parents=True, exist_ok=True)
    api_certification_path.write_text(
        _api_certification_checklist(
            repository=repository,
            product_name=product_name,
            product_version=product_version,
        ),
        encoding="utf-8",
    )

    ingestion_path = output_directory / "docs" / "INGESTION-PIPELINE-CHECKLIST.md"
    ingestion_path.write_text(
        _ingestion_pipeline_checklist(
            repository=repository,
            product_name=product_name,
            product_version=product_version,
        ),
        encoding="utf-8",
    )
    analytics_certification_path = (
        output_directory / "docs" / "ANALYTICS-DATA-PRODUCT-CERTIFICATION-CHECKLIST.md"
    )
    analytics_certification_path.write_text(
        _analytics_product_certification_checklist(
            repository=repository,
            product_name=product_name,
            product_version=product_version,
        ),
        encoding="utf-8",
    )
    return [
        *written_paths,
        readme_path,
        checklist_path,
        api_certification_path,
        ingestion_path,
        analytics_certification_path,
    ]


def _validate_identity_inputs(
    *, repository: str, product_name: str, product_version: str
) -> None:
    if not REPOSITORY_PATTERN.fullmatch(repository):
        raise ValueError("repository must match lotus-*")
    if not PRODUCT_NAME_PATTERN.fullmatch(product_name):
        raise ValueError("product_name must be PascalCase without separators")
    if not PRODUCT_VERSION_PATTERN.fullmatch(product_version):
        raise ValueError("product_version must be vN or semantic versioning")


def _load_required_json(path: Path, issues: list[str]) -> dict[str, Any]:
    if not path.exists():
        issues.append(f"{path}: required onboarding file is missing")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        issues.append(f"{path}: invalid JSON: {exc}")
        return {}


def _domain_product_onboarding_required_paths(
    *, output_directory: Path, repository: str, product_slug: str
) -> dict[str, Path]:
    return {
        "product": output_directory
        / "contracts"
        / "domain-data-products"
        / f"{repository}-products.v1.json",
        "telemetry": output_directory
        / "contracts"
        / "trust-telemetry"
        / f"{product_slug}.telemetry.v1.json",
        "slo": output_directory
        / "platform-contracts"
        / "mesh-slo"
        / f"{repository}-{product_slug}.slo.v1.json",
        "access": output_directory
        / "platform-contracts"
        / "mesh-access"
        / f"{repository}-{product_slug}.access.v1.json",
        "evidence": output_directory
        / "platform-contracts"
        / "mesh-evidence"
        / f"{repository}-{product_slug}.evidence-pack-policy.v1.json",
        "source_api_profile": output_directory
        / "contracts"
        / "source-data-products"
        / f"{product_slug}.api-profile.v1.json",
        "analytics_product_profile": output_directory
        / "contracts"
        / "analytics-products"
        / f"{product_slug}.analytics-profile.v1.json",
        "readme": output_directory / "README.md",
        "checklist": output_directory / "PRODUCT-ONBOARDING-CHECKLIST.md",
        "api_certification": output_directory
        / "docs"
        / "API-CERTIFICATION-CHECKLIST.md",
        "ingestion_pipeline": output_directory
        / "docs"
        / "INGESTION-PIPELINE-CHECKLIST.md",
        "analytics_certification": output_directory
        / "docs"
        / "ANALYTICS-DATA-PRODUCT-CERTIFICATION-CHECKLIST.md",
    }


def _load_domain_product_policy_payloads(
    *, required_paths: dict[str, Path], issues: list[str]
) -> dict[str, dict[str, Any]]:
    non_json_keys = {
        "readme",
        "checklist",
        "api_certification",
        "ingestion_pipeline",
        "analytics_certification",
    }
    return {
        key: _load_required_json(path, issues)
        for key, path in required_paths.items()
        if key not in non_json_keys
    }


def _validate_product_declaration(
    *,
    issues: list[str],
    product_payload: dict[str, Any],
    repository: str,
    product_name: str,
    product_version: str,
) -> None:
    if product_payload.get("contract_id") != "domain-data-products":
        issues.append("product declaration contract_id must be domain-data-products")
    if product_payload.get("producer_repository") != repository:
        issues.append("product declaration producer_repository does not match")
    products = product_payload.get("products", [])
    if not products:
        issues.append("product declaration must include at least one product")
        return
    product = products[0]
    if product.get("product_name") != product_name:
        issues.append("product declaration product_name does not match")
    if product.get("product_version") != product_version:
        issues.append("product declaration product_version does not match")
    if product.get("owner_repository") != repository:
        issues.append("product declaration owner_repository does not match")


def _validate_policy_identity(
    *,
    issues: list[str],
    payloads: dict[str, dict[str, Any]],
    product_id: str,
    repository: str,
) -> None:
    for key in (
        "telemetry",
        "slo",
        "access",
        "evidence",
        "source_api_profile",
        "analytics_product_profile",
    ):
        payload = payloads.get(key, {})
        if payload.get("product_id") != product_id:
            issues.append(f"{key} policy product_id does not match {product_id}")
        if payload.get("producer_repository") != repository:
            issues.append(f"{key} policy producer_repository does not match")


def _validate_source_api_profile(
    *, issues: list[str], source_api_profile: dict[str, Any]
) -> None:
    if source_api_profile.get("contract_id") != "lotus-source-data-product-api-profile":
        issues.append(
            "source_api_profile contract_id must be lotus-source-data-product-api-profile"
        )
    certification = source_api_profile.get("certification", {})
    for field in (
        "api_certification_required",
        "openapi_quality_required",
        "source_data_product_contract_guard_required",
        "domain_product_validation_required",
        "trust_telemetry_required",
        "mesh_certification_required",
        "live_canonical_evidence_required",
    ):
        if certification.get(field) is not True:
            issues.append(f"source_api_profile certification.{field} must be true")


def _validate_analytics_product_profile(
    *, issues: list[str], analytics_profile: dict[str, Any]
) -> None:
    if analytics_profile.get("contract_id") != "lotus-analytics-data-product-profile":
        issues.append(
            "analytics_product_profile contract_id must be lotus-analytics-data-product-profile"
        )
    for section_name, required_fields in {
        "analytics_methodology": (
            "methodology_document_required",
            "formula_dictionary_required",
            "deterministic_worked_examples_required",
            "edge_case_and_failure_behavior_required",
            "unsupported_state_catalog_required",
        ),
        "computation_contract": (
            "source_authority_map_required",
            "raw_vs_final_result_evidence_required",
            "reconciliation_evidence_required",
            "materiality_threshold_policy_required",
            "status_contract_required",
            "reason_codes_required",
            "source_alignment_controls_required",
            "support_safe_daily_evidence_required",
            "lineage_required",
            "restatement_policy_required",
        ),
        "downstream_realization": (
            "gateway_contract_required",
            "workbench_product_surface_required",
            "consumer_search_required_before_api_change",
            "same_rfc_consumer_updates_required",
        ),
        "proof_requirements": (
            "unit_tests_required",
            "integration_tests_required",
            "contract_openapi_tests_required",
            "e2e_or_live_canonical_proof_required",
            "observability_and_safe_diagnostics_required",
            "data_mesh_certification_required",
        ),
    }.items():
        section = analytics_profile.get(section_name, {})
        for field in required_fields:
            if section.get(field) is not True:
                issues.append(
                    f"analytics_product_profile {section_name}.{field} must be true"
                )


def _validate_required_markdown_text(
    *,
    issues: list[str],
    path: Path,
    missing_prefix: str,
    required_texts: tuple[str, ...],
) -> None:
    if not path.exists():
        issues.append(f"{path}: required onboarding file is missing")
        return
    content = path.read_text(encoding="utf-8")
    for required_text in required_texts:
        if required_text not in content:
            issues.append(f"{missing_prefix}: {required_text}")


def _validate_required_checklist_sections(
    *, issues: list[str], path: Path, sections: tuple[str, ...]
) -> None:
    if not path.exists():
        issues.append(f"{path}: required onboarding file is missing")
        return
    checklist = path.read_text(encoding="utf-8")
    for section in sections:
        if section not in checklist:
            issues.append(f"checklist missing section: {section}")


def validate_domain_product_onboarding_bundle(
    *,
    output_directory: Path,
    repository: str,
    product_name: str,
    product_version: str,
) -> list[str]:
    _validate_identity_inputs(
        repository=repository,
        product_name=product_name,
        product_version=product_version,
    )
    product_slug = _kebab(product_name)
    product_id = _product_id(repository, product_name, product_version)
    required_paths = _domain_product_onboarding_required_paths(
        output_directory=output_directory,
        repository=repository,
        product_slug=product_slug,
    )
    issues: list[str] = []
    payloads = _load_domain_product_policy_payloads(
        required_paths=required_paths,
        issues=issues,
    )

    _validate_product_declaration(
        issues=issues,
        product_payload=payloads.get("product", {}),
        repository=repository,
        product_name=product_name,
        product_version=product_version,
    )
    _validate_policy_identity(
        issues=issues,
        payloads=payloads,
        product_id=product_id,
        repository=repository,
    )
    _validate_source_api_profile(
        issues=issues,
        source_api_profile=payloads.get("source_api_profile", {}),
    )
    _validate_analytics_product_profile(
        issues=issues,
        analytics_profile=payloads.get("analytics_product_profile", {}),
    )

    _validate_required_markdown_text(
        issues=issues,
        path=required_paths["readme"],
        missing_prefix="README missing required guidance",
        required_texts=(
            product_id,
            "Keep source truth in the producer repository",
            "Publish through `lotus-gateway`",
            "Treat placeholders as blockers before production certification",
        ),
    )
    _validate_required_checklist_sections(
        issues=issues,
        path=required_paths["checklist"],
        sections=(
            "Producer declaration",
            "Runtime telemetry",
            "SLO policy",
            "Access policy",
            "Evidence policy",
            "Lifecycle policy",
            "Gateway publication",
            "Workbench discovery",
            "Tests",
            "Documentation",
            "Analytics product profile",
        ),
    )
    _validate_required_markdown_text(
        issues=issues,
        path=required_paths["api_certification"],
        missing_prefix="API certification checklist missing guidance",
        required_texts=(
            "every request option",
            "every output family",
            "OpenAPI",
            "Live canonical validation",
        ),
    )
    _validate_required_markdown_text(
        issues=issues,
        path=required_paths["ingestion_pipeline"],
        missing_prefix="ingestion checklist missing guidance",
        required_texts=(
            "Authoritative source systems",
            "Idempotency keys",
            "Source batch",
            "Runtime telemetry",
            "Canonical demo seed data",
        ),
    )
    _validate_required_markdown_text(
        issues=issues,
        path=required_paths["analytics_certification"],
        missing_prefix="analytics certification checklist missing guidance",
        required_texts=(
            "Methodology documentation",
            "Raw result",
            "materiality classification",
            "source-alignment controls",
            "Support-safe daily",
            "Gateway preserves",
            "Workbench renders",
            "All downstream consumers",
            "mesh certification",
        )
    )

    return issues


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate or validate an RFC-0091 domain-product onboarding bundle."
    )
    parser.add_argument("--repository", required=True)
    parser.add_argument("--product-name", required=True)
    parser.add_argument("--product-version", default="v1")
    parser.add_argument("--authoritative-domain", default="replace_with_domain")
    parser.add_argument("--product-family", default="replace_with_product_family")
    parser.add_argument("--output-directory", type=Path, default=None)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    output_directory = args.output_directory or (
        DEFAULT_OUTPUT_ROOT / f"{args.repository}-{_kebab(args.product_name)}"
    )
    if args.check:
        issues = validate_domain_product_onboarding_bundle(
            output_directory=output_directory,
            repository=args.repository,
            product_name=args.product_name,
            product_version=args.product_version,
        )
        for issue in issues:
            print(issue)
        return 1 if issues else 0

    written_paths = scaffold_domain_product_onboarding(
        repository=args.repository,
        product_name=args.product_name,
        product_version=args.product_version,
        authoritative_domain=args.authoritative_domain,
        product_family=args.product_family,
        output_directory=output_directory,
    )
    print(f"Wrote {len(written_paths)} onboarding files to {output_directory}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
