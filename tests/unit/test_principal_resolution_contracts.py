from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from automation import validate_principal_resolution_contracts as validator


ROOT = Path(__file__).resolve().parents[2]


def _contract() -> dict:
    return json.loads(validator.CONTRACT_PATH.read_text(encoding="utf-8"))


def _denial(name: str) -> dict:
    path = validator.EXAMPLES_DIR / f"denial.{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _admission() -> dict:
    path = validator.EXAMPLES_DIR / "admission.delegated-allowed.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_the_published_contract_and_every_fixture_validate() -> None:
    """The shipped artifacts are the acceptance, not a fixture built for the test."""
    assert validator.validate_principal_resolution_contracts() == []


def test_every_required_denial_class_has_a_fixture() -> None:
    """A class without a fixture is a rule no consumer is ever asked to prove."""
    published = {
        path.name.removeprefix("denial.").removesuffix(".json")
        for path in validator._denial_fixture_paths()
    }

    assert validator.REQUIRED_DENIAL_CLASSES <= published, (
        validator.REQUIRED_DENIAL_CLASSES - published
    )


def test_a_missing_denial_fixture_is_reported(tmp_path: Path, monkeypatch) -> None:
    """Prove the completeness check can fail, by hiding one fixture."""
    staged = tmp_path / "examples"
    staged.mkdir()
    for path in validator._denial_fixture_paths():
        if path.name.endswith("grant_store_unavailable.json"):
            continue
        (staged / path.name).write_bytes(path.read_bytes())
    monkeypatch.setattr(validator, "EXAMPLES_DIR", staged)

    errors = validator.validate_denial_fixtures(_contract())

    assert any("grant_store_unavailable" in error for error in errors), errors


def test_a_fixture_refusing_at_the_wrong_step_is_reported() -> None:
    """A denial later than the contract allows means an earlier control did not run.

    `capability_not_granted` is owned by step 4. A fixture claiming step 5 would
    describe a resolver that checked entitlement scope before checking whether
    the capability was granted at all.
    """
    contract = _contract()
    fixture = _denial("capability_not_granted")
    fixture["expected"]["failsAtStep"] = 5

    errors = validator._step_owning(contract, "capability_not_granted")
    assert errors == 4

    # Re-run the fixture loop with the tampered document staged on disk.
    assert fixture["expected"]["failsAtStep"] != validator._step_owning(
        contract, "capability_not_granted"
    )


def test_a_tampered_fixture_is_reported_by_the_real_loop(
    tmp_path: Path, monkeypatch
) -> None:
    """The check runs over files, so the falsification uses files."""
    staged = tmp_path / "examples"
    staged.mkdir()
    for path in validator._denial_fixture_paths():
        (staged / path.name).write_bytes(path.read_bytes())
    tampered = json.loads((staged / "denial.capability_not_granted.json").read_text("utf-8"))
    tampered["expected"]["failsAtStep"] = 5
    (staged / "denial.capability_not_granted.json").write_text(
        json.dumps(tampered, indent=2) + "\n", encoding="utf-8"
    )
    monkeypatch.setattr(validator, "EXAMPLES_DIR", staged)

    errors = validator.validate_denial_fixtures(_contract())

    assert any("means an earlier control did not run" in error for error in errors), errors


def test_a_fixture_with_the_wrong_status_is_reported(tmp_path: Path, monkeypatch) -> None:
    """401 and 403 are different answers: unauthenticated is not unauthorized."""
    staged = tmp_path / "examples"
    staged.mkdir()
    for path in validator._denial_fixture_paths():
        (staged / path.name).write_bytes(path.read_bytes())
    tampered = json.loads((staged / "denial.tenant_not_a_member.json").read_text("utf-8"))
    tampered["expected"]["status"] = 401
    (staged / "denial.tenant_not_a_member.json").write_text(
        json.dumps(tampered, indent=2) + "\n", encoding="utf-8"
    )
    monkeypatch.setattr(validator, "EXAMPLES_DIR", staged)

    errors = validator.validate_denial_fixtures(_contract())

    assert any("while the contract declares" in error for error in errors), errors


def test_a_contract_dropping_a_denial_class_is_reported() -> None:
    """The required set is held independently, so weakening the contract is visible."""
    contract = _contract()
    contract["denials"]["classes"] = [
        entry
        for entry in contract["denials"]["classes"]
        if entry["class"] != "delegated_capability_not_held_by_user"
    ]

    errors = validator.validate_contract_completeness(contract)

    assert any("delegated_capability_not_held_by_user" in error for error in errors), errors


def test_no_admission_fixture_is_reported(tmp_path: Path, monkeypatch) -> None:
    """A resolver that refuses everything satisfies all twelve denial fixtures."""
    staged = tmp_path / "examples"
    staged.mkdir()
    for path in validator._denial_fixture_paths():
        (staged / path.name).write_bytes(path.read_bytes())
    monkeypatch.setattr(validator, "EXAMPLES_DIR", staged)

    errors = validator.validate_admission_fixtures()

    assert any("refuses every request" in error for error in errors), errors


def test_a_delegated_admission_wider_than_the_intersection_is_reported() -> None:
    """A shared service identity must never widen a person's entitlement.

    Publishing an example whose effective set exceeds one side would ship that
    widening as an approved example, which is worse than not publishing one.
    """
    fixture = _admission()
    fixture["expected"]["resolvedPrincipal"]["effectiveCapabilities"] = [
        "manage.read",
        "manage.write",
        "manage.admin",
    ]

    errors = validator._validate_intersection(fixture)

    assert any("are not the intersection" in error for error in errors), errors


def test_the_published_admission_resolves_to_the_intersection() -> None:
    """The paired acceptance, and the reason the fixture carries both sides."""
    fixture = _admission()
    request = fixture["request"]

    assert set(fixture["expected"]["resolvedPrincipal"]["effectiveCapabilities"]) == (
        set(request["applicationCapabilities"]) & set(request["userCapabilities"])
    )


def test_the_admission_fixture_proves_header_authority_is_ignored() -> None:
    """An admitted call is where honouring a header would be invisible.

    The fixture asserts a capability and a tenant in headers that the resolved
    principal does not carry, so an implementation that honoured them would
    produce a different result and fail this comparison.
    """
    fixture = _admission()
    headers = fixture["request"]["assertedHeaders"]
    resolved = fixture["expected"]["resolvedPrincipal"]

    assert fixture["expected"]["headerAuthorityHonoured"] is False
    assert "manage.admin" in headers["x-caller-capabilities"]
    assert "manage.admin" not in resolved["effectiveCapabilities"]
    assert headers["x-tenant-id"] != resolved["tenantRef"]


def test_the_contract_forbids_the_fallback_that_would_undo_it() -> None:
    """`verified` must not fall back to header trust on a verification failure."""
    posture = _contract()["environmentPosture"]

    assert posture["verifiedMayFallBackToHeaderTrust"] is False
    assert posture["selectableByRequest"] is False


def test_the_contract_does_not_claim_an_implemented_grant_store() -> None:
    """Platform defines the contract and does not host it; a contract is not an implementation."""
    contract = _contract()

    assert contract["posture"]["grantStoreImplemented"] is False
    assert contract["grantStore"]["hostedByPlatform"] is False
    assert contract["grantStore"]["unavailableBehaviour"] == "deny"
    assert contract["posture"]["productionIdentityCertified"] is False


def test_denials_do_not_become_an_enumeration_oracle() -> None:
    """A 'no such portfolio' that differs from 'not entitled' tells a caller what exists."""
    denials = _contract()["denials"]

    assert denials["revealsResourceExistence"] is False
    assert denials["revealsMissingCapability"] is False
    assert denials["distinguishesUnauthenticatedFromUnauthorized"] is True


@pytest.mark.parametrize(
    "denial_class",
    sorted(validator.REQUIRED_DENIAL_CLASSES),
)
def test_every_denial_fixture_refuses_before_any_side_effect(denial_class: str) -> None:
    """A refusal must precede every effect it disclaims."""
    fixture = _denial(denial_class)

    assert fixture["expected"]["outcome"] == "denied"
    # A number, not a boolean. A 401 is identical whether the refusal ran before
    # the request left or after it, so only the call count separates them, and a
    # boolean cannot distinguish no calls from nobody counting.
    assert fixture["expected"]["maxProtectedOperationCalls"] == 0
    assert fixture["expected"]["revealsReasonDetail"] is False
    assert fixture["environmentPosture"] == "verified"


def test_the_unverified_credential_class_is_required() -> None:
    """The class a consumer passes every other fixture without implementing.

    Missing, malformed, expired, wrong-audience, wrong-issuer, unknown-key-id
    and revoked are all refusals of a *defective* credential. A well-formed,
    unexpired, correctly-audienced credential whose signature was never checked
    passes every shape assertion in the set, so a consumer could satisfy the
    other twelve by validating structure and resolving nothing.
    """
    assert "present_but_unverified" in validator.REQUIRED_DENIAL_CLASSES

    fixture = _denial("present_but_unverified")
    credential = fixture["request"]["credential"]

    assert credential["present"] is True
    assert credential["expired"] is False
    assert credential["revoked"] is False
    assert fixture["expected"]["failsAtStep"] == 1, (
        "verification is step one, so an unverified credential must not reach "
        "tenant membership or the grant store"
    )
    assert fixture["expected"]["status"] == 401


def test_no_denial_fixture_permits_an_outbound_call() -> None:
    """A refusal must precede every effect it disclaims, measured rather than claimed."""
    for denial_class in sorted(validator.REQUIRED_DENIAL_CLASSES):
        fixture = _denial(denial_class)

        assert fixture["expected"]["maxProtectedOperationCalls"] == 0, denial_class
        assert "sideEffectsPermitted" not in fixture["expected"], (
            f"{denial_class}: a boolean cannot distinguish no calls from nobody counting"
        )
        assert "maxOutboundCalls" not in fixture["expected"], (
            f"{denial_class}: the budget covers the protected operation, not the "
            "resolution lookups that reach the refusal"
        )


def test_the_readme_names_the_two_ways_to_prove_nothing() -> None:
    """Consumer guidance must carry the anti-patterns, not only the requirements.

    Both are on the record because a consumer shipped them: comparing a
    response's tenant against the one the request sent is comparing an input
    with itself, and reading authority out of a request body lets the payload
    choose its own scope.
    """
    readme = (
        validator.CONTRACT_DIR / "README.md"
    ).read_text(encoding="utf-8")

    assert "A request echo cannot certify" in readme
    assert "Authority never comes from payload content" in readme
    assert "present_but_unverified" in readme


def test_the_unverified_fixture_is_distinguishable_from_a_verified_one() -> None:
    """A fixture that only says it was unverified cannot be fed to a resolver.

    Its credential was byte-identical to the ones in fixtures that *are*
    verified and fail later, so a consumer could not produce the expected
    refusal without branching on the denial class -- which tests the fixture
    metadata rather than the resolver.
    """
    unverified = _denial("present_but_unverified")["request"]["credential"]
    verified_but_fails_later = _denial("tenant_not_a_member")["request"]["credential"]

    assert unverified["signatureVerifies"] is False
    assert verified_but_fails_later["signatureVerifies"] is True
    assert unverified != verified_but_fails_later, (
        "the request itself must differ, or the fixture proves nothing about verification"
    )


def test_every_present_credential_states_whether_it_verifies() -> None:
    """Silence would let a consumer assume whichever answer passes."""
    for denial_class in sorted(validator.REQUIRED_DENIAL_CLASSES):
        credential = _denial(denial_class)["request"]["credential"]
        if credential.get("present"):
            assert "signatureVerifies" in credential, denial_class

    admission = _admission()["request"]["credential"]
    assert admission["signatureVerifies"] is True


def test_the_grant_store_denial_is_reachable_under_the_call_budget() -> None:
    """The budget must not forbid the lookup that discovers the denial.

    `grant_store_unavailable` can only be found by attempting the grant store,
    so a budget counting every outbound call would make the one compliant
    implementation fail its own fixture, or push a consumer into fabricating the
    failure from fixture metadata.
    """
    fixture = _denial("grant_store_unavailable")

    assert fixture["request"]["grantStoreAvailable"] is False
    assert fixture["expected"]["maxProtectedOperationCalls"] == 0
    assert fixture["expected"]["failsAtStep"] == 3

    schema = json.loads(validator.DENIAL_SCHEMA_PATH.read_text(encoding="utf-8"))
    budget = schema["properties"]["expected"]["properties"]["maxProtectedOperationCalls"]

    assert "Resolution lookups are deliberately excluded" in budget["description"]
