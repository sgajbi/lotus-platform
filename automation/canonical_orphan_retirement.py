#!/usr/bin/env python3
"""Retire one proven orphan container from a fresh canonical cleanup plan.

The command is deliberately separate from canonical cleanup. It never removes a Compose project,
volume, image, network, or name-matched resource. Execution requires a caller-supplied SHA-256 and
an exact restatement of every target identity field recorded in the read-only plan.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

if __package__:
    from automation.canonical_docker_ownership import (
        COMPOSE_PROJECT_LABEL,
        COMPOSE_WORKING_DIR_LABEL,
        MISSING_LABELLED_CHECKOUT,
        build_cleanup_plan,
        canonical_project_roots,
        collect_registered_worktree_paths,
        inspect_docker,
        normalize_docker_path,
    )
else:
    from canonical_docker_ownership import (  # type: ignore[no-redef]
        COMPOSE_PROJECT_LABEL,
        COMPOSE_WORKING_DIR_LABEL,
        MISSING_LABELLED_CHECKOUT,
        build_cleanup_plan,
        canonical_project_roots,
        collect_registered_worktree_paths,
        inspect_docker,
        normalize_docker_path,
    )

PLAN_SCHEMA_VERSION = "1.1"
SELECTION_POLICY = "compose-ownership-labels-v2"
RECEIPT_SCHEMA_VERSION = "lotus.canonical-orphan-retirement-receipt.v1"
EXECUTION_CONFIRMATION = "RETIRE_EXACT_ORPHAN"


class OrphanRetirementRefused(RuntimeError):
    """Raised when exact orphan ownership cannot be proven."""


class ContainerNotFound(OrphanRetirementRefused):
    """Raised only when Docker proves the exact container no longer exists."""


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _parse_utc_timestamp(value: object, field_name: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise OrphanRetirementRefused(f"{field_name} is missing")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise OrphanRetirementRefused(
            f"{field_name} is not an ISO-8601 timestamp"
        ) from exc
    if parsed.tzinfo is None:
        raise OrphanRetirementRefused(f"{field_name} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _container_name(container: Mapping[str, Any]) -> str:
    name = str(container.get("Name") or "").lstrip("/")
    if name:
        return name
    names = container.get("Names") or []
    return str(names[0]).lstrip("/") if names else ""


def _labels(container: Mapping[str, Any]) -> Mapping[str, str]:
    labels = container.get("Config", {}).get("Labels") or container.get("Labels") or {}
    return labels if isinstance(labels, Mapping) else {}


def inspect_container(container_id: str) -> Mapping[str, Any]:
    result = subprocess.run(
        ["docker", "container", "inspect", container_id],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        diagnostic = f"{result.stderr}\n{result.stdout}".casefold()
        if "no such object" in diagnostic or "no such container" in diagnostic:
            raise ContainerNotFound(f"container {container_id} does not exist")
        raise OrphanRetirementRefused(
            f"container {container_id} cannot be inspected: {result.stderr.strip()}"
        )
    payload = json.loads(result.stdout)
    if not isinstance(payload, list) or len(payload) != 1:
        raise OrphanRetirementRefused(
            "Docker inspect did not return exactly one container"
        )
    if not isinstance(payload[0], Mapping):
        raise OrphanRetirementRefused(
            "Docker inspect returned an invalid container record"
        )
    return payload[0]


def remove_container(container_id: str) -> None:
    subprocess.run(
        ["docker", "container", "rm", "--force", container_id],
        check=True,
        capture_output=True,
        text=True,
    )


def _target_from_plan(plan: Mapping[str, Any], container_id: str) -> Mapping[str, Any]:
    conflicts = plan.get("ownership_conflicts")
    if not isinstance(conflicts, list):
        raise OrphanRetirementRefused("plan ownership_conflicts must be a list")
    matches = [
        item
        for item in conflicts
        if isinstance(item, Mapping) and item.get("id") == container_id
    ]
    if len(matches) != 1:
        raise OrphanRetirementRefused(
            "plan must contain exactly one ownership conflict for the exact container ID"
        )
    target = matches[0]
    if target.get("resource_type"):
        raise OrphanRetirementRefused("resource-only conflicts cannot be retired")
    if target.get("ownership_state") != MISSING_LABELLED_CHECKOUT:
        raise OrphanRetirementRefused(
            "only a missing_labelled_checkout container can be retired"
        )
    return target


def _assert_exact(value: object, expected: str, field_name: str) -> None:
    if value != expected:
        raise OrphanRetirementRefused(f"{field_name} does not match the approved plan")


def _assert_exact_path(value: object, expected: str, field_name: str) -> None:
    if not isinstance(value, str) or normalize_docker_path(
        value
    ) != normalize_docker_path(expected):
        raise OrphanRetirementRefused(f"{field_name} does not match the approved plan")


def validate_orphan_retirement(
    *,
    plan: Mapping[str, Any],
    plan_generated_at: datetime,
    now: datetime,
    max_plan_age_seconds: int,
    container_id: str,
    container_name: str,
    compose_project: str,
    labelled_working_dir: str,
    expected_working_dir: str,
    projects_root: str,
    workbench_repo_path: str,
    live_container: Mapping[str, Any],
    registered_worktrees: set[str],
    path_exists: Callable[[str], bool],
) -> dict[str, Any]:
    if plan.get("schema_version") != PLAN_SCHEMA_VERSION:
        raise OrphanRetirementRefused("unsupported cleanup-plan schema_version")
    if plan.get("selection_policy") != SELECTION_POLICY:
        raise OrphanRetirementRefused("unsupported cleanup-plan selection_policy")
    if max_plan_age_seconds <= 0:
        raise OrphanRetirementRefused("max plan age must be positive")
    age = now.astimezone(timezone.utc) - plan_generated_at
    if age < timedelta(seconds=-30):
        raise OrphanRetirementRefused("cleanup plan timestamp is in the future")
    if age > timedelta(seconds=max_plan_age_seconds):
        raise OrphanRetirementRefused("cleanup plan is stale")

    target = _target_from_plan(plan, container_id)
    _assert_exact(target.get("name"), container_name, "container name")
    _assert_exact(target.get("compose_project"), compose_project, "Compose project")
    _assert_exact_path(
        target.get("compose_working_dir"),
        labelled_working_dir,
        "labelled working directory",
    )
    _assert_exact_path(
        target.get("expected_working_dir"),
        expected_working_dir,
        "expected working directory",
    )

    allowed_roots = canonical_project_roots(projects_root, workbench_repo_path)
    canonical_root = allowed_roots.get(compose_project.casefold())
    if not canonical_root:
        raise OrphanRetirementRefused("Compose project is not canonical")
    _assert_exact_path(
        canonical_root, expected_working_dir, "canonical repository root"
    )

    live_id = str(live_container.get("Id") or live_container.get("ID") or "")
    _assert_exact(live_id, container_id, "live container ID")
    _assert_exact(
        _container_name(live_container), container_name, "live container name"
    )
    live_labels = _labels(live_container)
    _assert_exact(
        live_labels.get(COMPOSE_PROJECT_LABEL), compose_project, "live Compose project"
    )
    _assert_exact_path(
        live_labels.get(COMPOSE_WORKING_DIR_LABEL),
        labelled_working_dir,
        "live labelled working directory",
    )

    if path_exists(labelled_working_dir):
        raise OrphanRetirementRefused("labelled checkout now exists")
    normalized_labelled_path = normalize_docker_path(labelled_working_dir)
    if normalized_labelled_path in {
        normalize_docker_path(worktree) for worktree in registered_worktrees
    }:
        raise OrphanRetirementRefused(
            "labelled checkout is still a registered Git worktree"
        )

    return {
        "plan_fresh": True,
        "exact_plan_target": True,
        "canonical_project": True,
        "live_identity_matches": True,
        "labelled_checkout_absent": True,
        "labelled_checkout_not_registered": True,
        "scope": "exact_container_only",
    }


def build_receipt(
    *,
    status: str,
    plan_path: Path,
    plan_sha256: str,
    execute: bool,
    target: Mapping[str, str],
    checks: Mapping[str, Any] | None = None,
    before: Mapping[str, Any] | None = None,
    after: Mapping[str, Any] | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "action": "retire_exact_orphan_container",
        "mode": "execute" if execute else "dry_run",
        "status": status,
        "plan": {"path": str(plan_path.resolve()), "sha256": plan_sha256},
        "target": dict(target),
        "checks": dict(checks or {}),
        "before": dict(before or {}),
        "after": dict(after or {}),
        "error": error,
        "non_target_scope": {
            "compose_projects": "not_mutated",
            "volumes": "not_mutated",
            "images": "not_mutated",
            "networks": "not_mutated",
        },
    }


def collect_remaining_conflicts(
    *,
    projects_root: str,
    workbench_repo_path: str,
) -> dict[str, Any]:
    """Regenerate ownership evidence without granting any explicit project exception."""

    containers, volumes, images = inspect_docker()
    allowed_roots = canonical_project_roots(projects_root, workbench_repo_path)
    plan = build_cleanup_plan(
        projects_root=projects_root,
        workbench_repo_path=workbench_repo_path,
        containers=containers,
        volumes=volumes,
        images=images,
        registered_worktrees=collect_registered_worktree_paths(allowed_roots),
    )
    return {
        "generated_at": plan["generated_at"],
        "ownership_conflicts": plan["ownership_conflicts"],
    }


def write_receipt(path: Path, receipt: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    temporary_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary_path.replace(path)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--expected-plan-sha256", required=True)
    parser.add_argument("--container-id", required=True)
    parser.add_argument("--container-name", required=True)
    parser.add_argument("--compose-project", required=True)
    parser.add_argument("--labelled-working-dir", required=True)
    parser.add_argument("--expected-working-dir", required=True)
    parser.add_argument("--projects-root", required=True)
    parser.add_argument("--workbench-repo-path", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-plan-age-seconds", type=int, default=300)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirmation", default="")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    target = {
        "id": args.container_id,
        "name": args.container_name,
        "compose_project": args.compose_project,
        "compose_working_dir": args.labelled_working_dir,
        "expected_working_dir": args.expected_working_dir,
    }
    plan_sha256 = ""
    mutation_started = False
    try:
        if args.execute and args.confirmation != EXECUTION_CONFIRMATION:
            raise OrphanRetirementRefused(
                f"execution requires --confirmation {EXECUTION_CONFIRMATION}"
            )
        raw_plan = args.plan.read_bytes()
        plan_sha256 = sha256_bytes(raw_plan)
        if plan_sha256 != args.expected_plan_sha256:
            raise OrphanRetirementRefused("cleanup-plan SHA-256 does not match")
        plan = json.loads(raw_plan)
        if not isinstance(plan, Mapping):
            raise OrphanRetirementRefused("cleanup plan must be a JSON object")
        plan_generated_at = _parse_utc_timestamp(
            plan.get("generated_at"), "generated_at"
        )
        live_container = inspect_container(args.container_id)
        allowed_roots = canonical_project_roots(
            args.projects_root, args.workbench_repo_path
        )
        registered_worktrees = collect_registered_worktree_paths(allowed_roots)
        now = datetime.now(timezone.utc)
        checks = validate_orphan_retirement(
            plan=plan,
            plan_generated_at=plan_generated_at,
            now=now,
            max_plan_age_seconds=args.max_plan_age_seconds,
            container_id=args.container_id,
            container_name=args.container_name,
            compose_project=args.compose_project,
            labelled_working_dir=args.labelled_working_dir,
            expected_working_dir=args.expected_working_dir,
            projects_root=args.projects_root,
            workbench_repo_path=args.workbench_repo_path,
            live_container=live_container,
            registered_worktrees=registered_worktrees,
            path_exists=lambda value: Path(value).exists(),
        )
        before = {
            "container_present": True,
            "id": str(live_container.get("Id") or live_container.get("ID") or ""),
            "name": _container_name(live_container),
            "running": bool(live_container.get("State", {}).get("Running", False)),
            "ownership_conflicts": plan["ownership_conflicts"],
        }
        if args.execute:
            # Persist the approved exact target before mutation. If the final receipt cannot be
            # written, this durable pre-mutation record still distinguishes an interrupted action
            # from an unaudited deletion.
            write_receipt(
                args.output,
                build_receipt(
                    status="validated_pending_execution",
                    plan_path=args.plan,
                    plan_sha256=plan_sha256,
                    execute=True,
                    target=target,
                    checks=checks,
                    before=before,
                ),
            )
            mutation_started = True
            remove_container(args.container_id)
            try:
                inspect_container(args.container_id)
            except ContainerNotFound:
                after = {"container_present": False}
            else:
                raise OrphanRetirementRefused(
                    "container still exists after exact removal"
                )
            after["remaining_conflicts"] = collect_remaining_conflicts(
                projects_root=args.projects_root,
                workbench_repo_path=args.workbench_repo_path,
            )
            status = "retired"
        else:
            after = {
                "container_present": True,
                "mutation_performed": False,
                "remaining_conflicts": {
                    "generated_at": plan["generated_at"],
                    "ownership_conflicts": plan["ownership_conflicts"],
                },
            }
            status = "approved_not_executed"
        receipt = build_receipt(
            status=status,
            plan_path=args.plan,
            plan_sha256=plan_sha256,
            execute=args.execute,
            target=target,
            checks=checks,
            before=before,
            after=after,
        )
        write_receipt(args.output, receipt)
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0
    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
        subprocess.SubprocessError,
        OrphanRetirementRefused,
    ) as exc:
        receipt = build_receipt(
            status="indeterminate_after_mutation" if mutation_started else "refused",
            plan_path=args.plan,
            plan_sha256=plan_sha256,
            execute=args.execute,
            target=target,
            error=str(exc),
        )
        write_receipt(args.output, receipt)
        print(json.dumps(receipt, indent=2, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
