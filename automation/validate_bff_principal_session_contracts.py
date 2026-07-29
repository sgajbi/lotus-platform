from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from automation.json_contract_validation import validate_json_schema_subset
except ModuleNotFoundError:
    from json_contract_validation import validate_json_schema_subset


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = ROOT / "platform-contracts" / "bff-principal-session"
EXAMPLES_DIR = CONTRACT_DIR / "examples"
SESSION_SCHEMA_PATH = CONTRACT_DIR / "bff-principal-session.schema.json"
CERTIFICATION_SCHEMA_PATH = CONTRACT_DIR / "certification-posture.schema.json"
CERTIFICATION_PATH = CONTRACT_DIR / "certification-posture.v1.json"
SESSION_EXAMPLE_PATH = EXAMPLES_DIR / "bff-principal-session.valid.json"

SHA256 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_FIELD_NAMES = {
    "access_token",
    "authorization",
    "client_id",
    "cookie",
    "id_token",
    "jwt",
    "password",
    "raw_claims",
    "raw_token",
    "refresh_token",
    "session_secret",
    "token",
}
REQUIRED_FAILURE_CASES = {
    "missing_session",
    "malformed_session",
    "expired_session",
    "revoked_session",
    "wrong_audience",
    "wrong_issuer",
    "cross_tenant",
    "cross_portfolio",
    "capability_escalation",
    "browser_authority_header_override",
}
REQUIRED_FORBIDDEN_BROWSER_HEADERS = {
    "authorization",
    "cookie",
    "x-actor-id",
    "x-tenant-id",
    "x-roles",
    "x-capabilities",
    "x-portfolio-ids",
    "x-portfolio-scope",
    "x-service-identity",
}
ALLOWED_PROJECTED_HEADERS = {
    "X-Actor-Id",
    "X-Tenant-Id",
    "X-Region",
    "X-Capabilities",
    "X-Portfolio-Scope",
    "X-Correlation-Id",
}
REQUIRED_CERTIFICATION_CONTROLS = {
    "bank_identity_provider_selected_and_approved",
    "issuer_and_audience_contract_approved",
    "managed_key_discovery_and_rotation_live",
    "server_side_session_binding_implemented",
    "revocation_logout_and_expiry_verified",
    "workbench_gateway_consumer_contract_tests",
    "hostile_browser_header_override_proof",
    "tenant_and_portfolio_entitlement_denial_proof",
    "production_observability_and_audit_review",
    "mainline_ci_and_exact_main_evidence",
}


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must be a JSON object")
    return payload


def _utc(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        return datetime.fromisoformat(f"{value[:-1]}+00:00")
    except ValueError:
        return None


def _find_forbidden_fields(value: object, path: str = "payload") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = key.lower().replace("-", "_")
            if normalized in FORBIDDEN_FIELD_NAMES:
                errors.append(f"{path}.{key} is a forbidden raw identity field")
            errors.extend(_find_forbidden_fields(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_find_forbidden_fields(child, f"{path}[{index}]"))
    return errors


def validate_example_against_schema(
    *, schema_path: Path, example_path: Path
) -> list[str]:
    return validate_json_schema_subset(schema_path, example_path)


def validate_session_contract(contract: dict[str, Any]) -> list[str]:
    errors = _find_forbidden_fields(contract, "contract")
    _validate_header(contract, errors)
    _validate_posture(contract.get("posture"), errors)
    _validate_session_authority(contract.get("sessionAuthority"), errors)
    _validate_validated_principal(contract.get("validatedPrincipal"), errors)
    _validate_route_policy(
        contract.get("routePolicy"),
        contract.get("validatedPrincipal"),
        errors,
    )
    _validate_failure_cases(contract.get("failureCases"), errors)
    _validate_audit_safety(contract.get("auditSafety"), errors)
    return errors


def _validate_header(contract: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "schemaVersion": "lotus-platform.bff-principal-session.v1",
        "contractId": "lotus-platform-authenticated-bff-principal-session",
        "contractVersion": "1.0.0",
    }
    for field, value in expected.items():
        if contract.get(field) != value:
            errors.append(f"{field} must equal {value}")
    issue_refs = contract.get("issueRefs")
    if not isinstance(issue_refs, list) or not {
        "sgajbi/lotus-platform#563",
        "sgajbi/lotus-workbench#436",
        "sgajbi/lotus-idea#687",
    }.issubset(set(issue_refs)):
        errors.append("issueRefs must bind platform, Workbench, and Idea blockers")


def _validate_posture(posture: object, errors: list[str]) -> None:
    if not isinstance(posture, dict):
        errors.append("posture must be an object")
        return
    expected = {
        "evidenceClass": "source_contract",
        "idpIntegrationStatus": "external_not_configured",
        "productionIdentityCertified": False,
        "supportedFeaturePromoted": False,
        "localDevFixtureNonCertifying": True,
    }
    for field, value in expected.items():
        actual = posture.get(field)
        if isinstance(value, bool):
            invalid = actual is not value
        else:
            invalid = actual != value
        if invalid:
            errors.append(f"posture.{field} must remain {value!r}")


def _validate_session_authority(authority: object, errors: list[str]) -> None:
    if not isinstance(authority, dict):
        errors.append("sessionAuthority must be an object")
        return
    required_true = {
        "signatureVerificationRequired",
        "keyDiscoveryRequired",
        "expiryRequired",
        "revocationRequired",
        "replayProtectionRequired",
    }
    for field in required_true:
        if authority.get(field) is not True:
            errors.append(f"sessionAuthority.{field} must be true")
    if authority.get("rawTokenLoggingAllowed") is not False:
        errors.append("sessionAuthority.rawTokenLoggingAllowed must be false")
    if authority.get("tokenType") != "server_verified_session":
        errors.append("sessionAuthority.tokenType must be server_verified_session")


def _validate_validated_principal(principal: object, errors: list[str]) -> None:
    if not isinstance(principal, dict):
        errors.append("validatedPrincipal must be an object")
        return
    session_id = principal.get("sessionIdSha256")
    if not isinstance(session_id, str) or not SHA256.fullmatch(session_id):
        errors.append("validatedPrincipal.sessionIdSha256 must be a SHA-256 digest")
    auth_time = _utc(principal.get("authTimeUtc"))
    expires = _utc(principal.get("expiresAtUtc"))
    if auth_time is None or expires is None:
        errors.append("validatedPrincipal timestamps must be UTC date-times ending with Z")
    elif auth_time >= expires:
        errors.append("validatedPrincipal authTimeUtc must be before expiresAtUtc")
    for list_field in ("roles", "capabilities"):
        values = principal.get(list_field)
        if not isinstance(values, list) or not values:
            errors.append(f"validatedPrincipal.{list_field} must be a non-empty list")
        elif len(set(values)) != len(values):
            errors.append(f"validatedPrincipal.{list_field} must not contain duplicates")


def _validate_route_policy(
    route_policy: object,
    principal: object,
    errors: list[str],
) -> None:
    if not isinstance(route_policy, dict):
        errors.append("routePolicy must be an object")
        return
    projected_headers = route_policy.get("projectedHeaders")
    if not isinstance(projected_headers, list) or not projected_headers:
        errors.append("routePolicy.projectedHeaders must be a non-empty list")
    else:
        _validate_projected_headers(projected_headers, errors)
    forbidden_headers = route_policy.get("forbiddenBrowserAuthorityHeaders")
    if not isinstance(forbidden_headers, list):
        errors.append("routePolicy.forbiddenBrowserAuthorityHeaders must be a list")
    else:
        missing = REQUIRED_FORBIDDEN_BROWSER_HEADERS - {
            str(header).lower() for header in forbidden_headers
        }
        if missing:
            errors.append(
                "routePolicy.forbiddenBrowserAuthorityHeaders missing "
                f"{sorted(missing)}"
            )
    required_capabilities = route_policy.get("requiredCapabilities")
    if isinstance(required_capabilities, list) and isinstance(principal, dict):
        principal_capabilities = set(principal.get("capabilities", []))
        missing_capabilities = set(required_capabilities) - principal_capabilities
        if missing_capabilities:
            errors.append(
                "routePolicy.requiredCapabilities must be a subset of "
                f"validatedPrincipal.capabilities; missing {sorted(missing_capabilities)}"
            )


def _validate_projected_headers(
    projected_headers: list[object],
    errors: list[str],
) -> None:
    names: list[str] = []
    for index, item in enumerate(projected_headers):
        if not isinstance(item, dict):
            errors.append(f"routePolicy.projectedHeaders[{index}] must be an object")
            continue
        name = item.get("name")
        if name not in ALLOWED_PROJECTED_HEADERS:
            errors.append(f"routePolicy projected header {name!r} is not governed")
        names.append(str(name))
        if item.get("audience") != "lotus-gateway":
            errors.append("projected header audience must be lotus-gateway")
    if len(set(names)) != len(names):
        errors.append("routePolicy.projectedHeaders must not duplicate header names")


def _validate_failure_cases(failure_cases: object, errors: list[str]) -> None:
    if not isinstance(failure_cases, list):
        errors.append("failureCases must be a list")
        return
    missing = REQUIRED_FAILURE_CASES - set(failure_cases)
    if missing:
        errors.append(f"failureCases missing {sorted(missing)}")


def _validate_audit_safety(audit_safety: object, errors: list[str]) -> None:
    if not isinstance(audit_safety, dict):
        errors.append("auditSafety must be an object")
        return
    for field in (
        "rawClaimsPersisted",
        "rawTokenPersisted",
        "securityHeadersLogged",
        "businessIdentifiersInEvidence",
    ):
        if audit_safety.get(field) is not False:
            errors.append(f"auditSafety.{field} must be false")
    if audit_safety.get("productSafeDenialCode") != "AUTHENTICATED_PRINCIPAL_REQUIRED":
        errors.append("auditSafety.productSafeDenialCode must remain governed")


def validate_certification_posture(posture: dict[str, Any]) -> list[str]:
    errors = _find_forbidden_fields(posture, "certification")
    if posture.get("certificationStatus") != "not_certified":
        errors.append("certificationStatus must remain not_certified")
    for field in ("supportedFeaturePromoted", "productionIdentityCertified"):
        if posture.get(field) is not False:
            errors.append(f"{field} must remain false")
    controls = posture.get("requiredControls")
    if not isinstance(controls, dict):
        errors.append("requiredControls must be an object")
    elif set(controls) != REQUIRED_CERTIFICATION_CONTROLS:
        errors.append("requiredControls must contain exactly the governed controls")
    elif any(value is not False for value in controls.values()):
        errors.append("requiredControls must all remain false before certification")
    boundary = posture.get("authorityBoundary")
    if not isinstance(boundary, dict):
        errors.append("authorityBoundary must be an object")
    elif any(value is not False for value in boundary.values()):
        errors.append("authorityBoundary must keep all non-authority flags false")
    return errors


def validate_bff_principal_session_contracts() -> list[str]:
    errors = validate_example_against_schema(
        schema_path=SESSION_SCHEMA_PATH,
        example_path=SESSION_EXAMPLE_PATH,
    )
    errors.extend(
        validate_example_against_schema(
            schema_path=CERTIFICATION_SCHEMA_PATH,
            example_path=CERTIFICATION_PATH,
        )
    )
    errors.extend(validate_session_contract(_load(SESSION_EXAMPLE_PATH)))
    errors.extend(validate_certification_posture(_load(CERTIFICATION_PATH)))
    return errors


def main() -> int:
    errors = validate_bff_principal_session_contracts()
    if errors:
        print("BFF principal session contract validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("BFF principal session contracts validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
