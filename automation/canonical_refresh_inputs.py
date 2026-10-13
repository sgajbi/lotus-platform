"""Freeze reviewed Compose configuration and export committed build inputs."""
from __future__ import annotations

import argparse
import copy
import json
import os
import subprocess
from pathlib import Path

try:
    from automation.canonical_runtime_lease import digest, require
except ModuleNotFoundError:
    from canonical_runtime_lease import digest, require


def git(repo: Path, *arguments: str, data: bytes | None = None) -> bytes:
    return subprocess.run(['git', '-C', str(repo), *arguments], input=data,
                          capture_output=True, check=True).stdout


def export_commit(repo: Path, revision: str, destination: Path) -> None:
    """Read blobs, never the index, archive attributes or ignored working files."""
    require(git(repo, 'rev-parse', 'HEAD').decode().strip() == revision,
            'Build snapshot source differs from reviewed revision.')
    entries = []
    for record in git(repo, 'ls-tree', '-rz', '--full-tree', revision).split(b'\0'):
        if not record:
            continue
        metadata, name = record.split(b'\t', 1)
        mode, kind, object_id = metadata.split()
        require(mode in {b'100644', b'100755'} and kind == b'blob',
                'Committed build snapshot does not support symlinks or submodules.')
        relative = Path(os.fsdecode(name))
        require(not relative.is_absolute() and '..' not in relative.parts,
                'Invalid committed build path.')
        entries.append((relative, mode, object_id))
    # One batch preserves exact blob bytes, including executable script contents.
    blobs = git(repo, 'cat-file', '--batch', data=b''.join(row[2] + b'\n' for row in entries))
    offset = 0
    destination.mkdir()
    for relative, mode, expected_id in entries:
        end = blobs.index(b'\n', offset)
        object_id, kind, size = blobs[offset:end].split()
        require(object_id == expected_id and kind == b'blob', 'Committed blob identity changed.')
        count = int(size)
        content = blobs[end + 1:end + 1 + count]
        require(len(content) == count and blobs[end + 1 + count:end + 2 + count] == b'\n',
                'Incomplete committed build blob.')
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        path.chmod(0o755 if mode == b'100755' else 0o644)
        offset = end + count + 2
    require(offset == len(blobs), 'Unexpected committed build blob output.')


def freeze(repo: Path, revision: str, config: dict, expected_digest: str,
           output: Path, services: list[str]) -> Path:
    require(digest(config) == expected_digest, 'Evaluated Compose configuration differs from reviewed digest.')
    model = copy.deepcopy(config)
    snapshot = output / 'source'
    export_commit(repo, revision, snapshot)
    for name in services:
        service = model['services'][name]
        require(not service.get('env_file'), 'Evaluated Compose must resolve service env files.')
        build = service['build']
        require(all(value is not None for value in (service.get('environment') or {}).values()) and
                all(value is not None for value in (build.get('args') or {}).values()),
                'Evaluated Compose must resolve environment and build argument values.')
        context = Path(build['context']).resolve()
        dockerfile = Path(build.get('dockerfile', 'Dockerfile'))
        if not dockerfile.is_absolute():
            dockerfile = context / dockerfile
        try:
            context_relative = context.relative_to(repo.resolve())
            dockerfile_relative = dockerfile.resolve().relative_to(repo.resolve())
        except ValueError as exc:
            raise ValueError('Build input outside reviewed repository.') from exc
        exported_context = snapshot / context_relative
        exported_dockerfile = snapshot / dockerfile_relative
        require(exported_context.is_dir() and exported_dockerfile.is_file(),
                'Build context and Dockerfile must exist in the committed snapshot.')
        build['context'] = str(exported_context)
        build['dockerfile'] = str(exported_dockerfile)
    # `compose config` already doubles literal dollars for reuse, including JSON.
    # Preserve that representation; escaping again would change container values.
    path = output / 'compose.json'
    path.write_text(json.dumps(model, ensure_ascii=True), encoding='utf-8')
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['digest', 'freeze'])
    parser.add_argument('--config', required=True)
    parser.add_argument('--repo')
    parser.add_argument('--revision')
    parser.add_argument('--digest')
    parser.add_argument('--output')
    parser.add_argument('--services', nargs='+')
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text(encoding='utf-8-sig'))
    if args.action == 'digest':
        print(digest(config))
    else:
        require(all((args.repo, args.revision, args.digest, args.output, args.services)),
                'Exact reviewed configuration/source and output required.')
        freeze(Path(args.repo), args.revision, config, args.digest, Path(args.output), args.services)


if __name__ == '__main__':
    main()
