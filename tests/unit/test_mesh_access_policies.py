from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "automation" / "validate_mesh_access_policies.py"
POLICY_DIRECTORY = ROOT / "platform-contracts" / "mesh-access"


def _load_validator_module():
    automation_path = str(ROOT / "automation")
    if automation_path not in sys.path:
        sys.path.insert(0, automation_path)
    spec = importlib.util.spec_from_file_location(
        "validate_mesh_access_policies_test", VALIDATOR_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_checked_in_mesh_access_policies_are_valid() -> None:
    validator = _load_validator_module()

    assert validator.validate_mesh_access_policies(POLICY_DIRECTORY) == []


def test_mesh_access_policy_validation_rejects_missing_required_product(
    tmp_path: Path,
) -> None:
    validator = _load_validator_module()
    for policy_path in POLICY_DIRECTORY.glob("*.access.v1.json"):
        if "lotus-advise" not in policy_path.name:
            (tmp_path / policy_path.name).write_text(
                policy_path.read_text(encoding="utf-8"),
                encoding="utf-8",
            )

    issues = validator.validate_mesh_access_policies(tmp_path)

    assert issues == [
        f"{tmp_path}: missing required mesh access policy for lotus-advise product lotus-advise:AdvisoryProposalLifecycleRecord:v1",
        f"{tmp_path}: missing required mesh access policy for lotus-advise product lotus-advise:AdvisoryProposalMemoEvidencePack:v1",
    ]


def test_mesh_access_policy_validation_requires_catalog_approved_consumer(
    tmp_path: Path,
) -> None:
    validator = _load_validator_module()
    policy_path = tmp_path / "bad.access.v1.json"
    policy = json.loads(
        (
            POLICY_DIRECTORY / "lotus-risk-risk-metrics-report.access.v1.json"
        ).read_text(encoding="utf-8")
    )
    policy["allowed_consumers"][0]["consumer_repository"] = "lotus-workbench"
    policy_path.write_text(json.dumps(policy), encoding="utf-8")

    issues = validator.validate_mesh_access_policies(
        policy_path,
        required_products={},
    )

    assert issues == [
        f"{policy_path}: allowed_consumers[0].consumer_repository must be lotus-gateway or approved by the product catalog"
    ]


def test_mesh_access_policy_validation_requires_consumer_scope_lists(
    tmp_path: Path,
) -> None:
    validator = _load_validator_module()
    policy_path = tmp_path / "bad-scope.access.v1.json"
    policy = json.loads(
        (
            POLICY_DIRECTORY / "lotus-risk-risk-metrics-report.access.v1.json"
        ).read_text(encoding="utf-8")
    )
    policy["allowed_consumers"][0]["tenant_scope"] = []
    policy["allowed_consumers"][0]["roles"] = ["advisor", ""]
    policy["allowed_consumers"][0]["use_cases"] = "analytics_review"
    policy_path.write_text(json.dumps(policy), encoding="utf-8")

    issues = validator.validate_mesh_access_policies(
        policy_path,
        required_products={},
    )

    assert issues == [
        f"{policy_path}: allowed_consumers[0].tenant_scope must be non-empty strings",
        f"{policy_path}: allowed_consumers[0].roles must be non-empty strings",
        f"{policy_path}: allowed_consumers[0].use_cases must be non-empty strings",
    ]


def test_access_posture_for_context_returns_usable_or_restricted() -> None:
    validator = _load_validator_module()
    policy = json.loads(
        (
            POLICY_DIRECTORY / "lotus-core-portfolio-state-snapshot.access.v1.json"
        ).read_text(encoding="utf-8")
    )

    allowed = validator.access_posture_for_context(
        policy=policy,
        consumer_repository="lotus-gateway",
        tenant_id="TENANT_PRIVATE_BANKING_DEMO",
        role="advisor",
        use_case="portfolio_evidence_review",
    )
    restricted = validator.access_posture_for_context(
        policy=policy,
        consumer_repository="lotus-gateway",
        tenant_id="OTHER_TENANT",
        role="advisor",
        use_case="portfolio_evidence_review",
    )

    assert allowed == {
        "access_state": "usable",
        "customer_visible_state": "usable",
        "operator_visible_state": "usable",
        "reason": "Access allowed by mesh access policy.",
    }
    assert restricted["access_state"] == "restricted"
    assert restricted["customer_visible_state"] == "requestable"
    assert restricted["operator_visible_state"] == "restricted_with_reason"
    assert "client-confidential holdings" in restricted["reason"]
