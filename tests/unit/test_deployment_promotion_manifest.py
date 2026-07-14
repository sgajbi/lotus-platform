from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "automation" / "validate_deployment_promotion_manifest.py"
EXAMPLE_PATH = (
    ROOT
    / "platform-contracts"
    / "deployment-promotion"
    / "examples"
    / "lotus-archive-deployment-promotion.valid.json"
)


def _validator():
    spec = importlib.util.spec_from_file_location(
        "validate_deployment_promotion_manifest", VALIDATOR_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _manifest() -> dict:
    return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))


def test_valid_example_accepts_lotus_archive_first_proof_set() -> None:
    validator = _validator()

    assert validator.validate_all_manifests() == []


def test_rejects_mutable_release_and_deployment_tags() -> None:
    manifest = _manifest()
    manifest["release_evidence"]["image_ref"] = (
        "ghcr.io/sgajbi/lotus-archive:latest@sha256:"
        "1111111111111111111111111111111111111111111111111111111111111111"
    )
    manifest["environments"][0]["deployed_image_ref"] = manifest["release_evidence"][
        "image_ref"
    ]

    errors = _validator().validate_manifest(manifest)

    assert "release_evidence.image_ref must use image@sha256:<digest> without a tag" in errors
    assert "environments[0] staging: mutable image tag is not allowed" in errors


def test_rejects_missing_digest_references() -> None:
    manifest = _manifest()
    manifest["release_evidence"]["image_ref"] = "ghcr.io/sgajbi/lotus-archive:latest"
    manifest["environments"][0]["deployed_image_ref"] = "ghcr.io/sgajbi/lotus-archive"

    errors = _validator().validate_manifest(manifest)

    assert "release_evidence.image_ref must use image@sha256:<digest> without a tag" in errors
    assert (
        "environments[0] staging: deployed_image_ref must use image@sha256:<digest> "
        "without a tag"
    ) in errors


def test_rejects_release_evidence_and_deployed_digest_mismatch() -> None:
    manifest = _manifest()
    manifest["environments"][0]["deployed_digest"] = (
        "sha256:2222222222222222222222222222222222222222222222222222222222222222"
    )
    manifest["environments"][0]["release_evidence_image_digest"] = (
        "sha256:2222222222222222222222222222222222222222222222222222222222222222"
    )

    errors = _validator().validate_manifest(manifest)

    assert "environments[0] staging: deployed_image_ref digest mismatch" in errors
    assert "environments[0] staging: deployed_digest must match release evidence" in errors
    assert (
        "environments[0] staging: release_evidence_image_digest must match release evidence"
        in errors
    )


def test_rejects_rebuild_per_environment_promotion() -> None:
    manifest = _manifest()
    manifest["promotion_policy"]["rebuild_between_environments_allowed"] = True
    manifest["environments"][0]["rebuilt_in_environment"] = True

    errors = _validator().validate_manifest(manifest)

    assert "promotion_policy.rebuild_between_environments_allowed must be false" in errors
    assert "environments[0] staging: rebuilt_in_environment must be false" in errors


def test_allows_explicit_out_of_scope_environment_but_rejects_fake_proof() -> None:
    manifest = _manifest()
    production = manifest["environments"][1]
    production["deployed_digest"] = manifest["release_evidence"]["image_digest"]
    production["out_of_scope_reason"] = "missing"

    errors = _validator().validate_manifest(manifest)

    assert "environments[1] production: out_of_scope must not declare deployed image proof" in errors
    assert "environments[1] production: out_of_scope_reason is required" in errors


def test_rejects_production_certification_claim_without_live_proof() -> None:
    manifest = _manifest()
    manifest["production_certification_claimed"] = True

    errors = _validator().validate_manifest(manifest)

    assert (
        "production_certification_claimed must remain false until live deployment proof exists"
        in errors
    )


def test_schema_rejects_unknown_fields(tmp_path: Path) -> None:
    validator = _validator()
    manifest = _manifest()
    manifest["unexpected"] = "not governed"
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")

    errors = validator.validate_manifest_path(path)

    assert any("Additional properties are not allowed" in error for error in errors)
