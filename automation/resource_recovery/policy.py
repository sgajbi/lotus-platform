"""Admission for operator-reviewed resource-only recovery, never ownership inference."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from automation.canonical_docker_ownership import normalize_docker_path

SCHEMA = "lotus.resource-recovery.disposition.v2"
RENEWAL_SCHEMA = "lotus.resource-recovery.retirement.v2"
RENEWAL_FIELDS = {"archive_approval_sha256", "archive_receipt_sha256"}
RENEWABLE_FIELDS = {
    "schema_version",
    "approved_at",
    "expires_at",
}
FIELDS = {
    "schema_version",
    "operator",
    "approved_at",
    "expires_at",
    "source_context",
    "source_daemon",
    "verification_context",
    "verification_daemon",
    "plan_sha256",
    "inventory_sha256",
    "helper_root",
    "helper_files",
    "primary_head",
    "targets",
    "archive_root",
    "retain_until",
    "retention_authority",
    "archiver_image",
    "max_archive_bytes",
    "discovery",
    "runtime_authority",
}
LIVE_SCHEMA = "lotus.resource-recovery.live-observation.v1"
LIVE_FIELDS = {
    "schema_version",
    "run_id",
    "operation_token",
    "phase",
    "target_indexes",
    "approval_sha256",
    "discovery_receipt_sha256",
    "collection_started_at",
    "collection_finished_at",
    "source_context",
    "source_daemon",
    "verification_context",
    "verification_daemon",
    "holder",
    "scope_digest",
    "source_heads",
    "helper_files",
    "container_ids_before",
    "container_ids_after",
    "containers",
    "images",
    "volumes",
    "protected_checkout_paths",
}
HELPER_FILES = {
    "automation/Invoke-ResourceOnlyRecovery.ps1",
    "automation/resource_recovery/__init__.py",
    "automation/resource_recovery/policy.py",
    "automation/resource_recovery/archive_verification.py",
    "automation/resource_recovery/volume_io.py",
    "automation/resource_recovery/cli.py",
    "automation/canonical_docker_ownership.py",
}
SHA = re.compile(r"[0-9a-f]{64}")
IMAGE = re.compile(r"sha256:[0-9a-f]{64}")
VOLUME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,254}")


class Refused(ValueError):
    """Only a bounded reason code may cross the operator output boundary."""


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise Refused(reason)


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def file_digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def _unique_object(pairs: list[tuple[str, Any]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        require(key not in result, "DUPLICATE_JSON_FIELD")
        result[key] = value
    return result


def read_json(path: Path, expected: str | None = None) -> dict:
    safe_path(path)
    require(
        path.is_file() and path.stat().st_size <= 16 * 1024 * 1024,
        "JSON_BUDGET_OR_ABSENCE",
    )
    raw = path.read_bytes()
    if expected is not None:
        require(bool(SHA.fullmatch(expected)), "INVALID_DIGEST")
        require(hashlib.sha256(raw).hexdigest() == expected, "ARTIFACT_DIGEST_MISMATCH")
    value = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_unique_object)
    require(isinstance(value, dict), "INVALID_JSON_OBJECT")
    return value


def safe_path(path: Path) -> Path:
    require(path.is_absolute(), "ABSOLUTE_PATH_REQUIRED")
    for part in (path, *path.parents):
        if not part.exists() and not part.is_symlink():
            continue
        info = part.lstat()
        require(not stat.S_ISLNK(info.st_mode), "REPARSE_PATH_REFUSED")
        attributes = getattr(info, "st_file_attributes", 0)
        require(
            not attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 1024),
            "REPARSE_PATH_REFUSED",
        )
    return path.resolve()


def utc(value: Any) -> datetime:
    require(isinstance(value, str), "INVALID_TIME")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise Refused("INVALID_TIME") from exc
    require(parsed.utcoffset() == timedelta(0), "UTC_TIME_REQUIRED")
    return parsed


def fresh(value: Any, now: datetime, max_age: int = 300) -> None:
    age = now - utc(value)
    require(timedelta(0) <= age <= timedelta(seconds=max_age), "STALE_OBSERVATION")


def fingerprint(kind: str, record: dict) -> str:
    fields = (
        (
            "Id",
            "RepoTags",
            "RepoDigests",
            "Created",
            "Architecture",
            "Os",
            "Config",
            "RootFS",
        )
        if kind == "image"
        else ("Name", "CreatedAt", "Driver", "Options", "Labels", "Mountpoint", "Scope")
    )
    return digest({field: record.get(field) for field in fields})


def validate_sources(approval: dict, actual_root: Path) -> None:
    root = safe_path(actual_root)
    require(
        normalize_docker_path(str(root))
        == normalize_docker_path(approval["helper_root"]),
        "HELPER_ROOT_CHANGED",
    )
    files = approval["helper_files"]
    require(
        isinstance(files, dict) and set(files) == HELPER_FILES,
        "HELPER_CLOSURE_REQUIRED",
    )
    for relative, expected in files.items():
        candidate = safe_path(root / relative)
        require(candidate.is_relative_to(root), "HELPER_ESCAPE")
        require(
            candidate.is_file() and file_digest(candidate) == expected,
            "HELPER_SOURCE_CHANGED",
        )


def validate_approval(approval: dict, *, now: datetime) -> None:
    require(
        approval.get("schema_version")
        not in {
            "lotus.resource-recovery.disposition.v1",
            "lotus.resource-recovery.retirement.v1",
        },
        "UNSUPPORTED_INTERMEDIATE_SCHEMA",
    )
    renewal = approval.get("schema_version") == RENEWAL_SCHEMA
    require(
        set(approval) == (FIELDS | RENEWAL_FIELDS if renewal else FIELDS)
        and approval.get("schema_version") in {SCHEMA, RENEWAL_SCHEMA},
        "INVALID_DISPOSITION",
    )
    if renewal:
        for field in RENEWAL_FIELDS:
            require(
                isinstance(approval[field], str)
                and bool(SHA.fullmatch(approval[field])),
                "ARCHIVE_BINDING_REQUIRED",
            )
    for field in ("plan_sha256", "inventory_sha256"):
        require(
            isinstance(approval[field], str) and bool(SHA.fullmatch(approval[field])),
            "EVIDENCE_DIGEST_REQUIRED",
        )
    discovery = approval["discovery"]
    require(
        isinstance(discovery, dict)
        and set(discovery)
        == {
            "schema_version",
            "capture_sha256",
            "capture_receipt_sha256",
            "capture_started_at",
            "capture_finished_at",
            "capture_path",
            "capture_receipt_path",
            "native_manifest",
            "operator_attestation",
        }
        and discovery["schema_version"] == "lotus.resource-recovery.discovery.v1",
        "DISCOVERY_CLOSURE_REQUIRED",
    )
    for field in ("capture_sha256", "capture_receipt_sha256"):
        require(bool(SHA.fullmatch(discovery[field])), "DISCOVERY_DIGEST_REQUIRED")
    start, finish = (
        utc(discovery["capture_started_at"]),
        utc(discovery["capture_finished_at"]),
    )
    require(
        start <= finish <= now and finish - start <= timedelta(seconds=300),
        "INVALID_DISCOVERY_COLLECTION",
    )
    authority = approval["runtime_authority"]
    require(
        isinstance(authority, dict)
        and set(authority)
        == {"holder", "scope_digest", "source_heads", "observation_schema"}
        and authority["observation_schema"] == LIVE_SCHEMA
        and bool(authority["holder"])
        and bool(authority["source_heads"])
        and bool(re.fullmatch(r"sha256:[0-9a-f]{64}", authority["scope_digest"])),
        "RUNTIME_AUTHORITY_REQUIRED",
    )
    require(
        all(
            isinstance(repo, str)
            and isinstance(head, str)
            and bool(re.fullmatch(r"[0-9a-f]{40}", head))
            for repo, head in authority["source_heads"].items()
        ),
        "SOURCE_HEADS_REQUIRED",
    )
    require(
        authority["source_heads"].get("lotus-platform") == approval["primary_head"],
        "PRIMARY_SOURCE_BINDING_CHANGED",
    )
    attestation = discovery["operator_attestation"]
    require(
        isinstance(attestation, dict)
        and set(attestation)
        == {
            "reviewer",
            "capture_receipt_sha256",
            "scope_digest",
            "source_heads",
            "admission_record",
        }
        and attestation["reviewer"] == approval["operator"]
        and attestation["reviewer"] != authority["holder"]
        and attestation["capture_receipt_sha256"] == discovery["capture_receipt_sha256"]
        and attestation["scope_digest"] == authority["scope_digest"]
        and attestation["source_heads"] == authority["source_heads"]
        and isinstance(attestation["admission_record"], str)
        and bool(attestation["admission_record"]),
        "INDEPENDENT_DISCOVERY_REVIEW_REQUIRED",
    )
    for field in ("operator", "source_context", "source_daemon", "retention_authority"):
        require(
            isinstance(approval[field], str) and bool(approval[field].strip()),
            "EXPLICIT_AUTHORITY_REQUIRED",
        )
    require(
        utc(approval["approved_at"]) <= now < utc(approval["expires_at"]),
        "DISPOSITION_EXPIRED",
    )
    require(
        utc(approval["retain_until"]) > utc(approval["expires_at"]),
        "RETENTION_DECISION_REQUIRED",
    )
    require(
        bool(re.fullmatch(r"[0-9a-f]{40}", approval["primary_head"])),
        "PRIMARY_SOURCE_REQUIRED",
    )
    require(
        bool(IMAGE.fullmatch(approval["archiver_image"])), "IMMUTABLE_ARCHIVER_REQUIRED"
    )
    require(
        type(approval["max_archive_bytes"]) is int
        and approval["max_archive_bytes"] > 0,
        "ARCHIVE_BUDGET_REQUIRED",
    )
    safe_path(Path(approval["archive_root"]))
    targets = approval["targets"]
    require(isinstance(targets, list) and bool(targets), "EXACT_ALLOWLIST_REQUIRED")
    seen: set[tuple[str, str]] = set()
    for target in targets:
        require(
            isinstance(target, dict)
            and set(target) == {"kind", "id", "inspect_sha256"},
            "INVALID_TARGET",
        )
        require(target["kind"] in {"image", "volume"}, "INVALID_RESOURCE_KIND")
        pattern = IMAGE if target["kind"] == "image" else VOLUME
        require(bool(pattern.fullmatch(target["id"])), "EXACT_RESOURCE_ID_REQUIRED")
        require(
            bool(SHA.fullmatch(target["inspect_sha256"])),
            "RESOURCE_FINGERPRINT_REQUIRED",
        )
        key = (target["kind"], target["id"])
        require(key not in seen, "DUPLICATE_TARGET")
        seen.add(key)


def validate_renewal(approval: dict, original: dict) -> None:
    """Historical archive admission is provenance, never current permission."""
    require(
        approval.get("schema_version") == RENEWAL_SCHEMA
        and original.get("schema_version") == SCHEMA,
        "ORIGINAL_ARCHIVE_DISPOSITION_REQUIRED",
    )
    # Validate the original's bounded window at its historical decision time.
    # Current expiry/freshness comes only from the separate renewed admission.
    validate_approval(original, now=utc(original["approved_at"]))
    require(
        utc(original["approved_at"]) <= utc(approval["approved_at"]),
        "RENEWAL_PRECEDES_ARCHIVE_APPROVAL",
    )
    for field in FIELDS - RENEWABLE_FIELDS:
        require(approval[field] == original[field], "RENEWAL_IDENTITY_CHANGED")


def _record(snapshot: dict, kind: str, identifier: str) -> dict:
    records = snapshot["images" if kind == "image" else "volumes"]
    matches = [
        item
        for item in records
        if item.get("Id" if kind == "image" else "Name") == identifier
    ]
    require(len(matches) == 1, "TARGET_ABSENT_OR_AMBIGUOUS")
    return matches[0]


def validate_target(target: dict, snapshot: dict, plan: dict) -> dict:
    kind, identifier = target["kind"], target["id"]
    matches = [
        item
        for item in plan["ownership_conflicts"]
        if item.get("id") == identifier and item.get("resource_type") == kind
    ]
    require(
        len(matches) == 1
        and matches[0].get("ownership_state") == "unproven_resource_only_owner",
        "RESOURCE_ONLY_CONFLICT_REQUIRED",
    )
    record = _record(snapshot, kind, identifier)
    require(
        fingerprint(kind, record) == target["inspect_sha256"],
        "RESOURCE_IDENTITY_CHANGED",
    )
    labels = (
        (record.get("Config") or {}).get("Labels")
        if kind == "image"
        else record.get("Labels")
    ) or {}
    project = labels.get("com.docker.compose.project")
    require(
        isinstance(project, str) and bool(project.strip()),
        "UNLABELLED_RESOURCE_EXCLUDED",
    )
    require(project == matches[0].get("compose_project"), "PROJECT_CHANGED")
    protected = {normalize_docker_path(path) for path in plan["registered_worktrees"]}
    protected.update(
        normalize_docker_path(path)
        for path in plan["allowed_compose_projects"].values()
    )
    protected.update(
        normalize_docker_path(path)
        for path in snapshot.get("protected_checkout_paths", [])
    )
    for field in (
        "com.lotus.repository.checkout",
        "com.docker.compose.project.working_dir",
    ):
        checkout = labels.get(field)
        if checkout:
            require(
                normalize_docker_path(checkout) not in protected
                and not os.path.lexists(checkout),
                "ACTIVE_OWNER_EXCLUDED",
            )
    for container in snapshot["containers"]:
        used = (
            container.get("Image") == identifier
            if kind == "image"
            else any(
                mount.get("Type") == "volume" and mount.get("Name") == identifier
                for mount in container.get("Mounts", [])
            )
        )
        require(not used, "RESOURCE_HAS_CONSUMER")
    require(
        "buildkit" not in identifier.casefold()
        and "buildkit" not in project.casefold(),
        "BUILDKIT_EXCLUDED",
    )
    return record


def _discovery_list(kind: str, argv: list, output: str, listed: dict) -> list[str]:
    flags = {
        "container": ["--all", "--quiet", "--no-trunc"],
        "image": ["--all", "--quiet", "--no-trunc"],
        "network": ["--quiet", "--no-trunc"],
        "volume": ["--quiet"],
    }
    require(kind not in listed and argv[5:] == flags[kind], "DISCOVERY_LIST_CHANGED")
    values = output.splitlines()
    pattern = (
        VOLUME
        if kind == "volume"
        else (IMAGE if kind == "image" else re.compile(r"[0-9a-f]{64}"))
    )
    require(
        all(bool(pattern.fullmatch(value)) for value in values)
        and (kind == "image" or len(values) == len(set(values))),
        "DISCOVERY_LIST_IDENTITIES_INVALID",
    )
    return values


def _discovery_records(
    kind: str,
    records: list,
    ids: list,
    capture: dict,
    inventory: dict,
    image_alias_counts: Counter,
) -> None:
    key = "Name" if kind == "volume" else "Id"
    actual = [record.get(key) for record in records]
    require(
        len(set(actual)) == len(actual) and sorted(actual) == ids,
        "DISCOVERY_COVERAGE_LOST",
    )
    if kind == "image":
        tags = {record["Id"]: record.get("RepoTags") or [] for record in records}
        require(
            all(
                count == 1 or count == len(tags[identity])
                for identity, count in image_alias_counts.items()
            ),
            "UNPROVEN_IMAGE_LIST_ALIAS",
        )
    require(
        digest(records) == digest(capture.get(f"{kind}s")), "DISCOVERY_RECORDS_CHANGED"
    )
    if kind != "network":
        require(
            digest(records) == digest(inventory.get(f"{kind}s")),
            "DISCOVERY_INVENTORY_CHANGED",
        )


def validate_discovery(approval: dict, plan: dict, inventory: dict) -> None:
    """Historical raw native closure, explicitly approved; never current authority."""
    discovery = approval["discovery"]
    capture = read_json(Path(discovery["capture_path"]), discovery["capture_sha256"])
    receipt = read_json(
        Path(discovery["capture_receipt_path"]), discovery["capture_receipt_sha256"]
    )
    require(
        receipt.get("status") == "review-input-only-no-approval-generated"
        and receipt.get("source_daemon") == approval["source_daemon"]
        and capture.get("source_daemon") == approval["source_daemon"],
        "DISCOVERY_SOURCE_CHANGED",
    )
    require(
        receipt.get("source_baseline_sha256") == discovery["capture_sha256"]
        and receipt.get("inventory_sha256") == approval["inventory_sha256"]
        and receipt.get("plan_sha256") == approval["plan_sha256"],
        "DISCOVERY_ARTIFACT_CHANGED",
    )
    require(
        capture.get("observed_at") == discovery["capture_started_at"]
        and inventory.get("captured_at") == discovery["capture_started_at"],
        "DISCOVERY_START_CHANGED",
    )
    require(
        utc(discovery["capture_finished_at"])
        <= utc(plan["generated_at"])
        <= utc(approval["approved_at"]),
        "DISCOVERY_PLAN_TIME_CHANGED",
    )
    manifest = discovery["native_manifest"]
    calls = receipt.get("native_calls")
    require(
        isinstance(manifest, list)
        and len(manifest) > 0
        and len(manifest) % 2 == 0
        and isinstance(calls, list)
        and len(calls) == len(manifest),
        "NATIVE_MANIFEST_REQUIRED",
    )
    listed, inspected = (
        {},
        {kind: [] for kind in ("container", "image", "volume", "network")},
    )
    image_alias_counts: Counter = Counter()
    seen_paths: set[str] = set()
    previous_stop = utc(discovery["capture_started_at"])
    executable = None
    for index, entry in enumerate(manifest):
        require(
            isinstance(entry, dict)
            and set(entry)
            == {"request", "request_sha256", "response", "response_sha256"},
            "INVALID_NATIVE_MANIFEST",
        )
        require(
            all(
                entry[key] == calls[index].get(key)
                for key in ("request", "request_sha256", "response")
            ),
            "NATIVE_MANIFEST_CHANGED",
        )
        for key in ("request", "response"):
            resolved = str(safe_path(Path(entry[key])))
            require(resolved not in seen_paths, "DUPLICATE_NATIVE_ARTIFACT")
            seen_paths.add(resolved)
        request = read_json(Path(entry["request"]), entry["request_sha256"])
        response = read_json(Path(entry["response"]), entry["response_sha256"])
        require(
            set(request) == {"argv", "timeout_seconds", "terminate_owned_cli"}
            and request["timeout_seconds"] == 60
            and request["terminate_owned_cli"] is True,
            "NATIVE_BOUNDARY_CHANGED",
        )
        argv = request["argv"]
        require(
            isinstance(argv, list)
            and len(argv) >= 5
            and all(isinstance(v, str) for v in argv)
            and argv[1:3] == ["--context", approval["source_context"]],
            "NATIVE_SOURCE_CHANGED",
        )
        executable = argv[0] if executable is None else executable
        require(
            argv[0] == executable
            and Path(argv[0]).name.casefold() in {"docker", "docker.exe"},
            "NATIVE_EXECUTABLE_CHANGED",
        )
        require(
            response.get("request_sha256") == entry["request_sha256"]
            and response.get("accepted") is True
            and response.get("producer_stopped") is True
            and response.get("native_exit") == 0
            and response.get("status") == "exited"
            and response.get("stdout_truncated") is False
            and response.get("stderr_truncated") is False
            and not response.get("journal_failed"),
            "DISCOVERY_NATIVE_NOT_SUCCESSFUL",
        )
        birth = datetime.fromisoformat(response["started_at"].replace("Z", "+00:00"))
        stop = datetime.fromisoformat(response["stopped_at"].replace("Z", "+00:00"))
        require(
            birth.utcoffset() is not None
            and stop.utcoffset() is not None
            and previous_stop <= birth <= stop <= utc(discovery["capture_finished_at"]),
            "DISCOVERY_NATIVE_TIME_CHANGED",
        )
        previous_stop = stop
        output = response["stdout"]
        require(
            hashlib.sha256(output.encode()).hexdigest()
            == response.get("stdout_sha256"),
            "DISCOVERY_OUTPUT_CHANGED",
        )
        if index % 2 == 0:
            require(
                argv[3:] == ["info", "--format", "{{.ID}}"]
                and output.strip() == approval["source_daemon"],
                "DISCOVERY_DAEMON_NOT_PROVEN",
            )
            continue
        kind, action = argv[3:5]
        require(kind in inspected, "DISCOVERY_RESOURCE_KIND_CHANGED")
        if action == "ls":
            values = _discovery_list(kind, argv, output, listed)
            if kind == "image":
                image_alias_counts = Counter(values)
            listed[kind] = sorted(set(values))
        else:
            require(
                action == "inspect" and kind in listed and bool(argv[5:]),
                "DISCOVERY_INSPECT_CHANGED",
            )
            records = json.loads(output, object_pairs_hook=_unique_object)
            require(isinstance(records, list), "DISCOVERY_INSPECT_CHANGED")
            key = "Name" if kind == "volume" else "Id"
            require(
                [record.get(key) for record in records] == argv[5:],
                "DISCOVERY_INSPECT_COVERAGE_LOST",
            )
            inspected[kind].extend(records)
    require(
        previous_stop == utc(discovery["capture_finished_at"]),
        "DISCOVERY_FINISH_CHANGED",
    )
    require(set(listed) == set(inspected), "DISCOVERY_INCOMPLETE_KINDS")
    for kind, records in inspected.items():
        _discovery_records(
            kind, records, listed[kind], capture, inventory, image_alias_counts
        )
    for target in approval["targets"]:
        # Historical selection and exact inspection identity, not historical consumer permission.
        historical = {**capture, "containers": []}
        validate_target(target, historical, plan)


def validate_live(
    approval: dict, snapshot: dict, now: datetime, phase: str, target_index: int | None
) -> None:
    require(
        set(snapshot) == LIVE_FIELDS and snapshot.get("schema_version") == LIVE_SCHEMA,
        "LIVE_OBSERVATION_REQUIRED",
    )
    fresh(snapshot["collection_started_at"], now)
    require(
        utc(snapshot["collection_started_at"])
        <= utc(snapshot["collection_finished_at"])
        <= now,
        "LIVE_COLLECTION_TIME_CHANGED",
    )
    authority = approval["runtime_authority"]
    for field in ("holder", "scope_digest", "source_heads"):
        require(snapshot[field] == authority[field], "LIVE_AUTHORITY_CHANGED")
    require(
        snapshot["phase"] == phase
        and snapshot["target_indexes"]
        == (
            list(range(len(approval["targets"])))
            if target_index is None
            else [target_index]
        ),
        "LIVE_PHASE_OR_TARGET_CHANGED",
    )
    require(
        snapshot["helper_files"] == approval["helper_files"]
        and snapshot["discovery_receipt_sha256"]
        == approval["discovery"]["capture_receipt_sha256"]
        and bool(re.fullmatch(r"[0-9a-f-]{36}", snapshot["operation_token"]))
        and bool(re.fullmatch(r"[0-9a-f]{32}", snapshot["run_id"])),
        "LIVE_PROVENANCE_CHANGED",
    )
    before, after = snapshot["container_ids_before"], snapshot["container_ids_after"]
    ids = [record.get("Id") for record in snapshot["containers"]]
    require(
        isinstance(before, list)
        and isinstance(after, list)
        and all(
            isinstance(v, str) and bool(re.fullmatch(r"[0-9a-f]{64}", v))
            for v in before + after + ids
        )
        and len(set(before)) == len(before)
        and len(set(after)) == len(after)
        and len(set(ids)) == len(ids)
        and set(before) == set(after) == set(ids),
        "LIVE_CONSUMER_COVERAGE_LOST",
    )
    for container in snapshot["containers"]:
        require(
            isinstance(container.get("Image"), str)
            and bool(IMAGE.fullmatch(container["Image"]))
            and isinstance(container.get("State"), dict)
            and type(container["State"].get("Running")) is bool
            and isinstance(container.get("Mounts"), list),
            "LIVE_CONSUMER_METADATA_INCOMPLETE",
        )
        for mount in container["Mounts"]:
            require(
                isinstance(mount, dict)
                and isinstance(mount.get("Type"), str)
                and bool(mount["Type"])
                and (
                    mount["Type"] != "volume"
                    or (
                        isinstance(mount.get("Name"), str)
                        and bool(VOLUME.fullmatch(mount["Name"]))
                    )
                ),
                "LIVE_CONSUMER_METADATA_INCOMPLETE",
            )
    indexes = snapshot["target_indexes"]
    for kind, key in (("image", "Id"), ("volume", "Name")):
        expected = {
            approval["targets"][i]["id"]
            for i in indexes
            if approval["targets"][i]["kind"] == kind
        }
        actual = [record.get(key) for record in snapshot[f"{kind}s"]]
        require(
            len(actual) == len(set(actual)) and set(actual) == expected,
            "LIVE_TARGET_COVERAGE_LOST",
        )
    require(
        isinstance(snapshot["protected_checkout_paths"], list)
        and all(
            isinstance(path, str) and bool(path)
            for path in snapshot["protected_checkout_paths"]
        ),
        "CURRENT_OWNER_PROTECTION_REQUIRED",
    )


def admit(
    approval: dict,
    plan: dict,
    inventory: dict,
    snapshot: dict,
    *,
    now: datetime,
    phase: str,
    target_index: int | None = None,
) -> list[dict]:
    validate_approval(approval, now=now)
    require(phase in {"dry-run", "archive-verify", "retire"}, "INVALID_PHASE")
    require(
        approval["schema_version"] != RENEWAL_SCHEMA or phase == "retire",
        "RETIREMENT_ONLY_RENEWAL",
    )
    targets = approval["targets"]
    if target_index is not None:
        require(
            phase in {"retire", "archive-verify"}
            and type(target_index) is int
            and 0 <= target_index < len(targets),
            "INVALID_TARGET_INDEX",
        )
        targets = [targets[target_index]]
    require(
        all(target["id"] != approval["archiver_image"] for target in targets),
        "ARCHIVER_IMAGE_EXCLUDED",
    )
    require(
        plan.get("schema_version") == "1.2"
        and plan.get("selection_policy")
        == "compose-ownership-labels-and-reserved-ports-v3",
        "INVALID_PLAN",
    )
    validate_live(approval, snapshot, now, phase, target_index)
    require(
        snapshot["source_daemon"] == approval["source_daemon"], "SOURCE_DAEMON_CHANGED"
    )
    require(
        snapshot["source_context"] == approval["source_context"],
        "SOURCE_CONTEXT_CHANGED",
    )
    records = [validate_target(target, snapshot, plan) for target in targets]
    if any(target["kind"] == "volume" for target in approval["targets"]):
        inventory_names = {item.get("Name") for item in inventory["volumes"]}
        require(
            all(
                target["id"] in inventory_names
                for target in approval["targets"]
                if target["kind"] == "volume"
            ),
            "VOLUME_INVENTORY_MISMATCH",
        )
    if phase != "dry-run" and any(
        target["kind"] == "image" for target in approval["targets"]
    ):
        observed = snapshot.get("verification_daemon")
        require(
            bool(observed)
            and observed == approval["verification_daemon"]
            and observed != snapshot["source_daemon"],
            "DISTINCT_VERIFICATION_DAEMON_REQUIRED",
        )
        require(
            snapshot.get("verification_context") == approval["verification_context"],
            "VERIFICATION_CONTEXT_CHANGED",
        )
    return records
