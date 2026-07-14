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
                ROOT
                / "platform-standards"
                / "templates"
                / "workflows"
                / "pr-auto-merge.template.yml",
                ROOT / ".github" / "workflows" / "merged-pr-main-releasability.yml",
                ROOT / ".github" / "workflows" / "pr-auto-merge.yml",
                ROOT / ".github" / "workflows" / "feature-lane.yml",
                ROOT / ".github" / "workflows" / "pr-merge-gate.yml",
                ROOT / ".github" / "workflows" / "main-releasability.yml",
                ROOT / ".github" / "workflows" / "platform-end-to-end-validation.yml",
                ROOT / ".github" / "workflows" / "api-vocabulary-governance.yml",
                ROOT / ".github" / "workflows" / "mesh-certification-gate.yml",
                ROOT
                / ".github"
                / "workflows"
                / "service-cost-attribution-evidence.yml",
            ]
        )
    }

    auto_merge_path = (
        "platform-standards/templates/workflows/pr-auto-merge.template.yml"
    )
    dispatch_path = "platform-standards/templates/workflows/merged-pr-main-releasability.template.yml"
    root_auto_merge_path = ".github/workflows/pr-auto-merge.yml"
    root_dispatch_path = ".github/workflows/merged-pr-main-releasability.yml"
    cost_attribution_path = ".github/workflows/service-cost-attribution-evidence.yml"
    for allowlisted_dispatch_path in {dispatch_path, root_dispatch_path}:
        assert allowlisted_dispatch_path in ALLOWLIST
        assert workflow_results[allowlisted_dispatch_path].ok is True
        assert workflow_results[allowlisted_dispatch_path].has_pull_request_target is True
        assert workflow_results[allowlisted_dispatch_path].write_permissions == {
            "actions": "write",
        }

    for allowlisted_auto_merge_path in {auto_merge_path, root_auto_merge_path}:
        assert allowlisted_auto_merge_path in ALLOWLIST
        assert workflow_results[allowlisted_auto_merge_path].ok is True
        assert workflow_results[allowlisted_auto_merge_path].has_pull_request_target is True
        assert workflow_results[allowlisted_auto_merge_path].write_permissions == {}

    assert cost_attribution_path in ALLOWLIST
    assert workflow_results[cost_attribution_path].ok is True
    assert workflow_results[cost_attribution_path].has_pull_request_target is False
    assert workflow_results[cost_attribution_path].write_permissions == {
        "attestations": "write",
        "id-token": "write",
    }

    for workflow_path, result in workflow_results.items():
        if workflow_path in {
            auto_merge_path,
            root_auto_merge_path,
            dispatch_path,
            root_dispatch_path,
            cost_attribution_path,
        }:
            continue
        assert result.has_pull_request_target is False
        assert result.unexpected_write_permissions == {}
        assert result.missing_permissions is False
        assert result.ok is True
