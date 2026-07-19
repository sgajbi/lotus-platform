"""Contract tests for deterministic Node quality-tooling governance."""

from __future__ import annotations

import json
from pathlib import Path

from automation.quality_tooling.validate_node_quality_tooling import (
    validate_repository,
)

ROOT = Path(__file__).resolve().parents[3]


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_compliant_tool_package(repository: Path) -> None:
    _write_json(
        repository / "tools/api_governance/package.json",
        {
            "private": True,
            "engines": {"node": ">=20.17 <23"},
            "dependencies": {"@stoplight/spectral-cli": "6.16.1"},
        },
    )
    _write_json(
        repository / "tools/api_governance/package-lock.json",
        {"lockfileVersion": 3, "packages": {}},
    )
    runner = repository / "scripts/quality/openapi_spectral_gate.py"
    runner.parent.mkdir(parents=True, exist_ok=True)
    runner.write_text(
        'install = [npm_executable(), "ci", "--ignore-scripts"]\n'
        'binary = root / "node_modules" / ".bin" / "spectral"\n',
        encoding="utf-8",
    )


def _codes(repository: Path) -> set[str]:
    return {finding.code for finding in validate_repository(repository)}


def test_compliant_dedicated_quality_tool_package_passes(tmp_path: Path) -> None:
    _write_compliant_tool_package(tmp_path)

    assert validate_repository(tmp_path) == []


def test_blocking_workflow_rejects_npx_and_global_installs(tmp_path: Path) -> None:
    workflow = tmp_path / ".github/workflows/api-governance.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text(
        "steps:\n"
        "  - run: npx --yes @stoplight/spectral-cli lint openapi.json\n"
        "  - run: npm install -g @stoplight/spectral-cli\n",
        encoding="utf-8",
    )

    assert {"unbounded-npx", "global-npm-install"} <= _codes(tmp_path)


def test_quality_script_rejects_mutable_install(tmp_path: Path) -> None:
    script = tmp_path / "scripts/quality/openapi_gate.py"
    script.parent.mkdir(parents=True)
    script.write_text('command = ["npm", "install"]\n', encoding="utf-8")

    assert "mutable-npm-install" in _codes(tmp_path)


def test_tool_manifest_requires_lock_exact_versions_and_node_bounds(
    tmp_path: Path,
) -> None:
    _write_json(
        tmp_path / "tools/api_governance/package.json",
        {
            "engines": {"node": ">=20"},
            "devDependencies": {"@stoplight/spectral-cli": "^6.16.1"},
        },
    )

    assert {
        "missing-tool-lockfile",
        "non-exact-tool-dependency",
        "ungoverned-node-runtime",
        "missing-clean-install",
        "missing-local-binary",
    } <= _codes(tmp_path)


def test_report_only_inventory_is_not_treated_as_release_evidence(
    tmp_path: Path,
) -> None:
    report = tmp_path / "scripts/openapi_spectral_report.py"
    report.parent.mkdir(parents=True)
    report.write_text(
        'command = ["npx", "--yes", "@stoplight/spectral-cli@6.16.0"]\n',
        encoding="utf-8",
    )

    assert validate_repository(tmp_path) == []


def test_platform_guidance_owns_lock_backed_node_tooling_contract() -> None:
    skill = (
        ROOT / "codex/skills/lotus-ci-enforcement-governance/SKILL.md"
    ).read_text(encoding="utf-8")
    skill_reference = (
        ROOT
        / "codex/skills/lotus-ci-enforcement-governance/references/deterministic-node-quality-tooling.md"
    ).read_text(encoding="utf-8")
    standard = (
        ROOT
        / "platform-standards/Repository-Hygiene-and-Dependency-Model-Standard.md"
    ).read_text(encoding="utf-8")

    assert "references/deterministic-node-quality-tooling.md" in skill

    for content in (skill_reference, standard):
        assert "tools/api_governance/" in content
        assert "package-lock.json" in content
        assert "npm ci" in content
        assert "Unversioned `npx`" in content or "unversioned `npx`" in content
        assert "node_modules/.bin" in content
        assert "validate_node_quality_tooling.py" in content

    assert "Do not add Node to a Python-only service scaffold" in skill_reference
    assert "platform backend scaffold remains Python-only" in standard
