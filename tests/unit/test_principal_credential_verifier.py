from __future__ import annotations

import base64
import ast
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from automation import generate_principal_credential_vectors as generator
from automation.verify_principal_credential import (
    Denial,
    GrantSet,
    GrantStoreUnavailable,
    ResolvedPrincipal,
    VerificationInputs,
    resolve_principal,
    verify_credential,
)

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "platform-contracts" / "principal-credential" / "examples"


def _jwks() -> dict:
    return json.loads((EXAMPLES / "jwks.json").read_text(encoding="utf-8"))


def _vector(name: str) -> dict:
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


def _inputs_for(vector: dict, **overrides) -> VerificationInputs:
    supplied = vector["verification_inputs"]
    defaults = dict(
        expected_issuer=supplied["expected_issuer"],
        expected_audience=supplied["expected_audience"],
        jwks=_jwks(),
        now=datetime.fromisoformat(supplied["evaluate_at"].replace("Z", "+00:00")),
        revoked_credential_ids=frozenset(supplied["revoked_credential_ids"]),
        revoked_subjects=frozenset(supplied["revoked_subjects"]),
    )
    defaults.update(overrides)
    defaults.setdefault("revocation_valid_until", defaults["now"] + timedelta(seconds=120))
    defaults.setdefault("authority_valid_until", defaults["now"] + timedelta(seconds=120))
    return VerificationInputs(**defaults)


def _outcome(vector: dict, **overrides) -> str:
    result = verify_credential(vector["credential"], _inputs_for(vector, **overrides))
    return result.denial_class if isinstance(result, Denial) else "verified"


VECTOR_NAMES = sorted(
    path.name for path in EXAMPLES.glob("*.json") if path.name != "jwks.json"
)


def test_every_published_vector_is_exercised() -> None:
    """Guards the parametrised test below against silently covering nothing.

    A glob that matched no files would make every vector case pass by vacuum, and
    an empty run is the same green as a complete one.
    """
    assert len(VECTOR_NAMES) == 13


@pytest.mark.parametrize("name", VECTOR_NAMES)
def test_each_vector_produces_its_published_outcome(name: str) -> None:
    vector = _vector(name)

    assert _outcome(vector) == vector["expected_outcome"]


def test_a_structure_only_inspector_accepts_the_unverified_credential() -> None:
    """This is what the signature-free fixture set could not catch.

    The credential is well-formed, correctly issued and audienced, and unexpired.
    Every assertion a consumer can make without keys passes, so a resolver that
    inspects rather than verifies admits it. That is precisely the implementation
    this vector exists to separate out.
    """
    vector = _vector("denial.present_but_unverified.json")
    header, payload, signature = vector["credential"].split(".")
    claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    supplied = vector["verification_inputs"]
    evaluated_at = int(
        datetime.fromisoformat(supplied["evaluate_at"].replace("Z", "+00:00")).timestamp()
    )

    structurally_acceptable = (
        bool(header and payload and signature)
        and claims["iss"] == supplied["expected_issuer"]
        and claims["aud"] == supplied["expected_audience"]
        and claims["exp"] > evaluated_at
    )

    assert structurally_acceptable
    assert _outcome(vector) == "present_but_unverified"


def test_the_same_bytes_verify_when_the_foreign_key_is_trusted() -> None:
    """The refusal is about the key, not about malformed or expired content.

    Without this, `present_but_unverified` could be produced by any defect in the
    payload and the vector would prove nothing about signature checking.
    """
    vector = _vector("denial.present_but_unverified.json")
    foreign = Ed25519PrivateKey.from_private_bytes(generator.FOREIGN_SEED)
    widened = {
        "keys": [
            {
                "kty": "OKP",
                "crv": "Ed25519",
                "alg": "EdDSA",
                "kid": generator.TRUSTED_KEY_ID,
                "x": base64.urlsafe_b64encode(
                    foreign.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
                )
                .decode()
                .rstrip("="),
            }
        ]
    }

    assert _outcome(vector, jwks=widened) == "verified"


def test_one_flipped_signature_byte_is_refused() -> None:
    vector = _vector("valid.user.json")
    header, payload, signature = vector["credential"].split(".")
    raw = bytearray(base64.urlsafe_b64decode(signature + "=" * (-len(signature) % 4)))
    raw[0] ^= 0x01
    tampered = f"{header}.{payload}." + base64.urlsafe_b64encode(bytes(raw)).decode().rstrip("=")

    result = verify_credential(tampered, _inputs_for(vector))

    assert isinstance(result, Denial)
    assert result.denial_class == "present_but_unverified"


def test_an_unverifiable_credential_is_refused_before_its_claims_are_read() -> None:
    """Order is the security property, not a preference.

    This credential is both unsigned-by-us and expired. Reporting `expired` would
    mean the verifier had believed an expiry nobody signed; a forged credential
    could then be refused for a reason its own payload chose.
    """
    vector = _vector("denial.present_but_unverified.json")
    long_after_expiry = datetime(2030, 1, 1, tzinfo=timezone.utc)

    assert _outcome(vector, now=long_after_expiry) == "present_but_unverified"


def test_regenerating_the_vectors_reproduces_the_committed_bytes() -> None:
    """Ed25519 is deterministic, so drift here means the contract moved.

    Without this, a committed vector could stop matching the generator and the
    published bytes would quietly become unreproducible.
    """
    for name, payload in generator.build().items():
        committed = json.loads((EXAMPLES / name).read_text(encoding="utf-8"))
        assert committed == payload, name


def test_no_private_key_material_is_committed() -> None:
    """The repository publishes public keys and signatures only."""
    for path in EXAMPLES.glob("*.json"):
        body = path.read_text(encoding="utf-8")
        assert "PRIVATE KEY" not in body
        assert '"d"' not in body


# --- resolution: the five refusals -------------------------------------------

MEMBER = lambda subject, tenant: True  # noqa: E731
NON_MEMBER = lambda subject, tenant: False  # noqa: E731


def _resolution_inputs(vector: dict, **overrides) -> VerificationInputs:
    defaults = dict(
        tenant_members=MEMBER,
        grants_for=lambda subject, tenant: GrantSet(
            frozenset({"portfolio.read"}), frozenset({"PB_SG_GLOBAL_BAL_001"})
        ),
        application_grants_for=lambda actor, tenant: GrantSet(
            frozenset({"portfolio.read"}), frozenset({"PB_SG_GLOBAL_BAL_001"})
        ),
        required_capabilities=("portfolio.read",),
        requested_portfolios=("PB_SG_GLOBAL_BAL_001",),
    )
    defaults.update(overrides)
    return _inputs_for(vector, **defaults)


def test_a_delegated_credential_resolves_to_the_intersection() -> None:
    vector = _vector("valid.delegated.json")

    resolved = resolve_principal(vector["credential"], _resolution_inputs(vector))

    assert isinstance(resolved, ResolvedPrincipal)
    assert resolved.principal_kind == "delegated"
    assert resolved.delegated_actor == "service:lotus-workbench"
    assert resolved.capabilities == ("portfolio.read",)


def test_a_capability_the_application_holds_but_the_person_does_not_is_refused() -> None:
    """Rule 3. A shared service identity never widens a person's entitlement."""
    vector = _vector("valid.delegated.json")

    result = resolve_principal(
        vector["credential"],
        _resolution_inputs(
            vector,
            grants_for=lambda subject, tenant: GrantSet(frozenset(), frozenset()),
        ),
    )

    assert isinstance(result, Denial)
    assert result.denial_class == "delegated_capability_not_held_by_user"


def test_a_capability_not_granted_to_the_person_is_refused() -> None:
    """Rule 4. The route's required capability is intersected with the grant set,
    and a user credential holding only `portfolio.read` cannot satisfy a write."""
    vector = _vector("valid.user.json")

    result = resolve_principal(
        vector["credential"],
        _resolution_inputs(vector, required_capabilities=("portfolio.write",)),
    )

    assert isinstance(result, Denial)
    assert result.denial_class == "capability_not_granted"
    assert result.unauthenticated is False


def test_an_unavailable_grant_store_denies_rather_than_returning_nothing() -> None:
    """Rule 5. An empty grant set is indistinguishable from holding nothing."""
    vector = _vector("valid.user.json")

    def unavailable(subject: str, tenant: str) -> GrantSet:
        raise GrantStoreUnavailable("grant store unreachable")

    result = resolve_principal(
        vector["credential"], _resolution_inputs(vector, grants_for=unavailable)
    )

    assert isinstance(result, Denial)
    assert result.denial_class == "grant_store_unavailable"
    assert result.unauthenticated is False


def test_a_portfolio_outside_scope_is_refused_rather_than_narrowed() -> None:
    """Rule 4. A narrowed result is indistinguishable from a correct one."""
    vector = _vector("valid.user.json")

    result = resolve_principal(
        vector["credential"],
        _resolution_inputs(vector, requested_portfolios=("PB_SG_GLOBAL_INC_002",)),
    )

    assert isinstance(result, Denial)
    assert result.denial_class == "portfolio_outside_scope"


def test_tenant_membership_is_resolved_rather_than_taken_from_the_credential() -> None:
    """The credential names a tenant; it does not prove membership of it."""
    vector = _vector("valid.user.json")

    result = resolve_principal(
        vector["credential"], _resolution_inputs(vector, tenant_members=NON_MEMBER)
    )

    assert isinstance(result, Denial)
    assert result.denial_class == "tenant_not_a_member"


def test_a_denial_carries_its_class_and_nothing_about_the_resource() -> None:
    """Rule 6. A refusal must not become an enumeration oracle."""
    vector = _vector("valid.user.json")

    result = resolve_principal(
        vector["credential"],
        _resolution_inputs(vector, requested_portfolios=("PB_SG_GLOBAL_INC_002",)),
    )

    assert isinstance(result, Denial)
    assert "PB_SG_GLOBAL_INC_002" not in result.denial_class
    assert "PB_SG_GLOBAL_INC_002" not in result.detail


# --- membership is a refusal, not an optional filter ---------------------------


def _spy_grants():
    """A grant callback that records whether it was reached."""
    calls: list[tuple[str, str]] = []

    def grants_for(subject: str, tenant: str) -> GrantSet:
        calls.append((subject, tenant))
        return GrantSet(frozenset({"portfolio.read"}), frozenset({"PB_SG_GLOBAL_BAL_001"}))

    return grants_for, calls


def test_a_member_of_the_admitted_tenant_resolves() -> None:
    """The positive case, on a really signed credential."""
    vector = _vector("valid.user.json")

    resolved = resolve_principal(vector["credential"], _resolution_inputs(vector))

    assert isinstance(resolved, ResolvedPrincipal)
    assert resolved.tenant_id == "tenant-sg"


def test_a_non_member_is_refused() -> None:
    vector = _vector("valid.user.json")

    result = resolve_principal(
        vector["credential"], _resolution_inputs(vector, tenant_members=NON_MEMBER)
    )

    assert isinstance(result, Denial)
    assert result.denial_class == "tenant_not_a_member"


def test_an_absent_membership_resolver_refuses_rather_than_skipping_the_check() -> None:
    """The defect this replaces: no resolver meant no membership check at all.

    The condition was `tenant_members is not None and not tenant_members(...)`,
    so a correctly signed credential naming any tenant resolved as long as
    grants happened to be available. An unanswerable question is not a pass.

    It refuses as `grant_store_unavailable` rather than `tenant_not_a_member`,
    because the second would assert the subject is not a member and nothing
    established that.
    """
    vector = _vector("valid.user.json")
    grants_for, calls = _spy_grants()

    result = resolve_principal(
        vector["credential"],
        _resolution_inputs(vector, tenant_members=None, grants_for=grants_for),
    )

    assert isinstance(result, Denial)
    assert result.denial_class == "grant_store_unavailable"
    assert result.unauthenticated is False
    assert calls == [], "grant lookup must not run once membership is unresolvable"


def test_an_unavailable_membership_lookup_refuses_instead_of_raising() -> None:
    """Rule 5, on the one callback it did not cover.

    `tenant_members` was invoked outside the handler wrapping the other grant
    callbacks, so the documented GrantStoreUnavailable escaped to the caller as
    an exception rather than becoming the governed denial.
    """
    vector = _vector("valid.user.json")
    grants_for, calls = _spy_grants()

    def unavailable(subject: str, tenant: str) -> bool:
        raise GrantStoreUnavailable("membership store unreachable")

    result = resolve_principal(
        vector["credential"],
        _resolution_inputs(vector, tenant_members=unavailable, grants_for=grants_for),
    )

    assert isinstance(result, Denial)
    assert result.denial_class == "grant_store_unavailable"
    assert calls == [], "grant lookup must not run once membership is unavailable"


def test_membership_is_resolved_before_any_grant_lookup() -> None:
    """Ordering, asserted rather than assumed.

    A refusal that happens after the protected lookup has already run is not a
    refusal of the effect, only of the response.
    """
    vector = _vector("valid.user.json")
    order: list[str] = []

    def members(subject: str, tenant: str) -> bool:
        order.append("membership")
        return False

    def grants_for(subject: str, tenant: str) -> GrantSet:
        order.append("grants")
        return GrantSet(frozenset(), frozenset())

    result = resolve_principal(
        vector["credential"],
        _resolution_inputs(vector, tenant_members=members, grants_for=grants_for),
    )

    assert isinstance(result, Denial)
    assert order == ["membership"]


def test_a_non_delegated_credential_resolves_without_an_application_resolver() -> None:
    """`application_grants_for` is required only where authority is an intersection.

    A `user` or `service` credential has no acting application, so there is no
    second grant set to intersect with. The published contract briefly said all
    three resolvers were required, which would have had consumers reject valid
    non-delegated requests -- a doc asserting a stricter rule than the code.
    """
    vector = _vector("valid.user.json")

    resolved = resolve_principal(
        vector["credential"], _resolution_inputs(vector, application_grants_for=None)
    )

    assert isinstance(resolved, ResolvedPrincipal)
    assert resolved.principal_kind == "user"


def test_a_delegated_credential_still_requires_the_application_resolver() -> None:
    """The intersection cannot be computed from one side of it."""
    vector = _vector("valid.delegated.json")

    result = resolve_principal(
        vector["credential"], _resolution_inputs(vector, application_grants_for=None)
    )

    assert isinstance(result, Denial)
    assert result.denial_class == "grant_store_unavailable"


def test_wrapper_exports_the_same_implementation_and_cli(tmp_path) -> None:
    from automation import verify_principal_credential as wrapper
    from lotus_principal_authority import verifier, cli

    for name in ("Denial", "GrantSet", "GrantStoreUnavailable", "ResolvedPrincipal",
                 "VerificationInputs", "PrincipalAdmission", "verify_credential",
                 "resolve_principal", "resolve_admission"):
        assert getattr(wrapper, name) is getattr(verifier, name)
    assert wrapper.main is cli.main
    sources = [ROOT / "automation/verify_principal_credential.py", *
               (ROOT / "packages/principal-authority/src/lotus_principal_authority").glob("*.py")]
    definitions = [node.name for path in sources
                   for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
                   if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    assert definitions.count("verify_credential") == 1
    assert definitions.count("resolve_principal") == 1
    vector = _vector("valid.user.json")
    inputs = _inputs_for(vector)
    revocations = tmp_path / "revocations.json"
    revocations.write_text(json.dumps(dict(credential_ids=[], subjects=[],
        valid_until=inputs.revocation_valid_until.isoformat())), encoding="utf-8")
    arguments = ["--credential", vector["credential"], "--jwks", str(EXAMPLES / "jwks.json"),
                 "--issuer", inputs.expected_issuer, "--audience", inputs.expected_audience,
                 "--now", inputs.now.isoformat(), "--revocations", str(revocations)]
    commands = [[sys.executable, str(ROOT / "automation/verify_principal_credential.py")],
                [sys.executable, "-m", "lotus_principal_authority.cli"]]
    for command in commands:
        result = subprocess.run(command + arguments, capture_output=True, text=True, cwd=tmp_path)
        assert (result.returncode, result.stdout.strip()) == (0, "verified")
        assert vector["credential"] not in result.stdout + result.stderr
        absent_trust = subprocess.run(command + ["--issuer", inputs.expected_issuer, "--audience", inputs.expected_audience],
                                      capture_output=True, text=True, cwd=tmp_path)
        assert absent_trust.returncode == 2


def test_packaged_capability_proof_executes_real_runtime() -> None:
    result = subprocess.run([sys.executable, "-I", str(ROOT / "automation/principal_runtime_capability_proof.py")],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Ran 9 tests" in result.stderr


def test_credential_schema_accepts_verified_kinds_and_rejects_invalid_identity_shapes() -> None:
    schema = json.loads((EXAMPLES.parent / "principal-credential.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    for kind in ("user", "service", "delegated"):
        vector = _vector(f"valid.{kind}.json")
        claims = verify_credential(vector["credential"], _inputs_for(vector))
        assert not list(validator.iter_errors(claims))
    valid = generator._claims()
    key = Ed25519PrivateKey.from_private_bytes(generator.TRUSTED_SEED)
    header = {"alg": "EdDSA", "kid": generator.TRUSTED_KEY_ID}
    inputs = _inputs_for(_vector("valid.user.json"))
    for field in ("sub", "tenant", "jti", "act"):
        claims = dict(valid)
        if field == "act":
            claims["principal_kind"] = "delegated"
        controls = [f"a{chr(code)}b" for code in (*range(32), *range(127, 160))]
        for value in ["", " ", " leading", "trailing ", "x" * 201, True, "x\n", *controls]:
            invalid = dict(claims, **{field: value})
            assert list(validator.iter_errors(invalid)), (field, repr(value))
            result = verify_credential(generator._sign(key, header, invalid), inputs)
            assert isinstance(result, Denial)
            assert result.denial_class == "malformed_credential"
        for value in ("客戶-é", "顧問😀", "a\u0301", "a b", "x" * 200, "😀" * 200):
            printable = dict(claims, **{field: value})
            assert validator.is_valid(printable), (field, repr(value))
            assert isinstance(verify_credential(generator._sign(key, header, printable), inputs), dict)
        # Portable structural predicates do not encode Python's full Unicode
        # category table. Keep this documented semantic boundary explicit.
        for value in ("a\u200bb", "a\u00a0b"):
            semantic = dict(claims, **{field: value})
            assert validator.is_valid(semantic)
            result = verify_credential(generator._sign(key, header, semantic), inputs)
            assert isinstance(result, Denial)
            assert result.denial_class == "malformed_credential"
    assert list(validator.iter_errors(dict(valid, act="application")))
    assert list(validator.iter_errors(dict(valid, principal_kind="delegated")))
