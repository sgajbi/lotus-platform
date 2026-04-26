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
    "RFC-0098-per-pack-queue-and-concurrency-policy.md",
]

NEXT_AGENT_RUNTIME_RFC_STATUS = {
    "RFC-0098": "- status: implemented",
}

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

        expected_status = NEXT_AGENT_RUNTIME_RFC_STATUS.get(rfc_id, "- status: draft")
        assert expected_status in text, rfc_name
        assert "## implementation plan" in text, rfc_name
        assert "## acceptance criteria" in text, rfc_name
        assert "## initial priority" in text or "## current priority" in text, rfc_name
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


def test_rfc_0096_preserves_delegation_gold_standard_contract() -> None:
    text = _read(
        ROOT / "rfcs" / "RFC-0096-governed-multi-agent-delegation-model.md"
    )

    for expected in [
        "- status: implemented",
        "one accountable owner",
        "disjoint write scopes",
        "delegation output is not review",
        "lost delegated work is a finding",
        "delegation profiles",
        "`exploration`",
        "`implementation`",
        "`validation`",
        "`review_support`",
        "`documentation`",
        "`ci_triage`",
        "disallowed profiles",
        "delegation eligibility rules",
        "required delegation input envelope",
        "`delegation_task_id`",
        "`read_scope`",
        "`write_scope`",
        "`forbidden_actions`",
        "required delegation output envelope",
        "confirmation that unrelated work was not reverted",
        "task ledger integration",
        "`lost`",
        "`superseded`",
        "conflict and integration rules",
        "heartbeat integration",
        "engineering_task_id",
        "parent_engineering_task_id",
        "machine-readable contract boundary",
        "companion delegation policy contract",
        "slice 6: code review, api certification, and governance tightening",
        "slice 7: documentation, context, wiki, skills, and branch hygiene",
        "api certification posture is explicit",
        "implementation boundaries",
        "open implementation decisions",
        "resolved implementation decisions",
        "implementation status and evidence",
        "delegation policy contract and governed examples",
        "rfc-0094-compatible delegated task ledger helper",
        "optional rfc-0095 heartbeat source adapter",
        "openapi certification is not applicable",
        "artifact certification is applicable",
        "pre-implementation gold-standard review",
        "central agent context: no change yet because behavior is not implemented",
        "skills: no change yet because delegation guidance should be updated with the implementation",
        "wiki: no publication required for this tightening",
    ]:
        assert expected in text


def test_rfc_0097_preserves_task_flow_gold_standard_contract() -> None:
    text = _read(
        ROOT / "rfcs" / "RFC-0097-task-flow-runtime-for-long-running-workflow-packs.md"
    )

    for expected in [
        "- status: implemented",
        "## supported features",
        "source truth stays layered",
        "flow state, run state, and review state remain separate",
        "checkpoint evidence is durable",
        "replacement lineage is explicit",
        "bounded transitions only",
        "domain handoff is explicit",
        "degraded is not green",
        "minimum contract fields",
        "`task_flow_id`",
        "`workflow_pack_id`",
        "`run_refs`",
        "`review_refs`",
        "`replacement_lineage`",
        "transition rules",
        "cross-repo boundary rules",
        "`lotus-ai` owns task-flow contracts",
        "`lotus-gateway` owns external api shape",
        "`lotus-workbench` consumes gateway/bff apis only",
        "api certification pattern",
        "openapi schema and example accuracy",
        "heartbeat and operational attention",
        "stale active flows",
        "replacement-lineage inconsistencies",
        "slice 7: cleanup, structure, and documentation shape",
        "slice 8: code review, api certification, and governance tightening",
        "slice 9: documentation, context, wiki, supported features, skills, and branch hygiene",
        "required final-slice decisions",
        "implementation boundaries",
        "resolved for first-wave implementation closure",
        "pre-implementation gold-standard review",
        "task-flow-specific skill assessment: no new skill is needed yet",
        "repo wikis for `lotus-platform`, `lotus-ai`, `lotus-gateway`, and `lotus-workbench` were",
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


def test_rfc_0103_records_supported_scope_closure_and_deferrals() -> None:
    text = _read(
        ROOT
        / "rfcs"
        / "RFC-0103-document-archive-retrieval-retention-and-legal-hold.md"
    )

    for expected in [
        "- status: implemented for supported scope",
        "- implemented: 2026-04-25",
        "critical review outcome",
        "gold-pass readiness assessment",
        "implementation evidence and closure",
        "post-implementation slice audit",
        "gold-pass assessment",
        "locked first-wave decisions",
        "conditional decisions",
        "implementation prerequisites",
        "cross-rfc ownership boundaries",
        "document metadata contract",
        "source and evidence mapping",
        "api direction",
        "error handling requirements",
        "retention, purge, and legal hold direction",
        "access audit direction",
        "platform governance and enterprise data mesh requirements",
        "branching and delivery expectations",
        "slice 0: platform automation and scaffolding improvement",
        "slice 1: cleanup and structure",
        "slice 9: implementation proof",
        "second-last slice: hardening, review, and certification",
        "final slice: closure",
        "supported features",
        "started with no implementation-backed archive supported features",
        "supported-features entries must name",
        "documentation, wiki, and context impact",
        "resolved or deferred questions",
    ]:
        assert expected in text

    for expected in [
        "`lotus-archive` is a separate governable service/repository",
        "archive metadata is stored in postgresql",
        "document binaries are stored through an s3-compatible object-storage abstraction",
        "object storage is never directly exposed to workbench",
        "legal hold blocks purge regardless of retention eligibility",
        "signed url versus service-streamed download",
        "exact first-wave retention classes",
        "whether workbench document retrieval is shipped in rfc-0103 or deferred",
        "`lotus-report` hands successful rendered pdf artifacts to `lotus-archive`",
        "`lotus-gateway` exposes the product-facing archived document metadata and download facade",
        "workbench retrieval remains deliberately unsupported",
        "material issue found in\nthis audit was documentation drift",
        "service runbook now states report handoff and gateway retrieval are supported",
        "documentation-posture tests now guard those exact claims",
        "no placeholder mesh product was added for",
    ]:
        assert expected in text

    for expected in SECOND_LAST_TERMS:
        assert expected in text
    for expected in FINAL_SLICE_TERMS:
        assert expected in text

    assert text.index("slice 0: platform automation") < text.index(
        "slice 1: cleanup and structure"
    )
    assert text.index("slice 9: implementation proof") < text.index(
        "second-last slice: hardening"
    )
    assert text.index("second-last slice: hardening") < text.index(
        "final slice: closure"
    )


def test_rfc_0104_preserves_batch_reporting_gold_standard_contract() -> None:
    text = _read(
        ROOT
        / "rfcs"
        / "RFC-0104-batch-reporting-scheduler-concurrency-and-recovery.md"
    )

    for expected in [
        "- status: in progress",
        "gold-pass hardened: 2026-04-26",
        "implementation started: 2026-04-26",
        "critical review outcome",
        "locked first-wave decisions",
        "conditional decisions",
        "pre-implementation execution decisions",
        "architecture direction",
        "batch selectors",
        "selector source mapping",
        "state model",
        "data contract floor",
        "idempotency and duplicate prevention",
        "concurrency, back-pressure, and leases",
        "non-negotiable invariants",
        "storage and migration direction",
        "api direction",
        "swagger and api certification requirements",
        "platform governance and mesh requirements",
        "requirement traceability matrix",
        "error handling requirements",
        "observability floor",
        "slice 0: platform automation and scaffolding improvement",
        "slice 1: cleanup and structure",
        "slice 2: batch ledger, selectors, and idempotent materialization",
        "slice 3: scheduling and frequency materialization",
        "slice 4: dispatch, concurrency, back-pressure, and leases",
        "slice 5: retry, pause, resume, cancel, and recovery",
        "slice 6: apis, swagger, and certification",
        "slice 7: integration with report, render, and archive",
        "slice 8: documentation, runbook, and supportability floor",
        "slice 9: implementation proof",
        "second-last slice: hardening, review, and certification",
        "final slice: closure",
        "supported features",
        "currently has no implementation-backed batch reporting supported features",
        "implementation status and evidence",
        "slices 0, 1, 2, and 3 are implemented and merged",
        "generated openapi quality gate now checks every generated operation",
        "src/app/report_batch_orchestrator/",
        "batch_runtime_supported = false",
        "sgajbi/lotus-report#67",
        "ea2df53c6a0fd29b9dfdaf2647ef4209dfcdb023",
        "migrations/007_report_batch_ledger.sql",
        "docs/standards/batch-orchestration-source-map.md",
        "sgajbi/lotus-report#68",
        "f6587fc8bc1f58ea5cc812553817cc4fe5d7c428",
        "slice 3: scheduling and frequency materialization evidence",
        "src/app/report_batch_orchestrator/schedule.py",
        "batchcyclerequest",
        "scheduled idempotency identity",
        "sgajbi/lotus-report#69",
        "28c43e8",
        "4062d0e",
        "make test-coverage",
        "prevents a stuck docker build from occupying the pr merge gate indefinitely",
        "does not claim any rfc-0104 batch reporting supported feature",
        "documentation, wiki, and context impact",
        "branching and delivery expectations",
        "gold-pass readiness assessment",
        "second gold-pass additions",
    ]:
        assert expected in text

    for expected in [
        "`lotus-report` owns the batch control plane",
        "batch execution creates or references one durable `report_job` per batch item",
        "`lotus-render` remains the deterministic render owner",
        "`lotus-archive` remains the generated-document archive owner",
        "object storage is not exposed directly through batch apis",
        "retry and recovery must be item-level, not whole-batch blind reruns",
        "batch status is derived from durable item and job state",
        "broad replay, rerender, regenerate, and stuck-job command center tooling owned by rfc-0105",
        "final reporting entitlement and region/tenant segregation certification owned by rfc-0106",
        "final end-to-end production certification owned by rfc-0107",
        "every attribute described with type, meaning, allowed values, and example value",
        "full error examples for invalid selector, duplicate item, unsupported frequency",
        "if no wiki, context, or skills change is needed",
        "implementation begins only after the rfc is approved for execution",
        "if a source contract is missing, the rfc implementation must record a source gap",
        "any implementation that cannot populate one of these fields must document whether the field is",
        "aggregate batch counts must reconcile exactly with item states",
        "no implementation may depend on in-memory state for correctness",
        "implementation closure must update this matrix with concrete evidence paths",
        "`tbd` entries are acceptable while rfc-0104 is in progress",
    ]:
        assert expected in text

    for expected in SECOND_LAST_TERMS:
        assert expected in text
    for expected in FINAL_SLICE_TERMS:
        assert expected in text

    assert text.index("slice 0: platform automation") < text.index(
        "slice 1: cleanup and structure"
    )
    assert text.index("slice 9: implementation proof") < text.index(
        "second-last slice: hardening"
    )
    assert text.index("second-last slice: hardening") < text.index(
        "final slice: closure"
    )


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
