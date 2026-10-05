"""Executable policy/archive refusals; no application or Docker resources used."""

from __future__ import annotations

import copy
import hashlib
import gzip
import io
import json
import shutil
import subprocess
import sys
import tarfile
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from automation.resource_recovery import archive_verification as archive
from automation.resource_recovery import policy


@pytest.mark.parametrize("boundary", range(4))
def test_actual_wrapper_json_decode_preserves_timestamp_strings(tmp_path, boundary):
    """Execute each shipped decode pipeline, including restored-image and approval."""
    shell = shutil.which("pwsh")
    assert shell, "PowerShell 7.5+ is required for lossless JSON evidence"
    value = {
        "Config": {
            "Labels": {
                "created": "2026-10-03T03:02:26.458113+00:00",
                "foreign": "2026-10-03T03:02:26.4581130+05:30",
            }
        },
        "approved_at": "2026-10-05T09:28:58.1913539Z",
    }
    source = tmp_path / "wire.json"
    source.write_text(json.dumps(value), encoding="utf-8")
    script = r"""
param($Wrapper,$Wire,$Index)
$ErrorActionPreference='Stop'
$tokens=$null;$errors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile($Wrapper,[ref]$tokens,[ref]$errors)
if($errors.Count){throw 'PARSE_ERROR'}
$reads=@($ast.FindAll({param($node)
 $node -is [Management.Automation.Language.CommandAst] -and $node.GetCommandName() -eq 'ConvertFrom-Json' -and
 $node.Parent.Extent.Text -match 'Invoke-RecoveryDocker|\$Disposition'
},$true))
if($reads.Count -ne 4){throw 'EXACT_DECODE_BOUNDARIES_REQUIRED'}
$Disposition=$Wire
function Invoke-RecoveryDocker { Get-Content -LiteralPath $Wire -Raw }
$context='recording';$id='recording';$target=@{kind='image';id='recording'}
$verifyContext='recording';$Item=@{target=@{id='recording'}}
$matched=@('recording')
$pipeline=$reads[[int]$Index].Parent.Extent.Text
$decoded=Invoke-Expression $pipeline
if($decoded.approved_at -isnot [string] -or $decoded.Config.Labels.created -isnot [string]){throw 'STRING_TYPE_LOST'}
$decoded | ConvertTo-Json -Depth 10 -Compress
"""
    harness = tmp_path / "decode.ps1"
    harness.write_text(script, encoding="utf-8")
    result = subprocess.run(
        [
            shell,
            "-NoProfile",
            "-File",
            str(harness),
            str(ROOT / "automation/Invoke-ResourceOnlyRecovery.ps1"),
            str(source),
            str(boundary),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout) == value


@pytest.mark.parametrize("date_kind", ["Default", "Utc"])
def test_default_powershell_date_decode_fails_independent_exact_string_expectation(
    tmp_path,
    date_kind,
):
    shell = shutil.which("pwsh")
    assert shell
    wire = '{"label":"2026-10-03T03:02:26.4581130+05:30"}'
    result = subprocess.run(
        [
            shell,
            "-NoProfile",
            "-Command",
            "$value='" + wire + "' | ConvertFrom-Json -DateKind " + date_kind + "; "
            "if($value.label -isnot [datetime]){throw 'MUTATION_NOT_REPRODUCED'}; "
            "$value | ConvertTo-Json -Compress",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["label"] != json.loads(wire)["label"]


ROOT = Path(__file__).parents[2]
NOW = datetime(2026, 10, 5, 12, tzinfo=timezone.utc)
IMAGE_ID = "sha256:" + "a" * 64


def packet(tmp_path):
    image = {
        "Id": IMAGE_ID,
        "RepoTags": ["fixture:reviewed"],
        "RepoDigests": [],
        "Architecture": "amd64",
        "Os": "linux",
        "Created": "2026-10-01",
        "Config": {"Labels": {"com.docker.compose.project": "retired-fixture"}},
        "RootFS": {"Type": "layers", "Layers": []},
    }
    volume = {
        "Name": "reviewed-fixture-volume",
        "CreatedAt": "2026-10-01",
        "Driver": "local",
        "Labels": {"com.docker.compose.project": "retired-fixture"},
        "Options": {},
        "Mountpoint": "/fixture-only",
        "Scope": "local",
    }
    targets = [
        {
            "kind": kind,
            "id": record["Id" if kind == "image" else "Name"],
            "inspect_sha256": policy.fingerprint(kind, record),
        }
        for kind, record in [("image", image), ("volume", volume)]
    ]
    approval = dict(
        schema_version=policy.SCHEMA,
        operator="reviewer",
        approved_at=NOW.isoformat(),
        expires_at=(NOW + timedelta(hours=1)).isoformat(),
        retain_until=(NOW + timedelta(days=30)).isoformat(),
        retention_authority="reviewer",
        source_context="source",
        source_daemon="source-daemon",
        verification_context="isolated",
        verification_daemon="independent-daemon",
        plan_sha256="1" * 64,
        inventory_sha256="2" * 64,
        helper_root=str(ROOT),
        helper_files={
            name: policy.file_digest(ROOT / name) for name in policy.HELPER_FILES
        },
        primary_head="3" * 40,
        targets=targets,
        archive_root=str(tmp_path),
        archiver_image="sha256:" + "b" * 64,
        max_archive_bytes=1024 * 1024,
    )
    plan = dict(
        schema_version="1.2",
        selection_policy="compose-ownership-labels-and-reserved-ports-v3",
        generated_at=NOW.isoformat(),
        registered_worktrees=[],
        allowed_compose_projects={},
        ownership_conflicts=[
            dict(
                id=t["id"],
                resource_type=t["kind"],
                ownership_state="unproven_resource_only_owner",
                compose_project="retired-fixture",
            )
            for t in targets
        ],
    )
    inventory = {
        "captured_at": NOW.isoformat(),
        "volumes": [volume],
        "images": [image],
        "containers": [],
    }
    snapshot = dict(
        schema_version=policy.LIVE_SCHEMA,
        collection_started_at=NOW.isoformat(),
        collection_finished_at=NOW.isoformat(),
        source_context="source",
        source_daemon="source-daemon",
        verification_context="isolated",
        verification_daemon="independent-daemon",
        containers=[],
        images=[image],
        volumes=[volume],
        run_id="a" * 32,
        operation_token=str(uuid.uuid4()),
        phase="archive-verify",
        target_indexes=[0, 1],
        approval_sha256="1" * 64,
        discovery_receipt_sha256="1" * 64,
        holder="fixture-holder",
        scope_digest="sha256:" + "c" * 64,
        source_heads={"lotus-platform": "3" * 40},
        helper_files=approval["helper_files"],
        container_ids_before=[],
        container_ids_after=[],
        protected_checkout_paths=[],
    )
    approval["runtime_authority"] = dict(
        holder="fixture-holder",
        scope_digest=snapshot["scope_digest"],
        source_heads=snapshot["source_heads"],
        observation_schema=policy.LIVE_SCHEMA,
    )
    finalize_discovery(approval, plan, inventory, snapshot, NOW)
    return approval, plan, inventory, snapshot


def finalize_discovery(approval, plan, inventory, snapshot, now):
    """Explicit synthetic recorded-boundary fixture, not real Docker evidence or permission."""
    base = Path(approval["archive_root"]) / ("discovery-" + uuid.uuid4().hex)
    base.mkdir()
    start = now - timedelta(seconds=5)
    capture = dict(
        source_daemon=approval["source_daemon"],
        observed_at=start.isoformat(),
        containers=snapshot["containers"],
        images=snapshot["images"],
        volumes=snapshot["volumes"],
        networks=[],
    )
    inventory.update(
        captured_at=start.isoformat(),
        containers=capture["containers"],
        images=capture["images"],
        volumes=capture["volumes"],
    )
    manifest = []
    commands = []
    for kind in ("container", "image", "volume", "network"):
        key = "Name" if kind == "volume" else "Id"
        records = capture[f"{kind}s"]
        flags = (
            ["--all", "--quiet", "--no-trunc"]
            if kind in {"container", "image"}
            else (["--quiet", "--no-trunc"] if kind == "network" else ["--quiet"])
        )
        ids = sorted(record[key] for record in records)
        commands.append(([kind, "ls", *flags], "\n".join(ids)))
        if ids:
            commands.append(([kind, "inspect", *ids], json.dumps(records)))
    ticks = 0
    for command, output in commands:
        for argv, stdout in [
            (["info", "--format", "{{.ID}}"], approval["source_daemon"]),
            (command, output),
        ]:
            request = base / f"request-{ticks}.json"
            response = base / f"response-{ticks}.json"
            request.write_text(
                json.dumps(
                    dict(
                        argv=["docker", "--context", approval["source_context"], *argv],
                        timeout_seconds=60,
                        terminate_owned_cli=True,
                    )
                ),
                encoding="utf-8",
            )
            stamp = (start + timedelta(milliseconds=ticks + 1)).isoformat()
            response.write_text(
                json.dumps(
                    dict(
                        request_sha256=policy.file_digest(request),
                        accepted=True,
                        producer_stopped=True,
                        native_exit=0,
                        status="exited",
                        stdout_truncated=False,
                        stderr_truncated=False,
                        journal_failed=False,
                        started_at=stamp,
                        stopped_at=stamp,
                        stdout=stdout,
                        stdout_sha256=hashlib.sha256(stdout.encode()).hexdigest(),
                    )
                ),
                encoding="utf-8",
            )
            manifest.append(
                dict(
                    request=str(request),
                    request_sha256=policy.file_digest(request),
                    response=str(response),
                    response_sha256=policy.file_digest(response),
                )
            )
            ticks += 1
    capture_path = base / "capture.json"
    capture_path.write_text(json.dumps(capture), encoding="utf-8")
    for name, value in (("plan", plan), ("inventory", inventory)):
        path = base / f"{name}.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        approval[f"{name}_sha256"] = policy.file_digest(path)
    receipt = dict(
        status="review-input-only-no-approval-generated",
        source_daemon=approval["source_daemon"],
        source_baseline_sha256=policy.file_digest(capture_path),
        inventory_sha256=approval["inventory_sha256"],
        plan_sha256=approval["plan_sha256"],
        native_calls=[
            {k: v for k, v in entry.items() if k != "response_sha256"}
            for entry in manifest
        ],
    )
    receipt_path = base / "receipt.json"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    approval["discovery"] = dict(
        schema_version="lotus.resource-recovery.discovery.v1",
        capture_sha256=policy.file_digest(capture_path),
        capture_receipt_sha256=policy.file_digest(receipt_path),
        capture_started_at=start.isoformat(),
        capture_finished_at=stamp,
        capture_path=str(capture_path),
        capture_receipt_path=str(receipt_path),
        native_manifest=manifest,
        operator_attestation=dict(
            reviewer=approval["operator"],
            capture_receipt_sha256=policy.file_digest(receipt_path),
            scope_digest=approval["runtime_authority"]["scope_digest"],
            source_heads=approval["runtime_authority"]["source_heads"],
            admission_record="explicit-synthetic-test-review",
        ),
    )
    snapshot["discovery_receipt_sha256"] = policy.file_digest(receipt_path)


def test_admission_preserves_exact_records_and_source_closure(tmp_path):
    approval, plan, inventory, snapshot = packet(tmp_path)
    policy.validate_sources(approval, ROOT)
    assert policy.admit(
        approval, plan, inventory, snapshot, now=NOW, phase="archive-verify"
    ) == [snapshot["images"][0], snapshot["volumes"][0]]


@pytest.mark.parametrize(
    "change,reason",
    [
        ("expiry", "DISPOSITION_EXPIRED"),
        ("stale", "STALE_OBSERVATION"),
        ("daemon", "SOURCE_DAEMON_CHANGED"),
        ("context", "SOURCE_CONTEXT_CHANGED"),
        ("same-daemon", "DISTINCT_VERIFICATION_DAEMON_REQUIRED"),
        ("missing-daemon", "DISTINCT_VERIFICATION_DAEMON_REQUIRED"),
        ("fingerprint", "RESOURCE_IDENTITY_CHANGED"),
        ("image-consumer", "RESOURCE_HAS_CONSUMER"),
        ("stopped-volume-consumer", "RESOURCE_HAS_CONSUMER"),
        ("not-resource-only", "RESOURCE_ONLY_CONFLICT_REQUIRED"),
        ("anonymous", "UNLABELLED_RESOURCE_EXCLUDED"),
        ("registered", "ACTIVE_OWNER_EXCLUDED"),
        ("existing", "ACTIVE_OWNER_EXCLUDED"),
        ("buildkit", "BUILDKIT_EXCLUDED"),
        ("inventory", "VOLUME_INVENTORY_MISMATCH"),
        ("archiver", "ARCHIVER_IMAGE_EXCLUDED"),
        ("duplicate", "DUPLICATE_TARGET"),
    ],
)
def test_representative_bad_admissions_refuse(tmp_path, change, reason):
    approval, plan, inventory, snapshot = packet(tmp_path)
    labels = snapshot["images"][0]["Config"]["Labels"]
    if change == "expiry":
        approval["expires_at"] = NOW.isoformat()
    elif change == "stale":
        snapshot["collection_started_at"] = (NOW - timedelta(seconds=301)).isoformat()
    elif change == "daemon":
        snapshot["source_daemon"] = "foreign"
    elif change == "context":
        snapshot["source_context"] = "foreign"
    elif change == "same-daemon":
        snapshot["verification_daemon"] = snapshot["source_daemon"]
    elif change == "missing-daemon":
        snapshot["verification_daemon"] = None
    elif change == "fingerprint":
        snapshot["images"][0]["RepoTags"].append("foreign:tag")
    elif change == "image-consumer":
        snapshot["containers"] = [
            {
                "Id": "c" * 64,
                "Image": IMAGE_ID,
                "State": {"Running": False},
                "Mounts": [],
            }
        ]
        snapshot["container_ids_before"] = snapshot["container_ids_after"] = ["c" * 64]
    elif change == "stopped-volume-consumer":
        snapshot["containers"] = [
            {
                "Id": "c" * 64,
                "Image": "sha256:" + "f" * 64,
                "State": {"Running": False},
                "Mounts": [{"Type": "volume", "Name": approval["targets"][1]["id"]}],
            }
        ]
        snapshot["container_ids_before"] = snapshot["container_ids_after"] = ["c" * 64]
    elif change == "not-resource-only":
        plan["ownership_conflicts"][0]["ownership_state"] = "missing_labelled_checkout"
    elif change == "anonymous":
        labels.clear()
    elif change in {"registered", "existing"}:
        checkout = str(tmp_path / "owner")
        labels["com.lotus.repository.checkout"] = checkout
        if change == "registered":
            plan["registered_worktrees"] = [checkout]
        else:
            Path(checkout).mkdir()
    elif change == "buildkit":
        labels["com.docker.compose.project"] = "buildkit-worker"
        plan["ownership_conflicts"][0]["compose_project"] = "buildkit-worker"
    elif change == "inventory":
        inventory["volumes"] = []
    elif change == "archiver":
        approval["archiver_image"] = IMAGE_ID
    elif change == "duplicate":
        approval["targets"].append(copy.deepcopy(approval["targets"][0]))
    if change in {"anonymous", "registered", "existing", "buildkit"}:
        approval["targets"][0]["inspect_sha256"] = policy.fingerprint(
            "image", snapshot["images"][0]
        )
    with pytest.raises(policy.Refused, match=reason):
        policy.admit(
            approval, plan, inventory, snapshot, now=NOW, phase="archive-verify"
        )


def test_retirement_rechecks_second_exact_target_after_first_is_absent(tmp_path):
    approval, plan, inventory, snapshot = packet(tmp_path)
    snapshot["images"] = []
    snapshot.update(phase="retire", target_indexes=[1])
    assert (
        policy.admit(
            approval, plan, inventory, snapshot, now=NOW, phase="retire", target_index=1
        )
        == snapshot["volumes"]
    )
    for index in [-1, 2, True]:
        with pytest.raises(policy.Refused, match="INVALID_TARGET_INDEX"):
            policy.admit(
                approval,
                plan,
                inventory,
                snapshot,
                now=NOW,
                phase="retire",
                target_index=index,
            )
    snapshot["target_indexes"] = [0]
    with pytest.raises(policy.Refused, match="LIVE_TARGET_COVERAGE_LOST"):
        policy.admit(
            approval, plan, inventory, snapshot, now=NOW, phase="retire", target_index=0
        )


def test_helper_changes_and_duplicate_json_refuse(tmp_path):
    approval, *_ = packet(tmp_path)
    approval["helper_files"]["automation/resource_recovery/cli.py"] = "f" * 64
    with pytest.raises(policy.Refused, match="HELPER_SOURCE_CHANGED"):
        policy.validate_sources(approval, ROOT)
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text('{"operator":"first","operator":"second"}', encoding="utf-8")
    with pytest.raises(policy.Refused, match="DUPLICATE_JSON_FIELD"):
        policy.read_json(duplicate)


@pytest.mark.parametrize(
    "mutation,reason",
    [
        ("duplicate-container", "DISCOVERY_LIST_IDENTITIES_INVALID"),
        ("short-container", "DISCOVERY_LIST_IDENTITIES_INVALID"),
        ("blank-container", "DISCOVERY_LIST_IDENTITIES_INVALID"),
        ("unproven-image-alias", "UNPROVEN_IMAGE_LIST_ALIAS"),
        ("proven-image-alias", "RESOURCE_RECOVERY_CHECK_PASSED"),
        ("wrong-source", "DISCOVERY_DAEMON_NOT_PROVEN"),
        ("unstopped", "DISCOVERY_NATIVE_NOT_SUCCESSFUL"),
        ("missing-pair", "NATIVE_MANIFEST_REQUIRED"),
        ("self-attested", "INDEPENDENT_DISCOVERY_REVIEW_REQUIRED"),
        ("intermediate", "UNSUPPORTED_INTERMEDIATE_SCHEMA"),
        (None, "RESOURCE_RECOVERY_CHECK_PASSED"),
    ],
)
def test_real_cli_discovery_closure_refuses_hash_consistent_bad_evidence(
    tmp_path, mutation, reason
):
    approval, plan, inventory, live = packet(tmp_path)
    now = datetime.now(timezone.utc)
    approval.update(
        approved_at=now.isoformat(), expires_at=(now + timedelta(hours=1)).isoformat()
    )
    plan["generated_at"] = now.isoformat()
    if mutation == "proven-image-alias":
        live["images"][0]["RepoTags"].append("fixture:second-reviewed-tag")
        approval["targets"][0]["inspect_sha256"] = policy.fingerprint(
            "image", live["images"][0]
        )
    finalize_discovery(approval, plan, inventory, live, now)
    discovery = approval["discovery"]
    if mutation in {
        "duplicate-container",
        "short-container",
        "blank-container",
        "wrong-source",
        "unstopped",
        "unproven-image-alias",
        "proven-image-alias",
    }:
        index = (
            3
            if mutation in {"unproven-image-alias", "proven-image-alias"}
            else (0 if mutation in {"wrong-source", "unstopped"} else 1)
        )
        entry = discovery["native_manifest"][index]
        path = Path(entry["response"])
        response = json.loads(path.read_text())
        if mutation == "unstopped":
            response["producer_stopped"] = False
        else:
            response["stdout"] = {
                "duplicate-container": ("c" * 64 + "\n") * 2,
                "short-container": "c" * 12,
                "blank-container": "\n",
                "wrong-source": "foreign-daemon",
                "unproven-image-alias": (IMAGE_ID + "\n") * 2,
                "proven-image-alias": (IMAGE_ID + "\n") * 2,
            }[mutation]
            response["stdout_sha256"] = hashlib.sha256(
                response["stdout"].encode()
            ).hexdigest()
        path.write_text(json.dumps(response), encoding="utf-8")
        entry["response_sha256"] = policy.file_digest(path)
    elif mutation == "missing-pair":
        discovery["native_manifest"].pop()
    elif mutation == "self-attested":
        discovery["operator_attestation"]["reviewer"] = approval["runtime_authority"][
            "holder"
        ]
    elif mutation == "intermediate":
        approval["schema_version"] = "lotus.resource-recovery.disposition.v1"
    for name, value in (
        ("approval", approval),
        ("plan", plan),
        ("inventory", inventory),
    ):
        (tmp_path / f"{name}.json").write_text(json.dumps(value), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            str(ROOT / "automation/resource_recovery/cli.py"),
            "validate-local",
            "--root",
            str(ROOT),
            "--approval",
            str(tmp_path / "approval.json"),
            "--expected-approval-sha256",
            policy.file_digest(tmp_path / "approval.json"),
            "--plan",
            str(tmp_path / "plan.json"),
            "--inventory",
            str(tmp_path / "inventory.json"),
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == (
        0 if mutation in {None, "proven-image-alias"} else 1
    ), result.stdout + result.stderr
    assert result.stdout.strip() == reason


@pytest.mark.parametrize(
    "mutation,reason",
    [
        ("future", "STALE_OBSERVATION"),
        ("stale", "STALE_OBSERVATION"),
        ("restamped-finish", "STALE_OBSERVATION"),
        ("omitted-stopped", "LIVE_CONSUMER_COVERAGE_LOST"),
        ("list-drift", "LIVE_CONSUMER_COVERAGE_LOST"),
        ("short-id", "LIVE_CONSUMER_COVERAGE_LOST"),
        ("duplicate-inspect", "LIVE_CONSUMER_COVERAGE_LOST"),
        ("phase", "LIVE_PHASE_OR_TARGET_CHANGED"),
        ("index", "LIVE_PHASE_OR_TARGET_CHANGED"),
        ("scope", "LIVE_AUTHORITY_CHANGED"),
        ("source", "LIVE_AUTHORITY_CHANGED"),
        ("helper", "LIVE_PROVENANCE_CHANGED"),
        ("token", "LIVE_PROVENANCE_CHANGED"),
        ("run", "LIVE_PROVENANCE_CHANGED"),
        ("extra-field", "LIVE_OBSERVATION_REQUIRED"),
        ("missing-image", "LIVE_CONSUMER_METADATA_INCOMPLETE"),
        ("missing-mounts", "LIVE_CONSUMER_METADATA_INCOMPLETE"),
        ("partial-volume-mount", "LIVE_CONSUMER_METADATA_INCOMPLETE"),
    ],
)
def test_live_start_scope_complete_consumers_and_linkage_guards(
    tmp_path, mutation, reason
):
    approval, plan, inventory, live = packet(tmp_path)
    if mutation in {"future", "stale", "restamped-finish"}:
        live["collection_started_at"] = (
            NOW + timedelta(seconds=1)
            if mutation == "future"
            else NOW - timedelta(seconds=301)
        ).isoformat()
    elif mutation == "omitted-stopped":
        live["container_ids_before"] = live["container_ids_after"] = ["c" * 64]
    elif mutation == "list-drift":
        live["container_ids_after"] = ["c" * 64]
    elif mutation in {"short-id", "duplicate-inspect"}:
        identifier = "c" * (12 if mutation == "short-id" else 64)
        live["container_ids_before"] = live["container_ids_after"] = [identifier]
        live["containers"] = [{"Id": identifier}] * (
            2 if mutation == "duplicate-inspect" else 1
        )
    elif mutation == "phase":
        live["phase"] = "retire"
    elif mutation == "index":
        live["target_indexes"] = [0]
    elif mutation == "scope":
        live["scope_digest"] = "sha256:" + "f" * 64
    elif mutation == "source":
        live["source_heads"] = {"lotus-platform": "f" * 40}
    elif mutation == "helper":
        live["helper_files"] = {}
    elif mutation == "token":
        live["operation_token"] = "caller-token"
    elif mutation == "run":
        live["run_id"] = "foreign"
    elif mutation in {"missing-image", "missing-mounts", "partial-volume-mount"}:
        live["container_ids_before"] = live["container_ids_after"] = ["c" * 64]
        record = dict(
            Id="c" * 64, Image="sha256:" + "f" * 64, State={"Running": False}, Mounts=[]
        )
        if mutation == "missing-image":
            record.pop("Image")
        elif mutation == "missing-mounts":
            record.pop("Mounts")
        else:
            record["Mounts"] = [{"Type": "volume"}]
        live["containers"] = [record]
    else:
        live["unexpected"] = True
    with pytest.raises(policy.Refused, match=reason):
        policy.admit(approval, plan, inventory, live, now=NOW, phase="archive-verify")


def add_member(
    output,
    name,
    data=b"",
    *,
    kind=tarfile.REGTYPE,
    link="",
    uid=1201,
    gid=1202,
    mode=0o640,
):
    item = tarfile.TarInfo(name)
    item.type, item.linkname, item.uid, item.gid, item.mode = kind, link, uid, gid, mode
    item.size = len(data) if kind == tarfile.REGTYPE else 0
    output.addfile(item, io.BytesIO(data) if kind == tarfile.REGTYPE else None)


def image_archive(tmp_path, *, corrupt=False):
    layer = b"independent layer bytes"
    layer_hash = "sha256:" + hashlib.sha256(layer).hexdigest()
    config = json.dumps({"rootfs": {"diff_ids": [layer_hash]}}).encode()
    original = {
        "Id": "sha256:" + hashlib.sha256(config).hexdigest(),
        "RepoTags": ["fixture:reviewed"],
        "RootFS": {"Layers": [layer_hash]},
        "Config": {},
        "Architecture": "amd64",
        "Os": "linux",
    }
    path = tmp_path / "image.tar"
    with tarfile.open(path, "w") as output:
        add_member(
            output,
            "manifest.json",
            json.dumps(
                [
                    {
                        "Config": "config.json",
                        "RepoTags": original["RepoTags"],
                        "Layers": ["layer.tar"],
                    }
                ]
            ).encode(),
        )
        add_member(output, "config.json", config)
        add_member(output, "layer.tar", b"wrong bytes" if corrupt else layer)
    return path, original


def test_image_archive_and_restored_metadata_require_actual_bytes(tmp_path):
    path, original = image_archive(tmp_path)
    assert archive.verify_image(path, original, 1024 * 1024) == policy.file_digest(path)
    archive.verify_restored_image(original, copy.deepcopy(original))
    changed = copy.deepcopy(original)
    changed["Config"] = {"Env": ["lost-content"]}
    with pytest.raises(policy.Refused, match="RESTORED_IMAGE_MISMATCH"):
        archive.verify_restored_image(original, changed)
    path, original = image_archive(tmp_path, corrupt=True)
    with pytest.raises(policy.Refused, match="IMAGE_LAYER_CORRUPT"):
        archive.verify_image(path, original, 1024 * 1024)


def oci_image_archive(tmp_path, mutation=None):
    """Independent graph/config/compressed-content and DiffID fixture."""
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as layer:
        add_member(layer, "marker.txt", b"independent owned marker\n" * 1000)
    layer_bytes = raw.getvalue()
    compressed = gzip.compress(layer_bytes, mtime=0)
    config = {
        "architecture": "amd64",
        "os": "linux",
        "created": "2026-10-01",
        "config": {"Labels": {"com.docker.compose.project": "retired-fixture"}},
        "rootfs": {
            "type": "layers",
            "diff_ids": ["sha256:" + hashlib.sha256(layer_bytes).hexdigest()],
        },
    }
    if mutation == "diffid":
        config["rootfs"]["diff_ids"] = ["sha256:" + "0" * 64]
    if mutation == "platform":
        config["architecture"] = "arm64"
    if mutation == "metadata":
        config["config"]["Labels"]["extra"] = "not admitted"
    if mutation == "encoding":
        compressed = b"not a gzip stream"
    config_bytes = json.dumps(config).encode()

    def descriptor(content, media):
        return {
            "mediaType": media,
            "digest": "sha256:" + hashlib.sha256(content).hexdigest(),
            "size": len(content),
        }

    cfg = descriptor(config_bytes, archive.OCI_CONFIG)
    lay = descriptor(compressed, archive.OCI_LAYER + "+gzip")
    if mutation == "size":
        lay["size"] += 1
    if mutation == "unsupported":
        lay["mediaType"] += "+zstd"
    graph = {
        "schemaVersion": 2,
        "mediaType": archive.OCI_MANIFEST,
        "config": cfg,
        "layers": [lay],
    }
    graph_bytes = json.dumps(graph).encode()
    root = descriptor(graph_bytes, archive.OCI_MANIFEST)
    original = {
        "Id": root["digest"],
        "Descriptor": copy.deepcopy(root),
        "RepoTags": ["fixture:reviewed"],
        "Architecture": "amd64",
        "Os": "linux",
        "Created": "2026-10-01",
        "Config": {"Labels": {"com.docker.compose.project": "retired-fixture"}},
        "RootFS": {
            "Type": "layers",
            "Layers": ["sha256:" + hashlib.sha256(layer_bytes).hexdigest()],
        },
    }
    if mutation == "source-descriptor":
        original["Descriptor"]["size"] += 1
    if mutation == "layer-diffid":
        original["RootFS"]["Layers"] = config["rootfs"]["diff_ids"] = [
            "sha256:" + "e" * 64
        ]
        # Rebuild the config and manifest graph, keeping every descriptor internally sound.
        config_bytes = json.dumps(config).encode()
        cfg = descriptor(config_bytes, archive.OCI_CONFIG)
        graph["config"] = cfg
        graph_bytes = json.dumps(graph).encode()
        root = descriptor(graph_bytes, archive.OCI_MANIFEST)
        original["Id"] = root["digest"]
        original["Descriptor"] = copy.deepcopy(root)
    blobs = {
        "blobs/sha256/" + root["digest"][7:]: graph_bytes,
        "blobs/sha256/" + cfg["digest"][7:]: config_bytes,
        "blobs/sha256/" + lay["digest"][7:]: compressed,
    }
    if mutation in {"manifest", "config", "layer"}:
        selected = {"manifest": root, "config": cfg, "layer": lay}[mutation]
        blobs["blobs/sha256/" + selected["digest"][7:]] = (
            b"!" + blobs["blobs/sha256/" + selected["digest"][7:]][1:]
        )
    if mutation == "missing":
        del blobs["blobs/sha256/" + lay["digest"][7:]]
    manifest = [
        {
            "Config": "blobs/sha256/" + cfg["digest"][7:],
            "RepoTags": ["wrong:tag"] if mutation == "tag" else original["RepoTags"],
            "Layers": ["blobs/sha256/" + lay["digest"][7:]],
        }
    ]
    blobs.update(
        {
            "manifest.json": json.dumps(manifest).encode(),
            "index.json": json.dumps(
                {"schemaVersion": 2, "manifests": [root]}
            ).encode(),
            "oci-layout": b'{"imageLayoutVersion":"1.0.0"}',
        }
    )
    path = tmp_path / "image.tar"
    with tarfile.open(path, "w") as output:
        for name, content in blobs.items():
            add_member(output, name, content)
        if mutation == "duplicate":
            add_member(output, "index.json", blobs["index.json"])
        if mutation == "escape":
            add_member(output, "../escape", b"never extract")
    return path, original


@pytest.mark.parametrize(
    "mutation,reason",
    [
        ("manifest", "IMAGE_DESCRIPTOR_DIGEST_MISMATCH"),
        ("config", "IMAGE_DESCRIPTOR_DIGEST_MISMATCH"),
        ("layer", "IMAGE_DESCRIPTOR_DIGEST_MISMATCH"),
        ("size", "IMAGE_DESCRIPTOR_SIZE_MISMATCH"),
        ("diffid", "IMAGE_ROOTFS_MISMATCH"),
        ("platform", "IMAGE_PLATFORM_MISMATCH"),
        ("metadata", "IMAGE_METADATA_MISMATCH"),
        ("tag", "IMAGE_TAGS_MISMATCH"),
        ("missing", "IMAGE_MEMBER_ABSENT"),
        ("duplicate", "DUPLICATE_ARCHIVE_MEMBER"),
        ("escape", "ARCHIVE_PATH_ESCAPE"),
        ("unsupported", "IMAGE_DESCRIPTOR_UNSUPPORTED"),
        ("source-descriptor", "IMAGE_SOURCE_DESCRIPTOR_MISMATCH"),
        ("encoding", "IMAGE_LAYER_ENCODING_INVALID"),
        ("layer-diffid", "IMAGE_LAYER_CORRUPT"),
    ],
)
def test_oci_archive_content_refusals(tmp_path, mutation, reason):
    path, original = oci_image_archive(tmp_path, mutation)
    with pytest.raises(policy.Refused, match=reason):
        archive.image_identity(path, original, 1024 * 1024)


def test_oci_identity_and_bounded_decompression(tmp_path):
    path, original = oci_image_archive(tmp_path)
    identity = archive.image_identity(path, original, 1024 * 1024)
    assert identity["graph_id"] == original["Id"]
    assert identity["config_id"] != original["Id"]
    restored = copy.deepcopy(original)
    restored["Id"] = identity["config_id"]
    restored.pop("Descriptor")
    archive.verify_restored_image(original, restored, identity)
    restored["Id"] = "sha256:" + "f" * 64
    with pytest.raises(policy.Refused, match="RESTORED_IMAGE_MISMATCH"):
        archive.verify_restored_image(original, restored, identity)
    with pytest.raises(policy.Refused, match="IMAGE_DECOMPRESSION_BUDGET"):
        archive.image_identity(path, original, path.stat().st_size)


@pytest.mark.parametrize(
    "change", ["content", "mode", "missing", "escape", "duplicate", "hardlink"]
)
def test_volume_archive_guard_accepts_exact_content_and_refuses_mutations(
    tmp_path, change
):
    content = b"fixture bytes\x00\xff"
    expected = {
        "uid": 1201,
        "gid": 1202,
        "mode": 0o640,
        "kind": "file",
        "size": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
        "hardlink_to": "data",
    }
    manifest = {
        "schema_version": "lotus.resource-recovery.files.v1",
        "files": {"data": expected},
    }
    path = tmp_path / "volume.tar"
    with tarfile.open(path, "w") as output:
        add_member(output, "data", content)
    assert archive.verify_volume(path, manifest, 1024 * 1024) == policy.file_digest(
        path
    )
    archive.verify_restored_volume(manifest, copy.deepcopy(manifest))
    changed = copy.deepcopy(manifest)
    changed["files"]["data"]["uid"] = 0
    with pytest.raises(policy.Refused, match="RESTORED_VOLUME_MISMATCH"):
        archive.verify_restored_volume(manifest, changed)
    with tarfile.open(path, "w") as output:
        if change != "missing":
            add_member(
                output,
                "../escape" if change == "escape" else "data",
                b"wrong" if change == "content" else content,
                mode=0o600 if change == "mode" else 0o640,
                kind=tarfile.LNKTYPE if change == "hardlink" else tarfile.REGTYPE,
                link="foreign" if change == "hardlink" else "",
            )
        if change == "duplicate":
            add_member(output, "data", content)
    with pytest.raises(policy.Refused):
        archive.verify_volume(path, manifest, 1024 * 1024)


def test_shipped_cli_does_not_echo_private_parse_errors(tmp_path):
    path = tmp_path / "approval.json"
    path.write_text("PRIVATE-ARCHIVE-CONTENT invalid JSON", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            str(ROOT / "automation/resource_recovery/cli.py"),
            "validate-local",
            "--approval",
            str(path),
            "--root",
            str(ROOT),
            "--expected-approval-sha256",
            policy.file_digest(path),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert result.stdout.strip() == "RESOURCE_RECOVERY_CHECK_FAILED"
    assert "PRIVATE-ARCHIVE-CONTENT" not in result.stdout + result.stderr


def test_shipped_wrapper_missing_holder_refuses_before_any_boundary(tmp_path):
    shell = shutil.which("pwsh") or shutil.which("powershell")
    assert shell
    result = subprocess.run(
        [
            shell,
            "-NoProfile",
            "-File",
            str(ROOT / "automation/Invoke-ResourceOnlyRecovery.ps1"),
            "-Stage",
            "DryRun",
            "-ProjectsRoot",
            str(tmp_path),
            "-WorkbenchRepoPath",
            str(tmp_path),
            "-RuntimeHolder",
            " ",
            "-Disposition",
            str(tmp_path / "absent.json"),
            "-ExpectedDispositionSha256",
            "0" * 64,
            "-Plan",
            "absent",
            "-Inventory",
            "absent",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "receipt=" in result.stdout
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize(
    "mode,expected",
    [
        ("success", 0),
        ("docker-failure", 23),
        ("preflight-failure", 23),
        ("daemon-switch", 1),
        ("archive-success", 0),
        ("retire-success", 0),
        ("retire-renewed", 0),
        ("second-retirement-failure", 23),
        ("real-policy", 0),
        ("real-policy-sha-drift", 1),
        ("real-policy-list-drift", 1),
        ("real-policy-stopped-consumer", 1),
        ("real-policy-tag-drift", 1),
        ("real-policy-oci", 0),
        ("real-policy-oci-layer", 1),
        ("real-policy-oci-restored", 1),
        ("real-policy-oci-existing", 1),
        ("finish-failure", 1),
        ("unsafe-policy-output", 23),
        ("unsafe-single-policy-output", 23),
    ],
)
def test_full_shipped_wrapper_holds_original_fence_and_preserves_native_failure(
    tmp_path, mode, expected
):
    """Real adapter/OS lock and wrapper; recording CLI/Docker, not live admission."""
    shell = shutil.which("pwsh") or shutil.which("powershell")
    assert shell
    workspace = tmp_path / "workspace"
    primary = workspace / "lotus-platform/automation"
    primary.mkdir(parents=True)
    shutil.copy2(ROOT / "automation/CanonicalRuntimeReservation.psm1", primary)
    storage = tmp_path / "archives"
    # The real policy boundary requires private POSIX storage. Do not rely on
    # the runner's default umask to make a valid fixture admissible.
    storage.mkdir(mode=0o700)
    approval, plan, inventory, snapshot = packet(storage)
    oci_mode = mode.startswith("real-policy-oci")
    config_id = IMAGE_ID
    if oci_mode:
        source_archive, original = oci_image_archive(
            tmp_path, "layer" if mode.endswith("-layer") else None
        )
        if not mode.endswith("-layer"):
            config_id = archive.image_identity(source_archive, original, 1024 * 1024)[
                "config_id"
            ]
        approval["targets"] = [
            {
                "kind": "image",
                "id": original["Id"],
                "inspect_sha256": policy.fingerprint("image", original),
            }
        ]
        snapshot.update(images=[original], volumes=[], target_indexes=[0])
        plan["ownership_conflicts"] = [
            {
                "id": original["Id"],
                "resource_type": "image",
                "ownership_state": "unproven_resource_only_owner",
                "compose_project": "retired-fixture",
            }
        ]
    source_id = approval["targets"][0]["id"]
    current = datetime.now(timezone.utc)
    approval.update(
        approved_at=(current - timedelta(seconds=1)).isoformat(),
        expires_at=(current + timedelta(hours=1)).isoformat(),
    )
    plan["generated_at"] = (current - timedelta(seconds=1)).isoformat()
    finalize_discovery(approval, plan, inventory, snapshot, current)
    original_path = tmp_path / "archive-disposition.json"
    original_path.write_text(json.dumps(approval), encoding="utf-8")
    archive_identity = policy.file_digest(original_path)
    if mode == "retire-renewed":
        approval.update(
            schema_version=policy.RENEWAL_SCHEMA,
            archive_approval_sha256=archive_identity,
            archive_receipt_sha256="4" * 64,
        )
    approval_path = tmp_path / "approval.json"
    approval_path.write_text(json.dumps(approval), encoding="utf-8")
    image_path = tmp_path / "image.json"
    image_path.write_text(json.dumps([snapshot["images"][0]]), encoding="utf-8")
    restored_path = tmp_path / "restored-image.json"
    restored = copy.deepcopy(snapshot["images"][0])
    if oci_mode:
        restored["Id"] = config_id
        restored.pop("Descriptor")
    if mode == "real-policy-oci-restored":
        restored["Config"]["Labels"]["extra"] = "not admitted"
    restored_path.write_text(json.dumps([restored]), encoding="utf-8")
    volume_path = tmp_path / "volume.json"
    volume_path.write_text(json.dumps(snapshot["volumes"]), encoding="utf-8")
    lock = workspace / "lotus-platform/output/canonical-runtime/operation.lock"
    stage = (
        "ArchiveVerify"
        if mode in {"archive-success", "real-policy-tag-drift"} or oci_mode
        else "Retire"
        if mode in {"retire-success", "retire-renewed", "second-retirement-failure"}
        else "DryRun"
    )
    receipt_argument = ""
    if stage == "Retire":
        archive_identity = approval.get(
            "archive_approval_sha256", policy.file_digest(approval_path)
        )
        archive_directory = storage / archive_identity / "archives"
        archive_directory.mkdir(parents=True)
        (archive_directory / "prepared.json").write_text(
            "immutable-original-proof", encoding="utf-8"
        )
        receipt_argument = f"-VerificationReceipt '{tmp_path / 'reviewed-receipt.json'}' -ExpectedVerificationReceiptSha256 {'4' * 64}"
        if mode == "retire-renewed":
            receipt_argument += f" -ArchiveDisposition '{original_path}'"
    script = f"""
$ErrorActionPreference='Stop'
$global:preflightCount=0
$global:dockerCount=0
$global:removed=@()
$global:archiveChecked=$false
$global:targetChecked=$false
$global:containerLists=0
function global:Get-Acl {{
  $value=[pscustomobject]@{{}}
  $value | Add-Member ScriptMethod GetAccessRules {{ return @() }}
  return $value
}}
function global:git {{
  $global:LASTEXITCODE=0
  if ($args -contains 'rev-parse') {{ return '{approval["primary_head"]}' }}
}}
function global:python {{
  $global:LASTEXITCODE=0
  if ($args[0] -eq '{primary / "canonical_runtime_reservation.py"}') {{
    if ($args[1] -eq 'begin-change') {{ return '{{"operation":{{"token":"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"}},"bindings":[]}}' }}
    if ($args[1] -eq 'status') {{ return '{{"current":{{"holder":"fixture-holder","operation":{{"token":"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"}}}},"scopeDigest":"sha256:{"c" * 64}","scope":{{"sources":{{"lotus-platform":"{"3" * 40}"}}}}}}' }}
    if ($args[1] -eq 'preflight-operation') {{
      $global:preflightCount++
      if ('{mode}' -eq 'preflight-failure') {{ $global:LASTEXITCODE=23; return 'PRIVATE FAILURE' }}
      return '{{}}'
    }}
    if ($args[1] -eq 'finish') {{
      $outcome=$args[[Array]::IndexOf($args,'--outcome')+1]
      if ('{mode}' -eq 'finish-failure') {{ $global:LASTEXITCODE=23; return 'PRIVATE FAILURE' }}
      if ('{mode}' -notin @('success','archive-success','retire-success','retire-renewed','real-policy','real-policy-oci') -and $outcome -ne 'failure') {{ throw 'FALSE_FINISH_SUCCESS' }}
      return '{{}}'
    }}
    throw 'UNEXPECTED_PRIMARY_ACTION'
  }}
  if ($args[0] -ne '-I' -or $args[1] -ne '{ROOT / "automation/resource_recovery/cli.py"}') {{ throw 'WRONG_POLICY_SOURCE' }}
  if ($args[2] -eq 'protected-roots') {{ return '[]' }}
  if ('{mode}' -in @('unsafe-policy-output','unsafe-single-policy-output') -and $args[2] -eq 'prepare') {{
    $global:LASTEXITCODE=23
    if ('{mode}' -eq 'unsafe-single-policy-output') {{ return 'PRIVATE_FAILURE_TOKEN' }}
    return @('PRIVATE FAILURE secret-token','IMAGE_CONFIG_MISMATCH')
  }}
  if ('{mode}' -like 'real-policy*') {{
    $forward=@($args)
    if ('{mode}' -eq 'real-policy-sha-drift' -and $args[2] -eq 'prepare') {{
      $forward[[Array]::IndexOf($forward,'--expected-snapshot-sha256')+1]='{"f" * 64}'
    }}
    & '{sys.executable}' @forward
    if ($args[2] -eq 'verify-archive' -and $global:LASTEXITCODE -eq 0) {{ $global:archiveChecked=$true }}
    return
  }}
  if ('{mode}' -eq 'retire-renewed' -and ($args -notcontains '--archive-approval' -or $args -notcontains '{original_path}')) {{ throw 'RENEWAL_PROVENANCE_DROPPED' }}
  if ($args[2] -eq 'verify-retirement') {{
    $global:targetChecked=$false
    $directory=$args[[Array]::IndexOf($args,'--directory')+1]
    if ($directory -ne '{storage / archive_identity / "archives"}') {{ throw 'WRONG_ARCHIVE_IDENTITY' }}
  }}
  if ($args[2] -eq 'check-target') {{ $global:targetChecked=$true }}
  if ($args[2] -eq 'prepare') {{
    $directory=$args[[Array]::IndexOf($args,'--directory')+1]
    $approval=Get-Content -Raw '{approval_path}' | ConvertFrom-Json
    $targets=@()
    foreach ($target in $approval.targets) {{
      $original=if ($target.kind -eq 'image') {{ @(Get-Content -Raw '{image_path}' | ConvertFrom-Json)[0] }} else {{ @(Get-Content -Raw '{volume_path}' | ConvertFrom-Json)[0] }}
      $targets+=@{{target=$target; original=$original}}
    }}
    [IO.File]::WriteAllText((Join-Path $directory 'prepared.json'),(@{{targets=$targets}} | ConvertTo-Json -Depth 100))
  }}
  if ($args[2] -eq 'verify-archive') {{
    $global:archiveChecked=$true
    return @('{{"source_id":"{IMAGE_ID}","restore_ids":["{IMAGE_ID}"],"archive_sha256":"{"d" * 64}"}}','RESOURCE_RECOVERY_CHECK_PASSED')
  }}
  if ($args[2] -eq 'verify') {{
    $directory=$args[[Array]::IndexOf($args,'--directory')+1]
    [IO.File]::WriteAllText((Join-Path $directory 'verification.json'),'{{"controlled":true}}')
  }}
  return 'CONTROLLED_POLICY_BOUNDARY'
}}
function global:docker {{
  $global:LASTEXITCODE=0
  $global:dockerCount++
  if ($args -contains 'save' -or $args -contains 'run' -or $args -contains 'rm') {{
    [IO.File]::AppendAllText('{tmp_path / "source-actions.txt"}',(($args -join ' ')+[Environment]::NewLine))
  }}
  if ($global:preflightCount -lt 1) {{ throw 'IO_BEFORE_PRIMARY_PREFLIGHT' }}
  $contended=$false
  try {{ $attempt=[IO.File]::Open('{lock}','Open','ReadWrite','None'); $attempt.Dispose() }}
  catch [IO.IOException] {{ $contended=$true }}
  if (-not $contended) {{ throw 'DOCKER_WITHOUT_EXCLUSIVE_ORIGINAL_FENCE' }}
  if ('{mode}' -eq 'docker-failure') {{ $global:LASTEXITCODE=23; return 'PRIVATE FAILURE' }}
  if ($args -contains 'info') {{
    if ('{mode}' -eq 'daemon-switch') {{ return 'foreign-daemon' }}
    if ($args[1] -eq 'isolated') {{ return 'independent-daemon' }}
    return 'source-daemon'
  }}
  if ($args -contains 'inspect') {{
    if ($args -contains 'container') {{ return '{{"Id":"{"c" * 64}","Image":"{IMAGE_ID}","State":{{"Running":false}},"Mounts":[]}}' }}
    foreach ($removed in $global:removed) {{ if ($args -contains $removed) {{ throw 'REINSPECTED_ALREADY_RETIRED_TARGET' }} }}
    if ($args -contains 'image') {{
      if ($args[1] -eq 'isolated') {{
        if ($args[-1] -cne '{config_id}') {{ throw 'WRONG_RESTORE_SELECTOR' }}
        return Get-Content -Raw '{restored_path}'
      }}
      return Get-Content -Raw '{image_path}'
    }}
    if ($args -contains 'volume') {{ return Get-Content -Raw '{volume_path}' }}
  }}
  if ($args -contains 'ls') {{
    if ($args[1] -eq 'isolated' -and ($global:imageLoaded -or '{mode}' -eq 'real-policy-oci-existing')) {{ return '{config_id}' }}
    if ($args -contains 'container') {{
      $global:containerLists++
      if ('{mode}' -eq 'real-policy-stopped-consumer') {{ return '{"c" * 64}' }}
      if ('{mode}' -eq 'real-policy-list-drift' -and $global:containerLists -gt 1) {{ return '{"c" * 64}' }}
    }}
    if ('{mode}' -eq 'real-policy-tag-drift' -and $args -contains 'fixture:reviewed') {{ return 'sha256:{"f" * 64}' }}
    if ($args[1] -eq 'source' -and $args -contains 'fixture:reviewed') {{ return '{source_id}' }}
    return
  }}
  if ($args -contains 'save') {{
    if ('{mode}' -like 'real-policy-oci*') {{
      Copy-Item -LiteralPath '{tmp_path / "image.tar"}' -Destination $args[[Array]::IndexOf($args,'--output')+1]
    }}
    return
  }}
  if ($args -contains 'load' -or $args -contains 'create') {{
    if (-not $global:archiveChecked) {{ throw 'RESTORE_BEFORE_ARCHIVE_CHECK' }}
    $global:archiveChecked=$false
    if ($args -contains 'load') {{ $global:imageLoaded=$true }}
    return
  }}
  if ($args -contains 'run') {{
    if ($args -notcontains '--rm' -or $args -notcontains '--max-bytes' -or $args -contains '--publish') {{ throw 'UNBOUNDED_VOLUME_WORKER' }}
    return
  }}
  if ($args -contains 'rm') {{
    if (-not $global:targetChecked) {{ throw 'ARCHIVE_VERIFICATION_AGED_FINAL_TARGET_CHECK' }}
    if ($args -contains '--force' -or $args -contains '-f') {{ throw 'FORCE_RETIREMENT' }}
    if ('{mode}' -eq 'second-retirement-failure' -and $global:removed.Count -eq 1) {{ $global:LASTEXITCODE=23; return 'PRIVATE FAILURE' }}
    $global:removed += $args[-1]
    return
  }}
  throw 'UNEXPECTED_DOCKER_COMMAND'
}}
& '{ROOT / "automation/Invoke-ResourceOnlyRecovery.ps1"}' -Stage {stage} -ProjectsRoot '{workspace}' `
  -WorkbenchRepoPath '{workspace / "lotus-workbench"}' -RuntimeHolder fixture-holder `
  -Disposition '{approval_path}' -ExpectedDispositionSha256 '{policy.file_digest(approval_path)}' `
  -Plan '{tmp_path / "plan.json"}' -Inventory '{tmp_path / "inventory.json"}' {receipt_argument}
exit $LASTEXITCODE
"""
    # Leaf files exist only for the wrapper's primary-path validation; their
    # semantic admission is independently covered by the real policy tests.
    (tmp_path / "plan.json").write_text(json.dumps(plan), encoding="utf-8")
    (tmp_path / "inventory.json").write_text(json.dumps(inventory), encoding="utf-8")
    result = subprocess.run(
        [shell, "-NoProfile", "-Command", script], capture_output=True, text=True
    )
    assert result.returncode == expected, result.stdout + result.stderr
    assert "PRIVATE FAILURE" not in result.stdout + result.stderr
    assert "PRIVATE_FAILURE_TOKEN" not in result.stdout + result.stderr
    receipts = list(storage.glob("runs/*/receipt.json"))
    assert len(receipts) == 1
    receipt = json.loads(receipts[0].read_text(encoding="utf-8"))
    assert receipt["status"] == (
        {
            "DryRun": "dry_run_ready",
            "ArchiveVerify": "archive_verified",
            "Retire": "retired",
        }[stage]
        if expected == 0
        else "operation_finish_failed"
        if mode == "finish-failure"
        else "failed_or_interrupted"
    )
    assert receipt["operation_token"] == "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    if mode in {"unsafe-policy-output", "unsafe-single-policy-output"}:
        assert receipt["reason"] == "RESOURCE_RECOVERY_POLICY_REFUSED"
    if oci_mode:
        assert receipt["remaining_targets"] == approval["targets"]
        reasons = {
            "real-policy-oci-layer": "IMAGE_DESCRIPTOR_DIGEST_MISMATCH",
            "real-policy-oci-restored": "RESTORED_IMAGE_MISMATCH",
            "real-policy-oci-existing": "VERIFICATION_IMAGE_ALREADY_PRESENT",
        }
        if expected:
            assert receipt["reason"] == reasons[mode]
            assert reasons[mode] in result.stdout
        else:
            image_record = receipt["helper_resources"][0]
            assert image_record["restored_id"] == config_id
            assert image_record["restore_ids"] == [source_id, config_id]
        if mode != "real-policy-oci-restored" and expected:
            assert receipt["helper_resources"] == []
    if stage == "Retire":
        assert receipt["archive_approval_sha256"] == archive_identity
        assert (archive_directory / "prepared.json").read_text(
            encoding="utf-8"
        ) == "immutable-original-proof"
        assert receipt["remaining_targets"] == (
            [approval["targets"][1]] if expected else []
        )
        assert receipt["targets"][0]["status"] == "native_removal_absence_confirmed"
        assert receipt["targets"][1]["status"] == (
            "retirement_requested" if expected else "native_removal_absence_confirmed"
        )
    if stage == "ArchiveVerify" and mode == "archive-success":
        assert [item["kind"] for item in receipt["helper_resources"]] == [
            "image",
            "container",
            "volume",
            "container",
        ]
        assert receipt["helper_resources"][0]["status"] == "restore_completed_retained"
        assert receipt["helper_resources"][2]["status"] == "restore_completed_retained"
    if mode == "real-policy-tag-drift":
        assert receipt["helper_resources"] == []
    if mode in {
        "real-policy-sha-drift",
        "real-policy-list-drift",
        "real-policy-stopped-consumer",
        "real-policy-tag-drift",
    }:
        assert not (tmp_path / "source-actions.txt").exists()
    for admission in receipt["admissions"]:
        path = Path(admission["path"])
        observed = json.loads(path.read_text())
        assert policy.file_digest(path) == admission["sha256"]
        assert observed["approval_sha256"] == policy.file_digest(approval_path)
        assert observed["run_id"] == path.parent.name
        assert observed["operation_token"] == receipt["operation_token"]


@pytest.mark.parametrize(
    "mutation,reason",
    [
        (None, "RESOURCE_RECOVERY_CHECK_PASSED"),
        ("prepared-original", "PREPARED_IDENTITY_CHANGED"),
        ("prepared-target", "PREPARED_TARGETS_CHANGED"),
        ("restore", "RESTORED_IMAGE_MISMATCH"),
        ("receipt", "ARTIFACT_DIGEST_MISMATCH"),
    ],
)
@pytest.mark.parametrize("image_kind", ["classic", "oci"])
def test_full_shipped_cli_binds_archive_restore_and_retirement_receipt(
    tmp_path, mutation, reason, image_kind
):
    storage = tmp_path / "storage"
    storage.mkdir(mode=0o700)
    directory = storage / "reviewed/archives"
    directory.mkdir(parents=True)
    target_folder = directory / "0"
    target_folder.mkdir()
    image_path, original = (
        oci_image_archive if image_kind == "oci" else image_archive
    )(target_folder)
    assert image_path.name == "image.tar"
    approval, plan, inventory, snapshot = packet(storage)
    original["Config"].setdefault(
        "Labels", {"com.docker.compose.project": "retired-fixture"}
    )
    approval["targets"] = [
        {
            "kind": "image",
            "id": original["Id"],
            "inspect_sha256": policy.fingerprint("image", original),
        }
    ]
    current = datetime.now(timezone.utc)
    approval.update(
        approved_at=current.isoformat(),
        expires_at=(current + timedelta(hours=1)).isoformat(),
        retain_until=(current + timedelta(days=1)).isoformat(),
    )
    plan["generated_at"] = current.isoformat()
    snapshot.update(
        collection_started_at=current.isoformat(),
        collection_finished_at=current.isoformat(),
        target_indexes=[0],
        volumes=[],
    )
    snapshot["images"] = [original]
    plan["ownership_conflicts"] = [
        {
            "id": original["Id"],
            "resource_type": "image",
            "ownership_state": "unproven_resource_only_owner",
            "compose_project": "retired-fixture",
        }
    ]
    finalize_discovery(approval, plan, inventory, snapshot, current)
    for name, value in [
        ("plan", plan),
        ("inventory", inventory),
        ("snapshot", snapshot),
    ]:
        (tmp_path / f"{name}.json").write_text(json.dumps(value), encoding="utf-8")
    approval["plan_sha256"] = policy.file_digest(tmp_path / "plan.json")
    approval["inventory_sha256"] = policy.file_digest(tmp_path / "inventory.json")
    approval_path = tmp_path / "approval.json"
    approval_path.write_text(json.dumps(approval), encoding="utf-8")
    approval_sha = policy.file_digest(approval_path)
    common = [sys.executable, "-I", str(ROOT / "automation/resource_recovery/cli.py")]
    options = [
        "--approval",
        str(approval_path),
        "--expected-approval-sha256",
        approval_sha,
        "--root",
        str(ROOT),
        "--directory",
        str(directory),
        "--plan",
        str(tmp_path / "plan.json"),
        "--inventory",
        str(tmp_path / "inventory.json"),
    ]

    def invoke(action, extra=()):
        return subprocess.run(
            common + [action] + options + list(extra), capture_output=True, text=True
        )

    snapshot["approval_sha256"] = approval_sha
    (tmp_path / "snapshot.json").write_text(json.dumps(snapshot), encoding="utf-8")
    prepared = invoke(
        "prepare",
        [
            "--phase",
            "archive-verify",
            "--plan",
            str(tmp_path / "plan.json"),
            "--inventory",
            str(tmp_path / "inventory.json"),
            "--snapshot",
            str(tmp_path / "snapshot.json"),
            "--expected-snapshot-sha256",
            policy.file_digest(tmp_path / "snapshot.json"),
        ],
    )
    assert prepared.returncode == 0, prepared.stdout + prepared.stderr
    # Pre-load archive verification succeeds without any restored metadata.
    assert invoke("verify-archive", ["--target-index", "0"]).returncode == 0
    (target_folder / "restored.json").write_text(json.dumps(original), encoding="utf-8")
    verified = invoke("verify")
    assert verified.returncode == 0, verified.stdout
    receipt = {
        "status": "archive_verified",
        "approval_sha256": approval_sha,
        "verification_sha256": policy.file_digest(directory / "verification.json"),
    }
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    receipt_sha = policy.file_digest(receipt_path)
    if mutation in {"prepared-original", "prepared-target"}:
        prepared_path = directory / "prepared.json"
        value = json.loads(prepared_path.read_text(encoding="utf-8"))
        item = value["targets"][0]
        if mutation == "prepared-original":
            item["original"]["Config"] = {"Env": ["tampered"]}
        else:
            item["target"]["id"] = IMAGE_ID
        prepared_path.write_text(json.dumps(value), encoding="utf-8")
    elif mutation == "restore":
        changed = copy.deepcopy(original)
        changed["Os"] = "foreign"
        (target_folder / "restored.json").write_text(
            json.dumps(changed), encoding="utf-8"
        )
    elif mutation == "receipt":
        receipt["status"] = "archival_requested"
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    result = invoke(
        "verify-retirement",
        ["--receipt", str(receipt_path), "--expected-receipt-sha256", receipt_sha],
    )
    assert result.returncode == (0 if mutation is None else 1), (
        result.stdout + result.stderr
    )
    assert result.stdout.strip() == reason


def test_volume_archive_preserves_directory_symlink_and_hardlink_identity(tmp_path):
    content = b"hardlink fixture bytes"
    base = {"uid": 1201, "gid": 1202, "mode": 0o640}
    regular = dict(
        base,
        kind="file",
        size=len(content),
        sha256=hashlib.sha256(content).hexdigest(),
        hardlink_to="data",
    )
    manifest = {
        "schema_version": "lotus.resource-recovery.files.v1",
        "files": {
            ".": dict(base, kind="directory", mode=0o700),
            "data": regular,
            "alias": copy.deepcopy(regular),
            "pointer": dict(base, kind="symlink", link="data"),
        },
    }
    path = tmp_path / "volume.tar"
    with tarfile.open(path, "w") as output:
        add_member(output, ".", kind=tarfile.DIRTYPE, mode=0o700)
        add_member(output, "data", content)
        add_member(output, "alias", kind=tarfile.LNKTYPE, link="data")
        add_member(output, "pointer", kind=tarfile.SYMTYPE, link="data")
    assert archive.verify_volume(path, manifest, 1024 * 1024) == policy.file_digest(
        path
    )
    with pytest.raises(policy.Refused, match="ARCHIVE_BUDGET_OR_ABSENCE"):
        archive.verify_volume(path, manifest, 1)


def test_parent_checks_helper_digest_before_executing_verifier(tmp_path):
    shell = shutil.which("pwsh") or shutil.which("powershell")
    assert shell
    approval, *_ = packet(tmp_path)
    approval["helper_files"]["automation/resource_recovery/cli.py"] = "f" * 64
    approval_path = tmp_path / "approval.json"
    approval_path.write_text(json.dumps(approval), encoding="utf-8")
    marker = tmp_path / "verifier-was-run"
    script = f"""
function global:python {{ [IO.File]::WriteAllText('{marker}', 'UNSAFE'); $global:LASTEXITCODE=0 }}
& '{ROOT / "automation/Invoke-ResourceOnlyRecovery.ps1"}' -Stage DryRun -ProjectsRoot '{tmp_path}' `
  -WorkbenchRepoPath '{tmp_path}' -RuntimeHolder fixture-holder -Disposition '{approval_path}' `
  -ExpectedDispositionSha256 '{policy.file_digest(approval_path)}' -Plan absent -Inventory absent
exit $LASTEXITCODE
"""
    result = subprocess.run(
        [shell, "-NoProfile", "-Command", script], capture_output=True, text=True
    )
    assert result.returncode == 1
    assert not marker.exists()
    assert not (tmp_path / "lotus-platform").exists()


@pytest.mark.parametrize(
    "mutation,reason",
    [
        (None, "RESOURCE_RECOVERY_CHECK_PASSED"),
        ("target", "RENEWAL_IDENTITY_CHANGED"),
        ("helper", "HELPER_SOURCE_CHANGED"),
        ("daemon", "RENEWAL_IDENTITY_CHANGED"),
        ("archive", "IMAGE_LAYER_CORRUPT"),
        ("incomplete", "UNFINISHED_VERIFICATION_RECEIPT"),
        ("stale", "STALE_OBSERVATION"),
        ("receipt-binding", "RENEWAL_RECEIPT_CHANGED"),
        ("archive-binding", "ARTIFACT_DIGEST_MISMATCH"),
        ("expired", "DISPOSITION_EXPIRED"),
        ("snapshot-stale", "STALE_OBSERVATION"),
        ("verification-daemon", "RENEWAL_IDENTITY_CHANGED"),
        ("archive-directory", "IMMUTABLE_ARCHIVE_PATH"),
    ],
)
def test_shipped_cli_renews_retirement_without_rewriting_archive_provenance(
    tmp_path, mutation, reason
):
    current = datetime.now(timezone.utc)
    earlier = current - timedelta(seconds=600)
    storage = tmp_path / "storage"
    storage.mkdir(mode=0o700)
    approval, plan, inventory, snapshot = packet(storage)
    fixture_dir = storage / "fixture"
    fixture_dir.mkdir()
    image_path, original = image_archive(fixture_dir)
    original["Config"]["Labels"] = {"com.docker.compose.project": "retired-fixture"}
    approval["targets"] = [
        {
            "kind": "image",
            "id": original["Id"],
            "inspect_sha256": policy.fingerprint("image", original),
        }
    ]
    approval.update(
        approved_at=earlier.isoformat(),
        expires_at=(earlier + timedelta(hours=1)).isoformat(),
        retain_until=(current + timedelta(days=1)).isoformat(),
    )
    plan["generated_at"] = earlier.isoformat()
    snapshot.update(
        collection_started_at=earlier.isoformat(),
        collection_finished_at=earlier.isoformat(),
        target_indexes=[0],
        volumes=[],
    )
    plan["ownership_conflicts"] = [
        {
            "id": original["Id"],
            "resource_type": "image",
            "ownership_state": "unproven_resource_only_owner",
            "compose_project": "retired-fixture",
        }
    ]
    snapshot["images"] = [original]
    finalize_discovery(approval, plan, inventory, snapshot, earlier)
    for name, value in [("plan", plan), ("inventory", inventory)]:
        (tmp_path / f"original-{name}.json").write_text(
            json.dumps(value), encoding="utf-8"
        )
        approval[f"{name}_sha256"] = policy.file_digest(
            tmp_path / f"original-{name}.json"
        )
    original_path = tmp_path / "original-approval.json"
    original_path.write_text(json.dumps(approval), encoding="utf-8")
    original_sha = policy.file_digest(original_path)
    records = policy.admit(
        approval, plan, inventory, snapshot, now=earlier, phase="archive-verify"
    )
    snapshot["phase"] = "retire"
    with pytest.raises(policy.Refused, match="STALE_OBSERVATION"):
        policy.admit(approval, plan, inventory, snapshot, now=current, phase="retire")
    directory = storage / original_sha / "archives"
    (directory / "0").mkdir(parents=True)
    shutil.move(image_path, directory / "0/image.tar")
    (directory / "0/restored.json").write_text(json.dumps(original), encoding="utf-8")
    prepared = {
        "approval_sha256": original_sha,
        "targets": [{"target": approval["targets"][0], "original": records[0]}],
    }
    prepared_path = directory / "prepared.json"
    prepared_path.write_text(json.dumps(prepared), encoding="utf-8")

    def invoke(action, approved_path, options):
        return subprocess.run(
            [
                sys.executable,
                "-I",
                str(ROOT / "automation/resource_recovery/cli.py"),
                action,
                "--approval",
                str(approved_path),
                "--expected-approval-sha256",
                policy.file_digest(approved_path),
                "--root",
                str(ROOT),
                "--plan",
                str(tmp_path / "original-plan.json"),
                "--inventory",
                str(tmp_path / "original-inventory.json"),
            ]
            + options,
            capture_output=True,
            text=True,
        )

    verified = invoke("verify", original_path, ["--directory", str(directory)])
    assert verified.returncode == 0, verified.stdout
    receipt_path = tmp_path / "archive-receipt.json"
    receipt = {
        "status": "archive_verified",
        "approval_sha256": original_sha,
        "verification_sha256": policy.file_digest(directory / "verification.json"),
    }
    if mutation == "incomplete":
        receipt["status"] = "verification_completed_pending_finish"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    renewal = copy.deepcopy(approval)
    renewal.update(
        schema_version=policy.RENEWAL_SCHEMA,
        archive_approval_sha256=original_sha,
        archive_receipt_sha256=policy.file_digest(receipt_path),
        approved_at=current.isoformat(),
        expires_at=(current + timedelta(hours=1)).isoformat(),
    )
    snapshot.update(
        collection_started_at=current.isoformat(),
        collection_finished_at=current.isoformat(),
    )
    if mutation == "stale":
        snapshot["collection_started_at"] = earlier.isoformat()
    if mutation == "snapshot-stale":
        snapshot["collection_started_at"] = earlier.isoformat()
    for name, value in [
        ("plan", plan),
        ("inventory", inventory),
        ("snapshot", snapshot),
    ]:
        (tmp_path / f"fresh-{name}.json").write_text(
            json.dumps(value), encoding="utf-8"
        )
    if mutation == "target":
        renewal["targets"][0]["id"] = IMAGE_ID
    elif mutation == "helper":
        renewal["helper_files"]["automation/resource_recovery/cli.py"] = "f" * 64
    elif mutation == "daemon":
        renewal["source_daemon"] = "foreign-daemon"
    elif mutation == "verification-daemon":
        renewal["verification_daemon"] = "foreign-verifier"
    elif mutation == "expired":
        renewal["expires_at"] = current.isoformat()
    elif mutation == "archive-binding":
        renewal["archive_approval_sha256"] = "f" * 64
    elif mutation == "receipt-binding":
        renewal["archive_receipt_sha256"] = "f" * 64
    elif mutation == "archive":
        image_archive(directory / "0", corrupt=True)
    renewal_path = tmp_path / "renewal.json"
    renewal_path.write_text(json.dumps(renewal), encoding="utf-8")
    snapshot["approval_sha256"] = policy.file_digest(renewal_path)
    (tmp_path / "fresh-snapshot.json").write_text(
        json.dumps(snapshot), encoding="utf-8"
    )
    immutable_before = policy.file_digest(prepared_path)
    run_directory = storage / "fresh-retirement"
    run_directory.mkdir()
    if mutation == "archive-directory":
        run_directory = directory
    common = ["--archive-approval", str(original_path)]
    admission = invoke(
        "prepare",
        renewal_path,
        common
        + [
            "--phase",
            "retire",
            "--directory",
            str(run_directory),
            "--plan",
            str(tmp_path / "fresh-plan.json"),
            "--inventory",
            str(tmp_path / "fresh-inventory.json"),
            "--snapshot",
            str(tmp_path / "fresh-snapshot.json"),
            "--expected-snapshot-sha256",
            policy.file_digest(tmp_path / "fresh-snapshot.json"),
        ],
    )
    if admission.returncode:
        result = admission
    else:
        result = invoke(
            "verify-retirement",
            renewal_path,
            common
            + [
                "--directory",
                str(directory),
                "--receipt",
                str(receipt_path),
                "--expected-receipt-sha256",
                policy.file_digest(receipt_path),
            ],
        )
    assert result.returncode == (0 if mutation is None else 1), (
        result.stdout + result.stderr
    )
    assert result.stdout.strip() == reason
    assert policy.file_digest(prepared_path) == immutable_before
    assert prepared["approval_sha256"] == original_sha


def test_retirement_renewal_cannot_admit_another_archive_or_dry_run(tmp_path):
    original, plan, inventory, snapshot = packet(tmp_path)
    renewal = dict(
        original,
        schema_version=policy.RENEWAL_SCHEMA,
        archive_approval_sha256="1" * 64,
        archive_receipt_sha256="2" * 64,
    )
    policy.validate_renewal(renewal, original)
    for phase in ["dry-run", "archive-verify"]:
        with pytest.raises(policy.Refused, match="RETIREMENT_ONLY_RENEWAL"):
            policy.admit(renewal, plan, inventory, snapshot, now=NOW, phase=phase)
