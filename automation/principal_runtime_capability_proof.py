"""Executed unchanged inside and outside the checkout; no fixture/path imports."""

from __future__ import annotations

import base64
import json
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from lotus_principal_authority import (
    Denial, GrantSet, GrantStoreUnavailable, PrincipalAdmission, VerificationInputs,
    resolve_admission, resolve_principal, verify_credential,
)
from lotus_principal_authority import verifier


def encoded(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


class PrincipalRuntimeProof(unittest.TestCase):
    def setUp(self) -> None:
        self.key = Ed25519PrivateKey.generate()
        self.now = datetime(2026, 10, 12, tzinfo=timezone.utc)
        self.claims = dict(
            iss="https://synthetic.invalid", aud="synthetic-consumer", sub="user:one",
            tenant="tenant:one", principal_kind="user", jti="credential:one",
            exp=int(self.now.timestamp()) + 600, nbf=int(self.now.timestamp()),
        )
        self.header = dict(alg="EdDSA", kid="synthetic-key")
        jwk = dict(kty="OKP", crv="Ed25519", kid="synthetic-key", x=encoded(
            self.key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        ))
        grants = GrantSet(frozenset({"read", "write"}), frozenset({"portfolio:one", "portfolio:two"}))
        self.inputs = VerificationInputs(
            expected_issuer=self.claims["iss"], expected_audience=self.claims["aud"],
            jwks={"keys": [jwk]}, now=self.now,
            revoked_credential_ids=frozenset(), revoked_subjects=frozenset(),
            revocation_valid_until=self.now + timedelta(seconds=200),
            authority_valid_until=self.now + timedelta(seconds=150),
            tenant_members=lambda subject, tenant: True,
            grants_for=lambda subject, tenant: grants,
            application_grants_for=lambda actor, tenant: GrantSet(
                frozenset({"read"}), frozenset({"portfolio:one"})
            ),
            required_capabilities=("read",), requested_portfolios=("portfolio:one",),
        )

    def signed(self, *, claims=None, header=None, key=None, raw_header=None, raw_payload=None):
        h = encoded(raw_header or json.dumps(header or self.header).encode())
        p = encoded(raw_payload or json.dumps(claims or self.claims).encode())
        unsigned = f"{h}.{p}"
        return f"{unsigned}.{encoded((key or self.key).sign(unsigned.encode()))}"

    def denial(self, credential, inputs, expected):
        result = resolve_admission(credential, inputs)
        self.assertIsInstance(result, Denial)
        self.assertEqual(result.denial_class, expected)
        return result

    def test_positive_human_service_delegated_and_intersection(self):
        for kind in ("user", "service", "delegated"):
            claims = dict(self.claims, principal_kind=kind)
            if kind == "service":
                claims["sub"] = "service:one"
            if kind == "delegated":
                claims["act"] = "application:one"
            result = resolve_admission(self.signed(claims=claims), self.inputs)
            self.assertIsInstance(result, PrincipalAdmission)
            expected = ("read",) if kind == "delegated" else ("read", "write")
            self.assertEqual(result.principal.capabilities, expected)
            self.assertEqual(result.credential_expires_at.timestamp(), claims["exp"])

    def test_all_thirteen_real_denials_precede_protected_effect(self):
        token = self.signed()
        delegated = self.signed(claims=dict(self.claims, principal_kind="delegated", act="app"))
        def unavailable(subject, tenant):
            raise GrantStoreUnavailable("synthetic provider unavailable")
        cases = [
            (None, self.inputs, "missing_credential"),
            ("malformed", self.inputs, "malformed_credential"),
            (self.signed(claims=dict(self.claims, exp=int(self.now.timestamp()))), self.inputs, "expired_credential"),
            (token, replace(self.inputs, revoked_subjects=frozenset({"user:one"})), "revoked_principal"),
            (self.signed(claims=dict(self.claims, iss="other")), self.inputs, "wrong_issuer"),
            (self.signed(claims=dict(self.claims, aud="other")), self.inputs, "wrong_audience"),
            (self.signed(header=dict(self.header, kid="unknown")), self.inputs, "unknown_key_id"),
            (self.signed(key=Ed25519PrivateKey.generate()), self.inputs, "present_but_unverified"),
            (token, replace(self.inputs, tenant_members=lambda s, t: False), "tenant_not_a_member"),
            (token, replace(self.inputs, required_capabilities=("delete",)), "capability_not_granted"),
            (delegated, replace(self.inputs, grants_for=lambda s, t: GrantSet(frozenset(), frozenset())), "delegated_capability_not_held_by_user"),
            (token, replace(self.inputs, requested_portfolios=("foreign",)), "portfolio_outside_scope"),
            (token, replace(self.inputs, grants_for=unavailable), "grant_store_unavailable"),
        ]
        protected_calls = []
        observed = set()
        for credential, inputs, expected in cases:
            with self.subTest(expected=expected):
                result = resolve_admission(credential, inputs)
                if isinstance(result, PrincipalAdmission):
                    protected_calls.append(result.principal)
                self.assertIsInstance(result, Denial)
                observed.add(result.denial_class)
                self.assertEqual(result.denial_class, expected)
                self.assertNotIn("foreign", result.detail)
        self.assertEqual(len(observed), 13)
        self.assertEqual(protected_calls, [])

    def test_exclusive_expiry_leeway_nbf_and_integer_not_bool(self):
        epoch = int(self.now.timestamp())
        for claim, value in (("exp", epoch), ("exp", True), ("exp", 10 ** 100), ("exp", epoch + 0.5), ("nbf", True), ("nbf", None), ("nbf", epoch + 1)):
            with self.subTest(claim=claim, value=value):
                self.denial(self.signed(claims=dict(self.claims, **{claim: value})), self.inputs, "expired_credential")
        token = self.signed(claims=dict(self.claims, exp=epoch - 5))
        result = verify_credential(token, replace(self.inputs, leeway_seconds=5))
        self.assertEqual(result.denial_class, "expired_credential")
        self.assertIsInstance(verify_credential(self.signed(), self.inputs), dict)

    def test_missing_stale_and_fresh_known_empty_revocations(self):
        for changes in (
            {"revoked_subjects": None}, {"revoked_credential_ids": None},
            {"revoked_subjects": ""}, {"revocation_valid_until": None},
            {"revocation_valid_until": self.now},
            {"revocation_valid_until": self.now - timedelta(seconds=1)},
            {"authority_valid_until": None}, {"authority_valid_until": self.now},
        ):
            with self.subTest(changes=changes):
                self.denial(self.signed(), replace(self.inputs, **changes), "grant_store_unavailable")
        self.assertIsInstance(resolve_admission(self.signed(), self.inputs), PrincipalAdmission)

    def test_bounds_and_queue_recheck(self):
        token = self.signed()
        for seconds, inputs in (
            (150, self.inputs),
            (70, replace(self.inputs, revocation_valid_until=self.now + timedelta(seconds=70))),
            (300, replace(self.inputs, revocation_valid_until=self.now + timedelta(hours=1), authority_valid_until=self.now + timedelta(hours=1))),
        ):
            result = resolve_admission(token, inputs)
            self.assertEqual(result.valid_until, self.now + timedelta(seconds=seconds))
            self.assertTrue(result.is_current(result.valid_until - timedelta(microseconds=1)))
            self.assertFalse(result.is_current(result.valid_until))
            self.assertFalse(result.is_current(self.now - timedelta(microseconds=1)))
        short = resolve_admission(self.signed(claims=dict(self.claims, exp=int(self.now.timestamp()) + 20)), self.inputs)
        self.assertEqual(short.valid_until, self.now + timedelta(seconds=20))
        self.assertFalse(short.is_current(short.credential_expires_at))

    def test_bounded_identity_and_actor_shape(self):
        self.denial("x" * 16385, self.inputs, "malformed_credential")
        for name in ("sub", "jti", "tenant"):
            for value in (None, "", " ", "x\n", "x" * 201, True, ["x"]):
                with self.subTest(name=name, value=value):
                    self.denial(self.signed(claims=dict(self.claims, **{name: value})), self.inputs, "malformed_credential")
        self.denial(self.signed(claims=dict(self.claims, act="app")), self.inputs, "malformed_credential")
        self.denial(self.signed(claims=dict(self.claims, principal_kind="delegated", act=" ")), self.inputs, "malformed_credential")
        for value in ("", " ", "key\n", "x" * 201, True):
            self.denial(self.signed(header=dict(self.header, kid=value)), self.inputs, "malformed_credential")

    def test_duplicate_and_critical_headers_payload_and_duplicate_keys(self):
        for arguments in (
            {"raw_header": b'{"alg":"none","alg":"EdDSA","kid":"synthetic-key"}'},
            {"raw_payload": b'{"sub":"attacker",' + json.dumps(self.claims).encode()[1:]},
            {"header": dict(self.header, crit=["unknown"])},
            {"header": dict(self.header, b64=False)},
            {"header": dict(self.header, alg="none")},
        ):
            self.denial(self.signed(**arguments), self.inputs, "malformed_credential")
        self.denial(self.signed(), replace(self.inputs, jwks={"keys": self.inputs.jwks["keys"] * 2}), "unknown_key_id")

    def test_verify_before_trust_and_only_once(self):
        self.denial(self.signed(key=Ed25519PrivateKey.generate(), claims=dict(self.claims, iss="other", exp=0)), self.inputs, "present_but_unverified")
        with patch.object(verifier, "verify_credential", wraps=verify_credential) as spy:
            result = resolve_admission(self.signed(), self.inputs)
            self.assertIsInstance(result, PrincipalAdmission)
            self.assertEqual(spy.call_count, 1)
            self.assertEqual(resolve_principal(self.signed(), self.inputs), result.principal)

    def test_unavailable_or_malformed_authority_is_not_membership_or_empty_grants(self):
        for changes in (
            {"tenant_members": None}, {"tenant_members": lambda s, t: "yes"},
            {"grants_for": None}, {"grants_for": lambda s, t: None},
            {"grants_for": lambda s, t: GrantSet("read", frozenset())},
        ):
            self.denial(self.signed(), replace(self.inputs, **changes), "grant_store_unavailable")


if __name__ == "__main__":
    unittest.main(verbosity=2)
