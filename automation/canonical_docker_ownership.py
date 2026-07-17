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
from collections.abc import Iterable, Mapping, Sequence
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
EXACT_OWNED_CONTAINER_NAMES = frozenset({"lotus-direct-dev-ingress"})


def normalize_docker_path(value: str) -> str:
    """Normalize host paths recorded by Docker labels for stable boundary checks."""

    normalized = posixpath.normpath(value.strip().replace("\\", "/"))
    return normalized.rstrip("/").casefold()


def path_is_within(path: str, root: str) -> bool:
    normalized_path = normalize_docker_path(path)
    normalized_root = normalize_docker_path(root)
    return normalized_path == normalized_root or normalized_path.startswith(
        f"{normalized_root}/"
    )


def canonical_project_roots(
    projects_root: str, workbench_repo_path: str
) -> dict[str, str]:
    base = Path(projects_root)
    project_roots = {
        repository: normalize_docker_path(str(base / repository))
        for repository in CANONICAL_REPOSITORIES
    }
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
        if expected_root and working_dir and path_is_within(working_dir, expected_root)
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
) -> list[dict[str, str]]:
    conflicts: list[dict[str, str]] = []
    for item in items:
        labels = _labels(item)
        project = str(labels.get(COMPOSE_PROJECT_LABEL, ""))
        expected_root = allowed_project_roots.get(project.casefold(), "")
        if not expected_root:
            continue
        working_dir = str(labels.get(COMPOSE_WORKING_DIR_LABEL, ""))
        if working_dir and path_is_within(working_dir, expected_root):
            continue
        conflicts.append(
            {
                "id": str(item.get("Id") or item.get("ID") or ""),
                "name": _container_name(item),
                "compose_project": project,
                "compose_working_dir": working_dir,
                "expected_working_dir": expected_root,
                "conflict_reason": "compose_project_owned_by_different_working_directory",
            }
        )
    return sorted(conflicts, key=lambda item: item["name"])


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
) -> dict[str, Any]:
    allowed_project_roots = canonical_project_roots(projects_root, workbench_repo_path)
    owned_containers = select_owned_containers(containers, allowed_project_roots)
    conflicts = select_ownership_conflicts(containers, allowed_project_roots)
    conflicting_projects = {item["compose_project"] for item in conflicts}
    projects = set(allowed_project_roots).difference(conflicting_projects)
    projects.update(project for project in include_projects if project)
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "selection_policy": "compose-ownership-labels-v1",
        "allowed_compose_projects": allowed_project_roots,
        "exact_owned_container_names": sorted(EXACT_OWNED_CONTAINER_NAMES),
        "compose_projects": sorted(projects),
        "ownership_conflicts": conflicts,
        "containers": owned_containers,
        "volumes": select_project_resources(volumes, projects, resource_type="volume"),
        "images": select_project_resources(images, projects, resource_type="image"),
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
        raise RuntimeError(
            f"docker {resource_type} inspect returned a non-list payload"
        )
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
    plan = build_cleanup_plan(
        projects_root=args.projects_root,
        workbench_repo_path=args.workbench_repo_path,
        containers=containers,
        volumes=volumes,
        images=images,
        include_projects=args.include_project,
    )
    print(json.dumps(plan, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
