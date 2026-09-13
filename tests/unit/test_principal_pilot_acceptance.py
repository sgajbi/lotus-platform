"""The principal pilot-acceptance record binds each claimed proof to a test that exists.

A record that names tests is only evidence while those tests exist and cover the class they are
cited for. These checks make a renamed or deleted verifier test, a missing denial class, or a
live boundary quietly flipped to `true` fail here rather than being discovered when the record is
read as evidence.
"""

from __future__ import annotations

import json
import re
import subprocess
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORD_PATH = ROOT / "platform-contracts" / "principal-resolution" / "pilot-acceptance.v1.json"
RFC_PATH = ROOT / "rfcs" / "RFC-0109-lotus-production-principal-and-capability-resolution.md"
CONTRACT_PATH = ROOT / "platform-contracts" / "principal-resolution" / "resolved-principal.v1.json"
SCHEMA_PATH = ROOT / "platform-contracts" / "principal-resolution" / "resolved-principal.schema.json"
README_PATH = ROOT / "platform-contracts" / "principal-resolution" / "README.md"
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


def _consumer_git_tree_errors(receipt: dict, checkout: Path) -> list[str]:
    """Verify consumer-claimed files against the immutable checked-out tree."""
    revision = receipt.get("revision")
    if not isinstance(revision, str) or not FULL_SHA.fullmatch(revision):
        return ["receipt revision is not an immutable Git revision"]
    if not checkout.is_dir():
        return [f"pinned consumer checkout is unavailable: {checkout}"]
    exists = subprocess.run(
        ["git", "-C", str(checkout), "cat-file", "-e", f"{revision}^{{commit}}"],
        capture_output=True,
        text=True,
    )
    if exists.returncode != 0:
        return ["receipt revision is absent from the pinned consumer checkout"]

    errors: list[str] = []
    for path, expected_blob in receipt.get("proof_files", {}).items():
        tree = subprocess.run(
            ["git", "-C", str(checkout), "ls-tree", revision, "--", path],
            capture_output=True,
            text=True,
        )
        entries = tree.stdout.rstrip("\n").split("\n") if tree.stdout else []
        if len(entries) != 1:
            errors.append(f"receipt proof file is absent from consumer tree: {path}")
            continue
        fields = entries[0].split(maxsplit=3)
        if len(fields) != 4 or fields[1] != "blob" or fields[2] != expected_blob:
            errors.append(f"receipt proof blob does not match consumer tree: {path}")
    return errors


def _pilot_evidence_errors(record: dict) -> list[str]:
    pilot = record["pilot"]
    receipt_path = RECORD_PATH.parent / pilot.get("consumer_proof_receipt", "")
    errors: list[str] = []
    if pilot.get("consumer_repository") != "sgajbi/lotus-workbench":
        errors.append("consumer repository is not the accepted Workbench pilot")
    if not FULL_SHA.fullmatch(str(pilot.get("consumer_proof_revision", ""))):
        errors.append("consumer proof revision is not immutable")
    if not receipt_path.is_file():
        return [*errors, "consumer proof receipt is missing"]
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("repository") != pilot.get("consumer_repository"):
        errors.append("receipt repository does not match pilot")
    if receipt.get("revision") != pilot.get("consumer_proof_revision"):
        errors.append("receipt revision does not match pilot")
    proof_files = receipt.get("proof_files")
    if not isinstance(proof_files, dict) or set(proof_files) != set(pilot.get("consumer_proof_files", [])):
        errors.append("receipt proof files do not exactly match pilot")
    elif not all(FULL_SHA.fullmatch(str(blob)) for blob in proof_files.values()):
        errors.append("receipt contains a non-Git proof object")
    else:
        errors.extend(_consumer_git_tree_errors(receipt, ROOT.parent / "lotus-workbench"))
    return errors


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
    assert _pilot_evidence_errors(record) == []


def test_the_pilot_rejects_a_wrong_revision_or_missing_proof_file() -> None:
    record = _record()
    wrong_revision = deepcopy(record)
    wrong_revision["pilot"]["consumer_proof_revision"] = "0" * 40
    assert "receipt revision does not match pilot" in _pilot_evidence_errors(wrong_revision)

    missing_file = deepcopy(record)
    missing_file["pilot"]["consumer_proof_files"] = missing_file["pilot"]["consumer_proof_files"][:-1]
    assert "receipt proof files do not exactly match pilot" in _pilot_evidence_errors(missing_file)


def test_receipt_rejects_a_blob_that_is_not_in_the_pinned_consumer_tree() -> None:
    receipt = json.loads(
        (RECORD_PATH.parent / _record()["pilot"]["consumer_proof_receipt"]).read_text(
            encoding="utf-8"
        )
    )
    receipt["proof_files"] = dict(receipt["proof_files"])
    receipt["proof_files"]["tests/unit/principal-credential.test.ts"] = "0" * 40

    errors = _consumer_git_tree_errors(receipt, ROOT.parent / "lotus-workbench")

    assert "receipt proof blob does not match consumer tree: tests/unit/principal-credential.test.ts" in errors


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
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    readme = README_PATH.read_text(encoding="utf-8")
    grant_store = contract["grantStore"]
    assert grant_store["implementationOwnedBy"] == "lotus-platform identity and access governance"
    assert grant_store["hostingService"] is None
    assert grant_store["hostingServiceDesignated"] is False
    assert grant_store["operationsOwnedBy"] == "bank security authority / identity-provider operator"
    assert "tenant-membership owner" not in schema
    assert "tenant-membership owner" not in contract["nonGoals"]
    assert "still undesignated" in readme
    assert "once one is designated" in section
