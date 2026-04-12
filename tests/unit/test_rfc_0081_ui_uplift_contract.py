from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_rfc_0081_is_implementation_grade_and_has_final_slice() -> None:
    rfc = (
        ROOT / "rfcs" / "RFC-0081-lotus-workbench-ui-uplift-and-advisory-lifecycle-integration.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "# RFC-0081: Lotus Workbench UI Uplift and Advisory Lifecycle Integration",
        "## Decision",
        "## Enterprise-Grade Product Target State",
        "## Scope",
        "## Governed Source Of Truth",
        "## Architecture and Technology Review",
        "## Technical Decision Summary",
        "## Skills, Context, and Documentation Implications",
        "## Slice Review Governance",
        "### Slice 12: Documentation, Agent Context, Skill Alignment, and Branch Hygiene",
        "## Acceptance Criteria",
        "RFC-0076",
        "RFC-0077",
        "RFC-0078",
        "RFC-0079",
        "RFC-0080",
    ):
        assert required_item in rfc


def test_rfc_0081_bakes_visual_and_operating_patterns_into_the_contract() -> None:
    rfc = (
        ROOT / "rfcs" / "RFC-0081-lotus-workbench-ui-uplift-and-advisory-lifecycle-integration.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "## Visual and Interaction Patterns Derived From The References",
        "### Pattern 1: Entity-anchored shell header",
        "### Pattern 5: Decision rail and workflow rail",
        "### Pattern 8: Client artifact as product surface, not export button",
        "### Typography and font standards",
        "### Navigation and information architecture requirements",
        "### Codebase cleanup and dead-code expectations",
        "## Naming and Domain Language Standards",
        "## Frontend Topology and Code-Organization Standards",
        "## Agentic AI Product Readiness",
        "AI search and semantic discovery",
        "### Modern feature readiness requirements",
        "### Automation coverage requirements for new panels and screens",
        "### Caching and invalidation strategy",
        "cache lifecycle rules",
        "workspace and route usage frequency",
        "structured frontend event logging",
        "`Portfolio`",
        "`Performance`",
        "`Risk`",
        "`Proposal`",
        "`Advisory`",
        "AI-assisted",
    ):
        assert required_item in rfc


def test_rfc_0081_checklist_exists_and_matches_the_slice_model() -> None:
    checklist = (ROOT / "rfcs" / "RFC-0081-implementation-checklist.md").read_text(
        encoding="utf-8"
    )

    for required_item in (
        "# RFC-0081 Implementation Checklist",
        "## Slice 1: Current-State Assessment and UI Target Model",
        "## Slice 8: Micro-Frontend Composition and Extension Model",
        "## Slice 12: Documentation, Agent Context, Skill Alignment, and Branch Hygiene",
        "## Slice Review Gate",
    ):
        assert required_item in checklist

    for required_item in (
        "Define professional typography, sizing, and naming standards for the shell and shared UI layer.",
        "Define shell and navigation performance expectations.",
        "Define code-organization and file-structure standards for the modular UI topology.",
        "Define agentic AI extension standards for future workflow-native assist surfaces.",
        "Define architecture and UX standards for AI search and command-driven discovery surfaces.",
        "Define how new module routes and panels are incorporated into governed automation.",
        "Define caching, revalidation, and invalidation expectations aligned to gateway freshness metadata.",
        "Dead code and obsolete frontend patterns exposed by the uplift are removed.",
        "Banking-grade naming, typography, and code organization are standardized across the uplift.",
        "The shell and module model remain compatible with future agentic AI workflow surfaces.",
        "The shell and gateway model remain compatible with future AI search and modern discovery features.",
        "All new screens, panels, and workflow surfaces are represented in the governed automation and screenshot path.",
        "Front-office usage telemetry, logging, and tracing are sufficient to understand adoption, friction, and operational health.",
        "Caching and invalidation strategy improves speed without creating stale front-office workflow state.",
        "`lotus-workbench` is materially closer to an enterprise-grade front-office product platform, not just a visually improved UI.",
        "Review whether agent guidance must change once shell and module routing changes become real.",
    ):
        assert required_item in checklist


def test_rfc_0081_slice_1_evidence_exists_and_records_keep_replace_retire() -> None:
    evidence = (
        ROOT / "rfcs" / "RFC-0081-slice-1-current-state-assessment-and-target-model-evidence.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "# RFC-0081 Slice 1: Current-State Assessment and UI Target Model Evidence",
        "## Keep / replace / retire decisions",
        "### Keep",
        "### Replace",
        "### Retire",
        "## Review of slice 1",
        "Slice 1 is complete.",
    ):
        assert required_item in evidence


def test_rfc_0081_slice_2_evidence_exists_and_records_gateway_target_model() -> None:
    evidence = (
        ROOT / "rfcs" / "RFC-0081-slice-2-gateway-experience-contract-assessment-and-target-model-evidence.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "# RFC-0081 Slice 2: Gateway Experience-Contract Assessment and Target Model Evidence",
        "## Keep / replace / retire decisions",
        "## Target gateway experience-contract model confirmed by slice 2",
        "### 1. Shell bootstrap contract",
        "### 2. Workspace bootstrap contracts",
        "### 3. Workflow-truth contracts",
        "### 5. Cache and freshness model",
        "No immediate gateway guidance change is required before implementation begins.",
        "Slice 2 is complete.",
    ):
        assert required_item in evidence


def test_rfc_0081_slice_3_evidence_exists_and_records_shell_foundation_model() -> None:
    evidence = (
        ROOT / "rfcs" / "RFC-0081-slice-3-shell-navigation-and-design-system-foundation-evidence.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "# RFC-0081 Slice 3: Shell, Navigation, and Design-System Foundation Evidence",
        "## Keep / replace / retire decisions",
        "## Target shell and design-system foundation confirmed by slice 3",
        "### 1. Shell structure",
        "### 2. Navigation model",
        "### 3. Typography and token ownership",
        "### 5. Shell performance posture",
        "No immediate frontend skill or onboarding guidance update is required before implementation begins.",
        "Slice 3 is complete.",
    ):
        assert required_item in evidence


def test_rfc_0081_slice_4_evidence_exists_and_records_naming_topology_model() -> None:
    evidence = (
        ROOT / "rfcs" / "RFC-0081-slice-4-information-architecture-naming-and-typography-foundation-evidence.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "# RFC-0081 Slice 4: Shared Information Architecture, Naming, and Typography Foundation Evidence",
        "## Keep / replace / retire decisions",
        "## Target information architecture and naming model confirmed by slice 4",
        "### 1. Top-level shell vocabulary",
        "### 2. Route topology model",
        "### 3. Shared naming hierarchy",
        "### 5. Typography naming rule",
        "No immediate agent skill or onboarding guidance update is required before implementation begins.",
        "Slice 4 is complete.",
    ):
        assert required_item in evidence


def test_rfc_0081_slice_5_evidence_exists_and_records_gateway_hardening_model() -> None:
    evidence = (
        ROOT / "rfcs" / "RFC-0081-slice-5-gateway-composition-foundation-and-contract-hardening-evidence.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "# RFC-0081 Slice 5: Gateway Composition Foundation and Contract Hardening Evidence",
        "## Keep / replace / retire decisions",
        "## Target gateway composition model confirmed by slice 5",
        "### 1. Shell entry contract family",
        "### 2. Workspace bootstrap contract family",
        "### 4. Freshness and consistency model",
        "### 6. Caching, revalidation, and invalidation model",
        "No immediate agent skill or onboarding guidance update is required before implementation begins.",
        "Slice 5 is complete.",
    ):
        assert required_item in evidence


def test_rfc_0081_slice_6_evidence_exists_and_records_analytical_uplift_model() -> None:
    evidence = (
        ROOT / "rfcs" / "RFC-0081-slice-6-portfolio-performance-and-risk-surface-uplift-evidence.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "# RFC-0081 Slice 6: Portfolio, Performance, and Risk Surface Uplift Evidence",
        "## Keep / replace / retire decisions",
        "## Target analytical surface model confirmed by slice 6",
        "### 1. Portfolio workspace model",
        "### 2. Performance workspace model",
        "### 3. Risk workspace model",
        "### 5. Structural cleanup model",
        "No immediate panel-registry or runtime-guidance update is required before implementation begins.",
        "Slice 6 is complete.",
    ):
        assert required_item in evidence


def test_rfc_0081_slice_7_evidence_exists_and_records_proposal_workspace_model() -> None:
    evidence = (
        ROOT / "rfcs" / "RFC-0081-slice-7-advisory-and-proposal-workspace-integration-evidence.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "# RFC-0081 Slice 7: Advisory and Proposal Workspace Integration Evidence",
        "## Keep / replace / retire decisions",
        "## Target proposal and advisory workspace model confirmed by slice 7",
        "### 1. Proposal workspace model",
        "### 2. Advisory workspace model",
        "### 3. Workflow-truth model",
        "### 4. Artifact and consent model",
        "No immediate context or skill update is required before implementation begins.",
        "Slice 7 is complete.",
    ):
        assert required_item in evidence


def test_rfc_0081_slice_8_evidence_exists_and_records_module_extension_model() -> None:
    evidence = (
        ROOT / "rfcs" / "RFC-0081-slice-8-micro-frontend-composition-and-extension-model-evidence.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "# RFC-0081 Slice 8: Micro-Frontend Composition and Extension Model Evidence",
        "## Keep / replace / retire decisions",
        "## Target micro-frontend composition model confirmed by slice 8",
        "### 1. Shell-owned module registration model",
        "### 2. Module-boundary model",
        "### 3. Shared runtime and dependency model",
        "### 5. Automation and extension rule",
        "No immediate validator or onboarding guidance update is required before implementation begins.",
        "Slice 8 is complete.",
    ):
        assert required_item in evidence


def test_rfc_0081_slice_9_evidence_exists_and_records_ai_governance_model() -> None:
    evidence = (
        ROOT
        / "rfcs"
        / "RFC-0081-slice-9-ai-surface-governance-and-assistive-workflow-controls-evidence.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "# RFC-0081 Slice 9: AI Surface Governance and Assistive Workflow Controls Evidence",
        "## Keep / replace / retire decisions",
        "## Target AI governance model confirmed by slice 9",
        "### 1. AI disclosure model",
        "### 2. Human review and workflow separation model",
        "### 3. Feedback and quality loop model",
        "### 6. Retrieval and search governance linkage",
        "No immediate skill or onboarding guidance update is required before implementation begins.",
        "Slice 9 is complete.",
    ):
        assert required_item in evidence


def test_rfc_0081_slice_10_evidence_exists_and_records_ai_search_and_command_model() -> None:
    evidence = (
        ROOT
        / "rfcs"
        / "RFC-0081-slice-10-ai-search-command-surfaces-and-agentic-extension-model-evidence.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "# RFC-0081 Slice 10: AI Search, Command Surfaces, and Agentic Extension Model Evidence",
        "## Keep / replace / retire decisions",
        "## Target AI search and command model confirmed by slice 10",
        "### 1. Shell-owned discovery entry model",
        "### 2. Result-class model",
        "### 3. Search and assist separation model",
        "### 5. Command and search gateway model",
        "### 6. Automation and validation model",
        "No immediate skill or onboarding guidance update is required before implementation begins.",
        "Slice 10 is complete.",
    ):
        assert required_item in evidence


def test_rfc_0081_slice_11_evidence_exists_and_records_operability_model() -> None:
    evidence = (
        ROOT
        / "rfcs"
        / "RFC-0081-slice-11-performance-accessibility-and-operability-hardening-evidence.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "# RFC-0081 Slice 11: Performance, Accessibility, and Operability Hardening Evidence",
        "## Keep / replace / retire decisions",
        "## Target operability model confirmed by slice 11",
        "### 1. Performance-budget model",
        "### 2. Freshness and caching model",
        "### 3. Accessibility and keyboard-ergonomics model",
        "### 4. Observability and usage model",
        "### 6. Automation-coverage model",
        "No immediate skill or onboarding guidance update is required before implementation begins.",
        "Slice 11 is complete.",
    ):
        assert required_item in evidence


def test_rfc_0081_slice_12_evidence_exists_and_records_context_and_hygiene_posture() -> None:
    evidence = (
        ROOT
        / "rfcs"
        / "RFC-0081-slice-12-docs-context-skill-alignment-and-branch-hygiene-evidence.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "# RFC-0081 Slice 12: Documentation, Agent Context, Skill Alignment, and Branch Hygiene Evidence",
        "## Keep / replace / retire decisions",
        "## Documentation and context decision for this slice",
        "### 1. No immediate agent-context change is required before implementation begins",
        "### 2. Documentation updates must happen during implementation, not ahead of it",
        "### 3. Skills should only change when product routing changes materially",
        "### 4. Branch hygiene decision",
        "Slice 12 is complete.",
    ):
        assert required_item in evidence
