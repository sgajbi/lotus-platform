from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "automation" / "validate_bff_principal_session_contracts.py"
CONTRACT_DIR = ROOT / "platform-contracts" / "bff-principal-session"


def _validator():
    spec = importlib.util.spec_from_file_location(
        "bff_principal_session_validator", VALIDATOR_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _session_contract() -> dict:
    return json.loads(
        (CONTRACT_DIR / "examples" / "bff-principal-session.valid.json").read_text(
            encoding="utf-8"
        )
    )


def _certification_posture() -> dict:
    return json.loads(
        (CONTRACT_DIR / "certification-posture.v1.json").read_text(encoding="utf-8")
    )


def test_contract_family_accepts_governed_fixture_and_non_certifying_posture() -> None:
    assert _validator().validate_bff_principal_session_contracts() == []


def test_session_contract_rejects_production_claim_promotion() -> None:
    validator = _validator()
    contract = _session_contract()
    contract["posture"]["productionIdentityCertified"] = True
    contract["posture"]["supportedFeaturePromoted"] = True
    contract["posture"]["localDevFixtureNonCertifying"] = False

    errors = validator.validate_session_contract(contract)

    assert "posture.productionIdentityCertified must remain False" in errors
    assert "posture.supportedFeaturePromoted must remain False" in errors
    assert "posture.localDevFixtureNonCertifying must remain True" in errors


def test_session_contract_rejects_raw_identity_fields_and_weak_session_digest() -> None:
    validator = _validator()
    contract = _session_contract()
    contract["raw_token"] = "must-not-cross-contract-boundary"
    contract["validatedPrincipal"]["sessionIdSha256"] = "predictable"

    errors = validator.validate_session_contract(contract)

    assert "contract.raw_token is a forbidden raw identity field" in errors
    assert "validatedPrincipal.sessionIdSha256 must be a SHA-256 digest" in errors


def test_session_contract_requires_expiry_and_principal_capability_subset() -> None:
    validator = _validator()
    contract = _session_contract()
    contract["validatedPrincipal"]["expiresAtUtc"] = "2026-07-29T08:59:00Z"
    contract["routePolicy"]["requiredCapabilities"].append("idea.admin")

    errors = validator.validate_session_contract(contract)

    assert "validatedPrincipal authTimeUtc must be before expiresAtUtc" in errors
    assert any("missing ['idea.admin']" in error for error in errors)


def test_route_policy_rejects_ungoverned_or_duplicate_projected_headers() -> None:
    validator = _validator()
    contract = _session_contract()
    contract["routePolicy"]["projectedHeaders"].append(
        {
            "name": "X-General-Authority",
            "sourceClaim": "roles",
            "audience": "lotus-gateway",
        }
    )
    contract["routePolicy"]["projectedHeaders"].append(
        {
            "name": "X-Actor-Id",
            "sourceClaim": "subjectRef",
            "audience": "lotus-gateway",
        }
    )

    errors = validator.validate_session_contract(contract)

    assert "routePolicy projected header 'X-General-Authority' is not governed" in errors
    assert "routePolicy.projectedHeaders must not duplicate header names" in errors


def test_session_contract_requires_hostile_identity_failure_cases() -> None:
    validator = _validator()
    contract = _session_contract()
    contract["failureCases"] = ["missing_session"]
    contract["routePolicy"]["forbiddenBrowserAuthorityHeaders"] = ["Authorization"]

    errors = validator.validate_session_contract(contract)

    assert any("failureCases missing" in error for error in errors)
    assert any(
        "routePolicy.forbiddenBrowserAuthorityHeaders missing" in error
        for error in errors
    )


def test_published_schema_rejects_bad_issuer_and_extra_claims(tmp_path: Path) -> None:
    validator = _validator()
    contract = _session_contract()
    contract["sessionAuthority"]["trustedIssuer"] = "https://untrusted.example"
    contract["validatedPrincipal"]["raw_claims"] = {"role": "admin"}
    path = tmp_path / "bad-session.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    errors = validator.validate_example_against_schema(
        schema_path=validator.SESSION_SCHEMA_PATH,
        example_path=path,
    )

    assert any("trustedIssuer" in error and "does not match" in error for error in errors)
    assert any("raw_claims" in error for error in errors)


def test_certification_posture_rejects_evidence_free_completion() -> None:
    validator = _validator()
    posture = _certification_posture()
    posture["certificationStatus"] = "certified"
    posture["requiredControls"]["bank_identity_provider_selected_and_approved"] = True
    posture["authorityBoundary"]["browser_headers_may_assert_authority"] = True

    errors = validator.validate_certification_posture(posture)

    assert "certificationStatus must remain not_certified" in errors
    assert "requiredControls must all remain false before certification" in errors
    assert "authorityBoundary must keep all non-authority flags false" in errors
