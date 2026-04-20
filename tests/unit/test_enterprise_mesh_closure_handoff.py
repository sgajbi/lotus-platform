from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HANDOFF_PATH = ROOT / "docs" / "operations" / "enterprise-mesh-completion-handoff.md"
LEDGER_PATH = ROOT / "generated" / "enterprise-mesh-closure-ledger.json"
WIKI_PATH = ROOT / "wiki" / "Enterprise-Mesh-Status.md"
SIDEBAR_PATH = ROOT / "wiki" / "_Sidebar.md"
ENGINEERING_CONTEXT_PATH = ROOT / "context" / "LOTUS-ENGINEERING-CONTEXT.md"
REFERENCE_MAP_PATH = ROOT / "context" / "CONTEXT-REFERENCE-MAP.md"
REPOSITORY_CONTEXT_PATH = ROOT / "REPOSITORY-ENGINEERING-CONTEXT.md"

COMPLETED_RFCS = [
    "RFC-0084",
    "RFC-0085",
    "RFC-0086",
    "RFC-0087",
    "RFC-0088",
    "RFC-0089",
    "RFC-0090",
    "RFC-0091",
    "RFC-0092",
]

PRODUCT_IDS = [
    "lotus-core:PortfolioStateSnapshot:v1",
    "lotus-performance:ReturnsSeriesBundle:v1",
    "lotus-risk:RiskMetricsReport:v1",
    "lotus-advise:AdvisoryProposalLifecycleRecord:v1",
    "lotus-report:ClientReportEvidencePack:v1",
    "lotus-manage:PortfolioActionRegister:v1",
]

REPO_ROLES = {
    "lotus-platform": "governance_control_plane",
    "lotus-gateway": "read_only_api_publication_face",
    "lotus-workbench": "self_serve_discovery_surface",
    "lotus-ai": "explicit_non_first_wave_participant",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_enterprise_mesh_handoff_doc_preserves_completed_program_truth() -> None:
    text = _read(HANDOFF_PATH)

    assert "complete foundation and operating control plane" in text
    for rfc in COMPLETED_RFCS:
        assert rfc in text
    for product_id in PRODUCT_IDS:
        assert product_id in text
    for expected in [
        "lotus-gateway` is the read-only API publication face",
        "lotus-workbench` is the self-serve `/data-products` discovery surface",
        "lotus-ai` is explicitly not a first-wave producer",
        "generated/enterprise-mesh-closure-ledger.json",
        "Future work should not reopen the mesh foundation unless a defect is found.",
    ]:
        assert expected in text


def test_enterprise_mesh_closure_ledger_is_machine_readable_and_complete() -> None:
    ledger = json.loads(_read(LEDGER_PATH))

    assert ledger["contract_id"] == "lotus-enterprise-mesh-closure-ledger"
    assert ledger["status"] == "complete_foundation_and_operating_control_plane"
    assert ledger["completed_rfcs"] == COMPLETED_RFCS
    product_ids = {
        repo["product_id"]
        for repo in ledger["repositories"]
        if repo.get("product_id") is not None
    }
    assert product_ids == set(PRODUCT_IDS)
    roles = {repo["repo"]: repo["mesh_role"] for repo in ledger["repositories"]}
    for repo, role in REPO_ROLES.items():
        assert roles[repo] == role
    assert any(
        command.startswith("python automation/mesh_certification_gate.py")
        for command in ledger["validation_commands"]
    )
    assert "build production certification history" in ledger["future_work_boundary"]


def test_enterprise_mesh_status_wiki_is_linked_and_publishable() -> None:
    wiki = _read(WIKI_PATH)
    sidebar = _read(SIDEBAR_PATH)

    assert "[Enterprise Mesh Status](Enterprise-Mesh-Status)" in sidebar
    for rfc in COMPLETED_RFCS:
        assert rfc in wiki
    for product_id in PRODUCT_IDS:
        assert product_id in wiki
    assert "lotus-ai`: explicit non-first-wave participant" in wiki
    assert "enterprise-mesh-closure-ledger.json" in wiki


def test_platform_context_points_future_agents_to_mesh_handoff() -> None:
    for path in [
        ENGINEERING_CONTEXT_PATH,
        REFERENCE_MAP_PATH,
        REPOSITORY_CONTEXT_PATH,
    ]:
        text = _read(path)
        assert "enterprise-mesh-completion-handoff.md" in text
        assert "enterprise-mesh-closure-ledger.json" in text
