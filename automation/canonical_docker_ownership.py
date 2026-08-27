#!/usr/bin/env python3
"""Build a read-only Docker cleanup plan for the canonical front-office runtime.

Ownership is established from Docker Compose labels and explicit canonical repository
roots. Resource names are evidence only; they are never an ownership boundary.
"""

from __future__ import annotations

import argparse
import json
import posixpath
import subprocess
from collections.abc import Callable, Iterable, Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

COMPOSE_PROJECT_LABEL = "com.docker.compose.project"
COMPOSE_WORKING_DIR_LABEL = "com.docker.compose.project.working_dir"
CANONICAL_REPOSITORIES = (
    "lotus-core",
    "lotus-performance",
    "lotus-risk",
    "lotus-ai",
    "lotus-advise",
    "lotus-manage",
    "lotus-report",
    "lotus-archive",
    "lotus-render",
    "lotus-idea",
    "lotus-gateway",
    "lotus-workbench",
)
CANONICAL_COMPOSE_PROJECT_ALIASES = {
    "lotus-core": (
        "lotus-core-app-local",
        "lotus-core-canonical-ui",
    ),
}
EXACT_OWNED_CONTAINER_NAMES = frozenset({"lotus-direct-dev-ingress"})
ACTIVE_FOREIGN_OWNER = "active_foreign_owner"
MISSING_LABELLED_CHECKOUT = "missing_labelled_checkout"
UNPROVEN_RESOURCE_ONLY_OWNER = "unproven_resource_only_owner"


def normalize_docker_path(value: str) -> str:
    """Normalize host paths recorded by Docker labels for stable boundary checks."""

    normalized = posixpath.normpath(value.strip().replace("\\", "/"))
    return normalized.rstrip("/").casefold()


def paths_match_exactly(path: str, expected_path: str) -> bool:
    """Compare checkout paths without accepting nested worktrees or sibling prefixes."""

    return normalize_docker_path(path) == normalize_docker_path(expected_path)


def collect_registered_worktree_paths(
    allowed_project_roots: Mapping[str, str],
) -> set[str]:
    """Return every worktree registered by the canonical repositories.

    A missing directory is not sufficient orphan proof when Git still registers that path as a
    worktree. Collection therefore happens independently from filesystem existence checks.
    """

    registered: set[str] = set()
    for repository_root in sorted(set(allowed_project_roots.values())):
        root = Path(repository_root)
        if not root.is_dir():
            continue
        result = subprocess.run(
            ["git", "-C", str(root), "worktree", "list", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
        )
        for line in result.stdout.splitlines():
            if line.startswith("worktree "):
                registered.add(normalize_docker_path(line.removeprefix("worktree ")))
    return registered


def canonical_project_roots(
    projects_root: str, workbench_repo_path: str
) -> dict[str, str]:
    base = Path(projects_root)
    project_roots = {
        repository: normalize_docker_path(str(base / repository))
        for repository in CANONICAL_REPOSITORIES
    }
    for repository, aliases in CANONICAL_COMPOSE_PROJECT_ALIASES.items():
        repository_root = project_roots[repository]
        project_roots.update({alias: repository_root for alias in aliases})
    workbench_project = Path(workbench_repo_path).name.casefold()
    project_roots[workbench_project] = normalize_docker_path(workbench_repo_path)
    return project_roots


def _labels(item: Mapping[str, Any]) -> Mapping[str, str]:
    labels = item.get("Config", {}).get("Labels") or item.get("Labels") or {}
    return labels if isinstance(labels, Mapping) else {}


def _container_name(item: Mapping[str, Any]) -> str:
    name = str(item.get("Name") or "").lstrip("/")
    if name:
        return name
    names = item.get("Names") or []
    return str(names[0]).lstrip("/") if names else ""


def _owned_container_record(
    item: Mapping[str, Any],
    allowed_project_roots: Mapping[str, str],
) -> dict[str, str] | None:
    labels = _labels(item)
    name = _container_name(item)
    working_dir = str(labels.get(COMPOSE_WORKING_DIR_LABEL, ""))
    project = str(labels.get(COMPOSE_PROJECT_LABEL, ""))
    expected_root = allowed_project_roots.get(project.casefold(), "")
    matched_root = (
        expected_root
        if expected_root
        and working_dir
        and paths_match_exactly(working_dir, expected_root)
        else ""
    )
    if not matched_root and name not in EXACT_OWNED_CONTAINER_NAMES:
        return None
    provenance = (
        f"compose_working_dir:{matched_root}"
        if matched_root
        else f"exact_container_name:{name}"
    )
    return {
        "id": str(item.get("Id") or item.get("ID") or ""),
        "name": name,
        "compose_project": project,
        "compose_working_dir": working_dir,
        "ownership_provenance": provenance,
    }


def select_owned_containers(
    items: Iterable[Mapping[str, Any]],
    allowed_project_roots: Mapping[str, str],
) -> list[dict[str, str]]:
    records = (_owned_container_record(item, allowed_project_roots) for item in items)
    return sorted(
        (record for record in records if record is not None),
        key=lambda item: item["name"],
    )


def select_ownership_conflicts(
    items: Iterable[Mapping[str, Any]],
    allowed_project_roots: Mapping[str, str],
    *,
    registered_worktrees: Iterable[str] = (),
    checkout_exists: Callable[[str], bool] = lambda value: Path(value).is_dir(),
) -> list[dict[str, str]]:
    normalized_worktrees = {
        normalize_docker_path(worktree) for worktree in registered_worktrees
    }
    conflicts: list[dict[str, str]] = []
    for item in items:
        labels = _labels(item)
        project = str(labels.get(COMPOSE_PROJECT_LABEL, ""))
        expected_root = allowed_project_roots.get(project.casefold(), "")
        if not expected_root:
            continue
        working_dir = str(labels.get(COMPOSE_WORKING_DIR_LABEL, ""))
        if working_dir and paths_match_exactly(working_dir, expected_root):
            continue
        normalized_working_dir = (
            normalize_docker_path(working_dir) if working_dir else ""
        )
        ownership_state = ACTIVE_FOREIGN_OWNER
        if (
            working_dir
            and normalized_working_dir not in normalized_worktrees
            and not checkout_exists(working_dir)
        ):
            ownership_state = MISSING_LABELLED_CHECKOUT
        conflicts.append(
            {
                "id": str(item.get("Id") or item.get("ID") or ""),
                "name": _container_name(item),
                "compose_project": project,
                "compose_working_dir": working_dir,
                "expected_working_dir": expected_root,
                "conflict_reason": "compose_project_owned_by_different_working_directory",
                "ownership_state": ownership_state,
            }
        )
    return sorted(conflicts, key=lambda item: item["name"])


def select_resource_only_ownership_conflicts(
    *,
    containers: Iterable[Mapping[str, Any]],
    volumes: Iterable[Mapping[str, Any]],
    images: Iterable[Mapping[str, Any]],
    allowed_project_roots: Mapping[str, str],
    explicitly_included_projects: set[str],
) -> list[dict[str, str]]:
    """Reject residual Compose resources whose checkout ownership cannot be proven."""

    projects_with_container_evidence = {
        str(_labels(item).get(COMPOSE_PROJECT_LABEL, "")).casefold()
        for item in containers
        if str(_labels(item).get(COMPOSE_PROJECT_LABEL, "")).casefold()
        in allowed_project_roots
    }
    conflicts: list[dict[str, str]] = []
    for resource_type, items in (("volume", volumes), ("image", images)):
        for item in items:
            project = str(_labels(item).get(COMPOSE_PROJECT_LABEL, ""))
            expected_root = allowed_project_roots.get(project.casefold(), "")
            if (
                not expected_root
                or project.casefold() in projects_with_container_evidence
                or project.casefold() in explicitly_included_projects
            ):
                continue
            identifier = _resource_identifier(item, resource_type)
            conflicts.append(
                {
                    "id": str(item.get("Id") or item.get("ID") or identifier),
                    "name": identifier,
                    "resource_type": resource_type,
                    "compose_project": project,
                    "compose_working_dir": "",
                    "expected_working_dir": expected_root,
                    "conflict_reason": (
                        "compose_project_resource_without_working_directory_provenance"
                    ),
                    "ownership_state": UNPROVEN_RESOURCE_ONLY_OWNER,
                }
            )
    return sorted(conflicts, key=lambda item: (item["compose_project"], item["name"]))


def _resource_identifier(item: Mapping[str, Any], resource_type: str) -> str:
    if resource_type == "volume":
        return str(item.get("Name") or "")
    repo_tags = item.get("RepoTags") or []
    return str(repo_tags[0]) if repo_tags else str(item.get("Id") or "")


def _owned_project_resource_record(
    item: Mapping[str, Any],
    projects: set[str],
    resource_type: str,
) -> dict[str, str] | None:
    project = str(_labels(item).get(COMPOSE_PROJECT_LABEL, ""))
    if not project or project not in projects:
        return None
    identifier = _resource_identifier(item, resource_type)
    return {
        "id": str(item.get("Id") or item.get("ID") or identifier),
        "name": identifier,
        "compose_project": project,
        "ownership_provenance": f"compose_project:{project}",
    }


def select_project_resources(
    items: Iterable[Mapping[str, Any]],
    projects: set[str],
    *,
    resource_type: str,
) -> list[dict[str, str]]:
    records = (
        _owned_project_resource_record(item, projects, resource_type) for item in items
    )
    return sorted(
        (record for record in records if record is not None),
        key=lambda item: item["name"],
    )


def build_cleanup_plan(
    *,
    projects_root: str,
    workbench_repo_path: str,
    containers: Iterable[Mapping[str, Any]],
    volumes: Iterable[Mapping[str, Any]],
    images: Iterable[Mapping[str, Any]],
    include_projects: Iterable[str] = (),
    registered_worktrees: Iterable[str] = (),
    checkout_exists: Callable[[str], bool] = lambda value: Path(value).is_dir(),
) -> dict[str, Any]:
    container_items = list(containers)
    volume_items = list(volumes)
    image_items = list(images)
    included_projects = {project for project in include_projects if project}
    explicitly_included_projects = {project.casefold() for project in included_projects}
    allowed_project_roots = canonical_project_roots(projects_root, workbench_repo_path)
    owned_containers = select_owned_containers(container_items, allowed_project_roots)
    normalized_worktrees = sorted(
        {normalize_docker_path(worktree) for worktree in registered_worktrees}
    )
    conflicts = select_ownership_conflicts(
        container_items,
        allowed_project_roots,
        registered_worktrees=normalized_worktrees,
        checkout_exists=checkout_exists,
    )
    conflicts.extend(
        select_resource_only_ownership_conflicts(
            containers=container_items,
            volumes=volume_items,
            images=image_items,
            allowed_project_roots=allowed_project_roots,
            explicitly_included_projects=explicitly_included_projects,
        )
    )
    conflicts.sort(key=lambda item: (item["compose_project"], item["name"]))
    conflicting_projects = {item["compose_project"] for item in conflicts}
    projects = {
        item["compose_project"]
        for item in owned_containers
        if item["compose_project"]
        and item["compose_project"] not in conflicting_projects
    }
    projects.update(included_projects)
    return {
        "schema_version": "1.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "selection_policy": "compose-ownership-labels-v2",
        "allowed_compose_projects": allowed_project_roots,
        "registered_worktrees": normalized_worktrees,
        "exact_owned_container_names": sorted(EXACT_OWNED_CONTAINER_NAMES),
        "compose_projects": sorted(projects),
        "ownership_conflicts": conflicts,
        "containers": owned_containers,
        "volumes": select_project_resources(
            volume_items, projects, resource_type="volume"
        ),
        "images": select_project_resources(
            image_items, projects, resource_type="image"
        ),
    }


def _docker_inspect(
    resource_type: str, identifiers: Sequence[str]
) -> list[Mapping[str, Any]]:
    if not identifiers:
        return []
    result = subprocess.run(
        ["docker", resource_type, "inspect", *identifiers],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    if not isinstance(payload, list):
        raise TypeError(f"docker {resource_type} inspect returned a non-list payload")
    return payload


def _docker_identifiers(*arguments: str) -> list[str]:
    result = subprocess.run(
        ["docker", *arguments],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def inspect_docker() -> tuple[list[Mapping[str, Any]], ...]:
    container_ids = _docker_identifiers("container", "ls", "-aq", "--no-trunc")
    volume_names = _docker_identifiers("volume", "ls", "-q")
    image_ids = list(
        dict.fromkeys(_docker_identifiers("image", "ls", "-q", "--no-trunc"))
    )
    return (
        _docker_inspect("container", container_ids),
        _docker_inspect("volume", volume_names),
        _docker_inspect("image", image_ids),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--projects-root", required=True)
    parser.add_argument("--workbench-repo-path", required=True)
    parser.add_argument("--include-project", action="append", default=[])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    containers, volumes, images = inspect_docker()
    allowed_project_roots = canonical_project_roots(
        args.projects_root, args.workbench_repo_path
    )
    plan = build_cleanup_plan(
        projects_root=args.projects_root,
        workbench_repo_path=args.workbench_repo_path,
        containers=containers,
        volumes=volumes,
        images=images,
        include_projects=args.include_project,
        registered_worktrees=collect_registered_worktree_paths(allowed_project_roots),
    )
    print(json.dumps(plan, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
