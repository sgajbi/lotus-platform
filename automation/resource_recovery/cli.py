"""Source-safe policy/verification boundary. This CLI has no Docker mutation API."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tarfile
import tempfile
import types
from datetime import datetime, timezone
from pathlib import Path

# Direct isolated invocation loads only this explicitly reviewed repository closure.
_root = Path(__file__).resolve().parents[2]
# Pin the namespace explicitly: an installed regular package must not outrank
# this repository's namespace, nor may an unreviewed initializer execute first.
if (_root / "automation/__init__.py").exists():
    print("UNREVIEWED_PACKAGE_INITIALIZER")
    raise SystemExit(1)
_namespace = types.ModuleType("automation")
_namespace.__path__ = [str(_root / "automation")]
sys.modules["automation"] = _namespace
from automation.resource_recovery import archive_verification as archive  # noqa: E402
from automation.resource_recovery import policy  # noqa: E402


def write_private(path: Path, value: dict) -> None:
    policy.safe_path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, sort_keys=True)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def validate_local(args: argparse.Namespace) -> dict:
    approval = policy.read_json(args.approval, args.expected_approval_sha256)
    policy.validate_approval(approval, now=datetime.now(timezone.utc))
    policy.validate_sources(approval, args.root)
    policy.require(
        args.plan is not None and args.inventory is not None,
        "DISCOVERY_ARGUMENTS_REQUIRED",
    )
    plan = policy.read_json(args.plan, approval["plan_sha256"])
    inventory = policy.read_json(args.inventory, approval["inventory_sha256"])
    if approval["schema_version"] == policy.RENEWAL_SCHEMA:
        policy.require(
            args.archive_approval is not None, "ORIGINAL_ARCHIVE_APPROVAL_REQUIRED"
        )
        original = policy.read_json(
            args.archive_approval, approval["archive_approval_sha256"]
        )
        policy.validate_renewal(approval, original)
        policy.require(
            args.action
            in {"validate-local", "prepare", "check-target", "verify-retirement"},
            "RETIREMENT_ONLY_RENEWAL",
        )
    policy.validate_discovery(approval, plan, inventory)
    storage = policy.safe_path(Path(approval["archive_root"]))
    policy.require(storage.is_dir(), "ARCHIVE_STORAGE_MUST_EXIST")
    if os.name != "nt":
        policy.require(
            storage.stat().st_mode & 0o077 == 0, "PRIVATE_ARCHIVE_STORAGE_REQUIRED"
        )
    return approval


def admit_current(args: argparse.Namespace, approval: dict) -> None:
    if args.phase == "retire":
        archive_sha = approval.get(
            "archive_approval_sha256", args.expected_approval_sha256
        )
        immutable_directory = Path(approval["archive_root"]) / archive_sha / "archives"
        policy.require(
            not args.directory.resolve().is_relative_to(immutable_directory.resolve()),
            "IMMUTABLE_ARCHIVE_PATH",
        )
    policy.require(
        all(
            getattr(args, name) is not None
            for name in ("plan", "inventory", "snapshot")
        ),
        "OBSERVATION_ARGUMENTS_REQUIRED",
    )
    plan = policy.read_json(args.plan, approval["plan_sha256"])
    inventory = policy.read_json(args.inventory, approval["inventory_sha256"])
    policy.require(
        args.expected_snapshot_sha256 is not None, "LIVE_OBSERVATION_DIGEST_REQUIRED"
    )
    snapshot = policy.read_json(args.snapshot, args.expected_snapshot_sha256)
    policy.require(
        snapshot.get("approval_sha256") == args.expected_approval_sha256,
        "LIVE_APPROVAL_CHANGED",
    )
    records = policy.admit(
        approval,
        plan,
        inventory,
        snapshot,
        now=datetime.now(timezone.utc),
        phase=args.phase,
        target_index=args.target_index if args.action == "check-target" else None,
    )
    if args.action == "check-target":
        policy.require(args.target_index is not None, "TARGET_INDEX_REQUIRED")
        return
    policy.require(
        not (args.directory / "prepared.json").exists(), "IMMUTABLE_PREPARED_EXISTS"
    )
    write_private(
        args.directory / "prepared.json",
        {
            "approval_sha256": args.expected_approval_sha256,
            "targets": [
                {"target": target, "original": record}
                for target, record in zip(approval["targets"], records, strict=True)
            ],
        },
    )


def verified_archives(args: argparse.Namespace, approval: dict) -> list[dict]:
    prepared = policy.read_json(args.directory / "prepared.json")
    policy.require(
        prepared["approval_sha256"]
        == approval.get("archive_approval_sha256", args.expected_approval_sha256),
        "PREPARED_APPROVAL_CHANGED",
    )
    policy.require(
        [item["target"] for item in prepared["targets"]] == approval["targets"],
        "PREPARED_TARGETS_CHANGED",
    )
    for item in prepared["targets"]:
        policy.require(
            policy.fingerprint(item["target"]["kind"], item["original"])
            == item["target"]["inspect_sha256"],
            "PREPARED_IDENTITY_CHANGED",
        )
    results = []
    if args.action == "verify-archive":
        policy.require(
            type(args.target_index) is int
            and 0 <= args.target_index < len(prepared["targets"]),
            "INVALID_TARGET_INDEX",
        )
    for index, item in enumerate(prepared["targets"]):
        if args.action == "verify-archive" and index != args.target_index:
            continue
        target, original = item["target"], item["original"]
        folder = args.directory / str(index)
        identity = None
        if target["kind"] == "image":
            identity = archive.image_identity(
                folder / "image.tar", original, approval["max_archive_bytes"]
            )
            hashed = identity["archive_sha256"]
            if args.action != "verify-archive" or args.check_restored:
                archive.verify_restored_image(
                    original, policy.read_json(folder / "restored.json"), identity
                )
        else:
            manifest = policy.read_json(folder / "files.json")
            hashed = archive.verify_volume(
                folder / "volume.tar", manifest, approval["max_archive_bytes"]
            )
            if args.action != "verify-archive":
                archive.verify_restored_volume(
                    manifest, policy.read_json(folder / "restored-files.json")
                )
        results.append(
            {
                "kind": target["kind"],
                "id": target["id"],
                "inspect_sha256": target["inspect_sha256"],
                "archive_sha256": hashed,
            }
        )
        if identity is not None:
            results[-1]["image_identity"] = identity
        if args.action == "verify-archive" and identity is not None:
            print(json.dumps(identity, sort_keys=True))
    return results


def execute(args: argparse.Namespace) -> None:
    if args.action == "protected-roots":
        from automation.canonical_docker_ownership import (
            canonical_project_roots,
            collect_registered_worktree_paths,
        )

        policy.require(
            args.projects_root is not None and args.workbench_repo_path is not None,
            "CURRENT_ROOT_ARGUMENTS_REQUIRED",
        )
        roots = canonical_project_roots(
            str(args.projects_root), str(args.workbench_repo_path)
        )
        print(
            json.dumps(
                sorted(
                    set(roots.values()) | set(collect_registered_worktree_paths(roots))
                )
            )
        )
        return
    policy.require(
        args.approval is not None and args.expected_approval_sha256 is not None,
        "EXPLICIT_APPROVAL_REQUIRED",
    )
    approval = validate_local(args)
    if args.action == "validate-local":
        return
    policy.require(args.directory is not None, "DIRECTORY_REQUIRED")
    directory = policy.safe_path(args.directory)
    policy.require(
        directory.is_relative_to(policy.safe_path(Path(approval["archive_root"]))),
        "ARCHIVE_DIRECTORY_ESCAPE",
    )
    if args.action in {"prepare", "check-target"}:
        admit_current(args, approval)
        return
    results = verified_archives(args, approval)
    if args.action == "verify-archive":
        return
    if args.action == "verify":
        write_private(
            args.directory / "verification.json",
            {
                "schema_version": "lotus.resource-recovery.verification.v1",
                "approval_sha256": args.expected_approval_sha256,
                "source_daemon": approval["source_daemon"],
                "verification_daemon": approval["verification_daemon"],
                "targets": results,
            },
        )
    else:
        policy.require(
            args.receipt is not None and args.expected_receipt_sha256 is not None,
            "VERIFICATION_RECEIPT_REQUIRED",
        )
        archive_approval_sha = approval.get(
            "archive_approval_sha256", args.expected_approval_sha256
        )
        policy.require(
            approval.get("archive_receipt_sha256", args.expected_receipt_sha256)
            == args.expected_receipt_sha256,
            "RENEWAL_RECEIPT_CHANGED",
        )
        receipt = policy.read_json(args.receipt, args.expected_receipt_sha256)
        policy.require(
            receipt.get("status") == "archive_verified"
            and receipt.get("approval_sha256") == archive_approval_sha,
            "UNFINISHED_VERIFICATION_RECEIPT",
        )
        verification = policy.read_json(
            args.directory / "verification.json", receipt["verification_sha256"]
        )
        policy.require(
            verification.get("schema_version")
            == "lotus.resource-recovery.verification.v1"
            and verification.get("approval_sha256") == archive_approval_sha
            and verification.get("source_daemon") == approval["source_daemon"]
            and verification.get("verification_daemon")
            == approval["verification_daemon"],
            "VERIFICATION_IDENTITY_CHANGED",
        )
        policy.require(
            verification["targets"] == results, "VERIFICATION_RESULT_CHANGED"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=[
            "validate-local",
            "prepare",
            "check-target",
            "verify-archive",
            "verify",
            "verify-retirement",
            "protected-roots",
        ],
    )
    for name in (
        "approval",
        "root",
        "plan",
        "inventory",
        "snapshot",
        "directory",
        "receipt",
        "archive-approval",
        "projects-root",
        "workbench-repo-path",
    ):
        parser.add_argument("--" + name, type=Path, required=name == "root")
    parser.add_argument("--expected-approval-sha256")
    parser.add_argument("--expected-receipt-sha256")
    parser.add_argument("--expected-snapshot-sha256")
    parser.add_argument("--target-index", type=int)
    parser.add_argument("--check-restored", action="store_true")
    parser.add_argument(
        "--phase", choices=["dry-run", "archive-verify", "retire"], default="dry-run"
    )
    args = parser.parse_args(argv)
    try:
        execute(args)
        if args.action != "protected-roots":
            print("RESOURCE_RECOVERY_CHECK_PASSED")
        return 0
    except policy.Refused as exc:
        print(str(exc))
        return 1
    except (
        OSError,
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
        IndexError,
        OverflowError,
        tarfile.TarError,
    ):
        print("RESOURCE_RECOVERY_CHECK_FAILED")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
