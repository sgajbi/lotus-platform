from __future__ import annotations

import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from automation.canonical_docker_ownership import (
    ACTIVE_FOREIGN_OWNER,
    MISSING_LABELLED_CHECKOUT,
    UNPROVEN_RESOURCE_ONLY_OWNER,
    build_cleanup_plan,
    collect_registered_worktree_paths,
    normalize_docker_path,
    path_entry_exists,
    paths_match_exactly,
    select_ownership_conflicts,
)


def _container(name: str, project: str, working_dir: str) -> dict[str, object]:
    return {
        "Id": f"id-{name}",
        "Name": f"/{name}",
        "Config": {
            "Labels": {
                "com.docker.compose.project": project,
                "com.docker.compose.project.working_dir": working_dir,
            }
        },
    }


def _resource(name: str, project: str, *, checkout: str = "") -> dict[str, object]:
    labels = {"com.docker.compose.project": project}
    if checkout:
        labels["com.lotus.repository.checkout"] = checkout
    return {
        "Id": f"id-{name}",
        "Name": name,
        "RepoTags": [name],
        "Labels": labels,
    }


def test_checkout_path_match_is_normalized_and_exact() -> None:
    root = r"C:\Users\Sandeep\projects\lotus-core"

    assert normalize_docker_path(root) == "c:/users/sandeep/projects/lotus-core"
    assert paths_match_exactly(r"c:\users\sandeep\projects\lotus-core", root)
    assert not paths_match_exactly(
        r"C:\Users\Sandeep\projects\lotus-core\.worktrees\feature",
        root,
    )
    assert not paths_match_exactly(r"C:\Users\Sandeep\projects\lotus-core-shadow", root)
    assert not paths_match_exactly("/tmp/ActiveCheckout", "/tmp/activecheckout")


def test_path_entry_probe_distinguishes_absence_from_entry_and_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "automation.canonical_docker_ownership.os.lstat",
        lambda _: SimpleNamespace(),
    )
    assert path_entry_exists("broken-link-entry") is True

    monkeypatch.setattr(
        "automation.canonical_docker_ownership.os.lstat",
        lambda _: (_ for _ in ()).throw(FileNotFoundError()),
    )
    assert path_entry_exists("absent") is False

    monkeypatch.setattr(
        "automation.canonical_docker_ownership.os.lstat",
        lambda _: (_ for _ in ()).throw(PermissionError("denied")),
    )
    with pytest.raises(OSError, match="cannot prove path absence"):
        path_entry_exists("uninspectable")


def test_worktree_collection_refuses_an_unavailable_canonical_root(
    tmp_path: Path,
) -> None:
    missing_root = tmp_path / "missing-repository"

    with pytest.raises(FileNotFoundError, match="canonical repository root"):
        collect_registered_worktree_paths({"lotus-gateway": str(missing_root)})


def test_worktree_collection_propagates_git_enumeration_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository_root = tmp_path / "lotus-gateway"
    repository_root.mkdir()
    monkeypatch.setattr(
        "automation.canonical_docker_ownership.subprocess.run",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            subprocess.CalledProcessError(1, "git worktree list")
        ),
    )

    with pytest.raises(subprocess.CalledProcessError):
        collect_registered_worktree_paths({"lotus-gateway": str(repository_root)})


@pytest.mark.parametrize(
    "owned_project",
    ["lotus-core", "lotus-core-app-local", "lotus-core-canonical-ui"],
)
def test_cleanup_plan_selects_only_compose_resources_owned_by_canonical_roots(
    owned_project: str,
) -> None:
    unrelated_project = "lotus-core-certification"
    plan = build_cleanup_plan(
        projects_root=r"C:\Users\Sandeep\projects",
        workbench_repo_path=r"C:\Users\Sandeep\projects\lotus-workbench",
        containers=[
            _container(
                "lotus-core-canonical-ui-api",
                owned_project,
                r"C:\Users\Sandeep\projects\lotus-core",
            ),
            _container(
                "lotus-core-certification-postgres",
                unrelated_project,
                r"C:\Users\Sandeep\projects\lotus-core",
            ),
            _container(
                "lotus-unrelated-service",
                "lotus-unrelated",
                r"C:\Users\Sandeep\projects\lotus-unrelated",
            ),
        ],
        volumes=[
            _resource("lotus-core-canonical-ui-postgres", owned_project),
            _resource("lotus-core-certification-postgres", unrelated_project),
        ],
        images=[
            _resource("lotus-core-canonical-ui-api:local", owned_project),
            _resource("lotus-core-certification-api:local", unrelated_project),
        ],
    )

    assert plan["schema_version"] == "1.1"
    assert plan["selection_policy"] == "compose-ownership-labels-v2"
    assert plan["allowed_compose_projects"]["lotus-core"] == (
        "c:/users/sandeep/projects/lotus-core"
    )
    assert plan["allowed_compose_projects"]["lotus-core-app-local"] == (
        "c:/users/sandeep/projects/lotus-core"
    )
    assert plan["allowed_compose_projects"]["lotus-core-canonical-ui"] == (
        "c:/users/sandeep/projects/lotus-core"
    )
    assert owned_project in plan["compose_projects"]
    assert unrelated_project not in plan["compose_projects"]
    assert [item["name"] for item in plan["containers"]] == [
        "lotus-core-canonical-ui-api"
    ]
    assert [item["name"] for item in plan["volumes"]] == [
        "lotus-core-canonical-ui-postgres"
    ]
    assert [item["name"] for item in plan["images"]] == [
        "lotus-core-canonical-ui-api:local"
    ]
    assert "compose_working_dir:" in plan["containers"][0]["ownership_provenance"]
    assert plan["ownership_conflicts"] == []


def test_cleanup_plan_blocks_reused_project_name_from_another_worktree() -> None:
    plan = build_cleanup_plan(
        projects_root=r"C:\Users\Sandeep\projects",
        workbench_repo_path=r"C:\Users\Sandeep\projects\lotus-workbench",
        containers=[
            _container(
                "lotus-core-shadow-api",
                "lotus-core",
                r"C:\Users\Sandeep\projects\lotus-core-shadow",
            )
        ],
        volumes=[_resource("lotus-core-shadow-data", "lotus-core")],
        images=[_resource("lotus-core-shadow-api:local", "lotus-core")],
    )

    assert "lotus-core" not in plan["compose_projects"]
    assert plan["containers"] == []
    assert plan["volumes"] == []
    assert plan["images"] == []
    assert plan["ownership_conflicts"] == [
        {
            "id": "id-lotus-core-shadow-api",
            "name": "lotus-core-shadow-api",
            "compose_project": "lotus-core",
            "compose_working_dir": r"C:\Users\Sandeep\projects\lotus-core-shadow",
            "expected_working_dir": "c:/users/sandeep/projects/lotus-core",
            "conflict_reason": "compose_project_owned_by_different_working_directory",
            "ownership_state": MISSING_LABELLED_CHECKOUT,
        }
    ]


def test_cleanup_plan_blocks_nested_worktree_reusing_canonical_project() -> None:
    plan = build_cleanup_plan(
        projects_root=r"C:\Users\Sandeep\projects",
        workbench_repo_path=r"C:\Users\Sandeep\projects\lotus-workbench",
        containers=[
            _container(
                "lotus-core-nested-worktree-api",
                "lotus-core",
                r"C:\Users\Sandeep\projects\lotus-core\.worktrees\feature",
            )
        ],
        volumes=[],
        images=[],
    )

    assert plan["containers"] == []
    assert "lotus-core" not in plan["compose_projects"]
    assert plan["ownership_conflicts"][0]["conflict_reason"] == (
        "compose_project_owned_by_different_working_directory"
    )


def test_cleanup_plan_blocks_core_alias_owned_by_temporary_checkout() -> None:
    temporary_checkout = r"C:\Users\Sandeep\AppData\Local\Temp\canonical-run\lotus-core"
    plan = build_cleanup_plan(
        projects_root=r"C:\Users\Sandeep\projects",
        workbench_repo_path=r"C:\Users\Sandeep\projects\lotus-workbench",
        containers=[
            _container(
                "lotus-core-canonical-ui-postgres-1",
                "lotus-core-canonical-ui",
                temporary_checkout,
            )
        ],
        volumes=[
            _resource(
                "lotus-core-canonical-ui_postgres_data",
                "lotus-core-canonical-ui",
            )
        ],
        images=[],
    )

    assert "lotus-core-canonical-ui" not in plan["compose_projects"]
    assert plan["containers"] == []
    assert plan["volumes"] == []
    assert plan["ownership_conflicts"] == [
        {
            "id": "id-lotus-core-canonical-ui-postgres-1",
            "name": "lotus-core-canonical-ui-postgres-1",
            "compose_project": "lotus-core-canonical-ui",
            "compose_working_dir": temporary_checkout,
            "expected_working_dir": "c:/users/sandeep/projects/lotus-core",
            "conflict_reason": "compose_project_owned_by_different_working_directory",
            "ownership_state": MISSING_LABELLED_CHECKOUT,
        }
    ]


def test_cleanup_plan_blocks_resource_only_project_without_checkout_provenance() -> (
    None
):
    plan = build_cleanup_plan(
        projects_root=r"C:\Users\Sandeep\projects",
        workbench_repo_path=r"C:\Users\Sandeep\projects\lotus-workbench",
        containers=[],
        volumes=[_resource("lotus-core-residual-data", "lotus-core")],
        images=[_resource("lotus-core-residual-api:local", "lotus-core")],
    )

    assert "lotus-core" not in plan["compose_projects"]
    assert plan["volumes"] == []
    assert plan["images"] == []
    assert {
        (
            item["resource_type"],
            item["name"],
            item["conflict_reason"],
            item["ownership_state"],
        )
        for item in plan["ownership_conflicts"]
    } == {
        (
            "volume",
            "lotus-core-residual-data",
            "compose_project_resource_without_working_directory_provenance",
            UNPROVEN_RESOURCE_ONLY_OWNER,
        ),
        (
            "image",
            "lotus-core-residual-api:local",
            "compose_project_image_without_checkout_provenance",
            UNPROVEN_RESOURCE_ONLY_OWNER,
        ),
    }


def test_cleanup_plan_selects_resource_only_image_with_exact_checkout_label() -> None:
    checkout = r"C:\Users\Sandeep\projects\lotus-workbench"
    plan = build_cleanup_plan(
        projects_root=r"C:\Users\Sandeep\projects",
        workbench_repo_path=checkout,
        containers=[],
        volumes=[],
        images=[
            _resource(
                "lotus-workbench:latest",
                "lotus-workbench",
                checkout=checkout,
            )
        ],
    )

    assert plan["ownership_conflicts"] == []
    assert plan["compose_projects"] == ["lotus-workbench"]
    assert plan["images"] == [
        {
            "id": "id-lotus-workbench:latest",
            "name": "lotus-workbench:latest",
            "compose_project": "lotus-workbench",
            "repository_checkout": checkout,
            "ownership_provenance": (
                "repository_checkout:c:/users/sandeep/projects/lotus-workbench"
            ),
        }
    ]


@pytest.mark.parametrize(
    ("checkout", "reason"),
    [
        (
            r"C:\Users\Sandeep\projects\lotus-workbench-shadow",
            "compose_project_image_owned_by_different_checkout",
        ),
        (
            r"C:\Users\Sandeep\projects\lotus-workbench\.worktrees\feature",
            "compose_project_image_owned_by_different_checkout",
        ),
        ("", "compose_project_image_without_checkout_provenance"),
    ],
)
def test_cleanup_plan_rejects_unproven_resource_only_workbench_image(
    checkout: str, reason: str
) -> None:
    canonical_checkout = r"C:\Users\Sandeep\projects\lotus-workbench"
    plan = build_cleanup_plan(
        projects_root=r"C:\Users\Sandeep\projects",
        workbench_repo_path=canonical_checkout,
        containers=[],
        volumes=[],
        images=[
            _resource(
                "lotus-workbench:latest",
                "lotus-workbench",
                checkout=checkout,
            )
        ],
    )

    assert plan["compose_projects"] == []
    assert plan["images"] == []
    assert plan["ownership_conflicts"][0]["repository_checkout"] == checkout
    assert plan["ownership_conflicts"][0]["conflict_reason"] == reason


def test_foreign_image_label_blocks_project_even_with_owned_container() -> None:
    canonical_checkout = r"C:\Users\Sandeep\projects\lotus-workbench"
    plan = build_cleanup_plan(
        projects_root=r"C:\Users\Sandeep\projects",
        workbench_repo_path=canonical_checkout,
        containers=[
            _container(
                "lotus-workbench-1",
                "lotus-workbench",
                canonical_checkout,
            )
        ],
        volumes=[],
        images=[
            _resource(
                "lotus-workbench:foreign",
                "lotus-workbench",
                checkout=r"C:\Users\Sandeep\projects\lotus-workbench-shadow",
            )
        ],
    )

    assert plan["compose_projects"] == []
    assert plan["images"] == []
    assert plan["ownership_conflicts"][0]["conflict_reason"] == (
        "compose_project_image_owned_by_different_checkout"
    )


def test_unproven_volume_blocks_exact_resource_only_image_for_same_project() -> None:
    checkout = r"C:\Users\Sandeep\projects\lotus-workbench"
    plan = build_cleanup_plan(
        projects_root=r"C:\Users\Sandeep\projects",
        workbench_repo_path=checkout,
        containers=[],
        volumes=[_resource("lotus-workbench-cache", "lotus-workbench")],
        images=[
            _resource(
                "lotus-workbench:latest",
                "lotus-workbench",
                checkout=checkout,
            )
        ],
    )

    assert plan["compose_projects"] == []
    assert plan["volumes"] == []
    assert plan["images"] == []
    assert plan["ownership_conflicts"][0]["resource_type"] == "volume"


def test_resource_only_image_from_unrelated_project_is_ignored() -> None:
    plan = build_cleanup_plan(
        projects_root=r"C:\Users\Sandeep\projects",
        workbench_repo_path=r"C:\Users\Sandeep\projects\lotus-workbench",
        containers=[],
        volumes=[],
        images=[
            _resource(
                "customer-workbench:latest",
                "customer-workbench",
                checkout=r"C:\Users\Sandeep\projects\lotus-workbench",
            )
        ],
    )

    assert plan["compose_projects"] == []
    assert plan["ownership_conflicts"] == []
    assert plan["images"] == []


def test_cleanup_plan_blocks_resource_only_core_alias_without_checkout_provenance() -> (
    None
):
    plan = build_cleanup_plan(
        projects_root=r"C:\Users\Sandeep\projects",
        workbench_repo_path=r"C:\Users\Sandeep\projects\lotus-workbench",
        containers=[],
        volumes=[
            _resource("lotus-core-app-local_postgres_data", "lotus-core-app-local")
        ],
        images=[],
    )

    assert "lotus-core-app-local" not in plan["compose_projects"]
    assert plan["volumes"] == []
    assert plan["ownership_conflicts"][0]["conflict_reason"] == (
        "compose_project_resource_without_working_directory_provenance"
    )
    assert plan["ownership_conflicts"][0]["ownership_state"] == (
        UNPROVEN_RESOURCE_ONLY_OWNER
    )


def test_existing_foreign_checkout_is_not_classified_as_retirable() -> None:
    working_dir = r"C:\Users\Sandeep\projects\lotus-core-feature"
    conflicts = select_ownership_conflicts(
        [_container("lotus-core-feature-api", "lotus-core", working_dir)],
        {"lotus-core": "c:/users/sandeep/projects/lotus-core"},
        checkout_exists=lambda value: value == working_dir,
    )

    assert conflicts[0]["ownership_state"] == ACTIVE_FOREIGN_OWNER


def test_existing_filesystem_entry_is_not_classified_as_retirable(
    tmp_path: Path,
) -> None:
    labelled_path = tmp_path / "reclaimed-checkout"
    labelled_path.write_text("active ownership marker", encoding="utf-8")
    conflicts = select_ownership_conflicts(
        [_container("lotus-core-feature-api", "lotus-core", str(labelled_path))],
        {"lotus-core": normalize_docker_path(str(tmp_path / "lotus-core"))},
    )

    assert conflicts[0]["ownership_state"] == ACTIVE_FOREIGN_OWNER


def test_registered_missing_worktree_is_not_classified_as_retirable() -> None:
    working_dir = r"C:\Users\Sandeep\projects\lotus-core-feature"
    conflicts = select_ownership_conflicts(
        [_container("lotus-core-feature-api", "lotus-core", working_dir)],
        {"lotus-core": "c:/users/sandeep/projects/lotus-core"},
        registered_worktrees=[working_dir],
        checkout_exists=lambda _: False,
    )

    assert conflicts[0]["ownership_state"] == ACTIVE_FOREIGN_OWNER


def test_cleanup_plan_keeps_exact_ingress_but_rejects_similarly_named_container() -> (
    None
):
    plan = build_cleanup_plan(
        projects_root="/workspace/projects",
        workbench_repo_path="/workspace/projects/lotus-workbench",
        containers=[
            _container("lotus-direct-dev-ingress", "", ""),
            _container("lotus-direct-dev-ingress-copy", "", ""),
        ],
        volumes=[],
        images=[],
    )

    assert [item["name"] for item in plan["containers"]] == ["lotus-direct-dev-ingress"]
    assert plan["containers"][0]["ownership_provenance"] == (
        "exact_container_name:lotus-direct-dev-ingress"
    )


def test_include_projects_preserves_post_cleanup_assertion_scope() -> None:
    plan = build_cleanup_plan(
        projects_root="/workspace/projects",
        workbench_repo_path="/workspace/projects/lotus-workbench",
        containers=[],
        volumes=[_resource("owned-data", "canonical-owned")],
        images=[_resource("owned-api:local", "canonical-owned")],
        include_projects=["canonical-owned"],
    )

    assert "canonical-owned" in plan["compose_projects"]
    assert [item["name"] for item in plan["volumes"]] == ["owned-data"]
    assert [item["name"] for item in plan["images"]] == ["owned-api:local"]


def test_docker_inspect_tolerates_resources_that_vanished_after_listing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from automation.canonical_docker_ownership import _docker_inspect

    monkeypatch.setattr(
        "automation.canonical_docker_ownership.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=args,
            returncode=1,
            stdout='[{"Id": "id-survivor"}]\n',
            stderr="Error response from daemon: No such container: id-vanished\n",
        ),
    )

    assert _docker_inspect("container", ["id-survivor", "id-vanished"]) == [
        {"Id": "id-survivor"}
    ]


@pytest.mark.parametrize(
    "stderr",
    [
        "error during connect: the docker daemon is not running\n",
        # A vanished daemon socket also says "no such", but names a file, not a
        # docker object; tolerating it would report an empty inventory instead
        # of failing the run.
        "Cannot connect to the Docker daemon at unix:///var/run/docker.sock: "
        "dial unix /var/run/docker.sock: connect: no such file or directory\n",
        "Error response from daemon: No such container: id-vanished\n"
        "error during connect: connection reset\n",
    ],
)
def test_docker_inspect_raises_on_non_missing_object_failures(
    monkeypatch: pytest.MonkeyPatch, stderr: str
) -> None:
    from automation.canonical_docker_ownership import _docker_inspect

    monkeypatch.setattr(
        "automation.canonical_docker_ownership.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=args,
            returncode=1,
            stdout="",
            stderr=stderr,
        ),
    )

    with pytest.raises(subprocess.CalledProcessError):
        _docker_inspect("container", ["id-any"])
