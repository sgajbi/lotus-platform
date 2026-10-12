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

import base64
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Mapping, Sequence

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

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
    revoked_credential_ids: frozenset[str] | None = None
    revoked_subjects: frozenset[str] | None = None
    revocation_valid_until: datetime | None = None
    authority_valid_until: datetime | None = None
    leeway_seconds: int = 0
    tenant_members: Callable[[str, str], bool] | None = None
    grants_for: Callable[[str, str], GrantSet] | None = None
    application_grants_for: Callable[[str, str], GrantSet] | None = None
    required_capabilities: Sequence[str] = field(default_factory=tuple)
    requested_portfolios: Sequence[str] = field(default_factory=tuple)


def _b64url_decode(segment: str) -> bytes:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", segment):
        raise ValueError("invalid base64url")
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def _decode_json_segment(segment: str) -> dict[str, Any]:
    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON member")
            result[key] = value
        return result

    payload = json.loads(_b64url_decode(segment), object_pairs_hook=unique_object)
    if not isinstance(payload, dict):
        raise ValueError("segment is not a JSON object")
    return payload


def _public_key_for(jwks: Mapping[str, Any], key_id: str) -> Ed25519PublicKey | None:
    keys = jwks.get("keys")
    if not isinstance(keys, list):
        return None
    matching = [key for key in keys if isinstance(key, dict) and key.get("kid") == key_id]
    if len(matching) != 1:
        return None
    for key in matching:
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
    if credential is None or (isinstance(credential, str) and not credential.strip()):
        return Denial(MISSING_CREDENTIAL, unauthenticated=True, detail="no credential presented")
    if not isinstance(credential, str) or len(credential) > 16384:
        return Denial(MALFORMED_CREDENTIAL, unauthenticated=True)
    if (
        not _bounded_identity(inputs.expected_issuer)
        or not _bounded_identity(inputs.expected_audience)
        or not isinstance(inputs.jwks, Mapping)
        or not inputs.jwks
    ):
        return Denial(GRANT_STORE_UNAVAILABLE, unauthenticated=False)

    parts = credential.split(".")
    if len(parts) != 3 or not all(parts):
        return Denial(MALFORMED_CREDENTIAL, unauthenticated=True, detail="not a three-part JWS")

    header_segment, payload_segment, signature_segment = parts
    try:
        header = _decode_json_segment(header_segment)
        claims = _decode_json_segment(payload_segment)
        signature = _b64url_decode(signature_segment)
    except (ValueError, UnicodeError, RecursionError):
        return Denial(MALFORMED_CREDENTIAL, unauthenticated=True, detail="undecodable segment")

    # `alg` comes from the credential, so it is only ever compared against the one
    # algorithm this verifier implements. It never selects an implementation, which
    # is what makes `alg: none` and algorithm-confusion unreachable here.
    if header.get("alg") != SUPPORTED_ALGORITHM or "crit" in header or "b64" in header:
        return Denial(
            MALFORMED_CREDENTIAL, unauthenticated=True, detail="unsupported algorithm"
        )

    key_id = header.get("kid")
    if not _bounded_identity(key_id):
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

    if (
        not _aware(inputs.now)
        or type(inputs.leeway_seconds) is not int
        or not 0 <= inputs.leeway_seconds <= 300
    ):
        return Denial(GRANT_STORE_UNAVAILABLE, unauthenticated=False)
    now = inputs.now.timestamp()
    expiry = claims.get("exp")
    if type(expiry) is not int or now >= expiry + inputs.leeway_seconds:
        return Denial(EXPIRED_CREDENTIAL, unauthenticated=True, detail="expired or no expiry")
    try:
        datetime.fromtimestamp(expiry, timezone.utc)
    except (ValueError, OverflowError, OSError):
        return Denial(EXPIRED_CREDENTIAL, unauthenticated=True)
    not_before = claims.get("nbf")
    if "nbf" in claims and (
        type(not_before) is not int or now < not_before - inputs.leeway_seconds
    ):
        return Denial(EXPIRED_CREDENTIAL, unauthenticated=True, detail="not yet valid")

    credential_id = claims.get("jti")
    subject = claims.get("sub")
    kind = claims.get("principal_kind")
    if (
        not all(_bounded_identity(claims.get(name)) for name in ("sub", "jti", "tenant"))
        or kind not in ("user", "service", "delegated")
        or (kind == "delegated" and not _bounded_identity(claims.get("act")))
        or (kind != "delegated" and "act" in claims)
    ):
        return Denial(MALFORMED_CREDENTIAL, unauthenticated=True)
    if (
        not _identity_set(inputs.revoked_credential_ids)
        or not _identity_set(inputs.revoked_subjects)
        or not _fresh(inputs.revocation_valid_until, inputs.now)
    ):
        return Denial(GRANT_STORE_UNAVAILABLE, unauthenticated=False)
    if credential_id in inputs.revoked_credential_ids:
        return Denial(REVOKED_PRINCIPAL, unauthenticated=True, detail="credential revoked")
    if subject in inputs.revoked_subjects:
        return Denial(REVOKED_PRINCIPAL, unauthenticated=True, detail="subject revoked")

    return claims


def _resolve_verified(claims: dict[str, Any], inputs: VerificationInputs) -> Denial | ResolvedPrincipal:
    """Resolve current grants after cryptographic admission, without reparsing."""
    if not _fresh(inputs.authority_valid_until, inputs.now):
        return Denial(GRANT_STORE_UNAVAILABLE, unauthenticated=False)

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
    if type(is_member) is not bool:
        return Denial(GRANT_STORE_UNAVAILABLE, unauthenticated=False)
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

    if not _valid_grants(grants) or (
        principal_kind == "delegated" and not _valid_grants(application_grants)
    ):
        return Denial(GRANT_STORE_UNAVAILABLE, unauthenticated=False)
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


def _bounded_identity(value: object) -> bool:
    return (
        isinstance(value, str) and 0 < len(value) <= 200
        and value == value.strip() and value.isprintable()
    )


def _identity_set(value: object) -> bool:
    return isinstance(value, frozenset) and all(_bounded_identity(item) for item in value)


def _valid_grants(value: object) -> bool:
    return (
        isinstance(value, GrantSet) and _identity_set(value.capabilities)
        and _identity_set(value.portfolio_scope)
    )


def _aware(value: object) -> bool:
    return (
        isinstance(value, datetime) and value.tzinfo is not None
        and value.utcoffset() is not None
    )


def _fresh(until: datetime | None, now: datetime) -> bool:
    return _aware(until) and _aware(now) and now < until


@dataclass(frozen=True)
class PrincipalAdmission:
    """Verified principal and authoritative time bound; never a durable grant."""

    principal: ResolvedPrincipal
    evaluated_at: datetime
    credential_expires_at: datetime
    valid_until: datetime

    def is_current(self, now: datetime) -> bool:
        return _aware(now) and self.evaluated_at <= now < self.valid_until


def resolve_admission(credential: str | None, inputs: VerificationInputs) -> Denial | PrincipalAdmission:
    """Verify once; bound the result by expiry and current authoritative freshness."""
    claims = verify_credential(credential, inputs)
    if isinstance(claims, Denial):
        return claims
    principal = _resolve_verified(claims, inputs)
    if isinstance(principal, Denial):
        return principal
    try:
        expires = datetime.fromtimestamp(claims["exp"], timezone.utc)
    except (ValueError, OverflowError, OSError):
        return Denial(EXPIRED_CREDENTIAL, unauthenticated=True)
    valid_until = min(
        expires, inputs.revocation_valid_until, inputs.authority_valid_until,
        inputs.now + timedelta(seconds=300),
    )
    if inputs.now >= valid_until:
        return Denial(EXPIRED_CREDENTIAL, unauthenticated=True)
    return PrincipalAdmission(principal, inputs.now, expires, valid_until)


def resolve_principal(credential: str | None, inputs: VerificationInputs) -> Denial | ResolvedPrincipal:
    """Compatible result shape with the same fail-closed admission semantics."""
    result = resolve_admission(credential, inputs)
    return result.principal if isinstance(result, PrincipalAdmission) else result
