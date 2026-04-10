from __future__ import annotations

from automation.validate_workflow_action_runtime import (
    ACTION_MAJOR_BASELINE,
    ROOT,
    validate_workflow,
)


def test_platform_workflows_and_templates_meet_core_action_runtime_baseline() -> None:
    workflow_paths = [
        ROOT / ".github" / "workflows" / "feature-lane.yml",
        ROOT / ".github" / "workflows" / "pr-merge-gate.yml",
        ROOT / ".github" / "workflows" / "main-releasability.yml",
        ROOT / ".github" / "workflows" / "platform-end-to-end-validation.yml",
        ROOT / ".github" / "workflows" / "api-vocabulary-governance.yml",
        ROOT / "platform-standards" / "templates" / "workflows" / "feature-lane.backend.template.yml",
        ROOT / "platform-standards" / "templates" / "workflows" / "pr-merge-gate.backend.template.yml",
        ROOT / "platform-standards" / "templates" / "workflows" / "main-releasability.backend.template.yml",
    ]

    results = {result.workflow_path: result for result in map(validate_workflow, workflow_paths)}

    assert ACTION_MAJOR_BASELINE["actions/checkout"] == 6
    assert ACTION_MAJOR_BASELINE["actions/setup-python"] == 6
    assert ACTION_MAJOR_BASELINE["actions/setup-node"] == 5
    assert ACTION_MAJOR_BASELINE["actions/upload-artifact"] == 5

    for workflow_path, result in results.items():
        assert result.ok is True, f"{workflow_path} findings: {result.findings}"
