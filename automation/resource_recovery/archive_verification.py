"""Read archive bytes without extracting them into host or application paths."""

from __future__ import annotations

import hashlib
import gzip
import json
import posixpath
import re
import tarfile
import zlib
from pathlib import Path

from .policy import file_digest, require, safe_path


def _member_name(name: str) -> str:
    require(
        not name.startswith("/") and ".." not in name.split("/"), "ARCHIVE_PATH_ESCAPE"
    )
    return posixpath.normpath(name)


def _members(archive: tarfile.TarFile) -> dict[str, tarfile.TarInfo]:
    result: dict[str, tarfile.TarInfo] = {}
    for member in archive:
        require(len(result) < 100_000, "ARCHIVE_MEMBER_BUDGET")
        name = _member_name(member.name)
        require(name not in result, "DUPLICATE_ARCHIVE_MEMBER")
        result[name] = member
    return result


def _bytes(archive: tarfile.TarFile, member: tarfile.TarInfo) -> bytes:
    require(
        member.isfile() and member.size <= 8 * 1024 * 1024, "ARCHIVE_METADATA_BUDGET"
    )
    stream = archive.extractfile(member)
    require(stream is not None, "ARCHIVE_MEMBER_UNREADABLE")
    with stream:
        return stream.read()


def _member_hash(archive: tarfile.TarFile, member: tarfile.TarInfo) -> str:
    stream = archive.extractfile(member)
    require(stream is not None, "ARCHIVE_MEMBER_UNREADABLE")
    hashed = hashlib.sha256()
    with stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hashed.update(block)
    return hashed.hexdigest()


def check_budget(path: Path, budget: int) -> None:
    safe_path(path)
    require(
        path.is_file() and 0 < path.stat().st_size <= budget,
        "ARCHIVE_BUDGET_OR_ABSENCE",
    )


OCI_MANIFEST = "application/vnd.oci.image.manifest.v1+json"
OCI_CONFIG = "application/vnd.oci.image.config.v1+json"
OCI_LAYER = "application/vnd.oci.image.layer.v1.tar"


def _json(archive, members, name):
    require(name in members, "IMAGE_MEMBER_ABSENT")
    return json.loads(_bytes(archive, members[name]))


def _descriptor(archive, members, descriptor, media_types):
    require(isinstance(descriptor, dict), "IMAGE_DESCRIPTOR_INVALID")
    digest = descriptor.get("digest")
    require(
        isinstance(digest, str)
        and re.fullmatch(r"sha256:[0-9a-f]{64}", digest)
        and descriptor.get("mediaType") in media_types
        and not any(key in descriptor for key in ("urls", "data", "artifactType")),
        "IMAGE_DESCRIPTOR_UNSUPPORTED",
    )
    name = "blobs/sha256/" + digest[7:]
    member = members.get(name)
    require(member is not None and member.isfile(), "IMAGE_MEMBER_ABSENT")
    require(
        type(descriptor.get("size")) is int and descriptor["size"] == member.size,
        "IMAGE_DESCRIPTOR_SIZE_MISMATCH",
    )
    require(
        "sha256:" + _member_hash(archive, member) == digest,
        "IMAGE_DESCRIPTOR_DIGEST_MISMATCH",
    )
    return name


def _diff_id(archive, member, compressed, remaining):
    stream = archive.extractfile(member)
    require(stream is not None, "ARCHIVE_MEMBER_UNREADABLE")
    hashed = hashlib.sha256()
    count = 0
    try:
        with stream:
            reader = gzip.GzipFile(fileobj=stream) if compressed else stream
            try:
                while block := reader.read(min(1024 * 1024, remaining - count + 1)):
                    count += len(block)
                    require(count <= remaining, "IMAGE_DECOMPRESSION_BUDGET")
                    hashed.update(block)
            finally:
                if compressed:
                    reader.close()
    except (OSError, EOFError, zlib.error):
        require(False, "IMAGE_LAYER_ENCODING_INVALID")
    return "sha256:" + hashed.hexdigest(), count


def image_identity(path: Path, original: dict, budget: int) -> dict:
    """Validate content before returning the only permitted restoration identities."""
    check_budget(path, budget)
    with tarfile.open(path, "r:") as archive:
        members = _members(archive)
        require("manifest.json" in members, "IMAGE_MANIFEST_ABSENT")
        manifests = json.loads(_bytes(archive, members["manifest.json"]))
        require(
            isinstance(manifests, list) and len(manifests) == 1,
            "SINGLE_IMAGE_ARCHIVE_REQUIRED",
        )
        manifest = manifests[0]
        config_name = _member_name(manifest["Config"])
        require(config_name in members, "IMAGE_CONFIG_ABSENT")
        config_bytes = _bytes(archive, members[config_name])
        config_id = "sha256:" + hashlib.sha256(config_bytes).hexdigest()
        graph_id = None
        oci = "oci-layout" in members or "index.json" in members
        descriptors = None
        if oci:
            require(
                _json(archive, members, "oci-layout").get("imageLayoutVersion")
                == "1.0.0",
                "IMAGE_LAYOUT_UNSUPPORTED",
            )
            index = _json(archive, members, "index.json")
            require(
                index.get("schemaVersion") == 2
                and len(index.get("manifests", [])) == 1,
                "SINGLE_IMAGE_ARCHIVE_REQUIRED",
            )
            descriptor = index["manifests"][0]
            graph_name = _descriptor(archive, members, descriptor, {OCI_MANIFEST})
            graph_id = descriptor["digest"]
            source_descriptor = original.get("Descriptor")
            require(
                isinstance(source_descriptor, dict)
                and all(
                    source_descriptor.get(key) == descriptor[key]
                    for key in ("digest", "size", "mediaType")
                )
                and original["Id"] == graph_id,
                "IMAGE_SOURCE_DESCRIPTOR_MISMATCH",
            )
            graph = _json(archive, members, graph_name)
            require(
                graph.get("schemaVersion") == 2
                and graph.get("mediaType", OCI_MANIFEST) == OCI_MANIFEST
                and "artifactType" not in graph,
                "IMAGE_MANIFEST_UNSUPPORTED",
            )
            require(
                _descriptor(archive, members, graph["config"], {OCI_CONFIG})
                == config_name,
                "IMAGE_CONFIG_MISMATCH",
            )
            descriptors = graph["layers"]
            require(isinstance(descriptors, list), "IMAGE_LAYERS_INCOMPLETE")
            graph_layers = [
                _descriptor(archive, members, item, {OCI_LAYER, OCI_LAYER + "+gzip"})
                for item in descriptors
            ]
            require(
                graph_layers == manifest.get("Layers"), "IMAGE_GRAPH_LAYERS_MISMATCH"
            )
            annotations = descriptor.get("annotations", {})
            image_name = annotations.get("io.containerd.image.name")
            if image_name is not None:
                tags = original.get("RepoTags") or []
                require(
                    any(
                        image_name == tag or image_name == "docker.io/library/" + tag
                        for tag in tags
                    ),
                    "IMAGE_TAGS_MISMATCH",
                )
            ref_name = annotations.get("org.opencontainers.image.ref.name")
            if ref_name is not None:
                require(
                    any(
                        ref_name == tag.rsplit(":", 1)[-1]
                        for tag in original.get("RepoTags") or []
                    ),
                    "IMAGE_TAGS_MISMATCH",
                )
        else:
            require(config_id == original["Id"], "IMAGE_CONFIG_MISMATCH")
        require(
            sorted(manifest.get("RepoTags") or [])
            == sorted(original.get("RepoTags") or []),
            "IMAGE_TAGS_MISMATCH",
        )
        config = json.loads(config_bytes)
        if oci:
            require(
                config.get("architecture") == original.get("Architecture")
                and config.get("os") == original.get("Os")
                and config.get("variant") == original.get("Variant"),
                "IMAGE_PLATFORM_MISMATCH",
            )
            platform = descriptor.get("platform")
            if platform is not None:
                require(
                    all(
                        platform.get(key) == config.get(key)
                        for key in ("architecture", "os", "variant")
                    ),
                    "IMAGE_PLATFORM_MISMATCH",
                )
            require(
                config.get("config", {}) == original.get("Config")
                and config.get("created") == original.get("Created"),
                "IMAGE_METADATA_MISMATCH",
            )
            require(
                config.get("rootfs", {}).get("type") == "layers",
                "IMAGE_ROOTFS_MISMATCH",
            )
        layers = manifest.get("Layers")
        expected = original["RootFS"]["Layers"]
        require(
            config.get("rootfs", {}).get("diff_ids") == expected,
            "IMAGE_ROOTFS_MISMATCH",
        )
        require(
            isinstance(layers, list) and len(layers) == len(expected),
            "IMAGE_LAYERS_INCOMPLETE",
        )
        remaining = budget
        for index, (name, expected_digest) in enumerate(
            zip(layers, expected, strict=True)
        ):
            member = members.get(_member_name(name))
            require(member is not None and member.isfile(), "IMAGE_LAYER_ABSENT")
            digest, count = _diff_id(
                archive,
                member,
                bool(descriptors and descriptors[index]["mediaType"].endswith("+gzip")),
                remaining,
            )
            remaining -= count
            require(digest == expected_digest, "IMAGE_LAYER_CORRUPT")
    return {
        "archive_sha256": file_digest(path),
        "source_id": original["Id"],
        "config_id": config_id,
        "graph_id": graph_id,
        "restore_ids": list(dict.fromkeys([original["Id"], config_id])),
    }


def verify_image(path: Path, original: dict, budget: int) -> str:
    return image_identity(path, original, budget)["archive_sha256"]


def verify_volume(path: Path, manifest: dict, budget: int) -> str:
    check_budget(path, budget)
    require(
        manifest.get("schema_version") == "lotus.resource-recovery.files.v1",
        "INVALID_FILE_MANIFEST",
    )
    files = manifest["files"]
    require(isinstance(files, dict) and bool(files), "EMPTY_FILE_MANIFEST")
    with tarfile.open(path, "r:") as archive:
        members = _members(archive)
        require(set(members) == set(files), "VOLUME_ARCHIVE_INCOMPLETE")
        for name, expected in files.items():
            member = members[name]
            require(
                member.uid == expected["uid"]
                and member.gid == expected["gid"]
                and member.mode == expected["mode"],
                "ARCHIVE_OWNERSHIP_OR_MODE_MISMATCH",
            )
            kind = expected["kind"]
            if kind == "file":
                require(member.isfile() or member.islnk(), "FILE_TYPE_MISMATCH")
                if member.islnk():
                    require(
                        _member_name(member.linkname) == expected["hardlink_to"],
                        "HARDLINK_MISMATCH",
                    )
                else:
                    require(member.size == expected["size"], "FILE_SIZE_MISMATCH")
                require(
                    _member_hash(archive, member) == expected["sha256"],
                    "FILE_CONTENT_MISMATCH",
                )
            elif kind == "directory":
                require(member.isdir(), "FILE_TYPE_MISMATCH")
            elif kind == "symlink":
                require(
                    member.issym() and member.linkname == expected["link"],
                    "SYMLINK_MISMATCH",
                )
            else:
                require(False, "UNSUPPORTED_FILE_TYPE")
    return file_digest(path)


def verify_restored_image(
    original: dict, restored: dict, identity: dict | None = None
) -> None:
    allowed = identity["restore_ids"] if identity else [original.get("Id")]
    require(restored.get("Id") in allowed, "RESTORED_IMAGE_MISMATCH")
    if identity and restored.get("Id") == identity.get("graph_id"):
        require(
            restored.get("Descriptor") == original.get("Descriptor"),
            "RESTORED_IMAGE_MISMATCH",
        )
    for field in ("Architecture", "Os", "Config", "RootFS"):
        require(original.get(field) == restored.get(field), "RESTORED_IMAGE_MISMATCH")
    if identity and identity.get("graph_id"):
        for field in ("Created", "Variant"):
            require(
                original.get(field) == restored.get(field), "RESTORED_IMAGE_MISMATCH"
            )
    require(
        sorted(original.get("RepoTags") or [])
        == sorted(restored.get("RepoTags") or []),
        "RESTORED_TAGS_MISMATCH",
    )


def verify_restored_volume(original: dict, restored: dict) -> None:
    require(original == restored, "RESTORED_VOLUME_MISMATCH")
