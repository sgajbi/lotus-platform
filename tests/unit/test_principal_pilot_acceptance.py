"""The principal pilot-acceptance record binds each claimed proof to a test that exists.

A record that names tests is only evidence while those tests exist and cover the class they are
cited for. These checks make a renamed or deleted verifier test, a missing denial class, or a
live boundary quietly flipped to `true` fail here rather than being discovered when the record is
read as evidence.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORD_PATH = ROOT / "platform-contracts" / "principal-resolution" / "pilot-acceptance.v1.json"
RFC_PATH = ROOT / "rfcs" / "RFC-0109-lotus-production-principal-and-capability-resolution.md"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
DENIAL_CLASSES = (
    "missing_credential",
    "malformed_credential",
    "expired_credential",
    "wrong_audience",
    "wrong_issuer",
    "unknown_key_id",
    "revoked_principal",
    "present_but_unverified",
    "tenant_not_a_member",
    "capability_not_granted",
    "portfolio_outside_scope",
    "delegated_capability_not_held_by_user",
    "grant_store_unavailable",
)


def _record() -> dict:
    return json.loads(RECORD_PATH.read_text(encoding="utf-8"))


def _test_functions(path: Path) -> set[str]:
    return set(re.findall(r"^def (test_[A-Za-z0-9_]+)\(", path.read_text(encoding="utf-8"), re.M))


def test_every_cited_platform_test_exists_in_the_named_file() -> None:
    record = _record()
    evidence_file = ROOT / record["platform_evidence_file"]
    functions = _test_functions(evidence_file)

    cited = {name for proof in record["finite_acceptance"] for name in proof["platform_evidence"]}
    assert cited, "the record cites no platform tests at all"
    missing = sorted(cited - functions)
    assert missing == [], f"cited tests absent from {evidence_file.name}: {missing}"


def test_every_denial_class_has_a_measured_proof() -> None:
    """All thirteen, not a selection -- and each measured by at least one test here."""
    record = _record()
    proofs = {proof["proof"]: proof for proof in record["finite_acceptance"]}

    for denial in DENIAL_CLASSES:
        matching = [proof for name, proof in proofs.items() if name.startswith(denial)]
        assert matching, f"no finite-acceptance entry for {denial}"
        assert matching[0]["platform_evidence"], f"{denial} is claimed, not measured"


def test_consumer_only_proofs_say_so_and_are_not_counted_as_platform_evidence() -> None:
    record = _record()
    consumer_only = [proof for proof in record["finite_acceptance"] if not proof["platform_evidence"]]

    assert len(consumer_only) == 3
    assert all(proof["consumer"] == "claimed" and proof.get("note") for proof in consumer_only)
    assert "not certify" in record["consumer_claims_note"]


def test_the_pilot_and_its_revisions_are_exact() -> None:
    record = _record()
    pilot = record["pilot"]

    assert pilot["consumer"] == "lotus-workbench"
    assert FULL_SHA.fullmatch(pilot["merged_revision"])
    assert FULL_SHA.fullmatch(pilot["consumer_proof_revision"])
    assert pilot["consumer_proof_files"], "a pilot with no named proof files is a pilot by assertion"
    assert all(path.startswith("tests/") for path in pilot["consumer_proof_files"])


def test_live_boundaries_all_stay_false_until_separately_evidenced() -> None:
    record = _record()

    assert record["live_boundaries"] and all(
        value is False for value in record["live_boundaries"].values()
    ), record["live_boundaries"]


def test_ownership_names_the_declined_owner_and_the_corrected_one_consistently() -> None:
    record = _record()
    ownership = record["ownership"]
    rfc = RFC_PATH.read_text(encoding="utf-8")

    assert "lotus-core" in ownership["declined"]
    assert "lotus-platform identity and access governance" in ownership["grant_store_implementation"]
    section = rfc.split("### 2. Who owns the grant store")[1].split("### 3.")[0]
    assert "**Corrected 2026-09-13.**" in section
    assert "declined on 2026-09-08" in section
    assert "`lotus-platform` identity and access governance" in section
    assert "pilot-acceptance.v1.json" in rfc
