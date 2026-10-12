"""Offline credential check with explicitly supplied trust and revocation data."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from .verifier import Denial, VerificationInputs, verify_credential


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--credential")
    parser.add_argument("--jwks", type=Path, required=True)
    parser.add_argument("--issuer", required=True)
    parser.add_argument("--audience", required=True)
    parser.add_argument("--now", help="ISO-8601 aware evaluation time (default UTC now)")
    parser.add_argument("--revocations", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        jwks = json.loads(args.jwks.read_text(encoding="utf-8"))
        revocations = json.loads(args.revocations.read_text(encoding="utf-8"))
        sets = [revocations[name] for name in ("credential_ids", "subjects")]
        if not all(isinstance(items, list) and all(isinstance(item, str) for item in items) for items in sets):
            raise ValueError("invalid revocation sets")
        now = datetime.fromisoformat(args.now.replace("Z", "+00:00")) if args.now else datetime.now(timezone.utc)
        inputs = VerificationInputs(
            expected_issuer=args.issuer, expected_audience=args.audience,
            jwks=jwks, now=now,
            revoked_credential_ids=frozenset(sets[0]), revoked_subjects=frozenset(sets[1]),
            revocation_valid_until=datetime.fromisoformat(revocations["valid_until"].replace("Z", "+00:00")),
        )
        result = verify_credential(args.credential, inputs)
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        result = Denial("grant_store_unavailable", unauthenticated=False)
    if isinstance(result, Denial):
        print(f"denied: {result.denial_class}")
        return 1
    # Never print signed claims, credentials, subjects or provider exception text.
    print("verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
