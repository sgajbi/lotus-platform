from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
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
FEATURE_METADATA = {
    "feature/core-banking-integration": (
        "0052CC", "Core banking integration requirements, implementation and independent acceptance",
    ),
    "feature/composite-performance": (
        "5319E7", "Cohesive composite performance requirements, implementation and acceptance",
    ),
}


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


def test_canonical_feature_metadata_is_declared_once():
    helper = _load_helper_module()
    catalogue = {name: (color, description) for name, color, description in helper.LABELS}
    assert len(catalogue) == len(helper.LABELS)
    assert {name: catalogue.get(name) for name in FEATURE_METADATA} == FEATURE_METADATA
    assert "core-banking-integration" not in catalogue  # Preserve the distinct legacy label.


@pytest.fixture
def remote_boundary(monkeypatch):
    """Controlled gh boundary; never sends a live GitHub request."""
    helper = _load_helper_module()
    labels = {f"unrelated/{index}": {"id": index, "color": "ffffff", "description": "Preserve"}
              for index in range(110)}
    labels["core-banking-integration"] = {
        "id": 110, "color": "0E8A16", "description": "Existing legacy selector",
    }
    labels["priority/P1"] = {"id": 111, "color": "fbca04", "description": "Priority"}
    labels["status/in_progress"] = {"id": 112, "color": "ffffff", "description": "Lifecycle"}
    issues = {
        1: {"core-banking-integration", "priority/P1"},
        2: {"status/in_progress"},
        3: {"core-banking-integration", "unrelated/0"},
    }
    calls = []
    refusal = {}

    def gh(command, *, check):
        assert check is True
        assert command[:3] == ["gh", "label", "create"]
        assert command[-1] == "--force"
        assert command[4::2] == ["--repo", "--color", "--description", "--force"]
        calls.append(command)
        name = command[3]
        if name == refusal.get("label"):
            raise subprocess.CalledProcessError(refusal["code"], command, stderr=refusal["reason"])
        label = labels.setdefault(name, {"id": len(labels)})
        label.update(color=command[7], description=command[9])

    monkeypatch.setattr(helper.subprocess, "run", gh)
    return helper, labels, issues, calls, refusal


@pytest.mark.parametrize("repository", ["sgajbi/lotus-platform", "sgajbi/lotus-report"])
def test_missing_feature_labels_are_created_in_explicit_repository(remote_boundary, repository):
    helper, labels, _, calls, _ = remote_boundary
    assert helper.main(["--repository", repository]) == 0
    assert all(command[5] == repository for command in calls)
    assert {name: (labels[name]["color"], labels[name]["description"])
            for name in FEATURE_METADATA if name in labels} == FEATURE_METADATA


def test_existing_labels_reconcile_idempotently_without_membership_or_legacy_loss(remote_boundary):
    helper, labels, issues, calls, _ = remote_boundary
    for index, name in enumerate(FEATURE_METADATA, 113):
        labels[name] = {"id": index, "color": "000000", "description": "Drift"}
    issues[1].add("feature/core-banking-integration")
    issues[2].add("feature/composite-performance")
    issues[3].update(FEATURE_METADATA)
    assert list(labels).index("feature/core-banking-integration") > 100
    originals = copy.deepcopy(labels)
    issue_memberships = copy.deepcopy(issues)
    assert helper.main(["--repo", "sgajbi/lotus-platform"]) == 0
    first_state = copy.deepcopy(labels)
    assert helper.main(["--repo", "sgajbi/lotus-platform"]) == 0
    assert labels == first_state
    assert issues == issue_memberships
    assert {name: (labels[name]["color"], labels[name]["description"])
            for name in FEATURE_METADATA} == FEATURE_METADATA
    assert all(labels[name]["id"] == originals[name]["id"] for name in FEATURE_METADATA)
    assert all(labels[name] == label for name, label in originals.items() if name not in FEATURE_METADATA)
    assert len(calls) == 2 * len(helper.LABELS)  # Semantic idempotence still sends checked requests.


def test_feature_preview_is_offline_and_includes_full_catalogue(monkeypatch, capsys):
    helper = _load_helper_module()

    def refuse_network(*args, **kwargs):
        pytest.fail("Dry-run called gh")

    monkeypatch.setattr(helper.subprocess, "run", refuse_network)
    assert helper.main(["--repo", "sgajbi/lotus-report", "--dry-run"]) == 0
    preview = capsys.readouterr().out
    for name, (color, description) in FEATURE_METADATA.items():
        assert f"gh label create {name} --repo sgajbi/lotus-report --color {color} --description {description} --force" in preview
    assert "gh label create issue-discovery" in preview
    assert "gh issue" not in preview


@pytest.mark.parametrize("code,reason", [
    (1, "HTTP 401"), (1, "HTTP 403"), (1, "HTTP 422 validation failed"),
    (1, "HTTP 500"), (4, "Authentication required"), (2, "Connection refused"),
])
def test_refusal_stops_without_success_or_later_feature_mutation(remote_boundary, capsys, code, reason):
    helper, labels, issues, calls, refusal = remote_boundary
    memberships = copy.deepcopy(issues)
    refusal.update(label="feature/core-banking-integration", code=code, reason=reason)
    with pytest.raises(subprocess.CalledProcessError) as raised:
        helper.main(["--repository", "sgajbi/lotus-report"])
    assert raised.value.returncode == code
    assert raised.value.stderr == reason
    assert calls[-1][3] == refusal["label"]
    assert "feature/composite-performance" not in labels
    assert issues == memberships
    assert "Ensured" not in capsys.readouterr().out
    assert "issue-discovery" in labels  # Earlier upserts survive; reconciliation is not atomic.


@pytest.mark.parametrize("refusal", [0, 4])
def test_native_cli_reports_checked_boundary_success_or_refusal(refusal):
    bootstrap = """
import json, runpy, subprocess, sys
path, repository, refusal = sys.argv[1:]
def boundary(command, *, check):
    assert check is True
    assert command[:3] == ['gh', 'label', 'create']
    assert command[5] == repository
    print(json.dumps(command))
    if command[3] == 'feature/core-banking-integration' and int(refusal):
        raise subprocess.CalledProcessError(int(refusal), command)
subprocess.run = boundary
sys.argv = [path, '--repository', repository]
runpy.run_path(path, run_name='__main__')
"""
    result = subprocess.run(
        [sys.executable, "-c", bootstrap, str(HELPER_PATH), "sgajbi/lotus-report", str(refusal)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == refusal, result.stdout + result.stderr
    commands = [json.loads(line) for line in result.stdout.splitlines() if line.startswith("[")]
    if refusal:
        assert commands[-1][3] == "feature/core-banking-integration"
        assert "Command failed with exit code 4" in result.stderr
        assert "Ensured" not in result.stdout
    else:
        assert {command[3]: (command[7], command[9]) for command in commands
                if command[3] in FEATURE_METADATA} == FEATURE_METADATA
        assert "Ensured" in result.stdout
