from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_main_releasability_template_emits_release_evidence_artifacts() -> None:
    template = (
        ROOT / "platform-standards" / "templates" / "workflows" / "main-releasability.backend.template.yml"
    ).read_text(encoding="utf-8")
    standard = (
        ROOT / "platform-standards" / "Release-Evidence-and-SBOM-Foundation-Standard.md"
    ).read_text(encoding="utf-8")
    contract = (ROOT / "platform-standards" / "Backend-CI-Lane-Template-Contract.md").read_text(
        encoding="utf-8"
    )

    assert "Generate dependency SBOM" in template
    assert (
        "./.venv/bin/cyclonedx-py environment --output-format JSON --output-file sbom.cdx.json"
        in template
    )
    assert "Generate release metadata manifest" in template
    assert "release-evidence.json" in template
    assert "main-releasability-release-evidence" in template

    assert "Dependency SBOM Baseline" in standard
    assert "sbom.cdx.json" in standard
    assert "release-evidence.json" in standard
    assert "main-releasability-release-evidence" in standard

    assert "Required retained artifacts" in contract
    assert "main-releasability-release-evidence" in contract
    assert "sbom.cdx.json" in contract
    assert "release-evidence.json" in contract
