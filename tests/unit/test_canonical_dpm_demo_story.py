from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_canonical_dpm_demo_story_is_audience_ready_and_evidence_backed() -> None:
    deep_doc = (ROOT / "docs" / "demo" / "canonical-dpm-demo-story.md").read_text(
        encoding="utf-8"
    )
    wiki = (ROOT / "wiki" / "Canonical-DPM-Demo-Story.md").read_text(encoding="utf-8")
    sidebar = (ROOT / "wiki" / "_Sidebar.md").read_text(encoding="utf-8")
    home = (ROOT / "wiki" / "Home.md").read_text(encoding="utf-8")

    for content in (deep_doc, wiki):
        assert "PB_SG_GLOBAL_BAL_001" in content
        assert "BMK_PB_GLOBAL_BALANCED_60_40" in content
        assert "canonical-front-office-demo-data-contract.json" in content
        assert "canonical-front-office-demo-data-invariants.json" in content
        assert "workbench-panel-registry.json" in content
        assert "Invoke-Canonical-FrontOffice-QA.ps1" in content
        assert "dpm.command_center" in content
        assert "dpm.portfolio_memory" in content
        assert "dpm.proof_pack" in content
        assert "dpm.wave_command_center" in content
        assert "dpm.outcome_review" in content
        assert "advisory.advisor_cockpit" in content
        assert "advisory.bank_demo_proof" in content
        assert "ADVISOR_COCKPIT_ACTION_ACKNOWLEDGED" in content
        assert "BANK_DEMO_PROOF_PACK_CREATED" in content
        assert "2026-04-10" in content
        assert "2026-05-03" in content
        assert "sales" in content.lower()
        assert "pre-sales" in content.lower()
        assert "operations" in content.lower()
        assert "client demos" in content.lower()
        assert "```mermaid" in content

    for unsupported_claim in (
        "external OMS execution",
        "PM quality scoring",
        "client-communication source-event lineage",
        "autonomous AI decisioning",
        "local Workbench recomputation",
    ):
        assert unsupported_claim in deep_doc
        assert unsupported_claim in wiki

    assert "[Canonical DPM Demo Story](Canonical-DPM-Demo-Story)" in sidebar
    assert "[Canonical DPM Demo Story](Canonical-DPM-Demo-Story)" in home


def test_canonical_dpm_demo_story_uses_current_contract_identity() -> None:
    contract_text = (
        ROOT / "context" / "contracts" / "canonical-front-office-demo-data-contract.json"
    ).read_text(encoding="utf-8")
    panel_registry = (
        ROOT / "context" / "contracts" / "workbench-panel-registry.json"
    ).read_text(encoding="utf-8")
    deep_doc = (ROOT / "docs" / "demo" / "canonical-dpm-demo-story.md").read_text(
        encoding="utf-8"
    )

    for required_value in (
        "PB_SG_GLOBAL_BAL_001",
        "BMK_PB_GLOBAL_BALANCED_60_40",
        "MANDATE_PB_SG_GLOBAL_BAL_001",
        "PM_SG_DPM_001",
        "BOOK_SG_BALANCED_DPM",
        "MODEL_PB_SG_GLOBAL_BAL_DPM",
        "POLICY_DPM_SG_BALANCED_V1",
        "RFC41_MULTI_PORTFOLIO_EXPLICIT_LIST_CANONICAL",
        "RFC26_ADVISOR_COCKPIT_POLICY_ACTION_CANONICAL",
        "RFC28_BANK_DEMO_CLIENT_READY_PROOF_CANONICAL",
        "2026-05-03",
    ):
        assert required_value in contract_text
        assert required_value in deep_doc

    assert "DPM command-center portfolio valuation date | `2026-04-10`" in deep_doc
    assert "DPM campaign governance date | `2026-05-03`" in deep_doc

    for panel_id in (
        "dpm.command_center",
        "dpm.portfolio_memory",
        "dpm.proof_pack",
        "dpm.wave_command_center",
        "dpm.outcome_review",
        "advisory.advisor_cockpit",
        "advisory.bank_demo_proof",
    ):
        assert panel_id in panel_registry
        assert panel_id in deep_doc
