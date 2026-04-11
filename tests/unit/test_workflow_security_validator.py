from __future__ import annotations

from automation.validate_workflow_security import ALLOWLIST, ROOT, validate_workflow


def test_allowlisted_auto_merge_template_is_the_only_pull_request_target_exception() -> None:
    workflow_results = {
        result.workflow_path: result
        for result in (
            validate_workflow(path)
            for path in [
                ROOT / "platform-standards" / "templates" / "workflows" / "pr-auto-merge.template.yml",
                ROOT / ".github" / "workflows" / "feature-lane.yml",
                ROOT / ".github" / "workflows" / "pr-merge-gate.yml",
                ROOT / ".github" / "workflows" / "main-releasability.yml",
                ROOT / ".github" / "workflows" / "platform-end-to-end-validation.yml",
                ROOT / ".github" / "workflows" / "api-vocabulary-governance.yml",
            ]
        )
    }

    auto_merge_path = "platform-standards/templates/workflows/pr-auto-merge.template.yml"
    assert auto_merge_path in ALLOWLIST
    assert workflow_results[auto_merge_path].ok is True
    assert workflow_results[auto_merge_path].has_pull_request_target is True
    assert workflow_results[auto_merge_path].write_permissions == {
        "contents": "write",
        "pull-requests": "write",
    }

    for workflow_path, result in workflow_results.items():
        if workflow_path == auto_merge_path:
            continue
        assert result.has_pull_request_target is False
        assert result.unexpected_write_permissions == {}
        assert result.missing_permissions is False
        assert result.ok is True
