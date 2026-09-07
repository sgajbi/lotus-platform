"""Generate signed principal-credential test vectors.

The vectors carry real Ed25519 signatures over real bytes, so a consumer's
verifier either verifies them or does not. That is the whole point: the existing
principal-resolution fixtures state an expected outcome, and a harness can satisfy
them by branching on the denial class without verifying anything.

No private key is committed. Both keys are derived from documented 32-byte seeds,
so the vectors are reproducible from this file plus the seeds, and the repository
holds only public key material. Ed25519 signatures are deterministic (RFC 8032),
so regenerating produces byte-identical output and a drift check is meaningful.

The seeds are test material for fixtures. They authenticate nothing, and no
deployment may configure them.
"""

from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "platform-contracts" / "principal-credential" / "examples"

# Documented test seeds. The first is the issuer key this deployment trusts; the
# second is a key it does not, used to mint the credential whose signature must
# fail while every structural assertion passes.
TRUSTED_SEED = bytes.fromhex(
    "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"
)
FOREIGN_SEED = bytes.fromhex(
    "4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb"
)

TRUSTED_KEY_ID = "lotus-test-issuer-2026-09"
FOREIGN_KEY_ID = TRUSTED_KEY_ID  # deliberately the same id; see the vector note
UNKNOWN_KEY_ID = "lotus-test-issuer-retired"

ISSUER = "https://identity.lotus.test/realms/lotus"
WORKBENCH_AUDIENCE = "lotus-workbench-bff"
GATEWAY_AUDIENCE = "lotus-gateway"
TENANT = "tenant-sg"
USER_SUBJECT = "user:adviser.sg.001"
SERVICE_SUBJECT = "service:lotus-workbench"

# Fixed instants. A vector that expires relative to the run clock stops testing
# what it was written to test the moment CI is slow.
EVALUATION_INSTANT = "2026-09-07T12:00:00Z"
VALID_FROM = "2026-09-07T11:00:00Z"
VALID_UNTIL = "2026-09-07T13:00:00Z"
ALREADY_EXPIRED = "2026-09-07T11:30:00Z"


def _epoch(instant: str) -> int:
    return int(datetime.fromisoformat(instant.replace("Z", "+00:00")).timestamp())


def _b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _sign(private_key: Ed25519PrivateKey, header: dict[str, Any], claims: dict[str, Any]) -> str:
    header_segment = _b64url(json.dumps(header, separators=(",", ":"), sort_keys=True).encode())
    payload_segment = _b64url(json.dumps(claims, separators=(",", ":"), sort_keys=True).encode())
    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    return f"{header_segment}.{payload_segment}.{_b64url(private_key.sign(signing_input))}"


def _claims(**overrides: Any) -> dict[str, Any]:
    base = {
        "iss": ISSUER,
        "aud": WORKBENCH_AUDIENCE,
        "sub": USER_SUBJECT,
        "tenant": TENANT,
        "principal_kind": "user",
        "jti": "cred-0001",
        "nbf": _epoch(VALID_FROM),
        "exp": _epoch(VALID_UNTIL),
    }
    base.update(overrides)
    return base


def _vector(
    name: str,
    *,
    credential: str | None,
    expected: str,
    why: str,
    audience: str = WORKBENCH_AUDIENCE,
    revoked_credential_ids: list[str] | None = None,
    revoked_subjects: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "$schema": "https://lotus.dev/schemas/principal-credential-vector.v1",
        "vector_id": name,
        "expected_outcome": expected,
        "why": why,
        "verification_inputs": {
            "expected_issuer": ISSUER,
            "expected_audience": audience,
            "jwks": "jwks.json",
            "evaluate_at": EVALUATION_INSTANT,
            "revoked_credential_ids": revoked_credential_ids or [],
            "revoked_subjects": revoked_subjects or [],
        },
        "credential": credential,
    }


def build() -> dict[str, dict[str, Any]]:
    trusted = Ed25519PrivateKey.from_private_bytes(TRUSTED_SEED)
    foreign = Ed25519PrivateKey.from_private_bytes(FOREIGN_SEED)
    trusted_header = {"alg": "EdDSA", "kid": TRUSTED_KEY_ID, "typ": "JWT"}

    jwks = {
        "keys": [
            {
                "kty": "OKP",
                "crv": "Ed25519",
                "alg": "EdDSA",
                "use": "sig",
                "kid": TRUSTED_KEY_ID,
                "x": _b64url(
                    trusted.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
                ),
            }
        ]
    }

    files: dict[str, dict[str, Any]] = {"jwks.json": jwks}

    files["valid.user.json"] = _vector(
        "valid.user",
        credential=_sign(trusted, trusted_header, _claims()),
        expected="verified",
        why="A well-formed, in-window credential signed by the trusted issuer key.",
    )
    files["valid.service.json"] = _vector(
        "valid.service",
        credential=_sign(
            trusted,
            trusted_header,
            _claims(sub=SERVICE_SUBJECT, principal_kind="service", jti="cred-0002"),
        ),
        expected="verified",
        why="A service principal resolves to the same shape as a user principal.",
    )
    files["valid.delegated.json"] = _vector(
        "valid.delegated",
        credential=_sign(
            trusted,
            trusted_header,
            _claims(
                aud=GATEWAY_AUDIENCE,
                principal_kind="delegated",
                act=SERVICE_SUBJECT,
                jti="cred-0003",
            ),
        ),
        expected="verified",
        why=(
            "The Workbench-to-Gateway shape: a person as subject, the calling "
            "application as act, and Gateway as the audience."
        ),
        audience=GATEWAY_AUDIENCE,
    )

    # The vector that separates a verifier from an inspector. Same kid, so key
    # lookup succeeds and every structural assertion passes; the signature was
    # produced by a key this deployment does not trust.
    files["denial.present_but_unverified.json"] = _vector(
        "denial.present_but_unverified",
        credential=_sign(
            foreign, {"alg": "EdDSA", "kid": FOREIGN_KEY_ID, "typ": "JWT"}, _claims()
        ),
        expected="present_but_unverified",
        why=(
            "Well-formed, unexpired, correctly audienced, and signed by a key that "
            "is not the trusted one. Structure alone cannot refuse this."
        ),
    )
    files["denial.unknown_key_id.json"] = _vector(
        "denial.unknown_key_id",
        credential=_sign(
            trusted, {"alg": "EdDSA", "kid": UNKNOWN_KEY_ID, "typ": "JWT"}, _claims()
        ),
        expected="unknown_key_id",
        why="Signed by the trusted key but naming a key id this deployment does not publish.",
    )
    files["denial.wrong_issuer.json"] = _vector(
        "denial.wrong_issuer",
        credential=_sign(
            trusted, trusted_header, _claims(iss="https://identity.other.test/realms/lotus")
        ),
        expected="wrong_issuer",
        why="A validly signed credential from an issuer this deployment does not accept.",
    )
    files["denial.wrong_audience.json"] = _vector(
        "denial.wrong_audience",
        credential=_sign(trusted, trusted_header, _claims(aud="lotus-manage")),
        expected="wrong_audience",
        why="Minted for another service; a leaked credential must not be a general-purpose key.",
    )
    files["denial.expired_credential.json"] = _vector(
        "denial.expired_credential",
        credential=_sign(trusted, trusted_header, _claims(exp=_epoch(ALREADY_EXPIRED))),
        expected="expired_credential",
        why="Expired before the pinned evaluation instant.",
    )
    files["denial.not_yet_valid.json"] = _vector(
        "denial.not_yet_valid",
        credential=_sign(
            trusted,
            trusted_header,
            _claims(nbf=_epoch("2026-09-07T12:30:00Z"), exp=_epoch("2026-09-07T14:00:00Z")),
        ),
        expected="expired_credential",
        why=(
            "Not yet valid. It shares the expired class deliberately: a caller "
            "learns the credential is outside its window, not which end."
        ),
    )
    files["denial.revoked_principal.json"] = _vector(
        "denial.revoked_principal",
        credential=_sign(trusted, trusted_header, _claims(jti="cred-revoked")),
        expected="revoked_principal",
        why="Signature and window are good; the credential id is on the revocation list.",
        revoked_credential_ids=["cred-revoked"],
    )
    files["denial.algorithm_none.json"] = _vector(
        "denial.algorithm_none",
        credential=(
            _b64url(json.dumps({"alg": "none", "kid": TRUSTED_KEY_ID}, separators=(",", ":")).encode())
            + "."
            + _b64url(json.dumps(_claims(), separators=(",", ":"), sort_keys=True).encode())
            + "."
            + _b64url(b"not-a-signature")
        ),
        expected="malformed_credential",
        why=(
            "The classic downgrade. `alg` is compared against the one algorithm "
            "implemented and never selects an implementation, so this cannot verify."
        ),
    )
    files["denial.malformed_credential.json"] = _vector(
        "denial.malformed_credential",
        credential="not.a.jws",
        expected="malformed_credential",
        why="Three segments that do not decode.",
    )
    files["denial.missing_credential.json"] = _vector(
        "denial.missing_credential",
        credential=None,
        expected="missing_credential",
        why="No credential presented; unauthenticated rather than unauthorized.",
    )
    return files


def write() -> list[Path]:
    EXAMPLES.mkdir(parents=True, exist_ok=True)
    written = []
    for name, payload in build().items():
        path = EXAMPLES / name
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8"
        )
        written.append(path)
    return written


if __name__ == "__main__":
    for path in write():
        print(f"wrote {path.relative_to(ROOT)}")
