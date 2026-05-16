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

    source_paths = {
        artifact["source_path"]
        for artifact in [*catalog["products"], *catalog["consumers"]]
    }

    assert catalog["source_declaration_directory"] == (
        "federated:domain-product-source-manifest"
    )
    assert catalog["product_count"] == 60
    assert catalog["dependency_count"] == 28
    assert not any(
        source_path.startswith("platform-contracts/domain-data-products/")
        for source_path in source_paths
    )
    assert certification_report["summary"]["certification_state"] == "certified"
    assert certification_report["summary"]["included_repository_count"] == len(
        FIRST_WAVE_REPOSITORIES
    )
    assert certification_report["summary"]["pending_repository_count"] == 0
    assert certification_report["source_manifest_posture"]["included_repositories"] == (
        FIRST_WAVE_REPOSITORIES
    )
    assert certification_report["source_manifest_posture"]["pending_repositories"] == []


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
