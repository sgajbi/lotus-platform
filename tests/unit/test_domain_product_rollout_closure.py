from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROJECTS_ROOT = ROOT.parent
SOURCE_MANIFEST_PATH = (
    ROOT
    / "platform-contracts"
    / "domain-data-products"
    / "domain-product-source-manifest.v1.json"
)
CATALOG_PATH = ROOT / "generated" / "domain-product-catalog.json"
CERTIFICATION_REPORT_PATH = (
    ROOT / "generated" / "domain-product-certification-report.json"
)
RFC_0086_PATH = (
    ROOT
    / "rfcs"
    / "RFC-0086-repo-native-domain-product-onboarding-and-federated-rollout.md"
)

FIRST_WAVE_REPOSITORIES = [
    "lotus-core",
    "lotus-performance",
    "lotus-risk",
    "lotus-advise",
    "lotus-report",
    "lotus-manage",
]


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _catalog_source_paths(catalog: dict) -> set[str]:
    return {
        artifact["source_path"]
        for artifact in [*catalog["products"], *catalog["consumers"]]
    }


def _has_product(
    catalog: dict,
    *,
    product_name: str,
    producer_repository: str,
    lifecycle_status: str | None = None,
    current_route: str | None = None,
) -> bool:
    for product in catalog["products"]:
        if product["product_name"] != product_name:
            continue
        if product["producer_repository"] != producer_repository:
            continue
        if (
            lifecycle_status is not None
            and product["lifecycle_status"] != lifecycle_status
        ):
            continue
        if current_route is not None and current_route not in product["current_routes"]:
            continue
        return True
    return False


def _assert_product_present(catalog: dict, **criteria: str) -> None:
    assert _has_product(catalog, **criteria)


def _assert_certification_uses_first_wave_repo_sources(
    certification_report: dict,
) -> None:
    assert certification_report["summary"]["certification_state"] == "certified"
    assert certification_report["summary"]["included_repository_count"] == len(
        FIRST_WAVE_REPOSITORIES
    )
    assert certification_report["summary"]["pending_repository_count"] == 0
    assert certification_report["source_manifest_posture"]["included_repositories"] == (
        FIRST_WAVE_REPOSITORIES
    )
    assert certification_report["source_manifest_posture"]["pending_repositories"] == []


def test_rfc_0086_source_manifest_closes_first_wave_as_repo_native() -> None:
    manifest = _read_json(SOURCE_MANIFEST_PATH)
    by_repository = {entry["repository"]: entry for entry in manifest["repositories"]}

    assert list(by_repository) == FIRST_WAVE_REPOSITORIES

    for repository in FIRST_WAVE_REPOSITORIES:
        entry = by_repository[repository]
        repo_native_directory = (
            PROJECTS_ROOT / repository / entry["repo_native_declaration_path"]
        )

        assert entry["source_mode"] == "repo_native"
        assert entry["catalog_inclusion"] == "included"
        assert entry["repo_native_status"] == "implemented"
        assert entry["platform_declaration_paths"] == []
        assert repo_native_directory.exists()
        assert any(repo_native_directory.glob("*.v1.json"))


def test_rfc_0086_catalog_and_certification_use_repo_native_sources() -> None:
    catalog = _read_json(CATALOG_PATH)
    certification_report = _read_json(CERTIFICATION_REPORT_PATH)

    assert catalog["source_declaration_directory"] == (
        "federated:domain-product-source-manifest"
    )
    assert catalog["product_count"] == 71
    assert catalog["dependency_count"] == 46
    _assert_product_present(
        catalog,
        product_name="DpmPortfolioUniverseCandidate",
        producer_repository="lotus-core",
    )
    _assert_product_present(
        catalog,
        product_name="AdvisoryPolicyEvaluationRecord",
        producer_repository="lotus-advise",
        lifecycle_status="active",
        current_route="/advisory/policy-evaluations/review-queue",
    )
    _assert_product_present(
        catalog,
        product_name="AdvisoryActionItemRegister",
        producer_repository="lotus-advise",
        lifecycle_status="active",
        current_route="/advisory/cockpit/actions",
    )
    _assert_product_present(
        catalog,
        product_name="AdvisorCockpitOperatingSnapshot",
        producer_repository="lotus-advise",
        lifecycle_status="active",
        current_route="/advisory/cockpit/snapshot",
    )
    assert not any(
        source_path.startswith("platform-contracts/domain-data-products/")
        for source_path in _catalog_source_paths(catalog)
    )
    _assert_certification_uses_first_wave_repo_sources(certification_report)


def test_rfc_0086_documents_lotus_ai_and_platform_mirror_closure_posture() -> None:
    rfc = RFC_0086_PATH.read_text(encoding="utf-8")

    assert "| Status | Implemented |" in rfc
    assert (
        "`lotus-ai` is not a first-wave RFC-0086 producer or consumer declaration "
        "participant"
    ) in rfc
    assert (
        "transitional platform mirror declarations are retained as compatibility "
        "evidence only"
    ) in rfc
    assert "the active generated catalog must" in rfc
    assert (
        "not use `platform-contracts/domain-data-products/` as a product or consumer source path"
        in rfc
    )
