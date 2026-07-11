from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import subprocess


TRUSTED_REPOSITORY = "sgajbi/lotus-platform"
TRUSTED_SIGNER_WORKFLOW = (
    "sgajbi/lotus-platform/.github/workflows/service-cost-attribution-evidence.yml"
)
TRUSTED_SOURCE_REF = "refs/heads/main"


@dataclass(frozen=True)
class VerifiedCostAttributionAttestation:
    subject_sha256: str
    repository: str
    signer_workflow: str
    source_ref: str
    source_commit_sha: str


class GitHubCostAttributionAttestationVerifier:
    def __init__(
        self,
        *,
        command_runner: Callable[
            ..., subprocess.CompletedProcess[str]
        ] = subprocess.run,
        timeout_seconds: int = 60,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._command_runner = command_runner
        self._timeout_seconds = timeout_seconds

    def verify(
        self, *, artifact_path: Path, source_commit_sha: str
    ) -> VerifiedCostAttributionAttestation:
        if not artifact_path.is_file():
            raise ValueError("cost-attribution artifact path must be a file")
        if not source_commit_sha.strip():
            raise ValueError("source_commit_sha must not be blank")
        command = [
            "gh",
            "attestation",
            "verify",
            str(artifact_path),
            "--repo",
            TRUSTED_REPOSITORY,
            "--signer-workflow",
            TRUSTED_SIGNER_WORKFLOW,
            "--source-ref",
            TRUSTED_SOURCE_REF,
            "--source-digest",
            source_commit_sha,
            "--format",
            "json",
        ]
        try:
            result = self._command_runner(
                command,
                capture_output=True,
                text=True,
                timeout=self._timeout_seconds,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ValueError(
                "cost-attribution attestation verification unavailable"
            ) from exc
        if result.returncode != 0:
            raise ValueError("cost-attribution attestation verification failed")
        try:
            verified = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "cost-attribution attestation verification returned invalid JSON"
            ) from exc
        if not isinstance(verified, list) or not verified:
            raise ValueError(
                "cost-attribution attestation verification returned no attestations"
            )
        return VerifiedCostAttributionAttestation(
            subject_sha256=hashlib.sha256(artifact_path.read_bytes()).hexdigest(),
            repository=TRUSTED_REPOSITORY,
            signer_workflow=TRUSTED_SIGNER_WORKFLOW,
            source_ref=TRUSTED_SOURCE_REF,
            source_commit_sha=source_commit_sha,
        )
