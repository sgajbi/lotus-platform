"""Verify one existing workflow-bound admitted PostgreSQL service; never acquire an image.

Config/RootFS hashing is extracted from Performance's reviewed acquisition helper.
Child/config linkage comes from the central admitted tuple; no fresh registry bytes
or compressed transfer bytes are claimed by this local proof.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import time
import zlib
from pathlib import Path, PurePosixPath

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate_technology_governance_policy as policy

MAX_ARCHIVE_BYTES = 4 * 1024**3
MAX_EXPANDED_BYTES = 8 * 1024**3
MAX_JSON_BYTES = 2 * 1024**2
MAX_MEMBERS = 4096
MAX_LAYERS = 128
MAX_CAPTURE_BYTES = 4 * 1024**2
TOTAL_SECONDS = 240
COMMAND_SECONDS = 120
DIGEST = re.compile(r"sha256:[0-9a-f]{64}")


class Budget:
    """Shared wall deadline and decompressed byte cap, checked during every read."""

    def __init__(self):
        self.deadline = time.monotonic() + TOTAL_SECONDS
        self.expanded = 0

    def remaining(self) -> float:
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise ValueError("local verification deadline exhausted")
        return remaining

    def consume(self, count: int) -> None:
        self.remaining()
        self.expanded += count
        if self.expanded > MAX_EXPANDED_BYTES:
            raise ValueError("local verification expansion limit exceeded")


def command(argv: list[str], budget: Budget, *, artifact: Path | None = None) -> bytes:
    """Bound child time, file capture and export growth; no shell or retained secrets."""
    env = os.environ.copy()
    for key in ("DOCKER_HOST", "DOCKER_CONTEXT", "DOCKER_TLS_VERIFY", "DOCKER_CERT_PATH"):
        env.pop(key, None)
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"):
        env.pop(key, None)
    deadline = time.monotonic() + min(COMMAND_SECONDS, budget.remaining())
    with tempfile.TemporaryDirectory(prefix="lotus-service-command-") as temporary:
        stdout_path, stderr_path = Path(temporary) / "stdout", Path(temporary) / "stderr"
        with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
            process = subprocess.Popen(argv, stdout=stdout, stderr=stderr, env=env, stdin=subprocess.DEVNULL)
            try:
                while True:
                    _command_limits(stdout_path, stderr_path, artifact, deadline, budget)
                    if process.poll() is not None:
                        break
                    time.sleep(0.02)
                if process.returncode:
                    raise ValueError("local verification command failed")
            finally:
                if process.poll() is None:
                    process.kill()
                process.wait(timeout=5)
        _command_limits(stdout_path, stderr_path, artifact, deadline, budget)
        with stdout_path.open("rb") as stream:
            captured = stream.read(MAX_CAPTURE_BYTES + 1)
        if len(captured) > MAX_CAPTURE_BYTES:
            raise ValueError("local verification command capture limit exceeded")
        return captured


def _command_limits(stdout: Path, stderr: Path, artifact: Path | None, deadline: float, budget: Budget) -> None:
    budget.remaining()
    if time.monotonic() >= deadline:
        raise ValueError("local verification command deadline exceeded")
    if any(path.stat().st_size > MAX_CAPTURE_BYTES for path in (stdout, stderr)):
        raise ValueError("local verification command capture limit exceeded")
    if artifact is not None and artifact.exists() and artifact.stat().st_size > MAX_ARCHIVE_BYTES:
        raise ValueError("local verification export limit exceeded")


def sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _one_object(raw: bytes) -> dict:
    payload = json.loads(raw)
    if not isinstance(payload, list) or len(payload) != 1 or not isinstance(payload[0], dict):
        raise ValueError("local inspect must resolve exactly one object")
    return payload[0]


def admitted_mapping(expected_image: str) -> dict:
    errors = policy.validate_policy_path(exception_register_paths=[])
    if errors:
        raise ValueError("central policy did not validate")
    repository, _, digest = expected_image.partition("@")
    distribution = policy.PUBLISHER_DISTRIBUTIONS.get(repository, "")
    mapping = policy.resolve_distribution(
        policy.load_policy(), expected_image, distribution + "@" + digest, "linux/amd64",
    )
    policy.require_original_selection(mapping)
    return mapping


def policy_identity(expected_commit: str, budget: Budget) -> dict:
    if re.fullmatch(r"[0-9a-f]{40}", expected_commit) is None:
        raise ValueError("policy revision must be an exact commit")
    prefix = ["git", "-C", str(policy.ROOT)]
    actual = command(prefix + ["rev-parse", "HEAD"], budget).decode().strip()
    root = command(prefix + ["rev-parse", "--show-toplevel"], budget).decode().strip()
    if actual != expected_commit or Path(root).resolve() != policy.ROOT.resolve():
        raise ValueError("policy source differs from the expected checkout")
    if command(prefix + ["status", "--porcelain=v1", "-z", "--untracked-files=all"], budget):
        raise ValueError("policy checkout must be clean, including untracked files")
    blobs = {}
    for path in (policy.POLICY_PATH, policy.SCHEMA_PATH, Path(policy.__file__), Path(__file__)):
        relative = path.resolve().relative_to(policy.ROOT.resolve()).as_posix()
        committed = command(prefix + ["show", f"{expected_commit}:{relative}"], budget)
        if path.read_bytes().replace(b"\r\n", b"\n") != committed:
            raise ValueError("policy/helper bytes differ from expected committed source")
        blobs[relative] = sha256(committed)
    return {
        "commit": actual,
        "committed_content_sha256": blobs,
    }


def verify_service(container: dict, image: dict, container_id: str, expected_image: str) -> None:
    if container.get("Id") != container_id or container.get("Config", {}).get("Image") != expected_image:
        raise ValueError("service identity/requested image differs from workflow binding")
    image_id = container.get("Image", "")
    if not isinstance(image_id, str) or DIGEST.fullmatch(image_id) is None or image.get("Id") != image_id:
        raise ValueError("service immutable image differs from inspected image")
    if container.get("State", {}).get("Running") is not True:
        raise ValueError("bound service is not running")
    if (image.get("Os"), image.get("Architecture")) != ("linux", "amd64"):
        raise ValueError("service image platform differs from admission")
    # Docker abbreviates official repository names in metadata, never in selection.
    digest = expected_image.split("@", 1)[1]
    accepted = {expected_image, "postgres@" + digest, "library/postgres@" + digest}
    repo_digests = image.get("RepoDigests")
    if not isinstance(repo_digests, list) or not accepted.intersection(repo_digests):
        raise ValueError("service image lacks the admitted original index repository digest")


def _member_name(name: str) -> None:
    path = PurePosixPath(name)
    if (
        not name or "\\" in name or ":" in name or path.is_absolute()
        or any(part in ("", ".", "..") for part in name.rstrip("/").split("/"))
        or len(name) > 512
    ):
        raise ValueError("unsafe export member path")


class Export:
    """Index regular tar members without extraction; never resolve links or paths."""

    def __init__(self, archive, budget: Budget):
        self.archive, self.budget, self.members = archive, budget, {}
        total = 0
        for member in archive:
            budget.remaining()
            _member_name(member.name)
            if member.name in self.members or len(self.members) >= MAX_MEMBERS:
                raise ValueError("duplicate or excessive export members")
            if not (member.isfile() or member.isdir()) or member.pax_headers:
                raise ValueError("export links/special files/extended headers are forbidden")
            total += member.size
            if member.size < 0 or total > MAX_ARCHIVE_BYTES:
                raise ValueError("export member bytes exceed limit")
            self.members[member.name] = member

    def stream(self, name: str):
        _member_name(name)
        member = self.members.get(name)
        if member is None or not member.isfile():
            raise ValueError("export reference must resolve a regular member")
        stream = self.archive.extractfile(member)
        if stream is None:
            raise ValueError("export member unreadable")
        return stream

    def metadata(self, name: str) -> bytes:
        with self.stream(name) as stream:
            if self.members[name].size > MAX_JSON_BYTES:
                raise ValueError("export metadata exceeds limit")
            raw = stream.read(MAX_JSON_BYTES + 1)
            self.budget.consume(len(raw))
            return raw

    def layer_digest(self, name: str) -> str:
        with self.stream(name) as stream:
            compressed = stream.read(2) == b"\x1f\x8b"
            stream.seek(0)
            content = gzip.GzipFile(fileobj=DeadlineReader(stream, self.budget)) if compressed else stream
            digest = hashlib.sha256()
            try:
                while chunk := content.read(1024**2):
                    self.budget.consume(len(chunk))
                    digest.update(chunk)
            finally:
                if compressed:
                    content.close()
            return "sha256:" + digest.hexdigest()


class DeadlineReader:
    """Check every compressed input read, including runs of empty gzip members."""

    def __init__(self, stream, budget: Budget):
        self.stream, self.budget = stream, budget

    def read(self, size: int = -1) -> bytes:
        self.budget.remaining()
        if not 0 <= size <= 1024**2:
            raise ValueError("unbounded compressed input read")
        return self.stream.read(size)


def verify_export(path: Path, expected_config: str, image: dict, budget: Budget) -> dict:
    """Hash actual config and ordered uncompressed layer bytes, independent of Id."""
    if path.stat().st_size > MAX_ARCHIVE_BYTES:
        raise ValueError("export archive exceeds limit")
    _scan_headers(path, budget)
    with tarfile.open(path, "r:") as archive:
        exported = Export(archive, budget)
        entries = json.loads(exported.metadata("manifest.json"))
        if not isinstance(entries, list) or len(entries) != 1 or not isinstance(entries[0], dict):
            raise ValueError("export must contain exactly one platform image")
        entry = entries[0]
        raw_config = exported.metadata(entry["Config"])
        if sha256(raw_config) != expected_config:
            raise ValueError("exported config bytes differ from admitted config")
        config = json.loads(raw_config)
        if not isinstance(config, dict) or not isinstance(config.get("rootfs"), dict):
            raise ValueError("exported config must describe an object RootFS")
        if (config.get("os"), config.get("architecture")) != ("linux", "amd64"):
            raise ValueError("exported config platform differs from admission")
        rootfs = config.get("rootfs", {})
        layers, diff_ids = entry.get("Layers"), rootfs.get("diff_ids")
        _validate_layers(layers, diff_ids, rootfs.get("type"))
        actual = [exported.layer_digest(name) for name in layers]
        if actual != diff_ids or actual != image.get("RootFS", {}).get("Layers"):
            raise ValueError("exported RootFS differs from config/inspect")
    return {"config_digest": expected_config, "rootfs_diff_ids": actual, "platform": "linux/amd64"}


def _scan_headers(path: Path, budget: Budget) -> None:
    """Refuse extension records before tarfile can allocate their declared payload."""
    names = set()
    size = path.stat().st_size
    with path.open("rb") as stream:
        while True:
            budget.remaining()
            header = stream.read(512)
            if len(header) != 512:
                raise ValueError("truncated export header")
            if header == bytes(512):
                while chunk := stream.read(1024**2):
                    budget.remaining()
                    if any(chunk):
                        raise ValueError("nonzero export trailer")
                return
            if header[156:157] not in (b"0", b"\0", b"5"):
                raise ValueError("export extension/link/special header forbidden")
            member = tarfile.TarInfo.frombuf(header, "utf-8", "strict")
            _member_name(member.name)
            if member.name in names or len(names) >= MAX_MEMBERS:
                raise ValueError("duplicate or excessive export members")
            names.add(member.name)
            end = stream.tell() + ((member.size + 511) // 512) * 512
            if member.size < 0 or end > size:
                raise ValueError("truncated export member")
            stream.seek(end)


def _validate_layers(layers, diff_ids, rootfs_type) -> None:
    if (
        rootfs_type != "layers" or not isinstance(layers, list) or not isinstance(diff_ids, list)
        or not 1 <= len(layers) <= MAX_LAYERS or len(layers) != len(diff_ids)
        or any(not isinstance(name, str) for name in layers)
        or len(set(layers)) != len(layers)
        or any(not isinstance(value, str) or DIGEST.fullmatch(value) is None for value in diff_ids)
    ):
        raise ValueError("exported layer/config descriptors are malformed")


def verify(container_id: str, expected_image: str, expected_policy_commit: str, output: Path) -> dict:
    if re.fullmatch(r"[0-9a-f]{64}", container_id) is None:
        raise ValueError("workflow service binding must be a full container ID")
    if output.exists():
        raise ValueError("proof output must be unused")
    budget = Budget()
    source = policy_identity(expected_policy_commit, budget)
    mapping = admitted_mapping(expected_image)
    docker = ["docker", "--context", "default"]
    context = _one_object(command(docker + ["context", "inspect", "default"], budget))
    if context.get("Endpoints", {}).get("docker", {}).get("Host") != "unix:///var/run/docker.sock":
        raise ValueError("service proof requires the local Linux default daemon")
    container = _one_object(command(docker + ["container", "inspect", container_id], budget))
    image_id = container.get("Image", "")
    if not isinstance(image_id, str) or DIGEST.fullmatch(image_id) is None:
        raise ValueError("service has no immutable image identity")
    image = _one_object(command(docker + ["image", "inspect", image_id], budget))
    verify_service(container, image, container_id, expected_image)
    with tempfile.TemporaryDirectory(prefix="lotus-service-export-") as temporary:
        archive = Path(temporary) / "image.tar"
        command(docker + ["image", "save", "--platform", "linux/amd64", "--output", str(archive), image_id],
                budget, artifact=archive)
        content = verify_export(archive, mapping["platform_config_digest"], image, budget)
    # Re-inspect the bound service to reject replacement/stopping during verification.
    after = _one_object(command(docker + ["container", "inspect", container_id], budget))
    verify_service(after, image, container_id, expected_image)
    budget.remaining()
    result = {
        "schema_version": 1, "proof_type": "local-existing-service-content",
        "policy_source": source, "service_container_id": container_id,
        "service_image_id": image_id, "requested_image": expected_image,
        "admitted_index_digest": mapping["image_digest"],
        "admitted_child_digest": mapping["platform_manifest_digest"],
        "child_config_linkage": "central admitted tuple; no fresh manifest bytes retained",
        **content,
        "raw_export_retained": False, "raw_inspect_retained": False,
        "evidence_type": "checked-helper-produced hashes; temporary export/inspect deleted",
        "cold_acquisition_proven": False, "compressed_transfer_verified": False,
        "runtime_execution_verified": False,
    }
    # Exclusive creation avoids stale proofs masquerading as this invocation.
    stream = output.open("x", encoding="utf-8")
    try:
        with stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    except BaseException:
        output.unlink(missing_ok=True)
        raise
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--container-id", required=True)
    parser.add_argument("--expected-image", required=True)
    parser.add_argument("--expected-policy-commit", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        verify(args.container_id, args.expected_image, args.expected_policy_commit, args.output)
    except (OSError, ValueError, KeyError, TypeError, EOFError, tarfile.TarError, zlib.error, subprocess.SubprocessError) as exc:
        print(f"Local service content proof refused ({type(exc).__name__}); consumer must stop.")
        return 1
    print("Existing service config/RootFS proof passed; no acquisition or runtime execution claimed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
