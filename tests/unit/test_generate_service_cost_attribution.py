from __future__ import annotations

import json
from pathlib import Path

from automation.generate_service_cost_attribution import main


def test_cli_generates_atomic_source_safe_artifact(tmp_path: Path) -> None:
    source = tmp_path / "billing.json"
    source.write_text(
        json.dumps(
            {
                "authority": "governed-finops-export",
                "exportType": "normalized_service_billing_export",
                "exportVersion": "v1",
                "exportedAtUtc": "2026-07-11T01:00:00Z",
                "billingPeriodStart": "2026-07-01",
                "billingPeriodEnd": "2026-07-31",
                "currency": "SGD",
                "categoryCosts": {
                    name: "10.00"
                    for name in (
                        "compute",
                        "memory",
                        "database",
                        "network",
                        "storage",
                        "observability",
                        "shared_platform",
                    )
                },
                "sourceTotal": "70.00",
                "completenessStatus": "complete",
                "freshnessStatus": "current",
                "partialPeriod": False,
                "lateAdjustment": False,
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "evidence" / "cost.json"
    result = main(
        [
            "--billing-export",
            str(source),
            "--output",
            str(output),
            "--repository",
            "lotus-idea",
            "--service-id",
            "lotus-idea-api",
            "--environment",
            "production-like",
            "--region",
            "ap-southeast-1",
            "--source-commit-sha",
            "a" * 40,
            "--source-ref",
            "refs/heads/main",
            "--pipeline-run-id",
            "run-1",
            "--generated-at-utc",
            "2026-07-11T02:00:00Z",
            "--resource-observation-schema-version",
            "resource.v1",
            "--resource-observation-sha256",
            "b" * 64,
            "--resource-observation-run-id",
            "resource-1",
            "--shared-cost-numerator",
            "1",
            "--shared-cost-denominator",
            "1",
        ]
    )
    assert result == 0
    artifact = json.loads(output.read_text(encoding="utf-8"))
    assert artifact["currency"] == "SGD"
    assert artifact["costAttributionCertified"] is False
    assert artifact["certificationBlockers"] == ["artifact_attestation_missing"]
    assert not list(output.parent.glob(f".{output.name}.*"))
    assert source.exists()


def test_workflow_is_manual_main_only_protected_and_attests_exact_artifact() -> None:
    root = Path(__file__).resolve().parents[2]
    workflow = (
        root / ".github/workflows/service-cost-attribution-evidence.yml"
    ).read_text(encoding="utf-8")
    actionlint_config = (root / ".github/actionlint.yaml").read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "schedule:" not in workflow
    assert "github.ref == 'refs/heads/main'" in workflow
    assert "runs-on: [self-hosted, lotus-finops-evidence]" in workflow
    assert "self-hosted-runner:" in actionlint_config
    assert "lotus-finops-evidence" in actionlint_config
    assert "environment: finops-production-evidence" in workflow
    assert "id-token: write" in workflow
    assert "attestations: write" in workflow
    assert "actions/attest-build-provenance@v3" in workflow
    assert (
        "subject-path: output/cost-attribution/service-cost-attribution.json"
        in workflow
    )
    assert "path: output/cost-attribution/service-cost-attribution.json" in workflow
    assert "LOTUS_FINOPS_NORMALIZED_EXPORT_PATH" in workflow
    run_block = workflow.split("run: |", maxsplit=1)[1].split(
        "- name: Attest exact attribution artifact", maxsplit=1
    )[0]
    assert "${{ inputs." not in run_block
    assert '--repository "${SERVICE_REPOSITORY}"' in run_block
