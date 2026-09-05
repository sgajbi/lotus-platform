from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
HELPER_PATH = (
    ROOT
    / "codex"
    / "skills"
    / "lotus-app-issue-discovery"
    / "scripts"
    / "ensure_issue_discovery_labels.py"
)


def _load_helper_module():
    spec = importlib.util.spec_from_file_location("ensure_issue_discovery_labels", HELPER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("repository_flag", ["--repository", "--repo"])
def test_label_helper_accepts_canonical_flag_and_compatibility_alias(
    repository_flag: str, capsys: pytest.CaptureFixture[str]
) -> None:
    helper = _load_helper_module()

    assert helper.main([repository_flag, "sgajbi/lotus-platform", "--dry-run"]) == 0

    output = capsys.readouterr().out
    assert "gh label create issue-discovery --repo sgajbi/lotus-platform" in output
    assert "Ensured" in output


def test_label_helper_help_documents_both_repository_flags(
    capsys: pytest.CaptureFixture[str],
) -> None:
    helper = _load_helper_module()

    with pytest.raises(SystemExit, match="0"):
        helper.main(["--help"])

    help_text = capsys.readouterr().out
    assert "--repository" in help_text
    assert "--repo" in help_text
