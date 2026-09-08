"""Verify a Lotus principal credential and resolve it to a principal.

The fixture set published in ``platform-contracts/principal-resolution`` states its
own limit: it carries no signed bytes and no keys, so nothing in it can make a real
verifier fail. ``present_but_unverified`` is an instruction to a harness rather
than a property of a payload, and a consumer can satisfy every fixture by
inspecting structure and resolving nothing.

This module closes that gap. It verifies real Ed25519 signatures over real bytes,
so a consumer can generate its own keys, mint a credential this verifier rejects,
and prove its resolver refuses for the reason the contract names.

What it deliberately does not do: choose an identity provider, host the grant
store, or certify a production deployment. The grant store is injected, because
Platform defines the contract and does not own the data.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = ROOT / "platform-contracts" / "principal-credential"

SUPPORTED_ALGORITHM = "EdDSA"
SUPPORTED_KEY_TYPE = "OKP"
SUPPORTED_CURVE = "Ed25519"

# Denial classes are the published vocabulary from the principal-resolution
# contract. A verifier that invents its own names cannot be checked against the
# fixtures a consumer must prove.
MISSING_CREDENTIAL = "missing_credential"
MALFORMED_CREDENTIAL = "malformed_credential"
UNKNOWN_KEY_ID = "unknown_key_id"
PRESENT_BUT_UNVERIFIED = "present_but_unverified"
WRONG_ISSUER = "wrong_issuer"
WRONG_AUDIENCE = "wrong_audience"
EXPIRED_CREDENTIAL = "expired_credential"
REVOKED_PRINCIPAL = "revoked_principal"
TENANT_NOT_A_MEMBER = "tenant_not_a_member"
GRANT_STORE_UNAVAILABLE = "grant_store_unavailable"
CAPABILITY_NOT_GRANTED = "capability_not_granted"
DELEGATED_CAPABILITY_NOT_HELD_BY_USER = "delegated_capability_not_held_by_user"
PORTFOLIO_OUTSIDE_SCOPE = "portfolio_outside_scope"


class GrantStoreUnavailable(Exception):
    """Raised by a grant store that cannot answer.

    Rule 5 of the contract: unavailability is a denial, not an empty grant set.
    An empty set would be indistinguishable from a principal holding nothing, and
    the request would be refused for the wrong reason -- or, with a permissive
    consumer, not refused at all.
    """


@dataclass(frozen=True)
class Denial:
    """A refusal, carrying its class and nothing further.

    Rule 6: a denial distinguishes unauthenticated from unauthorized and reveals
    neither which capability was missing nor whether a named resource exists.
    ``detail`` is for the local operator log; it is never the wire response, and
    nothing in this module puts it there.
    """

    denial_class: str
    unauthenticated: bool
    detail: str = ""


@dataclass(frozen=True)
class ResolvedPrincipal:
    """The shape a downstream authorizes against."""

    principal_kind: str
    subject: str
    tenant_id: str
    capabilities: tuple[str, ...]
    portfolio_scope: tuple[str, ...]
    delegated_actor: str | None = None
    credential_id: str | None = None


@dataclass(frozen=True)
class GrantSet:
    capabilities: frozenset[str]
    portfolio_scope: frozenset[str]


@dataclass
class VerificationInputs:
    """Everything the verifier trusts, supplied by deployment rather than by the caller.

    ``expected_issuer`` and ``jwks`` are bound together on purpose. Selecting a key
    set from the credential's own unverified ``iss`` lets an attacker nominate the
    authority that will vouch for them; the only claim read before verification is
    ``kid``, and only to pick among keys this deployment already trusts.
    """

    expected_issuer: str
    expected_audience: str
    jwks: Mapping[str, Any]
    now: datetime
    revoked_credential_ids: frozenset[str] = frozenset()
    revoked_subjects: frozenset[str] = frozenset()
    leeway_seconds: int = 0
    tenant_members: Callable[[str, str], bool] | None = None
    grants_for: Callable[[str, str], GrantSet] | None = None
    application_grants_for: Callable[[str, str], GrantSet] | None = None
    required_capabilities: Sequence[str] = field(default_factory=tuple)
    requested_portfolios: Sequence[str] = field(default_factory=tuple)


def _b64url_decode(segment: str) -> bytes:
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def _decode_json_segment(segment: str) -> dict[str, Any]:
    payload = json.loads(_b64url_decode(segment))
    if not isinstance(payload, dict):
        raise ValueError("segment is not a JSON object")
    return payload


def _public_key_for(jwks: Mapping[str, Any], key_id: str) -> Ed25519PublicKey | None:
    keys = jwks.get("keys")
    if not isinstance(keys, list):
        return None
    for key in keys:
        if not isinstance(key, dict) or key.get("kid") != key_id:
            continue
        if (
            key.get("kty") != SUPPORTED_KEY_TYPE
            or key.get("crv") != SUPPORTED_CURVE
            or key.get("alg") not in (None, SUPPORTED_ALGORITHM)
        ):
            # A key of the wrong type under the right id is not a match. Falling
            # through to "unknown key" is correct: this deployment has no usable
            # key for that id, and saying more would describe the key set.
            return None
        try:
            return Ed25519PublicKey.from_public_bytes(_b64url_decode(str(key.get("x"))))
        except (ValueError, TypeError):
            return None
    return None


def _string_tuple(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return tuple(value)
    return ()


def verify_credential(
    credential: str | None, inputs: VerificationInputs
) -> Denial | dict[str, Any]:
    """Verify the credential's signature and time bounds, or refuse.

    Returns the verified claims. The order is the security property: nothing in
    the payload is believed until the signature over it verifies, so issuer,
    audience and expiry are checked afterwards. Checking expiry first would be
    refusing on the strength of bytes nobody signed.
    """
    if credential is None or not credential.strip():
        return Denial(MISSING_CREDENTIAL, unauthenticated=True, detail="no credential presented")

    parts = credential.split(".")
    if len(parts) != 3 or not all(parts):
        return Denial(MALFORMED_CREDENTIAL, unauthenticated=True, detail="not a three-part JWS")

    header_segment, payload_segment, signature_segment = parts
    try:
        header = _decode_json_segment(header_segment)
        claims = _decode_json_segment(payload_segment)
        signature = _b64url_decode(signature_segment)
    except (ValueError, json.JSONDecodeError, base64.binascii.Error):
        return Denial(MALFORMED_CREDENTIAL, unauthenticated=True, detail="undecodable segment")

    # `alg` comes from the credential, so it is only ever compared against the one
    # algorithm this verifier implements. It never selects an implementation, which
    # is what makes `alg: none` and algorithm-confusion unreachable here.
    if header.get("alg") != SUPPORTED_ALGORITHM:
        return Denial(
            MALFORMED_CREDENTIAL, unauthenticated=True, detail="unsupported algorithm"
        )

    key_id = header.get("kid")
    if not isinstance(key_id, str) or not key_id:
        return Denial(MALFORMED_CREDENTIAL, unauthenticated=True, detail="no key id")

    public_key = _public_key_for(inputs.jwks, key_id)
    if public_key is None:
        return Denial(UNKNOWN_KEY_ID, unauthenticated=True, detail="no trusted key for kid")

    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    try:
        public_key.verify(signature, signing_input)
    except InvalidSignature:
        return Denial(
            PRESENT_BUT_UNVERIFIED,
            unauthenticated=True,
            detail="signature did not verify against the trusted key",
        )

    # Everything below is verified data.
    if claims.get("iss") != inputs.expected_issuer:
        return Denial(WRONG_ISSUER, unauthenticated=True, detail="issuer not trusted here")
    if inputs.expected_audience not in _string_tuple(claims.get("aud")):
        return Denial(
            WRONG_AUDIENCE, unauthenticated=True, detail="credential minted for another service"
        )

    now = int(inputs.now.timestamp())
    expiry = claims.get("exp")
    if not isinstance(expiry, int) or now > expiry + inputs.leeway_seconds:
        return Denial(EXPIRED_CREDENTIAL, unauthenticated=True, detail="expired or no expiry")
    not_before = claims.get("nbf")
    if isinstance(not_before, int) and now < not_before - inputs.leeway_seconds:
        return Denial(EXPIRED_CREDENTIAL, unauthenticated=True, detail="not yet valid")

    credential_id = claims.get("jti")
    subject = claims.get("sub")
    if isinstance(credential_id, str) and credential_id in inputs.revoked_credential_ids:
        return Denial(REVOKED_PRINCIPAL, unauthenticated=True, detail="credential revoked")
    if isinstance(subject, str) and subject in inputs.revoked_subjects:
        return Denial(REVOKED_PRINCIPAL, unauthenticated=True, detail="subject revoked")

    return claims


def resolve_principal(
    credential: str | None, inputs: VerificationInputs
) -> Denial | ResolvedPrincipal:
    """The five refusals, in order, after verification.

    Each step refuses rather than narrows. A request for a portfolio outside scope
    is denied, not quietly served with that portfolio removed -- a narrowed result
    is indistinguishable from a correct one to the caller and to the audit record.
    """
    verified = verify_credential(credential, inputs)
    if isinstance(verified, Denial):
        return verified
    claims = verified

    subject = claims.get("sub")
    tenant_id = claims.get("tenant")
    principal_kind = claims.get("principal_kind")
    if (
        not isinstance(subject, str)
        or not isinstance(tenant_id, str)
        or principal_kind not in ("user", "service", "delegated")
    ):
        return Denial(MALFORMED_CREDENTIAL, unauthenticated=True, detail="incomplete principal")

    delegated_actor = claims.get("act")
    if principal_kind == "delegated" and not isinstance(delegated_actor, str):
        return Denial(
            MALFORMED_CREDENTIAL, unauthenticated=True, detail="delegated credential names no actor"
        )

    # Rule 4: resolution is five refusals, not five filters, and membership is
    # the second. It was previously skipped entirely when no resolver was
    # supplied -- `tenant_members is not None and ...` -- so a correctly signed
    # credential naming any tenant resolved as long as grants happened to be
    # available. An absent resolver is an unanswerable question, not a pass.
    #
    # Membership is resolved from the grant store, which the tenant-membership
    # owner owns, so its absence is `grant_store_unavailable` rather than a
    # membership refusal: refusing as `tenant_not_a_member` would assert that
    # the subject is not a member, which nothing established.
    if inputs.tenant_members is None:
        return Denial(
            GRANT_STORE_UNAVAILABLE,
            unauthenticated=False,
            detail="no membership resolver: tenant membership could not be established",
        )
    try:
        is_member = inputs.tenant_members(subject, tenant_id)
    except GrantStoreUnavailable:
        # Rule 5: unavailability is a denial. This call sat outside the handler
        # covering the other grant-store callbacks, so the documented exception
        # escaped to the caller instead of becoming the governed refusal.
        return Denial(
            GRANT_STORE_UNAVAILABLE, unauthenticated=False, detail="membership lookup failed"
        )
    if not is_member:
        return Denial(TENANT_NOT_A_MEMBER, unauthenticated=False, detail="not a member")

    if inputs.grants_for is None:
        return Denial(GRANT_STORE_UNAVAILABLE, unauthenticated=False, detail="no grant store")
    try:
        grants = inputs.grants_for(subject, tenant_id)
        application_grants = (
            inputs.application_grants_for(str(delegated_actor), tenant_id)
            if principal_kind == "delegated" and inputs.application_grants_for is not None
            else None
        )
    except GrantStoreUnavailable:
        return Denial(GRANT_STORE_UNAVAILABLE, unauthenticated=False, detail="grant store failed")

    capabilities = grants.capabilities
    portfolio_scope = grants.portfolio_scope
    if principal_kind == "delegated":
        if application_grants is None:
            return Denial(
                GRANT_STORE_UNAVAILABLE, unauthenticated=False, detail="no application grants"
            )
        # Rule 3: the intersection. A shared service identity never widens a
        # person's entitlement, and the person never gains what the application
        # was not granted.
        capabilities = capabilities & application_grants.capabilities
        portfolio_scope = portfolio_scope & application_grants.portfolio_scope

    required = frozenset(inputs.required_capabilities)
    if not required <= capabilities:
        if principal_kind == "delegated" and required <= application_grants.capabilities:
            return Denial(
                DELEGATED_CAPABILITY_NOT_HELD_BY_USER,
                unauthenticated=False,
                detail="application holds it, person does not",
            )
        return Denial(CAPABILITY_NOT_GRANTED, unauthenticated=False, detail="capability missing")

    requested = frozenset(inputs.requested_portfolios)
    if not requested <= portfolio_scope:
        return Denial(PORTFOLIO_OUTSIDE_SCOPE, unauthenticated=False, detail="outside scope")

    return ResolvedPrincipal(
        principal_kind=principal_kind,
        subject=subject,
        tenant_id=tenant_id,
        capabilities=tuple(sorted(capabilities)),
        portfolio_scope=tuple(sorted(portfolio_scope)),
        delegated_actor=delegated_actor if principal_kind == "delegated" else None,
        credential_id=claims.get("jti") if isinstance(claims.get("jti"), str) else None,
    )


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify a Lotus principal credential against a trusted key set."
    )
    parser.add_argument("--credential", help="compact JWS; omit to prove the missing case")
    parser.add_argument("--jwks", type=Path, default=CONTRACT_DIR / "examples" / "jwks.json")
    parser.add_argument("--issuer", required=True)
    parser.add_argument("--audience", required=True)
    parser.add_argument(
        "--now",
        help="RFC3339 instant to evaluate at; defaults to now, and fixtures pin it",
    )
    args = parser.parse_args(argv)

    now = (
        datetime.fromisoformat(args.now.replace("Z", "+00:00"))
        if args.now
        else datetime.now(timezone.utc)
    )
    outcome = verify_credential(
        args.credential,
        VerificationInputs(
            expected_issuer=args.issuer,
            expected_audience=args.audience,
            jwks=_load_json(args.jwks),
            now=now,
        ),
    )
    if isinstance(outcome, Denial):
        print(f"denied: {outcome.denial_class}")
        return 1
    print("verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
