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


def _resource(name: str, project: str) -> dict[str, object]:
    return {
        "Id": f"id-{name}",
        "Name": name,
        "RepoTags": [name],
        "Labels": {"com.docker.compose.project": project},
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
            "compose_project_resource_without_working_directory_provenance",
            UNPROVEN_RESOURCE_ONLY_OWNER,
        ),
    }


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
