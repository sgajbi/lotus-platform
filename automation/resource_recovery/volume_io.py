"""Isolated container worker: fixed mount paths, no Docker API or database process."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import stat
import subprocess
from pathlib import Path

SOURCE = Path("/source")
ARCHIVE = Path("/archive")


def file_manifest(root: Path) -> dict:
    files: dict = {}
    hardlinks: dict[tuple[int, int], str] = {}
    pending = [root]
    while pending:
        path = pending.pop()
        info = path.lstat()
        relative = path.relative_to(root).as_posix() if path != root else "."
        record = {
            "uid": info.st_uid,
            "gid": info.st_gid,
            "mode": stat.S_IMODE(info.st_mode),
            "mtime_ns": info.st_mtime_ns,
            "xattrs": {
                name: base64.b64encode(
                    os.getxattr(path, name, follow_symlinks=False)
                ).decode()
                for name in sorted(os.listxattr(path, follow_symlinks=False))
            },
        }
        if stat.S_ISDIR(info.st_mode):
            record["kind"] = "directory"
            pending.extend(sorted(path.iterdir(), reverse=True))
        elif stat.S_ISREG(info.st_mode):
            record["kind"] = "file"
            hashed = hashlib.sha256()
            with path.open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    hashed.update(block)
            record["sha256"] = hashed.hexdigest()
            record["size"] = info.st_size
            identity = (info.st_dev, info.st_ino)
            record["hardlink_to"] = hardlinks.setdefault(identity, relative)
        elif stat.S_ISLNK(info.st_mode):
            record.update(kind="symlink", link=os.readlink(path))
        else:
            raise ValueError("UNSUPPORTED_FILE_TYPE")
        files[relative] = record
    return {
        "schema_version": "lotus.resource-recovery.files.v1",
        "files": dict(sorted(files.items())),
    }


def archive_volume() -> None:
    before = file_manifest(SOURCE)
    subprocess.run(
        [
            "tar",
            "--sort=name",
            "--format=pax",
            "--numeric-owner",
            "--acls",
            "--xattrs",
            "--xattrs-include=*",
            "--selinux",
            "--sparse",
            "-cpf",
            str(ARCHIVE / "volume.tar"),
            "-C",
            str(SOURCE),
            ".",
        ],
        check=True,
        capture_output=True,
    )
    if file_manifest(SOURCE) != before:
        raise ValueError("SOURCE_CHANGED_DURING_ARCHIVAL")
    (ARCHIVE / "files.json").write_text(
        json.dumps(before, sort_keys=True), encoding="utf-8"
    )


def restore_volume() -> None:
    if any(SOURCE.iterdir()):
        raise ValueError("RESTORE_TARGET_NOT_EMPTY")
    subprocess.run(
        [
            "tar",
            "--numeric-owner",
            "--same-owner",
            "--same-permissions",
            "--acls",
            "--xattrs",
            "--xattrs-include=*",
            "--selinux",
            "-xpf",
            str(ARCHIVE / "volume.tar"),
            "-C",
            str(SOURCE),
        ],
        check=True,
        capture_output=True,
    )
    restored = file_manifest(SOURCE)
    original = json.loads((ARCHIVE / "files.json").read_text(encoding="utf-8"))
    if restored != original:
        raise ValueError("RESTORED_VOLUME_MISMATCH")
    (ARCHIVE / "restored-files.json").write_text(
        json.dumps(restored, sort_keys=True), encoding="utf-8"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["archive", "restore"])
    parser.add_argument("--max-bytes", type=int, required=True)
    args = parser.parse_args(argv)
    try:
        if args.max_bytes <= 0:
            raise ValueError("INVALID_ARCHIVE_BUDGET")
        # The shipped worker runs in Linux. Bound writes in the kernel, including
        # the tar child, rather than discovering an oversized archive afterwards.
        import resource

        resource.setrlimit(resource.RLIMIT_FSIZE, (args.max_bytes, args.max_bytes))
        if args.action == "archive":
            archive_volume()
        else:
            restore_volume()
        return 0
    except (OSError, ValueError, subprocess.SubprocessError):
        # Files, content, xattrs and child stderr remain private archive evidence.
        print("VOLUME_IO_FAILED")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
