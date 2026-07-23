from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class MeshMaturityProduct:
    product_id: str
    producer_repository: str


REQUIRED_MATURITY_PRODUCTS: tuple[MeshMaturityProduct, ...] = (
    MeshMaturityProduct(
        product_id="lotus-core:PortfolioStateSnapshot:v1",
        producer_repository="lotus-core",
    ),
    MeshMaturityProduct(
        product_id="lotus-core:DpmSourceReadiness:v1",
        producer_repository="lotus-core",
    ),
    MeshMaturityProduct(
        product_id="lotus-performance:ReturnsSeriesBundle:v1",
        producer_repository="lotus-performance",
    ),
    MeshMaturityProduct(
        product_id="lotus-risk:RiskMetricsReport:v1",
        producer_repository="lotus-risk",
    ),
    MeshMaturityProduct(
        product_id="lotus-advise:AdvisoryProposalLifecycleRecord:v1",
        producer_repository="lotus-advise",
    ),
    MeshMaturityProduct(
        product_id="lotus-advise:AdvisoryProposalMemoEvidencePack:v1",
        producer_repository="lotus-advise",
    ),
    MeshMaturityProduct(
        product_id="lotus-report:ClientReportEvidencePack:v1",
        producer_repository="lotus-report",
    ),
    MeshMaturityProduct(
        product_id="lotus-manage:PortfolioActionRegister:v1",
        producer_repository="lotus-manage",
    ),
)

CERTIFICATION_CANDIDATE_PRODUCTS: tuple[MeshMaturityProduct, ...] = (
    MeshMaturityProduct(
        product_id="lotus-idea:IdeaCandidate:v1",
        producer_repository="lotus-idea",
    ),
)

REQUIRED_PRODUCTS: dict[str, str] = {
    product.product_id: product.producer_repository
    for product in REQUIRED_MATURITY_PRODUCTS
}
REQUIRED_PRODUCT_IDS: frozenset[str] = frozenset(REQUIRED_PRODUCTS)
CERTIFICATION_CANDIDATE_PRODUCT_IDS: frozenset[str] = frozenset(
    product.product_id for product in CERTIFICATION_CANDIDATE_PRODUCTS
)
CERTIFICATION_CANDIDATE_REPOSITORIES: tuple[str, ...] = tuple(
    dict.fromkeys(product.producer_repository for product in CERTIFICATION_CANDIDATE_PRODUCTS)
)
REQUIRED_PRODUCER_REPOSITORIES: tuple[str, ...] = tuple(
    dict.fromkeys(product.producer_repository for product in REQUIRED_MATURITY_PRODUCTS)
)


def default_runtime_telemetry_directories() -> list[Path]:
    return [
        ROOT.parent / repository / "output" / "trust-telemetry" / "runtime"
        for repository in REQUIRED_PRODUCER_REPOSITORIES
    ]


def default_static_telemetry_directories() -> list[Path]:
    return [
        ROOT.parent / repository / "contracts" / "trust-telemetry"
        for repository in REQUIRED_PRODUCER_REPOSITORIES
    ]
