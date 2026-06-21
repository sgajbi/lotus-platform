from __future__ import annotations

from automation.validate_workflow_security import ALLOWLIST, ROOT, validate_workflow


def test_allowlisted_templates_are_the_only_pull_request_target_exceptions() -> None:
    workflow_results = {
        result.workflow_path: result
        for result in (
            validate_workflow(path)
            for path in [
                ROOT
                / "platform-standards"
                / "templates"
                / "workflows"
                / "merged-pr-main-releasability.template.yml",
                ROOT / "platform-standards" / "templates" / "workflows" / "pr-auto-merge.template.yml",
                ROOT / ".github" / "workflows" / "feature-lane.yml",
                ROOT / ".github" / "workflows" / "pr-merge-gate.yml",
                ROOT / ".github" / "workflows" / "main-releasability.yml",
                ROOT / ".github" / "workflows" / "platform-end-to-end-validation.yml",
                ROOT / ".github" / "workflows" / "api-vocabulary-governance.yml",
                ROOT / ".github" / "workflows" / "mesh-certification-gate.yml",
            ]
        )
    }

    auto_merge_path = "platform-standards/templates/workflows/pr-auto-merge.template.yml"
    dispatch_path = "platform-standards/templates/workflows/merged-pr-main-releasability.template.yml"
    assert dispatch_path in ALLOWLIST
    assert workflow_results[dispatch_path].ok is True
    assert workflow_results[dispatch_path].has_pull_request_target is True
    assert workflow_results[dispatch_path].write_permissions == {
        "actions": "write",
    }

    assert auto_merge_path in ALLOWLIST
    assert workflow_results[auto_merge_path].ok is True
    assert workflow_results[auto_merge_path].has_pull_request_target is True
    assert workflow_results[auto_merge_path].write_permissions == {}

    for workflow_path, result in workflow_results.items():
        if workflow_path in {auto_merge_path, dispatch_path}:
            continue
        assert result.has_pull_request_target is False
        assert result.unexpected_write_permissions == {}
        assert result.missing_permissions is False
        assert result.ok is True
