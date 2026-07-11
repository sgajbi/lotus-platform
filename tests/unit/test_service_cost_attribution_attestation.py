from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess

import pytest

from automation.cost_attribution.application import build_service_cost_attribution
from automation.cost_attribution.attestation import (
    GitHubCostAttributionAttestationVerifier,
    TRUSTED_REPOSITORY,
    TRUSTED_SIGNER_WORKFLOW,
    TRUSTED_SOURCE_REF,
    VerifiedCostAttributionAttestation,
)
from automation.cost_attribution.domain import BillingExport, ServiceAllocationRequest
from automation.cost_attribution.qualification import qualify_service_cost_attribution


class ExportPort:
    def load(self) -> BillingExport:
        return BillingExport(
            authority="finops",
            export_type="normalized",
            export_version="v1",
            export_digest_sha256="a" * 64,
            exported_at_utc=datetime(2026, 7, 11, tzinfo=UTC),
            billing_period_start=datetime(2026, 7, 1, tzinfo=UTC).date(),
            billing_period_end=datetime(2026, 7, 31, tzinfo=UTC).date(),
            currency="USD",
            category_costs={
                "compute": Decimal("10.00"),
                "memory": Decimal("10.00"),
                "database": Decimal("10.00"),
                "network": Decimal("10.00"),
                "storage": Decimal("10.00"),
                "observability": Decimal("10.00"),
                "shared_platform": Decimal("10.00"),
            },
            source_total=Decimal("70.00"),
            completeness_status="complete",
            freshness_status="current",
            partial_period=False,
            late_adjustment=False,
        )


def _artifact() -> dict[str, object]:
    return build_service_cost_attribution(
        billing_export_port=ExportPort(),
        request=ServiceAllocationRequest(
            repository="lotus-idea",
            service_id="lotus-idea-api",
            environment="production-like",
            region="ap-southeast-1",
            source_commit_sha="b" * 40,
            source_ref=TRUSTED_SOURCE_REF,
            pipeline_run_id="run-1",
            resource_observation_schema_version="resource.v1",
            resource_observation_sha256="c" * 64,
            resource_observation_run_id="resource-1",
            shared_cost_numerator=Decimal("1"),
            shared_cost_denominator=Decimal("1"),
        ),
        generated_at_utc=datetime(2026, 7, 11, 1, tzinfo=UTC),
    )


def _attestation(**overrides: str) -> VerifiedCostAttributionAttestation:
    values = {
        "subject_sha256": "d" * 64,
        "repository": TRUSTED_REPOSITORY,
        "signer_workflow": TRUSTED_SIGNER_WORKFLOW,
        "source_ref": TRUSTED_SOURCE_REF,
        "source_commit_sha": "b" * 40,
    }
    values.update(overrides)
    return VerifiedCostAttributionAttestation(**values)


def _artifact_content() -> bytes:
    return (json.dumps(_artifact(), indent=2, sort_keys=True) + "\n").encode("utf-8")


def test_qualification_binds_service_resource_and_exact_attestation() -> None:
    artifact_content = _artifact_content()
    qualification = qualify_service_cost_attribution(
        artifact_content=artifact_content,
        attestation=_attestation(
            subject_sha256=hashlib.sha256(artifact_content).hexdigest()
        ),
        generated_at_utc=datetime(2026, 7, 11, 2, tzinfo=UTC),
        qualification_run_id="qual-1",
    )
    assert qualification["costAttributionCertified"] is True
    assert qualification["attestationVerified"] is True
    assert qualification["resourceObservation"]["sha256"] == "c" * 64
    assert qualification["supportedFeaturePromoted"] is False


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"repository": "other/repo"}, "repository is not trusted"),
        ({"signer_workflow": "other/workflow.yml"}, "workflow is not trusted"),
        ({"source_ref": "refs/heads/feature"}, "refs/heads/main"),
        ({"source_commit_sha": "e" * 40}, "commit does not match"),
    ],
)
def test_qualification_rejects_attestation_mismatch(
    overrides: dict[str, str], message: str
) -> None:
    artifact_content = _artifact_content()
    attestation = _attestation(
        subject_sha256=hashlib.sha256(artifact_content).hexdigest(),
        **overrides,
    )
    with pytest.raises(ValueError, match=message):
        qualify_service_cost_attribution(
            artifact_content=artifact_content,
            attestation=attestation,
            generated_at_utc=datetime(2026, 7, 11, 2, tzinfo=UTC),
            qualification_run_id="qual-1",
        )


def test_qualification_rejects_artifact_other_than_attested_subject() -> None:
    artifact_content = _artifact_content()
    tampered = artifact_content.replace(b'"currency": "USD"', b'"currency": "EUR"')

    with pytest.raises(ValueError, match="subject digest"):
        qualify_service_cost_attribution(
            artifact_content=tampered,
            attestation=_attestation(
                subject_sha256=hashlib.sha256(artifact_content).hexdigest()
            ),
            generated_at_utc=datetime(2026, 7, 11, 2, tzinfo=UTC),
            qualification_run_id="qual-1",
        )


def test_github_verifier_uses_exact_trust_policy(tmp_path: Path) -> None:
    artifact = tmp_path / "cost.json"
    artifact.write_text(json.dumps(_artifact()), encoding="utf-8")
    calls: list[list[str]] = []

    def run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return subprocess.CompletedProcess(
            command, 0, stdout='[{"verified":true}]', stderr=""
        )

    receipt = GitHubCostAttributionAttestationVerifier(command_runner=run).verify(
        artifact_path=artifact, source_commit_sha="b" * 40
    )
    assert calls[0][calls[0].index("--repo") + 1] == TRUSTED_REPOSITORY
    assert calls[0][calls[0].index("--signer-workflow") + 1] == TRUSTED_SIGNER_WORKFLOW
    assert calls[0][calls[0].index("--source-ref") + 1] == TRUSTED_SOURCE_REF
    assert receipt.subject_sha256 == hashlib.sha256(artifact.read_bytes()).hexdigest()


@pytest.mark.parametrize(
    ("result", "message"),
    [
        (subprocess.CompletedProcess([], 1, stdout="", stderr="secret"), "failed"),
        (subprocess.CompletedProcess([], 0, stdout="bad", stderr=""), "invalid JSON"),
        (subprocess.CompletedProcess([], 0, stdout="[]", stderr=""), "no attestations"),
    ],
)
def test_github_verifier_fails_closed_without_leaking_output(
    tmp_path: Path, result: subprocess.CompletedProcess[str], message: str
) -> None:
    artifact = tmp_path / "cost.json"
    artifact.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match=message) as captured:
        GitHubCostAttributionAttestationVerifier(
            command_runner=lambda *args, **kwargs: result
        ).verify(artifact_path=artifact, source_commit_sha="b" * 40)
    assert "secret" not in str(captured.value)
