from __future__ import annotations

from automation.canonical_docker_ownership import (
    build_cleanup_plan,
    normalize_docker_path,
    paths_match_exactly,
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


def test_cleanup_plan_selects_only_compose_resources_owned_by_canonical_roots() -> None:
    owned_project = "lotus-core"
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

    assert plan["selection_policy"] == "compose-ownership-labels-v1"
    assert plan["allowed_compose_projects"]["lotus-core"] == (
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
        (item["resource_type"], item["name"], item["conflict_reason"])
        for item in plan["ownership_conflicts"]
    } == {
        (
            "volume",
            "lotus-core-residual-data",
            "compose_project_resource_without_working_directory_provenance",
        ),
        (
            "image",
            "lotus-core-residual-api:local",
            "compose_project_resource_without_working_directory_provenance",
        ),
    }


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
