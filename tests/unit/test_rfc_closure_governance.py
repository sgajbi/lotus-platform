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


def test_current_implementation_rfcs_include_second_last_and_final_closure_slices() -> None:
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
