from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_data_mesh_standard_is_contextual_and_certification_backed() -> None:
    standard = _read("docs/standards/Lotus Data Mesh Standard.md")
    wiki = _read("wiki/Data-Mesh-Standard.md")
    docs_index = _read("docs/README.md")
    sidebar = _read("wiki/_Sidebar.md")
    home = _read("wiki/Home.md")
    engineering_context = _read("context/LOTUS-ENGINEERING-CONTEXT.md")
    reference_map = _read("context/CONTEXT-REFERENCE-MAP.md")
    repo_context = _read("REPOSITORY-ENGINEERING-CONTEXT.md")

    for content in (standard, wiki):
        assert "```mermaid" in content
        assert "catalog inclusion" in content.lower()
        assert "not certification" in content.lower() or "never certification" in content.lower()
        assert "runtime trust telemetry" in content
        assert "SLO, access, and evidence" in content
        assert "Gateway" in content
        assert "Workbench" in content
        assert "lotus-idea" in content
        assert "not certified" in content.lower()

    for repository in (
        "lotus-core",
        "lotus-performance",
        "lotus-risk",
        "lotus-advise",
        "lotus-report",
        "lotus-manage",
        "lotus-idea",
        "lotus-gateway",
        "lotus-workbench",
        "lotus-ai",
    ):
        assert repository in standard

    for content in (docs_index, sidebar, home, engineering_context, reference_map, repo_context):
        assert "Lotus Data Mesh Standard" in content or "Data Mesh Standard" in content


def test_client_demo_certification_standard_is_audience_ready_and_evidence_backed() -> None:
    standard = _read("docs/standards/Lotus Client Demo Certification Standard.md")
    wiki = _read("wiki/Client-Demo-Certification.md")
    sidebar = _read("wiki/_Sidebar.md")
    home = _read("wiki/Home.md")
    canonical_demo = _read("wiki/Canonical-DPM-Demo-Story.md")
    engineering_context = _read("context/LOTUS-ENGINEERING-CONTEXT.md")
    reference_map = _read("context/CONTEXT-REFERENCE-MAP.md")
    repo_context = _read("REPOSITORY-ENGINEERING-CONTEXT.md")

    for content in (standard, wiki):
        assert "```mermaid" in content
        assert "Implementation-backed" in content
        assert "Bounded preview" in content
        assert "Diagnostic" in content
        assert "Planned" in content
        assert "Unsupported" in content
        assert "PB_SG_GLOBAL_BAL_001" in content
        assert "canonical-front-office-demo-data-contract.json" in content
        assert "canonical-front-office-demo-data-invariants.json" in content
        assert "workbench-panel-registry.json" in content
        assert "Invoke-Canonical-FrontOffice-QA.ps1" in content
        assert "Invoke-PlatformDemoReadinessCertification.ps1" in content
        assert "client" in content.lower()

    for content in (sidebar, home, canonical_demo, engineering_context, reference_map, repo_context):
        assert (
            "Lotus Client Demo Certification Standard" in content
            or "Client Demo Certification" in content
        )
