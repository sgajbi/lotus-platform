from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STANDARD_PATH = ROOT / "rfcs" / "RFC-GOVERNANCE-STANDARD.md"
README_PATH = ROOT / "rfcs" / "README.md"

CURRENT_IMPLEMENTATION_RFCS = [
    "RFC-0084-mesh-governance.md",
    "RFC-0085-gateway-governed-domain-product-publication-and-trust-contracts.md",
    "RFC-0086-repo-native-domain-product-onboarding-and-federated-rollout.md",
    "RFC-0087-live-trust-telemetry-and-certification-plane.md",
    "RFC-0088-self-serve-discovery-and-dependency-catalog.md",
    "RFC-0089-mesh-certification-merge-gate-and-operational-trust-enforcement.md",
    "RFC-0090-cross-repo-mesh-certification-pr-merge-gate.md",
]

NEXT_AGENT_RUNTIME_RFCS = [
    "RFC-0096-governed-multi-agent-delegation-model.md",
    "RFC-0097-task-flow-runtime-for-long-running-workflow-packs.md",
    "RFC-0098-per-pack-queue-and-concurrency-policy.md",
]

SECOND_LAST_TERMS = [
    "code review",
    "governance",
    "api certification",
]
FINAL_SLICE_TERMS = [
    "documentation",
    "agent context",
    "wiki",
    "skills",
    "branch hygiene",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").lower()


def test_rfc_readme_points_to_closure_governance_standard() -> None:
    readme = _read(README_PATH)

    assert "rfc-governance-standard.md" in readme
    assert "second-last" in readme
    assert "final slice" in readme
    assert "legacy rfcs" in readme


def test_next_agent_runtime_rfcs_are_ordered_and_closure_governed() -> None:
    readme = _read(README_PATH)
    wiki_index = _read(ROOT / "wiki" / "RFC-Index.md")
    reference_map = _read(ROOT / "context" / "CONTEXT-REFERENCE-MAP.md")

    previous_readme_position = -1
    previous_wiki_position = -1
    previous_reference_position = -1
    for rfc_name in NEXT_AGENT_RUNTIME_RFCS:
        rfc_id = rfc_name.split("-", 2)[0] + "-" + rfc_name.split("-", 2)[1]
        text = _read(ROOT / "rfcs" / rfc_name)

        if rfc_id == "RFC-0095":
            assert "- status: implemented" in text, rfc_name
        else:
            assert "- status: draft" in text, rfc_name
        assert "## implementation plan" in text, rfc_name
        assert "## acceptance criteria" in text, rfc_name
        assert "## initial priority" in text, rfc_name
        for expected in SECOND_LAST_TERMS:
            assert expected in text, f"{rfc_name} missing {expected}"
        for expected in FINAL_SLICE_TERMS:
            assert expected in text, f"{rfc_name} missing {expected}"

        readme_position = readme.index(rfc_name.lower())
        wiki_position = wiki_index.index(rfc_id.lower())
        reference_position = reference_map.index(rfc_id.lower())
        assert readme_position > previous_readme_position
        assert wiki_position > previous_wiki_position
        assert reference_position > previous_reference_position
        previous_readme_position = readme_position
        previous_wiki_position = wiki_position
        previous_reference_position = reference_position

    assert "recommended next implementation order" in readme
    assert "recommended next implementation order" in wiki_index
    assert "next draft implementation sequence" in reference_map


def test_rfc_0095_preserves_heartbeat_gold_standard_contract() -> None:
    text = _read(
        ROOT / "rfcs" / "RFC-0095-heartbeat-driven-monitoring-and-attention-surfacing.md"
    )

    for expected in [
        "source truth remains external",
        "deterministic evidence before notifications",
        "missing evidence is not green",
        "output/heartbeat/heartbeat-status.json",
        "output/heartbeat/heartbeat-status.md",
        "stable derived id",
        "deduplication_key",
        "source adapter contract",
        "read_status",
        "healthy",
        "degraded",
        "missing",
        "error",
        "configuration model",
        "read-only",
        "schema examples for healthy, warning, action-required, blocking, suppressed, and",
        "replacement-lineage, expired, superseded, and degraded states remain distinguishable",
        "suppression expiry cannot hide blocking evidence indefinitely",
        "github-runner compatibility",
        "record a conscious context and skills decision",
        "test plan",
        "implementation boundaries",
        "open implementation decisions",
        "advisory or becomes gate-affecting",
        "pre-implementation gold-standard review",
            "repo index and wiki index: updated",
            "central agent context: updated",
            "platform-automation-ops",
    ]:
        assert expected in text


def test_rfc_governance_standard_requires_closure_slices_and_skills_review() -> None:
    standard = _read(STANDARD_PATH)

    for expected in [
        "second-last slice",
        "api certification-pattern",
        "platform-governance conformance",
        "final slice",
        "agent context",
        "wiki updates",
        "skills and guidance assessment",
        "branch hygiene",
        "no-change decision",
        "legacy rfc posture",
    ]:
        assert expected in standard


def test_current_implementation_rfcs_include_second_last_and_final_closure_slices() -> (
    None
):
    for rfc_name in CURRENT_IMPLEMENTATION_RFCS:
        text = _read(ROOT / "rfcs" / rfc_name)

        assert "slice 7" in text, rfc_name
        assert "slice 8" in text, rfc_name
        for expected in SECOND_LAST_TERMS:
            assert expected in text, f"{rfc_name} missing {expected}"
        for expected in FINAL_SLICE_TERMS:
            assert expected in text, f"{rfc_name} missing {expected}"


def test_mesh_rfcs_are_marked_implemented_after_gateway_and_workbench_merge() -> None:
    for rfc_name in [
        "RFC-0085-gateway-governed-domain-product-publication-and-trust-contracts.md",
        "RFC-0087-live-trust-telemetry-and-certification-plane.md",
        "RFC-0088-self-serve-discovery-and-dependency-catalog.md",
        "RFC-0089-mesh-certification-merge-gate-and-operational-trust-enforcement.md",
    ]:
        text = (ROOT / "rfcs" / rfc_name).read_text(encoding="utf-8")

        assert "| Status | Implemented |" in text
        assert "pending merge" not in text.lower()
        assert "shared draft pr" not in text.lower()


def test_rfc_0089_preserves_concrete_mesh_certification_contract() -> None:
    text = _read(
        ROOT
        / "rfcs"
        / "RFC-0089-mesh-certification-merge-gate-and-operational-trust-enforcement.md"
    )

    for expected in [
        "lotus-core:portfoliostatesnapshot:v1",
        "lotus-performance:returnsseriesbundle:v1",
        "lotus-risk:riskmetricsreport:v1",
        "lotus-advise:advisoryproposallifecyclerecord:v1",
        "gate input contract",
        "operator status schema floor",
        "cross-repo boundary rules",
        "evidence required before marking implemented",
        "gateway_publication_drift",
        "workbench_consumption_drift",
    ]:
        assert expected in text


def test_rfc_0090_preserves_cross_repo_ci_enforcement_contract() -> None:
    text = _read(
        ROOT / "rfcs" / "RFC-0090-cross-repo-mesh-certification-pr-merge-gate.md"
    )

    for expected in [
        "repository checkout contract",
        "sgajbi/lotus-core",
        "sgajbi/lotus-performance",
        "sgajbi/lotus-risk",
        "sgajbi/lotus-advise",
        "sgajbi/lotus-gateway",
        "sgajbi/lotus-workbench",
        "branch override inputs",
        "artifact contract",
        "permissions and security contract",
        "failure semantics",
        "step summary contract",
        "--require-sibling-repos",
        "if: always()",
    ]:
        assert expected in text


def test_rfc_0091_preserves_enterprise_mesh_maturity_contract() -> None:
    text = _read(
        ROOT
        / "rfcs"
        / "RFC-0091-enterprise-data-mesh-maturity-and-production-readiness.md"
    )

    for expected in [
        "enterprise mesh maturity definition",
        "runtime telemetry emission and collection",
        "self-service product onboarding kit",
        "mesh slo policy",
        "access governance and entitled discovery",
        "certification history and customer evidence packs",
        "broader product rollout and lifecycle governance",
        "enterprise mesh certification gate",
        "implementation boundary",
        "done and not-done semantics",
        "ownership map",
        "implementation status and evidence",
        "| status | implemented |",
        "implemented on rfc-0091 branch; pr and merge hygiene pending",
        "automation/generate_domain_product_onboarding.py",
        "tests/unit/test_domain_product_onboarding_generator.py",
        "automation/collect_trust_telemetry.py",
        "tests/unit/test_trust_telemetry_collection.py",
        "platform-contracts/mesh-slo/",
        "automation/validate_mesh_slo_policies.py",
        "tests/unit/test_mesh_slo_policies.py",
        "platform-contracts/mesh-access/",
        "automation/validate_mesh_access_policies.py",
        "tests/unit/test_mesh_access_policies.py",
        "platform-contracts/mesh-evidence/",
        "automation/generate_mesh_evidence_pack.py",
        "tests/unit/test_mesh_evidence_pack.py",
        "lotus-report/contracts/domain-data-products/lotus-report-products.v1.json",
        "lotus-manage/contracts/domain-data-products/lotus-manage-products.v1.json",
        "enterprise-mesh-certification-status.json",
        "telemetry, slo, access, lifecycle, evidence, catalog, gateway, and workbench",
        "automation/mesh_maturity_scope.py",
        "tests/unit/test_mesh_maturity_scope.py",
        "slice 9 review result",
        "lotus-skill-routing-map.md",
        "generated/enterprise-mesh-maturity-matrix.json",
        "output/mesh-evidence-packs/<pack-id>/evidence-pack-manifest.json",
        "code review, api certification, and governance tightening",
        "documentation, agent context, wiki update, skills review, and branch hygiene",
        "lotus-gateway",
        "lotus-workbench",
        "platform-contracts/mesh-slo/",
        "platform-contracts/mesh-access/",
        "platform-contracts/mesh-evidence/",
        "customer-ready versus operator-only",
        "generate_enterprise_mesh_maturity_matrix.py --check",
        "static fixture fallback is explicit and cannot masquerade as live runtime evidence",
    ]:
        assert expected in text


def test_rfc_0092_preserves_production_mesh_operations_contract() -> None:
    text = _read(
        ROOT / "rfcs" / "RFC-0092-production-mesh-operations-and-escalation-control.md"
    )

    for expected in [
        "| status | implemented |",
        "production mesh operations",
        "enterprise-mesh-operating-report.json",
        "enterprise-mesh-operating-report.md",
        "production_ready_limited_history",
        "regression since previous",
        "escalation queue",
        "owner repository",
        "product operating posture",
        "code review, api certification, and governance tightening",
        "documentation, agent context, wiki, skills, and branch hygiene",
        "no new dedicated mesh-operations skill",
        "automation/generate_enterprise_mesh_operating_report.py",
        "tests/unit/test_enterprise_mesh_operating_report.py",
    ]:
        assert expected in text
