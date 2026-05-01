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
        "- status: first-wave scheduler/worker/gateway/workbench batch operation and scheduler administration implemented",
        "gold-pass hardened: 2026-04-26",
        "implementation started: 2026-04-26",
        "first-wave implementation proof completed: 2026-04-26",
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
        "implementation-backed batch materialization/status/control apis",
        "daemonized internal worker process",
        "daemonized internal scheduler process",
        "implementation status and evidence",
        "slices 0 through 7 plus the bounded run-once operator api, bounded runtime-pass,",
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
        "slice 4: dispatch, concurrency, back-pressure, and leases evidence",
        "slice 5: retry, pause, resume, cancel, and recovery evidence",
        "slice 8: documentation, runbook, and supportability floor evidence",
        "bounded internal single-batch worker run primitive",
        "sgajbi/lotus-report#70",
        "sgajbi/lotus-report#73",
        "sgajbi/lotus-report#74",
        "sgajbi/lotus-report#75",
        "sgajbi/lotus-report#76",
        "sgajbi/lotus-report#77",
        "sgajbi/lotus-report#78",
        "9deabddff47077d197cee8c659cd6cadce5a5b77",
        "gateway batch api exposes certified materialization/status/control/operator-run subset",
        "sgajbi/lotus-gateway#151",
        "sgajbi/lotus-gateway#152",
        "80232ba536c2bfff2760bae5dad70e1db35f18dc",
        "rbch_71903e99009b4eac87786b872a3a3307",
        "rjob_1aaca40b76b24a25aca25b6315be7e2d",
        "doc_415f47cfa5ee4d809c02b9802d5b2eab",
        "gateway scheduler administration lists and materializes due config-backed schedules",
        "a3612b964675ceab6b57798b2efce1cac4c1d1b1",
        "4834766d4e69ae3a1031dd09ec79277523e06abc",
        "rbch_e1a60d49cd1c4da5b2f3d965b761427c",
        "rjob_5cf6942f7afb4ea5ab3a7b2b7acf704c",
        "doc_e0cd40638ae84535ab18d2a43e65203f",
        "workbench gateway-backed batch operation materializes, statuses, and runs one explicit portfolio batch",
        "sgajbi/lotus-workbench#111",
        "19134f930e8efaab2454fe7eb93eb10930a367cf",
        "rbch_1408a522732f42f2b6e41fd229cad106",
        "rjob_bd4af9450b3e4461916adc5b4567137d",
        "doc_0a75c2af6ef74af5bd29d2867cdb33c8",
        "sgajbi/lotus-platform#210",
        "sgajbi/lotus-platform#211",
        "sgajbi/lotus-platform#215",
        "sgajbi/lotus-platform#216",
        "sgajbi/lotus-platform#217",
        "b312512cb2640018a825ac939d544fe4bf606095",
        "make test-coverage",
        "prevents a stuck docker build from occupying the pr merge gate indefinitely",
        "does not claim any rfc-0104 batch reporting supported feature",
        "documentation, wiki, and context impact",
        "branching and delivery expectations",
        "gold-pass readiness assessment",
        "second gold-pass additions",
        "final gold-pass assessment",
        "rbch_93e51832cec949138d2b7b76194acd69",
        "rjob_0aad4adaf9744c4bbc3fdb6ed564ea05",
        "doc_6529f8c0cf304d41868455c3554a88bb",
        "rbch_d2c627362ddf497d9c37487c0f0fc82d",
        "rjob_d3ab17b0f9d642a0b6913d5fd21ee49f",
        "doc_89b380fd820f4f9f962ff93ddc633edd",
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
        "verified no unresolved `todo`, `fixme`, `hack`, or `tbd` markers remain",
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


def test_rfc_0105_preserves_observability_operations_gold_pass_contract() -> None:
    text = _read(
        ROOT
        / "rfcs"
        / "RFC-0105-reporting-observability-operations-and-replay-tooling.md"
    )

    for expected in [
        "- status: implemented for first-wave scope",
        "gold-pass hardened: 2026-04-26",
        "rfc-0104 closure alignment: 2026-04-26",
        "critical review outcome",
        "gold-pass readiness assessment",
        "second gold-pass additions",
        "rfc-0104 closure alignment",
        "pre-implementation no-go gates",
        "mandatory data-protection proof",
        "slice exit discipline",
        "cross-rfc handoff rules",
        "locked first-wave decisions",
        "conditional decisions",
        "architecture direction",
        "required identifier contract",
        "observability and operations attribute inventory",
        "replay semantics",
        "slice 0: platform automation and scaffolding improvement",
        "slice 1: cleanup and structure",
        "slice 2: trace and structured logging",
        "slice 3: metrics, dashboards, alerts, and sla contracts",
        "slice 4: operator status and diagnostics apis",
        "slice 5: rerender from snapshot",
        "slice 6: regenerate from upstream data",
        "slice 7: replay failed jobs and batch items",
        "slice 8: stuck-state detection, recovery guidance, and sla monitoring",
        "slice 9: implementation proof",
        "second-last slice: hardening, review, and certification",
        "final slice: closure",
        "api certification requirements",
        "supported features governance",
        "evidence expectations",
        "implementation proof ledger",
        "final gold-pass assessment",
        "debt removed during the audit",
        "slice 2 trace and structured logging",
        "23dd048a3d2ee1f2dfc3fe4452b31953a8a93b4f",
        "f063bbc7541d72f85ddc2e8e8a12ed27efd0665d",
        "lotus-report/output/rfc-0105-live-evidence-20260428-165945",
        "lotus-report/output/rfc-0105-live-evidence-20260428-234551",
        "corr-rfc0105-3861407cce884357b0d9bf8461aa4fe2",
        "3861407cce884357b0d9bf8461aa4fe2",
        "rjob_ba42b5d2c4914cb5951b1a38ab767c65",
        "doc_0ec51648138642cdbd61e978a4649d59",
        "rasc_20260428t165956z",
        "corr-rfc0105-dff9bc7cc5a349a5bc80a4a39e463058",
        "dff9bc7cc5a349a5bc80a4a39e463058",
        "rjob_b9199ca7a9034926b5b43da27b918533",
        "doc_49d27942b1c341c381edda7349d476af",
        "rasc_20260428t234603z",
        "monthly-sg-global-bal-rfc0105-live",
        "corr-batch-scheduler-9-14b9f8d70ba6",
        "746234474cdfa25c95f08ca4796f893185b58b50",
        "ee835094e7bc0f407fe2afb002c90e0bccdbcd05",
        "proof exposed and fixed a production contract bug",
        "numbered per-call render/archive captures",
        "30-report-render-request-01..04.json",
        "scheduler-admin list/run-due observability",
        "scheduler-admin list/run-due over the config-backed scheduler source",
        "implemented for first-wave scope on 2026-04-28",
        "final assessment",
        "pre-existing published-wiki drift",
        "rfc-0106 remains the owner",
        "rfc-0107 remains the owner",
        "targeted replay/error coverage suite with `12 passed`",
        "combined coverage, docker build, and workflow lint all passed",
        "`get /reports/operations/attention` runs a deterministic source-backed scan over active durable report jobs",
        "`lotus_report_attention_events_last_count`",
        "97 passed, 29 skipped",
    ]:
        assert expected in text

    for expected in [
        "`lotus-report` owns reporting operation control",
        "`lotus-render` remains render execution owner",
        "`lotus-archive` owns archived document identity, retrieval, lifecycle, retention, legal hold",
        "identifier-only observability is the default",
        "rerender uses an existing immutable rfc-0101 snapshot",
        "regenerate creates a new data snapshot from upstream sources",
        "replay is an execution-control operation for failed or stuck work",
        "rerender, regenerate, replay, retry, and recovery must have separate command paths",
        "operator apis require certification, complete swagger, examples, safe errors",
        "live proof must follow a report from gateway/job creation through snapshot, render, archive",
        "first implementation wave must start with observability contracts/operator lookup before mutating",
        "gateway-facing scheduler administration for schedule listing and bounded due-schedule",
        "batch_schedule_run_correlation_id",
        "do not promote supported features until implementation-backed proof exists",
        "the next slice must not start until the current slice has a passing targeted validation set",
        "final role, entitlement, tenant, region, and document-access authorization to rfc-0106",
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


def test_rfc_0106_preserves_reporting_security_gold_pass_contract() -> None:
    text = _read(
        ROOT
        / "rfcs"
        / "RFC-0106-reporting-security-entitlements-and-region-tenant-segregation.md"
    )

    for expected in [
        "- status: gold-pass ready; implementation not started",
        "gold-pass hardened: 2026-04-26",
        "critical review outcome",
        "gold-pass readiness assessment",
        "second gold-pass additions",
        "pre-implementation no-go gates",
        "mandatory allow/deny evidence",
        "break-glass and privileged operator posture",
        "entitlement source-gap handling",
        "security slice exit discipline",
        "entitlement attribute inventory",
        "role and action matrix floor",
        "slice 0: platform automation and scaffolding improvement",
        "slice 1: cleanup and structure",
        "slice 2: caller context and entitlement contract",
        "slice 3: gateway and report enforcement",
        "slice 4: archive retrieval enforcement",
        "slice 5: service-to-service trust and sensitive data controls",
        "slice 6: api certification, swagger, and error contract",
        "slice 7: implementation proof",
        "second-last slice: hardening, review, and certification",
        "final slice: closure",
        "api certification requirements",
        "supported features governance",
        "evidence expectations",
        "implementation proof ledger",
        "final gold-pass assessment",
    ]:
        assert expected in text

    for expected in [
        "`lotus-gateway` is the product-facing authorization boundary",
        "`lotus-report` must independently enforce report request",
        "`lotus-render` must accept render work only from authorized service callers",
        "`lotus-archive` must independently enforce document metadata",
        "`lotus-workbench` consumes gateway-backed permissions only",
        "object storage is never exposed directly to workbench",
        "synthetic examples are mandatory in swagger, docs, tests, and wiki material",
        "security supported-features entries require positive and negative tests plus live proof",
        "cross-tenant, cross-region, cross-booking-center, unauthorized role, and unauthorized portfolio",
        "no-sensitive-content tests or review gates protect logs, metrics, traces, swagger, and docs",
        "denied responses must be product-safe",
        "break-glass access is not supported by default",
        "no implementation may silently substitute hardcoded user, tenant, region, booking-center, or role",
        "do not promote supported features until implementation-backed proof exists",
    ]:
        assert expected in text

    for expected in SECOND_LAST_TERMS:
        assert expected in text
    for expected in FINAL_SLICE_TERMS:
        assert expected in text

    assert text.index("slice 0: platform automation") < text.index(
        "slice 1: cleanup and structure"
    )
    assert text.index("slice 7: implementation proof") < text.index(
        "second-last slice: hardening"
    )
    assert text.index("second-last slice: hardening") < text.index(
        "final slice: closure"
    )


def test_rfc_0107_preserves_production_certification_gold_pass_contract() -> None:
    text = _read(
        ROOT / "rfcs" / "RFC-0107-enterprise-reporting-production-certification.md"
    )

    for expected in [
        "- status: gold-pass ready; implementation not started",
        "gold-pass hardened: 2026-04-26",
        "critical review outcome",
        "gold-pass readiness assessment",
        "second gold-pass additions",
        "pre-certification branch and pr gates",
        "live-stack evidence review requirements",
        "blocker classification",
        "clean-state and merge sequencing requirements",
        "entry criteria",
        "certification scenario matrix",
        "evidence pack contract",
        "architecture direction",
        "slice 0: platform automation and certification scaffolding improvement",
        "slice 1: cleanup and structure",
        "slice 2: certification harness and evidence pack",
        "slice 3: end-to-end functional certification",
        "slice 4: batch, replay, rerender, regenerate, and supersession certification",
        "slice 5: failure and recovery certification",
        "slice 6: security, segregation, audit, and observability certification",
        "slice 7: non-functional certification",
        "slice 8: documentation, wiki, context, supported-features, and release posture",
        "slice 9: implementation proof",
        "second-last slice: hardening, review, and certification",
        "final slice: closure",
        "api certification requirements",
        "supported features governance",
        "evidence expectations",
        "implementation proof ledger",
        "final gold-pass assessment",
    ]:
        assert expected in text

    for expected in [
        "rfc-0107 certifies the complete enterprise reporting platform",
        "missing capabilities must be blocked, excluded, or sent back to the owning rfc",
        "no production-ready claim from docs-only, mocked-only, or single happy-path proof",
        "certification uses real service apis and databases/object storage adapters",
        "evidence must name repo, branch, pr, commit, check, endpoint, and operational identifiers",
        "if a required upstream capability is missing, rfc-0107 must stop or narrow scope",
        "evidence-pack schema is test-protected",
        "unsupported operations are excluded rather than faked",
        "allow and deny paths are both proven",
        "thresholds are explicit before results are judged",
        "production certification must not proceed with unknown branch state",
        "the evidence must be reviewed critically",
        "p0/p1 blockers cannot be papered over by documentation",
        "before starting the next implementation rfc",
        "ci health must be checked after merge, not only before merge",
        "do not claim production readiness until certification evidence exists",
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


def test_rfc_0108_preserves_analytics_ui_observability_gold_pass_contract() -> None:
    text = _read(
        ROOT
        / "rfcs"
        / "RFC-0108-front-office-analytics-ui-observability-and-operational-posture.md"
    )

    for expected in [
        "- status: gold-pass current scope implemented; entitlement certification evidence partial",
        "front-office analytics ui observability",
        "interactive read/display flows",
        "browser to gateway to backend",
        "page load",
        "panel hydration",
        "api fan-out",
        "calculation freshness",
        "empty states",
        "degraded widgets",
        "user-visible stale data",
        "frontend/backend correlation",
        "no-sensitive-content controls",
        "client names",
        "portfolio ids",
        "holdings",
        "screen content",
        "advisor behavior",
        "entitlement failures",
        "pb_sg_global_bal_001",
        "critical review findings and gold-standard corrections",
        "requirement traceability",
        "dependency and ownership map",
        "delivery and branch hygiene expectations",
        "cross-slice acceptance criteria",
        "risk register",
        "slice 0: platform automation and scaffolding improvement",
        "slice 1: cleanup and structure",
        "slice 2: telemetry contract",
        "slice 3: browser-to-gateway trace and correlation propagation",
        "slice 4: gateway and analytics backend structured logging",
        "slice 5: metrics, dashboards, alerts, and freshness contracts",
        "slice 6: ui state and attention events",
        "slice 7: audit events for entitlement-relevant reads and privileged actions",
        "slice 8: canonical workbench implementation proof",
        "slice 9: rollout proof and expansion readiness",
        "second-last slice: hardening, review, and certification",
        "final slice: closure",
        "ecosystem completion slice 10: reopen governance and contract expansion",
        "ecosystem completion slice 11: platform automation, scaffolding, and ci enforcement",
        "ecosystem slice 15: dashboards, alerts, runbooks, and operator diagnostics",
        "ecosystem slice 16: ecosystem implementation proof",
        "ecosystem slice 17: ecosystem hardening, review, and certification",
        "platform.analytics.observability.ecosystem_hardening_certification",
        "slice 11 implementation evidence",
        "supported features governance",
        "implementation proof ledger",
        "not an extension of rfc-0105",
        "slice 0 is complete",
        "product telemetry, metrics, dashboards, alerts, attention events, audit events",
        "identify gaps in `lotus-platform` automation",
        "api certification pattern",
        "swagger quality",
        "health/liveness/readiness endpoints",
        "structured logging",
        "product-safe error handling",
        "test scaffolding",
        "ci defaults",
        "documentation scaffolding",
        "governance hooks",
        "remove dead code",
        "move long-lived operator or governance material to repo-local wiki source",
        "avoid duplicate documentation across repo docs and wiki source",
        "critically review the evidence",
        "iterate on implementation and evidence until the first-wave scope is genuinely gold standard",
        "verify platform governance and enterprise data mesh standards are met",
        "endpoints are grouped correctly",
        "every endpoint has clear what/when/how guidance",
        "full request and response examples exist",
        "every attribute has description, type, and example value",
        "ensure error handling is complete, correct, and properly tested",
        "consciously review whether skills, guidance, documentation, or agent context should be added",
        "`platform.scaffolding.analytics_ui_observability_baseline`",
        "artifact existence is not proof",
        "fix failures promptly",
        "`platform.analytics.observability.scaffold_ci_enforcement`",
    ]:
        assert expected in text

    for expected in SECOND_LAST_TERMS:
        assert expected in text
    for expected in FINAL_SLICE_TERMS:
        assert expected in text

    assert text.index("slice 0: platform automation") < text.index(
        "slice 1: cleanup and structure"
    )
    assert text.index("slice 1: cleanup and structure") < text.index(
        "slice 2: telemetry contract"
    )
    assert text.index("slice 2: telemetry contract") < text.index(
        "slice 3: browser-to-gateway"
    )
    assert text.index("slice 8: canonical workbench implementation proof") < text.index(
        "slice 9: rollout proof"
    )
    assert text.index("slice 9: rollout proof") < text.index(
        "second-last slice: hardening"
    )
    assert text.index("second-last slice: hardening") < text.index(
        "final slice: closure"
    )
    assert text.index("final slice: closure") < text.index(
        "ecosystem completion slice 10"
    )
    assert text.index("ecosystem completion slice 10") < text.index(
        "ecosystem completion slice 11"
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
