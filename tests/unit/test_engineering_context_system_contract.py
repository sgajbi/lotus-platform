from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTEXT_DIR = ROOT / "context"


def test_rfc_0073_slice_one_central_context_artifacts_exist_and_cross_link() -> None:
    rfc = (ROOT / "rfcs" / "RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md").read_text(
        encoding="utf-8"
    )
    checklist = (ROOT / "rfcs" / "RFC-0073-implementation-checklist.md").read_text(encoding="utf-8")
    context_index = (CONTEXT_DIR / "README.md").read_text(encoding="utf-8")
    quickstart = (CONTEXT_DIR / "LOTUS-QUICKSTART-CONTEXT.md").read_text(encoding="utf-8")
    engineering = (CONTEXT_DIR / "LOTUS-ENGINEERING-CONTEXT.md").read_text(encoding="utf-8")
    reference_map = (CONTEXT_DIR / "CONTEXT-REFERENCE-MAP.md").read_text(encoding="utf-8")
    ledger = (CONTEXT_DIR / "platform-engineering-ledger.md").read_text(encoding="utf-8")
    digest = (CONTEXT_DIR / "recent-architectural-decisions-digest.md").read_text(encoding="utf-8")

    assert "Slice 1 | Central context architecture | Complete" in checklist
    assert "human-maintained memory" in rfc
    assert "platform engineering ledger" in rfc
    assert "recent architectural decisions digest" in rfc

    assert "RFC-0073" in context_index
    assert "./LOTUS-QUICKSTART-CONTEXT.md" in context_index
    assert "./LOTUS-ENGINEERING-CONTEXT.md" in context_index
    assert "./CONTEXT-REFERENCE-MAP.md" in context_index
    assert "./lotus-context-manifest.json" in context_index

    assert "./LOTUS-ENGINEERING-CONTEXT.md" in quickstart
    assert "./CONTEXT-REFERENCE-MAP.md" in quickstart
    assert "./lotus-context-manifest.json" in quickstart
    assert "./platform-engineering-ledger.md" in quickstart
    assert "./recent-architectural-decisions-digest.md" in quickstart

    assert "./LOTUS-QUICKSTART-CONTEXT.md" in engineering
    assert "./CONTEXT-REFERENCE-MAP.md" in engineering
    assert "./lotus-context-manifest.json" in engineering
    assert "./platform-engineering-ledger.md" in engineering
    assert "./recent-architectural-decisions-digest.md" in engineering

    assert "./LOTUS-QUICKSTART-CONTEXT.md" in reference_map
    assert "./LOTUS-ENGINEERING-CONTEXT.md" in reference_map
    assert "./lotus-context-manifest.json" in reference_map
    assert "Repository-Local Context Documents" in reference_map

    assert "canonical local runtime must be treated as a governed operator flow" in ledger.lower()
    assert "ci should use github for heavy execution" in ledger.lower()
    assert "rfc-0071" in digest.lower()
    assert "rfc-0072" in digest.lower()
    assert "documentation and memory posture" in digest.lower()


def test_lotus_context_manifest_has_full_ecosystem_inventory_and_required_registries() -> None:
    manifest = json.loads((CONTEXT_DIR / "lotus-context-manifest.json").read_text(encoding="utf-8"))

    assert manifest["schema_version"] == "1.0"
    assert manifest["generated_by"] == "human-maintained"
    assert manifest["reading_order"] == [
        "AGENTS.md",
        "context/LOTUS-QUICKSTART-CONTEXT.md",
        "context/LOTUS-ENGINEERING-CONTEXT.md",
        "REPOSITORY-ENGINEERING-CONTEXT.md",
        "context/CONTEXT-REFERENCE-MAP.md",
    ]

    assert manifest["context_documents"]["index"] == "context/README.md"
    assert manifest["context_documents"]["quickstart"] == "context/LOTUS-QUICKSTART-CONTEXT.md"
    assert manifest["context_documents"]["engineering_context"] == "context/LOTUS-ENGINEERING-CONTEXT.md"
    assert manifest["context_documents"]["reference_map"] == "context/CONTEXT-REFERENCE-MAP.md"
    assert manifest["context_documents"]["platform_engineering_ledger"] == "context/platform-engineering-ledger.md"
    assert (
        manifest["context_documents"]["recent_architectural_decisions_digest"]
        == "context/recent-architectural-decisions-digest.md"
    )

    assert manifest["maintenance"]["central_owner_repository"] == "lotus-platform"
    assert manifest["maintenance"]["repository_local_context_pattern"] == "REPOSITORY-ENGINEERING-CONTEXT.md"
    assert "canonical commands or validation flow changes" in manifest["maintenance"]["update_triggers"]

    assert manifest["task_routes"]["frontend"][0] == "context/LOTUS-QUICKSTART-CONTEXT.md"
    assert "REPOSITORY-ENGINEERING-CONTEXT.md" in manifest["task_routes"]["backend"]
    assert "context/lotus-context-manifest.json" in manifest["task_routes"]["platform_validation"]

    repositories = {entry["repository"] for entry in manifest["applications"]}
    assert repositories == {
        "lotus-platform",
        "lotus-workbench",
        "lotus-gateway",
        "lotus-core",
        "lotus-performance",
        "lotus-risk",
        "lotus-advise",
        "lotus-manage",
        "lotus-report",
        "lotus-ai",
    }

    assert all(entry["repo_context_path"] == "REPOSITORY-ENGINEERING-CONTEXT.md" for entry in manifest["applications"])
    assert all("requires_platform_end_to_end_validation" in entry for entry in manifest["applications"])

    authority_domains = {entry["domain"] for entry in manifest["domain_authority_map"]}
    assert authority_domains == {
        "portfolio-management-and-transactions",
        "performance-analytics",
        "risk-analytics",
        "advisory-workflows",
        "management-and-operations",
        "reporting-and-document-generation",
        "ai-capabilities",
    }

    standard_names = {entry["name"] for entry in manifest["standards_registry"]}
    assert "Continuous Integration, Validation, and Release Governance Standard" in standard_names
    assert "Testing Pyramid and Coverage Standard" in standard_names
    assert "Domain Vocabulary Glossary" in standard_names

    active_rfcs = {entry["id"] for entry in manifest["active_rfc_registry"]}
    assert active_rfcs == {"RFC-0071", "RFC-0072", "RFC-0073"}
