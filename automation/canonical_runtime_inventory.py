"""Read actual canonical ports, evaluated sources and resource identities."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

try:
    from automation.canonical_docker_ownership import (
        CANONICAL_REPOSITORIES,
        canonical_project_roots,
        normalize_docker_path,
        paths_match_exactly,
    )
    from automation.canonical_runtime_lease import ReservationRefusal, validate_bindings
except ModuleNotFoundError:
    from canonical_docker_ownership import (
        CANONICAL_REPOSITORIES,
        canonical_project_roots,
        normalize_docker_path,
        paths_match_exactly,
    )
    from canonical_runtime_lease import ReservationRefusal, validate_bindings


def command(arguments: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(
        arguments, cwd=cwd, capture_output=True, text=True, check=False
    )
    if result.returncode:
        # Compose config may contain secrets. Never echo its payload or environment.
        raise ReservationRefusal(
            f"Runtime inventory command {arguments[0]} failed ({result.returncode})."
        )
    return result.stdout


def _canonical_projects_and_repositories(
    projects_root: Path,
    workbench: Path,
    runtime_mode: str = "full",
) -> tuple[dict[str, str], tuple[str, ...]]:
    if runtime_mode not in {"full", "core-manage"}:
        raise ReservationRefusal("Unknown explicit runtime mode.")
    projects = canonical_project_roots(str(projects_root), str(workbench))
    if runtime_mode == "core-manage":
        projects = {
            name: root
            for name, root in projects.items()
            if paths_match_exactly(root, str(projects_root / "lotus-core"))
            or paths_match_exactly(root, str(projects_root / "lotus-manage"))
        }
    projects["lotus-workbench"] = normalize_docker_path(str(workbench))
    projects["canonical-ingress"] = normalize_docker_path(
        str(projects_root / "lotus-platform")
    )
    repositories = (
        ("lotus-core", "lotus-manage", "lotus-workbench", "lotus-platform")
        if runtime_mode == "core-manage"
        else (*CANONICAL_REPOSITORIES, "lotus-platform")
    )
    return projects, repositories


def canonical_port_owners_for(
    projects_root: Path,
    workbench: Path,
    runtime_mode: str = "full",
) -> dict[int, dict[str, Any]]:
    """Resolve every canonical host port to its authoritative project checkout."""

    projects, repositories = _canonical_projects_and_repositories(
        projects_root, workbench, runtime_mode
    )
    launcher_projects = {80: "canonical-ingress", 8001: "lotus-manage"}
    if runtime_mode == "full":
        launcher_projects[8111] = "lotus-gateway"
    owners: dict[int, dict[str, Any]] = {
        port: {
            "compose_project": project,
            "working_dir": projects[project],
        }
        for port, project in launcher_projects.items()
    }
    for repo in repositories:
        root = workbench if repo == "lotus-workbench" else projects_root / repo
        if repo == "lotus-platform" or (
            runtime_mode == "core-manage" and repo == "lotus-workbench"
        ):
            continue
        config = json.loads(
            command(["docker", "compose", "config", "--format", "json"], root)
        )
        declared = config.get("name")
        if declared not in projects or not paths_match_exactly(
            projects[declared], str(root)
        ):
            raise ReservationRefusal(f"Undeclared canonical Compose project in {repo}.")
        for service in config["services"].values():
            for port in service.get("ports", []):
                published = str(port.get("published", ""))
                if not published.isdecimal():
                    raise ReservationRefusal(
                        f"Unbounded/dynamic canonical host port in {repo}."
                    )
                host_port = int(published)
                owner = {
                    "compose_project": str(declared),
                    "working_dir": projects[str(declared)],
                }
                existing = owners.get(host_port)
                if existing is None:
                    owners[host_port] = owner
                elif existing.get("ambiguous") is True:
                    if owner not in existing["owners"]:
                        existing["owners"].append(owner)
                        existing["owners"].sort(
                            key=lambda item: (
                                item["compose_project"],
                                item["working_dir"],
                            )
                        )
                elif existing != owner:
                    owners[host_port] = {
                        "ambiguous": True,
                        "owners": sorted(
                            [existing, owner],
                            key=lambda item: (
                                item["compose_project"],
                                item["working_dir"],
                            ),
                        ),
                    }
    return owners


def scope_for(projects_root: Path, workbench: Path, runtime_mode: str = "full") -> dict:
    projects, repositories = _canonical_projects_and_repositories(
        projects_root, workbench, runtime_mode
    )
    sources = {}
    for repo in repositories:
        root = workbench if repo == "lotus-workbench" else projects_root / repo
        sources[repo] = command(["git", "rev-parse", "HEAD"], root).strip()
    owners = canonical_port_owners_for(projects_root, workbench, runtime_mode)
    return {"projects": projects, "ports": sorted(owners), "sources": sources}


def select_containers(items: list, scope: dict) -> list:
    selected = []
    for item in items:
        labels = item.get("Config", {}).get("Labels") or {}
        project = labels.get("com.docker.compose.project", "")
        checkout = labels.get("com.docker.compose.project.working_dir", "")
        ports = sorted(
            {
                int(binding["HostPort"])
                for values in (
                    item.get("HostConfig", {}).get("PortBindings") or {}
                ).values()
                for binding in (values or [])
            }
        )
        ingress = item.get("Name", "").lstrip("/") == "lotus-direct-dev-ingress"
        running = item.get("State", {}).get("Running") is True
        relevant = (
            project in scope["projects"]
            or ingress
            or (running and bool(set(ports) & set(scope["ports"])))
        )
        if not relevant:
            continue  # Incidental certification/test projects on other ports are not canonical.
        if ingress:
            expected_mount = (
                scope["projects"]["canonical-ingress"]
                + "/platform-stack/dev-ingress/Caddyfile.direct-host"
            )
            if not any(
                mount.get("Destination") == "/etc/caddy/Caddyfile"
                and paths_match_exactly(mount.get("Source", ""), expected_mount)
                for mount in item.get("Mounts", [])
            ):
                raise ReservationRefusal(
                    f"Unproven ingress checkout for container {item['Id']}."
                )
            project, checkout = (
                "canonical-ingress",
                scope["projects"]["canonical-ingress"],
            )
        elif (
            project not in scope["projects"]
            or not checkout
            or not paths_match_exactly(checkout, scope["projects"][project])
        ):
            raise ReservationRefusal(
                f"Foreign/unproven container {item['Id']} claims canonical resources."
            )
        selected.append(
            {
                "kind": "container",
                "id": item["Id"],
                "project": project,
                "checkout": normalize_docker_path(checkout),
                "ports": ports,
            }
        )
    selected.sort(key=lambda item: (item["kind"], item["id"]))
    validate_bindings(selected, scope)
    return selected


def observe(scope: dict) -> list:
    ids = command(["docker", "ps", "-aq", "--no-trunc"]).split()
    containers = json.loads(command(["docker", "inspect", *ids])) if ids else []
    bindings = select_containers(containers, scope)
    docker_ports = {port for item in bindings for port in item["ports"]}
    # Windows is the governed local runtime. Inspection failures are not empty evidence.
    expression = r"""
$ErrorActionPreference = 'Stop'
$rows = @(Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -in @(__PORTS__) } | ForEach-Object {
  $p = Get-Process -Id $_.OwningProcess -ErrorAction Stop
  [pscustomobject]@{port=[int]$_.LocalPort; id="$($p.Id):$($p.StartTime.ToUniversalTime().ToString('o'))"; name=$p.ProcessName}
})
ConvertTo-Json -InputObject $rows -Compress
"""
    expression = expression.replace(
        "__PORTS__", ",".join(str(port) for port in scope["ports"])
    )
    listeners = json.loads(
        command(["powershell", "-NoProfile", "-Command", expression])
    )
    hosts: dict[str, list[int]] = {}
    for listener in listeners:
        port = listener["port"]
        if port not in scope["ports"]:
            continue
        docker_proxy = (
            listener["name"].lower().startswith(("com.docker", "docker", "vpnkit"))
        )
        if docker_proxy and port in docker_ports:
            continue
        hosts.setdefault(listener["id"], []).append(port)
    bindings.extend(
        {
            "kind": "host-process",
            "id": identity,
            "project": "host-listener",
            "checkout": "",
            "ports": sorted(set(ports)),
        }
        for identity, ports in hosts.items()
    )
    bindings.sort(key=lambda item: (item["kind"], item["id"]))
    validate_bindings(bindings, scope)
    return bindings
