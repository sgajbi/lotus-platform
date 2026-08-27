from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

from automation import canonical_orphan_retirement as retirement

CONTAINER_ID = "a" * 64
CONTAINER_NAME = "lotus-gateway-lotus-gateway-1"
COMPOSE_PROJECT = "lotus-gateway"
LABELLED_WORKING_DIR = r"C:\Users\Sandeep\projects\lotus-gateway-deleted"
EXPECTED_WORKING_DIR = r"C:\Users\Sandeep\projects\lotus-gateway"
PROJECTS_ROOT = r"C:\Users\Sandeep\projects"
WORKBENCH_REPO = r"C:\Users\Sandeep\projects\lotus-workbench"


def _plan(
    now: datetime,
    *,
    ownership_state: str = retirement.MISSING_LABELLED_CHECKOUT,
    resource_type: str | None = None,
) -> dict[str, object]:
    conflict: dict[str, object] = {
        "id": CONTAINER_ID,
        "name": CONTAINER_NAME,
        "compose_project": COMPOSE_PROJECT,
        "compose_working_dir": LABELLED_WORKING_DIR,
        "expected_working_dir": "c:/users/sandeep/projects/lotus-gateway",
        "conflict_reason": "compose_project_owned_by_different_working_directory",
        "ownership_state": ownership_state,
    }
    if resource_type:
        conflict["resource_type"] = resource_type
    return {
        "schema_version": retirement.PLAN_SCHEMA_VERSION,
        "generated_at": now.isoformat(),
        "selection_policy": retirement.SELECTION_POLICY,
        "ownership_conflicts": [conflict],
    }


def _live_container() -> dict[str, object]:
    return {
        "Id": CONTAINER_ID,
        "Name": f"/{CONTAINER_NAME}",
        "Config": {
            "Labels": {
                "com.docker.compose.project": COMPOSE_PROJECT,
                "com.docker.compose.project.working_dir": LABELLED_WORKING_DIR,
            }
        },
        "State": {"Running": True},
    }


def _validate(
    *,
    plan: dict[str, object] | None = None,
    now: datetime | None = None,
    live_container: dict[str, object] | None = None,
    registered_worktrees: set[str] | None = None,
    path_exists=lambda _: False,
) -> dict[str, object]:
    validation_now = now or datetime.now(timezone.utc)
    validation_plan = plan or _plan(validation_now)
    return retirement.validate_orphan_retirement(
        plan=validation_plan,
        plan_generated_at=datetime.fromisoformat(str(validation_plan["generated_at"])),
        now=validation_now,
        max_plan_age_seconds=300,
        container_id=CONTAINER_ID,
        container_name=CONTAINER_NAME,
        compose_project=COMPOSE_PROJECT,
        labelled_working_dir=LABELLED_WORKING_DIR,
        expected_working_dir=EXPECTED_WORKING_DIR,
        projects_root=PROJECTS_ROOT,
        workbench_repo_path=WORKBENCH_REPO,
        live_container=live_container or _live_container(),
        registered_worktrees=registered_worktrees or set(),
        path_exists=path_exists,
    )


def test_validation_approves_only_the_exact_missing_checkout_container() -> None:
    checks = _validate()

    assert checks == {
        "plan_fresh": True,
        "exact_plan_target": True,
        "canonical_project": True,
        "live_identity_matches": True,
        "labelled_checkout_absent": True,
        "labelled_checkout_not_registered": True,
        "scope": "exact_container_only",
    }


def test_documented_repository_root_cli_is_executable() -> None:
    result = subprocess.run(
        [sys.executable, "automation/canonical_orphan_retirement.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "Retire one proven orphan container" in result.stdout


@pytest.mark.parametrize(
    ("field", "replacement", "expected_message"),
    [
        ("id", "b" * 64, "exactly one ownership conflict"),
        ("name", "wrong-container", "container name"),
        ("compose_project", "lotus-advise", "Compose project"),
        ("compose_working_dir", r"C:\wrong", "labelled working directory"),
        ("expected_working_dir", r"C:\wrong", "expected working directory"),
    ],
)
def test_validation_refuses_plan_identity_drift(
    field: str, replacement: str, expected_message: str
) -> None:
    now = datetime.now(timezone.utc)
    plan = _plan(now)
    conflict = plan["ownership_conflicts"][0]
    assert isinstance(conflict, dict)
    conflict[field] = replacement

    with pytest.raises(retirement.OrphanRetirementRefused, match=expected_message):
        _validate(plan=plan, now=now)


@pytest.mark.parametrize(
    "ownership_state",
    ["active_foreign_owner", "unproven_resource_only_owner"],
)
def test_validation_refuses_non_orphan_ownership_states(ownership_state: str) -> None:
    now = datetime.now(timezone.utc)

    with pytest.raises(retirement.OrphanRetirementRefused, match="only a missing"):
        _validate(plan=_plan(now, ownership_state=ownership_state), now=now)


def test_validation_refuses_resource_only_conflict() -> None:
    now = datetime.now(timezone.utc)

    with pytest.raises(retirement.OrphanRetirementRefused, match="resource-only"):
        _validate(plan=_plan(now, resource_type="volume"), now=now)


def test_validation_refuses_stale_or_future_plan() -> None:
    now = datetime.now(timezone.utc)
    stale = _plan(now - timedelta(minutes=6))
    future = _plan(now + timedelta(minutes=1))

    with pytest.raises(retirement.OrphanRetirementRefused, match="stale"):
        _validate(plan=stale, now=now)
    with pytest.raises(retirement.OrphanRetirementRefused, match="future"):
        _validate(plan=future, now=now)


def test_validation_refuses_reappeared_or_registered_checkout() -> None:
    with pytest.raises(retirement.OrphanRetirementRefused, match="now exists"):
        _validate(path_exists=lambda value: value == LABELLED_WORKING_DIR)
    with pytest.raises(
        retirement.OrphanRetirementRefused, match="registered Git worktree"
    ):
        _validate(registered_worktrees={LABELLED_WORKING_DIR})


@pytest.mark.parametrize(
    ("field", "replacement", "expected_message"),
    [
        ("Id", "b" * 64, "live container ID"),
        ("Name", "/wrong-container", "live container name"),
    ],
)
def test_validation_refuses_live_container_identity_drift(
    field: str, replacement: str, expected_message: str
) -> None:
    live = _live_container()
    live[field] = replacement

    with pytest.raises(retirement.OrphanRetirementRefused, match=expected_message):
        _validate(live_container=live)


def test_validation_probes_the_exact_live_docker_label() -> None:
    now = datetime.now(timezone.utc)
    plan = _plan(now)
    conflict = plan["ownership_conflicts"][0]
    assert isinstance(conflict, dict)
    conflict["compose_working_dir"] = "/tmp/ActiveCheckout"
    live = _live_container()
    labels = live["Config"]
    assert isinstance(labels, dict)
    config_labels = labels["Labels"]
    assert isinstance(config_labels, dict)
    config_labels["com.docker.compose.project.working_dir"] = "/tmp/ActiveCheckout"
    observed: list[str] = []

    retirement.validate_orphan_retirement(
        plan=plan,
        plan_generated_at=now,
        now=now,
        max_plan_age_seconds=300,
        container_id=CONTAINER_ID,
        container_name=CONTAINER_NAME,
        compose_project=COMPOSE_PROJECT,
        labelled_working_dir="/tmp/ActiveCheckout",
        expected_working_dir=EXPECTED_WORKING_DIR,
        projects_root=PROJECTS_ROOT,
        workbench_repo_path=WORKBENCH_REPO,
        live_container=live,
        registered_worktrees=set(),
        path_exists=lambda value: observed.append(value) or False,
    )

    assert observed == ["/tmp/ActiveCheckout"]


def test_validation_refuses_posix_case_variant_restatement() -> None:
    now = datetime.now(timezone.utc)
    plan = _plan(now)
    conflict = plan["ownership_conflicts"][0]
    assert isinstance(conflict, dict)
    conflict["compose_working_dir"] = "/tmp/ActiveCheckout"
    live = _live_container()
    config = live["Config"]
    assert isinstance(config, dict)
    labels = config["Labels"]
    assert isinstance(labels, dict)
    labels["com.docker.compose.project.working_dir"] = "/tmp/ActiveCheckout"

    with pytest.raises(
        retirement.OrphanRetirementRefused, match="labelled working directory"
    ):
        retirement.validate_orphan_retirement(
            plan=plan,
            plan_generated_at=now,
            now=now,
            max_plan_age_seconds=300,
            container_id=CONTAINER_ID,
            container_name=CONTAINER_NAME,
            compose_project=COMPOSE_PROJECT,
            labelled_working_dir="/tmp/activecheckout",
            expected_working_dir=EXPECTED_WORKING_DIR,
            projects_root=PROJECTS_ROOT,
            workbench_repo_path=WORKBENCH_REPO,
            live_container=live,
            registered_worktrees=set(),
            path_exists=lambda _: False,
        )


def _write_plan(tmp_path: Path) -> tuple[Path, str]:
    plan_path = tmp_path / "cleanup-plan.json"
    plan_path.write_text(
        json.dumps(_plan(datetime.now(timezone.utc))), encoding="utf-8"
    )
    return plan_path, hashlib.sha256(plan_path.read_bytes()).hexdigest()


def _cli_arguments(plan_path: Path, digest: str, output: Path) -> list[str]:
    return [
        "--plan",
        str(plan_path),
        "--expected-plan-sha256",
        digest,
        "--container-id",
        CONTAINER_ID,
        "--container-name",
        CONTAINER_NAME,
        "--compose-project",
        COMPOSE_PROJECT,
        "--labelled-working-dir",
        LABELLED_WORKING_DIR,
        "--expected-working-dir",
        EXPECTED_WORKING_DIR,
        "--projects-root",
        PROJECTS_ROOT,
        "--workbench-repo-path",
        WORKBENCH_REPO,
        "--output",
        str(output),
    ]


def test_cli_dry_run_emits_approval_receipt_without_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan_path, digest = _write_plan(tmp_path)
    output = tmp_path / "dry-run-receipt.json"
    monkeypatch.setattr(retirement, "inspect_container", lambda _: _live_container())
    monkeypatch.setattr(
        retirement, "collect_registered_worktree_paths", lambda _: set()
    )
    removed: list[str] = []
    monkeypatch.setattr(retirement, "remove_container", removed.append)

    result = retirement.main(_cli_arguments(plan_path, digest, output))

    receipt = json.loads(output.read_text(encoding="utf-8"))
    assert result == 0
    assert receipt["status"] == "approved_not_executed"
    assert receipt["after"]["container_present"] is True
    assert receipt["after"]["mutation_performed"] is False
    assert (
        receipt["after"]["remaining_conflicts"]["ownership_conflicts"]
        == (receipt["before"]["ownership_conflicts"])
    )
    assert receipt["non_target_scope"]["volumes"] == "not_mutated"
    assert removed == []


def test_cli_execute_removes_only_exact_container_and_records_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan_path, digest = _write_plan(tmp_path)
    output = tmp_path / "execute-receipt.json"
    inspections = iter(
        [
            _live_container(),
            _live_container(),
            retirement.ContainerNotFound("container absent"),
        ]
    )

    def inspect(_: str) -> dict[str, object]:
        value = next(inspections)
        if isinstance(value, Exception):
            raise value
        return value

    monkeypatch.setattr(retirement, "inspect_container", inspect)
    monkeypatch.setattr(
        retirement, "collect_registered_worktree_paths", lambda _: set()
    )
    removed: list[str] = []
    monkeypatch.setattr(retirement, "remove_container", removed.append)
    monkeypatch.setattr(
        retirement,
        "collect_remaining_conflicts",
        lambda **_: {"generated_at": "after", "ownership_conflicts": []},
    )
    arguments = _cli_arguments(plan_path, digest, output) + [
        "--execute",
        "--confirmation",
        retirement.EXECUTION_CONFIRMATION,
    ]

    result = retirement.main(arguments)

    receipt = json.loads(output.read_text(encoding="utf-8"))
    assert result == 0
    assert removed == [CONTAINER_ID]
    assert receipt["status"] == "retired"
    assert receipt["checks"]["pre_mutation_revalidated"] is True
    assert receipt["after"] == {
        "container_present": False,
        "remaining_conflicts": {
            "generated_at": "after",
            "ownership_conflicts": [],
        },
    }


def test_execute_writes_a_pre_mutation_receipt_before_exact_removal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan_path, digest = _write_plan(tmp_path)
    output = tmp_path / "execute-receipt.json"
    inspections = iter(
        [
            _live_container(),
            _live_container(),
            retirement.ContainerNotFound("container absent"),
        ]
    )

    def inspect(_: str) -> dict[str, object]:
        value = next(inspections)
        if isinstance(value, Exception):
            raise value
        return value

    monkeypatch.setattr(retirement, "inspect_container", inspect)
    monkeypatch.setattr(
        retirement, "collect_registered_worktree_paths", lambda _: set()
    )
    monkeypatch.setattr(
        retirement,
        "collect_remaining_conflicts",
        lambda **_: {"generated_at": "after", "ownership_conflicts": []},
    )

    def remove(_: str) -> None:
        receipt = json.loads(output.read_text(encoding="utf-8"))
        assert receipt["status"] == "validated_pending_execution"
        assert receipt["before"]["id"] == CONTAINER_ID

    monkeypatch.setattr(retirement, "remove_container", remove)
    arguments = _cli_arguments(plan_path, digest, output) + [
        "--execute",
        "--confirmation",
        retirement.EXECUTION_CONFIRMATION,
    ]

    assert retirement.main(arguments) == 0


def test_cli_refuses_bad_digest_and_missing_execution_confirmation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan_path, digest = _write_plan(tmp_path)
    output = tmp_path / "refused-receipt.json"
    monkeypatch.setattr(retirement, "inspect_container", lambda _: _live_container())

    assert retirement.main(_cli_arguments(plan_path, "0" * 64, output)) == 2
    assert "SHA-256" in json.loads(output.read_text(encoding="utf-8"))["error"]

    arguments = _cli_arguments(plan_path, digest, output) + ["--execute"]
    assert retirement.main(arguments) == 2
    assert "confirmation" in json.loads(output.read_text(encoding="utf-8"))["error"]


def test_docker_inspect_distinguishes_absence_from_daemon_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    responses = iter(
        [
            SimpleNamespace(
                returncode=1, stdout="", stderr="Error: No such object: target"
            ),
            SimpleNamespace(returncode=1, stdout="", stderr="daemon unavailable"),
        ]
    )
    monkeypatch.setattr(
        retirement.subprocess, "run", lambda *args, **kwargs: next(responses)
    )

    with pytest.raises(retirement.ContainerNotFound):
        retirement.inspect_container(CONTAINER_ID)
    with pytest.raises(retirement.OrphanRetirementRefused, match="cannot be inspected"):
        retirement.inspect_container(CONTAINER_ID)


def test_execute_reports_indeterminate_if_post_removal_inspection_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan_path, digest = _write_plan(tmp_path)
    output = tmp_path / "indeterminate-receipt.json"
    inspections = iter(
        [
            _live_container(),
            _live_container(),
            retirement.OrphanRetirementRefused("daemon unavailable"),
        ]
    )

    def inspect(_: str) -> dict[str, object]:
        value = next(inspections)
        if isinstance(value, Exception):
            raise value
        return value

    monkeypatch.setattr(retirement, "inspect_container", inspect)
    monkeypatch.setattr(
        retirement, "collect_registered_worktree_paths", lambda _: set()
    )
    monkeypatch.setattr(retirement, "remove_container", lambda _: None)
    arguments = _cli_arguments(plan_path, digest, output) + [
        "--execute",
        "--confirmation",
        retirement.EXECUTION_CONFIRMATION,
    ]

    assert retirement.main(arguments) == 2
    receipt = json.loads(output.read_text(encoding="utf-8"))
    assert receipt["status"] == "indeterminate_after_mutation"
    assert receipt["error"] == "daemon unavailable"
    assert receipt["checks"]["pre_mutation_revalidated"] is True
    assert receipt["before"]["id"] == CONTAINER_ID


def test_execute_preserves_known_after_state_when_conflict_refresh_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan_path, digest = _write_plan(tmp_path)
    output = tmp_path / "indeterminate-refresh-receipt.json"
    inspections = iter(
        [
            _live_container(),
            _live_container(),
            retirement.ContainerNotFound("container absent"),
        ]
    )

    def inspect(_: str) -> dict[str, object]:
        value = next(inspections)
        if isinstance(value, Exception):
            raise value
        return value

    monkeypatch.setattr(retirement, "inspect_container", inspect)
    monkeypatch.setattr(
        retirement, "collect_registered_worktree_paths", lambda _: set()
    )
    monkeypatch.setattr(retirement, "remove_container", lambda _: None)
    monkeypatch.setattr(
        retirement,
        "collect_remaining_conflicts",
        lambda **_: (_ for _ in ()).throw(OSError("refresh unavailable")),
    )
    arguments = _cli_arguments(plan_path, digest, output) + [
        "--execute",
        "--confirmation",
        retirement.EXECUTION_CONFIRMATION,
    ]

    assert retirement.main(arguments) == 2
    receipt = json.loads(output.read_text(encoding="utf-8"))
    assert receipt["status"] == "indeterminate_after_mutation"
    assert receipt["checks"]["pre_mutation_revalidated"] is True
    assert receipt["before"]["id"] == CONTAINER_ID
    assert receipt["after"] == {"container_present": False}


def test_live_validation_runs_slow_git_probe_before_final_docker_and_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[str] = []
    args = SimpleNamespace(
        container_id=CONTAINER_ID,
        container_name=CONTAINER_NAME,
        compose_project=COMPOSE_PROJECT,
        labelled_working_dir=LABELLED_WORKING_DIR,
        expected_working_dir=EXPECTED_WORKING_DIR,
        projects_root=PROJECTS_ROOT,
        workbench_repo_path=WORKBENCH_REPO,
        max_plan_age_seconds=300,
    )
    monkeypatch.setattr(
        retirement,
        "collect_registered_worktree_paths",
        lambda _: events.append("git") or set(),
    )
    monkeypatch.setattr(
        retirement,
        "inspect_container",
        lambda _: events.append("docker") or _live_container(),
    )
    monkeypatch.setattr(
        retirement,
        "path_entry_exists",
        lambda _: events.append("path") or False,
    )
    now = datetime.now(timezone.utc)

    retirement.validate_live_request(
        args=args,
        plan=_plan(now),
        plan_generated_at=now,
    )

    assert events == ["git", "docker", "path"]


def test_execute_revalidates_identity_after_receipt_before_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan_path, digest = _write_plan(tmp_path)
    output = tmp_path / "race-refusal-receipt.json"
    changed = _live_container()
    changed["Name"] = "/reclaimed-by-active-owner"
    inspections = iter([_live_container(), changed])
    monkeypatch.setattr(retirement, "inspect_container", lambda _: next(inspections))
    monkeypatch.setattr(
        retirement, "collect_registered_worktree_paths", lambda _: set()
    )
    removed: list[str] = []
    monkeypatch.setattr(retirement, "remove_container", removed.append)
    arguments = _cli_arguments(plan_path, digest, output) + [
        "--execute",
        "--confirmation",
        retirement.EXECUTION_CONFIRMATION,
    ]

    assert retirement.main(arguments) == 2
    receipt = json.loads(output.read_text(encoding="utf-8"))
    assert receipt["status"] == "refused"
    assert "live container name" in receipt["error"]
    assert removed == []


def test_remaining_conflicts_are_regenerated_without_project_exceptions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        retirement, "inspect_docker", lambda: ([{"Id": "live"}], [], [])
    )
    monkeypatch.setattr(
        retirement, "collect_registered_worktree_paths", lambda _: {"registered"}
    )
    captured: dict[str, object] = {}

    def build_plan(**kwargs: object) -> dict[str, object]:
        captured.update(kwargs)
        return {
            "generated_at": "after",
            "ownership_conflicts": [{"id": "remaining"}],
        }

    monkeypatch.setattr(retirement, "build_cleanup_plan", build_plan)

    result = retirement.collect_remaining_conflicts(
        projects_root=PROJECTS_ROOT,
        workbench_repo_path=WORKBENCH_REPO,
    )

    assert result == {
        "generated_at": "after",
        "ownership_conflicts": [{"id": "remaining"}],
    }
    assert captured["containers"] == [{"Id": "live"}]
    assert captured["registered_worktrees"] == {"registered"}
    assert "include_projects" not in captured
