from __future__ import annotations

import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATOR_PATH = ROOT / "automation" / "generate_enterprise_mesh_maturity_matrix.py"
GENERATED_DIRECTORY = ROOT / "generated"
CHECKED_IN_GENERATED_AT = "2026-06-24T00:00:00Z"


def _load_generator_module():
    automation_path = str(ROOT / "automation")
    if automation_path not in sys.path:
        sys.path.insert(0, automation_path)
    spec = importlib.util.spec_from_file_location(
        "enterprise_mesh_maturity_matrix_test", GENERATOR_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_enterprise_mesh_maturity_matrix_classifies_every_lotus_repo() -> None:
    generator = _load_generator_module()

    matrix = generator.build_enterprise_mesh_maturity_matrix(
        generated_at_utc=CHECKED_IN_GENERATED_AT
    )

    repositories = {entry["repository"]: entry for entry in matrix["repositories"]}
    assert list(repositories) == generator.LOTUS_REPOSITORIES
    assert matrix["contract_id"] == "lotus-enterprise-mesh-maturity-matrix"
    assert matrix["governed_by_rfcs"] == ["RFC-0091"]
    assert matrix["summary"]["repository_count"] == len(generator.LOTUS_REPOSITORIES)
    assert matrix["summary"]["ambiguous_repository_count"] == 0
    assert matrix["ambiguous_repositories"] == []
    assert matrix["implementation_boundary"][
        "certification_candidate_repositories"
    ] == ["lotus-report", "lotus-idea"]
    assert matrix["implementation_boundary"]["future_wave_catalog_repositories"] == [
        "lotus-idea"
    ]

    for repository in (
        "lotus-core",
        "lotus-performance",
        "lotus-risk",
        "lotus-advise",
        "lotus-manage",
    ):
        assert repositories[repository]["classification"] == "certified_first_wave"
        assert repositories[repository]["ambiguous_participation"] is False

    assert repositories["lotus-core"]["first_wave_product_count"] == 2
    assert repositories["lotus-advise"]["first_wave_product_count"] == 2
    for repository in (
        "lotus-performance",
        "lotus-risk",
        "lotus-manage",
    ):
        assert repositories[repository]["first_wave_product_count"] == 1

    assert repositories["lotus-ai"]["classification"] == "not_mesh_participant"
    assert repositories["lotus-report"]["classification"] == "certification_candidate"
    assert repositories["lotus-report"]["first_wave_product_count"] == 0
    assert repositories["lotus-report"]["certification_candidate_product_count"] == 1
    assert "lotus-report#283" in repositories["lotus-report"]["required_next_step"]
    assert repositories["lotus-idea"]["classification"] == "certification_candidate"
    assert repositories["lotus-idea"]["mesh_role"] == "producer"
    assert repositories["lotus-idea"]["produced_product_count"] == 9
    assert repositories["lotus-idea"]["certification_candidate_product_count"] == 1
    assert repositories["lotus-idea"]["consumed_dependency_count"] == 17
    assert repositories["lotus-idea"]["ambiguous_participation"] is False
    assert repositories["lotus-gateway"]["mesh_role"] == "api_face"
    assert repositories["lotus-workbench"]["mesh_role"] == "discovery_and_operator_ux"


def test_enterprise_mesh_maturity_matrix_defines_candidate_products() -> None:
    generator = _load_generator_module()

    matrix = generator.build_enterprise_mesh_maturity_matrix(
        generated_at_utc=CHECKED_IN_GENERATED_AT
    )
    products = {entry["product_id"]: entry for entry in matrix["products"]}

    for product_id in generator.FIRST_WAVE_PRODUCTS:
        assert products[product_id]["classification"] == "certified_first_wave"
        assert products[product_id]["maturity_wave"] == "enterprise_wave_1"

    assert (
        products["lotus-report:ClientReportEvidencePack:v1"]["classification"]
        == "certification_candidate"
    )
    assert (
        products["lotus-manage:PortfolioActionRegister:v1"]["classification"]
        == "certified_first_wave"
    )
    assert matrix["summary"]["candidate_product_count"] == 2
    assert (
        products["lotus-idea:IdeaCandidate:v1"]["classification"]
        == "certification_candidate"
    )
    assert (
        products["lotus-idea:IdeaCandidate:v1"]["maturity_wave"]
        == "enterprise_wave_candidate"
    )


def test_enterprise_mesh_maturity_matrix_writes_json_and_markdown(
    tmp_path: Path,
) -> None:
    generator = _load_generator_module()

    generator.write_enterprise_mesh_maturity_matrix(
        output_directory=tmp_path,
        generated_at_utc=CHECKED_IN_GENERATED_AT,
    )

    matrix = json.loads(
        (tmp_path / "enterprise-mesh-maturity-matrix.json").read_text(
            encoding="utf-8"
        )
    )
    markdown = (tmp_path / "enterprise-mesh-maturity-matrix.md").read_text(
        encoding="utf-8"
    )

    assert matrix["summary"]["repository_count"] == len(generator.LOTUS_REPOSITORIES)
    assert "`lotus-report:ClientReportEvidencePack:v1`" in markdown
    assert "## Repository Maturity" in markdown
    assert "## Product Maturity" in markdown


def test_checked_in_enterprise_mesh_maturity_matrix_is_not_stale(
    tmp_path: Path,
) -> None:
    generator = _load_generator_module()

    generator.write_enterprise_mesh_maturity_matrix(
        output_directory=tmp_path,
        generated_at_utc=CHECKED_IN_GENERATED_AT,
    )

    for artifact_name in (
        "enterprise-mesh-maturity-matrix.json",
        "enterprise-mesh-maturity-matrix.md",
    ):
        assert (GENERATED_DIRECTORY / artifact_name).read_text(encoding="utf-8") == (
            tmp_path / artifact_name
        ).read_text(encoding="utf-8")


def test_enterprise_mesh_maturity_matrix_check_reports_stale_outputs(
    tmp_path: Path,
) -> None:
    generator = _load_generator_module()

    generator.write_enterprise_mesh_maturity_matrix(
        output_directory=tmp_path,
        generated_at_utc=CHECKED_IN_GENERATED_AT,
    )
    (tmp_path / "enterprise-mesh-maturity-matrix.md").write_text(
        "stale\n",
        encoding="utf-8",
    )

    issues = generator.check_enterprise_mesh_maturity_matrix(
        output_directory=tmp_path,
        generated_at_utc=CHECKED_IN_GENERATED_AT,
    )

    assert issues == [
        f"{tmp_path / 'enterprise-mesh-maturity-matrix.md'}: generated maturity artifact is stale"
    ]


def test_enterprise_mesh_maturity_matrix_detects_ambiguous_participation(
    tmp_path: Path,
) -> None:
    generator = _load_generator_module()
    catalog = json.loads(
        (ROOT / "generated" / "domain-product-catalog.json").read_text(
            encoding="utf-8"
        )
    )
    ambiguous_catalog = deepcopy(catalog)
    ambiguous_catalog["products"] = [
        product
        for product in ambiguous_catalog["products"]
        if product["product_id"] != "lotus-core:PortfolioStateSnapshot:v1"
    ]
    ambiguous_catalog["products"].append(
        {
            "product_id": "lotus-unknown:UnownedProduct:v1",
            "product_name": "UnownedProduct",
            "product_version": "v1",
            "producer_repository": "lotus-unknown",
            "lifecycle_status": "active",
            "source_path": "unknown",
        }
    )
    catalog_path = tmp_path / "domain-product-catalog.json"
    catalog_path.write_text(json.dumps(ambiguous_catalog), encoding="utf-8")

    matrix = generator.build_enterprise_mesh_maturity_matrix(
        catalog_path=catalog_path,
        generated_at_utc=CHECKED_IN_GENERATED_AT,
    )

    assert matrix["summary"]["ambiguous_repository_count"] == 2
    assert matrix["unknown_repositories"] == ["lotus-unknown"]
    assert matrix["missing_required_products"] == [
        "lotus-core:PortfolioStateSnapshot:v1"
    ]
    assert matrix["ambiguous_repositories"] == ["lotus-core", "lotus-unknown"]
