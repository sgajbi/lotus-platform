"""Acquire/preflight/fence/release the machine's one canonical runtime reservation."""

from __future__ import annotations

import argparse
import copy
import json
import os
import tempfile
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

try:
    from automation import canonical_runtime_lease as lease
    from automation import canonical_runtime_refresh as refresh
    from automation.canonical_runtime_inventory import observe, scope_for, paths_match_exactly
    from automation.canonical_runtime_inventory import observe_refresh_resources, observe_prepared_images, command
except ModuleNotFoundError:
    import canonical_runtime_lease as lease
    import canonical_runtime_refresh as refresh
    from canonical_runtime_inventory import observe, scope_for, paths_match_exactly
    from canonical_runtime_inventory import observe_refresh_resources, observe_prepared_images, command


@contextmanager
def exclusive(path: Path, *, refusal_message: str = "Canonical reservation transaction already in progress."):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as stream:
        stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise lease.ReservationRefusal(refusal_message) from exc
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)


def transact(path: Path, action: Callable[[dict], dict], *, write: bool) -> dict:
    with exclusive(path.with_suffix(".lock")):
        book = json.loads(path.read_text(encoding="utf-8")) if path.exists() else lease.empty_book()
        lease.validate_book(book)
        result = action(book)  # Observe at the durable boundary, under the machine book lock.
        lease.validate_book(book)
        if write:
            descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix="reservation-")
            try:
                with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                    json.dump(book, stream, indent=2, sort_keys=True)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(temporary, path)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
        return result


def guarded_transact(path: Path, action: Callable[[dict], dict], *, write: bool,
                     recovery: bool = False) -> dict:
    if not recovery:
        return transact(path, action, write=write)
    # Same order as the shipped adapter: whole-operation fence, then book lock.
    # Never replace a live durable operation while its owner still performs I/O.
    try:
        with exclusive(path.parent / "operation.lock", refusal_message=
                       "Whole-operation lock held or uninspectable; recovery/reclaim refused."):
            return transact(path, action, write=write)
    except OSError as exc:
        raise lease.ReservationRefusal("Whole-operation lock held or uninspectable; recovery/reclaim refused.") from exc


def execute(args: argparse.Namespace, book: dict) -> dict:
    root = Path(args.projects_root).resolve()
    platform = root / "lotus-platform"
    workbench = Path(args.workbench_repo_path).resolve() if args.workbench_repo_path else root / "lotus-workbench"
    lease.require(Path(__file__).resolve().parent.parent == platform,
                  "Use the canonical workspace Platform checkout, not a second reservation authority.")
    if args.action not in {"status", "acquire", "reclaim"}:
        admitted = lease.current(book)
        lease.require(admitted is not None, "No acquired canonical reservation; unreserved resources are not yours.")
        lease.owner(admitted, args.holder, datetime.now(timezone.utc),
                    teardown=args.action in {"preflight-teardown", "begin-teardown", "finish"}
                    or (args.action == "finish-refresh" and args.outcome == "failure"))
    admitted = lease.current(book)
    # Recovery rebinds reviewed live resources to the original reservation; it must not
    # manufacture a new source grant from checkouts that may have advanced meanwhile.
    teardown = args.action in {"preflight-teardown", "begin-teardown", "recover", "reclaim"} or (
        args.action == "finish" and admitted is not None and admitted["operation"] is not None
        and admitted["operation"]["action"] == "teardown"
    )
    # Teardown/reclaim carry the acquired resource/source scope, never manufacture a
    # replacement grant from a later checkout. New changes still require current exact sources.
    if admitted is not None and (teardown or args.action == "status"):
        scope = admitted["scope"]
        if args.action != "status":
            lease.require(paths_match_exactly(scope["projects"]["lotus-workbench"], str(workbench)),
                          "Selected Workbench checkout differs from acquired scope.")
    else:
        mode = getattr(args, "runtime_mode", "full")
        scope = scope_for(root, workbench) if mode == "full" else scope_for(root, workbench, mode)
    inventory = observe(scope)
    now = datetime.now(timezone.utc)
    common = {"holder": args.holder, "scope": scope, "bindings": inventory, "now": now}
    receipt = json.loads(Path(args.handover_receipt).read_text(encoding="utf-8-sig")) if args.handover_receipt else None
    if args.action in {"preview-refresh", "begin-refresh", "preflight-refresh", "prepare-refresh", "finish-refresh", "recover-refresh"}:
        plan_path = getattr(args, "refresh_plan", None)
        if args.action in {"preview-refresh", "begin-refresh"}:
            lease.require(plan_path and getattr(args, "refresh_plan_digest", ""), "Reviewed refresh plan and digest required.")
            plan = json.loads(Path(plan_path).read_text(encoding="utf-8-sig"))
            refresh.validate_plan(admitted, plan, args.refresh_plan_digest)
        else:
            lease.require(admitted["operation"] is not None and "refresh" in admitted["operation"], "No pending refresh operation.")
            plan = admitted["operation"]["refresh"]["plan"]
        for repository in set(plan["repositoryChanges"]) | {item["repository"] for item in plan["services"]}:
            checkout = workbench if repository == "lotus-workbench" else root / repository
            lease.require(not command(["git", "status", "--porcelain"], checkout).strip(), "Refresh sources must be clean committed inputs.")
        for service in plan["services"]:
            checkout = workbench if service["repository"] == "lotus-workbench" else root / service["repository"]
            lease.require(paths_match_exactly(plan["targetScope"]["projects"][service["project"]], str(checkout)),
                          "Planned service repository does not own its project checkout.")
        resources = observe_refresh_resources(scope, inventory)
        common["resources"] = resources
        if args.action in {"preview-refresh", "begin-refresh"}:
            # Exercise identical admission against a copy; preview grants no durable token.
            target = copy.deepcopy(book) if args.action == "preview-refresh" else book
            return refresh.begin(target, **common, plan=plan, plan_digest=args.refresh_plan_digest, token=str(uuid.uuid4()))
        common["token"] = args.operation_token
        if args.action == "preflight-refresh":
            return refresh.preflight(book, **common)
        if args.action == "prepare-refresh":
            lease.require(getattr(args, "prepared_images", None), "Prepared image references required.")
            references = json.loads(Path(args.prepared_images).read_text(encoding="utf-8-sig"))
            return refresh.prepare(book, **common, images=observe_prepared_images(references))
        if args.action == "finish-refresh":
            return refresh.finish(book, **common, outcome=args.outcome)
        common.pop("token")
        return refresh.recover(book, **common, receipt=receipt)
    if args.action == "status":
        return {"current": lease.current(book), "scope": scope, "scopeDigest": lease.digest(scope),
                "bindings": inventory, "bindingsDigest": lease.digest(inventory)}
    if args.action in {"acquire", "reclaim"}:
        return lease.acquire(book, **common, purpose=args.purpose, expires=args.expiry_utc,
                             reservation_id=str(uuid.uuid4()), receipt=receipt, reclaim=args.action == "reclaim")
    if args.action in {"preflight", "preflight-teardown"}:
        return lease.preflight(book, **common, teardown=args.action == "preflight-teardown")
    if args.action == "preflight-operation":
        return lease.operation_preflight(book, **common, token=args.operation_token)
    if args.action in {"begin-change", "begin-teardown"}:
        return lease.begin(book, **common, action="change" if args.action == "begin-change" else "teardown",
                           token=str(uuid.uuid4()))
    if args.action == "finish":
        return lease.finish(book, **common, token=args.operation_token, outcome=args.outcome)
    return lease.recover(book, **common, receipt=receipt)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["status", "acquire", "reclaim", "preflight", "preflight-teardown", "preflight-operation", "begin-change",
                                         "begin-teardown", "finish", "recover", "begin-refresh", "preflight-refresh",
                                         "prepare-refresh", "finish-refresh", "recover-refresh", "preview-refresh"])
    parser.add_argument("--projects-root", required=True)
    parser.add_argument("--workbench-repo-path", default="")
    parser.add_argument("--runtime-mode", choices=["full", "core-manage"], default="full")
    parser.add_argument("--holder", default="")  # Missing identity refuses every mutation, never a grant.
    parser.add_argument("--purpose", default="")
    parser.add_argument("--expiry-utc", default="")
    parser.add_argument("--handover-receipt")
    parser.add_argument("--operation-token", default="")
    parser.add_argument("--refresh-plan")
    parser.add_argument("--refresh-plan-digest", default="")
    parser.add_argument("--prepared-images")
    parser.add_argument("--outcome", choices=["success", "failure"], default="failure")
    args = parser.parse_args()
    path = Path(args.projects_root).resolve() / "lotus-platform/output/canonical-runtime/reservations.v1.json"
    try:
        result = guarded_transact(path, lambda book: execute(args, book),
                                  write=args.action not in {"status", "preflight", "preflight-teardown", "preflight-operation", "preflight-refresh", "preview-refresh"},
                                  recovery=args.action in {"recover", "reclaim", "recover-refresh"})
        print(json.dumps(result, indent=2, sort_keys=True))
        if args.action == "finish" and args.outcome == "success" and result["state"] == "active":
            if result["events"][-1]["operationAction"] == "teardown":
                raise lease.ReservationRefusal("Teardown incomplete; reservation retained.")
        return 0
    except (lease.ReservationRefusal, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Canonical reservation REFUSED: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
