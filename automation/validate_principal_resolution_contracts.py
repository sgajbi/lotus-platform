"""Validate the resolved-principal contract and its denial and admission fixtures.

RFC-0109 slice 1: platform publishes the delegated-principal and grant-resolution
contracts with a fixture per denial class. The checks here exist because a
published contract proves nothing on its own -- a consumer needs the hostile
cases, and the hostile cases need to agree with the contract they claim to test.

Three properties are worth naming, because they are the ones a schema alone does
not give:

1. every denial class the contract declares has a fixture, and every fixture
   names a declared class. A class without a fixture is a rule no consumer is
   asked to prove;
2. each fixture refuses at the resolution step the contract says owns its class.
   A denial at a later step means an earlier control did not run, and the
   request reached further than the contract allows;
3. at least one admission fixture exists. A resolver that refuses everything
   satisfies all twelve denial fixtures, so denials alone cannot show the
   contract is implemented.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    from automation.json_contract_validation import validate_json_schema_subset
except ModuleNotFoundError:
    from json_contract_validation import validate_json_schema_subset


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = ROOT / "platform-contracts" / "principal-resolution"
EXAMPLES_DIR = CONTRACT_DIR / "examples"
CONTRACT_SCHEMA_PATH = CONTRACT_DIR / "resolved-principal.schema.json"
CONTRACT_PATH = CONTRACT_DIR / "resolved-principal.v1.json"
DENIAL_SCHEMA_PATH = CONTRACT_DIR / "denial-fixture.schema.json"
ADMISSION_SCHEMA_PATH = CONTRACT_DIR / "admission-fixture.schema.json"

# Every consumer must prove these, per RFC-0109. The list is duplicated here on
# purpose: if the contract drops a class, this check reports it rather than
# agreeing with the contract about a weaker set.
REQUIRED_DENIAL_CLASSES = {
    "missing_credential",
    "malformed_credential",
    "expired_credential",
    "wrong_audience",
    "wrong_issuer",
    "unknown_key_id",
    "revoked_principal",
    "tenant_not_a_member",
    "capability_not_granted",
    "portfolio_outside_scope",
    "delegated_capability_not_held_by_user",
    "grant_store_unavailable",
    # The class that passes every other fixture in this set. A consumer can
    # satisfy all the others by validating structure and resolving nothing; only
    # this one requires that the credential was actually verified.
    "present_but_unverified",
}

FORBIDDEN_EVIDENCE_FIELDS = {
    "access_token",
    "authorization",
    "cookie",
    "id_token",
    "raw_token",
    "refresh_token",
    "session_secret",
}


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} does not contain a JSON object")
    return payload


def _denial_fixture_paths() -> list[Path]:
    return sorted(EXAMPLES_DIR.glob("denial.*.json"))


def _admission_fixture_paths() -> list[Path]:
    return sorted(EXAMPLES_DIR.glob("admission.*.json"))


def _find_forbidden_fields(value: object, path: str = "fixture") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key.lower().replace("-", "_") in FORBIDDEN_EVIDENCE_FIELDS:
                found.append(f"{path}.{key}")
            found.extend(_find_forbidden_fields(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(_find_forbidden_fields(item, f"{path}[{index}]"))
    return found


def _declared_denial_classes(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    denials = contract.get("denials")
    if not isinstance(denials, dict):
        return {}
    classes = denials.get("classes")
    if not isinstance(classes, list):
        return {}
    return {
        entry["class"]: entry
        for entry in classes
        if isinstance(entry, dict) and isinstance(entry.get("class"), str)
    }


def _step_owning(contract: dict[str, Any], denial_class: str) -> int | None:
    """The resolution step whose fail-closed list names this class."""
    order = contract.get("resolutionOrder")
    if not isinstance(order, list):
        return None
    for entry in order:
        if not isinstance(entry, dict):
            continue
        closes = entry.get("failsClosedOn")
        if isinstance(closes, list) and denial_class in closes:
            step = entry.get("step")
            return step if isinstance(step, int) else None
    return None


def validate_contract_completeness(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    declared = set(_declared_denial_classes(contract))
    for missing in sorted(REQUIRED_DENIAL_CLASSES - declared):
        errors.append(f"contract declares no denial class {missing!r}")
    for extra in sorted(declared - REQUIRED_DENIAL_CLASSES):
        errors.append(
            f"contract declares denial class {extra!r}, which this validator does not require; "
            "add it to REQUIRED_DENIAL_CLASSES with its fixture, or remove it"
        )
    return errors


def validate_denial_fixtures(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    declared = _declared_denial_classes(contract)
    fixtures = _denial_fixture_paths()
    if not fixtures:
        return ["no denial fixtures found, so every consumer check below would pass on nothing"]

    seen: set[str] = set()
    for path in fixtures:
        errors.extend(
            f"{path.name}: {error}"
            for error in validate_json_schema_subset(DENIAL_SCHEMA_PATH, path)
        )
        fixture = _load(path)
        denial_class = fixture.get("denialClass")
        if not isinstance(denial_class, str):
            continue
        seen.add(denial_class)

        if denial_class not in declared:
            errors.append(
                f"{path.name}: denial class {denial_class!r} is not declared by the contract"
            )
            continue

        expected = fixture.get("expected")
        if not isinstance(expected, dict):
            continue

        declared_status = declared[denial_class].get("status")
        if expected.get("status") != declared_status:
            errors.append(
                f"{path.name}: refuses with {expected.get('status')!r} while the contract "
                f"declares {declared_status!r} for {denial_class!r}"
            )

        owning_step = _step_owning(contract, denial_class)
        if owning_step is None:
            errors.append(
                f"{path.name}: no resolution step fails closed on {denial_class!r}, so the "
                "contract does not say where this denial happens"
            )
        elif expected.get("failsAtStep") != owning_step:
            errors.append(
                f"{path.name}: refuses at step {expected.get('failsAtStep')!r} while the "
                f"contract makes step {owning_step} own {denial_class!r}; a later refusal "
                "means an earlier control did not run"
            )

        kind = fixture.get("principalKind")
        applies = declared[denial_class].get("appliesTo")
        if isinstance(applies, list) and isinstance(kind, str) and kind not in applies:
            errors.append(
                f"{path.name}: exercises principal kind {kind!r}, which the contract does not "
                f"list under {denial_class!r}"
            )

        errors.extend(f"{path.name}: forbidden field {field}" for field in _find_forbidden_fields(fixture))

    for missing in sorted(REQUIRED_DENIAL_CLASSES - seen):
        errors.append(f"no denial fixture for required class {missing!r}")
    return errors


def validate_admission_fixtures() -> list[str]:
    errors: list[str] = []
    fixtures = _admission_fixture_paths()
    if not fixtures:
        return [
            "no admission fixture found; a resolver that refuses every request satisfies every "
            "denial fixture, so denials alone cannot show this contract is implemented"
        ]

    for path in fixtures:
        errors.extend(
            f"{path.name}: {error}"
            for error in validate_json_schema_subset(ADMISSION_SCHEMA_PATH, path)
        )
        fixture = _load(path)
        errors.extend(
            f"{path.name}: forbidden field {field}" for field in _find_forbidden_fields(fixture)
        )
        errors.extend(f"{path.name}: {error}" for error in _validate_intersection(fixture))
    return errors


def _validate_intersection(fixture: dict[str, Any]) -> list[str]:
    """A delegated admission must resolve to the intersection, not to either side.

    Stating `effectivePermissions: intersection` in the contract and then
    publishing an example whose effective set exceeds one side would ship the
    widening this rule exists to forbid, as an approved example.
    """
    if fixture.get("principalKind") != "delegated":
        return []
    request = fixture.get("request")
    expected = fixture.get("expected")
    if not isinstance(request, dict) or not isinstance(expected, dict):
        return []
    resolved = expected.get("resolvedPrincipal")
    if not isinstance(resolved, dict):
        return []

    application = request.get("applicationCapabilities")
    user = request.get("userCapabilities")
    effective = resolved.get("effectiveCapabilities")
    if not all(isinstance(value, list) for value in (application, user, effective)):
        return ["a delegated admission must state application, user and effective capabilities"]

    intersection = set(application) & set(user)
    if set(effective) != intersection:
        return [
            f"effective capabilities {sorted(effective)} are not the intersection of the "
            f"application's {sorted(application)} and the user's {sorted(user)}, which is "
            f"{sorted(intersection)}"
        ]
    return []


def validate_principal_resolution_contracts() -> list[str]:
    errors: list[str] = []
    for path in (CONTRACT_SCHEMA_PATH, CONTRACT_PATH, DENIAL_SCHEMA_PATH, ADMISSION_SCHEMA_PATH):
        if not path.is_file():
            errors.append(f"missing required contract artifact: {path.relative_to(ROOT)}")
    if errors:
        return errors

    errors.extend(validate_json_schema_subset(CONTRACT_SCHEMA_PATH, CONTRACT_PATH))
    contract = _load(CONTRACT_PATH)
    errors.extend(validate_contract_completeness(contract))
    errors.extend(validate_denial_fixtures(contract))
    errors.extend(validate_admission_fixtures())
    return errors


def main() -> int:
    errors = validate_principal_resolution_contracts()
    if errors:
        print("Principal resolution contract validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        f"Principal resolution contracts validated: {len(_denial_fixture_paths())} denial "
        f"fixture(s), {len(_admission_fixture_paths())} admission fixture(s)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
